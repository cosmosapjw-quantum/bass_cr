"""Serial local science ledger, including preparation, compiler and descendants."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import fcntl
import hashlib
import json
import math
import os
import resource
import shutil
import signal
import subprocess
import sys
import time

UNIT = Path(__file__).resolve().parents[1]
MEMORY = 536870912
TAIL = 0.10


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def self_cpu():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def tree_usage(root_pid):
    """Live own CPU plus waited child CPU; sample is conservative, not atomic."""
    stack, seen, ticks, rss = [root_pid], set(), 0, 0
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        try:
            raw = Path(f"/proc/{pid}/stat").read_text()
            fields = raw[raw.rfind(")") + 2:].split()
            ticks += sum(int(fields[i]) for i in (11, 12, 13, 14))
            rss += max(0, int(fields[21])) * os.sysconf("SC_PAGE_SIZE")
            stack.extend(map(int, Path(f"/proc/{pid}/task/{pid}/children").read_text().split()))
        except (FileNotFoundError, ProcessLookupError):
            pass
    return ticks / os.sysconf("SC_CLK_TCK"), rss


def main():
    wall_start = time.monotonic()
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["compile", "controls", "native", "independent", "plot"])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--reservation", type=float, required=True)
    args = parser.parse_args()
    (UNIT / "runs").mkdir(exist_ok=True)
    with (UNIT / "runs/.budget.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        budget = json.loads((UNIT / "BUDGET.json").read_text())
        if budget["science_closed"] or not 0.5 < args.reservation <= budget["remaining_cpu_s"]:
            raise SystemExit("OWN_UNIT_BUDGET_REFUSAL")
        out = UNIT / "runs" / args.run_id
        out.mkdir(exist_ok=False)
        files = sorted((UNIT / "implementation").glob("*.py")) + sorted((UNIT / "implementation").glob("*.cpp"))
        files += sorted((UNIT / "reference").glob("*.py"))
        manifest = {str(p.relative_to(UNIT)): sha(p) for p in files}
        write(out / "SOURCE_MANIFEST.json", manifest)
        for name in manifest:
            dest = out / "SOURCE_SNAPSHOT" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(UNIT / name, dest)
        inputs = {str(p.relative_to(UNIT)): sha(p) for p in sorted((UNIT / "inputs").glob("*")) if p.is_file()}
        write(out / "INPUT_MANIFEST.json", inputs)
        command = [sys.executable, str(UNIT / "implementation/worker.py"), args.mode, str(out)]
        cpu_limit = max(1, math.floor(args.reservation - 0.25))
        write(out / "COMMAND.json", {"argv": command, "reservation_cpu_s": args.reservation,
            "RLIMIT_AS_per_process_bytes": MEMORY, "sampled_descendant_RSS_limit_bytes": MEMORY,
            "RLIMIT_CPU_per_process_s": cpu_limit, "wall_limit_s": 50, "threads": 1,
            "aggregate_CPU_watchdog_poll_s": 0.05, "aggregate_CPU_watchdog_margin_s": 0.20})
        env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1",
                   NUMEXPR_NUM_THREADS="1", MPLCONFIGDIR=str(out / "mpl"), PYTHONDONTWRITEBYTECODE="1")
        def limits():
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
            resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
            if hasattr(os, "sched_getaffinity"):
                os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        failure, code, peak_sampled_rss = None, None, 0
        launch = time.monotonic()
        with (out / "stdout.txt").open("w") as stdout, (out / "stderr.txt").open("w") as stderr:
            try:
                proc = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env,
                                        preexec_fn=limits, start_new_session=True)
                while proc.poll() is None:
                    child_cpu, rss = tree_usage(proc.pid)
                    peak_sampled_rss = max(peak_sampled_rss, rss)
                    if child_cpu + self_cpu() >= args.reservation - 0.20:
                        failure = "AGGREGATE_CPU_WATCHDOG"
                    elif rss > MEMORY:
                        failure = "DESCENDANT_RSS_WATCHDOG"
                    elif time.monotonic() - launch >= 50:
                        failure = "WALL_TIMEOUT"
                    if failure:
                        try:
                            os.killpg(proc.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        break
                    time.sleep(0.05)
                code = proc.wait()
            except Exception as exc:
                failure = f"LAUNCH_OR_MONITOR_ERROR:{type(exc).__name__}:{exc}"
                if "proc" in locals() and proc.poll() is None:
                    os.killpg(proc.pid, signal.SIGKILL)
                    code = proc.wait()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        worker = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
        if code != 0:
            failure = failure or f"WORKER_EXIT_{code}"
        try:
            result = json.loads((out / "RESULT.json").read_text())
            if not str(result.get("status", "")).startswith("PASS"):
                failure = failure or "NONPASS_SCIENCE_RESULT"
        except Exception as exc:
            failure = failure or f"MISSING_OR_INVALID_RESULT:{type(exc).__name__}"
        final = {str(p.relative_to(UNIT)): sha(p) for p in files}
        final_inputs = {name: sha(UNIT / name) for name in inputs}
        if final != manifest or final_inputs != inputs:
            failure = failure or "SOURCE_OR_INPUT_CHANGED_DURING_EXECUTION"
        write(out / "FINAL_SOURCE_MANIFEST.json", final)
        coordinator = self_cpu()  # Includes interpreter startup and all preparation in this runner.
        measured = worker + coordinator
        charge = math.ceil((measured + TAIL) * 1e6) / 1e6
        if charge > args.reservation:
            failure = failure or "RESERVATION_EXCEEDED"
        receipt = {"run_id": args.run_id, "mode": args.mode, "status": "FAIL" if failure else "PASS",
            "failure": failure, "exit_code": code, "reservation_cpu_s": args.reservation,
            "worker_and_waited_descendants_cpu_s": worker, "coordinator_including_preparation_cpu_s": coordinator,
            "measured_cpu_s": measured, "charged_cpu_s": charge, "tail_cpu_s": charge-measured,
            "wall_s": time.monotonic()-wall_start, "max_child_rss_kib": after.ru_maxrss,
            "peak_sampled_descendant_rss_bytes": peak_sampled_rss,
            "source_unchanged": final == manifest, "inputs_unchanged": final_inputs == inputs,
            "utc": datetime.now(timezone.utc).isoformat(), "preventive_aggregate_hard_cap_proof": False,
            "guard_scope": "Serial reservation, per-process limits and sampled process-tree watchdog; sampling is not an atomic aggregate hard-cap proof"}
        write(out / "RECEIPT.json", receipt)
        budget["attempts"].append(receipt)
        budget["charge_cpu_s"] = round(budget["charge_cpu_s"]+charge, 6)
        budget["remaining_cpu_s"] = round(budget["cap_cpu_s"]-budget["charge_cpu_s"], 6)
        write(UNIT / "BUDGET.json", budget)
        print(json.dumps(receipt))
        raise SystemExit(1 if failure else 0)


if __name__ == "__main__":
    main()
