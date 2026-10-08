#!/usr/bin/env python3
"""Prospective B3 empirical temporal estimate; no collision or certification.

The engineering rule is preregistered for this fixed h/H/W/Q/initial family.
Held-out prediction and model spread support a conservative empirical estimate;
neither constitutes a rigorous error bound or closes spatial/all-bound/b gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from cr_repro.r3m11 import source_digest
from cr_repro.util import config_hash
from cr_repro.hydrogen import bound_quantum_numbers
from scripts.r3m17_temporal import (SOURCE,INITIAL_SHA,PINS,enriched,historical_baseline,
                                    read_json,sha,temporal_triplet,validate_result,validate_witness)

B2_RESULT=('results/R3M20_N1/intake/collision/result.json',
           'f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc')
B2_WITNESS=('results/R3M20_N1/intake/collision/r3m14_initial_binding.json',
            '4d61a07dac58a49da82580a31df22e718bbbb0a6236c82a9a0e9d923bbc737b0')
R18_SUMMARY=('results/R3M18/B_TEMPORAL_ANALYSIS.json',
             '630a74fb5089e363e3134fce23ffb4086f1bc0c153cc1e7e3e683c5738faea61')
INITIAL_ARRAY='79a6f07a458e2483f18e01d26c6c9ef380146ebd24844656700dcc0410875826'
B2_PREPARED_RECEIPT='a238656dc9091b9a1a2ba935408549f09c2f55e3cb59497e01c2d927a69cf0dd'
BASE_COMMIT='90d6cbad25e4bc49e9563f8721fdc408761b31c7'
CHANNELS=('P1','P2','P3')
FORECAST_KEYS=('single_power_old_triplet','even_dt2_dt4_old_triplet','leading_p2_B1_B2')
TOLERANCE=.001
ACCEPTED='TEMPORAL_ESTIMATE_VALIDATED_FOR_FIXED_H_SELECTED_SPANS'
# Set once from the pre-B3 deterministic payload. This is an independent code
# pin, not a digest supplied by the evaluated result or by its own report.
EXPECTED_FORECAST_PAYLOAD_SHA256='be693bbae3a90420b25f441431ee0f63b2dd8131fd1c2017c81c847e83a4c64e'


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def payload_hash(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def write_new(path,value):
    text=json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n'
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream: stream.write(text)


def number(x,name,*,positive=False):
    if isinstance(x,(bool,np.bool_)) or not isinstance(x,(int,float,np.integer,np.floating)):
        raise ValueError(f'{name}: actual number required, not Boolean/string')
    x=float(x)
    if not math.isfinite(x) or (positive and x<=0):
        raise ValueError(f'{name}: finite'+(' positive' if positive else '')+' number required')
    return x


def _probabilities(values,count):
    if len(values)!=count: raise ValueError(f'exactly {count} probabilities required')
    vals=[number(v,'probability',positive=True) for v in values]
    if any(v>1+2e-10 for v in vals): raise ValueError('probability exceeds one')
    return vals


def _steps(values,count):
    if len(values)!=count: raise ValueError(f'exactly {count} actual timesteps required')
    out=[number(v,'actual dt',positive=True) for v in values]
    if any(a<=b for a,b in zip(out,out[1:])):raise ValueError('distinct decreasing actual dt required')
    return out


def _even_fit(values,dt,query=0.):
    scale=max(dt); x=(np.asarray(dt,dtype=float)/scale)**2
    matrix=np.column_stack((np.ones(len(x)),x,x*x))
    offset=values[-1]; y=np.asarray(values)-offset
    if len(values)==3: coefficient=np.linalg.solve(matrix,y)
    else: coefficient,_,rank,_=np.linalg.lstsq(matrix,y,rcond=None)
    if np.linalg.matrix_rank(matrix)!=3:raise ValueError('even model rank loss')
    q=(query/scale)**2
    return float(offset+np.array([1.,q,q*q])@coefficient)


def _p2_fit(values,dt,query=0.):
    ratio=(dt[1]/dt[0])**2
    slope=(values[0]-values[1])/(1-ratio)
    central=values[0]-slope
    return float(central+slope*(query/dt[0])**2)


def _single_power(values,dt):
    fit=temporal_triplet(values,dt)
    p=fit['observed_order']; central=fit['extrapolated_value']
    if p is None or central is None:return None
    return float(p),float(central)


def channel_forecasts(values,actual_dt,next_actual_dt):
    values=_probabilities(values,3); dt=_steps(actual_dt,3)
    nxt=number(next_actual_dt,'next actual dt',positive=True)
    if nxt>=dt[-1]:raise ValueError('forecast dt must refine existing finest dt')
    fit=_single_power(values,dt)
    if fit is None:raise ValueError('old triplet single-power forecast is unresolved')
    p,central=fit
    return dict(zip(FORECAST_KEYS,(
        float(central-(central-values[-1])*(nxt/dt[-1])**p),
        _even_fit(values,dt,nxt),_p2_fit(values[-2:],dt[-2:],nxt))))


def channel_gate(values,actual_dt,frozen_forecasts):
    """Arithmetic kernel only. Caller numbers have no raw-evidence authority."""
    v=_probabilities(values,4); dt=_steps(actual_dt,4)
    if set(frozen_forecasts)!=set(FORECAST_KEYS):raise ValueError('three registered forecast models required')
    f={k:number(frozen_forecasts[k],'forecast',positive=True) for k in FORECAST_KEYS}
    changes=[v[2]-v[1],v[3]-v[2]]
    floor=64*np.finfo(float).eps*max(v)
    out={'accepted':False,'status':'UNRESOLVED_FINE_DIFFERENCES',
         'evidence_scope':'SYNTHETIC_OR_CALLER_VALUES_NOT_RAW_EVIDENCE',
         'values':v,'actual_dt':dt,'fine_signed_changes':changes,
         'fine_pair_absolute':abs(changes[-1]),'fine_pair_relative':abs(changes[-1])/v[-1],
         'relative_denominator_B3':v[-1],'roundoff_resolution_floor':floor,
         'relative_target':TOLERANCE,'certified_error_bound':None,
         'fine_observed_order':None,'clean_p2_diagnostic':None,
         'infinite_step_estimates':None,'E_model':None,'D_hold':None,'U_t':None,'U_t_relative':None,
         'leave_one_out_even_diagnostics':[],
         'central_value':v[-1],'central_semantics':'OBSERVED_B3_SELECTED_SPAN_NOT_EXTRAPOLATED_PRODUCTION_CENTRAL'}
    if min(map(abs,changes))<=floor:return out
    if changes[0]*changes[1]<=0:
        out['status']='SIGN_CHANGE_NONASYMPTOTIC'; return out
    if abs(changes[1])>=abs(changes[0]):
        out['status']='NO_FINE_CONTRACTION'; return out
    fit=_single_power(v[1:],dt[1:])
    if fit is None:
        out['status']='FINE_SINGLE_POWER_MODEL_UNRESOLVED'; return out
    p,pinf=fit
    estimates={'fine_p2':_p2_fit(v[2:],dt[2:]),
               'fine_even_dt2_dt4':_even_fit(v[1:],dt[1:]),
               'all_four_even_least_squares':_even_fit(v,dt),
               'fine_triplet_single_power':pinf}
    if not all(math.isfinite(x) and 0<x<=1+2e-10 for x in estimates.values()):
        out['status']='UNPHYSICAL_OR_NONFINITE_MODEL_ESTIMATE'; return out
    loo=[]
    for omitted in range(4):
        ix=[j for j in range(4) if j!=omitted]
        predicted=_even_fit([v[j] for j in ix],[dt[j] for j in ix],dt[omitted])
        loo.append({'omitted_cell':f'B{omitted}','predicted':predicted,
                    'signed_residual':v[omitted]-predicted,'diagnostic_only':True})
    e=max(abs(x-v[-1]) for x in estimates.values())
    d=max(abs(v[-1]-x) for x in f.values()); u=2*max(e,d)
    accepted=out['fine_pair_relative']<=TOLERANCE and u/v[-1]<=TOLERANCE
    out.update(accepted=accepted,status=ACCEPTED if accepted else 'EMPIRICAL_TEMPORAL_BUDGET_OPEN',
               fine_observed_order=p,clean_p2_diagnostic=1.5<=p<=2.5,
               infinite_step_estimates=estimates,E_model=e,D_hold=d,U_t=u,U_t_relative=u/v[-1],
               leave_one_out_even_diagnostics=loo,
               rule='same-sign contracting B1/B2/B3 increments; pair<=0.001; 2*max(E_model,D_hold)/B3<=0.001',
               p_range_is_veto=False,coarsest_LOO_residual_is_veto=False)
    return out


def _strict_result(raw,cfg):
    if canonical(raw.get('config'))!=canonical(enriched(cfg)):
        raise ValueError('typed exact config/source family mismatch')
    for key in ('dt_actual','v_au','nstep'):number(raw.get(key),key,positive=True)
    if type(raw['nstep']) is not int:raise ValueError('integer nstep required')
    audit=raw['analysis']['gram_audit']
    expected_qns=[list(q) for q in bound_quantum_numbers(cfg['project_nmax'])]
    if canonical(audit.get('quantum_numbers'))!=canonical(expected_qns) or type(audit.get('project_nmax')) is not int:
        raise ValueError('typed projector channel identity mismatch')
    for key in ('Gram_condition','wavefunction_norm','P_region','P_span_nmax'):
        number(audit[key],key,positive=key!='P_region')
    for key in ('Gram_eigenvalues','finite_grid_state_norms'):
        for val in audit[key]:number(val,key,positive=True)
    _probabilities([audit['P_span_by_nmax'][str(i)] for i in (1,2,3)],3)
    row=validate_result(raw,cfg)
    if audit['P_span_nmax']!=row['P3']:
        raise ValueError('selected-span readouts disagree')
    if audit.get('physical_all_bound_admitted') is not False or audit.get('continuum_probability') is not None:
        raise ValueError('finite-span observable semantics mismatch')
    return row


def _strict_witness(witness,cfg,raw,canonical_initial):
    for key in ('array_digest_match','norm_match','environment_match','numerical_state_substituted','numerical_state_renormalized'):
        if type(witness.get(key)) is not bool:raise ValueError('witness Boolean field type mismatch: '+key)
    validate_witness(witness,cfg)
    if witness['prepared_array_digest']!=INITIAL_ARRAY:
        raise ValueError('canonical initial array digest mismatch')
    if canonical(raw['initial'])!=canonical(canonical_initial) or canonical(witness.get('initial_metadata'))!=canonical(canonical_initial):
        raise ValueError('canonical initial metadata mismatch')
    if witness.get('dtype')!='<c16' or canonical(witness.get('shape'))!=canonical([350,300,600]) or witness.get('backend')!='cupy':
        raise ValueError('initial array shape/dtype/backend mismatch')
    dv=number(witness.get('dv'),'witness dv',positive=True)
    if not math.isclose(dv,.2**3,rel_tol=2e-14):raise ValueError('witness grid weighting mismatch')
    norms=[number(witness.get(k),k,positive=True) for k in ('prepared_norm','internal_norm')]
    if not math.isclose(norms[0],norms[1],rel_tol=1e-12) or not math.isclose(norms[0],1.,abs_tol=1e-10):
        raise ValueError('witness normalization mismatch')
    if not isinstance(witness.get('prepared_receipt_sha256'),str) or not re.fullmatch('[0-9a-f]{64}',witness['prepared_receipt_sha256']):
        raise ValueError('prepared receipt digest missing')


def _pinned(pair):
    path,digest=pair
    if sha(ROOT/path)!=digest:raise ValueError('pinned historical bytes changed: '+path)
    return read_json(ROOT/path)


def load_baseline():
    if source_digest()!=SOURCE:raise ValueError('frozen numerical source changed')
    historic=historical_baseline()
    rows={k:historic[k] for k in ('B0','B1')}
    for cell in ('B0','B1'):
        path,digest,cfgpath=PINS[cell]
        _strict_result(read_json(ROOT/path),read_json(ROOT/cfgpath))
    cfg=read_json(ROOT/'configs/r3m16/B1.json')
    cfg2=dict(cfg,dt=.0125)
    raw=_pinned(B2_RESULT); witness=_pinned(B2_WITNESS)
    rows['B2']=dict(_strict_result(raw,cfg2),result_sha256=B2_RESULT[1])
    _strict_witness(witness,cfg2,raw,raw['initial'])
    summary=_pinned(R18_SUMMARY)
    if canonical(rows)!=canonical(summary['rows']):raise ValueError('raw baseline and R3M18 summary disagree')
    return rows,cfg,raw['initial']


def build_forecast_payload():
    rows,cfg,initial=load_baseline()
    cfg3=dict(cfg,dt=.00625)
    horizon=rows['B2']['actual_dt']*rows['B2']['nstep']
    n=math.ceil(horizon/cfg3['dt']); dt=horizon/n
    if n!=7172 or dt!=rows['B2']['actual_dt']/2:raise ValueError('unexpected B3 integer schedule')
    predictions={p:channel_forecasts([rows[k][p] for k in ('B0','B1','B2')],
                                   [rows[k]['actual_dt'] for k in ('B0','B1','B2')],dt) for p in CHANNELS}
    return {'schema':'BASS_CR_R3M26_FROZEN_FORECAST_PAYLOAD_V1','base_commit':BASE_COMMIT,
            'numerical_source_digest':SOURCE,'initial_state_file_sha256':INITIAL_SHA,
            'initial_array_digest':INITIAL_ARRAY,'initial_metadata':initial,'rows':rows,
            'B3':{'config':cfg3,'nstep':n,'actual_dt':dt,'requested_dt':.00625,
                  'preparation_contract':{'fresh_full_B3_config_receipt_required':True,
                    'helper':'scripts/r3m13_initial_state_pair.py',
                    'expected_initial_file_sha256':INITIAL_SHA,
                    'expected_array_digest':INITIAL_ARRAY,
                    'B2_receipt_relabel_or_reuse_allowed':False,
                    'prepared_receipt_must_differ_from':B2_PREPARED_RECEIPT}},
            'forecasts':predictions,'baseline_provenance':{
                'B0_result':list(PINS['B0'][:2]),'B1_result':list(PINS['B1'][:2]),
                'B2_result':list(B2_RESULT),'B2_witness':list(B2_WITNESS),'R18_summary':list(R18_SUMMARY)},
            'criterion':{'relative_target':TOLERANCE,'factor':2.,
                         'E_model':'max(abs(P_infinity_model-B3)) over four registered models',
                         'D_hold':'max(abs(B3-frozen_forecast)) over three preregistered forecasts',
                         'U_t':'2*max(E_model,D_hold)',
                         'fine_increment_rule':'same sign and strict contraction on B1/B2/B3 only',
                         'p_range':'1.5..2.5 diagnostic only','LOO':'all four even-degree-two residuals diagnostic only',
                         'interpretation':'PROSPECTIVE_ENGINEERING_EMPIRICAL_ESTIMATE_NOT_CERTIFIED_BOUND'}}


def freeze_forecast():
    payload=build_forecast_payload(); digest=payload_hash(payload)
    if digest!=EXPECTED_FORECAST_PAYLOAD_SHA256:raise ValueError('forecast payload differs from preregistered code pin')
    return {'schema':'BASS_CR_R3M26_FORECAST_V1','payload':payload,'payload_sha256':digest,
            'B3_execution_status':'NOT_RUN','production_admitted':False,'certified_error_bound':None,
            'forecast_generated_before_B3':True,'instrumentation_sha256':sha(Path(__file__)),
            'runtime':{'python':platform.python_version(),'numpy':np.__version__,'GPU_executed':False}}


def evaluate_result(result_path,witness_path,forecast_path):
    forecast=read_json(forecast_path)
    if (forecast.get('schema')!='BASS_CR_R3M26_FORECAST_V1' or
            forecast.get('payload_sha256')!=EXPECTED_FORECAST_PAYLOAD_SHA256 or
            payload_hash(forecast.get('payload'))!=EXPECTED_FORECAST_PAYLOAD_SHA256):
        raise ValueError('forecast does not match preregistered independent hash pin')
    payload=forecast['payload']
    rows,cfg,initial=load_baseline()
    if canonical(payload['rows'])!=canonical(rows):raise ValueError('forecast historical raw identities disagree')
    cfg3=dict(cfg,dt=.00625)
    if canonical(payload['B3']['config'])!=canonical(cfg3):raise ValueError('B3 forecast config mismatch')
    raw=read_json(result_path); witness=read_json(witness_path)
    row=_strict_result(raw,cfg3)
    _strict_witness(witness,cfg3,raw,initial)
    if witness['prepared_receipt_sha256']==B2_PREPARED_RECEIPT:
        raise ValueError('fresh B3 preparation receipt required; B2 receipt reuse forbidden')
    if row['nstep']!=payload['B3']['nstep'] or row['actual_dt']!=payload['B3']['actual_dt']:
        raise ValueError('B3 actual dt differs from frozen forecast schedule')
    channels={p:channel_gate([rows[k][p] for k in ('B0','B1','B2')]+[row[p]],
                             [rows[k]['actual_dt'] for k in ('B0','B1','B2')]+[row['actual_dt']],
                             payload['forecasts'][p]) for p in CHANNELS}
    accepted=all(ch['accepted'] for ch in channels.values())
    return {'schema':'BASS_CR_R3M26_TEMPORAL_EVALUATION_V1',
            'status':ACCEPTED if accepted else 'TEMPORAL_ESTIMATE_NOT_VALIDATED',
            'claim_scope':'FIXED_H_SELECTED_P1_P2_P3_EMPIRICAL_TEMPORAL_ESTIMATE_ONLY',
            'channels':channels,'raw_B3_row':row,'certified_error_bound':None,
            'production_admitted':False,'total_error_budget_closed':False,
            'representation_change_admitted':False,
            'identity_basis':'PINNED_HISTORICAL_RAW_RESULTS_PLUS_SUBMITTED_B3_RAW_RESULT_AND_V2_WITNESS',
            'array_restore_or_checkpoint_rehash_performed':False,
            'input_files':{key:{'path':str(path),'sha256':sha(path)} for key,path in
                           (('result',result_path),('witness',witness_path),('forecast',forecast_path))},
            'forecast_payload_sha256':EXPECTED_FORECAST_PAYLOAD_SHA256,
            'numerical_source_digest':source_digest(),'instrumentation_sha256':sha(Path(__file__))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    first=sub.add_parser('forecast'); first.add_argument('--out',required=True,type=Path)
    second=sub.add_parser('evaluate')
    for flag in ('result','witness','forecast','out'):second.add_argument('--'+flag,required=True,type=Path)
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    result=freeze_forecast() if args.command=='forecast' else evaluate_result(args.result,args.witness,args.forecast)
    write_new(args.out,result)
    print(json.dumps({'output':str(args.out),'status':result.get('status','FORECAST_ONLY_B3_NOT_RUN'),
                      'production_admitted':False}))


if __name__=='__main__':main()
