#!/usr/bin/env python3
"""Changed-path C21K replay and small saved-callback benchmark; no native/IVP.

C21J's reviewed input and complete-protocol admission is reused byte-for-byte.
All numerical callback outputs and derivative nodes are recomputed. Original
accepted states are consumed only to reconstruct the unchanged physical summary.
Reported times are saved-callback replay times, never live-native speedups.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace

import numpy as np
import scipy.integrate

HERE = Path(__file__).resolve().parent
J_REPLAY_SHA256 = "7c855b9983c575042a18754687696a039bef31f5711c455f774b70c03bae52c1"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def replay_one(j, epoch, repo, job, mode, use_epoch):
    original, receipt = j.read_json(job / "result.json"), j.read_json(job / "JOB_RECEIPT.json")
    if receipt.get("execution") != "COMPLETE" or receipt.get("native_executed") is not True:
        raise j.ReplayError("MATCHING_COMPLETED_NATIVE_JOB_REQUIRED")
    if use_epoch:
        optimizer, scope = epoch.prepare_optimizer(c21i_dir=repo / j.I_REL)
    else:
        optimizer = j.load_module(repo / j.I_REL / "optimized_adapter.py", "_c21k_baseline_" + mode)
        scope = None
    base = optimizer.load_frozen_adapter(repo / j.H_REL)
    optimizer.source_snapshot(repo / j.F_REL, repo / j.G_REL)
    vendor = str(repo / j.F_REL / "vendor/pr79")
    if vendor not in sys.path:
        sys.path.insert(0, vendor)
    reference = base.private_reference(repo / j.F_REL)
    from run_experiment import Fixture
    import native_micro
    fixture = optimizer._freeze_fixture(Fixture(**j.read_json(job / "fixture.json")).validate())
    if fixture.digest != original["fixture_sha256"] or fixture.digest != receipt["fixture_sha256"]:
        raise j.ReplayError("FIXTURE_CANONICAL_IDENTITY")
    controls = original["tolerance_contract"]
    dynamic = np.asarray(controls["dynamic_indices"], int)
    scales = np.asarray(controls["fixed_diagonal_scaling"]["values"], float)[dynamic]
    rows = [j.parse_json(line) for line in (job / "native/native_points.jsonl").read_text().splitlines()]
    table = j.ReplyTable(rows)
    provider = j.make_recorded_provider(native_micro, table)
    admission = {"schema": "C21I_DETERMINISTIC_PROVIDER_ADMISSION_V1",
        "deterministic_successful_rhs": True,
        "provider_identity": {"native_points_sha256": j.digest(job / "native/native_points.jsonl")},
        "provider_kind": provider.kind,
        "admitted_by": "Immutable exact ASCII reply table; successful duplicate equality checked"}
    callback_type = optimizer.make_callback_type(base, mode,
                         cache_contract=admission if mode == "vectorized_exact" else None)
    segments = sorted((job / "segments").glob("segment_*"))
    records, index = [], 0
    public_opacity = sys.modules["run_experiment"].opacity
    public_hubble = sys.modules["event_coupler"].H

    def consume_saved_segment(fun, t_span, y0, *, method, rtol, atol, max_step, **kwargs):
        nonlocal index
        if kwargs or method != "Radau" or index >= len(segments):
            raise j.ReplayError("REPLAY_REFERENCE_CALL_CONTRACT")
        directory = segments[index]
        config, raw = j.read_json(directory / "config.json"), j.read_json(directory / "result.json")
        if j.bits(t_span) != j.bits([config["t0"], config["t1"]]):
            raise j.ReplayError("REPLAY_EVENT_CELL_IDENTITY")
        if j.bits(np.asarray(y0) / scales) != j.bits(config["y0"]):
            raise j.ReplayError("REPLAY_SCALED_INITIAL_IDENTITY")
        if j.bits(atol) != j.bits(config["atol"] * scales):
            raise j.ReplayError("REPLAY_TOLERANCE_IDENTITY")
        if j.bits([rtol, max_step]) != j.bits([config["rtol"], config["h_max"]]):
            raise j.ReplayError("REPLAY_METHOD_CONTROLS")
        cb = callback_type(fun, fixture, *t_span, scales, dynamic, reference,
                          controls["gas_fd_relative"], controls["time_fd_fraction"])
        pairs = j.rpc_pairs(directory / "rpc.jsonl", config, raw)
        values, output_hash = 0, hashlib.sha256()
        queries_before = len(table.queries)
        callback_ns = 0
        for request, expected in pairs:
            started = time.perf_counter_ns()
            actual = getattr(cb, request["op"])(request["t"], request["y"])
            callback_ns += time.perf_counter_ns() - started
            if j.bits(actual) != j.bits(expected):
                raise j.ReplayError("C21K_CALLBACK_REPLY_MISMATCH " + str((index, request["id"], request["op"])))
            values += np.asarray(actual).size
            output_hash.update(j.bits(actual)[1])
        if not j.equal_structure(cb.fd_nodes, j.read_json(directory / "derivative_nodes.json")):
            raise j.ReplayError("REPLAY_DERIVATIVE_NODE_IDENTITY")
        times, states = np.asarray(raw["accepted_times"]), np.asarray(raw["accepted_states"])
        if not raw["accepted_grid_complete"] or len(times) != raw["internal_steps"] + 1:
            raise j.ReplayError("SAVED_ACCEPTED_TRACE_INCOMPLETE")
        records.append({"segment": index, "rpc_replies": len(pairs), "binary64_values": values,
                        "reply_values_sha256": output_hash.hexdigest(), "callbacks": dict(cb.counts),
                        "recorded_provider_queries": len(table.queries)-queries_before,
                        "saved_callback_ns": callback_ns})
        index += 1
        return SimpleNamespace(t=times, y=(states*scales[None, :]).T, success=True, status=0,
             message="SAVED_ACCEPTED_STATES_REPLAY_NO_IVP_SOLVE", nfev=cb.counts["rhs_requests"],
             njev=cb.counts["jacobian_requests"], nlu=raw["counters"]["direct_factorizations"])

    reference.solve_ivp = consume_saved_segment
    replayed = reference.run_reference_tau(fixture, provider, rtol=controls["rtol"],
        atol=controls["atol"], max_step_divisor=controls["max_step_divisor"], max_evaluations=200000)
    if index != len(segments):
        raise j.ReplayError("UNCONSUMED_SAVED_SEGMENTS")
    same = {key: j.equal_structure(replayed[key], original[key]) for key in j.PHYSICAL_FIELDS}
    if not all(same.values()):
        raise j.ReplayError("C21K_PHYSICAL_SUMMARY_MISMATCH")
    if sys.modules["run_experiment"].opacity is not public_opacity or sys.modules["event_coupler"].H is not public_hubble:
        raise j.ReplayError("PUBLIC_MODULE_MUTATION")
    return {"job": job.name, "mode": mode, "epoch_cache": use_epoch, "status": "PASS_SCOPED",
            "fixture_sha256": fixture.digest, "segments": records,
            "rpc_replies": sum(r["rpc_replies"] for r in records),
            "binary64_values": sum(r["binary64_values"] for r in records),
            "recorded_provider_queries": provider.calls,
            "physical_fields_bitwise_equal": same,
            "epoch": None if scope is None else scope.summary(),
            "saved_callback_ns": sum(r["saved_callback_ns"] for r in records),
            "new_native_calls": 0, "new_IVP_solves": 0,
            "native_process_admission_verified_by_replay": False,
            "global_error_bound": None}


def run(args):
    if hashlib.sha256(args.j_replay.read_bytes()).hexdigest() != J_REPLAY_SHA256:
        raise RuntimeError("PINNED_C21J_REPLAY_REQUIRED")
    j = load_module(args.j_replay, "_c21k_j_replay")
    epoch = load_module(HERE / "epoch_adapter.py", "_c21k_epoch_replay")
    if j.digest(args.input_pins) != j.INPUT_PINS_SHA256:
        raise j.ReplayError("INPUT_PIN_FILE_IDENTITY")
    pins = j.read_json(args.input_pins)
    before = j.verify_inputs(args.repo, args.native_return, pins)
    args.out.mkdir(parents=True, exist_ok=False)
    report = {"schema": "C21K_EPOCH_REPLAY_V1", "status": "RUNNING", "cases": [],
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "j_replay_sha256": J_REPLAY_SHA256, "input_pins_sha256": j.INPUT_PINS_SHA256,
        "source": {name: j.digest(HERE / name) for name in ("epoch_adapter.py", "replay_epoch.py")},
        "new_native_calls": 0, "new_IVP_solves": 0, "global_error_bound": None}
    old_popen, old_solve = subprocess.Popen, scipy.integrate.solve_ivp

    def forbidden(*a, **kw):
        raise j.ReplayError("FORBIDDEN_NEW_NATIVE_PROCESS_OR_IVP")

    subprocess.Popen, scipy.integrate.solve_ivp = forbidden, forbidden
    try:
        base_job = args.native_return / "evidence/I_common_ic_vigilode_vectorized_base"
        for job, mode in [(base_job, "vectorized"), (base_job, "vectorized_exact"),
            (args.native_return / "evidence/I_common_ic_vigilode_vectorized_fd_half", "vectorized_exact")]:
            report["cases"].append(replay_one(j, epoch, args.repo, job, mode, True))
        if args.benchmark_pairs:
            # One warm-up per path, then paired alternating order on identical
            # saved work. Every measured callback remains equality-checked.
            warm = [replay_one(j, epoch, args.repo, base_job, "vectorized_exact", flag)
                    for flag in (False, True)]
            rows = []
            for pair in range(args.benchmark_pairs):
                order = (False, True) if pair % 2 == 0 else (True, False)
                row = {"pair": pair, "order": ["epoch" if x else "original_I_exact" for x in order]}
                for flag in order:
                    result = replay_one(j, epoch, args.repo, base_job, "vectorized_exact", flag)
                    row["epoch_ns" if flag else "original_I_exact_ns"] = result["saved_callback_ns"]
                row["speed_ratio_original_over_epoch"] = row["original_I_exact_ns"] / row["epoch_ns"]
                rows.append(row)
            ratios = [r["speed_ratio_original_over_epoch"] for r in rows]
            report["benchmark"] = {"scope": "SAVED_CALLBACK_COMPUTATION_ONLY_NO_NATIVE_NO_IVP",
                "warmup_per_path": 1, "pairs": rows,
                "median_paired_ratio": statistics.median(ratios),
                "minimum_paired_ratio": min(ratios), "maximum_paired_ratio": max(ratios),
                "stdev_paired_ratio": statistics.stdev(ratios) if len(ratios) > 1 else None,
                "warmup_ns": [x["saved_callback_ns"] for x in warm],
                "native_speedup": "NOT_EVALUATED", "NCP64_scaling": "NOT_EVALUATED"}
        report["input_files_unchanged"] = before == j.verify_inputs(args.repo, args.native_return, pins)
        report["status"] = "PASS_SCOPED"
    except BaseException as error:
        report.update(status="FAILED", error_class=type(error).__name__, error=str(error))
        (args.out / "failure.txt").write_text(traceback.format_exc())
    finally:
        subprocess.Popen, scipy.integrate.solve_ivp = old_popen, old_solve
        (args.out / "REPLAY_REPORT.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return 0 if report["status"] == "PASS_SCOPED" else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--native-return", type=Path, required=True)
    p.add_argument("--j-replay", type=Path, required=True)
    p.add_argument("--input-pins", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--benchmark-pairs", type=int, default=0, choices=range(0, 10))
    return run(p.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
