"""Exactly one arrival-panel repair; independent cases, ordered closeout."""
import argparse
import hashlib
import json
import math
import platform
import sys
import time

import numpy as np
import scipy

import convolution as c

CASES = {(128, 32): 160, (256, 32): 320, (512, 16): 304, (512, 32): 608}


def case_path(grid, birth):
    return c.ROOT / "evidence" / f"REPAIR_G{grid}_B{birth}.json"


def run_case(grid, birth):
    if (grid, birth) not in CASES:
        raise ValueError("REPAIR_CASE_BUDGET")
    path = case_path(grid, birth)
    if path.exists():
        raise RuntimeError("REPAIR_CASE_ALREADY_EXISTS")
    start, cpu = time.perf_counter(), time.process_time()
    result = c.convolve(c.T_END, grid, birth, panelized=True)
    if len(result["cohorts"]) != CASES[(grid, birth)]:
        raise ValueError("REPAIR_COHORT_CAP_OR_PANEL_MISMATCH")
    result["execution"] = {
        "wall_s": time.perf_counter()-start, "cpu_s": time.process_time()-cpu,
        "command": sys.argv, "python": sys.version, "numpy": np.__version__,
        "scipy": scipy.__version__, "platform": platform.platform(),
        "sources_sha256": {name: hashlib.sha256((c.ROOT/name).read_bytes()).hexdigest()
                           for name in ("convolution.py", "repair.py", "REPAIR_CONTRACT.json")},
    }
    path.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"case": [grid, birth], "cohorts": len(result["cohorts"]),
                      "wall_s": result["execution"]["wall_s"], "status": "EXECUTED"}), flush=True)


def closeout():
    path = c.ROOT / "evidence" / "REPAIR_VALIDATION.json"
    if path.exists():
        raise RuntimeError("REPAIR_CLOSEOUT_ALREADY_EXISTS")
    first_path = c.ROOT / "evidence" / "VALIDATION.json"
    contract = json.loads((c.ROOT / "REPAIR_CONTRACT.json").read_text())
    if hashlib.sha256(first_path.read_bytes()).hexdigest() != contract["first_failure_sha256"]:
        raise ValueError("FIRST_FAILURE_CHANGED")
    first = json.loads(first_path.read_text())
    results = {key: json.loads(case_path(*key).read_text()) for key in CASES}
    checks = []
    def check(name, value, limit):
        checks.append({"id": name, "metric": float(value), "limit": limit,
                       "status": "PASS" if np.isfinite(value) and value <= limit else "FAIL"})
    fields = [f for f in c.OBSERVABLES if f not in ("number_ledger", "energy_ledger_eV")]
    def values(result, index=1):
        return np.array([result["observables"][index][f] for f in fields])
    birth_delta = c.relative(values(results[(512, 16)]), values(results[(512, 32)]))
    check("PANEL_BIRTH_16_TO_32_MAX_OBSERVABLE_RELATIVE", birth_delta.max(), 3e-6)
    check("SOURCE_64_TO_96_MAX_OBSERVABLE_RELATIVE",
          max(float(c.relative(values(row, 0), values(row, 1)).max()) for row in results.values()), 2e-7)
    endpoint = results[(512, 32)]
    injected = endpoint["injected"][1]["kinetic_eV_m3"]
    def energies(key):
        return np.array([results[key]["observables"][1][f] for f in c.ENERGY_FIELDS])
    coarse = np.abs(energies((128, 32))-energies((256, 32)))/injected
    fine = np.abs(energies((256, 32))-energies((512, 32)))/injected
    check("PANEL_GRID_256_TO_512_ENERGY_FRACTION", fine.max(), .02)
    check("PANEL_GRID_FINE_DIFFERENCE_DECREASES", float(fine.max() > coarse.max()), 0)
    ne, ee = [], []
    for row in results.values():
        for obs, inj in zip(row["observables"], row["injected"]):
            ne.append(float(c.relative(obs["number_ledger"], inj["number_m3"])))
            ee += [float(c.relative(obs["energy_ledger_eV"], inj["kinetic_eV_m3"])),
                   float(c.relative(math.fsum(obs[f] for f in c.ENERGY_FIELDS), inj["kinetic_eV_m3"]))]
    check("CONVOLVED_NUMBER_LEDGER", max(ne), 2e-11)
    check("CONVOLVED_ENERGY_LEDGER", max(ee), 2e-11)
    check("NONNEGATIVE_COHORT_STATES", -min(row["minimum_state"] for row in results.values()), 0)
    check("CAUSAL_COHORT_AGES", max(max(-item["age_s"], item["age_s"]-c.T_END, 0)
                                   for row in results.values() for item in row["cohorts"]), 0)
    reused_ids = {"DIRECT_SOURCE_NUMBER_ENERGY_BINDING_PARTITIONS",
                  "RATIONAL_SOURCE_VS_RAW_SDCS_ADAPTIVE_INTEGRAL", "LOCAL_RAMP_VS_BIANCHI_SAMPLES",
                  "T0_AND_SOURCE_OFF_EXACT_ZERO"}
    reused = [row for row in first["checks"] if row["id"] in reused_ids]
    passed = all(row["status"] == "PASS" for row in checks+reused)
    report = {
        "id": "CR-PHYS05-REPAIR-CLOSEOUT-01", "status": "PASS_SCOPED" if passed else "FAIL",
        "checks": checks, "unchanged_source_zero_off_checks_reused": reused,
        "birth_refinement": {"fields": fields, "16_to_32_relative": birth_delta.tolist()},
        "grid_refinement": {"fields": c.ENERGY_FIELDS, "128_to_256_energy_fraction": coarse.tolist(),
                            "256_to_512_energy_fraction": fine.tolist()},
        "endpoint": endpoint["observables"][1], "selected_injected": endpoint["injected"][1],
        "cases": {f"g{g}_b{b}": {"file": str(case_path(g,b).relative_to(c.ROOT)),
                  "sha256": hashlib.sha256(case_path(g,b).read_bytes()).hexdigest(),
                  "cohorts": len(results[(g,b)]["cohorts"]),
                  "execution": results[(g,b)]["execution"]} for g,b in CASES},
        "repair_cohorts": sum(len(row["cohorts"]) for row in results.values()),
        "repair_cpu_s": sum(row["execution"]["cpu_s"] for row in results.values()),
        "repair_summed_process_wall_s": sum(row["execution"]["wall_s"] for row in results.values()),
        "first_failure_preserved_sha256": contract["first_failure_sha256"],
        "scope": first["scope"], "independent_review": "NOT_RUN", "global_admission": "HOLD",
        "next": "Independent review" if passed else "HOLD; repair budget exhausted",
    }
    path.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(json.dumps(report, indent=2), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", type=int)
    parser.add_argument("--birth-order", type=int)
    parser.add_argument("--closeout", action="store_true")
    args = parser.parse_args()
    if args.closeout:
        raise SystemExit(closeout())
    run_case(args.grid, args.birth_order)
