"""Tests for C21D SAME physical photon IC, source impulses, proper clock, gas and binding.

Independent physical reference lives in pinned original C21C vendor source.
No native Rust tests; no claim that EXP equals native PR150 PreparedAbsorption.
"""
import math
import numpy as np
import pytest
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'src'))
from c21d_trilane import (
    one_absorber_endpoint,evaluate_frozen_endpoint,run_common_ic,compare_grid,
    proper_dt,H,initial_atoms,make_cohorts,Y_HE,FIT,cross,BIND_EV,N_H0,
)
from scipy.integrate import quad
from scipy.integrate import solve_ivp


@pytest.mark.parametrize('mode',['BE','EXP'])
@pytest.mark.parametrize('kdt',[0.,.005,.3,7.,1e3])
def test_unique_positive_scalar_frozen_end_root(mode,kdt):
    a0=.2;p0=.5
    a,L=one_absorber_endpoint(p0,a0,kdt,mode)
    assert 0<=a<=a0 and 0<=L<=min(a0,p0)
    assert abs(a+L-a0)<2e-13
    calc=p0*(kdt*a/(1+kdt*a) if mode=='BE' else -math.expm1(-kdt*a))
    assert abs(L-calc)<2e-13


def test_one_absorber_zero_stock_and_bad_mode():
    assert one_absorber_endpoint(.2,0.,3.,'BE')==(0.,0.)
    assert one_absorber_endpoint(0.,.2,3.,'EXP')==(.2,0.)
    with pytest.raises(ValueError):one_absorber_endpoint(.2,0.,3.,'wrong')
    with pytest.raises(ValueError):one_absorber_endpoint(-1.,.2,3.,'BE')


@pytest.mark.parametrize('mode',['BE','EXP','MIDEXP'])
def test_multiabsorber_species_photon_nuclei_electrons(mode):
    p=np.array([.02,.01,.03]);a=np.array([.81,.19,.062,.013,Y_HE-.075])
    assert a[-1]>0
    k=np.array([[2e-12,0,0],[2e-12,3e-12,0],[1e-12,2e-12,4e-12]])
    p0=p.copy();a0=a.copy()
    p1,a1,species,err,calls=evaluate_frozen_endpoint(p,a,k,1e12,mode)
    assert np.array_equal(p,p0) and np.array_equal(a,a0)
    assert (p1>=0).all() and (a1>=0).all() and (species>=0).all()
    h,i,j=species.sum(axis=0)
    assert abs(sum(p0)-sum(p1)-h-i-j)<2e-14
    np.testing.assert_allclose(a1-a0,[-h,h,-i,i-j,j],atol=4e-14)
    assert abs(sum(a1[:2])-1.)<5e-14
    assert abs(sum(a1[2:])-Y_HE)<5e-14
    assert abs((a1[1]+a1[3]+2*a1[4])-(a0[1]+a0[3]+2*a0[4])-h-i-j)<3e-14
    assert err<2e-11 and calls<=160


@pytest.mark.parametrize('mode',['BE','EXP','MIDEXP'])
def test_heii_replenishment_with_initial_zero(mode):
    p=np.array([.02]);a=np.array([.8,.2,.08,0.,0.]);k=np.array([[0.,5e-13,1e-12]])
    p1,a1,e,_,_=evaluate_frozen_endpoint(p,a,k,1e12,mode)
    assert e[0,1]>e[0,2]>0
    assert a1[3]>0 and a1[4]>0
    assert abs(a1[2]+a1[3]+a1[4]-.08)<2e-15


@pytest.mark.parametrize('mode',['BE','EXP','MIDEXP'])
def test_inactive_heii_channel_exact_zero_not_bounded_solver_ghost(mode):
    p=np.array([.003]);a=np.array([.8,.2,.07,.009,Y_HE-.079])
    k=np.array([[2e-12,1e-12,0.]])
    _,a1,e,_,_=evaluate_frozen_endpoint(p,a,k,1e12,mode)
    assert e[0,2]==0.
    assert a1[4]==a[4]


def test_nonphysical_states_rejected_without_mutating_inputs():
    p=np.array([.01]);a=np.array([.8,.2,.07,.009,Y_HE-.079]);k=np.ones((1,3))*1e-12
    before=p.copy(),a.copy(),k.copy()
    with pytest.raises(ValueError):evaluate_frozen_endpoint(p,a,k,-1.,'BE')
    with pytest.raises(ValueError):evaluate_frozen_endpoint(p,a,np.ones((3,3)),-1.,'EXP')
    with pytest.raises(ValueError):evaluate_frozen_endpoint(p,a,np.ones((2,3)),1.,'BE')
    np.testing.assert_array_equal(p,before[0]);np.testing.assert_array_equal(a,before[1]);np.testing.assert_array_equal(k,before[2])


def test_proper_clock_direct_scipy_quad():
    x0=math.log(1/12);dx=.025
    dt=proper_dt(x0,x0+dx)
    ref=quad(lambda xx:1/H(xx),x0,x0+dx,epsabs=.01,epsrel=1e-13)[0]
    assert abs(dt-ref)/ref<5e-14
    with pytest.raises(ValueError):proper_dt(1,0)


def test_fit_vs_binding_cutoff_distinct():
    assert tuple(FIT) != tuple(BIND_EV)
    assert cross(2,54.419999)==0.
    assert cross(2,54.42)>0.


