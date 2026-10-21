"""Focused R1/R2 regression. Actual worker with explicitly labeled solver test double.

No physical ODE solve, performance benchmark, or 81-case rerun.
"""
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[_k]='1'
import argparse,json,multiprocessing as mp,time,traceback,hashlib
from pathlib import Path
import numpy as np
import adapter,runner,resources
HERE=Path(__file__).resolve().parent

def wait_double(template,s,p):
    time.sleep(30)
    raise AssertionError('test should terminate started worker before this returns')

def successful_double(template,s,p):
    return {'test_double':True,'physical_ODE_runs':0,'mapping':{},'diagnostics':{},'endpoint':{}},{'test_double_array':np.array([s,p])}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE/'repair_checks');out=ap.parse_args().out;out.mkdir(exist_ok=False);records=[]
    def check(name,fn):
        try:records.append({'name':name,'status':'PASS','details':fn()});print(name,'PASS',flush=True)
        except BaseException:records.append({'name':name,'status':'FAILED','error':traceback.format_exc()});print(name,'FAILED',flush=True)
    def metadata():
        result={}
        for site,ncp in [('unspecified',None),('sandbox',False),('ncp',True),('other',False)]:
            m=resources.execution_metadata(site);assert m['NCP_execution'] is ncp;assert m['observed_hostname'] and m['observed_platform'];assert 'operator-declared' in m['execution_site_basis'];result[site]=m
        default_sig=runner.signature()[1];sandbox_sig=runner.signature('sandbox')[1];assert default_sig!=sandbox_sig
        assert default_sig!='0090e1549b21b07e46001de2bf9cb2eab9bf0cba87ffe3d4d824ba117fecb44a'
        # CPU/memory restrictions still cap a63-worker NCP request including coordinator.
        snap={'allowed_cpus':list(range(64)),'quota':64.,'memory_limit':128*1024**3,'memory_available':120*1024**3}
        cap=resources.capacity(snap,63);assert 55 not in cap['cpu_candidates'];assert cap['maximum_workers']==62
        assert resources.capacity(dict(snap,quota=4.9),63)['maximum_workers']==3
        return {'sites':result,'default_manifest_identity':default_sig,'sandbox_manifest_identity':sandbox_sig,'synthetic_NCP63_request_admitted_workers':cap['maximum_workers'],'physical_ODE_runs':0}
    check('execution_site_and_CPUplan',metadata)
    def legacy():
        d=out/'old_v1';d.mkdir();runner.write_new(d/'RESERVATION.json',{'identity':'id'})
        assert runner.resume_status(d,'id')=='INCOMPLETE'
        d2=out/'failed';d2.mkdir();runner.write_new(d2/'RESERVATION.json',{'schema':'C21L_CASE_QUEUE_V2','state':'QUEUED','identity':'id'});runner.write_new(d2/'RESULT.json',{'identity':'id','status':'FAILED'})
        assert runner.resume_status(d2,'id')=='FAILED'
        try:runner.resume_status(d,'different')
        except RuntimeError:pass
        else:raise AssertionError('identity mismatch accepted')
        return {'old_v1_reservation_stays_incomplete':True,'failed_never_requeued':True,'mismatched_identity_rejected':True}
    check('legacy_and_failed_state_preservation',legacy)
    def actual_worker():
        plan,handles=resources.admit(1,'/tmp/bass_cpu_leases',execution_site='sandbox')
        runner.write_new(out/'WORKER_CONTROL_RESOURCES.json',plan)
        original_affinity=os.sched_getaffinity(0);processes=[];oldtemplate=adapter.make_template;oldsolve=adapter.solve_case
        try:
            os.sched_setaffinity(0,{plan['coordinator_cpu']});cpu=plan['worker_cpus'][0]
            ctx=mp.get_context('fork');tasks=ctx.Queue();results=ctx.Queue()
            adapter.make_template=lambda:None;adapter.solve_case=wait_double
            cases=[]
            for key in ('started_then_interrupted','queued_then_resumed'):
                d=out/key;d.mkdir();runner.write_new(d/'RESERVATION.json',{'schema':'C21L_CASE_QUEUE_V2','state':'QUEUED','identity':'id','test_double':True});cases.append(d)
            p=ctx.Process(target=runner.worker,args=(cpu,tasks,results,'sandbox'));p.start();processes.append(p)
            for d in cases:tasks.put((d.name,.1,.2,str(d),'id'))
            deadline=time.monotonic()+5
            while not (cases[0]/'STARTED.json').exists() and p.is_alive() and time.monotonic()<deadline:time.sleep(.01)
            assert (cases[0]/'STARTED.json').exists();p.terminate();p.join(3);assert not p.is_alive()
            assert runner.resume_status(cases[0],'id')=='INCOMPLETE';assert runner.resume_status(cases[1],'id')=='NOT_STARTED'
            original_reservation=(cases[1]/'RESERVATION.json').read_bytes()
            # Requeue only known-not-started case into a fresh real worker.
            adapter.solve_case=successful_double;tasks2=ctx.Queue();results2=ctx.Queue()
            q=ctx.Process(target=runner.worker,args=(cpu,tasks2,results2,'sandbox'));q.start();processes.append(q)
            tasks2.put((cases[1].name,.1,.2,str(cases[1]),'id'));tasks2.put(None)
            message=results2.get(timeout=5);q.join(3);assert q.exitcode==0 and message['status']=='COMPLETE'
            assert runner.resume_status(cases[1],'id')=='COMPLETE';assert runner.resume_status(cases[0],'id')=='INCOMPLETE'
            assert (cases[1]/'RESERVATION.json').read_bytes()==original_reservation
            r=json.loads((cases[1]/'RESULT.json').read_text());assert r['test_double'] and r['physical_ODE_runs']==0
            assert r['runtime']['execution_site']=='sandbox' and r['runtime']['NCP_execution'] is False and r['runtime']['observed_hostname']
            return {'actual_processes':2,'first_exit':p.exitcode,'resumed_exit':q.exitcode,'interrupted_case':'INCOMPLETE_preserved_not_retried','queued_case':'COMPLETE_after_known_unstarted_resume','test_double':True,'physical_ODE_runs':0,'cpu':cpu}
        finally:
            for p in processes:
                if p.is_alive():p.terminate();p.join(3)
            adapter.make_template=oldtemplate;adapter.solve_case=oldsolve;os.sched_setaffinity(0,original_affinity)
            for cpu,handle in handles:handle.close()
    check('actual_worker_queued_restart_test_double',actual_worker)
    final={'status':'PASS' if all(x['status']=='PASS' for x in records) else 'FAILED','checks':records,'physical_ODE_runs':0,'original_81_results_modified':False,'global_error_bound':None}
    runner.write_new(out/'REPAIR_CHECKS.json',final);print(json.dumps(final,indent=2));return 0 if final['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
