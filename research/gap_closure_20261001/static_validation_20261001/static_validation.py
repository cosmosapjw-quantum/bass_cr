"""Offline FD/qualification audit. No physical/native evaluation entry point.

Stored provider JSON+NPZ are admitted only through an explicit identity binding.
Binding sidecars are provenance assertions to be signed off by the execution
reviewer; this module verifies their consistency and exact source/payload bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SOURCE_DIR=REPO/'research/foundation_rebuild/ncp_shared_research_20260928/r4p0a_b0_static_tail_executor_20260930'
CENTERS=(-32.,-24.,-16.,-12.,12.,16.,24.,32.)
H_LADDER=(.4,.2,.1,.05)
UNITS={'z':'a0','time':'atomic_time','S':'dimensionless','D':'atomic_time^-1','velocity':'a0/atomic_time'}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def query_id(context,time_hex):
    obj={'schema':'BASS_TP2D_RUNTIME_QUERY_V1','context_id':context,'time_hex':time_hex}
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def load_source_plan():return json.loads((SOURCE_DIR/'BOUND_B0_TAIL_QUERY_PLAN.json').read_text())


def make_plan(source,verified_reuse=None):
    ctx=source['context']; frozen=ctx['frozen_physics_identity']
    identity={k:frozen[k] for k in ('basis_identity','analytic_source_sha256','analytic_library_sha256','same_center_order','qualification_sector','source_manifest_sha256','dependency_pins_sha256')}
    identity.update({k:ctx[k] for k in ('energy_keV_per_u','b_a0','velocity_au','radial_spec','native_backend')})
    identity['channel_count']=18
    points=sorted(set(CENTERS)|{float(z+s*h) for z in CENTERS for h in H_LADDER for s in (-1,1)})
    reuse=verified_reuse or {}
    allowed={float(z).hex() for z in points}
    if set(reuse)-allowed:raise ValueError('reuse outside FD plan')
    queries=[]
    for z in points:
        zh=float(z).hex()
        queries.append({'z_a0':z,'z_hex':zh,'time_hex':float(z/identity['velocity_au']).hex(),
            'role':'center_D' if z in CENTERS else 'shifted_S',
            'action':'VERIFIED_REUSE' if zh in reuse else 'NEW_QUALIFIED_QUERY',
            'reuse_evidence':reuse[zh]['evidence'] if zh in reuse else None})
    ladder=ctx['qualification_ladder'];new=len(points)-len(reuse)
    fd_context=hashlib.sha256(json.dumps({'schema':'BASS_G02_FD_CONTEXT_V1','identity':identity,
        'points':points,'ladder':ladder,'screens':ctx['active_screens']},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'schema':'BASS_G02_FD_PLAN_V1','identity':identity,'units':UNITS,'context_id':fd_context,
       'admitted_source_context_ids':[source['context_id'],ctx['parent_transport_context_id'],fd_context],
       'source_plan_sha256':hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
       'source_plan_parent_context':source['context_id'],'qualification_ladder':ladder,
       'active_screens':ctx['active_screens'],'centers':list(CENTERS),'h_ladder':list(H_LADDER),
       'queries':queries,'total_required_snapshots':len(points),'verified_reuse_count':len(reuse),
       'new_query_count':new,'max_raw_operator_evaluations':new*len(ladder),
       'native_authorized':False,'fresh_authorization_required':True,'old_A1_consumable':False,
       'temporal_gate_inherited':False,'rho_expansion_included':False,
       'acceptance':{'relative_target':1e-6,'absolute_target_atomic_time_inverse':1e-12,
          'order_window':[1.5,2.5],'minimum_consecutive_order_intervals':2,
          'scope':'DERIVATIVE_IMPLEMENTATION_DIAGNOSTIC_NOT_CERTIFIED_OPERATOR_ERROR'},
       'stop_rule':'Any identity/qualification/budget/resource failure stops; no retry, tolerance relaxation or grid expansion without new contract.',
       'new_native_calls_in_preparation':0}


def _inside(root,path):
    root=Path(root).resolve();p=(root/path).resolve()
    if not p.is_relative_to(root):raise ValueError('file escapes manifest directory')
    return p


def load_saved(root,desc,plan):
    if desc.get('identity')!=plan['identity'] or desc.get('units')!=UNITS:
        raise ValueError('source/basis/physics identity or unit mismatch')
    z=float(desc['z_a0']);zh=z.hex();th=float(z/plan['identity']['velocity_au']).hex()
    if desc.get('z_hex')!=zh or desc.get('time_hex')!=th:raise ValueError('z/time identity mismatch')
    if zh not in {q['z_hex'] for q in plan['queries']}:raise ValueError('snapshot outside plan')
    jp=_inside(root,desc['record']);payload=_inside(root,desc['payload'])
    if sha(jp)!=desc.get('record_sha256'):raise ValueError('record hash mismatch')
    rec=json.loads(jp.read_text())
    if rec.get('context_id') not in plan['admitted_source_context_ids']:
        raise ValueError('provider context is not an admitted source context')
    if (rec.get('schema')!='BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1' or rec.get('time_hex')!=th
        or rec.get('query_id')!=query_id(rec.get('context_id'),th)):
        raise ValueError('original provider record identity mismatch')
    if sha(payload)!=rec.get('payload_sha256'):raise ValueError('payload hash mismatch')
    qual=rec.get('qualification',{});diag=rec.get('selected_diagnostics',{});screens=plan['active_screens']
    pair=(qual.get('lower_resolution'),qual.get('selected_resolution'))
    if pair not in list(zip(plan['qualification_ladder'][:-1],plan['qualification_ladder'][1:])):
        raise ValueError('qualification is not an allowed adjacent pair')
    if qual.get('status')!='RUNTIME_QUERY_QUALIFIED':raise ValueError('snapshot not qualified')
    values=np.array([qual.get('max_raw_cross_relative_difference',np.inf),
        diag.get('S_hermiticity_relative',np.inf),diag.get('H_hermiticity_relative',np.inf),
        diag.get('metric_ratio',-np.inf)],float)
    if (not np.isfinite(values).all() or min(values)<0 or values[0]>screens['raw_cross_relative_max']
        or max(values[1:3])>screens['operator_hermiticity_relative_max'] or values[3]<screens['metric_min_ratio']):
        raise ValueError('qualification screens not satisfied')
    with np.load(payload,allow_pickle=False) as data:
        S=np.array(data['selected__S'],complex);D=np.array(data['selected__D'],complex)
    n=plan['identity']['channel_count']
    if S.shape!=(n,n) or D.shape!=(n,n) or not all(np.isfinite(a).all() for a in (S,D)):
        raise ValueError('matrix shape/finiteness mismatch')
    if np.linalg.norm(S-S.conj().T)/max(np.linalg.norm(S),1e-300)>screens['operator_hermiticity_relative_max']:
        raise ValueError('saved S is non-Hermitian')
    ev=np.linalg.eigvalsh(S)
    if ev[-1]<=0 or ev[0]/ev[-1]<screens['metric_min_ratio']:raise ValueError('saved metric inadmissible')
    return {'S':S,'D':D,'z_a0':z,'evidence':{'record_sha256':sha(jp),'payload_sha256':sha(payload),
       'query_id':rec['query_id'],'original_context_id':rec['context_id'],'identity_binding':desc}}


def verify_manifest(root,manifest,plan):
    if manifest.get('identity')!=plan['identity']:raise ValueError('manifest identity mismatch')
    out={}
    for desc in manifest['snapshots']:
        row=load_saved(root,desc,plan);key=float(row['z_a0']).hex()
        if key in out:raise ValueError('duplicate snapshot coordinate')
        out[key]=row
    return out


def _norm(a,order=2):return float(np.linalg.norm(a,ord=order))


def compare_ladder(D,ladder,velocity,relative_target=1e-6,absolute_target=1e-12):
    if not np.isfinite(velocity) or velocity<=0:raise ValueError('positive finite velocity required')
    if not np.isfinite([relative_target,absolute_target]).all() or min(relative_target,absolute_target)<=0:
        raise ValueError('positive finite acceptance thresholds required')
    if len(ladder)<4:raise ValueError('at least four shrinking h values required')
    hs=np.array([x[0] for x in ladder],float)
    if not np.isfinite(hs).all() or np.any(hs<=0) or np.any(np.diff(hs)>=0):raise ValueError('strictly shrinking positive h ladder required')
    D=np.asarray(D,complex)
    if D.ndim!=2 or D.shape[0]!=D.shape[1] or not np.isfinite(D).all():raise ValueError('square finite D required')
    direct=D+D.conj().T;rows=[]
    for h,minus,plus in ladder:
        minus=np.asarray(minus,complex);plus=np.asarray(plus,complex)
        if minus.shape!=D.shape or plus.shape!=D.shape or not all(np.isfinite(x).all() for x in (minus,plus)):
            raise ValueError('S shape/finiteness mismatch')
        fd=velocity*(plus-minus)/(2*h);error=fd-direct
        scale2=max(_norm(fd),_norm(direct),1e-300)
        scalef=max(_norm(fd,'fro'),_norm(direct,'fro'),1e-300)
        # A scale-dependent floor prevents zero derivative entries from dominating
        # through division by numerical zero; absolute error is reported separately.
        component_floor=max(absolute_target,np.finfo(float).eps*scale2)
        denominator=np.maximum(np.maximum(abs(fd),abs(direct)),component_floor)
        rows.append({'h_a0':float(h),'spectral_absolute':_norm(error),
           'spectral_relative':_norm(error)/scale2,'frobenius_absolute':_norm(error,'fro'),
           'frobenius_relative':_norm(error,'fro')/scalef,
           'elementwise_max_absolute':float(np.max(abs(error))),
           'elementwise_max_normalized':float(np.max(abs(error)/denominator)),
           'elementwise_denominator_floor':component_floor,'derivative_scale':scale2})
    errors=[r['spectral_absolute'] for r in rows]
    orders=[float(np.log(a/b)/np.log(ha/hb)) if a>0 and b>0 else None
              for a,b,ha,hb in zip(errors[:-1],errors[1:],hs[:-1],hs[1:])]
    good=[p is not None and 1.5<=p<=2.5 for p in orders]
    visible=any(a and b for a,b in zip(good[:-1],good[1:]))
    last=rows[-1]
    norm_pass=(last['spectral_absolute']<=absolute_target or last['spectral_relative']<=relative_target)
    frob_pass=(last['frobenius_absolute']<=absolute_target or last['frobenius_relative']<=relative_target)
    elem_pass=(last['elementwise_max_absolute']<=absolute_target or last['elementwise_max_normalized']<=relative_target)
    passed=bool(visible and norm_pass and frob_pass and elem_pass)
    return {'status':'FD_DIAGNOSTIC_PASS' if passed else ('ORDER_NOT_RESOLVED' if not visible else 'RESIDUAL_TARGET_NOT_MET'),
        'passed':passed,'rows':rows,'observed_orders':orders,'visible_second_order':visible,
        'relative_target':relative_target,'absolute_target_atomic_time_inverse':absolute_target,
        'rigorous_operator_error_bound':False,'native_calls':0}


def analyze(manifest,root,plan):
    samples=verify_manifest(root,manifest,plan)
    missing=[q['z_a0'] for q in plan['queries'] if q['z_hex'] not in samples]
    if missing:return {'status':'BLOCKED_RUNTIME_ENVIRONMENT_BLOCKER','missing_z_a0':missing,'physical_G02_closed':False,'native_calls':0}
    out=[]
    for z in plan['centers']:
        center=samples[float(z).hex()]
        ladder=[(h,samples[float(z-h).hex()]['S'],samples[float(z+h).hex()]['S']) for h in plan['h_ladder']]
        out.append({'z_a0':z,**compare_ladder(center['D'],ladder,plan['identity']['velocity_au'],
             plan['acceptance']['relative_target'],plan['acceptance']['absolute_target_atomic_time_inverse'])})
    return {'status':'ALL_FD_DIAGNOSTICS_PASS' if all(x['passed'] for x in out) else 'FD_VALIDATION_UNRESOLVED',
       'results':out,'native_calls':0,'physical_G02_closed':False,
       'closure_requires':'Independent review of actual source/payload identity bindings and the returned physical FD evidence; diagnostic pass alone does not certify operator error.'}


def three_level(values,resolutions=None,adjacent_tolerance=1e-9):
    if len(values)!=3 or adjacent_tolerance<=0:raise ValueError('three values and positive tolerance required')
    a,b,c=[np.asarray(x) for x in values]
    if a.shape!=b.shape or b.shape!=c.shape or not all(np.isfinite(x).all() for x in (a,b,c)):raise ValueError('compatible finite values required')
    d1=b-a;d2=c-b;n1=float(np.linalg.norm(d1));n2=float(np.linalg.norm(d2));scale=max(*(float(np.linalg.norm(x)) for x in (a,b,c)),1e-300)
    floor=16*np.finfo(float).eps*scale
    alignment=float(np.real(np.vdot(d1,d2))/(n1*n2)) if n1>floor and n2>floor else None
    ratio=n2/n1 if n1>floor else None
    order=None;rich=False
    if resolutions is not None:
        h=np.asarray(resolutions,float)
        if h.shape!=(3,) or np.any(h<=0) or not np.isfinite(h).all() or np.any(np.diff(h)>=0):raise ValueError('decreasing finite resolutions required')
        r1=h[0]/h[1];r2=h[1]/h[2]
        if np.isclose(r1,r2,rtol=1e-12) and ratio is not None and ratio>0:
            order=float(-np.log(ratio)/np.log(r1));rich=bool(0<ratio<1 and alignment is not None and alignment>.99)
    plateau=n1<=floor or n2<=floor
    consistency=bool(n1/scale<=adjacent_tolerance and n2/scale<=adjacent_tolerance)
    return {'status':'PLATEAU_OR_EXACTNESS_UNRESOLVED' if plateau else ('THREE_LEVEL_INTERNAL_CONSISTENCY' if consistency else 'THREE_LEVEL_DISAGREEMENT'),
      'difference_norms':[n1,n2],'relative_differences':[n1/scale,n2/scale],'difference_alignment':alignment,
      'contraction_ratio':ratio,'observed_order':order,'conditional_richardson_compatible':rich,
      'three_level_consistency':consistency,'rigorous_error_bound':False,
      'changes_existing_qualification':False,'adjacent_tolerance':adjacent_tolerance,
      'conditional_fine_error_estimate':n2*ratio/(1-ratio) if rich else None}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='mode',required=True)
    a=sub.add_parser('plan');a.add_argument('--source-plan',type=Path,default=SOURCE_DIR/'BOUND_B0_TAIL_QUERY_PLAN.json');a.add_argument('--reuse-manifest',type=Path);a.add_argument('--output',type=Path,required=True)
    a=sub.add_parser('analyze');a.add_argument('--contract',type=Path,required=True);a.add_argument('--manifest',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.mode=='plan':
        source=json.loads(args.source_plan.read_text());out=make_plan(source)
        if args.reuse_manifest:
            manifest=json.loads(args.reuse_manifest.read_text());reuse=verify_manifest(args.reuse_manifest.parent,manifest,out);out=make_plan(source,reuse)
    else:out=analyze(json.loads(args.manifest.read_text()),args.manifest.parent,json.loads(args.contract.read_text()))
    with args.output.open('x') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')


if __name__=='__main__':main()
