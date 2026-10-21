"""Retrospective REC116 axis-response diagnostic on completed C21M data.

No ODE, fitting, benchmark, solver replacement, or production-surrogate gate.
Only 15 axis-support trajectories enter prediction. The 12 mixed trajectories
are used solely to evaluate held-out residuals at all 101 stored times.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext
import itertools
import json
import math
from pathlib import Path

import numpy as np

import analyze_pilot as pilot

HERE=Path(__file__).resolve().parent
CHANNELS=('S_signed_F','P_m_signed_F','P_r_signed_F','P_tot_signed_F')
REC_SOURCE_SHA256='453eee672e2a6d78bf0f76aa42f5453e68c1066cc561f5fe547be9e30e01e457'


def predict(support,key):
    """Adapt REC116 predict/math.fsum to trajectories; no mixed values accepted."""
    s,m,r=key
    am,ar,anchor=(support[k] for k in ((s,m,0.),(s,0.,r),(s,0.,0.)))
    return np.array([[math.fsum((float(am[t,c]),float(ar[t,c]),-float(anchor[t,c])))
                      for c in range(len(CHANNELS))] for t in range(101)])


def stored_float_interaction(actual,am,ar,anchor):
    """REC116 exact_residual adapted to arrays; 80-digit stored-float algebra."""
    result=np.empty_like(actual)
    with localcontext() as context:
        context.prec=80
        for index in np.ndindex(actual.shape):
            a,m,r,z=(Decimal.from_float(float(v[index])) for v in (actual,am,ar,anchor))
            result[index]=float(a-m-r+z)
    return result


def ratio(value,scale):
    return float(value/scale) if scale!=0 else None


def analyze(analysis,run,output,reference):
    analysis,run,output=map(lambda p:Path(p).resolve(),(analysis,run,output))
    if output.exists():
        raise FileExistsError('CREATE_ONLY_OUTPUT_EXISTS')
    rec_source=HERE/'external_evidence/rec_source.py'
    if pilot.sha(rec_source)!=REC_SOURCE_SHA256:
        raise ValueError('ADOPTED_EXTERNAL_METHOD_SOURCE_CHANGED')
    output_manifest=json.loads((analysis/'OUTPUT_MANIFEST.json').read_text())
    for name,item in output_manifest['files'].items():
        if pilot.sha(analysis/name)!=item['sha256']:
            raise ValueError('ANALYSIS_INPUT_CHANGED:'+name)
    sources=json.loads((analysis/'INPUT_SOURCES.json').read_text())
    run_payload=json.loads((run/'MANIFEST.json').read_text())
    grid=run_payload['manifest']['grid']
    manifest_path,run_manifest,entries=pilot.load_new(run,grid)
    if (pilot.sha(manifest_path)!=sources['run_manifest_sha256']
            or run_manifest['identity']!=sources['run_identity']):
        raise ValueError('ANALYSIS_RUN_IDENTITY_MISMATCH')
    ref,entry=pilot.load_reference(reference,pilot.C21L)
    if pilot.sha(reference)!=sources['reference_reuse_sha256']:
        raise ValueError('ANALYSIS_REFERENCE_IDENTITY_MISMATCH')
    entries.append(entry)
    with np.load(analysis/'components27.npz',allow_pickle=False) as archive:
        saved={k:archive[k] for k in archive.files}
    lookup={str(cid):i for i,cid in enumerate(saved['case_id'])}
    source_by_id={item['case_id']:item for item in sources['source_trajectories']}
    table={}; raw_bindings=[]; before={}
    module=pilot.decomposition()
    for case,path,receipt_path,receipt,origin in entries:
        before[path]=pilot.sha(path); before[receipt_path]=pilot.sha(receipt_path)
        binding=source_by_id[case['case_id']]
        if before[path]!=binding['history_sha256'] or before[receipt_path]!=binding['receipt_sha256']:
            raise ValueError('ANALYSIS_SOURCE_BINDING_CHANGED')
        with np.load(path,allow_pickle=False) as raw:
            values=module.components(raw)
        index=lookup[case['case_id']]
        if any(not np.array_equal(values[channel],saved[channel][index]) for channel in CHANNELS):
            raise ValueError('SAVED_DIAGNOSTIC_DIFFERS_FROM_RAW_COMPONENTS')
        key=tuple(case[k] for k in ('S0','Pm0','Pr0'))
        if key in table:
            raise ValueError('DUPLICATE_PHYSICAL_COORDINATE')
        table[key]={'case_id':case['case_id'],'index':index,
                    'values':np.stack([values[k] for k in CHANNELS],axis=-1)}
        raw_bindings.append(binding)
    expected=set(itertools.product(pilot.SLICES,pilot.STRESSES,pilot.STRESSES))
    if set(table)!=expected or len(table)!=27:
        raise ValueError('EXPECTED_COMPLETE27_GRID')
    support={key:record['values'].copy() for key,record in table.items() if key[1]==0. or key[2]==0.}
    held=sorted(key for key in table if key[1]!=0. and key[2]!=0.)
    if len(support)!=15 or len(held)!=12:
        raise ValueError('AXIS_SUPPORT15_HELD_OUT12_REQUIRED')
    actual=np.stack([table[key]['values'] for key in held])
    predicted=np.stack([predict(support,key) for key in held])
    error=actual-predicted
    exact_interaction=np.stack([stored_float_interaction(table[key]['values'],support[key[0],key[1],0.],
                             support[key[0],0.,key[2]],support[key[0],0.,0.]) for key in held])
    support_scale=np.max(abs(np.stack(list(support.values()))),axis=(0,1))
    endpoint_scale=np.max(abs(np.stack(list(support.values()))[:,-1,:]),axis=0)
    increments=np.stack([value-support[key[0],0.,0.] for key,value in support.items()])
    increment_scale=np.max(abs(increments),axis=(0,1))
    endpoint_increment_scale=np.max(abs(increments[:,-1,:]),axis=0)
    relative_defined=actual!=0
    pointwise_relative=np.full_like(error,np.nan)
    pointwise_relative[relative_defined]=error[relative_defined]/abs(actual[relative_defined])
    scaled_error=np.full_like(error,np.nan)
    for c,scale in enumerate(support_scale):
        if scale!=0:
            scaled_error[:,:,c]=error[:,:,c]/scale
    closure=predicted[:,:,3]-predicted[:,:,1]-predicted[:,:,2]
    records=[]
    for n,key in enumerate(held):
        for t in range(101):
            record={'case_id':table[key]['case_id'],'S0':key[0],'Pm0':key[1],'Pr0':key[2],
                    'saved_index':t,'eta':float(saved['eta'][table[key]['index'],t]),
                    'redshift':float(1/saved['a'][table[key]['index'],t]-1)}
            for c,channel in enumerate(CHANNELS):
                record.update({channel+'_actual':float(actual[n,t,c]),channel+'_axis_prediction':float(predicted[n,t,c]),
                               channel+'_residual_actual_minus_prediction':float(error[n,t,c]),
                               channel+'_stored_float_interaction':float(exact_interaction[n,t,c]),
                               channel+'_pointwise_relative_defined':bool(relative_defined[n,t,c]),
                               channel+'_pointwise_relative':float(pointwise_relative[n,t,c]) if relative_defined[n,t,c] else None,
                               channel+'_support_scale_normalized_error':ratio(error[n,t,c],support_scale[c])})
            records.append(record)
    observables={}
    for c,channel in enumerate(CHANNELS):
        where=np.unravel_index(int(np.argmax(abs(error[:,:,c]))),error[:,:,c].shape)
        endpoint_max=float(np.max(abs(error[:,-1,c])))
        max_abs=float(np.max(abs(error[:,:,c])))
        defined=relative_defined[:,:,c]
        observables[channel]={
            'all_saved_max_abs_error':max_abs,'endpoint_max_abs_error':endpoint_max,
            'all_saved_rms_error':float(np.sqrt(np.mean(error[:,:,c]**2))),
            'endpoint_rms_error':float(np.sqrt(np.mean(error[:,-1,c]**2))),
            'all_saved_support_abs_scale':float(support_scale[c]),
            'endpoint_support_abs_scale':float(endpoint_scale[c]),
            'all_saved_max_error_over_support_scale':ratio(max_abs,support_scale[c]),
            'endpoint_max_error_over_support_scale':ratio(endpoint_max,endpoint_scale[c]),
            'all_saved_axis_increment_abs_scale':float(increment_scale[c]),
            'endpoint_axis_increment_abs_scale':float(endpoint_increment_scale[c]),
            'all_saved_max_error_over_axis_increment_scale':ratio(max_abs,increment_scale[c]),
            'endpoint_max_error_over_axis_increment_scale':ratio(endpoint_max,endpoint_increment_scale[c]),
            'all_saved_exact_stored_float_interaction_max_abs':float(np.max(abs(exact_interaction[:,:,c]))),
            'endpoint_exact_stored_float_interaction_max_abs':float(np.max(abs(exact_interaction[:,-1,c]))),
            'max_rounding_difference_error_vs_80digit_interaction':float(np.max(abs(error[:,:,c]-exact_interaction[:,:,c]))),
            'pointwise_relative_undefined_exact_zero_count':int(np.count_nonzero(~defined)),
            'pointwise_relative_max_abs_where_exact_actual_nonzero':float(np.max(abs(pointwise_relative[:,:,c][defined]))) if np.any(defined) else None,
            'all_saved_max_error_case_id':table[held[where[0]]]['case_id'],
            'all_saved_max_error_saved_index':int(where[1])}
    summary={
        'status':'RETROSPECTIVE_STORED_GRID_DIAGNOSTIC_COMPLETE',
        'formula':'Fhat(S,m,r)=F(S,m,0)+F(S,0,r)-F(S,0,0)',
        'coordinates':'signed full Frobenius S, Pm, Pr, Ptot; norms are not added',
        'existing_cases':27,'original_new_C21M_execution':26,'reused_C21L_reference':1,
        'support_cases':15,'held_out_mixed_cases':12,'saved_times_per_case':101,
        'new_ODE_runs':0,'benchmark_runs':0,'fitted_coefficients':0,
        'production_surrogate_approved':False,'measured_speedup':None,'global_error_bound':None,
        'external_method':{'repo':'https://github.com/cosmosapjw-quantum/rec_bianchi','PR':116,
                           'reviewed_head':'d2c0fbb5fa06dfc37db57876bb130ef8a4fa8a5d',
                           'fetched_source_sha256':REC_SOURCE_SHA256,
                           'reuse':'REC116 predict uses math.fsum and exact_residual uses 80-digit Decimal stored-float arithmetic; adapted to 101-time arrays.',
                           'local_scope_difference':'C21M collisionless z20->4, full Frobenius, full40-state27; external729 warm a=.1999->.2 results are not imported as local accuracy evidence.'},
        'scale_policy':'Support abs scale=max(abs(F)) over 15 support cases; axis-increment scale=max(abs(F_axis-F_anchor)). Separate all-times and endpoint scales. Exact-zero denominators yield null/NaN with explicit defined mask; no floor, clipping, or point removal.',
        'pointwise_relative_caution':'Raw relative errors retain every nonzero actual value, including arbitrarily small values near cancellation; exact-zero actual values are marked undefined. Absolute residuals at those points remain stored.',
        'prediction_total_policy':'Ptot uses the same axis formula independently; component-sum prediction and its floating-point closure difference are also retained.',
        'max_predicted_total_minus_predicted_component_sum_abs':float(np.max(abs(closure))),
        'reference_offset_policy':ref['offset_policy'],
        'actual_reference_initial_offsets':ref['actual_initial_signed_full_Frobenius'],
        'observables':observables,
        'limits':['Retrospective comparison on this finite stored grid only','Mixed trajectories were already computed and are used solely for validation, not fitting or support construction','No continuum, unsaved-time, other-amplitude, other-source or larger-grid error bound','No solver substitution or new performance claim','Matter/radiation remain gravitationally coupled despite near-additive responses']}
    output.mkdir(parents=True,exist_ok=False)
    arrays={'case_id':np.array([table[key]['case_id'] for key in held]),'channels':np.array(CHANNELS),
            'requested_signed_full':np.array(held),'actual':actual,'axis_prediction':predicted,
            'residual_actual_minus_prediction':error,'stored_float_interaction_80digit':exact_interaction,
            'pointwise_relative_error':pointwise_relative,'pointwise_relative_defined':relative_defined,
            'support_scale_normalized_error':scaled_error,'support_abs_scale':support_scale,
            'endpoint_support_abs_scale':endpoint_scale,'axis_increment_abs_scale':increment_scale,
            'predicted_total_from_component_sum':predicted[:,:,1]+predicted[:,:,2],
            'predicted_total_closure_residual':closure,
            'eta':np.stack([saved['eta'][table[key]['index']] for key in held]),
            'a':np.stack([saved['a'][table[key]['index']] for key in held]),
            'support_case_id':np.array([table[key]['case_id'] for key in sorted(support)]),
            'support_values':np.stack([support[key] for key in sorted(support)])}
    module.deterministic_npz(output/'axis_response_residuals.npz',arrays)
    for name,subset in [('heldout_trajectories.csv',records),('heldout_endpoints.csv',[r for r in records if r['saved_index']==100])]:
        with (output/name).open('x',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(records[0]));writer.writeheader();writer.writerows(subset)
    pilot.write(output/'SUMMARY.json',summary)
    pilot.write(output/'INPUT_BINDINGS.json',{'source_code_sha256':pilot.sha(Path(__file__)),
                'analysis_sha256':{name:pilot.sha(analysis/name) for name in ('components27.npz','INPUT_SOURCES.json','OUTPUT_MANIFEST.json')},
                'run_identity':run_manifest['identity'],'run_manifest_sha256':pilot.sha(manifest_path),
                'reference_reuse_sha256':pilot.sha(reference),'raw_bindings':raw_bindings,
                'support_case_ids':[table[key]['case_id'] for key in sorted(support)],
                'held_out_case_ids':[table[key]['case_id'] for key in held],
                'original_raw_and_receipts_unchanged':all(pilot.sha(path)==digest for path,digest in before.items()),
                'new_ODE_runs':0,'global_error_bound':None})
    if not all(pilot.sha(path)==digest for path,digest in before.items()):
        raise ValueError('ORIGINAL_INPUTS_CHANGED_DURING_READONLY_ANALYSIS')
    pilot.write(output/'OUTPUT_MANIFEST.json',{'files':{p.name:{'sha256':pilot.sha(p),'size':p.stat().st_size} for p in sorted(output.iterdir())},'global_error_bound':None})
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis',type=Path,default=HERE/'analysis_pilot27')
    parser.add_argument('--run',type=Path,default=HERE/'runs/pilot26')
    parser.add_argument('--reference',type=Path,default=HERE/'REFERENCE_REUSE.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(analyze(args.analysis,args.run,args.output,args.reference),indent=2))
