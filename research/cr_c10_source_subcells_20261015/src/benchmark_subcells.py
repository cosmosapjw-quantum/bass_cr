"""Matched-physics SOURCE07 frozen-gas source and vectorization benchmark.

Not a full reionization or a corrected arbitrary-history two-moment solver.
"""
from __future__ import annotations
import argparse,json,platform,statistics,time,sys,tracemalloc
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
import numpy as np
from source_subcells import (
    source_quadrature,source_and_reaction,centroid_control,
    source_continuum_reference,cached_source_kernel,batched_frozen_reactions,
    scalar_frozen_reactions,scalar_cached_reactions,PHYSICAL_BINDING
)

OWNER_RHO=(0.0017575700008892194,0.0001429214010766023,0.)
OWNER_DT=1e10
OWNER_EMISSION=4.298036114764196e-8
OWNER_HEI=1.4281834584030507e-9
OWNER_HI=2.978921350017158e-8
OWNER_HEAT=1.4592997571739564e-7


def _measure(callback,repeats=5):
    # First call warms module caches and CPU code paths, excluding import cost.
    callback()
    t=[]
    for i in range(repeats):
        start=time.perf_counter();callback();t.append(time.perf_counter()-start)
    return statistics.median(t),t


def one_qgrid(n,order=8):
    q=source_quadrature(n,1.,order)
    raw=source_and_reaction(q,OWNER_RHO,OWNER_DT,OWNER_EMISSION)
    centroid=centroid_control(q,OWNER_RHO,OWNER_DT,OWNER_EMISSION)
    return dict(nE=n,quadrature_order=order,positive_nodes=len(q.energy_eV),
                stored_q_state_f64bytes=n*2*8,
                quadrature_raw_array_bytes=sum(x.nbytes for x in (q.q_index,q.energy_eV,q.photon_weight_per_initial_H,q.energy_nodes_ref_eV)),
                source_number_per_H=q.count*OWNER_EMISSION,
                source_mean_energy_eV=q.physical_energy/q.count,
                N_U_residual=(raw['number_residual'],raw['energy_residual_eV']),
                rate_ref={'HI':OWNER_HI,'HeI':OWNER_HEI,'heat_eV':OWNER_HEAT},
                subcell_events=raw['absorb_species'].sum(axis=1).tolist(),
                centroid_events=centroid['absorb_species'].sum(axis=1).tolist(),
                subcell_heat_eV=raw['heat_species'].sum(axis=1).tolist(),
                centroid_heat_eV=centroid['heat_species'].sum(axis=1).tolist(),
                relative_heI={'subcell':raw['absorb_species'][1].sum()/OWNER_HEI-1,
                              'centroid':centroid['absorb_species'][1].sum()/OWNER_HEI-1},
                relative_total_abs={'subcell':raw['absorb_species'].sum()/(OWNER_HEI+OWNER_HI)-1,
                                    'centroid':centroid['absorb_species'].sum()/(OWNER_HEI+OWNER_HI)-1},
                relative_heat={'subcell':raw['heat_species'].sum()/OWNER_HEAT-1,
                               'centroid':centroid['heat_species'].sum()/OWNER_HEAT-1})


def _scalar_jobs(args):
    # Worker data are simple values, not mutable shared q-state.
    n,gas,dt,num,emitted=args
    q=cached_source_kernel(n)
    return [(e.tolist(),h.tolist()) for e,h in
            (scalar_frozen_reactions(q,g, float(t),emitted) for g,t in zip(gas,dt))]


