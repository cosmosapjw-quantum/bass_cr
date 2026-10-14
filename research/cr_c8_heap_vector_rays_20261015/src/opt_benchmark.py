"""Actual matched-accuracy optimization bench, not production AXBI benchmark.

Deterministic source fixtures; report medians and exact outcome identity for heap;
vectorized multi-ray error against scalar; optional process parallel baseline.
"""
from __future__ import annotations
import argparse, gc, json, random, statistics, time, os, platform, sys
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from compressed_cohorts import CompressedCohortTransport,frozen_be_readout,CompressionHold
from fast_compression import HeapCompressedCohortTransport
from batch_observables import batch_frozen_be_readout
from threshold_rt import frozen_source

NN=(1.e-3,8.e-5,2.e-5)


def timing(func,repeats:int=5):
    times=[]
    for _ in range(repeats):
        t=time.perf_counter_ns();func();times.append((time.perf_counter_ns()-t)*1e-9)
    return statistics.median(times),times


def setup_cohorts(axis:int,repeat:int=1):
    base=frozen_source(axis)
    if repeat==1:return base
    # Stack independent source-age populations into a *single* artificial ray;
    # physically this is only a fixed-geometry benchmark of scaling/decision.
    return [(e*(1.+2.e-5*j),n/repeat) for j in range(repeat) for e,n in base]


def compare_heap(repeats=5):
    cases=[('48_to32',setup_cohorts(16),32),('96_to48',setup_cohorts(32),48),
           ('240_to32',setup_cohorts(16,5),32),('384_to192',setup_cohorts(128),192)]
    rows=[]
    for name,arr,cap in cases:
        def call(cls):
            x=cls(arr,cap)
            try:r=x.compress(NN,1e9,.99,.1,20.);return ('PASS',x.cohorts,r)
            except CompressionHold as exc:return ('HOLD',x.cohorts,str(exc))
        a=call(CompressedCohortTransport)
        b=call(HeapCompressedCohortTransport)
        assert a==b,(name,a,b)
        # Keep exact scientific outcome verification separate from timings.
        fn1=lambda:call(CompressedCohortTransport)
        fn2=lambda:call(HeapCompressedCohortTransport)
        # Warmups for Python caches and likely branch prediction.
        fn1();fn2()
        slow,_=timing(fn1,repeats)
        fast,_=timing(fn2,repeats)
        rows.append(dict(name=name,n_initial=len(arr),n_final=len(a[1]),status=a[0],
                         reference_median_s=slow,heap_median_s=fast,
                         speedup_scan_over_heap=slow/fast,exact_parity=True))
    return rows


def _scalar_one(inp):
    ray,rho,dt,ratio=inp
    return frozen_be_readout(ray,rho,dt,ratio)


def compare_vectorized(repeats=5,include_process=True):
    rng=random.Random(505)
    base=frozen_source(16)
    rows=[]
    for count in (8,64,256):
        rays=[[(e*(1+0.0005*rng.random()),n) for e,n in base] for k in range(count)]
        neutrals=[tuple(z*rng.uniform(.7,1.3) for z in NN) for k in range(count)]
        dt=[1.e9*(.5+rng.random()) for _ in range(count)]
        ratio=[.99+.01*rng.random() for _ in range(count)]
        inputs=list(zip(rays,neutrals,dt,ratio))
        seq=lambda:[_scalar_one(v) for v in inputs]
        vec=lambda:batch_frozen_be_readout(rays,neutrals,dt,ratio)
        expected=seq();e,h=vec()
        max_rel=max(abs(float(e[j,k])-expected[j][0][k])/max(1.e-14,abs(expected[j][0][k]))
                        for j in range(count) for k in range(3))
        max_heat_rel=max(abs(float(h[j,k])-expected[j][1][k])/max(1.e-14,abs(expected[j][1][k]))
                        for j in range(count) for k in range(3))
        assert max_rel<5e-13 and max_heat_rel<5e-13,(max_rel,max_heat_rel)
        seq();vec()
        t_seq,_=timing(seq,repeats)
        t_vec,_=timing(vec,repeats)
        row=dict(rays=count,packets=count*len(base),scalar_median_s=t_seq,
                 numpy_median_s=t_vec,speedup_scalar_over_numpy=t_seq/t_vec,
                 max_event_rel=max_rel,max_heat_rel=max_heat_rel)
        if include_process and count in (64,256):
            # Process pool set up outside per-call timing; separately report
            # process startup costs and in-pool dispatch/IPC, no hidden prewarm.
            t0=time.perf_counter()
            with ProcessPoolExecutor(max_workers=2, mp_context=get_context("forkserver")) as pool:
                p0=time.perf_counter()
                pro=lambda:list(pool.map(_scalar_one,inputs,chunksize=8))
                x=pro(); assert x==expected
                p,_=timing(pro,3)
                row.update(two_process_median_s=p,speedup_scalar_over_two_process=t_seq/p,
                           pool_setup_s=p0-t0)
        rows.append(row)
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repeats',type=int,default=5)
    parser.add_argument('--no-process',action='store_true')
    a=parser.parse_args()
    out=dict(schema='bass_cr.optimized_c5_benchmark.v1',mode='same numerical inputs & reference decisions',
             python=sys.version,platform=platform.platform(),cpu_count=os.cpu_count(),
             repeats=a.repeats,compress=compare_heap(a.repeats),
             batched=compare_vectorized(a.repeats,not a.no_process),
             caution='Measured times are environment- and input-specific; no full native RT or chemistry solver was run.')
    print(json.dumps(out,indent=2,allow_nan=False))

if __name__=='__main__': main()
