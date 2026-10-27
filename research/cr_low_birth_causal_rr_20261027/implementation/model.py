#!/usr/bin/env python3
"""Pinned PHYS02 low-birth input and a new, explicitly frozen 100 K recipient.

No module-level scientific calculation. Callers run only through the bounded
runner after C4. Historical transport/source modules are never imported.
"""
import hashlib
import json
import math
from pathlib import Path

import numpy as np


UNIT_ID = "CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1"
CONTRACT_SHA256 = "0766fa66e643de2b50d797fa94838cb989e69c8d3aaa47fe8c31673764757210"
SOURCE_SHA256 = "8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf"
SOURCE_BYTES = 4394309
SOURCE_PATH = "research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json"
SOURCE_PAYLOAD_SHA256 = "7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc"
SOURCE_RETRIEVAL_REVISION = "ec463db0c7e5c7fb5070796071c926caa4db6445"
SOURCE_RETAINED_REVISION = "4ca5a90de79c8fb82a25fd9e83615bec0dfa870b"
SOURCE_FAMILY = "cr-source-family-13b884c8b34cc89c60e5a70842120ee2c8f136645de3592cb87fac2eefa636a8"
SOURCE_PARTITION = "birth-partition-0a332c1184f24587f59e32404c7c1673c5f84fedc0e3d93ffe2b376bc2c75204"
SOURCE_STATE = "PHYS02_T100K_nH140m3_YHe0.248_xHII0.01_xHeII0.01_xHeIII0_FIXED"
FRAME = "prescribed_gas_rest_frame_scalar"
MAPPING = "CONDITIONAL_ELEMENTAL_H_TO_H1_HE_TO_HE4"
INVENTORY_ID = "CR_LOW_BIRTH_100K_CONDITIONAL_H1_HE4_FIXED_INVENTORY_V1"
TAG = "direct_0p1_10"
T_END = 1.e10
CUTOFF_EV = .1
UPPER_EV = 10.
ACTIVE_SIZE = 3200
PROVIDER_SHA256 = "71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d"
TABLE_SHA256 = "a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389"
FIT_KEYS = ("I_eV", "Emax_eV", "E0_eV", "sigma0_Mb", "ya", "P", "yw", "y0", "y1")
FITS = {
    "H": (13.60, 50000., .4298, 54750., 32.88, 2.963, 0., 0., 0.),
    "He": (24.59, 50000., 13.61, 949.2, 1.469, 3.188, 2.039, .4434, 2.136),
}
DEGENERACY = {"H": 1., "He": 4.}
CONSTANTS = {"electron_mass_kg": 9.1093837139e-31,
             "epsilon0_F_m": 8.8541878188e-12,
             "eV_J": 1.602176634e-19,
             "h_J_s": 6.62607015e-34,
             "c_m_s": 299792458.}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def scalar(value, reason, *, positive=False):
    need(type(value) in (int, float) and math.isfinite(value), reason)
    need(value > 0 if positive else value >= 0, reason)
    return float(value)


def json_bytes(value):
    return (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, "DUPLICATE_JSON_KEY:" + key)
            out[key] = value
        return out

    def nonfinite(value):
        raise ValueError("NONFINITE_JSON_LITERAL:" + value)

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def write_json(path, value):
    with Path(path).open("xb") as stream:
        stream.write(json_bytes(value))


def write_npz(path, arrays):
    with Path(path).open("xb") as stream:
        np.savez(stream, **arrays)


def array_identity(values):
    array = np.asarray(values)
    need(array.dtype.kind in "fi", "NUMERIC_ARRAY_REQUIRED")
    array = np.asarray(array, dtype="<f8", order="C")
    return {"shape": list(array.shape), "dtype": "<f8", "order": "C",
            "sha256": sha256_bytes(array.tobytes(order="C"))}


