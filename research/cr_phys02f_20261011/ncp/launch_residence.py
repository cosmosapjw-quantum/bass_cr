#!/usr/bin/env python3
"""Standard-library admission and bounded coordinator. --plan imports no numerics."""
import os
for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS'):os.environ[k]='1'
import argparse, hashlib, importlib.util, json, pathlib, signal, subprocess, sys, time, traceback, uuid
from ops import sha,verify,probe
STUDY=pathlib.Path(__file__).resolve().parents[1]
SCI='b50c316e91ebea6b1d0e5a43367b1cb31ae8836af328521fb366af9f54e35ccf'
NCP='5c7517dcc08796f61ca811c7a5922622e0a2c5ff9be16312bbb1a768aa7db1f8'
VALIDATION='aa346614c4c444bac423eabd286939a4a1d2db20c0bb8e19281608f0ac778896'
INPUT='4f5a871e3995fa7f18f3dae0e4da8ca1f150814bbb3a6d71e997f6fdeaff3def'
DEP='248ad97e6417c3ba88bcbbfcb662f6fe65464e63eba6183421770ba06d41a341'
TASK='CR-PHYS02F-NCP-ADJOINT-RESIDENCE'
def load(p):return json.loads(pathlib.Path(p).read_text())
def write(p,x):
    with pathlib.Path(p).open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def utc():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
REPO=STUDY.parents[1]
def safe_file(root, rel):
    p=root/rel
    if p.is_symlink() or not p.resolve().is_relative_to(root.resolve()) or not p.is_file():raise ValueError('UNSAFE_OR_MISSING_FILE '+rel)
    return p

def frozen_payload():
    path=STUDY/'FILE_MANIFEST.json'
    if path.is_file():
        m=load(path)
        required=load(STUDY/'ncp/NCP_EXECUTION_CONTRACT.json')['admission']['review_required_code']+list(load(STUDY/'state/CONTRACT_IDENTITY.json'))
        prefix=STUDY.relative_to(REPO).as_posix()+'/'
        if m.get('schema')!='cr-phys02f-file-manifest.v1' or m.get('path_basis')!='repository-root' or any(prefix+rel not in m.get('files',{}) for rel in required):raise ValueError('CURRENT_F_MANIFEST_SCHEMA_ROOT_OR_COVERAGE_MISMATCH')
        return {'path':str(path),'verification':verify(REPO,path)}
    for root in (STUDY,REPO):
        path=root/'BUNDLE_MANIFEST.json'
        if path.is_file():
            m=load(path); unitpath=STUDY.relative_to(REPO).as_posix(); manifest=root/unitpath/'FILE_MANIFEST.json'
            if m.get('schema')=='cr-phys02f-self-contained-bundle.v1' and m.get('new_unit_path')==unitpath and manifest.is_file() and m.get('unit_manifest_sha256')==sha(manifest) and m.get('dependency_manifest_sha256')==DEP:
                return {'path':str(path),'verification':verify(root,path)}
    raise ValueError('CURRENT_F_FROZEN_FILE_MANIFEST_MISSING')

def solve_counts(run):
    reserved=len(list(run.glob('SOLVE_*_RESERVED.json')));completed=len(list(run.glob('SOLVE_*_COMPLETED.json')))
    return {'triangular_solve_reservations':reserved,'completed_triangular_solve_calls':completed,'actual_triangular_solve_calls':completed if reserved==completed else None,'actual_triangular_solve_calls_bounds':[completed,reserved]}

