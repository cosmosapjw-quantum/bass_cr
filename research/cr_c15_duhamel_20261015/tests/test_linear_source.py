"""Analytically validated endpoint-linear photon source, constant opacity."""
import numpy as np
import pytest
from scipy.integrate import quad

from linear_source import absorb_linear_source,phi2_neg
from exponential_source import absorb_with_source,midpoint_born_source


@pytest.mark.parametrize("tau",[0.,1e-12,1e-7,1e-4,1e-2,1.,10.,100.,2000.])
def test_exact_linear_source_reference(tau):
    dt=10.
    rates=np.array([[tau/dt*.5,tau/dt*.3,tau/dt*.2]])
    initial=np.array([1.8])
    src0=np.array([.01]);src1=np.array([.03])
    actual,events=absorb_linear_source(initial,src0,src1,rates,dt)
    oracle=initial[0]*np.exp(-tau)+quad(
       lambda t:(src0[0]+(src1[0]-src0[0])*t/dt)*np.exp(-tau*(1-t/dt)),
       0.,dt,epsabs=1e-14,epsrel=1e-12)[0]
    np.testing.assert_allclose(actual[0],oracle,rtol=4e-12,atol=2e-14)
    assert actual[0]>=0
    assert np.all(events>=0)
    np.testing.assert_allclose(initial+dt*.5*(src0+src1),
                    actual+events.sum(axis=1),rtol=6e-13,atol=2e-12)


def test_constant_source_parity_C14_exact_Duhamel():
    n=50
    photon=np.geomspace(1e-8,1e-3,n)
    src=np.geomspace(1e-17,1e-12,n)
    op=np.geomspace(1e-18,1e-6,n)
    R=op[:,None]*np.array([.6,.3,.1])
    dt=1e9
    lin,events=absorb_linear_source(photon,src,src,R,dt)
    exact,e,_=absorb_with_source(photon,src,R,dt)
    np.testing.assert_allclose(lin,exact,rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(events,e,rtol=1e-10,atol=1e-12)


def test_endpoint_source_recovered_in_large_opacity_limit():
    # No old photons, emission rises from 0 to a finite rate at the end.
    # Proper solution is ~S_end/lambda; midpoint birth is exponentially tiny.
    dt=1e5;lam=1e-2
    a,ev=absorb_linear_source(np.array([0.]),np.array([0.]),
                np.array([.1]),np.array([[lam,0,0]]),dt)
    assert np.isclose(a[0],.1/lam,rtol=.002)
    assert np.isclose(a[0]+ev.sum(),.5*.1*dt,rtol=1e-13)
    middle=midpoint_born_source(np.array([0.]),np.array([.05]),
                np.array([[lam,0,0]]),dt)
    assert middle[0]<a[0]*1e-100


def test_linear_source_invalid_inputs():
    with pytest.raises(ValueError):
        phi2_neg(np.array([-1.]))
    with pytest.raises(ValueError):
        absorb_linear_source(np.array([1.]),np.array([1.]),
                    np.array([-1.]),np.zeros((1,3)),1.)