def checked_file(path, digest, length=None):
    raw = Path(path).read_bytes()
    need(sha256_bytes(raw) == digest, "FILE_IDENTITY_MISMATCH:" + str(path))
    need(length is None or len(raw) == length, "FILE_LENGTH_MISMATCH:" + str(path))
    return raw


def source_arrays(path):
    """Read the preserved ramp atoms; no source regeneration or normalization."""
    raw = checked_file(path, SOURCE_SHA256, SOURCE_BYTES)
    rows = strict_json(raw)
    need(type(rows) is list, "SOURCE_RECORD_LIST_REQUIRED")
    low = [row for row in rows if row.get("tag") == TAG]
    need(len(low) == 1, "EXACT_LOW_NATIVE_BIRTH_TAG_REQUIRED")
    source = low[0]["source"]
    validate_actual_source(source)
    bins = source["history"][0]["bins"]
    need(len(bins) == ACTIVE_SIZE + 1, "EXACT_3200_ACTIVE_PLUS_CUTOFF_REQUIRED")
    active = bins[:-1]
    cutoff = bins[-1]
    need([row["stored_node_index"] for row in active] == list(range(ACTIVE_SIZE)),
         "STORED_NODE_ORDER_OR_BIRTH_PARTITION_CHANGED")
    need(cutoff["stored_node_index"] == "cutoff_boundary"
         and cutoff["energy_eV"] == CUTOFF_EV, "DIRECT_CUTOFF_ATOM_REQUIRED")
    for row in bins:
        coefficients = row["number_coefficients"]
        need(type(coefficients) is list and len(coefficients) == 2
             and coefficients[0] == 0., "EXACT_AFFINE_RAMP_SOURCE_REQUIRED")
        scalar(coefficients[1], "NONNEGATIVE_SOURCE_ATOM_REQUIRED")
        scalar(row["energy_eV"], "POSITIVE_SOURCE_ENERGY_REQUIRED", positive=True)
    energy = np.asarray([row["energy_eV"] for row in active], dtype=np.float64)
    amplitude = np.asarray([row["number_coefficients"][1] for row in active], dtype=np.float64)
    need(energy[0] == .10309375000000001 and energy[-1] == UPPER_EV
         and np.all(np.diff(energy) > 0) and np.all(energy > CUTOFF_EV),
         "STORED_LOW_ENERGY_SUPPORT_REQUIRED")
    acut = float(cutoff["number_coefficients"][1])
    declared = source["history"][0]
    summed_n = math.fsum([*map(float, amplitude), acut])
    summed_e = math.fsum([*(float(e) * float(a) for e, a in zip(energy, amplitude)),
                         CUTOFF_EV * acut])
    # This checks readback consistency; it does not replace or renormalize atoms.
    need(abs(summed_n - declared["number_coefficients"][1])
         <= 2e-14 * summed_n, "SOURCE_NUMBER_SUM_DISAGREES_WITH_STORED_RECORD")
    need(abs(summed_e - declared["energy_coefficients_eV"][1])
         <= 2e-14 * summed_e, "SOURCE_ENERGY_SUM_DISAGREES_WITH_STORED_RECORD")
    identity = {"path": SOURCE_PATH, "sha256": SOURCE_SHA256, "bytes": len(raw),
                "selected_tag": TAG, "retained_revision": SOURCE_RETAINED_REVISION,
                "retrieval_revision": SOURCE_RETRIEVAL_REVISION,
                "retained_revision_is_first_generating_commit": False,
                "source_payload_sha256": SOURCE_PAYLOAD_SHA256,
                "family_id": SOURCE_FAMILY, "partition_id": SOURCE_PARTITION,
                "native_birth_support_eV": [.1, 10.],
                "history_s": [0., T_END], "history_outside": "unknown",
                "subset_energy": array_identity(energy),
                "subset_A": array_identity(amplitude),
                "A_cutoff_m3_s2": acut, "A_cutoff_float_hex": acut.hex(),
                "stored_total_A_number_m3_s2": declared["number_coefficients"][1],
                "stored_total_A_energy_eV_m3_s2": declared["energy_coefficients_eV"][1],
                "normalization_applied_by_this_unit": [], "old_source_replay": 0}
    return energy, amplitude, acut, identity, source


