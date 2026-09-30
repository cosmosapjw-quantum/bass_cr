"""Read stored bytes and prepare contracts. This module has no science launcher."""
from pathlib import Path
import hashlib
import json
import math
import os
import numpy as np

HERE=Path(__file__).resolve().parent
CONTRACT=json.loads((HERE/'CONTRACT.json').read_text())
SELECTED=tuple(CONTRACT['selected_indices'])
SPECS={'B0':(1,2,1),'B1':(2,3,1),'B2':(3,4,1),'B3':(3,4,2)}
STATUS='R4P0_TAIL_AND_BASIS_PREFLIGHT_READY__NATIVE_AUTHORIZATION_PENDING'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_new(path,value):
    with Path(path).open('x') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
        f.flush();os.fsync(f.fileno())

def forbidden(action):
    raise PermissionError('NATIVE_AUTHORIZATION_PENDING: '+str(action))

def registry(name):
    if name not in SPECS:raise ValueError('unknown basis registry')
    lmax,nmax,npositive=SPECS[name]
    spec={**CONTRACT['frozen_transport_contract']['radial_spec'],
          'lmax':lmax,'bound_nmax':nmax,'positive_per_l':npositive}
    bank=[]
    for ell in range(lmax+1):
        for n in range(ell+1,nmax+1):
            bank.append({'l':ell,'principal_n':n,'positive_rank':None,'kind':'bound'})
        for rank in range(1,npositive+1):
            bank.append({'l':ell,'principal_n':None,'positive_rank':rank,'kind':'positive_pseudostate'})
    rows=[]
    for center in (0,1):
        for mode,r in enumerate(bank):
            for m in range(-r['l'],r['l']+1):
                rows.append({'index':len(rows),'center':center,'radial_mode':mode,'m':m,**r})
    original=[r['index'] for r in rows if r['center']==1 and r['kind']=='bound' and r['principal_n']<=2]
    return {'name':name,'radial_spec':spec,'radial_modes':bank,'channels':rows,
            'channel_count':len(rows),'ordering':'center, ascending l, negative principal n then positive rank, ascending m',
            'original_five_channel_projectile_span':original,
            'inherits_B0_temporal_certificate':False,
            'new_scientific_input':name!='B0','hidden_channel_deletion_allowed':False,
            'frozen_native_backend_status':'SUPPORTED_SP' if name=='B0' else 'UNSUPPORTED_L_GT_1',
            'full_two_center_gram_status':'STORED_A3_FINAL_AVAILABLE' if name=='B0' else 'NOT_MEASURED',
            'radial_coefficient_identity_status':'BIND_EXACT_STORED_B0' if name=='B0' else 'FUTURE_CONSTRUCTION_AND_QUALIFICATION_REQUIRED'}

def bind_bank(reg,modes):
    expected=reg['radial_modes']
    if len(modes)!=len(expected):raise ValueError('missing/extra radial mode; no hidden deletion')
    for planned,actual in zip(expected,modes):
        energy=actual['energy'];residual=actual['residual']
        if (actual['l']!=planned['l'] or actual['principal_n']!=planned['principal_n']
            or not isinstance(actual['identity'],str) or len(actual['identity'])!=64
            or any(ch not in '0123456789abcdef' for ch in actual['identity'])
            or not math.isfinite(energy) or not math.isfinite(residual) or residual<0 or residual>2e-8
            or abs(energy)<=100*residual
            or (planned['kind']=='bound' and energy>=0)
            or (planned['kind']=='positive_pseudostate' and not 0<energy<=reg['radial_spec']['positive_emax'])):
            raise ValueError('radial identity/order/classification/residual mismatch')
    return [{**r,'energy_Eh':modes[r['radial_mode']]['energy'],
             'radial_identity':modes[r['radial_mode']]['identity']} for r in reg['channels']]

def metric(S):
    S=np.asarray(S,complex)
    if S.shape!=(18,18) or not np.isfinite(S).all() or np.max(abs(S-S.conj().T))>1e-12:
        raise ValueError('invalid metric shape/finiteness/hermiticity')
    e=np.linalg.eigvalsh(S)
    if e[0]<=0 or e[0]/e[-1]<CONTRACT['frozen_transport_contract']['screens']['metric_min_ratio']:
        raise ValueError('invalid positive definite metric')
    return S,e

