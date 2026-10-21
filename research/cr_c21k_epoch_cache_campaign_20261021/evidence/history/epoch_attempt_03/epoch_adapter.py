"""C21K: exact, cell-owned opacity reuse and ordered scalar hoisting.

The original C21F reference and C21I callback source bytes are compiled unchanged
in private modules. Their module-local import bindings supply cached versions of
run_experiment.opacity. Its miss kernel hoists only identical scalar
subexpressions, preserving their original multiplication order. The cheap H
function stays original in production. No public module is patched, no
optical/gas/ledger RHS is cached under an epoch-only key, and no native call is
skipped by this layer. The inherited optional full-state cache remains separate.
"""
from __future__ import annotations

import builtins
from collections import OrderedDict
from dataclasses import asdict, is_dataclass
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
from types import ModuleType
import uuid

import numpy as np

HERE = Path(__file__).resolve().parent
C21I = HERE.parent / "cr_c21i_callback_optimization_20261020"
C21H = HERE.parent / "cr_c21h_vigilode_bridge_20261019"
C21G = HERE.parent / "cr_c21g_reference_refinement_20261019"
I_MANIFEST_SHA256 = "f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec"
I_ADAPTER_SHA256 = "bb73bfa9bd865f60eefeed55dbd05df076a9856544345595beb914676105396e"
REFERENCE_SHA256 = "714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0"
CAPACITY = 16
OPTIMIZATIONS = ("vectorized", "vectorized_exact")


class EpochError(RuntimeError):
    pass


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _record(raw):
    return {"bytes": len(raw), "sha256": _digest(raw)}


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def _verified_i(unit):
    unit = Path(unit).resolve()
    raw = (unit / "EXECUTION_MANIFEST.json").read_bytes()
    if _digest(raw) != I_MANIFEST_SHA256:
        raise EpochError("PINNED_C21I_MANIFEST_REQUIRED")
    manifest = json.loads(raw)
    expected = {"run_optimized_pilot.py", "optimized_adapter.py", "native_cache_contract.py"}
    if set(manifest["runtime_files"]) != expected:
        raise EpochError("PINNED_C21I_RUNTIME_SET_REQUIRED")
    payload = {}
    for name, identity in manifest["runtime_files"].items():
        path = unit / name
        if path.is_symlink():
            raise EpochError("PINNED_C21I_SOURCE_SYMLINK")
        value = path.read_bytes()
        if _record(value) != identity:
            raise EpochError("PINNED_C21I_RUNTIME_CHANGED " + name)
        payload[name] = value
    if _digest(payload["optimized_adapter.py"]) != I_ADAPTER_SHA256:
        raise EpochError("PINNED_C21I_ADAPTER_REQUIRED")
    return payload


