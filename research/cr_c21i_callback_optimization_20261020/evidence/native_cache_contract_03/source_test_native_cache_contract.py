"""Focused admission contracts with exact Python classes and stub IO only.

No Popen/native process, Rust compiler, ODE integrator or historical test is
called.  Temporary synthetic build records test the existing provenance gate;
they are not evidence that a stub binary was compiled from the native owner.
"""
from dataclasses import asdict
import copy
import hashlib
import importlib
import importlib.util
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import time
from types import ModuleType
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE.parent / "cr_c21e_event_native_20261018"
C21H = HERE.parent / "cr_c21h_vigilode_bridge_20261019"
NUMPY_BEFORE_HELPER = "numpy" in sys.modules
spec = importlib.util.spec_from_file_location("c21i_native_contract_tests", HERE / "native_cache_contract.py")
admit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admit)
NUMPY_AFTER_HELPER = "numpy" in sys.modules
sys.path.insert(0, str(C21H))
H = ModuleType("_c21i_contract_private_h")
H.__file__ = str(C21H / "run_pilot.py")
exec(compile(Path(H.__file__).read_bytes(), H.__file__, "exec"), H.__dict__)
REF = H.private_reference(SOURCE)
NATIVE_MODULE = importlib.import_module("native_micro")
NativeMicro = NATIVE_MODULE.NativeMicro
from event_coupler import ProviderFailure, temperature
from run_experiment import make_fixture
import numpy as np
spec = importlib.util.spec_from_file_location("c21i_native_test_opt", HERE / "optimized_adapter.py")
opt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(opt)
BASE = opt.load_frozen_adapter()


class NamedText(io.StringIO):
    def __init__(self, name):
        super().__init__()
        self.name = str(name)


class StubProcess:
    def __init__(self, command):
        self.pid = 424242
        self.args = list(command)
        self.stdin = io.BytesIO()
        self.stdout = io.BytesIO()
        self.returncode = None

    def poll(self):
        return self.returncode


class StubSelector:
    def select(self, timeout):
        raise AssertionError("Stub tests must supply complete buffered protocol lines")

    def close(self):
        pass


def record(path):
    raw = Path(path).read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


class NativeAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="c21i-admission-stub-")
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.build = self.root / "build"
        self.build.mkdir()
        self.binary = self.build / "native_point"
        self.binary.write_bytes(b"C21I TEST STUB BYTES - NOT A NATIVE BUILD\n")
        self.binary.chmod(0o755)
        (self.build / "owner_commit.txt").write_text(admit.OWNER + "\n")
        (self.build / "build_exit.txt").write_text("exit_code=0\n")
        (self.build / "owner_source.tar").write_bytes(b"Synthetic provenance test fixture; not an owner source archive.\n")
        wrapper_hash = record(SOURCE / "native/native_point.rs")["sha256"]
        archive = record(self.build / "owner_source.tar")
        (self.build / "input_sha256.txt").write_text(
            f'{record(self.binary)["sha256"]}  native_point\n'
            f'{wrapper_hash}  native_point.rs\n'
            f'{archive["sha256"]}  owner_source.tar\n')
        self.provenance = {
            "path": str(self.binary), **record(self.binary), "owner": admit.OWNER,
            "status": "RECORDED_PINNED_OWNER_BUILD", "owner_source_archive": archive,
            "native_wrapper_sha256": wrapper_hash, "build_directory": str(self.build),
            "meaning": "Build-script provenance and actual hashes; not a claim of bit-reproducible toolchains.",
        }
        self.fixture = make_fixture(a0=.09, dx=1e-7, opacity_scale=.0003, Y=0.)
        self.fixture_identity = {"fixture_sha256": self.fixture.digest,
                                 "fixture": json.loads(json.dumps(asdict(self.fixture)))}
        self.source_identity = {"scope": "STUB_TEST_ONLY", "runtime_files": {
            "native_cache_contract.py": record(HERE / "native_cache_contract.py"),
            "optimized_adapter.py": record(HERE / "optimized_adapter.py")}}
        # __init__ would launch a process: create the exact class with stub IO.
        self.native = NativeMicro.__new__(NativeMicro)
        self.native.command = [str(self.binary)]
        self.native.timeout = 15.0
        self.native.max_calls = 2
        self.native.calls = 0
        self.native.closed = False
        self.output = self.root / "native"
        self.output.mkdir()
        self.native.log = NamedText(self.output / "native_points.jsonl")
        self.native.stderr = NamedText(self.output / "native_stderr.log")
        self.native.process = StubProcess(self.native.command)
        self.native.selector = StubSelector()
        self.native.buffer = bytearray()
        self.process_record = {
            "owner": admit.OWNER, "command": self.native.command,
            "binary_sha256": record(self.binary)["sha256"], "timeout_s": 15.0, "max_calls": 2}
        (self.output / "native_process.json").write_text(json.dumps(self.process_record))
        self.provider = H.BudgetedNativeMicro(self.native, time.monotonic() + 60.0)

    def admitted(self, provider=None):
        return admit.admit_native_cache(provider or self.provider, self.provenance,
                                       self.fixture_identity, self.source_identity)

    def response(self):
        a, nh0, helium = .09, 1e-7, 0.
        gas = (.2, 0., 0., 1.)
        values = [a, nh0 / a**3, 0., temperature(gas, helium), *([0.] * 19)]
        return ("OK\t" + "\t".join(format(value, ".17e") for value in values) + "\n").encode("ascii")

    def native_call(self):
        return self.provider(.09, (.2, 0., 0., 1.), 1e-7, 0.)

    def callbacks(self, contract, guard, fun=None):
        m = len(self.fixture.q)
        dynamic = np.array([j for j in range(m+19) if j not in (m+1, m+2)])
        n = len(dynamic)
        if fun is None:
            def fun(t, u):
                self.native_call()
                return np.zeros(n)
        cls = opt.make_callback_type(BASE, "vectorized_exact", cache_contract=contract, cache_guard=guard)
        callback = cls(fun, self.fixture, self.fixture.x0, self.fixture.x0+1e-7,
                       np.ones(n), dynamic, REF)
        u = np.zeros(n)
        u[m], u[m+1] = .2, 1.
        return callback, u

    def test_helper_preserves_fresh_import_thread_order(self):
        self.assertFalse(NUMPY_BEFORE_HELPER)
        self.assertFalse(NUMPY_AFTER_HELPER)
        self.assertFalse(H.NUMPY_ALREADY_IMPORTED)

    def test_exact_bare_and_private_budgeted_class_contracts(self):
        for provider in (self.native, self.provider):
            with self.subTest(wrapper=provider is self.provider):
                contract, guard = self.admitted(provider)
                self.assertEqual(contract["provider_kind"], admit.NATIVE_KIND)
                self.assertTrue(contract["success_values_only"])
                self.assertEqual(contract["provider_identity"]["native_provenance"], self.provenance)
                guard(full_hash=True, current_provider=provider)
                self.assertEqual(self.native.calls, 0)
                self.assertEqual(self.native.process.stdin.getvalue(), b"")

    def test_unknown_subclass_and_preexisting_monkeypatch_rejected(self):
        class Foreign:
            kind = admit.NATIVE_KIND
        class Subclass(NativeMicro):
            pass
        with self.assertRaises(admit.NativeCacheAdmissionError):
            self.admitted(Foreign())
        foreign = Subclass.__new__(Subclass)
        vars(foreign).update(vars(self.native))
        with self.assertRaises(admit.NativeCacheAdmissionError):
            self.admitted(foreign)
        with mock.patch.object(NativeMicro, "__call__", lambda *args: None):
            with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "METHOD_CHANGED"):
                self.admitted()
        with mock.patch.object(NativeMicro, "kind", "FORGED"):
            with self.assertRaises(admit.NativeCacheAdmissionError):
                self.admitted()
        with mock.patch.object(NativeMicro, "__getattribute__", object.__getattribute__, create=True):
            with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "CLASS_NAMESPACE_CHANGED"):
                self.admitted()

    def test_post_admission_class_method_and_instance_override_rejected(self):
        _, guard = self.admitted()
        with mock.patch.object(NativeMicro, "__call__", lambda *args: None):
            with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "CLASS_REPLACED_OR_MUTATED"):
                guard()
        self.native._line = lambda: "OK"
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "CONFIGURATION_CHANGED"):
            guard()
        del self.native._line
        with mock.patch.dict(NATIVE_MODULE.__dict__, {"OWNER": "wrong"}):
            with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "GLOBAL_BINDING_CHANGED"):
                guard()

    def test_inner_outer_and_process_replacement_rejected(self):
        _, guard = self.admitted()
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "OUTER_PROVIDER_REPLACED"):
            guard(current_provider=object())
        original = self.provider.native
        replacement = NativeMicro.__new__(NativeMicro)
        vars(replacement).update(vars(original))
        self.provider.native = replacement
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "INNER_PROVIDER_OR_DEADLINE_CHANGED"):
            guard()
        self.provider.native = original
        process = self.native.process
        self.native.process = StubProcess(self.native.command)
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "PROCESS_REPLACED_OR_CHANGED"):
            guard()
        self.native.process = process
        process.pid += 1
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "PROCESS_REPLACED_OR_CHANGED"):
            guard()

    def test_closed_dead_and_replaced_or_closed_streams_rejected(self):
        _, guard = self.admitted()
        self.native.closed = True
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "PROVIDER_CLOSED"):
            guard()
        self.native.closed = False
        self.native.process.returncode = 0
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "PROVIDER_EXITED"):
            guard()
        self.native.process.returncode = None
        original = self.native.process.stdout
        self.native.process.stdout = io.BytesIO()
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "STREAM_REPLACED_OR_CLOSED"):
            guard()
        self.native.process.stdout = original
        original.close()
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "STREAM_REPLACED_OR_CLOSED"):
            guard()

    def test_timeout_changes_are_allowed_but_invalid_values_and_counter_reset_fail(self):
        _, guard = self.admitted()
        for timeout in (0.0001, 4., 15.):
            self.native.timeout = timeout
            guard()
        for timeout in (0., -1., 15.0001, float("inf"), float("nan"), True):
            self.native.timeout = timeout
            with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "TIMEOUT"):
                guard()
        self.native.timeout = 1.
        self.native.calls = 1
        guard()
        self.native.calls = 0
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "COUNTER_OR_CAP"):
            guard()
        self.native.calls = 3
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "COUNTER_OR_CAP"):
            guard()

    def test_nth_success_and_cached_hit_allowed_n_plus_one_miss_original_rejection(self):
        contract, guard = self.admitted()
        callback, u = self.callbacks(contract, guard)
        self.native.buffer.extend(self.response() * 2)
        t = self.fixture.x0 + .5e-7
        callback.original(t, u)
        changed = u.copy()
        changed[0] = np.nextafter(0., 1.)
        callback.original(t, changed)
        self.assertEqual(self.native.calls, self.native.max_calls)
        guard()
        hit = callback.original(t, u)
        self.assertTrue(np.isfinite(hit).all())
        self.assertEqual(self.native.calls, 2)
        self.assertEqual(callback.counts["original_rhs_cache_hits"], 1)
        changed[0] = 1.
        with self.assertRaisesRegex(ProviderFailure, "NATIVE_CALL_BUDGET"):
            callback.original(t, changed)
        self.assertEqual(self.native.calls, 2)
        self.assertEqual(len(self.native.process.stdin.getvalue().splitlines()), 2)
        self.assertEqual(len(self.native.log.getvalue().splitlines()), 2)
        guard(full_hash=True)

    def test_deadline_expired_hit_and_any_deadline_rebinding_fail(self):
        contract, guard = self.admitted()
        callback, u = self.callbacks(contract, guard, lambda t, u: np.zeros_like(u))
        callback.original(self.fixture.x0, u)
        with mock.patch.object(admit.time, "monotonic", return_value=self.provider.deadline):
            with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "NATIVE_JOB_WALL_BUDGET"):
                callback.original(self.fixture.x0, u)
        self.provider.deadline += 1.
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "DEADLINE_CHANGED"):
            guard()

    def test_owner_provenance_command_and_process_receipt_binding(self):
        original = copy.deepcopy(self.provenance)
        for key, value in (("owner", "wrong"), ("sha256", "0"*64),
                           ("status", "PR82_VERIFIED_BINARY_HASH_REUSED")):
            self.provenance[key] = value
            with self.assertRaises(admit.NativeCacheAdmissionError):
                self.admitted()
            self.provenance.clear()
            self.provenance.update(original)
        self.native.command.append("--export-source")
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "EXACT_SINGLE_BINARY_COMMAND_REQUIRED"):
            self.admitted()
        self.native.command.pop()
        self.process_record["owner"] = "wrong"
        (self.output / "native_process.json").write_text(json.dumps(self.process_record))
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "PROCESS_RECEIPT_MISMATCH"):
            self.admitted()

    def test_binary_and_build_files_are_immutable_during_the_lease(self):
        _, guard = self.admitted()
        original = self.binary.read_bytes()
        st = self.binary.stat()
        self.binary.write_bytes(original.replace(b"STUB", b"FAKE"))
        import os
        os.utime(self.binary, ns=(st.st_atime_ns, st.st_mtime_ns))
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "IMMUTABLE_FILE_CHANGED"):
            guard()
        self.binary.write_bytes(original)
        # A new admission is allowed only after all original identities verify.
        _, guard = self.admitted()
        replacement = self.build / "replacement"
        replacement.write_bytes(original)
        replacement.chmod(0o755)
        replacement.replace(self.binary)
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "IMMUTABLE_FILE_CHANGED"):
            guard()
        _, guard = self.admitted()
        (self.build / "build_exit.txt").write_text("exit_code=1\n")
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "IMMUTABLE_FILE_CHANGED"):
            guard()

    def test_context_mutation_contract_mutation_and_config_drift_fail(self):
        contract, guard = self.admitted()
        self.fixture_identity["fixture"]["q"][0] += 1.
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "IMMUTABLE_CONTEXT_CHANGED"):
            guard()
        self.fixture_identity = {"fixture_sha256": self.fixture.digest, "fixture": asdict(self.fixture)}
        contract, guard = self.admitted()
        self.source_identity["runtime_files"]["native_cache_contract.py"]["sha256"] = "0"*64
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "IMMUTABLE_CONTEXT_CHANGED"):
            guard()
        self.source_identity["runtime_files"]["native_cache_contract.py"] = record(HERE / "native_cache_contract.py")
        contract, guard = self.admitted()
        contract["budget_policy"] = "forged"
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "IMMUTABLE_CONTEXT_CHANGED"):
            guard()
        _, guard = self.admitted()
        self.native.max_calls += 1
        with self.assertRaisesRegex(admit.NativeCacheAdmissionError, "COMMAND_OR_CALL_CAP_CHANGED"):
            guard()

    def test_failed_and_nonfinite_values_never_enter_existing_exact_cache(self):
        contract, guard = self.admitted()
        def failed(t, u):
            raise ProviderFailure("STUB_EXPECTED_FAILURE")
        callback, u = self.callbacks(contract, guard, failed)
        for _ in range(2):
            with self.assertRaisesRegex(ProviderFailure, "STUB_EXPECTED_FAILURE"):
                callback.original(self.fixture.x0, u)
        self.assertEqual(len(callback._cache), 0)
        self.assertEqual(callback.counts["original_rhs_evaluations"], 2)
        callback, u = self.callbacks(contract, guard, lambda t, u: np.full_like(u, np.nan))
        for _ in range(2):
            with self.assertRaisesRegex(BASE.AdapterError, "ORIGINAL_RHS_RESULT_DOMAIN"):
                callback.original(self.fixture.x0, u)
        self.assertEqual(len(callback._cache), 0)
        self.assertEqual(self.native.calls, 0)

    def test_vectorized_default_needs_no_admission_exact_requires_one(self):
        cls = opt.make_callback_type(BASE, "vectorized")
        self.assertTrue(issubclass(cls, BASE.CellCallbacks))
        with self.assertRaisesRegex(opt.OptimizationError, "ADMISSION_REQUIRED"):
            opt.make_callback_type(BASE, "vectorized_exact")


if __name__ == "__main__":
    unittest.main(verbosity=2)