def validate_actual_source(source):
    need(source.get("schema") == "CR_PROPER_SOURCE_V1", "SOURCE_SCHEMA_MISMATCH")
    need(source.get("representation") == "atomic_bins", "ACTUAL_ATOMIC_BINS_REQUIRED")
    provenance = source.get("source", {})
    need(provenance.get("revision") == SOURCE_RETRIEVAL_REVISION
         and provenance.get("payload_sha256") == SOURCE_PAYLOAD_SHA256
         and provenance.get("repository") == "cosmosapjw-quantum/bass_cr",
         "EXACT_SOURCE_PROVENANCE_REQUIRED")
    need(source.get("particle") == {"kind": "electron", "isotope": "e-",
         "state": "PHYS02_direct_secondary_birth", "energy_coordinate": "kinetic_eV"},
         "ACTUAL_ELECTRON_BIRTH_STATE_REQUIRED")
    medium = source.get("medium", {})
    need(medium.get("state_id") == SOURCE_STATE and medium.get("frame") == FRAME
         and medium.get("temperature_K") == 100.
         and medium.get("proper_volume_mode") == "fixed"
         and medium.get("proper_volume_m3") is None, "SOURCE_PHYSICAL_STATE_MISMATCH")
    need(source.get("isotope_mapping") == MAPPING, "ISOTOPE_MAPPING_MISMATCH")
    need(source.get("support_eV") == [.1, 10.], "SOURCE_SUPPORT_EXPANSION_REFUSED")
    event = source.get("source_event", {})
    need(event.get("family_id") == SOURCE_FAMILY
         and event.get("partition_id") == SOURCE_PARTITION
         and event.get("native_birth_support_eV") == [.1, 10.]
         and event.get("family_native_birth_support_eV") == [.1, 900.]
         and event.get("clock_origin_s") == 0., "PHYSICAL_SOURCE_FAMILY_MISMATCH")
    norm = source.get("normalization", {})
    need(norm == {"clock_measure": "proper_s", "volume_measure": "proper_m3",
          "d_native_clock_d_proper_s": 1., "d_native_volume_d_proper_m3": 1.,
          "target_density_mode": "already_included", "target_density_m3": None,
          "applied_tokens": []}, "SOURCE_NORMALIZATION_OR_DUPLICATE_FACTOR_REFUSED")
    history = source.get("history")
    need(source.get("history_boundary") == "unknown_outside_recorded_segments"
         and type(history) is list and len(history) == 1
         and history[0].get("start_s") == 0.
         and history[0].get("stop_s") == T_END, "FINITE_ACTUAL_HISTORY_REQUIRED")


def inventory():
    n_h = 140.
    n_he = n_h * .248 / (4 * (1 - .248))
    n_e = .01 * (n_h + n_he)
    nb = n_h + 4 * n_he
    values = {"n_H_m3": n_h, "n_He_m3": n_he, "n_e_m3": n_e,
              "n_HII_m3": .01 * n_h, "n_HeII_m3": .01 * n_he,
              "n_HeIII_m3": 0., "n_b_m3": nb, "T_K": 100.}
    return {"inventory_id": INVENTORY_ID, "isotope_mapping": MAPPING,
            "frame": FRAME, "source_state_id": SOURCE_STATE,
            "constant_inventory": True,
            "semantics": {"n_H": "140", "n_He": "1085/94",
                          "n_e": "2849/1880", "n_b": "8750/47"},
            "recipe": "nHe=140*.248/(4*(1-.248)); ne=.01*(140+nHe); nb=140+4*nHe",
            "values": values, "binary64_hex": {k: v.hex() for k, v in values.items()},
            "model_choice": "new explicit conditional H1/He4-only inventory",
            "prior_PR109_nb_null_modified": False,
            "source_parent_ion_chemistry": None}


