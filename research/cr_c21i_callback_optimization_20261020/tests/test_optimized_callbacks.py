"""Focused C21I contracts against the frozen original RHS and C21H callback.

Capture stops before any solver.  Microphysics is explicitly manufactured;
the private-driver wiring test uses a tool stub, not a Rust/native execution.
"""
from dataclasses import asdict, replace
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE.parent / "cr_c21e_event_native_20261018"
C21G = HERE.parent / "cr_c21g_reference_refinement_20261019"
spec = importlib.util.spec_from_file_location("c21i_test_adapter", HERE / "optimized_adapter.py")
opt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(opt)
BASE = opt.load_frozen_adapter()
BASE.private_reference(SOURCE)
sys.path.insert(0, str(C21G))
from campaign_contract import fixture_scales
from run_experiment import make_fixture, Fixture
from event_coupler import ManufacturedMicro, ZeroMicro, ProviderFailure


class CapturedBeforeIntegrator(RuntimeError):
    pass


def capture(fixture=None, provider=None):
    reference = BASE.private_reference(SOURCE)
    fixture = opt._freeze_fixture(fixture or make_fixture(a0=.09, dx=1e-4, opacity_scale=.0003))
    provider = provider or ManufacturedMicro()
    scale = fixture_scales(asdict(fixture))
    captured = {}

    def stop(fun, span, y0, **kwargs):
        captured.update(fun=fun, span=span, y0=np.array(y0, copy=True), controls=kwargs)
        raise CapturedBeforeIntegrator()

    reference.solve_ivp = stop
    try:
        reference.run_reference_tau(fixture, provider, rtol=2e-11,
                                    atol=2e-14*np.asarray(scale["values"]))
    except CapturedBeforeIntegrator:
        pass
    else:
        raise AssertionError("Original event driver did not reach sentinel")
    m = len(fixture.q)
    dynamic = np.array([j for j in range(m+19) if not(fixture.Y == 0 and j in(m+1, m+2))])
    scales = np.asarray(scale["values"])[dynamic]
    return fixture, provider, reference, captured, scales, dynamic, scale


def admission(kind="MANUFACTURED_CONSERVATIVE_MICRO_NOT_GRACKLE"):
    return {"schema": "C21I_DETERMINISTIC_PROVIDER_ADMISSION_V1",
            "deterministic_successful_rhs": True, "provider_kind": kind,
            "provider_identity": {"test": "explicit manufactured successful RHS"},
            "admitted_by": "This test's captured original deterministic provider"}


def callbacks(data, mode, *, fun=None, guard=None):
    f, provider, ref, c, scales, dynamic, _ = data
    cls = BASE.CellCallbacks if mode == "original" else opt.make_callback_type(
        BASE, mode, cache_contract=admission(provider.kind), cache_guard=guard)
    return cls(fun or c["fun"], f, *c["span"], scales, dynamic, ref)


def physical_state(data):
    f, _, _, c, _, dynamic, _ = data
    u = c["y0"].copy()
    m = len(f.q)
    u[:m] = np.linspace(-.0125, .175, m)  # Admitted implicit continuation.
    for j, full in enumerate(dynamic):
        if full == m:
            u[j] = .31
        elif full == m+1:
            u[j] = .125
        elif full == m+2:
            u[j] = .03125
        elif full == m+3:
            u[j] *= 1.07
    return u


def bits(value):
    return np.ascontiguousarray(value, dtype="<f8").view("<u8")


