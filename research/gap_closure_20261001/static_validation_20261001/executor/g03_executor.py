"""Fresh G03-only admission, bounded dispatch and return; no legacy auth reuse."""
from __future__ import annotations
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent
if str(AUDIT) not in sys.path:sys.path.insert(0,str(AUDIT))
import static_validation as sv
REPO=sv.REPO
if str(sv.SOURCE_DIR) not in sys.path:sys.path.insert(0,str(sv.SOURCE_DIR))
import static_tail as old
from execution_admission import strict_json,THREAD_KEYS,consume_authorization
from parallel_bridge import GlobalBudget,PlannedQuery,dispatch_bounded,publish_pair,validate_pair
from resource_census import live_resource_census,verify_prior_pool_teardown
import hashlib,json,math,os,re,subprocess,time,traceback
import numpy as np

APPROVAL='YES_I_AUTHORIZE_TWO_G03_SIGNED48_STATIC_QUERIES'
APPROVAL_ENV='ALLOW_NEW_NATIVE_G03'
FROZEN_PLAN_SHA256='479ca3efdbbacfdc698b29a9c4eeef2597e5979b2960e14a594cad7f96bb01b4'
PLAN_PATH=HERE/'G03_SCIENCE_CONTRACT.json'
RESOURCE_PATH=HERE/'G03_RESOURCE_POLICY.json'
AUTHORITY_KEYS=('execution_commit','execution_tree','source_pins_sha256','query_plan_sha256','binding_inputs_sha256','resource_policy_sha256')
READY='G03_SIGNED48_EXECUTOR_READY_EXPLICIT_FRESH_NATIVE_AUTH_PENDING'
sha=sv.sha
write_new=old.write_new


