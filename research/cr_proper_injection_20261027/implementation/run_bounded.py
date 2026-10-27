#!/usr/bin/env python3
"""Create-only worker attempts with a 20 s, failure-inclusive unit CPU ledger.

Immutable attempt debits are authoritative. The mutable ledger is a reconciled
index, so a failed lock, argument parse, snapshot, or ledger write cannot make an
attempt disappear. A normal receipt and any later accounting debit share one
attempt_id; reconciliation charges the largest cumulative debit, not their sum.
No prior unit's unused allowance is imported.
"""
import argparse
import ctypes
import datetime
import fcntl
import hashlib
import json
import math
import os
import pathlib
import re
import resource
import signal
import subprocess
import sys
import time
import uuid


UNIT = pathlib.Path(__file__).resolve().parents[1]
UNIT_ID = "CR_PROPER_INJECTION_RETURN_V1"
HARD_CAP_S = 20.0
EVIDENCE = UNIT / "evidence"
LEDGER = EVIDENCE / "EXECUTION_LEDGER.json"
DEBITS = EVIDENCE / "ATTEMPT_DEBITS"
STATUSES = EVIDENCE / "BUDGET_STATUS"
RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")


def cpu(who):
    value = resource.getrusage(who)
    return value.ru_utime + value.ru_stime


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def finite_nonnegative(value, name):
    need(type(value) in (int, float) and math.isfinite(value) and value >= 0,
         name + ":FINITE_NONNEGATIVE_REQUIRED")
    return float(value)


