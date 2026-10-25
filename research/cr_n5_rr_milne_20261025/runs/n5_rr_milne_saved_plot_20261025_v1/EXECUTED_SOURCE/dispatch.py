"""Create-only, pinned-source, one-worker bounded launcher. Root owns publication."""
import argparse,datetime,hashlib,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
MIB=1024**2
THREADS=['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS']
def writej(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def snapshot():
    cg=Path('/sys/fs/cgroup');st=dict((k,int(v)) for k,v in (x.split() for x in (cg/'memory.stat').read_text().splitlines()));current=int((cg/'memory.current').read_text());maximum=int((cg/'memory.max').read_text());clean=max(0,st.get('inactive_file',0)-st.get('file_dirty',0)-st.get('file_writeback',0));available=max(0,maximum-current)+clean-64*MIB
    processes=[]
    for p in Path('/proc').iterdir():
      if p.name.isdigit():
       try:
        name=(p/'comm').read_text().strip()
        if any(x in name for x in ['python','rust','cargo','gcc','worker']):processes.append(dict(pid=int(p.name),comm=name))
       except (FileNotFoundError,PermissionError,ProcessLookupError):pass
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),affinity=sorted(os.sched_getaffinity(0)),cpu_max=(cg/'cpu.max').read_text().strip(),memory_current=current,memory_max=maximum,clean_inactive_file_reclaimable=clean,memory_available_after_reserve=available,memory_admitted=available>=512*MIB,memory_events=(cg/'memory.events').read_text(),processes=processes,NCP_runtime='UNOBSERVED',NCP_lease='UNOBSERVED')
def limits(cpu,cfg):
    os.sched_setaffinity(0,{cfg['execution_cpu']});resource.setrlimit(resource.RLIMIT_AS,(cfg['RLIMIT_AS_bytes'],cfg['RLIMIT_AS_bytes']));resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def run(unit,runid,mode):
    c=json.loads((unit/'inputs/CONFIG.json').read_text());r=c['resources'];r['execution_cpu']=r['reviewer_cpu'] if mode=='review' else r['worker_cpu'];names={'test':'test_run_id','science':'primary_run_id','plot':'plot_run_id','review':'review_run_id'}
    if runid!=c[names[mode]]:raise ValueError('RUN_ID_MISMATCH')
    r6=json.loads((unit/'review/R6_THEORY.json').read_text())
    if 'PASS' not in str(r6.get('status',r6.get('decision',''))):raise ValueError('R6_PASS_REQUIRED')
    out=unit/'runs'/runid;out.mkdir(parents=True,exist_ok=False);here=unit/'implementation';lease=here/'.rr_task_lease';leased=False;started=False;rc=None;error=None;status='FAILED_RETAINED';start=time.monotonic();cpu0=time.process_time();before=resource.getrusage(resource.RUSAGE_CHILDREN)
    key={'test':'test','science':'primary','plot':'plot','review':'review'}[mode];cpu=r[key+'_cpu_s'];wall=r[key+'_wall_s']
    try:
        with lease.open('x') as f:json.dump(dict(pid=os.getpid(),run_id=runid,mode=mode,unit=str(unit)),f)
        leased=True;state=snapshot();writej(out/'RESOURCE_ADMISSION.json',state)
        if not state['memory_admitted']:raise RuntimeError('MEMORY_ADMISSION_REJECTED')
        if not {r['execution_cpu'],r['coordinator_cpu']}.issubset(state['affinity']):raise RuntimeError('CPU_ADMISSION_REJECTED')
        # Aggregate prior new-unit worker usage, including failed attempts; never reset.
        charged=[]
        for p in sorted(unit.rglob('DISPATCH_RECEIPT.json')):
            rec=json.loads(p.read_text());charged.append(dict(path=str(p.relative_to(unit)),worker_cpu_s=rec['worker_cpu_s']))
        preflight=unit/'evidence/CODE_PREFLIGHT.json'
        preflight_cpu=json.loads(preflight.read_text()).get('charged_cpu_seconds',0.0) if preflight.exists() else 0.0
        used=sum(v['worker_cpu_s'] for v in charged)+preflight_cpu
        if used+cpu>r['new_unit_total_cpu_s']:raise RuntimeError('AGGREGATE_CPU_ADMISSION_REJECTED')
        os.sched_setaffinity(0,{r['coordinator_cpu']});pins=[];src=out/'EXECUTED_SOURCE';src.mkdir()
        for p in sorted(here.glob('*.py')):
            data=p.read_bytes();(src/p.name).open('xb').write(data);pins.append(dict(path=str(p.relative_to(unit)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
        if mode=='review':
            p=unit/'review/c9_independent.py';data=p.read_bytes();(src/p.name).open('xb').write(data);pins.append(dict(path=str(p.relative_to(unit)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
        for name in ['CONFIG.json','INPUT_MANIFEST.json']:(src/name).open('xb').write((unit/'inputs'/name).read_bytes())
        writej(out/'PRE_EXECUTION.json',dict(run_id=runid,mode=mode,source_pins=pins,CPU_limit_s=cpu,wall_limit_s=wall,RLIMIT_AS_bytes=r['RLIMIT_AS_bytes'],coordinator_cpu=r['coordinator_cpu'],worker_cpu=r['execution_cpu'],native_threads=1,inherited_known_worker_cpu_s=r['inherited_worker_cpu_s'],new_unit_charged_worker_cpu_s=used,charged_attempts=charged,delegated_lower_tier=True,observed_runtime_model='UNOBSERVED'))
        script={'test':'controls.py','science':'primary.py','plot':'plot_saved.py','review':'c9_independent.py'}[mode]
        command=[sys.executable,'-B',str(src/script),'--unit',str(unit),'--output',str(out),'--run-id',runid]
        env=os.environ.copy();env.update({k:'1' for k in THREADS});env['PYTHONDONTWRITEBYTECODE']='1';env['MPLCONFIGDIR']=str(out/'mpl_config')
        with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:
            p=subprocess.Popen(command,cwd=src,env=env,stdout=stdout,stderr=stderr,preexec_fn=lambda:limits(cpu,r),start_new_session=True);started=True
            try:rc=p.wait(timeout=wall)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGTERM)
                try:rc=p.wait(timeout=1)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
                raise RuntimeError('OWNED_WORKER_WALL_LIMIT')
        status='PASS' if rc==0 else 'FAILED_RETAINED'
    except Exception as ex:error=dict(type=type(ex).__name__,message=str(ex))
    finally:
        if leased:lease.unlink()
        after=resource.getrusage(resource.RUSAGE_CHILDREN);receipt=dict(schema='N5_RR_BOUNDED_DISPATCH_V1',run_id=runid,mode=mode,status=status,error=error,child_started=started,returncode=rc,worker_cpu_s=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,worker_peak_RSS_KiB=after.ru_maxrss if started else None,coordinator_cpu_s=time.process_time()-cpu0,wall_s=time.monotonic()-start,inherited_known_worker_cpu_s=r['inherited_worker_cpu_s'],CPU_limit_s=cpu,wall_limit_s=wall,delegated_lower_tier=True,observed_runtime_model='UNOBSERVED',global_spend=None,remaining=None,currency=None,EXECUTION=status,PUBLICATION='ROOT_OWNED',BACKUP='ROOT_PENDING',DAG='N5_PARTIAL_OPEN_N6_N7_NOT_ACTIVATED');writej(out/'DISPATCH_RECEIPT.json',receipt)
    print(json.dumps(dict(output=str(out),**receipt)));return 0 if status=='PASS' else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--mode',choices=['test','science','plot','review'],required=True);a=p.parse_args();raise SystemExit(run(a.unit.resolve(),a.run_id,a.mode))