def admission():
    pins={'state/SCIENTIFIC_CONTRACT.json':SCI,'ncp/NCP_EXECUTION_CONTRACT.json':NCP,'state/VALIDATION_CONTRACT.json':VALIDATION,'inputs/INPUT_IDENTITIES.json':INPUT,'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json':DEP}
    for rel,digest in pins.items():
        if sha(safe_file(STUDY,rel))!=digest:raise ValueError('EXACT_IDENTITY_MISMATCH '+rel)
    deps=load(STUDY/'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json')['files']
    inputs=load(STUDY/'inputs/INPUT_IDENTITIES.json')['files']
    if len(deps)!=538 or len(inputs)!=18:raise ValueError('EXACT_MEMBERSHIP_REQUIRED')
    for table in (deps, {v['path']:v for v in inputs.values()}):
        for rel,item in table.items():
            p=safe_file(REPO,rel)
            if p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:raise ValueError('INPUT_OR_DEPENDENCY_MISMATCH '+rel)
    if sha(STUDY/'ncp/ops.py')!=inputs['prior_resource_adapter']['sha256']:raise ValueError('OPS_COPY_MISMATCH')
    payload=frozen_payload()
    dag=load(STUDY/'state/NEXT_DAG.json')
    if dag.get('scientific_contract_sha256')!=SCI or dag.get('inherited_gates')!=load(STUDY/'state/SCIENTIFIC_CONTRACT.json')['inherited_gates']:raise ValueError('DAG_IDENTITY_MISMATCH')
    task=next((t for t in dag['tasks'] if t['id']==TASK),{})
    bounds={'max_G_builds':2,'max_resolvent_blocks':2,'max_triangular_solve_calls':10,'max_pulse_calls':0,'total_wall_s':900,'grid_cells':[3200,6400]}
    if task.get('status')!='READY' or any(task.get(k)!=v for k,v in bounds.items()) or task.get('consumed',False):raise ValueError('TASK_NOT_READY_OR_BUDGET_NOT_FRESH')
    reference=task['independent_review'];path=safe_file(STUDY,reference['path'])
    if sha(path)!=reference['sha256']:raise ValueError('REVIEW_HASH_MISMATCH')
    review=load(path)
    expected={'decision':'PASS_SCOPED','independent_of_implementation':True,'independent_of_candidate_design':True,'independent_of_acceptance':True,'reviewer_role':'INDEPENDENT_ASTRA','scientific_contract_sha256':SCI,'ncp_contract_sha256':NCP,'validation_contract_sha256':VALIDATION,'input_manifest_sha256':INPUT,'dependency_manifest_sha256':DEP}
    if any(review.get(k)!=v for k,v in expected.items()):raise ValueError('REVIEW_NOT_INDEPENDENT_OR_IDENTITY_MISMATCH')
    reviewed=review.get('reviewed_files',{})
    required=load(STUDY/'ncp/NCP_EXECUTION_CONTRACT.json')['admission']['review_required_code']
    if set(required)-set(reviewed):raise ValueError('REVIEW_CODE_COVERAGE_MISSING')
    for rel,item in reviewed.items():
        p=safe_file(STUDY,rel)
        if p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:raise ValueError('REVIEWED_FILE_MISMATCH '+rel)
    return {'payload_verification':payload,'review_sha256':reference['sha256'],'input_count':18,'dependency_count':538}
