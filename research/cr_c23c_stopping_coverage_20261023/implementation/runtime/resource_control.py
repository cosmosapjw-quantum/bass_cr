"""Read-only Linux resource admission for independent C21O science jobs.

The caller applies ``selected_worker_cpus`` / ``coordinator_cpu`` affinity and
sets numerical libraries to one thread *before* importing them. This module
does not reserve CPUs, edit leases, change affinity, or signal any process.
Admission is an observation, not a guarantee against concurrent allocations.

``choose_workers`` returns ``(count, receipt)``. Pass that receipt as ``budget``
to ``dispatch_allowed(fresh_snapshot, n_active, budget)``; its return value is
``(allowed, detail)``. The caller owns a finite wait deadline and its own worker
lifecycle. Existing workers are never stopped by this module.

Documented JSON lease formats (all listed CPUs remain reserved, even when a
lease contains an expiry/status that this module cannot authenticate):

* {"schema": "C21_CPU_LEASES_V1", "leases": [{"owner": "other", "cpus": [1, 2]}]}
* {"owners": {"other": [1, 2], "another": "4-5"}}
* [{"owner": "other", "cpus": [1, 2]}]

An unfamiliar document is conservatively scanned for nonnegative integer CPU
IDs and CPU-named range fields. If no reservation can be inferred, all eligible
CPUs are withheld. Unknown JSON is never treated as an empty lease. Read errors
also withhold all eligible CPUs. A missing explicitly named file is reported.

Visible cgroup/mount resolution follows the C21M/C21N shared_resources approach;
the observer samples /proc/stat and matching cgroup counters for 0.1 seconds.
Per-worker memory is a planning allowance, not a measured or enforced RSS cap.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import socket
import time

MIB = 1024 ** 2
GIB = 1024 ** 3
SAMPLE_SECONDS = 0.1
IDLE_THRESHOLD = 0.35
MAX_WORKERS = 62
THREAD_ENV = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")


def _read_text(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def _cpu_ids(value):
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return {value}
    if isinstance(value, (list, tuple)):
        result = set()
        for v in value:
            result.update(_cpu_ids(v))
        return result
    if not isinstance(value, str):
        raise ValueError("invalid CPU list")
    result = set()
    for field in value.split(","):
        field = field.strip()
        if not field:
            continue
        parts = field.split("-")
        if len(parts) > 2 or not all(p.isdigit() for p in parts):
            raise ValueError("invalid CPU range")
        lo, hi = int(parts[0]), int(parts[-1])
        if hi < lo or hi - lo > 65536:
            raise ValueError("invalid CPU range bounds")
        result.update(range(lo, hi + 1))
    return result


def _cgroup_locations(cgroup_text, mountinfo_text):
    """Locate membership and visible ancestors for cgroup v1 and v2."""
    groups = []
    for line in (cgroup_text or "").splitlines():
        pieces = line.split(":", 2)
        if len(pieces) == 3:
            groups.append((set(pieces[1].split(",")) - {""}, pieces[2]))
    result = []
    for line in (mountinfo_text or "").splitlines():
        if " - " not in line:
            continue
        left, right = line.split(" - ", 1)
        a, b = left.split(), right.split()
        if len(a) < 5 or len(b) < 3 or b[0] not in ("cgroup", "cgroup2"):
            continue
        mountroot = a[3].replace("\\040", " ")
        mount = Path(a[4].replace("\\040", " "))
        controllers = set(b[2].split(","))
        for own_controllers, membership in groups:
            if b[0] == "cgroup2" and own_controllers:
                continue
            if b[0] == "cgroup" and not controllers.intersection(own_controllers):
                continue
            if membership == mountroot:
                relative = ""
            elif membership.startswith(mountroot.rstrip("/") + "/"):
                relative = membership[len(mountroot):].lstrip("/")
            else:
                relative = ""  # mounted namespace root is the visible boundary
            current = mount / relative
            fallback = ".." in current.parts or not current.is_dir()
            if fallback:
                current = mount
            while current == mount or mount in current.parents:
                row = {"path": str(current), "version": 2 if b[0] == "cgroup2" else 1,
                       "controllers": sorted(own_controllers),
                       "namespace_root_fallback": fallback}
                if row not in result:
                    result.append(row)
                if current == mount:
                    break
                current = current.parent
    return result


def _decode_group(location):
    p = Path(location["path"])
    row = dict(location, quota_cores=None, cpu_limit_observed=False,
               usage_seconds=None, memory_limit_bytes=None,
               memory_current_bytes=None, memory_limit_observed=False,
               memory_headroom_bytes=None, cpuset=None, warnings=[])
    try:
        if row["version"] == 2:
            cpu = _read_text(p / "cpu.max")
            if cpu is not None:
                quota, period = cpu.split()
                if int(period) <= 0:
                    raise ValueError("invalid cpu.max period")
                row["cpu_limit_observed"] = True
                if quota != "max":
                    row["quota_cores"] = max(0., int(quota) / int(period))
            stats = dict(line.split() for line in (_read_text(p / "cpu.stat") or "").splitlines())
            if "usage_usec" in stats:
                row["usage_seconds"] = int(stats["usage_usec"]) / 1e6
            row["cpuset"] = _read_text(p / "cpuset.cpus.effective")
            limit, current = _read_text(p / "memory.max"), _read_text(p / "memory.current")
        else:
            quota, period = _read_text(p / "cpu.cfs_quota_us"), _read_text(p / "cpu.cfs_period_us")
            if quota is not None and period is not None:
                if int(period) <= 0:
                    raise ValueError("invalid cgroup v1 period")
                row["cpu_limit_observed"] = True
                if int(quota) >= 0:
                    row["quota_cores"] = int(quota) / int(period)
            usage = _read_text(p / "cpuacct.usage")
            row["usage_seconds"] = int(usage) / 1e9 if usage is not None else None
            row["cpuset"] = _read_text(p / "cpuset.effective_cpus") or _read_text(p / "cpuset.cpus")
            limit = _read_text(p / "memory.limit_in_bytes")
            current = _read_text(p / "memory.usage_in_bytes")
        if limit is not None:
            row["memory_limit_observed"] = True
            if limit != "max" and int(limit) < 2 ** 60:
                row["memory_limit_bytes"] = max(0, int(limit))
        if current is not None:
            row["memory_current_bytes"] = max(0, int(current))
        if row["memory_limit_bytes"] is not None and row["memory_current_bytes"] is not None:
            row["memory_headroom_bytes"] = max(0, row["memory_limit_bytes"] - row["memory_current_bytes"])
    except (ValueError, TypeError) as exc:
        row["warnings"].append("invalid cgroup observation: " + str(exc))
    return row


def _snapshot_once():
    warnings = []
    try:
        affinity = sorted(os.sched_getaffinity(0))
        affinity_observed = True
    except (AttributeError, OSError):
        affinity, affinity_observed = [], False
        warnings.append("CPU affinity unavailable")
    allowed = set(affinity)
    cgroup_cpuset = None
    groups = [_decode_group(loc) for loc in _cgroup_locations(
        _read_text("/proc/self/cgroup"), _read_text("/proc/self/mountinfo"))]
    for row in groups:
        if row["cpuset"]:
            try:
                parsed = _cpu_ids(row["cpuset"])
                allowed.intersection_update(parsed)
                cgroup_cpuset = parsed if cgroup_cpuset is None else cgroup_cpuset & parsed
            except ValueError:
                allowed.clear()
                cgroup_cpuset = set()
                warnings.append("Unparseable cgroup cpuset; no CPU admitted")
    mem = {}
    for line in (_read_text("/proc/meminfo") or "").splitlines():
        k, _, v = line.partition(":")
        if k in ("MemTotal", "MemAvailable", "MemFree"):
            try:
                mem[k] = int(v.split()[0]) * 1024
            except (ValueError, IndexError):
                warnings.append("Invalid /proc/meminfo " + k)
    host_available = mem.get("MemAvailable", mem.get("MemFree"))
    quotas = [x["quota_cores"] for x in groups if x["quota_cores"] is not None]
    limits = [x["memory_limit_bytes"] for x in groups if x["memory_limit_bytes"] is not None]
    headrooms = [x["memory_headroom_bytes"] for x in groups if x["memory_headroom_bytes"] is not None]
    memory_complete = host_available is not None and all(
        x["memory_limit_bytes"] is None or x["memory_current_bytes"] is not None for x in groups)
    if any(x["warnings"] for x in groups):
        memory_complete = False
        warnings.append("Invalid cgroup observation; admission must wait")
    total_candidates = ([mem["MemTotal"]] if "MemTotal" in mem else []) + limits
    available_candidates = ([host_available] if host_available is not None else []) + headrooms
    try:
        load = list(os.getloadavg())
    except (AttributeError, OSError):
        load = []
    return {"affinity": affinity, "affinity_observed": affinity_observed,
            "allowed_cpus": sorted(allowed), "cgroups": groups,
            "cgroup_cpuset": sorted(cgroup_cpuset) if cgroup_cpuset is not None else None,
            "cgroup_scope": "visible memberships and visible ancestors only",
            "cpu_quota_cores": min(quotas) if quotas else None,
            "cpu_limit_observed": any(x["cpu_limit_observed"] for x in groups),
            "memory_limit_bytes": min(total_candidates) if total_candidates else None,
            "host_mem_available_bytes": host_available,
            "memory_available_bytes": min(available_candidates) if available_candidates and memory_complete else None,
            "memory_observation_complete": memory_complete,
            "host_load_average": load, "warnings": warnings}


def _proc_cpu():
    result = {}
    for line in (_read_text("/proc/stat") or "").splitlines():
        fields = line.split()
        if fields and fields[0].startswith("cpu") and fields[0][3:].isdigit():
            try:
                numbers = list(map(int, fields[1:]))
                result[int(fields[0][3:])] = (sum(numbers[:8]), numbers[3] + numbers[4])
            except (ValueError, IndexError):
                pass
    return result


def observe_resources():
    """Observe current limits and a requested 0.1 s CPU sample; no mutations."""
    before = _snapshot_once()
    first = _proc_cpu()
    own0, start = time.process_time(), time.monotonic()
    time.sleep(SAMPLE_SECONDS)
    second = _proc_cpu()
    after = _snapshot_once()
    elapsed = max(time.monotonic() - start, 1e-12)
    own_cores = max(0., time.process_time() - own0) / elapsed
    busy = {}
    # A coordinator may pin itself after admission; retain worker CPU samples
    # beyond its current one-CPU affinity for later dispatch decisions.
    for cpu in sorted(set(first) | set(second)):
        a, b = first.get(cpu), second.get(cpu)
        if a is None or b is None or b[0] <= a[0]:
            busy[cpu] = 1.  # unknown is not an idle CPU
        else:
            busy[cpu] = min(1., max(0., 1. - (b[1] - a[1]) / (b[0] - a[0])))
    prior = {r["path"]: r for r in before["cgroups"]}
    quota_spares, observations = [], []
    for row in after["cgroups"]:
        q = row["quota_cores"]
        if q is None:
            continue
        old = prior.get(row["path"], {}).get("usage_seconds")
        current = row["usage_seconds"]
        if old is not None and current is not None and current >= old:
            usage = max(0., (current - old) / elapsed - own_cores)
            basis = "matching cgroup counter minus observing process CPU time"
        else:
            scope = after["cgroup_cpuset"] if after["cgroup_cpuset"] is not None else busy
            usage = sum(busy.get(cpu, 1.) for cpu in scope)
            basis = "conservative visible cgroup/host CPU busy sum; cgroup usage unavailable"
        spare = max(0., q - usage)
        quota_spares.append(spare)
        observations.append({"path": row["path"], "quota_cores": q,
                             "observed_other_and_child_cores": usage,
                             "spare_cores": spare, "basis": basis})
    after.update({"schema": "C21O_RESOURCE_OBSERVATION_V1",
                  "observed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  "hostname": socket.gethostname(), "observer_pid": os.getpid(),
                  "per_cpu_busy": busy, "sample_requested_seconds": SAMPLE_SECONDS,
                  "sample_elapsed_seconds": elapsed, "observer_cores": own_cores,
                  "quota_observations": observations,
                  "cpu_quota_spare_cores": min(quota_spares) if quota_spares else after["cpu_quota_cores"],
                  "idle_threshold": IDLE_THRESHOLD,
                  "numerical_thread_environment": {k: os.environ.get(k) for k in THREAD_ENV}})
    return after


def _lease_reservations(lease_path, eligible):
    receipt = {"path": str(lease_path) if lease_path is not None else None,
               "status": "NOT_REQUESTED", "reserved_cpus": [], "modified": False}
    if lease_path is None:
        return set(), receipt
    try:
        with Path(lease_path).open("rb") as f:
            raw = f.read(2 * MIB + 1)
        if len(raw) > 2 * MIB:
            raise ValueError("lease exceeds 2 MiB inspection limit")
        receipt["sha256"] = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw)
    except FileNotFoundError:
        receipt["status"] = "MISSING_AT_OBSERVATION"
        return set(), receipt
    except (OSError, ValueError, UnicodeError) as exc:
        receipt.update(status="UNREADABLE_RESERVED_ALL", reason=str(exc), reserved_cpus=sorted(eligible))
        return set(eligible), receipt
    reserved = set()
    try:
        schema = data.get("schema") if isinstance(data, dict) else None
        if schema not in (None, "C21_CPU_LEASES_V1"):
            raise ValueError("unknown schema")
        if isinstance(data, dict) and "owners" in data and isinstance(data["owners"], dict):
            for owner, cpus in data["owners"].items():
                if not isinstance(owner, str) or not owner:
                    raise ValueError("invalid owner")
                reserved.update(_cpu_ids(cpus))
        else:
            records = data.get("leases") if isinstance(data, dict) else data
            if not isinstance(records, list):
                raise ValueError("unknown lease shape")
            for record in records:
                if not isinstance(record, dict) or not isinstance(record.get("owner"), str) or not record["owner"]:
                    raise ValueError("invalid lease owner")
                reserved.update(_cpu_ids(record["cpus"]))
        receipt["status"] = "EXPLICIT_OWNER_LISTS"
    except (ValueError, TypeError, KeyError):
        def infer(node, key=""):
            if isinstance(node, int) and not isinstance(node, bool) and node >= 0:
                if node in eligible:
                    reserved.add(node)
            elif isinstance(node, dict):
                for k, v in node.items():
                    if str(k).isdigit() and int(k) in eligible:
                        reserved.add(int(k))
                    infer(v, str(k))
            elif isinstance(node, list):
                for v in node:
                    infer(v, key)
            elif isinstance(node, str):
                try:
                    reserved.update(_cpu_ids(node) & set(eligible))
                except ValueError:
                    pass
        infer(data)
        if reserved:
            receipt["status"] = "UNKNOWN_SCHEMA_INFERRED_RESERVED"
        else:
            reserved = set(eligible)
            receipt["status"] = "UNKNOWN_SCHEMA_RESERVED_ALL"
        receipt["inference"] = "Conservatively reserve plausible CPU IDs; semantics are unverified. No expiry or ownership is changed."
    receipt["reserved_cpus"] = sorted(reserved)
    return reserved, receipt


def _busy(snapshot, cpu):
    value = snapshot.get("per_cpu_busy", {}).get(cpu, snapshot.get("per_cpu_busy", {}).get(str(cpu), 1.))
    return float(value) if isinstance(value, (int, float)) and math.isfinite(value) else 1.


def _positive_mib(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(name + " must be a positive finite MiB allowance")
    return math.ceil(value * MIB)


def choose_workers(task_count, requested=None, per_worker_mib=512,
                   coordinator_mib=768, protected_cpus=(55,), lease_path=None):
    """Admit only pending jobs, accounting for one coordinator CPU/quota core."""
    if isinstance(task_count, bool) or not isinstance(task_count, int) or task_count < 0:
        raise ValueError("task_count must be a nonnegative integer")
    if requested is not None and (isinstance(requested, bool) or not isinstance(requested, int) or requested < 1):
        raise ValueError("requested must be a positive integer or None")
    worker_bytes = _positive_mib(per_worker_mib, "per_worker_mib")
    coordinator_bytes = _positive_mib(coordinator_mib, "coordinator_mib")
    protected = _cpu_ids(protected_cpus)
    s = observe_resources()
    candidates = set(s.get("allowed_cpus", ())) - protected
    leased, lease = _lease_reservations(lease_path, candidates)
    candidates.difference_update(leased)
    idle = sorted((c for c in candidates if _busy(s, c) <= IDLE_THRESHOLD), key=lambda c: (_busy(s, c), c))
    quota = s.get("cpu_quota_spare_cores")
    if not s.get("cpu_limit_observed") or not s.get("affinity_observed"):
        quota_slots = 0
    elif quota is None:
        quota_slots = max(0, len(idle) - 1)
    else:
        quota_slots = max(0, math.floor(quota - 1. + 1e-9))
    limit, available = s.get("memory_limit_bytes"), s.get("memory_available_bytes")
    reserve = max(GIB, math.ceil(limit / 8)) if limit is not None else GIB
    memory_slots = max(0, (available - reserve - coordinator_bytes) // worker_bytes) if available is not None and s.get("memory_observation_complete") else 0
    count = int(max(0, min(task_count, requested or MAX_WORKERS, MAX_WORKERS,
                           len(idle) - 1, quota_slots, memory_slots)))
    receipt = {"schema": "C21O_RESOURCE_ADMISSION_V1", "status": "ADMITTED" if count else "NO_WORK" if not task_count else "WAIT_FOR_RESOURCES",
               "workers": count, "max_workers": count, "task_count": task_count,
               "requested_workers": requested, "hard_worker_cap": MAX_WORKERS,
               "coordinator_cpu": idle[0] if count else None,
               "selected_worker_cpus": idle[1:count + 1] if count else [],
               "eligible_idle_cpus": idle, "protected_cpus": sorted(protected),
               "coordinator_quota_cores_reserved": 1,
               "cpu_quota_worker_slots": quota_slots, "memory_worker_slots": int(memory_slots),
               "per_worker_bytes": worker_bytes, "coordinator_bytes": coordinator_bytes,
               "memory_reserve_bytes": reserve, "lease": lease,
               "numerical_threads_per_worker": 1, "idle_threshold": IDLE_THRESHOLD,
               "snapshot": s, "exclusive_cpu_reservation": False,
               "memory_budget_basis": "Conservative planning allowance; not measured peak RSS or an enforced cap.",
               "caller_duties": "Apply own affinity and one-thread library settings; bound waits; preserve completed output; never touch another owner's work."}
    return count, receipt


def dispatch_allowed(snapshot, n_active, budget):
    """Return (bool, detail) for ONE extra dispatch, without stopping workers.

