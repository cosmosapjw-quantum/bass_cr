import os,tempfile
from pathlib import Path
import numpy as np
from bass_foundations.radial_basis import RadialSpec,atomic_bank
from cr_repro.observables import projectile_speed_au
import integration_runtime as ir


def test_real_analytic_worker_computes_full18_shaped_payload(tmp_path):
    build=os.environ.get('BASS_TEST_ANALYTIC_BUILD')
    if not build: raise RuntimeError('BASS_TEST_ANALYTIC_BUILD required')
    bank=atomic_bank(RadialSpec(radius=4,elements=3,degree=3,lmax=1,bound_nmax=1,positive_per_l=0,positive_emax=2,quad_order=6,grading=2))
    cfg={'speed':projectile_speed_au(100.),'b_a0':2.0,'same_center_order':12}
    ir.worker_init(cfg,bank,build,'ctx',tmp_path)
    from bass_foundations.two_center import Trajectory
    tr=ir._STATE['trajectory'];physics={'basis':'small','engine':ir._STATE['kernel'].receipt['library_sha256'],'same_center_order':12}
    role=ir.role_request('reference',-4.,0.,8,1,tr,bank[0].edges,physics,phase_budget=24.)
    got=ir.worker_task(role)
    assert got['reused'] is False
    rec,arr=ir.load_numeric_task(tmp_path,role['numerical_task_id'],'ctx')
    n=2*len(ir._STATE['channels'])//2
    assert rec['metadata']['backend']=='EXACT_SP_MOMENTS_CXX_V1'
    assert arr['S'].shape==(len(ir._STATE['channels']),len(ir._STATE['channels']))
    assert np.isfinite(arr['H']).all()
