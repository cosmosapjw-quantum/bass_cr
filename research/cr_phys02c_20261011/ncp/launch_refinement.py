#!/usr/bin/env python3
"""Bounded NCP coordinator. --plan never imports numerical libraries."""
import os
for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS'):os.environ[k]='1'
import argparse, importlib.util,json,pathlib,signal,subprocess,sys,time,traceback
from ops import sha,verify,probe
STUDY=pathlib.Path(__file__).resolve().parents[1]
SHA='e0445ecbf052a3441f6203f9e0463defcf0c24c0ee018a67e112d338991f47ee'
TASK='CR-PHYS02C-NCP-MATCHED-THIRD-GRID'

def utc():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def provenance():
    files=[STUDY/'state/SCIENTIFIC_CONTRACT.json',STUDY/'ncp/NCP_EXECUTION_CONTRACT.json',STUDY/'ncp/launch_refinement.py',STUDY/'ncp/ops.py',STUDY/'src/coherent_bed.py',STUDY/'tests/run_targeted.py']
    return {'command':sys.argv,'cwd':str(pathlib.Path.cwd()),'python':sys.version,'code_config_identities':{str(x.relative_to(STUDY)):{'bytes':x.stat().st_size,'sha256':sha(x)} for x in files if x.is_file()}}
