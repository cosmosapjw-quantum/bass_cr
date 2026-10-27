"""Bounded local CR clock dispatcher candidate; no work occurs on import.

One fresh coordinator process, one owned worker process group, immutable attempt
directories, exact source/input pins and retained actual cost receipts. Metadata
preparation, publication and remote CAS costs are recorded separately, not zeroed.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import resource
import secrets
import signal
import string
import subprocess
import sys
import time

UNIT_ID = "CR_RR_CAUSAL_ERLANG_CLOCK_V1"
MODES = ("controls", "primary", "independent", "plot")
STAGE_CAPS = {"controls": 5.0, "primary": 30.0, "independent": 15.0, "plot": 5.0}
TOTAL_CAP, COORDINATOR_CAP, UNUSED_R7 = 60.0, 2.0, 3.0
AS_LIMIT, MIN_RESERVE, WALL_LIMIT = 512 * 1024**2, 1024**3, 60.0
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
OMP_CONTROLS = {"OMP_DYNAMIC": "FALSE", "OMP_NESTED": "FALSE", "OMP_MAX_ACTIVE_LEVELS": "1"}
ROLES = {"code", "input", "contract", "previous_result"}
SHA256 = re.compile(r"[0-9a-f]{64}")


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def writej(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def decodej(raw):
    def bad(_):
        raise ValueError("nonfinite JSON constant")
    return json.loads(raw, parse_constant=bad)


def readj(path):
    return decodej(path.read_bytes())


def raw_pin(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def pin(path):
    h, size = hashlib.sha256(), 0
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            h.update(block)
            size += len(block)
    return {"bytes": size, "sha256": h.hexdigest()}


def cost(value):
    need(not isinstance(value, bool) and isinstance(value, (int, float))
         and math.isfinite(value) and value >= 0, "INVALID_ACTUAL_COST")
    return float(value)


def relative(value):
    need(isinstance(value, str), "RELATIVE_PATH_REQUIRED")
    p = PurePosixPath(value)
    need(p.parts and not p.is_absolute() and ".." not in p.parts and str(p) == value
         and "\\" not in value and not any(ord(c) < 32 for c in value), "UNSAFE_RELATIVE_PATH")
    return value


def admitted_file(unit, name):
    path = unit / relative(name)
    need(path.is_file() and path.resolve().is_relative_to(unit), "PINNED_REGULAR_UNIT_FILE_REQUIRED:" + name)
    for parent in (path, *path.parents):
        if parent == unit:
            break
        need(not parent.is_symlink(), "PINNED_SYMLINK_REJECTED:" + name)
    return path


def check_pin(unit, row):
    need(type(row) is dict and type(row.get("bytes")) is int and row["bytes"] >= 0
         and isinstance(row.get("sha256"), str) and SHA256.fullmatch(row["sha256"]), "INVALID_FILE_PIN")
    path = admitted_file(unit, row["path"])
    need(pin(path) == {"bytes": row["bytes"], "sha256": row["sha256"]},
         "EXACT_FILE_HASH_OR_SIZE_MISMATCH:" + row["path"])
    return path


def validate_plan(plan):
    need(type(plan) is dict and plan.get("schema") == "CR_CLOCK_EXECUTION_PLAN_V1"
         and plan.get("unit_id") == UNIT_ID, "EXECUTION_PLAN_IDENTITY")
    r = plan["resources"]
    exact = {"total_cpu_s": TOTAL_CAP, "coordinator_cpu_s": COORDINATOR_CAP,
             "r7_unused_reservation_s": UNUSED_R7, "wall_s": WALL_LIMIT,
             "RLIMIT_AS_bytes": AS_LIMIT, "native_threads": 1}
    need(all(not isinstance(r.get(k), bool) and r.get(k) == v for k, v in exact.items()),
         "FROZEN_RESOURCE_RESERVATION_MISMATCH")
    caps = r.get("stage_cpu_s")
    need(type(caps) is dict and set(caps) == set(STAGE_CAPS)
         and all(not isinstance(caps[k], bool) and caps[k] == v for k, v in STAGE_CAPS.items()),
         "FROZEN_STAGE_RESERVATION_MISMATCH")
    reserve = r.get("memory_reserve_bytes")
    need(type(reserve) is int and reserve >= MIN_RESERVE, "MINIMUM_ONE_GIB_RESERVE")
    cpus = r.get("cpus")
    need(type(cpus) is dict and set(cpus) == {"coordinator", "worker", "independent", "plot"}
         and all(type(c) is int and c >= 0 for c in cpus.values())
         and len(set(cpus.values())) == 4, "FOUR_DISTINCT_EXPLICIT_CPU_IDS_REQUIRED")
    commands = plan.get("mode_argv")
    need(type(commands) is dict and set(commands) == set(MODES), "ALL_MODE_ARGV_REQUIRED")
    for mode, argv in commands.items():
        need(type(argv) is list and argv and all(isinstance(a, str) and "\0" not in a for a in argv),
             "EXPLICIT_STRING_ARGV_REQUIRED:" + mode)
        need(relative(argv[0]).endswith(".py"), "PINNED_PYTHON_ENTRYPOINT_REQUIRED")
    return r


def prior_attempts(runs, current):
    rows = []
    for directory in sorted(runs.iterdir()):
        if not directory.is_dir() or directory == current:
            continue
        try:
            row = readj(directory / "DISPATCH_RECEIPT.json")
            need(row.get("schema") == "CR_CLOCK_BOUNDED_DISPATCH_V1"
                 and row.get("unit_id") == UNIT_ID and row.get("run_id") == directory.name
                 and row.get("mode") in MODES and row.get("accounting_complete") is True,
                 "INCOMPLETE_ATTEMPT_ACCOUNTING")
            cost(row["worker_cpu_s"])
            cost(row["coordinator_cpu_s"])
        except (OSError, ValueError, KeyError, TypeError, RuntimeError):
            raise RuntimeError("UNKNOWN_PRIOR_ATTEMPT_BUDGET:" + directory.name) from None
        rows.append(row)
    return rows


def accounting(rows, mode):
    worker = math.fsum(cost(r["worker_cpu_s"]) for r in rows)
    coordinator = math.fsum(cost(r["coordinator_cpu_s"]) for r in rows)
    stage = math.fsum(cost(r["worker_cpu_s"]) for r in rows if r["mode"] == mode)
    return {"worker_cpu_s": worker, "coordinator_cpu_s": coordinator,
            "stage_worker_cpu_s": stage, "total_cpu_s": worker + coordinator}


def process_memory_snapshot():
    values = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in {"VmRSS", "VmSize", "VmHWM", "VmPeak"}:
            amount, unit = value.split()
            need(unit == "kB", "PROCESS_MEMORY_UNIT")
            values[key + "_bytes"] = int(amount) * 1024
    need(len(values) == 4, "PROCESS_MEMORY_READBACK_INCOMPLETE")
    return {"pid": os.getpid(), **values}


def resource_snapshot(r):
    group = Path("/sys/fs/cgroup")
    stats = {k: int(v) for k, v in (line.split() for line in (group / "memory.stat").read_text().splitlines())}
    maximum_text, current = (group / "memory.max").read_text().strip(), int((group / "memory.current").read_text())
    need(maximum_text.isdecimal(), "FINITE_CGROUP_MEMORY_LIMIT_REQUIRED")
    maximum = int(maximum_text)
    need(maximum > 0 and current >= 0, "CGROUP_MEMORY_DOMAIN")
    for k in ("inactive_file", "file_dirty", "file_writeback", "shmem"):
        need(k in stats and stats[k] >= 0, "CGROUP_MEMORY_STAT_REQUIRED:" + k)
    meminfo = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in {"MemAvailable", "MemTotal"}:
            amount, unit = value.split()
            need(unit == "kB", "HOST_MEMORY_UNIT")
            meminfo[key + "_bytes"] = int(amount) * 1024
    need("MemAvailable_bytes" in meminfo, "HOST_MEMAVAILABLE_REQUIRED")
    clean = max(0, stats["inactive_file"] - stats["file_dirty"] - stats["file_writeback"] - stats["shmem"])
    # No active_file or slab_reclaimable credit; no cache dropping or unrelated kill.
    hypothetical_current = max(0, current - clean)
    group_available = max(0, maximum - hypothetical_current)
    available = min(meminfo["MemAvailable_bytes"], group_available)
    after_reserve = available - r["memory_reserve_bytes"]
    cpu_max = (group / "cpu.max").read_text().strip()
    quota, period = cpu_max.split()
    need(period.isdecimal() and int(period) > 0, "CPU_QUOTA_PERIOD")
    quota_ok = quota == "max" or (quota.isdecimal() and int(quota) >= 2 * int(period))
    affinity = sorted(os.sched_getaffinity(0))
    return {
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "affinity": affinity, "cpu_max": cpu_max, "coordinator_plus_worker_quota_admitted": quota_ok,
        "memory_max_bytes": maximum, "memory_current_bytes": current,
        "raw_memory_stat": stats, "host_memory": meminfo,
        "clean_inactive_file_bytes": clean, "conservative_available_before_reserve_bytes": available,
        "memory_reserve_bytes": r["memory_reserve_bytes"], "available_after_reserve_bytes": after_reserve,
        "RLIMIT_AS_bytes": AS_LIMIT, "memory_admitted": after_reserve >= AS_LIMIT,
        "formula": "clean=max(0,inactive_file-file_dirty-file_writeback-shmem); available=min(MemAvailable,memory.max-max(0,memory.current-clean))-reserve",
        "active_file_or_slab_reclaimability_credited": False, "cache_reclaimability_is_estimated": True,
        "drop_cache_or_kill_unrelated": False, "simultaneous_owned_workers": 1,
        "coordinator_process_memory": process_memory_snapshot(),
        "memory_events": (group / "memory.events").read_text(),
        "external_NCP_or_64core_scaling": "NOT_OBSERVED_NOT_CLAIMED",
    }


def verify_pins(unit, config_path, pins_path, config_raw):
    pins_raw = pins_path.read_bytes()
    data = decodej(pins_raw)
    need(type(data) is dict and data.get("schema") == "CR_CLOCK_SOURCE_PINS_V1"
         and data.get("unit_id") == UNIT_ID, "SOURCE_PINS_IDENTITY")
    need(data.get("config_sha256") == raw_pin(config_raw)["sha256"]
         and pin(config_path) == raw_pin(config_raw), "EXACT_CONFIG_HASH_REQUIRED")
    rows = data.get("files")
    need(type(rows) is list and rows, "SOURCE_INPUT_PIN_LIST_REQUIRED")
    seen = set()
    for row in rows:
        need(row.get("role") in ROLES, "UNADMITTED_PIN_ROLE")
        need(row["path"] not in seen, "DUPLICATE_SOURCE_PIN")
        seen.add(row["path"])
        check_pin(unit, row)
    need("implementation/dispatch.py" in seen, "DISPATCHER_SOURCE_PIN_REQUIRED")
    dispatch_row = next(r for r in rows if r["path"] == "implementation/dispatch.py")
    need(dispatch_row["role"] == "code" and pin(Path(__file__).resolve()) ==
         {"bytes": dispatch_row["bytes"], "sha256": dispatch_row["sha256"]}, "EXECUTING_DISPATCHER_PIN_MISMATCH")
    prep_pin = data.get("preparation_receipt")
    prep_path = check_pin(unit, prep_pin)
    prep = readj(prep_path)
    need(prep.get("no_prior_local_science_before_first_worker") is True
         and type(prep.get("prior_local_science_attempt_count")) is int
         and prep["prior_local_science_attempt_count"] == 0
         and "metadata_code_preparation_cpu_s" in prep and prep["metadata_code_preparation_cpu_s"] is None,
         "EXPLICIT_INITIAL_NO_SCIENCE_ATTESTATION_REQUIRED")
    need(prep.get("missing_prior_local_science_attempts", False) is False,
         "UNKNOWN_PREPARATION_SCIENCE_HISTORY")
    return data, prep_path, pins_raw


def snapshot_sources(unit, out, config_raw, pins_raw, pins, prep_path):
    dest = out / "EXECUTED_SOURCE"
    dest.mkdir()
    copied = []
    for row in pins["files"]:
        if row["role"] not in {"code", "contract"}:
            continue
        source = admitted_file(unit, row["path"])
        target = dest / relative(row["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        h, size = hashlib.sha256(), 0
        with source.open("rb") as incoming, target.open("xb") as outgoing:
            while block := incoming.read(1024 * 1024):
                outgoing.write(block)
                h.update(block)
                size += len(block)
        need({"bytes": size, "sha256": h.hexdigest()} == {"bytes": row["bytes"], "sha256": row["sha256"]},
             "SOURCE_CHANGED_DURING_SNAPSHOT:" + row["path"])
        copied.append({"path": row["path"], "role": row["role"], "bytes": size, "sha256": h.hexdigest()})
    admission = dest / "_admission"
    admission.mkdir()
    prep_raw = prep_path.read_bytes()
    need(raw_pin(prep_raw) == {"bytes": pins["preparation_receipt"]["bytes"],
                              "sha256": pins["preparation_receipt"]["sha256"]}, "PREPARATION_RECEIPT_DRIFT")
    for name, raw in (("EXECUTION_PLAN.json", config_raw), ("SOURCE_PINS.json", pins_raw),
                      ("PREPARATION_RECEIPT.json", prep_raw)):
        with (admission / name).open("xb") as stream:
            stream.write(raw)
    return dest, copied


def render_command(plan, mode, unit, out, snapshot, run_id):
    values = {
        "unit": str(unit), "output": str(out), "run_id": run_id, "snapshot": str(snapshot),
        "config": str(snapshot / "_admission/EXECUTION_PLAN.json"),
        "pins": str(snapshot / "_admission/SOURCE_PINS.json"),
    }
    argv = plan["mode_argv"][mode]
    for token in argv[1:]:
        for _, field, spec, conv in string.Formatter().parse(token):
            need(field is None or (field in values and not spec and not conv), "UNKNOWN_ARGV_TEMPLATE_FIELD")
    return [sys.executable, "-B", str(snapshot / relative(argv[0])),
            *(token.format_map(values) for token in argv[1:])]


def worker_identity(nonce):
    """Bind the child's PID namespace to the procfs mounted in this host."""
    raw = Path('/proc/self/stat').read_text()
    proc_pid = int(raw.split(' ', 1)[0])
    fields = raw[raw.rfind(')') + 2:].split()
    need(str(proc_pid) == os.readlink('/proc/self'), 'PROC_SELF_IDENTITY_MISMATCH')
    return {'namespace_pid': os.getpid(), 'proc_pid': proc_pid,
            'starttime_ticks': int(fields[19]), 'lease_nonce': nonce,
            'binding': 'child_preexec_actual_proc_self'}