def frozen_plan():
    if sha(PLAN_PATH)!=FROZEN_PLAN_SHA256:raise ValueError('frozen G03 science contract byte digest changed')
    spec=strict_json(PLAN_PATH);parent=sv.load_source_plan();identity=sv.make_plan(parent)['identity']
    if (spec['number_of_qualified_queries']!=2 or spec['runtime_inputs']!=old.BINDING['runtime_inputs']
        or spec['native_pins']!=old.BINDING['native'] or spec['basis_identity']!=identity['basis_identity']
        or spec['qualification_ladder']!=parent['context']['qualification_ladder']
        or spec['active_screens']!=parent['active_screens'] or spec['same_center_order']!=20
        or spec['physics']!={'energy_keV_per_u':100.0,'b_a0':2.0,'velocity_au':identity['velocity_au'],
                            'basis':'B0','channels':18,'selected_indices':[9,10,12,13,14]}
        or spec['resources']['maximum_raw_operator_evaluations']!=22
        or spec['resources']['maximum_workers']!=2 or spec['resources']['maximum_total_wall_seconds']!=900
        or spec['resources']['proposed_worker_memory_bytes']!=4<<30):
        raise ValueError('G03 frozen scientific/resource contract mismatch')
    if [q['z_a0'] for q in spec['queries']]!=[-48.,48.]:raise ValueError('exact signed48 pair required')
    queries=[]
    for row in spec['queries']:
        z=row['z_a0'];th=float(z/identity['velocity_au']).hex()
        if row['time_hex']!=th or row['time_au']!=float.fromhex(th) or row['R_a0']!=math.hypot(z,2):
            raise ValueError('G03 exact coordinate/time mismatch')
        queries.append({**row,'z_hex':float(z).hex(),'action':'NEW_QUALIFIED_QUERY'})
    context=hashlib.sha256(json.dumps({'schema':'BASS_G03_SIGNED48_CONTEXT_V1',
        'science_contract_sha256':FROZEN_PLAN_SHA256,'parent_context':parent['context_id']},
        sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'schema':'BASS_G03_SIGNED48_EXECUTION_PLAN_V1','identity':identity,'units':sv.UNITS,
        'context_id':context,'source_plan_parent_context':parent['context_id'],'queries':queries,
        'qualification_ladder':spec['qualification_ladder'],'active_screens':spec['active_screens'],
        'new_query_count':2,'max_raw_operator_evaluations':22,'verified_reuse_count':0,
        'native_authorized':False,'source_contract_sha256':FROZEN_PLAN_SHA256}

def exact_items(plan):
    if plan!=frozen_plan():raise ValueError('exact frozen G03 plan required')
    return [PlannedQuery(sv.query_id(plan['context_id'],q['time_hex']),q['time_hex'],None,None)
        for q in plan['queries'] if q['action']=='NEW_QUALIFIED_QUERY']


def fixed_scope():
    plan=frozen_plan();items=exact_items(plan)
    return {'schema':'BASS_G03_SIGNED48_AUTHORIZATION_PROPOSAL_V1','resource_sharing_policy':'COOPERATIVE_SHARED_HOST',
       'raw_operator_evaluation_cap':22,'operator_query_count':2,'reused_query_count':0,
       'native_parity':'NONE','derivative_fd_queries':0,'pilot_queries':0,'transport':False,
       'rho_expansion_queries':2,'numerical_threads':1,'parent_raw_attempts':0,'automatic_worker_scaling':False,
       'basis':'B0','channels':18,'energy_keV_per_u':100,'b_a0':2,'context_id':plan['context_id'],
       'time_hex':[q.time_hex for q in items],'runtime_query_ids':[q.query_id for q in items],
       'runtime_inputs':old.BINDING['runtime_inputs'],'native':old.BINDING['native'],
       'basis_identity':old.BINDING['basis_identity'],'claim_ceiling':old.BINDING['claim_ceiling']}

def validate_scope(proposal,authority,*,approved,unused=True,now=None):
    if not approved:raise PermissionError('G03_NATIVE_NOT_AUTHORIZED')
    if not unused:raise PermissionError('authorization already consumed')
    for key in AUTHORITY_KEYS:
        if proposal.get(key)!=authority[key]:raise ValueError('authority pin mismatch: '+key)
    if not re.fullmatch(r'G03-STATIC48-[A-Za-z0-9_.-]{15,60}',proposal.get('authorization_id','')):
        raise ValueError('fresh G03-only authorization ID required')
    if any(proposal.get(k)!=v for k,v in fixed_scope().items()):raise ValueError('frozen G03 scope mismatch')
    w=proposal.get('workers');cpus=proposal.get('approved_cpu_list',[])
    if (type(w) is not int or not 1<=w<=2 or proposal.get('hard_max_workers')!=2
       or len(cpus)!=w or len(set(cpus))!=w or any(type(c) is not int or c<0 for c in cpus)
       or proposal.get('worker_ram_bytes')!=4<<30 or proposal.get('total_worker_ram_cap_bytes')!=w*(4<<30)
       or proposal.get('minimum_live_available_bytes')!=(w*4+4)*(1<<30)):
        raise ValueError('bounded worker CPU/RAM scope mismatch')
    now=time.time() if now is None else now
    wall=proposal.get('wall_seconds');deadline=proposal.get('deadline_unix');grace=proposal.get('termination_grace_seconds')
    if (type(wall) is not int or not 1<=wall<=900 or not isinstance(deadline,(int,float)) or not math.isfinite(deadline)
       or not now<deadline<=now+wall+1 or type(grace) is not int or not 1<=grace<=120
       or not isinstance(proposal.get('cost_scope'),str) or not proposal['cost_scope'].strip()):
        raise ValueError('explicit unexpired wall/deadline/grace/cost scope required')
    return proposal


def required_sources():
    names=set(strict_json(sv.SOURCE_DIR/'DEPENDENCY_CLOSURE.json')['files'])
    names.update(str(p.relative_to(REPO)) for p in sv.SOURCE_DIR.glob('*.py'))
    names.update(str(p.relative_to(REPO)) for p in HERE.glob('*.py'))
    for p in (PLAN_PATH,RESOURCE_PATH,AUDIT/'static_validation.py',
        AUDIT.parent/'asymptotics_20261001/asymptotic_models.py',
        sv.SOURCE_DIR/'execution_evidence/R4P0-B0-STATIC-TAIL-20260930-A1/STATIC_TAIL_SNAPSHOTS.csv'):
        names.add(str(p.relative_to(REPO)))
    for n in ('BINDING_INPUTS.json','BOUND_B0_TAIL_QUERY_PLAN.json','DEPENDENCY_CLOSURE.json',
              'fixtures/R4P0/inputs/SCIENCE_CONTEXT.json','fixtures/R4P0/receipts/R4P0_TAIL_PREFLIGHT_CONTRACT.json'):
        names.add(str((sv.SOURCE_DIR/n).relative_to(REPO)))
    return sorted(names)

def verify_source(pins):
    if set(pins.get('source_files',{}))!=set(required_sources()):raise ValueError('exact imported source closure required')
    old.verify_source(pins,REPO)
    original=strict_json(REPO/'research/foundation_rebuild/ncp_shared_research_20260928/r4c_temporal_continuation/PINNED_DEPENDENCIES.json')['files']
    for name,digest in original.items():
        if sha(REPO/name)!=digest:raise ValueError('frozen numerical dependency drift: '+name)


def verify_inputs(inputs,build):
    contract,parent,native=old.verify_inputs(inputs,build)
    plan=frozen_plan()
    if (plan['source_plan_parent_context']!=parent['context_id']
        or plan['identity']['basis_identity']!=old.BINDING['basis_identity']):raise ValueError('signed48 parent scientific identity mismatch')
    return {**contract,'screens':plan['active_screens'],'runtime_reference_resolutions':plan['qualification_ladder']},plan,native


def verify_budget(budget,max_inflight):
    seed=budget.seed
    if (type(max_inflight) is not int or not 1<=max_inflight<=2 or seed.get('maximum')!=22
        or type(seed.get('maximum')) is not int or seed.get('parent_raw_attempts')!=0
        or strict_json(budget.root/'SEED.json')!=seed):raise ValueError('G03 budget/worker scope mismatch')


def _copy_new(source,target):
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(Path(source).read_bytes());f.flush();os.fsync(f.fileno())


def execute_plan(plan,out,budget,executor,compute,max_inflight):
    items=exact_items(plan);out=Path(out);verify_budget(budget,max_inflight)
    if any((out/n).exists() for n in ('runtime_queries','diagnostics','FIRST_FAILURE.json','PROVIDER_AUDIT.json','G03_RETURN_ANALYSIS.json')):
        raise FileExistsError('G03 return publication must be create-only')
    contract=strict_json(sv.SOURCE_DIR/'fixtures/R4P0/inputs/SCIENCE_CONTEXT.json')['context']['contract']
    contract={**contract,'screens':plan['active_screens'],'runtime_reference_resolutions':plan['qualification_ladder']}
    records={};worker_pids=set();samples=[]
    by_time={q['time_hex']:q for q in plan['queries']}
    def commit(item,value):
        if item.query_id in records:raise ValueError('duplicate G03 query publication')
        task=Path(value['task_dir']).resolve()
        if not task.is_relative_to((out/'worker_tasks').resolve()):raise ValueError('worker result escapes this run')
        rec=publish_pair(task/'runtime_queries',out/'runtime_queries',item,plan['context_id'],contract)
        from g03_rate_postprocess import analyze_query
        sample=analyze_query(out/'runtime_queries',item,by_time[item.time_hex],out/'diagnostics')
        sample['diagnostic_relative_path']='diagnostics/'+sample['diagnostic_relative_path']
        samples.append(sample);records[item.query_id]=rec;worker_pids.add(value['worker_pid'])
    try:
        dispatch_bounded(items,executor,compute,commit,max_inflight=max_inflight,
           deadline_unix=budget.seed['deadline_unix'],cancelled=lambda:(budget.root/'CANCELLED.json').exists())
        actual={p.stem for p in (out/'runtime_queries').glob('*.json')}
        payloads={p.stem for p in (out/'runtime_queries').glob('*.npz')}
        if actual!=payloads or actual!={q.query_id for q in items}:raise ValueError('exact2 new-query coverage mismatch')
        for item in items:validate_pair(out/'runtime_queries',item,plan['context_id'],contract)
        returned={'samples':sorted(samples,key=lambda x:x['z_a0']),'source_receipts_verified':True,
            'source_contract_sha256':FROZEN_PLAN_SHA256,'authorization':'See EXECUTION_ADMISSION.json in this run'}
        write_new(out/'RHO_SAMPLES.json',returned)
        adir=AUDIT.parent/'asymptotics_20261001'
        if str(adir) not in sys.path:sys.path.insert(0,str(adir))
        from asymptotic_models import evaluate_return,load_samples
        report=evaluate_return(load_samples(),returned)
        write_new(out/'G03_RETURN_ANALYSIS.json',report)
        audit={'schema':'BASS_G03_SIGNED48_PROVIDER_AUDIT_V1','completed_queries':2,'reused_queries':0,
           'total_snapshots':2,'raw_attempts':budget.used(),'maximum_raw_attempts':22,
           'worker_pids':sorted(worker_pids),'fd_diagnostic_status':'NOT_IN_SCOPE',
           'transport_executed':False,'rho_expansion_queries':2,'physical_G03_closed':False,
           'claim_ceiling':old.BINDING['claim_ceiling']}
        write_new(out/'PROVIDER_AUDIT.json',audit);return audit
    except BaseException as exc:
        if not (out/'FIRST_FAILURE.json').exists():write_new(out/'FIRST_FAILURE.json',{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
        if not (budget.root/'CANCELLED.json').exists():budget.cancel(str(exc))
        raise

def native_pool(proposal,pins,inputs,build,out,budget):
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing
    from g03_worker import initialize
    return ProcessPoolExecutor(max_workers=proposal['workers'],mp_context=multiprocessing.get_context('spawn'),
       initializer=initialize,initargs=(str(inputs),str(build),pins,str(out),str(budget.root),proposal['approved_cpu_list'],proposal['worker_ram_bytes']))


def request(proposal_path,pins_path,inputs,build,out,*,approved_sha,pool_factory=native_pool,preflight_only=False):
    proposal_path=Path(proposal_path);pins_path=Path(pins_path);out=Path(out)
    # Reject absent exact new approval before native construction, environment/input checks, factory or output mutation.
    if not preflight_only and (os.environ.get(APPROVAL_ENV)!=APPROVAL or approved_sha!=sha(proposal_path)):
        raise PermissionError('G03_NATIVE_NOT_AUTHORIZED')
    proposal=strict_json(proposal_path);pins=strict_json(pins_path)
    nonce=Path.home()/'.local/state/bass_r4c/authorizations'/(proposal.get('authorization_id','')+'.json')
    authority={'execution_commit':pins['execution_commit'],'execution_tree':pins['execution_tree'],
       'source_pins_sha256':sha(pins_path),'query_plan_sha256':sha(PLAN_PATH),
       'binding_inputs_sha256':sha(sv.SOURCE_DIR/'BINDING_INPUTS.json'),'resource_policy_sha256':sha(RESOURCE_PATH)}
    validate_scope(proposal,authority,approved=True,unused=not nonce.exists())
    if os.path.abspath(sys.executable)!=proposal.get('python_path'):raise ValueError('approved Python executable mismatch')
    for key,path in [('source_pins_path',pins_path),('runtime_inputs_path',inputs),('native_build_path',build)]:
        if str(Path(path).resolve())!=proposal.get(key):raise ValueError('approved local path mismatch: '+key)
    if not preflight_only and str(out.resolve())!=proposal.get('out_path'):raise ValueError('approved output path mismatch')
    verify_source(pins)
    head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
    tree=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^{tree}'],text=True).strip()
    if (head,tree)!=(proposal['execution_commit'],proposal['execution_tree']) or subprocess.check_output(['git','-C',str(REPO),'status','--porcelain','--untracked-files=all'],text=True):
        raise ValueError('exact clean execution commit/tree required')
    import scipy
    if sys.version_info<(3,11) or np.__version__!='2.3.5' or scipy.__version__!='1.17.0' or any(os.environ.get(k)!='1' for k in THREAD_KEYS):
        raise ValueError('prepared versions/thread limits required')
    if os.environ.get('BASS_ANALYTIC_SOURCE_ROOT',str(REPO))!=str(REPO):raise ValueError('external analytic source override forbidden')
    contract,plan,native=verify_inputs(inputs,build)
    if native!=pins['native']:raise ValueError('prepared native receipt mismatch')
    if out.resolve().is_relative_to(REPO) or out.exists():raise ValueError('fresh output outside worktree required')
    out.mkdir(parents=True)
    write_new(out/'PROPOSAL_PIN.json',{'proposal_sha256':sha(proposal_path),'native_authorized':not preflight_only})
    census=live_resource_census(proposal['approved_cpu_list'],proposal['workers'],proposal['worker_ram_bytes'],
       receipt_path=out/'INITIAL_RESOURCE_CENSUS.json',sharing_policy='COOPERATIVE_SHARED_HOST')
    verify_prior_pool_teardown(set(),run_pgid=os.getpgrp(),receipt_path=out/'INITIAL_OWN_POOL_TEARDOWN.json',settle_seconds=0.)
    admission={**proposal,'proposal_sha256':sha(proposal_path),'native':native,'preflight_only':preflight_only,
       'cost_limit_enforced_by_code':False,'new_authorization_consumed':False,'live_census_status':census['status'],
       'environment':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'threads':{k:os.environ[k] for k in THREAD_KEYS}}}
    write_new(out/'EXECUTION_ADMISSION.json',admission)
    if preflight_only:return {'status':READY,'new_native_operator_evaluations':0,'new_authorization_consumed':0}
    if not sys.flags.isolated or os.getpgrp()!=os.getpid():raise ValueError('isolated Python and dedicated process group required before consumption')
    consume_authorization(out,{**admission,'new_authorization_consumed':True})
    budget=GlobalBudget.create(out/'GLOBAL_BUDGET',parent_attempts=0,maximum=22,
       deadline_unix=min(proposal['deadline_unix'],time.time()+proposal['wall_seconds']))
    pool=None
    try:
        pool=pool_factory(proposal,pins,inputs,build,out,budget)
        from g03_worker import compute
        audit=execute_plan(plan,out,budget,pool,compute,proposal['workers'])
        pool.shutdown(wait=True);pool=None
        verify_prior_pool_teardown(set(audit['worker_pids']),run_pgid=os.getpgrp(),receipt_path=out/'FINAL_OWN_POOL_TEARDOWN.json')
        report={'status':'G03_SIGNED48_STATIC_RETURN_COMPLETE_REVIEW_REQUIRED','new_native_operator_evaluations':budget.used(),
           'new_authorization_consumed':1,'new_static_queries':2,'reused_static_queries':0,'physical_G03_closed':False,
           'fd_diagnostic_status':audit['fd_diagnostic_status'],'claim_ceiling':old.BINDING['claim_ceiling']}
        write_new(out/'RETURN_REPORT.json',report);return report
    except BaseException as exc:
        if not (out/'FIRST_FAILURE.json').exists():write_new(out/'FIRST_FAILURE.json',{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
        if not (budget.root/'CANCELLED.json').exists():budget.cancel(str(exc))
        write_new(out/'RETURN_REPORT.json',{'status':'G03_SIGNED48_EXECUTION_BLOCKED','new_native_operator_evaluations':budget.used(),
            'new_authorization_consumed':1,'physical_G03_closed':False,'claim_ceiling':old.BINDING['claim_ceiling']})
        raise
    finally:
        if pool is not None:pool.shutdown(wait=False,cancel_futures=True)
        # The dedicated supervisor reaps this run's process group on failure.
