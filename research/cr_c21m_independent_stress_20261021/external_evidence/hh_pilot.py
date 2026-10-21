"""Run the declared PR147 control slice; no benchmark and no historical HH rerun."""
from __future__ import annotations
# Set before importing the numerical owner, including in spawned workers.
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse,concurrent.futures as cf,fcntl,hashlib,json,multiprocessing,platform,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path
from bridge import make_grid,run_case,verify_donor
from resources import LeasePool
HERE=Path(__file__).resolve().parent

def digest(b):return hashlib.sha256(b).hexdigest()
def encoded(data):return (json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def write_new(path,data):
    path=Path(path);tmp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex)
    try:
        with tmp.open('xb') as f:f.write(encoded(data));f.flush();os.fsync(f.fileno())
        os.link(tmp,path)
    finally:tmp.unlink(missing_ok=True)

def identity():
    import numpy,scipy
    lock=verify_donor()
    return dict(schema='PHYS74_PILOT_IDENTITY_V1',files={n:digest((HERE/n).read_bytes()) for n in ('bridge.py','resources.py','pilot.py','DONOR_LOCK.json')},
        donor=lock,python=sys.version,numpy=numpy.__version__,scipy=scipy.__version__,
        frame='normal orthonormal',geometry='non-tilted LRS Bianchi I',HH_R10='OFF',
        rtol=3e-11,atol=3e-13,points=81,benchmark_campaign=False)

def check_existing(path,pin,request):
    if not path.exists():return None
    data=json.loads(path.read_text());payload=data['result']
    if data['identity_sha256']!=pin or payload['request']!=request or digest(encoded(payload))!=data['result_sha256']:
        raise ValueError('existing result identity/content mismatch: '+str(path))
    return payload

def main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--max-cpus',type=int,default=64);ap.add_argument('--memory-gib',type=float,default=128.)
    ap.add_argument('--reserve-gib',type=float,default=16.);ap.add_argument('--job-gib',type=float,default=1.)
    ap.add_argument('--lease-dir',type=Path,default=Path('/tmp/rei-bianchi-cooperative-leases'))
    ap.add_argument('--admission-wait-seconds',type=float,default=120.)
    ap.add_argument('--run',action='store_true');args=ap.parse_args(argv)
    if args.max_cpus<1 or args.memory_gib<=0 or args.reserve_gib<0 or args.job_gib<=0 or args.admission_wait_seconds<0:ap.error('invalid resource option')
    ident=identity();pin=digest(encoded(ident))
    requests=[dict(case_id=f'case-{i:03}',Sigma0_signed=s,Pi0_signed=p,points=81,rtol=3e-11,atol=3e-13) for i,(s,p) in enumerate(make_grid())]
    if not args.run:
        print(json.dumps(dict(status='PLAN_ONLY',identity_sha256=pin,cases=len(requests),
            max_cpus=args.max_cpus,memory_gib=args.memory_gib,reserve_gib=args.reserve_gib,
            no_foreign_process_veto=True,no_foreign_signals=True,no_benchmarks=True,HH_R10='OFF'),indent=2));return 0
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    (out/'cases').mkdir(exist_ok=True);(out/'invocations').mkdir(exist_ok=True)
    with (out/'run.lock').open('a+') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            print('SAME_OUTPUT_ALREADY_RUNNING: no duplicate execution');return 2
        ip=out/'IDENTITY.json'
        if ip.exists():
            if ip.read_bytes()!=encoded(ident):raise ValueError('output identity mismatch; use a distinct output directory')
        else:write_new(ip,ident)
        pending=[];reused=[];done=[];errors=[];events=[]
        for r in requests:
            if check_existing(out/'cases'/f"{r['case_id']}.json",pin,r) is None:pending.append(r)
            else:reused.append(r['case_id'])
        pool=LeasePool(args.lease_dir,max_cpus=args.max_cpus,memory_gib=args.memory_gib,reserve_gib=args.reserve_gib,job_gib=args.job_gib)
        futures={};idle_since=time.monotonic();peak=0
        invocation=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8]
        with cf.ProcessPoolExecutor(max_workers=pool.cap,mp_context=multiprocessing.get_context('spawn')) as executor:
            try:
                while pending or futures:
                    while pending and len(futures)<pool.cap:
                        lease,observation=pool.acquire(pending[0]['case_id'])
                        if lease is None:break
                        r=pending.pop(0)
                        try:f=executor.submit(run_case,r)
                        except BaseException:pool.release(lease);raise
                        futures[f]=(r,lease);events.append(dict(case=r['case_id'],**observation));peak=max(peak,len(futures))
                    if futures:
                        complete,_=cf.wait(futures,timeout=.5,return_when=cf.FIRST_COMPLETED)
                        for f in complete:
                            r,lease=futures.pop(f)
                            try:
                                result=f.result()
                                write_new(out/'cases'/f"{r['case_id']}.json",dict(identity_sha256=pin,result_sha256=digest(encoded(result)),result=result))
                                done.append(r['case_id'])
                            except Exception as exc:errors.append(dict(case=r['case_id'],type=type(exc).__name__,message=str(exc)))
                            finally:pool.release(lease)
                        idle_since=time.monotonic()
                    elif pending:
                        if time.monotonic()-idle_since>=args.admission_wait_seconds:break
                        time.sleep(.5)
            finally:
                # Only our submitted work is joined; no peer process is signalled.
                for f,(r,lease) in list(futures.items()):
                    try:f.result()
                    finally:pool.release(lease)
        receipt=dict(schema='PHYS74_PILOT_EXECUTION_V1',invocation=invocation,
            utc=datetime.now(timezone.utc).isoformat(),host=platform.node(),identity_sha256=pin,
            status='COMPLETE_PRELIMINARY_CONTROL' if not pending and not errors else 'PARTIAL',
            total_requested=len(requests),new_completed=len(done),reused=len(reused),failed=errors,
            pending=[r['case_id'] for r in pending],peak_concurrent_cases=peak,admissions=events,
            other_sessions_are_not_veto=True,cooperative_leases_are_advisory=True,
            benchmark_runs=0,HH_R10='OFF',continuum_certified=False,HHe_feedback=False)
        write_new(out/'invocations'/f'{invocation}.json',receipt)
        print(json.dumps({k:v for k,v in receipt.items() if k!='admissions'},indent=2))
        return 0 if receipt['status']=='COMPLETE_PRELIMINARY_CONTROL' else 3
if __name__=='__main__':raise SystemExit(main())
