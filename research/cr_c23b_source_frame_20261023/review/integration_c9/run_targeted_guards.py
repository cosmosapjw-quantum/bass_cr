"""Create-only independent review, coordinator2 and worker4, locked CPU lease."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,hashlib,importlib.util,json,os,subprocess,sys,time

BASE=Path(__file__).resolve().parent
PROJECT=BASE.parents[1]
RUN=BASE/sys.argv[1]
RUN.mkdir(exist_ok=False)
CONTROL=Path('/workspace/scratch/30d955d9ea43/c23a_external_sources_20261023/recovery/restored/repository/research/cr_c23a_external_supply_20261023/runtime/resource_control.py')
spec=importlib.util.spec_from_file_location('c23b_review_resource',CONTROL)
control=importlib.util.module_from_spec(spec);spec.loader.exec_module(control)
LEASE_DIR=Path('/tmp/rei-bianchi-cooperative-leases');LEASE_DIR.mkdir(exist_ok=True)
LEASE=LEASE_DIR/(RUN.name+'.json')
START=time.perf_counter()
def write(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def utc():return datetime.now(timezone.utc).isoformat()
released=False; owned=False; child=None
try:
    with (LEASE_DIR/'leases.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        others=[]
        for p in LEASE_DIR.glob('*.json'):
            data=json.loads(p.read_text())
            if data.get('schema')!='C21_CPU_LEASES_V1' or not isinstance(data.get('leases'),list):
                raise RuntimeError('Unknown cooperative lease encoding: '+p.name)
            for entry in data['leases']:
                cpus=entry.get('cpus')
                if not isinstance(cpus,list) or any(type(c) is not int or c<0 for c in cpus):
                    raise RuntimeError('Unknown CPU encoding: '+p.name)
                if set(cpus)&{2,4}:raise RuntimeError('Assigned review CPUs already leased')
            others.append({'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'content':data})
        count,admission=control.choose_workers(1,requested=1,per_worker_mib=128,coordinator_mib=128,protected_cpus=(0,1,3,5,6,7,8,55))
        admission['fixed_assignment']={'coordinator':2,'worker':4}
        admission['other_leases']=others
        write(RUN/'RESOURCE_ADMISSION.json',admission)
        if count!=1 or set(admission['eligible_idle_cpus'])!={2,4}:
            raise RuntimeError('Review CPU/resource admission blocked')
        lease={'schema':'C21_CPU_LEASES_V1','leases':[{'owner':'/root/c23b_frame_theory','cpus':[2,4],'run_id':RUN.name,'pid':os.getpid(),'created_utc':utc(),'native_threads_per_worker':1,'cpu55_protected':True}]}
        write(LEASE,lease);owned=True
        write(RUN/'LEASE_START.json',lease)
    snapshot=RUN/'source_snapshot';snapshot.mkdir()
    pins=[]
    for name in ('boost_kernel.py','primary_source_assembly.py'):
        src=PROJECT/'implementation'/name;data=src.read_bytes()
        with (snapshot/name).open('xb') as f:f.write(data)
        pins.append({'path':str(src),'snapshot':'source_snapshot/'+name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    for src,name in ((PROJECT/'source_providers/runs/c23b_pw19_spectral_source_20261023_v1/CASES.json','provider_cases.json'),(PROJECT/'implementation/runs/c23b_boost_and_source_20261023_v2/PRIMARY_SOURCE_ASSEMBLY.json','saved_v2_assemblies.json')):
        data=src.read_bytes()
        with (snapshot/name).open('xb') as f:f.write(data)
        pins.append({'path':str(src),'snapshot':'source_snapshot/'+name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    for src in (BASE/'guard_review_worker.py',BASE/'run_targeted_guards.py',CONTROL):
        data=src.read_bytes();pins.append({'path':str(src),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    write(RUN/'SOURCE_PINS.json',pins)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    for k in control.THREAD_ENV:env[k]='1'
    os.sched_setaffinity(0,{2})
    command=[sys.executable,str(BASE/'guard_review_worker.py'),str(RUN)]
    with (RUN/'stdout.log').open('x') as out,(RUN/'stderr.log').open('x') as err:
        child=subprocess.Popen(command,stdout=out,stderr=err,env=env,preexec_fn=lambda:os.sched_setaffinity(0,{4}))
        try:code=child.wait(timeout=55)
        except subprocess.TimeoutExpired:
            child.kill();child.wait();raise
    write(RUN/'PROCESS_EXIT.json',{'command':command,'exit_code':code,'completed_utc':utc(),'wall_s':time.perf_counter()-START,'coordinator_cpu':2,'worker_cpu':4,'maximum_worker_wall_s':55,'native_threads_per_worker':1})
    print((RUN/'stdout.log').read_text())
    if code:raise RuntimeError('Reviewer worker failed: '+(RUN/'stderr.log').read_text())
except Exception as exc:
    write(RUN/'FAILURE.json',{'class':'EXECUTION_OR_RESOURCE','type':type(exc).__name__,'message':str(exc),'utc':utc()})
    raise
finally:
    if owned:
        with (LEASE_DIR/'leases.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            LEASE.unlink();released=True
        write(RUN/'LEASE_RELEASED.json',{'lease_status':'RELEASED','cpus':[2,4],'utc':utc(),'other_owners_unchanged':True})
