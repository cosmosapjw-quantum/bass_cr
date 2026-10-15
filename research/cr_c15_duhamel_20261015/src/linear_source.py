"""Positive exact linear-in-time local photon-source exponential.

A bounded mathematical subsolver for SOURCE07 research. Absorber rates
constant on the proper interval, but injected source may vary linearly.
Not an exact solver for time-varying opacity, redshift or coupled gas.
"""
from __future__ import annotations
import numpy as np
from exponential_source import phi_neg


def phi2_neg(z):
    """Integral_0^1 u exp[-z(1-u)] du, strictly nonnegative for z>=0."""
    tau=np.asarray(z,dtype=float)
    if np.any(~np.isfinite(tau)) or np.any(tau<0):
        raise ValueError("nonnegative finite tau required")
    out=np.empty_like(tau)
    sm=tau<=1e-4
    x=tau[sm]
    out[sm]=.5+x*(-1/6+x*(1/24+x*(-1/120+x*(1/720-x/5040))))
    x=tau[~sm]
    out[~sm]=(x+np.expm1(-x))/x**2
    return out


def absorb_linear_source(photons, source_start, source_end, lambdas, dt):
    """Exact frozen-opacity linear source + old packet decay, species ledger.

    Inputs are [packet] photons, [packet] start/end photon/H/s, rate
    matrix [packet,species] in proper 1/s, dt proper seconds.
    """
    photon=np.asarray(photons,float)
    s0=np.asarray(source_start,float)
    s1=np.asarray(source_end,float)
    R=np.asarray(lambdas,float)
    if photon.ndim!=1 or R.ndim!=2 or R.shape[0]!=len(photon) or s0.shape!=photon.shape or s1.shape!=photon.shape:
        raise ValueError("shape mismatch")
    if not np.isfinite(dt) or dt<=0 or any(np.any(~np.isfinite(a)) or np.any(a<0)
                 for a in (photon,s0,s1,R)):
        raise ValueError("nonnegative finite input and positive dt required")
    lam=R.sum(axis=1)
    tau=dt*lam
    ph1=phi_neg(tau)
    ph2=phi2_neg(tau)
    start_weight=ph1-ph2
    # Endpoint-weighted emission is positive even for very large tau.
    end=photon*np.exp(-tau)+dt*(s0*start_weight+s1*ph2)

    # Each source portion has a separate positive absorption quadrature
    # to retain accuracy for tau approaching zero (avoid cancellation).
    small=tau<=1e-4
    lost_start=np.empty_like(tau)
    lost_end=np.empty_like(tau)
    x=tau[small]
    lost_start[small]=x*(1/3+x*(-1/8+x*(1/30+x*(-1/144+x/840))))
    lost_end[small]=x*(1/6+x*(-1/24+x*(1/120+x*(-1/720+x/5040))))
    lost_start[~small]=.5-start_weight[~small]
    lost_end[~small]=.5-ph2[~small]
    lost=photon*(-np.expm1(-tau))+dt*(s0*lost_start+s1*lost_end)
    branch=np.zeros_like(R)
    np.divide(R,lam[:,None],out=branch,where=lam[:,None]>0)
    events=lost[:,None]*branch
    if np.any(end<0) or np.any(events<0):
        raise ArithmeticError("invalid positive photon state")
    return end,events
