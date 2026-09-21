import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from cr_repro.tdl import TDLRunner
from cr_repro.aocc import OneElectronAOCC

def test_tdl_smoke(tmp_path):
 cfg=json.loads((ROOT/'configs/tdl_smoke_100kevu_b2.json').read_text());r=TDLRunner(cfg).run(tmp_path/'tdl')
 assert r['status']=='completed';assert 0<=r['analysis']['P_bound_truncated_nmax']<=1.1;assert r['initial']['energy_Eh']<0

def test_aocc_smoke():
 cfg=json.loads((ROOT/'configs/aocc_smoke_100kevu_b2.json').read_text());r=OneElectronAOCC(cfg).run()
 assert r['status']=='completed';assert abs(r['norm']-1)<1e-6;assert 0<=r['P_projectile_bound']<=1.01
