"""Optical-depth coordinate for the SAME C21E continuous photo/microphysics IVP.

The active population is B_i*exp(-tau_i), not a clipped number unknown.
Optical-depth and gas/ledger tolerances have different physical meanings and
are reported separately. No solver step is a native production certification.
"""
from __future__ import annotations
import math
import time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
import bootstrap  # bind the unmodified sibling before imports
from run_experiment import (Fixture, initial, breakpoints, opacity, totals)
from event_coupler import (H, BIND_EV, alpha, event_fractions,
                           require_state, DomainError, StepRejected)

MIN_SUBNORMAL=float(np.nextafter(0.,1.))
MAX_LOG=math.log(np.finfo(float).max)


def population(amounts, tau, active):
    """Positive coordinate map with structural inactive/zero cohorts.

    Internal Newton tau trials may be negative: the map remains positive.
    Accepted tau is checked independently. Computing log(B)-tau avoids losing
    a representable B*exp(-tau) merely because exp(-tau) alone underflows.
    """
    b=np.asarray(amounts,float);t=np.asarray(tau,float);mask=np.asarray(active,bool)
    if b.ndim!=1 or t.shape!=b.shape or mask.shape!=b.shape:
        raise DomainError('HAZARD_POPULATION_SHAPE')
    if not np.isfinite(b).all() or not np.isfinite(t).all() or (b<0).any():
        raise DomainError('HAZARD_POPULATION_DOMAIN')
    n=np.zeros_like(b);use=mask & (b>0)
    if use.any():
        logn=np.log(b[use])-t[use]
        if (logn>MAX_LOG).any():raise DomainError('HAZARD_INTERNAL_EXP_OVERFLOW')
        with np.errstate(under='ignore'):
            n[use]=np.exp(logn)
        n[use & (t==0)]=b[use & (t==0)]
    if not np.isfinite(n).all():raise DomainError('HAZARD_NONFINITE_POPULATION')
    return n


