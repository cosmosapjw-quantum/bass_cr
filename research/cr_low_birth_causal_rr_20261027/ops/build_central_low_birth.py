#!/usr/bin/env python3
"""Build one low-birth scoped central link, its exact return, and a proof.

This is an offline metadata builder, not a publisher or scientific calculation.
The caller supplies a freshly retrieved DAG, final owner-return JSON, actual
S/D identities, a dual-source R3 receipt and explicit saved-result pins. No
current HEAD or future result is invented. No scientific module is imported.

Example (root supplies the real files, identities and a new output location):
    python ops/build_central_low_birth.py \
      --dag /absolute/latest/DAG.json \
      --owner-return /absolute/final/CR_LOW_BIRTH_CAUSAL_RR_20261027.json \
      --central-head ACTUAL_LATEST_CENTRAL_SHA \
      --central-count-baseline /absolute/latest/CENTRAL_COUNT_BASELINE.json \
      --science-sha ACTUAL_S --documents-sha ACTUAL_D \
      --source-r3 /absolute/final/SOURCE_REMOTE_R3.json \
      --results /absolute/final/RESULTS_INPUT.json \
      --output-dir /absolute/new/central_candidate \
      --proof-file /absolute/new/central_candidate_proof.json

Only DAG.json and returns/CR_LOW_BIRTH_CAUSAL_RR_20261027.json are written beneath
output-dir. proof-file must be outside it. All outputs are create-only.
Existing central return files are neither read nor changed here. The publisher
must apply these two files onto the refreshed existing central tree, check that
the new return path is absent, and retain every other tree entry. This two-file
candidate must never be treated as a replacement for the complete central tree.

Adapted from prior build_central_proper.py at CR D8482ed83b14517b709ba6e801f6714cc333e720f,
Git blob8e94325515c72ad522cd225e72c5b5d8bb4cbfb1. That original is unchanged.
Author: /root/implementation (metadata author, not independent reviewer).
Final candidate review belongs to a different reviewer, including preservation
of concurrent PR108/B3h work and the actual publication expected-SHA contract.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

TARGET_ID = "CR_ALL_EXTERNAL_PHOTON_BARYON_SOURCE_INTERFACE"
UNIT_ID = "CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1"
UNIT_PATH = "research/cr_low_birth_causal_rr_20261027"
UNIT_ROOT = Path(__file__).resolve().parents[1]
LINK_KEY = "owner_return_low_birth_causal_rr_20261027"
RETURN_RELATIVE = "returns/CR_LOW_BIRTH_CAUSAL_RR_20261027.json"
EXPECTED_NODES = 88
EXPECTED_EDGES = 17
HISTORICAL_DECLARED_COMPLETE = 27
CENTRAL_UNIT_PATH = "research/orchestration_expansion_20261025"
OLD_PROPER_LINK = "owner_return_proper_injection_20261027"
N5_ID = "CR_N5_ATOMIC_ISOTOPE_COVERAGE"
HEIII_LINK = "owner_return_heiii_20261027"
B3H_ID = "B3h-native-finite-absorption"
SOURCE_RECORD_SHA256 = "8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf"
SOURCE_ARCHIVE_PROVIDERS = {"Dropbox", "Drive"}


class BuildError(ValueError):
    """The metadata inputs do not meet the fixed additive-build contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def reject_constant(token: str) -> None:
    raise BuildError(f"Nonfinite JSON constant is forbidden: {token}")


def decode_json(raw: bytes, label: str) -> Any:
    try:
        # Decimal preserves every input decimal value; no binary64 rounding of
        # historical scientific numbers occurs while rebuilding this metadata.
        return json.loads(raw.decode("utf-8"), parse_float=Decimal,
                          object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"{label}: invalid UTF-8 JSON: {exc}") from exc


def encode_json(value: Any, *, pretty: bool, depth: int = 0) -> str:
    """Encode supported JSON values, including exact parsed Decimal numbers.

    Sorted keys define the proof's canonical form. This is local canonical JSON,
    not a claim of compliance with RFC8785. String escaping uses stdlib json.
    """
    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    if isinstance(value, Decimal):
        require(value.is_finite(), "Nonfinite Decimal is forbidden")
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    require(type(value) in (dict, list),
            f"Unsupported JSON value type: {type(value).__name__}")
    if isinstance(value, dict):
        require(all(isinstance(key, str) for key in value), "JSON object keys must be strings")
        children = [
            json.dumps(key, ensure_ascii=False) + (": " if pretty else ":")
            + encode_json(value[key], pretty=pretty, depth=depth + 1)
            for key in sorted(value)
        ]
        opening, closing = "{", "}"
    else:
        children = [encode_json(item, pretty=pretty, depth=depth + 1) for item in value]
        opening, closing = "[", "]"
    if not children:
        return opening + closing
    if not pretty:
        return opening + ",".join(children) + closing
    pad = "  " * (depth + 1)
    return opening + "\n" + pad + (",\n" + pad).join(children) + "\n" + "  " * depth + closing


def canonical_bytes(value: Any) -> bytes:
    return encode_json(value, pretty=False).encode("utf-8")


def semantic_hash(value: Any) -> str:
    return sha256(canonical_bytes(value))


def exact_semantic_equal(left: Any, right: Any) -> bool:
    # Canonical equality also distinguishes booleans from integers.
    return canonical_bytes(left) == canonical_bytes(right)


def git_sha(value: Any, field: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None,
            f"{field}: immutable lowercase40-hex Git SHA required")
    require(len(set(value)) > 1, f"{field}: repeated-character placeholder SHA refused")
    return value


def digest_sha(value: Any, field: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None
            and len(set(value)) > 1, f"{field}: actual lowercase64-hex SHA256 required")
    return value


