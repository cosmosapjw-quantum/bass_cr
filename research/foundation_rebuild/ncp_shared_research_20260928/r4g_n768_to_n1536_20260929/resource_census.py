"""Durable, process-group-aware resource census for one N1536 run."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import statistics
import time


class ExternalResourceOverlap(ValueError):
    pass


class OwnPoolTeardownIncomplete(ValueError):
    pass


def _write_new(path: Path, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def _identity(pid: int, *, proc_root: Path, affinity_lookup) -> dict | None:
    root = proc_root / str(pid)
    try:
        fields = (root / "stat").read_text().rsplit(")", 1)[1].split()
        raw_cmd = (root / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
        # Process arguments are evidence, but may contain credentials. Match on
        # the original command and persist only a bounded, redacted rendering.
        cmd = re.sub(r"(?i)(--?(?:token|password|passwd|secret|api[-_]key|credential)(?:=|\s+))\S+",
                     r"\1[REDACTED]", raw_cmd)
        cg = (root / "cgroup").read_text().strip()
        return {"pid": pid, "ppid": int(fields[1]), "pgid": int(fields[2]),
                "sid": int(fields[3]), "state": fields[0],
                "cpu_time_ticks": (int(fields[11]) + int(fields[12])
                                   if len(fields) > 12 else None),
                "start_time_ticks": int(fields[19]) if len(fields) > 19 else None,
                "cmdline": cmd[:300], "cmdline_truncated": len(cmd) > 300,
                "bass_candidate": bool(re.search(r"BASS_HE|WU088_HH|bass_cr", raw_cmd, re.I)
                                       and re.search(r"python|worker|science|runtime", raw_cmd, re.I)),
                "cpu_affinity": sorted(affinity_lookup(pid)), "cgroup": cg[:300]}
    except (OSError, ProcessLookupError, IndexError, ValueError):
        return None


def _ancestors(pid: int, proc_root: Path) -> set[int]:
    result = {pid}
    current = pid
    while current > 1:
        try:
            fields = (proc_root / str(current) / "stat").read_text().rsplit(")", 1)[1].split()
            parent = int(fields[1])
        except (OSError, IndexError, ValueError):
            break
        if parent in result or parent < 1:
            break
        result.add(parent)
        current = parent
    return result


def classify_ownership(row: dict, *, self_pid: int, ancestors: set[int], run_pgid: int) -> str:
    if row["pid"] == self_pid:
        return "SELF"
    if row["pid"] in ancestors:
        return "ANCESTOR"
    if row["pgid"] == run_pgid:
        return "SAME_RUN_PROCESS_GROUP"
    return "EXTERNAL"


def collect_bass_candidates(requested: set[int], *, proc_root: Path = Path("/proc"),
                            affinity_lookup=None, self_pid: int | None = None,
                            run_pgid: int | None = None) -> list[dict]:
    affinity_lookup = affinity_lookup or os.sched_getaffinity
    self_pid = os.getpid() if self_pid is None else self_pid
    run_pgid = os.getpgrp() if run_pgid is None else run_pgid
    ancestors = _ancestors(self_pid, proc_root)
    rows = []
    for proc in proc_root.iterdir():
        if not proc.name.isdigit():
            continue
        row = _identity(int(proc.name), proc_root=proc_root,
                        affinity_lookup=affinity_lookup)
        if row is None or not row["bass_candidate"]:
            continue
        row["ownership"] = classify_ownership(row, self_pid=self_pid,
                                               ancestors=ancestors, run_pgid=run_pgid)
        row["requested_cpu_intersection"] = sorted(requested.intersection(row["cpu_affinity"]))
        rows.append(row)
    return sorted(rows, key=lambda x: x["pid"])


def _cpu_rows(raw: str) -> dict[int, tuple[int, int]]:
    rows = {}
    for line in raw.splitlines():
        parts = line.split()
        if not parts or not re.fullmatch(r"cpu\d+", parts[0]):
            continue
        values = [int(x) for x in parts[1:9]]
        if len(values) < 5:
            continue
        rows[int(parts[0][3:])] = (sum(values), values[3] + values[4])
    return rows


def _pressure(requested: set[int], peers: list[dict], *, proc_root: Path,
              affinity_lookup, proc_stat_reader, sleep_fn, sample_interval: float) -> dict:
    if not 0 <= sample_interval <= 1 or not math.isfinite(sample_interval):
        raise ValueError("bounded CPU-pressure sample interval required")
    before = _cpu_rows(proc_stat_reader())
    start = time.monotonic()
    peer_before = {r["pid"]: r for r in peers}
    sleep_fn(sample_interval)
    elapsed = time.monotonic() - start
    after = _cpu_rows(proc_stat_reader())
    busy = {}
    for cpu in sorted(requested):
        if cpu not in before or cpu not in after:
            raise ValueError("CPU-pressure sample missing approved CPU")
        total = after[cpu][0] - before[cpu][0]
        idle = after[cpu][1] - before[cpu][1]
        if total < 0 or idle < 0 or idle > total:
            raise ValueError("CPU-pressure counters invalid")
        busy[str(cpu)] = (total - idle) / total if total else 0.0
    values = list(busy.values())
    peer_deltas = {}
    for pid, first in peer_before.items():
        second = _identity(pid, proc_root=proc_root, affinity_lookup=affinity_lookup)
        if (second is not None and first["cpu_time_ticks"] is not None
            and second["cpu_time_ticks"] is not None
            and first["start_time_ticks"] == second["start_time_ticks"]
            and second["cpu_time_ticks"] >= first["cpu_time_ticks"]):
            peer_deltas[str(pid)] = ((second["cpu_time_ticks"] - first["cpu_time_ticks"])
                                     / os.sysconf("SC_CLK_TCK"))
    try:
        load_average = list(os.getloadavg())
    except OSError:
        load_average = None
    return {"per_cpu_busy_fraction": busy,
            "approved_cpu_mean_busy": statistics.mean(values) if values else None,
            "approved_cpu_median_busy": statistics.median(values) if values else None,
            "approved_cpu_max_busy": max(values) if values else None,
            "external_peer_cpu_time_delta_seconds": peer_deltas,
            "sample_interval_seconds": elapsed, "load_average": load_average}


def live_resource_census(cpus: list[int], workers: int, worker_ram_bytes: int,
                         *, receipt_path: Path, proc_root: Path = Path("/proc"),
                         affinity_lookup=None, self_pid: int | None = None,
                         run_pgid: int | None = None,
                         allowed: set[int] | None = None,
                         mem_available_bytes: int | None = None,
                         quota_cores: float | None = None,
                         sharing_policy: str = "EXCLUSIVE",
                         proc_stat_reader=None, sleep_fn=None,
                         sample_interval: float = 0.2) -> dict:
    """Persist the whole process census before reporting an overlap or limit failure."""
    affinity_lookup = affinity_lookup or os.sched_getaffinity
    if sharing_policy not in ("EXCLUSIVE", "COOPERATIVE_SHARED_HOST"):
        raise ValueError("unknown resource sharing policy")
    proc_stat_reader = proc_stat_reader or (lambda: Path("/proc/stat").read_text())
    sleep_fn = sleep_fn or time.sleep
    requested = set(cpus[:workers])
    allowed = set(affinity_lookup(0)) if allowed is None else set(allowed)
    if mem_available_bytes is None:
        meminfo = Path("/proc/meminfo").read_text()
        match = re.search(r"^MemAvailable:\s+(\d+) kB$", meminfo, re.M)
        mem_available_bytes = int(match.group(1)) * 1024 if match else -1
        cgroup_root = Path("/sys/fs/cgroup")
        cgroup_path = Path("/proc/self/cgroup").read_text().strip().split("::", 1)[-1].lstrip("/")
        node = cgroup_root / cgroup_path
        while node.is_relative_to(cgroup_root):
            memory_max = node / "memory.max"
            memory_current = node / "memory.current"
            if memory_max.is_file() and memory_current.is_file():
                limit = memory_max.read_text().strip()
                if limit != "max":
                    mem_available_bytes = min(mem_available_bytes,
                        max(0, int(limit) - int(memory_current.read_text().strip())))
            cpu_max = node / "cpu.max"
            if cpu_max.is_file():
                q, period = cpu_max.read_text().split()[:2]
                if q != "max":
                    value = int(q) / int(period)
                    quota_cores = value if quota_cores is None else min(quota_cores, value)
            if node == cgroup_root:
                break
            node = node.parent
    candidates = collect_bass_candidates(requested, proc_root=proc_root,
        affinity_lookup=affinity_lookup, self_pid=self_pid, run_pgid=run_pgid)
    offenders = [r for r in candidates if r["ownership"] == "EXTERNAL"
                 and r["requested_cpu_intersection"] and r["state"] not in ("Z", "X")]
    pressure = _pressure(requested, offenders, proc_root=proc_root,
        affinity_lookup=affinity_lookup, proc_stat_reader=proc_stat_reader,
        sleep_fn=sleep_fn, sample_interval=sample_interval)
    need = workers * worker_ram_bytes + (4 << 30)
    reason = None
    if len(requested) != workers or not requested.issubset(allowed):
        reason = "LIVE_CPU_AFFINITY_INVALID"
    elif quota_cores is not None and quota_cores < workers:
        reason = "LIVE_CPU_QUOTA_INVALID"
    elif mem_available_bytes < need:
        reason = "LIVE_RAM_SCOPE_INVALID"
    elif offenders and sharing_policy == "EXCLUSIVE":
        reason = "EXTERNAL_BASS_CPU_OVERLAP"
    receipt = {"schema": "BASS_R4K_STRUCTURED_RESOURCE_CENSUS_V1",
               "requested_cpus": sorted(requested), "allowed_affinity": sorted(allowed),
               "workers": workers, "worker_ram_bytes": worker_ram_bytes,
               "quota_cores": quota_cores, "mem_available_bytes": mem_available_bytes,
               "required_available_bytes": need, "candidate_processes": candidates,
               "external_offender_pids": [r["pid"] for r in offenders],
               "external_peer_pids": [r["pid"] for r in offenders],
               "resource_sharing_policy": sharing_policy,
               "cpu_pressure": pressure,
               "status": (reason or ("PASS_SHARED_HOST_PEERS_PRESENT"
                   if offenders and sharing_policy == "COOPERATIVE_SHARED_HOST" else "PASS")),
               "checked_unix": time.time()}
    _write_new(receipt_path, receipt)
    if offenders and sharing_policy == "EXCLUSIVE":
        raise ExternalResourceOverlap("EXTERNAL_BASS_CPU_OVERLAP: " +
            ",".join(map(str, receipt["external_offender_pids"])) +
            "; evidence=" + str(receipt_path))
    if reason is not None:
        raise ValueError(reason + "; evidence=" + str(receipt_path))
    return receipt


def verify_prior_pool_teardown(worker_pids: set[int], *, run_pgid: int,
                               receipt_path: Path, settle_seconds: float = 3.0,
                               proc_root: Path = Path("/proc"), affinity_lookup=None) -> dict:
    """Wait briefly for completed workers; never relabel their remnants external."""
    affinity_lookup = affinity_lookup or os.sched_getaffinity
    until = time.monotonic() + settle_seconds
    while True:
        lingering = []
        for pid in sorted(worker_pids):
            row = _identity(pid, proc_root=proc_root, affinity_lookup=affinity_lookup)
            if row is not None:
                lingering.append(row)
            elif (proc_root / str(pid)).exists():
                lingering.append({"pid": pid, "identity_unavailable": True})
        if not lingering or time.monotonic() >= until:
            break
        time.sleep(min(0.1, max(0, until - time.monotonic())))
    same_group = []
    for proc in proc_root.iterdir():
        if not proc.name.isdigit():
            continue
        row = _identity(int(proc.name), proc_root=proc_root, affinity_lookup=affinity_lookup)
        if row is not None and row["pgid"] == run_pgid:
            same_group.append(row)
    unknown_workers = [r for r in same_group if r["pid"] != os.getpid()
                       and "spawn_main" in r["cmdline"]
                       and r["pid"] not in worker_pids]
    receipt = {"schema": "BASS_R4K_PRIOR_POOL_TEARDOWN_V1",
               "prior_worker_pids": sorted(worker_pids), "lingering_workers": lingering,
               "unreceipted_same_group_workers": unknown_workers,
               "same_run_process_group": sorted(same_group, key=lambda x: x["pid"]),
               "run_pgid": run_pgid,
               "status": "OWN_POOL_TEARDOWN_INCOMPLETE" if lingering or unknown_workers else "PASS",
               "checked_unix": time.time()}
    _write_new(receipt_path, receipt)
    if lingering or unknown_workers:
        raise OwnPoolTeardownIncomplete("OWN_POOL_TEARDOWN_INCOMPLETE; evidence=" +
                                        str(receipt_path))
    return receipt
