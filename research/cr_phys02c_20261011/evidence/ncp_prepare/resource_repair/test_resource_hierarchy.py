"""Operational synthetic fixtures only: no numerical imports or transport."""
from pathlib import Path
import importlib.util,json,os,sys,tempfile
STUDY=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(STUDY/'ncp'));import ops
G=1024**3
results=[]
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);proc=root/'proc';cg=root/'cgroup';(proc/'self').mkdir(parents=True);leaf=cg/'jobs/task';leaf.mkdir(parents=True)
 (proc/'meminfo').write_text(f'MemTotal: {128*G//1024} kB\nMemAvailable: {120*G//1024} kB\n');(proc/'self/cgroup').write_text('0::/jobs/task\n');(proc/'self/mountinfo').write_text(f'10 9 0:1 / {cg} rw - cgroup2 cgroup2 rw\n')
 cpus=','.join(map(str,sorted(os.sched_getaffinity(0))));(leaf/'cpuset.cpus.effective').write_text(cpus)
 for p in [cg,cg/'jobs',leaf]:
  for name,value in {'cpu.max':'max 100000','memory.max':'max','memory.current':str(G//4)}.items():(p/name).write_text(value)
 parent=cg/'jobs'
 def case(name,limit,current,quota,wanted):
  (parent/'memory.max').write_text(str(limit));(parent/'memory.current').write_text(str(current));(parent/'cpu.max').write_text(quota)
  r=ops.probe(root,str(proc));assert r['admitted']==wanted,(name,r);assert len(r['cgroup_hierarchy']['ancestors'])==3
  results.append({'id':name,'status':'PASS_OPERATIONAL_ONLY','probe':r});return r
 r=case('EXACT_REVIEW_COUNTEREXAMPLE_LEAF_MAX_PARENT_8GiB_0p5CPU',8*G,G,'50000 100000',False)
 assert r['cpu_quota']==.5 and r['bounded_memory_bytes']==8*G and r['available_before_reserve_bytes']==7*G and r['reserve_bytes']==G and r['available_working_bytes']==6*G
 r=case('PARENT_QUOTA2_INSUFFICIENT_HEADROOM',32*G,25*G,'200000 100000',False)
 assert r['cpu_quota']==2 and r['available_before_reserve_bytes']==7*G and r['available_working_bytes']==3*G
 r=case('PARENT_SUFFICIENT_CAPACITY_POSITIVE',32*G,G,'200000 100000',True)
 assert r['cpu_quota']==2 and r['available_working_bytes']==27*G
 # Unknown mapping and unreadable ancestor limits never guess host capacity.
 (proc/'self/cgroup').write_text('0::/unresolved/task\n');r=ops.probe(root,str(proc));assert r['status']=='HOLD' and not r['capacity_established'];results.append({'id':'UNRESOLVED_MEMBERSHIP_HOLD','probe':r})
 (proc/'self/cgroup').write_text('0::/jobs/task\n');(parent/'memory.current').unlink();r=ops.probe(root,str(proc));assert r['status']=='HOLD' and not r['capacity_established'];results.append({'id':'UNREADABLE_ANCESTOR_HOLD','probe':r})
 (parent/'memory.current').write_text(str(G));(proc/'self/mountinfo').write_text('unresolvable mount fixture\n');r=ops.probe(root,str(proc));assert r['status']=='HOLD' and not r['capacity_established'];results.append({'id':'UNRESOLVED_MOUNT_HOLD','probe':r})
 # Replay old implementation's read-only counterexample through its read seam.
 spec=importlib.util.spec_from_file_location('before',Path(__file__).with_name('ops.before.py'));before=importlib.util.module_from_spec(spec);spec.loader.exec_module(before)
 original=before.read
 def oldread(p):
  p=str(p)
  if p=='/proc/meminfo':return f'MemTotal: {128*G//1024} kB\nMemAvailable: {120*G//1024} kB\n'
  if p=='/proc/self/cgroup':return '0::/jobs/task'
  if p.startswith('/sys/fs/cgroup/'):
   return {'cpu.max':'max 100000','memory.max':'max','memory.current':str(G//4),'cpuset.cpus.effective':cpus}.get(p.rsplit('/',1)[-1],original(p))
  return original(p)
 before.read=oldread;r=before.probe(root);assert r['admitted'] and r['available_working_bytes']==104*G and r['cpu_quota'] is None;results.append({'id':'PRESERVED_FIRST_FAILURE_OLD_PROBE_COUNTEREXAMPLE','old_probe':r})
Path(__file__).with_name('SYNTHETIC_RESOURCE_FIXTURES.json').write_text(json.dumps({'status':'PASS_OPERATIONAL_ONLY','transport_calls':0,'cases':results},indent=2)+'\n')
print('PASS_OPERATIONAL_ONLY: 6 repaired fixture cases and preserved old counterexample')
