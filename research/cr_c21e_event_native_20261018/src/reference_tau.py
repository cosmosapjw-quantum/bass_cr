"""Same continuous C21E equations in cumulative optical-depth coordinates.

Not a new cross-section fit or a positivity claim for gas internal stages.
Each impulse-born cohort uses N=N_birth*exp(-tau), with tau accumulated only
while active. Inactive/zero-weight cohorts are structural zeros. IEEE underflow
of a reconstructed survivor is reported, never replaced by an epsilon stock.
"""
from __future__ import annotations
import hashlib
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


def _reference_controls(rtol,atol,size,max_step_divisor):
    """Validate requested FP64 controls before any provider call.

    atol vectors describe the full tau/gas/ledger state. Fixed He fractions
    are removed only when the solver's dynamic-coordinate map is applied.
    """
    def real_array(value,reason):
        try:
            if np.iscomplexobj(value):raise DomainError(reason)
            return np.asarray(value,dtype=float)
        except (TypeError,ValueError,OverflowError) as error:
            raise DomainError(reason) from error
    relative=real_array(rtol,'RADAU_TOLERANCE_DOMAIN')
    absolute=real_array(atol,'RADAU_TOLERANCE_DOMAIN')
    divisor=real_array(max_step_divisor,'RADAU_MAX_STEP_DOMAIN')
    if relative.ndim!=0 or not np.isfinite(relative) or relative<=0:
        raise DomainError('RADAU_TOLERANCE_DOMAIN')
    if absolute.ndim not in (0,1) or (absolute.ndim==1 and absolute.shape!=(size,)):
        raise DomainError('RADAU_TOLERANCE_SHAPE')
    if not np.isfinite(absolute).all() or (absolute<=0).any():
        raise DomainError('RADAU_TOLERANCE_DOMAIN')
    # SciPy's FP64 IVP tolerance floor is 100*eps. Reject below it so that
    # a requested ladder level is never silently replaced by another level.
    floor=100*np.finfo(float).eps
    if relative<floor:raise DomainError('RADAU_RTOL_BELOW_FLOAT64_FLOOR')
    if divisor.ndim!=0 or not np.isfinite(divisor) or divisor<1:
        raise DomainError('RADAU_MAX_STEP_DOMAIN')
    return (float(relative),float(absolute) if absolute.ndim==0 else absolute.copy(),
            float(divisor),float(floor))


