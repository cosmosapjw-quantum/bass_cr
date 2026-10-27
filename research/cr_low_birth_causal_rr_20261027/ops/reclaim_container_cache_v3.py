#!/usr/bin/env python3
"""Ask the kernel to reclaim clean/file cache; keep all resource limits fixed."""
import datetime,json,pathlib,resource
UNIT=pathlib.Path('/workspace/scratch/865c84d871b7/bass_cr/research/cr_low_birth_causal_rr_20261027')
OUT=UNIT/'evidence/C04_CONTAINER_CACHE_RECLAIM_V3.json'
assert not OUT.exists()
root=pathlib.Path('/sys/fs/cgroup')
def mem():
 s={k:int(v) for k,v in (x.split() for x in (root/'memory.stat').read_text().splitlines())};limit=int((root/'memory.max').read_text());current=int((root/'memory.current').read_text());return {'max':limit,'current':current,'active_file':s['active_file'],'inactive_file':s['inactive_file'],'dirty':s['file_dirty'],'writeback':s['file_writeback'],'available_fixed_rule':max(0,limit-current+max(0,s['inactive_file']-s['file_dirty']-s['file_writeback']))}
before=mem();error=None
try:
 with (root/'memory.reclaim').open('w') as f:f.write('2147483648 swappiness=0\n')
except OSError as e:error={'type':type(e).__name__,'errno':e.errno,'message':str(e)}
u=resource.getrusage(resource.RUSAGE_SELF);cpu=u.ru_utime+u.ru_stime
result={'unit':'CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requested_operation':'kernel proactive file-cache reclaim 2GiB, swappiness=0','persistent_resource_limits_changed':False,'processes_signalled':0,'files_deleted_or_edited':False,'before':before,'after':mem(),'error':error,'process_CPU_through_receipt_s':cpu,'receipt_tail_reserve_s':.05,'charged_preparation_CPU_s':cpu+.05,'kernel_background_CPU_s':None,'scientific_workers_executed':0}
with OUT.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
