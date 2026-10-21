"""Create-only, resumable independent-physical-case PR147 sandbox pilot."""
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[_k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import argparse,csv,hashlib,json,multiprocessing as mp,platform,queue,sys,time,traceback
from pathlib import Path
from resources import admit,capacity,cpu_set,snapshot
HERE=Path(__file__).resolve().parent

def write_new(p,value):
    with Path(p).open('x') as f:json.dump(value,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')

def signature():
    from adapter import verify_source,digest,SETTINGS,S_GRID,P_GRID
    code={p:hashlib.sha256((HERE/p).read_bytes()).hexdigest() for p in ('adapter.py','runner.py','resources.py')}
    manifest={'schema':'C21L_PILOT_V1','source':verify_source(),'code':code,'settings':SETTINGS,'S_grid':S_GRID,'P_grid':P_GRID,'scientific_status':'EXPLORATORY_PRELIMINARY','global_error_bound':None}
    return manifest,digest(manifest)

def case_grid():
    from adapter import S_GRID,P_GRID
    return [('s%02d_p%02d'%(i,j),s,p) for i,s in enumerate(S_GRID) for j,p in enumerate(P_GRID)]

def resume_status(directory,identity):
    directory=Path(directory)
    if not directory.exists():return 'MISSING'
    reservation=json.loads((directory/'RESERVATION.json').read_text()) if (directory/'RESERVATION.json').exists() else {}
    if reservation.get('identity')!=identity:raise RuntimeError('CASE_RESUME_IDENTITY_MISMATCH:'+str(directory))
    p=directory/'RESULT.json'
    if not p.exists():return 'INCOMPLETE'
    r=json.loads(p.read_text())
    if r.get('identity')!=identity:raise RuntimeError('CASE_RESULT_IDENTITY_MISMATCH')
    if r['status']!='COMPLETE':return r['status']
    h=directory/'history.npz'
    if not h.exists() or hashlib.sha256(h.read_bytes()).hexdigest()!=r['history_sha256']:raise RuntimeError('COMPLETED_HISTORY_MISSING_OR_CHANGED')
    return 'COMPLETE'

def worker(cpu,tasks,results):
    os.sched_setaffinity(0,{cpu})
    import numpy as np, scipy
    from adapter import make_template,solve_case
    try:template=make_template()
    except BaseException:
        results.put({'kind':'WORKER_INIT_FAILED','cpu':cpu,'error':traceback.format_exc()});return
    while True:
        job=tasks.get()
        if job is None:return
        key,s,p,directory,identity=job;directory=Path(directory)
        try:
            rec,hist=solve_case(template,s,p)
            with (directory/'history.npz').open('xb') as f:np.savez_compressed(f,**hist)
            rec.update(status='COMPLETE',case_id=key,identity=identity,history_sha256=hashlib.sha256((directory/'history.npz').read_bytes()).hexdigest(),runtime={'pid':os.getpid(),'cpu':cpu,'affinity':sorted(os.sched_getaffinity(0)),'numpy':np.__version__,'scipy':scipy.__version__,'python':platform.python_version(),'threads':{k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')},'executor_identity':'native Python multiprocessing spawn; model identity not observable'})
            write_new(directory/'RESULT.json',rec)
            results.put({'case_id':key,'status':'COMPLETE','cpu':cpu})
        except BaseException:
            error=traceback.format_exc()
            with (directory/'failure.txt').open('x') as f:f.write(error)
            write_new(directory/'RESULT.json',{'case_id':key,'identity':identity,'status':'FAILED','error':error,'cpu':cpu,'global_error_bound':None})
            results.put({'case_id':key,'status':'FAILED','cpu':cpu})

def aggregate(out,statuses,run_id):
    rows=[]
    for key,s,p in case_grid():
        row={'case_id':key,'status':statuses[key],'requested_S0':s,'requested_P0':p}
        file=out/'cases'/key/'RESULT.json'
        if statuses[key]=='COMPLETE' and file.exists():
            r=json.loads(file.read_text());m=r['mapping'];d=r['diagnostics']
            row.update(actual_S0=m['actual']['S'],actual_P0=m['actual']['P'],Sigma0=m['actual']['Sigma_F'],Pi0=m['actual']['Pi_F'],Sigma_half0=m['actual']['Sigma_half'],Pi_half0=m['actual']['Pi_half'],k=m['k_gamma'],S_end=r['endpoint']['S'],P_end=r['endpoint']['P'],Sigma_end=r['endpoint']['Sigma_F'],Pi_end=r['endpoint']['Pi_F'],Sigma_half_end=r['endpoint']['Sigma_half'],Pi_half_end=r['endpoint']['Pi_half'],H_end=r['endpoint']['H'],a_end=r['endpoint']['a'],nfev=r['nfev'],solver_wall_s=r['solver_wall_s'],**d)
        rows.append(row)
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (out/('endpoints_'+run_id+'.csv')).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
    counts={s:list(statuses.values()).count(s) for s in sorted(set(statuses.values()))}
    summary={'status':'COMPLETED_EXPLORATORY_PILOT' if counts.get('COMPLETE')==81 else 'PARTIAL_EXPLORATORY_PILOT','completion_counts':counts,'requested_cases':81,'global_error_bound':None,'NCP_execution':False,'performance_benchmark':False,'scientific_admission':'PENDING_PARENT_REVIEW','statuses':statuses}
    write_new(out/('SUMMARY_'+run_id+'.json'),summary)
    return summary

def run(args):
    manifest,identity=signature();out=args.out.resolve()
    if args.plan_only:
        s=snapshot();plan={'identity':identity,'case_count':81,'snapshot':s,'capacity':capacity(s,args.workers,cpu_set(args.cpu_list) if args.cpu_list else None),'execution':'NOT_RUN'}
        print(json.dumps(plan,indent=2));return 0
    if not 0<args.timeout_seconds<=86400:raise ValueError('bounded timeout required')
    if args.resume:
        if not out.is_dir():raise RuntimeError('RESUME_OUTPUT_MISSING')
        if json.loads((out/'MANIFEST.json').read_text())!={'identity':identity,'manifest':manifest}:raise RuntimeError('CAMPAIGN_MANIFEST_IDENTITY_MISMATCH')
    else:
        out.mkdir(parents=True,exist_ok=False);write_new(out/'MANIFEST.json',{'identity':identity,'manifest':manifest});(out/'cases').mkdir()
    # Cooperative coordinator exclusion also prevents concurrent resume into one output.
    import fcntl
    lock=(out/'coordinator.lock').open('a+b')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:lock.close();raise RuntimeError('OUTPUT_COORDINATOR_BUSY')
    statuses={};pending=[]
    for key,s,p in case_grid():
        status=resume_status(out/'cases'/key,identity)
        if status=='MISSING':pending.append((key,s,p))
        else:statuses[key]=status
    run_id=time.strftime('%Y%m%dT%H%M%S')+'_%d'%os.getpid()
    if not pending:
        summary=aggregate(out,statuses,run_id);print(json.dumps(summary));lock.close();return 0 if summary['completion_counts'].get('COMPLETE')==81 else 2
    handles=[];processes=[];orig=set(os.sched_getaffinity(0));started=time.monotonic();failure=None
    try:
        plan,handles=admit(args.workers,args.lease_dir,cpu_set(args.cpu_list) if args.cpu_list else None)
        write_new(out/('RESOURCES_'+run_id+'.json'),plan)
        os.sched_setaffinity(0,{plan['coordinator_cpu']})
        ctx=mp.get_context('spawn');tasks=ctx.Queue();results=ctx.Queue()
        for cpu in plan['worker_cpus']:
            process=ctx.Process(target=worker,args=(cpu,tasks,results));process.start();processes.append(process)
        for key,s,p in pending:
            directory=out/'cases'/key;directory.mkdir(exist_ok=False)
            write_new(directory/'RESERVATION.json',{'case_id':key,'identity':identity,'requested_S0':s,'requested_P0':p,'automatic_retry':False})
            tasks.put((key,s,p,str(directory),identity));statuses[key]='INCOMPLETE'
        for process in processes:tasks.put(None)
        remaining=len(pending)
        while remaining and time.monotonic()-started<args.timeout_seconds:
            try:msg=results.get(timeout=.25)
            except queue.Empty:
                if not any(p.is_alive() for p in processes):failure='ALL_WORKERS_EXITED_WITH_PENDING_CASES';break
                continue
            if msg.get('kind')=='WORKER_INIT_FAILED':failure=msg;break
            statuses[msg['case_id']]=msg['status'];remaining-=1
            print(json.dumps({'completed_this_attempt':len(pending)-remaining,'total_pending':len(pending),**msg}),flush=True)
        if remaining and failure is None:failure='CAMPAIGN_TIMEOUT'
    except BaseException:
        failure=traceback.format_exc()
    finally:
        for p in processes:p.join(timeout=1)
        for p in processes:
            if p.is_alive():p.terminate()
        for p in processes:p.join(timeout=3)
        for p in processes:
            if p.is_alive():p.kill();p.join(timeout=3)
        os.sched_setaffinity(0,orig)
        for cpu,f in handles:f.close()
        # Accept all independently completed raw results even if another worker failed.
        for key,s,p in case_grid():
            state=resume_status(out/'cases'/key,identity)
            statuses[key]='NOT_RUN' if state=='MISSING' else state
        summary=aggregate(out,statuses,run_id)
        write_new(out/('RETURN_'+run_id+'.json'),{'failure':failure,'wall_seconds':time.monotonic()-started,'worker_exit_codes':[p.exitcode for p in processes],'summary':summary,'global_error_bound':None})
        lock.close()
    print(json.dumps(summary,indent=2));return 0 if summary['completion_counts'].get('COMPLETE')==81 else 2

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=HERE/'runs/pilot81');ap.add_argument('--workers',type=int,default=4);ap.add_argument('--cpu-list');ap.add_argument('--lease-dir',default='/tmp/bass_cpu_leases');ap.add_argument('--timeout-seconds',type=float,default=600);ap.add_argument('--resume',action='store_true');ap.add_argument('--plan-only',action='store_true');args=ap.parse_args();return run(args)
if __name__=='__main__':raise SystemExit(main())