def process_cpu(identity):
    try:
        raw = Path(f"/proc/{identity['proc_pid']}/stat").read_text()
    except FileNotFoundError:
        return None
    fields = raw[raw.rfind(")") + 2:].split()
    need(int(raw.split(' ', 1)[0]) == identity['proc_pid']
         and int(fields[19]) == identity['starttime_ticks'],
         'OWNED_WORKER_PROC_IDENTITY_CHANGED')
    return (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK")


def group_alive(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def terminate_owned(child, *, grace=.15):
    """Only the group created by this dispatcher's Popen is ever targeted."""
    if child is None:
        return True
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        child.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        pass
    if group_alive(child.pid):
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        child.wait(timeout=.15)
    except subprocess.TimeoutExpired:
        return False
    return not group_alive(child.pid)


def watch(child, identity, worker_limit, coordinator_prior, wall_deadline):
    while child.poll() is None:
        if time.monotonic() >= wall_deadline - .5:
            raise RuntimeError("OWNED_WORKER_WALL_GUARD")
        if coordinator_prior + time.process_time() >= COORDINATOR_CAP - .02:
            raise RuntimeError("COORDINATOR_CPU_GUARD")
        observed = process_cpu(identity)
        if observed is not None and observed >= worker_limit - .05:
            raise RuntimeError("OWNED_WORKER_CPU_GUARD")
        try:
            return child.wait(timeout=.02)
        except subprocess.TimeoutExpired:
            pass
    return child.returncode


def run(args):
    wall_start = time.monotonic()
    unit, config_path, pins_path = args.unit.resolve(), args.config.resolve(), args.pins.resolve()
    need(unit.is_dir(), "EXISTING_UNIT_REQUIRED")
    need(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.run_id), "SIMPLE_UNIQUE_RUN_ID_REQUIRED")
    out = unit / "runs" / args.run_id
    out.mkdir(parents=True, exist_ok=False)
    lease = unit / "implementation/.cr_clock_task_lease"
    nonce = secrets.token_hex(16)
    owned_lease, child, child_spawn_attempted = False, None, False
    child_reaped, accounting_complete = True, True
    command, limit, state, before_budget, source_pins = None, None, None, None, None
    status, error, returncode = "FAILED_RETAINED", None, None
    before_children = resource.getrusage(resource.RUSAGE_CHILDREN)
    original_affinity = os.sched_getaffinity(0)
    cleanup_note = None
    try:
        writej(lease, {"pid": os.getpid(), "nonce": nonce, "run_id": args.run_id,
                       "mode": args.mode, "created_utc": datetime.now(timezone.utc).isoformat()})
        owned_lease = True
        config_raw = config_path.read_bytes()
        plan = decodej(config_raw)
        r = validate_plan(plan)
        previous = prior_attempts(unit / "runs", out)
        before_budget = accounting(previous, args.mode)
        need(before_budget["coordinator_cpu_s"] + time.process_time() < COORDINATOR_CAP - .02,
             "COORDINATOR_RESERVATION_EXHAUSTED")
        remaining_coordinator = max(0.0, COORDINATOR_CAP - before_budget["coordinator_cpu_s"])
        available = min(
            STAGE_CAPS[args.mode] - before_budget["stage_worker_cpu_s"],
            TOTAL_CAP - before_budget["total_cpu_s"] - remaining_coordinator - UNUSED_R7,
        )
        limit = math.floor(available)
        need(limit >= 1, "NEW_UNIT_WORKER_RESERVATION_EXHAUSTED")
        state = resource_snapshot(r)
        writej(out / "RESOURCE_ADMISSION.json", state)
        need(state["memory_admitted"], "MEMORY_ADMISSION_REJECTED")
        need(state["coordinator_plus_worker_quota_admitted"], "COORDINATOR_AND_WORKER_QUOTA_REQUIRED")
        need(set(r["cpus"].values()) <= set(state["affinity"]), "CPU_AFFINITY_ADMISSION_REJECTED")
        worker = r["cpus"]["independent"] if args.mode == "independent" else r["cpus"]["plot"] if args.mode == "plot" else r["cpus"]["worker"]
        os.sched_setaffinity(0, {r["cpus"]["coordinator"]})
        source_pins, prep_path, pins_raw = verify_pins(unit, config_path, pins_path, config_raw)
        script = plan["mode_argv"][args.mode][0]
        need(any(row["path"] == script and row["role"] == "code" for row in source_pins["files"]),
             "WORKER_ENTRYPOINT_NOT_PINNED")
        snapshot, copied = snapshot_sources(unit, out, config_raw, pins_raw, source_pins, prep_path)
        need(pin(config_path) == raw_pin(config_raw) and pin(pins_path) == raw_pin(pins_raw),
             "CONFIG_OR_PINS_CHANGED_DURING_PREPARATION")
        command = render_command(plan, args.mode, unit, out, snapshot, args.run_id)
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment.update({key: "1" for key in THREADS})
        environment.update(OMP_CONTROLS)
        environment.update(PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1",
                           CR_CLOCK_WORKER_CPU_CAP_S=str(limit), MPLCONFIGDIR=str(out / "mpl_config"))
        writej(out / "PRE_EXECUTION.json", {
            "schema": "CR_CLOCK_PRE_EXECUTION_V1", "unit_id": UNIT_ID, "run_id": args.run_id,
            "mode": args.mode, "command": command, "config_pin": raw_pin(config_raw), "pins_pin": raw_pin(pins_raw),
            "source_pins": source_pins["files"], "executed_source_copies": copied,
            "worker_CPU_limit_s": limit, "worker_CPU_guard_s": max(0, limit - .05),
            "wall_limit_s": WALL_LIMIT, "RLIMIT_AS_bytes": AS_LIMIT, "worker_cpu": worker,
            "coordinator_cpu": r["cpus"]["coordinator"], "native_threads": 1,
            "thread_environment": {key: "1" for key in THREADS}, "openmp_controls": OMP_CONTROLS,
            "CR_CLOCK_WORKER_CPU_CAP_S": str(limit), "prior_accounting": before_budget,
            "new_unit_total_cpu_s": TOTAL_CAP, "R7_unused_reserved_cpu_s": UNUSED_R7,
            "budget_scope": "NEW_LOCAL_SCIENTIFIC_WORKER_AND_DISPATCHER_COORDINATOR_ONLY",
            "metadata_preparation_CPU_s": None, "publication_and_remote_CAS_excluded_separately": True,
            "historical_allowance_reused": False,
            "live_pinned_inputs_prechecked_worker_must_verify_on_load": True,
        })
        need(before_budget["coordinator_cpu_s"] + time.process_time() < COORDINATOR_CAP - .02,
             "COORDINATOR_RESERVATION_EXHAUSTED_DURING_PREPARATION")
        need(time.monotonic() < wall_start + WALL_LIMIT - .5, "NO_WORKER_WALL_BUDGET_REMAINS")

        def limits():
            os.sched_setaffinity(0, {worker})
            resource.setrlimit(resource.RLIMIT_AS, (AS_LIMIT, AS_LIMIT))
            resource.setrlimit(resource.RLIMIT_CPU, (limit, limit))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            writej(out / 'OWNED_WORKER_IDENTITY.json', worker_identity(nonce))

        with (out / "stdout.txt").open("x") as stdout, (out / "stderr.txt").open("x") as stderr:
            child_spawn_attempted = True
            child = subprocess.Popen(command, cwd=Path(command[2]).parent, env=environment,
                                     stdout=stdout, stderr=stderr, start_new_session=True, preexec_fn=limits)
            child_reaped = False
            identity = readj(out / 'OWNED_WORKER_IDENTITY.json')
            need(identity['namespace_pid'] == child.pid and identity['lease_nonce'] == nonce,
                 'OWNED_WORKER_NAMESPACE_BINDING_MISMATCH')
            returncode = watch(child, identity, limit, before_budget["coordinator_cpu_s"], wall_start + WALL_LIMIT)
            child_reaped = True
        need(not group_alive(child.pid), "UNEXPECTED_OWNED_DESCENDANT_PROCESS")
        need(returncode == 0, "WORKER_NONZERO_EXIT")
        # Detect live input/source drift; these files are not silently recopied.
        for row in source_pins["files"]:
            check_pin(unit, row)
        need(pin(config_path) == pin(snapshot / "_admission/EXECUTION_PLAN.json")
             and pin(pins_path) == pin(snapshot / "_admission/SOURCE_PINS.json"), "CONFIG_OR_PINS_CHANGED_DURING_RUN")
        status = "PASS"
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        if child is not None and (child.poll() is None or group_alive(child.pid)):
            child_reaped = terminate_owned(child)
            returncode = child.returncode
            if not child_reaped:
                accounting_complete = False
                cleanup_note = "OWNED_GROUP_NOT_REAPED; lease retained; no further dispatch may assume zero cost"
        try:
            os.sched_setaffinity(0, original_affinity)
        except OSError as exc:
            status = "FAILED_RETAINED"
            error = {"type": type(exc).__name__, "message": "COORDINATOR_AFFINITY_RESTORE_FAILED"}
        after_children = resource.getrusage(resource.RUSAGE_CHILDREN)
        worker_cost = (after_children.ru_utime + after_children.ru_stime
                       - before_children.ru_utime - before_children.ru_stime) if accounting_complete else None
        final_prior, prior_error = None, None
        try:
            final_prior = accounting(prior_attempts(unit / "runs", out), args.mode)
        except RuntimeError as exc:
            prior_error = str(exc)
            status = "BLOCKED_UNKNOWN_PRIOR_ATTEMPT_BUDGET"
        if not accounting_complete:
            status = "UNKNOWN_OWNED_CHILD_ACCOUNTING"
        elif (worker_cost is None or worker_cost < 0 or not math.isfinite(worker_cost)):
            accounting_complete = False
            status = "UNKNOWN_OWNED_CHILD_ACCOUNTING"
        if owned_lease and accounting_complete:
            try:
                owner = readj(lease)
                need(owner.get("pid") == os.getpid() and owner.get("nonce") == nonce,
                     "LEASE_OWNERSHIP_CHANGED")
                lease.unlink()
            except (OSError, ValueError, RuntimeError) as exc:
                status = "FAILED_RETAINED"
                cleanup_note = "Lease not removed without exact owner match: " + type(exc).__name__
        coordinator_cost = time.process_time()
        wall_used = time.monotonic() - wall_start
        if accounting_complete and final_prior is not None and (
            final_prior["stage_worker_cpu_s"] + worker_cost > STAGE_CAPS[args.mode]
            or final_prior["coordinator_cpu_s"] + coordinator_cost > COORDINATOR_CAP
            or final_prior["total_cpu_s"] + worker_cost + coordinator_cost + UNUSED_R7 > TOTAL_CAP
        ):
            status = "FAILED_RETAINED"
            error = {"type": "ResourceBudgetExceeded", "message": "MEASURED_STAGE_COORDINATOR_OR_UNIT_CEILING"}
        if wall_used > WALL_LIMIT:
            status = "FAILED_RETAINED" if accounting_complete else status
            error = {"type": "WallBudgetExceeded", "message": "MEASURED_INVOCATION_WALL_CEILING"}
        receipt = {
            "schema": "CR_CLOCK_BOUNDED_DISPATCH_V1", "unit_id": UNIT_ID, "run_id": args.run_id,
            "mode": args.mode, "status": status, "error": error,
            "accounting_complete": accounting_complete, "prior_accounting_error": prior_error,
            "child_spawn_attempted": child_spawn_attempted, "child_pid": child.pid if child else None,
            "owned_process_group": child.pid if child else None, "child_reaped": child_reaped,
            "returncode": returncode, "command": command,
            "worker_cpu_s": worker_cost, "coordinator_cpu_s": coordinator_cost, "wall_s": wall_used,
            "cost_measurement": "Actual RUSAGE_CHILDREN delta and process_time through final accounting; final receipt serialization/write is outside the sample",
            "worker_peak_RSS_KiB": after_children.ru_maxrss if child_spawn_attempted else None,
            "worker_CPU_limit_s": limit, "wall_limit_s": WALL_LIMIT, "RLIMIT_AS_bytes": AS_LIMIT,
            "new_unit_prior_actual_cpu": final_prior,
            "new_unit_cumulative_cpu_s": final_prior["total_cpu_s"] + worker_cost + coordinator_cost
                if final_prior is not None and accounting_complete else None,
            "new_unit_total_cpu_cap_s": TOTAL_CAP, "stage_cpu_cap_s": STAGE_CAPS[args.mode],
            "coordinator_cpu_cap_s": COORDINATOR_CAP, "R7_unused_reserved_cpu_s": UNUSED_R7,
            "metadata_code_preparation_cpu_s": None, "metadata_preparation_not_reported_as_zero": True,
            "publication_and_remote_Wolfram_CPU_scope": "SEPARATE; NOT_ZEROED_OR_TRANSFERRED",
            "historical_allowance_reused": False, "global_remaining": None, "currency": None,
            "cleanup_note": cleanup_note,
            "EXECUTION": status, "SCIENTIFIC_VALIDITY": "WORKER_AND_INDEPENDENT_REVIEW_OWNED",
            "PUBLICATION": "ROOT_OWNED", "BACKUP": "ROOT_PENDING", "DAG": "NO_AUTOMATIC_PROMOTION",
        }
        writej(out / "DISPATCH_RECEIPT.json", receipt)
    print(json.dumps({"output": str(out), **receipt}, ensure_ascii=False, allow_nan=False))
    return 0 if status == "PASS" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--pins", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run(args)
    except Exception as exc:
        # An unsafe/duplicate run path is never overwritten to attach a receipt.
        print(json.dumps({"status": "REFUSED_BEFORE_NEW_ATTEMPT_OR_RECEIPT_WRITE_FAILED",
                          "type": type(exc).__name__, "message": str(exc),
                          "coordinator_cpu_observed_s": time.process_time(),
                          "old_attempt_or_lease_overwritten": False}, allow_nan=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