class OptimizedCallbackTests(unittest.TestCase):
    def assert_bits(self, a, b):
        np.testing.assert_array_equal(bits(a), bits(b))

    def test_vectorized_jacobian_bitwise_for_y_zero_helium_and_existing_fixtures(self):
        fixtures = [make_fixture(a0=.09, dx=1e-4, opacity_scale=.0003, Y=y) for y in (0., .079)]
        for name in ("common_ic", "native_source"):
            path = SOURCE / "evidence/C21F_NATIVE_NCP_20261018T1358Z" / name / "fixture.json"
            fixtures.append(Fixture(**json.loads(path.read_text())))
        for f in fixtures:
            data = capture(f)
            for mode in ("vectorized", "vectorized_exact"):
                with self.subTest(Y=f.Y, M=len(f.q), mode=mode):
                    old, new = callbacks(data, "original"), callbacks(data, mode)
                    u = physical_state(data)
                    t = old.lo+.43*(old.hi-old.lo)
                    z = u/old.scales
                    self.assert_bits(old.jacobian(t, z), new.jacobian(t, z))
                    self.assert_bits(old.rhs(t, z), new.rhs(t, z))
                    self.assert_bits(old.partial_t(t, z), new.partial_t(t, z))
                    self.assertEqual(old.fd_nodes, new.fd_nodes)
                    self.assertEqual(old.counts["original_rhs_evaluations"]-
                                     new.counts["original_rhs_evaluations"], 2 if mode.endswith("exact") else 0)
                    self.assertEqual(new.counts["avoided_full_matrix_allocations"], 1)
                    self.assertEqual(new.counts["jacobian_scratch_bytes"], 8*new.n**2)

    def test_large_cohort_bitwise_assembly_and_three_term_rounding(self):
        f = make_fixture(a0=.09, dx=1e-4, opacity_scale=.0003)
        count = 128
        f = replace(f, q=tuple(f.q[j % len(f.q)] for j in range(count)),
                    amounts=tuple(f.amounts[j % len(f.q)]/count for j in range(count)),
                    birth=(f.x0,)*count)
        data = capture(f)
        old, new = callbacks(data, "original"), callbacks(data, "vectorized")
        z = physical_state(data)/old.scales
        self.assert_bits(old.jacobian((old.lo+old.hi)/2, z), new.jacobian((old.lo+old.hi)/2, z))
        rng = np.random.default_rng(73152)
        terms = np.ldexp(rng.uniform(-1., 1., (2048, 3)), rng.integers(-1020, 1000, (2048, 3)))
        terms[:4] = [[-0., -0., -0.], [0., -0., 0.], [1., -1., -0.], [1e100, 1., -1e100]]
        actual = np.sum(terms, axis=1)
        expected = np.array([float(np.sum(row)) for row in terms])
        self.assert_bits(actual, expected)

    def test_exact_y_zero_underflow_and_structural_signed_zeros(self):
        f = make_fixture(a0=.09, dx=1e-7, opacity_scale=.0003, Y=0.)
        f = replace(f, amounts=(0., *f.amounts[1:]))
        data = capture(f)
        old, new = callbacks(data, "original"), callbacks(data, "vectorized_exact")
        u = physical_state(data)
        u[:old.m] = 1000.
        u[0] = -0.
        z = u/old.scales
        t = old.lo+.5*(old.hi-old.lo)
        self.assertEqual(old.n, old.m+17)
        self.assertNotIn(old.m+1, new.dynamic)
        self.assertNotIn(old.m+2, new.dynamic)
        self.assert_bits(old.jacobian(t, z), new.jacobian(t, z))
        self.assert_bits(old.rhs(t, z), new.rhs(t, z))
        pop, logs = data[2].reconstruct_population(f.amounts, u[:old.m], old.active)
        self.assertTrue(np.all(pop == 0.))
        self.assertTrue(np.isfinite(logs[old.active & (np.asarray(f.amounts) > 0)]).all())
        self.assertTrue(np.all(new.jacobian(t, z)[:, -15:] == 0.))

    def test_gas_boundaries_and_inherited_helium_failure_are_preserved(self):
        data = capture()
        old, new = callbacks(data, "original"), callbacks(data, "vectorized_exact")
        u = physical_state(data)
        for x, y, zhe in ((0., 0., 0.), (1., .75, .25), (.4, .25, .75)):
            u[old.m:old.m+3] = (x, y, zhe)
            z = u/old.scales
            t = (old.lo+old.hi)/2
            self.assert_bits(old.jacobian(t, z), new.jacobian(t, z))
        # At this simplex vertex, no axis-aligned HeII stencil exists:
        # negative HeII is invalid and positive HeII makes HeII+HeIII>1.
        u[old.m:old.m+3] = (.4, 0., 1.)
        for cb in (old, new):
            with self.assertRaisesRegex(BASE.AdapterError, "NO_ADMISSIBLE_GAS_FD_STENCIL"):
                cb.jacobian((cb.lo+cb.hi)/2, u/cb.scales)
        u[old.m:old.m+3] = (.4, .8, .2)
        for cb in (old, new):
            with self.assertRaisesRegex(ProviderFailure, "MICRO_NEGATIVE_EVENT_OR_ESCAPE"):
                cb.rhs((cb.lo+cb.hi)/2, u/cb.scales)

    def test_cell_clamps_short_cells_and_represented_fd_nodes_match(self):
        for dx in (1e-4, 1e-7):
            data = capture(make_fixture(a0=.09, dx=dx, opacity_scale=.0003, Y=0.))
            old, new = callbacks(data, "original"), callbacks(data, "vectorized_exact")
            z = data[3]["y0"]/old.scales
            for t in (old.lo, old.left, old.hi, old.right,
                      old.lo+.5*(old.hi-old.lo), np.nextafter(old.left, old.right)):
                self.assert_bits(old.partial_t(t, z), new.partial_t(t, z))
            self.assertEqual(old.fd_nodes, new.fd_nodes)
            self.assertTrue(all(old.left < node < old.right for row in new.fd_nodes
                                if row["kind"] == "time" for node in row["nodes"]))
            one = float(np.nextafter(old.lo, old.hi))
            end = float(np.nextafter(one, old.hi))
            cls = type(new)
            tiny = cls(new.fun, new.f, old.lo, end, new.scales, new.dynamic, new.ref)
            with self.assertRaisesRegex(BASE.AdapterError, "NO_INTERIOR_TIME_FD_STENCIL"):
                tiny.partial_t(one, z)

    def test_cache_keys_include_t_u_ulp_signed_zero_and_passive_bits(self):
        data = capture()
        cb = callbacks(data, "vectorized_exact")
        u = physical_state(data)
        u[-1] = 0.
        t = (cb.lo+cb.hi)/2
        cb.original(t, u)
        cb.original(t, u.copy())
        self.assertEqual(cb.counts["original_rhs_cache_hits"], 1)
        for point, state in ((np.nextafter(t, cb.hi), u),
                             (t, np.concatenate((u[:-1], [-0.]))),
                             (t, np.concatenate((u[:-1], [np.nextafter(0., 1.)])))):
            cb.original(point, state)
        other = u.copy()
        other[0] = np.nextafter(other[0], math.inf)
        cb.original(t, other)
        self.assertEqual(cb.counts["original_rhs_evaluations"], 5)
        self.assertEqual(cb.counts["original_rhs_requests"], 6)
        # Direct original() test exercises the key's time signed-zero bits;
        # this synthetic callback is not a physical event-cell query.
        zero = callbacks(data, "vectorized_exact", fun=lambda t, u: u.copy())
        zero.original(0., u)
        zero.original(-0., u)
        self.assertEqual(zero.counts["original_rhs_evaluations"], 2)

    def test_cache_retains_cross_operation_base_and_has_bounded_lru(self):
        data = capture()
        cb = callbacks(data, "vectorized_exact")
        u = physical_state(data)
        z = u/cb.scales
        t = (cb.lo+cb.hi)/2
        cb.jacobian(t, z)
        cb.rhs(t, z)
        cb.partial_t(t, z)
        self.assertEqual(cb.counts["original_rhs_cache_hits"], 2)
        self.assertEqual(cb.counts["original_rhs_requests"], 13)
        self.assertEqual(cb.counts["original_rhs_evaluations"], 11)
        for value in range(30):
            v = u.copy()
            v[-1] = float(value)
            cb.original(t, v)
        self.assertEqual(len(cb._cache), opt.CACHE_CAPACITY)
        self.assertEqual(cb.counts["rhs_cache_peak_entries"], opt.CACHE_CAPACITY)
        self.assertGreater(cb.counts["original_rhs_cache_evictions"], 0)

    def test_cache_values_and_jacobian_results_cannot_alias_future_calls(self):
        data = capture()
        cb = callbacks(data, "vectorized_exact")
        u = physical_state(data)
        t = (cb.lo+cb.hi)/2
        expected = cb.original(t, u).copy()
        one = cb.original(t, u)
        one[:] = 9.
        self.assert_bits(cb.original(t, u), expected)
        first = cb.jacobian(t, u/cb.scales)
        saved = first.copy()
        other = u.copy()
        other[0] += .1
        second = cb.jacobian(t, other/cb.scales)
        self.assertFalse(np.shares_memory(first, second))
        self.assertFalse(np.shares_memory(first, cb._matrix))
        self.assert_bits(first, saved)
        self.assertFalse(cb.scales.flags.writeable)

    def test_exceptions_and_nonfinite_results_never_enter_cache(self):
        data = capture()
        attempts = []
        def transient(t, u):
            attempts.append(1)
            if len(attempts) == 1:
                raise RuntimeError("recorded transient failure")
            return u.copy()
        cb = callbacks(data, "vectorized_exact", fun=transient)
        u = physical_state(data)
        t = (cb.lo+cb.hi)/2
        with self.assertRaisesRegex(RuntimeError, "recorded transient"):
            cb.original(t, u)
        self.assertEqual(len(cb._cache), 0)
        cb.original(t, u)
        cb.original(t, u)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(cb.counts["original_rhs_evaluations"], 2)
        bad = callbacks(data, "vectorized_exact", fun=lambda t, u: np.full_like(u, np.nan))
        for _ in range(2):
            with self.assertRaisesRegex(BASE.AdapterError, "ORIGINAL_RHS_RESULT_DOMAIN"):
                bad.original(t, u)
        self.assertEqual(len(bad._cache), 0)
        self.assertEqual(bad.counts["original_rhs_evaluations"], 2)

    def test_cache_hits_do_not_bypass_domain_or_live_guards(self):
        data = capture()
        live = {"closed": False, "expired": False}
        def guard():
            if live["closed"]:
                raise RuntimeError("provider closed")
            if live["expired"]:
                raise RuntimeError("deadline expired")
        cb = callbacks(data, "vectorized_exact", guard=guard)
        z = physical_state(data)/cb.scales
        t = (cb.lo+cb.hi)/2
        cb.rhs(t, z)
        for point, state in ((cb.lo-1., z), (cb.hi+1., z),
                             (t, np.full(cb.n, np.nan)), (t, z[:-1])):
            with self.assertRaises(BASE.AdapterError):
                cb.rhs(point, state)
        for key in ("closed", "expired"):
            live[key] = True
            with self.assertRaisesRegex(RuntimeError, key):
                cb.rhs(t, z)
            live[key] = False
        self.assertEqual(cb.counts["original_rhs_evaluations"], 1)
        self.assertEqual(cb.counts["original_rhs_cache_hits"], 0)

    def test_new_closure_fixture_cell_and_changed_scope_cannot_reuse_cache(self):
        data = capture()
        a, b = callbacks(data, "vectorized_exact"), callbacks(data, "vectorized_exact")
        u = physical_state(data)
        t = (a.lo+a.hi)/2
        a.original(t, u)
        b.original(t, u)
        self.assertEqual(b.counts["original_rhs_cache_hits"], 0)
        self.assertIsNot(a._cache, b._cache)
        different = capture(replace(data[0], opacity_scale=data[0].opacity_scale*2))
        changed = callbacks(different, "vectorized_exact")
        self.assertNotEqual(a.cache_scope_sha256, changed.cache_scope_sha256)
        for attribute, value in (("fun", lambda t, u: u), ("f", different[0]),
                                 ("lo", np.nextafter(a.lo, a.hi))):
            cb = callbacks(data, "vectorized_exact")
            cb.original(t, u)
            setattr(cb, attribute, value)
            with self.assertRaisesRegex(opt.OptimizationError, "CALLBACK_FROZEN_SCOPE_CHANGED"):
                cb.original(t, u)

    def test_generic_stateful_callback_is_not_cached_by_default(self):
        with self.assertRaisesRegex(opt.OptimizationError, "ADMISSION_REQUIRED"):
            opt.make_callback_type(BASE, "vectorized_exact")
        data = capture()
        counter = []
        def stateful(t, u):
            counter.append(1)
            return u+len(counter)
        cb = callbacks(data, "vectorized", fun=stateful)
        u = physical_state(data)
        t = (cb.lo+cb.hi)/2
        a, b = cb.original(t, u), cb.original(t, u)
        self.assertFalse(np.array_equal(a, b))
        self.assertEqual(cb.counts["original_rhs_evaluations"], 2)
        class StatefulProvider(ManufacturedMicro):
            pass
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(opt.OptimizationError, "ADMISSION_REQUIRED"):
                opt.run_optimized_reference(data[0], StatefulProvider(), SOURCE, "unused",
                    temp, data[-1], optimization="vectorized_exact")

    def test_frozen_manifest_and_runtime_bytes_are_enforced(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = json.loads((opt.DEFAULT_C21H/"EXECUTION_MANIFEST.json").read_text())
            for name in ("EXECUTION_MANIFEST.json", *manifest["runtime_files"]):
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(opt.DEFAULT_C21H/name, path)
            module = opt.load_frozen_adapter(root)
            self.assertEqual(module.REFERENCE_SHA256, BASE.REFERENCE_SHA256)
            (root/"optical_adapter.py").write_bytes((root/"optical_adapter.py").read_bytes()+b"\n")
            with self.assertRaisesRegex(opt.OptimizationError, "RUNTIME_SOURCE_MISMATCH"):
                opt.load_frozen_adapter(root)
            (root/"EXECUTION_MANIFEST.json").write_text("{}")
            with self.assertRaisesRegex(opt.OptimizationError, "MANIFEST_MISMATCH"):
                opt.load_frozen_adapter(root)

    def test_fixture_snapshot_owns_mutable_lists_without_changing_json_scalar_types(self):
        original = make_fixture(a0=.09, dx=1e-4, opacity_scale=.0003)
        mutable = replace(original, q=list(original.q), birth=list(original.birth),
                          amounts=[0, *original.amounts[1:]], gas0=list(original.gas0))
        frozen = opt._freeze_fixture(mutable)
        digest = frozen.digest
        self.assertEqual(digest, mutable.digest)
        self.assertIsInstance(frozen.amounts[0], int)
        mutable.q[0] *= 2
        mutable.gas0[0] = .6
        self.assertEqual(frozen.digest, digest)
        self.assertIsInstance(frozen.q, tuple)
        self.assertNotEqual(mutable.digest, digest)

    def test_run_wrapper_provider_closed_deadline_and_exit_checks_precede_hits(self):
        data = capture()
        for failure, message in (("closed", "C21I_PROVIDER_CLOSED"),
                                 ("deadline", "NATIVE_JOB_WALL_BUDGET"),
                                 ("exit", "C21I_PROVIDER_EXITED")):
            with self.subTest(failure=failure):
                module = opt.load_frozen_adapter()
                process = SimpleNamespace(returncode=None)
                process.poll = lambda: process.returncode
                provider = SimpleNamespace(kind="EXPLICIT_GUARD_TOOL_STUB", deadline=math.inf,
                                           native=SimpleNamespace(closed=False, process=process))
                observed = []
                def driver(fixture, provider, *args, **kwargs):
                    cb = module.CellCallbacks(lambda t, u: u.copy(), fixture,
                        *data[3]["span"], data[4], data[5], data[2])
                    t = (cb.lo+cb.hi)/2
                    z = data[3]["y0"]/cb.scales
                    cb.rhs(t, z)
                    if failure == "closed":
                        provider.native.closed = True
                    elif failure == "deadline":
                        provider.deadline = time.monotonic()-1.
                    else:
                        process.returncode = 7
                    try:
                        cb.rhs(t, z)
                    finally:
                        observed.append(dict(cb.counts))
                    raise AssertionError("Expired/closed provider was bypassed")
                with tempfile.TemporaryDirectory() as temp:
                    with mock.patch.object(opt, "load_frozen_adapter", return_value=module), \
                            mock.patch.object(module, "run_rust_reference", side_effect=driver):
                        with self.assertRaisesRegex(module.AdapterError, message):
                            opt.run_optimized_reference(data[0], provider, SOURCE, "UNUSED",
                                temp, data[-1], optimization="vectorized_exact",
                                cache_contract=admission(provider.kind))
                self.assertEqual(observed[0]["original_rhs_evaluations"], 1)
                self.assertEqual(observed[0]["original_rhs_cache_hits"], 0)

    def test_callback_postguards_reject_late_evaluations_and_cache_hits(self):
        data = capture()
        u = physical_state(data)
        for mode in opt.OPTIMIZATIONS:
            with self.subTest(mode=mode, operation="underlying_rhs"):
                clock = {"now": 0.}
                def guard():
                    if clock["now"] >= 1.:
                        raise RuntimeError("FAKE_CLOCK_JOB_EXPIRED")
                def slow_value(t, u):
                    clock["now"] = 2.
                    return u.copy()
                cb = callbacks(data, mode, fun=slow_value, guard=guard)
                with self.assertRaisesRegex(RuntimeError, "FAKE_CLOCK_JOB_EXPIRED"):
                    cb.rhs((cb.lo+cb.hi)/2, u/cb.scales)
                self.assertEqual(cb.counts["original_rhs_evaluations"], 1)
                self.assertEqual(len(cb._cache), 0)
                self.assertEqual(cb.counts["original_rhs_cache_hits"], 0)

        clock = {"checks": 0, "expire_on_second_check": False}
        def guard_hit():
            if clock["expire_on_second_check"]:
                clock["checks"] += 1
                if clock["checks"] >= 2:
                    raise RuntimeError("FAKE_CLOCK_CACHE_COPY_EXPIRED")
        cb = callbacks(data, "vectorized_exact", fun=lambda t, u: u.copy(), guard=guard_hit)
        t = (cb.lo+cb.hi)/2
        cb.original(t, u)
        clock["expire_on_second_check"] = True
        with self.assertRaisesRegex(RuntimeError, "FAKE_CLOCK_CACHE_COPY_EXPIRED"):
            cb.original(t, u)
        self.assertEqual(cb.counts["original_rhs_evaluations"], 1)
        self.assertEqual(cb.counts["original_rhs_cache_hits"], 0)
        self.assertEqual(len(cb._cache), 1)  # Only the earlier timely value.

    def test_run_wrapper_entry_deadline_includes_setup_final_result_and_readback(self):
        data = capture()
        actual_snapshot = opt.source_snapshot
        for phase in ("setup", "final_result", "final_readback"):
            with self.subTest(phase=phase):
                module = opt.load_frozen_adapter()
                clock = {"now": 0., "snapshot_count": 0, "driver_count": 0}
                def setup(*args, **kwargs):
                    if phase == "setup":
                        clock["now"] = 2.
                    return module
                def snapshot(*args, **kwargs):
                    value = actual_snapshot(*args, **kwargs)
                    clock["snapshot_count"] += 1
                    if phase == "final_readback" and clock["snapshot_count"] == 2:
                        clock["now"] = 2.
                    return value
                def driver(*args, **kwargs):
                    clock["driver_count"] += 1
                    if phase == "final_result":
                        clock["now"] = 2.
                    return {"solver_diagnostics": {"counter_note": "FAKE_CLOCK_NO_SOLVER"}}
                with tempfile.TemporaryDirectory() as temp:
                    with mock.patch.object(opt, "load_frozen_adapter", side_effect=setup), \
                            mock.patch.object(opt, "source_snapshot", side_effect=snapshot), \
                            mock.patch.object(opt.time, "monotonic", side_effect=lambda: clock["now"]), \
                            mock.patch.object(module, "run_rust_reference", side_effect=driver):
                        with self.assertRaisesRegex(module.AdapterError, "RUST_JOB_WALL_BUDGET"):
                            opt.run_optimized_reference(data[0], ManufacturedMicro(), SOURCE,
                                "FAKE_CLOCK_NO_BINARY", temp, data[-1], wall_s=1.,
                                optimization="vectorized_exact")
                self.assertEqual(clock["driver_count"], 0 if phase == "setup" else 1)

        # Positive control: a timely setup consumes half of the supplied
        # budget, and the original driver's RPC wait receives only the rest.
        module = opt.load_frozen_adapter()
        clock = {"now": 0.}
        def timely_setup(*args, **kwargs):
            clock["now"] = .5
            return module
        def timely_driver(*args, **kwargs):
            self.assertEqual(args[-1], .5)
            return {"solver_diagnostics": {"counter_note": "FAKE_CLOCK_NO_SOLVER"}}
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.object(opt, "load_frozen_adapter", side_effect=timely_setup), \
                    mock.patch.object(opt.time, "monotonic", side_effect=lambda: clock["now"]), \
                    mock.patch.object(module, "run_rust_reference", side_effect=timely_driver):
                result = opt.run_optimized_reference(data[0], ManufacturedMicro(), SOURCE,
                    "FAKE_CLOCK_NO_BINARY", temp, data[-1], wall_s=1.,
                    optimization="vectorized_exact")
        self.assertEqual(result["callback_optimization"]["mode"], "vectorized_exact")

    def test_private_driver_binding_reuses_original_event_loop_and_trace_contract(self):
        data = capture(make_fixture(a0=.09, dx=1e-7, opacity_scale=.0003, Y=0.))
        module = opt.load_frozen_adapter()
        original_public = BASE.CellCallbacks
        seen = []
        def fake_segment(binary, config, callbacks, output, **kwargs):
            output.mkdir()
            t = config["t0"]+.5*(config["t1"]-config["t0"])
            callbacks.jacobian(t, config["y0"])
            callbacks.rhs(t, config["y0"])
            callbacks.partial_t(t, config["y0"])
            seen.append(dict(callbacks.counts))
            return {"accepted_grid_complete": True,
                    "accepted_times": [config["t0"], config["t1"]],
                    "accepted_states": [config["y0"], config["y0"]],
                    "internal_steps": 1, "counters": {"direct_factorizations": 1}}
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.object(opt, "load_frozen_adapter", return_value=module), \
                    mock.patch.object(module, "run_segment", side_effect=fake_segment):
                result = opt.run_optimized_reference(data[0], ManufacturedMicro(), SOURCE,
                    "TOOL_STUB_NOT_NATIVE", temp, data[-1], optimization="vectorized_exact")
        self.assertIs(BASE.CellCallbacks, original_public)
        self.assertEqual(result["callback_optimization"]["mode"], "vectorized_exact")
        self.assertEqual(result["global_error_bound"], None)
        self.assertTrue(result["accepted_state_trace_complete"])
        self.assertEqual(result["rhs_evaluations"], sum(s["original_rhs_evaluations"] for s in seen))
        self.assertEqual(len(result["rust_segments"]), len(seen))
        self.assertTrue(all(s["original_rhs_cache_hits"] == 2 for s in seen))
        self.assertEqual(result["tolerance_contract"]["integrated_state_size"], len(data[0].q)+17)


if __name__ == "__main__":
    unittest.main(verbosity=2)
