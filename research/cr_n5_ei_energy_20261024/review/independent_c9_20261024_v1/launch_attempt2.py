"""One create-only C9 attempt. Own process group only; failed cost retained."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time


def writej(path, obj):
    with path.open("x") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n")


def main():
    here = Path(__file__).resolve().parent
    unit = here.parents[1]
    c = json.loads((unit / "inputs/CASE.json").read_text())
    cfg = c["resources"]
    out = here / "run_attempt2"
    out.mkdir(exist_ok=False)
    lease = here / ".independent_c9_lease"
    start, cpu0 = time.monotonic(), time.process_time()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started, leased, returncode, error = False, False, None, None
    status = "FAILED_RETAINED"
    prior_review = [json.loads(q.read_text()) for q in sorted(here.glob("run*/DISPATCH_RECEIPT.json"))]
    prior_review_worker_cpu_s = sum(q["worker_cpu_s"] for q in prior_review)
    prior_review_wall_s = sum(q["wall_s"] for q in prior_review)
    cpu_limit = int(cfg["review_cpu_s"] - prior_review_worker_cpu_s)
    wall_limit = cfg["review_wall_s"] - prior_review_wall_s
    try:
        with lease.open("x") as f:
            json.dump({"pid": os.getpid(), "run_id": "n5_ei_energy_independent_c9_20261024_v1"}, f)
        leased = True
        cg = Path("/sys/fs/cgroup")
        stat = dict((k, int(v)) for k, v in (line.split() for line in (cg / "memory.stat").read_text().splitlines()))
        current, maximum = int((cg / "memory.current").read_text()), int((cg / "memory.max").read_text())
        clean = max(0, stat.get("inactive_file", 0) - stat.get("file_dirty", 0) - stat.get("file_writeback", 0))
        available = max(0, maximum - current) + clean - 64 * 1024**2
        processes = []
        for p in Path("/proc").iterdir():
            if p.name.isdigit():
                try:
                    comm = (p / "comm").read_text().strip()
                    if any(word in comm for word in ("python", "worker", "cargo", "rust")):
                        processes.append({"pid": int(p.name), "comm": comm, "cmdline": (p / "cmdline").read_bytes().replace(b"\x00", b" ").decode(errors="replace")[:800]})
                except (FileNotFoundError, ProcessLookupError, PermissionError):
                    pass
        production_lease = unit / "implementation/.ei_task_lease"
        state = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "affinity": sorted(os.sched_getaffinity(0)), "cpu_max": (cg / "cpu.max").read_text().strip(), "memory_current": current, "memory_max": maximum, "clean_reclaimable": clean, "memory_available_after_reserve": available, "memory_events": (cg / "memory.events").read_text(), "processes": processes, "production_lease_present": production_lease.exists(), "production_lease_content": production_lease.read_text() if production_lease.exists() else None, "NCP_runtime": "UNOBSERVED", "NCP_lease": "UNOBSERVED"}
        writej(out / "RESOURCE_ADMISSION.json", state)
        if production_lease.exists():
            raise RuntimeError("PRODUCTION_LEASE_ACTIVE")
        if available < cfg["RLIMIT_AS_bytes"]:
            raise RuntimeError("MEMORY_ADMISSION_REJECTED")
        if not {cfg["reviewer_cpu"], cfg["coordinator_cpu"]}.issubset(state["affinity"]):
            raise RuntimeError("CPU_ADMISSION_REJECTED")
        prior = []
        for p in sorted((unit / "runs").glob("*/DISPATCH_RECEIPT.json")):
            r = json.loads(p.read_text())
            prior.append({"path": str(p.relative_to(unit)), "worker_cpu_s": r["worker_cpu_s"]})
        prior_cpu = sum(p["worker_cpu_s"] for p in prior)
        if prior_cpu + cpu_limit > cfg["new_unit_total_cpu_s"]:
            raise RuntimeError("UNIT_AGGREGATE_CPU_ADMISSION_REJECTED")
        os.sched_setaffinity(0, {cfg["coordinator_cpu"]})
        executed = out / "EXECUTED_SOURCE"
        executed.mkdir()
        pins = []
        for name in ("oracle.py", "launch_attempt2.py", "REVIEW_SCOPE.json"):
            data = (here / name).read_bytes()
            (executed / name).open("xb").write(data)
            pins.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        writej(out / "PRE_EXECUTION.json", {"run_id": "n5_ei_energy_independent_c9_20261024_v1", "source_pins": pins, "primary_raw_go": True, "S0_freeze_released": True, "review_cpu_limit_s": cpu_limit, "review_wall_limit_s": wall_limit, "RLIMIT_AS_bytes": cfg["RLIMIT_AS_bytes"], "worker_cpu": cfg["reviewer_cpu"], "coordinator_cpu": cfg["coordinator_cpu"], "native_threads": 1, "inherited_known_worker_cpu_s": cfg["inherited_worker_cpu_s"], "prior_new_unit_worker_cpu_s": prior_cpu, "prior_attempts": prior, "prior_review_attempts": prior_review, "prior_review_worker_cpu_s": prior_review_worker_cpu_s, "prior_review_wall_s": prior_review_wall_s, "attempt_id": "n5_ei_energy_independent_c9_20261024_v1_attempt2", "requested_model": "inherited_parent_model", "observed_runtime_model": "UNOBSERVED"})
        env = os.environ.copy()
        env.update({k: "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")})
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        def limit():
            os.sched_setaffinity(0, {cfg["reviewer_cpu"]})
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
            resource.setrlimit(resource.RLIMIT_AS, (cfg["RLIMIT_AS_bytes"], cfg["RLIMIT_AS_bytes"]))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        with (out / "stdout.txt").open("x") as stdout, (out / "stderr.txt").open("x") as stderr:
            child = subprocess.Popen([sys.executable, "-B", str(executed / "oracle.py"), "--unit", str(unit), "--output", str(out)], cwd=executed, env=env, stdout=stdout, stderr=stderr, preexec_fn=limit, start_new_session=True)
            started = True
            try:
                returncode = child.wait(timeout=wall_limit)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    returncode = child.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    returncode = child.wait()
                raise RuntimeError("OWNED_C9_WORKER_WALL_LIMIT")
        status = "PASS" if returncode == 0 else "FAILED_RETAINED"
    except Exception as ex:
        error = {"type": type(ex).__name__, "message": str(ex)}
    finally:
        if leased:
            lease.unlink()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        receipt = {"schema": "N5_EI_INDEPENDENT_C9_DISPATCH_V1", "attempt_id": "n5_ei_energy_independent_c9_20261024_v1_attempt2", "prior_review_worker_cpu_s": prior_review_worker_cpu_s, "prior_review_wall_s": prior_review_wall_s, "status": status, "error": error, "child_started": started, "returncode": returncode, "worker_cpu_s": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime, "worker_peak_RSS_KiB": after.ru_maxrss if started else None, "coordinator_cpu_s": time.process_time() - cpu0, "wall_s": time.monotonic() - start, "CPU_limit_s": cpu_limit, "wall_limit_s": wall_limit, "inherited_known_worker_cpu_s": cfg["inherited_worker_cpu_s"], "global_spend": None, "remaining": None, "currency": None, "EXECUTION": status, "PUBLICATION": "ROOT_OWNED", "BACKUP": "ROOT_PENDING", "DAG": "N5_PARTIAL_OPEN_N6_N7_NOT_ACTIVATED"}
        writej(out / "DISPATCH_RECEIPT.json", receipt)
    print(json.dumps(receipt))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
