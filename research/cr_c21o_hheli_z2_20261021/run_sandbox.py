#!/usr/bin/env python3
"""Prepare, execute and resume only unstarted cases of the C21O model.

All science outputs are create-only. No SSH, process killing, foreign file
mutation, download or benchmarking occurs. The same entry point runs on an
observed sandbox or NCP host; resource admission is performed on that host.
"""
from __future__ import annotations
import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_key] = "1"
import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import platform
import sys
import time
import traceback

import numpy as np
import scipy
from coupled_model import CoupledFactory, RTOL, ATOL, N_OUTPUT, Z_START, Z_END
from atomic_network import AtomicNetwork21
from resource_control import choose_workers, observe_resources, dispatch_allowed

HERE = Path(__file__).resolve().parent
_FACTORIES = {}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp():
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def json_create(path, value):
    with Path(path).open("x", encoding="utf8") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")


def identity():
    paths = [HERE / name for name in ("atomic_network.py", "coupled_model.py", "run_sandbox.py", "resource_control.py")]
    paths += sorted((HERE / "vendor" / "atomic").rglob("*"))
    for name in ("builder.py", "prepared_momentum.py", "mass_shell_derivatives.py"):
        paths.append(HERE.parent / "cr_c21n_mass_shell_cache_20261021" / name)
    for name in ("adapter.py", "SOURCE_MANIFEST.json"):
        paths.append(HERE.parent / "cr_c21l_rei_pilot_20261021" / name)
    records = []
    for p in paths:
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
            records.append({"path": str(p.relative_to(HERE.parent)), "size": p.stat().st_size, "sha256": sha256(p)})
    payload = {"schema": "C21O_CONDITIONAL_HHELI_LRS_V1", "files": records,
               "original_LRS_source_commit": "3b85dedce84d37b3e165da00685a8a984950aafe",
               "base_document_head": "8dc5031b3323d4be42a7444843294200aa8887f2",
               "z_start": Z_START, "z_end": Z_END, "rtol": RTOL, "atol": ATOL,
               "FP": "float64", "default_n_output": N_OUTPUT,
               "model": "prescribed UV/temperature, photo+Case-A RR, trace-gas ne->Thomson",
               "atomic_model_parameters": AtomicNetwork21(electronic_isotope_equality=True).model_metadata(),
               "kinetic_configuration": {"mass_fraction_nonbaryonic": .1, "mass_over_Tref": 30.,
                                           "radial_cells": 24, "angular_cells": 12,
                                           "subcell_gauss_order": 3, "Tcmb0_K": 2.7255},
               "global_error_bound": None}
    payload["identity_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def prepare(directory):
    output = Path(directory).resolve()
    output.mkdir(parents=True, exist_ok=False)
    factory = CoupledFactory()
    cases, certificates = [], []
    for s in (-.6, -.3, 0., .3, .6):
        for pm in (-5e-4, 0., 5e-4):
            for pr in (-1.2e-3, 0., 1.2e-3):
                case = {"case_id": f"grid{len(cases):03d}", "signed_sigma": s,
                        "signed_pi_m": pm, "signed_pi_r": pr, "ellmax": 8,
                        "method": "BDF", "thomson": True}
                model = factory.build(s, pm, pr)
                certificates.append({"case_id": case["case_id"], "mapping": model.mapping})
                cases.append(case)
    json_create(output / "GRID45.json", {"schema": "C21O_CASE_GRID_V1", "cases": cases,
                                         "scope": "45 genuinely new z20->2 conditional chemistry-LRS IVPs"})
    json_create(output / "INITIAL_CERTIFICATES.json", certificates)
    # Focused physics checks, each is a distinct solver/model/grid variant.
    controls = [dict(cases[22], case_id="flrw_radau", method="Radau"),
                dict(cases[0], case_id="negative_extreme_L12", ellmax=12),
                dict(cases[-1], case_id="positive_extreme_L12", ellmax=12),
                dict(cases[-1], case_id="positive_extreme_thomson_off", thomson=False),
                dict(cases[22], case_id="cancellation_mplus", signed_pi_m=5e-4, signed_pi_r=-5e-4),
                dict(cases[22], case_id="cancellation_mminus", signed_pi_m=-5e-4, signed_pi_r=5e-4)]
    json_create(output / "CONTROLS6.json", {"schema": "C21O_CASE_GRID_V1", "cases": controls,
                                            "scope": "four numerical/physics controls plus two initially cancelling stress IVPs"})
    json_create(output / "SOURCE_IDENTITY.json", identity())
    print(json.dumps({"prepared": str(output), "science_cases": len(cases), "controls": len(controls), "ODE_integrations": 0}), flush=True)


def worker_init(cpus, expected_source_sha):
    if identity()["identity_sha256"] != expected_source_sha:
        raise RuntimeError("WORKER_SOURCE_IDENTITY_MISMATCH")
    if cpus and hasattr(os, "sched_setaffinity"):
        index = (mp.current_process()._identity[-1] - 1) if mp.current_process()._identity else 0
        os.sched_setaffinity(0, {int(cpus[index % len(cpus)])})


def run_case(case, directory, source_sha):
    output = Path(directory) / "cases" / case["case_id"]
    output.mkdir(parents=False, exist_ok=False)
    json_create(output / "STARTED.json", {"utc": stamp(), "pid": os.getpid(),
                "host": platform.node(), "affinity": sorted(os.sched_getaffinity(0)),
                "case": case, "source_identity_sha256": source_sha})
    try:
        if identity()["identity_sha256"] != source_sha:
            raise RuntimeError("PRE_CASE_SOURCE_IDENTITY_MISMATCH")
        ell = int(case.get("ellmax", 8))
        if ell not in _FACTORIES:
            _FACTORIES[ell] = CoupledFactory(ell)
        model = _FACTORIES[ell].build(case["signed_sigma"], case["signed_pi_m"],
                                     case["signed_pi_r"], thomson=case.get("thomson", True))
        history, receipt = model.integrate(method=case.get("method", "BDF"))
        with (output / "history.npz").open("xb") as f:
            np.savez_compressed(f, **history)
        if identity()["identity_sha256"] != source_sha:
            raise RuntimeError("POST_CASE_SOURCE_IDENTITY_MISMATCH_RAW_PRESERVED")
        receipt.update({"case": case, "source_identity_sha256": source_sha,
                        "history_sha256": sha256(output / "history.npz"),
                        "history_bytes": (output / "history.npz").stat().st_size,
                        "utc_completed": stamp(), "status": "PASS_SCOPED"})
        json_create(output / "RECEIPT.json", receipt)
        json_create(output / "COMPLETE.json", {"status": "PASS_SCOPED", "source_identity_sha256": source_sha,
                                               "history_sha256": receipt["history_sha256"],
                                               "receipt_sha256": sha256(output / "RECEIPT.json")})
        return {"case_id": case["case_id"], "status": "PASS_SCOPED", "wall_seconds": receipt["wall_seconds"]}
    except Exception as exc:
        if hasattr(exc, "partial_history"):
            with (output / "FAILED_HISTORY.npz").open("xb") as f:
                np.savez_compressed(f, **exc.partial_history)
        elif hasattr(exc, "partial_solution"):
            with (output / "FAILED_SOLUTION.npz").open("xb") as f:
                np.savez_compressed(f, eta=exc.partial_solution.t, Y=exc.partial_solution.y)
        failure = {"case_id": case["case_id"], "status": "FAILED_PRESERVED", "exception": repr(exc),
                   "traceback": traceback.format_exc(), "utc": stamp(),
                   "source_identity_sha256": source_sha}
        json_create(output / "FAILURE.json", failure)
        return failure


def run(grid_path, output_dir, requested, resume=False, lease_path=None, only=None):
    grid = json.loads(Path(grid_path).read_text())
    cases = grid["cases"]
    if len({c["case_id"] for c in cases}) != len(cases):
        raise ValueError("DUPLICATE_CASE_ID")
    for c in cases:
        if not c["case_id"].replace("_", "").isalnum():
            raise ValueError("UNSAFE_CASE_ID")
    output = Path(output_dir).resolve()
    source = identity()
    manifest = {"schema": "C21O_RUN_V1", "source": source, "grid": grid,
                "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
                "host": platform.node(), "requested_output": str(output),
                "initial_source_commit_binding": "file SHA256 manifest; publication commit added separately"}
    if resume:
        old = json.loads((output / "MANIFEST.json").read_text())
        if old["source"] != source or old["grid"] != grid:
            raise RuntimeError("RESUME_SOURCE_OR_INPUT_MISMATCH")
        for key in ("python", "numpy", "scipy"):
            if old[key] != manifest[key]:
                raise RuntimeError("RESUME_RUNTIME_MISMATCH:" + key)
    else:
        output.mkdir(parents=True, exist_ok=False)
        (output / "cases").mkdir()
        json_create(output / "MANIFEST.json", manifest)
    selected = set(only.split(",")) if only else {c["case_id"] for c in cases}
    if not selected <= {c["case_id"] for c in cases}:
        raise ValueError("UNKNOWN_SELECTED_CASE")
    pending, reused, held = [], [], []
    for case in cases:
        if case["case_id"] not in selected:
            continue
        d = output / "cases" / case["case_id"]
        if (d / "COMPLETE.json").exists():
            done = json.loads((d / "COMPLETE.json").read_text())
            recorded = json.loads((d / "RECEIPT.json").read_text())
            if (done["source_identity_sha256"] != source["identity_sha256"]
                    or done["history_sha256"] != sha256(d / "history.npz")
                    or done["receipt_sha256"] != sha256(d / "RECEIPT.json")
                    or recorded.get("case") != case
                    or recorded.get("source_identity_sha256") != source["identity_sha256"]
                    or recorded.get("history_sha256") != done["history_sha256"]):
                raise RuntimeError("COMPLETED_CASE_BYTE_MISMATCH:" + case["case_id"])
            reused.append(case["case_id"])
        elif d.exists():
            held.append(case["case_id"])
        else:
            pending.append(case)
    run_stamp = stamp() + f"_{os.getpid()}"
    workers, budget = choose_workers(len(pending), requested=requested,
                                     per_worker_mib=512, coordinator_mib=768,
                                     lease_path=lease_path)
    json_create(output / f"RESOURCES_{run_stamp}.json", budget)
    if not pending or workers == 0:
        summary = {"status": "REUSED_COMPLETE" if not pending and not held else "PENDING_RESOURCE_OR_HELD",
                   "reused": reused, "held": held, "not_started": [c["case_id"] for c in pending]}
        json_create(output / f"SUMMARY_{run_stamp}.json", summary)
        print(json.dumps(summary), flush=True)
        return summary
    cpus = budget.get("selected_worker_cpus", [])
    coordinator = budget.get("coordinator_cpu")
    if coordinator is not None:
        os.sched_setaffinity(0, {int(coordinator)})
    results, active = [], {}
    pause_started = None
    dispatch_snapshot = observe_resources()
    last_probe = time.monotonic()
    with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("spawn"),
                             initializer=worker_init, initargs=(cpus, source["identity_sha256"])) as executor:
        while pending or active:
            if time.monotonic() - last_probe > 2:
                dispatch_snapshot = observe_resources()
                last_probe = time.monotonic()
            allowed, detail = dispatch_allowed(dispatch_snapshot, len(active), budget)
            if allowed:
                pause_started = None
                if pending and len(active) < workers:
                    case = pending.pop(0)
                    future = executor.submit(run_case, case, str(output), source["identity_sha256"])
                    active[future] = case["case_id"]
                    # One admission gate grants only one new task. Account for
                    # reserved slots and take a fresh observation before another.
                    dispatch_snapshot = observe_resources()
                    last_probe = time.monotonic()
            elif not active:
                if pause_started is None:
                    pause_started = time.monotonic()
                if time.monotonic() - pause_started > 60:
                    break
                time.sleep(.25)
            if active:
                done, _ = wait(active, timeout=1, return_when=FIRST_COMPLETED)
                for future in done:
                    case_id = active.pop(future)
                    try:
                        result = future.result()
                    except Exception as exc:
                        result = {"case_id": case_id, "status": "WORKER_PROCESS_FAILED", "exception": repr(exc)}
                    results.append(result)
                    print(json.dumps(result, allow_nan=False), flush=True)
    complete = not pending and not held and all(r["status"] == "PASS_SCOPED" for r in results)
    summary = {"status": ("SELECTION_COMPLETE_SCOPED" if only else "COMPLETE_SCOPED") if complete else "PARTIAL_PRESERVED",
               "new_results": results, "reused": reused, "held": held,
               "not_started": [c["case_id"] for c in pending], "worker_count": workers,
               "source_identity_sha256": source["identity_sha256"], "global_error_bound": None}
    summary["selected_case_ids"] = sorted(selected)
    summary["unselected_case_ids"] = [c["case_id"] for c in cases if c["case_id"] not in selected]
    json_create(output / f"SUMMARY_{run_stamp}.json", summary)
    print(json.dumps({"summary": str(output / f"SUMMARY_{run_stamp}.json"), "status": summary["status"]}), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--output", required=True)
    p = sub.add_parser("run")
    p.add_argument("--grid", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--workers", type=int)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--lease-json")
    p.add_argument("--only", help="comma-separated case IDs; the full run manifest remains unchanged")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.output)
    else:
        result = run(args.grid, args.output, args.workers, args.resume, args.lease_json, args.only)
        if result["status"] not in ("COMPLETE_SCOPED", "SELECTION_COMPLETE_SCOPED", "REUSED_COMPLETE"):
            raise SystemExit(2)


if __name__ == "__main__":
    main()
