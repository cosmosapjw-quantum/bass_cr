#!/usr/bin/env python3
"""Read-only cache hints for the provided calculation runtime, no file edits."""
import datetime,json,os,pathlib,resource
UNIT=pathlib.Path('/workspace/scratch/865c84d871b7/bass_cr/research/cr_low_birth_causal_rr_20261027')
ROOT=pathlib.Path('/opt/codex/runtimes/codex-primary-runtime')
OUT=UNIT/'evidence/C04_RUNTIME_CACHE_RECLAIM_V2.json'
assert ROOT.is_dir() and not OUT.exists()
def mem():
 p=pathlib.Path('/sys/fs/cgroup');s={k:int(v) for k,v in (x.split() for x in (p/'memory.stat').read_text().splitlines())};m=int((p/'memory.max').read_text());c=int((p/'memory.current').read_text());return {'max':m,'current':c,'active_file':s['active_file'],'inactive_file':s['inactive_file'],'dirty':s['file_dirty'],'writeback':s['file_writeback'],'unchanged_admission_available':max(0,m-c+max(0,s['inactive_file']-s['file_dirty']-s['file_writeback']))}
before=mem();count=0;total=0;errors=[]
for p in ROOT.rglob('*'):
 if p.is_symlink() or not p.is_file():continue
 assert count<50000,'BOUNDED_RUNTIME_FILE_INVENTORY_EXCEEDED'
 try:
  fd=os.open(p,os.O_RDONLY)
  try:os.posix_fadvise(fd,0,0,os.POSIX_FADV_DONTNEED)
  finally:os.close(fd)
  count+=1;total+=p.stat().st_size
 except OSError as e:errors.append({'path':str(p.relative_to(ROOT)),'errno':e.errno})
u=resource.getrusage(resource.RUSAGE_SELF);cpu=u.ru_utime+u.ru_stime
r={'schema':'CR_LOW_BIRTH_RUNTIME_CACHE_RECLAIM_V2','unit':'CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime_root':str(ROOT),'operation':'POSIX_FADV_DONTNEED on read-only installed-runtime regular file descriptors; only disposable cache may be released','runtime_files_or_settings_modified':False,'cgroup_limits_or_global_cache_settings_modified':False,'processes_signalled':0,'files_addressed':count,'bytes_addressed':total,'errors':errors,'memory_before':before,'memory_after':mem(),'measured_process_CPU_through_receipt_s':cpu,'receipt_tail_reserve_s':.05,'charged_preparation_CPU_s':cpu+.05,'scientific_workers_executed':0,'fixed_required_memory_bytes':1342177280}
with OUT.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps(r))
