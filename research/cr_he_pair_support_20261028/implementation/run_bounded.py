#!/usr/bin/env python3
"""Serial, separately charged research jobs; metadata/provider CPU is excluded explicitly."""
import sys,os,time,json,hashlib,math,resource,subprocess,signal,fcntl,shutil,datetime
from pathlib import Path

U=Path(os.environ.get('CR_UNIT_ROOT',str(Path(__file__).resolve().parents[1]))).resolve()
UNIT='CR_PHYS02_HE_PAIR_SUPPORT_V1'
def write(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n');os.replace(tmp,p)
def ident(p):
    b=p.read_bytes();return {'path':str(p.relative_to(U)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
    run_id,mode,reservation=sys.argv[1],sys.argv[2],float(sys.argv[3])
    assert mode in ('probe','primary','controls','independent','plot','targeted')
    assert reservation>=2 and all(c.isalnum() or c in '_-' for c in run_id)
    out=U/'runs'/run_id;out.mkdir(exist_ok=False)
    lock=(U/'BUDGET.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    budget=json.loads((U/'BUDGET.json').read_text());assert budget['unit']==UNIT and budget['cap_cpu_s']==40
    assert budget.get('science_closed', False) is False and budget.get('additional_science_allowance_cpu_s') != 0, 'UNIT_SCIENCE_CLOSED'
    assert not any(x.get('status')=='RESERVED' for x in budget['attempts'])
    assert budget['charge_cpu_s']+reservation<=40
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    rec={'run_id':run_id,'mode':mode,'status':'RESERVED','reservation_cpu_s':reservation,'utc':started,'worker_memory_limit_bytes':536870912,'native_threads':1}
    budget['attempts'].append(rec.copy());write(U/'BUDGET.json',budget);write(out/'RESERVATION.json',rec)
    files=sorted((U/'implementation').glob('*.py'));manifest=[ident(p) for p in files]
    snap=out/'EXECUTED_SOURCE';snap.mkdir()
    for p in files:shutil.copyfile(p,snap/p.name)
    write(out/'SOURCE_MANIFEST.json',manifest)
    environment=os.environ.copy()
    for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS']:environment[name]='1'
    environment.update(CR_UNIT_ROOT=str(U),CR_BOUNDED_OUTDIR=str(out),MPLCONFIGDIR=str(out/'mplcache'),PYTHONDONTWRITEBYTECODE='1')
    hard=int(math.floor(reservation-.5))
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(hard,hard))
        resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
    if mode=='probe':
        command=[sys.executable,'-c','import sys,numpy,resource,json; print(json.dumps({"runtime":"PYTHON_PASS","numpy":numpy.__version__,"python":sys.version.split()[0],"max_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))']
    else:command=[sys.executable,str(U/'implementation'/(mode+'.py')),'--out-dir',str(out)]
    write(out/'COMMAND.json',{'argv':command,'cwd':str(U),'limits':{'cpu_hard_s':hard,'wall_timeout_s':50,'memory_bytes':536870912},'single_owned_process_group':True})
    proc=None;code=None;failure=None;t0=time.monotonic();stdout=stderr=''
    try:
        proc=subprocess.Popen(command,cwd=U,env=environment,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True,preexec_fn=limits)
        try:stdout,stderr=proc.communicate(timeout=50)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGKILL);stdout,stderr=proc.communicate();failure='OWNED_PROCESS_WALL_TIMEOUT'
        code=proc.returncode
    except Exception as e:failure=type(e).__name__+': '+str(e)
    (out/'stdout.txt').write_text(stdout);(out/'stderr.txt').write_text(stderr)
    self_usage=resource.getrusage(resource.RUSAGE_SELF);child_usage=resource.getrusage(resource.RUSAGE_CHILDREN)
    measured=self_usage.ru_utime+self_usage.ru_stime+child_usage.ru_utime+child_usage.ru_stime
    rounded=math.ceil(measured*1e6)/1e6;tail=.05;charge=round(rounded+tail,6)
    unchanged=manifest==[ident(p) for p in files]
    result_path=out/'RESULT.json';scientific=None
    if result_path.exists():
        try:scientific=json.loads(result_path.read_text()).get('status')
        except Exception:scientific='UNPARSEABLE'
    success=code==0 and failure is None and unchanged and charge<=reservation and (mode=='probe' or scientific in ('PASS','PASS_SCOPED','PASS_SCOPED_PAIR_SUPPORT'))
    rec.update(status='PASS' if success else 'FAIL',exit_code=code,failure=failure,measured_cpu_s=measured,worker_cpu_s=child_usage.ru_utime+child_usage.ru_stime,coordinator_cpu_s=self_usage.ru_utime+self_usage.ru_stime,tails_cpu_s=tail,rounding_tail_cpu_s=rounded-measured,charged_cpu_s=charge,wall_s=time.monotonic()-t0,source_unchanged=unchanged,scientific_status=scientific,maximum_worker_rss_kib=child_usage.ru_maxrss)
    budget['attempts'][-1]=rec;budget['charge_cpu_s']=round(sum(x['charged_cpu_s'] for x in budget['attempts']),6);budget['measured_cpu_s']=sum(x['measured_cpu_s'] for x in budget['attempts']);budget['tails_cpu_s']=sum(x['tails_cpu_s']+x['rounding_tail_cpu_s'] for x in budget['attempts']);budget['status']='OPEN';budget['remaining_cpu_s']=round(40-budget['charge_cpu_s'],6);budget['all_runtime_attempts_pass']=all(x['status']=='PASS' for x in budget['attempts']);budget['preventive_aggregate_hard_cap_proof']=False
    write(out/'RECEIPT.json',rec);write(U/'BUDGET.json',budget)
    print(json.dumps(rec));sys.exit(0 if success else 2)

if __name__=='__main__':main()
