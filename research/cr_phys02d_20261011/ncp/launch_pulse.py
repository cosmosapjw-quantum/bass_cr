#!/usr/bin/env python3
"""Standard-library admission and bounded coordinator. --plan imports no numerics."""
import os
for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS'):os.environ[k]='1'
import argparse, hashlib, importlib.util, json, pathlib, signal, subprocess, sys, time, traceback, uuid
from ops import sha,verify,probe
STUDY=pathlib.Path(__file__).resolve().parents[1]
SCI='bc05614e9812f616c4a4bb45805e4c0359a171813f7329794b0c10c3bf37dde2'
NCP='9dd8b098d828fcad5ddd5138afd29e9dce4805e26fbac897bd4c9a07779e8ff9'
INPUT='fdc6eaa7813ff22585668a5e0fe629ca7e7b3912cbcfb68050a30542f9a09978'
DEP='dd64b4b187ea9b12c147e2d6d50d71b2f94c61e43a2ad1d77bc4b486b6ca68f3'
TASK='CR-PHYS02D-NCP-PULSE-RESPONSE'
def load(p):return json.loads(pathlib.Path(p).read_text())
def write(p,x):
    with pathlib.Path(p).open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def utc():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def admission():
    for rel,digest in [('state/SCIENTIFIC_CONTRACT.json',SCI),('ncp/NCP_EXECUTION_CONTRACT.json',NCP),('inputs/INPUT_IDENTITIES.json',INPUT)]:
        if sha(STUDY/rel)!=digest:raise ValueError('EXACT_IDENTITY_MISMATCH '+rel)
    dependency_manifest=STUDY/'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'
    if sha(dependency_manifest)!=DEP:raise ValueError('DEPENDENCY_MANIFEST_IDENTITY_MISMATCH')
    dependency_verification=verify(STUDY.parents[1],dependency_manifest)
    inputs=load(STUDY/'inputs/INPUT_IDENTITIES.json')['inputs']
    for name,item in inputs.items():
        p=STUDY/item['path']
        if p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:raise ValueError('INPUT_MISMATCH '+name)
    if sha(STUDY/'ncp/ops.py')!=inputs['NCP_resource_adapter']['sha256']:raise ValueError('OPS_COPY_MISMATCH')
    root=next((p for p in (STUDY,*STUDY.parents) if (p/'BUNDLE_MANIFEST.json').is_file()),None)
    if root:payload=verify(root,root/'BUNDLE_MANIFEST.json')
    else:
        root=next((p for p in (STUDY,STUDY.parents[1]) if (p/'FILE_MANIFEST.json').is_file()),None)
        if root is None:raise ValueError('FROZEN_FILE_MANIFEST_MISSING')
        payload=verify(root,root/'FILE_MANIFEST.json')
    dag=load(STUDY/'state/NEXT_DAG.json')
    if dag.get('scientific_contract_sha256')!=SCI or dag.get('inherited_gates')!=load(STUDY/'state/SCIENTIFIC_CONTRACT.json')['inherited_gates']:raise ValueError('DAG_IDENTITY_MISMATCH')
    task=next((t for t in dag['tasks'] if t['id']==TASK),{})
    if task.get('status')!='READY' or task.get('max_transport_calls')!=2 or task.get('grid_cells')!=[3200,6400]:raise ValueError('TASK_NOT_READY')
    reference=task['independent_review'];path=(STUDY/reference['path']).resolve()
    if not path.is_relative_to(STUDY) or sha(path)!=reference['sha256']:raise ValueError('REVIEW_HASH_MISMATCH')
    r=load(path)
    if r.get('decision')!='PASS_SCOPED' or r.get('independent_of_implementation') is not True or r.get('independent_of_candidate_design') is not True or r.get('reviewer_role')!='INDEPENDENT_ASTRA' or r.get('scientific_contract_sha256')!=SCI or r.get('ncp_contract_sha256')!=NCP:raise ValueError('REVIEW_NOT_INDEPENDENT_OR_IDENTITY_MISMATCH')
    reviewed=r.get('reviewed_files',{})
    required=['src/pulse_response.py','ncp/launch_pulse.py','ncp/ops.py','ncp/collect_return.py']
    if any(p not in reviewed for p in required):raise ValueError('REVIEW_CODE_COVERAGE_MISSING')
    for rel,item in reviewed.items():
        p=(STUDY/rel).resolve()
        if not p.is_relative_to(STUDY) or not p.is_file() or p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:raise ValueError('REVIEWED_FILE_MISMATCH '+rel)
    return {'payload_verification':payload,'review_sha256':reference['sha256'],'input_count':len(inputs),'dependency_verification':dependency_verification}
