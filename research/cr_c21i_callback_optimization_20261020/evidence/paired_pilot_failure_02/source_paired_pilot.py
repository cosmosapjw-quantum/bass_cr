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
import signal
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


def _proc_identity_visible(proc_pid):
    """/proc can be mounted from an ancestor of our current PID namespace."""
    try:
        path = Path(f"/proc/{proc_pid}")
        namespace = os.readlink(path / "ns/pid")
        if namespace != os.readlink("/proc/self/ns/pid"):
            return None
        tail = (path / "stat").read_text().rsplit(") ", 1)[1].split()
        nspid = next(line.split()[1:] for line in (path / "status").read_text().splitlines()
                    if line.startswith("NSpid:"))
        return {"pid": int(nspid[-1]), "proc_pid": proc_pid, "ppid_proc": int(tail[1]),
                "start_ticks": int(tail[19]), "state": tail[0], "session": int(tail[3]),
                "pid_namespace": namespace}
    except (OSError, IndexError, ValueError, StopIteration):
        return None


def proc_identity(pid, proc_pid=None):
    """Resolve only our namespace; root lookup is limited to our own children."""
    if proc_pid is not None:
        result = _proc_identity_visible(proc_pid)
        return result if result is not None and result["pid"] == pid else None
    self_proc_pid = int(Path("/proc/self/stat").read_text().split(" ", 1)[0])
    if pid == os.getpid():
        return _proc_identity_visible(self_proc_pid)
    direct = _proc_identity_visible(pid)
    if direct is not None and direct["pid"] == pid:
        return direct
    try:
        visible_children = {int(child) for path in Path(f"/proc/{self_proc_pid}/task").glob("*/children")
                            for child in path.read_text().split()}
        for visible in visible_children:
            child = _proc_identity_visible(visible)
            if child is not None and child["pid"] == pid and child["ppid_proc"] == self_proc_pid:
                return child
    except (OSError, IndexError, ValueError):
        pass
    return None


def observe_owned(process, owned):
    """Extend one Popen's ancestry snapshot; never adopt an unrelated PID."""
    root = proc_identity(process.pid)
    self_proc_pid = int(Path("/proc/self/stat").read_text().split(" ", 1)[0])
    if not owned and root is not None and root["ppid_proc"] == self_proc_pid:
        owned[process.pid] = {**root, "parent_start_ticks": None, "depth": 0}
    queue = list(owned)
    for pid in queue:
        original = owned[pid]
        current = proc_identity(pid, original["proc_pid"])
        if current is None or current["start_ticks"] != original["start_ticks"]:
            continue
        try:
            child_pids = {int(child) for path in Path(f"/proc/{original['proc_pid']}/task").glob("*/children")
                          for child in path.read_text().split()}
        except OSError:
            continue  # A process/thread may disappear between observations.
        for child_visible in child_pids:
            child, parent_now = _proc_identity_visible(child_visible), proc_identity(pid, original["proc_pid"])
            if (child is None or child["ppid_proc"] != original["proc_pid"] or parent_now is None
                    or parent_now["start_ticks"] != original["start_ticks"]):
                continue
            child_pid = child["pid"]
            if child_pid not in owned:
                owned[child_pid] = {**child, "parent_start_ticks": original["start_ticks"],
                                    "depth": original["depth"]+1}
                queue.append(child_pid)


def owned_running(owned):
    result = []
    for original in owned.values():
        current = proc_identity(original["pid"], original["proc_pid"])
        if (current is not None and current["start_ticks"] == original["start_ticks"]
                and current["state"] not in ("Z", "X")):
            result.append(original)
    return result


def signal_owned(original, signum):
    """A pidfd closes the stat-check/signal PID-reuse race."""
    fd = None
    outcome = {"pid": original["pid"], "start_ticks": original["start_ticks"],
               "signal": signum}
    try:
        fd = os.pidfd_open(original["pid"])
        current = proc_identity(original["pid"], original["proc_pid"])
        if current is None or current["start_ticks"] != original["start_ticks"]:
            outcome["outcome"] = "GONE_OR_IDENTITY_CHANGED_NOT_SIGNALED"
        else:
            signal.pidfd_send_signal(fd, signum)
            outcome["outcome"] = "SIGNALED_OWNED_PIDFD"
    except ProcessLookupError:
        outcome["outcome"] = "ALREADY_EXITED"
    except OSError as error:
        outcome.update(outcome="SIGNAL_ERROR", error=repr(error))
    finally:
        if fd is not None:
            os.close(fd)
    return outcome


