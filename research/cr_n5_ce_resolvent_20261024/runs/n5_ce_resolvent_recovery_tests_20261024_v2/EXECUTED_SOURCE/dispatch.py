"""New recovery-v2 create-only bounded dispatcher. No remote operations."""
import argparse,datetime,hashlib,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
MIB=1024**2
INHERITED=19.728051114
THREADS=['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS']
def writej(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def snapshot():
    cg=Path('/sys/fs/cgroup');st=dict((k,int(v)) for k,v in (x.split() for x in (cg/'memory.stat').read_text().splitlines()));current=int((cg/'memory.current').read_text());maximum=int((cg/'memory.max').read_text());clean=max(0,st.get('inactive_file',0)-st.get('file_dirty',0)-st.get('file_writeback',0));available=max(0,maximum-current)+clean-64*MIB
    procs=[]
    for p in Path('/proc').iterdir():
        if p.name.isdigit():
            try:
                name=(p/'comm').read_text().strip()
                if any(x in name for x in ['python','rust','cargo','gcc','worker']):procs.append({'pid':int(p.name),'comm':name})
            except (FileNotFoundError,PermissionError):pass
    return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'memory_current':current,'memory_max':maximum,'memory_stats':{k:st.get(k) for k in ['anon','file','inactive_file','file_dirty','file_writeback','kernel','slab','pagetables']},'memory_events':(cg/'memory.events').read_text(),'clean_inactive_file_reclaimable':clean,'reclaimable_cache_reserve':64*MIB,'available_after_reserve':available,'memory_admitted':available>=512*MIB,'affinity':sorted(os.sched_getaffinity(0)),'cpu_max':(cg/'cpu.max').read_text().strip(),'processes':procs}
def limits(cpu):
    os.sched_setaffinity(0,{0});resource.setrlimit(resource.RLIMIT_AS,(512*MIB,512*MIB));resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def run(unit,runid,mode):
    here=unit/'implementation';out=unit/'runs'/runid;out.mkdir(parents=True,exist_ok=False);lease=here/'.recovery_v2_lease';leased=False;started=False;rc=None;error=None;status='FAILED_RETAINED';start=time.monotonic();cpu0=time.process_time();before=resource.getrusage(resource.RUSAGE_CHILDREN);cpu,wall=(10,30) if mode=='test' else (30,60)
    try:
        with lease.open('x') as f:json.dump({'pid':os.getpid(),'run_id':runid,'mode':mode},f)
        leased=True;state=snapshot();writej(out/'RESOURCE_ADMISSION.json',state)
        if not state['memory_admitted']:raise RuntimeError('MEMORY_ADMISSION_REJECTED')
        if not {0,8}.issubset(state['affinity']):raise RuntimeError('DECLARED_CPU_UNAVAILABLE')
        os.sched_setaffinity(0,{8});pins=[];src=out/'EXECUTED_SOURCE';src.mkdir()
        for p in sorted(here.glob('*.py')):
            data=p.read_bytes();(src/p.name).open('xb').write(data);pins.append({'path':str(p.relative_to(unit)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        for name in ['CASE_RECOVERY_V2.json','INPUT_MANIFEST_V2.json']:(src/name).open('xb').write((unit/'inputs'/name).read_bytes())
        writej(out/'PRE_EXECUTION.json',{'run_id':runid,'mode':mode,'cpu_limit_s':cpu,'wall_limit_s':wall,'RLIMIT_AS_bytes':512*MIB,'coordinator_cpu':8,'worker_cpu':0,'native_threads':1,'source_pins':pins,'case_sha256':hashlib.sha256((unit/'inputs/CASE_RECOVERY_V2.json').read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((unit/'inputs/INPUT_MANIFEST_V2.json').read_bytes()).hexdigest(),'inherited_known_worker_cpu_s':INHERITED,'requested_model':'gpt-6.1-sol','observed_runtime_model':'UNOBSERVED'})
        command=[sys.executable,'-B',str(here/('tests.py' if mode=='test' else 'primary.py')),'--output',str(out)]
        if mode=='science':command+=['--unit',str(unit),'--run-id',runid]
        env=os.environ.copy();env.update({k:'1' for k in THREADS});env['PYTHONDONTWRITEBYTECODE']='1'
        with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:
            p=subprocess.Popen(command,cwd=here,env=env,stdout=stdout,stderr=stderr,preexec_fn=lambda:limits(cpu),start_new_session=True);started=True
            try:rc=p.wait(timeout=wall)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGTERM)
                try:rc=p.wait(timeout=1)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
                raise RuntimeError('OWNED_WORKER_WALL_LIMIT')
        status='PASS' if rc==0 else 'FAILED_RETAINED'
    except Exception as e:error={'type':type(e).__name__,'message':str(e)}
    finally:
        if leased:lease.unlink()
        after=resource.getrusage(resource.RUSAGE_CHILDREN);receipt={'schema':'N5_RESOLVENT_RECOVERY_DISPATCH_V2','run_id':runid,'mode':mode,'status':status,'error':error,'child_started':started,'returncode':rc,'worker_cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'worker_peak_RSS_KiB':after.ru_maxrss if started else None,'coordinator_cpu_s':time.process_time()-cpu0,'wall_s':time.monotonic()-start,'inherited_known_worker_cpu_s':INHERITED,'global_spend':None,'remaining':None,'currency':None,'requested_model':'gpt-6.1-sol','observed_runtime_model':'UNOBSERVED','EXECUTION':status,'PUBLICATION':'ROOT_OWNED','BACKUP':'ROOT_PENDING','DAG':'N5_PARTIAL_OPEN_N6_N7_NOT_ACTIVATED'};writej(out/'DISPATCH_RECEIPT.json',receipt)
    print(json.dumps({'output':str(out),**receipt}));return 0 if status=='PASS' else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--mode',choices=['test','science'],required=True);a=p.parse_args();raise SystemExit(run(a.unit.resolve(),a.run_id,a.mode))
