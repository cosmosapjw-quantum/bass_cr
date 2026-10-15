"""Matched-input local C16/C17 timing and three-q process scheduling."""
from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path

import numpy as np

from owner_age_bridge import owner_namespace,verner_sigma_array
from continuous_source import proper_dt
from endpoint_quadrature import optical_quadrature
from species_events import species_resolved_affine
from owner_species_benchmark import case


def q_task(task):
    root,q=task
    ns=owner_namespace(Path(root))
    row=case(ns,q,nsteps=(32,64,128))
    return {"q":q,
            "old":[x["C16_species_total_max_rel_error"] for x in row["grid_runs"]],
            "new":[x["C17_species_total_max_rel_error"] for x in row["grid_runs"]],
            "events":row["grid_runs"][-1]["species_events_C17"]}


def benchmark(root:Path,repeats=3,npackets=4096):
    ns=owner_namespace(root)
    model=ns["model"]
    a0,a1=.105,.1055
    dt=proper_dt(model,a0,a1,0.)
    E0=np.linspace(13.60,99.9,npackets)
    Ej=E0*(a0/a1)
    y=ns["nhe"]/(model.nh*125.)
    species=np.array([.9,y*.85,y*.15])
    L0=29979245800.*np.column_stack(
            [verner_sigma_array(E0,p) for p in ns["fit"]])*(model.nh/a0**3)*species
    L1=29979245800.*np.column_stack(
            [verner_sigma_array(Ej,p) for p in ns["fit"]])*(model.nh/a1**3)*species
    weights=np.asarray(ns["spec"].phi(E0),float)
    weights/=sum(weights)
    N=.02*weights
    s0=model.rate(a0)*weights
    s1=model.rate(a1)*weights
    x,old=optical_quadrature(N,s0,s1,L0,L1,dt)
    got,correct,initial_diag=species_resolved_affine(
                  N,s0,s1,L0,L1,dt,chunk=256)
    np.testing.assert_allclose(got,x,rtol=1e-13,atol=1e-14)
    np.testing.assert_allclose(got+correct.sum(axis=1),
              N+.5*dt*(s0+s1),rtol=1e-12,atol=1e-12)
    schemes={}
    for label,fn in (("C16_approx",lambda:optical_quadrature(N,s0,s1,L0,L1,dt)),
                     ("C17_species_64x48",lambda:species_resolved_affine(N,s0,s1,L0,L1,dt,chunk=256)),
                     ("C17_species_32x24",lambda:species_resolved_affine(N,s0,s1,L0,L1,dt,outer_nodes=32,inner_nodes=24,chunk=256))):
        samples=[]
        for _ in range(repeats):
            st=time.perf_counter()
            ret=fn()
            samples.append(time.perf_counter()-st)
            assert np.all(ret[0]>=0) and np.all(ret[1]>=0)
        schemes[label]={"wall_samples_s":samples,"median_s":float(np.median(samples))}
    jobs={}
    tasks=[(str(root),q) for q in (-.01,0.,.01)]
    expected=[q_task(t) for t in tasks]
    for n in (1,2,3):
        samples=[]
        for _ in range(repeats):
            st=time.perf_counter()
            if n==1:
                actual=[q_task(t) for t in tasks]
            else:
                with ProcessPoolExecutor(max_workers=n,mp_context=get_context("spawn")) as pool:
                    actual=list(pool.map(q_task,tasks))
            samples.append(time.perf_counter()-st)
            for a,b in zip(expected,actual):
                np.testing.assert_array_equal(a["new"],b["new"])
                np.testing.assert_array_equal(a["events"],b["events"])
        jobs[str(n)]={"wall_samples_s":samples,
                      "median_wall_s":float(np.median(samples))}
    return {
      "schema":"BASS_CR_C17_SPECIES_COMPETING_RATES_BENCHMARK_V1",
      "source":"owner C8 Scenario+Verner species and n_H(a), manufactured 4096-channel spectral state",
      "npackets":npackets,
      "proper_dt_seconds":dt,
      "schemes":schemes,
      "q_processing":jobs,
      "species_difference_C16_vs_C17_per_original_H":
            (correct-old).sum(axis=0).tolist(),
      "source_events_C17_per_original_H":correct.sum(axis=0).tolist(),
      "raw_moment_defects":initial_diag,
      "speed_policy":"different species accuracy, do not interpret C16/C17 latency as matched-accuracy speedup",
      "global_Rust_speedup":"NOT_MEASURED"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--repeats",type=int,default=3)
    args=p.parse_args()
    result=benchmark(args.owner,args.repeats)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({
       "kernel_seconds":{k:v["median_s"] for k,v in result["schemes"].items()},
       "three_q_seconds":{k:v["median_wall_s"] for k,v in result["q_processing"].items()},
       "species_diff":result["species_difference_C16_vs_C17_per_original_H"]
    },indent=2))
