"""One structural/provenance comparison of the updated DAG; no science runs."""
from __future__ import annotations

from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import platform
import time

ROOT = Path(__file__).resolve().parents[1]
SELECTED = "CR_THEORY_SELF_CONSISTENT_FEEDBACK"
NEW = (
    "CR_THEORY_KERNEL_EVENT_ADAPTER",
    "CR_THEORY_THERMAL_CUTOFF_FEEDBACK",
    "CR_FEEDBACK_SELECTED_APPLICATION",
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode())


def main():
    started = time.perf_counter()
    prior_bytes = (ROOT / "inputs/prior/NEXT_DAG.json").read_bytes()
    current_bytes = (ROOT / "NEXT_DAG.json").read_bytes()
    prior, current = json.loads(prior_bytes), json.loads(current_bytes)
    reuse = json.loads((ROOT / "inputs/PRIOR_REUSE.json").read_text())
    source = next(row for row in reuse["files"] if row["copy"] == "inputs/prior/NEXT_DAG.json")
    old = {node["id"]: node for node in prior["nodes"]}
    new = {node["id"]: node for node in current["nodes"]}
    old_ids = list(old)
    checks = []

    def check(name, condition, detail):
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    check("prior_source_byte_identity",
          digest(prior_bytes) == source["sha256"] and len(prior_bytes) == source["bytes"],
          {"bytes": len(prior_bytes), "sha256": digest(prior_bytes),
           "authority": "inputs/PRIOR_REUSE.json",
           "source_science_commit": reuse["source_science_commit"]})
    check("baseline_and_new_counts",
          len(prior["nodes"]) == 30 and len(prior["edges"]) == 53
          and len(current["nodes"]) == 33 and len(current["edges"]) == 60
          and len(new) == 33,
          {"prior_nodes": 30, "prior_edges": 53, "current_nodes": len(current["nodes"]),
           "current_edges": len(current["edges"])})
    unchanged = [node_id for node_id in old if node_id != SELECTED and new.get(node_id) == old[node_id]]
    check("all_29_unselected_node_objects_preserved",
          len(unchanged) == 29 and set(unchanged) == set(old) - {SELECTED},
          {"count": len(unchanged), "meaning": "exact JSON object-value equality",
           "canonical_preserved_nodes_sha256": canonical([old[k] for k in unchanged])})
    hist = current["preservation"]
    check("selected_transition_and_historical_provenance",
          old[SELECTED]["status"] == "READY"
          and new[SELECTED]["status"] == "ACCEPTED_CONDITIONAL_CONSTRUCTION"
          and hist["prior_selected_ready_node"]["object"] == old[SELECTED]
          and hist["historical_prior_preservation"] == prior["preservation"]
          and hist["unchanged_prior_node_count"] == 29,
          {"selected": SELECTED, "from": old[SELECTED]["status"],
           "to": new[SELECTED]["status"],
           "prior_ready_canonical_sha256": canonical(old[SELECTED])})
    check("all_53_prior_edge_objects_preserved",
          current["edges"][:53] == prior["edges"],
          {"old_edge_objects": 53, "additional_edges": len(current["edges"]) - 53})
    edge_pairs = [(edge["from"], edge["to"]) for edge in current["edges"]]
    dependencies = [(dep, node["id"]) for node in current["nodes"] for dep in node.get("depends_on", [])]
    references_valid = all(a in new and b in new for a, b in edge_pairs)
    check("edge_dependency_identity_and_references",
          references_valid and Counter(edge_pairs) == Counter(dependencies)
          and len(set(edge_pairs)) == len(edge_pairs),
          {"all_node_references_exist": references_valid,
           "edge_pairs_match_declared_dependencies": Counter(edge_pairs) == Counter(dependencies)})
    indegree = {node_id: 0 for node_id in new}
    adjacency = {node_id: [] for node_id in new}
    for a, b in edge_pairs:
        if a in new and b in new:
            adjacency[a].append(b)
            indegree[b] += 1
    queue = deque(k for k, value in indegree.items() if value == 0)
    order = []
    while queue:
        node_id = queue.popleft()
        order.append(node_id)
        for child in adjacency[node_id]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    check("acyclic", len(order) == 33, {"topological_order": order})
    check("entire_global_overlay_preserved",
          current["global_overlay_snapshot"] == prior["global_overlay_snapshot"]
          and len(current["global_overlay_snapshot"]["nodes"]) == 19,
          {"global_nodes": 19,
           "entire_object_canonical_sha256": canonical(prior["global_overlay_snapshot"])})
    resolution = current["reference_resolution"]
    groups = ("original_source_nodes", "prior_theory_nodes", "current_nodes")
    partition = [node_id for group in groups for node_id in resolution[group]["node_ids"]]
    expected_theory_base = (
        "https://github.com/cosmosapjw-quantum/bass_cr/blob/"
        + reuse["source_science_commit"] + "/research/cr_thermal_evolution_20261012/"
    )
    check("origin_aware_reference_resolution",
          len(partition) == len(set(partition)) == 33 and set(partition) == set(new)
          and resolution["original_source_nodes"]["node_ids"] == old_ids[:22]
          and resolution["original_source_nodes"]["relative_path_base"]
              == prior["reference_resolution"]["inherited_nodes"]["relative_path_base"]
          and resolution["prior_theory_nodes"]["node_ids"] == old_ids[22:29]
          and resolution["prior_theory_nodes"]["relative_path_base"] == expected_theory_base
          and resolution["current_nodes"]["node_ids"] == [SELECTED, *NEW],
          {"original_source_nodes": 22, "prior_theory_nodes": 7, "current_nodes": 4,
           "prior_theory_base": expected_theory_base})
    outputs = new[SELECTED]["outputs"]
    missing = [rel for rel in outputs if not (ROOT / rel).is_file()]
    check("completed_selected_outputs_exist",
          not missing, {"completed_output_count": len(outputs), "missing": missing,
                        "future_node_outputs": "planned, not counted as completed files"})
    preserved_fields = ("consumer_budget", "consumer_status_unchanged",
                        "preserved_scientific_gates", "global_states_promoted", "new_NCP_dispatch")
    check("physical_dependencies_and_gates_preserved",
          all(current[key] == prior[key] for key in preserved_fields)
          and set(new[NEW[2]]["depends_on"]) == {
              SELECTED, NEW[0], "CR_SCENARIO_SOURCE_BINDING", "M1_CONSUMER_ERROR_BUDGET"}
          and current["next_here"] == list(NEW[:2]),
          {"preserved_fields": list(preserved_fields),
           "application_status": new[NEW[2]]["status"], "next_here": current["next_here"]})
    result = {
        "schema": "bass-cr-dag-structural-checks.v1",
        "unit_id": "CR-THEORY-FEEDBACK-20261013",
        "status": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL",
        "scope": "JSON structure, dependency topology and preserved-source provenance only",
        "scientific_validation_claim": False,
        "structural_check_runs": 1,
        "prior_scientific_checks_repeated": 0,
        "new_scientific_runs": 0,
        "checked_current_dag": {"path": "NEXT_DAG.json", "bytes": len(current_bytes),
                                "sha256": digest(current_bytes)},
        "prior_dag": {"path": "inputs/prior/NEXT_DAG.json", "bytes": len(prior_bytes),
                      "sha256": digest(prior_bytes)},
        "final_review_binding_at_check": current["acceptance_update"],
        "checks_passed": sum(row["status"] == "PASS" for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "runtime": {"python": platform.python_version(),
                    "elapsed_seconds": time.perf_counter() - started},
    }
    target = ROOT / "results/DAG_CHECKS.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "structural_checks": len(checks),
                      "nodes": len(new), "edges": len(edge_pairs),
                      "output": str(target)}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

