"""Create-only R17B2B run with measured admission; inherited A verify only."""
import argparse,hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
THREADS=['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']
def run(out):
 out.mkdir();(out/'logs').mkdir();(out/'results').mkdir()
 affinity=sorted(os.sched_getaffinity(0));reserve=20*2**30
 mem=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemTotal:')))*1024
 if len(affinity)<2 or mem<reserve+2*2**30:raise RuntimeError('RESOURCE_ADMISSION')
 # coordinator owns CPU0; every child inherits one different CPU and RLIMIT_AS.
 coordinator,worker=affinity[:2];os.sched_setaffinity(0,{coordinator})
 available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
 budget=min(mem,available)
 cgroup=Path('/sys/fs/cgroup')/next(line.split(':',2)[2].lstrip('/') for line in Path('/proc/self/cgroup').read_text().splitlines() if line.startswith('0::'))
 ancestors=[]
 for group in [cgroup,*cgroup.parents]:
  if not str(group).startswith('/sys/fs/cgroup'):continue
  row={'path':str(group)}
  for name in ['cpu.max','cpuset.cpus.effective','memory.max','memory.current']:
   file=group/name
   if file.exists():row[name]=file.read_text().strip()
  ancestors.append(row)
  if row.get('memory.max','max')!='max':budget=min(budget,int(row['memory.max'])-int(row.get('memory.current',0)))
  if row.get('cpu.max','max').split()[0]!='max':
   quota,period=map(int,row['cpu.max'].split())
   if quota/period<2:raise RuntimeError('CPU_RESERVE_QUOTA')
 limit=budget-reserve
 if limit<2*2**30:raise RuntimeError('MEMORY_RESERVE_ADMISSION')
 def admission():
  os.sched_setaffinity(0,{worker});resource.setrlimit(resource.RLIMIT_AS,(limit,limit))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',**{k:'1' for k in THREADS})
 commands=[('TESTS',[sys.executable,'-B','-m','unittest','discover','-s',str(ROOT/'tests')]),
 ('MUTANTS',[sys.executable,'-B',str(ROOT/'mutation_checks.py'),'--output',str(out/'mutants')]),
 ('BOUNDS',[sys.executable,'-B',str(ROOT/'run_bounds.py'),'--output',str(out/'results/BOUNDS.json')]),
 ('INDEPENDENT',[sys.executable,'-B',str(ROOT/'independent_check.py'),'--output',str(out/'results/INDEPENDENT.json')]),
 ('MPFR',[sys.executable,'-B',str(ROOT/'mpfr_check.py'),'--output',str(out/'results/MPFR.json')]),
 ('QUADRATURE',[sys.executable,'-B',str(ROOT/'quadrature_bound.py'),'--output',str(out/'results/QUADRATURE.json')]),
 ('DIAGNOSTIC',[sys.executable,'-B',str(ROOT/'diagnostic.py'),'--output',str(out/'results/DIAGNOSTIC.json')])]
 rows=[]
 for name,cmd in commands:
  start=time.monotonic();full=['/usr/bin/time','-v',*cmd]
  with (out/'logs'/(name+'.log')).open('x') as f:
   r=subprocess.run(full,stdout=f,stderr=subprocess.STDOUT,env=env,preexec_fn=admission)
  rows.append(dict(name=name,command=full,exit=r.returncode,elapsed_s=time.monotonic()-start,log=str(out/'logs'/(name+'.log'))))
  (out/'EXECUTION.json').write_text(json.dumps(dict(coordinator_cpu=coordinator,worker_cpu=worker,memory_reserve_bytes=reserve,worker_RLIMIT_AS=limit,host_mem_total_bytes=mem,host_mem_available_bytes=available,cgroup_ancestors=ancestors,commands=rows),indent=2)+'\n')
  if r.returncode:raise RuntimeError('FAILED_LOG_PRESERVED:'+name)
 # Bound result and arithmetic independent report are deterministic.
 assert (out/'results/BOUNDS.json').read_bytes()==(ROOT/'results/BOUNDS_FINAL.json').read_bytes(),'BOUNDS_REPRODUCTION'
 assert (out/'results/INDEPENDENT.json').read_bytes()==(ROOT/'results/INDEPENDENT.json').read_bytes(),'INDEPENDENT_REPRODUCTION'
 print('FOCUSED_FRESH_REPRODUCTION_PASS; old R16B/R17A/B1/R17B2A nominal suites=0')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path);a.add_argument('--verify-only',action='store_true');x=a.parse_args()
 if x.verify_only:
  m=json.loads((ROOT/'MANIFEST.json').read_text())
  for p,v in m['files'].items():
   raw=(ROOT/p).read_bytes();assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256'],p
  print('SEALED_PAYLOADS_VERIFIED',len(m['files']))
 else:
  if x.output is None:a.error('--output required')
  run(x.output.resolve())
