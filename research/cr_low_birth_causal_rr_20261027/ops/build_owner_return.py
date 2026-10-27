#!/usr/bin/env python3
"""Assemble actual low-birth owner-return metadata after S/D and all receipts exist.

No scientific implementation is imported or executed. No arrays or ZIP payloads
are opened, no directory is globbed, and no network/Git operation is performed.
All output paths are create-only. A partial I/O failure is retained for diagnosis.
The exact independently reviewed central validator is the sole local dependency.
This authoring revision has not been executed, imported or compiled by its author.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

UNIT_ROOT = Path(__file__).resolve().parents[1]
UNIT_ID = "CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1"
UNIT_PATH = "research/cr_low_birth_causal_rr_20261027"
CENTRAL_HELPER_SHA256 = "30680efa19450e9a0afc0186321c34bbc35b3771380792aa30eaac1779683fca"
ROLES = ("primary", "controls", "independent", "execution_ledger", "execution_budget", "final_review")
STAGES = tuple(f"{kind}{number:02d}" for kind in ("R", "C") for number in range(1, 11))


def load_validator():
    """Verify metadata-only dependency bytes before its definitions are loaded."""
    path = Path(__file__).with_name("build_central_low_birth.py")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CENTRAL_HELPER_SHA256:
        raise ValueError("Reviewed central metadata validator changed; focused review required")
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("cr_low_birth_central_metadata", path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the pinned metadata validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path.resolve(), raw


class Inputs:
    def __init__(self, core):
        self.core = core
        self.items: dict[Path, dict[str, Any]] = {}

    def remember(self, path: Path, raw: bytes, label: str) -> None:
        path = path.resolve(strict=True)
        old = self.items.get(path)
        if old is not None:
            self.core.require(old["raw"] == raw, "Input changed between reads: " + str(path))
            if label not in old["labels"]:
                old["labels"].append(label)
            return
        self.items[path] = {"raw": raw, "labels": [label]}

    def read(self, path: Path, label: str):
        self.core.require(path.suffix == ".json" and path.is_file() and not path.is_symlink(),
                          label + ": actual regular nonsymlink file required")
        resolved, raw, data = self.core.input_file(path, label)
        self.remember(resolved, raw, label)
        return resolved, raw, data

    def unit_json(self, path: Path, label: str):
        resolved, raw, data = self.read(path, label)
        self.core.require(resolved.is_relative_to(UNIT_ROOT), label + ": exact current unit file required")
        return resolved, raw, data

    def pinned_unit_json(self, row: Any, label: str):
        core = self.core
        core.require(type(row) is dict, label + ": exact saved pin required")
        relative = core.nonempty_identity(row.get("path"), label + ".path")
        core.require(not Path(relative).is_absolute() and ".." not in Path(relative).parts,
                     label + ": safe unit-local path required")
        path, raw, data = self.unit_json(UNIT_ROOT / relative, label)
        core.require(len(raw) == core.positive_integer(row.get("bytes"), label + ".bytes")
                     and core.sha256(raw) == core.digest_sha(row.get("sha256"), label + ".sha256"),
                     label + ": original saved bytes/SHA differ")
        return path, raw, data

    def unchanged(self) -> None:
        for path, item in self.items.items():
            self.core.require(path.is_file() and not path.is_symlink() and path.read_bytes() == item["raw"],
                              "An input changed during metadata assembly: " + str(path))

    def pins(self) -> list[dict[str, Any]]:
        return [{"path": str(path), "bytes": len(item["raw"]),
                 "sha256": self.core.sha256(item["raw"]), "labels": item["labels"]}
                for path, item in self.items.items()]


def integer(core, value: Any, label: str) -> int:
    core.require(type(value) is int and value >= 0, label + ": nonnegative integer required")
    return value


def validate_stages(inputs: Inputs, manifest: dict[str, Any], science: str, documents: str):
    core = inputs.core
    core.require(manifest.get("schema") == "CR_LOW_BIRTH_OWNER_RETURN_STAGE_INPUT_V1"
                 and manifest.get("unit") == UNIT_ID and type(manifest.get("stages")) is list,
                 "Explicit same-unit actual stage receipt manifest required")
    rows = manifest["stages"]
    core.require(len(rows) == len(STAGES) and all(type(row) is dict for row in rows),
                 "All actual twenty stage receipt pins are required")
    indexed = {row.get("stage"): row for row in rows}
    core.require(len(indexed) == len(STAGES) and set(indexed) == set(STAGES),
                 "Exactly R01-R10 and C01-C10 stage receipts required")
    receipts, commits, seen_paths = [], [], set()
    for number, stage in enumerate(STAGES, 1):
        row = indexed[stage]
        local = Path(core.nonempty_identity(row.get("local_path"), stage + ".local_path"))
        core.require(local.is_absolute(), "Stage local_path must be explicit and absolute")
        path, raw, data = inputs.read(local, "stage receipt " + stage)
        core.require(path not in seen_paths, "Stage receipt paths must be distinct")
        seen_paths.add(path)
        core.require(len(raw) == core.positive_integer(row.get("bytes"), stage + ".bytes")
                     and core.sha256(raw) == core.digest_sha(row.get("sha256"), stage + ".sha256"),
                     "Stage receipt differs from supplied raw pin: " + stage)
        core.require(data.get("schema") == "CR_LOW_BIRTH_STAGE_PUBLICATION_V1"
                     and data.get("stage") == stage and data.get("force") is False
                     and data.get("Git_ref_readback") is True,
                     "Actual non-force stage publication acknowledgement required: " + stage)
        commit = core.git_sha(data.get("commit"), stage + ".commit")
        parent = core.git_sha(data.get("expected_parent"), stage + ".expected_parent")
        core.git_sha(data.get("tree"), stage + ".tree")
        core.require(not commits or parent == commits[-1], "Stage publication ancestry chain is inconsistent")
        commits.append(commit)
        core.fixed_int(data.get("completed_loop_stage"), number, stage + ".completed_loop_stage")
        core.fixed_int(data.get("total_loop_stages"), len(STAGES), stage + ".total_loop_stages")
        archive = data.get("archive")
        core.require(type(archive) is dict, "Actual stage archive identity required")
        name = core.nonempty_identity(archive.get("name"), stage + ".archive.name")
        core.require(Path(name).name == name and name.endswith(".zip") and commit[:12] in name,
                     "Stage archive name must bind the actual stage commit")
        size = core.positive_integer(archive.get("bytes"), stage + ".archive.bytes")
        core.digest_sha(archive.get("sha256"), stage + ".archive.sha256")
        members = core.positive_integer(archive.get("members"), stage + ".archive.members")
        payloads = core.positive_integer(archive.get("payloads"), stage + ".archive.payloads")
        core.require(members == payloads + 1, "Stage archive manifest/member identity is inconsistent")
        providers = {}
        for provider in ("Dropbox", "Drive"):
            item = data.get(provider)
            core.require(type(item) is dict and item.get("ack") is True
                         and item.get("tier") in ("R2", "R3") and item.get("bytes") == size,
                         "Actual dual backup acknowledgement/tier/size required: " + stage)
            ident = core.nonempty_identity(item.get("id"), stage + "." + provider + ".id")
            providers[provider] = {"id": ident, "tier": item["tier"], "bytes": item["bytes"], "ack": True}
        completed = integer(core, data.get("central_completed"), stage + ".central_completed")
        core.require(completed <= core.EXPECTED_NODES, "Historical stage count exceeds original DAG total")
        core.fixed_int(data.get("central_total"), core.EXPECTED_NODES, stage + ".central_total")
        receipts.append({"stage": stage, "path": str(path), "bytes": len(raw),
                         "sha256": core.sha256(raw), "commit": commit,
                         "archive": {key: archive[key] for key in ("name", "bytes", "sha256", "members", "payloads")},
                         "providers": providers, "central_completed_as_published": completed,
                         "central_total_as_published": data["central_total"]})
    core.require(len(set(commits)) == len(STAGES) and science in commits and documents == commits[-1],
                 "Actual S/D must occur in the twenty distinct completed publication receipts")
    return {"R": f"{sum(row['stage'].startswith('R') for row in receipts)}/10",
            "C": f"{sum(row['stage'].startswith('C') for row in receipts)}/10",
            "total": f"{len(receipts)}/{len(STAGES)}", "actual_published_stage_commits": commits,
            "dual_R2_stage_receipts": len(receipts), "canonical_source_dual_R3": True,
            "stage_receipt_evidence": receipts,
            "historical_stage_counts_rewritten": False}


def validate_controls_history(inputs: Inputs, controls: dict[str, Any], ledger: dict[str, Any],
                              primary: dict[str, Any]):
    core = inputs.core
    core.require(controls.get("schema") == "CR_LOW_BIRTH_CONTROLS_ACCEPTANCE_V1"
                 and controls.get("unit") == UNIT_ID and controls.get("all_pass") is True,
                 "Actual C06 aggregate with preserved original failures required")
    checks = controls.get("checks")
    core.require(type(checks) is list and len(checks) == controls.get("count")
                 and all(type(row) is dict and row.get("pass") is True for row in checks),
                 "Every accepted aggregate control must be explicitly present and successful")
    names = [core.nonempty_identity(row.get("name"), "accepted control name") for row in checks]
    core.require(len(set(names)) == len(names), "Duplicate accepted control names refused")
    raw_results, basis_counts = {}, {}
    for row in checks:
        path, raw, source = inputs.pinned_unit_json(row.get("evidence"), "accepted control source")
        core.require(source.get("unit") == UNIT_ID and type(source.get("checks")) is list
                     and all(type(item) is dict for item in source["checks"]),
                     "Accepted control source must be an actual same-unit result")
        matching = [item for item in source["checks"] if item.get("name") == row["name"]]
        core.require(len(matching) == 1 and matching[0].get("pass") is True,
                     "Aggregate control is not backed by an actual successful source check")
        raw_results[path] = source
        basis = row.get("basis")
        core.require(basis in ("identity_scoped_reuse_no_rerun", "changed_exact_oracle_targeted_execution"),
                     "Unsupported control aggregation basis")
        basis_counts[basis] = basis_counts.get(basis, 0) + 1
        if basis == "changed_exact_oracle_targeted_execution":
            core.require(source.get("execution_scope") == "selected_control_only"
                         and source.get("only_requested") == row["name"] and source.get("count") == 1,
                         "Repair must be the actual selected one-control result")
    actual_evaluations = actual_passes = 0
    for source in raw_results.values():
        source_checks = source["checks"]
        core.fixed_int(source.get("count"), len(source_checks), "raw controls.count")
        passed = sum(item.get("pass") is True for item in source_checks)
        core.fixed_int(source.get("passed"), passed, "raw controls.passed")
        core.require(source.get("all_pass") is (passed == len(source_checks)), "Raw control outcome is inconsistent")
        actual_evaluations += len(source_checks)
        actual_passes += passed
    for key, value in (("actual_control_evaluations", actual_evaluations),
                       ("actual_pass_evaluations", actual_passes),
                       ("actual_failed_evaluations", actual_evaluations - actual_passes),
                       ("prior_accepted_reused", basis_counts.get("identity_scoped_reuse_no_rerun", 0)),
                       ("new_targeted_repair_checks", basis_counts.get("changed_exact_oracle_targeted_execution", 0))):
        core.fixed_int(controls.get(key), value, "controls." + key)
    core.require(controls.get("all_raw_control_attempts_pass") is False
                 and actual_passes < actual_evaluations and controls.get("exact_zero_checks_retained") is True
                 and controls.get("scientific_tolerances_relaxed") is False
                 and controls.get("old_suites_replayed") == 0,
                 "The actual failed oracle attempt and unchanged tolerance/reuse history must survive")
    failed_path, _, failed_result = inputs.pinned_unit_json(controls.get("failed_result_preserved"), "preserved failed control result")
    _, _, failed_receipt = inputs.pinned_unit_json(controls.get("failed_receipt_preserved"), "preserved failed control receipt")
    _, _, repair_receipt = inputs.pinned_unit_json(controls.get("repair_receipt"), "selected repair receipt")
    _, _, repair_review = inputs.pinned_unit_json(controls.get("repair_review"), "oracle diagnosis review")
    _, prepared_raw, prepared = inputs.pinned_unit_json(controls.get("prepared_source"), "reused preparation metadata")
    core.require(failed_path in raw_results and failed_result.get("unit") == UNIT_ID
                 and failed_result.get("all_pass") is False and failed_receipt.get("status") == "failed"
                 and failed_receipt.get("run_id") == "controls_v1"
                 and repair_receipt.get("status") == "completed" and repair_receipt.get("run_id") == "controls_v2",
                 "The original controls_v1 failure and unique controls_v2 recovery must remain explicit")
    attempts = {row["attempt_id"]: row for row in ledger["attempts"]}
    for receipt in (failed_receipt, repair_receipt):
        core.require(receipt.get("unit") == UNIT_ID and receipt.get("attempt_id") in attempts,
                     "Control receipt is missing from the actual same-unit debit ledger")
        debit = attempts[receipt["attempt_id"]]
        core.require(debit.get("status") == receipt.get("status")
                     and core.finite_number(debit.get("charged_cpu_s"), "control debit") + Decimal("1e-10")
                     >= core.finite_number(receipt.get("charged_cpu_s"), "control receipt cost"),
                     "Preserved control failure/repair cost is missing from its cumulative ledger debit")
    core.require(repair_review.get("unit") == UNIT_ID and prepared.get("unit") == UNIT_ID
                 and primary.get("preparation_sha256") == core.sha256(prepared_raw),
                 "Actual primary must reuse the same pinned preparation and same-unit repair review")
    summary = {key: deepcopy(value) for key, value in controls.items() if key != "checks"}
    summary["failed_attempt_id"] = failed_receipt["attempt_id"]
    summary["repair_attempt_id"] = repair_receipt["attempt_id"]
    summary["failed_attempt_cumulative_charged_cpu_s"] = attempts[failed_receipt["attempt_id"]]["charged_cpu_s"]
    summary["repair_attempt_cumulative_charged_cpu_s"] = attempts[repair_receipt["attempt_id"]]["charged_cpu_s"]
    summary["accepted_check_names"] = names
    return summary, prepared


def review_coverage(core, review: dict[str, Any], descriptors: list[dict[str, Any]], open_pointer: str) -> None:
    core.require(core.pointer(review, open_pointer) == [], "Final review still has open blocking findings")
    rows = review.get("reviewed_files")
    core.require(type(rows) is list and all(type(row) is dict for row in rows),
                 "Final independent review must pin its actual reviewed files")
    indexed = {}
    for row in rows:
        name = row.get("path")
        core.require(isinstance(name, str) and name and ".." not in Path(name).parts,
                     "Safe reviewed-file path required")
        if Path(name).is_absolute():
            path = Path(name).resolve(strict=True)
            if not path.is_relative_to(UNIT_ROOT):
                continue
            name = UNIT_PATH + "/" + path.relative_to(UNIT_ROOT).as_posix()
        elif not name.startswith(UNIT_PATH + "/"):
            name = UNIT_PATH + "/" + name
        indexed.setdefault(name, []).append(row)
    for descriptor in descriptors:
        if descriptor["role"] == "final_review":
            continue
        matches = indexed.get(descriptor["repo_path"], [])
        core.require(len(matches) == 1 and matches[0].get("bytes") == descriptor["bytes"]
                     and matches[0].get("sha256") == descriptor["sha256"],
                     "Actual current result/budget/ledger bytes were not pinned by final review: " + descriptor["role"])
    core.require(type(review.get("scientific_scope")) is dict and bool(review["scientific_scope"])
                 and type(review.get("runtime_limits")) is dict and bool(review["runtime_limits"]),
                 "Actual review scientific scope and runtime limitations must be explicit")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("primary", "controls", "independent", "final-review", "budget", "ledger",
                   "source-r3", "central-count-baseline", "dag", "stage-receipts"):
        parser.add_argument("--" + option, type=Path, required=True)
    for option in ("science-sha", "documents-sha", "central-head", "pull-request"):
        parser.add_argument("--" + option, required=True)
    parser.add_argument("--evidence-revision", action="append", default=[], metavar="ROLE=S|D",
                        help="Explicit evidence revision assignment; all six roles default to actual S.")
    parser.add_argument("--review-verdict-pointer", default="/verdict")
    parser.add_argument("--review-blocking-pointer", default="/blocking_findings")
    parser.add_argument("--review-open-blocking-pointer", default="/open_blocking_findings")
    parser.add_argument("--out-owner-return", type=Path, required=True)
    parser.add_argument("--out-results", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    core, helper_path, helper_raw = load_validator()
    inputs = Inputs(core)
    inputs.remember(helper_path, helper_raw, "pinned central metadata validator")
    source_path = Path(__file__).resolve()
    inputs.remember(source_path, source_path.read_bytes(), "owner-return metadata assembler")
    science = core.git_sha(args.science_sha, "actual S")
    documents = core.git_sha(args.documents_sha, "actual D")
    central_head = core.git_sha(args.central_head, "actual current central HEAD")
    revisions = {role: science for role in ROLES}
    overridden = set()
    for assignment in args.evidence_revision:
        pieces = assignment.split("=")
        core.require(len(pieces) == 2 and pieces[0] in ROLES and pieces[1] in ("S", "D")
                     and pieces[0] not in overridden, "Unique ROLE=S|D evidence assignment required")
        overridden.add(pieces[0])
        revisions[pieces[0]] = science if pieces[1] == "S" else documents
    paths = {"primary": args.primary, "controls": args.controls, "independent": args.independent,
             "execution_ledger": args.ledger, "execution_budget": args.budget, "final_review": args.final_review}
    descriptors, records = [], {}
    for role in ROLES:
        path, raw, data = inputs.unit_json(paths[role], role)
        descriptor = {"role": role, "local_path": str(path),
                      "repo_path": UNIT_PATH + "/" + path.relative_to(UNIT_ROOT).as_posix(),
                      "revision": revisions[role], "bytes": len(raw), "sha256": core.sha256(raw)}
        if role == "final_review":
            descriptor["acceptance"] = {"verdict_pointer": args.review_verdict_pointer,
                                        "blocking_count_pointer": args.review_blocking_pointer}
        descriptors.append(descriptor)
        records[role] = data
    results_input = {"schema": "CR_LOW_BIRTH_CENTRAL_RESULTS_INPUT_V1", "unit_id": UNIT_ID,
                     "science_commit_S": science, "documents_commit_D": documents, "files": descriptors}
    summary, result_evidence, preparation_evidence = core.validate_results(results_input, science, documents)
    for row in preparation_evidence:
        _, raw, _ = inputs.read(Path(row["path"]), "verified preparation input")
        core.require(len(raw) == row["bytes"] and core.sha256(raw) == row["sha256"],
                     "Preparation input changed after central validation")
    primary, controls, independent, ledger, budget, review = (records[role] for role in ROLES)
    review_coverage(core, review, descriptors, args.review_open_blocking_pointer)
    control_history, prepared = validate_controls_history(inputs, controls, ledger, primary)
    primary_pin = next(row for row in descriptors if row["role"] == "primary")
    checks = independent["numerical_acceptance"].get("checks")
    core.require(type(checks) is list and len(checks) == summary["independent_check_count"]
                 and all(type(row) is dict and row.get("pass") is True for row in checks),
                 "Every actual independent comparison must be explicitly successful")
    core.require(independent.get("comparison", {}).get("result_sha256") == primary_pin["sha256"]
                 and independent.get("comparison", {}).get("arrays_sha256")
                 == primary.get("artifacts", {}).get("ARRAYS.npz", {}).get("sha256"),
                 "Independent comparison must bind the exact saved primary result and array identity")
    dag_path, dag_raw, dag = inputs.read(args.dag, "current central DAG")
    core.validate_dag(dag)
    count_path, count_raw, count_input = inputs.read(args.central_count_baseline, "current central-count baseline")
    count_summary, count_evidence = core.validate_central_count_baseline(count_input, central_head, dag, core.sha256(dag_raw))
    for row in count_evidence:
        _, raw, _ = inputs.read(Path(row["path"]), "authoritative central-count return")
        core.require(len(raw) == row["bytes"] and core.sha256(raw) == row["sha256"], "Central-count authority changed")
    r3_path, r3_raw, r3 = inputs.read(args.source_r3, "actual canonical source dual R3")
    archive = core.validate_source_r3(r3)
    stages_path, stages_raw, stages = inputs.read(args.stage_receipts, "actual stage receipt pins")
    workflow = validate_stages(inputs, stages, science, documents)
    prep = summary["preparation_baseline"]
    monitor_rows = []
    for attempt in ledger["attempts"]:
        if attempt.get("worker_started") is True:
            core.require(attempt.get("aggregate_polling_is_kernel_hard_cap_proof") is False
                         and attempt.get("aggregate_monitor_is_non_atomic_estimate") is True,
                         "Observed monitor limits must not become a hard aggregate CPU proof")
        monitor_rows.append({key: deepcopy(attempt.get(key)) for key in
            ("attempt_id", "run_id", "worker_started", "status", "worker_cpu_s",
             "coordinator_cpu_through_receipt_s", "receipt_tail_reserve_s", "charged_cpu_s",
             "aggregate_worker_cpu_peak_estimate_s", "aggregate_monitor_polls",
             "maximum_observed_owned_processes", "aggregate_monitor_stop_reason",
             "aggregate_polling_is_kernel_hard_cap_proof", "aggregate_monitor_is_non_atomic_estimate")})
    core.require(budget.get("per_process_CPU_limit_is_aggregate_hard_proof") is False
                 and primary["numerical_acceptance"].get("arithmetic_interval_certification") is False
                 and primary["numerical_acceptance"].get("continuous_energy_or_physical_model_error_bound") is None,
                 "Actual arithmetic, physical-error and CPU-monitor claim ceilings must remain unchanged")
    results_raw = (core.encode_json(results_input, pretty=True) + "\n").encode("utf-8")
    owner = {
        "schema": "CR_LOW_BIRTH_CAUSAL_RR_OWNER_RETURN_V1", "unit_id": UNIT_ID, "unit_path": UNIT_PATH,
        "owner_repository": "cosmosapjw-quantum/bass_cr", "parent_node": core.TARGET_ID,
        "pull_request": args.pull_request, "science_commit_S": science, "documents_commit_D": documents,
        "central_commit_M": None, "central_base_sha": central_head, "central_expected_parent": central_head,
        "source_R3_receipt_sha256": core.sha256(r3_raw), "results_input_sha256": core.sha256(results_raw),
        "central_count_baseline_sha256": core.sha256(count_raw),
        "original_DAG": {"nodes": len(dag["nodes"]), "integration_edges": len(dag["integration_edges"]),
                         "declared_deliverable_count": count_summary["completed"], "new_count_effect": 0},
        "original_central_completed_total": count_summary["current_completed_total"],
        "historical_original_central_completed_total": count_summary["historical_completed_total"],
        "central_count_foreign_cause": count_summary["foreign_cause"],
        "unmerged_PR236_32_of_88_added": False, "original_node_status_changed": False,
        "scope_child": {"id": UNIT_ID, "completed": 1, "total": 1,
                        "parent_node": core.TARGET_ID, "original_central_count_effect": 0},
        "workflow": workflow,
        "gates": {"N4": "PARTIAL_OPEN", "N5": "PARTIAL_OPEN", "N6": "PREDECESSOR_GATED",
                  "N7": "PREDECESSOR_GATED", "L4_ready": False, "global_physical_completion": None,
                  "global_physical_error": None, "global_budget_remaining": None, "global_currency": None},
        "review_decision": summary["review_verdict"], "scientific_scope": summary["primary_scope"],
        "verification": {"new_controls_passed": summary["control_count"],
                         "independent_checks_passed": summary["independent_check_count"],
                         "all_runtime_attempts_pass": summary["all_runtime_attempts_pass"],
                         "all_resource_attempts_pass": summary["all_resource_attempts_pass"],
                         "all_worker_attempts_pass": summary["all_worker_attempts_pass"]},
        "execution": {"new_unit_cap_s": ledger["cap_s"], "charged_cpu_s": summary["charged_cpu_s"],
                      "legacy_ledger_measured_worker_plus_coordinator_cpu_s_as_saved":
                          ledger.get("measured_worker_plus_coordinator_cpu_s"),
                      "legacy_ledger_measurement_note":
                          "This saved ledger field includes the charged preparation baseline and its conservative tail; it is not pure measured CPU. The actual measured/tail/charged separation and closeout pin are preserved in review_runtime_limits.",
                      "baseline_preparation_cpu_s": prep["execution_ledger_baseline_preparation_cpu_s"],
                      "preparation_cost_manifest": prep["manifest_path"],
                      "preparation_cost_manifest_sha256": prep["manifest_sha256"],
                      "preserved_failed_preparation_receipt_paths": prep["explicitly_failed_preparation_receipt_paths"],
                      "preserved_failed_attempt_ids": summary["failed_attempt_ids"],
                      "old_or_parallel_budget_transferred": False, "unused_allowance_auto_carried_to_next_unit": False,
                      "hard_preventive_aggregate_cap_proof": False, "old_science_replays": ledger.get("old_science_replays")},
        "canonical_source_archive": {"science_commit_S": science, "canonical_same_immutable_zip": True,
                                     "source_rebuilt_after_seal": False,
                                     "archive": {key: archive[key] for key in ("name", "bytes", "sha256", "members", "payloads")},
                                     "provider_receipts": [{key: row[key] for key in
                                         ("provider", "id", "verification_tier", "archive_sha256", "downloaded_bytes",
                                          "archive_members", "manifest_payloads", "manifest_sha256")}
                                         for row in r3["providers"]]},
        "source_evidence": [{"path": row["repo_path"], "revision": row["revision"],
                             "bytes": row["bytes"], "sha256": row["sha256"]} for row in result_evidence],
        "preserved_control_history": control_history, "preserved_preparation_history": prep,
        "review_scientific_scope": deepcopy(review["scientific_scope"]),
        "review_runtime_limits": deepcopy(review["runtime_limits"]),
        "numerical_limitations": {"primary_status_as_saved": primary.get("status"),
            "primary_reference_status_as_saved": primary["numerical_acceptance"].get("independent_reference"),
            "independent_status_as_saved": independent["status"],
            "arithmetic_interval_certification": primary["numerical_acceptance"]["arithmetic_interval_certification"],
            "continuous_energy_or_physical_model_error_bound": None,
            "serialized_tail_records": deepcopy(primary["tails"]),
            "preparation_weight_diagnostics_as_saved": deepcopy(prepared.get("weights")),
            "zero_serialized_tail_is_not_an_exact_zero_remainder_certificate": True,
            "underflow_note": "A positive exact-arithmetic tail may underflow on conversion to binary64; ordinary-float zero is not an outward enclosure.",
            "caloric_partition_is_physical_heating_completion": False,
            "retained_photons_are_separate_from_w_ext_and_heating": True},
        "runtime_monitor_limitations": {"actual_attempt_monitor_records": monitor_rows,
            "hard_preventive_aggregate_cap_proof": False,
            "note": "Non-atomic procfs monitor samples can miss owned activity. Zero observed process/CPU samples do not erase terminal worker/coordinator CPU debits or prove an aggregate hard cap.",
            "memory_admission_is_estimate_not_guarantee": True},
        "metadata_assembly": {"new_scientific_execution": 0, "new_array_or_zip_reads": 0,
            "remote_queries": 0, "git_writes": 0, "central_candidate_created": False,
            "actual_stage_manifest_sha256": core.sha256(stages_raw),
            "validator_sha256": CENTRAL_HELPER_SHA256,
            "evidence_revision_assignments_supplied_by_root_not_remotely_verified_here": True,
            "actual_final_candidate_requires_separate_independent_review": True},
    }
    core.validate_owner_return(owner, central_head, science, documents,
        core.sha256(r3_raw), core.sha256(results_raw), archive, summary, result_evidence,
        count_summary, core.sha256(count_raw))
    owner_raw = (core.encode_json(owner, pretty=True) + "\n").encode("utf-8")
    core.require(core.exact_semantic_equal(core.decode_json(results_raw, "serialized results input"), results_input)
                 and core.exact_semantic_equal(core.decode_json(owner_raw, "serialized owner return"), owner),
                 "Exact Decimal metadata serialization changed a value")
    output_paths = [args.out_owner_return.resolve(), args.out_results.resolve(), args.receipt.resolve()]
    core.require(len(set(output_paths)) == len(output_paths)
                 and all(left not in right.parents for left in output_paths for right in output_paths if left != right),
                 "Output paths must be distinct and cannot contain another output path")
    for path in output_paths:
        core.require(not path.exists() and path not in inputs.items, "Output must be new and cannot replace an input")
    inputs.unchanged()
    for path in output_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
    core.write_new(output_paths[1], results_raw)
    core.write_new(output_paths[0], owner_raw)
    core.require(output_paths[1].read_bytes() == results_raw and output_paths[0].read_bytes() == owner_raw,
                 "Owner-return/results input output byte readback mismatch")
    inputs.unchanged()
    receipt = {"schema": "CR_LOW_BIRTH_OWNER_RETURN_ASSEMBLY_RECEIPT_V1", "unit": UNIT_ID,
               "status": "PASS_SCOPED_OFFLINE_OWNER_RETURN_METADATA_ASSEMBLY", "science_commit_S": science,
               "documents_commit_D": documents, "central_commit_M": None, "central_base_sha": central_head,
               "outputs": [{"path": str(path), "bytes": len(raw), "sha256": core.sha256(raw)}
                           for path, raw in ((output_paths[0], owner_raw), (output_paths[1], results_raw))],
               "inputs": inputs.pins(), "central_validator_accepts_in_memory_owner_return": True,
               "inputs_unchanged_at_end": True, "candidate_or_publication_created": False,
               "new_scientific_execution": 0, "new_array_or_zip_reads": 0, "remote_queries": 0,
               "separate_final_candidate_review_required": True}
    receipt_raw = (core.encode_json(receipt, pretty=True) + "\n").encode("utf-8")
    core.write_new(output_paths[2], receipt_raw)
    core.require(output_paths[2].read_bytes() == receipt_raw, "Assembly receipt byte readback mismatch")
    print(json.dumps({"status": receipt["status"], "outputs": receipt["outputs"],
                      "receipt_path": str(output_paths[2]), "receipt_sha256": core.sha256(receipt_raw)}, allow_nan=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("Owner-return metadata assembly refused: " + str(error), file=sys.stderr)
        raise SystemExit(2)
