"""Matched-formula NumPy vs owner scalar and 1/2/3-process scheduling benchmark."""
import argparse,json,time
from pathlib import Path
import numpy as np
from owner_age_bridge import owner_namespace,make_packets,run

def perf(root:Path,repeats:int):
    ns=owner_namespace(root)
    ages=np.geomspace(ns["model"].ar,.2,36)
    gas=(.6*ns["nh"],.75*ns["nhe"],.25*ns["nhe"])
    q=0.
    timings=[]
    for _ in range(repeats):
        t=time.perf_counter()
        slow=np.asarray([ns["vector"](float(a),q,gas) for a in ages])
        t_slow=time.perf_counter()-t
        t=time.perf_counter()
        fast=make_packets(ns,q,ages).response(np.asarray([gas]))[0]
        t_fast=time.perf_counter()-t
        sub=fast[:,[0,1,2,3]].copy()
        reduced=np.column_stack((sub,fast[:,5:8].sum(axis=1)))
        maxrel=float(np.max(np.abs(reduced-slow)/np.maximum(np.abs(slow),1e-14)))
        assert np.allclose(reduced,slow,rtol=4e-12,atol=1e-13),maxrel
        timings.append({'scalar_s':t_slow,'batched_s':t_fast,'max_relative_agreement':maxrel})
    parallel={}
    for w in (1,2,3):
        times=[]
        reference=None
        for _ in range(repeats):
            result=run(root,w)
            times.append(result["wall_seconds"])
            science=[[(k,v["weights"],v["holdout_max_error"]) for k,v in r["designs"].items()] for r in result["records"]]
            if reference is None:reference=science
            else:assert science==reference
        parallel[str(w)]={'times_s':times,'median_s':float(np.median(times))}
    med_scalar=float(np.median([x["scalar_s"] for x in timings]))
    med_batched=float(np.median([x["batched_s"] for x in timings]))
    return {
        'formula':'same owner source, gas, q and quadrature nodes',
        'scalar_batch':timings,'median_scalar_s':med_scalar,'median_batched_s':med_batched,
        'same_accuracy_kernel_speed_ratio':med_scalar/med_batched,
        'q_three_cases_process_count':parallel,
        'owner_source_sha256':run(root,1,qs=(0.,))['source_sha256'],
        'scientific_gate':'NOT_EVALUATED',
    }

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--rei-root',type=Path,required=True)
    p.add_argument('--repeats',type=int,default=3)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    res=perf(a.rei_root,a.repeats)
    a.out.parent.mkdir(exist_ok=True,parents=True)
    a.out.write_text(json.dumps(res,indent=2)+'\n')
    print(json.dumps({'speed_ratio':res['same_accuracy_kernel_speed_ratio'],
        'process_medians_s':{k:v['median_s'] for k,v in res['q_three_cases_process_count'].items()}},indent=2))
