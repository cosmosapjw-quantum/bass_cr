#!/usr/bin/env python3
"""Create-only C22C runs with threshold-segmented implicit integration.

This entry point uses new H1 excitation IVPs; it never reruns C21O, C22A, or C22B.  Freeze source before dispatch.  A completed
integration is an execution result; scientific acceptance is recorded separately.
"""
from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"

import argparse
from concurrent.futures import ProcessPoolExecutor, FIRST_COMPLETED, wait
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import multiprocessing as mp
from pathlib import Path
import platform
import re
import sys
import tempfile
import time
import traceback

import numpy as np
import scipy
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
REPO = RESEARCH.parent
RESOURCE_PATH = RESEARCH / "cr_c21o_hheli_z2_20261021" / "resource_control.py"
_spec = importlib.util.spec_from_file_location("c22c_resource_control", RESOURCE_PATH)
resource_control = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(resource_control)
_FACTORIES = {}
N_SAVED = 201
MAX_WORKERS = 2
SAVED_GRID_NAME = "eta_zero_geom1e-10_to_0.02_100_linear0.02_to_end_100"


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _json_default(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, default=_json_default).encode("utf8")


def atomic_create(path, writer):
    """Install one completed local file without replacing an existing name."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            writer(handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)  # atomic create; FileExistsError preserves target
    finally:
        Path(temporary).unlink(missing_ok=True)


def json_create(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False,
                      default=_json_default) + "\n").encode("utf8")
    atomic_create(path, lambda handle: handle.write(raw))


def npz_create(path, arrays):
    atomic_create(path, lambda handle: np.savez_compressed(handle, **arrays))


def source_identity():
    """Retain all frozen C22B dependencies; add separately identified C22C code/data."""
    old = json.loads((RESEARCH / "cr_c22b_compton_bath_20261022" / "evidence/SOURCE_FREEZE.json").read_text())
    paths = {REPO / row["path"] for row in old["files"]
             if row["path"] != "research/cr_c22b_compton_bath_20261022/run_pilot.py"}
    paths.update(HERE / name for name in ("model.py", "excitation.py", "run_pilot.py", "CONTRACT.json",
                 "sources/CCC_2S_1S.txt", "sources/CCC_2P_1S.txt"))
    vendor = RESEARCH / "cr_c21l_rei_pilot_20261021"
    for row in json.loads((vendor / "SOURCE_MANIFEST.json").read_text())["files"]:
        paths.add(vendor / "vendor/rei" / row["path"])
    records = [{"path": str(p.relative_to(REPO)), "size_bytes": p.stat().st_size,
                "sha256": sha256(p)} for p in sorted(paths)]
    payload = {"schema": "C22C_SOURCE_IDENTITY_V1", "files": records,
               "floating_point": "float64", "global_error_bound": None}
    payload["identity_sha256"] = hashlib.sha256(canonical(payload)).hexdigest()
    return payload


def default_cases():
    return json.loads((HERE / "inputs/NOMINAL_CASES.json").read_text())["cases"]


def read_cases(path):
    data = json.loads(Path(path).read_text()) if path else default_cases()
    cases = data["cases"] if isinstance(data, dict) else data
    if not isinstance(cases, list) or not cases:
        raise ValueError("CASES_MUST_BE_NONEMPTY_LIST")
    names = []
    for case in cases:
        name = case.get("name", "")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", name):
            raise ValueError("UNSAFE_CASE_NAME")
        names.append(name)
        for key in ("signed_sigma", "signed_pi_m", "signed_pi_r", "photon_scale", "temperature_K"):
            value = case.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("CASE_NONFINITE_OR_MISSING: " + name + ":" + key)
        if case["photon_scale"] < 0 or case["temperature_K"] <= 0:
            raise ValueError("CASE_NONPHYSICAL_PHOTON_SCALE_OR_T: " + name)
        ell = case.get("ellmax", 8)
        if isinstance(ell, bool) or not isinstance(ell, int) or ell < 2:
            raise ValueError("INVALID_ELLMAX: " + name)
    if len(set(names)) != len(names):
        raise ValueError("DUPLICATE_CASE_NAME")
    return cases


def discover_leases(explicit=None):
    """Bounded, read-only discovery; never delete, expire, or claim a lease."""
    cooperative = Path("/tmp/rei-bianchi-cooperative-leases")
    roots = {HERE, REPO, REPO.parent, Path("/tmp")}
    if cooperative.is_dir():
        roots.add(cooperative)
    directories = set(roots)
    for root in roots:
        for name in ("leases", ".leases", "resources", "state"):
            candidate = root / name
            if candidate.is_dir():
                directories.add(candidate)
    found = {Path(explicit).resolve()} if explicit else set()
    errors = []
    for directory in sorted(directories):
        try:
            for p in directory.iterdir():
                n = p.name.lower()
                if p.is_file() and p.suffix.lower() == ".json" and (
                        directory == cooperative or "lease" in n
                        or ("cpu" in n and any(t in n for t in ("owner", "alloc", "reserv")))):
                    found.add(p.resolve())
        except OSError as exc:
            errors.append({"directory": str(directory), "error": repr(exc)})
    if len(found) > 100:
        raise RuntimeError("LEASE_DISCOVERY_LIMIT_EXCEEDED")
    return sorted(found), {"directories": [str(p) for p in sorted(directories)],
                           "paths": [str(p) for p in sorted(found)], "errors": errors,
                           "scope": "known roots and immediate lease/resource/state subdirectories; not a host-wide scan"}


def lease_snapshot(eligible, explicit=None):
    paths, discovery = discover_leases(explicit)
    reserved, records = set(), []
    for path in paths:
        cpus, receipt = resource_control._lease_reservations(path, set(eligible))
        reserved.update(cpus)
        records.append(receipt)
    if discovery["errors"]:
        reserved.update(eligible)
    return reserved, {"discovery": discovery, "files": records,
                      "reserved_cpus": sorted(reserved), "modified": False,
                      "exclusive_reservation": False}


def worker_init(cpus, expected_source):
    if source_identity()["identity_sha256"] != expected_source:
        raise RuntimeError("WORKER_SOURCE_IDENTITY_MISMATCH")
    if hasattr(os, "sched_setaffinity"):
        index = (mp.current_process()._identity[-1] - 1) if mp.current_process()._identity else 0
        os.sched_setaffinity(0, {int(cpus[index % len(cpus)])})


class IntegrationFailure(RuntimeError):
    def __init__(self, message, arrays, segments):
        super().__init__(message)
        self.arrays, self.segments = arrays, segments


def endpoint_inset(model, boundary, toward, max_ulps=256):
    """Find a representable RHS time on the segment's actual energy branches.

    One eta ULP need not move E0*exp(-eta) across its threshold.  Compare every
    adopted photo-support threshold and the Li-I algorithm switch against the
    segment midpoint, advancing bounded eta ULPs until all strict sides agree.
    This changes the RHS evaluation point only, never the boundary state.
    """
    boundary, toward = float(boundary), float(toward)
    low, high = sorted((boundary, toward))
    midpoint = low + .5 * (high - low)
    if not low < midpoint < high:
        raise ValueError("THRESHOLD_INTERVAL_NO_STRICT_INTERIOR")
    thresholds = np.unique(np.r_[np.asarray(model.thresholds, dtype=float), 64.39])
    reference_energies = np.asarray(model.photon_energies(midpoint), dtype=float)
    reference_sides = np.sign(reference_energies[:, None] - thresholds[None, :])
    if (not np.all(np.isfinite(reference_energies)) or not np.all(np.isfinite(thresholds))
            or np.any(reference_sides == 0)):
        raise ValueError("THRESHOLD_REFERENCE_NOT_STRICT_OR_FINITE")
    candidate = boundary
    for steps in range(1, max_ulps + 1):
        candidate = float(np.nextafter(candidate, toward))
        if not low < candidate < high:
            raise ValueError("THRESHOLD_INSET_EXHAUSTED_INTERVAL")
        energies = np.asarray(model.photon_energies(candidate), dtype=float)
        actual_sides = np.sign(energies[:, None] - thresholds[None, :])
        if np.all(np.isfinite(energies)) and np.array_equal(actual_sides, reference_sides):
            return candidate, {"boundary_eta": boundary, "evaluation_eta": candidate,
                               "delta_eta": candidate - boundary, "ulp_steps": steps,
                               "max_ulps": max_ulps, "reference_eta": midpoint,
                               "thresholds_eV": thresholds.tolist(),
                               "evaluation_energies_eV": energies.tolist(),
                               "expected_sides": reference_sides.astype(int).tolist(),
                               "actual_sides": actual_sides.astype(int).tolist(),
                               "status": "PASS_ALL_ADOPTED_ENERGY_BRANCHES",
                               "state_mutation": "NONE"}
    raise ValueError("THRESHOLD_INSET_ULP_LIMIT_EXCEEDED")


def integrate_segmented(model, method, rtol, atol, log):
    end = float(model.eta_end)
    y0 = np.asarray(model.initial_state(), dtype=np.float64)
    if not (math.isfinite(end) and end > 0) or y0.ndim != 1 or not np.all(np.isfinite(y0)):
        raise ValueError("INVALID_INITIAL_STATE_OR_INTERVAL")
    raw_transitions = np.asarray(model.transition_times(), dtype=np.float64)
    if raw_transitions.ndim != 1 or not np.all(np.isfinite(raw_transitions)):
        raise ValueError("INVALID_TRANSITION_TIMES")
    breaks = sorted({0., end, *(float(x) for x in raw_transitions if 0. < x < end)})
    if end <= .02:
        raise ValueError("REGISTERED_SAVED_GRID_REQUIRES_ETA_END_GREATER_THAN_0.02")
    eta = np.r_[0., np.geomspace(1e-10, .02, 100), np.linspace(.02, end, 101)[1:]]
    if len(eta) != N_SAVED or not np.all(np.diff(eta) > 0):
        raise ValueError("INVALID_REGISTERED_SAVED_GRID")
    samples = np.full((len(y0), N_SAVED), np.nan, dtype=np.float64)
    samples[:, 0] = y0
    segment_records, accepted_t, accepted_y = [], [np.array([0.])], [y0[:, None].copy()]
    started = time.monotonic()
    for segment_index, (left, right) in enumerate(zip(breaks[:-1], breaks[1:])):
        # Cross sections jump at thresholds. Check actual energy arithmetic,
        # including the Li-I algorithm switch; a single eta ULP is insufficient.
        open_left, left_receipt = endpoint_inset(model, left, right)
        open_right, right_receipt = endpoint_inset(model, right, left)
        if open_left >= open_right:
            raise ValueError("THRESHOLD_INSETS_OVERLAP")
        def local_rhs(t, y):
            local_t = open_left if t < open_left else open_right if t > open_right else t
            return model.solver_rhs(float(local_t), y)
        log.write(f"{utc()} segment={segment_index} eta=[{left:.17g},{right:.17g}]\n")
        log.flush()
        try:
            sol = solve_ivp(local_rhs, (left, right), model.project(y0), method=method,
                            rtol=rtol, atol=atol, dense_output=True)
        except Exception as exc:
            arrays = {"eta": np.concatenate(accepted_t), "Y": np.concatenate(accepted_y, axis=1),
                      "failing_segment_start": np.array(left), "failing_segment_initial_state": y0}
            raise IntegrationFailure("SOLVER_EXCEPTION: " + repr(exc), arrays, segment_records) from exc
        accepted_t.append(sol.t[1:].copy())
        accepted_y.append(model.lift(sol.y[:, 1:]))
        record = {"index": segment_index, "eta_start": left, "eta_end": right,
                  "success": bool(sol.success), "message": str(sol.message),
                  "nfev": int(sol.nfev), "njev": int(sol.njev), "nlu": int(sol.nlu),
                  "accepted_mesh_points": int(sol.t.size),
                  "endpoint_branch_checks": {"left": left_receipt, "right": right_receipt}}
        segment_records.append(record)
        if not sol.success or not np.all(np.isfinite(sol.y)):
            raise IntegrationFailure("SEGMENT_INTEGRATION_FAILED: " + str(sol.message),
                                     {"eta": np.concatenate(accepted_t),
                                      "Y": np.concatenate(accepted_y, axis=1)}, segment_records)
        selection = (eta > left) & (eta <= right)
        samples[:, selection] = model.lift(sol.sol(eta[selection]))
        y0 = model.lift(sol.y[:, -1])
        log.write(f"{utc()} segment_complete={segment_index} nfev={sol.nfev}\n")
        log.flush()
    if not np.all(np.isfinite(samples)):
        raise IntegrationFailure("NONFINITE_OR_MISSING_SAVED_SAMPLE",
                                 {"eta": eta, "Y": samples}, segment_records)
    try:
        history = {key: np.asarray(value) for key, value in model.summarize(eta, samples).items()}
        history.update(eta=eta, Y=samples,
                       accepted_eta=np.concatenate(accepted_t),
                       accepted_Y=np.concatenate(accepted_y, axis=1))
        for key, value in history.items():
            if value.dtype.kind == "O":
                raise ValueError("OBJECT_ARRAY_FORBIDDEN: " + key)
            if key == "cancellation_fraction":
                defined = history.get("cancellation_fraction_defined")
                if (defined is None or defined.dtype.kind != "b" or defined.shape != value.shape
                        or np.any(np.isinf(value)) or not np.array_equal(np.isfinite(value), defined)
                        or not np.all(np.isnan(value[~defined]))):
                    raise ValueError("INVALID_UNDEFINED_CANCELLATION_MASK")
                continue
            if value.dtype.kind in "fci" and not np.all(np.isfinite(value)):
                raise ValueError("NONFINITE_SUMMARY_ARRAY: " + key)
    except Exception as exc:
        raise IntegrationFailure("POSTINTEGRATION_SUMMARY_EXCEPTION: " + repr(exc),
                                 {"eta": eta, "Y": samples, "accepted_eta": np.concatenate(accepted_t),
                                  "accepted_Y": np.concatenate(accepted_y, axis=1)}, segment_records) from exc
    return history, {"segments": segment_records, "transition_boundaries_eta": breaks,
                     "saved_times": N_SAVED, "saved_grid_name": SAVED_GRID_NAME,
                     "accepted_mesh_points": sum(len(t) for t in accepted_t),
                     "accepted_mesh_scope": "solver-returned accepted mesh; not a continuous-extremum or error bound",
                     "state_size": len(y0), "solver_state_size": model.solver_size, "method": method,
                     "rtol": rtol, "atol": atol, "wall_seconds": time.monotonic() - started,
                     "nfev": sum(r["nfev"] for r in segment_records),
                     "njev": sum(r["njev"] for r in segment_records),
                     "nlu": sum(r["nlu"] for r in segment_records),
                     "undefined_0_over_0": "cancellation_fraction is NaN exactly where cancellation_fraction_defined is false; infinity forbidden",
                     "clipping": "NONE", "global_error_bound": None}


def run_case(case, directory, source_sha, input_sha, method, rtol, atol):
    output = Path(directory) / "cases" / case["name"]
    output.mkdir(exist_ok=False)
    json_create(output / "STARTED.json", {"utc": utc(), "pid": os.getpid(),
                "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
                "case": case, "source_identity_sha256": source_sha, "input_sha256": input_sha})
    try:
        with (output / "RUN.log").open("x", encoding="utf8") as log:
            if source_identity()["identity_sha256"] != source_sha:
                raise RuntimeError("PRE_CASE_SOURCE_IDENTITY_MISMATCH")
            from model import ThermochemicalFactory
            ell = int(case.get("ellmax", 8))
            if ell not in _FACTORIES:
                _FACTORIES[ell] = ThermochemicalFactory(ellmax=ell)
            model = _FACTORIES[ell].build(case)
            metadata = model.metadata()
            json_create(output / "MODEL.json", metadata)
            history, receipt = integrate_segmented(model, method, rtol, atol, log)
            npz_create(output / "history.npz", history)
            if source_identity()["identity_sha256"] != source_sha:
                raise RuntimeError("POST_CASE_SOURCE_IDENTITY_MISMATCH_RAW_PRESERVED")
            diagnostics = {}
            for name in ("energy_relative_residual", "nucleus_max_relative_residual",
                         "charge_photon_relative_residual", "photon_number_relative_residual"):
                if name in history:
                    diagnostics[name + "_saved_max_abs"] = float(np.max(np.abs(history[name])))
            for name in ("temperature_K", "n_e_cm3", "UV_photons_per_H", "atomic_scaled"):
                if name in history:
                    diagnostics[name + "_saved_min"] = float(np.min(history[name]))
            receipt.update({"case": case, "status": "COMPLETED_SCOPED", "utc_completed": utc(),
                            "source_identity_sha256": source_sha, "input_sha256": input_sha,
                            "history_sha256": sha256(output / "history.npz"),
                            "history_bytes": (output / "history.npz").stat().st_size,
                            "model_metadata_sha256": sha256(output / "MODEL.json"),
                            "diagnostics": diagnostics,
                            "scientific_acceptance": "PENDING_SCOPE_MATCHED_REVIEW"})
            json_create(output / "RECEIPT.json", receipt)
            json_create(output / "COMPLETE.json", {"status": "COMPLETED_SCOPED",
                        "source_identity_sha256": source_sha, "input_sha256": input_sha,
                        "history_sha256": receipt["history_sha256"],
                        "receipt_sha256": sha256(output / "RECEIPT.json"), "global_error_bound": None})
            return {"name": case["name"], "status": "COMPLETED_SCOPED",
                    "wall_seconds": receipt["wall_seconds"], "diagnostics": diagnostics}
    except Exception as exc:
        if isinstance(exc, IntegrationFailure):
            npz_create(output / "FAILED_ACCEPTED_SOLUTION.npz", exc.arrays)
            json_create(output / "FAILED_SEGMENTS.json", exc.segments)
        failure = {"name": case["name"], "status": "FAILED_PRESERVED", "utc": utc(),
                   "exception": repr(exc), "traceback": traceback.format_exc(),
                   "source_identity_sha256": source_sha, "input_sha256": input_sha,
                   "failure_class": ("implementation_postprocessing" if str(exc).startswith("POSTINTEGRATION_SUMMARY")
                                     else "numerical_or_RHS_execution" if isinstance(exc, IntegrationFailure)
                                     else "implementation_or_input_dependency"),
                   "causal_diagnosis": "UNRESOLVED; inspect original exception and preserved arrays",
                   "global_error_bound": None}
        json_create(output / "FAILURE.json", failure)
        return failure


def execute(args):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,119}", args.run_id):
        raise ValueError("UNSAFE_RUN_ID")
    if not (math.isfinite(args.rtol) and math.isfinite(args.atol) and args.rtol > 0 and args.atol > 0):
        raise ValueError("TOLERANCES_MUST_BE_POSITIVE_FINITE")
    if not 1 <= args.workers <= MAX_WORKERS:
        raise ValueError("WORKERS_MUST_BE_1_OR_2")
    source = source_identity()
    frozen = json.loads(Path(args.source_freeze).read_text())
    if frozen != source:
        raise RuntimeError("SOURCE_FREEZE_MISMATCH")
    cases = read_cases(args.cases)
    inputs = {"schema": "C22C_INPUT_V1", "run_id": args.run_id, "cases": cases,
              "method": args.method, "rtol": args.rtol, "atol": args.atol,
              "saved_times": N_SAVED, "saved_grid_name": SAVED_GRID_NAME, "global_error_bound": None,
              "input_file_sha256": sha256(args.cases) if args.cases else None}
    input_sha = hashlib.sha256(canonical(inputs)).hexdigest()
    output = HERE / "runs" / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases").mkdir()
    json_create(output / "INPUT.json", inputs)
    json_create(output / "SOURCE_IDENTITY.json", source)
    json_create(output / "RUNTIME.json", {"utc": utc(), "python": sys.version,
                "numpy": np.__version__, "scipy": scipy.__version__, "host": platform.node(),
                "command": sys.argv, "input_sha256": input_sha,
                "source_identity_sha256": source["identity_sha256"],
                "thread_environment": {k: os.environ[k] for k in resource_control.THREAD_ENV}})
    eligible = set(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else set()
    reserved, leases = lease_snapshot(eligible, args.lease)
    workers, budget = resource_control.choose_workers(
        len(cases), requested=args.workers, per_worker_mib=512, coordinator_mib=768,
        protected_cpus=sorted({55} | reserved), lease_path=args.lease)
    resource = {"admission": budget, "lease_observation": leases, "run_worker_cap": MAX_WORKERS,
                "CPU55_protected": True, "coordinator_distinct_from_workers": True,
                "exclusive_cpu_reservation": False}
    json_create(output / "RESOURCE.json", resource)
    if workers == 0:
        summary = {"status": "HELD_FOR_RESOURCES", "not_started": [c["name"] for c in cases],
                   "source_identity_sha256": source["identity_sha256"], "new_ODE": 0,
                   "global_error_bound": None}
        json_create(output / "SUMMARY.json", summary)
        print(json.dumps(summary), flush=True)
        return 3
    initial_affinity = set(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None
    if initial_affinity is not None:
        os.sched_setaffinity(0, {budget["coordinator_cpu"]})
    pending, active, results, dispatches = list(cases), {}, [], []
    idle_since = None
    try:
        with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("spawn"),
                                 initializer=worker_init,
                                 initargs=(budget["selected_worker_cpus"], source["identity_sha256"])) as pool:
            while pending or active:
                if pending and len(active) < workers:
                    observed = resource_control.observe_resources()
                    dynamic_reserved, dynamic_leases = lease_snapshot(eligible, args.lease)
                    allowed, decision = resource_control.dispatch_allowed(observed, len(active), budget)
                    if dynamic_reserved & (set(budget["selected_worker_cpus"]) | {budget["coordinator_cpu"]}):
                        allowed = False
                        decision["reasons"].append("CURRENT_LEASE_INTERSECTS_ADMITTED_POOL")
                    decision.update(utc=utc(), allowed=allowed, lease_observation=dynamic_leases)
                    dispatches.append(decision)
                    if allowed:
                        idle_since = None
                        case = pending.pop(0)
                        future = pool.submit(run_case, case, str(output), source["identity_sha256"],
                                             input_sha, args.method, args.rtol, args.atol)
                        active[future] = case["name"]
                    elif not active:
                        idle_since = time.monotonic() if idle_since is None else idle_since
                        if time.monotonic() - idle_since >= 30.:
                            break
                        time.sleep(.2)
                if active:
                    done, _ = wait(active, timeout=.5, return_when=FIRST_COMPLETED)
                    for future in done:
                        name = active.pop(future)
                        try:
                            result = future.result()
                        except Exception as exc:
                            result = {"name": name, "status": "WORKER_PROCESS_FAILED",
                                      "exception": repr(exc), "traceback": traceback.format_exc()}
                        results.append(result)
                        print(json.dumps(result, allow_nan=False), flush=True)
    finally:
        if initial_affinity is not None:
            os.sched_setaffinity(0, initial_affinity)
    complete = not pending and len(results) == len(cases) and all(
        row["status"] == "COMPLETED_SCOPED" for row in results)
    json_create(output / "DISPATCH.json", dispatches)
    summary = {"schema": "C22C_EXECUTION_SUMMARY_V1",
               "status": "COMPLETE_SCOPED" if complete else "PARTIAL_PRESERVED",
               "results": results, "not_started": [c["name"] for c in pending],
               "worker_count": workers, "source_identity_sha256": source["identity_sha256"],
               "input_sha256": input_sha, "scientific_acceptance": "PENDING_SCOPE_MATCHED_REVIEW",
               "old_C21O_ODE_runs": 0, "old_C22A_ODE_runs": 0, "old_C22B_ODE_runs": 0, "global_error_bound": None}
    json_create(output / "SUMMARY.json", summary)
    print(json.dumps(summary, allow_nan=False), flush=True)
    return 0 if complete else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="new create-only runs/<id> directory")
    parser.add_argument("--cases", type=Path)
    parser.add_argument("--method", choices=("BDF", "Radau"), default="BDF")
    parser.add_argument("--rtol", type=float, default=3e-11)
    parser.add_argument("--atol", type=float, default=3e-13)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--lease", type=Path, help="additional explicit read-only CPU lease")
    parser.add_argument("--source-freeze", type=Path, help="previously created source manifest; required for a run")
    parser.add_argument("--freeze-source", type=Path, help="create only a source manifest and exit; ODE0")
    args = parser.parse_args(argv)
    if args.freeze_source is not None:
        if args.run_id:
            parser.error("--freeze-source and --run-id are separate actions")
        source = source_identity()
        json_create(args.freeze_source, source)
        print(json.dumps({"source_manifest": str(args.freeze_source),
                          "identity_sha256": source["identity_sha256"], "new_ODE": 0}), flush=True)
        return 0
    if not args.run_id or not args.source_freeze:
        parser.error("execution requires --run-id and --source-freeze")
    return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())