def nonempty_identity(value: Any, field: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{field}: explicit identity required")
    require(not re.fullmatch(r"(?i)(pending|placeholder|todo|tbd|unknown|actual[_ ].*|replace[_ ].*)", value.strip()),
            f"{field}: placeholder identity refused")
    return value


def positive_integer(value: Any, field: str) -> int:
    require(type(value) is int and value > 0, f"{field}: positive integer required")
    return value


def finite_number(value: Any, field: str) -> Decimal:
    require(type(value) is int or isinstance(value, Decimal), f"{field}: exact JSON number required")
    number = Decimal(value)
    require(number.is_finite(), f"{field}: finite number required")
    return number


def pointer(value: Any, location: str) -> Any:
    require(isinstance(location, str) and (location == "" or location.startswith("/")),
            "JSON pointer must be empty or begin with slash")
    current = value
    for escaped in location.split("/")[1:]:
        token = escaped.replace("~1", "/").replace("~0", "~")
        if type(current) is list:
            require(re.fullmatch(r"0|[1-9][0-9]*", token) is not None, "Invalid array JSON pointer")
            index = int(token)
            require(index < len(current), "JSON pointer array index is absent")
            current = current[index]
        else:
            require(type(current) is dict and token in current, "JSON pointer field is absent: " + location)
            current = current[token]
    return current


def no_private_secrets(value: Any) -> None:
    if type(value) is dict:
        for key, item in value.items():
            require(key.lower() not in {"signed_url", "download_url", "signed_download_url",
                                        "authorization", "access_token", "refresh_token"}
                    or item is None, "Private credential/download-link field refused: " + key)
            no_private_secrets(item)
    elif type(value) is list:
        for item in value:
            no_private_secrets(item)


def fixed_int(value: Any, expected: int, field: str) -> None:
    require(type(value) is int and value == expected,
            f"{field}: exact integer {expected} required")


def input_file(path: Path, label: str) -> tuple[Path, bytes, dict[str, Any]]:
    resolved = path.resolve(strict=True)
    require(resolved.is_file(), f"{label}: regular file required")
    raw = resolved.read_bytes()
    data = decode_json(raw, label)
    require(type(data) is dict, f"{label}: top-level JSON object required")
    return resolved, raw, data


def unit_local_file(relative: Any, label: str) -> tuple[Path, bytes, dict[str, Any]]:
    name = nonempty_identity(relative, label)
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts,
            label + ": unit-local relative path required")
    local = UNIT_ROOT / path
    require(local.is_file() and not local.is_symlink()
            and local.resolve(strict=True).is_relative_to(UNIT_ROOT),
            label + ": regular nonsymlink file inside this exact unit required")
    return input_file(local, label)


def validate_dag(dag: dict[str, Any]) -> tuple[int, list[dict[str, Any]], list[Any]]:
    nodes = dag.get("nodes")
    edges = dag.get("integration_edges")
    require(type(nodes) is list and len(nodes) == EXPECTED_NODES, "DAG must retain exactly88 nodes")
    require(type(edges) is list and len(edges) == EXPECTED_EDGES, "DAG must retain exactly17 edges")
    identifiers: list[str] = []
    for node in nodes:
        require(type(node) is dict, "Every DAG node must be an object")
        ident = node.get("id")
        require(isinstance(ident, str) and bool(ident), "Every DAG node needs an id")
        identifiers.append(ident)
    require(len(set(identifiers)) == len(identifiers), "Duplicate node IDs are forbidden")
    require(identifiers.count(TARGET_ID) == 1, "Exactly one original external-interface target required")
    target_index = identifiers.index(TARGET_ID)
    require(LINK_KEY not in nodes[target_index],
            "New owner-return link already exists; reuse/review existing evidence instead of overwriting")
    require(type(nodes[target_index].get("contract")) is dict, "Original target contract required")
    require(type(nodes[target_index].get(OLD_PROPER_LINK)) is dict,
            "Latest base must retain the prior proper-injection scoped link")
    for key, value in {"science_commit_S": "022c163726b814885805bd9a7ab988fe963cda4a",
                       "documents_commit_D": "8482ed83b14517b709ba6e801f6714cc333e720f",
                       "source_file": "returns/CR_PROPER_INJECTION_20261027.json",
                       "unit_id": "CR_PROPER_INJECTION_RETURN_V1"}.items():
        require(nodes[target_index][OLD_PROPER_LINK].get(key) == value,
                "Prior proper-injection identity changed: " + key)
    n5 = next((node for node in nodes if node["id"] == N5_ID), None)
    b3h = next((node for node in nodes if node["id"] == B3H_ID), None)
    require(n5 is not None and type(n5.get(HEIII_LINK)) is dict,
            "Latest base must retain N5 and the prior HeIII scoped link")
    for key, value in {"science_commit_S": "4e72c89b714431eb4c6ae07def777bbf72a5ae4c",
                       "documents_commit_D": "ec463db0c7e5c7fb5070796071c926caa4db6445",
                       "source_file": "returns/CR_HEIII_GROUND_RR_20261027.json"}.items():
        require(n5[HEIII_LINK].get(key) == value, "Prior HeIII identity changed: " + key)
    require(b3h is not None and type(b3h.get("status_observation")) is dict,
            "Latest base must retain the observed B3h owner state")
    require(dag.get("L4_ready") is False and "global_physical_completion" in dag
            and dag["global_physical_completion"] is None, "Original global physical gates changed; fresh admission required")
    for ident, expected in (("CR_N4_STOPPING_KERNEL", "PARTIAL_OPEN"),
                            (N5_ID, "PARTIAL_OPEN"),
                            ("CR_N6_CONSERVATIVE_COUPLING", "PREDECESSOR_GATED"),
                            ("CR_N7_NEW_PARCEL", "PREDECESSOR_GATED")):
        node = next((row for row in nodes if row["id"] == ident), None)
        require(node is not None and node.get("current_status") == expected,
                "Preserved CR predecessor gate changed: " + ident)
    return target_index, nodes, edges


