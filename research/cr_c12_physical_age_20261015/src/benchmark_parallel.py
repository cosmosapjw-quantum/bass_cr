"""Repeat serial/spawn q sweep and enforce exact scientific outcome parity."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from compare_ode import compare


def bench(owner:Path,repeats:int,n_age:int):
    times={}
    serial=compare(owner,n_age,1)
    times["1"]=[serial["wall_seconds"]]
    for workers in (2,3):
        reps=[]
        for _ in range(repeats):
            other=compare(owner,n_age,workers)
            for a,b in zip(serial["results"],other["results"]):
                assert a["q_ref"]==b["q_ref"]
                for mode in ("full","one","three"):
                    assert a["modes"][mode]["retained_age_nodes"]==b["modes"][mode]["retained_age_nodes"]
                    for field in a["modes"][mode]["final_gas"]:
                        np.testing.assert_allclose(
                          a["modes"][mode]["final_gas"][field],
                          b["modes"][mode]["final_gas"][field],
                          rtol=2e-12,atol=1e-11)
            reps.append(other["wall_seconds"])
        times[str(workers)]=reps
    # Additional warmed serial repeated timings, equal science.
    for _ in range(repeats-1):
        again=compare(owner,n_age,1)
        times["1"].append(again["wall_seconds"])
    return {"schema":"CR_C12_OS_PROCESS_BENCHMARK_V1",
        "metric":"wall with fresh spawn and source injection; not solver-only",
        "n_age":n_age,"repeats":repeats,
        "seconds":times,
        "medians":{k:float(np.median(v)) for k,v in times.items()},
        "science_results":"per-mode final state matches serial at 2e-12 rtol",
        "parallelism":"separate OS processes, NOT native subagents"}


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--repeats",type=int,default=3)
    ap.add_argument("--age",type=int,default=48)
    args=ap.parse_args()
    out=bench(args.owner,args.repeats,args.age)
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"seconds":out["seconds"],"medians":out["medians"]},indent=2))
