"""Tests for SOURCE07 C6 frozen-gas subcell source spectral representation."""
import numpy as np
import pytest
from source_subcells import *

OWNER_RHO=(0.0017575700008892194,0.0001429214010766023,0.)
OWNER_DT=1e10
OWNER_EMISSION=4.298036114764196e-8
OWNER_HEI=1.4281834584030507e-9
OWNER_HI=2.978921350017158e-8
OWNER_HEAT=1.4592997571739564e-7

@pytest.mark.parametrize('n',[64,128,256,512,1024])
def test_owner_source_subcell_vs_independent_continuum(n):
    q=source_quadrature(n)
    a=source_and_reaction(q,OWNER_RHO,OWNER_DT,OWNER_EMISSION)
    ev=a['absorb_species'].sum(axis=1)
    assert abs(ev[0]/OWNER_HI-1)<2e-10
    assert abs(ev[1]/OWNER_HEI-1)<2e-10
    assert abs(a['heat_species'].sum()/OWNER_HEAT-1)<2e-10
    assert abs(q.count-1)<4e-15
    assert abs(a['number_residual'])<2e-21
    assert abs(a['energy_residual_eV'])<2e-20

@pytest.mark.parametrize('n',[64,128,256,512])
def test_owner_centroid_hei_persistent_bias(n):
    q=source_quadrature(n)
    ctl=centroid_control(q,OWNER_RHO,OWNER_DT,OWNER_EMISSION)
    event=float(ctl['absorb_species'][1].sum())
    assert -0.0123 < (event/OWNER_HEI-1) < -0.0118

@pytest.mark.parametrize('n',[64,128,256])
@pytest.mark.parametrize('r',[1.,.95,.75])
def test_source_shape_and_fixed_q_moments_same_physical_source(n,r):
    q=source_quadrature(n,ratio_R=r)
    assert abs(q.count-1)<5e-15
    assert abs(q.physical_energy-20.27659539498146)<2e-10
    N,U=q.number_and_energy()
    assert abs(N.sum()-1)<1e-14
    assert abs(U.sum()*r-q.physical_energy)<1e-12
    res=source_and_reaction(q,OWNER_RHO,OWNER_DT,OWNER_EMISSION)
    assert abs(res['absorb_species'][1].sum()/OWNER_HEI-1)<1e-9

@pytest.mark.parametrize('ratio',[1.0,.998,.8])
def test_verner_numpy_matches_original_scalar_all_species(ratio):
    E=np.asarray([13.6,23.,24.59,37.,54.42,64.,433.,50000.])*ratio
    for k in ION_NAMES:
        old=np.asarray([verner(k,float(e)) for e in E])
        new=verner_numpy(k,E)
        np.testing.assert_allclose(old,new,rtol=5e-15,atol=0)

@pytest.mark.parametrize('n',[64,256])
def test_frozen_hei_and_heii_coupled_nonzero(n):
    gas=(.001,.0001,.00001)
    q=source_quadrature(n)
    res=source_and_reaction(q,gas,1e10)
    reference=source_continuum_reference(gas,1e10)
    for k in range(3):
        assert reference['event'][k]>0
        assert abs(res['absorb_species'][k].sum()/reference['event'][k]-1)<1e-10
        assert abs(res['heat_species'][k].sum()/reference['heat'][k]-1)<1e-10

@pytest.mark.parametrize('k',["HI","HeI","HeII"])
def test_same_number_energy_moments_cannot_determine_opacity(k):
    eth=ATOMIC[k][0]
    e1,e2=eth-.1,eth+.1
    assert verner(k,e1)==0
    # Same number=1, mean energy=eth. Nonlinearity/threshold means different opacity.
    assert abs(.5*e1+.5*e2-eth)<1e-12
    assert abs(.5*verner(k,e1)+.5*verner(k,e2)-verner(k,eth))>0

@pytest.mark.parametrize('args',[(256,1.01),(8,1),(256,0.05)])
def test_wrong_reference_grid_source_ownership_rejected(args):
    with pytest.raises(ValueError):source_quadrature(*args)

def test_binding_distinct_from_fit_threshold():
    assert all(PHYSICAL_BINDING[j]<ATOMIC[ion][0] for j,ion in enumerate(ION_NAMES))
    q=source_quadrature(256)
    res=source_and_reaction(q,(.001,.0001,.00001),1e9)
    np.testing.assert_allclose(res['binding_species'].sum(axis=1),res['absorb_species'].sum(axis=1)*np.asarray(PHYSICAL_BINDING),rtol=1e-14)

