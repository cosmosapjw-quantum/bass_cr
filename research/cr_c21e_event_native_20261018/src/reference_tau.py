"""Same continuous C21E equations in cumulative optical-depth coordinates.

Not a new cross-section fit or a positivity claim for gas internal stages.
Each impulse-born cohort uses N=N_birth*exp(-tau), with tau accumulated only
while active. Inactive/zero-weight cohorts are structural zeros. IEEE underflow
of a reconstructed survivor is reported, never replaced by an epsilon stock.
"""
from __future__ import annotations
import math
import time
import numpy as np
from scipy.integrate import solve_ivp
from event_coupler import H, BIND_EV, alpha, event_fractions, require_state, DomainError, StepRejected


def reconstruct_population(amounts, tau, active):
    amounts=np.asarray(amounts,dtype=float)
    tau=np.asarray(tau,dtype=float)
    active=np.asarray(active,dtype=bool)
    if amounts.ndim!=1 or tau.shape!=amounts.shape or active.shape!=amounts.shape:
        raise DomainError('OPTICAL_COORDINATE_SHAPE')
    if not np.isfinite(amounts).all() or not np.isfinite(tau).all() or (amounts<0).any():
        raise DomainError('OPTICAL_COORDINATE_DOMAIN')
    keep=active & (amounts>0)
    out=np.zeros_like(amounts)
    logs=np.full_like(amounts,-np.inf)
    # Internal implicit tau stages may be negative. Analytic continuation gives
    # a positive N; this does not project tau, alter the ODE or certify the stage.
    logs[keep]=np.log(amounts[keep])-tau[keep]
    if np.any(logs[keep]>np.log(np.finfo(float).max)):
        raise DomainError('OPTICAL_COORDINATE_OVERFLOW')
    with np.errstate(under='ignore'):
        out[keep]=np.exp(logs[keep])
    return out,logs


