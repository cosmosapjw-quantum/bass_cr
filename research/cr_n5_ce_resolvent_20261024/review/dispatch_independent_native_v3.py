"""Create-only independent C9 worker; root-owned science lease is shared."""
import datetime,hashlib,json,os,resource,signal,subprocess,sys,time
from pathlib import Path

def write(p,x):
    with p.open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')

def main():
    unit=Path(__file__).resolve().parents[1];primary=unit/'runs/n5_ce_resolvent_native_knot_primary_20261024_v3'
    assert (primary/'RESULT.json').is_file()
    runid='n5_c9_native_knot_binary64_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_v1'
    out=unit/'review/runs'/runid;out.mkdir(parents=True,exist_ok=False)
    lease=unit/'implementation/.recovery_v2_lease';leased=False;child=None;started=False;rc=None;error=None
    before=resource.getrusage(resource.RUSAGE_CHILDREN);t0=time.monotonic();c0=time.process_time()
    try:
        with lease.open('x') as f:json.dump({'pid':os.getpid(),'run_id':runid,'mode':'independent_C9_reference'},f)
        leased=True
        cg=Path('/sys/fs/cgroup');st=dict((k,int(v)) for k,v in (line.split() for line in (cg/'memory.stat').read_text().splitlines()));used=int((cg/'memory.current').read_text());maximum=int((cg/'memory.max').read_text());clean=max(0,st.get('inactive_file',0)-st.get('file_dirty',0)-st.get('file_writeback',0));available=max(0,maximum-used)+clean-64*1024**2
        affinity=sorted(os.sched_getaffinity(0));procs=[]
        for p in Path('/proc').iterdir():
            if p.name.isdigit():
                try:
                    comm=(p/'comm').read_text().strip()
                    if any(k in comm for k in ['python','rust','cargo','gcc','worker']):procs.append({'pid':int(p.name),'comm':comm})
                except (OSError,PermissionError):pass
        resource_state={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'memory_current':used,'memory_max':maximum,'memory_stats':{k:st.get(k) for k in ['anon','file','inactive_file','file_dirty','file_writeback','kernel','slab','pagetables']},'memory_events':(cg/'memory.events').read_text(),'available_after_reclaimable_clean_file_and64MiBreserve':available,'affinity':affinity,'cpu_max':(cg/'cpu.max').read_text(),'processes':procs}
        write(out/'RESOURCE_ADMISSION.json',resource_state)
        assert {1,8}.issubset(affinity),'REQUIRED_CPUS_UNAVAILABLE'
        assert available>=512*1024**2,'MEMORY_NOT_ADMITTED'
        os.sched_setaffinity(0,{8});pins=[]
        paths=[Path(__file__).resolve(),unit/'review/independent_reference_native_v3.py',unit/'FROZEN_CONTRACT.md',unit/'inputs/CASE_NATIVE_KNOT_V3.json',unit/'inputs/INPUT_MANIFEST_V3.json',primary/'PRE_EXECUTION.json',primary/'RESULT.json',primary/'SOURCE_WEIGHTED_RESULTS.json',primary/'FINITE_COMPARISONS.json']
        paths+=sorted(primary.glob('*.npz'))
        for p in paths:
            b=p.read_bytes();pins.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
        (out/'EXECUTED_INDEPENDENT_REFERENCE.py').open('xb').write((unit/'review/independent_reference_native_v3.py').read_bytes())
        write(out/'PRE_EXECUTION.json',{'run_id':runid,'primary_run_id':primary.name,'source_and_input_pins':pins,'precision_digits':80,'binary64_conversion':'Decimal.from_float','planned_cases':2,'planned_direct_probability_solves':4,'planned_energy_reward_solves':4,'planned_time_reward_solves':4,'planned_adjoint_source_solves':6,'native_threads':1,'worker_CPU':1,'coordinator_CPU':8,'CPU_cap_s':9,'wall_cap_s':29,'prior_review_worker_CPU_s':0.6884709999999999,'original_review_CPU_allocation_s':10,'RLIMIT_AS_bytes':512*1024**2,'old_science_replay':0,'provider_import':0,'new_ODE':0,'source_quadrature':0,'rate_quadrature':0})
        env=os.environ.copy();env.update({k:'1' for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS']});env['PYTHONDONTWRITEBYTECODE']='1'
        def limits():
            os.sched_setaffinity(0,{1});resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(9,9));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:
            child=subprocess.Popen([sys.executable,'-B',str(unit/'review/independent_reference_native_v3.py'),'--unit',str(unit),'--primary',str(primary),'--output',str(out)],stdout=stdout,stderr=stderr,env=env,preexec_fn=limits,start_new_session=True);started=True
            try:rc=child.wait(timeout=29)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGTERM)
                try:rc=child.wait(timeout=1)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);rc=child.wait()
                raise RuntimeError('OWNED_REVIEW_WALL_CAP')
    except Exception as e:error={'type':type(e).__name__,'message':str(e)}
    finally:
        if leased:
            assert json.loads(lease.read_text())['run_id']==runid
            lease.unlink()
        after=resource.getrusage(resource.RUSAGE_CHILDREN);record={'schema':'INDEPENDENT_C9_DISPATCH_NATIVE_V3','run_id':runid,'status':'PASS' if started and rc==0 and error is None else 'FAILED_RETAINED','child_started':started,'returncode':rc,'error':error,'worker_CPU_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'worker_peak_RSS_KiB':after.ru_maxrss if started else None,'coordinator_CPU_s':time.process_time()-c0,'wall_s':time.monotonic()-t0,'lease_removed':not lease.exists(),'global_spend':None,'remaining_global_budget':None,'EXECUTION':'INDEPENDENT_REFERENCE_ONLY','PUBLICATION':'NOT_PERFORMED','BACKUP':'ROOT_OWNED','DAG':'FINITE_CHAIN_ACCURACY_REVIEW; frozen grid gate remains separate'}
        write(out/'DISPATCH_RECEIPT.json',record)
    print(json.dumps({'output':str(out),**record}));return 0 if record['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
