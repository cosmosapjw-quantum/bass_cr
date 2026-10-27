"""One bounded C4 process-identity diagnostic; no scientific modules or input replay."""
import os, sys, json, subprocess, resource, hashlib, time, datetime
from pathlib import Path
U=Path(__file__).resolve().parents[1]
E=U/'evidence'
A='c4_pid_diagnostic_v1'
UNIT='CR_PHYS02_PARENT_EVENT_NATIVE25_V1'
def put(p,x):
    with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def stats(pid):
    b=Path(f'/proc/{pid}/stat').read_text();f=b[b.rfind(')')+2:].split()
    return {'requested':pid,'reported_pid':int(b.split(' ',1)[0]),'state':f[0],
            'ppid':int(f[1]),'pgrp':int(f[2]),'session':int(f[3]),'start_ticks':int(f[19])}
def usage():
    a=resource.getrusage(resource.RUSAGE_SELF);b=resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime
intent={'unit':UNIT,'attempt':A,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parent_CPU_hard_s':1,
        'child_CPU_hard_s':1,'wall_timeout_s':2,'preparation_reserve_total_s':4,
        'previous_charged_CPU_s':0.378105,'source_or_scientific_worker':False}
put(E/f'C04_PREPARATION_INTENT_{A}.json',intent)
resource.setrlimit(resource.RLIMIT_CPU,(1,1))
r={'schema':'CR_PARENT_PID_DIAGNOSTIC_V1','unit':UNIT,'attempt':A,'status':'failed',
   'scientific_worker_started':False,'old_science_replay':0,'intent':intent}
p=None;cleanup=True
try:
    r['self']={'os_pid':os.getpid(),'os_ppid':os.getppid(),'os_pgrp':os.getpgrp(),
               'os_sid':os.getsid(0),'proc_self':stats('self'),'proc_numeric':stats(os.getpid())}
    child="import os,time,json; print(json.dumps({'os_pid':os.getpid(),'os_ppid':os.getppid(),'os_pgrp':os.getpgrp(),'os_sid':os.getsid(0)}),flush=True); time.sleep(0.3)"
    p=subprocess.Popen([sys.executable,'-c',child],start_new_session=True,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    cleanup=False
    r['Popen_pid']=p.pid
    r['proc_child_initial']=stats(p.pid)
    r['initial_poll']=p.poll()
    out,err=p.communicate(timeout=2)
    cleanup=True
    r['child_exit_code']=p.returncode;r['child_stdout']=out;r['child_stderr']=err
    r['status']='completed' if p.returncode==0 else 'failed'
except BaseException as exc:r['failure']={'type':type(exc).__name__,'message':str(exc)}
finally:
    if p is not None and p.poll() is None:
        p.kill()
        try:p.wait(timeout=1);cleanup=True
        except BaseException as exc:r['cleanup_failure']=repr(exc)
r.update(terminal_debit=cleanup,cpu_accounting_complete=cleanup,cleanup_complete=cleanup,
         debit_kind='CUMULATIVE_SAME_ATTEMPT',debit_sequence=0,
         measured_preparation_CPU_s=usage(),conservative_tail_CPU_s=.05)
r['charged_preparation_CPU_s']=r['measured_preparation_CPU_s']+.05
put(E/f'C04_HOST_ADMISSION_{A}.json',r)
print(json.dumps(r))
raise SystemExit(0 if r['status']=='completed' and cleanup else 2)