def import_file(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def worker(run,fd):
    # Capability is a private inherited pipe, never a transferable CLI secret.
    with os.fdopen(fd,'r') as f:cap=f.read()
    reservation=load(run/'RESERVATION.json')
    if hashlib.sha256(cap.encode()).hexdigest()!=reservation['capability_sha256'] or os.getppid()!=reservation['coordinator_pid'] or reservation['run_dir']!=str(run):raise ValueError('NONTRANSFERABLE_RESERVATION_FAILED')
    admission()
    import platform,numpy as np,scipy
    from threadpoolctl import threadpool_info
    runtime={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'threadpools':threadpool_info()}
    write(run/'RUNTIME.json',runtime)
    if (runtime['python'],runtime['numpy'],runtime['scipy'])!=('3.12.3','2.4.2','1.17.0') or not runtime['threadpools'] or any(p['num_threads']!=1 for p in runtime['threadpools']):raise ValueError('EXACT_NUMERICAL_RUNTIME_REQUIRED')
    engine=import_file('phys02d_pulse',STUDY/'src/pulse_response.py')
    identities=load(STUDY/'inputs/INPUT_IDENTITIES.json')['inputs'];results=[]
    reference=load(STUDY/identities['paired_9600']['path'])
    for index,model in enumerate(('fullBED','legacy'),1):
        resources=probe(run);write(run/f'RESOURCE_BEFORE_BUILD_{index}.json',resources)
        if not resources['admitted'] or any(p['num_threads']!=1 for p in threadpool_info()):raise ValueError('RESOURCE_OR_THREADS_HOLD')
        write(run/f'BUILD_{index}_RESERVATION.json',{'model':model,'grid':[3200,6400],'state':'RESERVED_BEFORE_BUILD','utc':utc()})
        if model=='fullBED':atomic=import_file('phys02d_atomic',STUDY/identities['inherited_atomic']['path']); cascade=atomic.Cascade(3200,6400,atomic=atomic.AtomicData())
        else:parent=import_file('phys02d_parent',STUDY/identities['inherited_cascade']['path']);cascade=parent.Cascade(3200,6400,atomic=parent.AtomicData())
        data=np.load(STUDY/identities[model+'_9600_npz']['path'],allow_pickle=False)
        fields=load(STUDY/'ncp/NCP_EXECUTION_CONTRACT.json')['NPZ_fields']
        if any(k not in data for k in fields) or not np.array_equal(cascade.E,data['energy_eV']) or data['time_s'].shape!=(2,) or not np.array_equal(data['time_s'],np.array([0.,1e10])) or data['source_vectors'].shape!=(cascade.size,2) or data['birth_tags'].tolist()!=['direct_0p1_10','direct_10_900']:raise ValueError('STORED_SOURCE_GRID_FIELDS_MISMATCH')
        write(run/f'PULSE_{index}_RESERVATION.json',{'model':model,'state':'RESERVED_BEFORE_CALL','samples':17,'birth_columns':2,'utc':utc()})
        result=engine.pulse_response(cascade.G,data['source_vectors'],cascade.n,cascade.ix['heat'],cascade.functionals()[0])
        np.savez(run/f'PULSE_{model}_9600.npz',sample_u=result['sample_u'],pulse_states=result.pop('pulse_states'),integrator_states=result.pop('integrator_states'),energy_eV=cascade.E,source_vectors=data['source_vectors'])
        result['model']=model;result['physical_energy_scale_eV_m3']=float(data['physical_energy_scale_eV_m3']);result['SI_J1']=result['selected']['J1']*result['physical_energy_scale_eV_m3']*1.602176634e-19/1e10;result['SI_J2']=result['selected']['J2']*result['physical_energy_scale_eV_m3']*1.602176634e-19
        rows=reference.get('grid_results',[])
        row=next((r for r in rows if r.get('label')==model and r.get('cells')==[3200,6400]),None)
        if row is None:raise ValueError('SAVED_RAMP_ROW_MAPPING_MISSING')
        residuals={k:abs(result['selected'][field]-row['metrics_normalized'][k])/max(abs(row['metrics_normalized'][k]),1e-300) for k,field in [('heat_power','J1'),('heat','J2')]}
        terminal=np.asarray(data['terminal_yields']); saved_h=terminal[cascade.ix['heat']]
        residuals['terminal']=float(np.max(np.abs(np.array([x['H0'] for x in result['birth_columns']])-saved_h)/np.maximum(np.abs(saved_h),1e-300)))
        saved_metrics=row['metrics_normalized'];saved_R=saved_metrics['heat_power']/saved_metrics['terminal_heat_power'];saved_S=2*saved_metrics['heat']/saved_metrics['terminal_heat_power']
        result['saved_endpoint_cdf_bounds']=engine.check_saved_cdf_bounds(result['sample_u'],result['selected']['cdf'],saved_R,saved_S,{'input_key':'paired_9600',**identities['paired_9600'],'row_label':model,'R_fields':['metrics_normalized.heat_power','metrics_normalized.terminal_heat_power'],'S_fields':['metrics_normalized.heat','metrics_normalized.terminal_heat_power']})
        result['saved_ramp_relative_residuals']=residuals;result['crosscheck_label']='algebraic same-operator check, not independent physical validation'
        write(run/f'RESULT_{model}.json',result)
        if any(x>1e-9 for x in residuals.values()) or not result['saved_endpoint_cdf_bounds']['pass']:raise ArithmeticError('SAVED_RAMP_OR_TERMINAL_MISMATCH')
        results.append(result);del cascade,data,result
    write(run/'NUMERICAL_RESULT.json',{'status':'AWAITING_INDEPENDENT_ASTRA_REVIEW','models':results,'physical_G_builds':2,'pulse_calls':2,'runtime':runtime})
    return 0

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--plan',action='store_true');g.add_argument('--execute',action='store_true');g.add_argument('--collect',action='store_true');g.add_argument('--worker',action='store_true',help=argparse.SUPPRESS);p.add_argument('--run-dir');p.add_argument('--out');p.add_argument('--capability-fd',type=int,help=argparse.SUPPRESS);a=p.parse_args()
    if a.worker:
        if a.capability_fd is None or not a.run_dir:raise ValueError('PRIVATE_COORDINATOR_CAPABILITY_REQUIRED')
        return worker(pathlib.Path(a.run_dir).resolve(),a.capability_fd)
    if a.collect:
        from collect_return import collect
        if not a.run_dir:raise ValueError('--run-dir required')
        print(json.dumps(collect(STUDY,a.run_dir,a.out or STUDY/'evidence/returns'),indent=2));return 0
    coordinator_entry=time.monotonic();coordinator_start_utc=utc()
    plan={'state':'PREPARED_NOT_EXECUTED','utc':utc(),'command':sys.argv,'cwd':str(pathlib.Path.cwd()),'python':sys.version,'physical_G_builds':0,'pulse_calls':0,'resource_probe':probe(STUDY)}
    try:plan['admission']=admission();plan['admission_status']='READY'
    except Exception as e:plan['admission_status']='HOLD';plan['reason']=repr(e)
    if a.plan:print(json.dumps(plan,indent=2));return 0
    entry=coordinator_entry;deadline=entry+3600;start_utc=coordinator_start_utc;child=None;run=None;owned=False;observed_exit=None
    try:
        run=pathlib.Path(a.run_dir).resolve() if a.run_dir else STUDY/'evidence/runs'/('PULSE_'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'_'+uuid.uuid4().hex)
        run.mkdir(parents=True,exist_ok=False);owned=True;write(run/'PLAN_AND_ADMISSION.json',plan)
        if plan['admission_status']!='READY' or not plan['resource_probe']['admitted']:
            code=2;status='HOLD_BEFORE_BUILD'
        else:
            cap=uuid.uuid4().hex+uuid.uuid4().hex
            write(run/'RESERVATION.json',{'coordinator_pid':os.getpid(),'run_dir':str(run),'capability_sha256':hashlib.sha256(cap.encode()).hexdigest(),'state':'RESERVED_BEFORE_CHILD','max_G_builds':2,'max_pulse_calls':2,'wall_s':3600,'utc':utc()})
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
            receipt.update(command=sys.argv,cwd=str(pathlib.Path.cwd()),start_utc=start_utc,end_utc=utc(),elapsed_s=recording_start-entry,observed_child_exit=observed_exit,build_reservations=len(list(run.glob('BUILD_*_RESERVATION.json'))),pulse_reservations=len(list(run.glob('PULSE_*_RESERVATION.json'))),reservation_counts_are_completed_calls=False,deadline_s=3600,receipt_recording_started_after_deadline=recording_start>deadline,receipt_recording_overhead_classification='TERMINAL_RECEIPT_IO_OUTSIDE_CHILD_BUDGET')
            write(run/'ACTUAL_EXIT.json',receipt)
    return code

if __name__=='__main__':
    try:sys.exit(main())
    except Exception:traceback.print_exc();sys.exit(1)
