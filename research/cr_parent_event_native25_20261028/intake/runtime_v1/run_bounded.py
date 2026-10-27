#!/usr/bin/env python3
"""Create-only worker attempts with a separate 40 s, failure-inclusive ledger.

Immutable attempt debits are authoritative. The mutable ledger is a reconciled
index, so a failed lock, argument parse, snapshot, or ledger write cannot make an
attempt disappear. A normal receipt and any later accounting debit share one
attempt_id; reconciliation charges the largest cumulative debit, not their sum.
No prior unit's unused allowance is imported.

Adapted prospectively from immutable PR110 runner SHA256
629d14ab8dd93fe0b23fb6394038f061f4a3fc0642922d110788d67922e05d9f.
This draft must be installed under the new unit implementation directory and
independently reviewed before a fresh pinned C4 admission can authorize it.
Old preworker/plot failures and old ledger bytes are never modified or adopted.
Aggregate polling is protective monitoring, not a kernel-enforced proof that
all worker descendants together can never overshoot a CPU reservation.
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
import shutil
import subprocess
import sys
import time
import uuid


UNIT = pathlib.Path(__file__).resolve().parents[1]
UNIT_ID = "CR_PHYS02_PARENT_EVENT_NATIVE25_V1"
EXPECTED_UNIT_DIRECTORY = "cr_parent_event_native25_20261028"
BUDGET_ID = "CR_PARENT_EVENT_20261028_NEW40"
HARD_CAP_S = 40.0
EVIDENCE = UNIT / "evidence"
LEDGER = EVIDENCE / "EXECUTION_LEDGER.json"
DEBITS = EVIDENCE / "ATTEMPT_DEBITS"
STATUSES = EVIDENCE / "BUDGET_STATUS"
LEASES = EVIDENCE / "ATTEMPT_LEASES"
NAMED_ROLE_WORKER_CAPS = {"prepare": 3., "controls": 3., "primary": 4.,
                          "independent": 6., "plot_saved": 6.}
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
    raise ValueError("EXPLICIT_NEW_UNIT_ATTEMPT_ID_REQUIRED")


def checked_cost(receipt):
    need(isinstance(receipt, dict), "RECEIPT_OBJECT_REQUIRED")
    need(receipt.get("unit") == UNIT_ID, "FOREIGN_OR_UNIDENTIFIED_UNIT_DEBIT_REFUSED")
    need(receipt.get("terminal_debit") is True, "TERMINAL_DEBIT_REQUIRED")
    worker = finite_nonnegative(receipt["worker_cpu_s"], "worker_cpu_s")
    coordinator = finite_nonnegative(receipt["coordinator_cpu_through_receipt_s"],
                                     "coordinator_cpu_through_receipt_s")
    tail = finite_nonnegative(receipt["receipt_tail_reserve_s"], "receipt_tail_reserve_s")
    charged = finite_nonnegative(receipt["charged_cpu_s"], "charged_cpu_s")
    need(abs(charged - math.fsum((worker, coordinator, tail))) <= 1e-12,
         "RECEIPT_MEASURED_AND_TAIL_COMPONENTS_MUST_EQUAL_CHARGE")
    need(abs(finite_nonnegative(receipt.get("measured_attempt_cpu_s"), "measured_attempt_cpu_s")
             - math.fsum((worker, coordinator))) <= 1e-12,
         "PURE_MEASURED_ATTEMPT_TOTAL_MISMATCH")
    return charged


def reconcile(budget, *, active_reservation=None, active_attempt_id=None):
    """Read all cost evidence; malformed or inconsistent evidence fails closed."""
    preparation_verification = {"budget": budget}
    verify_preparation_cost_manifest(preparation_verification)
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

    need(budget.get("unit") == UNIT_ID, "EXACT_UNIT_ACCOUNTING_BASELINE_REQUIRED")
    baseline = finite_nonnegative(budget.get("spent_before_C4_admission"),
                                  "spent_before_C4_admission")
    preparation_measured = finite_nonnegative(budget.get("preparation_measured_CPU_s"),
                                              "preparation_measured_CPU_s")
    preparation_tail = finite_nonnegative(budget.get("preparation_conservative_tail_CPU_s"),
                                          "preparation_conservative_tail_CPU_s")
    need(abs(baseline - math.fsum((preparation_measured, preparation_tail))) <= 1e-12,
         "PREPARATION_MEASURED_PLUS_TAIL_BASELINE_MISMATCH")
    if LEDGER.exists():
        old = json.loads(LEDGER.read_bytes())
        need(old.get("unit") == UNIT_ID and isinstance(old.get("attempts"), list),
             "INVALID_OR_FOREIGN_EXECUTION_LEDGER")
        need(old.get("baseline_preparation_cpu_s", baseline) == baseline,
             "PREPARATION_BASELINE_CHANGED")
        need(old.get("preparation_measured_cpu_s") == preparation_measured
             and old.get("preparation_conservative_tail_cpu_s") == preparation_tail,
             "PREPARATION_COMPONENTS_CHANGED")
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
        need(receipt.get("cpu_accounting_complete") is True,
             "INCOMPLETE_OWNED_CHILD_CPU_REQUIRES_OWNER_RECONCILIATION")
    for path in sorted(LEASES.glob("*.json")):
        lease = json.loads(path.read_bytes())
        need(type(lease) is dict and lease.get("unit") == UNIT_ID,
             "FOREIGN_OR_MALFORMED_INVOCATION_LEASE")
        key = attempt_key(lease)
        need(path.name == key + ".json", "LEASE_FILENAME_IDENTITY_MISMATCH")
        if key != active_attempt_id:
            need(key in selected,
                 "UNKNOWN_NO_ACK_INVOCATION_LEASE_REQUIRES_OWNER_RECONCILIATION:"
                 + str(path.relative_to(UNIT)))
    for path in sorted((UNIT / "runs").glob("*/RESERVATION.json")):
        reservation = json.loads(path.read_bytes())
        need(isinstance(reservation, dict) and reservation.get("unit") == UNIT_ID
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
    worker_measured = math.fsum(r["worker_cpu_s"] for r in attempts)
    coordinator_measured = math.fsum(r["coordinator_cpu_through_receipt_s"] for r in attempts)
    receipt_tails = math.fsum(r["receipt_tail_reserve_s"] for r in attempts)
    measured = math.fsum((preparation_measured, worker_measured, coordinator_measured))
    tails = math.fsum((preparation_tail, receipt_tails))
    need(abs(charged - math.fsum((measured, tails))) <= 1e-10,
         "PURE_MEASURED_PLUS_CONSERVATIVE_TAIL_TOTAL_MISMATCH")
    return {
        "schema": "CR_PARENT_EVENT_EXECUTION_LEDGER_V1", "unit": UNIT_ID,
        "attempts": attempts, "baseline_preparation_cpu_s": baseline,
        "charged_cpu_s": charged,
        "preparation_measured_cpu_s": preparation_measured,
        "preparation_conservative_tail_cpu_s": preparation_tail,
        "worker_measured_cpu_s": worker_measured,
        "coordinator_measured_cpu_s": coordinator_measured,
        "attempt_receipt_conservative_tail_cpu_s": receipt_tails,
        "measured_total_cpu_s": measured,
        "conservative_tail_total_cpu_s": tails,
        "all_preparation_attempts_pass": all(r["status"] == "completed" for r in
                                               preparation_verification["verified_preparation_cost_records"]),
        "all_worker_and_preworker_attempts_pass": all(r["status"] == "completed" for r in attempts),
        "all_runtime_attempts_pass": all(r["status"] == "completed" for r in
            preparation_verification["verified_preparation_cost_records"] + attempts),
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
    need(UNIT.name == EXPECTED_UNIT_DIRECTORY and UNIT.parent.name == "research",
         "INSTALL_DRAFT_IN_EXACT_NEW_UNIT_BEFORE_EXECUTION")
    raw = (UNIT / "EXECUTION_BUDGET.json").read_bytes()
    budget = json.loads(raw)
    need(budget.get("unit") == UNIT_ID, "EXACT_UNIT_BUDGET_REQUIRED")
    state["budget"] = budget
    state["budget_sha256"] = hashlib.sha256(raw).hexdigest()
    need(budget.get("budget_id") == BUDGET_ID, "FRESH_PARENT_EVENT_BUDGET_ID_REQUIRED")
    need(budget.get("local_science_cpu_cap_s") == HARD_CAP_S,
         "HARD_40_SECOND_UNIT_CAP_REQUIRED")
    need(budget.get("historical_allowance_transferred") is False
         and budget.get("parallel_project_budget_transferred") is False,
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
    need(.005 <= budget.get("aggregate_worker_monitor_poll_s", 0.) <= .05,
         "BOUNDED_AGGREGATE_POLL_INTERVAL_REQUIRED")
    need(.05 <= budget.get("aggregate_worker_stop_margin_s", 0.) <= .5,
         "POSITIVE_AGGREGATE_STOP_MARGIN_REQUIRED")
    need(budget["coordinator_reserve_per_attempt_s"] == 2.05
         and budget["coordinator_receipt_tail_reserve_s"] == .05,
         "EXACT_2P05_COORDINATOR_INCLUDING_0P05_TAIL_REQUIRED")
    need(budget.get("preparation_reserve_cpu_s") == 4.,
         "EXACT_4_SECOND_PREPARATION_RESERVE_REQUIRED")
    need(budget.get("memory_admission_policy") == "RAW_HEADROOM_ONLY_V1"
         and budget.get("memory_reclaim_credit_bytes") == 0,
         "FRESH_RAW_HEADROOM_POLICY_REQUIRED_NO_INHERITED_FILE_LRU_CREDIT")
    need(type(budget.get("run_allocations")) is list and budget["run_allocations"],
         "FROZEN_NAMED_RUN_ALLOCATIONS_REQUIRED")
    names = set()
    for allocation in budget["run_allocations"]:
        name = allocation.get("run_id")
        need(isinstance(name, str) and RUN_ID.fullmatch(name) and name not in names,
             "UNIQUE_FROZEN_RUN_ALLOCATION_REQUIRED")
        names.add(name)
        reserve = finite_nonnegative(allocation.get("worker_cpu_reservation_s"), "allocated_worker_cpu")
        role = allocation.get("role")
        need(role in NAMED_ROLE_WORKER_CAPS and reserve == NAMED_ROLE_WORKER_CAPS[role],
             "EXACT_FROZEN_ROLE_WORKER_CAP_REQUIRED")
        need(allocation.get("coordinator_cpu_reservation_s") == 2.05,
             "EXACT_NAMED_COORDINATOR_RESERVATION_REQUIRED")
        allocated_memory = allocation.get("selected_memory_limit_bytes")
        need(type(allocated_memory) is int and allocated_memory == 268435456,
             "EXACT_NAMED_256_MIB_WORKER_LIMIT_REQUIRED")
        if role == "plot_saved":
            need(reserve >= 6., "NEW_PLOT_RESERVATION_MUST_BE_AT_LEAST_6_CPU_SECONDS")
    need(budget.get("status") == "FROZEN_C4_ADMITTED", "FROZEN_C4_ADMISSION_REQUIRED")
    verify_contract_and_input_manifest(state)
    verify_preparation_cost_manifest(state)
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
    need(isinstance(host, dict) and host.get("unit") == UNIT_ID
         and host.get("status") == "completed"
         and host.get("memory_gate") == "PASS"
         and host.get("memory_admission_policy") == budget["memory_admission_policy"],
         "C4_HOST_MEMORY_GATE_PASS_REQUIRED")
    need(any(row["path"] == host_record and row["sha256"] == expected_host_sha
             for row in state["verified_preparation_cost_records"]),
         "ACTUAL_C4_HOST_RECEIPT_MUST_BE_IN_SAME_UNIT_PREPARATION_DEBITS")
    probe = host.get("owned_PID_observation_probe", {})
    need(probe.get("status") == "PASS"
         and type(probe.get("known_Popen_PID")) is int and probe["known_Popen_PID"] > 0
         and type(probe.get("start_ticks")) is int and probe["start_ticks"] >= 0
         and probe.get("live_PID_observed") is True
         and probe.get("child_cleanup_complete") is True,
         "ACTUAL_KNOWN_PID_AND_START_IDENTITY_OBSERVATION_PROBE_REQUIRED")
    finite_nonnegative(probe.get("CPU_s"), "actual_C4_owned_PID_probe_CPU_s")
    host_memory = host.get("memory_admission", {})
    need(host_memory.get("estimator_version") == "RAW_HEADROOM_ONLY_V1"
         and host_memory.get("admission_pass") is True
         and host_memory.get("selected_worker_memory_limit_bytes") == 268435456
         and host_memory.get("minimum_host_memory_reserve_bytes") == 1073741824
         and host_memory.get("credited_reclaim_bytes") == 0,
         "EXACT_NEW_UNIT_C4_RAW_MEMORY_EVIDENCE_REQUIRED")
    need(host_memory.get("cgroup_v2_path") == budget.get("cgroup_v2_path")
         and isinstance(budget.get("process_cgroup_membership_sha256"), str)
         and re.fullmatch(r"[0-9a-f]{64}", budget["process_cgroup_membership_sha256"])
         and host_memory.get("process_cgroup_membership_sha256")
             == budget["process_cgroup_membership_sha256"],
         "EXACT_C4_CGROUP_PATH_AND_MEMBERSHIP_PIN_REQUIRED")
    verify_code_manifest(state)
    state["budget_admitted"] = True


def pinned_unit_json(name, digest, reason):
    need(isinstance(name, str) and name and not pathlib.Path(name).is_absolute()
         and ".." not in pathlib.Path(name).parts, reason + ":UNIT_LOCAL_PATH_REQUIRED")
    need(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest),
         reason + ":SHA256_REQUIRED")
    path = UNIT / name
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(UNIT),
         reason + ":REGULAR_UNIT_LOCAL_FILE_REQUIRED")
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == digest, reason + ":BYTES_CHANGED")
    return json.loads(raw)


def verify_contract_and_input_manifest(state):
    """Read pinned inputs as bytes only; never import or replay old science."""
    budget = state["budget"]
    contract = pinned_unit_json(budget.get("contract"), budget.get("contract_sha256"),
                                "FROZEN_R1_CONTRACT")
    execution = contract.get("execution", {})
    need(contract.get("unit") == UNIT_ID and execution.get("budget_id") == BUDGET_ID
         and execution.get("fresh_CPU_cap_s") == HARD_CAP_S
         and execution.get("old_remainder_rollover") is False,
         "EXACT_R1_NEW_UNIT_EXECUTION_CONTRACT_REQUIRED")
    manifest = pinned_unit_json(budget.get("input_manifest"), budget.get("input_manifest_sha256"),
                                "FROZEN_INPUT_MANIFEST")
    files = manifest.get("files")
    need(type(files) is list and len(files) == budget.get("source_input_file_count")
         and len(files) > 0, "EXACT_INPUT_MANIFEST_FILE_COUNT_REQUIRED")
    repo = UNIT.parents[1]
    policy_raw = (repo / "AGENTS.md").read_bytes()
    need(hashlib.sha256(policy_raw).hexdigest() == budget.get("AGENTS_sha256"),
         "PROJECT_POLICY_CHANGED_SINCE_C4")
    seen = set()
    for row in files:
        need(type(row) is dict, "INPUT_MANIFEST_ROW_REQUIRED")
        relative = row.get("path")
        need(isinstance(relative, str) and relative
             and not pathlib.Path(relative).is_absolute()
             and ".." not in pathlib.Path(relative).parts, "REPO_LOCAL_INPUT_REQUIRED")
        path = repo / relative
        need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(repo),
             "REGULAR_PINNED_INPUT_REQUIRED")
        need(path.resolve() not in seen, "DUPLICATE_PINNED_INPUT_REFUSED")
        seen.add(path.resolve())
        need(type(row.get("bytes")) is int and row["bytes"] >= 0
             and isinstance(row.get("sha256"), str)
             and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]), "EXACT_INPUT_BYTE_PIN_REQUIRED")
        raw = path.read_bytes()
        need(len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"],
             "PINNED_INPUT_CHANGED:" + relative)
    state["contract_sha256"] = budget["contract_sha256"]
    state["input_manifest_sha256"] = budget["input_manifest_sha256"]
    state["verified_source_input_file_count"] = len(files)


def verify_preparation_cost_manifest(state):
    """Bind a same-unit preparation baseline to exact actual receipt bytes."""
    budget = state["budget"]
    name = budget.get("preparation_cost_manifest")
    digest = budget.get("preparation_cost_manifest_sha256")
    need(isinstance(name, str) and name and not pathlib.Path(name).is_absolute()
         and ".." not in pathlib.Path(name).parts, "UNIT_LOCAL_PREPARATION_MANIFEST_REQUIRED")
    need(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest),
         "EXACT_PREPARATION_MANIFEST_SHA256_REQUIRED")
    manifest_path = UNIT / name
    need(manifest_path.is_file() and not manifest_path.is_symlink()
         and manifest_path.resolve().is_relative_to(UNIT), "REGULAR_UNIT_LOCAL_PREPARATION_MANIFEST_REQUIRED")
    raw = manifest_path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == digest, "PREPARATION_MANIFEST_BYTES_CHANGED")
    manifest = json.loads(raw)
    need(type(manifest) is dict and manifest.get("unit") == UNIT_ID
         and type(manifest.get("records")) is list and manifest["records"],
         "EXACT_NEW_UNIT_PREPARATION_MANIFEST_REQUIRED")
    seen, costs, measurements, tails, verified = set(), [], [], [], []
    for row in manifest["records"]:
        need(type(row) is dict, "PREPARATION_RECORD_OBJECT_REQUIRED")
        relative = row.get("path")
        need(isinstance(relative, str) and relative and not pathlib.Path(relative).is_absolute()
             and ".." not in pathlib.Path(relative).parts, "UNIT_LOCAL_PREPARATION_RECEIPT_REQUIRED")
        path = UNIT / relative
        need(path.is_file() and not path.is_symlink()
             and path.resolve().is_relative_to(UNIT), "REGULAR_UNIT_LOCAL_PREPARATION_RECEIPT_REQUIRED")
        resolved = path.resolve()
        need(resolved not in seen and resolved != manifest_path.resolve(),
             "UNIQUE_PREPARATION_RECEIPT_PATHS_REQUIRED")
        seen.add(resolved)
        length, expected = row.get("bytes"), row.get("sha256")
        need(type(length) is int and length > 0 and isinstance(expected, str)
             and re.fullmatch(r"[0-9a-f]{64}", expected), "EXACT_PREPARATION_RECEIPT_BYTE_PIN_REQUIRED")
        receipt_raw = path.read_bytes()
        need(len(receipt_raw) == length and hashlib.sha256(receipt_raw).hexdigest() == expected,
             "PREPARATION_RECEIPT_BYTES_CHANGED:" + relative)
        receipt = json.loads(receipt_raw)
        need(type(receipt) is dict and receipt.get("unit") == UNIT_ID
             and receipt.get("terminal_debit") is True
             and receipt.get("cpu_accounting_complete") is True
             and receipt.get("status") in ("completed", "failed"),
             "FOREIGN_UNIT_PREPARATION_COST_REFUSED")
        for flag in ("old_budget_transferred", "old_budgets_transferred",
                     "historical_allowance_transferred", "parallel_project_budget_transferred"):
            need(receipt.get(flag, False) is False, "OLD_OR_PARALLEL_PREPARATION_COST_REFUSED")
        cost = finite_nonnegative(receipt.get("charged_preparation_CPU_s"),
                                  "actual.charged_preparation_CPU_s")
        declared = finite_nonnegative(row.get("charged_preparation_CPU_s"),
                                      "manifest.record.charged_preparation_CPU_s")
        need(abs(cost - declared) <= 1e-12, "PREPARATION_RECORD_COST_MISMATCH")
        measured = finite_nonnegative(receipt.get("measured_preparation_CPU_s"),
                                      "actual.measured_preparation_CPU_s")
        tail = finite_nonnegative(receipt.get("conservative_tail_CPU_s"),
                                  "actual.conservative_tail_CPU_s")
        need(abs(cost - math.fsum((measured, tail))) <= 1e-12,
             "PREPARATION_CHARGE_MUST_EQUAL_MEASURED_PLUS_TAIL")
        need(abs(finite_nonnegative(row.get("measured_preparation_CPU_s"), "row.measured")
                 - measured) <= 1e-12
             and abs(finite_nonnegative(row.get("conservative_tail_CPU_s"), "row.tail")
                     - tail) <= 1e-12, "PREPARATION_MEASURED_TAIL_PIN_MISMATCH")
        costs.append(cost)
        measurements.append(measured)
        tails.append(tail)
        verified.append({"path": relative, "bytes": length, "sha256": expected,
                         "status": receipt["status"],
                         "measured_preparation_CPU_s": measured,
                         "conservative_tail_CPU_s": tail, "charged_preparation_CPU_s": cost})
    charged = math.fsum(costs)
    measured = math.fsum(measurements)
    tail = math.fsum(tails)
    declared_total = finite_nonnegative(manifest.get("charged_total_CPU_s"), "manifest.charged_total_CPU_s")
    baseline = finite_nonnegative(budget.get("spent_before_C4_admission"), "budget.spent_before_C4_admission")
    need(abs(charged - declared_total) <= 1e-12 and abs(charged - baseline) <= 1e-12,
         "EXACT_SAME_UNIT_PREPARATION_BASELINE_MISMATCH")
    need(abs(measured - finite_nonnegative(manifest.get("measured_total_CPU_s"),
                                          "manifest.measured_total_CPU_s")) <= 1e-12
         and abs(tail - finite_nonnegative(manifest.get("conservative_tail_total_CPU_s"),
                                           "manifest.conservative_tail_total_CPU_s")) <= 1e-12,
         "PREPARATION_MANIFEST_PURE_COMPONENT_TOTAL_MISMATCH")
    need(abs(measured - finite_nonnegative(budget.get("preparation_measured_CPU_s"),
                                          "budget.preparation_measured_CPU_s")) <= 1e-12
         and abs(tail - finite_nonnegative(budget.get("preparation_conservative_tail_CPU_s"),
                                           "budget.preparation_conservative_tail_CPU_s")) <= 1e-12,
         "FROZEN_PREPARATION_COMPONENT_TOTAL_MISMATCH")
    need(charged <= 4. and budget.get("preparation_reserve_cpu_s") == 4.,
         "FRESH_PREPARATION_RESERVE_EXCEEDED")
    state["preparation_cost_manifest_path"] = name
    state["preparation_cost_manifest_sha256"] = digest
    state["verified_preparation_charged_cpu_s"] = charged
    state["verified_preparation_measured_cpu_s"] = measured
    state["verified_preparation_conservative_tail_cpu_s"] = tail
    state["verified_preparation_cost_records"] = verified


def verify_code_manifest(state):
    budget = state["budget"]
    name = budget.get("code_manifest")
    digest = budget.get("code_manifest_sha256")
    need(isinstance(name, str) and name and not pathlib.Path(name).is_absolute()
         and ".." not in pathlib.Path(name).parts, "UNIT_LOCAL_FROZEN_CODE_MANIFEST_REQUIRED")
    need(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest),
         "FROZEN_CODE_MANIFEST_SHA256_REQUIRED")
    raw = (UNIT / name).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == digest, "FROZEN_CODE_MANIFEST_BYTES_CHANGED")
    manifest = json.loads(raw)
    need(manifest.get("unit") == UNIT_ID and type(manifest.get("files")) is list,
         "EXACT_UNIT_CODE_MANIFEST_REQUIRED")
    observed = set()
    for row in manifest["files"]:
        relative = pathlib.Path(row["path"])
        need(not relative.is_absolute() and ".." not in relative.parts
             and len(relative.parts) == 2 and relative.parts[0] in ("implementation", "review")
             and relative.suffix == ".py", "SCOPED_PYTHON_MANIFEST_PATH_REQUIRED")
        need(row["path"] not in observed, "DUPLICATE_CODE_MANIFEST_PATH")
        observed.add(row["path"])
        path = UNIT / relative
        need(path.is_file() and not path.is_symlink(), "REGULAR_FROZEN_CODE_REQUIRED")
        content = path.read_bytes()
        need(len(content) == row["bytes"] and hashlib.sha256(content).hexdigest() == row["sha256"],
             "FROZEN_CODE_CHANGED:" + row["path"])
    actual = {str(path.relative_to(UNIT)) for directory in ("implementation", "review")
              for path in (UNIT / directory).glob("*.py")}
    need(observed == actual, "FROZEN_CODE_MANIFEST_COVERAGE_MISMATCH")
    state["code_manifest_sha256"] = digest
    state["code_manifest"] = manifest


def memory_estimate_raw(*, host_available_bytes, cgroup_limit_bytes, cgroup_current_bytes,
                        counters, selected_worker_memory_bytes,
                        frozen_worker_memory_upper_cap_bytes,
                        minimum_host_memory_reserve_bytes):
    """Fresh unit policy: current raw headroom only, with zero reclaim credit.

    These non-atomic host/cgroup snapshots are admission observations rather
    than a kernel guarantee or an outward lower-bound certificate.
    """
    required_keys = {"file", "shmem", "active_file", "inactive_file", "file_mapped",
                     "file_dirty", "file_writeback", "unevictable"}
    need(type(counters) is dict and required_keys <= set(counters)
         and all(isinstance(k, str) and type(v) is int and v >= 0
                 for k, v in counters.items()), "EXPLICIT_NONNEGATIVE_MEMORY_COUNTERS_REQUIRED")
    need(type(host_available_bytes) is int and host_available_bytes >= 0
         and type(cgroup_current_bytes) is int and cgroup_current_bytes >= 0,
         "NONNEGATIVE_INTEGER_MEMORY_TOTALS_REQUIRED")
    need(cgroup_limit_bytes is None or type(cgroup_limit_bytes) is int
         and cgroup_limit_bytes > 0, "VALID_CGROUP_MEMORY_LIMIT_REQUIRED")
    selected = selected_worker_memory_bytes
    upper = frozen_worker_memory_upper_cap_bytes
    reserve = minimum_host_memory_reserve_bytes
    need(type(upper) is int and upper == 536870912
         and type(selected) is int and selected == 268435456,
         "FROZEN_256_MIB_SELECTED_AND_512_MIB_UPPER_REQUIRED")
    need(type(reserve) is int and reserve == 1073741824, "FROZEN_1_GIB_HOST_RESERVE_REQUIRED")
    raw_headroom = None if cgroup_limit_bytes is None else cgroup_limit_bytes - cgroup_current_bytes
    available = host_available_bytes if raw_headroom is None else min(host_available_bytes, max(0, raw_headroom))
    required = selected + reserve
    return {
        "estimator_version": "RAW_HEADROOM_ONLY_V1",
        "estimate_status": "FRESH_NONATOMIC_RAW_HEADROOM_ADMISSION_OBSERVATION",
        "host_MemAvailable_bytes": host_available_bytes,
        "cgroup_memory_max_bytes": cgroup_limit_bytes,
        "cgroup_memory_current_bytes": cgroup_current_bytes,
        "cgroup_raw_headroom_bytes": raw_headroom,
        "memory_stat_counters": dict(counters),
        "credited_reclaim_bytes": 0,
        "prior_file_LRU_policy_imported": False,
        "host_capped_available_estimate_bytes": available,
        "required_worker_plus_reserve_bytes": required,
        "admission_pass": available >= required,
        "estimate_formula": "min(host_MemAvailable,max(0,limit-current)); unlimited cgroup uses host only",
        "non_atomic_counter_snapshot": True, "admission_estimate_not_guarantee": True,
        "lower_bound_certificate": False, "OS_settings_changed": False,
        "frozen_worker_memory_upper_cap_bytes": upper,
        "selected_worker_memory_limit_bytes": selected, "worker_RLIMIT_AS_bytes": selected,
        "minimum_host_memory_reserve_bytes": reserve,
    }


def memory_capacity(budget, worker_memory_bytes=None):
    """Read fresh counters under the explicit new unit raw-headroom policy."""
    need(budget.get("memory_admission_policy") == "RAW_HEADROOM_ONLY_V1"
         and budget.get("memory_reclaim_credit_bytes") == 0,
         "NO_INHERITED_OR_UNREVIEWED_RECLAIM_CREDIT")
    selected = budget["worker_memory_bytes"] if worker_memory_bytes is None else worker_memory_bytes
    meminfo = dict(line.split(":", 1) for line in pathlib.Path("/proc/meminfo").read_text().splitlines())
    host_available = int(meminfo["MemAvailable"].split()[0]) * 1024
    root = pathlib.Path(budget["cgroup_v2_path"])
    need(root.is_absolute() and root.resolve().is_relative_to(pathlib.Path("/sys/fs/cgroup")),
         "ADMITTED_CGROUP_V2_PATH_REQUIRED")
    membership = pathlib.Path("/proc/self/cgroup").read_bytes()
    need(hashlib.sha256(membership).hexdigest() == budget["process_cgroup_membership_sha256"],
         "PROCESS_CGROUP_MEMBERSHIP_CHANGED_SINCE_C4")
    limit_raw = (root / "memory.max").read_text().strip()
    current = int((root / "memory.current").read_text().strip())
    counters = {key: int(value) for key, value in
                (line.split() for line in (root / "memory.stat").read_text().splitlines())}
    estimate = memory_estimate_raw(host_available_bytes=host_available,
        cgroup_limit_bytes=None if limit_raw == "max" else int(limit_raw),
        cgroup_current_bytes=current, counters=counters,
        selected_worker_memory_bytes=selected,
        frozen_worker_memory_upper_cap_bytes=budget["worker_memory_bytes"],
        minimum_host_memory_reserve_bytes=budget["minimum_host_memory_reserve_bytes"])
    estimate.update(observed_utc=utc_now(), cgroup_v2_path=str(root),
                    process_cgroup_membership=membership.decode("utf-8"),
                    process_cgroup_membership_sha256=hashlib.sha256(membership).hexdigest())
    return estimate


def configure_subreaper():
    # A worker's orphaned descendants remain owned by this standalone runner.
    # This permits RUSAGE_CHILDREN to include reaped descendants after a kill.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # Linux PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), "cannot enable owned-child subreaper")


def process_stat(pid):
    try:
        raw = pathlib.Path(f"/proc/{pid}/stat").read_text()
        fields = raw[raw.rfind(")") + 2:].split()
        return {"pid": pid, "ppid": int(fields[1]), "pgrp": int(fields[2]),
                "session": int(fields[3]), "own_ticks": int(fields[11]) + int(fields[12]),
                "reaped_descendant_ticks": int(fields[13]) + int(fields[14]),
                "start_ticks": int(fields[19])}
    except FileNotFoundError:
        return None


def child_pids(pid):
    try:
        raw = pathlib.Path(f"/proc/{pid}/task/{pid}/children").read_text()
        return [int(value) for value in raw.split()]
    except FileNotFoundError:
        return []


def capture_owned_worker_identity(state):
    """Bind the Popen child explicitly; a live unobservable child is a failure."""
    proc = state["process"]
    state["known_owned_worker_pid"] = proc.pid
    row = process_stat(proc.pid)
    if row is None:
        need(proc.poll() is not None, "LIVE_OWNED_WORKER_UNOBSERVABLE_AT_LAUNCH")
        state["worker_exited_before_identity_observation"] = True
        return
    need(row["ppid"] == os.getpid() and row["pgrp"] == proc.pid
         and row["session"] == proc.pid, "POPEN_CHILD_IDENTITY_OR_GROUP_MISMATCH")
    state["known_owned_worker_start_ticks"] = row["start_ticks"]
    state["known_owned_worker_pid_observed"] = True
    state.setdefault("observed_owned_pid_start_ticks", {})[proc.pid] = row["start_ticks"]


def owned_cpu_estimate(state):
    """Observe this standalone coordinator's descendants; no unrelated scans.

    Reparented children are visible because this process is a subreaper. Linux
    /proc reads are not atomic; raced reaping may conservatively double count
    one poll, and final RUSAGE_CHILDREN remains the measured debit authority.
    """
    proc = state["process"]
    # The inherited children-only census produced zero observed workers.
    # Seed the actual Popen PID as well as newly discovered descendants.
    queue = ([proc.pid] if proc.returncode is None else []) + child_pids(os.getpid())
    seen, rows = set(), []
    while queue:
        pid = queue.pop()
        if pid in seen:
            continue
        seen.add(pid)
        row = process_stat(pid)
        if row is None:
            if pid == proc.pid:
                need(proc.poll() is not None, "LIVE_OWNED_WORKER_UNOBSERVABLE_DURING_MONITOR")
            continue
        expected_start = state.get("observed_owned_pid_start_ticks", {}).get(pid)
        need(expected_start is None or row["start_ticks"] == expected_start,
             "OWNED_PID_START_IDENTITY_CHANGED")
        if pid == proc.pid:
            need(row["ppid"] == os.getpid()
                 and row["start_ticks"] == state.get("known_owned_worker_start_ticks"),
                 "KNOWN_POPEN_IDENTITY_MISMATCH")
            state["known_owned_worker_pid_observed"] = True
        queue.extend(child_pids(pid))
        state.setdefault("observed_owned_pid_start_ticks", {})[pid] = row["start_ticks"]
        need(row["pgrp"] == state["owned_process_group"]
             and row["session"] == state["owned_process_group"],
             "OWNED_WORKER_DESCENDANT_ESCAPED_PROCESS_GROUP")
        rows.append(row)
    ticks = math.fsum(row["own_ticks"] + row["reaped_descendant_ticks"] for row in rows)
    estimate = cpu(resource.RUSAGE_CHILDREN) + ticks / os.sysconf("SC_CLK_TCK")
    state["aggregate_worker_cpu_peak_estimate_s"] = max(
        estimate, state.get("aggregate_worker_cpu_peak_estimate_s", 0.))
    state["maximum_observed_owned_processes"] = max(
        len(rows), state.get("maximum_observed_owned_processes", 0))
    state["aggregate_monitor_polls"] = state.get("aggregate_monitor_polls", 0) + 1
    return estimate


def kill_owned_process_group(state):
    """The unreaped Popen PID cannot be recycled; never kill a stale PGID."""
    proc = state.get("process")
    if proc is not None and proc.returncode is None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def wait_owned_worker(state, budget):
    proc = state["process"]
    deadline = time.monotonic() + budget["wall_per_attempt_s"]
    margin = budget["aggregate_worker_stop_margin_s"]
    admission = state["admission"]
    while True:
        estimate = owned_cpu_estimate(state)
        coordinator = cpu(resource.RUSAGE_SELF)
        stop_reason = None
        if estimate >= admission["reserved_worker_cpu_s"] - margin:
            stop_reason = "AGGREGATE_WORKER_CPU_RESERVATION_APPROACHING"
        elif coordinator + budget["coordinator_receipt_tail_reserve_s"] >= admission["reserved_coordinator_cpu_s"]:
            stop_reason = "COORDINATOR_CPU_RESERVATION_APPROACHING"
        elif state.get("monitor_prior_charged_cpu_s", admission["prior_charged_cpu_s"]) + estimate + coordinator \
                + budget["coordinator_receipt_tail_reserve_s"] >= HARD_CAP_S - margin:
            stop_reason = "UNIT_CPU_CAP_APPROACHING"
        elif time.monotonic() >= deadline:
            state["timed_out"] = True
            stop_reason = "WORKER_WALL_LIMIT"
        if stop_reason is not None:
            state["aggregate_monitor_stop_reason"] = stop_reason
            remember_error(state, RuntimeError(stop_reason), "aggregate_worker_monitor")
            kill_owned_process_group(state)
            return proc.wait(timeout=5)
        code = proc.poll()
        if code is not None:
            return code
        time.sleep(budget["aggregate_worker_monitor_poll_s"])


def terminate_current_owned_descendants(state):
    """Rediscover only this coordinator's actual descendants during cleanup."""
    proc = state.get("process")
    queue = ([proc.pid] if proc is not None and proc.returncode is None else [])
    queue += child_pids(os.getpid())
    seen, identities = set(), []
    while queue:
        pid = queue.pop()
        if pid in seen:
            continue
        seen.add(pid)
        queue.extend(child_pids(pid))
        row = process_stat(pid)
        if row is not None:
            expected_start = state.get("observed_owned_pid_start_ticks", {}).get(pid)
            need(expected_start is None or row["start_ticks"] == expected_start,
                 "OWNED_PID_REUSED_DURING_CLEANUP")
            identities.append((pid, row["start_ticks"]))
            state.setdefault("observed_owned_pid_start_ticks", {})[pid] = row["start_ticks"]
    for pid, start_ticks in identities:
        current = process_stat(pid)
        if current is not None and current["start_ticks"] == start_ticks:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def cleanup_worker(state):
    proc = state.get("process")
    if proc is None:
        return
    kill_owned_process_group(state)
    terminate_current_owned_descendants(state)
    # A forbidden escaped group is still owned. Kill only the exact observed
    # descendant PID with the same kernel start-time identity, never by name.
    for pid, start_ticks in state.get("observed_owned_pid_start_ticks", {}).items():
        current = process_stat(pid)
        if current is not None and current["start_ticks"] == start_ticks:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    if proc.poll() is None:
        proc.wait(timeout=5)
    # No unrelated subprocess is launched by this standalone coordinator.
    # Reap all its owned descendants, including a forbidden escaped group.
    deadline = time.monotonic() + 5
    while True:
        # A fork, setsid or reparenting between monitor and root termination
        # does not remove ownership. Discover newly adopted children again.
        terminate_current_owned_descendants(state)
        try:
            pid, _status, _usage = os.wait4(-1, os.WNOHANG)
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
    allocation = [row for row in budget["run_allocations"] if row["run_id"] == args.run_id]
    need(len(allocation) == 1 and reserve == allocation[0]["worker_cpu_reservation_s"],
         "EXACT_FROZEN_NAMED_WORKER_RESERVATION_REQUIRED")
    interpreter = shutil.which(command[0])
    need(interpreter is not None and os.path.samefile(interpreter, sys.executable),
         "CURRENT_PINNED_PYTHON_INTERPRETER_REQUIRED")
    need(len(command) >= 2, "EXPLICIT_FROZEN_PYTHON_SCRIPT_REQUIRED")
    script = (UNIT / command[1]).resolve()
    try:
        script_name = str(script.relative_to(UNIT))
    except ValueError:
        raise ValueError("WORKER_SCRIPT_OUTSIDE_FROZEN_UNIT")
    need(script_name in {row["path"] for row in state["code_manifest"]["files"]}
         and script.name != "run_bounded.py", "FROZEN_SCIENTIFIC_WORKER_SCRIPT_REQUIRED")
    need(command.count("--out") == 1 and command.index("--out") + 1 < len(command)
         and not any(value.startswith("--out=") for value in command),
         "ONE_EXPLICIT_OWNED_WORKER_OUTPUT_REQUIRED")
    selected_out = (UNIT / command[command.index("--out") + 1]).resolve()
    need(selected_out == (UNIT / "runs" / args.run_id).resolve(),
         "WORKER_OUTPUT_MUST_MATCH_RUN_RESERVATION")
    state["stage"] = "memory_limit_selection"
    state["frozen_worker_memory_upper_cap_bytes"] = budget["worker_memory_bytes"]
    allocated_memory = allocation[0]["selected_memory_limit_bytes"]
    memory_limit = allocated_memory if args.memory_limit_bytes is None else args.memory_limit_bytes
    need(type(memory_limit) is int and 0 < memory_limit <= budget["worker_memory_bytes"],
         "MEMORY_LIMIT_MUST_BE_POSITIVE_AND_WITHIN_FROZEN_UPPER_CAP")
    need(memory_limit == allocated_memory, "EXACT_FROZEN_NAMED_MEMORY_LIMIT_REQUIRED")
    state["selected_worker_memory_limit_bytes"] = memory_limit
    state["stage"] = "ledger_lock"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    state["lock"] = (EVIDENCE / "SCIENCE_BUDGET.lock").open("a+")
    fcntl.flock(state["lock"], fcntl.LOCK_EX | fcntl.LOCK_NB)
    state["lock_held"] = True
    state["stage"] = "admission"
    prior = reconcile(budget, active_attempt_id=state["attempt_id"])
    need(all(row.get("run_id") != args.run_id for row in prior["attempts"]),
         "RUN_ID_ALREADY_CHARGED_USE_UNIQUE_REVIEWED_ALLOCATION")
    coordinator_reserve = allocation[0]["coordinator_cpu_reservation_s"]
    need(cpu(resource.RUSAGE_SELF) + budget["coordinator_receipt_tail_reserve_s"]
         <= coordinator_reserve, "COORDINATOR_RESERVATION_SPENT_BEFORE_LAUNCH")
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
    for row in state["code_manifest"]["files"]:
        path = UNIT / row["path"]
        content = path.read_bytes()
        need(len(content) == row["bytes"] and hashlib.sha256(content).hexdigest() == row["sha256"],
             "FROZEN_CODE_CHANGED_DURING_SNAPSHOT:" + row["path"])
        name = path.parent.name + "_" + path.name
        with (snapshot / name).open("xb") as stream:
            stream.write(content)
        manifest.append({"path": str(path.relative_to(UNIT)), "snapshot": name,
                         "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    atomic_json(out / "EXECUTED_SOURCE_MANIFEST.json", manifest, create_only=True)
    # A simultaneous rejected invocation may have deposited a standalone debit
    # since the first reconciliation. Read it before committing worker CPU.
    state["stage"] = "final_admission"
    verify_code_manifest(state)
    verify_contract_and_input_manifest(state)
    verify_preparation_cost_manifest(state)
    latest = reconcile(budget, active_reservation=(state["attempt_id"], args.run_id),
                       active_attempt_id=state["attempt_id"])
    state["monitor_prior_charged_cpu_s"] = latest["charged_cpu_s"]
    need(cpu(resource.RUSAGE_SELF) + budget["coordinator_receipt_tail_reserve_s"]
         <= coordinator_reserve, "FINAL_COORDINATOR_RESERVATION_EXHAUSTED")
    need(latest["charged_cpu_s"] + worker_limit + coordinator_reserve <= HARD_CAP_S,
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
               PYTHONDONTWRITEBYTECODE="1", MPLCONFIGDIR=str(out / "mplcache"),
               CR_BOUNDED_UNIT=UNIT_ID, CR_BOUNDED_OUTDIR=str(out.resolve()),
               CR_BOUNDED_ATTEMPT_ID=state["attempt_id"])

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
        state["stage"] = "worker_pid_identity"
        capture_owned_worker_identity(state)
        state["stage"] = "worker_wait"
        state["worker_exit_code"] = wait_owned_worker(state, budget)
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
        "schema": "CR_PARENT_EVENT_RUN_RECEIPT_V1", "unit": UNIT_ID,
        **admission, "attempt_id": state["attempt_id"], "run_id": state.get("run_id"),
        "invocation_started_utc": state["started_utc"], "receipt_utc": utc_now(),
        "budget_sha256": state.get("budget_sha256"), "cap_s": HARD_CAP_S,
        "budget_C4_admitted": state.get("budget_admitted", False),
        "host_admission_path": state.get("host_admission_path"),
        "host_admission_sha256": state.get("host_admission_sha256"),
        "host_admission_expected_sha256": state.get("host_admission_expected_sha256"),
        "code_manifest_sha256": state.get("code_manifest_sha256"),
        "contract_sha256": state.get("contract_sha256"),
        "input_manifest_sha256": state.get("input_manifest_sha256"),
        "verified_source_input_file_count": state.get("verified_source_input_file_count"),
        "preparation_cost_manifest_path": state.get("preparation_cost_manifest_path"),
        "preparation_cost_manifest_sha256": state.get("preparation_cost_manifest_sha256"),
        "verified_preparation_charged_cpu_s": state.get("verified_preparation_charged_cpu_s"),
        "verified_preparation_measured_cpu_s": state.get("verified_preparation_measured_cpu_s"),
        "verified_preparation_conservative_tail_cpu_s": state.get("verified_preparation_conservative_tail_cpu_s"),
        "verified_preparation_cost_records": state.get("verified_preparation_cost_records"),
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
        "invocation_lease_path": state.get("invocation_lease_path"),
        "known_owned_worker_pid": state.get("known_owned_worker_pid"),
        "known_owned_worker_start_ticks": state.get("known_owned_worker_start_ticks"),
        "known_owned_worker_pid_observed": state.get("known_owned_worker_pid_observed", False),
        "worker_exited_before_identity_observation": state.get("worker_exited_before_identity_observation", False),
        "timed_out": state["timed_out"], "last_stage": state["stage"],
        "aggregate_worker_cpu_peak_estimate_s": state.get("aggregate_worker_cpu_peak_estimate_s"),
        "aggregate_monitor_polls": state.get("aggregate_monitor_polls", 0),
        "aggregate_monitor_stop_reason": state.get("aggregate_monitor_stop_reason"),
        "maximum_observed_owned_processes": state.get("maximum_observed_owned_processes", 0),
        "aggregate_polling_is_kernel_hard_cap_proof": False,
        "aggregate_monitor_is_non_atomic_estimate": True,
        "errors": list(state["errors"]), "worker_cpu_s": worker,
        "coordinator_cpu_through_receipt_s": coordinator,
        "measured_attempt_cpu_s": math.fsum((worker, coordinator)),
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
            used_names = {row.get("run_id") for row in reconciled["attempts"]}
            unused_reservations = [row["worker_cpu_reservation_s"]
                                   + row["coordinator_cpu_reservation_s"]
                                   for row in budget.get("run_allocations", [])
                                   if row["run_id"] not in used_names]
            last_status = {
                "schema": "CR_PARENT_EVENT_FINAL_BUDGET_STATUS_V1", "unit": UNIT_ID,
                "attempt_id": state["attempt_id"], "created_utc": utc_now(),
                "authoritative_debit": str(debit_path.relative_to(UNIT)),
                "charged_cpu_s": reconciled["charged_cpu_s"], "cap_s": HARD_CAP_S,
                "remaining_not_transferable": remaining,
                "unique_attempts": len(reconciled["attempts"]),
                "ledger_lock_held": state["lock_held"],
                "ledger_synchronized": state["lock_held"],
                "budget_status": "EXCEEDED" if remaining < 0 else
                                 ("EXHAUSTED" if remaining == 0 else "WITHIN_CAP"),
                "admission_gate": ("OPEN_SUBJECT_TO_FRESH_LOCKED_RESERVATION" if
                    unused_reservations and remaining >= min(unused_reservations) else
                    "CLOSED_NO_ADMISSIBLE_UNUSED_FROZEN_ALLOCATION"),
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
            last_status = {"schema": "CR_PARENT_EVENT_FINAL_BUDGET_STATUS_V1", "unit": UNIT_ID,
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
        "budget": {"unit": UNIT_ID, "spent_before_C4_admission": None,
                   "preparation_measured_CPU_s": None,
                   "preparation_conservative_tail_CPU_s": None,
                   "coordinator_reserve_per_attempt_s": 2.05,
                   "coordinator_receipt_tail_reserve_s": 0.05},
    }
    try:
        state["stage"] = "create_only_invocation_lease"
        need(UNIT.name == EXPECTED_UNIT_DIRECTORY and UNIT.parent.name == "research",
             "DRAFT_NOT_INSTALLED_IN_NEW_UNIT")
        lease_path = LEASES / (state["attempt_id"] + ".json")
        atomic_json(lease_path, {
            "schema": "CR_PARENT_EVENT_INVOCATION_LEASE_V1", "unit": UNIT_ID,
            "attempt_id": state["attempt_id"], "run_id": None,
            "coordinator_pid": os.getpid(), "started_utc": state["started_utc"],
            "status": "STARTED_REQUIRES_SAME_ID_TERMINAL_DEBIT",
            "automatic_stale_lease_deletion": False,
        }, create_only=True)
        state["invocation_lease_path"] = str(lease_path.relative_to(UNIT))
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
            # A malformed budget must not suppress the independent debit.
            # This fixed emergency tail is charged, never an execution permit.
            receipt = make_receipt(state, 2.05)
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

