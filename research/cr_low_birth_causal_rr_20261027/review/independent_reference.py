#!/usr/bin/env python3
"""Independent finite-ramp reference for the frozen low-birth RR model.

Author: /root/theory_review (theory/reference author; not production author).
This source was prepared without executing scientific work. Run only through
the unit's admitted bounded runner. No production module is imported.

Independent numerical representation: one sparse augmented exponential in
dimensionless time, with active number and its integral as separate blocks.
Original E/A atoms are consumed directly; no old quadrature or solver replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import traceback


UNIT = "CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1"
CONTRACT_SHA256 = "0766fa66e643de2b50d797fa94838cb989e69c8d3aaa47fe8c31673764757210"
SOURCE_SHA256 = "8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf"
SOURCE_BYTES = 4394309
SOURCE_TAG = "direct_0p1_10"
STATE = "PHYS02_T100K_nH140m3_YHe0.248_xHII0.01_xHeII0.01_xHeIII0_FIXED"
FRAME = "prescribed_gas_rest_frame_scalar"
MAPPING = "CONDITIONAL_ELEMENTAL_H_TO_H1_HE_TO_HE4"
FAMILY = "cr-source-family-13b884c8b34cc89c60e5a70842120ee2c8f136645de3592cb87fac2eefa636a8"
PARTITION = "birth-partition-0a332c1184f24587f59e32404c7c1673c5f84fedc0e3d93ffe2b376bc2c75204"
T = 1.0e10
E_CUT = 0.1
ME = 9.1093837139e-31
EPS0 = 8.8541878188e-12
EV_J = 1.602176634e-19
CHARGE = 1.602176634e-19
PLANCK = 6.62607015e-34
C_LIGHT = 299792458.0
HBAR = PLANCK / (2.0 * math.pi)
REFERENCE_RTOL = 1.0e-9
LEDGER_RTOL = 1.0e-11
# This is an independently implemented represented-law comparison, separated
# from the R1 rare-channel reference gate. The rule is declared before execution.
COEFFICIENT_RTOL = 1.0e-11
FIT_LITERALS = {
    "H": ["13.60", "50000", ".4298", "54750", "32.88", "2.963", "0", "0", "0"],
    "He": ["24.59", "50000", "13.61", "949.2", "1.469", "3.188", "2.039", ".4434", "2.136"],
}
I_EV = {"H": 13.60, "He": 24.59}
MILNE_D = {"H": 1.0, "He": 4.0}
UNIT_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = UNIT_DIR.parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def write_json_new(path: Path, data: object) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def authorize(out: Path) -> dict:
    """Independent runner guard; importing production guard is prohibited."""
    require(os.environ.get("CR_BOUNDED_UNIT") == UNIT, "unit runner environment absent")
    require(os.environ.get("CR_BOUNDED_OUTDIR") == str(out), "runner output identity mismatch")
    require(out.is_dir(), "runner-owned output directory absent")
    reservation = json.loads((out / "RESERVATION.json").read_text())
    require(reservation.get("unit") == UNIT, "reservation unit mismatch")
    attempt = os.environ.get("CR_BOUNDED_ATTEMPT_ID")
    require(bool(attempt) and reservation.get("attempt_id") == attempt,
            "reservation attempt identity mismatch")
    require(sha256(UNIT_DIR / "CONTRACT.md") == CONTRACT_SHA256,
            "frozen contract digest mismatch")
    for name in ("RESULT.json", "ARRAYS.npz", "FAILURE.json"):
        require(not (out / name).exists(), "create-only output already exists: " + name)
    return reservation


def read_source(path: Path, np):
    raw = path.read_bytes()
    require(len(raw) == SOURCE_BYTES, "source byte count mismatch")
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "source SHA256 mismatch")
    records = json.loads(raw)
    require(isinstance(records, list), "source root must be the retained list")
    chosen = [record for record in records if record.get("tag") == SOURCE_TAG]
    require(len(chosen) == 1, "low native birth tag is not unique")
    source = chosen[0]["source"]
    require(source.get("schema") == "CR_PROPER_SOURCE_V1", "source schema mismatch")
    require(source.get("representation") == "atomic_bins", "atomic source representation required")
    require(source["particle"] == {
        "kind": "electron", "isotope": "e-", "state": "PHYS02_direct_secondary_birth",
        "energy_coordinate": "kinetic_eV",
    }, "source particle/state mismatch")
    medium = source["medium"]
    require(medium.get("state_id") == STATE and medium.get("frame") == FRAME,
            "source state/frame mismatch")
    require(medium.get("temperature_K") == 100.0, "source bath mismatch")
    require(medium.get("proper_volume_mode") == "fixed" and medium.get("proper_volume_m3") is None,
            "proper-volume contract mismatch")
    require(source.get("isotope_mapping") == MAPPING, "source isotope mapping mismatch")
    require(source.get("support_eV") == [E_CUT, 10.0], "native source support mismatch")
    event = source["source_event"]
    require(event.get("family_id") == FAMILY and event.get("partition_id") == PARTITION,
            "source event identity mismatch")
    require(event.get("native_birth_support_eV") == [E_CUT, 10.0]
            and event.get("clock_origin_s") == 0.0, "birth partition/clock mismatch")
    require(source.get("history_boundary") == "unknown_outside_recorded_segments",
            "outside-history status mismatch")
    norm = source["normalization"]
    require(norm.get("clock_measure") == "proper_s" and norm.get("volume_measure") == "proper_m3",
            "proper clock/volume units mismatch")
    require(norm.get("d_native_clock_d_proper_s") == 1.0
            and norm.get("d_native_volume_d_proper_m3") == 1.0,
            "source already proper; an additional Jacobian is forbidden")
    require(norm.get("target_density_mode") == "already_included"
            and norm.get("target_density_m3") is None and norm.get("applied_tokens") == [],
            "source target-factor ownership mismatch")
    history = source["history"]
    require(len(history) == 1, "exact single retained history segment required")
    segment = history[0]
    require(segment.get("start_s") == 0.0 and segment.get("stop_s") == T,
            "finite proper-time history mismatch")
    bins = segment["bins"]
    require(len(bins) == 3201, "source must contain 3200 active plus direct-cutoff atom")
    energies, coefficients = [], []
    for j, atom in enumerate(bins[:-1]):
        require(type(atom.get("stored_node_index")) is int and atom["stored_node_index"] == j,
                "saved active node order mismatch")
        coefficient = atom["number_coefficients"]
        require(len(coefficient) == 2 and coefficient[0] == 0.0, "source is not the admitted ramp")
        energy, slope = float(atom["energy_eV"]), float(coefficient[1])
        require(math.isfinite(energy) and E_CUT < energy <= 10.0, "active energy outside support")
        require(math.isfinite(slope) and slope >= 0.0, "negative/nonfinite source atom")
        energies.append(energy)
        coefficients.append(slope)
    cut = bins[-1]
    require(cut.get("stored_node_index") == "cutoff_boundary"
            and cut.get("energy_eV") == E_CUT, "direct-cutoff atom identity mismatch")
    require(len(cut["number_coefficients"]) == 2 and cut["number_coefficients"][0] == 0.0,
            "direct-cutoff source is not the admitted ramp")
    acut = float(cut["number_coefficients"][1])
    require(math.isfinite(acut) and acut >= 0.0, "invalid direct-cutoff coefficient")
    energy = np.asarray(energies, dtype=np.float64)
    source_a = np.asarray(coefficients, dtype=np.float64)
    require(bool(np.all(np.diff(energy) > 0.0)) and energy[-1] == 10.0,
            "source energies are not strictly ordered")
    source_n = math.fsum(coefficients + [acut])
    source_e = math.fsum([e * a for e, a in zip(energies, coefficients)] + [E_CUT * acut])
    for name, actual in (("number_coefficients", source_n), ("energy_coefficients_eV", source_e)):
        represented = segment[name]
        require(len(represented) == 2 and represented[0] == 0.0,
                "saved source moments are not the admitted ramp")
        expected = float(represented[1])
        require(expected > 0.0 and abs(actual - expected) / expected <= LEDGER_RTOL,
                "source atom sum disagrees with saved " + name)
    provenance = {
        "path": str(path), "sha256": SOURCE_SHA256, "bytes": SOURCE_BYTES,
        "tag": SOURCE_TAG, "source": source["source"], "state_id": STATE, "frame": FRAME,
        "isotope_mapping": MAPPING, "family_id": FAMILY, "partition_id": PARTITION,
        "native_birth_support_eV": [E_CUT, 10.0], "history_s": [0.0, T],
        "history_outside_record": None, "proper_volume_m3": None,
        "direct_cutoff_A_m3_s2": acut, "A_number_sum_m3_s2": source_n,
        "A_energy_sum_eV_m3_s2": source_e,
        "source_conversion_factors_applied_by_reference": [],
    }
    return energy, source_a, acut, provenance


def independent_coefficients(energy, np):
    """SI/log-form implementation, separate from production source/functions."""
    n_h = 140.0
    n_he = n_h * 0.248 / (4.0 * (1.0 - 0.248))
    n_e = 0.01 * (n_h + n_he)
    n_b = n_h + 4.0 * n_he
    targets = {"H": 0.01 * n_h, "He": 0.01 * n_he}
    velocity = np.sqrt(2.0 * EV_J * energy / ME)
    omega_p = math.sqrt(n_e * CHARGE * CHARGE / (EPS0 * ME))
    kappa = CHARGE * CHARGE / (4.0 * math.pi * EPS0)
    # Logarithms of products are evaluated as sums here. This is algebraically
    # the same frozen min(classical, quantum) prescription, with distinct FP order.
    log_classical = (np.log(velocity) + np.log(energy) + math.log(EV_J)
                     - math.log(kappa) - math.log(omega_p))
    log_quantum = (math.log(2.0) + np.log(energy) + math.log(EV_J)
                   - math.log(HBAR) - math.log(omega_p))
    coulomb_log = np.minimum(log_classical, log_quantum)
    stopping = ((4.0 * math.pi * kappa * kappa * n_e) / (ME * EV_J)) * coulomb_log / velocity
    gap = np.diff(np.concatenate((np.asarray([E_CUT]), energy)))
    drift = stopping / gap
    hazards = {}
    for channel in ("H", "He"):
        ionization, upper, e0, sigma0, ya, exponent, yw, y0, y1 = map(float, FIT_LITERALS[channel])
        photon_energy = energy + ionization
        require(bool(np.all(photon_energy >= ionization)) and bool(np.all(photon_energy <= upper)),
                "native Verner photon support exceeded")
        reduced = photon_energy / e0 - y0
        y = np.hypot(reduced, y1)
        log_sigma_pi_m2 = (math.log(sigma0 * 1.0e-22)
                           + np.log((reduced - 1.0) ** 2 + yw * yw)
                           + (exponent / 2.0 - 5.5) * np.log(y)
                           - exponent * np.log1p(np.sqrt(y / ya)))
        # SI Milne cross section: the one eV-to-J factor cancels the rest-energy
        # denominator. Ion target density is introduced exactly once here.
        sigma_rr_m2 = (np.exp(log_sigma_pi_m2) * photon_energy ** 2 * EV_J
                       / (MILNE_D[channel] * ME * C_LIGHT ** 2 * energy))
        hazards[channel] = targets[channel] * velocity * sigma_rr_m2
    for label, values in (("stopping", stopping), ("drift", drift),
                          ("lambda_H", hazards["H"]), ("lambda_He", hazards["He"])):
        require(bool(np.all(np.isfinite(values))) and bool(np.all(values > 0.0)),
                "invalid independent coefficient: " + label)
    inventory = {
        "temperature_K": 100.0, "n_H_m3": n_h, "n_He_m3": n_he,
        "n_e_thermal_m3": n_e, "n_b_m3": n_b,
        "n_HII_m3": targets["H"], "n_HeII_m3": targets["He"], "n_HeIII_m3": 0.0,
        "rational_semantics": {"n_He": "1085/94", "n_e": "2849/1880", "n_b": "8750/47"},
        "inventory_is_new_conditional_H1_He4_only": True,
        "prior_PR109_nb": None, "source_parent_ion_chemistry": None,
    }
    return stopping, drift, hazards, inventory


def solve_independent(source_a, drift, hazards, np):
    import scipy.sparse as sparse
    from scipy.sparse.linalg import expm_multiply

    size = len(source_a)
    source_sum = math.fsum(map(float, source_a))
    require(source_sum > 0.0, "active source must be positive")
    departure = drift + hazards["H"] + hazards["He"]
    active = sparse.diags((-T * departure, T * drift[1:]), (0, 1),
                          shape=(size, size), format="csr")
    active_coo = active.tocoo()
    # State order [normalized active n, normalized active O, absolute u, 1].
    # d(n_norm)/du = T L n_norm + u A/sum(A); d(O_norm)/du=n_norm.
    rows = np.concatenate((active_coo.row, np.arange(size, 2 * size),
                           np.arange(size), np.asarray([2 * size])))
    cols = np.concatenate((active_coo.col, np.arange(size),
                           np.full(size, 2 * size), np.asarray([2 * size + 1])))
    data = np.concatenate((active_coo.data, np.ones(size), source_a / source_sum,
                           np.asarray([1.0])))
    augmented = sparse.coo_matrix((data, (rows, cols)), shape=(2 * size + 2, 2 * size + 2)).tocsr()
    initial = np.zeros(2 * size + 2)
    initial[-1] = 1.0
    trace = -T * math.fsum(map(float, departure))
    state = expm_multiply(augmented, initial, start=0.0, stop=1.0, num=5,
                          endpoint=True, traceA=trace)
    require(bool(np.all(np.isfinite(state))), "nonfinite sparse exponential state")
    require(bool(np.all(state[0, :2 * size] == 0.0)), "initial cohort not zero")
    active_n = state[1:, :size] * (source_sum * T ** 2)
    occupancy = state[1:, size:2 * size] * (source_sum * T ** 3)
    occupancy_bins = np.diff(np.concatenate((np.zeros((1, size)), occupancy), axis=0), axis=0)
    require(bool(np.all(active_n >= 0.0)) and bool(np.all(occupancy >= 0.0))
            and bool(np.all(occupancy_bins >= 0.0)), "negative reference state/occupancy; no clipping")
    return active_n, occupancy, occupancy_bins, {
        "method": "independent_scipy_sparse_augmented_expm_multiply",
        "dimension": int(augmented.shape[0]), "nnz": int(augmented.nnz),
        "dimensionless_time": "u=t/T", "source_normalization": "A/sum_active(A)",
        "n_output_rescaling": "sum_active(A)*T^2",
        "O_output_rescaling": "sum_active(A)*T^3",
        "trace_argument": trace, "num_including_initial": 5,
        "production_imports": [], "old_source_or_transport_replays": 0,
        "ordinary_floating_point_not_outward_certificate": True,
        "clock_max_abs_error": float(np.max(np.abs(state[:, -2] - np.linspace(0.0, 1.0, 5)))),
        "constant_max_abs_error": float(np.max(np.abs(state[:, -1] - 1.0))),
    }


def total(values) -> float:
    return math.fsum(map(float, values))


def relative_error(actual: float, expected: float) -> float:
    require(math.isfinite(actual) and math.isfinite(expected), "nonfinite comparison")
    if expected == 0.0:
        return 0.0 if actual == 0.0 else math.inf
    return abs(actual - expected) / abs(expected)


def add_scalar_check(checks: list, label: str, actual: float, expected: float,
                     tolerance: float) -> None:
    error = relative_error(float(actual), float(expected))
    checks.append({"check": label, "actual": float(actual), "expected": float(expected),
                   "relative_error": error if math.isfinite(error) else None,
                   "tolerance": tolerance, "exact_zero_expected": expected == 0.0,
                   "pass": error <= tolerance})


def summarize(energy, source_a, acut, stopping, drift, hazards, inventory,
              active_n, occupancy, occupancy_bins, np):
    times = np.asarray([T / 4.0, T / 2.0, 3.0 * T / 4.0, T])
    source_n = math.fsum([*map(float, source_a), acut])
    source_e = math.fsum([*map(float, energy * source_a), E_CUT * acut])
    checks = []
    prefixes, bins = [], []
    for is_bin, rows in ((False, prefixes), (True, bins)):
        for index, stop in enumerate(times):
            start = float(times[index - 1]) if is_bin and index > 0 else 0.0
            occupation = occupancy_bins[index] if is_bin else occupancy[index]
            endpoint = active_n[index]
            active_delta = endpoint - (active_n[index - 1] if is_bin and index else 0.0)
            number_in = 0.5 * source_n * (float(stop) ** 2 - start ** 2)
            energy_in = 0.5 * source_e * (float(stop) ** 2 - start ** 2)
            direct_cut = 0.5 * acut * (float(stop) ** 2 - start ** 2)
            drift_cut = float(drift[0] * occupation[0])
            cutoff = direct_cut + drift_cut
            cutoff_energy = E_CUT * cutoff
            coulomb = total(stopping * occupation)
            channels = {}
            for channel in ("H", "He"):
                captures = hazards[channel] * occupation
                count = total(captures)
                kinetic = total(energy * captures)
                photon = total((energy + I_EV[channel]) * captures)
                channels[channel] = {
                    "capture_number_m3": count, "capture_kinetic_eV_m3": kinetic,
                    "retained_photon_number_m3": count, "retained_photon_energy_eV_m3": photon,
                    "binding_energy_change_eV_m3": -I_EV[channel] * count,
                    "endpoint_rate_m3_s": None if is_bin else total(hazards[channel] * endpoint),
                    "endpoint_kinetic_rate_eV_m3_s": None if is_bin else total(energy * hazards[channel] * endpoint),
                }
            ch, che = channels["H"], channels["He"]
            rr = [0.0] * 25
            rr[1], rr[2] = ch["capture_number_m3"] / inventory["n_b_m3"], -ch["capture_number_m3"] / inventory["n_b_m3"]
            rr[10], rr[11] = che["capture_number_m3"] / inventory["n_b_m3"], -che["capture_number_m3"] / inventory["n_b_m3"]
            rr[21] = -(ch["capture_number_m3"] + che["capture_number_m3"]) / inventory["n_b_m3"]
            rr[22] = -(ch["capture_kinetic_eV_m3"] + che["capture_kinetic_eV_m3"]) * EV_J / inventory["n_b_m3"]
            active_number, active_energy = total(active_delta), total(energy * active_delta)
            number_out = active_number + cutoff + ch["capture_number_m3"] + che["capture_number_m3"]
            kinetic_out = active_energy + coulomb + cutoff_energy + ch["capture_kinetic_eV_m3"] + che["capture_kinetic_eV_m3"]
            total_out = (active_energy + coulomb + cutoff_energy
                         + ch["retained_photon_energy_eV_m3"] + che["retained_photon_energy_eV_m3"]
                         + ch["binding_energy_change_eV_m3"] + che["binding_energy_change_eV_m3"])
            row = {
                "interval_s": [start, float(stop)], "injected_number_m3": number_in,
                "injected_energy_eV_m3": energy_in, "occupancy_total_m3_s": total(occupation),
                "cutoff_direct_number_m3": direct_cut, "cutoff_drift_number_m3": drift_cut,
                "cutoff_number_m3": cutoff, "cutoff_energy_eV_m3": cutoff_energy,
                "coulomb_energy_eV_m3": coulomb, "channels": channels, "rr_native25": rr,
                "full_source_native25": None, "physical_heating_completed": False,
                "count_closure_relative": abs(number_out - number_in) / number_in,
                "kinetic_energy_closure_relative": abs(kinetic_out - energy_in) / energy_in,
                "total_energy_closure_relative": abs(total_out - energy_in) / energy_in,
                "extensive_worldtube_totals": None,
            }
            if is_bin:
                row["active_number_change_m3"] = active_number
                row["active_energy_change_eV_m3"] = active_energy
            else:
                row["active_number_m3"] = active_number
                row["active_energy_eV_m3"] = active_energy
            name = ("bin" if is_bin else "prefix") + str(index + 1)
            for label, actual, expected in (("count", number_out, number_in),
                                             ("kinetic", kinetic_out, energy_in),
                                             ("total_energy", total_out, energy_in)):
                add_scalar_check(checks, "reference." + name + "." + label, actual, expected, LEDGER_RTOL)
            for channel in ("H", "He"):
                c = channels[channel]
                add_scalar_check(checks, "reference." + name + "." + channel + ".photon_identity",
                                 c["retained_photon_energy_eV_m3"],
                                 c["capture_kinetic_eV_m3"] + I_EV[channel] * c["capture_number_m3"], LEDGER_RTOL)
            # Charge-derived total-free change equals the nonthermal change;
            # reference scale is the RR event itself, never source injection.
            add_scalar_check(checks, "reference." + name + ".thermal_charge",
                             rr[2] + rr[11], rr[21], LEDGER_RTOL)
            rows.append(row)
    arrays = {
        "E_eV": energy, "A_m3_s2": source_a, "b_eV_s": stopping, "drift_s_inv": drift,
        "lambda_H_s_inv": hazards["H"], "lambda_He_s_inv": hazards["He"], "times_s": times,
        "n_prefix_m3": active_n, "O_prefix_m3_s": occupancy, "O_bins_m3_s": occupancy_bins,
    }
    for channel in ("H", "He"):
        arrays["capture_" + channel + "_prefix_m3"] = occupancy * hazards[channel]
        arrays["capture_" + channel + "_bins_m3"] = occupancy_bins * hazards[channel]
        arrays["photon_" + channel + "_energy_eV"] = energy + I_EV[channel]
        arrays["endpoint_" + channel + "_rate_m3_s"] = active_n * hazards[channel]
    return prefixes, bins, arrays, checks


def compare_primary(primary: Path, prefixes: list, bins: list, arrays: dict, checks: list, np):
    result_path, arrays_path = primary / "RESULT.json", primary / "ARRAYS.npz"
    observed = json.loads(result_path.read_text())
    require(observed.get("unit") == UNIT, "producer unit mismatch")
    array_diagnostics = {}
    exact = {"E_eV", "A_m3_s2", "times_s", "photon_H_energy_eV", "photon_He_energy_eV"}
    coefficients = {"b_eV_s", "drift_s_inv", "lambda_H_s_inv", "lambda_He_s_inv"}
    with np.load(arrays_path, allow_pickle=False) as loaded:
        for name, expected in arrays.items():
            require(name in loaded, "producer array absent: " + name)
            actual = loaded[name]
            require(actual.dtype == np.float64 and actual.shape == expected.shape,
                    "producer array type/shape mismatch: " + name)
            require(bool(np.all(np.isfinite(actual))), "nonfinite producer array: " + name)
            require(bool(np.all(actual >= 0.0)), "negative producer array: " + name)
            if name in exact:
                passed = bool(np.array_equal(actual, expected))
                checks.append({"check": "primary.array_identity." + name, "pass": passed})
                array_diagnostics[name] = {"bitwise_float_values_equal": passed}
                continue
            tolerance = COEFFICIENT_RTOL if name in coefficients else REFERENCE_RTOL
            a2 = actual.reshape((-1, actual.shape[-1]))
            e2 = expected.reshape((-1, expected.shape[-1]))
            diagnostics = []
            for row_index, (a, e) in enumerate(zip(a2, e2)):
                absdiff = np.abs(a - e)
                denom = total(np.abs(e))
                error = total(absdiff) / denom if denom else (0.0 if bool(np.all(a == e)) else math.inf)
                positive = e > 0.0
                component = float(np.max(absdiff[positive] / e[positive])) if bool(np.any(positive)) else 0.0
                zeros_equal = bool(np.all(a[~positive] == 0.0))
                checks.append({"check": "primary.array." + name + "." + str(row_index),
                               "relative_l1_error": error if math.isfinite(error) else None,
                               "tolerance": tolerance, "zero_components_equal": zeros_equal,
                               "pass": error <= tolerance and zeros_equal})
                diagnostics.append({"relative_l1_error": error if math.isfinite(error) else None,
                                    "maximum_positive_component_relative_error": component,
                                    "componentwise_max_is_diagnostic_only": True})
            array_diagnostics[name] = diagnostics
    scalars = ("injected_number_m3", "injected_energy_eV_m3", "occupancy_total_m3_s",
               "cutoff_direct_number_m3", "cutoff_drift_number_m3", "cutoff_number_m3",
               "cutoff_energy_eV_m3", "coulomb_energy_eV_m3")
    channel_fields = ("capture_number_m3", "capture_kinetic_eV_m3", "retained_photon_number_m3",
                      "retained_photon_energy_eV_m3", "binding_energy_change_eV_m3",
                      "endpoint_rate_m3_s", "endpoint_kinetic_rate_eV_m3_s")
    for group, expected_rows in (("prefixes", prefixes), ("observation_bins", bins)):
        actual_rows = observed[group]
        require(len(actual_rows) == 4, "producer must return exactly four " + group)
        for index, (actual, expected) in enumerate(zip(actual_rows, expected_rows)):
            label = "primary." + group + "." + str(index)
            require(actual.get("interval_s") == expected["interval_s"], "producer interval mismatch")
            require(actual.get("full_source_native25") is None and actual.get("physical_heating_completed") is False,
                    "producer promoted a forbidden physical gate")
            active_fields = (("active_number_m3", "active_energy_eV_m3") if group == "prefixes"
                             else ("active_number_change_m3", "active_energy_change_eV_m3"))
            for field in scalars + active_fields:
                add_scalar_check(checks, label + "." + field, actual[field], expected[field], REFERENCE_RTOL)
            for channel in ("H", "He"):
                for field in channel_fields:
                    expected_value = expected["channels"][channel][field]
                    actual_value = actual["channels"][channel].get(field)
                    if expected_value is None:
                        require(actual_value is None, "bin endpoint rate must be null")
                    else:
                        add_scalar_check(checks, label + "." + channel + "." + field,
                                         actual_value, expected_value, REFERENCE_RTOL)
            actual_rr = actual["rr_native25"]
            require(len(actual_rr) == 25, "producer RR native25 length mismatch")
            for j, value in enumerate(expected["rr_native25"]):
                add_scalar_check(checks, label + ".rr_native25." + str(j), actual_rr[j], value, REFERENCE_RTOL)
            # Independently recompute the producer's reported physical ledgers.
            channels = actual["channels"]
            active_n = float(actual[active_fields[0]])
            active_e = float(actual[active_fields[1]])
            number_out = active_n + float(actual["cutoff_number_m3"]) + math.fsum(float(channels[c]["capture_number_m3"]) for c in ("H", "He"))
            kinetic_out = active_e + float(actual["coulomb_energy_eV_m3"]) + float(actual["cutoff_energy_eV_m3"]) + math.fsum(float(channels[c]["capture_kinetic_eV_m3"]) for c in ("H", "He"))
            total_out = active_e + float(actual["coulomb_energy_eV_m3"]) + float(actual["cutoff_energy_eV_m3"]) + math.fsum(float(channels[c]["retained_photon_energy_eV_m3"]) + float(channels[c]["binding_energy_change_eV_m3"]) for c in ("H", "He"))
            for metric, value, denominator in (("count", number_out, actual["injected_number_m3"]),
                                                ("kinetic", kinetic_out, actual["injected_energy_eV_m3"]),
                                                ("total_energy", total_out, actual["injected_energy_eV_m3"])):
                add_scalar_check(checks, label + ".independent_ledger." + metric, value, denominator, LEDGER_RTOL)
            for channel in ("H", "He"):
                c = channels[channel]
                add_scalar_check(checks, label + "." + channel + ".independent_photon_identity",
                                 c["retained_photon_energy_eV_m3"],
                                 c["capture_kinetic_eV_m3"] + I_EV[channel] * c["capture_number_m3"], LEDGER_RTOL)
            add_scalar_check(checks, label + ".independent_thermal_charge",
                             actual_rr[2] + actual_rr[11], actual_rr[21], LEDGER_RTOL)
    return {"result_sha256": sha256(result_path), "arrays_sha256": sha256(arrays_path),
            "primary_path": str(primary), "array_diagnostics": array_diagnostics}


def run(args, out: Path, reservation: dict) -> int:
    import numpy as np
    import scipy

    source_path = (Path(args.source_records).resolve() if args.source_records else
                   REPO_DIR / "research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json")
    bindings_path = UNIT_DIR / "intake/RR_SOURCE_BINDINGS.json"
    bindings = json.loads(bindings_path.read_text())
    for channel, retained in zip(("H", "He"), bindings["channels"]):
        require(retained["fit_decimal_literals"] == FIT_LITERALS[channel]
                and retained["milne_d"] == MILNE_D[channel], "retained source fit/Milne identity mismatch")
    energy, source_a, acut, provenance = read_source(source_path, np)
    stopping, drift, hazards, inventory = independent_coefficients(energy, np)
    active_n, occupancy, occupancy_bins, solver = solve_independent(source_a, drift, hazards, np)
    prefixes, bins, arrays, checks = summarize(energy, source_a, acut, stopping, drift, hazards,
                                              inventory, active_n, occupancy, occupancy_bins, np)
    comparison = compare_primary(Path(args.primary).resolve(), prefixes, bins, arrays, checks, np)
    passed = all(check["pass"] for check in checks)
    arrays_path = out / "ARRAYS.npz"
    with arrays_path.open("xb") as handle:
        np.savez_compressed(handle, **arrays)
    result = {
        "schema": "CR_LOW_BIRTH_RR_INDEPENDENT_REFERENCE_V1", "unit": UNIT,
        "status": "PASS" if passed else "FAILED_COMPARISON", "attempt_id": reservation["attempt_id"],
        "author_role": "theory_and_independent_reference_author_not_production_author",
        "code_sha256": sha256(Path(__file__).resolve()), "contract_sha256": CONTRACT_SHA256,
        "source_bindings_sha256": sha256(bindings_path), "input": provenance,
        "constants": {"CODATA_edition": 2022, "source_revision": "SciPy_v1.17.0",
                      "me_kg": ME, "eps0_F_m": EPS0, "e_C": CHARGE, "eV_J": EV_J,
                      "h_J_s": PLANCK, "hbar_J_s": HBAR, "c_m_s": C_LIGHT},
        "inventory": inventory, "solver": solver, "prefixes": prefixes, "observation_bins": bins,
        "comparison": comparison,
        "numerical_acceptance": {"pass": passed, "check_count": len(checks),
                                 "passed_count": sum(check["pass"] for check in checks),
                                 "reference_relative_tolerance": REFERENCE_RTOL,
                                 "ledger_relative_tolerance": LEDGER_RTOL,
                                 "coefficient_relative_tolerance": COEFFICIENT_RTOL,
                                 "checks": checks},
        "artifacts": {"ARRAYS.npz": {"sha256": sha256(arrays_path), "bytes": arrays_path.stat().st_size}},
        "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                    "scipy": scipy.__version__, "cpu_authority": "bounded_runner_immutable_receipt"},
        "physical_heating_completed": False, "full_source_native25": None,
        "global_physical_completion": None, "continuous_energy_error_bound": None,
        "source_parent_ion_chemistry": None, "proper_worldtube_totals": None,
        "old_science_replays": 0, "cumulative_prefixes_are_nonadditive": True,
    }
    write_json_new(out / "RESULT.json", result)
    print(json.dumps({"status": result["status"], "checks": len(checks),
                      "passed": result["numerical_acceptance"]["passed_count"],
                      "result": str(out / "RESULT.json")}, allow_nan=False))
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--primary", required=True)
    parser.add_argument("--source-records")
    args = parser.parse_args()
    out = Path(args.out).resolve()
    reservation = authorize(out)
    try:
        return run(args, out, reservation)
    except Exception as exc:
        failure = {"schema": "CR_LOW_BIRTH_RR_INDEPENDENT_FAILURE_V1", "unit": UNIT,
                   "status": "FAILED", "attempt_id": reservation["attempt_id"],
                   "exception_type": type(exc).__name__, "message": str(exc),
                   "traceback": traceback.format_exc(), "automatic_retry": False,
                   "old_science_replays": 0, "code_sha256": sha256(Path(__file__).resolve())}
        if not (out / "FAILURE.json").exists():
            write_json_new(out / "FAILURE.json", failure)
        print(json.dumps({"status": "FAILED", "type": type(exc).__name__, "message": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