class EpochMemo:
    """Private job context; both LRU tables are emptied at every event cell.

    Cache keys preserve the exact binary64 argument supplied to the original
    functions, including signed zero. Fixture containers must already be frozen
    by C21I. Successful cached opacity arrays have immutable bytes backing; each
    consumer receives independent writable copies, matching the old ownership.
    """

    def __init__(self, enabled=True, capacity=CAPACITY, *, cache_hubble=True,
                 factor_opacity=False):
        if type(enabled) is not bool or type(capacity) is not int or not 1 <= capacity <= CAPACITY:
            raise EpochError("EPOCH_CACHE_CONFIGURATION")
        self.enabled, self.capacity = enabled, capacity
        self.cache_hubble, self.factor_opacity = cache_hubble, factor_opacity
        self._opacity, self._hubble = None, None
        self._cross, self._c_cm_s, self._coefficient = None, None, None
        self._fixture, self._fixture_bits, self._cell = None, None, None
        self._opacities, self._hubbles = OrderedDict(), OrderedDict()
        self.counts = {name: 0 for name in (
            "cells", "opacity_requests", "opacity_hits", "opacity_misses",
            "opacity_evictions", "opacity_peak_entries", "opacity_return_copies",
            "hubble_requests", "hubble_hits", "hubble_misses", "hubble_evictions",
            "hubble_peak_entries")}
        self.modules = {}
        self.cell_records = []
        self._cell_start = None

    def _finish_cell(self):
        if self._cell_start is not None:
            self.cell_records.append({
                "cell_bits": self._cell.hex(),
                "counts": {key: self.counts[key] - self._cell_start[key]
                           for key in self.counts if key not in
                           ("cells", "opacity_peak_entries", "hubble_peak_entries")}})
            self._cell_start = None

    def begin_cell(self, fixture, lo, hi):
        if not (is_dataclass(fixture) and fixture.__dataclass_params__.frozen
                and all(isinstance(getattr(fixture, key), tuple)
                        for key in ("gas0", "q", "birth", "amounts"))):
            raise EpochError("EPOCH_FIXTURE_OWNED_TUPLES_REQUIRED")
        if not (math.isfinite(lo) and math.isfinite(hi) and lo < hi):
            raise EpochError("EPOCH_CELL_DOMAIN")
        identity = _canonical(asdict(fixture))
        if self._fixture is not None and (fixture is not self._fixture or identity != self._fixture_bits):
            raise EpochError("EPOCH_FIXTURE_SCOPE_CHANGED")
        self._finish_cell()
        self._fixture, self._fixture_bits = fixture, identity
        if self.factor_opacity:
            if self._cross is None or self._c_cm_s is None:
                raise EpochError("EPOCH_ORIGINAL_KERNEL_NOT_BOUND")
            # Exactly the two multiplications at the left of the old scalar
            # expression; no reassociation, vector reduction or new rounding.
            self._coefficient = fixture.opacity_scale * self._c_cm_s * fixture.nh0
        self._cell = struct.pack("<dd", float(lo), float(hi))
        self._opacities.clear()
        self._hubbles.clear()
        self.counts["cells"] += 1
        self._cell_start = dict(self.counts)

    def _key(self, x):
        if self._cell is None:
            raise EpochError("EPOCH_CELL_NOT_BOUND")
        x = float(x)
        if not math.isfinite(x):
            raise EpochError("EPOCH_NONFINITE_ARGUMENT")
        return struct.pack("<d", x)

    def _check_functions(self):
        opacity_module = self.modules.get("run_experiment")
        hubble_module = self.modules.get("event_coupler")
        if opacity_module is not None and opacity_module[0].opacity is not self._opacity:
            raise EpochError("EPOCH_OPACITY_FUNCTION_CHANGED")
        if self.factor_opacity and opacity_module is not None:
            if (opacity_module[0].cross is not self._cross
                    or opacity_module[0].C_CM_S != self._c_cm_s):
                raise EpochError("EPOCH_ORIGINAL_KERNEL_CHANGED")
        if hubble_module is not None and hubble_module[0].H is not self._hubble:
            raise EpochError("EPOCH_HUBBLE_FUNCTION_CHANGED")

    def opacity(self, fixture, x):
        self._check_functions()
        key = self._key(x)
        if fixture is not self._fixture or self._opacity is None:
            raise EpochError("EPOCH_OPACITY_SCOPE_MISMATCH")
        self.counts["opacity_requests"] += 1
        if self.enabled and key in self._opacities:
            value = self._opacities[key]
            self._opacities.move_to_end(key)
            self.counts["opacity_hits"] += 1
        else:
            if self.factor_opacity:
                energy = np.asarray(fixture.q) * math.exp(-x)
                density = self._coefficient * math.exp(-3*x)
                value = (energy, np.array([[density*self._cross(j, float(e))
                                           for j in range(3)] for e in energy]))
            else:
                value = self._opacity(fixture, x)
            self.counts["opacity_misses"] += 1
            energy, opacity = (np.asarray(a, dtype=float) for a in value)
            m = len(fixture.q)
            if (energy.shape != (m,) or opacity.shape != (m, 3)
                    or not np.isfinite(energy).all() or not np.isfinite(opacity).all()):
                raise EpochError("EPOCH_OPACITY_RESULT_DOMAIN")
            original_owned = (energy, opacity)
            if self.enabled:
                value = tuple(np.frombuffer(a.tobytes(order="C"), dtype=a.dtype).reshape(a.shape)
                              for a in original_owned)
                self._opacities[key] = value
                if len(self._opacities) > self.capacity:
                    self._opacities.popitem(last=False)
                    self.counts["opacity_evictions"] += 1
                self.counts["opacity_peak_entries"] = max(
                    self.counts["opacity_peak_entries"], len(self._opacities))
            # The miss already owns freshly computed arrays. Return them,
            # retaining a separate immutable cache copy only when enabled.
            return original_owned
        self.counts["opacity_return_copies"] += 2
        return value[0].copy(), value[1].copy()

    def hubble(self, x):
        self._check_functions()
        key = self._key(x)
        if self._hubble is None:
            raise EpochError("EPOCH_HUBBLE_SCOPE_MISMATCH")
        self.counts["hubble_requests"] += 1
        if self.enabled and key in self._hubbles:
            value = self._hubbles[key]
            self._hubbles.move_to_end(key)
            self.counts["hubble_hits"] += 1
            return value
        value = self._hubble(x)
        self.counts["hubble_misses"] += 1
        if not math.isfinite(value):
            raise EpochError("EPOCH_HUBBLE_RESULT_DOMAIN")
        if self.enabled:
            self._hubbles[key] = value
            if len(self._hubbles) > self.capacity:
                self._hubbles.popitem(last=False)
                self.counts["hubble_evictions"] += 1
            self.counts["hubble_peak_entries"] = max(
                self.counts["hubble_peak_entries"], len(self._hubbles))
        return value

    def importer(self, name, globals=None, locals=None, fromlist=(), level=0):
        original = builtins.__import__(name, globals, locals, fromlist, level)
        if level or name not in ("run_experiment", "event_coupler"):
            return original
        if name not in self.modules:
            private = ModuleType("_c21k_" + name + "_" + uuid.uuid4().hex)
            private.__dict__.update(vars(original))
            if name == "run_experiment":
                self._opacity = original.opacity
                if self.factor_opacity:
                    self._cross, self._c_cm_s = original.cross, original.C_CM_S
                private.opacity = self.opacity
            else:
                self._hubble = original.H
                if self.cache_hubble:
                    private.H = self.hubble
            self.modules[name] = (original, private)
        real, private = self.modules[name]
        if real is not original:
            raise EpochError("EPOCH_SOURCE_MODULE_REPLACED")
        if name == "run_experiment" and original.opacity is not self._opacity:
            raise EpochError("EPOCH_OPACITY_FUNCTION_CHANGED")
        if name == "event_coupler" and original.H is not self._hubble:
            raise EpochError("EPOCH_HUBBLE_FUNCTION_CHANGED")
        return private

    def summary(self):
        self._check_functions()
        self._finish_cell()
        if self._fixture is not None and _canonical(asdict(self._fixture)) != self._fixture_bits:
            raise EpochError("EPOCH_FIXTURE_CHANGED_DURING_JOB")
        return {"schema": "C21K_EPOCH_MEMOIZATION_V1", "enabled": self.enabled,
                "capacity_per_function_per_cell": self.capacity if self.enabled else 0,
                "key": "Exact binary64 clamped epoch argument; signed zero preserved",
                "scope": "Private verified original source, frozen fixture, one event cell",
                "kernels": ["run_experiment.opacity"] + (["event_coupler.H"] if self.cache_hubble else []),
                "miss_operation": ("ORIGINAL_ORDER_SCALAR_COMMON_SUBEXPRESSIONS_HOISTED"
                                   if self.factor_opacity else "UNCHANGED_ORIGINAL_FUNCTION"),
                "hubble": "MEMOIZED" if self.cache_hubble else "UNCHANGED_ORIGINAL_FUNCTION",
                "full_rhs_and_native_response_cached_by_this_layer": False,
                "counts": dict(self.counts), "cells": list(self.cell_records)}


