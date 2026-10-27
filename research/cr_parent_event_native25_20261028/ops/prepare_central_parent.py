#!/usr/bin/env python3
"""Prospective, offline, create-only CR parent-event central package builder.

Author: /root/theory_review (metadata author; NOT its independent reviewer).
No scientific/production module, subprocess, Git client or network is used.
Only a new candidate DAG, one return and an external preservation proof can be
written. Root must supply actual final S/D and pinned completed evidence, then
obtain a different review and publish exactly two paths on the current tree.
See PREPARE_CENTRAL_PARENT_KO.md. Merely writing this source executes nothing.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import re
import sys


WORKSPACE = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSPACE / "bass_cr"
UNIT = "CR_PHYS02_PARENT_EVENT_NATIVE25_V1"
UNIT_PATH = "research/cr_parent_event_native25_20261028"
UNIT_ROOT = REPO_ROOT / UNIT_PATH
REPOSITORY = "cosmosapjw-quantum/bass_cr"
BRANCH = "research/cr-parent-event-native25-20261028"
CENTRAL_REPOSITORY = "cosmosapjw-quantum/rei_bianchi"
CENTRAL_BRANCH = "research/orchestration-sandbox-20261022"
CENTRAL_UNIT_PATH = "research/orchestration_expansion_20261025"
TARGET = "CR_ALL_EXTERNAL_PHOTON_BARYON_SOURCE_INTERFACE"
LINK = "owner_return_parent_event_native25_20261028"
RETURN = "returns/CR_PARENT_EVENT_NATIVE25_20261028.json"
CONTRACT_SHA = "01cc2d2835e3ad61c49cd0b68b8c413ebd7e0b8fb5228877804159c4e3f71162"
INPUT_SHA = "2273f08ac1716d233097d17c73818d39a9337da34712290a4b4171430d24f9b3"
SOURCE_SHA = "8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf"
STAGES = [f"{prefix}{number:02}" for prefix in ("R", "C") for number in range(1, 11)]
GATES = {"CR_N4_STOPPING_KERNEL": "PARTIAL_OPEN",
         "CR_N5_ATOMIC_ISOTOPE_COVERAGE": "PARTIAL_OPEN",
         "CR_N6_CONSERVATIVE_COUPLING": "PREDECESSOR_GATED",
         "CR_N7_NEW_PARCEL": "PREDECESSOR_GATED"}
REQUIRED_FILES = {"dag", "central_baseline", "publication_state", "contract", "input_manifest",
                  "report", "budget", "execution_budget", "execution_ledger", "preparation_ledger",
                  "primary", "controls", "reference", "C9", "admission", "source_archive", "source_R3"}
ACCOUNTING_TOLERANCE = Decimal("1e-10")  # recorded JSON float summation only; no science tolerance


class Refusal(ValueError):
    pass


def need(condition, code):
    if not condition:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "DUPLICATE_JSON_KEY")
        value[key] = item
    return value


def reject_constant(_):
    raise Refusal("NONFINITE_JSON_CONSTANT")


def decode(raw):
    # Historical decimal values are not rounded through binary64.
    return json.loads(raw.decode("utf-8"), parse_float=Decimal,
                      object_pairs_hook=unique_object, parse_constant=reject_constant)


def encode(value, pretty=False, depth=0):
    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    if type(value) is Decimal:
        need(value.is_finite(), "NONFINITE_DECIMAL")
        return str(value)
    if type(value) is str:
        return json.dumps(value, ensure_ascii=False)
    need(type(value) in (dict, list), "UNSUPPORTED_JSON_VALUE")
    if type(value) is dict:
        need(all(type(key) is str for key in value), "NONSTRING_OBJECT_KEY")
        children = [json.dumps(key, ensure_ascii=False) + (": " if pretty else ":")
                    + encode(value[key], pretty, depth + 1) for key in sorted(value)]
        start, end = "{", "}"
    else:
        children = [encode(item, pretty, depth + 1) for item in value]
        start, end = "[", "]"
    if not children:
        return start + end
    if not pretty:
        return start + ",".join(children) + end
    pad = "  " * (depth + 1)
    return start + "\n" + pad + (",\n" + pad).join(children) + "\n" + "  " * depth + end


def raw_json(value):
    return (encode(value, True) + "\n").encode("utf-8")


def semantic_sha(value):
    # Local exact-number canonicalization, not an RFC 8785 claim.
    return sha(encode(value).encode("utf-8"))


def same(left, right):
    return encode(left) == encode(right)


def hex_value(value, length):
    need(type(value) is str and re.fullmatch("[0-9a-f]{" + str(length) + "}", value)
         and len(set(value)) > 1, "ACTUAL_IMMUTABLE_HEX_ID_REQUIRED")
    return value


def integer(value, minimum=0):
    need(type(value) is int and value >= minimum, "NONNEGATIVE_INTEGER_REQUIRED")
    return value


def number(value):
    need(type(value) in (int, Decimal), "FINITE_NUMERIC_JSON_FIELD_REQUIRED")
    result = Decimal(value)
    need(result.is_finite(), "NONFINITE_NUMERIC_FIELD")
    return result


def close(left, right, code):
    need(abs(number(left) - number(right)) <= ACCOUNTING_TOLERANCE, code)


def text(value):
    need(type(value) is str and bool(value.strip()), "NONEMPTY_TEXT_REQUIRED")
    return value


def pointer(value, location):
    need(type(location) is str and (not location or location.startswith("/")), "JSON_POINTER_REQUIRED")
    for key in location.split("/")[1:]:
        key = key.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if type(value) is list else value[key]
    return value


def absolute(path):
    p = Path(text(path))
    need(p.is_absolute() and p == p.resolve(), "ABSOLUTE_NONSYMLINK_PATH_REQUIRED")
    return p


def unit_relative(path):
    p = Path(text(path))
    need(not p.is_absolute() and ".." not in p.parts, "SAFE_UNIT_RELATIVE_PATH_REQUIRED")
    result = absolute(str(UNIT_ROOT / p))
    need(result.is_relative_to(UNIT_ROOT), "FOREIGN_UNIT_PATH_REFUSED")
    return result


class Inputs:
    def __init__(self):
        self.seen = {}

    def read(self, path, expected=None, role=None):
        p = absolute(str(path))
        need(p.is_file() and not p.is_symlink(), "REGULAR_INPUT_FILE_REQUIRED")
        before = p.stat()
        raw = p.read_bytes()
        after = p.stat()
        need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
             == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), "INPUT_CHANGED_DURING_READ")
        pin = {"path": str(p), "bytes": len(raw), "sha256": sha(raw)}
        if expected is not None:
            need(integer(expected.get("bytes"), 1) == len(raw)
                 and hex_value(expected.get("sha256"), 64) == pin["sha256"], "INPUT_BYTE_PIN_MISMATCH")
        if str(p) in self.seen:
            need(self.seen[str(p)]["bytes"] == len(raw) and self.seen[str(p)]["sha256"] == sha(raw),
                 "INPUT_IDENTITY_CHANGED")
        self.seen[str(p)] = pin
        if role:
            pin = {"role": role, **pin}
        return raw, pin

    def pinned(self, pin, role):
        need(type(pin) is dict, "PIN_OBJECT_REQUIRED")
        raw, actual = self.read(pin.get("path"), pin, role)
        return decode(raw), actual

    def recheck(self):
        for pin in list(self.seen.values()):
            self.read(pin["path"], pin)


def validate_dag(dag):
    need(type(dag) is dict and type(dag.get("nodes")) is list and len(dag["nodes"]) == 88
         and type(dag.get("integration_edges")) is list and len(dag["integration_edges"]) == 17,
         "EXACT_88_NODES_17_EDGES_REQUIRED")
    ids = [text(node.get("id")) for node in dag["nodes"]]
    need(len(set(ids)) == 88 and ids.count(TARGET) == 1, "UNIQUE_ORIGINAL_NODE_IDENTITIES_REQUIRED")
    index = ids.index(TARGET)
    target = dag["nodes"][index]
    need(LINK not in target and type(target.get("contract")) is dict, "NEW_LINK_MUST_BE_ABSENT")
    for key in ("owner_return_20261025", "owner_return_proper_injection_20261027",
                "owner_return_low_birth_causal_rr_20261027"):
        need(type(target.get(key)) is dict, "PRIOR_CR_OWNER_RETURN_MUST_REMAIN")
    nodes = dict(zip(ids, dag["nodes"]))
    for ident, status in GATES.items():
        need(ident in nodes and nodes[ident].get("current_status") == status, "PREDECESSOR_GATE_CHANGED")
    need(type(nodes["CR_N5_ATOMIC_ISOTOPE_COVERAGE"].get("owner_return_heiii_20261027")) is dict,
         "PRIOR_HEIII_RETURN_REQUIRED")
    need(dag.get("L4_ready") is False and "global_physical_completion" in dag
         and dag["global_physical_completion"] is None, "ORIGINAL_GLOBAL_GATES_CHANGED")
    return index


def validate_baseline(inputs, baseline, dag, dag_pin, identities):
    need(baseline.get("head") == identities["central_parent"]
         and baseline.get("tree") == identities["central_base_tree"]
         and baseline.get("DAG_sha256") == dag_pin["sha256"]
         and type(baseline.get("completed")) is int and baseline["completed"] == 28
         and type(baseline.get("total")) is int and baseline["total"] == 88,
         "FRESH_ROOT_BASELINE_HEAD_TREE_DAG_28_88_REQUIRED")
    qualification, qpin = inputs.pinned(baseline["source_baseline"], "central_qualification")
    need(qualification.get("unit") == UNIT
         and qualification.get("verdict") == "QUALIFIED_CENTRAL_BASELINE_NO_CR_PHYSICS_CHANGE"
         and qualification.get("blocking_findings") == []
         and qualification.get("central_head") == identities["central_parent"]
         and qualification.get("central_tree") == identities["central_base_tree"]
         and qualification.get("dag_sha256") == dag_pin["sha256"]
         and qualification.get("current_central_completed") == 28
         and qualification.get("current_central_total") == 88
         and qualification.get("nodes") == 88 and qualification.get("integration_edges") == 17,
         "ACTUAL_QUALIFIED_CURRENT_CENTRAL_INPUT_REQUIRED")
    authority = qualification["count_authority"]
    need(authority.get("counts_inferred_from_status_strings") is False
         and authority.get("PR236_32_added") is False and authority.get("prior28_preserved") is True,
         "CURRENT_COUNT_MUST_BE_EXPLICIT_NOT_HEURISTIC")
    row = qualification["authoritative_return"]
    observed, apin = inputs.pinned(row, "authoritative_current_count_return")
    need(row.get("revision") == identities["central_parent"]
         and authority.get("revision") == identities["central_parent"]
         and row.get("repo_path") == authority.get("source_file"), "COUNT_AUTHORITY_REVISION_MISMATCH")
    matches = [node for node in dag["nodes"] if type(node.get("status_observation")) is dict
               and CENTRAL_UNIT_PATH + "/" + node["status_observation"].get("source_file", "") == row["repo_path"]
               and node["status_observation"].get("json_pointer") == row["json_pointer"]]
    need(len(matches) == 1 and matches[0]["id"] != TARGET, "ACTUAL_FOREIGN_COUNT_OBSERVATION_REQUIRED")
    need(same(pointer(observed, row["json_pointer"]), matches[0]["status_observation"]["value"]),
         "CURRENT_DAG_AND_ACTUAL_OWNER_RETURN_DIFFER")
    for location in (authority["top_json_pointer"], authority["observation_json_pointer"]):
        counts = pointer(observed, location)
        need(type(counts.get("completed")) is int and counts["completed"] == 28
             and type(counts.get("total")) is int and counts["total"] == 88, "ACTUAL_CURRENT_COUNT_NOT_28_88")
    return {"central_head": identities["central_parent"], "base_tree": identities["central_base_tree"],
            "dag_sha256": dag_pin["sha256"], "completed": 28, "total": 88,
            "historical_completed": 27, "current_completed_total": "28/88", "historical_completed_total": "27/88",
            "historical_27_to_28_cause": "Previously admitted foreign B3h completion; not this CR unit",
            "current_authority_node": matches[0]["id"], "current_authority": row,
            "counts_inferred_from_status_strings": False, "unmerged_PR236_32_of_88_added": False,
            "this_CR_count_effect": 0, "evidence": [qpin, apin]}


def validate_publication(state, identities):
    need(state.get("repo") == REPOSITORY and state.get("branch") == BRANCH
         and state.get("head") == identities["D"], "ACTUAL_FINAL_PUBLICATION_STATE_REQUIRED")
    rows = state.get("stages")
    need(type(rows) is list and [r.get("stage") for r in rows] == STAGES, "TWENTY_ACTUAL_STAGE_RECEIPTS_REQUIRED")
    commits = []
    for ordinal, row in enumerate(rows, 1):
        need(row.get("schema") == "CR_PARENT_EVENT_STAGE_PUBLICATION_V1"
             and row.get("force") is False and row.get("Git_ref_readback") is True
             and row.get("completed_loop_stage") == ordinal and row.get("total_loop_stages") == 20,
             "ACTUAL_EXPECTED_SHA_NONFORCE_STAGE_RECEIPT_REQUIRED")
        commit = hex_value(row.get("commit"), 40)
        hex_value(row.get("tree"), 40)
        parent = hex_value(row.get("expected_parent"), 40)
        if commits:
            need(parent == commits[-1], "ACTUAL_STAGE_PARENT_CHAIN_BROKEN")
        commits.append(commit)
        archive = row["archive"]
        size = integer(archive.get("bytes"), 1)
        hex_value(archive.get("sha256"), 64)
        for provider in ("Dropbox", "Drive"):
            ack = row[provider]
            need(ack.get("ack") is True and ack.get("tier") in ("R2", "R3")
                 and ack.get("bytes") == size and text(ack.get("id"))
                 and int(ack["metadata"]["size"]) == size and ack["metadata"]["id"] == ack["id"],
                 "ACTUAL_DUAL_STAGE_ACK_AND_METADATA_REQUIRED")
    need(len(set(commits)) == 20 and commits[-2] == identities["S"] and commits[-1] == identities["D"]
         and state.get("tree") == rows[-1]["tree"], "S_C09_AND_D_C10_ACTUAL_PUBLICATION_BINDING_REQUIRED")
    return {"R": "10/10", "C": "10/10", "total": "20/20",
            "actual_published_stage_commits": commits, "dual_R2_stage_receipts": 20,
            "canonical_source_dual_R3": True, "automatic_next_node": False}


def check_rows(rows, count, label):
    need(type(rows) is list and len(rows) == integer(count, 1)
         and all(type(row) is dict and row.get("pass") is True for row in rows), label)


def validate_reference_composite(inputs, reference):
    """Validate a saved evidence join only; do not rerun even the four repairs."""
    need(reference.get("schema") == "CR_PARENT_EVENT_INDEPENDENT_COMPOSITE_V1"
         and reference.get("status") == "PASS_SCOPED_INDEPENDENT_REFERENCE_COMPOSITE"
         and reference.get("unit") == UNIT, "ACTUAL_SCOPED_REFERENCE_COMPOSITE_REQUIRED")
    sources = reference.get("source_results", {})
    loaded, pins = {}, []
    for role in ("original_reference", "targeted_recovery", "original_failed_receipt", "original_executed_reference"):
        pin = sources[role]
        absolute_pin = {**pin, "path": str(unit_relative(pin["path"]))}
        raw, actual = inputs.read(absolute_pin["path"], absolute_pin, role)
        pins.append(actual)
        if role != "original_executed_reference":
            loaded[role] = decode(raw)
    old, new, receipt = (loaded[key] for key in
                         ("original_reference", "targeted_recovery", "original_failed_receipt"))
    need(old.get("schema") == "CR_PARENT_EVENT_INDEPENDENT_REFERENCE_V1" and old.get("unit") == UNIT
         and old.get("status") == "FAILED" and old.get("production_imports") == []
         and old.get("old_science_replays") == 0, "ORIGINAL_FAILED_REFERENCE_MUST_BE_PRESERVED")
    need(new.get("schema") == "CR_PARENT_EVENT_INDEPENDENT_TARGETED_RECOVERY_V1" and new.get("unit") == UNIT
         and new.get("status") == "PASS_SCOPED_EXACT_HALF_RECOVERY" and new.get("production_imports") == []
         and new.get("old_successful_checks_reexecuted") == 0 and new.get("tolerance_changed") is False
         and new.get("absolute_floor_added") is False and new.get("original_failure_erased") is False,
         "ACTUAL_FOUR_ONLY_UNRELAXED_ORACLE_RECOVERY_REQUIRED")
    need(same(new.get("original_reference"), sources["original_reference"])
         and same(new.get("original_failed_receipt"), sources["original_failed_receipt"])
         and same(new.get("original_executed_reference"), sources["original_executed_reference"])
         and same(old.get("primary"), reference.get("primary")) and same(new.get("primary"), old.get("primary")),
         "COMPOSITE_SOURCE_OR_PRIMARY_BINDING_MISMATCH")
    need(receipt.get("unit") == UNIT and receipt.get("status") == "failed"
         and receipt.get("terminal_debit") is True and receipt.get("cpu_accounting_complete") is True,
         "ORIGINAL_FAILED_CPU_RECEIPT_REQUIRED")
    targets = {"prefixes.0.fixture.2.s_m3", "prefixes.2.fixture.2.s_m3",
               "prefixes.3.fixture.2.s_m3", "observation_bins.0.fixture.2.s_m3"}
    old_rows, new_rows = old["checks"], new["checks"]
    old_failed = [row for row in old_rows if row.get("pass") is False]
    need(len(old_rows) == 3450 and len({r["id"] for r in old_rows}) == 3450
         and sum(r.get("pass") is True for r in old_rows) == 3446
         and {r["id"] for r in old_failed} == targets
         and len(new_rows) == 4 and {r["id"] for r in new_rows} == targets,
         "EXACT_ORIGINAL_3446_PLUS_TARGETED_FOUR_INVENTORY_REQUIRED")
    for document, executed, passed, failed_count in ((old, 3450, 3446, 4), (new, 4, 4, 0)):
        acc = document.get("acceptance", {})
        need(all(type(acc.get(key)) is int and acc[key] == value for key, value in
                 (("executed", executed), ("passed", passed), ("failed", failed_count), ("inherited_checks_added", 0))),
             "COMPOSITE_SOURCE_ACTUAL_EVALUATION_COUNTS_CHANGED")
    need(type(new.get("selected_check_ids")) is list and len(new["selected_check_ids"]) == 4
         and set(new["selected_check_ids"]) == targets, "ONLY_FOUR_NAMED_REPAIRS_MAY_BE_SELECTED")
    check_rows(new_rows, 4, "FOUR_ACTUAL_RECOVERY_CHECKS_REQUIRED")
    for row in new_rows:
        original = next(item for item in old_failed if item["id"] == row["id"])
        need(row.get("expected") == "0" and row.get("observed") == "0"
             and row.get("tolerance") == "1E-11" and row.get("zero_rule") == "exact when scale is zero"
             and same(row.get("exact_expected_fraction"), {"numerator": 0, "denominator": 1})
             and same(row.get("superseded_original_oracle_failure"), original),
             "EXACT_ZERO_REPAIR_OR_ORIGINAL_FAILURE_CHANGED")
    replacement = {row["id"]: row for row in new_rows}
    expected = [replacement.get(row["id"], row) for row in old_rows]
    need(same(reference.get("checks"), expected)
         and same(reference.get("superseded_oracle_failures"), old_failed),
         "COMPOSITE_MUST_COPY_3446_ORIGINAL_PASS_ROWS_AND_ONLY_REPLACE_FOUR")
    acceptance = reference["acceptance"]
    for key, value in (("unique_checks", 3450), ("passed", 3450), ("failed", 0),
                       ("actual_evaluations", 3454), ("reused_passed_checks", 3446),
                       ("newly_evaluated_checks", 4), ("previous_failed_evaluations", 4),
                       ("inherited_checks_added", 0)):
        need(type(acceptance.get(key)) is int and acceptance[key] == value, "COMPOSITE_ACCOUNTING_MISMATCH:" + key)
    need("executed" not in acceptance and reference.get("full_reference_rerun") is False
         and reference.get("old_successful_checks_reexecuted") == 0
         and reference.get("original_failure_erased") is False
         and reference.get("fit_or_Q8_or_old_source_or_RR_replay") == 0,
         "COMPOSITE_CANNOT_CLAIM_A_FULL_RERUN")
    return pins


def validate_results(primary, controls, reference, primary_pin, input_manifest):
    need(primary.get("unit") == UNIT and primary.get("schema") == "CR_PARENT_EVENT_RESULT_V1"
         and primary.get("status") == "PASS_SCOPED_PARENT_EVENT_PARTIAL_RETURN", "ACTUAL_SCOPED_PRIMARY_REQUIRED")
    accepted = primary["acceptance"]
    need(accepted.get("internal_pass") is True
         and accepted.get("passed_checks") == accepted.get("total_checks")
         and accepted.get("physical_error_certificate") is False
         and accepted.get("old_reference_or_controls_added_to_new_count") is False, "PRIMARY_ACCEPTANCE_SCOPE_MISMATCH")
    check_rows(accepted.get("checks"), accepted.get("total_checks"), "ACTUAL_PRIMARY_CHECKS_REQUIRED")
    scope = primary["scope"]
    need(scope.get("birth_tag") == "direct_0p1_10" and scope.get("nb_m3") == "8750/47"
         and scope.get("T_K") == "100" and scope.get("proper_clock") == "proper_s"
         and scope.get("proper_volume_mode") == "fixed"
         and scope.get("frame") == "prescribed_gas_rest_frame_scalar"
         and scope.get("same_state_inventory_id") == "CR_LOW_BIRTH_100K_CONDITIONAL_H1_HE4_FIXED_INVENTORY_V1"
         and scope.get("isotope_mapping") == "CONDITIONAL_ELEMENTAL_H_TO_H1_HE_TO_HE4"
         and scope.get("nH_total_m3") == "140" and scope.get("nHe_total_m3") == "1085/94"
         and scope.get("native_birth_support_eV") == [Decimal("0.1"), Decimal("10")]
         and scope.get("identification_support_eV") == [Decimal(0), Decimal(1000)]
         and scope.get("history_s") == [Decimal(0), Decimal(10000000000)],
         "EXACT_SELECTED_SAME_STATE_SCOPE_REQUIRED")
    for key in ("history_outside", "absolute_proper_volume_m3", "actual_full_physical_native25",
                "actual_external_work", "global_physical_completion", "global_physical_error",
                "global_budget_remaining", "currency"):
        need(key in scope and scope[key] is None, "PRIMARY_NULL_CEILING_CHANGED:" + key)
    for key in ("foreign_consumer_activation", "original_RR_chain_replay", "full9600_operator_recovery",
                "full9600_G_recovery", "physical_heating_complete"):
        need(scope.get(key) is False, "PRIMARY_FALSE_CEILING_CHANGED:" + key)
    for key in ("old_source_or_RR_replay", "old_science_replays"):
        need(type(scope.get(key)) is int and scope[key] == 0, "OLD_SCIENCE_REPLAY_REFUSED")
    need(primary["input_identity"]["source_record"]["sha256"] == SOURCE_SHA
         and primary["input_identity"].get("input_manifest_sha256") == INPUT_SHA
         and same(primary["input_identity"].get("all_input_pins"), input_manifest["files"]),
         "ORIGINAL_SOURCE_RECORD_OR_MANIFEST_CHANGED")
    unresolved = primary.get("unresolved_inputs")
    required_nulls = {"actual_s", "actual_p", "actual_d", "actual_HeII_residual_state", "partner_energy",
                      "partner_history", "partner_pool", "partner_native_response", "actual_proton_work",
                      "actual_full_physical_native25", "full9600_native25", "absolute_worldtube_totals"}
    need(type(unresolved) is dict and required_nulls <= set(unresolved)
         and all(unresolved[key] is None for key in required_nulls), "UNIDENTIFIED_ACTUAL_INPUT_PROMOTED")
    for name, role in (("prefixes", "nonadditive_cumulative_prefix"), ("observation_bins", "disjoint_observation_bin")):
        rows = primary.get(name)
        need(type(rows) is list and len(rows) == 4, "FOUR_PREFIXES_AND_FOUR_BINS_REQUIRED")
        for index, row in enumerate(rows):
            need(row.get("index") == index and row.get("role") == role
                 and all(key in row and row[key] is None for key in
                         ("actual_full_native25", "actual_external_work", "actual_temperature_point"))
                 and row.get("physical_heating_complete") is False, "WINDOW_ROLE_OR_PHYSICAL_CEILING_CHANGED")
    registry = primary["adoption_registry"]
    need(registry.get("scope") == "partial_bookkeeping_only_no_full_consumer_activation"
         and registry.get("prefixes_additively_adopted") is False
         and registry.get("aggregate_includes_prior_RR") is True
         and registry.get("full_consumer_activation") is False
         and registry.get("all_response_components_once") is True
         and registry.get("claim_count") == len(registry.get("claims", [])), "EVENT_OWNERSHIP_SCOPE_CHANGED")
    control_rows = []
    for item in controls:
        need(item.get("unit") == UNIT and item.get("schema") == "CR_PARENT_EVENT_CONTROLS_V1"
             and item.get("status") == "PASS" and item.get("passed_checks") == item.get("total_checks")
             and item.get("old_science_replay") == 0, "ACTUAL_ACCEPTED_CURRENT_CONTROL_RESULT_REQUIRED")
        check_rows(item.get("checks"), item.get("total_checks"), "ACTUAL_CONTROL_CHECKS_REQUIRED")
        control_rows.append({"selection": item.get("selection"), "selected_names": item.get("selected_names"),
                             "passed": item["passed_checks"], "executed": item["total_checks"]})
    is_composite = reference.get("schema") == "CR_PARENT_EVENT_INDEPENDENT_COMPOSITE_V1"
    expected_schema = "CR_PARENT_EVENT_INDEPENDENT_COMPOSITE_V1" if is_composite else "CR_PARENT_EVENT_INDEPENDENT_REFERENCE_V1"
    expected_status = "PASS_SCOPED_INDEPENDENT_REFERENCE_COMPOSITE" if is_composite else "PASS_SCOPED_INDEPENDENT_REFERENCE"
    need(reference.get("unit") == UNIT and reference.get("schema") == expected_schema
         and reference.get("status") == expected_status
         and reference.get("production_imports") == [] and reference.get("old_science_replays") == 0
         and reference.get("inherited_checks_added") == 0, "ACTUAL_INDEPENDENT_REFERENCE_REQUIRED")
    acc = reference["acceptance"]
    count_key = "unique_checks" if is_composite else "executed"
    need(acc.get("failed") == 0 and acc.get("passed") == acc.get(count_key)
         and acc.get("inherited_checks_added") == 0, "REFERENCE_ACCEPTANCE_FAILED")
    check_rows(reference.get("checks"), acc.get(count_key), "ACTUAL_REFERENCE_CHECKS_REQUIRED")
    checked_primary = reference.get("primary", {})
    need(str(unit_relative(checked_primary.get("path"))) == primary_pin["path"]
         and all(checked_primary.get(k) == primary_pin[k] for k in ("bytes", "sha256")),
         "REFERENCE_MUST_HAVE_CHECKED_THIS_EXACT_PRIMARY_FILE")
    return {"primary_checks_passed": accepted["passed_checks"],
            "accepted_control_results": control_rows,
            "accepted_control_evaluations": sum(row["passed"] for row in control_rows),
            "independent_checks_passed": acc["passed"], "independent_categories": acc.get("by_category"),
            "independent_actual_evaluations": acc["actual_evaluations"] if is_composite else acc["executed"],
            "independent_reused_passed_checks": acc["reused_passed_checks"] if is_composite else 0,
            "independent_newly_evaluated_checks": acc["newly_evaluated_checks"] if is_composite else acc["executed"],
            "independent_previous_failed_evaluations": acc["previous_failed_evaluations"] if is_composite else 0,
            "independent_evidence_form": "accepted composite with original FAILED preserved" if is_composite else "one saved full run",
            "old_checks_added": 0, "primary_worker_independent_status_as_saved": accepted.get("independent_reference"),
            "final_reference_status": reference["status"], "all_scoped_scientific_checks_pass": True}


def validate_budget(inputs, budget, ledger, preparation, closeout):
    for item in (budget, ledger, preparation, closeout):
        need(item.get("unit") == UNIT, "FOREIGN_BUDGET_REFUSED")
    need(budget.get("schema") == "CR_PARENT_EVENT_EXECUTION_BUDGET_V1"
         and ledger.get("schema") == "CR_PARENT_EVENT_EXECUTION_LEDGER_V1"
         and preparation.get("schema") == "CR_PARENT_EVENT_PREPARATION_LEDGER_V1"
         and closeout.get("schema") == "CR_PARENT_EVENT_BUDGET_CLOSEOUT_V1", "CURRENT_BUDGET_SCHEMAS_REQUIRED")
    need(number(budget.get("local_science_cpu_cap_s")) == 40 and number(ledger.get("cap_s")) == 40
         and number(closeout.get("cap_s")) == 40 and closeout.get("closed") is True,
         "CLOSED_SEPARATE_40_CPU_BUDGET_REQUIRED")
    need(budget.get("historical_allowance_transferred") is False
         and budget.get("parallel_project_budget_transferred") is False
         and budget.get("preventive_aggregate_kernel_hard_cap_proof") is False
         and ledger.get("historical_transferred") is False
         and ledger.get("parallel_project_budget_transferred") is False
         and "global_remaining" in ledger and ledger["global_remaining"] is None
         and "global_budget_remaining" in closeout and closeout["global_budget_remaining"] is None
         and ledger.get("old_science_replays") == 0 and closeout.get("old_science_replays") == 0,
         "NO_CARRY_GLOBAL_NULL_AND_PROOF_CEILINGS_REQUIRED")
    prep_path = unit_relative(budget["preparation_cost_manifest"])
    prep_raw, _ = inputs.read(prep_path)
    need(sha(prep_raw) == budget.get("preparation_cost_manifest_sha256")
         and same(decode(prep_raw), preparation), "PREPARATION_BUDGET_PIN_MISMATCH")
    groups = {}
    all_preparation_rows = preparation.get("all_cumulative_records")
    need(type(all_preparation_rows) is list and all_preparation_rows, "ACTUAL_PREPARATION_HISTORY_REQUIRED")
    for row in all_preparation_rows:
        actual, _ = inputs.pinned({**row, "path": str(unit_relative(row["path"]))}, "preparation_receipt")
        need(actual.get("unit") == UNIT and actual.get("attempt") == row.get("attempt")
             and actual.get("status") in ("failed", "completed"), "UNKNOWN_OR_FOREIGN_PREPARATION_DEBIT")
        for key in ("charged_preparation_CPU_s", "measured_preparation_CPU_s", "conservative_tail_CPU_s"):
            close(actual.get(key), row.get(key), "PREPARATION_RECEIPT_COST_MISMATCH")
            need(number(row[key]) >= 0, "NEGATIVE_PREPARATION_COST")
        close(row["charged_preparation_CPU_s"], number(row["measured_preparation_CPU_s"])
              + number(row["conservative_tail_CPU_s"]), "PREPARATION_MEASURED_TAIL_SUM_MISMATCH")
        need(actual.get("status") == row.get("status"), "PREPARATION_FAILURE_STATUS_CHANGED")
        groups.setdefault(text(row["attempt"]), []).append(row)
    maxima = [max(rows, key=lambda r: (number(r["charged_preparation_CPU_s"]), integer(r["debit_sequence"])))
              for _, rows in sorted(groups.items())]
    need(same(sorted(preparation.get("records", []), key=lambda r: r["attempt"]), maxima),
         "PREPARATION_MUST_USE_MAX_CUMULATIVE_PER_ATTEMPT")
    prep_charged = sum((number(r["charged_preparation_CPU_s"]) for r in maxima), Decimal(0))
    prep_measured = sum((number(r["measured_preparation_CPU_s"]) for r in maxima), Decimal(0))
    prep_tail = sum((number(r["conservative_tail_CPU_s"]) for r in maxima), Decimal(0))
    for field, value in (("charged_total_CPU_s", prep_charged), ("measured_total_CPU_s", prep_measured),
                         ("conservative_tail_total_CPU_s", prep_tail)):
        close(preparation.get(field), value, "PREPARATION_TOTAL_MISMATCH")
    close(ledger.get("baseline_preparation_cpu_s"), prep_charged, "LEDGER_PREPARATION_BASELINE_MISMATCH")
    attempts = ledger.get("attempts")
    need(type(attempts) is list and attempts, "ACTUAL_ATTEMPT_LEDGER_REQUIRED")
    ids = [text(row.get("attempt_id")) for row in attempts]
    need(len(set(ids)) == len(ids), "DUPLICATE_CANONICAL_ATTEMPT")
    immutable = {}
    debit_dir = UNIT_ROOT / "evidence/ATTEMPT_DEBITS"
    debit_names = sorted(str(p) for p in debit_dir.glob("*.json"))
    need(debit_names, "IMMUTABLE_ATTEMPT_DEBITS_REQUIRED")
    for name in debit_names:
        raw, _ = inputs.read(name, role="immutable_attempt_debit")
        item = decode(raw)
        need(item.get("unit") == UNIT and item.get("terminal_debit") is True
             and item.get("cpu_accounting_complete") is True and item.get("status") in ("failed", "completed"),
             "UNKNOWN_NO_ACK_OR_NONTERMINAL_DEBIT_REFUSED")
        immutable.setdefault(text(item.get("attempt_id")), []).append(item)
    need(set(immutable) == set(ids), "LEDGER_OMITS_OR_INVENTS_ACTUAL_ATTEMPT")
    worker = coordinator = tails = charged_attempts = Decimal(0)
    fields = ("worker_cpu_s", "coordinator_cpu_through_receipt_s", "receipt_tail_reserve_s", "charged_cpu_s")
    for row in attempts:
        need(row.get("unit") == UNIT and row.get("terminal_debit") is True
             and row.get("cpu_accounting_complete") is True, "CANONICAL_ATTEMPT_UNRESOLVED")
        choices = immutable[row["attempt_id"]]
        maximum = max(number(item["charged_cpu_s"]) for item in choices)
        matches = [item for item in choices if number(item["charged_cpu_s"]) == maximum
                   and all(same(item.get(key), row.get(key)) for key in fields + ("status", "run_id"))]
        need(matches, "CANONICAL_ATTEMPT_IS_NOT_ACTUAL_MAX_CUMULATIVE_DEBIT")
        costs = [number(row[key]) for key in fields]
        need(all(value >= 0 for value in costs), "NEGATIVE_ATTEMPT_COST")
        close(costs[3], sum(costs[:3], Decimal(0)), "ATTEMPT_MEASURED_TAIL_SUM_MISMATCH")
        worker += costs[0]
        coordinator += costs[1]
        tails += costs[2]
        charged_attempts += costs[3]
        need(row.get("aggregate_polling_is_kernel_hard_cap_proof") is False, "HARD_CAP_PROOF_PROMOTED")
    # Unit-local reservations must be acknowledged by an actual terminal debit.
    reservation_names = sorted(str(p) for p in (UNIT_ROOT / "runs").glob("*/RESERVATION.json"))
    for name in reservation_names:
        raw, _ = inputs.read(name, role="actual_run_reservation")
        reservation = decode(raw)
        need(reservation.get("unit") == UNIT and reservation.get("attempt_id") in immutable,
             "UNACKNOWLEDGED_UNIT_RESERVATION_REFUSED")
    charged = prep_charged + charged_attempts
    measured = prep_measured + worker + coordinator
    conservative = prep_tail + tails
    need(0 <= charged <= 40, "UNIT_CPU_CAP_EXCEEDED")
    for field, value in (("charged_cpu_s", charged), ("measured_total_cpu_s", measured),
                         ("conservative_tail_total_cpu_s", conservative),
                         ("preparation_measured_cpu_s", prep_measured),
                         ("preparation_conservative_tail_cpu_s", prep_tail),
                         ("worker_measured_cpu_s", worker), ("coordinator_measured_cpu_s", coordinator),
                         ("remaining_not_transferable", Decimal(40) - charged)):
        close(ledger.get(field), value, "EXECUTION_LEDGER_AGGREGATE_MISMATCH:" + field)
    for field, value in (("charged_cpu_s", charged), ("measured_cpu_s", measured),
                         ("conservative_tail_cpu_s", conservative)):
        close(closeout.get(field), value, "FINAL_BUDGET_CLOSEOUT_MISMATCH")
    failed_preparation = [r["path"] for r in maxima if r["status"] != "completed"]
    failed_attempts = [r["attempt_id"] for r in attempts if r["status"] != "completed"]
    all_pass = not failed_preparation and not failed_attempts
    need(ledger.get("all_runtime_attempts_pass") is all_pass
         and closeout.get("all_runtime_attempts_pass") is all_pass
         and ledger.get("all_preparation_attempts_pass") is (not failed_preparation)
         and ledger.get("all_worker_and_preworker_attempts_pass") is (not failed_attempts)
         and preparation.get("all_preparation_attempts_completed") is (not failed_preparation),
         "FAILED_ATTEMPTS_CANNOT_BECOME_ALL_PASS")
    return {"new_unit_cap_s": 40, "charged_cpu_s": ledger["charged_cpu_s"],
            "measured_cpu_s": closeout["measured_cpu_s"],
            "conservative_tail_cpu_s": closeout["conservative_tail_cpu_s"],
            "remaining_not_transferable": ledger["remaining_not_transferable"],
            "preparation_charged_cpu_s": preparation["charged_total_CPU_s"],
            "preparation_measured_cpu_s": preparation["measured_total_CPU_s"],
            "preparation_conservative_tail_cpu_s": preparation["conservative_tail_total_CPU_s"],
            "preserved_failed_preparation_receipt_paths": failed_preparation,
            "preserved_failed_attempt_ids": failed_attempts, "all_runtime_attempts_pass": all_pass,
            "old_or_parallel_budget_transferred": False, "unused_allowance_auto_carried_to_next_unit": False,
            "old_science_replays": 0, "global_budget_remaining": None,
            "hard_preventive_aggregate_cap_proof": False,
            "deduplication": "one maximum cumulative immutable debit per attempt; preparation separately reconciled",
            "immutable_debit_inventory": debit_names, "reservation_inventory": reservation_names}


def validate_source(source, r3, identities, source_pin):
    need(source.get("schema") == "CR_PARENT_EVENT_ARCHIVE_RECEIPT_V1" and source.get("unit") == UNIT
         and source.get("kind") == "SOURCE" and source.get("source_archive_rebuilt") is False
         and source.get("all_members_SHA256_bytes_CRC_verified") is True and source.get("ZIP_testzip_PASS") is True,
         "ACTUAL_SEALED_SOURCE_RECEIPT_REQUIRED")
    identity = source["identity"]
    need(identity.get("unit") == UNIT and identity.get("unit_path") == UNIT_PATH
         and identity.get("repository") == REPOSITORY and identity.get("S") == identities["S"]
         and identity.get("D") is None and identity.get("M") is None
         and identity.get("actual_published_loop_stages") == 19 and identity.get("source_input_payloads") == 17,
         "CANONICAL_SOURCE_MUST_BIND_ACTUAL_S_ONLY")
    archive = source["archive"]
    need(archive.get("name") == "BASS_CR_PARENT_EVENT_SOURCE_20261028_" + identities["S"][:12] + ".zip"
         and integer(archive.get("bytes"), 1) and integer(archive.get("payloads"), 1)
         and archive.get("members") == archive["payloads"] + 1, "CANONICAL_SOURCE_ARCHIVE_IDENTITY_REQUIRED")
    hex_value(archive.get("sha256"), 64)
    hex_value(archive.get("manifest_sha256"), 64)
    need(r3.get("schema") == "CR_PARENT_EVENT_DUAL_RAW_R3_V1" and r3.get("unit") == UNIT
         and r3.get("both_original_full_GET_and_all_members_PASS") is True
         and r3.get("source_archive_rebuilt") is False and r3.get("old_science_replays") == 0,
         "ACTUAL_DUAL_SOURCE_R3_REQUIRED")
    for key in ("name", "bytes", "sha256", "members", "payloads", "manifest_sha256"):
        need(same(r3["archive"].get(key), archive.get(key)), "SOURCE_R3_ARCHIVE_MISMATCH")
    need(all(r3["archive_receipt_pin"].get(k) == source_pin[k] for k in ("path", "bytes", "sha256")),
         "R3_MUST_PIN_ACTUAL_SOURCE_RECEIPT")
    providers = r3.get("providers")
    need(type(providers) is list and [r.get("provider") for r in providers] == ["Dropbox", "Drive"],
         "EXACT_TWO_ORIGINAL_PROVIDERS_REQUIRED")
    public = []
    for row in providers:
        text(row.get("id"))
        need(row.get("status") == "PASS" and row.get("verification_tier") == "R3"
             and row.get("HTTP_status") == 200 and row.get("raw_HTTP_method") == "GET"
             and row.get("HEAD_or_Range_used") is False and row.get("downloaded_original_file") is True
             and row.get("all_payload_sha256_and_CRC_PASS") is True
             and row.get("downloaded_bytes") == archive["bytes"] and row.get("archive_sha256") == archive["sha256"]
             and row.get("archive_members") == archive["members"] and row.get("manifest_payloads") == archive["payloads"]
             and row.get("manifest_sha256") == archive["manifest_sha256"], "ACTUAL_FULL_GET_HASH_CRC_REQUIRED")
        public.append({key: row[key] for key in ("provider", "id", "status", "verification_tier", "HTTP_status",
                                               "downloaded_bytes", "archive_sha256", "archive_members", "manifest_payloads")})
    return {"science_commit_S": identities["S"], "canonical_same_immutable_zip": True,
            "source_rebuilt_after_seal": False,
            "archive": {key: archive[key] for key in ("name", "bytes", "sha256", "members", "payloads", "manifest_sha256")},
            "providers": public, "R3_scope": "Recorded actual provider original full GET and every payload hash/CRC",
            "new_backup_download_by_this_builder": False}


def contains_pin(rows, expected, role=None):
    matches = [row for row in rows if row.get("path") == expected["path"]
               and (role is None or row.get("role") == role)]
    return len(matches) == 1 and all(matches[0].get(k) == expected[k] for k in ("path", "bytes", "sha256"))


def validate_admission(review, admission, pins, identities, reference_source_pins):
    need(review.get("schema") == "CR_PARENT_EVENT_C09_INDEPENDENT_REVIEW_V1" and review.get("unit") == UNIT
         and review.get("decision") == "PASS_SCOPED_PARTIAL_RETURN"
         and type(review.get("blocking_findings")) is int and review["blocking_findings"] == 0,
         "ACTUAL_DIFFERENT_REVIEWER_C9_ACCEPTANCE_REQUIRED")
    reviewed = review.get("reviewed_files")
    need(type(reviewed) is list and len({r["path"] for r in reviewed}) == len(reviewed), "UNIQUE_C9_INPUT_PINS_REQUIRED")
    for role in ("primary", "reference", "controls"):
        for pin in pins[role]:
            need(contains_pin(reviewed, pin), "C9_DOES_NOT_BIND_ACTUAL_RESULT:" + role)
    for pin in reference_source_pins:
        if pin["role"] in ("original_reference", "targeted_recovery"):
            need(contains_pin(reviewed, pin), "C9_MUST_BIND_BOTH_COMPOSITE_SOURCE_RESULTS")
    need(admission.get("schema") == "CR_PARENT_EVENT_FINAL_ADMISSION_V1" and admission.get("unit") == UNIT
         and admission.get("decision") == "ADMITTED_SCOPED_PARTIAL_RETURN" and admission.get("S") == identities["S"]
         and admission.get("automatic_next_node") is False and admission.get("L4") is False
         and "global_physical_completion" in admission and admission["global_physical_completion"] is None
         and admission.get("physical_heating_complete") is False, "ACTUAL_FINAL_ROOT_ADMISSION_REQUIRED")
    admitted = admission.get("reviewed_files")
    need(type(admitted) is list and len({r["path"] for r in admitted}) == len(admitted), "UNIQUE_ADMISSION_INPUT_PINS_REQUIRED")
    for role in ("report", "budget", "primary", "controls", "reference", "C9", "source_R3"):
        for pin in pins[role]:
            need(contains_pin(admitted, pin, role), "ROOT_ADMISSION_DOES_NOT_BIND_ACTUAL_EVIDENCE:" + role)


def preservation(before, after, index, link):
    restored = deepcopy(after)
    need(same(restored["nodes"][index].pop(LINK), link) and same(restored, before),
         "REMOVING_SINGLE_LINK_MUST_RESTORE_ENTIRE_ORIGINAL_DAG")
    other_before = [n for i, n in enumerate(before["nodes"]) if i != index]
    other_after = [n for i, n in enumerate(after["nodes"]) if i != index]
    top_before = {k: v for k, v in before.items() if k != "nodes"}
    top_after = {k: v for k, v in after.items() if k != "nodes"}
    need(same(other_before, other_after) and same(top_before, top_after), "OTHER_OWNER_OR_TOP_METADATA_CHANGED")
    prior = {key: semantic_sha(value) for key, value in before["nodes"][index].items() if key.startswith("owner_return_")}
    special = {node["id"]: semantic_sha(node) for node in before["nodes"]
               if node["id"] in set(GATES) | {"B3h-native-finite-absorption"}}
    return {"removed_link_restores_entire_DAG_exact_semantic_identity": True,
            "input_DAG_semantic_sha256": semantic_sha(before), "removed_link_DAG_semantic_sha256": semantic_sha(restored),
            "target_existing_fields_unchanged": True, "target_original_contract_unchanged": True,
            "target_current_status_before": before["nodes"][index]["current_status"],
            "target_current_status_after": after["nodes"][index]["current_status"],
            "other87nodes_unchanged": True, "other87nodes_semantic_sha256": semantic_sha(other_before),
            "all_non_node_top_metadata_unchanged": True, "non_node_top_metadata_semantic_sha256": semantic_sha(top_before),
            "all17edges_unchanged": True, "integration_edges_sha256": semantic_sha(before["integration_edges"]),
            "all_prior_target_owner_return_fields_unchanged": True, "prior_target_owner_return_sha256": prior,
            "N5_entire_node_unchanged": True, "B3h_entire_current_node_unchanged": True,
            "preserved_special_node_sha256": special, "original_nodes": 88, "original_integration_edges": 17,
            "historical_declared_deliverable_count": 27, "preserved_declared_deliverable_count": 28, "new_count_effect": 0}


def write_new(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--proof-file", required=True)
    args = parser.parse_args(argv)
    inputs = Inputs()
    raw, input_pin = inputs.read(absolute(args.input), role="root_final_build_input")
    need(sha(raw) == hex_value(args.input_sha256, 64), "ROOT_BUILD_INPUT_PIN_MISMATCH")
    config = decode(raw)
    need(config.get("schema") == "CR_PARENT_EVENT_CENTRAL_BUILD_INPUT_V1" and config.get("unit") == UNIT,
         "CURRENT_UNIT_ROOT_FINAL_BUILD_INPUT_REQUIRED")
    identities = config.get("identities")
    need(type(identities) is dict and set(identities) == {"S", "D", "central_parent", "central_base_tree"},
         "EXACT_FOUR_ACTUAL_COMMIT_IDENTITIES_REQUIRED")
    for value in identities.values():
        hex_value(value, 40)
    need(identities["S"] != identities["D"], "ACTUAL_DISTINCT_S_D_REQUIRED")
    need(type(config.get("files")) is dict and set(config["files"]) == REQUIRED_FILES,
         "EXACT_REQUIRED_ACTUAL_EVIDENCE_ROLES_REQUIRED")
    data, pins = {}, {}
    for role, spec in config["files"].items():
        specs = spec if role == "controls" else [spec]
        need(type(specs) is list and specs, "NONEMPTY_ACTUAL_CONTROL_RESULT_LIST_REQUIRED")
        values, pinrows = [], []
        for pin in specs:
            if role == "report":
                report_raw, actual = inputs.read(pin["path"], pin, role)
                need(UNIT in report_raw.decode("utf-8"), "FINAL_REPORT_MUST_NAME_THIS_UNIT")
                value = None
            else:
                value, actual = inputs.pinned(pin, role)
            values.append(value)
            pinrows.append(actual)
        need(len({p["path"] for p in pinrows}) == len(pinrows), "DUPLICATE_EVIDENCE_FILE")
        data[role] = values if role == "controls" else values[0]
        pins[role] = pinrows
    need(pins["contract"][0]["sha256"] == CONTRACT_SHA and pins["input_manifest"][0]["sha256"] == INPUT_SHA,
         "FROZEN_CONTRACT_OR_INPUT_MANIFEST_CHANGED")
    need(len(data["input_manifest"].get("files", [])) == 17, "SEVENTEEN_PINNED_ORIGINAL_INPUTS_REQUIRED")
    index = validate_dag(data["dag"])
    count = validate_baseline(inputs, data["central_baseline"], data["dag"], pins["dag"][0], identities)
    workflow = validate_publication(data["publication_state"], identities)
    reference_source_pins = []
    if data["reference"].get("schema") == "CR_PARENT_EVENT_INDEPENDENT_COMPOSITE_V1":
        reference_source_pins = validate_reference_composite(inputs, data["reference"])
    verification = validate_results(data["primary"], data["controls"], data["reference"],
                                    pins["primary"][0], data["input_manifest"])
    with localcontext() as context:
        context.prec = 80  # metadata debit addition only, no scientific calculation
        execution = validate_budget(inputs, data["execution_budget"], data["execution_ledger"],
                                    data["preparation_ledger"], data["budget"])
    archive = validate_source(data["source_archive"], data["source_R3"], identities, pins["source_archive"][0])
    validate_admission(data["C9"], data["admission"], pins, identities, reference_source_pins)
    primary = data["primary"]
    evidence = [row for role in sorted(pins) for row in pins[role]] + reference_source_pins
    owner_return = {
        "schema": "CR_PARENT_EVENT_NATIVE25_OWNER_RETURN_V1", "unit_id": UNIT, "unit_path": UNIT_PATH,
        "owner_repository": REPOSITORY, "pull_request": "https://github.com/" + REPOSITORY + "/pull/111",
        "parent_node": TARGET, "science_commit_S": identities["S"], "documents_commit_D": identities["D"],
        "central_base_sha": identities["central_parent"], "central_expected_parent": identities["central_parent"],
        "central_base_tree": identities["central_base_tree"], "central_commit_M": None,
        "original_DAG": {"nodes": 88, "integration_edges": 17, "declared_deliverable_count": 28, "new_count_effect": 0},
        "original_central_completed_total": "28/88", "historical_original_central_completed_total": "27/88",
        "central_count_baseline_sha256": pins["central_baseline"][0]["sha256"],
        "central_count_authority": count, "original_node_status_changed": False,
        "unmerged_PR236_32_of_88_added": False,
        "scope_child": {"id": UNIT, "parent_node": TARGET, "completed": 1, "total": 1,
                        "original_central_count_effect": 0, "scope": "admitted partial parent-event bookkeeping only"},
        "workflow": workflow, "scientific_scope": primary["scope"],
        "actual_input_identity": primary["input_identity"],
        "coefficient_identification": {key: primary["coefficient_identification"][key] for key in
             ("theta_order", "theta_decimal", "rcond_inf_decimal", "sensitivity_decimal", "status")},
        "identified_target_totals": primary["projection_validation"]["target_totals"],
        "representation": {"recovered_coefficients": "MODEL_IDENTIFIED, not original saved coefficient bytes",
            "canonical_source_record_unchanged": True, "source_record_sha256": SOURCE_SHA,
            "selected_birth_tag": "direct_0p1_10", "cumulative_prefixes": 4, "disjoint_observation_bins": 4,
            "He_marginal_constraint": "s + p + 2*d = N_selected_He; p is an unresolved outside partner",
            "actual_He_branch_point": None, "conditional_fixtures_are_actual_measurements": False,
            "default_cutoff": "retained separate selected nonthermal component",
            "caloric_endpoint_update": "explicit conditional fixture only; no physical-heating completion",
            "source_binding_convention_residual": "separate atomic-energy sidecar; not heat or w_ext",
            "retained_photons": "exact saved separate photon port; no spectrum/history reconstruction",
            "actual_proton_debit": None, "actual_full_native25": None},
        "unresolved_inputs": primary["unresolved_inputs"], "event_ownership": {key: primary["adoption_registry"][key]
            for key in ("scope", "claim_count", "prefixes_additively_adopted", "aggregate_includes_prior_RR",
                        "full_consumer_activation", "all_response_components_once")},
        "verification": {**verification, "all_runtime_attempts_pass": execution["all_runtime_attempts_pass"]},
        "review_decision": data["C9"]["decision"], "root_admission": data["admission"]["decision"],
        "execution": execution, "canonical_source_archive": archive,
        "source_R3_receipt_sha256": pins["source_R3"][0]["sha256"],
        "source_evidence": evidence,
        "gates": {"N4": "PARTIAL_OPEN", "N5": "PARTIAL_OPEN", "N6": "PREDECESSOR_GATED",
                  "N7": "PREDECESSOR_GATED", "L4_ready": False, "global_physical_completion": None,
                  "global_physical_error": None, "global_budget_remaining": None, "global_currency": None,
                  "physical_heating_complete": False, "automatic_next_node": False},
        "limitations": {"arithmetic_interval_certificate": False, "physical_error_certificate": False,
                        "continuous_energy_convergence_completed": False, "full9600_operator_recovered": False,
                        "private_conversation_full_search": "UNAVAILABLE",
                        "Drive_inventory": "PARTIAL_NOT_EXHAUSTIVE", "foreign_UNKNOWN_NO_ACK_preserved": True},
        "metadata_assembly": {"builder_author": "/root/theory_review", "scientific_execution": False,
                              "old_science_replays": 0, "metadata_CPU_s": None,
                              "provider_downloads": 0, "git_operations": 0,
                              "final_central_candidate_independent_review": "PENDING_DIFFERENT_REVIEWER"}}
    link = {"unit_id": UNIT, "source_file": RETURN, "json_pointer": "",
            "science_commit_S": identities["S"], "documents_commit_D": identities["D"]}
    candidate = deepcopy(data["dag"])
    candidate["nodes"][index][LINK] = link
    preserved = preservation(data["dag"], candidate, index, link)
    files = {"DAG.json": raw_json(candidate), RETURN: raw_json(owner_return)}
    publishable = [{"path": name, "bytes": len(payload), "sha256": sha(payload)} for name, payload in files.items()]
    output, proof_path = absolute(args.output_dir), absolute(args.proof_file)
    allowed = WORKSPACE / "parent_release_closeout"
    need(output.is_relative_to(allowed) and proof_path.is_relative_to(allowed)
         and not proof_path.is_relative_to(output) and not output.exists() and not proof_path.exists(),
         "NEW_EXTERNAL_CANDIDATE_AND_SEPARATE_CREATE_ONLY_PROOF_REQUIRED")
    inputs.recheck()
    need(execution["immutable_debit_inventory"] == sorted(str(p) for p in (UNIT_ROOT / "evidence/ATTEMPT_DEBITS").glob("*.json"))
         and execution["reservation_inventory"] == sorted(str(p) for p in (UNIT_ROOT / "runs").glob("*/RESERVATION.json")),
         "RUNTIME_INVENTORY_CHANGED_DURING_METADATA_BUILD")
    proof = {"schema": "CR_PARENT_EVENT_CENTRAL_BUILD_PROOF_V1", "unit": UNIT,
        "status": "PASS_SCOPED_OFFLINE_METADATA_BUILD", "identities": identities,
        "central_head_supplied_by_root": identities["central_parent"],
        "central_base_tree_supplied_by_root": identities["central_base_tree"],
        "science_commit_S_supplied_by_root": identities["S"], "documents_commit_D_supplied_by_root": identities["D"],
        "target_id": TARGET, "target_index": index, "added_link_key": LINK, "added_link": link,
        "publishable_files": publishable, "validated_central_count_baseline": count, "preservation": preserved,
        "input_manifest": input_pin, "inputs": list(inputs.seen.values()),
        "input_files_unchanged_at_end": True, "new_scientific_execution": 0, "old_science_replay": 0,
        "central_writes": 0, "git_operations": 0, "remote_queries": 0, "metadata_CPU_s": None,
        "remote_head_verified_by_builder": False, "source_backup_GET_by_builder": False,
        "central_candidate_only": True, "publish_repository": CENTRAL_REPOSITORY, "publish_branch": CENTRAL_BRANCH,
        "publish_paths": [CENTRAL_UNIT_PATH + "/" + row["path"] for row in publishable],
        "publisher_requirements": ["fresh actual remote HEAD/tree and new-return HTTP404",
            "different reviewer actual candidate acceptance and root admission",
            "apply exactly these two blobs to the actual base tree; retain every other tree entry",
            "expected_sha equals reviewed current parent; force=false",
            "postcommit actual M receipt and full raw two-blob R3; no precommit self-SHA"],
        "independent_review": {"status": "PENDING_DIFFERENT_REVIEWER", "builder_author": "/root/theory_review"}}
    # All validations precede any output. Interrupted partial outputs are retained
    # and cannot be reused or overwritten by this command.
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=False)
    (output / "returns").mkdir()
    for name, payload in files.items():
        write_new(output / name, payload)
    inputs.recheck()
    need(sorted(p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file())
         == sorted(files), "CANDIDATE_MUST_CONTAIN_EXACTLY_TWO_FILES")
    for row in publishable:
        actual = (output / row["path"]).read_bytes()
        need(len(actual) == row["bytes"] and sha(actual) == row["sha256"], "ACTUAL_CANDIDATE_WRITEBACK_MISMATCH")
    proof["actual_candidate_writeback_hashes_verified"] = True
    write_new(proof_path, raw_json(proof))
    print(encode({"status": proof["status"], "proof": str(proof_path),
                  "proof_sha256": sha(proof_path.read_bytes()), "publishable_files": publishable,
                  "central_completed_total": "28/88", "CR_count_effect": 0}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Refusal, KeyError, TypeError, ValueError, OSError) as error:
        # Failure is not publication, ACK, or scientific failure. Do not remove
        # an existing or partial candidate to manufacture a successful retry.
        print(json.dumps({"status": "REFUSED_METADATA_BUILD", "error_class": type(error).__name__,
                          "reason": str(error), "scientific_execution": False, "central_writes": 0}), file=sys.stderr)
        raise SystemExit(2)