def execute(repeats=5,ray_cases=(8,32,128),nE=256,processes=(1,2,4)):
    rho=np.asarray(OWNER_RHO)
    items=[one_qgrid(n) for n in (64,128,256,512,1024)]
    orders=[]
    for n in (64,256):
        for order in (4,8,12,16):
            q=source_quadrature(n,order=order)
            v=source_and_reaction(q,rho,OWNER_DT,OWNER_EMISSION)
            orders.append(dict(nE=n,order=order,
                relative_HeI=v['absorb_species'][1].sum()/OWNER_HEI-1,
                relative_total=v['absorb_species'].sum()/(OWNER_HI+OWNER_HEI)-1,
                relative_heat=v['heat_species'].sum()/OWNER_HEAT-1))
    # For speed compare exactly the SAME nodes, Verner function and physical
    # redshift/absorption, not 2 methods with different source/solver accuracy.
    q=cached_source_kernel(nE)
    results=[]
    rng=np.random.default_rng(20261015)
    for count in ray_cases:
        gas=rho*(.8+0.4*rng.random((count,3)))
        gas[:,2]=rng.uniform(0,1e-5,count)
        dt=OWNER_DT*(.8+0.4*rng.random(count))
        func_vector=lambda:batched_frozen_reactions(q,gas,dt,OWNER_EMISSION,batch_size=16)
        def func_scalar():
            return np.stack([scalar_frozen_reactions(q,g,float(t),OWNER_EMISSION)[0] for g,t in zip(gas,dt)])
        v=func_vector();s=func_scalar();np.testing.assert_allclose(v[0],s,rtol=2e-12,atol=1e-25)
        def func_cached_scalar():
            return np.stack([scalar_cached_reactions(q,g,float(t),OWNER_EMISSION)[0] for g,t in zip(gas,dt)])
        sc=func_cached_scalar()
        np.testing.assert_allclose(v[0],sc,rtol=2e-12,atol=1e-25)
        scalar_t,scalar_runs=_measure(func_scalar,repeats)
        cached_t,cached_runs=_measure(func_cached_scalar,repeats)
        vector_t,vector_runs=_measure(func_vector,repeats)
        results.append(dict(rays=count,scalar_uncached_ms=scalar_t*1e3,scalar_cached_ms=cached_t*1e3,vector_ms=vector_t*1e3,
                            speedup_uncached_over_numpy=scalar_t/vector_t,speedup_cached_over_numpy=cached_t/vector_t,
                            max_relative_event_diff=float(np.max(np.abs((v[0]-s)/(np.abs(s)+1e-30)))),
                            scalar_times_ms=[x*1e3 for x in scalar_runs],cached_times_ms=[x*1e3 for x in cached_runs],vector_times_ms=[x*1e3 for x in vector_runs]))
    # Run optional CPU-bound independent-ray scalar baseline with *separate*
    # processes; report observed speed, never hardcode concurrency advantage.
    count=max(ray_cases)
    gas=rho*(.8+0.4*rng.random((count,3)))
    gas[:,2]=rng.uniform(0,1e-5,count)
    dt=OWNER_DT*(.8+0.4*rng.random(count))
    parallel=[]
    for workers in processes:
        if workers==1:
            med,times=_measure(lambda:_scalar_jobs((nE,gas,dt,count,OWNER_EMISSION)),repeats=3)
        else:
            def runpool():
                chunks=np.array_split(np.arange(count),workers)
                payload=[(nE,gas[z],dt[z],len(z),OWNER_EMISSION) for z in chunks]
                with ProcessPoolExecutor(max_workers=workers,mp_context=get_context('spawn')) as pool:
                    return list(pool.map(_scalar_jobs,payload))
            # Process start/teardown included; the production local task is not
            # an endlessly re-used shared worker pool.
            med,times=_measure(runpool,repeats=3)
        parallel.append(dict(workers=workers,median_ms=med*1e3,raw_ms=[x*1e3 for x in times]))
    return dict(kind='SOURCE07 C6 q0 positive source subcell and performance preview',
        status='LOCAL_COMPONENT_ONLY_NO_COUPLED_HISTORY',
        source_id='MD14_Z002_FESC_BB50K_13P6_100_V1_NATIVE48_FROZEN_GAS',
        gas=OWNER_RHO,dt_s=OWNER_DT,source_number_per_H=OWNER_EMISSION,
        owner_continuum={'HI':OWNER_HI,'HeI':OWNER_HEI,'heat_eV':OWNER_HEAT},
        binding_eV=PHYSICAL_BINDING,fit_cutoffs_eV=(13.6,24.59,54.42),
        results=items,gauss_orders=orders,vectorization=results,independent_processes=parallel,
        env=dict(python=sys.version.split()[0],numpy=np.__version__,machine=platform.machine()),
        caveats='Source-conditioned smooth blackbody within each original native cell ONLY; after arbitrary attenuation N,U do not determine opacity. Independent quadrature numbers are empirical, not directed interval error bounds. No owner AXBI mutation or full coupled history.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repeats',type=int,default=3)
    p.add_argument('--rays',type=int,nargs='+',default=[8,32,128]);p.add_argument('--workers',type=int,nargs='+',default=[1,2,4]);p.add_argument('--nE',type=int,default=256)
    args=p.parse_args()
    print(json.dumps(execute(args.repeats,tuple(args.rays),args.nE,tuple(args.workers)),indent=2))
