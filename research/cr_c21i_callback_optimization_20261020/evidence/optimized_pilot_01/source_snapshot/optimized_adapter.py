"""Opt-in C21I callback economy around the unchanged, pinned C21H driver.

The vectorized path assembles the *same* reduced Jacobian, preserving each
three-species sum and the original finite-difference nodes.  The exact path
adds a cell-owned, bounded cache of successful original RHS values.  It is
admitted only for a declared deterministic provider; successful value reuse
does not suppress domain, live-provider or one-job deadline checks.
"""
from __future__ import annotations

from collections import OrderedDict
import copy
from dataclasses import asdict, fields
import hashlib
import json
import math
from pathlib import Path
import struct
import time
from types import ModuleType
import uuid

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_C21H = HERE.parent / "cr_c21h_vigilode_bridge_20261019"
DEFAULT_C21G = HERE.parent / "cr_c21g_reference_refinement_20261019"
C21H_MANIFEST_SHA256 = "7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb"
C21G_MANIFEST_SHA256 = "7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed"
OPTIMIZATIONS = ("baseline", "vectorized", "vectorized_exact")
CACHE_CAPACITY = 16


class OptimizationError(RuntimeError):
    pass


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _verified_files(root, manifest_hash, field):
    root = Path(root).resolve()
    raw = (root / "EXECUTION_MANIFEST.json").read_bytes()
    if _digest(raw) != manifest_hash:
        raise OptimizationError("FROZEN_EXECUTION_MANIFEST_MISMATCH")
    manifest = json.loads(raw)
    payload = {}
    for name, record in manifest[field].items():
        rel = Path(name)
        if rel.is_absolute() or ".." in rel.parts:
            raise OptimizationError("FROZEN_SOURCE_RELATIVE_PATH")
        data = (root / rel).read_bytes()
        if {"bytes": len(data), "sha256": _digest(data)} != record:
            raise OptimizationError("FROZEN_RUNTIME_SOURCE_MISMATCH " + name)
        payload[name] = data
    return manifest, payload


def load_frozen_adapter(c21h_dir=DEFAULT_C21H):
    """Verify all eight frozen runtime files once, then load verified bytes.

    The returned module is private to its caller.  Rebinding CellCallbacks
    cannot change a public C21H import or the original source file.
    """
    manifest, payload = _verified_files(c21h_dir, C21H_MANIFEST_SHA256,
                                        "runtime_files")
    if len(payload) != 8:
        raise OptimizationError("C21H_EIGHT_RUNTIME_FILES_REQUIRED")
    path = Path(c21h_dir).resolve() / "optical_adapter.py"
    module = ModuleType("_c21i_frozen_c21h_" + uuid.uuid4().hex)
    module.__file__ = str(path)
    exec(compile(payload["optical_adapter.py"], str(path), "exec"), module.__dict__)
    module.c21i_frozen_identity = {
        "manifest_sha256": C21H_MANIFEST_SHA256,
        "runtime_files": copy.deepcopy(manifest["runtime_files"])}
    return module


def source_snapshot(source_dir, c21g_dir=DEFAULT_C21G):
    """Use the existing C21G authority for all ten inherited source files."""
    raw = (Path(c21g_dir) / "EXECUTION_MANIFEST.json").read_bytes()
    if _digest(raw) != C21G_MANIFEST_SHA256:
        raise OptimizationError("C21G_MANIFEST_MISMATCH")
    manifest = json.loads(raw)
    records = manifest["c21f_runtime_files"]
    for rel, expected in records.items():
        p = Path(rel)
        if p.is_absolute() or ".." in p.parts:
            raise OptimizationError("C21G_SOURCE_RELATIVE_PATH")
        data = (Path(source_dir) / p).read_bytes()
        if {"bytes": len(data), "sha256": _digest(data)} != expected:
            raise OptimizationError("C21G_SOURCE_MISMATCH " + rel)
    return {"manifest_sha256": C21G_MANIFEST_SHA256,
            "runtime_files": copy.deepcopy(records)}


