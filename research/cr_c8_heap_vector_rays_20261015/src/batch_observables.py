"""Vectorized, independent-ray Verner frozen-neutral photoevents and photoheat.

Consumes photon cohorts with actual physical E [eV] and number per H, already
produced by a chosen source/characteristic. Angles, source ages and clocks remain
separate; a ray's physical source and proper neutral densities are never mixed.

Does not implement SOURCE07 itself, nor a nonlinear chemistry history, and the
NumPy reduction order need not be byte-identical to the reference scalar summation.
"""
from __future__ import annotations
from math import isfinite
from typing import Sequence
import numpy as np
from compressed_cohorts import _validate_neutrals, frozen_be_readout
from threshold_rt import ATOMIC, ION_NAMES, C_CM_S, SOURCE_EDGES


def _cross_sections_numpy(energies: np.ndarray) -> np.ndarray:
    """Elementwise port of the *same* Verner expression and zero below threshold."""
    if energies.ndim != 1 or np.any(~np.isfinite(energies)) or np.any(energies<=0) or np.any(energies>50000):
        raise ValueError('finite energies in Verner range required')
    out=np.empty((len(energies),3),dtype=np.float64)
    for k,name in enumerate(ION_NAMES):
        th,e0,s0,ya,p,yw,y0,y1=ATOMIC[name]
        out[:,k]=0.
        mask=energies>=th
        en=energies[mask]
        xx=en/e0-y0
        yy=np.hypot(xx,y1)
        out[mask,k]=s0*((xx-1)**2+yw*yw)*yy**(p/2-5.5)*(1+np.sqrt(yy/ya))**(-p)*1e-18
    return out


def batch_frozen_be_readout(
    rays:Sequence[Sequence[tuple[float,float]]],
    neutrals_cm3:Sequence[Sequence[float]],
    dt_s:Sequence[float],
    ratios:Sequence[float],
) -> tuple[np.ndarray,np.ndarray]:
    """Batch independent rays; shape (nrays,3) for events and excess heat.

    Each ray can use different proper neutrals, dt, and energy-redshift ratio.
    The function does not apply a source Jacobian: that is owned by the producer.
    """
    n=len(rays)
    if not(len(neutrals_cm3)==len(dt_s)==len(ratios)==n):
        raise ValueError('independent-ray input lengths must match')
    rho=np.asarray([_validate_neutrals(a,float(t)) for a,t in zip(neutrals_cm3,dt_s)],dtype=np.float64).reshape(n,3)
    dt=np.asarray(dt_s,dtype=np.float64)
    factors=np.asarray(ratios,dtype=np.float64)
    if np.any(~np.isfinite(factors)) or np.any(factors<=0):
        raise ValueError('invalid per-ray redshift factor')
    energies=[];counts=[];owners=[]
    for k,ray in enumerate(rays):
        for e,m in ray:
            if not(isfinite(e) and isfinite(m)) or e<=0 or m<0:
                raise ValueError('invalid photon packet')
            energies.append(float(e));counts.append(float(m));owners.append(k)
    if not owners:return np.zeros((n,3)),np.zeros((n,3))
    rid=np.asarray(owners,dtype=np.intp)
    energies=np.asarray(energies,dtype=np.float64)*factors[rid]
    if np.any(~np.isfinite(energies)) or np.any(energies<=0) or np.any(energies>50000):
        raise ValueError('forecast outside energy support')
    counts=np.asarray(counts,dtype=np.float64)
    active=energies>=SOURCE_EDGES[0]
    if not np.any(active):return np.zeros((n,3)),np.zeros((n,3))
    energies=energies[active];counts=counts[active];rid=rid[active]
    sigma=_cross_sections_numpy(energies)
    r=dt[rid,None]*C_CM_S*rho[rid,:]*sigma
    ev=(counts[:,None]/(1.+r.sum(axis=1))[:,None])*r
    thresholds=np.asarray([ATOMIC[z][0] for z in ION_NAMES],dtype=np.float64)
    heat=ev*(energies[:,None]-thresholds[None,:])
    return (np.stack([np.bincount(rid,weights=ev[:,i],minlength=n) for i in range(3)],axis=1),
            np.stack([np.bincount(rid,weights=heat[:,i],minlength=n) for i in range(3)],axis=1))
