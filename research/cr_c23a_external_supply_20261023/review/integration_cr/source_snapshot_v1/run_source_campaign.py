"""Create-only, resource-admitted new frozen-source response campaign.

Examples: python run_source_campaign.py --run-id c23a_p19_subflow_20261023_v1
This is not a historical rerun, cosmological IVP, or a full thermochemical model.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
THREAD_KEYS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
for name in THREAD_KEYS:
    os.environ[name] = "1"


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")


def digest(path):
    data = Path(path).read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def worker(run):
    os.sched_setaffinity(0, {1})
    started, cpu0 = time.perf_counter(), time.process_time()
    import numpy as np
    from igm.p19_uvb import P19Fiducial
    from photo_subflow import advance, POPULATIONS, CHANNELS, KB_EV_K
    identity = json.loads((run / "SOURCE_IDENTITY.json").read_text())
    for filename, expected in identity["files"].items():
        if digest(ROOT / filename) != expected:
            raise RuntimeError("EXECUTION_SOURCE_CHANGED: " + filename)
    contract = json.loads((run / "INPUT.json").read_text())
    model = P19Fiducial()
    rows = []
    max_inventory = max_charge = max_energy = max_semigroup = 0.0
    for z in model.z_nodes:
        rates = model.evaluate(z)
        gammas = dict(zip(CHANNELS, rates.gamma_s_inv))
        heats = dict(zip(CHANNELS, rates.heat_ev_s_inv))
        for label, ic in contract["initial_conditions"].items():
            xs = ic["populations"]
            ne0 = xs["HII"]+xs["HeII"]+2*xs["HeIII"]
            particles0 = math.fsum(xs.values())+ne0
            u0 = 1.5*KB_EV_K*particles0*ic["temperature_K"]
            for dose in contract["max_rate_duration"]:
                dt = dose/max(gammas.values())
                args = (gammas, heats, contract["binding_ev"])
                out = advance(xs, u0, dt, *args)
                first = advance(xs, u0, dt/2, *args)
                second = advance(first.populations, first.thermal_energy_ev, dt/2, *args)
                sd = max(abs(out.populations[k]-second.populations[k]) for k in POPULATIONS)
                d = out.diagnostics
                max_inventory = max(max_inventory, abs(d["hydrogen_inventory_residual"]), abs(d["helium_inventory_residual"]))
                max_charge = max(max_charge, abs(d["charge_event_residual"]))
                max_energy = max(max_energy, abs(d["energy_event_residual_ev"])/max(1.0,out.imported_energy_ev))
                max_semigroup = max(max_semigroup, sd)
                row = dict(redshift=z, initial=label, max_rate_duration=dose, duration_s=dt,
                           temperature_K=out.temperature_K, initial_temperature_K=ic["temperature_K"],
                           heat_ev=out.heat_increment_ev, binding_ev=out.binding_increment_ev,
                           imported_ev=out.imported_energy_ev, U_ev=out.thermal_energy_ev,
                           electron_increment=out.electron_increment,
                           frozen_particle_temperature_K=2*out.thermal_energy_ev/(3*KB_EV_K*particles0),
                           semigroup_population_abs=sd,
                           hydrogen_residual=d["hydrogen_inventory_residual"],
                           helium_residual=d["helium_inventory_residual"],
                           charge_residual=d["charge_event_residual"],
                           energy_residual_ev=d["energy_event_residual_ev"])
                row.update(out.populations)
                row.update({"events_"+k:v for k,v in out.events.items()})
                row["nonnegative"] = int(d["nonnegative"])
                rows.append(row)
    with (run/"responses.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    with (run/"responses.npz").open("xb") as f:
        np.savez_compressed(f, **{k:np.array([r[k] for r in rows]) for k in rows[0]})
    limits = contract["acceptance_before_run"]
    checks = {
        "declared_new_exposure_count": len(rows)==contract["expected_new_source_subflows"],
        "nonnegative": all(r["nonnegative"] for r in rows),
        "H_He_inventory": max_inventory<=limits["absolute_inventory_residual_per_reference"],
        "electron_event_count": max_charge<=limits["absolute_charge_event_residual_per_reference"],
        "energy_event_ledger": max_energy<=limits["relative_energy_ledger_scale_max_1_ev"],
        "semigroup": max_semigroup<=limits["semigroup_absolute_population_per_reference"],
    }
    neutral_at1 = [r for r in rows if r["initial"]=="neutral" and r["max_rate_duration"]==1]
    summary = {
        "run_id":run.name, "status":"PASS_SCOPED" if all(checks.values()) else "FAIL",
        "finished_utc":datetime.now(timezone.utc).isoformat(), "checks":checks,
        "new_source_subflows":len(rows), "semigroup_comparison_subflows":2*len(rows),
        "new_cosmological_ODE":0, "historical_science_reruns":0,
        "maximum_inventory_absolute":max_inventory, "maximum_charge_absolute":max_charge,
        "maximum_energy_relative":max_energy, "maximum_semigroup_population_absolute":max_semigroup,
        "dose1_neutral_temperature_range_K":[min(r["temperature_K"] for r in neutral_at1),max(r["temperature_K"] for r in neutral_at1)],
        "max_frozen_particle_temperature_overestimate_ratio":max(r["frozen_particle_temperature_K"]/r["temperature_K"] for r in rows),
        "selected_rows":[r for r in rows if r["initial"]=="neutral" and r["redshift"] in (0.,3.,6.,10.,15.1) and r["max_rate_duration"] in (1.,100.)],
        "time_wall_s":time.perf_counter()-started,"time_cpu_s":time.process_time()-cpu0,
        "worker_affinity":sorted(os.sched_getaffinity(0)),"thread_env":{k:os.environ[k] for k in THREAD_KEYS},
        "global_error_bound":None,
        "scope":"Independent fixed-redshift response benchmark; exposures may exceed physical cosmic time, and are not time evolution of the IGM",
    }
    write_json(run/"SUMMARY.json", summary)
    write_json(run/"COMPLETE.json", {"status":summary["status"],"files":{p.name:digest(p) for p in run.iterdir() if p.is_file()}})
    print(json.dumps(summary,ensure_ascii=False))
    return 0 if all(checks.values()) else 2


def dispatch(run_id):
    if not run_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for c in run_id):
        raise ValueError("lowercase create-only run ID required")
    sys.path.insert(0,str(ROOT/"runtime"))
    from resource_control import observe_resources
    observed = observe_resources()
    run = ROOT/"runs"/run_id
    run.mkdir(parents=True,exist_ok=False)
    write_json(run/"RESOURCE_OBSERVED.json",observed)
    if not {0,1}.issubset(os.sched_getaffinity(0)):
        raise RuntimeError("COORDINATOR0_WORKER1_NOT_ADMITTED")
    spare, memory = observed.get("cpu_quota_spare_cores"), observed.get("memory_available_bytes")
    if spare is None or memory is None or not observed.get("memory_observation_complete") or spare < 1.2 or memory < 768*1024**2:
        write_json(run/"BLOCKED.json",{"status":"NOT_RUN_RESOURCE_BLOCKED","reason":"insufficient or unavailable current CPU/memory headroom","source_subflows":0})
        raise RuntimeError("INSUFFICIENT_OR_UNAVAILABLE_CURRENT_CPU_OR_MEMORY_HEADROOM")
    lease_dir = Path("/tmp/rei-bianchi-cooperative-leases")
    lease_dir.mkdir(exist_ok=True)
    lease_path = lease_dir/(run_id+".json")
    with (lease_dir/"leases.lock").open("a+") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        seen = []
        for p in lease_dir.glob("*.json"):
            doc = json.loads(p.read_text())
            entries = doc.get("leases",[doc])
            if not isinstance(entries,list) or any(not isinstance(x,dict) or "cpus" not in x for x in entries):
                raise RuntimeError("UNRECOGNIZED_LEASE: "+p.name)
            for item in entries:
                if not isinstance(item["cpus"],list) or any(type(c) is not int or c<0 for c in item["cpus"]):
                    raise RuntimeError("UNRECOGNIZED_CPU_ENCODING_WITHHOLDS_ALLOCATION: "+p.name)
                if {0,1}&set(item["cpus"]):
                    raise RuntimeError("LEASE_CPU_CONFLICT: "+p.name)
            seen.append({"path":str(p),"sha256":digest(p)["sha256"]})
        lease={"schema":"C21_CPU_LEASES_V1","leases":[{"owner":run_id,"cpus":[0,1],"pid":os.getpid()}]}
        write_json(lease_path,lease)
        write_json(run/"LEASE.json",dict(lease,observed_other_leases=seen,protected_cpu55=True,coordinator_cpu=0,worker_cpu=1,native_threads=1))
    try:
        os.sched_setaffinity(0,{0})
        source_files=["photo_subflow.py","run_source_campaign.py","CONTRACT.json","igm/p19_uvb.py","igm/sources/P19V1_rates_fiducial.txt","runtime/resource_control.py"]
        files={f:digest(ROOT/f) for f in source_files}
        identity={"files":files,"source_identity_sha256":hashlib.sha256(json.dumps(files,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"native_threads":1,"create_only":True}
        write_json(run/"SOURCE_IDENTITY.json",identity)
        with (run/"INPUT.json").open("xb") as f:f.write((ROOT/"CONTRACT.json").read_bytes())
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),"--worker",str(run)],env=os.environ.copy(),timeout=60,capture_output=True,text=True)
        with (run/"WORKER_STDOUT.txt").open("x") as f:f.write(proc.stdout)
        with (run/"WORKER_STDERR.txt").open("x") as f:f.write(proc.stderr)
        write_json(run/"DISPATCH_COMPLETE.json",{"returncode":proc.returncode,"worker_timeout_s":60,"cpu55_used":False,"coordinator_cpu":0,"worker_cpu":1})
        print(proc.stdout)
        if proc.returncode:print(proc.stderr,file=sys.stderr)
        return proc.returncode
    finally:
        # Only remove this process's exact owned lease; other owners remain intact.
        with (lease_dir/"leases.lock").open("a+") as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if lease_path.exists() and json.loads(lease_path.read_text())==lease:
                lease_path.unlink()
        write_json(run/"LEASE_RELEASED.json",{"owner":run_id,"released_utc":datetime.now(timezone.utc).isoformat()})


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--run-id");p.add_argument("--worker",type=Path)
    args=p.parse_args()
    sys.exit(worker(args.worker) if args.worker else dispatch(args.run_id))