def run_reference(f:Fixture,provider,rtol=2e-10,atol=2e-13,max_cohorts=128,
                  *,tau_atol=1e-12,method='Radau',output:Path|None=None):
    """Integrate tau+gas+independent ledgers on the exact C21E event partition.

    `atol` applies to original gas/ledger variables. `tau_atol` is dimensionless.
    State/opacity/source/microphysics are unchanged. No log photon floor, no
    projected gas and no replacement of failed native rates is introduced.
    """
    f.validate();M=len(f.q)
    if M>max_cohorts:raise DomainError('HAZARD_COHORT_BUDGET')
    if method not in ('Radau','DOP853'):raise DomainError('REFERENCE_METHOD')
    if not all(math.isfinite(v) and v>0 for v in (rtol,atol,tau_atol)):
        raise DomainError('REFERENCE_TOLERANCE_DOMAIN')
    gas0,_=initial(f);amounts=np.array(f.amounts)
    # tau[M],gas[4], photo/CI/RR[3 each],DR,escape,CMB,photonwork,gaswork,heat
    state=np.zeros(M+19);state[M:M+4]=gas0
    ix={'photo':M+4,'ci':M+7,'rr':M+10,'dr':M+13,'escape':M+14,
        'cmb':M+15,'photon_work':M+16,'gas_work':M+17,'heat':M+18}
    abs_tol=np.full(M+19,atol);abs_tol[:M]=tau_atol
    # Absent helium is removed from the nonlinear vector, not projected during RHS.
    free=np.array([i for i in range(M+19) if f.Y>0 or i not in (M+1,M+2)],dtype=int)
    cuts=breakpoints(f);rows=[];nfev=0;rhs_calls=0;micro_calls=0
    start=time.monotonic();log=None
    cache_key=None;cache_value=None
    if output is not None:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        log=(output/'hazard_segments.jsonl').open('x')
    try:
        for lo,hi in zip(cuts[:-1],cuts[1:]):
            active=np.array([b<=lo for b in f.birth]);used=active & (amounts>0)
            old_tau=state[:M].copy()
            def rhs(x,v):
                nonlocal rhs_calls,micro_calls,cache_key,cache_value
                rhs_calls+=1
                # Same smooth-cell one-sided sampling policy as parent.
                xx=min(max(x,lo+1e-9*(hi-lo)),hi-1e-9*(hi-lo))
                g=v[M:M+4];require_state(g,f.Y)
                n=population(amounts,v[:M],used)
                E,k=opacity(f,xx);h=H(xx)
                lam=k*alpha(g,f.Y)[None,:]*used[:,None]
                events=n[:,None]*lam
                species=events.sum(axis=0)
                heat=float(np.sum(events*(E[:,None]-np.array(BIND_EV)[None,:])))
                # Native nonphoto point depends on gas/epoch, not tau or ledgers.
                # Reuse only exact binary input identity, never a tolerance bucket.
                key=(xx,f.nh0,f.Y,g.tobytes())
                if key!=cache_key:
                    cache_value=provider(math.exp(xx),g,f.nh0,f.Y);micro_calls+=1
                    cache_value.validate(f.Y);cache_key=key
                micro=cache_value
                out=np.zeros_like(v)
                out[:M]=lam.sum(axis=1)/h
                out[M:M+3]=(event_fractions(species,f.Y)+micro.fraction_s)/h
                out[M+3]=(heat+micro.thermal_ev_h_s)/h-2*g[3]
                for key,vals in [('photo',species),('ci',micro.ci_h_s),('rr',micro.rr_h_s)]:
                    out[ix[key]:ix[key]+3]=vals/h
                out[ix['dr']]=micro.dr_h_s/h
                out[ix['escape']]=micro.escaped_ev_h_s/h
                out[ix['cmb']]=micro.cmb_ev_h_s/h
                out[ix['photon_work']]=float(n@E)
                out[ix['gas_work']]=2*g[3]
                out[ix['heat']]=heat/h
                if not np.isfinite(out).all():raise DomainError('HAZARD_RHS_NONFINITE')
                return out
            def reduced_rhs(x,reduced):
                full=np.zeros(M+19);full[free]=reduced
                return rhs(x,full)[free]
            solution=solve_ivp(reduced_rhs,(lo,hi),state[free],method=method,rtol=rtol,atol=abs_tol[free],max_step=(hi-lo)/8)
            if not solution.success:raise StepRejected('HAZARD_IVP_FAILED '+solution.message)
            state=np.zeros(M+19);state[free]=solution.y[:,-1];nfev+=solution.nfev
            require_state(state[M:M+4],f.Y)
            if not np.isfinite(state).all() or (state[:M]<0).any():
                raise StepRejected('HAZARD_ACCEPTED_NEGATIVE_OR_NONFINITE_TAU')
            if (state[:M][used]<old_tau[used]).any():raise StepRejected('HAZARD_ACCEPTED_DECREASING_TAU')
            if not (state[:M][~used]==old_tau[~used]).all():raise StepRejected('HAZARD_UNBORN_EVOLUTION')
            row={'x0':lo,'x1':hi,'active_count':int(used.sum()),
                 'max_tau':float(state[:M].max(initial=0)),
                 'gas':state[M:M+4].tolist(),'nfev':solution.nfev,
                 'njev':solution.njev,'nlu':solution.nlu,'accepted_steps':len(solution.t)-1}
            rows.append(row)
            if log is not None:
                import json
                log.write(json.dumps(row,allow_nan=False)+'\n');log.flush()
    finally:
        if log is not None:log.close()
    # Source quantities are counted at exactly the same fixed impulse times.
    source_n=math.fsum(n for n,b in zip(f.amounts,f.birth) if b>f.x0)
    source_u=math.fsum(n*q*math.exp(-b) for n,q,b in zip(f.amounts,f.q,f.birth) if b>f.x0)
    final_active=np.array([b<=f.x0+f.dx for b in f.birth])
    photons=population(amounts,state[:M],final_active)
    ledgers={k:state[j:j+3].tolist() if k in ('photo','ci','rr') else float(state[j]) for k,j in ix.items()}
    ledgers.update(source_n=source_n,source_u=source_u)
    result=totals(f,state[M:M+4],photons,ledgers)
    underflow=(amounts>0)&final_active&(photons==0)
    result.update(schema='C21F_OPTICAL_DEPTH_CONTINUOUS_REFERENCE_V1',fixture_sha256=f.digest,
                  microphysics=provider.kind,status='COMPLETED_IVP_LEDGER_ADMISSION_SEPARATE',
                  reference_method=method,reference_coordinate='TAU_WITH_EXACT_BIRTH_AMPLITUDES',
                  optical_depth=state[:M].tolist(),max_optical_depth=float(state[:M].max(initial=0)),
                  nfev=nfev,rhs_calls=rhs_calls,micro_calls=micro_calls,wall_s=time.monotonic()-start,
                  micro_cache_policy='ONE_ENTRY_EXACT_INPUT_BYTES_ONLY',
                  tolerances={'rtol':rtol,'gas_ledger_atol':atol,'optical_depth_atol':tau_atol},
                  underflow={'cohorts':int(underflow.sum()),'upper_bound_per_zero_H':MIN_SUBNORMAL,
                             'interpretation':'f64 representation limit, not a resolved positive tail'},
                  segments=rows,
                  independence='Exact coordinate transform of parent continuous ODE; independent of discrete event step, SAME microphysical provider')
    return result
