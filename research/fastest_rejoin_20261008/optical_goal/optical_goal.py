"""Conditional first-cell Thomson depth enclosure from BRIDGE12 *stored* residual slices.

Proof convention:
 s=t/L in [0,1], e=z_true-z_hat, r=z_hat' - F(s,z_hat).
 tau_goal = C_T*nH0*L*int_0^1 exp(-alpha*s)*X_e(s) ds.
 e(s)=-int_0^s r(u)du+int_0^s (F(z_true)-F(z_hat))(u)du.
 The second term uses donor's full-tube Jacobian absolute majorant and
 all-prefix |e| bound. This is NOT a new independent validation of that donor.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from math import factorial
import json, hashlib

class SourceContractError(ValueError): pass

def q(x):
    if isinstance(x,bool):raise SourceContractError('BOOLEAN_NOT_NUMERIC')
    try:return F(x)
    except (TypeError,ValueError,ZeroDivisionError,OverflowError) as e:raise SourceContractError('INVALID_RATIONAL_INPUT') from e

def exact_binary_float(x):
    if not isinstance(x,float):raise SourceContractError('EXPECTED_EXACT_BINARY64')
    return F.from_float(x)

def interval(v):
    if not isinstance(v,(list,tuple)) or len(v)!=2:raise SourceContractError('TWO_ENDPOINT_INTERVAL_REQUIRED')
    a,b=map(q,v)
    if a>b:raise SourceContractError('REVERSED_INTERVAL')
    return a,b

def multiply_intervals(x,y):
    a,b=interval(x);c,d=interval(y)
    vals=(a*c,a*d,b*c,b*d)
    return min(vals),max(vals)

def moment_J(a,b,alpha,n):
    """Integral from a to b of du Integral from u to 1 of Taylor_n(exp(-alpha*s)) ds."""
    ans=F(0)
    for k in range(n+1):
        term=(-alpha)**k/F(factorial(k)*(k+1))
        ans+=term*((b-a)-(b**(k+2)-a**(k+2))/F(k+2))
    return ans

def exp_integrated_kernel(a,b,alpha):
    if not (F(0)<=a<b<=F(1)) or not (F(0)<=alpha<=F(1)):
        raise SourceContractError('EXP_KERNEL_DOMAIN')
    # exp(-x) in [Taylor5, Taylor6] for 0<=x<=1; positive integration weights.
    lo=moment_J(a,b,alpha,5);hi=moment_J(a,b,alpha,6)
    if not F(0)<=lo<=hi:raise SourceContractError('KERNEL_NOT_NONNEGATIVE')
    return lo,hi

def error_from_slices(slices,alpha,f_he,coupling,scale):
    """Full-cell signed tau_cont-tau_linear error from sliced residual and coupling.

    residual values are derivatives per normalized s in z=(h,y,z,w/w0,P/P0).
    coupling is donor N*sup|e| for h, HeII, HeIII (per normalized s).
    scale=C_T*nH0*L; no extra H, density, a^-3 or time factor.
    """
    alpha=q(alpha);f_he=q(f_he);scale=q(scale)
    if not F(0)<=alpha<=1 or not F(0)<=f_he<=1 or scale<=0:
        raise SourceContractError('PHYSICAL_CLOCK_OR_SCALE_DOMAIN')
    if len(coupling)!=3 or any(q(e)<0 for e in coupling):
        raise SourceContractError('THREE_NONNEGATIVE_COUPLING_BOUNDS_REQUIRED')
    if not isinstance(slices,list) or not slices:
        raise SourceContractError('RESIDUAL_PANELS_REQUIRED')
    pos=F(0);low=F(0);high=F(0)
    for panel in slices:
        if not isinstance(panel,dict):raise SourceContractError('BAD_PANEL')
        a,b=interval(panel.get('s'))
        if a!=pos or b>1 or b<=a:
            raise SourceContractError('RESIDUAL_PANELS_NOT_CONTIGUOUS')
        res=panel.get('residual')
        if not isinstance(res,list) or len(res)!=5:raise SourceContractError('EXPECTED_FIVE_SCALED_RESIDUALS')
        h,y,z=(interval(res[i]) for i in range(3))
        lo=h[0]+f_he*(y[0]+2*z[0]);hi=h[1]+f_he*(y[1]+2*z[1])
        jlo,jhi=exp_integrated_kernel(a,b,alpha)
        p=multiply_intervals((-hi,-lo),(jlo,jhi))
        low+=p[0];high+=p[1];pos=b
    if pos!=1:raise SourceContractError('RESIDUAL_PANELS_DO_NOT_COVER_CELL')
    _,jtot=exp_integrated_kernel(F(0),F(1),alpha)
    cp=sum((q(v)*w for v,w in zip(coupling,[F(1),f_he,2*f_he])),F(0))
    remainder=scale*jtot*cp
    return {'forcing':(scale*low,scale*high),
            'remainder':remainder,
            'difference':(scale*low-remainder,scale*high+remainder),
            'panels':len(slices)}

def linear_native_tau(initial,eop,f_he,alpha,scale):
    """Exact-real proper nH(t) and linearly interpolated *native* ion fractions."""
    if len(initial)!=3 or len(eop)!=3:raise SourceContractError('GAS_THREE_FRACTIONS_REQUIRED')
    f_he=q(f_he);alpha=q(alpha);scale=q(scale)
    X0=q(initial[0])+f_he*(q(initial[1])+2*q(initial[2]))
    X1=q(eop[0])+f_he*(q(eop[1])+2*q(eop[2]))
    if X0<=0 or X1<=0 or not 0<=alpha<=1 or scale<=0:
        raise SourceContractError('INVALID_LINEAR_XE_OR_CLOCK')
    b=X1-X0
    def partial(n):
        return sum(((-alpha)**k/F(factorial(k))*(X0/F(k+1)+b/F(k+2)) for k in range(n+1)),F(0))
    lo=partial(5);hi=partial(6)
    if not lo<=hi:raise SourceContractError('BAD_ALTERNATING_TAU_BOUND')
    return scale*lo,scale*hi

def certify_first_cell(cert_path,residual_path,point_path):
    cert_bytes=Path(cert_path).read_bytes()
    cert=json.loads(cert_bytes); slices=json.loads(Path(residual_path).read_text());data=json.loads(Path(point_path).read_text())
    if cert.get('task')!='REI-XTHREAD-BRIDGE12-20261008' or cert.get('status')!='FIRST_CONTINUOUS_COHORT_CELL_ENDPOINT_ERROR_ENCLOSED_CONDITIONAL':
        raise SourceContractError('UNPINNED_SCIENTIFIC_TARGET')
    if cert.get('time_s')!=data.get('time_s') or not cert.get('no_source_birth') or not cert.get('no_cutoff_crossing'):
        raise SourceContractError('SOURCE_CLOCK_OR_SMOOTH_CELL_MISMATCH')
    if data.get('first_step_from_original_initial_state') is not True or any(q(v)!=0 for v in cert['initial_gas_and_count_error']):
        raise SourceContractError('NONZERO_INITIAL_ERROR_NOT_SUPPORTED')
    if len(slices)!=cert['time_panels'] or len(cert['duhamel_coupling_remainder_upper_scaled'])!=5:
        raise SourceContractError('DONOR_CERTIFICATE_SLICE_MISMATCH')
    if data['seed']['gas'][:3] != data['source_point']['old'][:3]:
        raise SourceContractError('SAME_INITIAL_STATE_REQUIRED')
    # Producer constants are IEEE-754 values in the realified donor; keep their bits.
    H=exact_binary_float(1e-14)
    L=exact_binary_float(cert['time_s'][1]);nH0=exact_binary_float(1e-4)
    f=exact_binary_float(.083)
    CT=F(299792458)*exact_binary_float(6.6524587e-29)*F(10**6)
    alpha=3*H*L
    scale=CT*nH0*L
    coupling=[q(v) for v in cert['duhamel_coupling_remainder_upper_scaled'][:3]]
    response=error_from_slices(slices,alpha,f,coupling,scale)
    nominal=linear_native_tau([exact_binary_float(float(v)) for v in data['seed']['gas'][:3]],
                              [exact_binary_float(float(v)) for v in data['source_point']['gas'][:3]], f,alpha,scale)
    d=response['difference']
    cont=nominal[0]+d[0],nominal[1]+d[1]
    if not cont[0]<=cont[1]:raise SourceContractError('INCONSISTENT_GOAL_INTERVAL')
    return {**response,'nominal':nominal,'continuous':cont,
            'same_declared_continuous_target':True,
            'observer_tail':None,
            'source_sha256':hashlib.sha256(cert_bytes).hexdigest(),
            'constants':{'sigmaT_m2':exact_binary_float(6.6524587e-29), 'C_T_cm3_per_s':CT,
                         'nH0_cm3':nH0,'H_s':H,'duration_s':L,
                         'f_he':f,'alpha':alpha,'scale':scale},
            'premises':{'interval_backend':'inherited BRIDGE12 Decimal60 with directed and exp/ln contracts',
                        'not_independent_proof_of_donor':True,
                        'single_cell_only':True,
                        'physical_atomic_rate_accuracy':False,
                        'full_history_tau':False,
                        'uniform_parameter_cumulative_ledger':False,
                        'matched_discrete_family_tau':False,
                        'cutoff_or_birth_in_cell':False}}

def to_json(o):
    if isinstance(o,F):return {'num':str(o.numerator),'den':str(o.denominator)}
    if isinstance(o,dict):return {k:to_json(v) for k,v in o.items()}
    if isinstance(o,(tuple,list)):return [to_json(v) for v in o]
    return o

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--donor',required=True);a.add_argument('--output',required=True)
    x=a.parse_args();p=Path(x.donor);res=certify_first_cell(p/'results/final_verified/interval/CELL_CERTIFICATE.json',p/'results/final_verified/interval/RESIDUAL_SLICES.json',p/'inputs/NEXT_CELL_INPUT.json')
    out=Path(x.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(to_json(res),indent=2)+'\n')
    for key in ('nominal','forcing','remainder','difference','continuous'):
        v=res[key];print(key,tuple(f'{float(t):.18e}' for t in v) if isinstance(v,tuple) else f'{float(v):.18e}')
