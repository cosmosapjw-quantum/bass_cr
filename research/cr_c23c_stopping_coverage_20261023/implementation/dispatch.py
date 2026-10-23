"""One create-only local job with observed admission and cooperative CPU lease."""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "implementation/runtime"))
from resource_control import choose_workers


def write(path, obj):
    with path.open("x") as f:
        json.dump(obj, f, indent=2); f.write("\n")


def digest(path):
    b=path.read_bytes()
    return {"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}


def dispatch(run_id, entry, timeout):
    if not run_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for c in run_id):
        raise ValueError("lowercase create-only run ID required")
    script=(ROOT/entry).resolve()
    if ROOT not in script.parents or not script.is_file():
        raise ValueError("entry must be an existing project script")
    if not 1 <= timeout <= 180:
        raise ValueError("bounded local timeout required")
    run=ROOT/"runs"/run_id; run.mkdir(parents=True,exist_ok=False)
    lease_dir=Path("/tmp/rei-bianchi-cooperative-leases");lease_dir.mkdir(exist_ok=True)
    own=lease_dir/(run_id+".json")
    with (lease_dir/"leases.lock").open("a+") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        foreign=[];observed=[]
        for p in lease_dir.glob("*.json"):
            d=json.loads(p.read_text());records=d.get("leases",[d]) if isinstance(d,dict) else d
            if not isinstance(records,list) or any(not isinstance(r,dict) or "cpus" not in r or
                    not isinstance(r["cpus"],list) or any(type(c) is not int or c<0 for c in r["cpus"]) for r in records):
                write(run/"BLOCKED.json",{"status":"NOT_RUN_RESOURCE_BLOCKED","reason":"UNKNOWN_FOREIGN_LEASE","path":str(p)})
                raise RuntimeError("unrecognized foreign lease; no worker started")
            foreign.extend({"owner":r.get("owner",p.stem),"cpus":r["cpus"]} for r in records)
            observed.append({"path":str(p),**digest(p)})
        write(run/"FOREIGN_LEASES.json",{"schema":"C21_CPU_LEASES_V1","leases":foreign})
        count,budget=choose_workers(1,requested=1,per_worker_mib=512,coordinator_mib=256,
                                   protected_cpus=(55,),lease_path=run/"FOREIGN_LEASES.json")
        write(run/"RESOURCE_ADMISSION.json",budget)
        if count!=1:
            write(run/"BLOCKED.json",{"status":"NOT_RUN_RESOURCE_BLOCKED","new_ODE":0})
            raise RuntimeError("current resource admission denied")
        coordinator=budget["coordinator_cpu"];cpu=budget["selected_worker_cpus"][0]
        lease={"schema":"C21_CPU_LEASES_V1","leases":[{"owner":run_id,"cpus":[coordinator,cpu],"pid":os.getpid()}]}
        write(own,lease)
        write(run/"LEASE.json",dict(lease,other_leases=observed,coordinator_cpu=coordinator,
                                    worker_cpu=cpu,native_threads=1,protected_cpu55=True))
    try:
        os.sched_setaffinity(0,{coordinator})
        paths=list((ROOT/"implementation").rglob("*.py")) + [ROOT/"CONTRACT.json",ROOT/"inputs/photoelectron_atoms.csv"]
        paths += list((ROOT/"theory/atomic_coverage/implementation").glob("*.py"))
        if script not in paths: paths.append(script)
        pins={str(p.relative_to(ROOT)):digest(p) for p in sorted(set(paths))}
        identity=hashlib.sha256(json.dumps(pins,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        write(run/"SOURCE_IDENTITY.json",{"files":pins,"execution_source_identity_sha256":identity})
        with (run/"INPUT.json").open("xb") as f:f.write((ROOT/"CONTRACT.json").read_bytes())
        env=os.environ.copy()
        for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","BLIS_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
            env[k]="1"
        command=[sys.executable,str(script),"--worker",str(run),"--cpu",str(cpu)]
        write(run/"COMMAND.json",{"command":command,"timeout_s":timeout,"utc":datetime.now(timezone.utc).isoformat()})
        start=time.perf_counter()
        proc=subprocess.run(command,env=env,capture_output=True,text=True,timeout=timeout)
        for name,body in [("WORKER_STDOUT.txt",proc.stdout),("WORKER_STDERR.txt",proc.stderr)]:
            with (run/name).open("x") as f:f.write(body)
        write(run/"DISPATCH_COMPLETE.json",{"returncode":proc.returncode,"wall_s":time.perf_counter()-start,
              "coordinator_cpu":coordinator,"worker_cpu":cpu,"native_threads":1,"cpu55_used":False})
        print(proc.stdout)
        if proc.returncode: print(proc.stderr,file=sys.stderr)
        return proc.returncode
    except subprocess.TimeoutExpired as exc:
        write(run/"FAILED.json",{"class":"runtime","reason":"worker timeout","timeout_s":timeout,
                                  "stdout":str(exc.stdout),"stderr":str(exc.stderr)})
        raise
    finally:
        with (lease_dir/"leases.lock").open("a+") as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if own.exists() and json.loads(own.read_text())==lease:own.unlink()
        write(run/"LEASE_RELEASED.json",{"owner":run_id,"utc":datetime.now(timezone.utc).isoformat()})


if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--run-id",required=True);a.add_argument("--entry",default="implementation/run_binding.py");a.add_argument("--timeout",type=int,default=90)
    p=a.parse_args();sys.exit(dispatch(p.run_id,p.entry,p.timeout))
