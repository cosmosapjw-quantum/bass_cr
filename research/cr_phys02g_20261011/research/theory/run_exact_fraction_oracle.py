#!/usr/bin/env python3
"""Create-only, deadline-bounded coordinator for the one exact candidate oracle."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


def utc():
    return datetime.now(timezone.utc).isoformat()


def identity(path):
    data=path.read_bytes()
    return {"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}


def main():
    here=Path(__file__).resolve().parent
    unit=here.parents[1]
    reservation=here/"EXACT_FRACTION_ORACLE_RESERVATION.json"
    receipt=here/"EXACT_FRACTION_ORACLE_RECEIPT.json"
    result=here/"EXACT_FRACTION_ORACLE.json"
    stdout=here/"EXACT_FRACTION_ORACLE.stdout.txt"
    stderr=here/"EXACT_FRACTION_ORACLE.stderr.txt"
    for path in [reservation,receipt,result,stdout,stderr]:
        if path.exists():
            raise SystemExit("create-only execution artifact exists: "+str(path))
    command=[sys.executable,str(here/"exact_fraction_oracle.py"),"--output",str(result)]
    sources={
        str(path.relative_to(unit)):identity(path)
        for path in [
            here/"exact_fraction_oracle.py",Path(__file__).resolve(),
            here/"MOMENT_ENVELOPES_DERIVATION_KO.md",here/"SOURCE_POINTERS.json",
            unit/"state/SCIENTIFIC_CONTRACT.json",
            unit/"state/VALIDATION_CONTRACT.json",
            unit/"ncp/NCP_EXECUTION_CONTRACT.json"
        ]
    }
    reserved_utc=utc()
    with reservation.open("x",encoding="utf-8") as out:
        json.dump({"schema":"cr-phys02g-exact-oracle-reservation.v1",
                   "reserved_utc":reserved_utc,"max_runs":1,"retry":False,
                   "max_wall_s":120,"command":command,"source_identity":sources},
                  out,ensure_ascii=False,indent=2)
        out.write("\n")
    start_utc=utc()
    start=time.perf_counter()
    timed_out=False
    exception=None
    actual_exit=None
    with stdout.open("xb") as out,stderr.open("xb") as err:
        try:
            child=subprocess.Popen(command,cwd=unit,stdout=out,stderr=err)
            try:
                actual_exit=child.wait(timeout=120)
            except subprocess.TimeoutExpired:
                timed_out=True
                child.kill()
                actual_exit=child.wait()
        except BaseException as exc:
            exception={"type":type(exc).__name__,"message":str(exc)}
    end=time.perf_counter()
    end_utc=utc()
    row={"schema":"cr-phys02g-exact-oracle-execution.v1",
         "role":"candidate_theory_contributor_not_independent_review",
         "status":"COMPLETED" if actual_exit==0 else "FAILED",
         "reserved_utc":reserved_utc,"started_utc":start_utc,"ended_utc":end_utc,
         "wall_s":end-start,"actual_exit":actual_exit,"timed_out":timed_out,
         "exception":exception,"execute_calls":1,"retry":False,"deadline_s":120,
         "command":command,"cwd":str(unit),"python":platform.python_version(),
         "source_identity":sources,"raw_stdout":identity(stdout),
         "raw_stderr":identity(stderr),"result":identity(result) if result.exists() else None,
         "physical_G":0,"physical_pulse":0,"expm":0,"linear_solves":0,
         "actual_cached_analysis":0}
    with receipt.open("x",encoding="utf-8") as out:
        json.dump(row,out,ensure_ascii=False,indent=2)
        out.write("\n")
    print(json.dumps(row,ensure_ascii=False))
    return 0 if actual_exit==0 else 1


if __name__=="__main__":
    raise SystemExit(main())
