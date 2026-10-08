"""Allocation/FFT preflight only. No preparation or collision propagation."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cupy as cp
from cr_repro.r3m11 import ControlledTDLRunner, source_digest

def probe(config):
    cfg=json.loads(Path(config).read_text())
    if cfg['backend'] != 'cupy': raise ValueError('GPU-only resource preflight')
    free,total=cp.cuda.runtime.memGetInfo()
    n=1
    for axis in ('xlim','ylim','zlim'):
        n*=round((cfg['grid'][axis][1]-cfg['grid'][axis][0])/cfg['grid']['dx'])
    # Before allocating: 16 complex-equivalent arrays plus 2 GiB workspace/slack.
    # This is a conservative declared budget, not the 1.953125 array-size ratio.
    budget=256*n+2*1024**3
    reserve=1536*1024**2
    record=dict(schema='R3M15_RESOURCE_PREFLIGHT_V1',points=n,free_before=free,total=total,
                declared_job_budget_bytes=budget,reserve_bytes=reserve,source_digest=source_digest(),
                cpu_fallback_allowed=False,fft_workspace_included=True)
    if budget+reserve>free:
        return dict(record,status='RESOURCE_BLOCKED_PREALLOCATION')
    runner=ControlledTDLRunner(cfg)
    state=cp.zeros(runner.spec.shape(),dtype=cp.complex128)
    transformed=cp.fft.fftn(state)
    restored=cp.fft.ifftn(transformed)
    cp.cuda.Stream.null.synchronize()
    cache=cp.fft.config.get_plan_cache()
    workspace=cache.get_curr_memsize()
    free_after,_=cp.cuda.runtime.memGetInfo()
    allocated=free-free_after
    # Additional four complex + four real arrays and 1 GiB slack cover
    # real/imaginary-step expression temporaries beyond this live allocation.
    estimate=allocated+96*n+1024**3
    status='PASS_RESOURCE_PREFLIGHT' if estimate<=budget and free_after>reserve else 'RESOURCE_BLOCKED_FFT_BUDGET'
    return dict(record,status=status,fft_plan_cache_bytes=workspace,
                pool_total_bytes=cp.get_default_memory_pool().total_bytes(),
                live_allocation_delta_bytes=allocated,estimated_peak_bytes=estimate,
                free_after_fft=free_after,backend='cupy',cupy=cp.__version__)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();r=probe(a.config)
    with open(a.out,'x') as f: json.dump(r,f,indent=2)
    print(json.dumps(r));sys.exit(0 if r['status']=='PASS_RESOURCE_PREFLIGHT' else 3)
