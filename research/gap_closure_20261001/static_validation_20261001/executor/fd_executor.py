"""Fresh G02-only admission, bounded dispatch and return; no legacy auth reuse."""
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

APPROVAL='YES_I_AUTHORIZE_66_G02_STATIC_FD_QUERIES'
APPROVAL_ENV='ALLOW_NEW_NATIVE_G02'
FROZEN_PLAN_SHA256='6644827b9cbde65a5a27f8d2229ed9dc99caf9022c70e2c8663a43dfda0b1c7c'
PLAN_PATH=AUDIT/'E_SDOT_FD_EXECUTION_CONTRACT.json'
RESOURCE_PATH=HERE/'RESOURCE_POLICY.json'
AUTHORITY_KEYS=('execution_commit','execution_tree','source_pins_sha256','query_plan_sha256','binding_inputs_sha256','resource_policy_sha256')
READY='G02_FD_EXECUTOR_READY_EXPLICIT_FRESH_NATIVE_AUTH_PENDING'
sha=sv.sha
write_new=old.write_new


def frozen_plan():
    if sha(PLAN_PATH)!=FROZEN_PLAN_SHA256:raise ValueError('frozen G02 plan byte digest changed')
    plan=strict_json(PLAN_PATH)
    manifest=strict_json(AUDIT/'REUSE_MANIFEST.json')
    verified=sv.verify_manifest(AUDIT,manifest,plan)
    if plan!=sv.make_plan(sv.load_source_plan(),verified):raise ValueError('frozen G02 plan semantic mismatch')
    if (plan['new_query_count'],plan['max_raw_operator_evaluations'],plan['verified_reuse_count'])!=(66,726,6):
        raise ValueError('G02 scope must be exactly66new+6reused')
    return plan


def exact_items(plan):
    if plan!=frozen_plan():raise ValueError('exact frozen G02 plan required')
    return [PlannedQuery(sv.query_id(plan['context_id'],q['time_hex']),q['time_hex'],None,None)
        for q in plan['queries'] if q['action']=='NEW_QUALIFIED_QUERY']


def fixed_scope():
    plan=frozen_plan();items=exact_items(plan)
    return {'schema':'BASS_G02_FD_AUTHORIZATION_PROPOSAL_V1','resource_sharing_policy':'COOPERATIVE_SHARED_HOST',
       'raw_operator_evaluation_cap':726,'operator_query_count':66,'reused_query_count':6,
       'native_parity':'NONE','derivative_fd_queries':66,'pilot_queries':0,'transport':False,
       'rho_expansion_queries':0,'numerical_threads':1,'parent_raw_attempts':0,'automatic_worker_scaling':False,
       'basis':'B0','channels':18,'energy_keV_per_u':100,'b_a0':2,'context_id':plan['context_id'],
       'time_hex':[q.time_hex for q in items],'runtime_query_ids':[q.query_id for q in items],
       'runtime_inputs':old.BINDING['runtime_inputs'],'native':old.BINDING['native'],
       'basis_identity':old.BINDING['basis_identity'],'claim_ceiling':old.BINDING['claim_ceiling']}


def validate_scope(proposal,authority,*,approved,unused=True,now=None):
    if not approved:raise PermissionError('G02_NATIVE_NOT_AUTHORIZED')
    if not unused:raise PermissionError('authorization already consumed')
    for key in AUTHORITY_KEYS:
        if proposal.get(key)!=authority[key]:raise ValueError('authority pin mismatch: '+key)
    if not re.fullmatch(r'G02-FD-[A-Za-z0-9_.-]{15,70}',proposal.get('authorization_id','')):
        raise ValueError('fresh G02-only authorization ID required')
    if any(proposal.get(k)!=v for k,v in fixed_scope().items()):raise ValueError('frozen G02 scope mismatch')
    w=proposal.get('workers');cpus=proposal.get('approved_cpu_list',[])
    if (type(w) is not int or not 1<=w<=8 or proposal.get('hard_max_workers')!=8
       or len(cpus)!=w or len(set(cpus))!=w or any(type(c) is not int or c<0 for c in cpus)
       or proposal.get('worker_ram_bytes')!=1<<30 or proposal.get('total_worker_ram_cap_bytes')!=w*(1<<30)
       or proposal.get('minimum_live_available_bytes')!=(w+4)*(1<<30)):
        raise ValueError('bounded worker CPU/RAM scope mismatch')
    now=time.time() if now is None else now
    wall=proposal.get('wall_seconds');deadline=proposal.get('deadline_unix');grace=proposal.get('termination_grace_seconds')
    if (type(wall) is not int or wall<=0 or not isinstance(deadline,(int,float)) or not math.isfinite(deadline)
       or not now<deadline<=now+wall+1 or type(grace) is not int or not 1<=grace<=120
       or not isinstance(proposal.get('cost_scope'),str) or not proposal['cost_scope'].strip()):
        raise ValueError('explicit unexpired wall/deadline/grace/cost scope required')
    return proposal


