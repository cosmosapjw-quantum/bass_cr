"""Create-only strict native build; compilation is recorded separately from science."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

p=argparse.ArgumentParser()
p.add_argument("--output",type=Path,required=True)
p.add_argument("--receipt",type=Path,required=True)
a=p.parse_args()
source=Path(__file__).with_name("clock_kernel.cpp").resolve()
if a.output.exists() or a.receipt.exists():
    raise RuntimeError("CREATE_ONLY_NATIVE_BUILD")
a.output.parent.mkdir(parents=True,exist_ok=True)
a.receipt.parent.mkdir(parents=True,exist_ok=True)
command=["c++","-std=c++17","-O2","-shared","-fPIC","-fno-fast-math",
         "-ffp-contract=off","-frounding-math","-DCR_STRICT_BUILD=1","-DCR_LAPACK_LP64=1",
         str(source),"-o",str(a.output),"-l:liblapack.so.3","-l:libblas.so.3"]
before=resource.getrusage(resource.RUSAGE_CHILDREN)
start=time.monotonic()
def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(10,10))
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30,preexec_fn=limits)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
receipt={"schema":"CR_CLOCK_STRICT_NATIVE_BUILD_V1","command":command,"returncode":run.returncode,
         "stdout":run.stdout,"stderr":run.stderr,"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
         "compiler_cpu_s":after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
         "coordinator_cpu_s":time.process_time(),"wall_s":time.monotonic()-start,
         "compiler_peak_RSS_KiB":after.ru_maxrss,"build_scope":"CODE_PREPARATION; no scientific inputs loaded, no native entry called",
         "scientific_execution":False,"fast_math":False,"FMA_contraction":False}
if run.returncode==0:
    receipt["binary_sha256"]=hashlib.sha256(a.output.read_bytes()).hexdigest()
    receipt["binary_bytes"]=a.output.stat().st_size
    receipt["linked_libraries"]=subprocess.run(["ldd",str(a.output)],capture_output=True,text=True,check=True).stdout
with a.receipt.open("x") as f:
    json.dump(receipt,f,indent=2);f.write("\n")
print(json.dumps({k:receipt.get(k) for k in ("returncode","source_sha256","binary_sha256","binary_bytes","compiler_cpu_s","wall_s")}))
raise SystemExit(run.returncode)
