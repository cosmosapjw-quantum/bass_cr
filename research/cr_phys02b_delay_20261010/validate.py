"""Run the frozen CR-PHYS02B finite-generator validation and preserve a receipt."""

import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy

import causal_generator as c


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else c.ROOT / "evidence/VALIDATION.json"
    if output.exists():
        raise FileExistsError(f"Preserve existing evidence: {output}")
    wall0, cpu0 = time.monotonic(), time.process_time()
    contract = json.loads((c.ROOT / "CONTRACT.json").read_text())
    ac = contract["acceptance"]
    energies, times = ac["impulses_eV"], ac["times_s"]
    result = {
        "id": contract["id"], "status": "RUNNING",
        "command": [sys.executable, *sys.argv],
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__},
        "inputs": {p: digest(c.ROOT / p) for p in ("CONTRACT.json", "REPAIR_CONTRACT.json", "SOURCE_MANIFEST.json",
                                                  "causal_generator.py", "validate.py")},
        "scope": "Fixed-gas conditional old-method finite-generator impulse experiment only",
        "histories": [], "checks": {},
        "full_CR_PHYS02": "HOLD_SOURCE_CONVOLUTION_AND_10_8700_EV_DOMAIN_ABSENT",
        "global_scientific_admission": "HOLD",
    }
    try:
        generators = [c.assemble(n) for n in ac["grid_intervals"]]
        all_channels = []
        max_e_err = max_n_err = 0.
        minimum = 0.
        for resolution, g in zip(ac["grid_intervals"], generators):
            initial = np.column_stack([g.impulse(e) for e in energies])
            channels = []
            # All frozen impulses share the same characteristic/collision map.
            for t in times:
                states = c.evolve(g, initial, t)
                row = []
                for k, e in enumerate(energies):
                    y = states[:, k]
                    obs = g.observe(y)
                    max_e_err = max(max_e_err, abs(obs["energy_ledger_eV"] / e - 1))
                    max_n_err = max(max_n_err, abs(obs["number_ledger"] - 1))
                    minimum = min(minimum, obs["minimum_state"])
                    row.append(c.energy_channels(g, y) / e)
                    result["histories"].append({"grid_intervals": resolution,
                                                 "actual_grid_nodes": g.n,
                                                 "injection_eV": e, "time_s": t,
                                                 **obs})
                channels.append(row)
            all_channels.append(np.array(channels))
        differences = [float(np.max(np.abs(b - a)))
                       for a, b in zip(all_channels[:-1], all_channels[1:])]
        result["grid_refinement"] = {"channel_order": ["active", "binding", "excitation", "heat", "cutoff"],
                                      "max_energy_fraction_differences": differences,
                                      "observed_order": math.log2(differences[0] / differences[1])}
        result["checks"]["grid"] = (differences[-1] <= ac["grid_observable_energy_fraction"]
                                           and differences[-1] < differences[0])
        g = generators[0]
        # SSPRK2 time refinement at the same frozen 1e11s epoch and CFL limit.
        # The reference follows characteristics, with sparse collision stages.
        t = 1e11
        base_steps = max(1, math.ceil(t * g.rho / 0.4))
        rk_errors = np.zeros(3)
        initial = np.column_stack([g.impulse(e) for e in energies])
        ref = c.evolve(g, initial, t, steps=base_steps * 8)
        # Same-stage dense/sparse check at base resolution audits the actual
        # characteristic code path independently of the refined time reference.
        sparse = c.evolve(g, initial, t, steps=base_steps)
        dense = c.evolve(g, initial, t, steps=base_steps, method="dense")
        sparse_dense_errors = [float(np.max(np.abs(c.energy_channels(g, sparse[:, j])
                                                  - c.energy_channels(g, dense[:, j]))) / e)
                               for j, e in enumerate(energies)]
        for k, factor in enumerate((1, 2, 4)):
            rk = c.evolve_ssprk2(g, initial, t, base_steps * factor)
            for j, e in enumerate(energies):
                minimum = min(minimum, float(rk.min()))
                error = np.max(np.abs(c.energy_channels(g, rk[:, j])
                                     - c.energy_channels(g, ref[:, j]))) / e
                rk_errors[k] = max(rk_errors[k], error)
        result["time_refinement"] = {"time_s": t, "grid_intervals": 128,
                                      "steps": [base_steps * f for f in (1, 2, 4)],
                                      "reference_steps": base_steps * 8,
                                      "method": "Characteristic drag with midpoint collision stages; SSPRK2 vs refined sparse exponential, same-stage dense/sparse parity",
                                      "maximum_energy_fraction_errors": rk_errors.tolist(),
                                      "observed_orders": np.log2(rk_errors[:-1] / rk_errors[1:]).tolist(),
                                      "sparse_dense_max_energy_fraction": max(sparse_dense_errors)}
        result["checks"]["time"] = bool(rk_errors[-1] < ac["time_observable_energy_fraction"]
                                           and np.all(np.diff(rk_errors) < 0)
                                           and max(sparse_dense_errors) < ac["number_energy_ledger_relative"])
        fineq = c.assemble(128, quadrature_order=12)
        qdiff = 0.
        y1 = c.evolve(g, initial, t)
        y2 = c.evolve(fineq, initial, t)
        for j, e in enumerate(energies):
            qdiff = max(qdiff, float(np.max(np.abs(c.energy_channels(g, y1[:, j])
                                                  - c.energy_channels(fineq, y2[:, j]))) / e))
        result["quadrature_refinement"] = {"orders": [8, 12], "time_s": t,
                                            "maximum_energy_fraction_difference": qdiff}
        result["checks"]["quadrature"] = qdiff < ac["quadrature_observable_energy_fraction"]
        result["ledger"] = {"maximum_energy_relative_error": max_e_err,
                              "maximum_number_absolute_error": max_n_err,
                              "minimum_population_or_reservoir": minimum}
        result["checks"]["ledgers"] = (max_e_err < ac["number_energy_ledger_relative"]
                                              and max_n_err < ac["number_energy_ledger_relative"])
        result["checks"]["nonnegative"] = minimum >= 0.
        result["checks"]["t0_causal"] = all(
            h["binding_energy_eV"] == h["excitation_energy_eV"] == h["coulomb_heat_eV"] == 0.
            for h in result["histories"] if h["time_s"] == 0)
        result["checks"]["off"] = all(np.array_equal(c.evolve(g, g.impulse(e), 1e13, enabled=False),
                                                       g.impulse(e)) for e in energies)
        expected_tau = 9.456523330348772e10
        computed_tau = float(c.cooling_time(20., g.gas))
        post_arrival = [h for h in result["histories"]
                        if h["injection_eV"] == 20. and h["time_s"] > expected_tau]
        result["continuum_arrival_oracle"] = {
            "injection_eV": 20., "expected_proper_time_s": expected_tau,
            "computed_proper_time_s": computed_tau,
            "relative_time_difference": abs(computed_tau / expected_tau - 1),
            "post_arrival_active_energy_eV": [h["active_energy_eV"] for h in post_arrival],
        }
        result["checks"]["continuum_arrival"] = (abs(computed_tau / expected_tau - 1)
                                                   < ac["number_energy_ledger_relative"]
                                                   and all(h["active_energy_eV"] == 0.
                                                           for h in post_arrival))
        result["status"] = "PASS_SCOPED" if all(result["checks"].values()) else "FAIL"
        result["exit_code"] = 0 if result["status"] == "PASS_SCOPED" else 1
    except Exception as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["exit_code"] = 1
    result["measured_process_cpu_s"] = time.process_time() - cpu0
    result["measured_process_wall_s"] = time.monotonic() - wall0
    result["unmeasured_overhead"] = "UNKNOWN_NOT_ZERO"
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "histories"}, indent=2))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
