"""Independent Radau checks of species photoevent-time moments and heating."""
from __future__ import annotations
import numpy as np
import pytest
from scipy.integrate import solve_ivp

from species_events import species_resolved_affine,affine_photoheat


@pytest.mark.parametrize("l0,l1,s0,s1,eng0,eng1",[
  ([2.,.5,.1],[.3,1.,.8],1.,.5,90.,75.),
  ([100.,0.,0.],[0.,100.,0.],1.,1.,100.,60.),
  ([0.,0.,0.],[4.,1.,.5],1.,.7,100.,80.),
  ([.2,.5,0.],[2.,.1,1.],.1,.3,90.,87.)
])
def test_time_barycentre_and_photoheat_vs_independent_Radau(l0,l1,s0,s1,eng0,eng1):
    n0=.6
    l0=np.asarray(l0);l1=np.asarray(l1)
    binding=np.array([13.6,24.59,54.42])
    photon,event,diag,moment=species_resolved_affine(
       np.array([n0]),np.array([s0]),np.array([s1]),
       l0[None,:],l1[None,:],1.,with_time_moments=True)
    heat=affine_photoheat(event,moment,np.array([eng0]),np.array([eng1]),binding)
    def rhs(t,z):
        lam=l0+(l1-l0)*t
        S=s0+(s1-s0)*t
        return np.r_[S-lam.sum()*z[0], lam*z[0],
                      t*lam*z[0],
                      lam*z[0]*(eng0+(eng1-eng0)*t-binding)]
    sol=solve_ivp(rhs,(0,1),np.r_[n0,np.zeros(9)],method="Radau",
                   rtol=1e-11,atol=1e-13)
    assert sol.success
    target=sol.y[:,-1]
    np.testing.assert_allclose(photon[0],target[0],rtol=5e-9,atol=2e-10)
    np.testing.assert_allclose(event[0],target[1:4],rtol=3e-7,atol=1e-8)
    np.testing.assert_allclose(moment[0],target[4:7],rtol=1e-6,atol=1e-8)
    np.testing.assert_allclose(heat[0],target[7:10],rtol=1e-6,atol=1e-7)
    assert np.all(heat>=0)
    assert np.all(moment<=event+1e-13)


def test_constant_energy_heat_reduces_to_events_times_excess():
    n=np.array([.7])
    S=np.array([.5])
    a=np.array([[1.,.5,.2]])
    b=np.array([[.5,1.,.2]])
    _,ev,_,moment=species_resolved_affine(n,S,S,a,b,1.,with_time_moments=True)
    I=np.array([13.6,24.59,54.42])
    H=affine_photoheat(ev,moment,np.array([100.]),np.array([100.]),I)
    np.testing.assert_allclose(H,ev*(100.-I),rtol=2e-13,atol=1e-12)


def test_heat_requires_threshold_event_partition():
    ev=np.array([[.1,.2,.3]])
    t=np.array([[.05,.1,.15]])
    with pytest.raises(ValueError):
        affine_photoheat(ev,t,np.array([50.]),np.array([40.]),np.array([13.6,24.59,54.42]))
