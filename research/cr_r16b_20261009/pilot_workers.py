"""Bounded 1/2/4/8 process admission pilots on new interval panel kernels."""
import argparse,hashlib,json,os,time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from prepare import compute_cell

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--stage',required=True);a.add_argument('--output',type=Path,required=True)
    x=a.parse_args();results=[];expected=None
    for workers in (1,2,4,8):
        start=time.monotonic()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            data=list(pool.map(compute_cell,[(x.stage,i,4) for i in (0,4,8,12,16,20,24,31)]))
        hashes=[]
        for c in data:
            c={k:v for k,v in c.items() if k not in ('worker_wall_s','worker_peak_RSS_KiB')}
            hashes.append(hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest())
        if expected is None:expected=hashes
        assert hashes==expected,'PARALLEL_NUMERICAL_IDENTITY'
        r={'workers':workers,'wall_s':time.monotonic()-start,'peak_RSS_KiB_per_worker_upper':max(c['worker_peak_RSS_KiB'] for c in data),'kernel_digest_by_cell':hashes,'bitwise_same_outputs':True}
        results.append(r);print(json.dumps(r),flush=True)
    ans={'pilots':results,'fastest_measured_workers':min(results,key=lambda r:r['wall_s'])['workers'],
         'affinity_cpus':sorted(os.sched_getaffinity(0)),'coordinator_reserve_cpus':1,'RAM_reserve_GiB':24,
         'full_certificate_schedule':'initial new full-time panel preparation already running serial; completed panels never repeated for scaling',
         'MPI':False,'NCP64_speedup_claim':False}
    with x.output.open('x') as f:f.write(json.dumps(ans,indent=2)+'\n')
