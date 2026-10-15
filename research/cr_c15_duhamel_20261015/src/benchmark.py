"""Matched C15 no-threshold pruning, cached birth template, OS q parallel."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
import numpy as np
from owner_age_bridge import owner_namespace
from continuous_source import evolve_continuous

def compute(root,q,n,cache=True,prune=True):
    ns=owner_namespace(Path(root))
    r=evolve_continuous(ns,q,n,cached_birth_spectrum=cache,
                        exact_zero_prune=prune)
    return {"gas":r["gas_final"],"N":r["ledgers"]["final_photons_per_H"],
            "memory":r["packet_bytes"],"n":r["photon_packet_count"],
            "cpu":r["wall_seconds"]}

def agree(a,b):
    for k in a["gas"]:
        np.testing.assert_allclose(a["gas"][k],b["gas"][k],rtol=3e-13,atol=1e-11)
    np.testing.assert_allclose(a["N"],b["N"],rtol=1e-12,atol=1e-13)

def bench(root,nsteps=128,repeats=3):
    root=str(root)
    baseline=compute(root,0.,nsteps,cache=True,prune=True)
    modes={}
    for name,opts in {
       "default_cached_pruned":dict(cache=True,prune=True),
       "uncached_pruned":dict(cache=False,prune=True),
       "cached_unpruned":dict(cache=True,prune=False)
    }.items():
        times=[]
        for _ in range(repeats):
            t=time.perf_counter();run=compute(root,0.,nsteps,**opts)
            times.append(time.perf_counter()-t)
            agree(baseline,run)
        modes[name]={"median_wall_s":float(np.median(times)),
             "wall_samples_s":times,"packet_bytes":run["memory"],
             "npackets":run["n"]}
    qs=(-.01,0.,.01)
    science=[compute(root,q,nsteps) for q in qs]
    process={}
    for workers in (1,2,3):
        elapsed=[]
        for _ in range(repeats):
            t=time.perf_counter()
            if workers==1:
                result=[compute(root,q,nsteps) for q in qs]
            else:
                with ProcessPoolExecutor(max_workers=workers,
                              mp_context=get_context("spawn")) as pool:
                    result=list(pool.map(compute,[root]*3,qs,[nsteps]*3))
            elapsed.append(time.perf_counter()-t)
            for a,b in zip(science,result):
                agree(a,b)
        process[str(workers)]={"median_wall_s":float(np.median(elapsed)),
                                "wall_samples_s":elapsed}
    return {"schema":"C15_MATCHED_ACCURACY_PERFORMANCE_V1",
       "nsteps":nsteps,"repeats":repeats,"modes":modes,
       "q_processes":process,
       "source_claim":"cache/prune comparisons numerically matched; processes compare three q jobs",
       "global_rei_solver_speed":"NOT_MEASURED"}

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--owner",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    a.add_argument("--steps",type=int,default=128)
    a.add_argument("--repeats",type=int,default=3)
    x=a.parse_args()
    d=bench(x.owner,x.steps,x.repeats)
    x.out.parent.mkdir(exist_ok=True,parents=True)
    x.out.write_text(json.dumps(d,indent=2)+"\n")
    print(json.dumps({"modes":{k:v["median_wall_s"] for k,v in d["modes"].items()},
          "processes":{k:v["median_wall_s"] for k,v in d["q_processes"].items()}},indent=2))