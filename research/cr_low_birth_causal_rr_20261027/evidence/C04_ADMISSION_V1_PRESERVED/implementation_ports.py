#!/usr/bin/env python3
"""Finite-bin ownership and RR-only native25 event ports for this new unit."""
import hashlib
import json
import math

from model import (CONSTANTS, FITS, FRAME, INVENTORY_ID, MAPPING, SOURCE_FAMILY,
                   SOURCE_PARTITION, SOURCE_STATE, T_END, UNIT_ID, need, scalar)


CHANNELS = {
    "H": {"target": "H1II", "target_state": "bare",
          "product": "H1I", "final_state": "1s", "isotope": "H1",
          "product_index": 1, "target_index": 2, "g_bound": 2, "g_ion": 1, "d": 1},
    "He": {"target": "He4II", "target_state": "1s",
           "product": "He4I", "final_state": "1s2_singlet", "isotope": "He4",
           "product_index": 10, "target_index": 11, "g_bound": 1, "g_ion": 2, "d": 4},
}


def context_record(gas):
    values = gas["values"]
    context = {
        "unit": UNIT_ID, "source_family_id": SOURCE_FAMILY,
        "birth_partition_id": SOURCE_PARTITION,
        "source_record_state_id": SOURCE_STATE,
        "donor_state_id": INVENTORY_ID, "recipient_state_id": INVENTORY_ID,
        "inventory_id": INVENTORY_ID, "inventory_values": dict(values),
        "donor_frame": FRAME, "recipient_frame": FRAME,
        "isotope_mapping": MAPPING, "native_birth_support_eV": [.1, 10.],
        "known_history_s": [0., T_END], "clock_origin_s": 0.,
        "history_outside": "unknown", "proper_volume_mode": "fixed",
        "proper_volume_m3": None, "proper_clock": "proper_s",
        "donor_nb_m3": values["n_b_m3"], "recipient_nb_m3": values["n_b_m3"],
        "normalization": {"source_clock_factor": 1., "source_volume_factor": 1.,
                          "source_target_density": "already_included",
                          "new_source_multipliers_applied": [],
                          "rr_target_density_applications": 1},
        "constant_inventory": True, "component": "ground_spontaneous_only",
        "angular_scope": "scalar", "recoil": "zero",
        "channels": {key: dict(value) for key, value in CHANNELS.items()},
        "full_source_native25": None, "source_parent_ion_chemistry": None,
    }
    validate_context(context)
    return context


def validate_context(context):
    need(type(context) is dict and context.get("unit") == UNIT_ID, "EXACT_UNIT_CONTEXT_REQUIRED")
    need(context.get("source_family_id") == SOURCE_FAMILY
         and context.get("birth_partition_id") == SOURCE_PARTITION,
         "SOURCE_FAMILY_OR_PARTITION_MISMATCH")
    need(context.get("source_record_state_id") == SOURCE_STATE
         and context.get("donor_state_id") == INVENTORY_ID
         and context.get("recipient_state_id") == INVENTORY_ID
         and context.get("inventory_id") == INVENTORY_ID, "MATCHING_EXPLICIT_STATE_REQUIRED")
    need(context.get("donor_frame") == FRAME and context.get("recipient_frame") == FRAME,
         "MIXED_FRAME_REFUSED")
    need(context.get("isotope_mapping") == MAPPING, "WRONG_ISOTOPE_MAPPING")
    need(context.get("native_birth_support_eV") == [.1, 10.], "NATIVE_BIRTH_SUPPORT_CHANGED")
    need(context.get("known_history_s") == [0., T_END]
         and context.get("clock_origin_s") == 0.
         and context.get("history_outside") == "unknown", "ACTUAL_FINITE_HISTORY_REQUIRED")
    need(context.get("proper_clock") == "proper_s"
         and context.get("proper_volume_mode") == "fixed"
         and context.get("proper_volume_m3") is None, "PROPER_CLOCK_VOLUME_CONTRACT_MISMATCH")
    expected_norm = {"source_clock_factor": 1., "source_volume_factor": 1.,
                     "source_target_density": "already_included",
                     "new_source_multipliers_applied": [],
                     "rr_target_density_applications": 1}
    need(context.get("normalization") == expected_norm, "DUPLICATE_OR_UNKNOWN_NORMALIZATION")
    need(context.get("constant_inventory") is True, "FROZEN_INVENTORY_REQUIRED")
    values = context.get("inventory_values", {})
    n_h = 140.
    n_he = n_h * .248 / (4 * (1 - .248))
    expected = {"n_H_m3": n_h, "n_He_m3": n_he,
                "n_e_m3": .01 * (n_h + n_he), "n_HII_m3": .01 * n_h,
                "n_HeII_m3": .01 * n_he, "n_HeIII_m3": 0.,
                "n_b_m3": n_h + 4 * n_he, "T_K": 100.}
    need(values == expected, "FROZEN_100K_INVENTORY_MISMATCH")
    nb = scalar(context.get("recipient_nb_m3"), "EXPLICIT_MATCHING_NB_REQUIRED", positive=True)
    need(context.get("donor_nb_m3") == nb == values["n_b_m3"], "EXPLICIT_MATCHING_NB_REQUIRED")
    need(context.get("component") == "ground_spontaneous_only"
         and context.get("angular_scope") == "scalar" and context.get("recoil") == "zero",
         "GROUND_SCALAR_ZERO_RECOIL_SCOPE_REQUIRED")
    need(context.get("channels") == CHANNELS, "ISOTOPE_STATE_BRANCH_OR_DEGENERACY_MISMATCH")
    need(context.get("source_parent_ion_chemistry") is None
         and context.get("full_source_native25") is None, "UNKNOWN_SOURCE_CHEMISTRY_MUST_REMAIN_NULL")
    return nb


