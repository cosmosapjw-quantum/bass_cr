import os
import pytest
import numpy as np
from analytic_moments import moments

def test_exact_ring_polynomials_against_uniform_phi():
    k=np.array([0.,.001,1.,18.5,128.5,200.])
    phi=np.arange(8192)*(2*np.pi/8192);c,s=np.cos(phi),np.sin(phi)
    p=np.array([np.ones_like(c),c,c*c,s*s,c**3,c*s*s])
    ref=(np.exp(1j*k[:,None]*c)@p.T)*(2*np.pi/len(phi))
    np.testing.assert_allclose(moments(k),ref,rtol=2e-12,atol=5e-14)

from pathlib import Path
from bass_foundations.radial_basis import RadialSpec,atomic_bank
from bass_foundations.two_center import Trajectory,symmetric_channels
from aligned_cross import cross_blocks
from exact_cross import cross,MomentKernel,KEYS

@pytest.fixture(scope='module')
def kernel():
    return MomentKernel(os.environ.get('BASS_MOMENT_BUILD',Path(__file__).resolve().parents[1]/'native_build_final'))

@pytest.fixture(scope='module')
def small():
    bank=atomic_bank(RadialSpec(radius=10.,elements=6,lmax=1,bound_nmax=2,positive_per_l=1))
    return symmetric_channels(bank)

@pytest.mark.parametrize('z,vel',[(0.,((0,0,0),(0,0,2.))),(-2.,((.2,-.1,.3),(-.3,.2,1.2))),(3.,((0,0,0),(0,0,0)))])
def test_analytic_raw_six_blocks_against_unpruned_ring(small,kernel,z,vel):
    tr=Trajectory(((.3,-.2,.4),(2.3,-.2,z+.4)),vel)
    ref=cross_blocks(tr,small,small[0].radial.edges,.13,order=8)
    actual=cross(tr,small,.13,kernel,order=8,batch=91)
    for k in KEYS:
        np.testing.assert_allclose(actual[k],ref[k],rtol=3e-11,atol=2e-13,err_msg=k)

def test_recurrence_and_zero_limit_against_general_bessel_evaluator():
    from scipy.special import jv
    k=np.r_[0.,1e-12,.001,np.linspace(3.99,4.01,20),np.linspace(4,250,2001)]
    j0,j1,j2,j3=jv(np.arange(4)[:,None],k[None,:])
    expected=np.array([2*np.pi*j0,2j*np.pi*j1,np.pi*(j0-j2),np.pi*(j0+j2),.5j*np.pi*(3*j1-j3),.5j*np.pi*(j1+j3)]).T
    np.testing.assert_allclose(moments(k),expected,rtol=5e-11,atol=4e-14)

@pytest.mark.parametrize('bad',[[np.nan],[-1.],[np.inf],[[1.]]])
def test_invalid_moments_are_rejected(bad):
    with pytest.raises(ValueError):moments(bad)

def test_channel_permutation_preserves_all_raw_blocks(small,kernel):
    shuffled=tuple(small[i] for i in np.random.default_rng(62).permutation(len(small)))
    tr=Trajectory(((0,0,0),(2,0,0)),((.1,.2,.3),(.2,-.1,1.3)))
    a=cross_blocks(tr,shuffled,shuffled[0].radial.edges,-.4,order=6)
    b=cross(tr,shuffled,-.4,kernel,order=6,batch=31)
    for k in KEYS:np.testing.assert_allclose(a[k],b[k],rtol=4e-11,atol=2e-13)

def test_incomplete_multiplet_uses_general_complex_kernel(small,kernel):
    subset=tuple(c for c in small if c.m!=1)
    tr=Trajectory(((0,0,0),(2,0,-1)),((.1,.2,.3),(.2,-.1,1.3)))
    a=cross_blocks(tr,subset,subset[0].radial.edges,.1,order=6)
    b=cross(tr,subset,.1,kernel,order=6)
    assert b['metadata']['cartesian_specialization'] is False
    for k in KEYS:np.testing.assert_allclose(a[k],b[k],rtol=4e-11,atol=2e-13)

def test_disjoint_support_is_exact_zero(small,kernel):
    a=cross(Trajectory(((0,0,0),(50,0,0))),small,0.,kernel,order=6)
    assert all(np.count_nonzero(a[k])==0 for k in KEYS)

def test_native_binary_tampering_is_rejected(tmp_path):
    import shutil,json
    src=Path(os.environ.get('BASS_MOMENT_BUILD',Path(__file__).resolve().parents[1]/'native_build_final'))
    shutil.copy2(src/'BUILD.json',tmp_path/'BUILD.json');shutil.copy2(src/'libmoments.so',tmp_path/'libmoments.so')
    p=tmp_path/'libmoments.so';p.write_bytes(p.read_bytes()+b'x')
    with pytest.raises(ValueError,match='identity'):MomentKernel(tmp_path)

def test_disjoint_even_sector_has_correct_reduced_shape(small,kernel):
    a=cross(Trajectory(((0,0,0),(50,0,0))),small,0.,kernel,order=6,sector='even')
    assert a['S_tp'].shape==(7,7)
    assert a['metadata']['sector']=='even'
    assert all(np.count_nonzero(a[k])==0 for k in KEYS)

def test_disjoint_does_not_bypass_symmetry_guard(small,kernel):
    tr=Trajectory(((0,0,0),(50,0,0)),((0,0,0),(0,.1,1.)))
    with pytest.raises(ValueError,match='planar'):cross(tr,small,0.,kernel,order=6,sector='even')

def test_complex_radial_payload_is_not_silently_discarded(small,kernel):
    from dataclasses import replace
    bad=list(small)
    radial=replace(bad[0].radial,polynomial_coefficients=np.asarray(bad[0].radial.polynomial_coefficients,complex))
    bad[0]=replace(bad[0],radial=radial)
    with pytest.raises(ValueError,match='real radial'):cross(Trajectory(((0,0,0),(2,0,0))),bad,0.,kernel,order=6)

def test_repeated_identity_with_different_coefficients_is_rejected(small,kernel):
    from dataclasses import replace
    bad=list(small)
    # Same radial ID occurs on both centres. A stale ID must not alias a changed array.
    i=next(i for i,c in enumerate(bad) if c.center==1 and c.radial.identity==bad[0].radial.identity)
    r=bad[i].radial
    bad[i]=replace(bad[i],radial=replace(r,polynomial_coefficients=r.polynomial_coefficients*1.001))
    with pytest.raises(ValueError,match='identity'):cross(Trajectory(((0,0,0),(2,0,0))),bad,0.,kernel,order=6)