def projector(S,c,indices=SELECTED):
    if tuple(indices)!=SELECTED:raise ValueError('R4A negative-energy selector required; positive pseudostates excluded')
    S,e=metric(S);c=np.asarray(c,complex)
    if c.shape!=(18,) or not np.isfinite(c).all():raise ValueError('invalid state')
    ix=np.array(indices);G=S[np.ix_(ix,ix)];v=(S@c)[ix]
    probability=np.vdot(v,np.linalg.solve(G,v))
    norm=np.vdot(c,S@c)
    if abs(probability.imag)>1e-12 or probability.real < -1e-12 or probability.real>norm.real+1e-12:
        raise ValueError('projector probability unresolved')
    J=np.eye(18,dtype=complex)[:,ix]
    Q=S@J@np.linalg.solve(G,J.conj().T@S)
    checks={'hermiticity_defect':float(np.linalg.norm(Q-Q.conj().T,2)),
            'metric_idempotence_defect':float(np.linalg.norm(Q@np.linalg.solve(S,Q)-Q,2)),
            'gram_condition':float(np.linalg.cond(G)),
            'metric_eigenvalue_range':[float(e[0]),float(e[-1])],
            'metric_condition':float(np.linalg.cond(S)),
            'min_Q_eigenvalue':float(np.linalg.eigvalsh((Q+Q.conj().T)*0.5)[0]),
            'min_S_minus_Q_eigenvalue':float(np.linalg.eigvalsh(((S-Q)+(S-Q).conj().T)*0.5)[0])}
    if max(checks['hermiticity_defect'],checks['metric_idempotence_defect'],
           -checks['min_Q_eigenvalue'],-checks['min_S_minus_Q_eigenvalue'])>1e-12:
        raise ValueError('Gram projector checks unresolved')
    return float(probability.real),checks

def operator_diagnostics(S,H,D):
    S,e=metric(S);H=np.asarray(H,complex);D=np.asarray(D,complex)
    if any(a.shape!=(18,18) or not np.isfinite(a).all() for a in (H,D)):
        raise ValueError('invalid full operator')
    K=np.linalg.solve(S,H-1j*D)
    result={key:float(np.linalg.norm(a[:9,9:],2)) for key,a in [('S_tp_2norm',S),('H_tp_2norm',H),('D_tp_2norm',D),('K_tp_2norm',K)]}
    full=float(np.linalg.norm(K,2));result.update(K_relative=result['K_tp_2norm']/full,
        metric_eigenvalue_range=[float(e[0]),float(e[-1])],metric_condition=float(np.linalg.cond(S)),
        b_a0=2.,z_a0=12.,R_a0=math.sqrt(4.+144.),tail_error_bound=None)
    return result