def validate_central_count_baseline(baseline: dict[str, Any], central_head: str,
                                    dag: dict[str, Any], dag_digest: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Read current declared counts from a pinned foreign owner return, not statuses."""
    require(baseline.get("schema") == "CR_LOW_BIRTH_CENTRAL_COUNT_BASELINE_V1",
            "Explicit authoritative central-count baseline required")
    require(git_sha(baseline.get("central_head"), "count baseline.central_head") == central_head
            and digest_sha(baseline.get("dag_sha256"), "count baseline.dag_sha256") == dag_digest,
            "Central-count baseline does not bind the actual current HEAD and DAG bytes")
    require(baseline.get("historical_original_central_completed_total")
            == f"{HISTORICAL_DECLARED_COMPLETE}/{EXPECTED_NODES}"
            and baseline.get("unmerged_PR236_32_of_88_added") is False
            and baseline.get("counts_inferred_from_status_strings") is False,
            "Historical27/88, separate PR23632/88 and explicit nonheuristic counting required")
    cause = baseline.get("foreign_cause")
    require(type(cause) is dict, "Explicit scoped foreign count cause required")
    node_id = nonempty_identity(cause.get("node_id"), "count cause.node_id")
    foreign_unit = nonempty_identity(cause.get("unit_id"), "count cause.unit_id")
    require(node_id != TARGET_ID and foreign_unit != UNIT_ID,
            "This CR scoped link cannot supply its own foreign central-count increment")
    node = next((row for row in dag["nodes"] if row["id"] == node_id), None)
    require(node is not None and type(node.get("status_observation")) is dict,
            "Foreign count cause must be an existing observed node in the actual current DAG")
    observed = node["status_observation"]
    row = baseline.get("authoritative_return")
    require(type(row) is dict, "Pinned actual authoritative count return required")
    local = Path(nonempty_identity(row.get("local_path"), "count return.local_path"))
    require(local.is_absolute() and not local.is_symlink(),
            "Count return requires an explicit absolute regular nonsymlink source")
    path, raw, authority = input_file(local, "authoritative central count return")
    length = positive_integer(row.get("bytes"), "count return.bytes")
    digest = digest_sha(row.get("sha256"), "count return.sha256")
    require(len(raw) == length and sha256(raw) == digest,
            "Authoritative count-return byte identity failed")
    revision = git_sha(row.get("revision"), "count return.revision")
    require(revision == central_head, "Count return must be pinned at the supplied current central HEAD")
    relative = nonempty_identity(observed.get("source_file"), "count observation.source_file")
    require(not Path(relative).is_absolute() and ".." not in Path(relative).parts
            and relative.startswith("returns/") and relative != RETURN_RELATIVE,
            "Foreign count authority must name an existing safe central return path")
    location = nonempty_identity(row.get("json_pointer"), "count return.json_pointer")
    require(row.get("repo_path") == CENTRAL_UNIT_PATH + "/" + relative
            and location == observed.get("json_pointer"),
            "Count return path/pointer must match the actual DAG observation")
    value = pointer(authority, location)
    require(type(value) is dict and exact_semantic_equal(value, observed.get("value"))
            and value.get("unit_id") == foreign_unit,
            "Pinned foreign return differs from the current DAG's exact scoped observation")
    original = value.get("original_DAG")
    require(type(original) is dict
            and exact_semantic_equal(original, authority.get("original_DAG"))
            and exact_semantic_equal(original, baseline.get("original_DAG")),
            "Baseline, authoritative top-level and observed original_DAG counts must match exactly")
    fixed_int(original.get("total"), EXPECTED_NODES, "count original_DAG.total")
    before, completed, effect = (original.get(key) for key in
                                ("before_completed", "completed", "completion_count_effect"))
    require(type(before) is int and type(completed) is int and type(effect) is int
            and 0 <= before <= EXPECTED_NODES and 0 <= completed <= EXPECTED_NODES
            and before + effect == completed,
            "Explicit authoritative before/completed/effect count arithmetic is inconsistent")
    scope = nonempty_identity(original.get("count_scope"), "foreign count_scope")
    summary = {"central_head": central_head, "dag_sha256": dag_digest,
               "completed": completed, "total": EXPECTED_NODES,
               "current_completed_total": f"{completed}/{EXPECTED_NODES}",
               "historical_completed_total": f"{HISTORICAL_DECLARED_COMPLETE}/{EXPECTED_NODES}",
               "foreign_cause": {"node_id": node_id, "unit_id": foreign_unit,
                   "before_completed": before, "completion_count_effect": effect,
                   "count_scope": scope, "source_file": relative,
                   "source_revision": revision, "source_sha256": digest,
                   "json_pointer": location},
               "counts_inferred_from_status_strings": False,
               "unmerged_PR236_32_of_88_added": False, "this_CR_count_effect": 0}
    evidence = [{"role": "authoritative_central_count_return", "path": str(path),
                 "repo_path": row["repo_path"], "revision": revision,
                 "bytes": length, "sha256": digest}]
    no_private_secrets(baseline)
    return summary, evidence


def validate_source_r3(receipt: dict[str, Any]) -> dict[str, Any]:
    """Validate actual saved dual full-GET receipt metadata; do not redownload."""
    require(receipt.get("both_original_full_GET_and_all_members_PASS") is True,
            "Actual dual original-byte full-GET R3 PASS is required")
    require(receipt.get("source_archive_rebuilt") is False,
            "The sealed source archive must not have been rebuilt")
    archive = receipt.get("archive")
    require(type(archive) is dict, "Actual source archive identity is required")
    name = nonempty_identity(archive.get("name"), "archive.name")
    require(Path(name).name == name and name.endswith(".zip"), "Safe actual source ZIP basename required")
    size = positive_integer(archive.get("bytes"), "archive.bytes")
    digest = digest_sha(archive.get("sha256"), "archive.sha256")
    members = positive_integer(archive.get("members"), "archive.members")
    payloads = positive_integer(archive.get("payloads"), "archive.payloads")
    require(members == payloads + 1, "Archive requires one manifest plus its declared payloads")
    providers = receipt.get("providers")
    require(type(providers) is list and len(providers) == 2, "Exactly Dropbox and Drive R3 receipts required")
    names = set()
    manifest_digests = set()
    for row in providers:
        require(type(row) is dict and row.get("provider") in SOURCE_ARCHIVE_PROVIDERS,
                "Unexpected source-backup provider")
        require(row["provider"] not in names, "Duplicate provider is not dual backup")
        names.add(row["provider"])
        nonempty_identity(row.get("id"), row["provider"] + ".id")
        require(row.get("verification_tier") == "R3" and row.get("raw_HTTP_method") == "GET"
                and type(row.get("HTTP_status")) is int and row["HTTP_status"] == 200
                and row.get("HEAD_or_Range_used") is False
                and row.get("downloaded_original_file") is True
                and row.get("all_payload_sha256_and_CRC_PASS") is True,
                "Original full GET plus every member SHA/CRC must actually pass")
        require(row.get("downloaded_bytes") == size and row.get("archive_sha256") == digest
                and row.get("archive_members") == members and row.get("manifest_payloads") == payloads,
                "Provider R3 archive identity mismatch")
        manifest_digests.add(digest_sha(row.get("manifest_sha256"), "provider.manifest_sha256"))
    require(names == SOURCE_ARCHIVE_PROVIDERS and len(manifest_digests) == 1,
            "Providers must return the same immutable source archive and manifest")
    no_private_secrets(receipt)
    return {"name": name, "bytes": size, "sha256": digest,
            "members": members, "payloads": payloads,
            "manifest_sha256": next(iter(manifest_digests)),
            "source_R3_receipts_validated": True, "fresh_download_by_builder": False}


def validate_preparation_baseline(budget: dict[str, Any], budget_row: dict[str, Any],
                                  ledger_baseline: Decimal) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate this unit's incurred costs, never transfer another unit's allowance."""
    require(budget_row["repo_path"] == UNIT_PATH + "/EXECUTION_BUDGET.json"
            and Path(budget_row["local_path"]).resolve(strict=True)
            == (UNIT_ROOT / "EXECUTION_BUDGET.json").resolve(strict=True)
            and not Path(budget_row["local_path"]).is_symlink(),
            "The pinned execution_budget must be this unit's actual active EXECUTION_BUDGET.json")
    require(budget.get("unit") == UNIT_ID and budget.get("status") == "FROZEN_C4_ADMITTED"
            and finite_number(budget.get("local_science_cpu_cap_s"), "budget.cap") == 40
            and budget.get("historical_allowance_transferred") is False
            and budget.get("parallel_PR108_budget_transferred") is False,
            "Active admitted separate40 CPU budget with no old/parallel transfer required")
    relative = budget.get("preparation_cost_manifest")
    expected = digest_sha(budget.get("preparation_cost_manifest_sha256"),
                          "budget.preparation_cost_manifest_sha256")
    path, raw, manifest = unit_local_file(relative, "preparation cost manifest")
    require(sha256(raw) == expected, "Actual preparation manifest bytes differ from active budget pin")
    require(manifest.get("unit") == UNIT_ID and type(manifest.get("records")) is list
            and bool(manifest["records"]), "Actual same-unit preparation receipt manifest required")
    transfer_flags = ("old_budget_transferred", "old_budgets_transferred",
                      "historical_allowance_transferred", "parallel_PR108_budget_transferred",
                      "historical_transferred", "parallel_project_budget_transferred")
    require(all(manifest.get(flag, False) is False for flag in transfer_flags),
            "Old or parallel preparation budget transfer refused")
    resource_pass = manifest.get("all_resource_attempts_pass")
    require(type(resource_pass) is bool, "Actual preparation resource-attempt outcome must remain explicit")
    evidence = [{"role": "preparation_cost_manifest", "path": str(path),
                 "repo_path": UNIT_PATH + "/" + relative, "revision": budget_row["revision"],
                 "bytes": len(raw), "sha256": expected}]
    seen, costs, verified, failed_paths = set(), [], [], []
    tolerance = Decimal("1e-12")
    for row in manifest["records"]:
        require(type(row) is dict, "Each preparation receipt descriptor must be an object")
        receipt_relative = row.get("path")
        receipt_path, receipt_raw, receipt = unit_local_file(receipt_relative, "preparation receipt")
        require(receipt_path not in seen and receipt_path != path
                and receipt_path != (UNIT_ROOT / "EXECUTION_BUDGET.json").resolve(strict=True),
                "Preparation receipts must be unique and cannot alias their manifest or active budget")
        seen.add(receipt_path)
        length = positive_integer(row.get("bytes"), "preparation receipt.bytes")
        digest = digest_sha(row.get("sha256"), "preparation receipt.sha256")
        require(len(receipt_raw) == length and sha256(receipt_raw) == digest,
                "Preparation receipt byte identity failed: " + receipt_relative)
        require(receipt.get("unit") == UNIT_ID and row.get("unit", UNIT_ID) == UNIT_ID
                and all(receipt.get(flag, False) is False for flag in transfer_flags),
                "Foreign-unit or transferred preparation cost refused: " + receipt_relative)
        cost = finite_number(receipt.get("charged_preparation_CPU_s"), "actual preparation cost")
        declared = finite_number(row.get("charged_preparation_CPU_s"), "manifest preparation row cost")
        require(cost >= 0 and declared >= 0 and abs(cost - declared) <= tolerance,
                "Preparation row does not match its actual nonnegative incurred cost: " + receipt_relative)
        costs.append(cost)
        verified.append({"path": receipt_relative, "bytes": length, "sha256": digest,
                         "charged_preparation_CPU_s": cost})
        evidence.append({"role": "preparation_receipt", "path": str(receipt_path),
                         "repo_path": UNIT_PATH + "/" + receipt_relative,
                         "revision": budget_row["revision"], "bytes": length, "sha256": digest})
        # The manifest carries the complete resource outcome. These explicit
        # negative receipt fields additionally prevent a conflicting blanket PASS.
        if (("memory_gate" in receipt and receipt["memory_gate"] != "PASS")
                or bool(receipt.get("error")) or bool(receipt.get("errors"))
                or receipt.get("all_resource_attempts_pass") is False):
            failed_paths.append(receipt_relative)
    require(not failed_paths or resource_pass is False,
            "Preparation manifest hides an explicitly failed resource receipt")
    measured = sum(costs, Decimal(0))
    declared_total = finite_number(manifest.get("charged_total_CPU_s"), "preparation manifest total")
    budget_baseline = finite_number(budget.get("spent_before_C4_admission"), "active budget preparation baseline")
    require(declared_total >= 0 and budget_baseline >= 0 and ledger_baseline >= 0
            and all(abs(measured - value) <= tolerance
                    for value in (declared_total, budget_baseline, ledger_baseline)),
            "Actual preparation costs, manifest total, active budget and execution ledger baseline differ")
    summary = {"manifest_path": relative, "manifest_bytes": len(raw), "manifest_sha256": expected,
               "actual_record_count": len(verified), "verified_records": verified,
               "charged_preparation_CPU_s": measured, "manifest_charged_total_CPU_s": declared_total,
               "active_budget_spent_before_C4_admission": budget_baseline,
               "execution_ledger_baseline_preparation_cpu_s": ledger_baseline,
               "comparison_absolute_tolerance_CPU_s": tolerance,
               "all_resource_attempts_pass": resource_pass,
               "explicitly_failed_preparation_receipt_paths": failed_paths,
               "preserved_first_admission_status": manifest.get("preserved_first_admission_status"),
               "old_or_parallel_budget_transferred": False}
    return summary, evidence


def validate_results(manifest: dict[str, Any], science: str, documents: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    require(manifest.get("schema") == "CR_LOW_BIRTH_CENTRAL_RESULTS_INPUT_V1"
            and manifest.get("unit_id") == UNIT_ID, "Exact low-birth results-input manifest required")
    require(git_sha(manifest.get("science_commit_S"), "results.S") == science
            and git_sha(manifest.get("documents_commit_D"), "results.D") == documents,
            "Results-input S/D do not match explicit CLI identities")
    rows = manifest.get("files")
    require(type(rows) is list and len(rows) >= 6, "Required saved result files are absent")
    records, evidence = {}, []
    local_paths, repository_paths = set(), set()
    for row in rows:
        require(type(row) is dict, "Each results-input file descriptor must be an object")
        role = nonempty_identity(row.get("role"), "result.role")
        require(role not in records, "Duplicate results-input role: " + role)
        local = Path(nonempty_identity(row.get("local_path"), "result.local_path"))
        require(local.is_absolute(), "Result local_path must be explicit and absolute")
        repo_path = nonempty_identity(row.get("repo_path"), "result.repo_path")
        require(not Path(repo_path).is_absolute() and ".." not in Path(repo_path).parts
                and repo_path.startswith(UNIT_PATH + "/"), "Result repo_path must stay in this unit")
        revision = git_sha(row.get("revision"), "result.revision")
        require(revision in (science, documents), "Result evidence revision is not actual S or D")
        length = positive_integer(row.get("bytes"), "result.bytes")
        digest = digest_sha(row.get("sha256"), "result.sha256")
        path, raw, data = input_file(local, role)
        require(path not in local_paths and repo_path not in repository_paths,
                "Different result roles must not alias the same local or repository file")
        local_paths.add(path)
        repository_paths.add(repo_path)
        require(len(raw) == length and sha256(raw) == digest, "Saved result byte identity failed: " + role)
        records[role] = (data, row)
        evidence.append({"role": role, "path": str(path), "repo_path": repo_path,
                         "revision": revision, "bytes": length, "sha256": digest})
    required = {"primary", "controls", "independent", "execution_ledger", "execution_budget", "final_review"}
    require(required <= set(records), "A required real result/review/ledger file is missing")
    primary = records["primary"][0]
    controls = records["controls"][0]
    independent = records["independent"][0]
    ledger = records["execution_ledger"][0]
    budget, budget_row = records["execution_budget"]
    review, review_row = records["final_review"]
    for label, data in (("primary", primary), ("controls", controls),
                        ("independent", independent), ("execution_ledger", ledger),
                        ("execution_budget", budget)):
        require(data.get("unit") == UNIT_ID, "Foreign-unit result refused: " + label)
    require(primary.get("schema") == "CR_LOW_BIRTH_CAUSAL_RR_RESULT_V1"
            and primary.get("numerical_acceptance", {}).get("internal_pass") is True,
            "Actual primary internal acceptance is required")
    require(primary.get("input", {}).get("sha256") == SOURCE_RECORD_SHA256
            and primary["input"].get("selected_tag") == "direct_0p1_10"
            and len(primary.get("prefixes", [])) == 4
            and len(primary.get("observation_bins", [])) == 4,
            "Actual preserved source and four-prefix/four-bin response required")
    for key in ("full_source_native25", "source_parent_ion_chemistry",
                "absolute_worldtube_totals", "global_physical_completion", "global_physical_error"):
        require(key in primary and primary[key] is None, "Primary claim ceiling changed: " + key)
    require(primary.get("physical_heating_completed") is False
            and primary.get("old_budget_carried") is False
            and primary.get("old_science_replay") == 0, "Primary preserved scope flags required")
    context = primary.get("context")
    require(type(context) is dict and context.get("inventory_id") == "CR_LOW_BIRTH_100K_CONDITIONAL_H1_HE4_FIXED_INVENTORY_V1"
            and context.get("donor_state_id") == context.get("recipient_state_id") == context["inventory_id"],
            "Actual same-state conditional inventory required")
    nb = finite_number(context.get("recipient_nb_m3"), "primary.context.recipient_nb_m3")
    require(nb > 0 and finite_number(context.get("donor_nb_m3"), "primary.context.donor_nb_m3") == nb,
            "Actual equal explicit donor/recipient nb required")
    require(controls.get("all_pass") is True, "Changed controls did not pass")
    count = positive_integer(controls.get("count"), "controls.count")
    fixed_int(controls.get("passed"), count, "controls.passed")
    require(independent.get("schema") == "CR_LOW_BIRTH_RR_INDEPENDENT_REFERENCE_V1"
            and independent.get("status") == "PASS"
            and independent.get("numerical_acceptance", {}).get("pass") is True,
            "Actual independent numerical acceptance is required")
    check_count = positive_integer(independent["numerical_acceptance"].get("check_count"), "independent.check_count")
    fixed_int(independent["numerical_acceptance"].get("passed_count"), check_count, "independent.passed_count")
    require(finite_number(ledger.get("cap_s"), "ledger.cap_s") == 40,
            "Separate40 CPU budget is required")
    charged = finite_number(ledger.get("charged_cpu_s"), "ledger.charged_cpu_s")
    require(0 <= charged <= 40 and ledger.get("global_remaining") is None
            and ledger.get("historical_transferred") is False
            and ledger.get("parallel_project_budget_transferred") is False,
            "Budget cap/global-null/no-transfer contract failed")
    attempts = ledger.get("attempts")
    require(type(attempts) is list and bool(attempts) and all(type(row) is dict for row in attempts),
            "Actual attempt debit ledger required")
    attempt_ids = [nonempty_identity(row.get("attempt_id"), "attempt_id") for row in attempts]
    require(len(set(attempt_ids)) == len(attempt_ids), "Canonical ledger must have unique attempt IDs")
    for row in attempts:
        require(row.get("unit") == UNIT_ID and row.get("terminal_debit") is True
                and row.get("cpu_accounting_complete") is True, "Unresolved or foreign CPU debit")
        require(finite_number(row.get("charged_cpu_s"), "attempt.charged_cpu_s") >= 0,
                "Negative attempt debit")
        subtotal = sum((finite_number(row.get(key), "attempt." + key) for key in
                        ("worker_cpu_s", "coordinator_cpu_through_receipt_s", "receipt_tail_reserve_s")), Decimal(0))
        require(finite_number(row["charged_cpu_s"], "attempt.charged_cpu_s") + Decimal("1e-10") >= subtotal,
                "Attempt debit omits a recorded worker/coordinator/tail cost")
    baseline = finite_number(ledger.get("baseline_preparation_cpu_s"), "ledger.baseline_preparation_cpu_s")
    preparation, preparation_evidence = validate_preparation_baseline(budget, budget_row, baseline)
    accounted = sum((finite_number(row["charged_cpu_s"], "attempt.charged_cpu_s") for row in attempts), baseline)
    require(abs(accounted - charged) <= Decimal("1e-10"), "Ledger aggregate differs from unique recorded attempt costs")
    require(abs(finite_number(ledger.get("remaining_not_transferable"), "ledger.remaining_not_transferable")
                - (Decimal(40) - charged)) <= Decimal("1e-10"), "Ledger remaining balance is inconsistent")
    review_unit = review.get("unit", review.get("unit_id"))
    require(review_unit == UNIT_ID, "Final review must name this exact unit")
    acceptance = review_row.get("acceptance", {})
    verdict = pointer(review, acceptance.get("verdict_pointer", "/verdict"))
    require(isinstance(verdict, str) and verdict.startswith("PASS_SCOPED"),
            "Actual scoped final review acceptance required")
    blockers = pointer(review, acceptance.get("blocking_count_pointer", "/core_blocking_findings"))
    require(type(blockers) is int and blockers == 0 or type(blockers) is list and not blockers,
            "Final review still has core blockers")
    failed_ids = [row["attempt_id"] for row in attempts if row.get("status") != "completed"]
    return ({"control_count": count, "independent_check_count": check_count,
             "review_verdict": verdict, "charged_cpu_s": charged,
             "failed_attempt_ids": failed_ids, "all_worker_attempts_pass": not failed_ids,
             "all_resource_attempts_pass": preparation["all_resource_attempts_pass"],
             "all_runtime_attempts_pass": preparation["all_resource_attempts_pass"] and not failed_ids,
             "preparation_baseline": preparation,
             "primary_scope": {"source_record_sha256": SOURCE_RECORD_SHA256,
                "selected_birth_tag": "direct_0p1_10", "cumulative_prefixes": 4,
                "disjoint_observation_bins": 4,
                "same_state_nb_m3": primary["context"]["recipient_nb_m3"],
                "inventory_id": primary["context"]["inventory_id"],
                "rr_native25_scope": "integrated_RR_event_only",
                "full_source_native25": None, "source_parent_ion_chemistry": None,
                "physical_heating_completed": False, "absolute_worldtube_totals": None}}, evidence, preparation_evidence)


def validate_owner_return(owner_return: dict[str, Any], central_head: str,
                          science: str, documents: str, r3_digest: str,
                          results_digest: str, archive: dict[str, Any],
                          result_summary: dict[str, Any], result_evidence: list[dict[str, Any]],
                          count_baseline: dict[str, Any], count_baseline_digest: str) -> dict[str, str]:
    require(owner_return.get("parent_node") == TARGET_ID,
            "owner-return parent_node must be the original external-interface target")
    require(owner_return.get("owner_repository") == "cosmosapjw-quantum/bass_cr",
            "owner-return owner_repository must be cosmosapjw-quantum/bass_cr")
    unit_id = owner_return.get("unit_id")
    require(unit_id == UNIT_ID and owner_return.get("unit_path") == UNIT_PATH,
            "Exact new unit identity and path required")
    require(isinstance(owner_return.get("pull_request"), str)
            and re.fullmatch(r"https://github\.com/cosmosapjw-quantum/bass_cr/pull/[1-9][0-9]*",
                             owner_return["pull_request"]) is not None,
            "An actual repository pull-request URL is required")
    require(git_sha(owner_return.get("science_commit_S"), "science_commit_S") == science
            and git_sha(owner_return.get("documents_commit_D"), "documents_commit_D") == documents,
            "Owner-return S/D differ from explicit CLI identities")
    require(owner_return.get("central_commit_M") is None,
            "Precommit owner return must leave its unknown self-commit null; use a postcommit receipt")
    require(owner_return.get("source_R3_receipt_sha256") == r3_digest
            and owner_return.get("results_input_sha256") == results_digest,
            "Final owner return must bind the actual R3 and results-input bytes")

    # Either existing receipt spelling is accepted; every supplied binding must
    # equal the caller's current observed HEAD. The tool does not fetch a HEAD.
    base_fields = [field for field in ("central_base_sha", "central_expected_parent")
                   if field in owner_return]
    require(bool(base_fields), "owner-return requires central_base_sha or central_expected_parent")
    for field in base_fields:
        require(git_sha(owner_return[field], field) == central_head,
                f"{field} differs from --central-head; refresh/rebase the metadata before building")

    original = owner_return.get("original_DAG")
    require(type(original) is dict, "owner-return original_DAG accounting object required")
    fixed_int(original.get("nodes"), EXPECTED_NODES, "original_DAG.nodes")
    fixed_int(original.get("integration_edges"), EXPECTED_EDGES, "original_DAG.integration_edges")
    fixed_int(original.get("declared_deliverable_count"), count_baseline["completed"],
              "original_DAG.declared_deliverable_count")
    fixed_int(original.get("new_count_effect"), 0, "original_DAG.new_count_effect")
    require(owner_return.get("original_central_completed_total") == count_baseline["current_completed_total"]
            and owner_return.get("historical_original_central_completed_total")
            == count_baseline["historical_completed_total"]
            and owner_return.get("central_count_baseline_sha256") == count_baseline_digest
            and owner_return.get("unmerged_PR236_32_of_88_added") is False,
            "Current authoritative count, historical27/88 and separate PR23632/88 must remain distinct")
    require(owner_return.get("original_node_status_changed") is False,
            "This scoped link must not claim an original-node status change")
    child = owner_return.get("scope_child", {})
    nonempty_identity(child.get("id"), "scope_child.id")
    fixed_int(child.get("completed"), 1, "scope_child.completed")
    fixed_int(child.get("total"), 1, "scope_child.total")
    fixed_int(child.get("original_central_count_effect"), 0, "scope_child.original_central_count_effect")
    require(child.get("parent_node") == TARGET_ID, "Scoped child must use the original parent")
    workflow = owner_return.get("workflow", {})
    require(workflow.get("R") == "10/10" and workflow.get("C") == "10/10"
            and workflow.get("total") == "20/20", "Both actual full loops must be complete")
    commits = workflow.get("actual_published_stage_commits")
    require(type(commits) is list and len(commits) == 20
            and all(isinstance(commit, str) for commit in commits)
            and len(set(commits)) == 20, "Twenty distinct actual stage publications required")
    for commit in commits:
        git_sha(commit, "workflow.stage_commit")
    require(science in commits and documents == commits[-1], "Actual S/D must bind the completed publication workflow")
    fixed_int(workflow.get("dual_R2_stage_receipts"), 20, "workflow.dual_R2_stage_receipts")
    require(workflow.get("canonical_source_dual_R3") is True, "Actual source dual R3 required")
    gates = owner_return.get("gates", {})
    for name, expected in (("N4", "PARTIAL_OPEN"), ("N5", "PARTIAL_OPEN"),
                           ("N6", "PREDECESSOR_GATED"), ("N7", "PREDECESSOR_GATED")):
        require(gates.get(name) == expected, "Preserved owner gate mismatch: " + name)
    require(gates.get("L4_ready") is False, "L4 must remain false")
    for key in ("global_physical_completion", "global_physical_error", "global_budget_remaining", "global_currency"):
        require(key in gates and gates[key] is None, "Global field must remain explicitly null: " + key)
    require(owner_return.get("review_decision") == result_summary["review_verdict"], "Final review verdict mismatch")
    require(exact_semantic_equal(owner_return.get("scientific_scope"), result_summary["primary_scope"]),
            "Owner-return scientific scope differs from the actual saved response")
    verification = owner_return.get("verification", {})
    fixed_int(verification.get("new_controls_passed"), result_summary["control_count"], "verification.new_controls_passed")
    fixed_int(verification.get("independent_checks_passed"), result_summary["independent_check_count"], "verification.independent_checks_passed")
    require(verification.get("all_runtime_attempts_pass") is result_summary["all_runtime_attempts_pass"],
            "Runtime failures must not be promoted to blanket PASS")
    require(verification.get("all_resource_attempts_pass") is result_summary["all_resource_attempts_pass"],
            "The actual preparation resource failures must remain explicit")
    execution = owner_return.get("execution", {})
    require(finite_number(execution.get("new_unit_cap_s"), "execution.new_unit_cap_s") == 40
            and finite_number(execution.get("charged_cpu_s"), "execution.charged_cpu_s") == result_summary["charged_cpu_s"],
            "Owner execution summary differs from the actual separate40 CPU ledger")
    require(execution.get("preserved_failed_attempt_ids") == result_summary["failed_attempt_ids"]
            and execution.get("old_or_parallel_budget_transferred") is False
            and execution.get("unused_allowance_auto_carried_to_next_unit") is False
            and execution.get("hard_preventive_aggregate_cap_proof") is False,
            "Failure/no-carry/runtime-proof ceiling must be preserved")
    preparation = result_summary["preparation_baseline"]
    require(abs(finite_number(execution.get("baseline_preparation_cpu_s"), "execution.baseline_preparation_cpu_s")
                - preparation["execution_ledger_baseline_preparation_cpu_s"]) <= Decimal("1e-12")
            and execution.get("preparation_cost_manifest") == preparation["manifest_path"]
            and execution.get("preparation_cost_manifest_sha256") == preparation["manifest_sha256"]
            and execution.get("preserved_failed_preparation_receipt_paths")
            == preparation["explicitly_failed_preparation_receipt_paths"],
            "Owner execution summary must preserve the exact same-unit preparation chain and failures")
    source_archive = owner_return.get("canonical_source_archive", {})
    require(source_archive.get("science_commit_S") == science
            and source_archive.get("canonical_same_immutable_zip") is True
            and source_archive.get("source_rebuilt_after_seal") is False,
            "Canonical immutable source receipt must bind actual S")
    require(science[:12] in archive["name"], "Canonical source ZIP name must identify actual S")
    for key in ("name", "bytes", "sha256", "members", "payloads"):
        require(source_archive.get("archive", {}).get(key) == archive[key], "Source archive receipt differs: " + key)
    source_evidence = owner_return.get("source_evidence")
    require(type(source_evidence) is list and all(type(row) is dict for row in source_evidence),
            "Actual source-evidence pins required")
    for required_row in result_evidence:
        matching = [row for row in source_evidence if row.get("path") == required_row["repo_path"]]
        require(len(matching) == 1, "Exactly one evidence pin required for: " + required_row["role"])
        for key in ("revision", "bytes", "sha256"):
            require(matching[0].get(key) == required_row[key], "Published evidence pin differs: " + required_row["role"])
    no_private_secrets(owner_return)

    return {"unit_id": unit_id, "source_file": RETURN_RELATIVE, "json_pointer": "",
            "science_commit_S": science, "documents_commit_D": documents}


def preservation_proof(original: dict[str, Any], candidate: dict[str, Any],
                       target_index: int, link: dict[str, str],
                       count_baseline: dict[str, Any]) -> dict[str, Any]:
    require(len(candidate["nodes"]) == EXPECTED_NODES
            and len(candidate["integration_edges"]) == EXPECTED_EDGES,
            "Candidate changed original node/edge counts")
    restored = deepcopy(candidate)
    require(restored["nodes"][target_index].get(LINK_KEY) == link,
            "Candidate link does not match the supplied final owner return")
    del restored["nodes"][target_index][LINK_KEY]
    require(exact_semantic_equal(restored, original),
            "Removing the new link did not restore the complete original DAG")

    before_target = original["nodes"][target_index]
    after_target_without_link = deepcopy(candidate["nodes"][target_index])
    del after_target_without_link[LINK_KEY]
    require(exact_semantic_equal(before_target, after_target_without_link),
            "An existing target field changed")
    before_other = [node for index, node in enumerate(original["nodes"]) if index != target_index]
    after_other = [node for index, node in enumerate(candidate["nodes"]) if index != target_index]
    require(len(before_other) == 87 and exact_semantic_equal(before_other, after_other),
            "One of the87 other nodes changed")
    before_top = {key: value for key, value in original.items() if key != "nodes"}
    after_top = {key: value for key, value in candidate.items() if key != "nodes"}
    require(exact_semantic_equal(before_top, after_top), "Top-level metadata or edges changed")

    n5_before = next((node for node in original["nodes"]
                      if node["id"] == "CR_N5_ATOMIC_ISOTOPE_COVERAGE"), None)
    n5_after = next((node for node in candidate["nodes"]
                     if node["id"] == "CR_N5_ATOMIC_ISOTOPE_COVERAGE"), None)
    require(n5_before is not None and exact_semantic_equal(n5_before, n5_after),
            "Original N5 node or its status/return history changed")
    b3h_before = next(node for node in original["nodes"] if node["id"] == B3H_ID)
    b3h_after = next(node for node in candidate["nodes"] if node["id"] == B3H_ID)
    require(exact_semantic_equal(b3h_before, b3h_after), "Concurrent B3h owner fields changed")
    require(exact_semantic_equal(before_target[OLD_PROPER_LINK],
                                candidate["nodes"][target_index][OLD_PROPER_LINK]),
            "Prior proper-injection link changed")
    require(exact_semantic_equal(n5_before[HEIII_LINK], n5_after[HEIII_LINK]),
            "Prior HeIII link changed")
    return {
        "removed_link_restores_entire_DAG_exact_semantic_identity": True,
        "input_DAG_semantic_sha256": semantic_hash(original),
        "removed_link_DAG_semantic_sha256": semantic_hash(restored),
        "target_existing_fields_unchanged": True,
        "target_before_semantic_sha256": semantic_hash(before_target),
        "target_after_without_link_semantic_sha256": semantic_hash(after_target_without_link),
        "target_original_contract_unchanged": True,
        "target_current_status_before": before_target.get("current_status"),
        "target_current_status_after": candidate["nodes"][target_index].get("current_status"),
        "other87nodes_unchanged": True,
        "other87nodes_before_semantic_sha256": semantic_hash(before_other),
        "other87nodes_after_semantic_sha256": semantic_hash(after_other),
        "all_non_node_top_metadata_unchanged": True,
        "all17edges_unchanged": True,
        "integration_edges_sha256": semantic_hash(original["integration_edges"]),
        "N5_entire_node_unchanged": True,
        "N5_current_status_before": n5_before.get("current_status"),
        "N5_current_status_after": n5_after.get("current_status"),
        "N5_semantic_sha256": semantic_hash(n5_before),
        "prior_proper_link_unchanged": True,
        "prior_proper_link_semantic_sha256": semantic_hash(before_target[OLD_PROPER_LINK]),
        "prior_HeIII_link_unchanged": True,
        "prior_HeIII_link_semantic_sha256": semantic_hash(n5_before[HEIII_LINK]),
        "B3h_entire_current_node_unchanged": True,
        "B3h_current_status_before": b3h_before.get("current_status"),
        "B3h_current_status_after": b3h_after.get("current_status"),
        "B3h_semantic_sha256": semantic_hash(b3h_before),
        "original_nodes": EXPECTED_NODES,
        "original_integration_edges": EXPECTED_EDGES,
        "preserved_declared_deliverable_count": count_baseline["completed"],
        "historical_declared_deliverable_count": HISTORICAL_DECLARED_COMPLETE,
        "declared_count_basis": "Pinned actual current central-count baseline and foreign authoritative return; no status inference",
        "foreign_count_cause": count_baseline["foreign_cause"],
        "new_count_effect": 0,
    }


def write_new(path: Path, raw: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dag", required=True, type=Path)
    parser.add_argument("--owner-return", required=True, type=Path)
    parser.add_argument("--central-head", required=True)
    parser.add_argument("--central-count-baseline", required=True, type=Path)
    parser.add_argument("--science-sha", required=True)
    parser.add_argument("--documents-sha", required=True)
    parser.add_argument("--source-r3", required=True, type=Path)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--proof-file", required=True, type=Path)
    args = parser.parse_args()

    central_head = git_sha(args.central_head, "--central-head")
    science = git_sha(args.science_sha, "--science-sha")
    documents = git_sha(args.documents_sha, "--documents-sha")
    dag_path, dag_raw, dag = input_file(args.dag, "latest central DAG")
    return_path, return_raw, owner_return = input_file(args.owner_return, "final owner return")
    r3_path, r3_raw, r3_receipt = input_file(args.source_r3, "actual dual source R3 receipt")
    results_path, results_raw, results_input = input_file(args.results, "actual saved results input")
    count_path, count_raw, count_input = input_file(args.central_count_baseline, "actual central-count baseline")
    target_index, _, _ = validate_dag(dag)
    count_baseline, count_evidence = validate_central_count_baseline(count_input, central_head, dag, sha256(dag_raw))
    archive = validate_source_r3(r3_receipt)
    result_summary, result_evidence, preparation_evidence = validate_results(results_input, science, documents)
    link = validate_owner_return(owner_return, central_head, science, documents,
        sha256(r3_raw), sha256(results_raw), archive, result_summary, result_evidence,
        count_baseline, sha256(count_raw))
    direct_inputs = [(dag_path, dag_raw), (return_path, return_raw),
                     (r3_path, r3_raw), (results_path, results_raw), (count_path, count_raw)]
    all_saved_inputs = result_evidence + preparation_evidence + count_evidence
    out = args.output_dir.resolve()
    proof_path = args.proof_file.resolve()
    require(not out.exists(), "--output-dir must be a new create-only directory")
    require(not proof_path.exists(), "--proof-file already exists")
    require(out != proof_path and out not in proof_path.parents,
            "--proof-file must be outside the two-file candidate directory")
    require(proof_path not in {path for path, _raw in direct_inputs}
            and proof_path not in {Path(row["path"]) for row in all_saved_inputs},
            "Proof path collides with an input")
    require(all(out not in path.parents for path, _raw in direct_inputs)
            and all(out not in Path(row["path"]).parents for row in all_saved_inputs),
            "Candidate output directory must not contain an input")

    candidate = deepcopy(dag)
    candidate["nodes"][target_index][LINK_KEY] = link
    preservation = preservation_proof(dag, candidate, target_index, link, count_baseline)
    candidate_raw = (encode_json(candidate, pretty=True) + "\n").encode("utf-8")
    # Verify the actual JSON roundtrip as well, retaining exact decimal values.
    decoded_candidate = decode_json(candidate_raw, "serialized candidate")
    require(exact_semantic_equal(candidate, decoded_candidate),
            "DAG JSON serialization changed a value")
    preservation_proof(dag, decoded_candidate, target_index, link, count_baseline)

    # No path is changed before all input and semantic checks above have passed.
    # A later IO failure retains any newly created partial outputs for diagnosis;
    # a retry must use another fresh output directory, never overwrite history.
    out.mkdir(parents=True, exist_ok=False)
    (out / "returns").mkdir(exist_ok=False)
    write_new(out / "DAG.json", candidate_raw)
    write_new(out / RETURN_RELATIVE, return_raw)  # Exact root-supplied bytes.
    written_dag = (out / "DAG.json").read_bytes()
    written_return = (out / RETURN_RELATIVE).read_bytes()
    require(written_dag == candidate_raw, "DAG output byte readback mismatch")
    require(written_return == return_raw, "Owner-return output byte readback mismatch")
    actual_preservation = preservation_proof(
        dag, decode_json(written_dag, "written DAG"), target_index, link, count_baseline)
    require(exact_semantic_equal(preservation, actual_preservation),
            "Written-candidate preservation proof differs")
    require(all(path.read_bytes() == raw for path, raw in direct_inputs)
            and all(sha256(Path(row["path"]).read_bytes()) == row["sha256"] for row in all_saved_inputs),
            "An input changed during the offline build; candidate requires refreshed review")

    proof = {
        "schema": "CR_LOW_BIRTH_CENTRAL_ADDITIVE_BUILD_PROOF_V1",
        "status": "PASS_SCOPED_OFFLINE_METADATA_BUILD",
        "central_head_supplied_by_root": central_head,
        "science_commit_S_supplied_by_root": science,
        "documents_commit_D_supplied_by_root": documents,
        "remote_head_verified_by_builder": False,
        "target_id": TARGET_ID,
        "target_index": target_index,
        "added_link_key": LINK_KEY,
        "added_link": link,
        "inputs": [
            {"kind": "latest_DAG", "path": str(dag_path), "bytes": len(dag_raw),
             "sha256": sha256(dag_raw)},
            {"kind": "final_owner_return", "path": str(return_path), "bytes": len(return_raw),
             "sha256": sha256(return_raw)},
            {"kind": "actual_dual_source_R3", "path": str(r3_path), "bytes": len(r3_raw),
             "sha256": sha256(r3_raw)},
            {"kind": "actual_results_input", "path": str(results_path), "bytes": len(results_raw),
             "sha256": sha256(results_raw)},
            {"kind": "actual_central_count_baseline", "path": str(count_path), "bytes": len(count_raw),
             "sha256": sha256(count_raw)},
        ],
        "saved_result_evidence": result_evidence,
        "saved_preparation_cost_evidence": preparation_evidence,
        "saved_central_count_evidence": count_evidence,
        "validated_central_count_baseline": count_baseline,
        "validated_result_summary": result_summary,
        "validated_canonical_source_archive": archive,
        "publishable_files": [
            {"path": "DAG.json", "bytes": len(written_dag), "sha256": sha256(written_dag)},
            {"path": RETURN_RELATIVE, "bytes": len(written_return),
             "sha256": sha256(written_return)},
        ],
        "local_output_directory": str(out),
        "owner_return_exact_input_bytes_preserved": True,
        "input_files_unchanged_at_end": True,
        "preservation": actual_preservation,
        "serialization": "UTF-8 sorted-key JSON; Decimal input values retained exactly; "
                         "proof canonical form is compact local JSON, not RFC8785",
        "publication_scope": {
            "central_writes": 0,
            "git_operations": 0,
            "remote_queries": 0,
            "existing_return_files_written_or_deleted": [],
            "remote_new_return_path_absence_checked": False,
            "required_publisher_action": "Refresh expected central HEAD and base tree; require the "
                                         "new return path to be absent; apply only the two listed "
                                         "files onto that existing tree with non-force expected-SHA "
                                         "publication. Preserve every other path and parallel owner.",
        },
        "independent_review": {
            "metadata_author": "/root/implementation",
            "author_is_independent_reviewer": False,
            "status": "PENDING_DIFFERENT_REVIEWER",
            "scope": "Independent source reviewer checks exact final candidate, root-supplied return "
                     "evidence, publication parent and PR108/B3h preservation.",
        },
        "new_scientific_execution": 0,
        "old_science_replay": 0,
        "new_R3_network_requests": 0,
        "source_archives_created_or_rebuilt": 0,
        "prior_ops_state_files_mutated": [],
    }
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_raw = (encode_json(proof, pretty=True) + "\n").encode("utf-8")
    write_new(proof_path, proof_raw)
    print(json.dumps({
        "status": proof["status"], "central_head": central_head,
        "output_dir": str(out), "proof_file": str(proof_path),
        "proof_sha256": sha256(proof_raw),
        "publishable_files": proof["publishable_files"],
        "nodes": EXPECTED_NODES, "edges": EXPECTED_EDGES,
        "declared_complete": count_baseline["completed"],
        "historical_declared_complete": HISTORICAL_DECLARED_COMPLETE, "new_count_effect": 0,
    }, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError) as error:
        print(f"Central metadata build failed: {error}", file=sys.stderr)
        raise SystemExit(2)