def _private(path, raw, scope):
    module = ModuleType("_c21k_" + Path(path).stem + "_" + uuid.uuid4().hex)
    module.__file__ = str(Path(path).resolve())
    module.__package__ = ""
    local_builtins = dict(vars(builtins))
    local_builtins["__import__"] = scope.importer
    module.__dict__["__builtins__"] = local_builtins
    exec(compile(raw, module.__file__, "exec", dont_inherit=True,
                 optimize=sys.flags.optimize), module.__dict__)
    return module


def prepare_optimizer(*, c21i_dir=C21I, enabled=True):
    """Return a fresh C21I optimizer and its non-shared epoch context."""
    payload = _verified_i(c21i_dir)
    scope = EpochMemo(enabled=enabled, cache_hubble=False, factor_opacity=True)
    optimizer = _private(Path(c21i_dir) / "optimized_adapter.py",
                         payload["optimized_adapter.py"], scope)
    load_base = optimizer.load_frozen_adapter
    make_callback = optimizer.make_callback_type

    def load_frozen_adapter(c21h_dir=C21H):
        base = load_base(c21h_dir)
        original_private = base.private_reference

        def private_reference(source_dir):
            # The original admission establishes and validates the public
            # namespace. Only the second, private execution gets new bindings.
            original_private(source_dir)
            path = Path(source_dir).resolve() / "src/reference_tau.py"
            raw = path.read_bytes()
            if _digest(raw) != REFERENCE_SHA256:
                raise EpochError("PINNED_REFERENCE_REQUIRED")
            return _private(path, raw, scope)

        base.private_reference = private_reference
        return base

    def make_callback_type(base, optimization="vectorized_exact", **kwargs):
        if optimization not in OPTIMIZATIONS:
            raise EpochError("EPOCH_OPTIMIZATION_MODE")
        inherited = make_callback(base, optimization, **kwargs)

        class EpochCell(inherited):
            def __init__(self, fun, fixture, lo, hi, *args, **kw):
                scope.begin_cell(fixture, lo, hi)
                super().__init__(fun, fixture, lo, hi, *args, **kw)

        return EpochCell

    optimizer.load_frozen_adapter = load_frozen_adapter
    optimizer.make_callback_type = make_callback_type
    return optimizer, scope