def import_file(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def numerical_preflight(run=None):
    import platform,numpy as np,scipy
    from threadpoolctl import threadpool_info
    runtime={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'threadpools':threadpool_info()}
    if run is not None:write(run/'RUNTIME.json',runtime)
    if (runtime['python'],runtime['numpy'],runtime['scipy'])!=('3.12.3','2.4.2','1.17.0') or not runtime['threadpools'] or any(p['num_threads']!=1 for p in runtime['threadpools']):raise ValueError('EXACT_NUMERICAL_RUNTIME_REQUIRED')
    ids=load(STUDY/'inputs/INPUT_IDENTITIES.json')['files']
    # Verify all four NPZ whole-byte hashes before any NPZ load.
    for key in ('fullBED_9600_npz','legacy_9600_npz','actual_fullBED_pulse','actual_legacy_pulse'):
        item=ids[key];p=safe_file(REPO,item['path'])
        if p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:raise ValueError('NPZ_WHOLE_FILE_MISMATCH '+key)
    grid=import_file('phys02f_pinned_saved_grid',REPO/ids['saved_grid_adapter']['path'])
    bundles,source_receipt=grid.preflight_saved_inputs(REPO,ids)
    engine=import_file('phys02f_residence',STUDY/'src/residence.py')
    pulses,pulse_receipt=engine.preflight_pulses(REPO,ids,bundles)
    receipt={'sources':source_receipt,'pulse_arrays':pulse_receipt,'runtime':runtime,'physical_G_builds':0,'pulse_calls':0,'expm_calls':0}
    if run is not None:write(run/'INPUT_PREFLIGHT_RECEIPT.json',receipt)
    return grid,engine,bundles,pulses,runtime

def worker(run,fd):
    with os.fdopen(fd,'r') as f:cap=f.read()
    reservation=load(run/'RESERVATION.json')
    if hashlib.sha256(cap.encode()).hexdigest()!=reservation['capability_sha256'] or os.getppid()!=reservation['coordinator_pid'] or reservation['run_dir']!=str(run):raise ValueError('NONTRANSFERABLE_RESERVATION_FAILED')
    admission()
    grid,engine,bundles,pulses,runtime=numerical_preflight(run)
    import numpy as np
    from threadpoolctl import threadpool_info
    ids=load(STUDY/'inputs/INPUT_IDENTITIES.json')['files']
    prior_study=(REPO/ids['prior_inputs']['path']).parents[1]
    prior=load(REPO/ids['prior_inputs']['path'])['inputs'];results=[]
    for index,model in enumerate(('fullBED','legacy'),1):
        resources=probe(run);write(run/f'RESOURCE_BEFORE_BUILD_{index}.json',resources)
        if not resources['admitted'] or any(p['num_threads']!=1 for p in threadpool_info()):raise ValueError('RESOURCE_OR_THREADS_HOLD')
        write(run/f'BUILD_{index}_RESERVATION.json',{'model':model,'state':'RESERVED_BEFORE_BUILD','utc':utc()})
        data=bundles[model]
        key='inherited_atomic' if model=='fullBED' else 'inherited_cascade'
        module=import_file('phys02f_'+model,(prior_study/prior[key]['path']).resolve())
        cascade=grid.make_saved_grid_cascade(module.parent if model=='fullBED' else module,data['energy_eV'],atomic=module.AtomicData())
        identity=grid.operator_identity(cascade)
        # Completion is durable even if the following parity gate fails.
        write(run/f'G_COMPLETION_{index}.json',{'model':model,'state':'COMPLETED_CONSTRUCTOR','utc':utc(),'operator_identity':identity})
        ref=load(REPO/ids['actual_'+model+'_G']['path'])['operator_identity']
        parity=engine.operator_parity(identity,ref)
        write(run/f'G_PARITY_{index}.json',parity)
        engine.structure(cascade.G,cascade.n,cascade.ix['heat'])
        write(run/f'RESOLVENT_{index}_RESERVATION.json',{'model':model,'state':'RESERVED_BEFORE_FIVE_SOLVES','max_solve_calls':5,'utc':utc()})
        def track(state,name):write(run/f'SOLVE_{index}_{name}_{state}.json',{'model':model,'solve':name,'state':state,'utc':utc()})
        arrays,result=engine.diagnostic(cascade.G,data['energy_eV'],data['source_vectors'][:cascade.n],pulses[model]['pulse_states'][-1,:cascade.n],cascade.ix['heat'],on_solve=track)
        result=engine.check_saved(result,load(REPO/ids['actual_'+model+'_result']['path']))
        result['model']=model;result['operator_parity']=parity
        np.savez(run/f'RESIDENCE_{model}_9600.npz',**arrays)
        write(run/f'RESULT_{model}.json',result)
        write(run/f'RESOLVENT_{index}_COMPLETION.json',{'model':model,'state':'COMPLETED_FIVE_SOLVES_AND_CROSSCHECKS','solve_calls':5,'utc':utc()})
        results.append(result);del cascade,arrays
    write(run/'NUMERICAL_RESULT.json',{'status':'AWAITING_INDEPENDENT_ASTRA_REVIEW','models':results,'completed_G_builds':2,'completed_resolvent_blocks':2,'actual_triangular_solve_calls':10,'pulse_calls':0,'expm_calls':0,'runtime':runtime})
    return 0

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--plan',action='store_true');g.add_argument('--preflight',action='store_true');g.add_argument('--execute',action='store_true');g.add_argument('--collect',action='store_true');g.add_argument('--worker',action='store_true',help=argparse.SUPPRESS);p.add_argument('--run-dir');p.add_argument('--out');p.add_argument('--capability-fd',type=int,help=argparse.SUPPRESS);a=p.parse_args()
    if a.worker:
        if a.capability_fd is None or not a.run_dir:raise ValueError('PRIVATE_COORDINATOR_CAPABILITY_REQUIRED')
        return worker(pathlib.Path(a.run_dir).resolve(),a.capability_fd)
    if a.collect:
        from collect_return import collect
        if not a.run_dir:raise ValueError('--run-dir required')
        print(json.dumps(collect(STUDY,a.run_dir,a.out or STUDY/'evidence/returns'),indent=2));return 0
    if a.preflight:
        admission()
        grid,engine,bundles,pulses,runtime=numerical_preflight();receipt={'runtime':runtime,'source_models':list(bundles),'pulse_models':list(pulses),'physical_G_builds':0}
        print(json.dumps(receipt,indent=2));return 0
    coordinator_entry=time.monotonic();coordinator_start_utc=utc()
    plan={'state':'PREPARED_NOT_EXECUTED','utc':utc(),'command':sys.argv,'cwd':str(pathlib.Path.cwd()),'python':sys.version,'physical_G_builds':0,'pulse_calls':0,'resource_probe':{'status':'NOT_PROBED_BY_STDLIB_PLAN'}}
    try:plan['admission']=admission();plan['admission_status']='READY'
    except Exception as e:plan['admission_status']='HOLD';plan['reason']=repr(e)
    if a.plan:print(json.dumps(plan,indent=2));return 0
    entry=coordinator_entry;deadline=entry+900;start_utc=coordinator_start_utc;child=None;run=None;owned=False;observed_exit=None
    try:
        if not a.run_dir or not pathlib.Path(a.run_dir).is_absolute():raise ValueError('FRESH_ABSOLUTE_RUN_DIR_REQUIRED')
        run=pathlib.Path(a.run_dir).resolve()
        if run.is_relative_to(REPO) or run.is_symlink():raise ValueError('RUN_MUST_BE_OUTSIDE_SOURCE')
        run.mkdir(parents=True,exist_ok=False);owned=True;write(run/'PLAN_AND_ADMISSION.json',plan)
        if plan['admission_status']!='READY':
            code=2;status='HOLD_BEFORE_BUILD'
        else:
            cap=uuid.uuid4().hex+uuid.uuid4().hex
            write(run/'RESERVATION.json',{'coordinator_pid':os.getpid(),'run_dir':str(run),'capability_sha256':hashlib.sha256(cap.encode()).hexdigest(),'state':'RESERVED_BEFORE_CHILD','max_G_builds':2,'max_pulse_calls':0,'max_resolvent_blocks':2,'max_triangular_solve_calls':10,'wall_s':900,'utc':utc()})
            readfd,writefd=os.pipe();os.write(writefd,cap.encode());os.close(writefd)
            try:
                with (run/'stdout.log').open('xb') as out,(run/'stderr.log').open('xb') as err:
                    if time.monotonic()>=deadline:raise TimeoutError('COORDINATOR_PREPARATION_EXHAUSTED_DEADLINE')
                    child=subprocess.Popen([sys.executable,__file__,'--worker','--run-dir',str(run),'--capability-fd',str(readfd)],pass_fds=(readfd,),stdout=out,stderr=err,start_new_session=True)
                    try:observed_exit=child.wait(timeout=max(0,deadline-time.monotonic()));code=observed_exit;status='AWAITING_INDEPENDENT_ASTRA_REVIEW' if code==0 else 'FIRST_FAILURE_PRESERVED'
                    except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);observed_exit=child.wait();code=124;status='TIMEOUT'
            finally:os.close(readfd)
        receipt={'status':status,'actual_exit':code}
    except Exception:
        if child is not None and child.poll() is None:
            os.killpg(child.pid,signal.SIGKILL);observed_exit=child.wait()
        receipt={'status':'COORDINATOR_EXCEPTION_FIRST_FAILURE_PRESERVED','actual_exit':1,'exception':traceback.format_exc()};code=1
        if not owned:raise
    finally:
        if owned:
            recording_start=time.monotonic()
            receipt.update(command=sys.argv,cwd=str(pathlib.Path.cwd()),start_utc=start_utc,end_utc=utc(),elapsed_s=recording_start-entry,observed_child_exit=observed_exit,build_reservations=len(list(run.glob('BUILD_*_RESERVATION.json'))),resolvent_reservations=len(list(run.glob('RESOLVENT_*_RESERVATION.json'))),completed_resolvent_blocks=len(list(run.glob('RESOLVENT_*_COMPLETION.json'))),triangular_solve_reservations=len(list(run.glob('SOLVE_*_RESERVED.json'))),completed_triangular_solve_calls=len(list(run.glob('SOLVE_*_COMPLETED.json'))),pulse_calls=0,expm_calls=0,completed_G_builds=len(list(run.glob('G_COMPLETION_*.json'))),reservation_counts_are_completed_calls=False,deadline_s=900,receipt_recording_started_after_deadline=recording_start>deadline,receipt_recording_overhead_classification='TERMINAL_RECEIPT_IO_OUTSIDE_CHILD_BUDGET')
            receipt.update(solve_counts(run))
            write(run/'ACTUAL_EXIT.json',receipt)
    return code

if __name__=='__main__':
    try:sys.exit(main())
    except Exception:traceback.print_exc();sys.exit(1)
