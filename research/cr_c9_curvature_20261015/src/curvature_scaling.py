"""Optional independent-ray parallel benchmark; per-ray source ownership retained.

The multi-process run is not a native subagent, source/chemistry evolution, or a
benchmark of rei_bianchi's own multi-threaded Rust q-transport. This trial uses
32- or 64-ray synthetic frozen neutral tuples with identical energy support.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from time import perf_counter
from statistics import median
import argparse,json
from threshold_rt import frozen_source
from directed_curvature import DirectedCurvatureHeap
from curvature_benchmark import OWNER_BIND, DT


def lane(i):
    neutrals=(.001*(1+.002*i),8e-5*(1+.001*i),2e-5*(1-.0005*i))
    photons=frozen_source(16)
    obj=DirectedCurvatureHeap(photons,22,binding_eV=OWNER_BIND)
    cert=obj.compress(neutrals,DT,.995,.01,1.)
    return (cert.final_cohorts,cert.merges,obj.moments(),
            cert.event_absolute_bounds,cert.heat_absolute_bounds_eV)


def run(nray=32,repeats=3):
    names=list(range(nray));truth=[lane(i) for i in names]
    rows=[]
    for workers in (1,2,4):
        times=[]
        for _ in range(repeats):
            t=perf_counter()
            if workers==1:
                out=[lane(i) for i in names]
            else:
                with ProcessPoolExecutor(max_workers=workers,mp_context=get_context('fork')) as pool:
                    out=list(pool.map(lane,names,chunksize=max(1,nray//(workers*4))))
            times.append((perf_counter()-t)*1000)
            assert out==truth
        rows.append(dict(workers=workers,timing_ms=times,median_ms=median(times),
                         exact_per_ray_readout_match=True))
    return dict(scope='frozen neutral independent rays, SOURCE07 C4 owner geometry NOT_RUN',
                ray_count=nray, source_n16=48,cap=22,source_fixed_binding=OWNER_BIND,
                repeats=repeats,rows=rows)

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--rays',type=int,default=32)
    pa.add_argument('--repeats',type=int,default=3);a=pa.parse_args()
    print(json.dumps(run(a.rays,a.repeats),indent=2))