def run_optimized_reference(fixture, provider, source_dir, binary, out, scale_contract,
                            rtol=2e-11, alpha=2e-14, max_step_divisor=8.,
                            method="vigilode-rodas5p", fd_relative=None,
                            time_fd_fraction=1e-4, max_evaluations=200000, wall_s=300.,
                            *, optimization="vectorized_exact", cache_contract=None,
                            cache_guard=None, c21h_dir=C21H, c21g_dir=C21G,
                            c21i_dir=C21I):
    if optimization not in OPTIMIZATIONS:
        raise EpochError("EPOCH_OPTIMIZATION_MODE")
    optimizer, scope = prepare_optimizer(c21i_dir=c21i_dir)
    result = optimizer.run_optimized_reference(
        fixture, provider, source_dir, binary, out, scale_contract, rtol, alpha,
        max_step_divisor, method, fd_relative, time_fd_fraction, max_evaluations,
        wall_s, optimization=optimization, cache_contract=cache_contract,
        cache_guard=cache_guard, c21h_dir=c21h_dir, c21g_dir=c21g_dir)
    _verified_i(c21i_dir)
    result["epoch_optimization"] = scope.summary()
    result["c21k_source_composition"] = {
        "original_reference_sha256": REFERENCE_SHA256,
        "original_i_adapter_sha256": I_ADAPTER_SHA256,
        "original_source_bytes_modified": False,
        "public_sys_modules_rebound": False,
        "private_import_bindings": ["reference:run_experiment.opacity",
                                    "callbacks:run_experiment.opacity"],
        "hubble_binding": "UNCHANGED_ORIGINAL_FUNCTION",
        "global_error_bound": None}
    return result
