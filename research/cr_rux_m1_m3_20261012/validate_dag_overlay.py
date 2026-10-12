"""Validate actual dependency semantics, including claim-conditional gates."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def dependencies(node, flags):
    deps = set(node["depends_on"])
    for flag, values in node.get("required_if", {}).items():
        if flags.get(flag, False):
            deps.update(values)
    return deps


def graph(nodes, flags):
    by_id = {n["id"]: n for n in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("DUPLICATE_NODE")
    remain = {k: dependencies(n, flags) for k, n in by_id.items()}
    if any(v - by_id.keys() for v in remain.values()):
        raise ValueError("MISSING_DEPENDENCY")
    order = []
    while remain:
        ready = sorted(k for k, values in remain.items() if not values)
        if not ready:
            raise ValueError("CYCLE")
        order.extend(ready)
        for k in ready:
            del remain[k]
        for values in remain.values():
            values.difference_update(ready)
    return by_id, order


def ancestors(by_id, id_, flags):
    done, todo = set(), list(dependencies(by_id[id_], flags))
    while todo:
        k = todo.pop()
        if k not in done:
            done.add(k)
            todo.extend(dependencies(by_id[k], flags))
    return done


def main():
    original = json.loads((BASE / "inputs/REI_ATOMIC_REUSE_DAG_20261012.json").read_text())
    g = json.loads((BASE / "REI_ATOMIC_REUSE_DAG_CR_OVERLAY_20261012.json").read_text())
    local = json.loads((BASE / "NEXT_DAG.json").read_text())
    flags = {"cr_processes_enabled": True, "he_precision_claimed": True, "hh_processes_enabled": True, "spatial_topology_claimed": True}
    by_id, order_off = graph(g["nodes"], {})
    _, order_all = graph(g["nodes"], flags)
    _, local_order = graph(local["nodes"], {})
    sources = [s["id"] for s in g["source_registry"]]
    assert len(sources) == len(set(sources))
    for node in g["nodes"]:
        assert set(node["sources"]) <= set(sources)
    for node in original["nodes"]:
        assert by_id[node["id"]]["status"] == node["status"] == "PROPOSED_NOT_EXECUTED"
        assert by_id[node["id"]]["execution_owner"] == node["execution_owner"]
    off = ancestors(by_id, "RUX16", {})
    enabled = ancestors(by_id, "RUX16", flags)
    assert not {"RUX12", "RUX13", "RUX14", "RUX15", "RUX13_BIND"} & off
    assert {"RUX12", "RUX13", "RUX14", "RUX15", "RUX13_BIND"} <= enabled
    assert "RUX03_CR_SCREEN" in ancestors(by_id, "RUX04", {})
    assert "RUX13_BIND" in ancestors(by_id, "RUX05", {"cr_processes_enabled": True})
    assert "RUX13_BIND" not in ancestors(by_id, "RUX05", {})
    assert "RUX11" not in ancestors(by_id, "RUX03_CR_SCREEN", flags)
    assert g["main_nodes"] and "main_critical_path" not in g
    result = {"status": "PASS_DAG_STRUCTURE_AND_CONDITIONAL_DEPENDENCIES", "global_nodes": len(by_id), "local_nodes": len(local["nodes"]), "original_global_statuses_preserved": True, "source_references_resolved": True, "baseline_cr_off_requires_optional_extensions": False, "enabled_claim_requires_its_extensions": True, "early_screen_before_RUX04": True, "on_requires_native_binding_before_first_interval": True, "baseline_topological_order": order_off, "all_extensions_topological_order": order_all, "local_topological_order": local_order, "scientific_validation": "NOT_IMPLIED_BY_DAG_CHECK"}
    (BASE / "evidence/DAG_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if not k.endswith("order")}))


if __name__ == "__main__":
    main()