def load(p):return json.loads(pathlib.Path(p).read_text())
def dump(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def admission():
    if sha(STUDY/'state/SCIENTIFIC_CONTRACT.json')!=SHA:raise ValueError('CONTRACT_SHA_MISMATCH')
    contract=load(STUDY/'state/SCIENTIFIC_CONTRACT.json');dag=load(STUDY/'state/NEXT_DAG.json')
    if dag.get('scientific_contract_sha256')!=SHA or dag.get('inherited_gates')!=contract['inherited_gates']:raise ValueError('DAG_IDENTITY_OR_GLOBAL_GATES_MISMATCH')
    task=next((t for t in dag.get('tasks',[]) if t.get('id')==TASK),None)
    if not task or task.get('status')!='READY' or task.get('max_transport_calls')!=2:raise ValueError('TASK_NOT_READY')
    r=task['independent_review'];p=(STUDY/r['path']).resolve()
    if not p.is_relative_to(STUDY) or sha(p)!=r['sha256']:raise ValueError('REVIEW_PATH_OR_HASH_MISMATCH')
    review=load(p)
    if review.get('decision') not in ('PASS_SCOPED','PROMOTE_SCOPED') or review.get('independent_of_implementation') is not True or review.get('independent_of_candidate_design') is not True:raise ValueError('INDEPENDENT_REVIEW_NOT_ADMITTED')
    # Restore bundle wins if present; otherwise frozen Git FILE_MANIFEST is mandatory.
    repository=STUDY.parents[1];manifestroot=next((x for x in (STUDY,*STUDY.parents) if (x/'BUNDLE_MANIFEST.json').is_file()),None)
    if manifestroot:verified=verify(manifestroot,manifestroot/'BUNDLE_MANIFEST.json')
    else:
        candidate=next((x for x in (STUDY,repository) if (x/'FILE_MANIFEST.json').is_file()),None)
        if candidate is None:raise ValueError('FROZEN_FILE_MANIFEST_MISSING')
        verified=verify(candidate,candidate/'FILE_MANIFEST.json')
    return {'task':task,'payload_verification':verified}

def worker(run):
    result={'start_utc':utc(),'provenance':provenance(),'schema':'cr-phys02c-ncp-result.v1','status':'RUNNING','checks':[],'transport_calls_started':0,'global_gates':load(STUDY/'state/SCIENTIFIC_CONTRACT.json')['inherited_gates'],'prior_science_suites_rerun':0,'scientific_contract_sha256':SHA}
    code=1
    try:
        admission()
        if not probe(run)['admitted']:raise RuntimeError('NCP_RESOURCE_ADMISSION_FAILED')
        if not (run/'RESERVATION.json').is_file():raise RuntimeError('COORDINATOR_RESERVATION_MISSING')
        spec=importlib.util.spec_from_file_location('targeted',STUDY/'tests/run_targeted.py');api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
        def ncpresources(*args,**kwargs):
            r=probe(run);r['threadpools']=api.threadpool_info();r['admitted']=r['admitted'] and all(t['num_threads']==1 for t in r['threadpools']);return r
        api.resources=ncpresources
        if not all(t['num_threads']==1 for t in api.threadpool_info()):raise RuntimeError('ACTUAL_NUMERICAL_THREADS_NOT_ONE')
        result['runtime']={'python':sys.version,'numpy':api.np.__version__,'scipy':api.scipy.__version__,'threadpools':api.threadpool_info()}
        # Changed atomic domain checks only, no inherited suite.
        atomic=api.atomic_checks(result);source=api.cc.ElectronSource()
        dump(run/'CALL_01_RESERVATION.json',{'model':'fullBED','grid':[3200,6400],'state':'RESERVED_BEFORE_BUILD','call_limit':2})
        new=api.run_grid((3200,6400),atomic,source,run,result,'fullBED')
        if any(x['status']=='FAIL' for x in result['checks']):raise RuntimeError('FIRST_NEW_GRID_VALIDATION_FAILURE')
        dump(run/'CALL_02_RESERVATION.json',{'model':'legacy','grid':[3200,6400],'state':'RESERVED_BEFORE_BUILD','call_limit':2})
        old=api.run_grid((3200,6400),api.cc.AtomicData(),source,run,result,'legacy')
        refs=load(STUDY/'ncp/NCP_EXECUTION_CONTRACT.json')['reference_results']
        newold=next(r for r in load(STUDY/refs['fullBED'])['grid_results'] if r['cells']==[1600,3200])
        legacyold=next(r for r in load(STUDY/refs['legacy'])['grid_results'] if r['cells']==[1600,3200])
        meshes=[]
        for label,c,f in [('fullBED',newold,new),('legacy',legacyold,old)]:
            changes={k:api.relative(f['metrics_normalized'][k],c['metrics_normalized'][k]) for k in f['metrics_normalized']}
            passed=all(v<(api.TOL['mesh_cutoff_and_low_boundary_count_relative'] if k in ('cutoff_number','low_cross_number') else api.TOL['mesh_channel_relative']) for k,v in changes.items())
            api.check(result,'TWO_GRID_CHANNEL_CONVERGENCE_'+label,passed,{'relative_changes':changes,'coarse':[1600,3200],'fine':[3200,6400]});meshes.append(changes)
        paired=[]
        def append(group,key,nc,nf,lc,lf):
            dc=nc-lc;df=nf-lf;r=abs(df-dc)/abs(df) if df else None;signs=dc*df>0
            paired.append({'group':group,'observable':key,'delta_4800':dc,'delta_9600':df,'empirical_r':r,'signs_agree':signs,'resolution_status':'EMPIRICALLY_RESOLVED' if r is not None and r<1/3 and signs else ('EXACT_ZERO_DELTA' if dc==df==0 else 'UNRESOLVED')})
        for k in new['metrics_normalized']:append('parent_output_vector_normalized',k,newold['metrics_normalized'][k],new['metrics_normalized'][k],legacyold['metrics_normalized'][k],old['metrics_normalized'][k])
        for tag in new['final']['components']:
            for k in new['final']['components'][tag]:
                if not k.endswith('residual'):append(tag,k,newold['final']['components'][tag][k],new['final']['components'][tag][k],legacyold['final']['components'][tag][k],old['final']['components'][tag][k])
        result['paired_deltas']=paired;result['status']='PASS_SCOPED' if all(x['status']=='PASS_SCOPED' for x in result['checks']) else 'FAIL';code=0 if result['status']=='PASS_SCOPED' else 1
    except Exception:
        result['status']='EXECUTION_FAILED';result['exception']=traceback.format_exc();traceback.print_exc()
    finally:result['actual_exit']=code;result['end_utc']=utc();dump(run/'NUMERICAL_RESULT.json',result)
    return code

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--plan',action='store_true');g.add_argument('--execute',action='store_true');g.add_argument('--worker',action='store_true');p.add_argument('--run-dir');a=p.parse_args()
    if a.worker:
        def timeout_handler(signum,frame):raise TimeoutError('WORKER_3600_SECOND_WALL_BUDGET')
        signal.signal(signal.SIGALRM,timeout_handler);signal.alarm(3600)
        return worker(pathlib.Path(a.run_dir))
    plan={'start_utc':utc(),'provenance':provenance(),'state':'PREPARED_NOT_EXECUTED','resource_probe':probe(STUDY),'task_id':TASK,'maximum_transport_calls':2,'total_wall_budget_s':3600,'grid':[3200,6400],'models_in_order':['fullBED','legacy'],'transport_executed':False}
    try:plan['admission']=admission();plan['admission_status']='READY'
    except Exception as e:plan['admission_status']='HOLD';plan['reason']=repr(e)
    if a.plan:print(json.dumps(plan,indent=2));return 0
    if not a.run_dir:raise ValueError('--run-dir required')
    run=pathlib.Path(a.run_dir).resolve()
    if run.exists():raise ValueError('Use a new run directory; preserve all first failures')
    run.mkdir(parents=True);dump(run/'PLAN_AND_ADMISSION.json',plan)
    if plan['admission_status']!='READY' or not plan['resource_probe']['admitted']:
        dump(run/'ACTUAL_EXIT.json',{'start_utc':plan['start_utc'],'end_utc':utc(),'provenance':provenance(),'status':'HOLD_BEFORE_TRANSPORT','actual_exit':2,'transport_calls_started':0});return 2
    # Exact reference identities must be supplied and frozen by root.
    config=load(STUDY/'ncp/NCP_EXECUTION_CONTRACT.json')
    for model,rel in config['reference_results'].items():
        pin=config['reference_result_identities'][model];q=(STUDY/rel).resolve()
        if q.stat().st_size!=pin['bytes'] or sha(q)!=pin['sha256']:raise ValueError('REFERENCE_IDENTITY_MISMATCH')
    dump(run/'RESERVATION.json',{'maximum_calls':2,'wall_seconds':3600,'nontransferable':True,'state':'RESERVED_BEFORE_PROCESS_START'})
    start=time.monotonic()
    with open(run/'stdout.log','wb') as out,open(run/'stderr.log','wb') as err:
        child=subprocess.Popen([sys.executable,str(pathlib.Path(__file__).resolve()),'--worker','--run-dir',str(run)],stdout=out,stderr=err,start_new_session=True)
        timed=False
        try:code=child.wait(timeout=3600)
        except subprocess.TimeoutExpired:
            timed=True;os.killpg(child.pid,signal.SIGTERM)
            try:code=child.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
    dump(run/'ACTUAL_EXIT.json',{'start_utc':plan['start_utc'],'end_utc':utc(),'provenance':provenance(),'actual_child_exit':code,'coordinator_exit':124 if timed else code,'timeout':timed,'elapsed_seconds':time.monotonic()-start,'status':'ACTUAL_FAILURE' if code else 'AWAITING_INDEPENDENT_ASTRA_REVIEW','resources_end':probe(run)})
    return 124 if timed else code

if __name__=='__main__':
    try:sys.exit(main())
    except Exception:
        actual=traceback.format_exc();traceback.print_exc()
        if '--run-dir' in sys.argv:
            path=pathlib.Path(sys.argv[sys.argv.index('--run-dir')+1])
            if path.is_dir() and not (path/'ACTUAL_EXIT.json').exists():dump(path/'ACTUAL_EXIT.json',{'end_utc':utc(),'provenance':provenance(),'start_utc':load(path/'PLAN_AND_ADMISSION.json').get('start_utc') if (path/'PLAN_AND_ADMISSION.json').exists() else None,'actual_exit':1,'status':'OPERATIONAL_FAILURE','exception':actual,'transport_calls_started':'SEE_ACTUAL_RESULTS_OR_RESERVATIONS; NOT_INFERRED'})
        sys.exit(1)