def required_sources():
    names=set(strict_json(sv.SOURCE_DIR/'DEPENDENCY_CLOSURE.json')['files'])
    names.update(str(p.relative_to(REPO)) for p in sv.SOURCE_DIR.glob('*.py'))
    names.update(str(p.relative_to(REPO)) for p in HERE.glob('*.py'))
    names.update(str(p.relative_to(REPO)) for p in AUDIT.glob('*.py'))
    names.update(str(p.relative_to(REPO)) for p in (PLAN_PATH,RESOURCE_PATH,AUDIT/'REUSE_MANIFEST.json'))
    names.update(str(p.relative_to(REPO)) for p in (AUDIT/'reused_snapshots').glob('*'))
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
        or plan['identity']['basis_identity']!=old.BINDING['basis_identity']):raise ValueError('FD parent scientific identity mismatch')
    return {**contract,'screens':plan['active_screens'],'runtime_reference_resolutions':plan['qualification_ladder']},plan,native


def verify_budget(budget,max_inflight):
    seed=budget.seed
    if (type(max_inflight) is not int or not 1<=max_inflight<=8 or seed.get('maximum')!=726
        or type(seed.get('maximum')) is not int or seed.get('parent_raw_attempts')!=0
        or strict_json(budget.root/'SEED.json')!=seed):raise ValueError('G02 budget/worker scope mismatch')


def _copy_new(source,target):
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(Path(source).read_bytes());f.flush();os.fsync(f.fileno())


