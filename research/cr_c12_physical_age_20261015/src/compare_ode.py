"""Independent DOP853 comparison: full source ages vs positive compressed ages.

The three signed q cases can be scheduled concurrently through OS processes;
this is not native agent delegation. Uses spawn to avoid unsafe inherited
OpenMP/BLAS thread state. All owners are read-only.
"""
from __future__ import annotations
import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path
import time
import numpy as np

from owner_age_bridge import owner_namespace
from physical_age import Gas, emission_packets
from independent_ode import solve_reference


def one_q(q:float, root:str, n_age:int) -> dict:
    ns=owner_namespace(Path(root))
    initial=Gas()
    train=(initial,Gas(.25,.25,.6,.15,1500.),Gas(.95,.8,.15,.05,400.))
    rows={}
    for mode in ("full","one","three"):
        start=time.perf_counter()
        packets,meta=emission_packets(ns,q,n_age,train,mode)
        result=solve_reference(ns,packets,initial,8e10)
        elapsed=time.perf_counter()-start
        rows[mode]={
            "final_gas":result["final_gas"],
            "reference_nfev":result["nfev"],
            "photon_number_residual":result["photons_residual"],
            "energy_residual_eV_per_H":result["energy_residual"],
            "retained_age_nodes":meta["retained_age_nodes"],
            "packet_bytes":meta["packet_bytes"],
            "npackets":meta["npackets"],
            "wall_seconds":elapsed,
            "original_photon_number_per_H":meta["source_photons_per_H"],
            "compression_training_relative_error":meta["training_relative_error"],
            "compression_numerics":meta["compression_numerics"],
        }
    reference=rows["full"]["final_gas"]
    for mode in ("one","three"):
        rows[mode]["relative_to_full_DOP853"]={
            k:float(rows[mode]["final_gas"][k]-reference[k])
            for k in reference}
    return {"q_ref":q,"age_count":n_age,"modes":rows}


def compare(root:Path,n_age:int=48,workers:int=1,qs=(-.01,0.,.01))->dict:
    if workers not in (1,2,3):
        raise ValueError("worker count must be 1/2/3")
    qs=tuple(map(float,qs))
    start=time.perf_counter()
    if workers==1:
        rows=[one_q(q,str(root),n_age) for q in qs]
    else:
        with ProcessPoolExecutor(max_workers=min(workers,len(qs)),
                                 mp_context=get_context("spawn")) as pool:
            rows=list(pool.map(one_q,qs,[str(root)]*len(qs),[n_age]*len(qs)))
    return {
        "schema":"CR_C12_WEIGHTED_SOURCE_DOP853_COMPARISON_V2",
        "source":"owner MD14-parameterized rate/H dln a; unattenuated age-dependent photon reservoir",
        "reference":"same local photon/photo H/He ODE, adaptive DOP853",
        "worker_count":workers,
        "wall_seconds":time.perf_counter()-start,
        "scientific_gate":"EXPLORATORY_ONLY",
        "results":rows,
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner",type=Path,required=True)
    ap.add_argument("--age",type=int,default=48)
    ap.add_argument("--workers",type=int,choices=(1,2,3),default=1)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    out=compare(args.owner,args.age,args.workers)
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    for row in out["results"]:
        print("q",row["q_ref"],"modes",[
            (m,row["modes"][m]["retained_age_nodes"],
             round(row["modes"][m]["wall_seconds"],3),
             row["modes"][m]["final_gas"]["xhi"],
             row["modes"][m]["final_gas"]["temp_K"])
            for m in ("full","one","three")],flush=True)
    print("wall_seconds",out["wall_seconds"],flush=True)
