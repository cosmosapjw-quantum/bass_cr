"""Create-only bounded launcher with retained failures and complete attempt costs.

Worker ceilings and the 2 s local-misc reservation are cumulative across retries.
A missing or invalid receipt is UNKNOWN_PRIOR_ATTEMPT_BUDGET, never unused credit.
Only this launcher's owned child process group may be terminated.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import sys
import time

THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
OMP_CONTROLS = {"OMP_DYNAMIC": "FALSE", "OMP_NESTED": "FALSE", "OMP_MAX_ACTIVE_LEVELS": "1"}
MODES = {"controls": "test", "primary": "primary", "review": "review", "plot": "plot"}


def writej(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def finite_cost(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError("invalid attempt cost")
    return float(value)


def prior_attempts(runs, current=None):
    receipts = []
    if not runs.exists():
        return receipts
    for directory in sorted(runs.iterdir()):
        if not directory.is_dir() or directory == current:
            continue
        try:
            row = json.loads((directory / "DISPATCH_RECEIPT.json").read_text())
            if row["run_id"] != directory.name or row["mode"] not in MODES:
                raise ValueError("run identity")
            finite_cost(row["worker_cpu_s"])
            finite_cost(row["coordinator_cpu_s"])
        except (OSError, ValueError, TypeError, KeyError):
            raise RuntimeError("UNKNOWN_PRIOR_ATTEMPT_BUDGET:" + directory.name)
        receipts.append(row)
    return receipts


def preparation_costs(unit):
    root = unit / "preparations"
    if not root.is_dir():
        raise RuntimeError("UNKNOWN_PRIOR_ATTEMPT_BUDGET:preparation ledger absent")
    values = []
    for directory in sorted(root.iterdir()):
        if not directory.is_dir():
            continue
        try:
            row = json.loads((directory / "PREPARATION_RECEIPT.json").read_text())
            if row["run_id"] != directory.name:
                raise ValueError("preparation identity")
            values.append(finite_cost(row["process_cpu_s"]))
        except (OSError, ValueError, TypeError, KeyError):
            raise RuntimeError("UNKNOWN_PRIOR_ATTEMPT_BUDGET:" + directory.name)
    if not values:
        raise RuntimeError("UNKNOWN_PRIOR_ATTEMPT_BUDGET:empty preparation ledger")
    return values


def acquire_lease(lease, payload):
    with lease.open("x") as stream:
        json.dump(payload, stream, allow_nan=False)
        stream.write("\n")


def process_memory_snapshot():
    """Actual process RSS/virtual size, distinct from aggregate cgroup usage."""
    fields = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in ("VmRSS", "VmSize", "VmHWM", "VmPeak"):
            amount, unit = value.split()
            if unit != "kB":
                raise RuntimeError("UNRECOGNIZED_PROCESS_MEMORY_UNIT")
            fields[key + "_bytes"] = int(amount) * 1024
    if set(fields) != {key + "_bytes" for key in ("VmRSS", "VmSize", "VmHWM", "VmPeak")}:
        raise RuntimeError("PROCESS_MEMORY_READBACK_INCOMPLETE")
    return {"pid": os.getpid(), "source": "/proc/self/status", **fields}


def snapshot(resources):
    group = Path("/sys/fs/cgroup")
    stats = {key: int(value) for key, value in (line.split() for line in (group / "memory.stat").read_text().splitlines())}
    maximum_text = (group / "memory.max").read_text().strip()
    if not maximum_text.isdecimal():
        raise RuntimeError("FINITE_OBSERVED_MEMORY_LIMIT_REQUIRED")
    maximum, current = int(maximum_text), int((group / "memory.current").read_text())
    excluded = sum(stats.get(key, 0) for key in ("file_dirty", "file_writeback", "shmem", "unevictable"))
    inactive, active = stats.get("inactive_file", 0), stats.get("active_file", 0)
    clean_inactive = max(0, inactive - excluded)
    clean_active = max(0, active - max(0, excluded - inactive))
    estimate = max(0, maximum - current) + clean_inactive + clean_active // 2 - resources["memory_reserve_bytes"]
    return {"observed_utc": datetime.now(timezone.utc).isoformat(),
            "affinity": sorted(os.sched_getaffinity(0)), "cpu_max": (group / "cpu.max").read_text().strip(),
            "memory_max_bytes": maximum, "memory_current_bytes": current,
            "clean_inactive_file_bytes": clean_inactive, "clean_active_file_bytes": clean_active,
            "active_file_reclaimability_fraction": .5,
            "excluded_dirty_writeback_shmem_unevictable_bytes": excluded,
            "memory_reserve_bytes": resources["memory_reserve_bytes"],
            "memory_available_after_reserve": estimate,
            "memory_admitted": estimate >= resources["RLIMIT_AS_bytes"],
            "coordinator_process_memory": process_memory_snapshot(),
            "simultaneous_owned_workers": 1,
            "memory_aggregate_note": (
                "memory.current includes the coordinator and other cgroup residents; "
                "one owned worker runs sequentially; the 1 GiB reserve covers coordinator "
                "growth and nonreclaimable growth beyond this snapshot"),
            "memory_events": (group / "memory.events").read_text(),
            "estimated_cache_reclaimability_not_raw_free_memory": True,
            "admission_revision": "inherited clean inactive + half clean active; exclusions allocated once",
            "external_NCP": "UNOBSERVED"}


def validate_resources(r):
    expected = {"new_unit_total_cpu_s": 30.0, "test_cpu_s": 5, "primary_cpu_s": 8,
                "review_cpu_s": 10, "plot_cpu_s": 5, "misc_cpu_s": 2,
                "wall_s": 60, "worker_cpu": 0, "reviewer_cpu": 2, "coordinator_cpu": 8,
                "native_threads": 1, "RLIMIT_AS_bytes": 512 * 1024**2,
                "memory_reserve_bytes": 1024**3}
    if any(r.get(key) != value or isinstance(r.get(key), bool) for key, value in expected.items()):
        raise ValueError("FROZEN_RESOURCE_RESERVATION_MISMATCH")


def authorize_run(unit, config, mode, runid):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", runid):
        raise ValueError("SIMPLE_NONPATH_RUN_ID_REQUIRED")
    expected = config[MODES[mode] + "_run_id"]
    if runid == expected:
        return
    path = unit / "implementation/RUN_AUTHORIZATIONS.json"
    data = json.loads(path.read_text())
    if not any(row.get("mode") == mode and row.get("original_run_id") == expected
               and row.get("authorized_run_id") == runid and row.get("reason")
               for row in data.get("runs", [])):
        raise ValueError("RUN_ID_NOT_AUTHORIZED")


def selected_input_run(unit, config, mode):
    """A retained retry becomes a downstream input only by explicit selection."""
    expected = config[MODES[mode] + "_run_id"]
    path = unit / "implementation/RUN_AUTHORIZATIONS.json"
    if not path.exists():
        return expected
    selection = json.loads(path.read_text()).get("selected_input_runs", {}).get(mode, expected)
    authorize_run(unit, config, mode, selection)
    return selection


def run(unit, runid, mode):
    config = json.loads((unit / "inputs/CONFIG.json").read_text())
    r = config["resources"]
    validate_resources(r)
    authorize_run(unit, config, mode, runid)
    out = unit / "runs" / runid
    out.mkdir(parents=True, exist_ok=False)
    here, lease = unit / "implementation", unit / "implementation/.heiii_task_lease"
    leased = started = False
    child = None
    returncode = error = command = None
    status = "FAILED_RETAINED"
    wall_start = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    worker = r["reviewer_cpu"] if mode == "review" else r["worker_cpu"]
    original_affinity = os.sched_getaffinity(0)
    used = stage_used = misc_used = limit = None
    try:
        acquire_lease(lease, {"pid": os.getpid(), "run_id": runid, "mode": mode,
                              "created_utc": datetime.now(timezone.utc).isoformat()})
        leased = True
        state = snapshot(r)
        writej(out / "RESOURCE_ADMISSION.json", state)
        if not state["memory_admitted"]:
            raise RuntimeError("MEMORY_ADMISSION_REJECTED")
        required_cpus = {r["worker_cpu"], r["reviewer_cpu"], r["coordinator_cpu"]}
        if len(required_cpus) != 3 or not required_cpus.issubset(state["affinity"]) or 55 in required_cpus:
            raise RuntimeError("CPU_ADMISSION_REJECTED")
        quota, period = state["cpu_max"].split()
        if quota != "max" and int(quota) / int(period) < 2:
            raise RuntimeError("COORDINATOR_AND_WORKER_QUOTA_REQUIRED")
        previous = prior_attempts(unit / "runs", out)
        prepared = preparation_costs(unit)
        stage_used = sum(row["worker_cpu_s"] for row in previous if row["mode"] == mode)
        misc_used = sum(prepared) + sum(row["coordinator_cpu_s"] for row in previous)
        used = sum(prepared) + sum(row["worker_cpu_s"] + row["coordinator_cpu_s"] for row in previous)
        available = min(r[MODES[mode] + "_cpu_s"] - stage_used, r["new_unit_total_cpu_s"] - used)
        limit = math.floor(available)
        if limit < 1 or misc_used + time.process_time() >= r["misc_cpu_s"]:
            raise RuntimeError("NEW_UNIT_CPU_RESERVATION_EXHAUSTED")
        if used + limit + max(0, r["misc_cpu_s"] - misc_used) > r["new_unit_total_cpu_s"]:
            raise RuntimeError("NEW_UNIT_CPU_CEILING")
        review = json.loads((unit / "review/R6_THEORY.json").read_text())
        if review.get("decision") != "PASS_SCOPED_AFTER_TARGETED_REPAIR":
            raise ValueError("R6_PASS_REQUIRED")
        if mode in ("review", "plot"):
            result = json.loads((unit / "runs" / selected_input_run(unit, config, "primary") / "RESULT.json").read_text())
            if result.get("status") != "PASS" or result.get("actual_primary_RHS") != 224:
                raise RuntimeError("PRIMARY_PASS_REQUIRED")
        os.sched_setaffinity(0, {r["coordinator_cpu"]})
        source_dir = out / "EXECUTED_SOURCE"
        source_dir.mkdir()
        sources = sorted(here.glob("*.py"))
        if mode == "review":
            sources.append(unit / "review/c9_independent.py")
        pins = []
        for source in sources:
            raw = source.read_bytes()
            with (source_dir / source.name).open("xb") as stream:
                stream.write(raw)
            pins.append({"path": str(source.relative_to(unit)), "bytes": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest()})
        for path in (unit / "inputs/CONFIG.json", unit / "inputs/INPUT_MANIFEST.json",
                     unit / "FROZEN_CONTRACT.md", unit / "THEORY_KO.md"):
            with (source_dir / path.name).open("xb") as stream:
                stream.write(path.read_bytes())
        auth = here / "RUN_AUTHORIZATIONS.json"
        if auth.exists():
            with (source_dir / auth.name).open("xb") as stream:
                stream.write(auth.read_bytes())
        if mode == "review":
            command = [sys.executable, "-B", str(source_dir / "c9_independent.py"),
                       "--unit-dir", str(unit), "--primary-dir", str(unit / "runs" / selected_input_run(unit, config, "primary")),
                       "--controls-dir", str(unit / "runs" / selected_input_run(unit, config, "controls")), "--out-dir", str(out)]
        else:
            script = {"controls": "controls.py", "primary": "primary.py", "plot": "plot_saved.py"}[mode]
            command = [sys.executable, "-B", str(source_dir / script), "--unit", str(unit),
                       "--output", str(out), "--run-id", runid]
        writej(out / "PRE_EXECUTION.json", {
            "run_id": runid, "mode": mode, "source_pins": pins, "command": command,
            "CPU_limit_s": limit, "wall_limit_s": r["wall_s"], "RLIMIT_AS_bytes": r["RLIMIT_AS_bytes"],
            "worker_cpu": worker, "coordinator_cpu": r["coordinator_cpu"], "native_threads": 1,
            "native_thread_environment": {key: "1" for key in THREADS},
            "openmp_controls": OMP_CONTROLS,
            "new_unit_already_charged_cpu_s": used, "stage_already_charged_worker_cpu_s": stage_used,
            "misc_already_charged_cpu_s": misc_used, "new_unit_ceiling_cpu_s": 30,
            "historical_allowance_reused": False, "all_prior_attempts_with_receipts_required": True})
        environment = os.environ.copy()
        environment.update({key: "1" for key in THREADS})
        environment.update(OMP_CONTROLS)
        environment.update(PYTHONDONTWRITEBYTECODE="1", MPLCONFIGDIR=str(out / "mpl_config"))

        def limits():
            os.sched_setaffinity(0, {worker})
            resource.setrlimit(resource.RLIMIT_AS, (r["RLIMIT_AS_bytes"], r["RLIMIT_AS_bytes"]))
            resource.setrlimit(resource.RLIMIT_CPU, (limit, limit))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

        with (out / "stdout.txt").open("x") as stdout, (out / "stderr.txt").open("x") as stderr:
            child = subprocess.Popen(command, cwd=source_dir, env=environment, stdout=stdout,
                                     stderr=stderr, preexec_fn=limits, start_new_session=True)
            started = True
            try:
                returncode = child.wait(timeout=max(.01, r["wall_s"] - (time.monotonic() - wall_start)))
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    returncode = child.wait(timeout=.5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    returncode = child.wait()
                raise RuntimeError("OWNED_CHILD_WALL_LIMIT")
        status = "PASS" if returncode == 0 else "FAILED_RETAINED"
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            returncode = child.wait()
        if leased:
            lease.unlink()
        os.sched_setaffinity(0, original_affinity)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        worker_cost = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
        coordinator_cost = time.process_time()
        if ((stage_used is not None and stage_used + worker_cost > r[MODES[mode] + "_cpu_s"])
                or (misc_used is not None and misc_used + coordinator_cost > r["misc_cpu_s"])
                or (used is not None and used + worker_cost + coordinator_cost > r["new_unit_total_cpu_s"])):
            status = "FAILED_RETAINED"
            error = {"type": "ResourceBudgetExceeded", "message": "MEASURED_NEW_UNIT_OR_STAGE_CPU_CEILING"}
        receipt = {
            "schema": "CR_HEIII_BOUNDED_DISPATCH_V1", "run_id": runid, "mode": mode,
            "status": status, "error": error, "child_started": started, "returncode": returncode,
            "command": command, "worker_cpu_s": worker_cost,
            "worker_peak_RSS_KiB": after.ru_maxrss if started else None,
            "coordinator_cpu_s": coordinator_cost, "wall_s": time.monotonic() - wall_start,
            "CPU_limit_s": limit, "wall_limit_s": r["wall_s"],
            "new_unit_previously_charged_cpu_s": used,
            "new_unit_cumulative_cpu_s": used + worker_cost + coordinator_cost if used is not None else None,
            "historical_known_lineage_cpu_s": r["inherited_known_lineage_cpu_s"],
            "separate_C23E_cpu_s": r["separate_C23E_lineage_cpu_s"],
            "prior_HeI_completed_unit_cpu_s": r["prior_HeI_completed_unit_cpu_s"],
            "historical_allowance_reused": False, "global_remaining": None, "currency": None,
            "EXECUTION": status, "PUBLICATION": "ROOT_OWNED", "BACKUP": "ROOT_PENDING",
            "DAG": "N5_PARTIAL_OPEN_N6_N7_PREDECESSOR_GATED"}
        writej(out / "DISPATCH_RECEIPT.json", receipt)
    print(json.dumps({"output": str(out), **receipt}))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=tuple(MODES), required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.unit.resolve(), args.run_id, args.mode))