def _freeze_fixture(fixture):
    """Freeze JSON-list inputs as tuples before constructing the RHS closure."""
    values = {field.name: getattr(fixture, field.name) for field in fields(fixture)}
    for name in ("gas0", "q", "birth", "amounts"):
        # Preserve scalar encodings (including integer-valued JSON fields)
        # while taking ownership of the formerly mutable container.
        values[name] = tuple(values[name])
    frozen = type(fixture)(**values).validate()
    if frozen.digest != fixture.digest:
        raise OptimizationError("FIXTURE_FREEZE_CHANGED_IDENTITY")
    return frozen


def _validated_contract(contract):
    if (not isinstance(contract, dict)
            or contract.get("schema") != "C21I_DETERMINISTIC_PROVIDER_ADMISSION_V1"
            or contract.get("deterministic_successful_rhs") is not True
            or not isinstance(contract.get("provider_identity"), dict)
            or not contract["provider_identity"]
            or not isinstance(contract.get("provider_kind"), str)
            or not contract["provider_kind"]
            or not isinstance(contract.get("admitted_by"), str)
            or not contract["admitted_by"]):
        raise OptimizationError("EXACT_CACHE_DETERMINISTIC_PROVIDER_ADMISSION_REQUIRED")
    # Round-trip establishes an owned immutable serialization, not purity proof.
    return json.loads(_canonical(contract))


