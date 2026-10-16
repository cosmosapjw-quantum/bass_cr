"""Independent Radau/QUAD, physical conservation and original-input scoped tests."""
import math,sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad,solve_ivp
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from c21b_age_reactor import (
 A_REF,BIND_EV,FIT_EV,NH0_CM3,Y_HE,EV_ERG,KB_ERG_K,C_CM_S,
 E_from_q20,to_ref_energy,from_ref_energy,hubble,exact_pair,
 PhotonReactor,initial_state,nH_total,md14_rate_per_total_h_s,
 blackbody_shape,bb50k_positive_bins,verner_sigma_cm2,
)


def assert_closure(s,eps_n=2e-11,eps_e=5e-11):
    s.validation()
    r=s.ledgers()
    scale_n=max(1e-8,s.initial_n+s.source_n)
    scale_e=max(1e-5,s.initial_u+s.source_u+s.initial_w)
    assert abs(r['number_residual'])<=eps_n*scale_n+2e-16,r
    assert abs(r['energy_residual_ev_per_H'])<=eps_e*scale_e+2e-14,r
    assert min(s.photo_events)>=0
    assert min(s.photoheat)>=-1e-20
    return r


def reference_free_ode(s0,xf,opacity_scale):
    """True continuous ODE for the *same* initial real-Verner monoenergetic packet.

    Independent Radau solver, no pair map or symmetric composition. Integrates
    photon, all nuclei, thermal energy, photon cosmological work and gas work.
    Source=0, but gas ionization and radiation interact nonlinearly. Split at
    exact Verner cutoff because the fitting rate is discontinuous there.
    """
    assert len(s0.photons)==1
    p=s0.photons[0];q=p.q20
    y=np.array([p.number,*s0.atoms,s0.thermal_ev,0.,0.],dtype=float)
    x0=s0.x
    cuts=[x0]+sorted(set(math.log(q/cut) for cut in FIT_EV if x0<math.log(q/cut)<xf))+[xf]
    for lo,hi in zip(cuts[:-1],cuts[1:]):
        def rhs(x,z):
            # One-sided fit evaluation inside a smooth threshold panel.
            xx=min(max(x,lo+(hi-lo)*1e-9),hi-(hi-lo)*1e-9)
            E=q*math.exp(-xx)
            n,hh0,hhp,he0,hep,hepp,w,wgamma,wgas=z
            A=[hh0,he0,hep]
            ev=[C_CM_S*nH_total(xx)*opacity_scale*verner_sigma_cm2(j,E)*A[j]*n/hubble(xx) for j in range(3)]
            return np.array([-sum(ev),-ev[0],ev[0],-ev[1],ev[1]-ev[2],ev[2],
                             sum(qv*(E-b) for qv,b in zip(ev,BIND_EV))-2*w,E*n,2*w])
        sol=solve_ivp(rhs,(lo,hi),y,method='Radau',atol=3e-13,rtol=2e-11,
                      max_step=(hi-lo)/8)
        assert sol.success,sol.message
        y=sol.y[:,-1]
    return y


@pytest.mark.parametrize('N,A,k,dt',[
    (.2,.2,1e-4,1e4),(.9,.1,1e-4,1e4),(.1,.9,1e-4,1e4),
    (.01,.9,1e-8,1e5),(.9,.01,20,100),(1e-12,1e-12,1e-3,1e5),
])
def test_pair_exact_independent_radau(N,A,k,dt):
    n1,a1,delta=exact_pair(N,A,k,dt)
    assert n1>=0 and a1>=0 and 0<=delta<=min(N,A)+2e-16
    assert abs((N-A)-(n1-a1))<5e-14
    if k*max(N,A)*dt<200:
        z=solve_ivp(lambda t,v: [-k*v[0]*v[1],-k*v[0]*v[1]],(0,dt),[N,A],
          method='Radau',atol=1e-14,rtol=1e-11)
        assert z.success
        assert np.allclose([n1,a1],z.y[:,-1],rtol=1e-9,atol=2e-13)


def test_pair_rejects_negative_and_nan():
    for case in [(-1,.1,1.,1.),(.1,.1,-1.,1.),(.1,.1,1.,float('nan'))]:
        with pytest.raises(ValueError):exact_pair(*case)


@pytest.mark.parametrize('aa,E',[(1/21,14.),(.084,54.42),(.2,91.)])
def test_common_q_and_physical_energy(aa,E):
    q20=aa*E
    qref=to_ref_energy(q20)
    assert math.isclose(qref,21*q20,rel_tol=5e-15)
    assert math.isclose(from_ref_energy(qref),q20,rel_tol=1e-15)
    assert math.isclose(E_from_q20(from_ref_energy(qref),math.log(aa)),E,rel_tol=5e-15)


def test_native_density_and_helium_total():
    a=0.047620181473387826
    assert math.isclose(nH_total(math.log(a)),.0017577960178838546,rel_tol=3e-15)
    assert math.isclose(Y_HE,.08130135170951498,rel_tol=3e-15)


def test_Verner_three_thresholds_and_positivity():
    for j,th in enumerate(FIT_EV):
        assert verner_sigma_cm2(j,th-1e-6)==0
        assert verner_sigma_cm2(j,th)>0
        assert verner_sigma_cm2(j,th+10)>0
        assert th>BIND_EV[j]