def json_bytes(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf-8")


def atomic_json(path, value, *, create_only):
    """Publish complete bytes; hard-link publication never replaces a receipt."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(json_bytes(value))
            stream.flush()
            os.fsync(stream.fileno())
        if create_only:
            os.link(temporary, path)
        else:
            os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def attempt_key(receipt):
    key = receipt.get("attempt_id")
    if key is not None:
        need(isinstance(key, str) and key.startswith("attempt_")
             and RUN_ID.fullmatch(key) is not None, "INVALID_RECEIPT_ATTEMPT_ID")
        return key
    # Immutable receipts from the first runner version have only run_id.
    run_id = receipt.get("run_id")
    need(isinstance(run_id, str) and bool(run_id), "LEGACY_RECEIPT_RUN_ID_REQUIRED")
    return "legacy_run_id:" + run_id


def checked_cost(receipt):
    need(isinstance(receipt, dict), "RECEIPT_OBJECT_REQUIRED")
    need(receipt.get("unit", UNIT_ID) == UNIT_ID, "FOREIGN_UNIT_DEBIT_REFUSED")
    worker = finite_nonnegative(receipt["worker_cpu_s"], "worker_cpu_s")
    coordinator = finite_nonnegative(receipt["coordinator_cpu_through_receipt_s"],
                                     "coordinator_cpu_through_receipt_s")
    tail = finite_nonnegative(receipt["receipt_tail_reserve_s"], "receipt_tail_reserve_s")
    charged = finite_nonnegative(receipt["charged_cpu_s"], "charged_cpu_s")
    need(charged + 1e-12 >= math.fsum((worker, coordinator, tail)),
         "RECEIPT_UNDERCHARGES_RECORDED_CPU")
    return charged


def reconcile(budget, *, active_reservation=None):
    """Read all cost evidence; malformed or inconsistent evidence fails closed."""
    selected = {}
    paths = {}

    def add(receipt, path):
        key = attempt_key(receipt)
        cost = checked_cost(receipt)
        paths.setdefault(key, set()).add(path)
        paths[key].update(receipt.get("accounting_source_paths", []))
        if key in selected:
            need(selected[key].get("run_id") == receipt.get("run_id"),
                 "ATTEMPT_ID_RUN_ID_COLLISION")
        if key not in selected or cost > selected[key]["charged_cpu_s"]:
            selected[key] = dict(receipt)

    baseline = finite_nonnegative(budget.get("spent_before_C4_admission", 0.0),
                                  "spent_before_C4_admission")
    if LEDGER.exists():
        old = json.loads(LEDGER.read_bytes())
        need(old.get("unit") == UNIT_ID and isinstance(old.get("attempts"), list),
             "INVALID_OR_FOREIGN_EXECUTION_LEDGER")
        need(old.get("baseline_preparation_cpu_s", baseline) == baseline,
             "PREPARATION_BASELINE_CHANGED")
        for item in old["attempts"]:
            add(item, str(LEDGER.relative_to(UNIT)))
        old_sum = math.fsum((baseline, *(r["charged_cpu_s"] for r in selected.values())))
        if "charged_cpu_s" in old:
            stored_total = finite_nonnegative(old["charged_cpu_s"], "ledger.charged_cpu_s")
            need(abs(stored_total - old_sum) <= 1e-10,
                 "LEDGER_TOTAL_DISAGREES_WITH_UNIQUE_ATTEMPTS")
    receipt_paths = list((UNIT / "runs").glob("*/RECEIPT.json"))
    receipt_paths += list(DEBITS.glob("*.json"))
    receipt_paths += list(EVIDENCE.glob("PREWORKER_DEBIT_*.json"))
    for path in sorted(receipt_paths):
        add(json.loads(path.read_bytes()), str(path.relative_to(UNIT)))
    for receipt in selected.values():
        need(receipt.get("cpu_accounting_complete", True) is True,
             "INCOMPLETE_OWNED_CHILD_CPU_REQUIRES_OWNER_RECONCILIATION")
    for path in sorted((UNIT / "runs").glob("*/RESERVATION.json")):
        reservation = json.loads(path.read_bytes())
        need(isinstance(reservation, dict)
             and reservation.get("run_id") == path.parent.name,
             "INVALID_SAVED_RESERVATION:" + str(path.relative_to(UNIT)))
        identity = (reservation.get("attempt_id"), reservation["run_id"])
        if active_reservation is not None and identity == active_reservation:
            continue
        key = attempt_key(reservation)
        need(key in selected,
             "UNKNOWN_NO_ACK_RESERVATION_REQUIRES_OWNER_RECONCILIATION:"
             + str(path.relative_to(UNIT)))
    attempts = []
    for key, receipt in sorted(selected.items()):
        receipt["accounting_source_paths"] = sorted(paths[key])
        receipt["accounting_deduplication_key"] = key
        attempts.append(receipt)
    charged = math.fsum((baseline, *(r["charged_cpu_s"] for r in attempts)))
    measured = math.fsum((baseline, *(r["worker_cpu_s"]
                                     + r["coordinator_cpu_through_receipt_s"]
                                     for r in attempts)))
    return {
        "schema": "CR_PROPER_EXECUTION_LEDGER_V2", "unit": UNIT_ID,
        "attempts": attempts, "baseline_preparation_cpu_s": baseline,
        "charged_cpu_s": charged,
        "measured_worker_plus_coordinator_cpu_s": measured,
        "cap_s": HARD_CAP_S, "remaining_not_transferable": HARD_CAP_S - charged,
        "global_remaining": None, "historical_transferred": False,
        "parallel_project_budget_transferred": False,
        "deduplication": "one attempt_id; maximum cumulative debit across immutable receipts",
        "old_science_replays": 0,
    }


def remember_error(state, error, stage=None):
    state["errors"].append({"stage": stage or state["stage"],
                            "type": type(error).__name__, "message": str(error)})
    if isinstance(error, KeyboardInterrupt):
        state["exit_code"] = 130
    elif isinstance(error, SystemExit) and isinstance(error.code, int):
        state["exit_code"] = error.code
    else:
        state["exit_code"] = 125


def load_budget(state):
    raw = (UNIT / "EXECUTION_BUDGET.json").read_bytes()
    budget = json.loads(raw)
    need(budget.get("unit") == UNIT_ID, "EXACT_UNIT_BUDGET_REQUIRED")
    need(budget.get("local_science_cpu_cap_s") == HARD_CAP_S,
         "HARD_20_SECOND_UNIT_CAP_REQUIRED")
    need(budget.get("historical_allowance_transferred") is False
         and budget.get("parallel_PR108_budget_transferred") is False,
         "NONTRANSFERABLE_BUDGET_REQUIRED")
    need(budget.get("native_threads") == 1, "ONE_NATIVE_THREAD_REQUIRED")
    for key in ("coordinator_reserve_per_attempt_s", "coordinator_receipt_tail_reserve_s"):
        need(finite_nonnegative(budget[key], key) > 0, key + ":POSITIVE_REQUIRED")
    for key in ("worker_memory_bytes", "minimum_host_memory_reserve_bytes", "wall_per_attempt_s"):
        need(type(budget[key]) is int and budget[key] > 0, key + ":POSITIVE_INTEGER_REQUIRED")
    need(budget["worker_memory_bytes"] == 536870912
         and budget["minimum_host_memory_reserve_bytes"] == 1073741824,
         "FIXED_512_MIB_WORKER_AND_1_GIB_RESERVE_REQUIRED")
    need(budget["wall_per_attempt_s"] <= 60, "WALL_LIMIT_ABOVE_60_SECONDS_REFUSED")
    state["budget"] = budget
    state["budget_sha256"] = hashlib.sha256(raw).hexdigest()
    need(budget.get("status") == "FROZEN_C4_ADMITTED", "FROZEN_C4_ADMISSION_REQUIRED")
    host_record = budget.get("host_admission")
    need(isinstance(host_record, str) and bool(host_record)
         and not pathlib.Path(host_record).is_absolute()
         and ".." not in pathlib.Path(host_record).parts,
         "UNIT_LOCAL_C4_HOST_ADMISSION_REQUIRED")
    host_raw = (UNIT / host_record).read_bytes()
    expected_host_sha = budget.get("host_admission_sha256")
    state["host_admission_sha256"] = hashlib.sha256(host_raw).hexdigest()
    state["host_admission_expected_sha256"] = expected_host_sha
    state["host_admission_path"] = host_record
    need(isinstance(expected_host_sha, str)
         and re.fullmatch(r"[0-9a-f]{64}", expected_host_sha) is not None,
         "FROZEN_C4_HOST_ADMISSION_SHA256_REQUIRED")
    need(state["host_admission_sha256"] == expected_host_sha,
         "FROZEN_C4_HOST_ADMISSION_SHA256_MISMATCH")
    host = json.loads(host_raw)
    need(isinstance(host, dict) and host.get("memory_gate") == "PASS",
         "C4_HOST_MEMORY_GATE_PASS_REQUIRED")
    state["budget_admitted"] = True


def memory_capacity(budget, worker_memory_bytes=None):
    """Conservative runtime estimate; hard RLIMIT_AS remains independent."""
    selected = budget["worker_memory_bytes"] if worker_memory_bytes is None else worker_memory_bytes
    need(type(selected) is int and 0 < selected <= budget["worker_memory_bytes"],
         "MEMORY_LIMIT_MUST_BE_POSITIVE_AND_WITHIN_FROZEN_UPPER_CAP")
    meminfo = dict(line.split(":", 1) for line in pathlib.Path("/proc/meminfo").read_text().splitlines())
    host_available = int(meminfo["MemAvailable"].split()[0]) * 1024
    root = pathlib.Path("/sys/fs/cgroup")
    limit_raw = (root / "memory.max").read_text().strip()
    current = int((root / "memory.current").read_text().strip())
    stat = {key: int(value) for key, value in
            (line.split() for line in (root / "memory.stat").read_text().splitlines())}
    inactive = stat["inactive_file"]
    dirty, writeback = stat["file_dirty"], stat["file_writeback"]
    need(min(host_available, current, inactive, dirty, writeback) >= 0,
         "NONNEGATIVE_MEMORY_COUNTERS_REQUIRED")
    clean_inactive = max(0, inactive - dirty - writeback)
    limit = None if limit_raw == "max" else int(limit_raw)
    need(limit is None or limit > 0, "VALID_CGROUP_MEMORY_LIMIT_REQUIRED")
    raw_headroom = None if limit is None else limit - current
    cgroup_estimate = None if limit is None else max(0, raw_headroom + clean_inactive)
    available = host_available if limit is None else min(host_available, cgroup_estimate)
    required = selected + budget["minimum_host_memory_reserve_bytes"]
    return {
        "observed_utc": utc_now(), "host_MemAvailable_bytes": host_available,
        "cgroup_v2_path": str(root), "cgroup_memory_max_bytes": limit,
        "cgroup_memory_current_bytes": current,
        "cgroup_raw_headroom_bytes": raw_headroom,
        "inactive_file_bytes": inactive, "file_dirty_bytes": dirty,
        "file_writeback_bytes": writeback,
        "conservative_clean_inactive_allowance_bytes": clean_inactive,
        "cgroup_available_estimate_bytes": cgroup_estimate,
        "host_capped_available_estimate_bytes": available,
        "required_worker_plus_reserve_bytes": required,
        "admission_pass": available >= required,
        "estimate_formula": "min(host_MemAvailable, max(0, limit-current+max(0,inactive_file-file_dirty-file_writeback)))",
        "unlimited_cgroup_rule": "host_MemAvailable only when memory.max=max",
        "non_atomic_counter_snapshot": True, "admission_estimate_not_guarantee": True,
        "frozen_worker_memory_upper_cap_bytes": budget["worker_memory_bytes"],
        "selected_worker_memory_limit_bytes": selected,
        "worker_RLIMIT_AS_bytes": selected,
    }


def configure_subreaper():
    # A worker's orphaned descendants remain owned by this standalone runner.
    # This permits RUSAGE_CHILDREN to include reaped descendants after a kill.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # Linux PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), "cannot enable owned-child subreaper")


def cleanup_worker(state):
    proc = state.get("process")
    if proc is None:
        return
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    if proc.poll() is None:
        proc.wait(timeout=5)
    # No unrelated subprocess is launched by this coordinator. Reap only the
    # owned group; the worker must not escape its newly created session/group.
    deadline = time.monotonic() + 5
    while True:
        try:
            pid, _status, _usage = os.wait4(-proc.pid, os.WNOHANG)
        except ChildProcessError:
            break
        if pid == 0:
            need(time.monotonic() < deadline, "OWNED_CHILD_REAP_TIMEOUT")
            time.sleep(0.01)


def execute_attempt(state, argv):
    state["stage"] = "argparse"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--cpu-reserve", required=True, type=float)
    parser.add_argument("--memory-limit-bytes", type=int, default=None,
                        help="positive per-attempt RLIMIT_AS, at most the frozen worker upper cap")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    state["run_id"] = args.run_id
    state["requested_memory_limit_bytes"] = args.memory_limit_bytes
    need(RUN_ID.fullmatch(args.run_id) is not None and ".." not in args.run_id,
         "SAFE_UNIQUE_RUN_ID_REQUIRED")
    reserve = finite_nonnegative(args.cpu_reserve, "cpu_reserve")
    need(reserve > 0, "POSITIVE_WORKER_RESERVATION_REQUIRED")
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    need(bool(command) and all(isinstance(x, str) and "\0" not in x for x in command),
         "EXPLICIT_NONEMPTY_COMMAND_REQUIRED")
    state["command"] = command
    state["stage"] = "budget_read"
    load_budget(state)
    budget = state["budget"]
    state["stage"] = "memory_limit_selection"
    state["frozen_worker_memory_upper_cap_bytes"] = budget["worker_memory_bytes"]
    memory_limit = budget["worker_memory_bytes"] if args.memory_limit_bytes is None else args.memory_limit_bytes
    need(type(memory_limit) is int and 0 < memory_limit <= budget["worker_memory_bytes"],
         "MEMORY_LIMIT_MUST_BE_POSITIVE_AND_WITHIN_FROZEN_UPPER_CAP")
    state["selected_worker_memory_limit_bytes"] = memory_limit
    state["stage"] = "ledger_lock"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    state["lock"] = (EVIDENCE / "SCIENCE_BUDGET.lock").open("a+")
    fcntl.flock(state["lock"], fcntl.LOCK_EX | fcntl.LOCK_NB)
    state["lock_held"] = True
    state["stage"] = "admission"
    prior = reconcile(budget)
    coordinator_reserve = max(budget["coordinator_reserve_per_attempt_s"],
                              cpu(resource.RUSAGE_SELF)
                              + budget["coordinator_receipt_tail_reserve_s"])
    # RLIMIT_CPU has integer seconds. Admission reserves its full hard ceiling,
    # while a measured overrun of the caller's smaller reserve still fails.
    worker_limit = math.ceil(reserve)
    need(prior["charged_cpu_s"] + worker_limit + coordinator_reserve <= HARD_CAP_S,
         "UNIT_CPU_ADMISSION_DENIED")
    allowed = os.sched_getaffinity(0)
    need(bool(allowed), "NO_ADMITTED_CPU_AFFINITY")
    slot = min(allowed)
    memory = memory_capacity(budget, memory_limit)
    state["memory_admission"] = memory
    need(memory["admission_pass"], "EFFECTIVE_CGROUP_MEMORY_RESERVE_ADMISSION_DENIED")
    state["admission"] = {
        "attempt_id": state["attempt_id"], "unit": UNIT_ID,
        "run_id": args.run_id, "command": command,
        "reserved_worker_cpu_s": reserve, "worker_RLIMIT_CPU_s": worker_limit,
        "reserved_coordinator_cpu_s": coordinator_reserve,
        "prior_charged_cpu_s": prior["charged_cpu_s"], "cap_s": HARD_CAP_S,
        "worker_affinity": [slot], "native_threads": 1,
        "frozen_worker_memory_upper_cap_bytes": budget["worker_memory_bytes"],
        "selected_worker_memory_limit_bytes": memory_limit,
        "worker_RLIMIT_AS": memory_limit,
        "host_available_memory_bytes": memory["host_MemAvailable_bytes"],
        "host_memory_reserve_bytes": budget["minimum_host_memory_reserve_bytes"],
        "wall_timeout_s": budget["wall_per_attempt_s"], "created_utc": utc_now(),
    }
    state["stage"] = "output_directory"
    runs = UNIT / "runs"
    runs.mkdir(exist_ok=True)
    out = runs / args.run_id
    out.mkdir(exist_ok=False)
    state["out"] = out
    atomic_json(out / "RESERVATION.json", state["admission"], create_only=True)
    state["stage"] = "source_snapshot"
    snapshot = out / "EXECUTED_SOURCE"
    snapshot.mkdir()
    manifest = []
    for path in sorted((UNIT / "implementation").glob("*.py")) + sorted((UNIT / "review").glob("*.py")):
        content = path.read_bytes()
        name = path.parent.name + "_" + path.name
        with (snapshot / name).open("xb") as stream:
            stream.write(content)
        manifest.append({"path": str(path.relative_to(UNIT)), "snapshot": name,
                         "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    atomic_json(out / "EXECUTED_SOURCE_MANIFEST.json", manifest, create_only=True)
    # A simultaneous rejected invocation may have deposited a standalone debit
    # since the first reconciliation. Read it before committing worker CPU.
    state["stage"] = "final_admission"
    latest = reconcile(budget, active_reservation=(state["attempt_id"], args.run_id))
    need(latest["charged_cpu_s"] + worker_limit
         + max(coordinator_reserve, cpu(resource.RUSAGE_SELF)
               + budget["coordinator_receipt_tail_reserve_s"]) <= HARD_CAP_S,
         "FINAL_UNIT_CPU_ADMISSION_DENIED")
    final_memory = memory_capacity(budget, memory_limit)
    state["final_memory_admission"] = final_memory
    need(final_memory["admission_pass"], "FINAL_CGROUP_MEMORY_RESERVE_ADMISSION_DENIED")
    atomic_json(out / "FINAL_ADMISSION.json", {
        "attempt_id": state["attempt_id"], "run_id": args.run_id,
        "prior_charged_cpu_s": latest["charged_cpu_s"], "cap_s": HARD_CAP_S,
        "memory_admission": final_memory,
    }, create_only=True)
    configure_subreaper()
    env = dict(os.environ)
    env.update(OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", OMP_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1",
               PYTHONDONTWRITEBYTECODE="1", MPLCONFIGDIR=str(out / "mplcache"))

    def limits():
        os.sched_setaffinity(0, {slot})
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (worker_limit, worker_limit))

    state["stage"] = "worker_launch"
    state["worker_launch_attempted"] = True
    with (out / "stdout.txt").open("x") as stdout, (out / "stderr.txt").open("x") as stderr:
        proc = subprocess.Popen(command, cwd=UNIT, env=env, stdout=stdout, stderr=stderr,
                                preexec_fn=limits, start_new_session=True)
        state["process"] = proc
        state["worker_started"] = True
        state["owned_process_group"] = proc.pid
        state["stage"] = "worker_wait"
        try:
            state["worker_exit_code"] = proc.wait(timeout=budget["wall_per_attempt_s"])
        except subprocess.TimeoutExpired:
            state["timed_out"] = True
            os.killpg(proc.pid, signal.SIGKILL)
            state["worker_exit_code"] = proc.wait()
    raw_code = state["worker_exit_code"]
    state["exit_code"] = 124 if state["timed_out"] else (raw_code if raw_code >= 0 else 128 - raw_code)
    state["stage"] = "worker_finished"


def make_receipt(state, tail):
    worker = cpu(resource.RUSAGE_CHILDREN)
    coordinator = cpu(resource.RUSAGE_SELF)
    admission = state.get("admission", {})
    worker_exceeded = worker > admission.get("reserved_worker_cpu_s", math.inf)
    coordinator_exceeded = (coordinator + tail
                            > admission.get("reserved_coordinator_cpu_s", math.inf))
    failed = bool(state["errors"] or state["exit_code"] or worker_exceeded or coordinator_exceeded)
    if failed and state["exit_code"] == 0:
        state["exit_code"] = 1
    return {
        "schema": "CR_PROPER_RUN_RECEIPT_V2", "unit": UNIT_ID,
        **admission, "attempt_id": state["attempt_id"], "run_id": state.get("run_id"),
        "invocation_started_utc": state["started_utc"], "receipt_utc": utc_now(),
        "budget_sha256": state.get("budget_sha256"), "cap_s": HARD_CAP_S,
        "budget_C4_admitted": state.get("budget_admitted", False),
        "host_admission_path": state.get("host_admission_path"),
        "host_admission_sha256": state.get("host_admission_sha256"),
        "host_admission_expected_sha256": state.get("host_admission_expected_sha256"),
        "requested_memory_limit_bytes": state.get("requested_memory_limit_bytes"),
        "frozen_worker_memory_upper_cap_bytes": state.get("frozen_worker_memory_upper_cap_bytes"),
        "selected_worker_memory_limit_bytes": state.get("selected_worker_memory_limit_bytes"),
        "memory_admission": state.get("memory_admission"),
        "final_memory_admission": state.get("final_memory_admission"),
        "receipt_kind": "worker_attempt" if state["worker_started"] else "preworker_debit",
        "status": "failed" if failed else "completed",
        "exit_code": state["exit_code"], "worker_exit_code": state.get("worker_exit_code"),
        "worker_started": state["worker_started"],
        "terminal_debit": True,
        "cpu_accounting_complete": state.get("cleanup_complete", False),
        "worker_launch_attempted": state["worker_launch_attempted"],
        "owned_process_group": state.get("owned_process_group"),
        "timed_out": state["timed_out"], "last_stage": state["stage"],
        "errors": list(state["errors"]), "worker_cpu_s": worker,
        "coordinator_cpu_through_receipt_s": coordinator,
        "receipt_tail_reserve_s": tail,
        "charged_cpu_s": math.fsum((worker, coordinator, tail)),
        "worker_reservation_exceeded": worker_exceeded,
        "coordinator_reservation_exceeded": coordinator_exceeded,
        "wall_s": time.monotonic() - state["wall_started"],
        "max_child_rss_KiB": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "old_science_replays": 0, "historical_allowance_transferred": False,
        "failure_class": state["errors"][0]["stage"] if state["errors"] else
                         ("WORKER_FAILURE_OR_RESERVATION_EXCEEDED" if failed else None),
    }


def save_debit(state, receipt, sequence):
    name = state["attempt_id"] + ("" if sequence == 0 else "_amendment_" + str(sequence)) + ".json"
    try:
        path = DEBITS / name
        atomic_json(path, receipt, create_only=True)
    except Exception as error:
        # This path needs no ledger lock and does not depend on runs/<run_id>.
        remember_error(state, error, "standalone_debit_primary_write")
        receipt = make_receipt(state, receipt["receipt_tail_reserve_s"])
        path = EVIDENCE / ("PREWORKER_DEBIT_" + name)
        atomic_json(path, receipt, create_only=True)
    return receipt, path


def finalize_attempt(state):
    if state.get("budget_sha256") is None:
        # An argparse failure still uses the real preparation baseline whenever
        # it is readable; this does not authorize or launch a worker.
        try:
            load_budget(state)
        except BaseException as error:
            remember_error(state, error, "accounting_budget_read")
    budget = state["budget"]
    tail = budget["coordinator_receipt_tail_reserve_s"]
    last_receipt = None
    last_status = None
    for sequence in range(3):
        errors_before = len(state["errors"])
        before = cpu(resource.RUSAGE_SELF)
        receipt = make_receipt(state, tail)
        receipt, debit_path = save_debit(state, receipt, sequence)
        last_receipt = receipt
        try:
            if sequence == 0 and state.get("out") is not None:
                atomic_json(state["out"] / "RECEIPT.json", receipt, create_only=True)
            reconciled = reconcile(budget)
            remaining = reconciled["remaining_not_transferable"]
            last_status = {
                "schema": "CR_PROPER_FINAL_BUDGET_STATUS_V1", "unit": UNIT_ID,
                "attempt_id": state["attempt_id"], "created_utc": utc_now(),
                "authoritative_debit": str(debit_path.relative_to(UNIT)),
                "charged_cpu_s": reconciled["charged_cpu_s"], "cap_s": HARD_CAP_S,
                "remaining_not_transferable": remaining,
                "unique_attempts": len(reconciled["attempts"]),
                "ledger_lock_held": state["lock_held"],
                "ledger_synchronized": state["lock_held"],
                "budget_status": "EXCEEDED" if remaining < 0 else
                                 ("EXHAUSTED" if remaining == 0 else "WITHIN_CAP"),
                "admission_gate": "OPEN_SUBJECT_TO_FRESH_LOCKED_RESERVATION" if
                    remaining >= 1 + budget["coordinator_reserve_per_attempt_s"] else
                    "CLOSED_NO_COMPLETE_WORKER_RESERVATION",
                "next_admission_reconciles_all_standalone_debits": True,
                "global_remaining": None, "historical_allowance_transferred": False,
                "old_science_replays": 0,
            }
            if state.get("budget_admitted") is not True:
                last_status["admission_gate"] = "CLOSED_INVALID_BUDGET_CONFIGURATION"
            reconciled["latest_budget_status"] = last_status
            if state["lock_held"]:
                try:
                    atomic_json(LEDGER, reconciled, create_only=False)
                except BaseException as error:
                    remember_error(state, error, "ledger_write")
                    last_status["ledger_synchronized"] = False
                    last_status["admission_gate"] = "CLOSED_ACCOUNTING_WRITE_FAILURE"
            last_status["accounting_errors"] = list(state["errors"])
            suffix = "" if sequence == 0 else "_amendment_" + str(sequence)
            atomic_json(STATUSES / (state["attempt_id"] + suffix + ".json"),
                        last_status, create_only=True)
            if remaining < 0:
                state["exit_code"] = 125
        except BaseException as error:
            remember_error(state, error, "receipt_or_ledger_finalization")
            last_status = {"schema": "CR_PROPER_FINAL_BUDGET_STATUS_V1", "unit": UNIT_ID,
                           "attempt_id": state["attempt_id"], "created_utc": utc_now(),
                           "budget_status": "UNKNOWN_ACCOUNTING_RECONCILIATION_REQUIRED",
                           "admission_gate": "CLOSED_ACCOUNTING_FAILURE",
                           "authoritative_debit": str(debit_path.relative_to(UNIT)),
                           "this_attempt_charged_cpu_s": receipt["charged_cpu_s"],
                           "charged_cpu_s": None, "remaining_not_transferable": None,
                           "cap_s": HARD_CAP_S, "ledger_synchronized": False,
                           "accounting_errors": list(state["errors"]),
                           "global_remaining": None, "historical_allowance_transferred": False}
            try:
                atomic_json(STATUSES / (state["attempt_id"] + "_closed_" + str(sequence) + ".json"),
                            last_status, create_only=True)
            except BaseException as status_error:
                remember_error(state, status_error, "closed_budget_status_write")
        elapsed_accounting_cpu = cpu(resource.RUSAGE_SELF) - before
        if (len(state["errors"]) == errors_before
                and cpu(resource.RUSAGE_SELF) + cpu(resource.RUSAGE_CHILDREN)
                <= receipt["charged_cpu_s"]):
            break
        if sequence == 2:
            # Prior errors have cumulative debits; the closed status retains
            # the latest error. The enlarged tail covers final bookkeeping.
            break
        tail = max(tail, 2 * elapsed_accounting_cpu,
                   budget["coordinator_reserve_per_attempt_s"] if sequence == 1 else 0.01)
    print(json.dumps({"receipt": last_receipt, "final_budget_status": last_status}, allow_nan=False))
    return state["exit_code"]


def main(argv=None):
    # Defaults debit malformed invocations/configuration failures only.
    # They never authorize a worker: execute_attempt must load the exact budget.
    state = {
        "attempt_id": "attempt_" + uuid.uuid4().hex,
        "started_utc": utc_now(), "wall_started": time.monotonic(),
        "stage": "entry", "errors": [], "exit_code": 0,
        "worker_started": False, "worker_launch_attempted": False,
        "timed_out": False, "lock_held": False,
        "budget": {"spent_before_C4_admission": 0.0,
                   "coordinator_reserve_per_attempt_s": 0.3,
                   "coordinator_receipt_tail_reserve_s": 0.005},
    }
    try:
        execute_attempt(state, sys.argv[1:] if argv is None else argv)
    except BaseException as error:
        remember_error(state, error)
    finally:
        try:
            cleanup_worker(state)
            state["cleanup_complete"] = True
        except BaseException as error:
            remember_error(state, error, "owned_worker_cleanup")
        try:
            code = finalize_attempt(state)
        except BaseException as error:
            # Even an unexpected finalizer failure gets an independent debit.
            remember_error(state, error, "top_level_finalizer")
            receipt = make_receipt(state, state["budget"]["coordinator_reserve_per_attempt_s"])
            try:
                receipt, path = save_debit(state, receipt, "emergency_" + uuid.uuid4().hex)
                print(json.dumps({"receipt": receipt, "debit_path": str(path),
                                  "admission_gate": "CLOSED_ACCOUNTING_FAILURE"}), file=sys.stderr)
            except BaseException as terminal:
                print(json.dumps({"UNSAVED_CPU_DEBIT": receipt,
                                  "fatal_write_error": str(terminal),
                                  "admission_gate": "CLOSED_STORAGE_FAILURE"}), file=sys.stderr)
            code = 125
        finally:
            if state.get("lock") is not None:
                state["lock"].close()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
