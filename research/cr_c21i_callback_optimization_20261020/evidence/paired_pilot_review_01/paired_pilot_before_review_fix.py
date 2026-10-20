"""Bounded manufactured end-to-end comparison; every process and raw is kept.

Compare the unchanged C21H runner with C21I's instrumented baseline, vectorized,
and exact successful-value reuse paths using ONE already-built Rust binary.
This program never launches native chemistry, changes tolerances, or flushes
the operating-system cache.  The first observation and later fresh-process
observations are reported separately; they are not controlled cold-cache runs.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import struct
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent.parent
H = HERE.parent / "cr_c21h_vigilode_bridge_20261019"
MODES = ("c21h_original", "baseline", "vectorized", "vectorized_exact")
METHODS = ("vigilode-rodas5p", "diffsol-bdf")
THREAD_ENV = {name: "1" for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS",
    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "RAYON_NUM_THREADS")}
PHYSICAL = ("gas", "photons", "temperature_K", "photon_number",
    "photon_energy_eV_H", "number_defect_H", "energy_defect_eV_H",
    "species_defect", "ledgers", "optical_depth", "log_survivor",
    "underflowed_positive_cohorts", "min_internal_optical_depth",
    "min_accepted_optical_depth", "photon_clipping", "tolerance_contract")


def utc():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def new(path, obj):
    with Path(path).open("x") as stream:
        json.dump(obj, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def record(path):
    data = Path(path).read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def bits(value):
    """Canonical structure with float64 bits, including signed zero."""
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("NONFINITE_COMPARISON")
        return {"binary64": struct.pack("<d", value).hex()}
    if isinstance(value, list):
        return [bits(v) for v in value]
    if isinstance(value, dict):
        return {k: bits(v) for k, v in sorted(value.items())}
    return value


def identity(bridge, build):
    values = {"bridge": record(bridge), "build_receipt": record(build),
              "benchmark_source": record(__file__), "units": {}}
    for key, root in (("H", H), ("I", HERE)):
        manifest = read(root / "EXECUTION_MANIFEST.json")
        files = {}
        for rel, expected in manifest["runtime_files"].items():
            if Path(rel).is_absolute() or ".." in Path(rel).parts:
                raise ValueError("SOURCE_PATH")
            actual = record(root / rel)
            if actual != expected:
                raise ValueError("RUNTIME_MANIFEST_MISMATCH " + key + ":" + rel)
            files[rel] = actual
        values["units"][key] = {"manifest": record(root / "EXECUTION_MANIFEST.json"),
                                 "runtime_files": files}
    source = HERE.parent / "cr_c21e_event_native_20261018"
    g = HERE.parent / "cr_c21g_reference_refinement_20261019"
    inherited = read(g / "EXECUTION_MANIFEST.json")
    values["G_manifest"] = record(g / "EXECUTION_MANIFEST.json")
    values["F_runtime"] = {}
    for rel, expected in inherited["c21f_runtime_files"].items():
        actual = record(source / rel)
        if actual != expected:
            raise ValueError("INHERITED_SOURCE_MISMATCH " + rel)
        values["F_runtime"][rel] = actual
    if read(build)["binary_sha256"] != values["bridge"]["sha256"]:
        raise ValueError("BUILD_BINARY_MISMATCH")
    return values


def collect(job):
    receipt = read(job / "JOB_RECEIPT.json")
    if receipt["execution"] != "COMPLETE":
        return {"execution": receipt["execution"], "receipt": receipt}
    result = read(job / "result.json")
    callbacks, wire = Counter(), Counter()
    fd = []
    process = []
    for segment in sorted((job / "segments").glob("segment_*")):
        sr = read(segment / "receipt.json")
        callbacks.update(sr["callbacks"])
        process.append(read(segment / "process_exit.json"))
        fd.append(read(segment / "derivative_nodes.json"))
        for line in (segment / "rpc.jsonl").read_text().splitlines():
            row = json.loads(line)
            direction, message = row["direction"], row["message"]
            wire["logged_bytes"] += len((line + "\n").encode())
            # H send uses Python json.dumps defaults; Rust receive serialization
            # is not retained byte-for-byte, so the latter is a canonical
            # reserialization measure, not observed physical wire bytes.
            wire[direction + "_messages"] += 1
            wire[direction + "_canonical_message_bytes"] += len(
                (json.dumps(message, allow_nan=False) + "\n").encode())
            if message.get("type") == "request":
                wire["rpc_" + message["op"]] += 1
    trace = [{"accepted_times": s["raw_result"]["accepted_times"],
              "accepted_states": s["raw_result"]["accepted_states"],
              "config": s["config"]} for s in result["rust_segments"]]
    scientific = {key: result[key] for key in PHYSICAL}
    return {"execution": "COMPLETE", "job_wall_s": receipt["wall_s"],
        "reference_wall_s": result["wall_s"], "native_executed": receipt["native_executed"],
        "fixture_sha256": result["fixture_sha256"], "callbacks": dict(callbacks),
        "communication": dict(wire), "rhs_evaluations": result["rhs_evaluations"],
        "solver": result["solver_diagnostics"],
        "rust_counters": [s["raw_result"].get("counters", {}) for s in result["rust_segments"]],
        "physical_bits": bits(scientific), "trace_bits": bits(trace),
        "fd_nodes_bits": bits(fd),
        "independent_balances_bits": bits(read(job / "INDEPENDENT_BALANCES.json")),
        "process_exits": process, "input_identity": receipt["input_identity"],
        "bridge_identity": receipt["bridge_identity"],
        "callback_optimization": result.get("callback_optimization")}


def summary(rows):
    comparisons = []
    for row in rows:
        refs = [r for r in rows if r["method"] == row["method"]
                and r["round"] == row["round"] and r["mode"] == "c21h_original"]
        if not refs:
            continue
        ref = refs[0]
        success = row["execution"] == ref["execution"] == "COMPLETE"
        checks = {key: success and row[key] == ref[key] for key in
            ("fixture_sha256", "input_identity", "bridge_identity", "physical_bits",
             "trace_bits", "fd_nodes_bits", "independent_balances_bits", "rust_counters")}
        comparisons.append({"method": row["method"], "round": row["round"],
            "mode": row["mode"], "checks": checks,
            "all_bitwise_and_identity_checks_pass": all(checks.values())})
    estimates = []
    for method in METHODS:
        for mode in MODES:
            selected = [r for r in rows if r["method"] == method and r["mode"] == mode]
            later = [r for r in selected if r["round"] > 0]
            item = {"method": method, "mode": mode, "completed": sum(r["execution"] == "COMPLETE" for r in selected),
                    "attempts": len(selected), "total_process_wall_s_including_failures": sum(r["process_wall_s"] for r in selected),
                    "first_process_wall_s": selected[0]["process_wall_s"] if selected else None}
            ratios = {key: [] for key in ("process_wall_s", "job_wall_s", "reference_wall_s")}
            for r in later:
                ref = next((v for v in rows if v["method"] == method and v["round"] == r["round"] and v["mode"] == "c21h_original"), None)
                if r["execution"] != "COMPLETE" or ref is None or ref["execution"] != "COMPLETE":
                    continue
                for key in ratios:
                    ratios[key].append(ref[key] / r[key])
            item["later_paired_speedup_raw"] = ratios
            item["later_paired_speedup_median"] = {k: statistics.median(v) if v else None for k, v in ratios.items()}
            item["later_process_wall_raw_s"] = [r["process_wall_s"] for r in later]
            item["complete_rhs_evaluations"] = [r["rhs_evaluations"] for r in selected if r["execution"] == "COMPLETE"]
            estimates.append(item)
    return {"comparisons": comparisons, "estimates": estimates,
            "all_jobs_complete": all(r["execution"] == "COMPLETE" for r in rows),
            "all_comparisons_pass": all(c["all_bitwise_and_identity_checks_pass"] for c in comparisons),
            "total_process_wall_s_including_failures": sum(r["process_wall_s"] for r in rows)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", type=Path, required=True)
    parser.add_argument("--build-receipt", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--later-repeats", type=int, default=3)
    args = parser.parse_args(argv)
    if args.cpu == 55 or args.cpu not in os.sched_getaffinity(0):
        raise ValueError("LOCAL_CPU_NOT_ADMITTED")
    if not 1 <= args.later_repeats <= 5:
        raise ValueError("BOUNDED_REPEAT_COUNT")
    before = identity(args.bridge, args.build_receipt)
    args.out.mkdir(parents=True, exist_ok=False)
    new(args.out / "SOURCE_BEFORE.json", before)
    new(args.out / "PLAN.json", {"at": utc(), "methods": METHODS, "modes": MODES,
        "rounds": args.later_repeats + 1, "max_concurrent_jobs": 1, "thread_environment": THREAD_ENV,
        "cpu": args.cpu, "exclusive_allocation_verified": False,
        "native_chemistry": False, "fixture": "unchanged H smoke Y0 M9 dx1e-7 full28/integrated26",
        "rtol": 2e-11, "alpha": 2e-14, "max_step_divisor": 8,
        "first_observation": "fresh process; OS cache not flushed and binary previously built/run",
        "later_observations": "fresh Python and fresh Rust segment processes, cache order rotated",
        "baseline_note": "c21h_original runs unchanged H. baseline is I instrumentation/guard baseline.",
        "wire_note": "logged wrapper bytes are actual file bytes; received message sizes are canonical reserialization estimates",
        "global_error_bound": None})
    env = os.environ.copy(); env.update(THREAD_ENV)
    rows = []
    started = time.monotonic()
    try:
        for round_id in range(args.later_repeats + 1):
            for method in METHODS:
                order = MODES[round_id % len(MODES):] + MODES[:round_id % len(MODES)]
                for mode in order:
                    name = f"round{round_id:02}_{method}_{mode}"
                    job = args.out / name
                    runner = H / "run_pilot.py" if mode == "c21h_original" else HERE / "run_optimized_pilot.py"
                    cmd = [sys.executable, str(runner), "smoke", "--out", str(job),
                           "--bridge", str(args.bridge.resolve()), "--bridge-build-receipt", str(args.build_receipt.resolve()),
                           "--method", method]
                    if mode != "c21h_original":
                        cmd += ["--optimization", mode]
                    row = {"at": utc(), "round": round_id, "method": method, "mode": mode, "command": cmd}
                    start = time.monotonic()
                    with (args.out / (name + ".stdout")).open("x") as stdout, (args.out / (name + ".stderr")).open("x") as stderr:
                        run = subprocess.run(cmd, env=env, stdout=stdout, stderr=stderr,
                            preexec_fn=lambda: os.sched_setaffinity(0, {args.cpu}), timeout=330)
                    row.update(process_wall_s=time.monotonic() - start, exit_code=run.returncode)
                    if (job / "JOB_RECEIPT.json").exists():
                        row.update(collect(job))
                    else:
                        row.update(execution="FAILED_BEFORE_JOB_RECEIPT")
                    rows.append(row)
                    new(args.out / (name + ".OBSERVATION.json"), row)
                    print(json.dumps({k: row[k] for k in ("round", "method", "mode", "execution", "process_wall_s")}), flush=True)
        result = summary(rows)
    except BaseException:
        with (args.out / "HARNESS_FAILURE.log").open("x") as stream:
            stream.write(traceback.format_exc())
        raise
    finally:
        after = identity(args.bridge, args.build_receipt)
        new(args.out / "SOURCE_AFTER.json", after)
        new(args.out / "HARNESS_RECEIPT.json", {"at": utc(), "wall_s": time.monotonic() - started,
            "attempted_rows": len(rows), "sources_unchanged": before == after,
            "python": platform.python_version(), "native_executed": False})
    if before != after:
        raise ValueError("POST_BENCHMARK_SOURCE_DRIFT")
    new(args.out / "SUMMARY.json", result)
    payloads = {str(p.relative_to(args.out)): record(p) for p in sorted(args.out.rglob("*")) if p.is_file()}
    new(args.out / "PAYLOAD_MANIFEST.json", {"files": payloads, "payload_count": len(payloads)})
    return 0 if result["all_jobs_complete"] and result["all_comparisons_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
