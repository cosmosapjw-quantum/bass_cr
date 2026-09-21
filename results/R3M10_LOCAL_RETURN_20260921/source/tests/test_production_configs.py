"""Regression checks for supplied production-grid construction failures."""
import json
from pathlib import Path
import numpy as np
import pytest
from cr_repro.grid import GridSpec
ROOT=Path(__file__).resolve().parents[1]
@pytest.mark.parametrize('name',['baseline','dt025','dx03125','plane25','z75','boxwide'])
def test_production_grid_is_integral_and_avoids_coulomb_nodes(name):
    cfg=json.loads((ROOT/f'configs/tdl_prod_100kevu_b2_{name}.json').read_text())
    grid=GridSpec.from_dict(cfg['grid'])
    x,y,z=grid.axes(np)
    # Both nuclei move within y=0. A half-step y offset excludes either singularity at any time.
    assert np.min(np.abs(y)) >= 0.49*grid.dx
    assert cfg['z_stop'] < cfg['grid']['zlim'][1]-cfg['absorber_width']

def test_plane_and_final_separation_are_varied_independently():
    load=lambda n:json.loads((ROOT/f'configs/tdl_prod_100kevu_b2_{n}.json').read_text())
    a,p,z=map(load,['baseline','plane25','z75'])
    assert p['z_stop']==a['z_stop'] and p['capture_plane']!=a['capture_plane']
    assert z['capture_plane']==a['capture_plane'] and z['z_stop']!=a['z_stop']
