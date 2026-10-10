"""One frozen source-convolution qualification, retaining its first result."""
from pathlib import Path
import hashlib
import json
import math
import platform
import sys
import time

import numpy as np
import scipy
from scipy.integrate import quad

import convolution as c


def main():
    started = time.perf_counter()
    cpu_started = time.process_time()
    output = c.ROOT / "evidence" / "VALIDATION.json"
    if output.exists():
        raise RuntimeError("FIRST_RESULT_ALREADY_EXISTS")
    checks = []
    def check(name, value, limit):
        row = {"id": name, "metric": float(value), "limit": limit,
               "status": "PASS" if np.isfinite(value) and value <= limit else "FAIL"}
        checks.append(row)
        print(json.dumps(row), flush=True)

    source = c.DirectSource(96)
    parts = source.partitions()
    partition_errors = []
    for field, total in parts["all"].items():
        summed = math.fsum(parts[band][field] for band in
                          ("below_10", "selected_10_1000", "above_1000"))
        partition_errors.append(float(c.relative(total, summed)))
    check("DIRECT_SOURCE_NUMBER_ENERGY_BINDING_PARTITIONS", max(partition_errors), 2e-12)

    direct_errors = []
    for energy in (0., 10., 100., 1000.):
        direct = 0.0
        for target, density in source.densities.items():
            def integrand(log_k):
                k = math.exp(log_k)
                return float(source.model.q_proper_m3_s_eV(k)*k
                             * source.rudd.proton_speed_m_s(k)*density
                             * source.rudd.dsigma_dW_m2_per_eV(k, energy, target))
            direct += quad(integrand, math.log(1e6), math.log(4e6),
                           epsabs=1e-80, epsrel=1e-11)[0]
        direct_errors.append(float(c.relative(direct, source.spectrum(energy))))
    check("RATIONAL_SOURCE_VS_RAW_SDCS_ADAPTIVE_INTEGRAL", max(direct_errors), 2e-10)

    bianchi_samples = source.bianchi_samples()
    check("LOCAL_RAMP_VS_BIANCHI_SAMPLES",
          max(value for row in bianchi_samples for errors in row["relative_by_target"].values()
              for value in errors), 3e-6)

    results = {}
    for grid, birth in ((128, 32), (256, 32), (512, 8), (512, 16), (512, 32)):
        print(f"START grid={grid} birth_order={birth}", flush=True)
        result = c.convolve(c.T_END, grid, birth)
        results[f"g{grid}_b{birth}"] = result
        print(f"DONE grid={grid} birth_order={birth}", flush=True)

    fields = [f for f in c.OBSERVABLES if f not in ("number_ledger", "energy_ledger_eV")]
    def values(result, index=1):
        return np.array([result["observables"][index][field] for field in fields])
    birth_coarse = c.relative(values(results["g512_b8"]), values(results["g512_b16"]))
    birth_fine = c.relative(values(results["g512_b16"]), values(results["g512_b32"]))
    check("BIRTH_TIME_16_TO_32_MAX_OBSERVABLE_RELATIVE", float(birth_fine.max()), 3e-6)
    check("SOURCE_64_TO_96_MAX_OBSERVABLE_RELATIVE",
          max(float(c.relative(values(row, 0), values(row, 1)).max()) for row in results.values()), 2e-7)

    injected = results["g512_b32"]["injected"][1]["kinetic_eV_m3"]
    def energy_values(result):
        return np.array([result["observables"][1][f] for f in c.ENERGY_FIELDS])
    coarse_grid = np.abs(energy_values(results["g128_b32"])-energy_values(results["g256_b32"]))/injected
    fine_grid = np.abs(energy_values(results["g256_b32"])-energy_values(results["g512_b32"]))/injected
    check("GRID_256_TO_512_ENERGY_FRACTION", float(fine_grid.max()), .02)
    check("GRID_FINE_MAX_DIFFERENCE_DECREASES", float(fine_grid.max() > coarse_grid.max()), 0)

    number_errors, energy_errors = [], []
    for result in results.values():
        for obs, inj in zip(result["observables"], result["injected"]):
            number_errors.append(float(c.relative(obs["number_ledger"], inj["number_m3"])))
            energy_errors.append(float(c.relative(obs["energy_ledger_eV"], inj["kinetic_eV_m3"])))
            energy_errors.append(float(c.relative(math.fsum(obs[f] for f in c.ENERGY_FIELDS), inj["kinetic_eV_m3"])))
    check("CONVOLVED_NUMBER_LEDGER", max(number_errors), 2e-11)
    check("CONVOLVED_ENERGY_LEDGER", max(energy_errors), 2e-11)
    check("NONNEGATIVE_COHORT_STATES", -min(result["minimum_state"] for result in results.values()), 0)
    check("CAUSAL_COHORT_AGES", max(max(-row["age_s"], row["age_s"]-c.T_END, 0)
                                   for result in results.values() for row in result["cohorts"]), 0)
    zero = c.convolve(0, 16, 8)
    off = c.convolve(c.T_END, 16, 8, False)
    check("T0_AND_SOURCE_OFF_EXACT_ZERO", max(abs(x) for result in (zero, off)
                                             for obs in result["observables"] for x in obs.values()), 0)
    status = "PASS_SCOPED" if all(row["status"] == "PASS" for row in checks) else "FAIL"
    report = {
        "id": "CR-PHYS05-FIRST-QUALIFICATION", "status": status,
        "scope": "Fixed 100K bath; direct-born 10-1000eV electrons from 1-4MeV proton source; local ramp Q=tA; no production or history admission",
        "checks": checks, "source_partitions_coefficients": parts,
        "source_partition_cumulative_at_endpoint": {
            band: {field.removesuffix("_s2"): .5*c.T_END**2*value for field, value in row.items()}
            for band, row in parts.items()},
        "source_sampling": bianchi_samples,
        "birth_refinement": {"fields": fields, "8_to_16_relative": birth_coarse.tolist(),
                             "16_to_32_relative": birth_fine.tolist()},
        "grid_refinement": {"fields": c.ENERGY_FIELDS, "128_to_256_energy_fraction": coarse_grid.tolist(),
                            "256_to_512_energy_fraction": fine_grid.tolist()},
        "results": results,
        "kernel_time_evidence_reused": "../cr_phys02b_delay_20261010/evidence/REPAIR_VALIDATION.json; unchanged sha-bound kernel; no new time-accuracy admission",
        "execution": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
                      "platform": platform.platform(), "wall_s": time.perf_counter()-started,
                      "cpu_s": time.process_time()-cpu_started, "cohorts": 120,
                      "command": "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/cr_phys05_source_convolution_20261010/validate.py",
                      "source_sha256": {name: hashlib.sha256((c.ROOT/name).read_bytes()).hexdigest()
                                        for name in ("convolution.py", "validate.py", "EXECUTION_CONTRACT.json")}},
        "independent_review": "NOT_RUN", "global_admission": "HOLD",
    }
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"status": status, "wall_s": report["execution"]["wall_s"],
                      "endpoint": results["g512_b32"]["observables"][1]}), flush=True)
    return 0 if status == "PASS_SCOPED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
