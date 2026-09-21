import json
from pathlib import Path
import numpy as np
import pytest
from cr_repro.aocc import OneElectronAOCC
ROOT=Path(__file__).resolve().parents[1]
def config(name):return json.loads((ROOT/f'configs/aocc_{name}_100kevu_b2.json').read_text())
@pytest.mark.parametrize('time',[-3.5,0.,2.1])
def test_batched_integrals_match_original_state_loop(time):
    obj=OneElectronAOCC(config('smoke'))
    for got,want in zip(obj.matrix(time),obj.matrix_reference(time)):
        np.testing.assert_allclose(got,want,rtol=1e-11,atol=1e-12)

def test_whole_trajectory_matches_original_dynamics():
    cfg=config('smoke');old=OneElectronAOCC(cfg);old.matrix=old.matrix_reference
    ref=old.run();got=OneElectronAOCC(cfg).run()
    for field in ('P_projectile_bound','P_target_bound','norm'):
        np.testing.assert_allclose(got[field],ref[field],rtol=1e-10,atol=1e-12)

@pytest.mark.parametrize('basis',['baseline','basis_large'])
def test_production_basis_matrix_parity(basis):
    cfg=json.loads((ROOT/f'configs/aocc_prod_100kevu_b2_{basis}.json').read_text())
    obj=OneElectronAOCC(cfg)
    for time in [obj.t0,0.0,obj.tf]:
        for got,want in zip(obj.matrix(time),obj.matrix_reference(time)):
            np.testing.assert_allclose(got,want,rtol=1e-11,atol=1e-12)
