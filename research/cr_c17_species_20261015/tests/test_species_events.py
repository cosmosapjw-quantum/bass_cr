"""Competing HI/HeI/HeII time-affine photoevent integrals vs independent Radau."""
import numpy as np
from scipy.integrate import solve_ivp
import pytest

from species_events import species_resolved_affine
from endpoint_quadrature import optical_quadrature
from exponential_source import absorb_with_source


def reference(n0,s0,s1,l0,l1,h):
    l0=np.asarray(l0,float);l1=np.asarray(l1,float)
    def rhs(u,z):
        lam=l0+(l1-l0)*u
        S=s0+(s1-s0)*u
        return np.r_[h*(S-lam.sum()*z[0]),h*lam*z[0]]
    def jac(u,z):
        lam=l0+(l1-l0)*u
        A=np.zeros((len(lam)+1,len(lam)+1))
        A[0,0]=-h*lam.sum()
        A[1:,0]=h*lam
        return A
    sol=solve_ivp(rhs,(0.,1.),np.r_[n0,np.zeros(len(l0))],method='Radau',
                  jac=jac,rtol=2e-11,atol=3e-14)
    assert sol.success
    return sol.y[:,-1]


def test_anomalous_species_branch_swap_counterexample():
    # Lambda_total stays 100, yet the dominant HI/HeI channels swap.
    # The total photon stock cannot diagnose species assignment.
    n0=np.array([1.]);s0=np.array([1.]);s1=np.array([1.])
    r0=np.array([[100.,0.,0.]])
    r1=np.array([[0.,100.,0.]])
    out,evt,diag=species_resolved_affine(n0,s0,s1,r0,r1,1.)
    independent=reference(1.,1.,1.,r0[0],r1[0],1.)
    np.testing.assert_allclose(np.r_[out[0],evt[0]],independent,
        rtol=2e-8,atol=2e-10)
    c16,approx=optical_quadrature(n0,s0,s1,r0,r1,1.)
    np.testing.assert_allclose(out,c16,atol=1e-14)
    assert np.max(abs(approx[0]-evt[0])) > .5
    np.testing.assert_allclose(out+evt.sum(axis=1),n0+.5*(s0+s1))


@pytest.mark.parametrize("s0,s1,initial,L0,L1",[
 (0.,0.,1.,[2.,1.,0.],[3.,1.,.4]),
 (.1,.2,.5,[.1,1.,.4],[2.,.1,.4]),
 (1.,.3,0.,[0.,.3,1.],[10.,.1,0.]),
 (0.,1.,0.,[150.,0.,.1],[1.,150.,.1]),
 (1.,1.,.2,[2000.,0.,0.],[0.,100.,5.]),
 (1.,.1,.5,[0.,0.,0.],[0.,0.,0.]),
 (.2,.3,.7,[100.,0.,0.],[100.,0.,0.]),
 (1.,.2,.5,[0.,500.,0.],[300.,0.,0.]),
])
def test_species_integrals_against_independent_stiff_ode(s0,s1,initial,L0,L1):
    old=np.array([initial])
    s=np.array([s0]);e=np.array([s1])
    l0=np.array([L0]);l1=np.array([L1])
    final,events,diag=species_resolved_affine(old,s,e,l0,l1,1.)
    true=reference(initial,s0,s1,L0,L1,1.)
    np.testing.assert_allclose(np.r_[final[0],events[0]],true,
        rtol=5e-6,atol=8e-9)
    assert np.all(events>=0) and np.all(final>=0)
    np.testing.assert_allclose(final+events.sum(axis=1),
                    old+.5*(s+e),rtol=1e-12,atol=1e-12)


def test_constant_gas_matches_C14_three_species_events_exact():
    n0=np.array([.2,.3,.4])
    s=np.array([.01,.1,.6])
    r=np.array([[.1,.2,0.],
                [0.,.1,.1],
                [100.,200.,300.]])
    new,ev,diag=species_resolved_affine(n0,s,s,r,r,1.)
    reference,old_events,_=absorb_with_source(n0,s,r,1.)
    np.testing.assert_allclose(new,reference,rtol=1e-12,atol=1e-13)
    np.testing.assert_allclose(ev,old_events,rtol=1e-9,atol=1e-12)


def test_chunk_equivalence_and_positivity():
    rng=np.random.default_rng(15)
    n=30
    N=rng.uniform(0,.1,size=n)
    s0=rng.uniform(0,.1,size=n)
    s1=rng.uniform(0,.1,size=n)
    r0=rng.uniform(0,100,size=(n,3))
    r1=rng.uniform(0,100,size=(n,3))
    a,b,diag=species_resolved_affine(N,s0,s1,r0,r1,1.,chunk=7)
    c,d,_=species_resolved_affine(N,s0,s1,r0,r1,1.,chunk=32)
    np.testing.assert_allclose(a,c,rtol=0,atol=0)
    np.testing.assert_allclose(b,d,rtol=0,atol=0)
    assert np.all(b>=0)
    np.testing.assert_allclose(a+b.sum(axis=1),N+.5*(s0+s1),
                      rtol=5e-13,atol=1e-13)


def test_invalid_inputs():
    N=np.zeros(1);s=np.ones(1)
    rates=np.ones((1,3))
    with pytest.raises(ValueError):
        species_resolved_affine(N,-s,s,rates,rates,1.)
    with pytest.raises(ValueError):
        species_resolved_affine(N,s,s,rates,rates,-1.)
    with pytest.raises(ValueError):
        species_resolved_affine(N,s,s,rates,rates,1.,chunk=0)
