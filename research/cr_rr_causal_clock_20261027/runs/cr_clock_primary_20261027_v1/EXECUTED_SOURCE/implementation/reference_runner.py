"""Run the separately authored reference in this frozen source snapshot."""
import os
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
p=argparse.ArgumentParser()
for name in ("unit","output","config","pins"):
    p.add_argument("--"+name,type=Path,required=True)
p.add_argument("--run-id",required=True)
a=p.parse_args()
pins=json.loads(a.pins.read_text())
record=next(x for x in pins["files"] if x["path"]=="REFERENCE_PLAN.json")
plan=a.unit/"REFERENCE_PLAN.json"
if hashlib.sha256(plan.read_bytes()).hexdigest()!=record["sha256"] or plan.stat().st_size!=record["bytes"]:
    raise RuntimeError("REFERENCE_PLAN_PIN")
script=Path(__file__).with_name("independent_reference.py")
sys.argv=[str(script),"--root-dir",str(a.unit),"--plan",str(plan),"--out-dir",str(a.output/"payload"),
          "--run-id",a.run_id,"--cpu-limit-s",os.environ["CR_CLOCK_WORKER_CPU_CAP_S"]]
runpy.run_path(str(script),run_name="__main__")