def run_reference_tau(f,provider,rtol=2e-10,atol=2e-13,max_cohorts=128,
                      max_evaluations=200000):
    from run_experiment import breakpoints, initial, opacity, totals
    f.validate();M=len(f.q)
    if M>max_cohorts:raise DomainError('RADAU_DENSE_COHORT_BUDGET')
    if not all(math.isfinite(v) and v>0 for v in (rtol,atol)):
        raise DomainError('RADAU_TOLERANCE_DOMAIN')
    if max_evaluations<1:raise DomainError('RADAU_EVALUATION_BUDGET')
    g,_=initial(f);y=np.zeros(M+19);y[M:M+4]=g
    ix={'photo':M+4,'ci':M+7,'rr':M+10,'dr':M+13,'escape':M+14,
        'cmb':M+15,'photon_work':M+16,'gas_work':M+17,'heat':M+18}
    amounts=np.asarray(f.amounts,dtype=float)
    birth=np.asarray(f.birth,dtype=float)
    source_n=0.;source_u=0.;nfev=0;calls=0;min_internal_tau=0.
    accepted_min_tau=0.;t0=time.monotonic();cuts=breakpoints(f)
    for lo,hi in zip(cuts[:-1],cuts[1:]):
        active=birth<=lo
        def rhs(x,v):
            nonlocal calls,min_internal_tau
            calls+=1
            if calls>max_evaluations:raise StepRejected('RADAU_EVALUATION_BUDGET')
            xx=min(max(x,lo+1e-9*(hi-lo)),hi-1e-9*(hi-lo))
            gv=v[M:M+4];require_state(gv,f.Y)
            pop,_=reconstruct_population(amounts,v[:M],active)
            if active.any():min_internal_tau=min(min_internal_tau,float(v[:M][active].min()))
            micro=provider(math.exp(xx),gv,f.nh0,f.Y);micro.validate(f.Y)
            E,k=opacity(f,xx)
            hazard=k*alpha(gv,f.Y)[None,:]
            rates=pop[:,None]*hazard
            h=H(xx);species=rates.sum(axis=0)
            heat=float(np.sum(rates*(E[:,None]-np.asarray(BIND_EV)[None,:])))
            out=np.zeros_like(v)
            # tau' has no multiplying N and no population division.
            out[:M]=hazard.sum(axis=1)*active/h
            out[M:M+3]=(event_fractions(species,f.Y)+micro.fraction_s)/h
            out[M+3]=(heat+micro.thermal_ev_h_s)/h-2*gv[3]
            out[ix['photo']:ix['photo']+3]=species/h
            out[ix['ci']:ix['ci']+3]=micro.ci_h_s/h
            out[ix['rr']:ix['rr']+3]=micro.rr_h_s/h
            out[ix['dr']]=micro.dr_h_s/h
            out[ix['escape']]=micro.escaped_ev_h_s/h
            out[ix['cmb']]=micro.cmb_ev_h_s/h
            out[ix['photon_work']]=float(pop@E)
            out[ix['gas_work']]=2*gv[3]
            out[ix['heat']]=heat/h
            if not np.isfinite(out).all():raise DomainError('OPTICAL_RHS_NONFINITE')
            return out
        # Absent helium is not an unknown. Remove its fixed fractions from the
        # numerical Jacobian rather than perturbing forbidden He components.
        dynamic=np.array([j for j in range(len(y)) if not (f.Y==0 and j in (M+1,M+2))])
        def reduced_rhs(x,u):
            full=y.copy();full[dynamic]=u
            return rhs(x,full)[dynamic]
        solution=solve_ivp(reduced_rhs,(lo,hi),y[dynamic],method='Radau',rtol=rtol,atol=atol,max_step=(hi-lo)/8)
        if not solution.success:raise StepRejected('RADAU_TAU_FAILED '+solution.message)
        if not np.isfinite(solution.y).all():raise StepRejected('RADAU_TAU_NONFINITE')
        if active.any():
            min_tau=float(solution.y[:M][active].min())
            accepted_min_tau=min(accepted_min_tau,min_tau)
            if min_tau<0:raise StepRejected('RADAU_ACCEPTED_NEGATIVE_OPTICAL_DEPTH')
        y[dynamic]=solution.y[:,-1];require_state(y[M:M+4],f.Y)
        nfev+=solution.nfev
        # Birth changes the cohort's activation, not its cumulative tau.
        for index,xb in enumerate(birth):
            if xb==hi and xb>f.x0:
                if y[index]!=0.:raise StepRejected('UNBORN_OPTICAL_DEPTH_CHANGED')
                source_n+=float(amounts[index]);source_u+=float(amounts[index]*f.q[index]*math.exp(-xb))
    active=birth<=f.x0+f.dx
    pop,logs=reconstruct_population(amounts,y[:M],active)
    led={key:y[j:j+3].tolist() if key in ('photo','ci','rr') else float(y[j]) for key,j in ix.items()}
    led.update(source_n=source_n,source_u=source_u)
    result=totals(f,y[M:M+4],pop,led)
    result.update(schema='C21F_OPTICAL_DEPTH_RADAU_REFERENCE_V1',fixture_sha256=f.digest,
        microphysics=provider.kind,nfev=nfev,rhs_evaluations=calls,wall_s=time.monotonic()-t0,
        status='PASS_SCOPED_CONTINUOUS_IVP',reference_coordinates='cumulative_optical_depth',
        optical_depth=y[:M].tolist(),log_survivor=[float(v) if np.isfinite(v) else None for v in logs],
        underflowed_positive_cohorts=int(np.sum(active & (amounts>0) & (pop==0))),
        min_internal_optical_depth=min_internal_tau,min_accepted_optical_depth=accepted_min_tau,
        photon_clipping=False,gas_domain='unchanged original strict domain',
        independence='Same continuous equations and microphysical kernel; different integration coordinates, not discrete event solver',
        tolerance_contract={'rtol':rtol,'atol':atol,'note':'tau absolute tolerance is dimensionless, not equal to absolute photon count tolerance'})
    return result