def cleanup_owned(process, owned):
    begin = time.monotonic()
    signals = []
    observe_owned(process, owned)
    initially_running = owned_running(owned)
    for signum in (signal.SIGTERM, signal.SIGKILL):
        for original in sorted(owned_running(owned), key=lambda v: v["depth"], reverse=True):
            signals.append(signal_owned(original, signum))
        until = time.monotonic()+.5
        while owned_running(owned) and time.monotonic() < until:
            process.poll()
            observe_owned(process, owned)
            time.sleep(.01)
    try:
        process.wait(timeout=.5)
    except subprocess.TimeoutExpired:
        pass
    remaining = owned_running(owned)
    return {"wall_s": time.monotonic()-begin, "observed_owned": list(owned.values()),
            "initially_running": initially_running, "signals": signals,
            "remaining_running": remaining,
            "complete": not remaining and process.poll() is not None,
            "scope": "Popen root and descendants actually observed by verified parent/start-time chain; no campaign-wide process signals"}


def run_attempt(cmd, env, cpu, prefix, timeout=330.):
    """Retain a started attempt, even on launch/timeout/collection failure."""
    initial = {"at": utc(), "command": cmd, "cpu": cpu, "timeout_s": timeout,
               "state": "LAUNCH_REQUESTED", "thread_environment": THREAD_ENV}
    new(Path(str(prefix)+".ATTEMPT.json"), initial)
    start = time.monotonic()
    process, owned = None, {}
    outcome = {"launch_attempted": True, "process_started": False,
               "timed_out": False, "interrupted": False, "exit_code": None}
    try:
        with Path(str(prefix)+".stdout").open("x") as stdout, Path(str(prefix)+".stderr").open("x") as stderr:
            process = subprocess.Popen(cmd, env=env, stdout=stdout, stderr=stderr,
                start_new_session=True, preexec_fn=lambda: os.sched_setaffinity(0, {cpu}))
            outcome.update(process_started=True, pid=process.pid)
            observe_owned(process, owned)
            while True:
                observe_owned(process, owned)
                remaining = timeout-(time.monotonic()-start)
                if remaining <= 0:
                    outcome["timed_out"] = process.poll() is None
                    break
                try:
                    process.wait(timeout=min(.025, remaining))
                    break
                except subprocess.TimeoutExpired:
                    continue
            outcome["runner_process_wall_s"] = time.monotonic()-start
    except BaseException as error:
        outcome.update(error_class=type(error).__name__, error=str(error),
                       interrupted=isinstance(error, (KeyboardInterrupt, SystemExit)))
        with Path(str(prefix)+".PROCESS_FAILURE.log").open("x") as stream:
            stream.write(traceback.format_exc())
    finally:
        if process is not None:
            # H's Rust segment starts its own session.  Killing only the Python
            # group would leave it outside that group; use the observed PID tree.
            try:
                outcome["cleanup"] = cleanup_owned(process, owned)
            except BaseException as error:
                outcome["cleanup"] = {"complete": False, "error_class": type(error).__name__,
                                      "error": str(error), "observed_owned": list(owned.values())}
            outcome["exit_code"] = process.poll()
        else:
            outcome["cleanup"] = {"complete": True, "observed_owned": [],
                                  "remaining_running": [], "signals": [], "wall_s": 0.}
        outcome["process_wall_s"] = time.monotonic()-start
        new(Path(str(prefix)+".PROCESS_RECEIPT.json"), outcome)
    return outcome


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
    if (values["units"]["H"]["manifest"]["sha256"] != "7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb"
            or values["G_manifest"]["sha256"] != "7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed"):
        raise ValueError("PINNED_INHERITED_MANIFEST_MISMATCH")
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
        return {"execution": receipt["execution"], "receipt": receipt,
                "native_executed": receipt.get("native_executed"),
                "job_wall_s": receipt.get("wall_s")}
    result = read(job / "result.json")
    callbacks, wire = Counter(), Counter()
    fd = []
    process = []
    for segment in sorted((job / "segments").glob("segment_*")):
        sr = read(segment / "receipt.json")
        callbacks.update(sr["callbacks"])
        process.append(read(segment / "process_exit.json"))
        fd.append(read(segment / "derivative_nodes.json"))
        wire["logged_bytes"] += (segment / "rpc.jsonl").stat().st_size
        for line in (segment / "rpc.jsonl").read_text().splitlines():
            row = json.loads(line)
            direction, message = row["direction"], row["message"]
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
        "native_process_started": receipt.get("native_process_started"),
        "native_launch_attempted": receipt.get("native_launch_attempted"),
        "fixture_sha256": result["fixture_sha256"], "callbacks": dict(callbacks),
        "communication": dict(wire), "rhs_evaluations": result["rhs_evaluations"],
        "solver": result["solver_diagnostics"],
        "rust_counters": [s["raw_result"].get("counters", {}) for s in result["rust_segments"]],
        "physical_bits": bits(scientific), "trace_bits": bits(trace),
        "fd_nodes_bits": bits(fd),
        "independent_balances_bits": bits(read(job / "INDEPENDENT_BALANCES.json")),
        "process_exits": process, "input_identity": receipt["input_identity"],
        "bridge_identity": receipt["bridge_identity"],
        "complete_accepted_trace": result.get("accepted_state_trace_complete") is True and
            all(s["raw_result"].get("accepted_grid_complete") is True for s in result["rust_segments"]),
        "global_error_bound": result.get("global_error_bound"),
        "runtime": {key: receipt.get(key) for key in ("python", "numpy", "scipy", "thread_environment")},
        "callback_optimization": result.get("callback_optimization")}


