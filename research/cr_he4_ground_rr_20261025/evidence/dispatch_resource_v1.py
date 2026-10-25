"""Create-only one-worker launcher; historical budgets are immutable provenance."""
import argparse,datetime,hashlib,json,os,resource,signal,subprocess,sys,time
from pathlib import Path

THREADS=['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS']

def writej(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def snapshot(r):
    cg=Path('/sys/fs/cgroup');st={k:int(v) for k,v in (x.split() for x in (cg/'memory.stat').read_text().splitlines())}
    cur=int((cg/'memory.current').read_text());maximum=int((cg/'memory.max').read_text())
    clean=max(0,st.get('inactive_file',0)-st.get('file_dirty',0)-st.get('file_writeback',0))
    avail=max(0,maximum-cur)+clean-r['memory_reserve_bytes']
    return {'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'affinity':sorted(os.sched_getaffinity(0)),'cpu_max':(cg/'cpu.max').read_text().strip(),
      'memory_max_bytes':maximum,'memory_current_bytes':cur,'clean_inactive_file_bytes':clean,
      'memory_reserve_bytes':r['memory_reserve_bytes'],'memory_available_after_reserve':avail,
      'memory_admitted':avail>=r['RLIMIT_AS_bytes'],'memory_events':(cg/'memory.events').read_text(),
      'CPU55_present':55 in os.sched_getaffinity(0),'external_NCP':'UNOBSERVED'}

def run(unit,runid,mode):
    c=json.loads((unit/'inputs/CONFIG.json').read_text());r=dict(c['resources'])
    key={'controls':'test','primary':'primary','review':'review','plot':'plot'}[mode]
    expected=c[key+'_run_id'];
    if runid!=expected:raise ValueError('RUN_ID_MISMATCH')
    if mode in ['primary','review','plot']:
        review=json.loads((unit/'review/R6_THEORY.json').read_text())
        if 'PASS' not in str(review.get('status',review.get('decision',''))):raise ValueError('R6_PASS_REQUIRED')
    out=unit/'runs'/runid;out.mkdir(parents=True,exist_ok=False)
    here=unit/'implementation';lease=here/'.he4_task_lease';leased=False;started=False;rc=None;err=None;command=None
    status='FAILED_RETAINED';start=time.monotonic();cpu0=time.process_time();before=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu=r[key+'_cpu_s'];wall=r['wall_s'];worker=r['reviewer_cpu'] if mode=='review' else r['worker_cpu']
    try:
        with lease.open('x') as f:json.dump({'pid':os.getpid(),'run_id':runid,'mode':mode},f)
        leased=True;state=snapshot(r);writej(out/'RESOURCE_ADMISSION.json',state)
        if not state['memory_admitted']:raise RuntimeError('MEMORY_ADMISSION_REJECTED')
        if not {worker,r['coordinator_cpu']}.issubset(state['affinity']) or worker==r['coordinator_cpu'] or worker==55:raise RuntimeError('CPU_ADMISSION_REJECTED')
        quota,period=state['cpu_max'].split()
        if quota!='max' and int(quota)/int(period)<2:raise RuntimeError('COORDINATOR_AND_WORKER_QUOTA_REQUIRED')
        receipts=[json.loads(p.read_text()) for p in sorted((unit/'runs').glob('*/DISPATCH_RECEIPT.json'))]
        used=sum(v['worker_cpu_s']+v['coordinator_cpu_s'] for v in receipts)
        if used+cpu>r['new_unit_total_cpu_s']:raise RuntimeError('NEW_UNIT_CPU_CEILING')
        os.sched_setaffinity(0,{r['coordinator_cpu']});src=out/'EXECUTED_SOURCE';src.mkdir();pins=[]
        sources=sorted(here.glob('*.py'))
        if mode=='review':sources.append(unit/'review/c9_independent.py')
        for p in sources:
            b=p.read_bytes();(src/p.name).open('xb').write(b)
            pins.append({'path':str(p.relative_to(unit)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
        for filename in ['CONFIG.json','INPUT_MANIFEST.json']:(src/filename).open('xb').write((unit/'inputs'/filename).read_bytes())
        script={'controls':'controls.py','primary':'primary.py','review':'c9_independent.py','plot':'plot_saved.py'}[mode]
        command=[sys.executable,'-B',str(src/script),'--unit',str(unit),'--output',str(out),'--run-id',runid]
        writej(out/'PRE_EXECUTION.json',{'run_id':runid,'mode':mode,'source_pins':pins,'command':command,
          'CPU_limit_s':cpu,'wall_limit_s':wall,'RLIMIT_AS_bytes':r['RLIMIT_AS_bytes'],
          'worker_cpu':worker,'coordinator_cpu':r['coordinator_cpu'],'native_threads':1,
          'new_unit_already_charged_cpu_s':used,'new_unit_ceiling_cpu_s':30,
          'historical_known_lineage_cpu_s':r['inherited_known_lineage_cpu_s'],
          'separate_C23E_cpu_s':r['separate_C23E_lineage_cpu_s'],'historical_allowance_reused':False,
          'role':'independent_review' if mode=='review' else 'delegated_implementation_executor'})
        env=os.environ.copy();env.update({k:'1' for k in THREADS});env['PYTHONDONTWRITEBYTECODE']='1';env['MPLCONFIGDIR']=str(out/'mpl_config')
        def limits():
            os.sched_setaffinity(0,{worker});resource.setrlimit(resource.RLIMIT_AS,(r['RLIMIT_AS_bytes'],r['RLIMIT_AS_bytes']));resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:
            p=subprocess.Popen(command,cwd=src,env=env,stdout=stdout,stderr=stderr,preexec_fn=limits,start_new_session=True);started=True
            try:rc=p.wait(timeout=wall)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGTERM)
                try:rc=p.wait(timeout=1)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
                raise RuntimeError('OWNED_CHILD_WALL_LIMIT')
        status='PASS' if rc==0 else 'FAILED_RETAINED'
    except Exception as ex:err={'type':type(ex).__name__,'message':str(ex)}
    finally:
        if leased:lease.unlink()
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        rec={'schema':'CR_HE4_BOUNDED_DISPATCH_V1','run_id':runid,'mode':mode,'status':status,
          'error':err,'child_started':started,'returncode':rc,'command':command,
          'worker_cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
          'worker_peak_RSS_KiB':after.ru_maxrss if started else None,'coordinator_cpu_s':time.process_time()-cpu0,
          'wall_s':time.monotonic()-start,'CPU_limit_s':cpu,'wall_limit_s':wall,
          'historical_known_lineage_cpu_s':r['inherited_known_lineage_cpu_s'],
          'separate_C23E_cpu_s':r['separate_C23E_lineage_cpu_s'],'historical_allowance_reused':False,
          'global_remaining':None,'currency':None,'EXECUTION':status,'PUBLICATION':'ROOT_OWNED',
          'BACKUP':'ROOT_PENDING','DAG':'N5_PARTIAL_OPEN_N6_N7_GATED'}
        writej(out/'DISPATCH_RECEIPT.json',rec)
    print(json.dumps({'output':str(out),**rec}));return 0 if status=='PASS' else 1

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--mode',choices=['controls','primary','review','plot'],required=True);a=p.parse_args();raise SystemExit(run(a.unit.resolve(),a.run_id,a.mode))
