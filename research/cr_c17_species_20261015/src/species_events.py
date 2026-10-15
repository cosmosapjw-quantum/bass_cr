"""C17 competing-species H/He photon photoevent quadrature.

Piecewise-affine proper-time photon emission S(t) [photons/(H second)]
and nonnegative species rates lambda_j(t) [s^-1]. Each time cell uses
the *same* C16 Duhamel total-photon survivor, but now the species
absorption integrals are computed as explicit positive time integrals,
not a fitted opacity branching fraction.

E_j = integral_0^dt lambda_j(t) N(t) dt, with
N(t)=N0 exp(-int_0^t lambda)
     +integral_0^t S(s) exp(-int_s^t lambda) ds.
The vectorized nested positive Gauss quadrature is independent from
the old C16 branching formula; SciPy Radau is the external reference.

Only local temporal photon/HI/HeI/HeII reaction physics is addressed:
no spatial ray flux, evolving gas chemistry, OTS or owner R*J.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss

from endpoint_quadrature import optical_quadrature, _checked


def _legendre01(n):
    x,w=leggauss(n)
    return .5*(x+1),.5*w


def _source_at_outer(s0,s1,lt0,lt1,dt,frac,inner_nodes):
    """Positive source-born N(t) at outer t/dt quadrature abscissae.

    Arrays first axis photons, second axis outer time.
    Chunked caller bounds memory for packet x outer x inner tensors.
    """
    frac=np.asarray(frac,float)
    m=len(s0)
    t=dt*frac[None,:]                              # [1,T]
    Lt=lt0[:,None]+(lt1-lt0)[:,None]*frac[None,:]
    St=s0[:,None]+(s1-s0)[:,None]*frac[None,:]
    span=t
    scale=np.maximum(1.,np.maximum(span*Lt, np.sqrt(span*lt0[:,None])))
    limit=np.minimum(scale,80.)
    r,w=_legendre01(inner_nodes)
    z=limit[:,:,None]*r[None,None,:]         # optical x
    u=z/scale[:,:,None]                      # reverse time frac in [0,1]
    attenuation=span[:,:,None]*(Lt[:,:,None]*u+
                      .5*(lt0[:,None,None]-Lt[:,:,None])*u*u)
    emission=St[:,:,None]+(s0[:,None,None]-St[:,:,None])*u
    # Source-born stock at each requested t, preserving exact time 0.
    return span * limit/scale * np.sum(
       w[None,None,:]*emission*np.exp(-attenuation),axis=2)


def _integrate_old(N0,l0,l1,dt,order):
    """Exactly age-zero photons: optically adapted positive event integral."""
    total0=l0.sum(axis=1)
    total1=l1.sum(axis=1)
    scale=np.maximum(1.,np.maximum(dt*total0,np.sqrt(dt*total1)))
    limit=np.minimum(scale,80.)
    x,w=_legendre01(order)
    z=limit[:,None]*x[None,:]
    u=z/scale[:,None]
    ell=l0[:,None,:]+(l1-l0)[:,None,:]*u[:,:,None]
    tau=dt*(total0[:,None]*u+
             .5*(total1-total0)[:,None]*u*u)
    weight=N0[:,None,None]*dt*(limit/scale)[:,None,None]*(
         w[None,:,None]*ell*np.exp(-tau)[:,:,None])
    return np.sum(weight,axis=1),np.sum(weight*u[:,:,None],axis=1)


def _integrate_birth(s0,s1,l0,l1,dt,outer,inner):
    """Continuous births: ∫ lambda_j(t) N_source(t) dt."""
    t,w=_legendre01(outer)
    Lt=l0[:,None,:]+(l1-l0)[:,None,:]*t[None,:,None]
    Ns=_source_at_outer(s0,s1,l0.sum(axis=1),
                        l1.sum(axis=1),dt,t,inner)
    weighted=dt*w[None,:,None]*Lt*Ns[:,:,None]
    return np.sum(weighted,axis=1),np.sum(weighted*t[None,:,None],axis=1)


def species_resolved_affine(photons,source_start,source_end,rate_start,
                            rate_end,dt,*,outer_nodes=64,
                            inner_nodes=48,chunk=256,
                            with_time_moments=False,
                            quadrature_defect_budget=1e-3):
    """Positive species-resolved source/opacity update, batched.

    Returns: survivor [P], species photoevents [P,3] (or [P,S]).
    Surviving total uses C16 optical quadrature, and old+new event
    integral moments use independently evaluated positive quadrature.
    The two sets can differ by numerical quadrature: renormalize
    ONLY each old/new species event vector by its physically computed
    total lost photons to close the ledger. Large quadrature defects
    are reported as errors, not hidden by tolerant normalization.
    """
    N,s0,s1,L0,L1=_checked(photons,source_start,source_end,
                            rate_start,rate_end,dt)
    if chunk<1 or outer_nodes<8 or inner_nodes<8 or quadrature_defect_budget<=0:
        raise ValueError("invalid quadrature resource bounds")
    m=len(N);species=L0.shape[1]
    out=np.empty(m,dtype=float)
    events=np.empty((m,species),dtype=float)
    time_moments=np.empty((m,species),dtype=float) if with_time_moments else None
    diagnostics={"max_old_moment_relative_defect":0.,
                 "max_birth_moment_relative_defect":0.,
                 "quadrature_nodes":(int(outer_nodes),int(inner_nodes)),
                 "chunk":int(chunk)}
    for low in range(0,m,chunk):
        hi=min(m,low+chunk)
        n=N[low:hi];s=s0[low:hi];s_end=s1[low:hi]
        a=L0[low:hi];b=L1[low:hi]
        total,_=optical_quadrature(n,s,s_end,a,b,dt,nodes=max(64,inner_nodes))
        # A truly zero-opacity channel has exactly zero absorption.
        # Force its analytic photon endpoint rather than subtract two
        # roundoff-different near-equal source integrals.
        no_opacity=(a.sum(axis=1)+b.sum(axis=1)==0.)
        total[no_opacity]=n[no_opacity]+.5*dt*(s[no_opacity]+s_end[no_opacity])
        old_end=n*np.exp(-dt*.5*(a.sum(axis=1)+b.sum(axis=1)))
        birth_end=total-old_end
        birth_end=np.maximum(birth_end,0.)
        old_exact=n*(-np.expm1(-dt*.5*(a.sum(axis=1)+b.sum(axis=1))))
        birth_exact=dt*.5*(s+s_end)-birth_end
        tol=1e-12*np.maximum(1.,dt*(s+s_end))
        if np.any(birth_exact < -tol):
            raise ArithmeticError("quadrature created net photon abundance")
        birth_exact=np.maximum(birth_exact,0.)
        birth_exact[no_opacity]=0.

        old_num,old_first=_integrate_old(n,a,b,dt,outer_nodes)
        born_num,born_first=_integrate_birth(s,s_end,a,b,dt,outer_nodes,inner_nodes)
        old_sum=old_num.sum(axis=1)
        born_sum=born_num.sum(axis=1)
        old_ratio=np.abs(old_sum-old_exact)/np.maximum(old_exact,1e-22)
        birth_ratio=np.abs(born_sum-birth_exact)/np.maximum(birth_exact,1e-22)
        diagnostics["max_old_moment_relative_defect"]=max(
               diagnostics["max_old_moment_relative_defect"],float(np.max(old_ratio,initial=0.)))
        diagnostics["max_birth_moment_relative_defect"]=max(
               diagnostics["max_birth_moment_relative_defect"],float(np.max(birth_ratio,initial=0.)))
        if np.any((old_ratio>quadrature_defect_budget)&(old_exact>1e-18)) or np.any((birth_ratio>quadrature_defect_budget)&(birth_exact>1e-18)):
            raise ArithmeticError("source/old photoevent quadrature exceeds numerical fidelity budget")
        if np.any((old_sum<=0)&(old_exact>1e-18)) or np.any((born_sum<=0)&(birth_exact>1e-18)):
            bad_old=np.flatnonzero((old_sum<=0)&(old_exact>1e-18))
            bad_birth=np.flatnonzero((born_sum<=0)&(birth_exact>1e-18))
            raise ArithmeticError(f"positive event quadrature missed actual absorption: old={bad_old}, birth={bad_birth}, tau0={dt*a.sum(axis=1)}, tau1={dt*b.sum(axis=1)}, s0={s}, s1={s_end}, born_exact={birth_exact}, born_quad={born_sum}")
        # Normalization does not change the physical sign or ratios of
        # the independently integrated HI/HeI/HeII event moments.
        old_scale=np.zeros_like(old_exact)
        src_scale=np.zeros_like(birth_exact)
        np.divide(old_exact,old_sum,out=old_scale,where=old_sum>0)
        np.divide(birth_exact,born_sum,out=src_scale,where=born_sum>0)
        ev=old_num*old_scale[:,None]+born_num*src_scale[:,None]
        if with_time_moments:
            time_moments[low:hi]=old_first*old_scale[:,None]+born_first*src_scale[:,None]
        if np.any(ev<0) or np.any(total<0):
            raise ArithmeticError("unphysical negative photon event or survivor")
        out[low:hi]=total
        events[low:hi]=ev
    if with_time_moments:
        return out,events,diagnostics,time_moments
    return out,events,diagnostics


def affine_photoheat(events, time_moments, energy_start_eV,
                     energy_end_eV, binding_eV):
    """Species photoelectron heat for linear physical photon-energy drift.

    E(t)=E0+(E1-E0)t/dt, and time_moment_j=∫(t/dt)lambda_j N dt.
    Q_j=(E0-I_j)events_j+(E1-E0)time_moment_j.
    Input energies MUST be above species binding where reactions occur;
    split the step at ionization-energy thresholds first.
    """
    ev=np.asarray(events,float)
    moment=np.asarray(time_moments,float)
    e0=np.asarray(energy_start_eV,float)
    e1=np.asarray(energy_end_eV,float)
    bind=np.asarray(binding_eV,float)
    if (ev.ndim!=2 or moment.shape!=ev.shape or e0.shape!=(len(ev),)
         or e1.shape!=e0.shape or bind.shape!=(ev.shape[1],)):
        raise ValueError("invalid time-dependent photoheat shapes")
    if (not all(np.all(np.isfinite(x)) for x in (ev,moment,e0,e1,bind))
            or np.any(ev<0) or np.any(moment<0) or np.any(moment>ev+1e-13)):
        raise ValueError("nonphysical events or temporal photoevent moments")
    active=ev>1e-14
    if np.any(active & ((e0[:,None]<bind[None,:])
                         | (e1[:,None]<bind[None,:]))):
        raise ValueError("active photon energy crosses physical binding; split interval")
    # Two manifestly nonnegative pieces for threshold-partitioned
    # intervals with E0,E1 >= I_j.
    left=np.maximum(ev-moment,0)
    right=moment
    heating=left*(e0[:,None]-bind[None,:])+right*(e1[:,None]-bind[None,:])
    if np.any(heating<-1e-12):
        raise ArithmeticError("negative photoelectron heat")
    return heating


if __name__=="__main__":
    n=np.array([1.])
    s0=np.array([1.])
    s1=s0.copy()
    r0=np.array([[100.,0.,0.]])
    r1=np.array([[0.,100.,0.]])
    x,ev,info=species_resolved_affine(n,s0,s1,r0,r1,1.)
    print("survivor",x,"HI/HeI/HeII events",ev,"diagnostic",info)
