"""Meter this unit's single-process scientific jobs; retain all failed attempts."""
import sys, os, json, math, time, resource, subprocess, signal, hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
job=sys.argv[1]
command=sys.argv[2:]
if not command:raise SystemExit('supply JOB COMMAND ...')
ledger_path=HERE/'evidence/EXECUTIONS.json'
ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {
    'limit_local_scientific_cpu_s':60,'jobs':[],
    'metadata_provider_remote_cpu':'UNKNOWN_NOT_ZERO','all_service_hard_cap_claim':False}
if any(j['id']==job for j in ledger['jobs']):raise SystemExit('job id already exists; inspect evidence')
used=sum(j['charged_cpu_s'] for j in ledger['jobs'])
remaining=60-used
if remaining<2:raise SystemExit('budget cannot admit another job')
soft=max(1,math.floor(remaining)-1)
def limits():resource.setrlimit(resource.RLIMIT_CPU,(soft,soft+1))
before=resource.getrusage(resource.RUSAGE_CHILDREN)
start=time.monotonic(); own=time.process_time()
p=subprocess.Popen(command,cwd=HERE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                   text=True,start_new_session=True,preexec_fn=limits)
timed_out=False
try:output,_=p.communicate(timeout=45)
except subprocess.TimeoutExpired:
    timed_out=True;os.killpg(p.pid,signal.SIGKILL);output,_=p.communicate()
after=resource.getrusage(resource.RUSAGE_CHILDREN)
cpu=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)
supervisor=time.process_time()-own
log=HERE/'evidence'/str(job+'.log');log.write_text(output)
pins={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
      for name in ('frontier.py','test_frontier.py','run_bounded.py')}
record={'id':job,'command':command,'cwd':str(HERE),'python':sys.version,
        'exit_code':p.returncode,'status':'completed' if p.returncode==0 else 'failed',
        'wall_s':time.monotonic()-start,'worker_cpu_s':cpu,'supervisor_cpu_s':supervisor,
        'charged_cpu_s':cpu+supervisor,'cpu_soft_limit_s':soft,'timeout':timed_out,
        'source_sha256':pins,'log':str(log.relative_to(HERE))}
ledger['jobs'].append(record)
ledger['charged_local_cpu_s']=used+record['charged_cpu_s']
ledger['budget_result']='pass_scoped' if ledger['charged_local_cpu_s']<=60 else 'fail'
ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')
print(output,end='');print(json.dumps(record))
raise SystemExit(p.returncode if p.returncode>=0 else 128-p.returncode)