def interval(value, reason):
    need(type(value) in (list, tuple) and len(value) == 2, reason)
    left = scalar(value[0], reason)
    right = scalar(value[1], reason)
    need(left < right, reason)
    return [left, right]


def overlaps(a, b):
    return max(a[0], b[0]) < min(a[1], b[1])


def canonical_id(payload, prefix):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return prefix + hashlib.sha256(raw).hexdigest()


def claim_birth(context, registry):
    validate_context(context)
    need(type(registry) is list, "SHARED_BIRTH_REGISTRY_REQUIRED")
    claim = {"family_id": context["source_family_id"],
             "native_birth_support_eV": list(context["native_birth_support_eV"]),
             "injection_window_s": list(context["known_history_s"])}
    for old in registry:
        need(not (old["family_id"] == claim["family_id"]
                  and overlaps(old["native_birth_support_eV"], claim["native_birth_support_eV"])
                  and overlaps(old["injection_window_s"], claim["injection_window_s"])),
             "DUPLICATE_OR_OVERLAPPING_SOURCE_BIRTH_CLAIM")
    claim["claim_id"] = canonical_id(claim, "birth-claim-")
    registry.append(claim)
    return claim


def claim_return(context, channel, window, registry, *, role="disjoint_observation_bin"):
    validate_context(context)
    need(channel in CHANNELS, "UNSUPPORTED_RR_CHANNEL")
    need(role == "disjoint_observation_bin", "CUMULATIVE_PREFIX_IS_NONADDITIVE")
    need(type(registry) is list, "SHARED_RETURN_REGISTRY_REQUIRED")
    window = interval(window, "FINITE_NONEMPTY_OBSERVATION_BIN_REQUIRED")
    need(0. <= window[0] < window[1] <= T_END, "OBSERVATION_OUTSIDE_KNOWN_HISTORY")
    claim = {"family_id": context["source_family_id"], "channel": channel,
             "native_birth_support_eV": list(context["native_birth_support_eV"]),
             "observation_bin_s": window}
    for old in registry:
        need(not (old["family_id"] == claim["family_id"] and old["channel"] == channel
                  and overlaps(old["native_birth_support_eV"], claim["native_birth_support_eV"])
                  and overlaps(old["observation_bin_s"], window)),
             "DUPLICATE_OR_OVERLAPPING_CAUSAL_RETURN")
    # Producer revisions and eventual/finite metadata are deliberately absent.
    claim["event_id"] = canonical_id(claim, "causal-rr-event-")
    claim["horizon"] = "finite_known_history_observation_bin"
    registry.append(claim)
    return claim


def native25_rr(context, captures, kinetics):
    nb = validate_context(context)
    need(set(captures) == set(CHANNELS) and set(kinetics) == set(CHANNELS),
         "EXACT_TWO_CHANNEL_EVENT_REQUIRED")
    result = [0.] * 25
    for channel in CHANNELS:
        count = scalar(captures[channel], "NONNEGATIVE_RR_COUNT_REQUIRED")
        kinetic = scalar(kinetics[channel], "NONNEGATIVE_CAPTURE_KINETIC_REQUIRED")
        need(count == 0. and kinetic == 0. or count > 0.
             and .1 * count <= kinetic * (1. + 4e-15)
             and kinetic <= 10. * count * (1. + 4e-15),
             "CAPTURE_KINETIC_SUPPORT_MISMATCH")
        row = CHANNELS[channel]
        result[row["product_index"]] = count / nb
        result[row["target_index"]] = -count / nb
    result[21] = -math.fsum(captures.values()) / nb
    result[22] = -math.fsum(kinetics.values()) * CONSTANTS["eV_J"] / nb
    return {"values": result, "order": "Y[21],zeta,w_nt,w_ext,logT",
            "kind": "integrated_RR_event_only", "delta_nb_m3": 0.,
            "nb_m3": nb, "same_state_inventory": INVENTORY_ID,
            "thermal_electron_change": math.fsum((result[2], result[11], -result[21])),
            "full_source_native25": None, "coupled_state_update": None,
            "logT_zero_semantics": "frozen diagnostic; no thermal evolution claim"}


def retained_port(context, channel, window, atom_energy, atom_counts):
    validate_context(context)
    need(channel in CHANNELS, "UNSUPPORTED_RR_CHANNEL")
    interval(window, "FINITE_PHOTON_OBSERVATION_BIN_REQUIRED")
    need(0 <= window[0] < window[1] <= T_END, "PHOTON_TIME_SUPPORT_EXPANSION")
    need(len(atom_energy) == len(atom_counts) and len(atom_energy) > 0,
         "EXPLICIT_PHOTON_ATOM_PAIRS_REQUIRED")
    threshold = FITS[channel][0]
    for energy, count in zip(atom_energy, atom_counts):
        scalar(float(energy), "FINITE_PHOTON_ENERGY_REQUIRED", positive=True)
        scalar(float(count), "NONNEGATIVE_PHOTON_COUNT_REQUIRED")
        need(.1 + threshold <= energy <= 10. + threshold and energy <= 50000.,
             "PHOTON_SUPPORT_EXPANSION")
    return {"port": "retained_photon", "channel": channel,
            "observation_bin_s": list(window), "native_birth_support_eV": [.1, 10.],
            "spectrum_kind": "explicit_operator_derived_discrete_capture_atoms",
            "atom_count": len(atom_counts), "frame": FRAME,
            "number_m3": math.fsum(map(float, atom_counts)),
            "energy_eV_m3": math.fsum(float(e) * float(n) for e, n in zip(atom_energy, atom_counts)),
            "w_ext": 0., "physical_heating": None, "escape_or_absorption": None,
            "absolute_worldtube_photon_count": None,
            "continuous_time_spectrum": None}
