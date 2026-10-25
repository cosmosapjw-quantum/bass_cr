"""Create-only bounded interface verification; no historical science replay."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import io
import json
import os
import math
from pathlib import Path
import resource
import shutil
import signal
import sys
import time
import traceback
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def prior_attempt_costs(runs: Path, current: Path) -> list[float]:
    """An interrupted/missing receipt is unknown cost, never an unused allowance."""
    costs = []
    for directory in sorted(runs.iterdir()):
        if not directory.is_dir() or directory == current:
            continue
        receipt = directory / "RECEIPT.json"
        if not receipt.is_file():
            raise RuntimeError(f"UNKNOWN_PRIOR_ATTEMPT_BUDGET: {directory.name}")
        cost = json.loads(receipt.read_text()).get("CPU_s")
        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
            raise RuntimeError(f"INVALID_PRIOR_ATTEMPT_BUDGET: {directory.name}")
        costs.append(float(cost))
    return costs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not args.run_id.replace("_", "").replace("-", "").isalnum():
        raise ValueError("simple non-path run ID required")
    out = HERE / "runs" / args.run_id
    out.mkdir(parents=True, exist_ok=False)
    start, cpu0 = time.monotonic(), time.process_time()
    previous = prior_attempt_costs(HERE / "runs", out)
    remaining = 30.0 - sum(previous)
    affinity = sorted(os.sched_getaffinity(0))
    cpus = [c for c in affinity if c != 55]
    worker = 1 if 1 in cpus else cpus[0]
    if len(cpus) < 2 or remaining <= 0:
        raise RuntimeError("CPU/budget admission unavailable")
    cg = Path("/sys/fs/cgroup")
    limit = int((cg / "memory.max").read_text())
    current = int((cg / "memory.current").read_text())
    stat = {k: int(v) for k, v in (x.split() for x in (cg / "memory.stat").read_text().splitlines())}
    available_estimate = limit - current + stat.get("inactive_file", 0)
    admission = {"observed_utc": datetime.now(timezone.utc).isoformat(), "affinity": affinity,
                 "worker_CPU": worker, "coordinator_reserved_CPU": cpus[-1], "protected_CPU": 55,
                 "cpu_max": (cg / "cpu.max").read_text().strip(),
                 "memory_max_B": limit, "memory_current_B": current,
                 "inactive_file_reclaimable_estimate_B": stat.get("inactive_file", 0),
                 "available_with_inactive_file_estimate_B": available_estimate,
                 "RAM_cap_B": 512 * 1024**2, "reserve_B": 1024**3,
                 "new_unit_CPU_cap_s": 30, "remaining_unit_CPU_before_s": remaining,
                 "previous_attempt_CPU_s": previous, "native_threads": 1,
                 "estimated_memory_not_raw_free_memory": True}
    dump(out / "RESOURCE_ADMISSION.json", admission)
    if available_estimate < 512 * 1024**2 + 1024**3:
        raise RuntimeError("RAM cap plus reserve unavailable under observed cache estimate")
    os.sched_setaffinity(0, {worker})
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, int(remaining)), max(2, int(remaining) + 1)))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    source_manifest = {}
    for name in ("contracts.py", "consume_saved.py", "test_contracts.py", "run_checks.py"):
        raw = (HERE / name).read_bytes()
        source_manifest[name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    dump(out / "EXECUTED_SOURCE_MANIFEST.json", source_manifest)
    (out / "EXECUTED_SOURCE").mkdir()
    for name in source_manifest:
        shutil.copyfile(HERE / name, out / "EXECUTED_SOURCE" / name)
    def timeout_handler(_signum, _frame):
        raise TimeoutError("external interface wall limit60s exceeded")
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)
    stream = io.StringIO()
    passed = False
    try:
        import test_contracts
        from consume_saved import consume_all, PINS
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromModule(test_contracts))
        (out / "TEST_LOG.txt").write_text(stream.getvalue())
        dump(out / "INPUT_MANIFEST.json", {k: asdict(v) for k, v in PINS.items()})
        if not result.wasSuccessful():
            raise RuntimeError("targeted interface controls failed")
        actual = consume_all(ROOT)
        dump(out / "RESULT.json", actual)
        passed = True
        summary = {"targeted_tests": result.testsRun, "C23B_atoms": actual["C23B"]["source_atoms_consumed"],
                   "C23B_cases": len(actual["C23B"]["cases"]),
                   "C23E_saved_points": actual["C23E"]["saved_points_consumed"],
                   "C23E_saved_events": actual["C23E"]["saved_events_consumed"],
                   "C23E_max_normalized_transfer": actual["C23E"]["max_transfer_error_normalized"]}
    except Exception:
        (out / "FAILURE.txt").write_text(traceback.format_exc())
        summary = {"failure": traceback.format_exc()}
    finally:
        signal.alarm(0)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        receipt = {"status": "PASS_SCOPED" if passed else "FAIL", "command": sys.argv,
                   "CPU_s": time.process_time() - cpu0, "wall_s": time.monotonic() - start,
                   "peak_RSS_KiB": usage.ru_maxrss, "python": sys.version,
                   "old_source_quadrature": 0, "old_rate_evaluation": 0, "new_ODE": 0,
                   "new_source_quadrature": 0, "old_solver_replay": 0, **summary}
        dump(out / "RECEIPT.json", receipt)
        print(json.dumps(receipt, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
