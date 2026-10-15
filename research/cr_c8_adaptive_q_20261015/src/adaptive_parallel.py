"""Bounded 1/2/4 process source-local independent ray benchmark.

Runs different physical gas/time rays in separate processes. Native subagents
are NOT involved; only multiprocessing for verified numerical kernels.
"""
import argparse,json,time
from concurrent.futures import ProcessPoolExecutor
from adaptive_q import AdaptiveQGrid
from moment_envelopes import cached_template
from adaptive_benchmark import current_packets,HEI_FOCUS_BUDGET
import numpy as np


def _solve(idx:int):
    # All independently scheduled jobs start from the SAME COLD template state.
    # Avoid a misleading speedup from fork-inherited warmed parent LRU entries.
    cached_template.cache_clear()
    oracle,ratio,gas,dt=current_packets(bool(idx%2))
    # Actual q rays are externally different physical characteristics; these
    # settings are bounded manufactured controls, NOT SOURCE07 gas chronology.
    rho=(gas[0]*(1.+idx*.025),gas[1]*(1.+idx*.02),gas[2]*(1.+idx*.01))
    a=AdaptiveQGrid(oracle,np.geomspace(13.6,433.,65),ratio,rho,dt,HEI_FOCUS_BUDGET,4)
    out=a.run(96)
    return (idx,out['widths'],out['mass'],out['reference_energy_eV'])


def measure(workers:int,ray_count:int=4):
    if workers not in (1,2,4) or ray_count not in (2,4,8):
        raise ValueError('workload/cpu bound violated')
    t=time.perf_counter()
    if workers==1:
        x=[_solve(i) for i in range(ray_count)]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            x=list(pool.map(_solve,range(ray_count)))
    return {'workers':workers,'rays':ray_count,'seconds':time.perf_counter()-t,'outputs':x}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--rays',type=int,default=4);args=ap.parse_args()
    data=[measure(w,args.rays) for w in (1,2,4)]
    baseline=data[0]['outputs']
    assert all(x['outputs']==baseline for x in data)
    print(json.dumps({'model':'FOUR_INDEPENDENT_FROZEN_RAYS_NOT_EOR','results':data},indent=2))
