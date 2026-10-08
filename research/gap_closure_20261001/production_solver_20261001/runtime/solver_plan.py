"""Exact legacy midpoint query plan, bound to an explicit numerical context."""
import copy
import hashlib
import json
import math
import re
import bootstrap_runtime
from parallel_bridge import query_id

METHOD='LEGACY_TP1_CHOLESKY_MIDPOINT_EXPM_V1'
CEILINGS={'capture_execution_allowed':False,'production_admission':'HOLD','all_bound':'OPEN',
          'b_grid':'NO_GO','original_capture_gap_resolved':False,
          'continuous_global_supremum_bound':False,'continuous_trajectory_error_bound':False}

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def make_plan(t0,tf,nstep,context_id,*,qualification_contract,selected_indices):
    t0=float(t0);tf=float(tf)
    if not math.isfinite(t0) or not math.isfinite(tf) or not tf>t0 or type(nstep) is not int or nstep<1:
        raise ValueError('finite increasing window and positive integer nstep required')
    if not isinstance(context_id,str) or not re.fullmatch('[0-9a-f]{64}',context_id):
        raise ValueError('exact 64-hex numerical context identity required')
    if (not isinstance(selected_indices,list) or not selected_indices or len(set(selected_indices))!=len(selected_indices)
        or any(type(x) is not int or not 0<=x<18 for x in selected_indices)):
        raise ValueError('explicit unique selected indices in the 18-channel model required')
    contract=copy.deepcopy(qualification_contract)
    ladder=contract.get('runtime_reference_resolutions');screens=contract.get('screens',{})
    if (not isinstance(ladder,list) or len(ladder)<2 or any(set(r)!={'order','subdivisions'}
        or type(r['order']) is not int or not 2<=r['order']<=64 or type(r['subdivisions']) is not int
        or r['subdivisions'] not in (1,2,4) for r in ladder)
        or len({(r['order'],r['subdivisions']) for r in ladder})!=len(ladder)):
        raise ValueError('explicit ordered qualification ladder required')
    for key in ('raw_cross_relative_max','operator_hermiticity_relative_max','metric_min_ratio','candidate_norm_drift_max'):
        value=screens.get(key)
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:
            raise ValueError('positive explicit screen required: '+key)
    dt=(tf-t0)/nstep
    if not math.isfinite(dt) or dt<=0:raise ValueError('finite positive step width required')
    queries=[];steps=[]
    def entry(t,role,step=None):
        th=float(t).hex()
        return {'query_id':query_id(context_id,th),'time_hex':th,'role':role,'step':step}
    queries.append(entry(t0,'initial'))
    for j in range(nstep):
        # These are the exact operations in metric_transport.run_candidate.
        ta=t0+j*dt;tb=ta+dt;tm=.5*(ta+tb)
        if not tb>ta:raise ValueError('step collapsed under floating-point representation')
        item=entry(tm,'midpoint',j);queries.append(item)
        steps.append({'index':j,'ta_hex':ta.hex(),'tb_hex':tb.hex(),'midpoint_hex':tm.hex(),'query_id':item['query_id']})
    queries.append(entry(tf,'final'))
    if len({q['query_id'] for q in queries})!=nstep+2:raise ValueError('distinct endpoint/midpoint identities required')
    plan={'schema':'BASS_PRODUCTION_CANDIDATE_QUERY_PLAN_V1','method':METHOD,'context_id':context_id,
          'channel_count':18,'t0_hex':t0.hex(),'tf_hex':tf.hex(),'nstep':nstep,'dt_hex':dt.hex(),
          'selected_indices':selected_indices.copy(),'qualification_contract':contract,
          'queries':queries,'steps':steps,'operator_interpolation_used':False,**CEILINGS}
    plan['plan_sha256']=digest(plan)
    return plan

def validate_plan(plan):
    rebuilt=make_plan(float.fromhex(plan['t0_hex']),float.fromhex(plan['tf_hex']),plan['nstep'],plan['context_id'],
                      qualification_contract=plan['qualification_contract'],selected_indices=plan['selected_indices'])
    if plan!=rebuilt:raise ValueError('plan identity/content/legacy-grid mismatch')
    return plan
