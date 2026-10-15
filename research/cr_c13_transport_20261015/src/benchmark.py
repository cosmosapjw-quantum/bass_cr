"""Matched source-formula vectorization and OS-process scheduling."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

import numpy as np
from owner_age_bridge import owner_namespace
from transport import integrate,make_birth_cohort,vector_photo_reactions,C


def reference_scalar(photons,E,n,dt,fit,bind,sigma_fn):
    survivor=np.empty_like(photons)
    absorbed=np.zeros(3);heats=np.zeros(3)
    for k in range(len(E)):
        taus=np.array([C*dt*n[j]*sigma_fn(float(E[k]),fit[j]) for j in range(3)])
        t=taus.sum()
        p=taus*(-np.expm1(-t)/t) if t>0 else np.zeros(3)
        event=photons[k]*p
        survivor[k]=photons[k]*np.exp(-t)
        absorbed+=event
        heats+=event*(E[k]-bind)
    return survivor,absorbed,heats


def q_work(q,root,nsteps):
    owner=owner_namespace(Path(root))
    d=integrate(owner,float(q),int(nsteps))
    return {k:d[k] for k in ("q","gas_final","ledgers","elapsed_wall_seconds")}


def bench(root:Path,nsteps:int=64,repeats:int=3):
    ns=owner_namespace(root)
    source=make_birth_cohort(ns,.1,0.,.11,nmu=12,energy_order=16)
    # Use meaningful photon opacities and a vector of all He species.
    n=np.array([1.7e-4,1.5e-5,1e-6])
    bind=np.array(ns["bind"]);dt=2e11
    ref=reference_scalar(source.photons_per_H,source.current_energy_eV,
                         n,dt,ns["fit"],bind,ns["sigma"])
    got=vector_photo_reactions(source.photons_per_H,source.current_energy_eV,
                               n,dt,ns["fit"],bind)
    for a,b in zip(ref,got):
        np.testing.assert_allclose(a,b,rtol=4e-13,atol=1e-14)
    trial=[]
    for _ in range(repeats):
        t=time.perf_counter()
        reference_scalar(source.photons_per_H,source.current_energy_eV,n,dt,ns["fit"],bind,ns["sigma"])
        scalar=time.perf_counter()-t
        t=time.perf_counter()
        vector_photo_reactions(source.photons_per_H,source.current_energy_eV,n,dt,ns["fit"],bind)
        vec=time.perf_counter()-t
        trial.append((scalar,vec))
    qcases=(-.01,0.,.01)
    jobs={}
    base=[q_work(q,str(root),nsteps) for q in qcases]
    for workers in (1,2,3):
        times=[]
        for _ in range(repeats):
            t=time.perf_counter()
            if workers==1:
                records=[q_work(q,str(root),nsteps) for q in qcases]
            else:
                with ProcessPoolExecutor(max_workers=workers,mp_context=get_context("spawn")) as pool:
                    records=list(pool.map(q_work,qcases,[str(root)]*3,[nsteps]*3))
            times.append(time.perf_counter()-t)
            for expected,actual in zip(base,records):
                assert expected["q"]==actual["q"]
                for k in expected["gas_final"]:
                    np.testing.assert_allclose(expected["gas_final"][k],
                           actual["gas_final"][k],rtol=2e-12,atol=1e-11)
        jobs[str(workers)]={"runs_seconds":times,
                  "median_seconds":float(np.median(times))}
    return {
       "schema":"CR_C13_BENCHMARK_V1",
       "qcases":qcases,"nsteps":nsteps,"repeats":repeats,
       "packet_count_for_kernel":source.count,
       "kernel_scalar_median_s":float(np.median([x[0] for x in trial])),
       "kernel_vector_median_s":float(np.median([x[1] for x in trial])),
       "kernel_speed_ratio":float(np.median([x[0] for x in trial])/np.median([x[1] for x in trial])),
       "processes":jobs,
       "scope":"same source, same exact sigma, no direct Rust full-solver claim",
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--nsteps",type=int,default=64)
    ap.add_argument("--repeats",type=int,default=3)
    opt=ap.parse_args()
    r=bench(opt.owner,opt.nsteps,opt.repeats)
    opt.out.parent.mkdir(exist_ok=True,parents=True)
    opt.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps({"scalar_s":r["kernel_scalar_median_s"],
            "vector_s":r["kernel_vector_median_s"],
            "kernel_ratio":r["kernel_speed_ratio"],
            "process_s":{k:v["median_seconds"] for k,v in r["processes"].items()}},indent=2))