def make_callback_type(base_module, optimization="vectorized", *,
                       cache_contract=None, cache_guard=None):
    """Bind callbacks in a caller-owned original module.

    Direct users of the exact mode must supply their concrete deterministic
    provider admission and any live guard.  A .kind string alone is insufficient.
    Cache contents belong to one instance; changed closure/cell/fixture uses a
    new instance.  This factory does not silently cache generic callbacks.
    """
    if optimization not in OPTIMIZATIONS:
        raise OptimizationError("UNKNOWN_CALLBACK_OPTIMIZATION")
    exact = optimization == "vectorized_exact"
    admission = _validated_contract(cache_contract) if exact else None
    original_type = base_module.CellCallbacks

    class OptimizedCellCallbacks(original_type):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.scales = self.scales.copy()
            self.dynamic = self.dynamic.copy()
            self.active = self.active.copy()
            for array in (self.scales, self.dynamic, self.active):
                array.setflags(write=False)
            expected = np.array([j for j in range(self.m + 19)
                                 if not (self.f.Y == 0 and j in (self.m+1, self.m+2))])
            if not np.array_equal(self.dynamic, expected):
                raise OptimizationError("CANONICAL_DYNAMIC_ORDER_REQUIRED")
            self._row = np.full(self.m+19, -1, dtype=int)
            self._row[self.dynamic] = np.arange(self.n)
            self._matrix = None if optimization == "baseline" else np.zeros((self.n, self.n))
            self._cache = OrderedDict()
            self._ownership = (self.fun, self.f, self.ref, self.scales, self.dynamic,
                               self.active, struct.pack("<dd", self.lo, self.hi))
            context = {"admission": admission, "fixture": asdict(self.f),
                       "cell_bits": struct.pack("<dd", self.lo, self.hi).hex(),
                       "scales_bits": self.scales.astype("<f8").tobytes().hex(),
                       "dynamic": self.dynamic.tolist(),
                       "reference_sha256": base_module.REFERENCE_SHA256}
            self.cache_scope_sha256 = _digest(_canonical(context))
            self.counts.update({key: 0 for key in (
                "original_rhs_requests", "original_rhs_cache_hits",
                "original_rhs_cache_misses", "original_rhs_cache_evictions",
                "original_rhs_result_copies", "rhs_cache_payload_bytes",
                "rhs_cache_peak_entries", "rhs_cache_key_ns", "rhs_cache_hit_ns",
                "original_rhs_execution_ns", "jacobian_return_allocations",
                "avoided_full_matrix_allocations")})
            self.counts["jacobian_scratch_allocations"] = int(self._matrix is not None)
            self.counts["jacobian_scratch_bytes"] = 0 if self._matrix is None else self._matrix.nbytes
            self.counts["rhs_cache_capacity"] = CACHE_CAPACITY if exact else 0

        def _guard(self):
            if cache_guard is not None:
                cache_guard()
            owned = self._ownership
            if (self.fun is not owned[0] or self.f is not owned[1]
                    or self.ref is not owned[2] or self.scales is not owned[3]
                    or self.dynamic is not owned[4] or self.active is not owned[5]
                    or struct.pack("<dd", self.lo, self.hi) != owned[6]
                    or any(a.flags.writeable for a in (self.scales, self.dynamic, self.active))):
                raise OptimizationError("CALLBACK_FROZEN_SCOPE_CHANGED")

        def physical(self, t, z):
            value = super().physical(t, z)
            self._guard()
            return value

        def original(self, t, u):
            self._guard()
            self.counts["original_rhs_requests"] += 1
            key = None
            if exact:
                started = time.perf_counter_ns()
                key = (struct.pack("<d", float(t)),
                       np.ascontiguousarray(u, dtype="<f8").tobytes())
                self.counts["rhs_cache_key_ns"] += time.perf_counter_ns()-started
                started = time.perf_counter_ns()
                cached = self._cache.get(key)
                if cached is not None:
                    result = cached.copy()
                    self.counts["original_rhs_result_copies"] += 1
                    self.counts["rhs_cache_hit_ns"] += time.perf_counter_ns()-started
                    self._guard()
                    self._cache.move_to_end(key)
                    self.counts["original_rhs_cache_hits"] += 1
                    return result
                self.counts["original_rhs_cache_misses"] += 1
            started = time.perf_counter_ns()
            try:
                result = super().original(t, u)
            finally:
                self.counts["original_rhs_execution_ns"] += time.perf_counter_ns()-started
            if exact:
                # super() has already enforced the finite result/shape contract.
                cached = result.copy()
                cached.setflags(write=False)
                result = result.copy()
                self.counts["original_rhs_result_copies"] += 2
                # A value finishing after the one-job deadline is a failure;
                # it must not become a successful reusable cache entry.
                self._guard()
                self._cache[key] = cached
                if len(self._cache) > CACHE_CAPACITY:
                    self._cache.popitem(last=False)
                    self.counts["original_rhs_cache_evictions"] += 1
                self.counts["rhs_cache_peak_entries"] = max(
                    self.counts["rhs_cache_peak_entries"], len(self._cache))
                self.counts["rhs_cache_payload_bytes"] = len(self._cache)*(8+16*self.n)
                return result
            self._guard()
            return result

        def rhs(self, t, z):
            result = super().rhs(t, z)
            self._guard()
            return result

        def partial_t(self, t, z):
            result = super().partial_t(t, z)
            self._guard()
            return result

        def jacobian(self, t, z):
            if optimization == "baseline":
                result = super().jacobian(t, z)
                self._guard()
                return result
            from event_coupler import H, BIND_EV, alpha, DomainError
            from run_experiment import opacity
            self.counts["jacobian_requests"] += 1
            u = self.physical(t, z)
            full = self.full(u)
            base = self.original(t, u)
            reduced = self._matrix
            reduced.fill(0.)  # Every inactive and passive column is reset.
            xx = min(max(t, self.left), self.right)
            energy, k = opacity(self.f, xx)
            pop, _ = self.ref.reconstruct_population(self.f.amounts, full[:self.m], self.active)
            rates = pop[:, None]*k*alpha(full[self.m:self.m+4], self.f.Y)[None, :]
            species = -rates
            # Axis 1 is the same contiguous length-three reduction as the
            # original per-cohort np.sum.  There is no cross-cohort reduction.
            heat = np.sum(species*(energy[:, None]-np.asarray(BIND_EV)[None, :]), axis=1)
            hubble = H(xx)
            reduced[self._row[self.m], :self.m] = species[:, 0]/hubble
            if self.f.Y == 0:
                if np.any(species[:, 1:] != 0):
                    raise DomainError("HE_EVENTS_WITHOUT_HE")
            else:
                reduced[self._row[self.m+1], :self.m] = ((species[:, 1]-species[:, 2])/self.f.Y)/hubble
                reduced[self._row[self.m+2], :self.m] = (species[:, 2]/self.f.Y)/hubble
            reduced[self._row[self.m+3], :self.m] = heat/hubble
            reduced[self._row[self.m+18], :self.m] = heat/hubble
            for channel in range(3):
                reduced[self._row[self.m+4+channel], :self.m] = species[:, channel]/hubble
            reduced[self._row[self.m+16], :self.m] = -pop*energy
            for j, full_index in enumerate(self.dynamic):
                if not self.m <= full_index < self.m+4:
                    continue
                first, second, kind = self.gas_nodes(u, j)
                offsets = (float(first[j]-u[j]), float(second[j]-u[j]))
                w = base_module.derivative_weights(offsets)
                reduced[:, j] = (w[1]*(self.original(t, first)-base)
                                 + w[2]*(self.original(t, second)-base))
                self.counts["gas_fd_columns"] += 1
                self.counts["gas_fd_one_sided_columns"] += int(kind == "one_sided")
                self.fd_nodes.append({"kind": "gas", "time": t, "full_index": int(full_index),
                                      "offsets": list(offsets), "stencil": kind})
            self.counts["analytic_tau_columns"] += self.m
            self.counts["exact_passive_columns"] += 15
            # Preserve multiplication-before-division and never expose scratch.
            np.multiply(reduced, self.scales[None, :], out=reduced)
            np.divide(reduced, self.scales[:, None], out=reduced)
            if not np.isfinite(reduced).all():
                raise base_module.AdapterError("JACOBIAN_NONFINITE")
            self.counts["avoided_full_matrix_allocations"] += 1
            self.counts["jacobian_return_allocations"] += 1
            result = reduced.copy()
            self._guard()
            return result

    OptimizedCellCallbacks.__name__ = "C21I_" + optimization + "_CellCallbacks"
    return OptimizedCellCallbacks


