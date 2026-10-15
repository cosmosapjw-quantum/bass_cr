"""C16 actual owner-opacity kernel and q-task process benchmarks."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
import numpy as np

from owner_age_bridge import owner_namespace,verner_sigma_array
from continuous_source import proper_dt
from endpoint_quadrature import endpoint_weighted,optical_quadrature
from owner_ray_benchmark import experiment


def q_task(args):
    root,q=args
    ns=owner_namespace(Path(root))
    start=time.perf_counter()
    res=experiment(ns,q,nsteps=(16,32,64,128),threshold_aware=True)
    err=[r["methods"]["C16_optical_quad"]["max_relative_photon_error"]
         for r in res["curves"]]
    return {"q":q,"error_series":err,
            "threshold_event_count":len(res["detected_events_scale_factor"]),
            "elapsed_s":time.perf_counter()-start}


def benchmark(root:Path,repeats=3,packets=4096):
    ns=owner_namespace(root)
    m=ns["model"]
    x=np.linspace(13.62,99.9,packets)
    w=np.asarray(ns["spec"].phi(x))
    w=w/np.sum(w)
    a0,a1=.105,.1052
    dt=proper_dt(m,a0,a1,0.)
    y=ns["nhe"]/(m.nh*125.)
    comp=np.array([.9,y*.85,y*.15])

    def rate(a):
        gas=m.nh/a**3*comp
        energy=x*(a0/a)
        sigma=np.column_stack([verner_sigma_array(energy,p) for p in ns["fit"]])
        return 29979245800.*sigma*gas[None,:]

    L0,L1=rate(a0),rate(a1)
    S0=m.rate(a0)*w
    S1=m.rate(a1)*w
    before=.01*w
    ref,refev=optical_quadrature(before,S0,S1,L0,L1,dt)
    fast,fastev=endpoint_weighted(before,S0,S1,L0,L1,dt)
    rel=float(np.max(abs(fast-ref)/np.maximum(abs(ref),1e-25)))
    timing={}
    for name,fn in (("endpoint_weighted",endpoint_weighted),
                    ("optical_quadrature",optical_quadrature)):
        runs=[]
        for _ in range(repeats):
            t=time.perf_counter()
            out,event=fn(before,S0,S1,L0,L1,dt)
            runs.append(time.perf_counter()-t)
            if not np.all(out>=0) or not np.all(event>=0):
                raise AssertionError("negative result")
            np.testing.assert_allclose(
                 out+event.sum(axis=1),
                 before+.5*dt*(S0+S1),rtol=2e-12,atol=1e-12)
        timing[name]={"runs_s":runs,"median_s":float(np.median(runs))}

    jobs={}
    args=[(str(root),q) for q in (-.01,0.,.01)]
    baseline=[q_task(x) for x in args]
    for n in (1,2,3):
        elapsed=[]
        for _ in range(repeats):
            t=time.perf_counter()
            if n==1:
                got=[q_task(x) for x in args]
            else:
                with ProcessPoolExecutor(max_workers=n,mp_context=get_context("spawn")) as pool:
                    got=list(pool.map(q_task,args))
            elapsed.append(time.perf_counter()-t)
            for a,b in zip(baseline,got):
                np.testing.assert_array_equal(a["error_series"],b["error_series"])
                assert a["q"]==b["q"]
        jobs[str(n)]={"wall_samples_s":elapsed,
                      "median_wall_s":float(np.median(elapsed))}

    return {
       "schema":"C16_ENDPOINT_OPTICAL_BENCHMARK_V1",
       "physical_source":"actual owner Verner HI/HeI/HeII and BB50000K spectrum; fixed controlled gas",
       "packet_count":packets,
       "proper_dt_seconds":dt,
       "vectorized_kernels":timing,
       "endpoint_relative_to_quad_max":rel,
       "q_3process_threshold_aware_Radau":jobs,
       "claim":"same source and photon ledger; fast vs quad have different error profiles; q processes scientifically equivalent",
       "production_Rust_speedup":"NOT_MEASURED"
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--repeats",type=int,default=3)
    opt=ap.parse_args()
    x=benchmark(opt.owner,opt.repeats)
    opt.out.parent.mkdir(parents=True,exist_ok=True)
    opt.out.write_text(json.dumps(x,indent=2)+"\n")
    print(json.dumps({
      "kernel_medians_s":{k:v["median_s"] for k,v in x["vectorized_kernels"].items()},
      "max_approx_rel":x["endpoint_relative_to_quad_max"],
      "q_process_medians_s":{k:v["median_wall_s"] for k,v in x["q_3process_threshold_aware_Radau"].items()}
    },indent=2))