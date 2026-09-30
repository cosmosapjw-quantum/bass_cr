"""Eight B0 snapshots only; thin binding to unchanged scientific primitives."""
from __future__ import annotations
import bootstrap_tail
from bootstrap_tail import HERE,REPO,R4C
from pathlib import Path
import hashlib,json,math,os,re,subprocess,sys,time,traceback
import numpy as np
from execution_admission import strict_json,THREAD_KEYS,check_native_build,consume_authorization
from parallel_bridge import GlobalBudget,PlannedQuery,dispatch_bounded,publish_pair,validate_pair
from resource_census import live_resource_census,verify_prior_pool_teardown
from tail_plan_adapter import bind_runtime_plan,snapshot_diagnostics

READY='R4P0_B0_OPERATOR_EXECUTOR_READY__EXPLICIT_NATIVE_AUTH_PENDING'
APPROVAL='YES_I_AUTHORIZE_EIGHT_B0_STATIC_SNAPSHOTS'
BINDING=strict_json(HERE/'BINDING_INPUTS.json')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_new(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:
        json.dump(obj,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())

def binding_plan():
    f=HERE/'fixtures/R4P0'
    return bind_runtime_plan(strict_json(f/'receipts/R4P0_TAIL_PREFLIGHT_CONTRACT.json'),strict_json(f/'inputs/SCIENCE_CONTEXT.json'))

def exact_items(plan):
    if plan!=binding_plan():raise ValueError('exact frozen eight-query runtime plan required')
    return [PlannedQuery(r['runtime_query_id'],r['time_hex'],None,None) for r in plan['queries']]

def validate_scope(proposal,authority,*,approved,unused=True,now=None):
    if not approved:raise PermissionError('R4P0_NATIVE_NOT_AUTHORIZED')
    if not unused:raise PermissionError('authorization already consumed')
    for k in ('execution_commit','execution_tree','source_pins_sha256','query_plan_sha256','binding_inputs_sha256'):
        if proposal.get(k)!=authority[k]:raise ValueError('authority pin mismatch: '+k)
    nonce=proposal.get('authorization_id','')
    if not re.fullmatch(r'R4P0-[A-Za-z0-9_.-]{15,80}',nonce):raise ValueError('fresh R4P0 authorization ID required')
    w=proposal.get('workers');cpus=proposal.get('approved_cpu_list',[])
    if (type(w) is not int or not 1<=w<=8 or proposal.get('hard_max_workers')!=8
        or len(cpus)!=w or len(set(cpus))!=w or any(type(c) is not int or c<0 for c in cpus)
        or proposal.get('worker_ram_bytes')!=1<<30
        or proposal.get('total_worker_ram_cap_bytes')!=w*(1<<30)
        or proposal.get('minimum_live_available_bytes')!=(w+4)*(1<<30)):
        raise ValueError('bounded worker CPU/RAM scope mismatch')
    scope={'resource_sharing_policy':'COOPERATIVE_SHARED_HOST','raw_operator_evaluation_cap':88,
           'operator_query_count':8,'native_parity':'NONE','derivative_fd_queries':0,
           'pilot_queries':0,'transport':False,'numerical_threads':1}
    if any(proposal.get(k)!=v for k,v in scope.items()):raise ValueError('static-only scientific/resource scope mismatch')
    now=time.time() if now is None else now
    wall=proposal.get('wall_seconds');deadline=proposal.get('deadline_unix');grace=proposal.get('termination_grace_seconds')
    if (type(wall) is not int or wall<=0 or not isinstance(deadline,(int,float)) or not math.isfinite(deadline)
        or not now<deadline<=now+wall+1 or type(grace) is not int or not 1<=grace<=120
        or not isinstance(proposal.get('cost_scope'),str) or not proposal['cost_scope'].strip()):
        raise ValueError('explicit unexpired wall/deadline/grace/cost scope required')
    return proposal

def verify_source(pins,root=REPO):
    for n,pin in pins['source_files'].items():
        p=Path(root)/n
        if p.is_symlink() or not p.is_file() or sha(p)!=pin:raise ValueError('pinned source mismatch: '+n)

def verify_inputs(inputs,build):
    inputs=Path(inputs);build=Path(build)
    for n,pin in BINDING['runtime_inputs'].items():
        p=inputs/n
        if p.is_symlink() or not p.is_file() or p.stat().st_size!=pin['bytes'] or sha(p)!=pin['sha256']:raise ValueError('frozen bank/input mismatch: '+n)
    old=strict_json(inputs/'SCIENCE_CONTEXT.json');basis=strict_json(inputs/'BASIS.json')
    if basis['identity']!=BINDING['basis_identity'] or basis['identity']!=old['context']['physics_identity']['basis_identity']:
        raise ValueError('frozen B0 bank identity mismatch')
    plan=binding_plan()
    if plan!=strict_json(HERE/'BOUND_B0_TAIL_QUERY_PLAN.json'):raise ValueError('delivered bound plan mismatch')
    if old!=strict_json(HERE/'fixtures/R4P0/inputs/SCIENCE_CONTEXT.json'):raise ValueError('frozen physics/context mismatch')
    contract=old['context']['contract'];contract={**contract,'screens':plan['active_screens']}
    native=check_native_build(build,contract,REPO/'research/foundation_rebuild/tp2a_analytic_pruning_20260926/code/moment_kernel.cpp')
    if any(native[k]!=v for k,v in BINDING['native'].items()):raise ValueError('frozen native source/library/BUILD mismatch')
    # Stored coefficients only: load_bank never constructs an eigensystem.
    from runtime import load_bank
    bank,record=load_bank(inputs)
    from bass_foundations.two_center import symmetric_channels
    from preflight import registry,bind_bank
    rows=bind_bank(registry('B0'),record['modes'])
    if len(symmetric_channels(bank))!=18 or len(rows)!=18 or record['identity']!=BINDING['basis_identity']:
        raise ValueError('frozen B0 channels/coefficient bank mismatch')
    return contract,plan,native

def execute_plan(plan,out,budget,executor,compute,max_inflight):
    items=exact_items(plan);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    contract=strict_json(HERE/'fixtures/R4P0/inputs/SCIENCE_CONTEXT.json')['context']['contract']
    contract={**contract,'screens':plan['active_screens']}
    by_id={r['runtime_query_id']:r for r in plan['queries']};records={};worker_pids=set()
    def commit(item,value):
        if item.query_id in records:raise ValueError('duplicate query publication')
        task=Path(value['task_dir'])
        rec=publish_pair(task/'runtime_queries',out/'runtime_queries',item,plan['context_id'],contract)
        # Keep qualified matrices BEFORE any postprocessing diagnostic failure.
        with np.load(out/'runtime_queries'/(item.query_id+'.npz'),allow_pickle=False) as f:
            matrices=[np.array(f['selected__'+k]) for k in ('S','H','D')]
        diag=snapshot_diagnostics(*matrices,by_id[item.query_id])
        diag.update(P_selected_at_this_tail_sample=None,Sdot_source='ASSUMED_KINEMATIC_IDENTITY_D_PLUS_D_DAGGER',
                    qualification=strict_json(out/'runtime_queries'/(item.query_id+'.json'))['qualification'],
                    raw_attempts=rec['raw_attempts'])
        write_new(out/'diagnostics'/(item.query_id+'.json'),diag)
        records[item.query_id]=rec;worker_pids.add(value['worker_pid'])
    try:
        dispatch_bounded(items,executor,compute,commit,max_inflight=max_inflight,
            deadline_unix=budget.seed['deadline_unix'],cancelled=lambda:(budget.root/'CANCELLED.json').exists())
        actual_json={x.stem for x in (out/'runtime_queries').glob('*.json')}
        actual_npz={x.stem for x in (out/'runtime_queries').glob('*.npz')}
        if actual_json!=actual_npz or actual_json!=set(by_id):raise ValueError('exact eight-pair canonical coverage mismatch')
        for item in items:validate_pair(out/'runtime_queries',item,plan['context_id'],contract)
        audit={'schema':'BASS_R4P0_STATIC_PROVIDER_AUDIT_V1','completed_queries':8,
               'required_queries':8,'ordered_query_ids':[i.query_id for i in items],
               'raw_attempts':budget.used(),'maximum_raw_attempts':88,
               'worker_pids':sorted(worker_pids),'static_screens_executed':list(plan['active_screens']),
               'independent_derivative_screen_executed':False,'temporal_screen_executed':False,
               'transport_executed':False,'tail_error_bound_certified':False,
               'claim_ceiling':BINDING['claim_ceiling']}
        write_new(out/'PROVIDER_AUDIT.json',audit);return audit
    except BaseException as exc:
        if not (out/'FIRST_FAILURE.json').exists():write_new(out/'FIRST_FAILURE.json',{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
        if not (budget.root/'CANCELLED.json').exists():budget.cancel(str(exc))
        raise

def native_pool(proposal,pins,inputs,build,out,budget):
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing
    from tail_worker import initialize,compute
    return ProcessPoolExecutor(max_workers=proposal['workers'],mp_context=multiprocessing.get_context('spawn'),
        initializer=initialize,initargs=(str(inputs),str(build),pins,str(out),str(budget.root),proposal['approved_cpu_list'],proposal['worker_ram_bytes']))

def request(proposal_path,pins_path,inputs,build,out,*,approved_sha,pool_factory=native_pool,preflight_only=False):
    proposal_path=Path(proposal_path);pins_path=Path(pins_path);out=Path(out)
    proposal=strict_json(proposal_path);pins=strict_json(pins_path)
    nonce_path=Path.home()/'.local/state/bass_r4c/authorizations'/(proposal.get('authorization_id','')+'.json')
    authority={'execution_commit':pins['execution_commit'],'execution_tree':pins['execution_tree'],
               'source_pins_sha256':sha(pins_path),'query_plan_sha256':sha(HERE/'BOUND_B0_TAIL_QUERY_PLAN.json'),
               'binding_inputs_sha256':sha(HERE/'BINDING_INPUTS.json')}
    approved=approved_sha==sha(proposal_path) and os.environ.get('ALLOW_NEW_NATIVE_R4P0')==APPROVAL
    if preflight_only:
        # Validate proposal shape and identity, without treating this as approval.
        validate_scope(proposal,authority,approved=True,unused=not nonce_path.exists())
    else:validate_scope(proposal,authority,approved=approved,unused=not nonce_path.exists())
    bound=binding_plan()
    fixed={'runtime_inputs':BINDING['runtime_inputs'],'basis_identity':BINDING['basis_identity'],
           'research_archive_sha256':BINDING['research_archive_sha256'],'a3_archive_sha256':BINDING['a3_archive_sha256'],
           'basis':'B0','channels':18,'energy_keV_per_u':100,'b_a0':2,'context_id':bound['context_id'],
           'signed_z_a0':[r['z_a0'] for r in bound['queries']],
           'runtime_query_ids':[r['runtime_query_id'] for r in bound['queries']],
           'time_hex':[r['time_hex'] for r in bound['queries']],
           'parent_raw_attempts':0,'automatic_worker_scaling':False}
    if any(proposal.get(k)!=v for k,v in fixed.items()):raise ValueError('approved scientific/input scope mismatch')
    if any(proposal.get('native',{}).get(k)!=v for k,v in BINDING['native'].items()):raise ValueError('approved native pin mismatch')
    if os.path.abspath(sys.executable)!=proposal.get('python_path'):raise ValueError('approved Python executable mismatch')
    for key,path in [('source_pins_path',pins_path),('runtime_inputs_path',inputs),('native_build_path',build)]:
        if str(Path(path).resolve())!=proposal.get(key):raise ValueError('approved local path mismatch: '+key)
    if not preflight_only and str(out.resolve())!=proposal.get('out_path'):raise ValueError('approved output path mismatch')
    verify_source(pins)
    actual_head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
    actual_tree=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^{tree}'],text=True).strip()
    if (actual_head,actual_tree)!=(proposal['execution_commit'],proposal['execution_tree']) or subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True):
        raise ValueError('exact clean execution commit/tree required')
    if sys.version_info<(3,11):raise ValueError('Python>=3.11 required')
    import scipy
    if np.__version__!='2.3.5' or scipy.__version__!='1.17.0' or any(os.environ.get(k)!='1' for k in THREAD_KEYS):raise ValueError('prepared versions/thread limits required')
    if os.environ.get('BASS_ANALYTIC_SOURCE_ROOT',str(REPO))!=str(REPO):raise ValueError('external analytic source override forbidden')
    contract,plan,native=verify_inputs(inputs,build)
    if out.resolve().is_relative_to(REPO) or out.exists():raise ValueError('fresh output outside worktree required')
    out.mkdir(parents=True)
    write_new(out/'PROPOSAL_PIN.json',{'proposal_sha256':sha(proposal_path),'proposal_bytes':proposal_path.stat().st_size,'native_authorized':not preflight_only})
    census=live_resource_census(proposal['approved_cpu_list'],proposal['workers'],proposal['worker_ram_bytes'],
        receipt_path=out/'INITIAL_RESOURCE_CENSUS.json',sharing_policy='COOPERATIVE_SHARED_HOST')
    verify_prior_pool_teardown(set(),run_pgid=os.getpgrp(),receipt_path=out/'INITIAL_OWN_POOL_TEARDOWN.json',settle_seconds=0.)
    admission={**proposal,'proposal_sha256':sha(proposal_path),'native':native,
               'environment':{'python':sys.version,'executable':sys.executable,'numpy':np.__version__,'scipy':scipy.__version__,'threads':{k:os.environ[k] for k in THREAD_KEYS}},
               'cost_limit_enforced_by_code':False,'static_screens':plan['active_screens'],
               'new_authorization_consumed':False,'preflight_only':preflight_only,'live_census_status':census['status']}
    write_new(out/'EXECUTION_ADMISSION.json',admission)
    if preflight_only:return {'status':READY,'new_native_operator_evaluations':0,'new_authorization_consumed':0}
    if not sys.flags.isolated or os.getpgrp()!=os.getpid():raise ValueError('isolated Python and dedicated process group required before consumption')
    consume_authorization(out,{**admission,'new_authorization_consumed':True})
    budget=GlobalBudget.create(out/'GLOBAL_BUDGET',parent_attempts=0,maximum=88,deadline_unix=min(proposal['deadline_unix'],time.time()+proposal['wall_seconds']))
    pool=None
    try:
        pool=pool_factory(proposal,pins,inputs,build,out,budget)
        from tail_worker import compute
        audit=execute_plan(plan,out,budget,pool,compute,proposal['workers'])
        pool.shutdown(wait=True);pool=None
        verify_prior_pool_teardown(set(audit['worker_pids']),run_pgid=os.getpgrp(),receipt_path=out/'FINAL_OWN_POOL_TEARDOWN.json')
        report={'status':'R4P0_B0_EIGHT_STATIC_SNAPSHOTS_COMPLETE__TAIL_GATE_UNRESOLVED',
                'new_native_operator_evaluations':budget.used(),'new_authorization_consumed':1,
                'static_queries':8,'claim_ceiling':BINDING['claim_ceiling']}
        write_new(out/'RETURN_REPORT.json',report);return report
    except BaseException as exc:
        if not (out/'FIRST_FAILURE.json').exists():write_new(out/'FIRST_FAILURE.json',{'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
        if not (budget.root/'CANCELLED.json').exists():budget.cancel(str(exc))
        write_new(out/'RETURN_REPORT.json',{'status':'R4P0_B0_STATIC_EXECUTION_BLOCKED','new_native_operator_evaluations':budget.used(),'new_authorization_consumed':1,'claim_ceiling':BINDING['claim_ceiling']})
        raise
    finally:
        if pool is not None:pool.shutdown(wait=False,cancel_futures=True)
        # This is not a worker-exit receipt: the dedicated supervisor must reap
        # the whole group on failure/deadline and package all partial evidence.