def run_optimized_reference(fixture, provider, source_dir, binary, out, scale_contract,
                            rtol=2e-11, alpha=2e-14, max_step_divisor=8.,
                            method="vigilode-rodas5p", fd_relative=None,
                            time_fd_fraction=1e-4, max_evaluations=200000, wall_s=300.,
                            *, optimization="vectorized", cache_contract=None,
                            cache_guard=None, c21h_dir=DEFAULT_C21H, c21g_dir=DEFAULT_C21G):
    """Execute the original C21H event driver with a private callback binding.

    Native provider admissions are supplied by the source/binary-bound runner.
    This function automatically admits only the exact pinned stateless
    ManufacturedMicro/ZeroMicro classes with an empty instance configuration.
    """
    if optimization not in OPTIMIZATIONS:
        raise OptimizationError("UNKNOWN_CALLBACK_OPTIMIZATION")
    if not math.isfinite(wall_s) or wall_s <= 0:
        raise OptimizationError("POSITIVE_FINITE_JOB_WALL_REQUIRED")
    # The caller supplies the remaining one-job budget.  Frozen source and
    # fixture setup consume that budget instead of creating a later epoch.
    deadline = time.monotonic() + wall_s
    base = load_frozen_adapter(c21h_dir)
    sources = source_snapshot(source_dir, c21g_dir)
    base.private_reference(source_dir)  # Establish the pinned module namespace.
    from event_coupler import ManufacturedMicro, ZeroMicro
    from run_experiment import Fixture
    if type(fixture) is not Fixture:
        raise OptimizationError("PINNED_FIXTURE_TYPE_REQUIRED")
    frozen = _freeze_fixture(fixture)
    fixture_digest = frozen.digest
    controls = copy.deepcopy(scale_contract)
    if optimization == "vectorized_exact":
        if cache_contract is None and type(provider) in (ManufacturedMicro, ZeroMicro) and not vars(provider):
            cache_contract = {
                "schema": "C21I_DETERMINISTIC_PROVIDER_ADMISSION_V1",
                "deterministic_successful_rhs": True, "provider_kind": provider.kind,
                "provider_identity": {"class": type(provider).__name__, "configuration": {},
                    "source": sources["runtime_files"]["src/event_coupler.py"]},
                "admitted_by": "Pinned stateless original provider class and immutable fixture"}
        cache_contract = _validated_contract(cache_contract)
        if cache_contract["provider_kind"] != provider.kind:
            raise OptimizationError("CACHE_PROVIDER_KIND_MISMATCH")
    def live_guard():
        if time.monotonic() >= deadline:
            raise base.AdapterError("RUST_JOB_WALL_BUDGET")
        provider_deadline = getattr(provider, "deadline", None)
        if provider_deadline is not None and time.monotonic() >= provider_deadline:
            raise base.AdapterError("NATIVE_JOB_WALL_BUDGET")
        native = getattr(provider, "native", provider)
        if getattr(native, "closed", False):
            raise base.AdapterError("C21I_PROVIDER_CLOSED")
        process = getattr(native, "process", None)
        if process is not None and process.poll() is not None:
            raise base.AdapterError("C21I_PROVIDER_EXITED")
        if cache_guard is not None:
            cache_guard()

    base.CellCallbacks = make_callback_type(base, optimization,
                                             cache_contract=cache_contract, cache_guard=live_guard)
    try:
        live_guard()
        remaining = deadline-time.monotonic()
        if remaining <= 0:
            raise base.AdapterError("RUST_JOB_WALL_BUDGET")
        result = base.run_rust_reference(frozen, provider, source_dir, binary, out, controls,
            rtol, alpha, max_step_divisor, method, fd_relative, time_fd_fraction,
            max_evaluations, remaining)
        live_guard()
    finally:
        _verified_files(c21h_dir, C21H_MANIFEST_SHA256, "runtime_files")
        if source_snapshot(source_dir, c21g_dir) != sources or frozen.digest != fixture_digest:
            raise OptimizationError("OPTIMIZATION_SCOPE_CHANGED_DURING_JOB")
    live_guard()
    result["callback_optimization"] = {
        "mode": optimization, "c21h_identity": base.c21i_frozen_identity,
        "inherited_source_identity": sources, "fixture_sha256": fixture_digest,
        "exact_cache_admission": cache_contract if optimization == "vectorized_exact" else None,
        "cache_capacity_per_cell": CACHE_CAPACITY if optimization == "vectorized_exact" else 0,
        "error_norm_and_full_state": "UNCHANGED_C21H",
        "accumulation_order": "Original per-cohort three-species reduction; original row arithmetic and gas/time FD order",
        "allocation_counter_scope": "Explicit callback scratch/owned-result/cache payload only; not total Python/NumPy allocations",
        "timing_counter_scope": "Per-call instrumented RHS/key/hit wall-clock nanoseconds; not an isolated native or total-time decomposition"}
    result["solver_diagnostics"]["counter_note"] += (
        " C21I original_rhs_requests includes internal derivative requests; "
        "original_rhs_cache_hits are successful-value reuses; original_rhs_evaluations "
        "and reference rhs_evaluations count actual underlying calls, including failed attempts. "
        "Native counters remain provider-owned actual calls.")
    return result
