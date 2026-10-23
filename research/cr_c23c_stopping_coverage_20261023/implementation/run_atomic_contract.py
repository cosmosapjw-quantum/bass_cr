"""Resource-run wrapper for new C23C atomic bookkeeping/coverage witnesses."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def main(run,cpu):
    os.sched_setaffinity(0,{cpu})
    for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","BLIS_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
        if os.environ.get(key)!="1":raise RuntimeError("native thread contract")
    t,c=time.perf_counter(),time.process_time()
    p=ROOT/"theory/atomic_coverage/implementation/verify_atomic_contract.py"
    spec=importlib.util.spec_from_file_location("atomic_checks",p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.run_checks()
    with (run/"ATOMIC_CONTRACT_CHECKS.json").open("x") as f:json.dump(result,f,indent=2);f.write("\n")
    summary={k:v for k,v in result.items() if k!="checks"}
    summary.update(wall_s=time.perf_counter()-t,cpu_s=time.process_time()-c,
                   maxrss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   worker_cpu=cpu,native_threads=1,cpu55_used=False)
    for name,data in [("SUMMARY.json",summary),("COMPLETE.json",{"status":"COMPLETE_SCOPED","new_ODE":0})]:
        with (run/name).open("x") as f:json.dump(data,f,indent=2);f.write("\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--worker",type=Path,required=True);p.add_argument("--cpu",type=int,required=True);a=p.parse_args();main(a.worker,a.cpu)
