"""Real small-FEM integration test; no 18-channel historical rerun."""
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import os
import numpy as np
import pytest
import qualification_runtime as qr
import run_full_geometry_qualification as runner
from bass_foundations.radial_basis import RadialSpec,atomic_bank
from cr_repro.observables import projectile_speed_au
from build_native import build

@pytest.fixture(scope='module')
def native_dir(tmp_path_factory):
    existing=os.environ.get('BASS_TEST_NATIVE_BUILD')
    if existing:return str(Path(existing).resolve())
    directory=tmp_path_factory.mktemp('native')/'build'
    build(directory)
    return str(directory)


def test_real_spawn_geometry_and_checkpoint_reuse(tmp_path,native_dir):
    bank=atomic_bank(RadialSpec(radius=4.,elements=4,degree=4,lmax=0,bound_nmax=1,positive_per_l=0))
    config={'energy_keV_per_u':100.,'b_a0':2.,'epsilon_z_a0':1e-4,'phase_budget_rad':24.,'phase_order':24,
        'reference_orders':[32,40],'candidate_orders':[24,32,40],'same_center_order':20,'speed':projectile_speed_au(100.),
        'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8}}
    context={'scope':'small basis integration smoke','basis':[m.identity for m in bank]}
    cid=qr._digest(context);old=tmp_path/'first';old.mkdir();new=tmp_path/'second';new.mkdir();ids=[]
    ctx=mp.get_context('spawn')
    with ProcessPoolExecutor(max_workers=2,mp_context=ctx,initializer=qr.worker_init,initargs=(config,bank,native_dir,cid,str(old))) as pool:
        def ensure(specs):
            filled=[]
            for s in specs:
                s=dict(s);s['task_id']=qr.task_identity(s['method'],s['z_center_a0'],s['dz_a0'],context,
                    reference_order=s.get('reference_order'),candidate_order=s.get('candidate_order'))
                ids.append(s['task_id']);filled.append(s)
            results=list(pool.map(qr.worker_task,filled))
            assert all(not r['reused'] for r in results)
            return [qr.task_row(old,s['task_id'],cid) for s in filled]
        result=runner.execute_geometry_policy(-2.,config,config['epsilon_z_a0']/config['speed'],ensure)
    assert result['status']=='GEOMETRY_QUALIFIED'
    assert result['qualified_candidate_order']==24
    assert result['qualified_reference_order']==40
    assert len(ids)==9
    assert qr.restore_tasks(old,new,cid,set(ids))==9
    spec=runner.candidate_task_specs(-2.,config,context)[1]
    with ProcessPoolExecutor(max_workers=1,mp_context=ctx,initializer=qr.worker_init,initargs=(config,bank,native_dir,cid,str(new))) as pool:
        reused=pool.submit(qr.worker_task,spec).result(timeout=60)
    assert reused['reused'] is True
    _,a=qr.load_task(old,spec['task_id'],cid);_,b=qr.load_task(new,spec['task_id'],cid)
    for k in a:np.testing.assert_array_equal(a[k],b[k])