@pytest.mark.parametrize('mode',['BE','EXP','MIDEXP'])
def test_same_source_cohorts_and_global_ledgers(mode):
    res=run_common_ic(mode,8)
    cohorts,nold=make_cohorts(math.log(1/12),.025)
    source_n=sum(c.start_n for c in cohorts[nold:])
    source_u=sum(c.start_n*c.q20*math.exp(-c.birth_x) for c in cohorts[nold:])
    assert res['cohort_names']==[c.name for c in cohorts]
    assert abs(res['source_n']-source_n)<2e-17
    assert abs(res['source_u']-source_u)<2e-15
    assert abs(res['number_res'])<2e-14
    assert abs(res['energy_res'])<6e-13
    assert min(res['photons'])>=0 and min(res['gas'])>=0
    assert min(res['events'])>=0 and min(res['heat_ev_H'])>=0
    assert res['max_root_residual']<2e-11


@pytest.mark.parametrize('mode',['BE','EXP','MIDEXP'])
def test_absorption_off_keeps_nonnegative_positive_births_and_exact_work(mode):
    res=run_common_ic(mode,4,opacity_scale=0.)
    assert res['events']==[0.,0.,0.]
    assert res['heat_ev_H']==[0.,0.,0.]
    assert abs(res['number_res'])<2e-14
    assert abs(res['energy_res'])<8e-13
    assert min(res['photons'])>=0


@pytest.mark.parametrize('mode',['BE','EXP','MIDEXP'])
def test_rate_stays_finite_at_required_true_physical_endpoint(mode):
    # Near-depleted end is allowed as a physical state without an artificial
    # neutral fraction floor or division by an endpoint population.
    res=run_common_ic(mode,8,opacity_scale=.005)
    assert all(math.isfinite(x) for x in res['gas']+res['photons']+res['events'])
    assert abs(res['energy_res'])<1e-12


def test_continuous_reference_comparison_and_clocks():
    d=compare_grid((4,8),dx=.025,opacity_scale=.001)
    assert d['controls']['cohorts']==9
    assert abs(d['ref']['photon_mass_res'])<3e-13
    assert abs(d['ref']['energy_res'])<3e-12
    assert len(d['mathematical_photo_lanes'])==3
    for z in d['mathematical_photo_lanes']:
        assert z['cases'][0]['source_n']==z['cases'][1]['source_n']
    assert d['mathematical_photo_lanes'][0]['cases'][0]['source_n']==d['mathematical_photo_lanes'][1]['cases'][0]['source_n']


def test_endpoint_exp_not_equal_prepared_absorption_claim():
    assert 'No literal native PreparedAbsorption data' in compare_grid((2,))['claims']


def test_convergence_comparison_scoped_first_order_after_refinement():
    out=compare_grid((16,32,64),dx=.025,opacity_scale=.001)
    b,e,mid=out['mathematical_photo_lanes']
    assert b['cases'][-1]['state_max_abs_error_vs_radau']<b['cases'][0]['state_max_abs_error_vs_radau']
    assert e['cases'][-1]['state_max_abs_error_vs_radau']<e['cases'][0]['state_max_abs_error_vs_radau']
    for z in (b,e):
        for i in range(2):
            assert .90 < z['cases'][i]['next_error_order'] < 1.04
    assert e['cases'][-1]['state_max_abs_error_vs_radau'] < b['cases'][-1]['state_max_abs_error_vs_radau']


def test_zero_dt_scalar_photon_exactly_preserved():
    assert one_absorber_endpoint(.002,.004,0.,'EXP')==(.004,0.)


def test_bad_scalar_nan_rejected():
    with pytest.raises(ValueError):one_absorber_endpoint(math.nan,.2,4.,'EXP')


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):run_common_ic('BE',0)
    with pytest.raises(ValueError):run_common_ic('EXP',1,opacity_scale=-1)
    with pytest.raises(ValueError):run_common_ic('EXP',4100)


def test_midpoint_exposure_second_order_same_physics():
    out=compare_grid((16,32,64,128),dx=.025,opacity_scale=.001)
    b,e,mid=out['mathematical_photo_lanes']
    assert min(x['source_n'] for x in mid['cases'])==max(x['source_n'] for x in mid['cases'])
    assert mid['cases'][-1]['state_max_abs_error_vs_radau']<e['cases'][-1]['state_max_abs_error_vs_radau']
    assert mid['cases'][-1]['state_max_abs_error_vs_radau']<b['cases'][-1]['state_max_abs_error_vs_radau']
    assert mid['cases'][-1]['state_max_abs_error_vs_radau']<3e-8
    assert 1.85<mid['cases'][-2]['next_error_order']<2.05
    assert max(abs(x['energy_res']) for x in mid['cases'])<3e-13


def test_trapezoidal_exposure_local_third_order_coeff():
    from scipy.integrate import quad
    a0,a1,a2,k0,k1,k2=(.6,.28,-.17,1.2,-.23,.09)
    # The Wolfram-derived leading defect in dt midpoint k * trapezoid A.
    coef=k0*a2/12-k1*a1/12-k2*a0/24
    def A(t):return a0+a1*t+a2*t*t/2
    def k(t):return k0+k1*t+k2*t*t/2
    for dt in [.04,.02,.01]:
        exact=quad(lambda t:A(t)*k(t),0.,dt,epsabs=1e-16)[0]
        approximation=dt*k(dt/2)*(A(0)+A(dt))/2
        measured=(approximation-exact)/(dt**3)
        assert abs(measured-coef)<.0025


def test_midexp_smooth_grid_approaches_quadratic_in_scope():
    out=compare_grid((32,64,128),dx=.0125,opacity_scale=.001)
    mid=out['mathematical_photo_lanes'][2]['cases']
    assert .80 < mid[-2]['next_error_order']/2 < 1.09
    assert mid[-1]['state_max_abs_error_vs_radau']<mid[0]['state_max_abs_error_vs_radau']


def test_no_fabricated_native_owner_certification():
    a=compare_grid((2,))
    assert 'No literal native PreparedAbsorption data' in a['claims']
    assert 'No native C21 production certification' in a['claims']
