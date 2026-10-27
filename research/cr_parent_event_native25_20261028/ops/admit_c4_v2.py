"""Fresh, measured C4 preparation; no model/science import or worker execution.

Run only after C04 preflight and all worker sources/static reviews are complete.
Creates immutable cumulative preparation receipts, including refusal costs.
A successful receipt freezes this unit's code/input/resource budget only.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
UNIT_ID = "CR_PHYS02_PARENT_EVENT_NATIVE25_V1"
TAIL = .05
PREPARATION_CAP = 4.
SELECTED_MEMORY = 268435456
HOST_RESERVE = 1073741824


def cpu(who):
    r = resource.getrusage(who)
    return r.ru_utime + r.ru_stime


def pin(path):
    b = path.read_bytes()
    return {"path": str(path.relative_to(UNIT)), "bytes": len(b),
            "sha256": hashlib.sha256(b).hexdigest()}


def write_new(path, obj, created_paths=None):
    b = (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode()
    with path.open("xb") as f:
        if created_paths is not None:
            created_paths.append(path)
        f.write(b)
    return {"path": str(path.relative_to(UNIT)), "bytes": len(b),
            "sha256": hashlib.sha256(b).hexdigest()}


def record_failure(receipt, exc, context):
    failure = {"type": type(exc).__name__, "message": str(exc),
               "context": context, "traceback": traceback.format_exc()}
    receipt.setdefault("failures", []).append(failure)
    receipt["failure"] = failure
    receipt["status"] = "failed"


def cumulative_debit(receipt, cleanup_complete, sequence):
    measured = cpu(resource.RUSAGE_SELF) + cpu(resource.RUSAGE_CHILDREN)
    charged = math.fsum((measured, TAIL))
    receipt.update(terminal_debit=cleanup_complete,
                   cpu_accounting_complete=cleanup_complete,
                   cleanup_complete=cleanup_complete,
                   debit_kind="CUMULATIVE_SAME_ATTEMPT",
                   debit_sequence=sequence,
                   measured_preparation_CPU_s=measured,
                   conservative_tail_CPU_s=TAIL,
                   charged_preparation_CPU_s=charged)
    if charged > PREPARATION_CAP:
        failure = {"type": "PreparationBudgetExceeded", "charged_CPU_s": charged}
        receipt.setdefault("failures", []).append(failure)
        receipt["failure"] = failure
        receipt["status"] = "failed"
    return measured, charged


def preparation_ledger(evidence):
    """Retain all actual debits; charge each attempt's maximum only once."""
    if list(evidence.glob("C04_PREPARATION_UNKNOWN_*.json")):
        raise RuntimeError("UNKNOWN_PREPARATION_ACCOUNTING_REQUIRES_OWNER_RECONCILIATION")
    selected, all_rows = {}, []
    for path in sorted(evidence.glob("C04_HOST_ADMISSION_*.json")):
        r = json.loads(path.read_text())
        if (r.get("unit") != UNIT_ID or r.get("terminal_debit") is not True
                or r.get("cpu_accounting_complete") is not True
                or r.get("status") not in ("completed", "failed")):
            raise RuntimeError("UNRECONCILED_PREPARATION_RECEIPT")
        attempt = r.get("attempt")
        sequence = r.get("debit_sequence", 0)
        if not isinstance(attempt, str) or not attempt or type(sequence) is not int or sequence < 0:
            raise RuntimeError("PREPARATION_ATTEMPT_AND_SEQUENCE_REQUIRED")
        fields = ("measured_preparation_CPU_s", "conservative_tail_CPU_s",
                  "charged_preparation_CPU_s")
        costs = {key: r[key] for key in fields}
        if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0
               for v in costs.values()):
            raise RuntimeError("FINITE_NONNEGATIVE_PREPARATION_COST_REQUIRED")
        if abs(costs[fields[2]] - math.fsum((costs[fields[0]], costs[fields[1]]))) > 1e-12:
            raise RuntimeError("PREPARATION_COMPONENT_COST_MISMATCH")
        row = {**pin(path), **costs, "attempt": attempt, "debit_sequence": sequence,
               "status": r["status"]}
        all_rows.append(row)
        old = selected.get(attempt)
        if old is None or (row[fields[2]], sequence) > (old[fields[2]], old["debit_sequence"]):
            selected[attempt] = row
    for path in sorted(evidence.glob("C04_PREPARATION_INTENT_*.json")):
        intent = json.loads(path.read_text())
        if intent.get("unit") != UNIT_ID or intent.get("attempt") not in selected:
            raise RuntimeError("UNKNOWN_NO_ACK_PREPARATION_INTENT:" + path.name)
    rows = [selected[key] for key in sorted(selected)]
    if not rows:
        raise RuntimeError("ACTUAL_PREPARATION_DEBIT_REQUIRED")
    ledger = {"schema": "CR_PARENT_EVENT_PREPARATION_LEDGER_V1", "unit": UNIT_ID,
              "status": "ACTUAL_RECONCILED", "records": rows,
              "all_cumulative_records": all_rows,
              "aggregation": "maximum cumulative charged debit per attempt; no prefix-plus-amendment sum",
              "all_preparation_attempts_completed": all(x["status"] == "completed" for x in rows),
              "measured_total_CPU_s": math.fsum(x["measured_preparation_CPU_s"] for x in rows),
              "conservative_tail_total_CPU_s": math.fsum(x["conservative_tail_CPU_s"] for x in rows),
              "charged_total_CPU_s": math.fsum(x["charged_preparation_CPU_s"] for x in rows)}
    if ledger["charged_total_CPU_s"] > PREPARATION_CAP:
        raise RuntimeError("ALL_PREPARATION_ATTEMPTS_EXCEED_FROZEN_RESERVE")
    return ledger