def run_reference_tau(f,provider,rtol=2e-10,atol=2e-13,max_cohorts=128,
                      max_evaluations=200000,max_step_divisor=8.0):
    """Integrate the unchanged optical-depth IVP with explicit controls.

    atol is a positive finite scalar or a full-state vector of length M+19.
    max_step_divisor bounds each accepted x=ln(a) step by its event interval
    width divided by this finite value, which must be at least one.
    """
    from run_experiment import breakpoints, initial, opacity, totals
    f.validate();M=len(f.q)
    if M>max_cohorts:raise DomainError('RADAU_DENSE_COHORT_BUDGET')
    rtol,atol,max_step_divisor,rtol_floor=_reference_controls(rtol,atol,M+19,max_step_divisor)
    if max_evaluations<1:raise DomainError('RADAU_EVALUATION_BUDGET')
    g,_=initial(f);y=np.zeros(M+19);y[M:M+4]=g
    ix={'photo':M+4,'ci':M+7,'rr':M+10,'dr':M+13,'escape':M+14,
        'cmb':M+15,'photon_work':M+16,'gas_work':M+17,'heat':M+18}
    amounts=np.asarray(f.amounts,dtype=float)
    birth=np.asarray(f.birth,dtype=float)
    source_n=0.;source_u=0.;nfev=0;calls=0;min_internal_tau=0.;segments=[]
    accepted_min_tau=0.;t0=time.monotonic();cuts=breakpoints(f)
    # Absent helium is not an unknown. The same coordinate map reduces both
    # the state/Jacobian and a requested full-state absolute-tolerance vector.
    dynamic=np.array([j for j in range(len(y)) if not (f.Y==0 and j in (M+1,M+2))])
    solver_atol=atol if np.ndim(atol)==0 else atol[dynamic].copy()
    for lo,hi in zip(cuts[:-1],cuts[1:]):
        active=birth<=lo;calls_before=calls
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
        def reduced_rhs(x,u):
            full=y.copy();full[dynamic]=u
            return rhs(x,full)[dynamic]
        max_step=(hi-lo)/max_step_divisor
        if not math.isfinite(max_step) or max_step<=0:raise DomainError('RADAU_MAX_STEP_DOMAIN')
        solution=solve_ivp(reduced_rhs,(lo,hi),y[dynamic],method='Radau',rtol=rtol,atol=solver_atol,max_step=max_step)
        if not solution.success:raise StepRejected('RADAU_TAU_FAILED '+solution.message)
        if not np.isfinite(solution.y).all():raise StepRejected('RADAU_TAU_NONFINITE')
        if active.any():
            min_tau=float(solution.y[:M][active].min())
            accepted_min_tau=min(accepted_min_tau,min_tau)
            if min_tau<0:raise StepRejected('RADAU_ACCEPTED_NEGATIVE_OPTICAL_DEPTH')
        y[dynamic]=solution.y[:,-1];require_state(y[M:M+4],f.Y)
        nfev+=solution.nfev
        steps=np.diff(solution.t)
        segments.append({'segment':len(segments),'x0':float(lo),'x1':float(hi),
            'nfev':int(solution.nfev),'njev':int(solution.njev),'nlu':int(solution.nlu),
            'accepted_steps':int(len(steps)),
            'accepted_grid_sha256':hashlib.sha256(np.ascontiguousarray(solution.t,dtype='<f8').tobytes(order='C')).hexdigest(),
            'min_x_step':float(steps.min()) if len(steps) else None,
            'max_x_step':float(steps.max()) if len(steps) else None,
            'max_step_bound':float(max_step),'rhs_evaluations':calls-calls_before,
            'status':int(solution.status),'message':str(solution.message)})
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
    nonempty=[s for s in segments if s['accepted_steps']]
    diagnostics={'method':'Radau','independent_variable':'x=ln(a)','segments':segments,
        'accepted_grid_encoding':'C-contiguous little-endian float64 x values, including the initial point and every accepted endpoint',
        **{key:sum(s[key] for s in segments) for key in ('nfev','njev','nlu','accepted_steps')},
        'min_x_step':min(s['min_x_step'] for s in nonempty) if nonempty else None,
        'max_x_step':max(s['max_x_step'] for s in nonempty) if nonempty else None,
        'rhs_evaluations':calls,'rhs_evaluations_include_jacobian_finite_differences':True,
        'counter_note':'nfev is reported by SciPy; rhs_evaluations counts every actual RHS/provider callback, including finite-difference Jacobian callbacks; these counts need not agree'}
    blocks=[{'name':'optical_depth','start':0,'stop':M,'units':'dimensionless'},
        {'name':'gas_fractions','start':M,'stop':M+3,'units':['HII/H','HeII/He','HeIII/He']},
        {'name':'thermal','start':M+3,'stop':M+4,'units':'eV per total H nucleus'}]
    for key,index in ix.items():
        blocks.append({'name':key,'start':index,'stop':index+(3 if key in ('photo','ci','rr') else 1),
            'units':'events per total H nucleus' if key in ('photo','ci','rr','dr') else 'eV per total H nucleus'})
    result.update(schema='C21F_OPTICAL_DEPTH_RADAU_REFERENCE_V1',fixture_sha256=f.digest,
        microphysics=provider.kind,nfev=nfev,rhs_evaluations=calls,wall_s=time.monotonic()-t0,
        status='PASS_SCOPED_CONTINUOUS_IVP',reference_coordinates='cumulative_optical_depth',
        optical_depth=y[:M].tolist(),log_survivor=[float(v) if np.isfinite(v) else None for v in logs],
        underflowed_positive_cohorts=int(np.sum(active & (amounts>0) & (pop==0))),
        min_internal_optical_depth=min_internal_tau,min_accepted_optical_depth=accepted_min_tau,
        photon_clipping=False,gas_domain='unchanged original strict domain',
        independence='Same continuous equations and microphysical kernel; different integration coordinates, not discrete event solver',
        solver_diagnostics=diagnostics,
        tolerance_contract={'rtol':rtol,'atol':float(atol) if np.ndim(atol)==0 else atol.tolist(),
            'atol_kind':'scalar' if np.ndim(atol)==0 else 'full_state_vector',
            'full_state_size':len(y),'integrated_state_size':len(dynamic),'dynamic_indices':dynamic.tolist(),
            'integrated_atol':float(solver_atol) if np.ndim(solver_atol)==0 else solver_atol.tolist(),
            'max_step_divisor':max_step_divisor,'rtol_minimum':rtol_floor,
            'rtol_floor_policy':'reject_below_100_float64_epsilon','coordinate_blocks':blocks,
            'endpoint_sampling_policy':'The provider epoch, opacity and H use xx=min(max(x,lo+1e-9*(hi-lo)),hi-1e-9*(hi-lo)) in each event interval; the state and integration grid retain x',
            'note':'tau absolute tolerance is dimensionless, not equal to absolute photon count tolerance',
            'interpretation':'requested local integration-error scales in the listed coordinates, not a bound on global state or photon errors'})
    return result
