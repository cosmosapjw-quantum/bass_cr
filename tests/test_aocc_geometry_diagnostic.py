import json
from pathlib import Path
from scripts.diagnose_aocc_basis import diagnose

ROOT=Path(__file__).resolve().parents[1]

def test_geometry_identity_smoke():
    cfg=json.loads((ROOT/'configs/aocc_smoke_100kevu_b2.json').read_text())
    rec=diagnose(cfg,[0.0])
    g=rec['geometry'][0]
    assert rec['basis_dimension']>0
    assert g['overlap_min_eigenvalue']>0
    assert g['moving_basis_identity_defect'] < 1e-5
    assert g['hamiltonian_hermiticity_defect'] < 1e-10
    assert 0 <= g['max_target_projectile_bound_subspace_overlap'] <= 1+1e-10