def closeout(root):
    root=Path(root)
    for name,pin in CONTRACT['input_files'].items():
        p=root/name
        if not p.is_file() or p.is_symlink() or p.stat().st_size!=pin['bytes'] or digest(p.read_bytes())!=pin['sha256']:
            raise ValueError('input identity mismatch: '+name)
    raw=(HERE/'R4O_PRERECORDED_EVIDENCE.json').read_bytes()
    if digest(raw)!=CONTRACT['r4o_evidence_sha256']:raise ValueError('R4O identity mismatch')
    oracle=json.loads(raw);basis=json.loads((root/'BASIS.json').read_text());rows=bind_bank(registry('B0'),basis['modes'])
    if [r['index'] for r in rows if r['center']==1 and r['kind']=='bound']!=list(SELECTED):raise ValueError('R4A selector mismatch')
    arrays={}
    for key,name in [('reference','REFERENCE_STATES.npz'),('N768','CANDIDATE_N768.npz'),('N1536','CANDIDATE_N1536.npz')]:
        with np.load(root/name,allow_pickle=False) as f:arrays[key]={k:np.array(f[k]) for k in f.files}
    if any(not np.array_equal(d['initial_state'],arrays['reference']['initial_state']) for d in arrays.values()):
        raise ValueError('original initial state mismatch')
    with np.load(root/'runtime_queries'/(CONTRACT['final_query_id']+'.npz'),allow_pickle=False) as f:
        S,H,D=[np.array(f['selected__'+k]) for k in ('S','H','D')]
    probabilities={};checks=None
    for key,d in arrays.items():probabilities[key],checks=projector(S,d['final_state'])
    expected=[oracle['selected_span'][k] for k in ('reference','n768','n1536')]
    ulps=CONTRACT['roundoff_reproduction']['probability_ulps']
    for actual,ref in zip(probabilities.values(),expected):
        if abs(actual-ref)>ulps*math.ulp(ref):raise ValueError('R4O probability reproduction mismatch')
    diff=abs(probabilities['N1536']-probabilities['reference']);older=abs(probabilities['N768']-probabilities['reference'])
    allowance=2*ulps*max(math.ulp(x) for x in probabilities.values())
    if min(diff,older)<=allowance:raise ValueError('observable order numerically unresolved')
    interval=[math.log2((older-allowance)/(diff+allowance)),math.log2((older+allowance)/(diff-allowance))]
    if not interval[0]<=oracle['selected_span']['observed_order']<=interval[1]:raise ValueError('R4O observable order mismatch')
    obs={'status':'FINITE_SPAN_SELECTED_OBSERVABLE_TEMPORALLY_ADMITTED','selected_indices':list(SELECTED),
         'excluded_positive_indices':CONTRACT['excluded_positive_indices'],'projector_formula':'Q = S J solve(J^dagger S J, J^dagger S)',
         'probability_evaluation':'v=(S@c)[indices]; real(v^dagger solve(G,v))',
         'probabilities':probabilities,'absolute_difference':diff,'relative_difference':diff/probabilities['reference'],
         'observed_order':math.log2(older/diff),'order_roundoff_interval':interval,
         'probability_roundoff_differences':[a-b for a,b in zip(probabilities.values(),expected)],
         'projector':checks,'claim_labels':['NOT_ALL_BOUND','NOT_ASYMPTOTIC_CAPTURE','NOT_PRODUCTION_CAPTURE']}
    current=json.loads((root/'TEMPORAL_PAIR_N768_N1536.json').read_text());prev=json.loads((root/'TEMPORAL_PAIR_N384_N768.json').read_text())
    report=json.loads((root/'RETURN_REPORT.json').read_text());gate=json.loads((root/'TEMPORAL_GATE.json').read_text());coverage=json.loads((root/'CACHE_COVERAGE_AUDIT.json').read_text());replay=json.loads((root/'CACHE_ONLY_REPLAY_AUDIT.json').read_text())
    reference_receipt=json.loads((root/'REFERENCE_RECEIPT.json').read_text())
    screens=CONTRACT['frozen_transport_contract']['screens']
    for field,limit in [('candidate_reference_metric_distance',screens['candidate_reference_metric_distance_max']),
                        ('candidate_refinement_metric_distance',screens['candidate_refinement_metric_distance_max']),
                        ('previous_norm_drift',screens['candidate_norm_drift_max']),
                        ('selected_norm_drift',screens['candidate_norm_drift_max'])]:
        if not math.isfinite(current[field]) or not 0<=current[field]<=limit:raise ValueError('frozen temporal/norm screen mismatch')
    if reference_receipt['max_norm_drift']>screens['reference_norm_drift_max']:raise ValueError('reference norm screen mismatch')
    distances=[gate['previous_reference_distance'],current['candidate_reference_metric_distance'],current['candidate_refinement_metric_distance']]
    triangle_allowance=128*np.finfo(float).eps*max(1.,*distances)
    if any(not math.isfinite(d) or d<0 for d in distances) or 2*max(distances)>sum(distances)+triangle_allowance:
        raise ValueError('general triangle inconsistency')
    if (report['execution_head'],report['execution_tree'])!=(CONTRACT['a3_commit'],CONTRACT['a3_tree']):
        raise ValueError('science execution identity mismatch')
    if (report['status']!='N1536_TEMPORAL_GATE_CLOSED' or not current['qualified'] or not gate['triangle_consistent']
        or not gate['reference_norm_pass'] or not gate['all_required_operators_qualified']
        or not current['previous_norm_pass'] or not current['selected_norm_pass']
        or coverage['verified']!=1538 or coverage['union_pairs']!=3583 or report['lifetime_raw_attempts_used']!=5046
        or replay['native_operator_calls']!=0 or not replay['original_initial_state_used']):raise ValueError('temporal admission receipts mismatch')
    pr=math.log2(prev['candidate_reference_metric_distance']/current['candidate_reference_metric_distance']);ps=math.log2(prev['candidate_refinement_metric_distance']/current['candidate_refinement_metric_distance'])
    # R4O orders are approximate printed diagnostics; preserve receipt-derived values.
    # This diagnostic comparison does not modify any temporal/operator screen.
    if max(abs(pr-oracle['temporal']['p_ref_768_1536']),abs(ps-oracle['temporal']['p_self']))>1e-11:raise ValueError('temporal order mismatch')
    baseline=operator_diagnostics(S,H,D)
    if any(not math.isclose(baseline[k],v,rel_tol=2e-12,abs_tol=1e-15) for k,v in oracle['terminal_cross_blocks'].items()):raise ValueError('terminal operator baseline mismatch')
    return {'schema':'BASS_R4O_REPRODUCED_CLOSEOUT_V1','observable':obs,
        'temporal':{'gate':'CLOSED_FOR_CURRENT_FIXED_BASIS_AND_WINDOW','p_ref':pr,'p_self':ps,
                    'd_ref_1536':current['candidate_reference_metric_distance'],'d_768_1536':current['candidate_refinement_metric_distance'],
                    'previous_norm_drift':current['previous_norm_drift'],'current_norm_drift':current['selected_norm_drift'],
                    'reference_norm_drift':reference_receipt['max_norm_drift'],'triangle_distances':distances,
                    'triangle_roundoff_allowance':triangle_allowance,
                    'recorded_R4O_order_differences':[pr-oracle['temporal']['p_ref_768_1536'],ps-oracle['temporal']['p_self']],
                    'no_automatic_N3072':True,'extends_to_other_bases_or_windows':False},
        'terminal_baseline_diagnostics':baseline,'input_pins':CONTRACT['input_files'],
        'claim_ceiling':CONTRACT['claim_ceiling'],'native_operator_calls':0,'authorization_nonce_consumed':False}

