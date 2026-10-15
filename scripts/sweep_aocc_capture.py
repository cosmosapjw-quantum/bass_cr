"""Bounded exploratory single-impact-parameter capture sweep, not a b-grid gate."""
import argparse,json,time
from pathlib import Path
from cr_repro.aocc import OneElectronAOCC

def sweep(base):
    choices=[("baseline",{}),("np_plus1",{"np":int(base["np"])+1}),
             ("eps_max_half",{"eps_max":float(base["eps_max"])/2}),
             ("eps_max_double",{"eps_max":float(base["eps_max"])*2})]
    results=[]
    for name,updates in choices:
        cfg=dict(base,**updates)
        start=time.perf_counter()
        try:
            sol=OneElectronAOCC(cfg).run()
            results.append({"variant":name,"delta":updates,"wall_seconds":time.perf_counter()-start,
                            "status":"completed","P_projectile_bound":sol["P_projectile_bound"],
                            "P_target_bound":sol["P_target_bound"],"norm":sol["norm"],
                            "nbasis":sol["nbasis"],"nstep":sol["nstep"]})
        except Exception as exc:
            results.append({"variant":name,"delta":updates,"wall_seconds":time.perf_counter()-start,
                            "status":"error","error_type":type(exc).__name__,"message":str(exc)})
        print(results[-1],flush=True)
    return {"schema":"BASS_CR_EXPLORATORY_CAPTURE_SWEEP_V1","gate":"NOT_EVALUATED",
            "claim":"single-b exploratory, not production convergence","results":results}

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("config");ap.add_argument("--output",required=True)
    args=ap.parse_args();out=sweep(json.loads(Path(args.config).read_text()))
    Path(args.output).write_text(json.dumps(out,indent=2)+"\n")
