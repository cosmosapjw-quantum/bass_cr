"""Create-only C23B source-frame campaign; no old ODE or provider rerun."""
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
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
THREAD_KEYS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
for key in THREAD_KEYS:
    os.environ[key] = "1"


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def digest(path):
    raw = Path(path).read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def rel(residual, scale):
    return abs(residual)/max(abs(scale), 1e-300)


def worker(run):
    os.sched_setaffinity(0, {1})
    start, cpu0 = time.perf_counter(), time.process_time()
    from boost_kernel import Boost, ElectronMeasure, ELECTRON_REST_EV, sum_moments
    from boosted_deposition import prepare_boosted
    from source_ledger import DecayClock
    from primary_source_assembly import assemble
    from vendor.fs2010_operator import FS2010Response
    pins = json.loads((run/"SOURCE_IDENTITY.json").read_text())
    for name, expected in pins["files"].items():
        if digest(ROOT/name) != expected:
            raise RuntimeError("SOURCE_CHANGED: "+name)
    contract = json.loads((run/"INPUT.json").read_text())
    model = FS2010Response(ROOT/"vendor/21cmFAST/tables", axis=contract["FS_axis"])
    maxima = {key: 0.0 for key, value in contract["acceptance_before_run"].items()
              if type(value) is float}
    rows, partitions, clocks = [], [], []
    positive, nulltails = True, True

    def inspect(prepared):
        nonlocal positive, nulltails
        partition = prepared.partition
        total = partition["all"]
        parts = sum_moments([partition[k] for k in ("below", "covered", "above")])
        metrics = {
            "number_partition_relative": rel(parts.number-total.number, total.number),
            "energy_partition_relative": rel(parts.kinetic_ev-total.kinetic_ev, total.kinetic_ev),
            "parallelpc_partition_scale_totalenergy": rel(parts.parallel_pc_ev-total.parallel_pc_ev, total.total_ev),
            "positive_basis_covered_number_relative": rel(math.fsum(prepared.number_basis)-partition["covered"].number, partition["covered"].number),
            "positive_basis_covered_energy_relative": rel(math.fsum(prepared.energy_basis)-partition["covered"].kinetic_ev, partition["covered"].kinetic_ev),
        }
        for key, value in metrics.items():
            maxima[key] = max(maxima[key], value)
        positive &= all(x >= 0 for x in (*prepared.number_basis, *prepared.energy_basis))
        for xi in contract["xi_queries"]:
            row = prepared.at(xi)
            row.update(ionized_fraction=xi)
            nulltails &= row["unresolved_tail_heat"] is None and row["unresolved_tail_ionization"] is None
            rows.append(row)
        partitions.append({"identity": prepared.source_identity, "boost_u": prepared.boost_u,
                           "moments": {k: v.as_tuple() for k, v in partition.items()},
                           "metrics": metrics, "overlap_cells": prepared.actual_overlap_cells})

    for item in contract["synthetic_rest_measures"]:
        energy = tuple(item["energies_eV"])
        weights = item.get("weights")
        if weights is None:
            high_weight = item["mean_eV"]/energy[-1]
            weights = [1-high_weight, high_weight]
        source = ElectronMeasure(energy, tuple(weights), "parent_rest", "electrons_per_event", item["id"])
        rest = source.total(Boost(0))
        for u in contract["boost_u_grid"]:
            boost = Boost(u)
            prepared = prepare_boosted(model, source, boost)
            inspect(prepared)
            for directions in ("isotropic", "equal_opposite_lrs_beams", "single_beam"):
                clock = DecayClock(2.5, 880.0, boost, 0.125, 1e13, 3.0)
                output = clock.electron_sources(source, parent_directions=directions)
                physical = output["physical_number_kinetic_total_parallelpc_per_m3_s"]
                expected_n = 2.5/880/boost.gamma*rest.number
                expected_total = 2.5/880*rest.total_ev
                expected_k = 2.5/880/boost.gamma*(rest.kinetic_ev+boost.gamma_minus_one*rest.total_ev)
                expected_pc = 2.5/880*boost.beta*rest.total_ev if directions == "single_beam" else 0.0
                error = max(rel(physical[0]-expected_n, expected_n), rel(physical[1]-expected_k, expected_k),
                            rel(physical[2]-expected_total, expected_total), rel(physical[3]-expected_pc, expected_total))
                maxima["clock_identity_relative"] = max(maxima["clock_identity_relative"], error)
                clocks.append({"identity":item["id"], "boost_u":u, "directions":directions,
                               "normalization_error":error, "source":output})

    # Consume the already completed C23B source quadrature, never rerun it.
    atom_path = ROOT/contract["saved_PW19_atoms"]["relative_path"]
    expected = contract["saved_PW19_atoms"]
    if digest(atom_path) != {"bytes": expected["bytes"], "sha256": expected["sha256"]}:
        raise RuntimeError("SAVED_PW19_ATOM_IDENTITY_MISMATCH")
    groups = {}
    with atom_path.open(newline="") as f:
        for row in csv.DictReader(f):
            key = (float(row["redshift"]), row["channel"])
            groups.setdefault(key, [[], []])
            groups[key][0].append(float(row["kinetic_eV"]))
            groups[key][1].append(float(row["number_weight_per_target_s"]))
    cases = json.loads((atom_path.parent/"CASES.json").read_text())
    by_case = {(c["redshift"], c["channel"]): c for c in cases}
    for key, (energies, weights) in groups.items():
        identity = f"PW19_release_z{key[0]}_{key[1]}_bath_source"
        source = ElectronMeasure(tuple(energies), tuple(weights), "bath", "electrons_per_target_per_second", identity)
        actual = source.total(Boost(0))
        saved = by_case[key]["result"]
        maxima["saved_source_moment_relative"] = max(maxima["saved_source_moment_relative"],
            rel(actual.number-saved["number_per_target_s"], saved["number_per_target_s"]),
            rel(actual.kinetic_ev-saved["kinetic_eV_per_target_s"], saved["kinetic_eV_per_target_s"]))
        prepared = prepare_boosted(model, source, Boost(0))
        inspect(prepared)

    assembled = []
    for redshift in sorted({c["redshift"] for c in cases}):
        selected = [c for c in cases if c["redshift"] == redshift]
        for label, population in contract["source_assembly_inventory"].items():
            item = assemble(selected, population)
            item["inventory_label"] = label
            total_rate = item["electron_number_source_per_reference_s"]
            maxima["charge_and_nuclei_relative"] = max(maxima["charge_and_nuclei_relative"],
                *(rel(item[k], total_rate) for k in ("hydrogen_nucleus_source_residual", "helium_nucleus_source_residual", "charge_source_residual")))
            maxima["primary_energy_ledger_relative"] = max(maxima["primary_energy_ledger_relative"],
                rel(item["energy_source_residual"], item["photon_absorption_eV_per_reference_s"]))
            assembled.append(item)

    guards = []
    def reject(label, function):
        try:
            function()
        except (ValueError, TypeError, ArithmeticError):
            guards.append({"guard":label, "PASS":True})
        else:
            guards.append({"guard":label, "PASS":False})
    for label, value in (("negative", -1), ("nan", float("nan")), ("infinity", float("inf")), ("bool", True)):
        reject("boost_"+label, lambda value=value: Boost(value))
    reject("negative_atom", lambda: ElectronMeasure((-1,), (1,), "parent_rest", "electrons_per_event", "bad"))
    reject("negative_weight", lambda: ElectronMeasure((1,), (-1,), "parent_rest", "electrons_per_event", "bad"))
    reject("unknown_frame", lambda: ElectronMeasure((1,), (1,), "unknown", "electrons_per_event", "bad"))
    reject("unknown_units", lambda: ElectronMeasure((1,), (1,), "parent_rest", "eV", "bad"))
    reject("absent_identity", lambda: ElectronMeasure((1,), (1,), "parent_rest", "electrons_per_event", ""))
    bath = ElectronMeasure((20,), (1,), "bath", "electrons_per_target_per_second", "guard")
    reject("double_boost_bath", lambda: bath.total(Boost(.1)))
    reject("bath_decay_clock", lambda: DecayClock(1,1,Boost(0),1,1,1).electron_sources(bath, parent_directions="isotropic"))
    reject("unresolved_zero_reference", lambda: DecayClock(1,1,Boost(0),1,1,0))
    reject("zero_fill_absent_population", lambda: assemble(cases[:3], {"HI":1}))
    reject("mixed_source_epoch", lambda: assemble([cases[0],cases[4],cases[8]], contract["source_assembly_inventory"]["neutral_fit_labels"]))
    reject("FS_extrapolation", lambda: model.at(100, .05))
    reject("physical_FS_missing_composition", lambda: model.require_physical_coupling(x_HII=.1,x_HeII=.1,x_HeIII=0,source_He_over_H=None,model_He_over_H=.083,closure_resolved=False))

    checks = {key: maxima[key] <= contract["acceptance_before_run"][key] for key in maxima}
    checks.update(all_basis_weights_nonnegative=positive, tail_heating_must_remain_null=nulltails,
                  guards=all(g["PASS"] for g in guards), saved_atom_count=sum(len(x[0]) for x in groups.values())==expected["count"],
                  source_assembly_count=len(assembled)==6, contraction_count=len(partitions)==49)
    write_json(run/"FINITE_TABLE_RESPONSES.json", rows)
    write_json(run/"PARTITIONS.json", partitions)
    write_json(run/"CLOCKS.json", clocks)
    write_json(run/"PRIMARY_SOURCE_ASSEMBLY.json", assembled)
    write_json(run/"GUARDS.json", guards)
    summary = {"run_id":run.name, "status":"PASS_SCOPED" if all(checks.values()) else "FAIL",
        "maxima":maxima, "checks":checks, "new_contractions":len(partitions), "table_queries":len(rows),
        "new_clock_evaluations":len(clocks), "new_primary_source_assemblies":len(assembled),
        "consumed_saved_PW19_atoms":sum(len(x[0]) for x in groups.values()), "guard_count":len(guards),
        "source_quadratures_reexecuted":0, "completed_calculation_reruns":0, "new_ODE":0,
        "wall_s":time.perf_counter()-start, "cpu_s":time.process_time()-cpu0,
        "maxrss_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "affinity":sorted(os.sched_getaffinity(0)), "native_threads":{k:os.environ[k] for k in THREAD_KEYS},
        "finished_utc":datetime.now(timezone.utc).isoformat(), "global_error_bound":None,
        "physical_FS_coupling":"NOT_ADMITTED", "thermal_heating_assembly":"OPEN"}
    write_json(run/"SUMMARY.json",summary)
    write_json(run/"COMPLETE.json",{"status":summary["status"],"files":{p.name:digest(p) for p in run.iterdir() if p.is_file()}})
    print(json.dumps(summary,ensure_ascii=False))
    return 0 if all(checks.values()) else 2


