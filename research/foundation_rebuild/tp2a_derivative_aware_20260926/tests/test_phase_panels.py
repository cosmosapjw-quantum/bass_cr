import numpy as np
import pytest
from phase_panels import phase_split_edges
from bass_foundations.radial_basis import RadialSpec,atomic_bank
from bass_foundations.two_center import Trajectory,symmetric_channels
from fast_cross import fast_cross as original
from fast_cross_phase import fast_cross as candidate


def test_existing_radial_elements_are_split_before_gauss_rule_underresolves_phase():
    e=64.*(np.arange(41)/40.)**2
    R=np.sqrt(40.);vparallel=2.00798106651023*(-6.)/R
    q=phase_split_edges(e,R,vparallel,max_phase=24.)
    coeff=abs(vparallel)/(2*R)
    assert np.all(coeff*np.diff(q*q)<=24.*(1+2e-14))
    assert len(q)>len(e)
    assert all(np.any(q==x) for x in e)
    assert q[0]==0 and q[-1]==64 and np.all(np.diff(q)>0)


@pytest.mark.parametrize('sep,velocity,budget',[(2.,0.,24.),(6.3,2.,0.),(-2.,2.,24.),(2.,float('nan'),24.)])
def test_zero_phase_and_invalid_inputs(sep,velocity,budget):
    e=np.array([0.,1.,3.])
    if velocity==0:
        np.testing.assert_array_equal(phase_split_edges(e,sep,velocity,budget),e)
    else:
        with pytest.raises(ValueError):phase_split_edges(e,sep,velocity,budget)


def test_subdivision_does_not_change_exact_lens_volume():
    from aligned_cross import geometry_pairs,intersection_volume
    e=np.array([0.,.2,.8,2.,5.]);R=1.7
    mesh=phase_split_edges(e,R,2.1,3.)
    volume=sum(float(np.sum(w))*2*np.pi for r0,r1,w in geometry_pairs(mesh,R,8))
    assert abs(volume/intersection_volume(5.,R)-1)<1e-13


def test_no_subdivision_path_matches_immutable_original():
    bank=atomic_bank(RadialSpec(radius=4,elements=4,degree=4,lmax=0,bound_nmax=1))
    ch=symmetric_channels(bank);tr=Trajectory(((0,0,0),(2,0,-1)),((0,0,0),(0,0,1.3)))
    a=original(tr,ch,bank[0].edges,.1,order=8)
    b=candidate(tr,ch,bank[0].edges,.1,order=8,phase_budget=None)
    for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt'):
        np.testing.assert_array_equal(a[k],b[k])


def test_subdivision_keeps_raw_coulomb_and_direct_D():
    bank=atomic_bank(RadialSpec(radius=4,elements=4,degree=4,lmax=0,bound_nmax=1))
    ch=symmetric_channels(bank);tr=Trajectory(((0,0,0),(2,0,-1)),((.1,0,.2),(0,0,1.3)))
    a=original(tr,ch,bank[0].edges,.1,order=32)
    b=candidate(tr,ch,bank[0].edges,.1,order=24,phase_budget=2.)
    for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt'):
        np.testing.assert_allclose(a[k],b[k],rtol=2e-11,atol=2e-13)
