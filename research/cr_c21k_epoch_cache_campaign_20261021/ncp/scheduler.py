"""Bounded Linux process coordinator; imports no scientific runtime.

An explicit, unexpired owner allocation is mandatory for --execute. Jobs retain
their own source admission and scientific receipts. Successful process exit is
never sufficient for COMPLETE. Existing attempts are immutable and not retried.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import secrets

GIB = 1024 ** 3
THREAD_ENV = {k: "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS", "RAYON_NUM_THREADS")}
THREAD_ENV.update(OMP_NESTED="FALSE", OMP_MAX_ACTIVE_LEVELS="1",
                  PYTHONDONTWRITEBYTECODE="1")
TERMINAL_FAILURE = {"FAILED", "TIMED_OUT", "INTERRUPTED", "BLOCKED", "NOT_RUN", "SCOPED_HOLD"}


class AdmissionError(RuntimeError):
    pass


def utc():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise AdmissionError("DUPLICATE_JSON_KEY " + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(AdmissionError(value)))


def write_new(path, value):
    path = Path(path)
    with path.open("xb") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def file_record(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise AdmissionError("REGULAR_FILE_REQUIRED " + str(path))
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return {"bytes": path.stat().st_size, "sha256": h.hexdigest()}


def host_fingerprint():
    machine = Path("/etc/machine-id")
    raw = machine.read_bytes().strip() if machine.is_file() else b""
    return hashlib.sha256(raw + b"\0" + socket.gethostname().encode()).hexdigest()


def cpu_set(text):
    result = set()
    for part in text.strip().split(","):
        if not part:
            continue
        bounds = part.split("-")
        a, b = int(bounds[0]), int(bounds[-1])
        if a < 0 or b < a:
            raise AdmissionError("INVALID_CPU_RANGE")
        result.update(range(a, b + 1))
    return result


def cgroup_paths():
    """Visible unified hierarchy, including every visible parent constraint."""
    root = Path("/sys/fs/cgroup")
    if not (root / "cgroup.controllers").exists():
        raise AdmissionError("CGROUP_V2_REQUIRED_OR_EXPLICIT_IMPLEMENTATION_UPDATE")
    relative = ""
    for line in Path("/proc/self/cgroup").read_text().splitlines():
        if line.startswith("0::"):
            relative = line[3:].lstrip("/")
    candidate = root / relative
    current = candidate if candidate.is_dir() else root
    paths = []
    while current.is_relative_to(root):
        paths.append(current)
        if current == root:
            break
        current = current.parent
    return paths


def resource_snapshot(affinity=None):
    info = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value = line.split(":", 1)
        if key in ("MemTotal", "MemAvailable"):
            info[key] = int(value.split()[0]) * 1024
    quotas, limits, remaining, cpus = [], [], [], set(affinity or os.sched_getaffinity(0))
    observations = []
    for path in cgroup_paths():
        item = {"path": str(path)}
        for name in ("cpu.max", "cpuset.cpus.effective", "memory.max", "memory.current"):
            f = path / name
            item[name] = f.read_text().strip() if f.is_file() else None
        if item["cpu.max"]:
            quota, period = item["cpu.max"].split()
            if quota != "max":
                quotas.append(int(quota) / int(period))
        if item["cpuset.cpus.effective"]:
            cpus &= cpu_set(item["cpuset.cpus.effective"])
        if item["memory.max"] and item["memory.max"] != "max":
            limit = int(item["memory.max"])
            limits.append(limit)
            if item["memory.current"] is not None:
                remaining.append(max(0, limit - int(item["memory.current"])))
        observations.append(item)
    total = min([info["MemTotal"]] + limits)
    available = min([info["MemAvailable"]] + remaining)
    return {"observed_at_utc": utc(), "host_fingerprint_sha256": host_fingerprint(),
            "affinity_cpu_ids": sorted(cpus), "cpu_quota": min(quotas) if quotas else None,
            "memory_limit_bytes": total, "memory_available_bytes": available,
            "cgroup_observations": observations}


def admitted_capacity(snapshot, allocation, now=None):
    now = time.time() if now is None else now
    if allocation.get("schema") != "C21K_OWNER_ALLOCATION_V1" or not allocation.get("owner_allocation_id"):
        raise AdmissionError("EXPLICIT_OWNER_ALLOCATION_REQUIRED")
    if allocation.get("host_fingerprint_sha256") != snapshot["host_fingerprint_sha256"]:
        raise AdmissionError("ALLOCATION_HOST_MISMATCH")
    expiry = datetime.fromisoformat(allocation["expires_at_utc"].replace("Z", "+00:00"))
    if expiry.tzinfo is None or expiry.timestamp() <= now:
        raise AdmissionError("ALLOCATION_EXPIRED")
    ids = allocation.get("cpu_ids")
    if not isinstance(ids, list) or any(type(x) is not int or x < 0 for x in ids) or len(set(ids)) != len(ids):
        raise AdmissionError("EXPLICIT_DISTINCT_ALLOCATED_CPUS_REQUIRED")
    cpus = sorted(set(ids) & set(snapshot["affinity_cpu_ids"]) - {55})
    if len(cpus) < 2:
        raise AdmissionError("COORDINATOR_PLUS_ONE_WORKER_CPUS_REQUIRED")
    quota = snapshot["cpu_quota"]
    total_slots = min(len(cpus), math.floor(quota) if quota is not None else len(cpus))
    reserve = max(GIB, math.ceil(snapshot["memory_limit_bytes"] / 8))
    job_rss = allocation.get("per_job_rss_budget_bytes")
    coordinator_rss = allocation.get("coordinator_rss_budget_bytes")
    if type(job_rss) is not int or job_rss <= 0 or type(coordinator_rss) is not int or coordinator_rss <= 0:
        raise AdmissionError("POSITIVE_MEASURED_OR_CONSERVATIVE_RSS_BUDGET_REQUIRED")
    free = max(0, snapshot["memory_available_bytes"] - reserve - coordinator_rss)
    max_jobs = min(total_slots - 1, free // job_rss)
    if "maximum_concurrent_jobs" in allocation:
        cap = allocation["maximum_concurrent_jobs"]
        if type(cap) is not int or cap < 1:
            raise AdmissionError("INVALID_JOB_CAP")
        max_jobs = min(max_jobs, cap)
    if max_jobs < 1:
        raise AdmissionError("INSUFFICIENT_CPU_QUOTA_OR_MEMORY")
    return {"cpu_ids": cpus, "maximum_concurrent_jobs": max_jobs,
            "maximum_cpu_jobs": min(total_slots - 1, allocation.get("maximum_concurrent_jobs", total_slots - 1)),
            "available_new_job_memory_slots": free // job_rss,
            "memory_reserve_bytes": reserve, "per_job_rss_budget_bytes": job_rss,
            "coordinator_rss_budget_bytes": coordinator_rss,
            "allocation_expiry_epoch": expiry.timestamp()}


@contextmanager
def exclusive_lock(path):
    f = Path(path).open("a+b")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        f.close()
        raise AdmissionError("LEASE_BUSY " + str(path))
    try:
        yield f
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


def acquire_cpu(directory, cpu):
    f = (Path(directory) / ("cpu_%d.lock" % cpu)).open("a+b")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        f.close()
        return None
    return f


def validate_manifest(manifest):
    if manifest.get("schema") != "C21K_BOUNDED_CAMPAIGN_V1":
        raise AdmissionError("CAMPAIGN_SCHEMA")
    jobs = manifest.get("jobs", [])
    ids = [j["job_id"] for j in jobs]
    if not jobs or len(ids) != len(set(ids)):
        raise AdmissionError("EMPTY_OR_DUPLICATE_JOBS")
    if not 0 < manifest.get("campaign_timeout_seconds", 0) <= 86400:
        raise AdmissionError("BOUNDED_CAMPAIGN_DEADLINE_REQUIRED")
    units = [j.get("raw_attempt_units", 1) for j in jobs if j.get("kind") != "external_complete"]
    if any(type(x) is not int or x < 1 for x in units) or sum(units) > manifest.get("maximum_raw_attempt_units", 0):
        raise AdmissionError("CENTRAL_RAW_ATTEMPT_BUDGET")
    import re
    if any(re.fullmatch(r"[a-zA-Z0-9_-]+", key) is None for key in ids):
        raise AdmissionError("UNSAFE_JOB_ID")
    remaining = set(ids)
    while remaining:
        ready = {key for key in remaining if not (set(next(j for j in jobs if j["job_id"] == key).get("dependencies", [])) & remaining)}
        if not ready:
            raise AdmissionError("DAG_CYCLE")
        remaining -= ready
    for job in jobs:
        if not set(job.get("dependencies", [])) <= set(ids):
            raise AdmissionError("MISSING_DEPENDENCY")
        if job.get("kind") == "external_complete":
            if not job.get("receipt_file") or not job.get("receipt_record"):
                raise AdmissionError("EXTERNAL_RECEIPT_REQUIRED")
            continue
        command = job.get("command")
        if not isinstance(command, list) or not command or any(not isinstance(x, str) for x in command):
            raise AdmissionError("ARGV_REQUIRED")
        if not job.get("success") or not job.get("result_receipt"):
            raise AdmissionError("SCIENTIFIC_RECEIPT_PREDICATE_REQUIRED")
        rel = Path(job["result_receipt"])
        if rel.is_absolute() or ".." in rel.parts:
            raise AdmissionError("RESULT_RECEIPT_MUST_STAY_IN_JOB_PAYLOAD")
        if not 0 < job.get("timeout_seconds", 0) <= 7200:
            raise AdmissionError("BOUNDED_JOB_DEADLINE_REQUIRED")
    return manifest


def verify_inputs(manifest):
    for entry in manifest.get("input_files", []):
        if file_record(entry["path"]) != entry["record"]:
            raise AdmissionError("INPUT_IDENTITY_CHANGED " + entry["path"])


def check_receipt(path, predicates):
    result = read_json(path)
    for criterion in predicates:
        value = result
        for part in criterion["path"].split("."):
            if not isinstance(value, dict) or part not in value:
                raise AdmissionError("RESULT_FIELD_MISSING " + criterion["path"])
            value = value[part]
        if "equals" in criterion and value != criterion["equals"]:
            raise AdmissionError("RESULT_NOT_COMPLETE " + criterion["path"])
        if "one_of" in criterion and value not in criterion["one_of"]:
            raise AdmissionError("RESULT_NOT_ADMITTED " + criterion["path"])
    return result


def verify_external(job):
    path = Path(job["receipt_file"])
    if file_record(path) != job["receipt_record"]:
        raise AdmissionError("EXTERNAL_RECEIPT_CHANGED")
    result = check_receipt(path, job["success"])
    if "payload_files" not in result:
        raise AdmissionError("EXTERNAL_PAYLOAD_INVENTORY_REQUIRED")
    records = inventory(path.parent)
    records.pop(path.name)
    if records != result["payload_files"]:
        raise AdmissionError("EXTERNAL_PAYLOAD_CHANGED")
    for check in job.get("context_files", []):
        expected = result
        for name in check["receipt_path"].split("."):
            expected = expected[name]
        if file_record(check["path"]) != {k: expected[k] for k in ("bytes", "sha256")}:
            raise AdmissionError("EXTERNAL_CONTEXT_CHANGED " + check["receipt_path"])
    return result


def inventory(directory):
    result = {}
    for path in sorted(Path(directory).rglob("*")):
        if path.is_symlink():
            raise AdmissionError("OUTPUT_SYMLINK")
        if path.is_file():
            result[str(path.relative_to(directory))] = file_record(path)
    return result


def job_signature(job, manifest):
    return digest({"job": job, "source_identity": manifest["source_identity"],
                   "input_files": manifest.get("input_files", [])})


def resume_status(directory, job, manifest):
    terminal = Path(directory) / "COORDINATOR_RECEIPT.json"
    if not terminal.is_file():
        return "INTERRUPTED"
    prior = read_json(terminal)
    if prior.get("signature") != job_signature(job, manifest):
        raise AdmissionError("RESUME_IDENTITY_MISMATCH " + job["job_id"])
    if prior["status"] != "COMPLETE":
        return prior["status"]
    for name, record in prior["payload_files"].items():
        if file_record(Path(directory) / "payload" / name) != record:
            raise AdmissionError("RESUME_PAYLOAD_CHANGED")
    if inventory(Path(directory) / "payload") != prior["payload_files"]:
        raise AdmissionError("RESUME_PAYLOAD_SET_CHANGED")
    check_receipt(Path(directory) / "payload" / job["result_receipt"], job["success"])
    return "COMPLETE"


def expand(command, cpu, job_dir, output, jobs, bindings):
    values = {**bindings, "cpu": str(cpu), "job_out": str(job_dir / "payload"), "campaign_out": str(output)}
    values.update({"job:" + j["job_id"]: str(output / "jobs" / j["job_id"] / "payload") for j in jobs})
    import re
    def substitute(value):
        def replace(match):
            if match.group(1) not in values:
                raise AdmissionError("UNBOUND_ARGUMENT " + match.group(1))
            return str(values[match.group(1)])
        return re.sub(r"\$\{([^}]+)\}", replace, value)
    return [substitute(x) for x in command]


def process_identity(pid):
    fields = (Path('/proc') / str(pid) / 'stat').read_text().rpartition(')')[2].split()
    return {"start_ticks": int(fields[19]), "state": fields[0],
            "rss_bytes": int(fields[21]) * os.sysconf('SC_PAGE_SIZE')}


def owned_processes(token):
    """Inspect only ownership markers, never persist process environments."""
    marker = ("BASS_C21K_ATTEMPT_TOKEN=" + token).encode()
    result = {}
    for directory in Path('/proc').iterdir():
        if not directory.name.isdigit():
            continue
        try:
            if directory.stat().st_uid != os.getuid():
                continue
            pid = int(directory.name)
            before = process_identity(pid)
            if marker not in (directory / 'environ').read_bytes().split(b'\0'):
                continue
            after = process_identity(pid)
            if before['start_ticks'] == after['start_ticks']:
                result[pid] = after
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    return result


def enable_subreaper():
    import ctypes
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:
        raise AdmissionError("LINUX_CHILD_SUBREAPER_REQUIRED")


def verify_process_observation():
    """Bounded runtime capability check, never a scientific/native probe."""
    token = secrets.token_hex(24)
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(1)'],
        env={**os.environ, **THREAD_ENV, 'BASS_C21K_ATTEMPT_TOKEN': token},
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(.03)
        try:
            raw = (Path('/proc') / str(child.pid) / 'environ').read_bytes()
        except (PermissionError, FileNotFoundError) as exc:
            raise AdmissionError('OWNED_PROCESS_OBSERVATION_UNAVAILABLE: no native job launched') from exc
        if ('BASS_C21K_ATTEMPT_TOKEN=' + token).encode() not in raw.split(b'\0'):
            raise AdmissionError('OWNED_PROCESS_MARKER_NOT_OBSERVABLE: no native job launched')
        try:
            before = process_identity(child.pid)
            observed = owned_processes(token).get(child.pid)
            after = process_identity(child.pid)
        except (OSError, ValueError, IndexError) as exc:
            raise AdmissionError('OWNED_PROCESS_TRACKER_UNAVAILABLE: no native job launched') from exc
        if (observed is None or before['start_ticks'] != observed['start_ticks']
            or before['start_ticks'] != after['start_ticks']
            or observed['state'] in ('Z', 'X', 'x')
            or type(observed['rss_bytes']) is not int or observed['rss_bytes'] <= 0):
            raise AdmissionError('OWNED_PROCESS_TRACKER_NOT_VERIFIED: no native job launched')
    finally:
        if child.poll() is None: child.terminate()
        try: child.wait(timeout=1)
        except subprocess.TimeoutExpired:
            child.kill(); child.wait(timeout=1)


def stop_owned(task):
    """Stop exact marker/start-time owners, including setsid grandchildren."""
    known = dict(task.get('owned', {}))
    forced = set()
    for sig, duration in ((signal.SIGTERM, .5), (signal.SIGKILL, 1.5)):
        # Popen establishes direct-child ownership even if /proc access changes.
        if task['process'].poll() is None:
            task['process'].send_signal(sig)
            forced.add(task['process'].pid)
        deadline = time.monotonic() + duration
        while True:
            known.update(owned_processes(task['token']))
            live = []
            for pid, original in list(known.items()):
                try:
                    current = process_identity(pid)
                    if current['start_ticks'] != original['start_ticks']:
                        continue
                    if current['state'] != 'Z':
                        os.kill(pid, sig); live.append(pid); forced.add(pid)
                    elif pid != task['process'].pid:
                        try: os.waitpid(pid, os.WNOHANG)
                        except ChildProcessError: pass
                except (FileNotFoundError, ProcessLookupError):
                    pass
            task['process'].poll()
            if not live or time.monotonic() >= deadline:
                break
            time.sleep(.02)
    task['process'].wait(timeout=2)
    survivors = {pid: identity for pid, identity in owned_processes(task['token']).items()
                 if identity['state'] != 'Z'}
    if survivors:
        raise AdmissionError("OWNED_DESCENDANT_CLEANUP_FAILED")
    for pid, identity in known.items():
        if pid == task['process'].pid:
            continue
        try:
            current = process_identity(pid)
            if current['start_ticks'] == identity['start_ticks']:
                os.waitpid(pid, os.WNOHANG)
        except (FileNotFoundError, ProcessLookupError, ChildProcessError):
            pass
    return {"forced_process_count": len(forced), "unresolved_owned_processes": 0}


def run_campaign(manifest, allocation, output, *, resume=False):
    validate_manifest(manifest)
    if manifest.get("binding_status") != "BOUND":
        raise AdmissionError("UNBOUND_CAMPAIGN_CANNOT_EXECUTE")
    verify_inputs(manifest)
    enable_subreaper()
    output = Path(output).resolve()
    if not resume:
        output.mkdir(parents=True, exist_ok=False)
    elif not output.is_dir():
        raise AdmissionError("RESUME_OUTPUT_MISSING")
    with exclusive_lock(output / ".coordinator.lock"):
        identity_file = output / "CAMPAIGN_IDENTITY.json"
        if identity_file.exists():
            if read_json(identity_file) != {"manifest_sha256": digest(manifest)}:
                raise AdmissionError("RESUME_MANIFEST_MISMATCH")
        else:
            write_new(identity_file, {"manifest_sha256": digest(manifest)})
        initial_affinity = set(os.sched_getaffinity(0))
        snapshot = resource_snapshot(initial_affinity)
        capacity = admitted_capacity(snapshot, allocation)
        lease_dir = Path(allocation["lease_directory"]).resolve()
        lease_dir.mkdir(parents=True, exist_ok=True)
        coordinator = None
        for cpu in capacity["cpu_ids"]:
            handle = acquire_cpu(lease_dir, cpu)
            if handle is not None:
                coordinator = (cpu, handle)
                break
        if coordinator is None:
            raise AdmissionError("NO_COORDINATOR_CPU_LEASE")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        write_new(output / ("ADMISSION_" + stamp + ".json"), {"snapshot": snapshot,
            "allocation_sha256": digest(allocation), "capacity": capacity,
            "coordinator_cpu": coordinator[0], "protected_cpu_ids": [55]})
        os.sched_setaffinity(0, {coordinator[0]})
        jobs = manifest["jobs"]
        (output / "jobs").mkdir(exist_ok=True)
        statuses, active = {}, {}
        campaign_deadline = min(time.monotonic() + manifest["campaign_timeout_seconds"],
            time.monotonic() + capacity["allocation_expiry_epoch"] - time.time())
        failure = None
        try:
            verify_process_observation()
            for job in jobs:
                key = job["job_id"]
                if job.get("kind") == "external_complete":
                    try:
                        verify_external(job)
                        statuses[key] = "HISTORICAL_COMPLETE" if job.get('historical_only') else "COMPLETE"
                    except (OSError, ValueError, AdmissionError):
                        statuses[key] = "BLOCKED"
                elif (output / "jobs" / key).exists():
                    statuses[key] = resume_status(output / "jobs" / key, job, manifest)
            while len(statuses) < len(jobs):
                now = time.monotonic()
                for key, task in list(active.items()):
                    process = task["process"]
                    task['owned'].update(owned_processes(task['token']))
                    owned_live = owned_processes(task['token'])
                    rss = sum(item['rss_bytes'] for item in owned_live.values())
                    task['peak_observed_group_rss_bytes'] = max(task['peak_observed_group_rss_bytes'], rss)
                    memory_exceeded = rss > capacity['per_job_rss_budget_bytes']
                    timed_out = now >= task["deadline"] or now >= campaign_deadline
                    cleanup = None
                    if timed_out or memory_exceeded:
                        cleanup = stop_owned(task)
                    if process.poll() is None:
                        continue
                    lingering = [pid for pid, identity in owned_live.items()
                                 if pid != process.pid and identity['state'] != 'Z']
                    if cleanup is None:
                        cleanup = stop_owned(task)
                    unexpected_cleanup = bool(cleanup['forced_process_count']) and not timed_out and not memory_exceeded
                    task["stdout"].close(); task["stderr"].close()
                    status = "TIMED_OUT" if timed_out else "FAILED"
                    error = "GROUP_RSS_BUDGET_EXCEEDED" if memory_exceeded else "OWNED_DESCENDANT_SURVIVED_LEADER" if lingering or unexpected_cleanup else None
                    scientific_summary = None
                    if process.returncode == 0 and not timed_out and not memory_exceeded and not lingering and not unexpected_cleanup:
                        try:
                            result = check_receipt(task["directory"] / "payload" / task["job"]["result_receipt"], task["job"]["success"])
                            if task["job"].get("kind") == "standalone_g_campaign":
                                nested = result.get("jobs", [])
                                scientific_summary = {"campaign_status": result.get("status"),
                                    "actual_job_receipts": len(nested),
                                    "complete_job_receipts": sum(j.get("status") == "COMPLETE" for j in nested),
                                    "conditional_history_jobs_not_run": max(0, 12 - len(nested)),
                                    "reference_status": result.get("reference_status"),
                                    "refinement_execution": result.get("refinement_execution")}
                                if len(nested) < 8 or any(j.get("status") != "COMPLETE" for j in nested):
                                    raise AdmissionError("G_REFERENCE_EXECUTION_INCOMPLETE")
                            status = "SCOPED_HOLD" if (task["job"].get("kind") == "standalone_g_campaign"
                                and result.get("status") != "COMPLETED_BOUNDED_PILOT") else "COMPLETE"
                        except (OSError, ValueError, AdmissionError) as exc:
                            error = str(exc)
                    records = inventory(task["directory"] / "payload")
                    write_new(task["directory"] / "COORDINATOR_RECEIPT.json", {
                        "schema": "C21K_COORDINATOR_JOB_RECEIPT_V1", "job_id": key,
                        "signature": job_signature(task["job"], manifest), "status": status,
                        "exit_code": process.returncode, "timed_out": timed_out,
                        "cpu": task["cpu"], "wall_seconds": time.monotonic() - task["started"],
                        "payload_files": records, "result_error": error,
                        "scientific_summary": scientific_summary,
                        "cleanup": cleanup, "peak_observed_group_rss_bytes": task['peak_observed_group_rss_bytes'],
                        "finished_at_utc": utc(), "global_error_bound": None})
                    task["lease"].close()
                    statuses[key] = status
                    del active[key]
                if now >= campaign_deadline:
                    for job in jobs:
                        if job["job_id"] not in statuses and job["job_id"] not in active:
                            statuses[job["job_id"]] = "NOT_RUN"
                    if not active:
                        break
                progress = False
                for job in jobs:
                    key = job["job_id"]
                    if key in statuses or key in active:
                        continue
                    dependencies = job.get("dependencies", [])
                    if any(statuses.get(dep) in TERMINAL_FAILURE for dep in dependencies):
                        statuses[key] = "BLOCKED"; progress = True; continue
                    if any(statuses.get(dep) != "COMPLETE" for dep in dependencies):
                        continue
                    try:
                        fresh = resource_snapshot(initial_affinity)
                        current = admitted_capacity(fresh, allocation)
                    except AdmissionError:
                        if not active:
                            statuses[key] = "BLOCKED"; progress = True
                        continue
                    # Reserve one full per-job RSS budget for every active job,
                    # including children whose RSS has not grown yet. Current
                    # available memory makes this deliberately conservative.
                    if len(active) >= current["maximum_concurrent_jobs"]:
                        break
                    leased = {coordinator[0]} | {t["cpu"] for t in active.values()}
                    selected = None
                    for cpu in current["cpu_ids"]:
                        if cpu not in leased:
                            handle = acquire_cpu(lease_dir, cpu)
                            if handle is not None:
                                selected = (cpu, handle); break
                    if selected is None:
                        continue
                    try:
                        verify_inputs(manifest)
                    except BaseException:
                        selected[1].close()
                        raise
                    directory = output / "jobs" / key
                    directory.mkdir(exist_ok=False)
                    command = expand(job["command"], selected[0], directory, output, jobs, manifest.get("bindings", {}))
                    write_new(directory / "RESERVATION.json", {"job_id": key,
                        "signature": job_signature(job, manifest), "reserved_at_utc": utc(),
                        "raw_attempt_units": job.get("raw_attempt_units", 1),
                        "cpu": selected[0], "argv": command,
                        "thread_environment": THREAD_ENV, "automatic_retry": False})
                    stdout = (directory / "stdout.txt").open("xb")
                    stderr = (directory / "stderr.txt").open("xb")
                    cpu = selected[0]
                    token = secrets.token_hex(24)
                    try:
                        process = subprocess.Popen(command, cwd=manifest.get("working_directory"),
                            env={**os.environ, **THREAD_ENV, 'BASS_C21K_ATTEMPT_TOKEN': token}, stdout=stdout, stderr=stderr,
                            start_new_session=True, preexec_fn=lambda cpu=cpu: os.sched_setaffinity(0, {cpu}))
                    except BaseException:
                        stdout.close(); stderr.close(); selected[1].close()
                        raise
                    started = time.monotonic()
                    active[key] = {"process": process, "stdout": stdout, "stderr": stderr,
                        "directory": directory, "job": job, "cpu": cpu, "lease": selected[1],
                        "token": token, "owned": {}, "peak_observed_group_rss_bytes": 0,
                        "started": started, "deadline": min(campaign_deadline, started + job["timeout_seconds"])}
                    progress = True
                if not active and not progress and len(statuses) < len(jobs):
                    for job in jobs:
                        if job["job_id"] not in statuses:
                            statuses[job["job_id"]] = "BLOCKED"
                    break
                if active:
                    time.sleep(0.05)
        except BaseException as exc:
            failure = type(exc).__name__ + ": " + str(exc)
            raise
        finally:
            cleanup_errors = []
            for key, task in active.items():
                try:
                    stop_owned(task)
                except BaseException as exc:
                    cleanup_errors.append({'job_id': key, 'error': type(exc).__name__ + ': ' + str(exc)})
                finally:
                    task["stdout"].close(); task["stderr"].close(); task["lease"].close()
                statuses[key] = "INTERRUPTED"
            os.sched_setaffinity(0, initial_affinity)
            coordinator[1].close()
            for job in jobs:
                statuses.setdefault(job['job_id'], 'NOT_RUN')
            comparison = {}
            for job in jobs:
                other = job.get('comparison_evidence_dependency')
                if other:
                    comparison[job['job_id']] = {'against':other,
                        'availability':'BOTH_TERMINALS_COMPLETE_REQUIRES_SCIENTIFIC_COMPARISON' if statuses.get(job['job_id'])=='COMPLETE' and statuses.get(other)=='COMPLETE' else 'COMPARISON_UNAVAILABLE',
                        'soft_dependency':True}
            write_new(output / ("CAMPAIGN_RETURN_" + stamp + ".json"), {
                "schema": "C21K_COORDINATOR_RETURN_V1", "created_at_utc": utc(),
                "manifest_sha256": digest(manifest), "statuses": statuses,
                "science_jobs_accounting": manifest.get("science_jobs_accounting"),
                "failure": failure, "global_error_bound": None,
                "cleanup_errors": cleanup_errors,
                "comparison_evidence": comparison,
                "publication": "NOT_PUBLISHED", "backup": "NOT_BACKED_UP",
                "native_performance": "REQUIRES_ACTUAL_JOB_TIMERS_AND_ANALYSIS"})
        return statuses


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--allocation", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--inspect-resources", action="store_true")
    args = parser.parse_args(argv)
    if args.inspect_resources:
        print(json.dumps(resource_snapshot(), indent=2)); return 0
    if args.manifest is None:
        parser.error("--manifest is required")
    manifest = validate_manifest(read_json(args.manifest))
    verify_inputs(manifest)
    if not args.execute:
        print(json.dumps({"status": "PREPARED_NOT_RUN", "manifest_sha256": digest(manifest),
            "coordinator_nodes": len(manifest["jobs"]), "science_jobs_accounting": manifest.get("science_jobs_accounting"),
            "global_error_bound": None})); return 0
    if args.allocation is None or args.out is None:
        parser.error("--execute requires --allocation and --out")
    statuses = run_campaign(manifest, read_json(args.allocation), args.out, resume=args.resume)
    print(json.dumps({"statuses": statuses, "global_error_bound": None}))
    return 0 if all(s in ("COMPLETE", "HISTORICAL_COMPLETE") for s in statuses.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
