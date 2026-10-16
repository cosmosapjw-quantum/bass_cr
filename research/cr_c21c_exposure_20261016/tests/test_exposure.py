"""C21C R5/C5/C6/C7/C8 independently falsifiable validations."""
from __future__ import annotations
import math
import pytest
import numpy as np
from scipy.integrate import solve_ivp
from exposure_contract import (
 exact_pair_exposure,native_photo_rates,pair_to_native,q20_to_qref,energy_from_qref,
 BIND_EV,EV_ERG,exprelminus
)
from radau_exposure_oracle import run_reference,VERNER,cross,make_cohorts
from compare_c21b import run_split_reference


@pytest.mark.parametrize('n,a,k,dt',[
 (1.,.1,3.,2.),(.1,1.,3.,2.),(.1,.1,3.,2.),
 (.9,.5000000000000001,2.,.3),(.1,0.,3.,2.),(0.,.1,3.,2.),
 (.1,.1,0.,2.),(.1,.1,3.,0.),(.01,.01,1e-7,1e-5)
])
def test_pair_invariants_and_exposure(n,a,k,dt):
    p=exact_pair_exposure(n,a,k,dt)
    assert p.events_per_H>=0
    assert p.photon_after>=0 and p.absorber_after>=0
    assert abs((p.photon_after-p.absorber_after)-(n-a))<2e-15
    assert abs(n-p.photon_after-p.events_per_H)<2e-15
    assert abs(a-p.absorber_after-p.events_per_H)<2e-15
    if k>0 and dt>0 and min(n,a)>0:
        assert abs(p.gamma_exposure_s*p.absorber_exposure_H_s-p.events_per_H)<2e-14
    if n>=a and p.absorber_after>0 and p.events_per_H>0:
        assert p.gamma_endpoint_BE_s>=p.gamma_exposure_s*(1-2e-14)


@pytest.mark.parametrize('n,a,k,dt',[(.5,.2,2.,1.5),(.2,.5,2.,1.5),(.3,.3,.3,1.),(.01,.5,12.,.2)])
def test_exposure_and_pair_vs_independent_radau(n,a,k,dt):
    p=exact_pair_exposure(n,a,k,dt)
    def rhs(t,y):
        f=k*y[0]*y[1]
        return [-f,-f,y[1],y[0]]
    sol=solve_ivp(rhs,(0,dt),[n,a,0,0],method='Radau',rtol=2e-12,atol=4e-14)
    assert sol.success
    assert np.allclose([p.photon_after,p.absorber_after,p.absorber_exposure_H_s,
                        p.photon_exposure_H_s],sol.y[:,-1],rtol=2e-10,atol=1e-12)


def test_stiff_endpoint_is_ill_conditioned_without_threshold_widening():
    p=exact_pair_exposure(1.0,0.1,3.,2.)
    bridge=pair_to_native(p,55.,2,1e-3)
    assert bridge.status[2]=='ENDPOINT_BE_REPRESENTABLE'
    assert bridge.endpoint_condition[2]>40
    assert math.isclose(bridge.gamma_exposure_s[2],p.gamma_exposure_s,rel_tol=1e-13)
    assert bridge.gamma_endpoint_s[2]>bridge.gamma_exposure_s[2]
    extreme=exact_pair_exposure(10.,.01,1.,100.)
    very=pair_to_native(extreme,80.,2,1e-3)
    assert extreme.absorber_after==0 and extreme.events_per_H>0
    assert very.status[2]=='HOLD_ENDPOINT_RATE_UNREPRESENTABLE'
    assert very.gamma_endpoint_s[2] is None
    assert 0<very.gamma_exposure_s[2]<11
    # Never invent epsilon denominators to force a native endpoint gamma.


def test_nearly_equal_population_limit_and_weak_rates():
    for k,dt in [(1e-8,1e-5),(.4,3.),(1e5,1e5)]:
        p=exact_pair_exposure(.1,.1,k,dt)
        exact=.1/(1+.1*k*dt)
        assert math.isclose(p.photon_after,exact,rel_tol=2e-14)
        assert math.isclose(p.absorber_exposure_H_s,math.log1p(.1*k*dt)/k,rel_tol=2e-14)
    weak=exact_pair_exposure(1e-7,1e-4,1e-5,1e-3)
    assert abs(weak.events_per_H-1e-7*1e-4*1e-5*1e-3)<1e-24
    assert abs(exprelminus(0)-1)<1e-20


def test_be_rate_and_exposure_rate_are_different_physics_interfaces():
    p=exact_pair_exposure(.5,.15,4.,1.)
    b=pair_to_native(p,60.,2,3e-4)
    events=b.events_H[2]
    assert math.isclose(events,b.gamma_exposure_s[2]*p.absorber_exposure_H_s,rel_tol=1e-13)
    assert math.isclose(events,b.gamma_endpoint_s[2]*p.absorber_after*p.elapsed_s,rel_tol=1e-13)
    assert b.gamma_endpoint_s[2]>b.gamma_exposure_s[2]
    assert math.isclose(b.events_cm3_s[2],3e-4*events/p.elapsed_s,rel_tol=1e-14)
    assert math.isclose(b.heat_exposure_erg_abs_s[2]*p.absorber_exposure_H_s,
                        events*(60-BIND_EV[2])*EV_ERG,rel_tol=1e-14)


def test_absent_absorber_and_all_zero_events():
    b=native_photo_rates([0,0,0],[0,0,0],[0,1,0],[0,.1,0],1,1e-3)
    assert b.status[0]=='ZERO_EVENTS_ZERO_ABSORBER'
    assert b.gamma_exposure_s==(0.,0.,0.)
    with pytest.raises(ValueError,match='no true absorber exposure'):
        native_photo_rates([.001,0,0],[0,0,0],[0,1,0],[0,.1,0],1,1e-3)


