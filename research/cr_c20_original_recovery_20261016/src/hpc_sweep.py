"""Bounded independent NCP Rust photon/source/threshold resolution benchmark.

The controller creates only JSON. Each native Rust child receives one CPU,
no oversubscribed OpenMP/BLAS, an input ID and wall limit. Existing NCP tasks
own the remaining CPUs. No background scientific job remains after return.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, pathlib, subprocess, time

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def make_cases():
    out=[]
    for a1 in (0.0891,0.0914,0.095):
        for n in (32,64,128,256,512,1024):
            out.append((a1,n,1,1))
    out.extend([(0.0914,1024,1,0),(0.0914,1024,0,1)])
    return out

def single(spec,bin,config,checkpoint,cpu):
    a,n,src,op=spec
    command=["taskset","-c",str(cpu),str(bin.resolve()),str(config),str(checkpoint),
             repr(a),str(n),str(src),str(op)]
    start=time.monotonic()
    r=subprocess.run(command,text=True,capture_output=True,timeout=150,check=False,
                     env={**os.environ,"OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1"})
    if r.returncode:
        return dict(case=spec,cpu=cpu,status="FAIL",exit_code=r.returncode,
                    stderr=r.stderr[:1800],seconds=time.monotonic()-start)
    try:
        v=json.loads(r.stdout)
        photon_scale=max(v["input_n"]+v["source_n"],1e-30)
        energy_scale=max(v["input_u_ev_h"]+v["source_u_ev_h"],1e-30)
        assert v["schema"]=="BASS_CR_C20_NATIVE_FLRW_VERER_COHORT_V1"
        assert abs(v["number_residual"])<=1e-11*photon_scale+2e-17
        assert abs(v["energy_residual_ev_h"])<=1e-11*energy_scale+2e-15
        assert min(v["species_events_per_h"])>=0
        assert min(v["species_heat_ev_h"])>=-1e-22
        assert v["photon_redshift_work_ev_h"]>=-1e-15
        assert v["time_gl4_s"]>0
    except (ValueError,KeyError,AssertionError) as e:
        return dict(case=spec,cpu=cpu,status="FAIL_SCIENCE_GATE",
                    message=str(e),output=r.stdout[:1200])
    return dict(case=spec,cpu=cpu,status="PASS_SCOPED",seconds=time.monotonic()-start,result=v)

def main():
    pa=argparse.ArgumentParser()
    for key in ("bin","config","checkpoint","out"):
        pa.add_argument("--"+key,type=pathlib.Path,required=True)
    pa.add_argument("--workers",type=int,default=8)
    pa.add_argument("--cpu-first",type=int,default=40)
    args=pa.parse_args()
    assert 1<=args.workers<=12
    available=os.sched_getaffinity(0)
    cpus=list(range(args.cpu_first,args.cpu_first+args.workers))
    if not all(c in available for c in cpus):raise ValueError("NCP affinity unavailable")
    specs=make_cases()
    started=time.monotonic()
    results={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        tasks={pool.submit(single,s,args.bin,args.config,args.checkpoint,
                    cpus[i%len(cpus)]):i for i,s in enumerate(specs)}
        for f in concurrent.futures.as_completed(tasks):
            results[tasks[f]]=f.result()
    ordered=[results[i] for i in range(len(specs))]
    final=dict(schema="C20_NCP64_SOURCE_CONDITIONAL_COHORT_SWEEP_V1",
      compute_host=os.uname().nodename,
      provenance=dict(binary_sha256=sha(args.bin),config_sha256=sha(args.config),
                      checkpoint_sha256=sha(args.checkpoint)),
      cpus=cpus,workers=args.workers,aggregate_wall_s=time.monotonic()-started,
      cases=ordered,pass_count=sum(d["status"]=="PASS_SCOPED" for d in ordered))
    args.out.write_text(json.dumps(final,indent=2)+"\n")
    print("C20_NCP_SWEEP",final["pass_count"],len(specs),"PASSED",final["aggregate_wall_s"],"s")
    if final["pass_count"]!=len(specs):
        for v in ordered:
            if v["status"]!="PASS_SCOPED":print("FAILED",v["case"],v.get("message",v.get("stderr")))
        raise SystemExit(2)
if __name__=="__main__": main()
