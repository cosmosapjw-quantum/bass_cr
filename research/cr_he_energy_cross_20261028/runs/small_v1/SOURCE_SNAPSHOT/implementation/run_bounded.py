"""Serial measured science runner. Prior unit budgets are never read or changed."""
import argparse
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

UNIT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def cpu_self():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["small", "native", "independent", "plot"])
    p.add_argument("--run-id", required=True)
    p.add_argument("--reservation", type=float, required=True)
    args = p.parse_args()
    with (UNIT / "runs/.budget.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        budget = json.loads((UNIT / "BUDGET.json").read_text())
        if budget["science_closed"] or not 0 < args.reservation <= budget["remaining_cpu_s"]:
            raise SystemExit("OWN_UNIT_BUDGET_REFUSAL")
        out = UNIT / "runs" / args.run_id
        out.mkdir(exist_ok=False)
        files = list((UNIT / "implementation").glob("*.py")) + list((UNIT / "reference").glob("*.py"))
        manifest = {str(f.relative_to(UNIT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
        write(out / "SOURCE_MANIFEST.json", manifest)
        cmd = [sys.executable, str(UNIT / "implementation/worker.py"), args.mode, str(out)]
        write(out / "COMMAND.json", {"argv": cmd, "reservation_cpu_s": args.reservation,
            "memory_bytes": 536870912, "wall_s": 50, "threads": 1})
        env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
            MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1", MPLCONFIGDIR=str(out / "mpl"))
        def limits():
            cap = max(1, math.floor(args.reservation - 0.25))
            resource.setrlimit(resource.RLIMIT_CPU, (cap, cap))
            resource.setrlimit(resource.RLIMIT_AS, (536870912, 536870912))
            if hasattr(os, "sched_getaffinity"):
                os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        c0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        s0, t0 = cpu_self(), time.monotonic()
        failure = None
        with (out / "stdout.txt").open("w") as stdout, (out / "stderr.txt").open("w") as stderr:
            process = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, env=env, preexec_fn=limits)
            try:
                code = process.wait(timeout=50)
            except subprocess.TimeoutExpired:
                process.kill()
                code = process.wait()
                failure = "WALL_TIMEOUT"
        c1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        coordinator = cpu_self() - s0
        worker = c1.ru_utime + c1.ru_stime - c0.ru_utime - c0.ru_stime
        measured = worker + coordinator
        charge = math.ceil((measured + 0.05) * 1e6) / 1e6
        if code != 0:
            failure = failure or f"WORKER_EXIT_{code}"
        result = None
        if (out / "RESULT.json").exists():
            result = json.loads((out / "RESULT.json").read_text())
        if result is None or not str(result.get("status", "")).startswith("PASS"):
            failure = failure or "MISSING_OR_FAILED_SCIENCE_RESULT"
        final = {str(f.relative_to(UNIT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
        if final != manifest:
            failure = "SOURCE_CHANGED_DURING_EXECUTION"
        if charge > args.reservation:
            failure = failure or "RESERVATION_EXCEEDED"
        receipt = {"run_id": args.run_id, "mode": args.mode, "status": "FAIL" if failure else "PASS",
            "failure": failure, "exit_code": code, "reservation_cpu_s": args.reservation,
            "worker_cpu_s": worker, "coordinator_cpu_s": coordinator, "measured_cpu_s": measured,
            "charged_cpu_s": charge, "tail_cpu_s": charge - measured, "wall_s": time.monotonic() - t0,
            "source_unchanged": final == manifest, "utc": datetime.now(timezone.utc).isoformat(),
            "max_child_rss_kib": c1.ru_maxrss, "preventive_aggregate_hard_cap_proof": False}
        write(out / "RECEIPT.json", receipt)
        budget["attempts"].append(receipt)
        budget["charge_cpu_s"] = round(budget["charge_cpu_s"] + charge, 6)
        budget["remaining_cpu_s"] = round(budget["cap_cpu_s"] - budget["charge_cpu_s"], 6)
        write(UNIT / "BUDGET.json", budget)
        print(json.dumps(receipt))
        raise SystemExit(1 if failure else 0)


if __name__ == "__main__":
    main()