def dispatch(run_id):
    if not run_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for c in run_id):
        raise ValueError("explicit lowercase create-only run ID required")
    sys.path.insert(0,str(ROOT/"runtime"))
    from resource_control import observe_resources
    observed = observe_resources()
    run = ROOT/"runs"/run_id
    run.mkdir(parents=True, exist_ok=False)
    write_json(run/"RESOURCE_OBSERVED.json", observed)
    spare, memory = observed.get("cpu_quota_spare_cores"), observed.get("memory_available_bytes")
    if not {0,1}.issubset(os.sched_getaffinity(0)) or spare is None or memory is None or not observed.get("memory_observation_complete") or spare < 1.2 or memory < 768*1024**2:
        write_json(run/"BLOCKED.json",{"status":"NOT_RUN_RESOURCE_BLOCKED","new_ODE":0})
        raise RuntimeError("CURRENT_CPU_OR_MEMORY_NOT_ADMITTED")
    lease_dir = Path("/tmp/rei-bianchi-cooperative-leases")
    lease_dir.mkdir(exist_ok=True)
    lease_path = lease_dir/(run_id+".json")
    lease={"schema":"C21_CPU_LEASES_V1","leases":[{"owner":run_id,"cpus":[0,1],"pid":os.getpid()}]}
    with (lease_dir/"leases.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        seen=[]
        for path in lease_dir.glob("*.json"):
            doc=json.loads(path.read_text()); entries=doc.get("leases",[doc])
            if not isinstance(entries,list) or any(not isinstance(x,dict) or "cpus" not in x for x in entries):
                raise RuntimeError("UNKNOWN_LEASE_FORMAT: "+path.name)
            for item in entries:
                cpus=item["cpus"]
                if not isinstance(cpus,list) or any(type(c) is not int or c<0 for c in cpus):
                    raise RuntimeError("UNKNOWN_CPU_ENCODING: "+path.name)
                if {0,1}&set(cpus):raise RuntimeError("LEASE_CONFLICT: "+path.name)
            seen.append({"path":str(path),**digest(path)})
        write_json(lease_path,lease)
        write_json(run/"LEASE.json",dict(lease,other_leases=seen,coordinator_cpu=0,worker_cpu=1,protected_cpu55=True,native_threads=1))
    try:
        os.sched_setaffinity(0,{0})
        files=[str(p.relative_to(ROOT)) for p in ROOT.rglob("*.py") if "__pycache__" not in p.parts]
        files += ["CONTRACT.json"]+[str(p.relative_to(ROOT)) for p in (ROOT/"vendor/21cmFAST/tables").glob("*.dat")]
        provider="../source_providers/runs/c23b_pw19_spectral_source_20261023_v1/"
        files += [provider+"photoelectron_atoms.csv",provider+"CASES.json"]
        pins={name:digest(ROOT/name) for name in sorted(files)}
        write_json(run/"SOURCE_IDENTITY.json",{"files":pins,"source_identity_sha256":hashlib.sha256(json.dumps(pins,sort_keys=True,separators=(",",":")).encode()).hexdigest()})
        with (run/"INPUT.json").open("xb") as f:f.write((ROOT/"CONTRACT.json").read_bytes())
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),"--worker",str(run)],
                            env=os.environ.copy(),timeout=60,capture_output=True,text=True)
        with (run/"WORKER_STDOUT.txt").open("x") as f:f.write(proc.stdout)
        with (run/"WORKER_STDERR.txt").open("x") as f:f.write(proc.stderr)
        write_json(run/"DISPATCH_COMPLETE.json",{"returncode":proc.returncode,"timeout_s":60,"cpu55_used":False,"coordinator_cpu":0,"worker_cpu":1})
        print(proc.stdout)
        if proc.returncode: print(proc.stderr,file=sys.stderr)
        return proc.returncode
    except subprocess.TimeoutExpired as exc:
        write_json(run/"FAILED.json",{"class":"runtime","reason":"worker timeout60s","stdout":str(exc.stdout),"stderr":str(exc.stderr)})
        raise
    finally:
        with (lease_dir/"leases.lock").open("a+") as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if lease_path.exists() and json.loads(lease_path.read_text())==lease:
                lease_path.unlink()
        write_json(run/"LEASE_RELEASED.json",{"owner":run_id,"released_utc":datetime.now(timezone.utc).isoformat()})


if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--run-id");parser.add_argument("--worker",type=Path)
    args=parser.parse_args()
    sys.exit(worker(args.worker) if args.worker else dispatch(args.run_id))
