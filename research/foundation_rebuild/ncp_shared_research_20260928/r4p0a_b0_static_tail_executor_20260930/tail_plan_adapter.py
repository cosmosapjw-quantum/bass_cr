"""Exact B0-only tail-plan binding and stored-operator diagnostics.

No native library is imported, no evaluator is invoked, and no authorization is
consumed. The runtime IDs follow the frozen qualified provider's documented
schema, but bind a NEW static-tail context, not the old transport context.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import numpy as np
from projector_rate_probe import rate_matrices

PREPARATION_COMMIT='f7b5eef95895f299327562859ce0b278ffa8679c'
SIGNED_Z=(-16.,16.,-20.,20.,-24.,24.,-32.,32.)
ACTIVE_SCREENS=('raw_cross_relative_max','operator_hermiticity_relative_max','metric_min_ratio')
SELECTED=(9,10,12,13,14)

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def runtime_query_id(context_id, time_hex):
    if not isinstance(context_id,str) or len(context_id)!=64:
        raise ValueError('SHA256 context identity required')
    tt=float.fromhex(time_hex)
    if not math.isfinite(tt) or tt.hex()!=time_hex:
        raise ValueError('canonical finite binary64 time required')
    return digest({'schema':'BASS_TP2D_RUNTIME_QUERY_V1','context_id':context_id,'time_hex':time_hex})

def bind_runtime_plan(tail, old_context):
    """Bind the existing eight PLAN_ONLY rows without altering any time bits.

    This document is not an execution approval. A future bounded launcher must
    also pin its own exact commit/tree/dependency bytes and authority object.
    """
    tail=copy.deepcopy(tail);old_context=copy.deepcopy(old_context)
    c=old_context['context']['contract'];physics=old_context['context']['physics_identity']
    conditions=[tail['basis']=='B0',tail['query_count']==8,
        tail['b_a0']==c['b_a0']==2., tail['energy_keV_per_u']==c['energy_keV_per_u']==100.,
        tail['radial_spec']==c['radial_spec'],c['radial_spec']['lmax']==1,
        tail['same_center_order']==c['same_center_order']==20,
        tail['native_backend']==c['analytic_backend']=='EXACT_SP_MOMENTS_CXX_V1',
        tail['qualification_ladder']==c['runtime_reference_resolutions'],
        tail['qualification_screens']==c['screens'],
        len(tail['qualification_ladder'])==11,
        tail['maximum_future_raw_attempts']==88,
        tail['operator_only'] is True,tail['new_native_samples_authorized'] is False,
        tail['query_id_semantics']=='PLAN_ONLY_NOT_QUALIFIED_PROVIDER_CACHE_IDS',
        tail['first_passing_adjacent_pair_required'] is True]
    if not all(conditions):raise ValueError('tail preparation contract outside frozen B0 scope')
    samples=tail['samples']
    if len(samples)!=8 or tuple(s['z_a0'] for s in samples)!=SIGNED_Z:
        raise ValueError('exact signed eight-point order required')
    v=math.sqrt(2*(1000.*c['energy_keV_per_u']/27.211386245988)/1822.888486209)
    if tail['velocity_au']!=v:raise ValueError('frozen velocity arithmetic mismatch')
    for row in samples:
        z=row['z_a0'];tt=z/v
        if (row['z_hex']!=float(z).hex() or row['time_hex']!=tt.hex() or
            row['time_au']!=tt or row['R_a0']!=math.sqrt(c['b_a0']**2+z*z)):
            raise ValueError('tail time/z/radius arithmetic mismatch')
    if len({r['query_id'] for r in samples})!=8:
        raise ValueError('plan IDs not unique')
    context={
        'schema':'BASS_R4P0A_B0_STATIC_TAIL_CONTEXT_V1',
        'preparation_commit':PREPARATION_COMMIT,
        'source_tail_contract_digest':digest(tail),
        'parent_transport_context_id':old_context['context_id'],
        'frozen_physics_identity':physics,
        'energy_keV_per_u':100.,'b_a0':2.,'velocity_au':v,
        'radial_spec':c['radial_spec'],'same_center_order':20,
        'native_backend':'EXACT_SP_MOMENTS_CXX_V1',
        'qualification_ladder':c['runtime_reference_resolutions'],
        'active_screens':{k:c['screens'][k] for k in ACTIVE_SCREENS},
        'scope':'EIGHT_SIGNED_STATIC_B0_SNAPSHOTS_NOT_TRANSPORT',
        'allowed_time_hex':[r['time_hex'] for r in samples]}
    cid=digest(context)
    rows=[]
    for row in samples:
        item={k:row[k] for k in ('z_a0','z_hex','R_a0','time_au','time_hex')}
        item['plan_query_id']=row['query_id']
        item['runtime_query_id']=runtime_query_id(cid,row['time_hex']);rows.append(item)
    return {'schema':'BASS_R4P0A_BOUND_QUERY_PLAN_V1','context_id':cid,'context':context,
        'queries':rows,'query_count':8,'max_raw_operator_evaluations':88,
        'active_screens':context['active_screens'],
        'native_authorized':False,'temporal_gate_inherited':False,
        'independent_metric_derivative_validation':False,
        'tail_error_bound_certified':False,'interpolation_allowed':False,
        'positive_negative_reuse_allowed':False,'baseline_new_evaluation_allowed':False,
        'claim_ceiling':copy.deepcopy(tail['claim_ceiling'])}

def snapshot_diagnostics(S,H,D,row):
    """Postprocess one qualified B0 snapshot without inventing a state at its time.

    All three matrices are in the pinned a0/Eh/atomic-time convention, so hbar=1.
    Raw block norms retain their coordinate-specific meaning; rho is the local
    selected-span generalized rate envelope under Sdot=D+D^dagger, not a tail
    integral or independent derivative test.
    """
    arrays=[np.asarray(x,complex) for x in (S,H,D)]
    if any(x.shape!=(18,18) or not np.isfinite(x).all() for x in arrays):
        raise ValueError('finite 18x18 B0 snapshots required')
    S,H,D=arrays
    J=np.eye(18,dtype=complex)[:,SELECTED]
    rate=rate_matrices(S,H,D,J,hbar=1.)
    K=np.linalg.solve(S,H-1j*D)
    t,p=slice(0,9),slice(9,18)
    spec=lambda x:float(np.linalg.norm(x,2))
    eig=np.linalg.eigvalsh(S);out={k:row[k] for k in ('z_a0','R_a0','time_hex')}
    for key,a in [('S',S),('H',H),('D',D),('K',K)]:
        out[key+'_tp_2norm']=spec(a[t,p]);out[key+'_pt_2norm']=spec(a[p,t])
    kn=spec(K)
    out.update({'K_2norm':kn,'K_tp_relative':out['K_tp_2norm']/kn if kn else None,
        'metric_min':float(eig[0]),'metric_max':float(eig[-1]),
        'metric_condition':rate['S_condition'],
        'rho_per_atomic_time':rate['rho'],
        'rho_interpretation':'LOCAL_GALERKIN_RATE_ENVELOPE_UNDER_SDOT_IDENTITY',
        'metric_identity_residual':rate['metric_identity_residual'],
        'independent_metric_derivative_validation':False,
        'Pdot_at_this_tail_sample':None,'state_available_at_this_tail_sample':False,
        'tail_error_bound_certified':False})
    return out
