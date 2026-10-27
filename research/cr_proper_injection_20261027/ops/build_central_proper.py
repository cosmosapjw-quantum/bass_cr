#!/usr/bin/env python3
"""Build two local additive central files and a separate preservation proof.

This is an offline metadata builder, not a publisher or scientific calculation.
The caller supplies a freshly retrieved DAG, the final owner-return JSON, and
the central HEAD observed for those inputs. No HEAD is hard-coded.

Example (root supplies the real files, identities and a new output location):
    python ops/build_central_proper.py \
      --dag /absolute/latest/DAG.json \
      --owner-return /absolute/final/CR_PROPER_INJECTION_20261027.json \
      --central-head ACTUAL_LATEST_CENTRAL_SHA \
      --output-dir /absolute/new/central_candidate \
      --proof-file /absolute/new/central_candidate_proof.json

Only DAG.json and returns/CR_PROPER_INJECTION_20261027.json are written beneath
output-dir. proof-file must be outside it. All outputs are create-only.
Existing central return files are neither read nor changed here. The publisher
must apply these two files onto the refreshed existing central tree, check that
the new return path is absent, and retain every other tree entry. This two-file
candidate must never be treated as a replacement for the complete central tree.

Author: /root/source_qualification (metadata author, not independent reviewer).
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
LINK_KEY = "owner_return_proper_injection_20261027"
RETURN_RELATIVE = "returns/CR_PROPER_INJECTION_20261027.json"
EXPECTED_NODES = 88
EXPECTED_EDGES = 17
PRESERVED_DECLARED_COMPLETE = 27


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
    return value


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
    return target_index, nodes, edges


def validate_owner_return(owner_return: dict[str, Any], central_head: str) -> dict[str, str]:
    require(owner_return.get("parent_node") == TARGET_ID,
            "owner-return parent_node must be the original external-interface target")
    require(owner_return.get("owner_repository") == "cosmosapjw-quantum/bass_cr",
            "owner-return owner_repository must be cosmosapjw-quantum/bass_cr")
    unit_id = owner_return.get("unit_id")
    require(isinstance(unit_id, str) and bool(unit_id.strip()), "owner-return unit_id required")
    science = git_sha(owner_return.get("science_commit_S"), "science_commit_S")
    documents = git_sha(owner_return.get("documents_commit_D"), "documents_commit_D")

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
    fixed_int(original.get("declared_deliverable_count"), PRESERVED_DECLARED_COMPLETE,
              "original_DAG.declared_deliverable_count")
    fixed_int(original.get("new_count_effect"), 0, "original_DAG.new_count_effect")

    return {"unit_id": unit_id, "source_file": RETURN_RELATIVE, "json_pointer": "",
            "science_commit_S": science, "documents_commit_D": documents}


def preservation_proof(original: dict[str, Any], candidate: dict[str, Any],
                       target_index: int, link: dict[str, str]) -> dict[str, Any]:
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
        "original_nodes": EXPECTED_NODES,
        "original_integration_edges": EXPECTED_EDGES,
        "preserved_declared_deliverable_count": PRESERVED_DECLARED_COMPLETE,
        "declared_count_basis": "Root owner-return accounting; no status-prefix reinterpretation",
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
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--proof-file", required=True, type=Path)
    args = parser.parse_args()

    central_head = git_sha(args.central_head, "--central-head")
    dag_path, dag_raw, dag = input_file(args.dag, "latest central DAG")
    return_path, return_raw, owner_return = input_file(args.owner_return, "final owner return")
    target_index, _, _ = validate_dag(dag)
    link = validate_owner_return(owner_return, central_head)
    out = args.output_dir.resolve()
    proof_path = args.proof_file.resolve()
    require(not out.exists(), "--output-dir must be a new create-only directory")
    require(not proof_path.exists(), "--proof-file already exists")
    require(out != proof_path and out not in proof_path.parents,
            "--proof-file must be outside the two-file candidate directory")
    require(proof_path not in (dag_path, return_path), "Proof path collides with an input")
    require(out not in dag_path.parents and out not in return_path.parents,
            "Candidate output directory must not contain an input")

    candidate = deepcopy(dag)
    candidate["nodes"][target_index][LINK_KEY] = link
    preservation = preservation_proof(dag, candidate, target_index, link)
    candidate_raw = (encode_json(candidate, pretty=True) + "\n").encode("utf-8")
    # Verify the actual JSON roundtrip as well, retaining exact decimal values.
    decoded_candidate = decode_json(candidate_raw, "serialized candidate")
    require(exact_semantic_equal(candidate, decoded_candidate),
            "DAG JSON serialization changed a value")
    preservation_proof(dag, decoded_candidate, target_index, link)

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
        dag, decode_json(written_dag, "written DAG"), target_index, link)
    require(exact_semantic_equal(preservation, actual_preservation),
            "Written-candidate preservation proof differs")
    require(dag_path.read_bytes() == dag_raw and return_path.read_bytes() == return_raw,
            "An input changed during the offline build; candidate requires refreshed review")

    proof = {
        "schema": "CR_PROPER_CENTRAL_ADDITIVE_BUILD_PROOF_V1",
        "status": "PASS_SCOPED_OFFLINE_METADATA_BUILD",
        "central_head_supplied_by_root": central_head,
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
        ],
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
            "metadata_author": "/root/source_qualification",
            "author_is_independent_reviewer": False,
            "status": "PENDING_DIFFERENT_REVIEWER",
            "scope": "Fresh theory reviewer checks exact final candidate, root-supplied return "
                     "evidence, publication parent and PR108/B3h preservation.",
        },
        "new_scientific_execution": 0,
        "old_science_replay": 0,
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
        "declared_complete": PRESERVED_DECLARED_COMPLETE, "new_count_effect": 0,
    }, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError) as error:
        print(f"Central metadata build failed: {error}", file=sys.stderr)
        raise SystemExit(2)