def test_q_ref_roundtrip_and_source_birthday():
    co,n0=make_cohorts(math.log(1/12),.025)
    assert len(co)==9 and n0==3
    for photon in co:
        for a in [1/12,math.exp(photon.birth_x),math.exp(math.log(1/12)+.025)]:
            assert math.isclose(energy_from_qref(q20_to_qref(photon.q20),a),photon.q20/a,rel_tol=4e-16)


@pytest.fixture(scope='module')
def actual():
    return run_reference()


def test_native_original_verner_fit_thresholds(actual):
    for j,r in enumerate(VERNER):
        th=r[0]
        assert cross(j,th-.000001)==0
        assert cross(j,th)>0
        assert cross(j,th+1e-5)>0
    assert actual.segments>3
    assert all(e>0 for e in actual.endpoint_rates.events_H)
    assert all(e>0 for e in actual.exposures)


def test_radau_source_age_gas_exposure_and_energy(actual):
    assert len(actual.cohorts)==9
    assert abs(actual.mass_res)<3e-13
    assert abs(actual.energy_res)<2e-12
    assert abs(sum(actual.yfinal[:len(actual.cohorts)])+sum(actual.endpoint_rates.events_H)-
               sum(c.start_n for c in actual.cohorts))<1e-12
    assert all(x>0 for x in actual.endpoint_rates.gamma_exposure_s)
    assert all(x>0 for x in actual.endpoint_rates.gamma_endpoint_s)
    for e,ig,coef in zip(actual.endpoint_rates.events_H,actual.exposures,actual.endpoint_rates.gamma_exposure_s):
        assert abs(e-ig*coef)<3e-15


@pytest.mark.parametrize('n',[2,4,8])
def test_previous_exact_source_age_reactor_approaches_independent_reference(actual,n):
    st=run_split_reference(n)
    ni=len(actual.cohorts)
    actual_arr=np.r_[actual.yfinal[:ni],actual.yfinal[ni:ni+5],actual.yfinal[ni+5]]
    st_arr=np.r_[[p.number for p in st.photons],st.atoms,st.thermal_ev]
    delta=float(max(abs(st_arr-actual_arr)))
    assert delta<{2:.0015,4:.0006,8:.0002}[n]
    assert abs(st.ledgers()['number_residual'])<1e-12
    assert abs(st.ledgers()['energy_residual_ev_per_H'])<2e-12


def test_rate_bridge_rejects_invalid_domains():
    with pytest.raises(ValueError):exact_pair_exposure(-1,.1,1,1)
    with pytest.raises(ValueError):native_photo_rates([-.1,0,0],[0,0,0],[1,1,1],[1,1,1],1,1)
    with pytest.raises(ValueError):native_photo_rates([0,0,0],[0,0,0],[1,1,1],[1,1,1],0,1)
    with pytest.raises(ValueError):pair_to_native(exact_pair_exposure(.5,.1,1,1),12.,2,1.)


def test_native_helium_intermediate_may_have_endpoint_less_than_exposure(actual):
    """HeII is created by HeI photoionization, so its population need not fall."""
    gamma_exposure=actual.endpoint_rates.gamma_exposure_s
    gamma_end=actual.endpoint_rates.gamma_endpoint_s
    assert gamma_end[0]>gamma_exposure[0]
    assert gamma_end[1]>gamma_exposure[1]
    assert gamma_end[2]<gamma_exposure[2]
    assert .85<gamma_end[2]/gamma_exposure[2]<.9
    # Reject a tempting but incorrect generalization of the pure depletion bound.


def test_external_total_h_normalization_is_per_total_H(actual):
    for j,e in enumerate(actual.endpoint_rates.events_H):
        assert math.isclose(actual.endpoint_rates.events_cm3_s[j],
          actual.endpoint_rates.nH_total_cm3*e/actual.endpoint_rates.delta_t_s,
          rel_tol=3e-15)
    assert actual.yfinal[len(actual.cohorts)]+actual.yfinal[len(actual.cohorts)+1]==pytest.approx(1.,abs=1e-12)
    assert sum(actual.yfinal[len(actual.cohorts)+2:len(actual.cohorts)+5])==pytest.approx(
        .2454/(4*(1-.2454)),abs=1e-12)


def test_cross_check_against_original_pr76_exact_pair():
    import sys,pathlib
    d=pathlib.Path(__file__).resolve().parents[1]/'vendor'/'pr76'
    sys.path.insert(0,str(d))
    from c21b_age_reactor import exact_pair
    for N,A,k,dt in [(.3,.1,5.,.5),(.1,.3,5.,.5),(.1,.1,1.,2.),(1.,.1,3.,2.)]:
        p=exact_pair_exposure(N,A,k,dt)
        np,ap,ep=exact_pair(N,A,k,dt)
        assert np==pytest.approx(p.photon_after,abs=1e-15)
        assert ap==pytest.approx(p.absorber_after,abs=1e-15)
        assert ep==pytest.approx(p.events_per_H,abs=1e-15)


def test_zero_opacity_radau_positive_two_birth_control():
    no=run_reference(opacity_scale=0)
    assert all(x==0 for x in no.endpoint_rates.events_H)
    assert no.mass_res==pytest.approx(0,abs=1e-13)
    assert no.energy_res==pytest.approx(0,abs=3e-12)
    assert all(s=='ENDPOINT_BE_REPRESENTABLE' for s in no.endpoint_rates.status)
    assert all(e>0 for e in no.exposures)
