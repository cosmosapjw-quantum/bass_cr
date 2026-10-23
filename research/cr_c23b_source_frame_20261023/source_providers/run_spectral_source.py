"""Cooperative create-only runner for the new C23B spectral source audit."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
COORDINATOR=6
WORKER=3
THREAD_KEYS=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')
for key in THREAD_KEYS:os.environ[key]='1'

def write(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')

def digest(path):
    b=path.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def worker(run,guard=False):
    os.sched_setaffinity(0,{WORKER})
    identity=json.loads((run/'SOURCE_IDENTITY.json').read_text())
    for name,expected in identity['files'].items():
        if digest(ROOT/name)!=expected:raise RuntimeError('SOURCE_CHANGED:'+name)
    if guard:
        from targeted_atomic_guard import validate
    else:
        from validate_spectral_source import validate
    result=validate(run)
    result['actual_affinity']=sorted(os.sched_getaffinity(0))
    result['thread_environment']={k:os.environ[k] for k in THREAD_KEYS}
    write(run/'WORKER_RECEIPT.json',result)
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result['status']=='PASS_SCOPED' else 2

def dispatch(run_id,guard=False):
    if not run_id or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for c in run_id):raise ValueError('CREATE_ONLY_RUN_ID_REQUIRED')
    from resource_control import observe_resources
    observed=observe_resources()
    run=ROOT/'runs'/run_id;run.mkdir(parents=True,exist_ok=False)
    write(run/'RESOURCE_OBSERVED.json',observed)
    spare,memory=observed.get('cpu_quota_spare_cores'),observed.get('memory_available_bytes')
    if not {COORDINATOR,WORKER}.issubset(os.sched_getaffinity(0)) or spare is None or memory is None or not observed.get('memory_observation_complete') or spare<1.2 or memory<768*1024**2:
        write(run/'BLOCKED.json',{'status':'NOT_RUN_RESOURCE_BLOCKED','new_ODE':0});raise RuntimeError('RESOURCE_NOT_ADMITTED')
    lease_dir=Path('/tmp/rei-bianchi-cooperative-leases');lease_dir.mkdir(exist_ok=True)
    lease_path=lease_dir/(run_id+'.json')
    with (lease_dir/'leases.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);seen=[]
        for path in lease_dir.glob('*.json'):
            doc=json.loads(path.read_text());entries=doc.get('leases',[doc])
            if not isinstance(entries,list) or any(not isinstance(x,dict) or 'cpus' not in x for x in entries):raise RuntimeError('UNKNOWN_LEASE_ENCODING:'+path.name)
            for item in entries:
                if not isinstance(item['cpus'],list) or any(type(c) is not int or c<0 for c in item['cpus']):raise RuntimeError('UNKNOWN_CPU_ENCODING:'+path.name)
                if {COORDINATOR,WORKER}&set(item['cpus']):raise RuntimeError('CPU_LEASE_CONFLICT:'+path.name)
            seen.append({'path':str(path),**digest(path)})
        lease={'schema':'C21_CPU_LEASES_V1','leases':[{'owner':run_id,'cpus':[COORDINATOR,WORKER],'pid':os.getpid()}]}
        write(lease_path,lease);write(run/'LEASE.json',dict(lease,observed_other_leases=seen,protected_cpu55=True,native_threads=1,coordinator_cpu=COORDINATOR,worker_cpu=WORKER))
    try:
        os.sched_setaffinity(0,{COORDINATOR})
        files=['spectral_photo_source.py','validate_spectral_source.py','run_spectral_source.py','resource_control.py','CONTRACT.json']
        if guard:files.append('targeted_atomic_guard.py')
        files+=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'data').glob('*')) if p.is_file()]
        files+=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'taira_v1_0_0/cloudy_formatted_data/pw19').glob('*.out'))]
        pins={name:digest(ROOT/name) for name in files}
        write(run/'SOURCE_IDENTITY.json',{'files':pins,'source_identity_sha256':hashlib.sha256(json.dumps(pins,sort_keys=True,separators=(',',':')).encode()).hexdigest()})
        with (run/'INPUT.json').open('xb') as f:f.write((ROOT/'CONTRACT.json').read_bytes())
        command=[sys.executable,str(Path(__file__).resolve()),'--worker',str(run)]
        if guard:command.append('--guard')
        proc=subprocess.run(command,env=os.environ.copy(),capture_output=True,text=True,timeout=60)
        with (run/'WORKER_STDOUT.txt').open('x') as f:f.write(proc.stdout)
        with (run/'WORKER_STDERR.txt').open('x') as f:f.write(proc.stderr)
        write(run/'DISPATCH_COMPLETE.json',{'returncode':proc.returncode,'worker_timeout_s':60,'cpu55_used':False})
        print(proc.stdout)
        if proc.returncode:print(proc.stderr,file=sys.stderr)
        return proc.returncode
    finally:
        with (lease_dir/'leases.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if lease_path.exists() and json.loads(lease_path.read_text())==lease:lease_path.unlink()
        write(run/'LEASE_RELEASED.json',{'owner':run_id,'released_utc':datetime.now(timezone.utc).isoformat()})

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run-id');parser.add_argument('--worker',type=Path);parser.add_argument('--guard',action='store_true');args=parser.parse_args()
    sys.exit(worker(args.worker,args.guard) if args.worker else dispatch(args.run_id,args.guard))
