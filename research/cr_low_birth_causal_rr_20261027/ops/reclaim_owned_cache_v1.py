#!/usr/bin/env python3
"""Release only disposable clean file cache for this task; never edit bytes."""
import datetime,hashlib,json,os,pathlib,resource
ROOT=pathlib.Path('/workspace/scratch/865c84d871b7')
UNIT=ROOT/'bass_cr/research/cr_low_birth_causal_rr_20261027'
OUT=UNIT/'evidence/C04_OWNED_CACHE_RECLAIM_V1.json'
assert not OUT.exists()
scope=['bass_cr','restored','next_intake','release_source','release_closeout','readbacks','next_deliverables','deliverables','project_sources','final','ops','next_ops']
def mem():
 root=pathlib.Path('/sys/fs/cgroup');return {'current':int((root/'memory.current').read_text()),'max':(root/'memory.max').read_text().strip(),'stat':{k:int(v) for k,v in (x.split() for x in (root/'memory.stat').read_text().splitlines()) if k in ['anon','file','active_file','inactive_file','file_dirty','file_writeback','slab_reclaimable']}}
before=mem();count=0;total=0;errors=[]
for folder in scope:
 for p in (ROOT/folder).rglob('*'):
  if p.is_symlink() or not p.is_file():continue
  try:
   fd=os.open(p,os.O_RDONLY)
   try:os.posix_fadvise(fd,0,0,os.POSIX_FADV_DONTNEED)
   finally:os.close(fd)
   count+=1;total+=p.stat().st_size
  except OSError as e:errors.append({'path':str(p.relative_to(ROOT)),'errno':e.errno})
usage=resource.getrusage(resource.RUSAGE_SELF);cpu=usage.ru_utime+usage.ru_stime
result={'schema':'CR_LOW_BIRTH_OWNED_FILE_CACHE_RECLAIM_V1','unit':'CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':scope,'operation':'POSIX_FADV_DONTNEED on read-only regular task-owned file descriptors','file_bytes_modified':False,'global_cache_or_cgroup_settings_modified':False,'processes_signalled':0,'file_count':count,'file_bytes_addressed':total,'errors':errors,'memory_before':before,'memory_after':mem(),'measured_process_CPU_through_receipt_s':cpu,'receipt_tail_reserve_s':.05,'charged_preparation_CPU_s':cpu+.05,'old_budget_transferred':False,'scientific_workers_executed':0}
with OUT.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