def process_stat(pid):
    text = Path(f"/proc/{pid}/stat").read_text()
    fields = text[text.rfind(")") + 2:].split()
    return {"pid": pid, "state": fields[0], "ppid": int(fields[1]),
            "pgrp": int(fields[2]), "session": int(fields[3]),
            "start_ticks": int(fields[19])}


def cgroup_view():
    membership = Path("/proc/self/cgroup").read_bytes()
    rel = next(line[3:] for line in membership.decode().splitlines() if line.startswith("0::"))
    candidates = []
    for line in Path("/proc/self/mountinfo").read_text().splitlines():
        left, right = line.split(" - ", 1)
        if right.split()[0] != "cgroup2":
            continue
        fields = left.split()
        root, mount = fields[3], fields[4]
        if rel == root:
            path = Path(mount)
        elif root == "/":
            path = Path(mount) / rel.lstrip("/")
        elif rel.startswith(root.rstrip("/") + "/"):
            path = Path(mount) / rel[len(root):].lstrip("/")
        else:
            continue
        if (path / "memory.max").is_file():
            candidates.append((len(root), path.resolve(), Path(mount).resolve()))
    if not candidates:
        raise RuntimeError("NO_EFFECTIVE_CGROUP_V2_MEMORY_VIEW")
    _, path, mount = max(candidates, key=lambda row: row[0])
    # The runner pins and monitors one effective view. Do not silently discard
    # a separately visible tighter ancestor: report it for explicit review.
    ancestors = []
    current = path
    while current.is_relative_to(mount):
        limit = (current / "memory.max").read_text().strip()
        used = int((current / "memory.current").read_text())
        ancestors.append({"path": str(current), "memory_max": limit,
                          "memory_current": used,
                          "raw_headroom": None if limit == "max" else int(limit) - used})
        if current == mount:
            break
        current = current.parent
    return path, membership, ancestors


