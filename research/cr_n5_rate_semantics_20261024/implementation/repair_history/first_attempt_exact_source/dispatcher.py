"""Create-only, leased, resource-bounded test/science child dispatcher."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import sys
import time


MIB = 1024 * 1024
THREAD_ENV = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def create_output(root, run_id):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_\-]{0,119}", run_id):
        raise ValueError("INVALID_RUN_ID")
    root.mkdir(parents=True, exist_ok=True)
    output = root / run_id
    output.mkdir(exist_ok=False)
    return output


def memory_admission(current, maximum, inactive_file, dirty, writeback):
    if any(isinstance(x, bool) or not isinstance(x, int) or x < 0
           for x in (current, maximum, inactive_file, dirty, writeback)):
        raise ValueError("INVALID_MEMORY_COUNTER")
    headroom = max(0, maximum - current)
    clean_reclaimable = max(0, inactive_file - dirty - writeback)
    available_after_reserve = headroom + clean_reclaimable - 64 * MIB
    return {"headroom_bytes": headroom, "clean_inactive_file_reclaimable_bytes": clean_reclaimable,
            "worker_reserve_bytes": 64 * MIB, "required_after_reserve_bytes": 256 * MIB,
            "available_after_reserve_bytes": available_after_reserve,
            "admitted": available_after_reserve >= 256 * MIB}


def resource_snapshot():
    cg = Path("/sys/fs/cgroup")
    maximum_text = (cg / "memory.max").read_text().strip()
    if maximum_text == "max":
        raise RuntimeError("FINITE_CGROUP_MEMORY_LIMIT_REQUIRED")
    current = int((cg / "memory.current").read_text())
    maximum = int(maximum_text)
    stats = dict((key, int(value)) for key, value in (line.split() for line in (cg / "memory.stat").read_text().splitlines()))
    check = memory_admission(current, maximum, stats.get("inactive_file", 0), stats.get("file_dirty", 0), stats.get("file_writeback", 0))
    affinity = sorted(os.sched_getaffinity(0))
    processes = []
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            try:
                name = (entry / "comm").read_text().strip()
                if any(token in name for token in ("python", "rust", "cargo", "gcc", "g++", "cc1", "worker")):
                    processes.append({"pid": int(entry.name), "comm": name})
            except (FileNotFoundError, PermissionError):
                pass
    return {"cgroup_memory_current": current, "cgroup_memory_max": maximum,
            "cgroup_memory_selected_stat": {key: stats.get(key) for key in ("anon", "file", "inactive_file", "file_dirty", "file_writeback")},
            "memory_admission": check, "affinity": affinity, "cgroup_cpu_max": (cg / "cpu.max").read_text().strip(),
            "relevant_processes": processes, "coordinator_cpu": 8, "worker_cpu": 0,
            "native_threads": 1, "cpu_limit_s": 30, "wall_limit_s": 60,
            "address_space_limit_bytes": 512 * MIB, "external_NCP_lease": "UNOBSERVED"}


def child_limits():
    os.sched_setaffinity(0, {0})
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_AS, (512 * MIB, 512 * MIB))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def dispatch(unit, run_id, mode):
    here = Path(__file__).resolve().parent
    output = create_output(here / "runs", run_id)
    start_wall, start_cpu = time.monotonic(), time.process_time()
    lease = here / ".n5_local_lease"
    lease_acquired = False
    child_returncode = None
    status, error = "NOT_RUN", None
    before_child = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        descriptor = os.open(lease, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "w") as handle:
            handle.write(json.dumps({"pid": os.getpid(), "run_id": run_id, "mode": mode}))
        lease_acquired = True
        snapshot = resource_snapshot()
        if not snapshot["memory_admission"]["admitted"]:
            raise RuntimeError("MEMORY_ADMISSION_REJECTED")
        if not {0, 8}.issubset(set(snapshot["affinity"])):
            raise RuntimeError("DECLARED_CPU_AFFINITY_UNAVAILABLE")
        source_pins = [{"path": str(path.relative_to(unit)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
                       for path in sorted(here.glob("*.py"))]
        manifest = unit / "inputs/INPUT_MANIFEST.json"
        write_json(output / "PRE_EXECUTION.json", {"run_id": run_id, "mode": mode,
                    "utc": datetime.now(timezone.utc).isoformat(), "resource_snapshot": snapshot,
                    "source_pins": source_pins, "input_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                    "inherited_known_lineage_worker_cpu_s": 15.493261114,
                    "global_spend": None, "remaining": None, "currency": None})
        os.sched_setaffinity(0, {8})
        env = os.environ.copy()
        env.update({key: "1" for key in THREAD_ENV})
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        if mode == "test":
            command = [sys.executable, "-B", str(here / "tests.py"), "--output", str(output)]
        else:
            command = [sys.executable, "-B", str(here / "run_diagnostic.py"), "--unit", str(unit), "--output", str(output), "--run-id", run_id]
        with (output / "stdout.txt").open("x") as stdout, (output / "stderr.txt").open("x") as stderr:
            child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env,
                                     cwd=str(here), preexec_fn=child_limits, start_new_session=True)
            try:
                child_returncode = child.wait(timeout=60)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child_returncode = child.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child_returncode = child.wait()
                raise RuntimeError("OWNED_CHILD_WALL_LIMIT_EXCEEDED")
        status = "PASS" if child_returncode == 0 else "FAILED_RETAINED"
    except Exception as exc:
        status, error = "FAILED_RETAINED", {"type": type(exc).__name__, "message": str(exc)}
    finally:
        if lease_acquired:
            lease.unlink()
        after_child = resource.getrusage(resource.RUSAGE_CHILDREN)
        receipt = {"schema": "N5_BOUNDED_DISPATCH_RECEIPT_V1", "run_id": run_id, "mode": mode,
                   "status": status, "error": error, "child_returncode": child_returncode,
                   "worker_cpu_s": (after_child.ru_utime + after_child.ru_stime) - (before_child.ru_utime + before_child.ru_stime),
                   "worker_peak_rss_kib": after_child.ru_maxrss,
                   "coordinator_cpu_s": time.process_time() - start_cpu,
                   "wall_s": time.monotonic() - start_wall,
                   "inherited_known_lineage_worker_cpu_s": 15.493261114,
                   "global_spend": None, "remaining": None, "currency": None,
                   "new_ODE": 0, "old_science_replays": 0, "new_source_quadratures": 0,
                   "EXECUTION": status, "PUBLICATION": "PARENT_OWNED_NOT_ATTEMPTED",
                   "BACKUP": "PARENT_OWNED_PENDING", "DAG": "N5_SCOPED_CHILD;N6_N7_OPEN"}
        write_json(output / "DISPATCH_RECEIPT.json", receipt)
    print(json.dumps({"output": str(output), **receipt}))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--mode", choices=("test", "science"), required=True)
    args = parser.parse_args()
    raise SystemExit(dispatch(args.unit.resolve(), args.run_id, args.mode))
