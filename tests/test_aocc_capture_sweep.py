import json
from pathlib import Path
from scripts.sweep_aocc_capture import sweep

def test_smoke_capture_sensitivity_and_invariants():
    cfg=json.loads((Path(__file__).resolve().parents[1]/'configs/aocc_smoke_100kevu_b2.json').read_text())
    data=sweep(cfg)
    assert data["gate"]=="NOT_EVALUATED"
    rows={r["variant"]:r for r in data["results"]}
    assert all(r["status"]=="completed" for r in rows.values())
    assert all(abs(r["norm"]-1)<1e-8 for r in rows.values())
    assert rows["baseline"]["nbasis"] == rows["eps_max_half"]["nbasis"]
    assert abs(rows["baseline"]["P_projectile_bound"]-rows["eps_max_half"]["P_projectile_bound"])<1e-11
    assert rows["np_plus1"]["nbasis"] > rows["baseline"]["nbasis"]
    assert rows["eps_max_double"]["nbasis"] > rows["baseline"]["nbasis"]
