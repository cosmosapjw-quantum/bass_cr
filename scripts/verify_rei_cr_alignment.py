#!/usr/bin/env python3
"""Check the read-only BASS-CR -> REI mission DAG projection, not physics acceptance."""
from __future__ import annotations
import json
from pathlib import Path
DAG=Path(__file__).resolve().parents[1]/"governance"/"REI_CR_CONSUMER_DAG.v1.json"
def validate(d:dict)->None:
    assert d["schema"]=="bass_cr_rei_consumer_dag_v1"
    assert d["authority"]["owner"]=="cosmosapjw-quantum/rei_bianchi"
    assert d["authority"]["canonical_delta"]==0
    assert d["authority"]["working_is_not_additive"] is True
    assert d["authority"]["receipt"] is None
    assert d["baseline"]["CR"]=="OFF"
    assert d["baseline"]["auto_next"] is False
    assert d["baseline"]["production"]=="HOLD"
    a=d["nodes"];by={n["id"]:n for n in a}
    assert len(by)==len(a)==6
    for n in a:
        assert n["optional"] is True
        assert n["status"] not in ("PASS","DONE","PROMOTED")
        assert n["output"]
        assert all(x in by for x in n["deps"])
        assert all(x in d["external"] for x in n["requires"])
    assert by["BCR-02"]["deps"]==[], "CR-OFF must not depend on optional CR source adapter"
    assert set(by["BCR-03"]["deps"])=={"BCR-01","BCR-02"}
    assert "REI:RUX11" in by["BCR-03"]["requires"]
    assert "REI:RUX13" in by["BCR-04"]["requires"]
    assert d["routing"]["CR_after"]=="REI:RUX11"
    active,seen=set(),set()
    def visit(i:str)->None:
        assert i not in active,"cycle in local projection"
        if i in seen:return
        active.add(i)
        for j in by[i]["deps"]:visit(j)
        active.remove(i);seen.add(i)
    for node in a:visit(node["id"])
if __name__=="__main__":
    validate(json.loads(DAG.read_text(encoding="utf-8")))
    print("REI_CR_PROJECTION_STRUCTURE_PASS (no physical EoR or native REI DAG claim)")
