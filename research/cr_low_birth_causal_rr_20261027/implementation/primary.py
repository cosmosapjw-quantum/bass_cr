#!/usr/bin/env python3
"""Four-prefix causal low-birth response from one pinned prepared operator."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from model import (CONSTANTS, CONTRACT_SHA256, FITS, SOURCE_SHA256, T_END, UNIT_ID,
                   array_identity, checked_file, need, strict_json, write_json, write_npz)
from ports import (claim_birth, claim_return, native25_rr, retained_port,
                   validate_context)
from prepare import require_runner
from uniformization import propagate


def total(array):
    return math.fsum(map(float, np.asarray(array).ravel()))


def relative_residual(residual, scale):
    need(math.isfinite(residual) and math.isfinite(scale) and scale >= 0,
         "FINITE_RESIDUAL_SCALE_REQUIRED")
    return abs(residual) / scale if scale > 0 else (0. if residual == 0 else math.inf)


def read_prepared(directory, expected_sha256):
    raw = checked_file(directory / "PREPARATION.json", expected_sha256)
    record = strict_json(raw)
    need(record.get("unit") == UNIT_ID
         and record.get("contract_sha256") == CONTRACT_SHA256
         and record["input"]["sha256"] == SOURCE_SHA256, "EXACT_PREPARED_CONTEXT_REQUIRED")
    validate_context(record["context"])
    checked_file(directory / "PREPARED.npz", record["PREPARED_npz"]["sha256"],
                 record["PREPARED_npz"]["bytes"])
    with np.load(directory / "PREPARED.npz", allow_pickle=False) as saved:
        arrays = {key: saved[key].copy() for key in saved.files}
    need(set(arrays) == set(record["array_identities"]), "PREPARED_MEMBER_IDENTITY_MISMATCH")
    for key, values in arrays.items():
        need(array_identity(values) == record["array_identities"][key],
             "PREPARED_ARRAY_HASH_MISMATCH:" + key)
    return arrays, record


def row_summary(energy, amplitude, acut, stopping, drift, lambdas,
                current_n, previous_n, occupancy, window, context, *, prefix, registry):
    left, right = window
    injected_n = math.fsum((total(amplitude), acut)) * (right * right - left * left) / 2
    injected_u = math.fsum((total(energy * amplitude), .1 * acut)) * (right * right - left * left) / 2
    active = current_n if prefix else current_n - previous_n
    active_n, active_u = total(active), total(energy * active)
    direct = acut * (right * right - left * left) / 2
    drift_cut = float(drift[0] * occupancy[0])
    cutoff = math.fsum((direct, drift_cut))
    caloric = total(stopping * occupancy)
    channels, captures, kinetics, retained, claims = {}, {}, {}, {}, []
    for channel in ("H", "He"):
        atoms = lambdas[channel] * occupancy
        count = total(atoms)
        kinetic = total(energy * atoms)
        photon_e = energy + FITS[channel][0]
        port = retained_port(context, channel, window, photon_e, atoms)
        photon_u = port["energy_eV_m3"]
        binding = -FITS[channel][0] * count
        event_residual = math.fsum((-kinetic, binding, photon_u))
        channels[channel] = {
            "capture_number_m3": count, "capture_kinetic_eV_m3": kinetic,
            "retained_photon_number_m3": count,
            "retained_photon_energy_eV_m3": photon_u,
            "binding_energy_change_eV_m3": binding,
            "event_energy_residual_eV_m3": event_residual,
            "event_energy_relative_residual": relative_residual(event_residual, photon_u),
            "endpoint_rate_m3_s": total(lambdas[channel] * current_n) if prefix else None,
            "endpoint_kinetic_rate_eV_m3_s": total(energy * lambdas[channel] * current_n) if prefix else None,
        }
        captures[channel], kinetics[channel] = count, kinetic
        retained[channel] = port
        if not prefix:
            claims.append(claim_return(context, channel, window, registry))
    native = native25_rr(context, captures, kinetics)
    count_residual = math.fsum((active_n, cutoff, captures["H"], captures["He"], -injected_n))
    kinetic_residual = math.fsum((active_u, .1 * cutoff, caloric,
                                  kinetics["H"], kinetics["He"], -injected_u))
    total_residual = math.fsum((active_u, .1 * cutoff, caloric,
        channels["H"]["retained_photon_energy_eV_m3"],
        channels["He"]["retained_photon_energy_eV_m3"],
        channels["H"]["binding_energy_change_eV_m3"],
        channels["He"]["binding_energy_change_eV_m3"], -injected_u))
    nb = context["recipient_nb_m3"]
    row = {
        "interval_s": list(window),
        "role": "nonadditive_cumulative_prefix" if prefix else "disjoint_observation_bin",
        "injected_number_m3": injected_n, "injected_energy_eV_m3": injected_u,
        "occupancy_total_m3_s": total(occupancy),
        "occupancy_meaning": "actual integral of active cohort number density over this interval",
        "cutoff_direct_number_m3": direct, "cutoff_drift_number_m3": drift_cut,
        "cutoff_number_m3": cutoff, "cutoff_energy_eV_m3": .1 * cutoff,
        "coulomb_energy_eV_m3": caloric,
        "coulomb_energy_meaning": "prescribed caloric stopping ledger; physical thermal closure absent",
        "channels": channels, "retained_photon_ports": retained,
        "rr_native25": native["values"],
        "rr_native25_contract": {key: value for key, value in native.items() if key != "values"},
        "full_source_native25": None, "coupled_state_update": None,
        "physical_heating_completed": False, "physical_heating_J_m3": None,
        "absolute_worldtube_number": None, "absolute_worldtube_energy_J": None,
        "return_claims": claims,
        "count_residual_m3": count_residual,
        "kinetic_energy_residual_eV_m3": kinetic_residual,
        "total_energy_residual_eV_m3": total_residual,
        "count_relative_residual": relative_residual(count_residual, injected_n),
        "kinetic_energy_relative_residual": relative_residual(kinetic_residual, injected_u),
        "total_energy_relative_residual": relative_residual(total_residual, injected_u),
        "thermal_electron_relative_residual": relative_residual(
            native["thermal_electron_change"], math.fsum(captures.values()) / nb),
    }
    if prefix:
        row.update(active_number_m3=active_n, active_energy_eV_m3=active_u,
                   active_number_per_baryon_diagnostic=active_n / nb,
                   active_energy_J_per_baryon_diagnostic=active_u * CONSTANTS["eV_J"] / nb,
                   endpoint_side="known-history left limit" if right == T_END else "within known history")
    else:
        row.update(active_number_change_m3=active_n, active_energy_change_eV_m3=active_u,
                   includes_prior_injected_survivors=True)
    return row


def prefix_tail(record, amplitude, energy, lambdas):
    active_a = total(amplitude)
    maximum_e = float(np.max(energy))
    rows = []
    for weights in record["weights"]:
        t = weights["time_s"]
        count_bound = active_a * t * t / 2 * weights["tail_count_fraction"]
        occupancy_bound = active_a * t * t * t / 6 * weights["tail_occupancy_fraction"]
        channels = {}
        for channel in ("H", "He"):
            lammax = float(np.max(lambdas[channel]))
            capture = min(count_bound, lammax * occupancy_bound)
            channels[channel] = {
                "capture_number_m3": capture,
                "capture_kinetic_eV_m3": maximum_e * capture,
                "retained_photon_energy_eV_m3": (maximum_e + FITS[channel][0]) * capture,
                "endpoint_rate_m3_s": lammax * count_bound,
                "lambda_max_s_inv": lammax,
            }
        rows.append({"time_s": t, "source_count_bound_m3": count_bound,
                     "source_energy_bound_eV_m3": maximum_e * count_bound,
                     "occupancy_bound_m3_s": occupancy_bound, "channels": channels,
                     "kind": "exact-arithmetic truncation bound evaluated in ordinary floating point",
                     "outward_interval_enclosure": False})
    return rows


def sum_tail(left, right):
    if left is None:
        return right
    summed = {"source_count_bound_m3": math.fsum((left["source_count_bound_m3"], right["source_count_bound_m3"])),
              "source_energy_bound_eV_m3": math.fsum((left["source_energy_bound_eV_m3"], right["source_energy_bound_eV_m3"])),
              "occupancy_bound_m3_s": math.fsum((left["occupancy_bound_m3_s"], right["occupancy_bound_m3_s"])),
              "kind": "sum of two endpoint truncation bounds", "outward_interval_enclosure": False,
              "channels": {}}
    for channel in ("H", "He"):
        summed["channels"][channel] = {
            key: math.fsum((left["channels"][channel][key], right["channels"][channel][key]))
            for key in ("capture_number_m3", "capture_kinetic_eV_m3", "retained_photon_energy_eV_m3")}
    return summed


def check_row(row, bounds):
    residuals = ("count_relative_residual", "kinetic_energy_relative_residual",
                 "total_energy_relative_residual", "thermal_electron_relative_residual")
    checks = {name: row[name] <= 1e-11 for name in residuals}
    checks["source_count_tail"] = bounds["source_count_bound_m3"] <= 1e-13 * row["injected_number_m3"]
    checks["source_energy_tail"] = bounds["source_energy_bound_eV_m3"] <= 1e-13 * row["injected_energy_eV_m3"]
    for channel in ("H", "He"):
        values = row["channels"][channel]
        checks[channel + "_event_energy"] = values["event_energy_relative_residual"] <= 1e-11
        for quantity in ("capture_number_m3", "capture_kinetic_eV_m3", "retained_photon_energy_eV_m3"):
            value = values[quantity]
            bound = bounds["channels"][channel][quantity]
            checks[channel + "_" + quantity + "_tail"] = value > 0 and bound <= 1e-12 * value
    row["truncation_bounds"] = bounds
    row["internal_checks"] = checks
    return all(checks.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--preparation-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    unit = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    require_runner(unit, out)
    data, preparation = read_prepared(args.prepared.resolve(), args.preparation_sha256)
    energy, amplitude = data["E_eV"], data["A_m3_s2"]
    acut = float(data["A_cutoff_m3_s2"])
    times = data["times_s"]
    lambdas = {"H": data["lambda_H_s_inv"], "He": data["lambda_He_s_inv"]}
    state, occupied, algorithm = propagate(amplitude, data["drift_s_inv"],
        lambdas["H"], lambdas["He"], times, float(data["nu_s_inv"]),
        data["weights_n"], data["weights_o"])
    bins = np.diff(np.vstack((np.zeros_like(occupied[0]), occupied)), axis=0)
    need(np.all(bins >= 0) and np.all(np.isfinite(bins)), "NONNEGATIVE_FINITE_BIN_OCCUPANCY_REQUIRED")
    context = preparation["context"]
    birth_registry, return_registry = [], []
    birth_claim = claim_birth(context, birth_registry)
    tails = prefix_tail(preparation, amplitude, energy, lambdas)
    prefixes, observation_bins, accepted = [], [], []
    previous_time, previous_state, previous_tail = 0., np.zeros_like(state[0]), None
    for index, time_value in enumerate(times):
        prefix = row_summary(energy, amplitude, acut, data["b_eV_s"], data["drift_s_inv"],
            lambdas, state[index], np.zeros_like(state[index]), occupied[index],
            [0., float(time_value)], context, prefix=True, registry=None)
        observation = row_summary(energy, amplitude, acut, data["b_eV_s"], data["drift_s_inv"],
            lambdas, state[index], previous_state, bins[index],
            [previous_time, float(time_value)], context, prefix=False, registry=return_registry)
        accepted.append(check_row(prefix, tails[index]))
        accepted.append(check_row(observation, sum_tail(previous_tail, tails[index])))
        prefixes.append(prefix)
        observation_bins.append(observation)
        previous_time, previous_state, previous_tail = float(time_value), state[index], tails[index]
    output_arrays = {key: data[key] for key in
        ("E_eV", "A_m3_s2", "b_eV_s", "drift_s_inv", "lambda_H_s_inv", "lambda_He_s_inv", "times_s")}
    output_arrays.update(n_prefix_m3=state, O_prefix_m3_s=occupied, O_bins_m3_s=bins)
    for channel in ("H", "He"):
        output_arrays["capture_" + channel + "_prefix_m3"] = occupied * lambdas[channel][None, :]
        output_arrays["capture_" + channel + "_bins_m3"] = bins * lambdas[channel][None, :]
        output_arrays["photon_" + channel + "_energy_eV"] = energy + FITS[channel][0]
        output_arrays["endpoint_" + channel + "_rate_m3_s"] = state * lambdas[channel][None, :]
    write_npz(out / "ARRAYS.npz", output_arrays)
    array_raw = (out / "ARRAYS.npz").read_bytes()
    result = {
        "schema": "CR_LOW_BIRTH_CAUSAL_RR_RESULT_V1", "unit": UNIT_ID,
        "status": "PRIMARY_INTERNAL_PASS_REFERENCE_PENDING" if all(accepted) else "PRIMARY_NUMERICAL_FAILURE",
        "input": preparation["input"], "coefficient_identity": preparation["array_identities"],
        "preparation_sha256": args.preparation_sha256,
        "constants": preparation["constants"], "inventory": preparation["inventory"],
        "context": context, "algorithm": algorithm, "prefixes": prefixes,
        "observation_bins": observation_bins, "tails": tails,
        "birth_claim": birth_claim, "return_registry": return_registry,
        "numerical_acceptance": {"internal_pass": all(accepted),
            "independent_reference": "PENDING", "capture_reference_relative": 1e-9,
            "closure_relative": 1e-11, "source_tail_relative": 1e-13,
            "channel_tail_relative": 1e-12,
            "arithmetic_interval_certification": False,
            "continuous_energy_or_physical_model_error_bound": None},
        "artifacts": {"ARRAYS.npz": {"bytes": len(array_raw),
            "sha256": hashlib.sha256(array_raw).hexdigest(),
            "arrays": {key: array_identity(value) for key, value in output_arrays.items()}}},
        "full_source_native25": None, "source_parent_ion_chemistry": None,
        "physical_heating_completed": False, "absolute_worldtube_totals": None,
        "global_physical_completion": None, "global_physical_error": None,
        "old_science_replay": 0, "old_budget_carried": False,
        "scope": "new finite-time fixed100K conditional H1/He4 low-birth discrete recipient; no coupled bath or photon transport",
    }
    write_json(out / "RESULT.json", result)
    print(json.dumps({"status": result["status"], "prefixes": len(prefixes),
                      "observation_bins": len(observation_bins),
                      "return_claims": len(return_registry), "algorithm": algorithm}, allow_nan=False))
    need(all(accepted), "PRIMARY_INTERNAL_CONSERVATION_OR_TAIL_FAILURE")


if __name__ == "__main__":
    main()
