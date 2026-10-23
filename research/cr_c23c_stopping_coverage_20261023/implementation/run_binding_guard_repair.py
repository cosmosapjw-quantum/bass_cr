"""Target only C9 unhandled request fields; reuse the 18 valid-input results."""
import argparse
from dataclasses import asdict
from fractions import Fraction as F
import json
import os
from pathlib import Path
import resource
import time

ROOT=Path(__file__).resolve().parents[1]


def main(run,cpu):
    os.sched_setaffinity(0,{cpu})
    from source_cutoff_binding import SavedSupplier,bind
    start,c0=time.perf_counter(),time.process_time()
    source=SavedSupplier((ROOT/"inputs/photoelectron_atoms.csv").read_bytes())
    prior=json.loads((ROOT/"runs/c23c_source_cutoff_binding_20261023_v1/CASES.json").read_text())[0]
    req=prior["request"]
    checks=[]
    for key,value in [("preexisting_nonthermal_atoms",[]),("initial_free_electron_count","1"),("physical_heating_eV_per_s","0")]:
        try:bind(source,dict(req,**{key:value}))
        except ValueError as exc:checks.append({"name":key,"status":"PASS_REJECTED","reason":str(exc)})
        else:raise AssertionError(key)
    try:bind(source,[])
    except ValueError as exc:checks.append({"name":"nonobject_request","status":"PASS_REJECTED","reason":str(exc)})
    else:raise AssertionError("nonobject_request")
    valid=bind(source,req)
    state=asdict(valid.pop("state"));inv=valid.pop("inventory")
    # Validate unchanged values from the first saved candidate, without replaying the sweep.
    for key,value in state.items():
        expected=prior["state"][key]
        assert value==(F(expected) if isinstance(value,F) else expected),(key,value,expected)
    assert inv.common_count==F(prior["common_count"]) and inv.common_energy==F(prior["common_energy_eV"])
    checks.append({"name":"one_valid_changed_path","status":"PASS_EXACT_SAVED_ENDPOINT"})
    summary={"status":"PASS_SCOPED_FINDING_CLOSED","checks":checks,"checks_total":len(checks),
             "original_18_case_sweep_replayed":False,"source_quadratures":0,"new_ODE":0,
             "wall_s":time.perf_counter()-start,"cpu_s":time.process_time()-c0,
             "maxrss_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             "worker_cpu":cpu,"native_threads":1,"cpu55_used":False}
    for name,data in [("SUMMARY.json",summary),("COMPLETE.json",{"status":"COMPLETE_SCOPED"})]:
        with (run/name).open("x") as f:json.dump(data,f,indent=2);f.write("\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--worker",type=Path,required=True);p.add_argument("--cpu",type=int,required=True);a=p.parse_args();main(a.worker,a.cpu)
