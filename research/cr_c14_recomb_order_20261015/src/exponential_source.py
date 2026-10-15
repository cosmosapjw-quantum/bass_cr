"""Exact positive photon birth/absorption in a constant-coefficient cell.

A reference kernel for the strongly absorbing SOURCE07/C13 regime.
This is a local Duhamel / exponential integrator. No claims for the
full time-varying Bianchi-I radiation, multiple ionization stages,
or owner R*J ray transport before real interface tests.
"""
from __future__ import annotations
import numpy as np


def phi_neg(z):
    """phi(-z)=(1-e^-z)/z, entire extension at zero, z>=0."""
    t=np.asarray(z,dtype=float)
    if not np.all(np.isfinite(t)) or np.any(t<0):
        raise ValueError("finite nonnegative tau required")
    a=np.empty_like(t)
    small=t<=1e-5
    x=t[small]
    a[small]=1.+x*(-.5+x*(1./6.+x*(-1./24.+x*(1./120.-x/720.))))
    x=t[~small]
    a[~small]=-np.expm1(-x)/x
    return a


def absorbed_source_fraction(z):
    """1-phi(-z), evaluated without catastrophic cancellation near zero."""
    t=np.asarray(z,dtype=float)
    if not np.all(np.isfinite(t)) or np.any(t<0):
        raise ValueError("finite nonnegative tau required")
    a=np.empty_like(t)
    small=t<=1e-5
    x=t[small]
    a[small]=x*(.5+x*(-1./6.+x*(1./24.+x*(-1./120.+x/720.))))
    x=t[~small]
    a[~small]=1.-phi_neg(x)
    return a


def absorb_with_source(initial_photons, source_rate, species_lambda, dt):
    """Exact frozen-gas photon update for continuous uniform-time emission.

    Inputs:
      initial_photons  [packet] in photons/H
      source_rate      [packet] in photons/(H second)
      species_lambda   [packet,species] in s^-1
      dt               >0, proper seconds
    Returns (final_photons, species_event_counts, deposited_source_age_stock).
    The photon/ionization ledger holds to roundoff. Handles tau->0 exactly.
    """
    before=np.asarray(initial_photons,dtype=float)
    source=np.asarray(source_rate,dtype=float)
    rates=np.asarray(species_lambda,dtype=float)
    if before.ndim!=1 or source.shape!=before.shape or rates.ndim!=2 or rates.shape[0]!=len(before):
        raise ValueError("requires [packet], [packet], [packet,species] shapes")
    if dt<=0 or not np.isfinite(dt) or np.any(before<0) or np.any(source<0) or np.any(rates<0):
        raise ValueError("nonnegative finite photon/source/rates and positive finite proper dt")
    if not np.all(np.isfinite(before)) or not np.all(np.isfinite(source)) or not np.all(np.isfinite(rates)):
        raise ValueError("nonfinite state")
    lam=rates.sum(axis=1)
    tau=dt*lam
    emitted=source*dt
    retained=emitted*phi_neg(tau)
    end=before*np.exp(-tau)+retained
    lost=before*(-np.expm1(-tau))+emitted*absorbed_source_fraction(tau)
    branches=np.zeros_like(rates)
    np.divide(rates,lam[:,None],out=branches,where=lam[:,None]>0)
    events=lost[:,None]*branches
    if np.any(end<-1e-14) or np.any(events<-1e-14):
        raise AssertionError("positivity violation")
    return end,events,retained


def midpoint_born_source(initial_photons, source_rate, species_lambda, dt):
    """Old midpoint-birth quadrature of the same frozen-coefficient problem."""
    before=np.asarray(initial_photons,dtype=float)
    source=np.asarray(source_rate,dtype=float)
    lam=np.asarray(species_lambda,dtype=float).sum(axis=1)
    return before*np.exp(-lam*dt)+(source*dt)*np.exp(-.5*lam*dt)


def test_matrix_lambda_from_owner(ns, a_mid=.105):
    """Subset of actual owner H/He Verner lambda(E), proper cm^-3."""
    from owner_age_bridge import verner_sigma_array
    E=np.array([13.61,20.,40.,60.,90.])
    nh=ns['model'].nh/a_mid**3
    y=ns['nhe']/(ns['model'].nh*125)
    gas=np.array([nh*.9,nh*y*.85,nh*y*.15])
    return E,29979245800.*gas[None,:]*np.column_stack(
        [verner_sigma_array(E,p) for p in ns["fit"]])


if __name__=='__main__':
    from pathlib import Path
    from owner_age_bridge import owner_namespace
    from scipy.integrate import quad
    ns=owner_namespace(Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi'))
    E,lam=test_matrix_lambda_from_owner(ns)
    total_dt=quad(lambda u:1/ns['model'].hubble(np.exp(u),0.),
                   np.log(.1),np.log(.11))[0]
    for n in (16,32,64,128,1024):
        dt=total_dt/n
        source=np.full(len(E),.05/total_dt/len(E))
        current=np.zeros(len(E))
        mid=np.zeros(len(E))
        for i in range(n):
            current,ev,_=absorb_with_source(current,source,lam,dt)
            mid=midpoint_born_source(mid,source,lam,dt)
        exact=source*phi_neg(total_dt*lam.sum(axis=1))*total_dt
        print(n,'tau_lowE',lam[0].sum()*dt,'relDuhamel',np.max(abs(current-exact)/np.maximum(abs(exact),1e-20)),
              'relMidpoint',np.max(abs(mid-exact)/np.maximum(abs(exact),1e-20)),
              'absolute_mid_highopacity',abs(mid[0]-exact[0]),flush=True)
