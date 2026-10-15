import json
from pathlib import Path
from scripts.sweep_aocc_basis_metadata import sweep
def test_sweep_has_distinct_pseudostate_and_bound_variants():
    cfg=json.loads((Path(__file__).resolve().parents[1]/'configs/aocc_smoke_100kevu_b2.json').read_text())
    out=sweep(cfg)
    base=out['records'][0]
    assert len(out['records'])==5
    assert out['not_a_capture_probability_or_convergence_test']
    assert all(r['nbasis']>=2*r['negative_per_center'] for r in out['records'])
    assert out['records'][-1]['nbasis']>=base['nbasis']