def execute_plan(plan,out,budget,executor,compute,max_inflight):
    items=exact_items(plan);out=Path(out);verify_budget(budget,max_inflight)
    if any((out/n).exists() for n in ('runtime_queries','reused_snapshots','FIRST_FAILURE.json','PROVIDER_AUDIT.json','ALL_SNAPSHOTS_MANIFEST.json')):
        raise FileExistsError('G02 return publication must be create-only')
    contract=strict_json(sv.SOURCE_DIR/'fixtures/R4P0/inputs/SCIENCE_CONTEXT.json')['context']['contract']
    contract={**contract,'screens':plan['active_screens'],'runtime_reference_resolutions':plan['qualification_ladder']}
    manifest=strict_json(AUDIT/'REUSE_MANIFEST.json');records={};worker_pids=set()
    for desc in manifest['snapshots']:
        # Strong raw-attempt qualification recheck in addition to offline identity checks.
        rec=strict_json(AUDIT/desc['record'])
        item=PlannedQuery(rec['query_id'],rec['time_hex'],None,None)
        validate_pair((AUDIT/desc['record']).parent,item,rec['context_id'],contract)
        for key in ('record','payload'):_copy_new(AUDIT/desc[key],out/desc[key])
    by_time={q['time_hex']:q for q in plan['queries']}
    def commit(item,value):
        if item.query_id in records:raise ValueError('duplicate G02 query publication')
        task=Path(value['task_dir']).resolve()
        if not task.is_relative_to((out/'worker_tasks').resolve()):raise ValueError('worker result escapes this run')
        rec=publish_pair(task/'runtime_queries',out/'runtime_queries',item,plan['context_id'],contract)
        q=by_time[item.time_hex]
        manifest['snapshots'].append({'z_a0':q['z_a0'],'z_hex':q['z_hex'],'time_hex':item.time_hex,
           'identity':plan['identity'],'units':sv.UNITS,'record':'runtime_queries/'+item.query_id+'.json',
           'payload':'runtime_queries/'+item.query_id+'.npz','record_sha256':rec['json_sha256'],
           'binding_provenance':{'authorization':'See EXECUTION_ADMISSION.json and AUTHORIZATION_CONSUMED.json in this run',
                                 'plan_sha256':FROZEN_PLAN_SHA256,'kind':'NEW_G02_FD_STATIC_QUERY'}})
        records[item.query_id]=rec;worker_pids.add(value['worker_pid'])
    try:
        dispatch_bounded(items,executor,compute,commit,max_inflight=max_inflight,
           deadline_unix=budget.seed['deadline_unix'],cancelled=lambda:(budget.root/'CANCELLED.json').exists())
        actual={p.stem for p in (out/'runtime_queries').glob('*.json')}
        payloads={p.stem for p in (out/'runtime_queries').glob('*.npz')}
        if actual!=payloads or actual!={q.query_id for q in items}:raise ValueError('exact66 new-query coverage mismatch')
        for item in items:validate_pair(out/'runtime_queries',item,plan['context_id'],contract)
        checked=sv.verify_manifest(out,manifest,plan)
        if len(checked)!=72:raise ValueError('exact72 total-query coverage mismatch')
        write_new(out/'ALL_SNAPSHOTS_MANIFEST.json',manifest)
        result=sv.analyze(manifest,out,plan);write_new(out/'FD_RESULTS.json',result)
        audit={'schema':'BASS_G02_FD_PROVIDER_AUDIT_V1','completed_queries':66,'reused_queries':6,
           'total_snapshots':72,'raw_attempts':budget.used(),'maximum_raw_attempts':726,
           'worker_pids':sorted(worker_pids),'fd_diagnostic_status':result['status'],
           'transport_executed':False,'rho_expansion_queries':0,'physical_G02_closed':False,
           'claim_ceiling':old.BINDING['claim_ceiling']}
        write_new(out/'PROVIDER_AUDIT.json',audit);return audit
    except BaseException as exc:
        if not (out/'FIRST_FAILURE.json').exists():write_new(out/'FIRST_FAILURE.json',{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
        if not (budget.root/'CANCELLED.json').exists():budget.cancel(str(exc))
        raise


def native_pool(proposal,pins,inputs,build,out,budget):
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing
    from fd_worker import initialize
    return ProcessPoolExecutor(max_workers=proposal['workers'],mp_context=multiprocessing.get_context('spawn'),
       initializer=initialize,initargs=(str(inputs),str(build),pins,str(out),str(budget.root),proposal['approved_cpu_list'],proposal['worker_ram_bytes']))


def request(proposal_path,pins_path,inputs,build,out,*,approved_sha,pool_factory=native_pool,preflight_only=False):
    proposal_path=Path(proposal_path);pins_path=Path(pins_path);out=Path(out)
    # Reject absent exact new approval before native construction, environment/input checks, factory or output mutation.
    if not preflight_only and (os.environ.get(APPROVAL_ENV)!=APPROVAL or approved_sha!=sha(proposal_path)):
        raise PermissionError('G02_NATIVE_NOT_AUTHORIZED')
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
    budget=GlobalBudget.create(out/'GLOBAL_BUDGET',parent_attempts=0,maximum=726,
       deadline_unix=min(proposal['deadline_unix'],time.time()+proposal['wall_seconds']))
    pool=None
    try:
        pool=pool_factory(proposal,pins,inputs,build,out,budget)
        from fd_worker import compute
        audit=execute_plan(plan,out,budget,pool,compute,proposal['workers'])
        pool.shutdown(wait=True);pool=None
        verify_prior_pool_teardown(set(audit['worker_pids']),run_pgid=os.getpgrp(),receipt_path=out/'FINAL_OWN_POOL_TEARDOWN.json')
        report={'status':'G02_FD_STATIC_RETURN_COMPLETE_REVIEW_REQUIRED','new_native_operator_evaluations':budget.used(),
           'new_authorization_consumed':1,'new_static_queries':66,'reused_static_queries':6,'physical_G02_closed':False,
           'fd_diagnostic_status':audit['fd_diagnostic_status'],'claim_ceiling':old.BINDING['claim_ceiling']}
        write_new(out/'RETURN_REPORT.json',report);return report
    except BaseException as exc:
        if not (out/'FIRST_FAILURE.json').exists():write_new(out/'FIRST_FAILURE.json',{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
        if not (budget.root/'CANCELLED.json').exists():budget.cancel(str(exc))
        write_new(out/'RETURN_REPORT.json',{'status':'G02_FD_EXECUTION_BLOCKED','new_native_operator_evaluations':budget.used(),
            'new_authorization_consumed':1,'physical_G02_closed':False,'claim_ceiling':old.BINDING['claim_ceiling']})
        raise
    finally:
        if pool is not None:pool.shutdown(wait=False,cancel_futures=True)
        # The dedicated supervisor reaps this run's process group on failure.
