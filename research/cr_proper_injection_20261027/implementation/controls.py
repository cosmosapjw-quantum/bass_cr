"""Targeted controls for new proper-injection contracts; no old science replay.

Run only under the separately frozen unit runner and budget. All fixtures here
are explicitly synthetic controls; no control supplies missing physical inputs.
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import sys

from ports import (ContractError, EV_J, attach_rr_return, build_source_event,
                   canonical_event_id, claim_injection, integrate_history,
                   normalize_to_proper, project_native25, validate_source)


def source_fixture(kind="electron", representation="moments"):
    isotope, coordinate = {"electron": ("e-", "kinetic_eV"),
                           "photon": ("gamma", "photon_energy_eV"),
                           "baryon": ("H1", "kinetic_eV")}[kind]
    source = {
        "schema": "CR_PROPER_SOURCE_V1",
        "source": {"repository": "synthetic/contract_controls", "revision": "a" * 40,
                   "payload_sha256": "b" * 64, "evidence_kind": "synthetic_control"},
        "particle": {"kind": kind, "isotope": isotope, "state": "explicit_control_state",
                     "energy_coordinate": coordinate},
        "medium": {"state_id": "synthetic-state-1", "frame": "bath_frame_rest_target",
                   "temperature_K": 10000.0, "proper_volume_mode": "fixed", "proper_volume_m3": 7.0},
        "isotope_mapping": "CONDITIONAL_ELEMENTAL_H_TO_H1_HE_TO_HE4",
        "support_eV": [1.0, 100.0], "representation": representation,
        "normalization": {"clock_measure": "proper_s", "volume_measure": "proper_m3",
                          "d_native_clock_d_proper_s": 1.0, "d_native_volume_d_proper_m3": 1.0,
                          "target_density_mode": "already_included", "target_density_m3": None,
                          "applied_tokens": []},
        "history_boundary": "unknown_outside_recorded_segments",
        "history": [{"start_s": 0.0, "stop_s": 2.0,
                     "number_coefficients": [0.0, 3.0], "energy_coefficients_eV": [0.0, 15.0]}]}
    source["source_event"] = build_source_event(
        physical_definition_sha256="1" * 64, energy_array_sha256="2" * 64,
        source_array_sha256="3" * 64, family_native_birth_support_eV=[1.0, 100.0],
        native_birth_support_eV=source["support_eV"], clock_origin_s=0.0)
    if representation == "atomic_bins":
        source["history"][0]["bins"] = [{"energy_eV": 5.0, "number_coefficients": [0.0, 3.0]}]
    return source


def response_fixture(injection):
    return {"state_id": injection["medium"]["state_id"], "frame": injection["medium"]["frame"],
            "temperature_K": injection["medium"]["temperature_K"],
            "isotope_mapping": injection["isotope_mapping"],
            "raw_source_digest": injection["raw_source_digest"],
            "history_digest": injection["history_digest"], "evidence_kind": "synthetic_control",
            "input_support_eV": injection["support_eV"],
            "source_distribution_qualification": "same_full_source_distribution",
            "return_horizon": "finite", "proper_time_window_s": injection["proper_time_window_s"],
            "method": "independently_supplied_control_moments",
            "channel": "He4III_to_He4II_1s", "threshold_eV": 54.42,
            "target_isotope": "He4", "final_state": "1s",
            "component": "ground_spontaneous_only",
            "angular_scope": "SCALAR_ISOTROPIC_ENSEMBLE_ONLY",
            "native_photon_max_eV": 50000.0, "mass_model": "stationary_heavy_target_zero_recoil",
            "capture_kinetic_support_eV": [1.0, 100.0],
            "revision": "c" * 40, "payload_sha256": "d" * 64,
            "count_m3": 1.0,
            "kinetic_energy_eV_m3": injection["coordinate_energy_eV_m3"] / injection["number_m3"]}


def run_c9_qualification_delta_controls():
    """Only the changed isotope/state/component guards; no old suite replay."""
    rows = []
    source = source_fixture()
    injection = integrate_history(source)
    response = response_fixture(injection)

    def reject(name, selected_injection, selected_response, expected_code):
        registry = []
        try:
            attach_rr_return(selected_injection, selected_response, return_registry=registry)
        except ContractError as exc:
            passed = expected_code in str(exc) and registry == []
        else:
            passed = False
        rows.append({"id": name, "pass": passed})

    wrong_source = deepcopy(source)
    wrong_source["isotope_mapping"] = "CONDITIONAL_ELEMENTAL_HE_TO_HE3"
    wrong_injection = integrate_history(wrong_source)
    reject("C9_both_sides_wrong_He3_mapping", wrong_injection, response_fixture(wrong_injection),
           "HE4_ISOTOPE_MAPPING_UNQUALIFIED")
    for name, key, value, code in (
        ("C9_wrong_target_isotope", "target_isotope", "He3", "RR_TARGET_ISOTOPE_MISMATCH"),
        ("C9_wrong_final_state", "final_state", "2s", "RR_FINAL_STATE_MISMATCH"),
        ("C9_stimulated_component", "component", "ground_stimulated", "RR_COMPONENT_MISMATCH"),
        ("C9_wrong_angular_scope", "angular_scope", "angle_resolved", "RR_ANGULAR_SCOPE_MISMATCH"),
        ("C9_missing_target_isotope", "target_isotope", None, "RR_TARGET_ISOTOPE_MISMATCH"),
        ("C9_missing_final_state", "final_state", None, "RR_FINAL_STATE_MISMATCH"),
        ("C9_missing_component", "component", None, "RR_COMPONENT_MISMATCH"),
        ("C9_missing_angular_scope", "angular_scope", None, "RR_ANGULAR_SCOPE_MISMATCH"),
    ):
        reject(name, injection, dict(response, **{key: value}), code)
    for label, mapping in (
        ("combined_H1_He4", "CONDITIONAL_ELEMENTAL_H_TO_H1_HE_TO_HE4"),
        ("inherited_He4", "CONDITIONAL_ELEMENTAL_HE_TO_HE4"),
    ):
        admitted_source = deepcopy(source)
        admitted_source["isotope_mapping"] = mapping
        admitted_injection = integrate_history(admitted_source)
        registry = []
        result = attach_rr_return(admitted_injection, response_fixture(admitted_injection),
                                  return_registry=registry)
        rows.append({"id": "C9_approved_mapping_" + label,
                     "pass": result["compatible"] and len(registry) == 1
                     and result["density_delta"]["native21_m3"][11] == 1.0
                     and result["density_delta"]["native21_m3"][12] == -1.0})
    return {"schema": "CR_PROPER_INJECTION_C9_QUALIFICATION_DELTA_V1",
            "fixture_kind": "synthetic_control", "checks": rows,
            "passed": sum(row["pass"] for row in rows), "total": len(rows),
            "all_pass": all(row["pass"] for row in rows), "old_science_replays": 0}


def run_controls():
    rows = []

    def check(name, condition):
        rows.append({"id": name, "pass": bool(condition)})

    def rejects(name, action, code):
        try:
            action()
        except ContractError as exc:
            check(name, code in str(exc))
        else:
            check(name, False)

    for kind in ("electron", "photon", "baryon"):
        result = integrate_history(source_fixture(kind))
        check(kind + "_linear_N", result["number_m3"] == 6.0)
        check(kind + "_linear_E", result["coordinate_energy_eV_m3"] == 30.0)
        check(kind + "_proper_rate", result["endpoint_number_rate_m3_s"] == 6.0)
        check(kind + "_worldtube_count", result["worldtube_count"] == 42.0)
        check(kind + "_nb_missing", result["native25"] is None and result["nb_m3"] is None)
        check(kind + "_no_reconstructed_spectrum", result["spectrum"] is None)
    s = source_fixture()
    proper = normalize_to_proper(s)
    rejects("repeat_normalization", lambda: normalize_to_proper(proper), "RAW_SOURCE_REQUIRED")
    forged_proper = deepcopy(proper)
    forged_proper["history"][0]["number_coefficients"][1] *= 2
    rejects("changed_proper_coefficients", lambda: integrate_history(forged_proper),
            "PROPER_INJECTION_CHANGED_AFTER_NORMALIZATION")
    s2 = deepcopy(s)
    s2["normalization"].update(clock_measure="native_clock", volume_measure="native_volume",
                              d_native_clock_d_proper_s=2.0, d_native_volume_d_proper_m3=3.0,
                              target_density_mode="rate_coefficient", target_density_m3=7.0)
    scaled = integrate_history(s2)
    check("clock_argument_and_rate_each_once", scaled["number_m3"] == 6 * 2 * 2 * 3 * 7)
    check("clock_energy_same_factor", scaled["coordinate_energy_eV_m3"] == 30 * 2 * 2 * 3 * 7)
    s3 = deepcopy(s)
    s3["history"][0]["number_coefficients"] = [2.0, 3.0, 6.0]
    s3["history"][0]["energy_coefficients_eV"] = [10.0, 15.0, 30.0]
    check("quadratic_exact_integral", integrate_history(s3)["number_m3"] == 26.0)
    check("subwindow_exact_integral", integrate_history(s, [1.0, 2.0])["number_m3"] == 4.5)
    pieces = deepcopy(s)
    pieces["history"] = [{"start_s": 0.0, "stop_s": 1.0, "number_coefficients": [2.0],
                          "energy_coefficients_eV": [10.0]},
                         {"start_s": 2.0, "stop_s": 3.0, "number_coefficients": [2.0],
                          "energy_coefficients_eV": [10.0]}]
    rejects("unknown_history_gap", lambda: integrate_history(pieces), "TIME_HISTORY_GAP_UNQUALIFIED")
    rejects("point_inside_unknown_gap", lambda: integrate_history(pieces, [1.5, 1.5]),
            "TIME_HISTORY_GAP_UNQUALIFIED")
    check("subwindow_within_known_piece", integrate_history(pieces, [2.0, 3.0])["number_m3"] == 2)
    pieces["history_gap_policy"] = "explicit_zero_gaps"
    piece_result = integrate_history(pieces)
    check("explicit_zero_gap", piece_result["number_m3"] == 4 and piece_result["exposure_s"] == 3
          and piece_result["supported_duration_s"] == 2 and piece_result["known_zero_gap_duration_s"] == 1)
    check("explicit_gap_endpoint_rate", integrate_history(pieces, [0, 1.5])["endpoint_number_rate_m3_s"] == 0)
    explicit_zero = deepcopy(pieces)
    del explicit_zero["history_gap_policy"]
    explicit_zero["history"].insert(1, {"start_s": 1.0, "stop_s": 2.0,
                                       "number_coefficients": [0.0], "energy_coefficients_eV": [0.0]})
    check("explicit_zero_segment", integrate_history(explicit_zero)["number_m3"] == 4)
    rejects("post_history_not_zero_extended", lambda: integrate_history(s, [0, 3]), "TIME_SUPPORT_EXTENSION")
    check("left_rate_at_history_start_unknown", integrate_history(s, [0, 0])["endpoint_number_rate_m3_s"] is None)
    pieces["history"][1]["start_s"] = 0.5
    rejects("overlapping_history", lambda: validate_source(pieces), "OVERLAPPING_HISTORY")
    zero = deepcopy(s)
    zero["history"][0].update(number_coefficients=[0.0], energy_coefficients_eV=[0.0])
    check("zero_source", integrate_history(zero)["number_m3"] == 0)
    no_history = deepcopy(s)
    no_history["history"] = None
    null = integrate_history(no_history)
    check("missing_history_nulls", all(null[k] is None for k in
          ("number_m3", "coordinate_energy_J_m3", "endpoint_number_rate_m3_s", "exposure_s", "native25")))
    rejects("no_mean_time_exposure", lambda: integrate_history(no_history, [0, 2]), "MISSING_HISTORY")
    bins = integrate_history(source_fixture(representation="atomic_bins"))
    check("atomic_weights_not_samples", bins["spectrum"] == [{"energy_eV": 5.0, "count_m3": 6.0,
                                                            "segment_start_s": 0.0}])

    def mutated(path, value):
        result = deepcopy(s)
        target = result
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return result

    for name, path, value, code in [
        ("duplicate_target_density", ["normalization", "target_density_m3"], 5, "DUPLICATE_TARGET"),
        ("duplicate_clock", ["normalization", "d_native_clock_d_proper_s"], 2, "PROPER_CLOCK"),
        ("duplicate_volume", ["normalization", "d_native_volume_d_proper_m3"], 2, "PROPER_VOLUME"),
        ("forged_applied_token", ["normalization", "applied_tokens"], ["clock"], "ALREADY_APPLIED"),
        ("negative_source", ["history", 0, "number_coefficients"], [-1, 3], "FINITE_DOMAIN"),
        ("NaN_source", ["history", 0, "number_coefficients"], [float("nan"), 3], "FINITE_DOMAIN"),
        ("infinite_endpoint", ["history", 0, "stop_s"], float("inf"), "FINITE_DOMAIN"),
        ("support_extension", ["support_eV"], [10, 100], "MOMENT_OUTSIDE"),
        ("zero_counterpart", ["history", 0, "energy_coefficients_eV"], [1, 15], "ZERO_COUNTERPART"),
        ("no_frame", ["medium", "frame"], "", "REQUIRED"),
        ("variable_volume", ["medium", "proper_volume_mode"], "expanding", "VARYING_VOLUME"),
        ("electron_isotope", ["particle", "isotope"], "He4", "ELECTRON_ISOTOPE"),
        ("unfrozen_revision", ["source", "revision"], "main", "IMMUTABLE_SOURCE"),
    ]:
        rejects(name, lambda p=path, v=value: validate_source(mutated(p, v)), code)
    bad_bins = source_fixture(representation="atomic_bins")
    bad_bins["history"][0]["bins"][0]["energy_eV"] = 1000
    rejects("bin_support_extension", lambda: validate_source(bad_bins), "SUPPORT_EXTENSION")
    result = integrate_history(s)
    registry = []
    claim_injection(result, registry)
    provenance_variant = deepcopy(s)
    provenance_variant["source"].update(revision="e" * 40, payload_sha256="f" * 64)
    variant_result = integrate_history(provenance_variant)
    check("producer_variant_same_family", variant_result["source_event"]["family_id"] == result["source_event"]["family_id"]
          and variant_result["raw_source_digest"] != result["raw_source_digest"])
    rejects("fullBED_legacy_same_injection", lambda: claim_injection(variant_result, registry),
            "OVERLAPPING_SAME_SOURCE_EVENT_CLAIM")
    rejects("malformed_registry_not_silently_skipped", lambda: claim_injection(result, [{}]),
            "REGISTRY_SOURCE_FAMILY_REQUIRED")
    low, high = deepcopy(s), deepcopy(s)
    for selected, support, ncoef, ecoef in ((low, [1.0, 10.0], 2.0, 2.0),
                                         (high, [10.0, 100.0], 1.0, 13.0)):
        selected["support_eV"] = support
        selected["history"][0].update(number_coefficients=[0.0, ncoef], energy_coefficients_eV=[0.0, ecoef])
        selected["source_event"] = build_source_event(
            physical_definition_sha256="1" * 64, energy_array_sha256="2" * 64,
            source_array_sha256="3" * 64, family_native_birth_support_eV=[1.0, 100.0],
            native_birth_support_eV=support, clock_origin_s=0.0)
    low_result, high_result = integrate_history(low), integrate_history(high)
    rejects("selected_total_low_overlap", lambda: claim_injection(low_result, registry),
            "OVERLAPPING_SAME_SOURCE_EVENT_CLAIM")
    split_registry = []
    claim_injection(low_result, split_registry)
    claim_injection(high_result, split_registry)
    check("low_high_disjoint_claims", len(split_registry) == 2
          and low_result["number_m3"] + high_result["number_m3"] == result["number_m3"]
          and low_result["coordinate_energy_eV_m3"] + high_result["coordinate_energy_eV_m3"] == result["coordinate_energy_eV_m3"])
    time_registry = []
    claim_injection(integrate_history(s, [0.0, 1.0]), time_registry)
    claim_injection(integrate_history(s, [1.0, 2.0]), time_registry)
    check("disjoint_time_claims", len(time_registry) == 2)
    bad_clock = deepcopy(s)
    bad_clock["source_event"]["clock_origin_s"] = 1.0
    rejects("unbound_clock_origin", lambda: validate_source(bad_clock), "SOURCE_EVENT_FAMILY_OR_PARTITION_ID_MISMATCH")
    response = response_fixture(result)
    seen = set()
    return_registry = []
    rejects("RR_shared_registry_required", lambda: attach_rr_return(result, response),
            "SHARED_RETURN_REGISTRY_REQUIRED")
    rr = attach_rr_return(result, response, return_registry=return_registry, seen_event_ids=seen)
    check("RR_count", rr["integrated_count_m3"] == 1)
    check("RR_retained_photon", rr["retained_photon_port"]["integrated_energy_J_m3"] == (5 + 54.42) * EV_J)
    check("RR_external_ledger_zero", rr["density_delta"]["w_ext_J_m3"] == 0)
    check("RR_heat_null", rr["physical_heating_J_m3"] is None)
    rejects("same_event_duplicate", lambda: attach_rr_return(result, response, return_registry=return_registry,
                                                              seen_event_ids=seen), "DUPLICATE_SAME_EVENT")
    revised_response = dict(response, payload_sha256="e" * 64, return_horizon="eventual")
    rejects("same_event_new_representation", lambda: attach_rr_return(result, revised_response,
                                                                       return_registry=return_registry, seen_event_ids=seen),
            "DUPLICATE_SAME_EVENT")
    variant_response = response_fixture(variant_result)
    check("RR_id_independent_of_producer", canonical_event_id(result, response)
          == canonical_event_id(variant_result, variant_response))
    scalar_repr = deepcopy(s)
    scalar_repr["source_event"].update(clock_origin_s=0, family_native_birth_support_eV=[1, 100],
                                      native_birth_support_eV=[1, 100])
    scalar_result = integrate_history(scalar_repr)
    check("RR_id_independent_of_integer_float_metadata", canonical_event_id(result, response)
          == canonical_event_id(scalar_result, response_fixture(scalar_result)))
    rejects("RR_variant_same_event", lambda: attach_rr_return(variant_result, variant_response,
                                                               return_registry=return_registry, seen_event_ids=seen),
            "DUPLICATE_SAME_EVENT")
    rejects("RR_total_low_overlap", lambda: attach_rr_return(low_result, response_fixture(low_result),
                                                              return_registry=return_registry),
            "OVERLAPPING_SAME_RR_RETURN_CLAIM")
    first_half = integrate_history(s, [0.0, 1.0])
    second_half = integrate_history(s, [1.0, 2.0])
    rejects("RR_whole_split_time_overlap", lambda: attach_rr_return(first_half, response_fixture(first_half),
                                                                     return_registry=return_registry),
            "OVERLAPPING_SAME_RR_RETURN_CLAIM")
    check("failed_RR_claim_does_not_mutate_registry", len(return_registry) == 1)
    disjoint_returns = []
    attach_rr_return(first_half, response_fixture(first_half), return_registry=disjoint_returns)
    attach_rr_return(second_half, response_fixture(second_half), return_registry=disjoint_returns)
    check("RR_disjoint_time_returns", len(disjoint_returns) == 2)
    disjoint_birth_returns = []
    attach_rr_return(low_result, response_fixture(low_result), return_registry=disjoint_birth_returns)
    attach_rr_return(high_result, response_fixture(high_result), return_registry=disjoint_birth_returns)
    check("RR_disjoint_birth_returns", len(disjoint_birth_returns) == 2)
    for field, value, code in [
        ("state_id", "other-state", "DONOR_RECIPIENT_STATE_MISMATCH"),
        ("temperature_K", 100, "DONOR_RECIPIENT_STATE_MISMATCH"),
        ("frame", "other-frame", "MIXED_FRAME"),
        ("isotope_mapping", "elemental-He-to-He3", "ISOTOPE_MAPPING_MISMATCH"),
        ("raw_source_digest", "e" * 64, "SOURCE_IDENTITY_MISMATCH"),
        ("history_digest", "f" * 64, "SOURCE_HISTORY_MISMATCH"),
        ("input_support_eV", [1, 1000], "SUPPORT_MISMATCH"),
        ("method", "conditional_mean_time_as_exposure", "MEAN_TIME_IS_NOT_EXPOSURE"),
        ("method", "saved_resolvent_eventual", "EVENTUAL_RESOLVENT_NOT_FINITE_RETURN"),
        ("source_distribution_qualification", "moments_only", "SOURCE_SPECTRAL_PROJECTION_UNQUALIFIED"),
        ("proper_time_window_s", [0, 20], "FINITE_RETURN_WINDOW_MISMATCH"),
    ]:
        bad = dict(response, **{field: value})
        rejected = attach_rr_return(result, bad)
        check("RR_refusal_" + field + "_" + code,
              not rejected["compatible"] and code in rejected["reasons"])
    eventual = dict(response, return_horizon="eventual")
    check("eventual_does_not_become_finite", not attach_rr_return(result, eventual, return_registry=[])["finite_return_claim"])
    nb = {"donor_state_id": s["medium"]["state_id"], "recipient_state_id": s["medium"]["state_id"],
          "frame": s["medium"]["frame"], "nb_m3": 10.0, "normalization": "actual_baryon_density"}
    rr_native = attach_rr_return(result, response, return_registry=[], nb_context=nb)["native25"]["delta"]
    check("native25_RR_stoichiometry", rr_native[11] == 0.1 and rr_native[12] == -0.1 and rr_native[21] == -0.1)
    check("native25_RR_external_zero", rr_native[23] == 0 and rr_native[24] == 0)
    delta = {"native21_m3": [0.0] * 21, "fast_electrons_m3": 0.0,
             "w_nt_J_m3": 0.0, "w_ext_J_m3": 0.0, "baryons_m3": 2.0}
    delta["native21_m3"][1] = 2
    initial = [0.0] * 25
    initial[12], initial[21], initial[22] = 0.25, 0.1, 3.0
    native = project_native25(delta, nb, source_state_id=s["medium"]["state_id"],
                              frame=s["medium"]["frame"], initial_native25=initial)
    check("baryon_denominator_species", native["delta"][1] == 1 / 6 and native["delta"][12] == -1 / 24)
    check("baryon_denominator_electron", math.isclose(native["delta"][21], -1 / 60, rel_tol=1e-15))
    check("baryon_denominator_energy", native["delta"][22] == -0.5)
    rejects("changing_nb_no_state", lambda: project_native25(delta, nb, source_state_id=s["medium"]["state_id"],
                                                             frame=s["medium"]["frame"]), "CHANGING_NB")
    rejects("borrowed_nb", lambda: project_native25(delta, dict(nb, donor_state_id="PW19_other_state"),
                                                    source_state_id=s["medium"]["state_id"],
                                                    frame=s["medium"]["frame"], initial_native25=initial), "STATE_MISMATCH")
    rows.extend(run_c9_qualification_delta_controls()["checks"])
    return {"schema": "CR_PROPER_INJECTION_CONTROLS_V1", "fixture_kind": "synthetic_control",
            "checks": rows, "passed": sum(row["pass"] for row in rows), "total": len(rows),
            "all_pass": all(row["pass"] for row in rows), "old_science_replays": 0}


if __name__ == "__main__":
    result = run_controls()
    encoded = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if len(sys.argv) == 2:
        target = Path(sys.argv[1])
        with target.open("x") as stream:
            stream.write(encoded)
    else:
        print(encoded, end="")
    raise SystemExit(0 if result["all_pass"] else 1)
