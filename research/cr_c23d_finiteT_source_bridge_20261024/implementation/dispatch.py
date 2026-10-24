import pathlib,os,json,subprocess,time,datetime,hashlib,signal
ROOT=pathlib.Path(__file__).resolve().parents[2];unit=pathlib.Path(__file__).resolve().parents[1];runtime=unit/'runtime';runtime.mkdir(parents=True,exist_ok=True);(unit/'runs').mkdir(parents=True,exist_ok=True);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run=unit/'runs'/('c23d_source_ee_'+stamp+'_v1');run.mkdir();lease=runtime/'ACTIVE_LOCAL_LEASE.json'
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
processes=[]
for p in pathlib.Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
   if 'c23d' in cmd or 'run_bridge.py' in cmd:processes.append({'pid':int(p.name),'command':cmd[:500]})
  except OSError:pass
observed={'affinity':sorted(os.sched_getaffinity(0)),'cpu_max':pathlib.Path('/sys/fs/cgroup/cpu.max').read_text().strip(),'memory_max':pathlib.Path('/sys/fs/cgroup/memory.max').read_text().strip(),'task_processes':processes,'cpu55':'ABSENT_PROTECTED_UNTOUCHED','external_runtime':'UNOBSERVED','ps_utility':'FAILED fatal library error lookup self; /proc used'}
assert 0 in observed['affinity'] and 8 in observed['affinity'];write(run/'RESOURCE_ADMISSION.json',observed)
with lease.open('x') as f:json.dump({'run':str(run),'coordinator_pid':os.getpid(),'worker_cpu':0,'coordinator_cpu':8,'native_threads':1,'cpu_limit_s':120,'wall_limit_s':180,'rss_limit_MiB':512,'status':'OWNED'},f)
os.sched_setaffinity(0,{8});cmd=['python',str(unit/'implementation/run_bridge.py'),str(run)];write(run/'COMMAND.json',{'argv':cmd,'environment':{k:'1' for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']}});env=os.environ.copy();env.update({k:'1' for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']});start=time.perf_counter();reason=None
try:
 with (run/'STDOUT.txt').open('w') as stdout,(run/'STDERR.txt').open('w') as stderr:
  worker=subprocess.Popen(cmd,stdout=stdout,stderr=stderr,env=env)
  write(run/'WORKER_START.json',{'pid':worker.pid,'started_utc':stamp})
  while worker.poll() is None:
   if time.perf_counter()-start>180:reason='WALL_LIMIT_180S';worker.kill();break
   try:
    status=pathlib.Path('/proc')/str(worker.pid)/'status';rss=next(int(x.split()[1]) for x in status.read_text().splitlines() if x.startswith('VmRSS:'))
    if rss>512*1024:reason='RSS_LIMIT_512MiB';worker.kill();break
   except (OSError,StopIteration):pass
   time.sleep(.2)
  code=worker.wait()
 write(run/'DISPATCH_COMPLETE.json',{'returncode':code,'dispatch_wall_s':time.perf_counter()-start,'limit_failure':reason,'coordinator_cpu_index':8,'worker_cpu_index':0,'science_worker_cpu_limit_s':120,'worker_wall_limit_s':180,'worker_rss_limit_MiB':512})
finally:
 write(run/'LEASE_RELEASED.json',{'run':str(run),'owned_lease_released':True});lease.unlink()
print(str(run),code,flush=True)