def operationally_complete(row):
    return (row.get("execution") == "COMPLETE" and row.get("exit_code") == 0
            and not row.get("timed_out", False) and not row.get("error_class")
            and row.get("native_executed") is False
            and row.get("native_process_started") is False
            and row.get("native_launch_attempted") is False
            and row.get("complete_accepted_trace") is True
            and row.get("global_error_bound") is None
            and row.get("cleanup", {}).get("complete") is True
            and bool(row.get("process_exits"))
            and all(p.get("process_started") is True and p.get("exit_code") == 0
                    for p in row["process_exits"]))


def summary(rows, expected_keys=None):
    if expected_keys is None:
        expected_keys = {(r, method, mode) for r in range(max((v["round"] for v in rows), default=0)+1)
                         for method in METHODS for mode in MODES}
    observed = [(row["round"], row["method"], row["mode"]) for row in rows]
    cardinality = len(observed) == len(set(observed)) and set(observed) == set(expected_keys)
    comparisons = []
    for row in rows:
        refs = [r for r in rows if r["method"] == row["method"]
                and r["round"] == row["round"] and r["mode"] == "c21h_original"]
        if not refs:
            continue
        ref = refs[0]
        success = operationally_complete(row) and operationally_complete(ref)
        checks = {key: success and row[key] == ref[key] for key in
            ("fixture_sha256", "input_identity", "bridge_identity", "physical_bits",
             "trace_bits", "fd_nodes_bits", "independent_balances_bits", "rust_counters", "runtime")}
        comparisons.append({"method": row["method"], "round": row["round"],
            "mode": row["mode"], "checks": checks,
            "all_bitwise_and_identity_checks_pass": all(checks.values())})
    estimates = []
    for method in METHODS:
        for mode in MODES:
            selected = [r for r in rows if r["method"] == method and r["mode"] == mode]
            later = [r for r in selected if r["round"] > 0]
            item = {"method": method, "mode": mode, "completed": sum(operationally_complete(r) for r in selected),
                    "attempts": len(selected), "total_process_wall_s_including_failures": sum(r["process_wall_s"] for r in selected),
                    "first_process_wall_s": selected[0]["process_wall_s"] if selected else None}
            ratios = {key: [] for key in ("process_wall_s", "job_wall_s", "reference_wall_s")}
            for r in later:
                ref = next((v for v in rows if v["method"] == method and v["round"] == r["round"] and v["mode"] == "c21h_original"), None)
                if not operationally_complete(r) or ref is None or not operationally_complete(ref):
                    continue
                for key in ratios:
                    ratios[key].append(ref[key] / r[key])
            item["later_paired_speedup_raw"] = ratios
            item["later_paired_speedup_median"] = {k: statistics.median(v) if v else None for k, v in ratios.items()}
            item["later_process_wall_raw_s"] = [r["process_wall_s"] for r in later]
            item["complete_rhs_evaluations"] = [r["rhs_evaluations"] for r in selected if operationally_complete(r)]
            estimates.append(item)
    return {"comparisons": comparisons, "estimates": estimates,
            "planned_attempts": len(expected_keys), "actual_attempts": len(rows),
            "planned_attempt_cardinality_and_uniqueness": cardinality,
            "not_attempted_keys": sorted(set(expected_keys)-set(observed)),
            "all_jobs_complete": cardinality and all(operationally_complete(r) for r in rows),
            "all_comparisons_pass": cardinality and bool(comparisons) and all(c["all_bitwise_and_identity_checks_pass"] for c in comparisons),
            "total_process_wall_s_including_failures": sum(r["process_wall_s"] for r in rows)}