def test_source_weights_positive_and_normalized():
    for n in (1,2,4,8):
        bins=bb50k_positive_bins(n)
        assert len(bins)==3*n
        assert math.fsum(f for _,f in bins)==pytest.approx(1.,abs=2e-15)
        assert all(f>0 and FIT_EV[0]<e<100 for e,f in bins)


def test_source_on_no_opacity_quad_reference():
    x0=math.log(1/12)
    x1=x0+.025
    qbins=bb50k_positive_bins(2)
    avgE=math.fsum(e*f for e,f in qbins)
    # Continuous-source integral, independent of two GL2 birth impulses.
    n_ref=quad(lambda x:md14_rate_per_total_h_s(x)/hubble(x),x0,x1,epsrel=2e-13)[0]
    u_ref=quad(lambda x:md14_rate_per_total_h_s(x)/hubble(x)*math.exp(x-x1),x0,x1,epsrel=2e-13)[0]*avgE
    errors=[]
    for steps in (1,2,4):
        reactor=PhotonReactor(energy_nodes=2,opacity_scale=0.)
        s=reactor.advance(initial_state(x0),x1,steps)
        assert_closure(s)
        errors.append(abs(s.number_photons()-n_ref))
        assert abs(s.energy_photons()-u_ref)/u_ref < 2e-5
    assert errors[2] < errors[1] < errors[0]
    assert errors[2]/n_ref<1e-8


def test_source_free_gas_geometry_exact():
    x0=math.log(1/12);x1=x0+.02
    s=PhotonReactor(energy_nodes=1).advance(initial_state(x0),x1,3,source_on=False)
    assert_closure(s)
    assert s.thermal_ev==pytest.approx(s.initial_w*math.exp(-2*(x1-x0)),rel=4e-15)
    assert s.binding_ev()==pytest.approx(s.initial_b,rel=1e-15)
    assert s.source_n==0


def test_source_off_real_Verner_Radau_comparison_and_refinement():
    x0=math.log(1/12);x1=x0+.0008
    initial=initial_state(x0,8500.,(0.2,0.2,0.01),((60.,.01),))
    opacity=.004
    ref=reference_free_ode(initial,x1,opacity)
    err=[]
    for steps in (2,4,8,16):
        s=PhotonReactor(energy_nodes=2,opacity_scale=opacity).advance(initial.clone(),x1,steps,source_on=False)
        assert_closure(s)
        got=np.array([s.photons[0].number,*s.atoms,s.thermal_ev,s.work_gamma,s.work_gas])
        err.append(float(np.max(np.abs(got-ref))))
    assert err[-1]<err[-2]<err[-3]
    # Symmetric map with smooth real Verner coefficients: second-order trend.
    assert 2.7<err[-2]/err[-1]<5.3,err


def test_threshold_event_real_Verner_Radau_and_ledgers():
    x0=math.log(1/12);xf=x0+math.log(54.43/54.42)+.001
    initial=initial_state(x0,8500.,(.2,.2,.01),((54.43,.008),))
    ref=reference_free_ode(initial,xf,.002)
    s=PhotonReactor(energy_nodes=2,opacity_scale=.002).advance(initial.clone(),xf,16,source_on=False)
    assert_closure(s)
    assert s.crossings[2]>=1
    assert abs(s.photons[0].number-ref[0])<2e-7
    assert abs(s.atoms[4]-ref[5])<2e-7


def test_actual_md14_Verner_source_on_gas_evolution_and_ledgers():
    x0=math.log(1/12);end=x0+.0004
    initial=initial_state(x0,8500.,(.2,.2,.01),((60.,.0002),))
    state=PhotonReactor(energy_nodes=2,opacity_scale=.004).advance(initial,end,8,source_on=True)
    r=assert_closure(state)
    assert state.source_n>0
    assert state.atoms[1]>.2
    assert state.atoms[4]>Y_HE*.01
    assert r['photons_per_H']>0
    assert all(p.birth_x is None or x0<p.birth_x<end for p in state.photons)
    assert all(math.isclose(p.q20,math.exp(p.birth_x)*p.energy_emitted_ev,rel_tol=2e-15)
               for p in state.photons if p.birth_x is not None)


def test_stiff_rate_limit_remains_positive_and_stoichiometric():
    x0=math.log(1/12)
    s0=initial_state(x0,8500.,(0.01,0.01,0.0),((60.,.2),))
    s=PhotonReactor(energy_nodes=1,source_scale=0,opacity_scale=10.).advance(s0,x0+.0001,4,source_on=False)
    assert_closure(s)
    assert s.photons[0].number>=0
    assert s.atoms[2]>=0 and s.atoms[3]>=0 and s.atoms[4]>=0


def test_invalid_time_and_state_rejection():
    x=math.log(1/12)
    r=PhotonReactor(energy_nodes=1)
    s=initial_state(x)
    with pytest.raises(ValueError):r.advance(s,x,2)
    with pytest.raises(ValueError):r.advance(s,x+.01,0)
    with pytest.raises(ValueError):initial_state(x,fractions=(.1,.8,.5))
    with pytest.raises(ValueError):md14_rate_per_total_h_s(math.log(1/3))
