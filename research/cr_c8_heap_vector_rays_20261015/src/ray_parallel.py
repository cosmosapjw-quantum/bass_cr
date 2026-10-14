"""Optional process-parallel compression of independent photon rays.

Ray ownership and proper clocks must be assigned by the caller. Parallelism
is deterministic and isolated: input arrays are never modified, results are
returned in lane order, and ANY hold prevents admission of an ensemble result.
On small rays multiprocessing is usually slower than single-process heap.
No process pool is made except by explicit workers>1 from an actual CLI/test.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from typing import Sequence
from fast_compression import HeapCompressedCohortTransport


def _run_single(arg):
    cohorts,cap,neutrals,dt_s,min_ratio,eb,hb=arg
    trial=HeapCompressedCohortTransport(cohorts,cap)
    cert=trial.compress(neutrals,dt_s,min_ratio,eb,hb)
    return trial.cohorts, cert


def compress_rays(rays:Sequence[Sequence[tuple[float,float]]],
                  cap_per_ray:Sequence[int],
                  neutrals_cm3:Sequence[Sequence[float]],
                  dt_s:Sequence[float],
                  min_redshift_ratio:Sequence[float],
                  event_budget:float=.01, heat_budget_eV:float=.1,
                  workers:int=1):
    """New outputs only, no mutation; all lanes successful or raises Hold.

    Unlike an angular-averaged recompression, no two ray identifiers are merged.
    """
    n=len(rays)
    if not(n==len(cap_per_ray)==len(neutrals_cm3)==len(dt_s)==len(min_redshift_ratio)):
        raise ValueError('ray controls must match ray count')
    if isinstance(workers,bool) or not isinstance(workers,int) or workers<1 or workers>16:
        raise ValueError('workers must be integer 1..16')
    args=[(tuple(rays[i]),cap_per_ray[i],tuple(neutrals_cm3[i]),dt_s[i],
           min_redshift_ratio[i],event_budget,heat_budget_eV) for i in range(n)]
    if workers==1:return [_run_single(a) for a in args]
    with ProcessPoolExecutor(max_workers=workers, mp_context=get_context("forkserver")) as pool:
        return list(pool.map(_run_single,args,chunksize=max(1,n//(4*workers))))
