import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import pytest
import runtime
from bass_foundations.radial_basis import RadialSpec,atomic_bank
from bass_foundations.two_center import symmetric_channels,Trajectory
from full_operator import assemble_full

@pytest.fixture(scope='module')
def bank():return atomic_bank(RadialSpec(radius=6,elements=5,lmax=0,bound_nmax=1,positive_per_l=0))

def cfg():return {'speed':1.2,'b_a0':2.,'cross_order':8,'same_center_order':12,'epsilon_z_a0':1e-4,'screens':{'metric_derivative_relative_max':1.,'metric_min_ratio':1e-8,'operator_hermiticity_relative_max':1e-11}}

def test_full_raw_reference_parity(bank):
    ch=symmetric_channels(bank);tr=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,1.2)))
    a=runtime.fast_full(tr,ch,-2.,order=10,same_order=12);b=assemble_full(tr,ch,-2.,same_order=12,cross_order=10)
    for k in runtime.KEYS:np.testing.assert_allclose(a[k],b[k],atol=1e-13,rtol=2e-12)

def test_atomic_create_only(tmp_path):
    p=tmp_path/'a.json';runtime.write_json(p,{'x':1})
    with pytest.raises(FileExistsError):runtime.write_json(p,{'x':2})
    assert p.read_text().find('1')>=0
    assert not list(tmp_path.glob('.partial_*'))

def test_bank_roundtrip_bytes(bank,tmp_path):
    runtime.save_bank(tmp_path,bank);b,r=runtime.load_bank(tmp_path)
    for a,c in zip(bank,b):
        assert a.identity==c.identity
        assert a.polynomial_coefficients.tobytes()==c.polynomial_coefficients.tobytes()
        assert not c.polynomial_coefficients.flags.writeable

def test_bank_corruption_fails(bank,tmp_path):
    runtime.save_bank(tmp_path,bank);p=tmp_path/'BASIS.npz';p.write_bytes(p.read_bytes()+b'bad')
    with pytest.raises(ValueError,match='identity'):runtime.load_bank(tmp_path)

def test_spawn_and_serial_exact_parity(bank,tmp_path):
    a=tmp_path/'serial';b=tmp_path/'parallel';a.mkdir();b.mkdir();conf=cfg();ident='same'
    runtime.worker_init(conf,bank,ident,str(a),None,None,None)
    direct=runtime.worker_geometry(-3.)
    with ProcessPoolExecutor(max_workers=2,mp_context=mp.get_context('spawn'),initializer=runtime.worker_init,initargs=(conf,bank,ident,str(b),None,None,None)) as pool:
        future=pool.submit(runtime.worker_geometry,-3.);parallel=future.result(timeout=60)
    assert direct['metric_connection_relative']==parallel['metric_connection_relative']
    for p in (a/'nodes').glob('*.json'):
        import json
        t=float.fromhex(json.loads(p.read_text())['time_hex'])
        x,_=runtime.load_node(a,t,ident);y,_=runtime.load_node(b,t,ident)
        for k in runtime.KEYS:np.testing.assert_array_equal(x[k],y[k])

def test_resume_validates_bytes_and_avoids_reintegration(bank,tmp_path,monkeypatch):
    a=tmp_path/'old';b=tmp_path/'new';a.mkdir();b.mkdir();runtime.worker_init(cfg(),bank,'abc',str(a),None,None,None);runtime.worker_geometry(-3.)
    assert runtime.restore_nodes(a,b,'abc')==3
    runtime.worker_init(cfg(),bank,'abc',str(b),None,None,None)
    def no_compute(*args,**kw):raise AssertionError('recomputed persisted node')
    monkeypatch.setattr(runtime,'fast_full',no_compute)
    r=runtime.worker_geometry(-3.);assert r['new_operator_evaluations']==0
    with pytest.raises(ValueError,match='identity'):runtime.restore_nodes(a,tmp_path/'bad','different')
