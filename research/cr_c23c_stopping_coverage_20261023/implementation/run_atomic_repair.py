"""Run only the six changed N5 contract checks after the independent C9 findings."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import resource
import time

ROOT=Path(__file__).resolve().parents[1]


def main(run,cpu):
    os.sched_setaffinity(0,{cpu});start,c0=time.perf_counter(),time.process_time()
    path=ROOT/"theory/atomic_coverage/implementation/verify_atomic_repair.py"
    spec=importlib.util.spec_from_file_location("atomic_repair_checks",path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    r=m.run_checks()
    r.update(wall_s=time.perf_counter()-start,cpu_s=time.process_time()-c0,
             maxrss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             worker_cpu=cpu,native_threads=1,cpu55_used=False)
    for name,data in [("SUMMARY.json",r),("COMPLETE.json",{"status":"COMPLETE_SCOPED"})]:
        with (run/name).open("x") as f:json.dump(data,f,indent=2);f.write("\n")
    print(json.dumps(r,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--worker",type=Path,required=True);p.add_argument("--cpu",type=int,required=True);a=p.parse_args();main(a.worker,a.cpu)
