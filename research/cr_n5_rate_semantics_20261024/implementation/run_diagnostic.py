"""One new algebraic diagnostic. Invoked only by the bounded dispatcher."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time

from n5_semantics import (InputError, admit_rate, ce_envelope, contained_path,
                          exact_decimal, exact_temperature_rows, first_event_estimate, hazard_limit,
                          import_pinned, product, real, verify_manifest)
from decimal_reference import (reference_envelope, reference_first_event,
                               reference_hazard_limit, reference_product, scaled_error)


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def load_source_channels(unit, case):
    path = contained_path(unit, case["reused_paths"]["phys83_module"])
    source = contained_path(unit, case["reused_paths"]["phys83_source_directory"])
    provider = import_pinned(path, "_n5_exact_phys83_constructor")
    counts = {}
    old_profiler = sys.getprofile()
    source_name = str(path)

    def guard(frame, event, argument):
        if event == "call" and frame.f_code.co_filename == source_name:
            name = frame.f_code.co_name
            counts[name] = counts.get(name, 0) + 1
            if name in {"moments", "evaluate"}:
                raise InputError("FORBIDDEN_PROVIDER_RATE_EXECUTION")

    sys.setprofile(guard)
    try:
        loaded = {name: provider.MatchedCEChannel(name, source) for name in ("2S", "2P")}
    finally:
        sys.setprofile(old_profiler)
    arrays = {name: (tuple(map(float, item.energy_eV)), tuple(map(float, item.W_eV_cm2)))
              for name, item in loaded.items()}
    return arrays, float(provider.GAP_EV), counts


def run(unit, output, run_id):
    started_wall, started_cpu = time.monotonic(), time.process_time()
    pins = verify_manifest(unit)
    case = json.loads((unit / "inputs/CASE.json").read_text())
    paths = case["reused_paths"]
    required = {"inputs/CASE.json", paths["mfpt"], paths["case"], paths["rates"],
                paths["atomic_contract"], paths["phys83_module"]}
    if not required.issubset(set(pins["paths"])):
        raise InputError("REQUIRED_INPUT_NOT_MANIFEST_PINNED")
    old_case = json.loads(contained_path(unit, paths["case"]).read_text())
    for now, old in (("temperature_K", "temperature_K"), ("n_e_thermal_cm3", "n_e_thermal_cm3"),
                     ("log_lambda", "log_lambda")):
        if exact_decimal(case[now]) != exact_decimal(old_case[old]):
            raise InputError(f"REUSED_MFPT_CONTEXT_MISMATCH:{now}")
    if case["frame"] != old_case["frame"] or case["clock"] != old_case["time_unit"] or not old_case["closed_box"]:
        raise InputError("REUSED_FRAME_CLOCK_BOUNDARY_MISMATCH")
    if case["mean_upper_theta"] != 80 or sorted(case["chi"]) != [1.5, 3.0]:
        raise InputError("UNADMITTED_MFPT_CONTEXT_SELECTION")
    if case["old_science_replay"] is not False or case["no_interpolation_temperature"] is not True:
        raise InputError("EXECUTION_POLICY_MISMATCH")
    if any(value is not None for value in case["actual_missing_hazards"].values()):
        raise InputError("MISSING_HAZARD_WAS_POPULATED")
    atom = import_pinned(contained_path(unit, paths["atomic_contract"]), "_n5_exact_c23c_atomic_contract")
    population_labels = list(atom.POPULATION_LABELS)
    if len(population_labels) != 21:
        raise InputError("INHERITED_POPULATION_REGISTRY_MISMATCH")
    mfpt = json.loads(contained_path(unit, paths["mfpt"]).read_text())
    if len(mfpt) != 6 or len({(row["redshift"], row["chi"]) for row in mfpt}) != 6:
        raise InputError("SAVED_MFPT_CONTEXT_COUNT")
    with contained_path(unit, paths["rates"]).open(newline="") as handle:
        saved_rates = list(csv.DictReader(handle))
    if len(saved_rates) != 132:
        raise InputError("PHYS83_TABLE_ROW_COUNT")
    selected_rates = exact_temperature_rows(saved_rates, case["temperature_K"])
    if len(selected_rates) != 2 or {row["upper_level"] for row in selected_rates} != {"2S", "2P"}:
        raise InputError("EXACT_TEMPERATURE_ROWS_UNAVAILABLE")
    temperature = real(case["temperature_K"], "T", strictly_positive=True)
    theta = product(real(case["kb_J_K"], "kB", strictly_positive=True), temperature) / real(case["eV_J"], "eV_J", strictly_positive=True)
    upper = product(case["mean_upper_theta"], theta)
    channels, threshold, constructor_counts = load_source_channels(unit, case)
    envelopes = {}
    references = []
    for chi in case["chi"]:
        domain = [product(chi, theta), upper]
        for selection in ("2S", "2P", "2S+2P"):
            names = selection.split("+")
            chosen = {name: channels[name] for name in names}
            envelope = ce_envelope(chosen, domain, threshold_eV=threshold,
                                   n_1s_cm3=case["n_H1_1s_cm3"], eV_J=case["eV_J"], m_e_kg=case["m_e_kg"])
            reference = reference_envelope(chosen, domain, threshold, case["n_H1_1s_cm3"], case["eV_J"], case["m_e_kg"])
            error = scaled_error(envelope["hmax_per_proper_s"], reference["hmax"])
            if error > exact_decimal("5e-14"):
                raise InputError("ENVELOPE_DECIMAL_REFERENCE_MISMATCH")
            envelope.update({"chi": chi, "selection": selection, "decimal_reference_hmax": str(reference["hmax"]),
                             "decimal_scaled_relative_error": float(error), "decimal_reference_energy_eV": str(reference["energy_eV"])})
            envelopes[(chi, selection)] = envelope
            references.append({"family": "CE_ENVELOPE", "chi": chi, "selection": selection, "scaled_relative_error": float(error)})
    hcrit_rows, thermal_rows, ce_rows = [], [], []
    semantic_admissions = []
    for context in mfpt:
        chi, redshift = context["chi"], context["redshift"]
        if chi not in case["chi"] or redshift not in old_case["redshifts"]:
            raise InputError("UNKNOWN_SAVED_MFPT_CONTEXT")
        saved = context["upper_boundaries_theta"]["80"]
        mean = real(saved["active_weighted_mean_s"], "mean_s", strictly_positive=True)
        fraction = real(saved["active_fraction"], "active_fraction")
        if fraction > 1:
            raise InputError("ACTIVE_FRACTION_ABOVE_ONE")
        base = {"redshift": redshift, "chi": chi, "reflecting_upper_theta": 80,
                "active_mean_first_entry_proper_s": mean, "active_fraction": fraction,
                "mean_provenance": "reused_C23D_direct_MFPT_quadrature_R80",
                "frame": case["frame"], "clock": case["clock"]}
        for epsilon in case["epsilons"]:
            value = hazard_limit(epsilon, mean)
            error = scaled_error(value, reference_hazard_limit(epsilon, mean))
            if error > exact_decimal("5e-14"):
                raise InputError("HCRIT_DECIMAL_REFERENCE_MISMATCH")
            hcrit_rows.append({**base, "epsilon_active": epsilon, "hcrit_per_proper_s": value,
                               "quantity_kind": "sufficient_uniform_hazard_envelope_limit",
                               "actual_missing_competing_hazard_per_s": None, "actual_competition_probability": None,
                               "scaled_relative_error_vs_80digit": float(error)})
        for rate in selected_rates:
            for direction in ("up", "down"):
                q = real(float(rate[f"q_{direction}_cm3_s"]), "saved_q", strictly_positive=True)
                identity = {"process": f"H1_CE_{direction}", "nuclide": "H1", "charge": 0,
                            "internal_state": "1S" if direction == "up" else rate["upper_level"],
                            "quantity_kind": "Maxwell_thermal_rate_coefficient", "frame": case["frame"],
                            "clock": case["clock"], "unit": "cm^3/s", "interpolation": "none_exact_saved_T_row",
                            "isotope_mapping": "source_H1_only"}
                provider = {**identity, "owner_gate": "NUMERICALLY_CHECKED_SCOPED", "temperature_K_values": [temperature],
                            "value": q, "scope": "PHYS83_finite_source_thermal_rates", "source_identity": paths["rates"]}
                admission = admit_rate({**identity, "temperature_K": temperature}, provider)
                if not admission["admitted"]:
                    raise InputError("EXACT_SAVED_RATE_SEMANTICS_REJECTED")
                rate_target = product(case["n_e_thermal_cm3"], q)
                comparison = product(rate_target, mean)
                rate_error = scaled_error(rate_target, reference_product(case["n_e_thermal_cm3"], rate[f"q_{direction}_cm3_s"]))
                product_error = scaled_error(comparison, reference_product(case["n_e_thermal_cm3"], rate[f"q_{direction}_cm3_s"], mean))
                if max(rate_error, product_error) > exact_decimal("5e-14"):
                    raise InputError("THERMAL_PRODUCT_DECIMAL_REFERENCE_MISMATCH")
                thermal_rows.append({**base, "upper_level": rate["upper_level"], "direction": direction,
                                     "source_temperature_K": temperature, "saved_q_cm3_s_text": rate[f"q_{direction}_cm3_s"],
                                     "saved_q_cm3_s": q, "n_e_thermal_cm3": case["n_e_thermal_cm3"],
                                     "lambda_per_frozen_target_per_proper_s": rate_target,
                                     "lambda_target_times_ee_active_mean": comparison,
                                     "quantity_kind": "frozen_target_thermal_rate_EE_first_entry_comparison",
                                     "tagged_electron_event_probability": None, "evolved_atomic_event_count": None,
                                     "heat_rate": None, "scaled_relative_error_lambda": float(rate_error),
                                     "scaled_relative_error_product": float(product_error)})
                if redshift == old_case["redshifts"][0] and chi == case["chi"][0]:
                    semantic_admissions.append(admission)
        for selection in ("2S", "2P", "2S+2P"):
            envelope = envelopes[(chi, selection)]
            event = first_event_estimate(envelope["hmax_per_proper_s"], mean, fraction)
            ref_active, ref_whole = reference_first_event(envelope["hmax_per_proper_s"], mean, fraction)
            active_error = scaled_error(event["active_first_event_upper_estimate"], ref_active)
            whole_error = scaled_error(event["whole_selected_first_event_upper_estimate"], ref_whole)
            if max(active_error, whole_error) > exact_decimal("5e-14"):
                raise InputError("CE_BOUND_DECIMAL_REFERENCE_MISMATCH")
            ce_rows.append({**base, "channel_selection": selection, "hmax_per_proper_s": envelope["hmax_per_proper_s"],
                            "maximizing_energy_eV": envelope["maximizing_energy_eV"],
                            "full_pre_entry_domain_eV": envelope["full_pre_entry_domain_eV"], **event,
                            "ground_H1_target_density_cm3": case["n_H1_1s_cm3"],
                            "quantity_kind": "conditional_first_CE_before_EE_first_entry_upper_estimate",
                            "physical_probability_certificate": None, "global_error_bound": None,
                            "scaled_relative_error_active": float(active_error), "scaled_relative_error_whole": float(whole_error)})
    if tuple(map(len, (hcrit_rows, thermal_rows, ce_rows))) != (18, 24, 18):
        raise InputError("DIAGNOSTIC_ROW_COUNTS")
    source_arrays = {key: {"energy_eV": list(value[0]), "W_eV_cm2": list(value[1])} for key, value in channels.items()}
    write_json(output / "SOURCE_ARRAYS_REUSED.json", {"source": paths["phys83_module"], "channels": source_arrays,
                                                      "method": "exact_pinned_constructor_arrays_only", "threshold_eV": threshold})
    write_json(output / "HCRIT.json", hcrit_rows)
    write_json(output / "THERMAL_TARGET_COMPARISONS.json", thermal_rows)
    write_json(output / "CE_PATH_ENDPOINT_SAMPLES.json", [
        {"chi": chi, "selection": "2S+2P", "full_pre_entry_domain_eV": envelopes[(chi, "2S+2P")]["full_pre_entry_domain_eV"],
         "source_initial_energy_eV": case["source_initial_energy_eV"],
         "samples": envelopes[(chi, "2S+2P")]["endpoint_samples"]}
        for chi in case["chi"]])
    write_json(output / "CE_ENVELOPES.json", [{key: val for key, val in envelope.items() if key != "endpoint_samples"}
                                             for envelope in envelopes.values()])
    write_json(output / "CE_FIRST_EVENT_ESTIMATES.json", ce_rows)
    write_json(output / "RATE_SEMANTIC_ADMISSIONS.json", semantic_admissions)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result = {"schema": "CR_N5_ALGEBRAIC_RESULT_V1", "run_id": run_id,
              "claim_gate": "NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_DIAGNOSTIC",
              "input_manifest": pins, "row_counts": {"hcrit": 18, "thermal_target": 24, "conditional_ce_first_event": 18,
                                                     "distinct_ce_envelopes": 6},
              "theta_eV": theta, "source_initial_energy_eV": case["source_initial_energy_eV"],
              "full_path_upper_eV": upper, "source_native_CE_threshold_eV": threshold,
              "population_labels_reused": population_labels, "provider_constructor_call_trace": constructor_counts,
              "new_linear_ODE": 0, "new_coupled_cosmological_ODE": 0, "new_source_quadratures": 0,
              "provider_rate_evaluations": 0, "PHYS84_source_executions": 0, "old_science_replays": 0,
              "new_algebraic_diagnostic_campaigns": 1, "global_error_bound": None, "global_completion_percent": None,
              "actual_missing_hazards": case["actual_missing_hazards"],
              "cpu_s": time.process_time() - started_cpu, "wall_s": time.monotonic() - started_wall,
              "peak_rss_kib": usage.ru_maxrss,
              "EXECUTION": "COMPLETE_SCOPED", "PUBLICATION": "PARENT_OWNED_NOT_ATTEMPTED",
              "BACKUP": "PARENT_OWNED_PENDING", "DAG": "N5_SCOPED_CHILD_CHECKED;N5_PARENT_PARTIAL;N6_N7_OPEN"}
    write_json(output / "RESULT.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    try:
        result = run(args.unit.resolve(), args.output.resolve(), args.run_id)
    except Exception as exc:
        write_json(args.output / "FAILURE.json", {"type": type(exc).__name__, "message": str(exc),
                                                   "science_replay": False, "status": "FAILED_RETAINED"})
        raise
    print(json.dumps({"run_id": args.run_id, "status": result["claim_gate"], "row_counts": result["row_counts"]}))


if __name__ == "__main__":
    main()