def tail_contract():
    frozen=CONTRACT['frozen_transport_contract'];energy=frozen['energy_keV_per_u']
    # Exact expression and constants pinned in cr_repro.observables/constants.
    v=math.sqrt(2*(1000*float(energy)/27.211386245988)/1822.888486209)
    samples=[]
    context=digest(json.dumps({'basis':'B0','radial_spec':frozen['radial_spec'],'b_a0':2.,'energy_keV_per_u':energy,'frame_ETF':'FROZEN_TP2D_FULL'},sort_keys=True).encode())
    for zabs in (16.,20.,24.,32.):
        for sign in (-1.,1.):
            z=sign*zabs;t=z/v
            qid=digest(json.dumps({'tail_plan_context':context,'time_hex':t.hex()},sort_keys=True,separators=(',',':')).encode())
            samples.append({'z_a0':z,'z_hex':z.hex(),'R_a0':math.sqrt(2.*2.+z*z),'time_au':t,'time_hex':t.hex(),'query_id':qid})
    return {'schema':'BASS_R4P0_OPERATOR_ONLY_TAIL_PREREGISTRATION_V1','status':'USER_APPROVAL_REQUIRED','basis':'B0',
        'b_a0':2.,'energy_keV_per_u':energy,'velocity_au':v,'velocity_expression':'sqrt(2*(1000*E/HARTREE_EV)/U_OVER_ME)',
        'radial_spec':frozen['radial_spec'],'same_center_order':frozen['same_center_order'],
        'frame_ETF_conventions':'UNCHANGED_FROZEN_TP2D_FULL','operator_only':True,'new_native_samples_authorized':False,
        'samples':samples,'query_count':len(samples),'query_id_semantics':'PLAN_ONLY_NOT_QUALIFIED_PROVIDER_CACHE_IDS',
        'qualification_ladder':frozen['runtime_reference_resolutions'],
        'qualification_screens':frozen['screens'],'first_passing_adjacent_pair_required':True,
        'maximum_future_raw_attempts':len(samples)*len(frozen['runtime_reference_resolutions']),
        'raw_attempt_definition':'qualified-provider raw operator evaluation, not individual native contraction calls',
        'record_metrics':['R','metric_eigenvalue_range','cond(S)','S_tp_2norm','H_tp_2norm','D_tp_2norm','K_tp_2norm','K_relative','selected_resolution','ordered_raw_convergence_diagnostics'],
        'generator_definition':'K = solve(S,H-iD); TP = target rows/projectile columns',
        'native_backend':frozen['analytic_backend'],'tail_error_bound':None,'diagnostics_are_tail_certificates':False,
        'window_preregistration':{'basis':'B0','b_a0':2.,'candidate_windows_a0':[[-L,L] for L in (12.,16.,20.,24.,32.)],
           'initial_state_policy':'fresh original target1s at each separately approved window initial time',
           'comparison':'same semantic finite-span selected observable at each endpoint; do not compare gauge-dependent coefficient populations',
           'separate_temporal_qualification_per_window':True,'reuse_short_window_certificate':False,
           'dt_reference_current_window':(12./v-(-12./v))/1536,'nstep':'USER_APPROVAL_REQUIRED','reference_rerun':'USER_APPROVAL_REQUIRED',
           'window_error_tolerance':'USER_APPROVAL_REQUIRED','automatic_execution':False,'launcher_available':False},
        'error_axes':{'temporal':'CLOSED_ONLY_B0_Z_MINUS12_PLUS12','finite_window':'OPEN','basis_omission':'OPEN','all_bound_truncation':'OPEN','b_integration':'NO_GO'},
        'claim_ceiling':CONTRACT['claim_ceiling']}

