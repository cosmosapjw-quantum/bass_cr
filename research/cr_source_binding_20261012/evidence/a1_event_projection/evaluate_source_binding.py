#!/usr/bin/env python3
"""Read-only physical postprocessing of the pinned PHYS02/M0 records.

No source quadrature, generator, transport solve, or kernel fit is performed.
Fractions preserve the stored decimal inputs; this does not remove their
underlying physical or numerical uncertainty.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path

EV_J = F("1.602176634e-19")
KB_J_K = F("1.380649e-23")


def read_json(path):
    return json.loads(Path(path).read_text(), parse_float=str)


def frac(value):
    if isinstance(value, dict):
        return F(int(value["numerator"]), int(value["denominator"]))
    return F(value)


def decimal(value):
    with localcontext() as ctx:
        ctx.prec = 50
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def serial(value):
    if isinstance(value, F):
        return decimal(value)
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def linear_source_observables(scale_eV_m3, T_s, H0, R, S):
    """scale=T^2 A_E; H0 is normalized to TOTAL selected birth energy."""
    scale, T, h, r, s = map(frac, (scale_eV_m3, T_s, H0, R, S))
    if scale < 0 or T <= 0 or not (0 <= h <= 1 and 0 <= s <= r <= 1):
        raise ValueError("Passive fixed-bath source inputs outside domain")
    q = scale * EV_J / T
    injected = scale * EV_J / 2
    return {
        "q_star_J_m3_s": q,
        "selected_injected_energy_J_m3": injected,
        "heat_power_J_m3_s": q * h * r,
        "cumulative_heat_J_m3": injected * h * s,
        "same_operator_prompt_power_J_m3_s": q * h,
        "same_operator_prompt_cumulative_J_m3": injected * h,
        "prompt_power_absolute_error_J_m3_s": q * h * (1 - r),
        "prompt_cumulative_absolute_error_J_m3": injected * h * (1 - s),
        "endpoint_heat_to_injection_power_fraction": h * r,
        "cumulative_heat_to_injected_energy_fraction": h * s,
    }


def calorimeter(nH, Y, xi):
    nH, Y, xi = map(frac, (nH, Y, xi))
    if nH <= 0 or not (0 <= Y < 1 and 0 <= xi <= 1):
        raise ValueError("Invalid fixed-composition gas")
    nHe = nH * Y / (4 * (1 - Y))
    ne = xi * (nH + nHe)
    ntot = nH + nHe + ne
    return {"n_H_m3": nH, "n_He_m3": nHe, "n_e_m3": ne,
            "n_particles_m3": ntot, "C_V_J_m3_K": F(3, 2) * KB_J_K * ntot}


def passive_energy_envelope(selected_energy, all_energy, selected_heat, Cv):
    """Cumulative source-attributed kinetic-energy bounds, zero initial stock.

    Applies to passive deposition without energy borrowed from the bath.
    No pointwise heating-power or coupled-temperature bound is implied.
    """
    es, ea, hs, cv = map(frac, (selected_energy, all_energy, selected_heat, Cv))
    if not (0 <= hs <= es <= ea and cv > 0):
        raise ValueError("Energy budget or heat capacity outside domain")
    tail = ea - es
    return {
        "all_secondary_injected_energy_J_m3": ea,
        "omitted_birth_energy_J_m3": tail,
        "selected_heat_plus_all_omitted_heat_upper_J_m3": hs + tail,
        "all_secondary_heat_energy_upper_J_m3": ea,
        "omitted_birth_delta_T_upper_K": tail / cv,
        "selected_heat_plus_all_omitted_delta_T_upper_K": (hs + tail) / cv,
        "all_secondary_delta_T_upper_K": ea / cv,
        "scope": "Source-attributed calorimetric bounds for the recorded active-proton source; not all CR processes or a cosmological history",
    }


def evaluate(input_dir):
    root = Path(input_dir)
    cache = read_json(root / "CACHED_RESPONSE.json")
    pulse = read_json(root / "PULSE_RECORD.json")
    paired = read_json(root / "PAIRED_RECORD.json")
    coverage = read_json(root / "SOURCE_COVERAGE_RECORD.json")["coverage"]
    T = frac(cache["T_s"])
    scales = {frac(m["physical_energy_scale_eV_m3"]) for m in pulse["models"]}
    if len(scales) != 1:
        raise ValueError("Model records have different source scales")
    scale = scales.pop()
    gas = calorimeter("140", "0.248", "0.01")
    Cv = gas["C_V_J_m3_K"]
    gas["reference_temperature_K"] = F(100)
    gas["reference_thermal_energy_J_m3"] = Cv * 100
    checks = []

    def compare(name, got, reference, tolerance=F("1e-12")):
        got, reference = frac(got), frac(reference)
        error = abs(got - reference)
        rel = error / abs(reference) if reference else error
        checks.append({"id": name, "got": got, "reference": reference,
                       "relative_error": rel, "tolerance": tolerance,
                       "passed": rel <= tolerance})

    rows = []
    for row in cache["rows"]:
        m = {k: frac(v) for k, v in row["moments"].items()}
        out = linear_source_observables(scale, T, m["H0"], m["R"], m["S"])
        out.update({"model": row["model"], "representation": row["representation"],
                    "H0": m["H0"], "p": m["p"], "R": m["R"], "S": m["S"],
                    "calorimetric_heat_rate_K_s": out["heat_power_J_m3_s"] / Cv,
                    "calorimetric_delta_T_K": out["cumulative_heat_J_m3"] / Cv,
                    "prompt_power_over_causal": 1 / m["R"],
                    "prompt_cumulative_over_causal": 1 / m["S"],
                    "prompt_calorimetric_absolute_error_K": out["prompt_cumulative_absolute_error_J_m3"] / Cv,
                    "heat_to_reference_thermal_energy_fraction": out["cumulative_heat_J_m3"] / (Cv * 100)})
        rows.append(out)
        run = next(g for g in paired["grid_results"] if g["label"] == row["model"])
        old = run["final"]["components"]["selected_total"]
        ion_rate = frac(old["ionizations_HI_rate_m3_s"]) + frac(old["ionizations_HeI_rate_m3_s"])
        ion_count = frac(old["ionizations_HI_m3"]) + frac(old["ionizations_HeI_m3"])
        per_particle_thermal = F(3, 2) * KB_J_K * gas["reference_temperature_K"]
        out.update({"secondary_degradation_electron_rate_m3_s": ion_rate,
                    "secondary_degradation_electron_count_m3": ion_count,
                    "secondary_particle_number_Tdot_correction_K_s": -per_particle_thermal * ion_rate / Cv,
                    "secondary_only_local_Tdot_frozen_coeff_K_s": (out["heat_power_J_m3_s"] - per_particle_thermal * ion_rate) / Cv,
                    "secondary_only_linearized_delta_T_frozen_coeff_K": (out["cumulative_heat_J_m3"] - per_particle_thermal * ion_count) / Cv,
                    "secondary_event_scope": "Additional ions from electron degradation; primary proton birth-ionization is not in this event ledger"})
        label = row["model"] + "/" + row["representation"]
        compare(label + "/paired_power", out["heat_power_J_m3_s"], old["heat_power_J_m3_s"])
        compare(label + "/paired_cumulative", out["cumulative_heat_J_m3"], old["heat_J_m3"])
        compare(label + "/paired_injection", out["selected_injected_energy_J_m3"], old["injected_energy_J_m3"])

    births = []
    for model in pulse["models"]:
        selected = next(r for r in rows if r["model"] == model["model"] and r["representation"] == "selected_record")
        run = next(g for g in paired["grid_results"] if g["label"] == model["model"])
        subtotals = []
        for tag, column in zip(["direct_0p1_10", "direct_10_900"], model["birth_columns"]):
            h, r, s = map(frac, (column["H0"], column["R"], column["S"]))
            out = linear_source_observables(scale, T, h, r, s)
            old = run["final"]["components"][tag]
            energy_weight = frac(old["injected_energy_J_m3"]) / selected["selected_injected_energy_J_m3"]
            out.update({"model": model["model"], "birth_tag": tag,
                        "H0_per_total_selected_energy": h,
                        "H0_per_own_birth_energy": h / energy_weight,
                        "injected_energy_weight": energy_weight,
                        "endpoint_heat_share": out["heat_power_J_m3_s"] / selected["heat_power_J_m3_s"],
                        "cumulative_heat_share": out["cumulative_heat_J_m3"] / selected["cumulative_heat_J_m3"],
                        "calorimetric_delta_T_K": out["cumulative_heat_J_m3"] / Cv})
            # The common scale is kept above to avoid applying energy_weight twice.
            out["birth_injected_energy_J_m3"] = frac(old["injected_energy_J_m3"])
            compare(model["model"] + "/" + tag + "/power", out["heat_power_J_m3_s"], old["heat_power_J_m3_s"])
            compare(model["model"] + "/" + tag + "/cumulative", out["cumulative_heat_J_m3"], old["heat_J_m3"])
            births.append(out)
            subtotals.append(out)
        for key in ["heat_power_J_m3_s", "cumulative_heat_J_m3"]:
            compare(model["model"] + "/birth_sum/" + key, sum(x[key] for x in subtotals), selected[key])

    selected = next(r for r in rows if r["model"] == "fullBED" and r["representation"] == "selected_record")
    AE_full = frac(coverage["all_direct_A_energy_eV_m3_s2"])
    AE = scale / T**2
    bands = {k: frac(v) for k, v in coverage["band_A_energy_eV_m3_s2"].items()}
    compare("source/selected_A_energy", AE, bands["direct_low"] + bands["direct_high_selected"])
    compare("source/selected_fraction", AE / AE_full, coverage["selected_fraction_of_all_direct"])
    compare("source/full_band_sum", sum(bands.values()), AE_full)
    all_energy = AE_full * T**2 * EV_J / 2
    envelope = passive_energy_envelope(selected["selected_injected_energy_J_m3"], all_energy, selected["cumulative_heat_J_m3"], Cv)
    envelope["selected_birth_energy_fraction"] = AE / AE_full
    envelope["omitted_birth_energy_fraction"] = 1 - AE / AE_full
    envelope["all_secondary_upper_to_reference_thermal_energy_fraction"] = all_energy / (Cv * 100)
    paired_full = next(g for g in paired["grid_results"] if g["label"] == "fullBED")
    old = paired_full["final"]["components"]["selected_total"]
    ledger_keys = ["active_electron_energy_J_m3", "heat_J_m3", "binding_HI_J_m3", "binding_HeI_J_m3", "excitation_HI_J_m3", "excitation_HeI_J_m3", "cutoff_energy_J_m3"]
    energy_ledger = {k: {"energy_J_m3": frac(old[k]), "fraction_of_selected_injection": frac(old[k]) / selected["selected_injected_energy_J_m3"]} for k in ledger_keys}
    compare("energy/selected_ledger_sum", sum(frac(old[k]) for k in ledger_keys), selected["selected_injected_energy_J_m3"])
    zero = linear_source_observables(0, T, selected["H0"], selected["R"], selected["S"])
    compare("zero_source/exact_zero", sum(v for k, v in zero.items() if k.endswith(("J_m3", "J_m3_s"))), 0, F(0))
    status = "PASS_RECORDED_SOURCE_BINDING" if all(c["passed"] for c in checks) else "FAIL"
    return serial({
        "schema": "cr-source-binding-result.v1", "status": status,
        "arithmetic": "Exact rational arithmetic on stored decimal records; 50-digit decimal serialization",
        "T_s": T, "source": {"energy_scale_eV_m3": scale, "selected_A_energy_eV_m3_s2": AE,
        "all_secondary_A_energy_eV_m3_s2": AE_full, "q_star_J_m3_s": selected["q_star_J_m3_s"],
        "selected_injected_energy_J_m3": selected["selected_injected_energy_J_m3"],
        "source_shape": "Q_e(W,t)=t A(W), zero initial stock, normalized with selected energy integral"},
        "gas_calorimeter": gas, "rows": rows, "birth_rows": births,
        "cumulative_energy_envelope": envelope, "selected_energy_ledger": energy_ledger,
        "comparison_tolerance_meaning": "Agreement of two preserved numerical records after a unit/normalization transform; not a physical error bound",
        "checks": checks, "maximum_relative_readback_difference": max(c["relative_error"] for c in checks),
        "new_execution_counts": {"generator_builds": 0, "transport_solves": 0, "pulse_calls": 0, "source_quadratures": 0},
        "consumer_budget": {"observable": None, "absolute_tolerance": None, "relative_tolerance": None,
        "reference_denominator": None, "binding_scope": "Executed BASS_CR fixed-bath electron source; REI selected CR-on history remains unprovided"}})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", type=Path, default=Path(__file__).parent / "inputs")
    p.add_argument("--output", type=Path, default=Path(__file__).parent / "results/SOURCE_BOUND_RESPONSE.json")
    args = p.parse_args()
    result = evaluate(args.inputs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": len(result["checks"]),
                      "failed": [c["id"] for c in result["checks"] if not c["passed"]],
                      "maximum_relative_difference": result["maximum_relative_readback_difference"]}))
    raise SystemExit(0 if result["status"].startswith("PASS") else 1)


if __name__ == "__main__":
    main()
