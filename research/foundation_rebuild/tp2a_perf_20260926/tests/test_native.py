from pathlib import Path
import numpy as np
import pytest
from build_native import build
from native_ring import NativeRing
from fast_cross import ring_basis,fast_cross
from bass_foundations.radial_basis import RadialSpec,atomic_bank
from bass_foundations.two_center import Trajectory,symmetric_channels

@pytest.fixture(scope='module')
def native(tmp_path_factory):
    p=tmp_path_factory.mktemp('native')/'build';build(p);return NativeRing(p)

@pytest.fixture(scope='module')
def basis():
    b=atomic_bank(RadialSpec(radius=10,elements=6,lmax=1,bound_nmax=2,positive_per_l=1))
    return symmetric_channels(b),b[0].edges

def test_native_every_complex_component(native,basis):
    ch,_=basis;ch=ch[:len(ch)//2]
    rng=np.random.default_rng(67);r=rng.uniform(.02,9.99,31);xyz=rng.normal(size=(31,9,3));xyz*=r[:,None,None]/np.linalg.norm(xyz,axis=-1)[:,:,None]
    vel=np.array([.4,-.2,1.8])
    for got,ref in zip(native(r,xyz,ch,vel),ring_basis(r,xyz,ch,vel)):
        np.testing.assert_allclose(got,ref,rtol=2e-13,atol=2e-13)

def test_native_full_cross(native,basis):
    ch,e=basis;tr=Trajectory(((0,0,0),(2,0,0)),((.1,.2,.3),(.2,-.1,2.)))
    ref=fast_cross(tr,ch,e,-.2,order=6);got=fast_cross(tr,ch,e,-.2,order=6,evaluator=native)
    for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt'):
        np.testing.assert_allclose(got[k],ref[k],atol=1e-13,rtol=2e-12)

def test_native_hash_tamper_rejected(tmp_path):
    p=tmp_path/'build';build(p)
    lib=p/'libring_sp.so';lib.write_bytes(lib.read_bytes()+b'tampered')
    with pytest.raises(ValueError,match='identity'):NativeRing(p)

def test_native_bad_shape_rejected(native,basis):
    with pytest.raises(ValueError,match='shape'):
        native(np.ones(2),np.zeros((1,9,3)),basis[0][:9],np.zeros(3))