Current cgroup memory/CPU usage already includes active children. Thus fresh
headroom is charged for one additional worker plus reserve/coordinator margin,
while n_active is separately compared with the original admitted concurrency.
Host load average is recorded but is not a veto when local safe slots exist.
"""
    if isinstance(n_active, bool) or not isinstance(n_active, int) or n_active < 0:
        raise ValueError("n_active must be a nonnegative integer")
    reasons = []
    if n_active >= budget["max_workers"]:
        reasons.append("ADMITTED_CONCURRENCY_FULL")
    # Do not reinterpret the coordinator's deliberate one-CPU affinity as a
    # loss of the separately admitted workers' affinity. Preserve the initial
    # admission, then narrow only by a currently observed cgroup cpuset.
    eligible = set(budget["selected_worker_cpus"])
    if budget["coordinator_cpu"] is not None:
        eligible.add(budget["coordinator_cpu"])
    current_cpuset = snapshot.get("cgroup_cpuset")
    if current_cpuset is not None:
        eligible.intersection_update(current_cpuset)
    eligible.difference_update(budget["protected_cpus"])
    leased, lease = _lease_reservations(budget.get("lease", {}).get("path"), eligible)
    eligible.difference_update(leased)
    if budget["coordinator_cpu"] not in eligible:
        reasons.append("COORDINATOR_CPU_UNAVAILABLE")
    idle = sorted(c for c in budget["selected_worker_cpus"] if c in eligible and _busy(snapshot, c) <= budget["idle_threshold"])
    if not idle:
        reasons.append("NO_IDLE_ADMITTED_WORKER_CPU")
    spare = snapshot.get("cpu_quota_spare_cores")
    if not snapshot.get("cpu_limit_observed") or not snapshot.get("affinity_observed"):
        reasons.append("CPU_LIMIT_OR_AFFINITY_UNKNOWN")
    elif spare is not None and spare + 1e-9 < 2.:
        reasons.append("CPU_QUOTA_HEADROOM_LOW")
    available = snapshot.get("memory_available_bytes")
    current_limit = snapshot.get("memory_limit_bytes")
    reserve = max(budget["memory_reserve_bytes"], math.ceil(current_limit / 8) if current_limit is not None else GIB)
    required = reserve + budget["coordinator_bytes"] + budget["per_worker_bytes"]
    if not snapshot.get("memory_observation_complete") or available is None or available < required:
        reasons.append("MEMORY_HEADROOM_LOW_OR_UNKNOWN")
    return not reasons, {"schema": "C21O_DISPATCH_DECISION_V1", "allowed": not reasons,
                         "reasons": reasons, "n_active": n_active,
                         "max_workers": budget["max_workers"], "idle_worker_cpus": idle,
                         "required_fresh_memory_bytes": required,
                         "memory_reserve_bytes": reserve,
                         "available_memory_bytes": available,
                         "cpu_quota_spare_cores": spare, "lease": lease,
                         "existing_worker_action": "UNCHANGED",
                         "wait_policy": "Caller must enforce a finite deadline."}