def finish_run(output, before, rows, bridge, build, expected_keys, started, harness_error=None):
    """Postcheck failure is evidence, not an exception hiding earlier evidence."""
    after = None
    try:
        after = identity(bridge, build)
        new(output / "SOURCE_AFTER.json", after)
    except BaseException as error:
        new(output / "SOURCE_AFTER_FAILURE.json", {"at": utc(), "error_class": type(error).__name__,
                                                  "error": str(error), "traceback": traceback.format_exc()})
    result = summary(rows, expected_keys)
    result.update(sources_unchanged=after is not None and before == after,
                  harness_error=harness_error)
    result["accepted"] = (result["all_jobs_complete"] and result["all_comparisons_pass"]
                          and result["sources_unchanged"] and harness_error is None)
    observed_native = [r.get("native_executed", False if not r.get("process_started") else None) for r in rows]
    native_executed = True if any(v is True for v in observed_native) else (False if all(v is False for v in observed_native) else None)
    new(output / "SUMMARY.json", result)
    new(output / "HARNESS_RECEIPT.json", {"at": utc(), "wall_s": time.monotonic()-started,
        "attempted_rows": len(rows), "planned_attempts": len(expected_keys),
        "total_process_wall_s_including_failures": result["total_process_wall_s_including_failures"],
        "sources_unchanged": result["sources_unchanged"], "accepted": result["accepted"],
        "python": platform.python_version(), "native_chemistry_requested": False,
        "native_executed_from_available_job_receipts": native_executed,
        "native_execution_unknown_attempts": sum(v is None for v in observed_native),
        "harness_error": harness_error, "global_error_bound": None})
    payloads = {str(p.relative_to(output)): record(p) for p in sorted(output.rglob("*")) if p.is_file()}
    new(output / "PAYLOAD_MANIFEST.json", {"files": payloads, "payload_count": len(payloads)})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", type=Path, required=True)
    parser.add_argument("--build-receipt", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--monitor-cpu", type=int)
    parser.add_argument("--later-repeats", type=int, default=3)
    args = parser.parse_args(argv)
    affinity_before = sorted(os.sched_getaffinity(0))
    if args.cpu == 55 or args.cpu not in affinity_before:
        raise ValueError("LOCAL_CPU_NOT_ADMITTED")
    if args.monitor_cpu is not None and (args.monitor_cpu == 55 or args.monitor_cpu not in affinity_before):
        raise ValueError("LOCAL_MONITOR_CPU_NOT_ADMITTED")
    if not 1 <= args.later_repeats <= 5:
        raise ValueError("BOUNDED_REPEAT_COUNT")
    if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
        raise ValueError("LINUX_PIDFD_REQUIRED_FOR_OWNED_TIMEOUT_CLEANUP")
    # Validate both against the initially allowed set, before narrowing only
    # this monitor.  Each owned child explicitly binds its separately admitted CPU.
    if args.monitor_cpu is not None:
        os.sched_setaffinity(0, {args.monitor_cpu})
    before = identity(args.bridge, args.build_receipt)
    args.out.mkdir(parents=True, exist_ok=False)
    new(args.out / "SOURCE_BEFORE.json", before)
    new(args.out / "PLAN.json", {"at": utc(), "methods": METHODS, "modes": MODES,
        "rounds": args.later_repeats + 1, "max_concurrent_jobs": 1, "thread_environment": THREAD_ENV,
        "cpu": args.cpu, "monitor_cpu": args.monitor_cpu, "affinity_before": affinity_before,
        "monitor_affinity": sorted(os.sched_getaffinity(0)), "exclusive_allocation_verified": False,
        "native_chemistry": False, "fixture": "unchanged H smoke Y0 M9 dx1e-7 full28/integrated26",
        "rtol": 2e-11, "alpha": 2e-14, "max_step_divisor": 8,
        "first_observation": "fresh process; OS cache not flushed and binary previously built/run",
        "later_observations": "fresh Python and fresh Rust segment processes, cache order rotated",
        "baseline_note": "c21h_original runs unchanged H. baseline is I instrumentation/guard baseline.",
        "timing_scope": "process_wall includes launch, fixed 25ms ownership-observation polling and owned cleanup; job/reference clocks remain separate",
        "timeout_s": 330, "timeout_context": "inherited H job budget 300s plus 30s outer grace; timed-out attempts retained and campaign stops",
        "cleanup_scope": "only Popen root and observed /proc parent+start-time descendants, signaled with verified pidfd; Rust may use a different session",
        "wire_note": "logged wrapper bytes are actual file bytes; received message sizes are canonical reserialization estimates",
        "global_error_bound": None})
    env = os.environ.copy(); env.update(THREAD_ENV)
    rows = []
    expected_keys = {(r, method, mode) for r in range(args.later_repeats+1) for method in METHODS for mode in MODES}
    started = time.monotonic()
    harness_error = None
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
                    row.update(run_attempt(cmd, env, args.cpu, args.out / name))
                    try:
                        if (job / "JOB_RECEIPT.json").exists():
                            row.update(collect(job))
                        else:
                            row.update(execution="FAILED_BEFORE_JOB_RECEIPT")
                    except BaseException as error:
                        row.update(execution="FAILED_RESULT_COLLECTION", collection_error_class=type(error).__name__,
                                   collection_error=str(error))
                        with (args.out / (name+".COLLECTION_FAILURE.log")).open("x") as stream:
                            stream.write(traceback.format_exc())
                    if row["timed_out"]:
                        row["execution"] = "TIMED_OUT"
                    elif not row["cleanup"]["complete"]:
                        row["execution"] = "OWNED_CLEANUP_INCOMPLETE"
                    elif row["exit_code"] != 0 and row["execution"] == "COMPLETE":
                        row["execution"] = "RUNNER_EXIT_NONZERO_WITH_COMPLETE_RECEIPT"
                    rows.append(row)
                    new(args.out / (name + ".OBSERVATION.json"), row)
                    print(json.dumps({k: row[k] for k in ("round", "method", "mode", "execution", "process_wall_s")}), flush=True)
                    if (row["timed_out"] or row["interrupted"] or row.get("error_class")
                            or row["execution"] in ("FAILED_RESULT_COLLECTION", "OWNED_CLEANUP_INCOMPLETE")):
                        raise RuntimeError("STOP_AFTER_RECORDED_HARNESS_FAILURE " + name)
    except BaseException as error:
        harness_error = {"error_class": type(error).__name__, "error": str(error)}
        with (args.out / "HARNESS_FAILURE.log").open("x") as stream:
            stream.write(traceback.format_exc())
    finally:
        result = finish_run(args.out, before, rows, args.bridge, args.build_receipt,
                            expected_keys, started, harness_error)
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