def test_vectorized_across_separate_gas_states_equals_scalar():
    q=cached_source_kernel(256)
    rng=np.random.default_rng(20261015)
    gas=rng.uniform(1e-9,2e-3,size=(17,3))
    dt=rng.uniform(1e7,1e11,size=17)
    ev,heat=batched_frozen_reactions(q,gas,dt,emitted_per_H=OWNER_EMISSION,batch_size=5)
    for i in range(17):
        es,hs=scalar_frozen_reactions(q,gas[i],float(dt[i]),OWNER_EMISSION)
        np.testing.assert_allclose(ev[i],es,rtol=1e-12,atol=1e-28)
        np.testing.assert_allclose(heat[i],hs,rtol=1e-12,atol=1e-27)


def test_cached_quad_readonly_and_reused():
    a=cached_source_kernel(128)
    b=cached_source_kernel(128)
    assert a is b
    with pytest.raises(ValueError):a.sigma_cm2[0,0]=0.0
    with pytest.raises(ValueError):a.quad.photon_weight_per_initial_H[0]=0.


def test_batch_rejects_invalid_physics():
    q=cached_source_kernel(64)
    with pytest.raises(ValueError):batched_frozen_reactions(q,np.ones((2,3)),np.ones(1))
    with pytest.raises(ValueError):batched_frozen_reactions(q,np.array([[-1.,0.,0.]]),np.ones(1))
    with pytest.raises(ValueError):batched_frozen_reactions(q,np.ones((2,3)),np.ones(2),batch_size=0)

@pytest.mark.parametrize('n',[64,256])
def test_scalar_uncached_and_cached_match_vector_all_moments(n):
    r=cached_source_kernel(n)
    gas=(.001,.000142,.00001)
    t=1e10
    a,b=scalar_frozen_reactions(r,gas,t)
    c,d=scalar_cached_reactions(r,gas,t)
    e,h=batched_frozen_reactions(r,[gas],[t])
    np.testing.assert_allclose(a,c,rtol=1e-13,atol=1e-29)
    np.testing.assert_allclose(b,d,rtol=1e-13,atol=1e-29)
    np.testing.assert_allclose(a,e[0],rtol=1e-13,atol=1e-29)
    np.testing.assert_allclose(b,h[0],rtol=1e-13,atol=1e-29)

@pytest.mark.parametrize('kind',["HeI","HeII"])
@pytest.mark.parametrize('eps',[1e-2,1e-4,1e-6])
def test_same_N_U_but_different_threshold_reaction(kind,eps):
    chi=ATOMIC[kind][0]
    neutral=np.zeros(3);neutral[ION_NAMES.index(kind)]=1e-6
    left,right=np.array([chi-eps,chi+eps]),np.array([chi])
    a,_=reaction_fraction(left,neutral,1e9)
    b,_=reaction_fraction(right,neutral,1e9)
    mi=ION_NAMES.index(kind)
    assert abs(np.mean(left)-chi)<1e-12
    assert a[mi].sum()/2 < b[mi][0]*0.6
    assert a[mi].sum()/2 > b[mi][0]*0.39


def test_real_owner_frozen_source_centroid_values_agree_with_native_rust():
    q=source_quadrature(256)
    g=centroid_control(q,OWNER_RHO,OWNER_DT,OWNER_EMISSION)
    assert abs(g['total_absorbed']-3.12053792820337006e-08)<2e-20
    assert abs(g['total_heat']-1.45995781352239345e-07)<3e-20


def test_external_angular_owner_weight_once_not_recomputed():
    q=source_quadrature(256,ratio_R=.85)
    w=.12345
    res=source_and_reaction(q,OWNER_RHO,OWNER_DT,OWNER_EMISSION*w)
    N,U=q.number_and_energy()
    assert abs(res['emitted_per_H']/OWNER_EMISSION/w-1)<5e-15
    assert abs(res['physical_energy_per_H']-(U.sum()*.85)*(OWNER_EMISSION*w))<2e-19
    assert abs(res['energy_residual_eV'])<2e-20


@pytest.mark.parametrize('order',[4,8,12,16])
def test_smooth_split_gauss_quadrature_order_for_owner_source(order):
    q=source_quadrature(128,order=order)
    ev=source_and_reaction(q,OWNER_RHO,OWNER_DT,OWNER_EMISSION)
    assert abs(ev['absorb_species'][1].sum()/OWNER_HEI-1)<2e-10
    assert abs(ev['heat_species'].sum()/OWNER_HEAT-1)<2e-10
