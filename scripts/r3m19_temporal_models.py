#!/usr/bin/env python3
"""Scalar same-grid temporal-model diagnostics; no production admission.

Three samples determine an interpolation, not its remainder. Values at dt=0
are model-dependent. P/norm is an explicitly different diagnostic observable;
it never replaces the subnormalized physical capture probability.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[1]
CANONICAL_PATH=ROOT/'results/R3M18/B_TEMPORAL_ANALYSIS.json'
CANONICAL_SHA256='630a74fb5089e363e3134fce23ffb4086f1bc0c153cc1e7e3e683c5738faea61'
CANONICAL_HEAD='3d033eb08a0efd99257470f0fa27214f569b427a'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def pairs(items):
        out={}
        for key,value in items:
            if key in out:raise ValueError('duplicate JSON key: '+key)
            out[key]=value
        return out
    def invalid(value):raise ValueError('nonfinite JSON token: '+value)
    return json.loads(Path(path).read_text(),object_pairs_hook=pairs,parse_constant=invalid)


def write_new(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')


def _triplet(values,steps):
    if len(values)!=3 or len(steps)!=3:
        raise ValueError('exactly three values and actual dt values required')
    if not all(math.isfinite(x) for x in values):
        raise ValueError('finite values required')
    if not all(math.isfinite(x) and x>0 for x in steps) or not steps[0]>steps[1]>steps[2]:
        raise ValueError('strictly decreasing finite positive actual dt required')
    return np.asarray(values,dtype=float),np.asarray(steps,dtype=float)


def even_interpolant(values,steps):
    """Interpolate P∞+c2*u+c4*u² with u=(dt/dt_finest)² to limit scaling loss."""
    values,steps=_triplet(values,steps)
    u=(steps/steps[-1])**2
    matrix=np.column_stack((np.ones(3),u,u*u))
    condition=float(np.linalg.cond(matrix))
    if not math.isfinite(condition) or condition>=1/np.finfo(float).eps:
        raise ValueError('even interpolation is numerically singular')
    c0,c2,c4=map(float,np.linalg.solve(matrix,values))
    reconstructed=matrix@np.array([c0,c2,c4])
    correction=c0-float(values[-1])
    return {
        'status':'THREE_POINT_INTERPOLATION_ONLY',
        'model':'P(dt)=P_infinity+c2_scaled*(dt/dt_ref)^2+c4_scaled*(dt/dt_ref)^4',
        'dt_ref_au':float(steps[-1]),'P_at_dt_zero':c0,
        'c2_scaled_at_finest':c2,'c4_scaled_at_finest':c4,
        'c2_physical_au':c2/float(steps[-1]**2),
        'c4_physical_au':c4/float(steps[-1]**4),
        'coefficient_units':'P dimensionless; physical c2 in t_a^-2 and c4 in t_a^-4',
        'fine_error_absolute_under_model':abs(correction),
        'fine_error_relative_under_model':abs(correction)/abs(float(values[-1])) if values[-1]!=0 else None,
        'signed_dt4_over_dt2_at_coarsest':c4*float(u[0])/c2 if c2!=0 else None,
        'scaled_matrix_condition':condition,
        'reconstruction_max_absolute':float(np.max(abs(reconstructed-values))),
        'three_point_fit_validates_remainder':False,'certified_error_bound':None,
        'unidentified_even_degree_six':{
            'null_term':'lambda*product_j(u-u_j), u=(dt/dt_ref)^2',
            'u_samples':u.tolist(),
            'P0_shift_per_lambda':-float(np.prod(u)),
            'three_point_data_constrain_lambda':False,
            'meaning':'This smooth even term preserves all three samples but changes the dt=0 limit; local positivity may restrict lambda, not identify it.',
        },
    }


def single_power_model(values,steps):
    values,steps=_triplet(values,steps)
    d01,d12=map(float,np.diff(values))
    out={'status':'UNRESOLVED_DIFFERENCES','observed_order':None,'P_at_dt_zero':None,
         'fine_error_absolute_under_model':None,'fine_error_relative_under_model':None,
         'model':'P(dt)=P_infinity+c*dt^p; fitted on the same three samples',
         'budget_closed':False,'three_point_fit_validates_remainder':False,'certified_error_bound':None}
    floor=64*np.finfo(float).eps*float(np.max(abs(values)))
    if min(abs(d01),abs(d12))<=floor:return out
    if d01*d12<0:
        out['status']='SIGN_CHANGE';return out
    if abs(d12)>=abs(d01):
        out['status']='NO_CONTRACTION';return out
    l01,l12=math.log(steps[0]/steps[1]),math.log(steps[1]/steps[2])
    ratio=d01/d12
    def model(p):return math.expm1(p*l01)/(-math.expm1(-p*l12))
    if not model(1e-6)<ratio<model(12):
        out['status']='NO_POSITIVE_ORDER_IN_REGISTERED_RANGE';return out
    p=brentq(lambda x:model(x)-ratio,1e-6,12,xtol=1e-12)
    correction=d12/math.expm1(p*l12)
    out.update(status='EMPIRICAL_CONTRACTION_ONLY',observed_order=p,
               P_at_dt_zero=float(values[-1])+correction,
               fine_error_absolute_under_model=abs(correction),
               fine_error_relative_under_model=abs(correction)/abs(float(values[-1])) if values[-1]!=0 else None)
    return out


def channel_models(values,steps):
    values,steps=_triplet(values,steps)
    d01,d12=map(float,np.diff(values))
    p2_correction=d12/((steps[1]/steps[2])**2-1)
    return {
        'values':values.tolist(),'actual_dt':steps.tolist(),
        'signed_coarse_change':d01,'signed_fine_change':d12,
        'fine_pair_relative':abs(d12)/abs(float(values[-1])) if values[-1]!=0 else None,
        'single_power':single_power_model(values,steps),
        'even_dt2_dt4':even_interpolant(values,steps),
        'assumed_second_order':{
            'P_at_dt_zero':float(values[-1])+float(p2_correction),
            'fine_error_absolute':abs(float(p2_correction)),
            'fine_error_relative':abs(float(p2_correction))/abs(float(values[-1])) if values[-1]!=0 else None,
            'p_equals_two_independently_validated':False,
            'meaning':'two finest levels with an assumed leading dt^2 error, not a bound',
        },
        'budget_closed':False,'production_admitted':False,
    }


def _validate_rows(rows):
    if not isinstance(rows,dict) or not all(k in rows for k in ('B0','B1','B2')):
        raise ValueError('B0/B1/B2 rows required')
    horizons=[]
    for name in ('B0','B1','B2'):
        row=rows[name]
        for field in ('P1','P2','P3','norm','actual_dt'):
            value=row[field]
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
                raise ValueError('invalid finite scalar '+name+'.'+field)
        if not 0<row['norm']<=1+2e-10 or row['actual_dt']<=0:
            raise ValueError('invalid norm or dt')
        if not 0<=row['P1']<=row['P2']<=row['P3']<=row['norm']:
            raise ValueError('invalid finite-span probability nesting')
        nstep=row['nstep']
        if type(nstep) is not int or nstep<1:raise ValueError('invalid nstep')
        horizons.append(nstep*row['actual_dt'])
    if not all(math.isclose(x,horizons[0],rel_tol=2e-14,abs_tol=0.) for x in horizons):
        raise ValueError('physical horizon identity mismatch')
    return horizons


def analyze_rows(rows):
    horizons=_validate_rows(rows)
    data=[rows[k] for k in ('B0','B1','B2')]
    steps=[r['actual_dt'] for r in data]
    values={p:[r[p] for r in data] for p in ('P1','P2','P3')}
    values.update(shell_n2=[r['P2']-r['P1'] for r in data],
                  shell_n3=[r['P3']-r['P2'] for r in data],
                  P3_divided_by_survival_norm=[r['P3']/r['norm'] for r in data])
    observables={key:channel_models(value,steps) for key,value in values.items()}
    for key,value in observables.items():
        value['physical_capture_probability']=key!='P3_divided_by_survival_norm'
        value['scope']=('SURVIVAL_CONDITIONED_DIAGNOSTIC_NOT_CAPTURE_PROBABILITY' if key=='P3_divided_by_survival_norm'
                        else 'FINITE_SELECTED_SPAN_OR_NESTED_SPAN_INCREMENT_NOT_ALL_BOUND')
    norms=[r['norm'] for r in data]
    decomp=[]
    for old,new in zip(data[:-1],data[1:]):
        state_term=(new['P3']-old['P3'])/new['norm']
        norm_term=old['P3']*(1/new['norm']-1/old['norm'])
        direct=new['P3']/new['norm']-old['P3']/old['norm']
        decomp.append({'raw_capture_change_over_new_norm':state_term,
                       'normalization_change_term':norm_term,
                       'conditional_observable_change':direct,
                       'identity_residual':abs(state_term+norm_term-direct)})
    return {
        'schema':'BASS_CR_R3M19_TEMPORAL_MODEL_COMPARISON_V1',
        'status':'SCALAR_DIAGNOSTIC_COMPLETE_NOT_SCIENTIFIC_ADMISSION',
        'actual_horizons_au':horizons,
        'observables':observables,
        'CAP_norm_diagnostic':{
            'norms':norms,'absorbed_probability':[1-x for x in norms],
            'signed_norm_changes':[norms[j+1]-norms[j] for j in range(2)],
            'relative_norm_changes':[(norms[j+1]-norms[j])/norms[j+1] for j in range(2)],
            'conditional_probability_decomposition':decomp,
            'CAP_channel_specific_error_inferred':False,
            'meaning':'total norm loss cannot identify channel-specific CAP bias; no post-hoc renormalization of physical outputs',
        },
        'three_point_fit_validates_remainder':False,
        'production_admitted':False,'representation_change_admitted':False,
        'source_observables_overwritten':False,
        'decision':'TIME_REFINEMENT_STILL_OPEN',
    }


def analyze_file(path):
    path=Path(path)
    digest=sha(path)
    if path.resolve()==CANONICAL_PATH.resolve() and digest!=CANONICAL_SHA256:
        raise ValueError('canonical R3M18 temporal summary identity changed')
    source=read_json(path)
    result=analyze_rows(source['rows'])
    result['source']={'path':str(path),'sha256':digest,
                      'canonical_sha_matched':digest==CANONICAL_SHA256,
                      'canonical_repository_head':CANONICAL_HEAD if digest==CANONICAL_SHA256 else None}
    result['instrumentation_sha256']=sha(Path(__file__))
    result['evidence_scope']={
        'execution':'arithmetic recomputation from small repository summaries only',
        'B2_raw_state_reprojection':'NOT_RUN',
        'B2_raw_result_in_repository':(ROOT/'results/R3M18/B2_result.json').is_file(),
        'small_evidence_gap':'At canonical R3M18, B2 raw result/witness/seal receipts are referenced in external pointers, not committed as raw small files; local handoff should publish existing bytes unchanged.',
        'large_arrays_downloaded':False,'production_trajectories_run':False,
    }
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=CANONICAL_PATH)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError('preserve existing diagnostic evidence')
    result=analyze_file(args.input)
    write_new(args.out,result)
    print(json.dumps({'status':result['status'],'out':str(args.out),'production_admitted':False}))


if __name__=='__main__':main()
