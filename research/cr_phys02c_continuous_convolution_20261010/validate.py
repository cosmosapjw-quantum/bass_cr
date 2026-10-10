"""One frozen campaign. Refuse to overwrite the first validation receipt."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[key] = "1"
import numpy as np
import scipy
import convolution as c

CASES = ((128,32,160),(256,32,320),(512,16,304),(512,32,608))
OUT = c.ROOT / "evidence"

def worker(case, method="sparse", cpu_limit=900., wall_limit=1800.):
    n, order, cap = case
    name = f"case_{n}_{order}_{method}"
    path = OUT / f"{name}.json"
    if path.exists():
        raise FileExistsError(path)
    progress = {"calls":0,"wall_s":0.,"cpu_s":0.}
    def update(calls, wall, cpu):
        progress.update(calls=calls, wall_s=wall, cpu_s=cpu)
        (OUT / f"{name}_PROGRESS.json").write_text(json.dumps(progress, indent=2)+"\n")
    try:
        result = c.integrate(n,order,method,call_cap=cap,cpu_limit=cpu_limit,
                             wall_limit=wall_limit,progress=update)
        result["status"] = "EXECUTED"
    except Exception as error:
        result = {"status":"HOLD_FIRST_FAILURE","exception":repr(error),**progress}
    path.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    return result

def scaled_diff(a,b,energy_only=False,relative=False):
    keys = c.ENERGIES if energy_only else c.OBSERVABLES
    rows = []
    for j in (0,1,"total"):
        oa,ob = (a["total"],b["total"]) if j == "total" else (a["branches"][j],b["branches"][j])
        scale = b["Ucross_eV"] if j == "total" else c.RESIDUAL[j]*b["analytic_C"][j]
        for key in keys:
            x,y = np.asarray(oa[key]),np.asarray(ob[key])
            denominator = np.maximum(abs(x),abs(y)) if relative else np.full_like(x,scale)
            value = np.divide(abs(x-y),denominator,out=np.zeros_like(x),where=denominator!=0)
            rows.append({"branch":j,"observable":key,"value":float(np.max(value))})
    return {"maximum":max(row["value"] for row in rows),"rows":rows}

def source_endpoint_check():
    packet = json.loads(c.A.PACKET.read_text())
    error = 0.
    for row in packet["rows"]:
        if row["initial_energy_eV"] == c.E0 and row["proper_time_s"] in (0,c.T):
            f,count,_ = c.source(row["proper_time_s"])
            for j,b in enumerate(row["boundary"]):
                if b["energy_meV"] != round(c.RESIDUAL[j]*1000):
                    raise ValueError("PACKET_ENDPOINT_RESIDUAL")
                for x,y in ((f[j],b["flux_per_initial_electron_per_s"]),
                            (count[j],b["cumulative_crossing_count_per_initial_electron"])):
                    error=max(error,abs(x-y)/max(abs(x),abs(y)) if x or y else 0.)
    return error

def main():
    OUT.mkdir(exist_ok=True)
    output = OUT / "VALIDATION.json"
    if output.exists():
        raise FileExistsError("FIRST_FAILURE_MUST_BE_PRESERVED")
    start = time.monotonic()
    receipt = {"id":"CR-PHYS02C-CONTINUOUS-CROSSING-CONVOLUTION01", "status":"RUNNING",
        "HARNESS_UNAVAILABLE":True,"command":[sys.executable,*sys.argv],
        "environment":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,"threads":1,"maximum_processes":4},
        "source_identities":{"P02B":c.A.P02B_SHA,"boundary_packet":c.A.PACKET_SHA},
        "implementation_sha256":hashlib.sha256(Path(c.__file__).read_bytes()).hexdigest(),
        "validator_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "physical_history":"HOLD","global_scientific_admission":"HOLD"}
    output.write_text(json.dumps(receipt,indent=2)+"\n")
    try:
        c.A.verify_inputs()
        receipt["endpoint_relative_error"] = source_endpoint_check()
        # Static admission: confirm frozen panel counts and SSPRK2 cap, no evolve.
        for n,order,cap in CASES:
            g = c.P.assemble(n)
            if (len(c.panels(g))-1)*order != cap:
                raise RuntimeError("HOLD_PANEL_COUNT_CONFLICT")
        g = c.P.assemble(128)
        if max(128,int(np.ceil(c.T*g.rho/.2))) > 256:
            raise RuntimeError("HOLD_SSPRK2_PREFLIGHT_CAP")
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(worker,CASES))
        receipt["cases"] = results
        if any(r["status"] != "EXECUTED" for r in results):
            raise RuntimeError("HOLD_FIRST_CASE_FAILURE")
        used_cpu = sum(r["cpu_s"] for r in results)
        if time.monotonic()-start >= 1800 or used_cpu >= 3600:
            raise RuntimeError("HOLD_AGGREGATE_BUDGET")
        rk = worker(CASES[0],"ssprk2",3600-used_cpu,1800-(time.monotonic()-start))
        receipt["time_reference"] = rk
        if rk["status"] != "EXECUTED":
            raise RuntimeError("HOLD_REFERENCE_FAILURE")
        birth = scaled_diff(results[2],results[3],relative=True)
        grid1 = scaled_diff(results[0],results[1],energy_only=True)
        grid2 = scaled_diff(results[1],results[3],energy_only=True)
        timing = scaled_diff(results[0],rk,energy_only=True)
        receipt.update(birth_order=birth,grid_refinement=[grid1,grid2],time_refinement=timing)
        source_err = number_err = energy_err = 0.
        for r in [*results,rk]:
            analytic = np.asarray(r["analytic_C"])
            source_err=max(source_err,float(np.max(abs(np.asarray(r["integrated_source"])-analytic)/analytic)))
            for b in r["branch_ledgers"]:
                number_err=max(number_err,abs(b["number"]-b["expected_number"])/b["expected_number"])
                energy_err=max(energy_err,abs(b["energy_eV"]-b["expected_energy_eV"])/b["expected_energy_eV"])
            number_err=max(number_err,abs(r["total_number_ledger"]-1))
            energy_err=max(energy_err,abs(r["total_energy_ledger_eV"]/c.E0-1))
        receipt["ledger_errors"]={"source":source_err,"number":number_err,"energy":energy_err}
        receipt["checks"]={"birth_order":birth["maximum"]<=3e-6,
            "grid":grid2["maximum"]<=.02 and grid2["maximum"]<grid1["maximum"],
            "time":timing["maximum"]<=2e-4,
            "ledgers":max(source_err,number_err,energy_err,receipt["endpoint_relative_error"])<=2e-11,
            "call_count":sum(r["calls"] for r in [*results,rk])==1552}
        receipt["status"]="PASS_SCOPED" if all(receipt["checks"].values()) else "FAIL_FIRST_CAMPAIGN"
    except Exception as error:
        receipt["status"]="HOLD_FIRST_FAILURE"
        receipt["exception"]=repr(error)
    receipt["aggregate_wall_s"]=time.monotonic()-start
    receipt["measured_child_cpu_s"]=sum(r.get("cpu_s",0) for r in receipt.get("cases",[]))+receipt.get("time_reference",{}).get("cpu_s",0)
    receipt["unmeasured_overhead"]="UNKNOWN_NOT_ZERO"
    output.write_text(json.dumps(receipt,indent=2,allow_nan=False)+"\n")
    print(json.dumps({k:receipt[k] for k in ("status","aggregate_wall_s","measured_child_cpu_s")}))
    return 0 if receipt["status"]=="PASS_SCOPED" else 1

if __name__=="__main__":
    raise SystemExit(main())
