"""Independent variable-opacity source oracle, conservation, stiff counterexamples."""
import numpy as np
import pytest
from scipy.integrate import quad

from endpoint_quadrature import (
    endpoint_weighted,optical_quadrature,retarded_fraction
)
from linear_source import absorb_linear_source


def scalar_quad(s0,s1,l0,l1,dt):
    # Independent SciPy adaptive reference for exactly linear lambda(t).
    end=l1*dt
    scale=max(1.,end,np.sqrt(l0*dt))
    limit=min(scale,120.)
    def f(x):
        u=x/scale
        expo=-dt*(l1*u+.5*(l0-l1)*u*u)
        return (s1+(s0-s1)*u)*np.exp(expo)*dt/scale
    return quad(f,0.,limit,epsabs=1e-14,epsrel=2e-13,limit=300)[0]


@pytest.mark.parametrize("l0,l1",[
    (0.,0.),(1e-10,0.),(0.,1e-10),(.1,.2),(3.,2.),
    (2000.,1000.),(0.,2000.),(2000.,0.),(500.,700.),
    (1e5,1e5),(1e5,0.)
])
def test_vector_optical_quadrature_vs_independent_scipy(l0,l1):
    n0=np.array([.43]);s0=np.array([.12]);s1=np.array([.28])
    d=1.
    r0=np.array([[.7*l0,.2*l0,.1*l0]])
    r1=np.array([[.7*l1,.2*l1,.1*l1]])
    n,e=optical_quadrature(n0,s0,s1,r0,r1,d)
    expected=n0[0]*np.exp(-.5*(l0+l1)*d)+scalar_quad(s0[0],s1[0],l0,l1,d)
    np.testing.assert_allclose(n,[expected],rtol=2e-11,atol=4e-14)
    assert np.all(n>=0) and np.all(e>=0)
    np.testing.assert_allclose(n+e.sum(axis=1),
         n0+.5*(s0+s1)*d,rtol=2e-12,atol=1e-13)


@pytest.mark.parametrize("l0,l1",[(0.,0.),(.02,.02),(2.,2.),(1e3,1e3)])
def test_C15_linear_source_exact_constant_opacity_parity(l0,l1):
    n0=np.array([.2]);s0=np.array([.13]);s1=np.array([.17])
    r0=np.array([[l0*.8,l0*.2,0.]])
    r1=np.array([[l1*.8,l1*.2,0.]])
    exact,events=absorb_linear_source(n0,s0,s1,r0,1.)
    for f in (endpoint_weighted,optical_quadrature):
        out,events2=f(n0,s0,s1,r0,r1,1.)
        np.testing.assert_allclose(out,exact,rtol=3e-12,atol=4e-14)
        np.testing.assert_allclose(events2,events,rtol=2e-12,atol=4e-14)


def test_retarded_fraction_nonnegative_and_endpoint_limit():
    val=retarded_fraction(np.array([0.,1e-10,.1,1.,10.,100.,2308.]))
    assert np.all(val>=0) and np.all(val<=.5)
    assert val[0]==.5
    assert abs(val[-1]-1/2308)<1e-15


def test_vectorized_mixed_zero_rate_and_nonzero_emission():
    n=500
    rate0=np.geomspace(1e-12,1e4,n)
    rate1=np.geomspace(1e-13,2e4,n)
    rate0[:10]=0.;rate1[:10]=0.
    source0=np.linspace(0.,.1,n)
    source1=np.linspace(.2,0.,n)
    N0=np.linspace(0.,.2,n)
    l0=np.column_stack([rate0*.7,rate0*.2,rate0*.1])
    l1=np.column_stack([rate1*.7,rate1*.2,rate1*.1])
    for f in (endpoint_weighted,optical_quadrature):
        final,ev=f(N0,source0,source1,l0,l1,1.)
        assert np.all(final>=0)
        assert np.all(ev>=0)
        np.testing.assert_allclose(final+ev.sum(axis=1),
             N0+.5*(source0+source1),rtol=2e-12,atol=3e-13)


def test_negative_rates_rejected():
    N=np.zeros(1);S=np.ones(1)
    r=np.array([[-1.,0.,0.]])
    for f in (endpoint_weighted,optical_quadrature):
        with pytest.raises(ValueError):
            f(N,S,S,r,r,1.)


def test_nonuniform_endpoint_error_and_positional_conservation():
    # λ_end differs substantially from mean; the fast approximation has
    # a measurable error while the optical quadrature is the actual
    # linear-rate photon survivor reference.
    N0=np.array([0.])
    s0=np.array([1.]);s1=np.array([1.])
    l0=np.array([[1500.,0.,0.]])
    l1=np.array([[0.,0.,0.]])
    reference,_=optical_quadrature(N0,s0,s1,l0,l1,1.)
    approximation,_=endpoint_weighted(N0,s0,s1,l0,l1,1.)
    assert abs(reference[0]-approximation[0])/reference[0]>.05
    assert reference[0]>0
