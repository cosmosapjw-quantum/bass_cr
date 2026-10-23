"""Bounded create-only C9 review; six new cell integrals, no producer run."""
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PROVIDER = HERE.parents[1] / 'source_providers'
RUN_ID = 'c23b_provider_independent_c9_20261023_v1'
COORDINATOR, WORKER = 7, 5
THREAD_KEYS = ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
               'BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')
for key in THREAD_KEYS:
    os.environ[key] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

def write(path,obj):
    with path.open('x') as f:
        json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False)
        f.write('\n')

def digest(path):
    b=path.read_bytes()
    return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def main():
    spec=importlib.util.spec_from_file_location('c9_resource_control',PROVIDER/'resource_control.py')
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    observed=module.observe_resources()
    run=HERE/'runs'/RUN_ID
    run.mkdir(parents=True,exist_ok=False)
    write(run/'RESOURCE_OBSERVED.json',observed)
    spare,memory=observed.get('cpu_quota_spare_cores'),observed.get('memory_available_bytes')
    admitted=({COORDINATOR,WORKER}.issubset(os.sched_getaffinity(0))
        and spare is not None and memory is not None
        and observed.get('memory_observation_complete')
        and spare >= 1.2 and memory >= 768*1024**2)
    if not admitted:
        write(run/'BLOCKED.json',{'status':'NOT_RUN_RESOURCE_BLOCKED','new_ODE':0})
        raise RuntimeError('RESOURCE_NOT_ADMITTED')
    leases=Path('/tmp/rei-bianchi-cooperative-leases')
    leases.mkdir(exist_ok=True)
    lease_path=leases/(RUN_ID+'.json')
    with (leases/'leases.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        seen=[]
        for path in leases.glob('*.json'):
            data=json.loads(path.read_text());entries=data.get('leases',[data])
            if not isinstance(entries,list) or any(not isinstance(x,dict) or 'cpus' not in x for x in entries):
                raise RuntimeError('UNKNOWN_LEASE_ENCODING:'+path.name)
            for item in entries:
                if not isinstance(item['cpus'],list) or any(type(c) is not int or c<0 for c in item['cpus']):
                    raise RuntimeError('UNKNOWN_CPU_ENCODING:'+path.name)
                if {COORDINATOR,WORKER} & set(item['cpus']):
                    raise RuntimeError('CPU_LEASE_CONFLICT:'+path.name)
            seen.append({'path':str(path),**digest(path)})
        lease={'schema':'C21_CPU_LEASES_V1','leases':[{'owner':RUN_ID,'cpus':[COORDINATOR,WORKER],'pid':os.getpid()}]}
        write(lease_path,lease)
        write(run/'LEASE.json',dict(lease,observed_other_leases=seen,
            protected_cpu55=True,native_threads=1,coordinator_cpu=COORDINATOR,worker_cpu=WORKER))
    try:
        os.sched_setaffinity(0,{COORDINATOR})
        write(run/'INPUT.json',{'run_id':RUN_ID,'review_script':digest(HERE/'audit_provider.py'),
            'dispatch_script':digest(Path(__file__)),
            'resource_gate':digest(PROVIDER/'resource_control.py'),
            'snapshot_manifest':digest(HERE/'SNAPSHOT_MANIFEST.json'),
            'new_reference_scope':'3 HI cells at z2.479; 6 mp70 count/kinetic integrals',
            'full_case_integrations':0,'producer_runs':0,'new_ODE':0,'historical_reruns':0})
        proc=subprocess.run([sys.executable,str(HERE/'audit_provider.py'),str(run)],
            env=os.environ.copy(),capture_output=True,text=True,timeout=60)
        with (run/'WORKER_STDOUT.txt').open('x') as f:f.write(proc.stdout)
        with (run/'WORKER_STDERR.txt').open('x') as f:f.write(proc.stderr)
        write(run/'DISPATCH_COMPLETE.json',{'returncode':proc.returncode,'timeout_s':60,
            'coordinator_affinity':sorted(os.sched_getaffinity(0)),
            'worker_cpu':WORKER,'cpu55_used':False,
            'finished_utc':datetime.now(timezone.utc).isoformat()})
        print(proc.stdout)
        if proc.returncode:print(proc.stderr,file=sys.stderr)
        return proc.returncode
    finally:
        with (leases/'leases.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if lease_path.exists() and json.loads(lease_path.read_text())==lease:
                lease_path.unlink()
        write(run/'LEASE_RELEASED.json',{'owner':RUN_ID,'released_utc':datetime.now(timezone.utc).isoformat()})

if __name__=='__main__':
    raise SystemExit(main())
