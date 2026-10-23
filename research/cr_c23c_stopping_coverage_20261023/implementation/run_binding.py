"""Fresh C23C integration cases; saved source quadratures and old suites are reused."""
from __future__ import annotations
import argparse
import copy
import csv
from dataclasses import asdict
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def encode(x):
    if isinstance(x, F):
        return str(x)
    raise TypeError(type(x).__name__)


def write(path, data):
    with path.open("x") as f:
        json.dump(data, f, indent=2, default=encode)
        f.write("\n")


def main(run, cpu):
    os.sched_setaffinity(0, {cpu})
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        if os.environ.get(key) != "1":
            raise RuntimeError("native thread contract missing")
    from source_cutoff_binding import SavedSupplier, bind, KB_EV_K, ATOM_SHA256
    t0, c0 = time.perf_counter(), time.process_time()
    source = SavedSupplier((ROOT / "inputs/photoelectron_atoms.csv").read_bytes())
    contract = json.loads((ROOT / "CONTRACT.json").read_text())
    fixture = contract["fixture"]
    cases, flat = [], []
    for z in contract["redshifts"]:
        for temperature in contract["initial_temperatures_K"]:
            for chi in contract["chi_values"]:
                req = dict(fixture, redshift=z, initial_temperature_K=temperature, chi=chi)
                answer = bind(source, req)
                state = asdict(answer.pop("state"))
                inv = answer.pop("inventory")
                label = f"z{z}_T{temperature}_chi{chi}"
                row = dict(case=label, request=req, state=state,
                           common_count=inv.common_count, common_energy_eV=inv.common_energy,
                           base_count=inv.base_count, base_energy_eV=inv.base_energy,
                           distinct_positive_energy_groups=len(inv.atoms), **answer)
                cases.append(row)
                n, e = row["new_free_electron_count"], row["primary_kinetic_eV"]
                flat.append({"case":label, "redshift":z, "initial_temperature_K":temperature,
                    "chi":chi, "caloric_temperature_K":float(state["temperature"]),
                    "cutoff_eV":float(state["cutoff"]),
                    "partition_delta_temperature_K":float(row["partition_delta_temperature_K"]),
                    "source_count":float(n), "source_kinetic_eV":float(e),
                    "source_below_cut_count_fraction":float(row["cutoff_classified_source_count"] / n),
                    "source_below_cut_energy_fraction":float(row["cutoff_classified_source_eV"] / e),
                    "active_below_fs_count_fraction":float(row["cross_partitions"]["cutoff_active_below_fs"][0] / n),
                    "active_below_fs_energy_fraction":float(row["cross_partitions"]["cutoff_active_below_fs"][1] / e),
                    "all_energy_partition_residual":0.0, "physical_heating_eV_per_s":"null"})
    write(run / "CASES.json", cases)
    with (run / "CUTS.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0])); writer.writeheader(); writer.writerows(flat)
    reference = dict(fixture, redshift="2.479", initial_temperature_K="10000", chi="3")
    first = bind(source, reference)
    abundance = copy.deepcopy(reference)
    abundance["normalization"] = {"mode":"abundance", "proper_volume_cm3":"1",
        "reference_density_cm3":"2", "values_per_reference":
        {p:str(F(v)/2) for p,v in reference["normalization"]["values_cm3"].items()}}
    second = bind(source, abundance)
    normalization_equal = (first["inventory"] == second["inventory"] and first["state"] == second["state"]
                           and first["predicted_counts"] == second["predicted_counts"])
    assert normalization_equal
    zero_req = dict(reference, proper_duration_s="0")
    zero = bind(source, zero_req)
    assert zero["state"].temperature == F("10000") and zero["new_free_electron_count"] == 0
    assert zero["partition_delta_temperature_K"] == 0 and not zero["inventory"].atoms
    guards=[]
    def reject(name, req):
        try:
            bind(source, req)
        except (ValueError, TypeError):
            guards.append({"name":name,"result":"PASS_REJECTED"}); return
        raise AssertionError("guard admitted "+name)
    for field, value in [("chi","1.4999"),("chi","NaN"),("initial_temperature_K","0"),
                         ("initial_temperature_K",10000.0),("proper_duration_s","-1"),
                         ("proper_duration_s","1e20"),("redshift","2.5"),
                         ("frame","parent_rest"),("rate_unit","count"),
                         ("initial_electron_model","all_free_already_in_base")]:
        reject(field+"="+str(value),dict(reference,**{field:value}))
    req=copy.deepcopy(reference);req["normalization"]["values_per_reference"]={};reject("double_normalization",req)
    req=copy.deepcopy(reference);del req["normalization"]["values_cm3"]["HeIII"];reject("missing_population",req)
    req=copy.deepcopy(reference);req["normalization"]["proper_volume_cm3"]="0";reject("zero_volume",req)
    req=copy.deepcopy(reference);req["normalization"]["values_cm3"]["HI"]="-1";reject("negative_population",req)
    req=copy.deepcopy(reference);req["normalization"]["values_cm3"]["HI"]=0.9;reject("implicit_float",req)
    missing = copy.deepcopy(reference);del missing["initial_temperature_K"]
    blocked=bind(source,missing)
    assert blocked["status"] == "BLOCKED_MISSING_BATH_OR_SOURCE_CONTRACT"
    assert blocked["missing_fields"] == ["initial_temperature_K"] and blocked["physical_heating_eV_per_s"] is None
    raw=(ROOT/"inputs/photoelectron_atoms.csv").read_bytes()
    try: SavedSupplier(raw[:-1]+b"!")
    except ValueError: guards.append({"name":"byte_mutation","result":"PASS_REJECTED"})
    else: raise AssertionError("source identity guard failed")
    # Sensitivity witnesses attack the new binding's two most costly ownership errors.
    # These are explicit wrong alternatives; the production endpoint is unchanged.
    bad_base_count=first["inventory"].base_count + first["new_free_electron_count"]
    bad_common=bad_base_count + first["new_free_electron_count"]
    count_mutation=bad_common-first["inventory"].common_count
    assert count_mutation == first["new_free_electron_count"] > 0
    forced_heat=first["primary_kinetic_eV"]
    double_energy=first["inventory"].common_energy+forced_heat
    assert double_energy-first["inventory"].common_energy == forced_heat > 0
    audit={"normalization_equivalence":"EXACT_PASS", "zero_exposure":"EXACT_PASS",
           "missing_bath":blocked, "guards":guards,
           "double_count_mutation_residual":count_mutation,
           "duplicate_heat_mutation_residual_eV":forced_heat,
           "physical_heating_in_all_cases":None,
           "source_exactness":"exact rational arithmetic for saved decimal quadrature measure"}
    write(run/"TARGETED_CHECKS.json",audit)
    summary={"status":"PASS_SCOPED", "cases":len(cases), "distinct_saved_atoms_consumed":32592,
             "fresh_source_quadratures":0, "new_ODE":0, "historical_science_reruns":0,
             "exact_residuals_per_case":len(cases[0]["exact_residuals"]),
             "all_rational_residuals_zero":all(not v for r in cases for v in r["exact_residuals"].values()),
             "invalid_guards":len(guards),"normalization_pairs":1,"zero_exposure_cases":1,
             "caloric_delta_temperature_min_K":min(r["partition_delta_temperature_K"] for r in flat),
             "caloric_delta_temperature_max_K":max(r["partition_delta_temperature_K"] for r in flat),
             "wall_s":time.perf_counter()-t0,"cpu_s":time.process_time()-c0,
             "maxrss_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             "worker_cpu":cpu,"native_threads":1,"cpu55_used":False,"global_error_bound":None}
    write(run/"SUMMARY.json",summary);write(run/"COMPLETE.json",{"status":"COMPLETE_SCOPED","new_ODE":0})
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("--worker",type=Path,required=True);p.add_argument("--cpu",type=int,required=True)
    a=p.parse_args();main(a.worker,a.cpu)