def coefficient_arrays(energy, gas):
    energy = np.asarray(energy, dtype=np.float64)
    need(energy.ndim == 1 and energy.size > 0 and np.all(np.isfinite(energy))
         and np.all(energy > CUTOFF_EV) and np.all(energy <= UPPER_EV)
         and np.all(np.diff(energy) > 0), "ORDERED_LOW_ACTIVE_ENERGY_REQUIRED")
    c = CONSTANTS
    ev, me, eps, h, light = (c[k] for k in
        ("eV_J", "electron_mass_kg", "epsilon0_F_m", "h_J_s", "c_m_s"))
    hbar = h / (2 * math.pi)
    kappa = ev ** 2 / (4 * math.pi * eps)
    ne = gas["values"]["n_e_m3"]
    v = np.sqrt(2 * energy * ev / me)
    omega = math.sqrt(ne * ev ** 2 / (eps * me))
    classical = np.log(v * energy * ev / (kappa * omega))
    quantum = np.log(2 * energy * ev / (hbar * omega))
    clog = np.minimum(classical, quantum)
    need(np.all(np.isfinite(clog)) and np.all(clog > 0), "POSITIVE_COULOMB_LOG_REQUIRED")
    b = 4 * math.pi * kappa ** 2 * ne / (me * v * ev) * clog
    gaps = np.diff(np.concatenate(([CUTOFF_EV], energy)))
    drift = b / gaps
    out = {"E_eV": energy, "b_eV_s": b, "drift_s_inv": drift,
           "log_classical": classical, "log_quantum": quantum,
           "v_m_s": v}
    for channel, density_key in (("H", "n_HII_m3"), ("He", "n_HeII_m3")):
        photo = energy + FITS[channel][0]
        sigma_pi = photo_cm2(channel, photo)
        sigma_rr = sigma_pi * photo ** 2 / (DEGENERACY[channel] * (me * light ** 2 / ev) * energy)
        lam = gas["values"][density_key] * v * (1e-4 * sigma_rr)
        need(np.all(np.isfinite(lam)) and np.all(lam > 0), "POSITIVE_ACTUAL_RR_HAZARD_REQUIRED")
        out["lambda_" + channel + "_s_inv"] = lam
        out["sigma_PI_" + channel + "_cm2"] = sigma_pi
        out["sigma_RR_" + channel + "_cm2"] = sigma_rr
    return out


def photo_cm2(channel, photon_energy):
    need(channel in FITS, "UNSUPPORTED_GROUND_PHOTO_CHANNEL")
    energy = np.asarray(photon_energy, dtype=np.float64)
    threshold, upper, e0, sigma0, ya, power, yw, y0, y1 = FITS[channel]
    need(np.all(np.isfinite(energy)) and np.all(energy >= threshold)
         and np.all(energy <= upper), "NATIVE_PHOTO_SUPPORT_REQUIRED")
    x = energy / e0 - y0
    y = np.hypot(x, y1)
    value = 1e-18 * sigma0 * ((x - 1) ** 2 + yw ** 2) * y ** (power / 2 - 5.5) \
        * (1 + np.sqrt(y / ya)) ** (-power)
    need(np.all(np.isfinite(value)) and np.all(value > 0), "POSITIVE_PHOTO_CROSS_SECTION_REQUIRED")
    return value


def constants_record():
    values = dict(CONSTANTS)
    values["hbar_J_s"] = values["h_J_s"] / (2 * math.pi)
    return {"edition": "CODATA2022 via official SciPy1.17.0 recipe",
            "scipy_source_commit": "8c75ae75176236f233824e9a0483c26a69e6dfec",
            "values": values, "binary64_hex": {k: v.hex() for k, v in values.items()},
            "hbar_recipe": "h/(2*math.pi)", "quantum_constant": 0.,
            "old_RR_2018_mass_reused": False,
            "historical_full_operator_bitwise_recovery": False}