def prepare(root,out):
    result=closeout(root);tail=tail_contract();registries=[registry(n) for n in SPECS]
    registries[0]['resolved_channels']=bind_bank(registries[0],json.loads((Path(root)/'BASIS.json').read_text())['modes'])
    authority={k:CONTRACT[k] for k in ('a3_commit','a3_tree','science_return_sha256','science_return_bytes','r4o_research_commit','r4o_evidence_sha256')}
    templates={'schema':'BASS_R4P0_FUTURE_UNAPPROVED_NATIVE_TEMPLATES_V1','authority':authority,
       'operator_only':{'status':'USER_APPROVAL_REQUIRED','scope':'B0_ONLY_EIGHT_SIGNED_OPERATOR_SAMPLES_NO_TRANSPORT',
           'authorization_id':None,'cpus':None,'workers':None,'worker_ram_bytes':None,'total_ram_cap_bytes':None,
           'deadline_unix':None,'wall_seconds':None,'termination_grace_seconds':None,'cost_scope':None,
           'raw_attempt_cap_proposal':tail['maximum_future_raw_attempts'],'native_parity':'NOT_INCLUDED',
           'one_numerical_thread_per_worker':True,'resource_sharing_policy':'COOPERATIVE_SHARED_HOST'},
       'basis':{'status':'USER_APPROVAL_REQUIRED','registries':['B1','B2','B3'],'full_Gram_conditioning':'NOT_MEASURED',
           'frozen_native_backend_admission':'BLOCKED_L_GT_1','new_backend_implementation_or_qualification_authorized':False},
       'full_window':tail['window_preregistration'],'no_native_launcher_in_this_package':True,'claim_ceiling':CONTRACT['claim_ceiling']}
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    files={'R4O_TEMPORAL_CLOSEOUT.json':result,'FINITE_SPAN_OBSERVABLE.json':result['observable'],
           'R4P0_TAIL_PREFLIGHT_CONTRACT.json':tail,'B0_B3_BASIS_REGISTRY_CONTRACT.json':{'registries':registries,'new_basis_cache_relabeling_allowed':False},
           'FUTURE_NATIVE_TEMPLATES.json':templates}
    for name,value in files.items():write_new(out/name,value)
    receipt={'status':STATUS,'native_operator_calls':0,'authorization_nonce_consumed':False,
             'claim_ceiling':CONTRACT['claim_ceiling'],'generated_file_sha256':{name:digest((out/name).read_bytes()) for name in files}}
    write_new(out/'PREPARATION_RECEIPT.json',receipt)
    return receipt