def memory_observation():
    path, membership, ancestors = cgroup_view()
    mem = {line.split(":", 1)[0]: int(line.split()[1]) * 1024
           for line in Path("/proc/meminfo").read_text().splitlines()
           if len(line.split()) >= 3 and line.split()[2] == "kB"}
    stat = {p[0]: int(p[1]) for line in (path / "memory.stat").read_text().splitlines()
            if len(p := line.split()) == 2}
    first = ancestors[0]
    raw = first["raw_headroom"]
    keys = {"file", "shmem", "active_file", "inactive_file", "file_mapped", "file_dirty", "file_writeback", "unevictable"}
    if not keys <= set(stat) or any(type(v) is not int or v < 0 for v in stat.values()):
        raise RuntimeError("EXPLICIT_NONNEGATIVE_MEMORY_COUNTERS_REQUIRED")
    protected_min = int((path / "memory.min").read_text().strip())
    protected_low = int((path / "memory.low").read_text().strip())
    if protected_min < 0 or protected_low < 0:
        raise RuntimeError("NONNEGATIVE_CGROUP_PROTECTION_REQUIRED")
    candidate = min(stat["file"], stat["active_file"]+stat["inactive_file"])
    excluded = sum(stat[k] for k in ("shmem", "file_mapped", "file_dirty", "file_writeback", "unevictable"))
    eligible = max(0, candidate-excluded)
    protection_clear = protected_min == 0 and protected_low == 0
    credit = min(eligible//4, HOST_RESERVE) if raw is not None and protection_clear else 0
    available = min(mem["MemAvailable"], max(0, raw+credit)) if raw is not None else mem["MemAvailable"]
    raw_pass = raw is None or raw >= SELECTED_MEMORY
    tighter = [x for x in ancestors[1:] if x["raw_headroom"] is not None
               and x["raw_headroom"] < available]
    return {"estimator_version": "CAPPED_CLEAN_FILE_LRU25_V2",
            "admission_pass": raw_pass and available >= SELECTED_MEMORY + HOST_RESERVE and not tighter,
            "host_MemAvailable_bytes": mem["MemAvailable"],
            "cgroup_memory_max_bytes": first["memory_max"] if raw is None else int(first["memory_max"]),
            "cgroup_memory_current_bytes": first["memory_current"],
            "cgroup_raw_headroom_bytes": raw, "memory_stat_counters": stat,
            "credited_reclaim_bytes": credit, "prior_file_LRU_policy_imported": False,
            "candidate_file_LRU_bytes": candidate, "excluded_counter_sum_bytes": excluded,
            "eligible_file_estimate_bytes": eligible, "credit_fraction": .25,
            "credit_cap_bytes": HOST_RESERVE, "memory_min_bytes": protected_min,
            "memory_low_bytes": protected_low, "credit_protection_gate": protection_clear,
            "raw_worker_headroom_pass": raw_pass,
            "host_capped_available_estimate_bytes": available,
            "required_worker_plus_reserve_bytes": SELECTED_MEMORY + HOST_RESERVE,
            "selected_worker_memory_limit_bytes": SELECTED_MEMORY,
            "frozen_worker_memory_upper_cap_bytes": 536870912,
            "minimum_host_memory_reserve_bytes": HOST_RESERVE,
            "cgroup_v2_path": str(path), "process_cgroup_membership": membership.decode(),
            "process_cgroup_membership_sha256": hashlib.sha256(membership).hexdigest(),
            "visible_cgroup_views": ancestors, "unreviewed_tighter_ancestor_views": tighter,
            "non_atomic_counter_snapshot": True, "admission_estimate_not_guarantee": True,
            "lower_bound_certificate": False, "OS_settings_changed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    if args.attempt != "c4_v2":
        raise ValueError("THIS_SOURCE_ADMITS_ONLY_UNSTARTED_C4_V2")
    evidence = UNIT / "evidence"
    evidence.mkdir(exist_ok=True)
    intent = {"unit": UNIT_ID, "attempt": args.attempt,
              "source": pin(Path(__file__).resolve()),
              "observed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "preparation_cap_CPU_s": PREPARATION_CAP, "tail_CPU_s": TAIL,
              "scientific_worker_started": False, "old_science_replay": 0}
    intent_path = evidence / "C04_PREPARATION_INTENT_c4_v2.json"
    created_intents = []
    receipt = {"schema": "CR_PARENT_EVENT_C4_HOST_ADMISSION_V1", "unit": UNIT_ID,
               "attempt": args.attempt, "observed_utc": intent["observed_utc"],
               "status": "failed", "memory_gate": "NOT_OBSERVED",
               "memory_admission_policy": "CAPPED_CLEAN_FILE_LRU25_V2",
               "owned_PID_observation_probe": {"status": "NOT_RUN"},
               "source": intent["source"], "old_budget_transferred": False,
               "parallel_project_budget_transferred": False, "template_only": False,
               "scientific_worker_started": False, "model_imports": 0,
               "CPU_accounting_scope": "whole preparation process RUSAGE_SELF plus its actual children; tail separate"}
    proc = None
    code_manifest = None
    cleanup_complete = True
    try:
        write_new(intent_path, intent, created_intents)
        def preparation_cpu_limit(signum, frame):
            raise RuntimeError("PREPARATION_SELF_CPU_SOFT_LIMIT")
        signal.signal(signal.SIGXCPU, preparation_cpu_limit)
        resource.setrlimit(resource.RLIMIT_CPU, (3, 4))
        receipt["self_CPU_soft_hard_limits_s"] = [3, 4]
        receipt["preventive_hard_aggregate_CPU_bound_proven"] = False
        preflight_path = UNIT / "intake/preflight/C04_V2.json"
        preflight = json.loads(preflight_path.read_text())
        guards = preflight.get("guards", {})
        cr_owner = preflight.get("owners", {}).get("CR", {})
        if (preflight.get("schema") != "CR_PARENT_NODE_PREFLIGHT_V1"
                or preflight.get("stage") != "C04_V2"
                or guards.get("own_local_remote_expected_match") is not True
                or guards.get("central_head_and_DAG_qualified") is not True
                or cr_owner.get("repository") != "bass_cr"
                or cr_owner.get("branch") != "research/cr-parent-event-native25-20261028"
                or not preflight.get("local_HEAD")
                or preflight["local_HEAD"] != cr_owner.get("head")
                or preflight.get("source_and_previous_backup_receipt_check") != "PASS"):
            raise RuntimeError("ACTUAL_C04_PREFLIGHT_REQUIRED")
        receipt["owner_head"] = preflight["local_HEAD"]
        receipt["preflight"] = pin(preflight_path)
        receipt["source_and_previous_backup_receipts_rechecked"] = True
        review_path = UNIT / "review/RUNTIME_MEMORY_V2_REVIEW.json"
        review = json.loads(review_path.read_text())
        receipt["independent_static_review_sha256"] = pin(review_path)["sha256"]
        receipt["independent_static_review_record"] = review
        runtime_pin = pin(UNIT / "implementation/run_bounded.py")
        if (review.get("unit") != UNIT_ID or
                review.get("verdict") != "PASS_SCOPED_STATIC_NO_EXECUTION" or
                review.get("blocking_findings") != [] or
                review.get("reviewed_source", {}).get("sha256") != runtime_pin["sha256"] or
                review.get("reviewed_source", {}).get("bytes") != runtime_pin["bytes"]):
            raise RuntimeError("ACTUAL_RUNTIME_STATIC_REVIEW_PIN_MISMATCH")
        receipt["actual_reviewed_runtime"] = runtime_pin
        policy_path = UNIT / "coding/C04_MEMORY_POLICY_V2.json"
        policy = json.loads(policy_path.read_text())
        if policy.get("policy") != "CAPPED_CLEAN_FILE_LRU25_V2" or policy.get("credit_fraction") != .25 or policy.get("credit_cap_bytes") != HOST_RESERVE:
            raise RuntimeError("EXPLICIT_MEMORY_POLICY_V2_REQUIRED")
        prior = policy["previous_attempt"]
        if pin(UNIT / prior["path"])["sha256"] != prior["sha256"]:
            raise RuntimeError("PREVIOUS_V1_FAILURE_IDENTITY_CHANGED")
        receipt["memory_policy"] = pin(policy_path)
        receipt["previous_failed_attempt_preserved"] = prior
        # Exact inherited input identities are rechecked without imports.
        manifest = json.loads((UNIT / "inputs/INPUT_MANIFEST.json").read_text())
        for row in manifest["files"]:
            input_path = REPO / row["path"]
            if input_path.stat().st_size != row["bytes"]:
                raise RuntimeError("PINNED_SOURCE_SIZE_CHANGED:" + row["path"])
            raw = input_path.read_bytes()
            if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
                raise RuntimeError("PINNED_SOURCE_CHANGED:" + row["path"])
        code_paths = sorted([* (UNIT / "implementation").glob("*.py"),
                             * (UNIT / "review").glob("*.py")])
        required = {"parent_event.py", "controls.py", "independent_reference.py",
                    "plot_saved.py", "run_bounded.py"}
        if not required.issubset({p.name for p in code_paths}):
            raise RuntimeError("ALL_FROZEN_WORKER_SOURCES_REQUIRED")
        code_manifest = {"schema": "CR_PARENT_EVENT_FROZEN_CODE_MANIFEST_V1", "unit": UNIT_ID,
                         "status": "FROZEN", "files": [pin(p) for p in code_paths],
                         "template_only": False, "science_import_or_compile_performed": False}
        memory = memory_observation()
        receipt["memory_admission"] = memory
        receipt["memory_gate"] = "PASS" if memory["admission_pass"] else "REFUSED"
        if not memory["admission_pass"]:
            raise RuntimeError("FRESH_RAW_MEMORY_OR_EFFECTIVE_VIEW_ADMISSION_REFUSED")
        probe_before = cpu(resource.RUSAGE_SELF) + cpu(resource.RUSAGE_CHILDREN)
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.12)"],
                                start_new_session=True, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        cleanup_complete = False
        identity = process_stat(proc.pid)
        if identity["ppid"] != os.getpid() or identity["pgrp"] != proc.pid or proc.poll() is not None:
            raise RuntimeError("KNOWN_LIVE_OWNED_PID_OBSERVATION_FAILED")
        if proc.wait(timeout=3) != 0:
            raise RuntimeError("OWNED_PID_PROBE_CHILD_FAILED")
        cleanup_complete = True
        receipt["owned_PID_observation_probe"] = {
            "status": "PASS", "known_Popen_PID": proc.pid, "start_ticks": identity["start_ticks"],
            "live_PID_observed": True, "child_cleanup_complete": True,
            "observed_identity": identity,
            "CPU_s": cpu(resource.RUSAGE_SELF) + cpu(resource.RUSAGE_CHILDREN) - probe_before,
            "cost_already_in_total_preparation": True}
        receipt["status"] = "completed"
    except BaseException as exc:
        record_failure(receipt, exc, "admission_or_probe")
    finally:
        try:
            if proc is not None:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=2)
                cleanup_complete = proc.poll() is not None
        except BaseException as exc:
            cleanup_complete = False
            record_failure(receipt, exc, "owned_probe_cleanup")

    host_pin = None
    created_budgets = []
    budget_path = UNIT / "EXECUTION_BUDGET.json"
    try:
        if intent_path not in created_intents:
            raise RuntimeError("UNOWNED_OR_UNWRITTEN_PREPARATION_INTENT")
        if not cleanup_complete:
            raise RuntimeError("OWNED_PROBE_CLEANUP_UNRESOLVED")
        measured, charged = cumulative_debit(receipt, cleanup_complete, 0)
        host_pin = write_new(evidence / "C04_HOST_ADMISSION_c4_v2.json", receipt)
        if receipt["status"] != "completed":
            if cpu(resource.RUSAGE_SELF) + cpu(resource.RUSAGE_CHILDREN) > charged:
                raise RuntimeError("REFUSAL_RECEIPT_TAIL_EXCEEDED")
            print(json.dumps({"status": "REFUSED", "receipt": host_pin,
                              "charged_preparation_CPU_s": charged,
                              "failure": receipt.get("failure")}))
            return 2

        ledger = preparation_ledger(evidence)
        ledger_pin = write_new(evidence / "C04_PREPARATION_LEDGER.json", ledger)
        code_pin = write_new(evidence / "C04_CODE_MANIFEST.json", code_manifest)
        template = UNIT / "intake/runtime_draft/EXECUTION_BUDGET_TEMPLATE_V2.json"
        budget = json.loads(template.read_text())
        budget.update(status="FROZEN_C4_ADMITTED", template_only=False,
                      spent_before_C4_admission=ledger["charged_total_CPU_s"],
                      preparation_measured_CPU_s=ledger["measured_total_CPU_s"],
                      preparation_conservative_tail_CPU_s=ledger["conservative_tail_total_CPU_s"],
                      preparation_cost_manifest=ledger_pin["path"],
                      preparation_cost_manifest_sha256=ledger_pin["sha256"],
                      host_admission=host_pin["path"], host_admission_sha256=host_pin["sha256"],
                      code_manifest=code_pin["path"], code_manifest_sha256=code_pin["sha256"],
                      cgroup_v2_path=receipt["memory_admission"]["cgroup_v2_path"],
                      process_cgroup_membership_sha256=receipt["memory_admission"]["process_cgroup_membership_sha256"])
        budget["stage_authority"]["C04_preflight"] = receipt["preflight"]
        budget["notes"] = ["Actual same-unit preparation and code/resource/input pins; prior remainder transfer forbidden."]
        budget_pin = write_new(budget_path, budget, created_budgets)
        post_cpu = cpu(resource.RUSAGE_SELF) + cpu(resource.RUSAGE_CHILDREN)
        check = {"unit": UNIT_ID, "measured_through_postwrite_CPU_s": post_cpu,
                 "charged_receipt_CPU_s": charged,
                 "observed_postwrite_covered_by_tail": post_cpu <= charged,
                 "budget": budget_pin, "scientific_worker_started": False,
                 "remaining_receipt_tail_is_not_hard_proof": True}
        write_new(evidence / "C04_POSTWRITE_CHECK.json", check)
        # Also sample after the check's own serialization. Remaining print/exit
        # cost still uses the declared tail, not a claimed hard upper bound.
        after_check_cpu = cpu(resource.RUSAGE_SELF) + cpu(resource.RUSAGE_CHILDREN)
        if not check["observed_postwrite_covered_by_tail"] or after_check_cpu > charged:
            raise RuntimeError("POSTWRITE_TAIL_REFUSED")
        print(json.dumps({"status": "FROZEN_C4_ADMITTED", "charged_preparation_CPU_s": charged,
                          "measured_preparation_CPU_s": measured, "tail_CPU_s": TAIL,
                          "observed_after_check_CPU_s": after_check_cpu,
                          "memory_available_bytes": receipt["memory_admission"]["host_capped_available_estimate_bytes"],
                          "budget": budget_pin}))
        return 0
    except BaseException as exc:
        record_failure(receipt, exc, "finalization")
        quarantine_ok = True
        if budget_path in created_budgets:
            try:
                failed_dir = evidence / ("C04_FAILED_FINALIZATION_c4_v2_" + str(time.time_ns()))
                failed_dir.mkdir()
                target = failed_dir / budget_path.name
                budget_path.rename(target)
                receipt["quarantined_owned_budget"] = pin(target)
            except BaseException as quarantine_exc:
                quarantine_ok = False
                record_failure(receipt, quarantine_exc, "owned_budget_quarantine")
        receipt["active_budget_created_by_this_attempt"] = bool(created_budgets)
        receipt["active_budget_removed_on_failure"] = not created_budgets or not budget_path.exists()
        receipt["prior_prefix_receipt"] = host_pin
        receipt["maximum_cumulative_debit_only_no_double_charge"] = True
        try:
            if intent_path not in created_intents or not cleanup_complete or not quarantine_ok:
                raise RuntimeError("PREPARATION_FINALIZATION_REQUIRES_UNKNOWN_ACCOUNTING")
            measured, charged = cumulative_debit(receipt, True, 1)
            amendment_path = evidence / "C04_HOST_ADMISSION_c4_v2_amendment_1.json"
            amendment_pin = write_new(amendment_path, receipt)
            if cpu(resource.RUSAGE_SELF) + cpu(resource.RUSAGE_CHILDREN) > charged:
                raise RuntimeError("FAILURE_AMENDMENT_TAIL_EXCEEDED")
            print(json.dumps({"status": "FINALIZATION_REFUSED", "receipt": amendment_pin,
                              "charged_preparation_CPU_s": charged,
                              "budget_executable_path_present": budget_path.exists()}))
            return 3
        except BaseException as final_exc:
            # This is not a zero-cost receipt or a valid terminal debit. It
            # blocks a later admission until the owner reconciles actual cost.
            record_failure(receipt, final_exc, "failure_debit_or_coverage")
            unknown = {"schema": "CR_PARENT_EVENT_C4_UNKNOWN_FINALIZATION_V1",
                       "unit": UNIT_ID, "attempt": args.attempt,
                       "status": "UNKNOWN_NO_ACK", "terminal_debit": False,
                       "cpu_accounting_complete": False,
                       "measured_current_process_CPU_lower_bound_s":
                           cpu(resource.RUSAGE_SELF) + cpu(resource.RUSAGE_CHILDREN),
                       "cleanup_complete": cleanup_complete,
                       "active_budget_removed_on_failure": receipt["active_budget_removed_on_failure"],
                       "failure_history": receipt.get("failures", []),
                       "prior_prefix_receipt": host_pin,
                       "owner_reconciliation_required": True,
                       "scientific_worker_started": False}
            try:
                unknown_path = evidence / ("C04_PREPARATION_UNKNOWN_c4_v2_" + str(time.time_ns()) + ".json")
                unknown["durable_record"] = write_new(unknown_path, unknown)
            except BaseException as storage_exc:
                unknown["durable_record_error"] = repr(storage_exc)
            # If even durable writing failed, the invocation's stderr and the
            # create-only intent remain the explicit unresolved evidence.
            try:
                print(json.dumps(unknown), file=sys.stderr)
            except BaseException:
                pass
            return 4


if __name__ == "__main__":
    raise SystemExit(main())
