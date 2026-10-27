#!/usr/bin/env python3
"""Bounded parent-event attribution and partial finite-event native25 consumer.

This module never imports an old source, Cascade, RR operator, or consumer.
Only the new three-basis attribution is evaluated. Saved response quantities
and discrete photon atoms remain identity-bound inputs. An affine He intercept
is not an observed exclusive branch. Missing physical partner/work inputs stay
null. Authoritative increments are independent of rounded endpoint diagnostics.
"""
import argparse
import copy
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import wraps
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys


UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
UNIT_ID = "CR_PHYS02_PARENT_EVENT_NATIVE25_V1"
PRECISION = 80
CONTRACT_SHA = "01cc2d2835e3ad61c49cd0b68b8c413ebd7e0b8fb5228877804159c4e3f71162"
MANIFEST_SHA = "2273f08ac1716d233097d17c73818d39a9337da34712290a4b4171430d24f9b3"
SOURCE_SHA = "8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf"
MOMENT_SHA = "4e210fb042c8b4d92fd8577b30af78686500de8d7b7ea89be5baeea6564ee1f8"
COVERAGE_SHA = "36ea403320bcc711c4955de55e2a7e9f65c2deaf851a882bd9581585fb857624"
RR_RESULT_SHA = "ae8452f25958c47349d313926ef14e7ab7d78691ba6bb3b8395dc399aa49b0ce"
RR_ARRAYS_SHA = "2c3624e4ca6d087436f79360497e75b0c84fb2c8ea6b83bb855a9a0cd0005c1d"
PAYLOAD_SHA = "7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc"
SOURCE_REVISION = "ec463db0c7e5c7fb5070796071c926caa4db6445"
RETAINED_REVISION = "4ca5a90de79c8fb82a25fd9e83615bec0dfa870b"
FAMILY = "cr-source-family-13b884c8b34cc89c60e5a70842120ee2c8f136645de3592cb87fac2eefa636a8"
PARTITION = "birth-partition-0a332c1184f24587f59e32404c7c1673c5f84fedc0e3d93ffe2b376bc2c75204"
SOURCE_STATE = "PHYS02_T100K_nH140m3_YHe0.248_xHII0.01_xHeII0.01_xHeIII0_FIXED"
STATE = "CR_LOW_BIRTH_100K_CONDITIONAL_H1_HE4_FIXED_INVENTORY_V1"
FRAME = "prescribed_gas_rest_frame_scalar"
ISOTOPE = "CONDITIONAL_ELEMENTAL_H_TO_H1_HE_TO_HE4"
TAG = "direct_0p1_10"
TIMES = (2500000000., 5000000000., 7500000000., 10000000000.)
RECOVERY = ((0., .1), (3., 10.), (100., 1000.))
HOLDOUT = ((.1, 1.), (1., 3.), (10., 100.))
THETA_ORDER = ("theta_H", "theta_He1", "theta_He2")
SPECIES = ("n", "H1I", "H1II", "DI", "DII", "TI", "TII", "He3I", "He3II",
           "He3III", "He4I", "He4II", "He4III", "Li6I", "Li6II", "Li6III",
           "Li6IV", "Li7I", "Li7II", "Li7III", "Li7IV")
CHARGES = (0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3)
MASSES = (1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 6, 6, 6, 6, 7, 7, 7, 7)
NATIVE_BASIS_SOURCE = {
    "repository": "cosmosapjw-quantum/rei_bianchi",
    "revision": "d91de6299e614520949c5873a9378000ceb1f85c",
    "path": "research/rei_expanded_event_consumer/cr_integrated_return_20261027/vendor/native_identity/atomic_model.json",
    "git_blob": "73285c1585f8edca92487effe95e68448f3163b8",
    "sha256": "9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614",
    "adoption": "reviewed static species order only; no foreign inventory or rates",
}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def high_precision(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        with localcontext() as context:
            context.prec = PRECISION
            return function(*args, **kwargs)
    return wrapped


def D(value):
    """An existing float is lifted exactly, never via its short decimal text."""
    if isinstance(value, Decimal):
        result = value
    elif type(value) is float:
        result = Decimal.from_float(value)
    elif isinstance(value, Fraction):
        result = Decimal(value.numerator) / Decimal(value.denominator)
    elif isinstance(value, str) and "/" in value:
        numerator, denominator = value.split("/")
        result = Decimal(numerator) / Decimal(denominator)
    else:
        require(type(value) in (str, int), "FINITE_SCALAR_REQUIRED")
        result = Decimal(value)
    require(result.is_finite(), "NONFINITE_SCALAR_REFUSED")
    return result


def dsum(values):
    return sum(values, Decimal(0))


def to_json(value):
    if isinstance(value, Decimal):
        require(value.is_finite(), "NONFINITE_OUTPUT_REFUSED")
        return str(value)
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): to_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json(item) for item in value]
    return value


def write_json_new(path, value):
    data = (json.dumps(to_json(value), indent=2, allow_nan=False) + "\n").encode()
    with Path(path).open("xb") as stream:
        stream.write(data)
    return file_identity(path)


def file_identity(path, display=None):
    path = Path(path)
    data = path.read_bytes()
    return {"path": str(path if display is None else display), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def array_identity(array):
    return {"shape": list(array.shape), "dtype": array.dtype.str, "order": "C",
            "bytes": array.nbytes, "sha256": hashlib.sha256(array.tobytes(order="C")).hexdigest()}


def own_scale_error(value, reference):
    value, reference = D(value), D(reference)
    if reference == 0:
        require(value == 0, "NONZERO_PREDICTION_ON_EXACT_ZERO_REFERENCE")
        return Decimal(0)
    return abs(value - reference) / abs(reference)


def incremental_error(terms):
    terms = [D(value) for value in terms]
    scale = dsum(abs(value) for value in terms)
    return Decimal(0) if scale == 0 else abs(dsum(terms)) / scale


def checked(name, condition, **details):
    return {"name": name, "pass": bool(condition), **details}


def admitted_output(value):
    out = Path(value).resolve()
    require(UNIT.name == "cr_parent_event_native25_20261028" and UNIT.parent.name == "research",
            "EXACT_NEW_UNIT_INSTALLATION_REQUIRED")
    require(os.environ.get("CR_BOUNDED_UNIT") == UNIT_ID, "BOUNDED_NEW_UNIT_REQUIRED")
    require(os.environ.get("CR_BOUNDED_OUTDIR") == str(out), "OWNED_OUTPUT_ENV_MISMATCH")
    require(out.parent == UNIT / "runs" and out.is_dir(), "RUNNER_CREATED_OUTPUT_REQUIRED")
    reservation = json.loads((out / "RESERVATION.json").read_bytes())
    require(reservation.get("unit") == UNIT_ID and reservation.get("run_id") == out.name
            and reservation.get("attempt_id") == os.environ.get("CR_BOUNDED_ATTEMPT_ID"),
            "ACTUAL_RESERVATION_IDENTITY_REQUIRED")
    require(reservation.get("native_threads") == 1
            and reservation.get("selected_worker_memory_limit_bytes") == 268435456,
            "FROZEN_THREAD_AND_SELECTED_MEMORY_REQUIRED")
    return out


def load_retained_inputs():
    """Only byte checks and saved data reads; no old scientific imports."""
    contract_raw = (UNIT / "CONTRACT.json").read_bytes()
    require(hashlib.sha256(contract_raw).hexdigest() == CONTRACT_SHA, "R1_CONTRACT_CHANGED")
    manifest_raw = (UNIT / "inputs/INPUT_MANIFEST.json").read_bytes()
    require(hashlib.sha256(manifest_raw).hexdigest() == MANIFEST_SHA, "INPUT_MANIFEST_CHANGED")
    manifest = json.loads(manifest_raw)
    require(len(manifest["files"]) == 17, "EXACT_17_INPUT_PINS_REQUIRED")
    data, identities, seen = {}, {}, set()
    json_needed = {SOURCE_SHA, MOMENT_SHA, COVERAGE_SHA, RR_RESULT_SHA}
    for row in manifest["files"]:
        relative = Path(row["path"])
        require(not relative.is_absolute() and ".." not in relative.parts,
                "REPO_LOCAL_PINNED_INPUT_REQUIRED")
        path = REPO / relative
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(REPO),
                "REGULAR_PINNED_INPUT_REQUIRED")
        require(path.resolve() not in seen, "DUPLICATE_PINNED_INPUT")
        seen.add(path.resolve())
        raw = path.read_bytes()
        require(len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"],
                "SOURCE_BYTE_PIN_MISMATCH:" + row["path"])
        identities[row["sha256"]] = dict(row)
        if row["sha256"] in json_needed:
            data[row["sha256"]] = json.loads(raw)
        if row["sha256"] == MOMENT_SHA:
            data["moment_lexemes"] = json.loads(raw, parse_float=str)
    require(json_needed <= set(data) and RR_ARRAYS_SHA in identities,
            "REQUIRED_RETAINED_SOURCE_OR_RESPONSE_MISSING")
    source_rows = [row for row in data[SOURCE_SHA] if row["tag"] == TAG]
    require(len(source_rows) == 1, "EXACT_NATIVE_BIRTH_TAG_REQUIRED")
    source = source_rows[0]["source"]
    saved = data[RR_RESULT_SHA]
    validate_actual_source(source, saved)
    endpoint = data[COVERAGE_SHA]["coverage"]["minimum_sampled_proton_ejection_endpoint_eV"]
    require(type(endpoint) is float and math.isfinite(endpoint)
            and endpoint == 2154.927725029828 and endpoint > 1000.,
            "ACTUAL_COMMON_SOURCE_ENDPOINT_MUST_COVER_IDENTIFICATION_BANDS")
    identity = {
        "source_record": identities[SOURCE_SHA], "moment_source": identities[MOMENT_SHA],
        "coverage_source": identities[COVERAGE_SHA], "saved_response": identities[RR_RESULT_SHA],
        "saved_response_arrays": identities[RR_ARRAYS_SHA],
        "contract": {"path": str((UNIT / "CONTRACT.json").relative_to(REPO)), "sha256": CONTRACT_SHA},
        "input_manifest_sha256": MANIFEST_SHA, "all_input_pins": manifest["files"],
        "family_id": FAMILY, "partition_id": PARTITION,
        "retained_revision": RETAINED_REVISION, "source_revision": SOURCE_REVISION,
        "source_payload_sha256": PAYLOAD_SHA, "retained_revision_is_first_generating_commit": False,
        "native_basis_static_source": NATIVE_BASIS_SOURCE,
        "common_endpoint_eV_as_saved": endpoint,
    }
    return {"source": source, "saved": saved, "identity": identity,
            "moments": data[MOMENT_SHA]["details"]["direct_electron_source_bands"],
            "moment_lexemes": data["moment_lexemes"]["details"]["direct_electron_source_bands"]}


def validate_actual_source(source, saved):
    require(source.get("schema") == "CR_PROPER_SOURCE_V1", "SOURCE_SCHEMA_MISMATCH")
    require(source["source"]["revision"] == SOURCE_REVISION
            and source["source"]["payload_sha256"] == PAYLOAD_SHA
            and source["source"]["evidence_kind"] == "stored_physical", "SOURCE_REVISION_OR_PAYLOAD_MISMATCH")
    require(source["particle"] == {"kind": "electron", "isotope": "e-",
                "state": "PHYS02_direct_secondary_birth", "energy_coordinate": "kinetic_eV"},
            "SOURCE_PARTICLE_OR_ENERGY_COORDINATE_MISMATCH")
    require(source["medium"] == {"state_id": SOURCE_STATE, "frame": FRAME, "temperature_K": 100.,
                                  "proper_volume_mode": "fixed", "proper_volume_m3": None},
            "SOURCE_STATE_FRAME_OR_VOLUME_MISMATCH")
    require(source["isotope_mapping"] == ISOTOPE and source["support_eV"] == [.1, 10.],
            "SOURCE_ISOTOPE_OR_SUPPORT_MISMATCH")
    event = source["source_event"]
    require(event["family_id"] == FAMILY and event["partition_id"] == PARTITION
            and event["native_birth_support_eV"] == [.1, 10.]
            and event["clock_origin_s"] == 0., "PHYSICAL_SOURCE_FAMILY_OR_BIRTH_PARTITION_MISMATCH")
    require(source["normalization"] == {
        "clock_measure": "proper_s", "volume_measure": "proper_m3",
        "d_native_clock_d_proper_s": 1., "d_native_volume_d_proper_m3": 1.,
        "target_density_mode": "already_included", "target_density_m3": None, "applied_tokens": []},
        "ONCE_ONLY_SOURCE_NORMALIZATION_MISMATCH")
    require(source["representation"] == "atomic_bins"
            and source["history_boundary"] == "unknown_outside_recorded_segments"
            and len(source["history"]) == 1, "EXACT_FINITE_HISTORY_REQUIRED")
    history = source["history"][0]
    require(history["start_s"] == 0. and history["stop_s"] == TIMES[-1], "PROPER_HISTORY_WINDOW_MISMATCH")
    require(len(history["bins"]) == 3201, "EXACT_3200_ACTIVE_PLUS_GHOST_REQUIRED")
    previous = .1
    for index, atom in enumerate(history["bins"][:-1]):
        require(type(atom["stored_node_index"]) is int and atom["stored_node_index"] == index,
                "CANONICAL_STORED_GRID_INDEX_MISMATCH")
        energy, coefficients = atom["energy_eV"], atom["number_coefficients"]
        require(type(energy) is float and math.isfinite(energy) and previous < energy <= 10.,
                "CANONICAL_GRID_OR_BIRTH_SUPPORT_MISMATCH")
        require(len(coefficients) == 2 and coefficients[0] == 0.
                and type(coefficients[1]) is float and math.isfinite(coefficients[1])
                and coefficients[1] >= 0., "EXACT_NONNEGATIVE_AFFINE_SOURCE_REQUIRED")
        previous = energy
    require(previous == 10., "EXACT_UPPER_LOW_BIRTH_BOUNDARY_REQUIRED")
    ghost = history["bins"][-1]
    require(ghost["stored_node_index"] == "cutoff_boundary" and ghost["energy_eV"] == .1
            and ghost["number_coefficients"][0] == 0.
            and ghost["number_coefficients"][1] == saved["input"]["A_cutoff_m3_s2"],
            "ORIGINAL_DIRECT_CUTOFF_GHOST_REQUIRED")
    require(history["number_coefficients"] == [0., saved["input"]["stored_total_A_number_m3_s2"]]
            and history["energy_coefficients_eV"] == [0., saved["input"]["stored_total_A_energy_eV_m3_s2"]],
            "ORIGINAL_SAVED_TOTAL_SOURCE_IDENTITY_REQUIRED")
    require(saved["unit"] == "CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1"
            and saved["input"]["sha256"] == SOURCE_SHA and saved["input"]["selected_tag"] == TAG
            and saved["input"]["family_id"] == FAMILY and saved["input"]["partition_id"] == PARTITION,
            "SAVED_RESPONSE_SOURCE_IDENTITY_MISMATCH")
    context = saved["context"]
    require(context["donor_state_id"] == STATE == context["recipient_state_id"]
            and context["source_record_state_id"] == SOURCE_STATE
            and context["donor_frame"] == FRAME == context["recipient_frame"]
            and context["isotope_mapping"] == ISOTOPE, "SAVED_RESPONSE_SAME_STATE_BINDING_MISMATCH")
    require(saved["inventory"]["semantics"] == {"n_H": "140", "n_He": "1085/94",
                                                 "n_e": "2849/1880", "n_b": "8750/47"},
            "TOTAL_NUCLEI_INVENTORY_SEMANTICS_REQUIRED")
    require(saved["inventory"]["values"]["T_K"] == 100.
            and saved["inventory"]["values"]["n_HeIII_m3"] == 0.
            and context["component"] == "ground_spontaneous_only"
            and context["angular_scope"] == "scalar" and context["recoil"] == "zero",
            "SAVED_RESPONSE_SCOPE_MISMATCH")
    require(len(saved["prefixes"]) == 4 and len(saved["observation_bins"]) == 4,
            "EXACT_FOUR_PREFIX_FOUR_BIN_RESPONSE_REQUIRED")
    for index, time_s in enumerate(TIMES):
        start = 0. if index == 0 else TIMES[index-1]
        prefix, interval = saved["prefixes"][index], saved["observation_bins"][index]
        require(prefix["interval_s"] == [0., time_s]
                and prefix["role"] == "nonadditive_cumulative_prefix"
                and interval["interval_s"] == [start, time_s]
                and interval["role"] == "disjoint_observation_bin"
                and interval["includes_prior_injected_survivors"] is True,
                "SAVED_FINITE_BIN_OR_OLD_COHORT_SEMANTICS_CHANGED")


@high_precision
def positive_moments(I, a, b):
    I, a, b = D(I), D(a), D(b)
    require(I > 0 and 0 <= a <= b <= 1000, "MOMENT_DOMAIN_OUTSIDE_FIXED_COMMON_SUPPORT")
    if a == b:
        return (Decimal(0),) * 4
    K = I + a
    z = (b-a) / (I+b)
    F0, F1 = z * (1-z/2), z*z/2
    if z <= Decimal("0.5"):
        power, partial = z*z*z, Decimal(0)
        for order in range(3, 4097):
            partial += power/order
            remainder = power*z / ((order+1)*(1-z))
            if remainder <= Decimal("1e-70")*partial:
                F2 = partial
                break
            power *= z
        else:
            raise ArithmeticError("POSITIVE_MOMENT_SERIES_DID_NOT_MEET_INTERNAL_TARGET")
    else:
        F2 = ((I+b)/K).ln() - z-z*z/2
    N0 = I**3/K**2*F0
    N1 = I**2/K**2*(a*F0+K*F1)
    E0 = I*N1
    E1 = I**2/K**2*(a*a*F0+2*a*K*F1+K*K*F2)
    require(all(value >= 0 and value.is_finite() for value in (N0, N1, E0, E1)),
            "POSITIVE_MOMENT_FAILURE")
    return N0, N1, E0, E1


@high_precision
def basis_moments(a, b):
    h = positive_moments(D(float("13.605693122994")), D(a), D(b))
    he = positive_moments(D(float("24.59")), D(a), D(b))
    return [D(7)/3*h[0]+h[1], he[0], he[1]], [D(7)/3*h[2]+h[3], he[2], he[3]]


@high_precision
def inverse3(matrix):
    require(len(matrix) == 3 and all(len(row) == 3 for row in matrix), "THREE_BASIS_ONLY")
    augmented = [[D(value) for value in row] + [Decimal(int(i == j)) for j in range(3)]
                 for i, row in enumerate(matrix)]
    pivots = []
    for column in range(3):
        selected = max(range(column, 3), key=lambda row: abs(augmented[row][column]))
        pivot = augmented[selected][column]
        require(pivot != 0, "SINGULAR_THREE_BASIS_MATRIX")
        pivots.append({"column": column, "selected_row": selected, "pivot_decimal": str(pivot)})
        augmented[column], augmented[selected] = augmented[selected], augmented[column]
        augmented[column] = [value/pivot for value in augmented[column]]
        for row in range(3):
            if row != column:
                factor = augmented[row][column]
                augmented[row] = [a-factor*b for a, b in zip(augmented[row], augmented[column])]
    return [row[3:] for row in augmented], pivots


@high_precision
def recovery_metrics(B, inverse, z):
    norm = max(dsum(abs(value) for value in row) for row in B)
    inv_norm = max(dsum(abs(value) for value in row) for row in inverse)
    require(norm > 0 and inv_norm > 0, "INVALID_SCALED_MATRIX_NORM")
    rcond = 1/(norm*inv_norm)
    dz = [Decimal("2e-12")*dsum(abs(value) for value in row) for row in inverse]
    sensitivity = [bound/abs(value) if value != 0 else None for value, bound in zip(z, dz)]
    lower = [value-bound for value, bound in zip(z, dz)]
    checks = [checked("rcond_inf", rcond >= Decimal("1e-6"), value=str(rcond)),
              checked("component_sensitivity", all(value is not None and value <= Decimal("1e-8")
                                                       for value in sensitivity)),
              checked("positive_envelope", all(value > 0 for value in lower))]
    return rcond, sensitivity, lower, checks


@high_precision
def identify_coefficients(moment_rows, lexeme_rows):
    by_band = {(float(row["lower_eV"]), float(row["upper_eV"])): row
               for row in moment_rows if row["upper_eV"] is not None}
    lexemes = {(float(row["lower_eV"]), float(row["upper_eV"])): row
               for row in lexeme_rows if row["upper_eV"] is not None}
    require(set(RECOVERY+HOLDOUT) <= set(by_band), "FIXED_RECOVERY_AND_HOLDOUT_ROWS_REQUIRED")
    b = [D(by_band[band]["electron_energy_coefficient_eV_m3_s2"]) for band in RECOVERY]
    require(all(value > 0 for value in b), "POSITIVE_PINNED_MOMENTS_REQUIRED")
    M = [basis_moments(*band)[1] for band in RECOVERY]
    R = [1/value for value in b]
    RM = [[R[i]*M[i][j] for j in range(3)] for i in range(3)]
    c = [1/max(abs(RM[i][j]) for i in range(3)) for j in range(3)]
    require(all(value > 0 and value.is_finite() for value in c), "POSITIVE_COLUMN_SCALES_REQUIRED")
    B = [[RM[i][j]*c[j] for j in range(3)] for i in range(3)]
    inverse, pivots = inverse3(B)
    z = [dsum(row) for row in inverse]
    theta = [c[j]*z[j] for j in range(3)]
    rcond, sensitivity, lower, checks = recovery_metrics(B, inverse, z)
    residual = [dsum(B[i][j]*z[j] for j in range(3))-1 for i in range(3)]
    checks.append(checked("highprecision_solve_residual", max(map(abs, residual)) <= Decimal("1e-65")))
    recovery = []
    for band in RECOVERY:
        raw = by_band[band]["electron_energy_coefficient_eV_m3_s2"]
        recovery.append({"interval_eV": list(band), "saved_binary64": raw, "saved_hex": float(raw).hex(),
                         "saved_exact_lift_decimal": str(D(raw)),
                         "saved_raw_json_lexeme": lexemes[band]["electron_energy_coefficient_eV_m3_s2"]})
    holdouts = []
    for band in HOLDOUT:
        raw = by_band[band]["electron_energy_coefficient_eV_m3_s2"]
        moments = basis_moments(*band)[1]
        predicted = dsum(value*coef for value, coef in zip(moments, theta))
        error = own_scale_error(predicted, raw)
        passed = error <= Decimal("2e-12")
        holdouts.append({"interval_eV": list(band), "saved_binary64": raw,
                         "saved_hex": float(raw).hex(), "predicted_decimal": str(predicted),
                         "relative_error_decimal": str(error), "relative_error_float64": float(error),
                         "pass": passed, "used_for_fit": False})
        checks.append(checked("holdout_"+str(band), passed, relative_error=str(error)))
    passed = all(row["pass"] for row in checks)
    return to_json({
        "status": "MODEL_IDENTIFIED_FROM_PINNED_MOMENTS_NOT_ORIGINAL_COEFFICIENT_BYTES" if passed
                  else "MODEL_IDENTIFICATION_UNRESOLVED",
        "theta_order": THETA_ORDER, "theta_decimal": theta if passed else None,
        "candidate_theta_decimal": theta,
        "theta_float64": [float(value) for value in theta] if passed else None,
        "theta_float64_hex": [float(value).hex() for value in theta] if passed else None,
        "input_representation": {
            "moments": "exact lift of original stored binary64; raw lexemes separately retained",
            "I_H_source_binary64_hex": float("13.605693122994").hex(),
            "I_He_source_binary64_hex": float("24.59").hex(),
            "I_H_source_exact_lift_decimal": D(float("13.605693122994")),
            "I_He_source_exact_lift_decimal": D(float("24.59")),
            "declared_energy_conventions_separate": True,
            "recovery_edges_binary64_hex": [[a.hex(), b.hex()] for a, b in RECOVERY]},
        "recovery_bands": recovery, "holdout_results": holdouts,
        "M_decimal": M, "B_decimal": B, "inverse_B_decimal": inverse,
        "row_scales_decimal": R, "column_scales_decimal": c, "z_decimal": z,
        "rcond_inf_decimal": rcond, "sensitivity_decimal": sensitivity,
        "positive_lower_z_decimal": lower, "solve_residual_decimal": residual,
        "precision_decimal_digits": PRECISION, "pivot_log": pivots, "checks": checks,
        "outward_arithmetic_certificate": False, "fourth_coefficient_fit": False,
    })


def q8_project_basis(energy_with_cutoff):
    """Original Q8 cell rule and number-linear projector, on saved grid only."""
    import numpy as np
    energy = np.asarray(energy_with_cutoff, dtype=np.float64)
    require(energy.ndim == 1 and len(energy) >= 2 and bool(np.all(np.isfinite(energy)))
            and energy[0] >= .1 and energy[-1] <= 10.
            and bool(np.all(np.diff(energy) > 0)), "INVALID_FIXED_BIRTH_GRID")
    xi, weights = np.polynomial.legendre.leggauss(8)
    lo, hi = energy[:-1], energy[1:]
    points = (lo[:, None]+hi[:, None])/2+(hi[:, None]-lo[:, None])/2*xi
    omega = (hi[:, None]-lo[:, None])/2*weights
    alpha = (points-lo[:, None])/(hi[:, None]-lo[:, None])
    require(bool(np.all((0 <= alpha) & (alpha <= 1))) and bool(np.all(omega > 0)),
            "NONCONVEX_Q8_PROJECTOR_NO_CLIPPING_ALLOWED")
    xh, xe = points/float("13.605693122994"), points/float("24.59")
    h0, he0 = (1+xh)**-3, (1+xe)**-3
    basis = ((7./3)*h0+xh*h0, he0, xe*he0)
    K = np.zeros((len(energy), 3), dtype=np.float64)
    quadrature_count, quadrature_energy = [], []
    for index, values in enumerate(basis):
        masses = omega*values
        K[1:, index] += np.sum(masses*alpha, axis=1)
        K[:-1, index] += np.sum(masses*(1-alpha), axis=1)
        quadrature_count.append(math.fsum(map(float, masses.ravel())))
        quadrature_energy.append(math.fsum(map(float, (masses*points).ravel())))
    require(bool(np.all(np.isfinite(K))) and bool(np.all(K >= 0)), "NONPOSITIVE_BASIS_PROJECTION")
    return K, xi, weights, quadrature_count, quadrature_energy


@high_precision
def project_identified_source(retained, identified):
    import numpy as np
    require(identified["theta_decimal"] is not None, "NO_ADOPTED_MODEL_COEFFICIENTS")
    source, saved = retained["source"], retained["saved"]
    atoms = source["history"][0]["bins"]
    ordered = [atoms[-1]]+atoms[:-1]
    E = np.asarray([row["energy_eV"] for row in ordered], dtype=np.float64)
    A = np.asarray([row["number_coefficients"][1] for row in ordered], dtype=np.float64)
    require(hashlib.sha256(E[1:].tobytes()).hexdigest() == saved["input"]["subset_energy"]["sha256"]
            and hashlib.sha256(A[1:].tobytes()).hexdigest() == saved["input"]["subset_A"]["sha256"],
            "ACTUAL_SOURCE_ACTIVE_ARRAY_BYTE_IDENTITY_MISMATCH")
    K, xi, weights, qn, qe = q8_project_basis(E)
    theta = [D(value) for value in identified["theta_decimal"]]
    tf = [float(value) for value in theta]
    AH = tf[0]*K[:, 0]
    AHe = tf[1]*K[:, 1]+tf[2]*K[:, 2]
    prediction = AH+AHe
    residual = prediction-A
    positive = A > 0
    errors = np.zeros_like(A)
    errors[positive] = np.abs(residual[positive])/A[positive]
    zero_pass = bool(np.all(prediction[~positive] == 0.))
    max_error = float(np.max(errors))
    checks = [checked("canonical_each_positive_atom", max_error <= 2e-11, maximum=max_error),
              checked("canonical_exact_zero_atoms", zero_pass)]
    basis_checks = []
    for index in range(3):
        kn = dsum(D(float(value)) for value in K[:, index])
        ke = dsum(D(float(e))*D(float(value)) for e, value in zip(E, K[:, index]))
        en, ee = own_scale_error(kn, qn[index]), own_scale_error(ke, qe[index])
        basis_checks.append({"basis": THETA_ORDER[index], "count_relative": str(en),
                             "energy_relative": str(ee)})
        checks.append(checked("Q8_projector_count_energy_"+str(index),
                              max(en, ee) <= Decimal("2e-11")))
    nm, em = basis_moments(float(E[0]), float(E[-1]))
    targets = {}
    for label, values, positions in (("H", AH, (0,)), ("He", AHe, (1, 2))):
        number = dsum(D(float(value)) for value in values)
        energy = dsum(D(float(e))*D(float(value)) for e, value in zip(E, values))
        analytic_n = dsum(theta[index]*nm[index] for index in positions)
        analytic_e = dsum(theta[index]*em[index] for index in positions)
        en, ee = own_scale_error(number, analytic_n), own_scale_error(energy, analytic_e)
        targets[label] = to_json({"number_coefficient_m3_s2": number,
            "energy_coefficient_eV_m3_s2": energy,
            "analytic_number_coefficient_m3_s2": analytic_n,
            "analytic_energy_coefficient_eV_m3_s2": analytic_e,
            "analytic_number_relative_error": en, "analytic_energy_relative_error": ee,
            "direct_cutoff_number_coefficient_m3_s2": D(float(values[0])),
            "direct_cutoff_energy_coefficient_eV_m3_s2": D(float(E[0]))*D(float(values[0]))})
        checks.append(checked("projected_vs_analytic_target_"+label,
                              max(en, ee) <= Decimal("2e-11")))
    reconstructed_n = dsum(D(targets[s]["number_coefficient_m3_s2"]) for s in ("H", "He"))
    reconstructed_e = dsum(D(targets[s]["energy_coefficient_eV_m3_s2"]) for s in ("H", "He"))
    total_n_error = own_scale_error(reconstructed_n, source["history"][0]["number_coefficients"][1])
    total_e_error = own_scale_error(reconstructed_e, source["history"][0]["energy_coefficients_eV"][1])
    checks.append(checked("canonical_total_number_energy", max(total_n_error, total_e_error) <= Decimal("2e-11")))
    validation = to_json({"status": "PASS_SCOPED_PROJECTION" if all(row["pass"] for row in checks)
                         else "MODEL_IDENTIFICATION_UNRESOLVED",
        "canonical_atom_count": len(E), "active_atom_count": 3200, "cutoff_row": 0,
        "max_atom_relative_error": max_error, "canonical_exact_zero_pass": zero_pass,
        "atom_relative_tolerance": 2e-11,
        "canonical_total_number_relative_error": total_n_error,
        "canonical_total_energy_relative_error": total_e_error,
        "target_totals": targets, "quadrature_projector_invariants": basis_checks,
        "quadrature": {"rule": "original eight-point Gauss-Legendre per original low cell",
            "numpy_version": np.__version__, "nodes": array_identity(xi), "weights": array_identity(weights),
            "cell_points": "(lo+hi)/2+(hi-lo)/2*xi",
            "number_linear_projector": True, "original_source_modules_imported": False},
        "new_source_normalization_factors": [], "canonical_source_replaced": False,
        "residual_reassigned": False, "checks": checks})
    arrays = {"energy_eV_with_cutoff": E, "canonical_A_m3_s2": A, "basis_K": K,
              "identified_A_H_m3_s2": AH, "identified_A_He_m3_s2": AHe,
              "reconstruction_residual_A_m3_s2": residual, "atom_relative_error": errors,
              "quadrature_nodes": xi, "quadrature_weights": weights}
    return validation, arrays


def source_scope():
    return {"birth_tag": TAG, "native_birth_support_eV": [.1, 10.],
        "identification_support_eV": [0., 1000.], "history_s": [0., TIMES[-1]],
        "history_outside": None, "proper_clock": "proper_s", "frame": FRAME,
        "proper_volume_mode": "fixed", "absolute_proper_volume_m3": None,
        "isotope_mapping": ISOTOPE, "same_state_inventory_id": STATE,
        "T_K": "100", "nH_total_m3": "140", "nHe_total_m3": "1085/94", "nb_m3": "8750/47",
        "foreign_consumer_activation": False, "old_source_or_RR_replay": 0,
        "old_science_replays": 0, "original_RR_chain_replay": False,
        "full9600_operator_recovery": False, "full9600_G_recovery": False,
        "actual_full_physical_native25": None,
        "actual_external_work": None, "physical_heating_complete": False,
        "global_physical_completion": None, "global_physical_error": None,
        "global_budget_remaining": None, "currency": None}


@high_precision
def run_prepare(out):
    retained = load_retained_inputs()
    identified = identify_coefficients(retained["moments"], retained["moment_lexemes"])
    result = {"schema": "CR_PARENT_EVENT_PREPARATION_V1", "unit": UNIT_ID,
              "status": "MODEL_IDENTIFICATION_UNRESOLVED", "scope": source_scope(),
              "producer_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "input_identity": retained["identity"], "coefficient_identification": identified,
              "projection_validation": None, "artifacts": {}, "checks": list(identified["checks"])}
    if identified["theta_decimal"] is not None:
        validation, arrays = project_identified_source(retained, identified)
        result["projection_validation"] = validation
        result["checks"] += validation["checks"]
        import numpy as np
        path = out / "ATTRIBUTION_ARRAYS.npz"
        with path.open("xb") as stream:
            np.savez(stream, **arrays)
        result["artifacts"]["ATTRIBUTION_ARRAYS.npz"] = {
            **file_identity(path, str(path.relative_to(UNIT))),
            "arrays": {name: array_identity(value) for name, value in arrays.items()}}
    if all(row["pass"] for row in result["checks"]):
        result["status"] = "PASS_SCOPED_MODEL_IDENTIFICATION"
    write_json_new(out / "PREPARATION.json", result)
    return 0 if result["status"] == "PASS_SCOPED_MODEL_IDENTIFICATION" else 1


def actual_binding_context():
    return {"source_record_sha256": SOURCE_SHA, "source_revision": SOURCE_REVISION,
        "source_payload_sha256": PAYLOAD_SHA, "source_family_id": FAMILY,
        "birth_partition_id": PARTITION, "birth_tag": TAG,
        "source_state_id": SOURCE_STATE, "donor_state_id": STATE, "recipient_state_id": STATE,
        "donor_frame": FRAME, "recipient_frame": FRAME, "isotope_mapping": ISOTOPE,
        "temperature_K": "100", "nH_semantics": "total_nuclei",
        "nH_m3": "140", "nHe_m3": "1085/94", "xHII": "0.01", "xHeII": "0.01", "xHeIII": "0",
        "donor_nb_m3": "8750/47", "recipient_nb_m3": "8750/47",
        "native_birth_support_eV": [.1, 10.], "history_s": [0., TIMES[-1]],
        "history_law": "q_j(t)=t*A_j", "history_outside": None,
        "proper_clock": "proper_s", "clock_origin_s": 0.,
        "proper_volume_mode": "fixed", "proper_volume_m3": None,
        "source_target_density": "already_included", "source_proper729": "already_included",
        "source_angle_integration": "already_included", "additional_source_multiplier": 1.,
        "clock_jacobian": 1., "volume_jacobian": 1.,
        "per_baryon_already_applied": False, "energy_unit_conversion_already_applied": False,
        "actual_external_work": None, "actual_He_parameters": {"s": None, "p": None, "d": None}}


@high_precision
def validate_binding(context):
    """Absent inputs remain absent; present incompatible metadata is refused."""
    require(type(context) is dict, "EXPLICIT_SOURCE_RECIPIENT_CONTRACT_REQUIRED")
    expected = actual_binding_context()
    optional_missing = {"history_s", "donor_nb_m3", "recipient_nb_m3", "donor_state_id", "recipient_state_id"}
    for key, wanted in expected.items():
        if key in optional_missing:
            continue
        require(key in context and context[key] == wanted, "WRONG_OR_MIXED_BINDING:"+key)
    for key in ("donor_state_id", "recipient_state_id"):
        if context.get(key) is not None:
            require(context[key] == STATE, "WRONG_SAME_TEMPERATURE_STATE:"+key)
    for key in ("donor_nb_m3", "recipient_nb_m3"):
        if context.get(key) is not None:
            require(D(context[key]) == D("8750/47"), "WRONG_OR_FOREIGN_BARYON_DENSITY:"+key)
    if context.get("history_s") is None:
        return {"status": "UNBOUND_HISTORY_NO_INFERENCE", "derived_rate": None,
                "exposure": None, "finite_event_N_E": None, "native25": None,
                "per_baryon_values": None}
    require(context["history_s"] == [0., TIMES[-1]], "WRONG_PROPER_HISTORY_OR_CLOCK")
    if any(context.get(key) is None for key in optional_missing-{"history_s"}):
        return {"status": "UNBOUND_SAME_STATE_NB", "per_baryon_values": None,
                "native25": None, "derived_consumer_rate": None, "exposure": None,
                "proper_density_history_bound": True}
    return {"status": "BOUND_CONDITIONAL_SAME_STATE", "proper_density_history_bound": True,
            "nb_m3_decimal": str(D("8750/47")), "absolute_worldtube_totals": None}


@high_precision
def finite_source_factor(a, b, history=(0., 10000000000.)):
    require(history is not None, "MISSING_HISTORY_CANNOT_BE_INFERRED")
    a, b, first, last = D(a), D(b), D(history[0]), D(history[1])
    require(first <= a <= b <= last, "QUERY_OUTSIDE_KNOWN_PROPER_HISTORY")
    return (b-a)*(b+a)/2


@high_precision
def baseline_inventory():
    nH, nHe, ne, nb = Fraction(140), Fraction(1085, 94), Fraction(2849, 1880), Fraction(8750, 47)
    species = [Fraction(0) for _ in SPECIES]
    species[1], species[2] = nH*Fraction(99, 100)/nb, nH*Fraction(1, 100)/nb
    species[10], species[11] = nHe*Fraction(99, 100)/nb, nHe*Fraction(1, 100)/nb
    require(sum(a*y for a, y in zip(MASSES, species)) == 1, "EXACT_BASELINE_BARYON_IDENTITY_FAILED")
    require(sum(q*y for q, y in zip(CHARGES, species)) == ne/nb, "EXACT_BASELINE_CHARGE_IDENTITY_FAILED")
    return to_json({"species_order": SPECIES, "charges": CHARGES, "mass_numbers": MASSES,
        "Y_rational": [str(value) for value in species], "Y_decimal": [D(value) for value in species],
        "Y_float64_diagnostic": [float(value) for value in species],
        "n_b_m3_rational": str(nb), "n_b_m3_decimal": D(nb),
        "n_part0_m3_rational": str(nH+nHe+ne), "n_part0_m3_decimal": D(nH+nHe+ne),
        "T0_K_decimal": "100", "initial_selected_zeta": "0", "initial_selected_w_nt": "0",
        "scoped_external_reference_offset": "0", "actual_total_external_reservoir": None,
        "inventory_semantics": "new exact conditional H1/He4 total-nuclei inventory; source bytes not renormalized",
        "source_neutral_factor_already_applied": True, "foreign_state_adopted": False})


@high_precision
def native_affine(JH, NHe, CH, CHe):
    JH, NHe, CH, CHe = map(D, (JH, NHe, CH, CHe))
    require(all(value >= 0 for value in (JH, NHe, CH, CHe)), "NONNEGATIVE_EVENT_EXTENTS_REQUIRED")
    nb = D("8750/47")
    density = [Decimal(0)]*21
    density[1], density[2] = -JH+CH, JH-CH
    density[10], density[11] = -NHe+CHe, NHe-CHe
    vp, vd = [0]*21, [0]*21
    vp[11], vp[12] = -1, 1
    vd[10], vd[11], vd[12] = 1, -2, 1
    require(sum(a*v for a, v in zip(MASSES, vp)) == 0
            and sum(a*v for a, v in zip(MASSES, vd)) == 0,
            "EXACT_AFFINE_BARYON_COEFFICIENT_IDENTITY_FAILED")
    require(sum(q*v for q, v in zip(CHARGES, vp)) == 1
            and sum(q*v for q, v in zip(CHARGES, vd)) == 0,
            "EXACT_AFFINE_PARTNER_CHARGE_IDENTITY_FAILED")
    return to_json({"intercept_decimal": [value/nb for value in density],
        "coefficient_p_decimal": [D(value)/nb for value in vp],
        "coefficient_d_decimal": [D(value)/nb for value in vd],
        "intercept_float64": [float(value/nb) for value in density],
        "density_intercept_decimal": density,
        "coefficient_p_density_exact": vp, "coefficient_d_density_exact": vd,
        "parameter_units": "proper m^-3", "actual_parameters": {"s": None, "p": None, "d": None},
        "intercept_is_actual_branch": False, "unknown_partner_addendum": None,
        "domain": "p>=0,d>=0,p+2*d<=N_eHe; necessary marginal constraint only",
        "marginal_He_electron_count_m3": NHe, "delta_nb_m3": "0",
        "delta_nb_scope": "selected direct collision events, not full external proton injection"})


@high_precision
def evaluate_family(affine, p, d, *, baseline_Y=None):
    require(p is not None and d is not None, "NO_DEFAULT_ACTUAL_HE_BRANCH")
    p, d, marginal = D(p), D(d), D(affine["marginal_He_electron_count_m3"])
    p_exact, d_exact, marginal_exact = map(Fraction, (p, d, marginal))
    require(p_exact >= 0 and d_exact >= 0 and p_exact+2*d_exact <= marginal_exact,
            "HE_SELECTED_MARGINAL_DOMAIN_REFUSED")
    values = [D(a)+p*D(b)+d*D(c) for a, b, c in zip(affine["intercept_decimal"],
              affine["coefficient_p_decimal"], affine["coefficient_d_decimal"])]
    if baseline_Y is not None:
        require(len(baseline_Y) == 21 and all(D(base)+delta >= 0 for base, delta in zip(baseline_Y, values)),
                "NEGATIVE_TWO_PART_RECIPIENT_SPECIES_REFUSED")
    return values


def exact_terminating_decimal(value):
    """Represent a finite rational exactly without the active Decimal context.

    Used only for He fixture boundaries/remainders. This does not change the
    80-digit fit, projection, or ordinary native arithmetic precision.
    """
    require(isinstance(value, Fraction), "EXACT_FRACTION_REQUIRED")
    numerator, denominator = value.numerator, value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    require(denominator == 1, "NONTERMINATING_DECIMAL_REFUSED")
    places = max(twos, fives)
    coefficient = abs(numerator) * 2**(places-twos) * 5**(places-fives)
    digits = tuple(int(digit) for digit in str(coefficient))
    # Decimal(tuple) is exact; no division, unary plus, normalize, or quantize.
    return Decimal((int(numerator < 0), digits, -places))


def refuse_unclosed_activation(affine, *, partner_response=None, exclusive_branch=None):
    require(exclusive_branch is not None and partner_response is not None,
            "FULL_ACTIVATION_REQUIRES_EXCLUSIVE_BRANCH_AND_PARTNER_RESPONSE")
    raise ValueError("ACTUAL_FULL_CONSUMER_ACTIVATION_NOT_ADMITTED_BY_THIS_PARTIAL_UNIT")


@high_precision
def selected_nonthermal(active_n, active_u, cutoff_n, cutoff_u):
    """Signed active changes in a bin are preserved; cutoff remains positive."""
    active_n, active_u, cutoff_n, cutoff_u = map(D, (active_n, active_u, cutoff_n, cutoff_u))
    require(cutoff_n >= 0 and cutoff_u >= 0, "NEGATIVE_CUTOFF_EXTENTS")
    nb, ev = D("8750/47"), D("1.602176634e-19")
    return to_json({
        "retention": {"delta_zeta": (active_n+cutoff_n)/nb, "delta_w_nt_J_per_baryon": (active_u+cutoff_u)*ev/nb},
        "assimilation_fixture": {"delta_zeta": active_n/nb, "delta_w_nt_J_per_baryon": active_u*ev/nb},
        "default_cutoff": "retained_unresolved_selected_nonthermal_reservoir",
        "actual_partner_addendum": None, "actual_full_nonthermal_state": None,
        "cutoff_spectrum_below_boundary": None, "nb_division_count": 1, "eV_to_J_conversion_count": 1})


@high_precision
def decimal_log1p(value):
    value = D(value)
    require(value > -1, "NONPOSITIVE_TEMPERATURE_RATIO")
    if value == 0:
        return Decimal(0)
    if abs(value) <= Decimal("0.125"):
        power, partial = value, Decimal(0)
        for order in range(1, 4097):
            partial += power/order if order % 2 else -power/order
            remainder = abs(power*value)/((order+1)*(1-abs(value)))
            if remainder <= Decimal("1e-70")*abs(partial):
                return partial
            power *= value
        raise ArithmeticError("LOG1P_SERIES_DID_NOT_MEET_INTERNAL_TARGET")
    return (1+value).ln()


def closed_caloric_fixture():
    return {"classification": "explicit_conditional_fixture_not_actual_He_branch",
        "p_m3": "0", "d_m3": "0", "partner_closure": "no_outside_partner_by_explicit_p0_fixture",
        "EOS": "monatomic_translational_ideal_gas_cv_3kB_over_2",
        "hidden_excitation_thermal_transfer": False, "actual_donor_debit_claimed": False,
        "frozen_100K_response_postprocessing": True, "rate_feedback": False}


@high_precision
def finite_caloric(q_J_m3, n_thermal_m3, *, prior_Q_J_m3, prior_n_thermal_m3, closure):
    require(closure == closed_caloric_fixture(), "EXPLICIT_PARTNER_EOS_CLOSURE_REQUIRED")
    q, n, prior_q, prior_n = map(D, (q_J_m3, n_thermal_m3, prior_Q_J_m3, prior_n_thermal_m3))
    require(q >= 0 and n >= 0 and prior_q >= 0 and prior_n >= 0, "NONNEGATIVE_CALORIC_FIXTURE_EXTENTS_REQUIRED")
    base = baseline_inventory()
    n0, T0 = D(base["n_part0_m3_decimal"]), D(base["T0_K_decimal"])
    cv = D("1.380649e-23")*3/2
    U0 = cv*n0*T0
    Ua, Da = U0+prior_q, n0+prior_n
    require(Ua > 0 and Da > 0 and Da+n > 0 and Ua+q > 0, "NONPOSITIVE_CALORIC_STATE")
    delta = (q*Da-Ua*n)/(Ua*(Da+n))
    log_delta = decimal_log1p(delta)
    return to_json({"Q_J_m3": q, "thermal_count_m3": n,
        "baseline_thermal_energy_J_m3": Ua, "baseline_particle_density_m3": Da,
        "baseline_energy_two_part": {"origin": U0, "prefix_increment": prior_q},
        "baseline_particle_two_part": {"origin": n0, "prefix_increment": prior_n},
        "delta_T_ratio": delta, "delta_logT": log_delta,
        "delta_logT_float64": math.log1p(float(delta)),
        "temperature_baseline_decimal": Ua/(cv*Da),
        "conditional": True, "explicit_closure": closure,
        "actual_temperature_point": None, "physical_heating_complete": False,
        "coupled_thermal_history_solved": False, "rate_feedback_recomputed": False})


@high_precision
def caloric_for_saved_row(saved_row, previous_prefix, mode):
    require(mode in ("retention", "assimilation"), "UNKNOWN_CUTOFF_CLOSURE")
    ev = D("1.602176634e-19")
    def increments(row):
        if row is None:
            return Decimal(0), Decimal(0)
        q = D(row["coulomb_energy_eV_m3"])
        n = Decimal(0)
        if mode == "assimilation":
            q += D(row["cutoff_energy_eV_m3"])
            n = D(row["cutoff_number_m3"])
        return q*ev, n
    q, n = increments(saved_row)
    prior_q, prior_n = increments(previous_prefix)
    result = finite_caloric(q, n, prior_Q_J_m3=prior_q, prior_n_thermal_m3=prior_n,
                           closure=closed_caloric_fixture())
    result["mode"] = mode
    result["cutoff_default_actual_adoption"] = False
    return result


def _overlap(first, second):
    return max(D(first[0]), D(second[0])) < min(D(first[1]), D(second[1]))


def claim_components(packet, registry, *, components=("birth", "RR:H", "RR:He", "cutoff")):
    """Atomic once-only bookkeeping claims; never activates an unknown state."""
    require(type(registry) is list, "EXPLICIT_SHARED_OWNERSHIP_REGISTRY_REQUIRED")
    require(packet.get("role") == "disjoint_observation_bin", "CUMULATIVE_PREFIX_IS_NOT_ADDITIVE")
    require(packet.get("conditional_fixture", False) is False, "CONDITIONAL_FIXTURE_IS_NOT_ACTUAL_FAMILY_CLAIM")
    identity = packet["claim_identity"]
    require(identity["family_id"] == FAMILY and identity["recipient_identity"] == STATE,
            "UNKNOWN_PHYSICAL_FAMILY_OR_RECIPIENT")
    window, support = packet["interval_s"], identity["native_birth_support_eV"]
    require(len(window) == 2 and D(0) <= D(window[0]) < D(window[1]) <= D(TIMES[-1]),
            "INVALID_CLAIM_PROPER_INTERVAL")
    require(len(support) == 2 and D(.1) <= D(support[0]) < D(support[1]) <= D(10.),
            "CLAIM_SUPPORT_EXTENSION_REFUSED")
    require(len(set(components)) == len(components)
            and set(components) <= {"birth", "RR:H", "RR:He", "cutoff"}, "EXPLICIT_UNIQUE_COMPONENTS_REQUIRED")
    pending = []
    for component in components:
        claim = {"family_id": FAMILY, "recipient_identity": STATE, "component": component,
            "interval_s": list(window), "native_birth_support_eV": list(support),
            "clock": "proper_s", "clock_origin_s": 0.,
            "interval_meaning": "birth_interval" if component == "birth" else "observation_interval",
            "scope": "partial_bookkeeping_only_no_full_consumer_activation"}
        for old in registry+pending:
            require(not(old["family_id"] == claim["family_id"]
                    and old["recipient_identity"] == claim["recipient_identity"]
                    and old["component"] == component
                    and _overlap(old["interval_s"], window)
                    and _overlap(old["native_birth_support_eV"], support)),
                    "SAME_EVENT_OVERLAP_OR_AGGREGATE_PRIOR_RR_DUPLICATION")
        pending.append(claim)
    registry.extend(pending)
    return copy.deepcopy(pending)


def claim_saved_rr_component(saved_claim, registry, *, recipient_identity=STATE):
    require(saved_claim.get("horizon") == "finite_known_history_observation_bin"
            and saved_claim.get("channel") in ("H", "He"), "EXACT_SAVED_FINITE_RR_COMPONENT_REQUIRED")
    packet = {"role": "disjoint_observation_bin", "interval_s": saved_claim["observation_bin_s"],
        "claim_identity": {"family_id": saved_claim["family_id"], "recipient_identity": recipient_identity,
                           "native_birth_support_eV": saved_claim["native_birth_support_eV"]}}
    return claim_components(packet, registry, components=("RR:"+saved_claim["channel"],))


@high_precision
def energy_sidecars(JH, NHe, row):
    JH, NHe = D(JH), D(NHe)
    ch, ce = D(row["channels"]["H"]["capture_number_m3"]), D(row["channels"]["He"]["capture_number_m3"])
    ph = D(row["channels"]["H"]["retained_photon_energy_eV_m3"])
    pe = D(row["channels"]["He"]["retained_photon_energy_eV_m3"])
    active = D(row["active_energy_eV_m3"] if row["role"] == "nonadditive_cumulative_prefix"
               else row["active_energy_change_eV_m3"])
    injected, cut, coulomb = map(D, (row["injected_energy_eV_m3"], row["cutoff_energy_eV_m3"], row["coulomb_energy_eV_m3"]))
    IHsrc, I1src, IHstar, I1star, I2star, IHRR, IHeRR = map(D,
        ("13.605693122994", "24.59", "13.6", "24.59", "54.42", "13.60", "24.59"))
    source_h, source_he = IHsrc*JH, I1src*NHe
    L0 = injected+source_h+source_he
    chemical = IHstar*(JH-ch)+I1star*(NHe-ce)
    literal_terms = {"source_H_convention": (IHsrc-IHstar)*JH,
        "source_He_convention": (I1src-I1star)*NHe,
        "RR_H_convention": (IHstar-IHRR)*ch, "RR_He_convention": (I1star-IHeRR)*ce}
    literal = dsum(literal_terms.values())
    balance = L0-(active+cut+coulomb+ph+pe+chemical)
    saved_residual = injected-(active+cut+coulomb+ph+pe-IHRR*ch-IHeRR*ce)
    return to_json({"L0_eV_m3": L0,
        "L0_status": "canonical_kinetic_plus_model_identified_electron_equivalent_binding_functional_not_actual_proton_debit",
        "source_binding_H_eV_m3": source_h, "source_binding_He_electron_equivalent_eV_m3": source_he,
        "RR_binding_release_H_eV_m3": IHRR*ch, "RR_binding_release_He_eV_m3": IHeRR*ce,
        "chemical_intercept_eV_m3": chemical, "chemical_coefficient_p_eV": I2star,
        "chemical_coefficient_d_eV": I2star-I1star, "chemical_intercept_is_actual_branch": False,
        "literal_convention_residual_eV_m3": literal, "literal_terms_eV_m3": literal_terms,
        "literal_H_difference_eV": IHsrc-IHstar,
        "branch_lift": {"coefficient_p_eV": I2star, "coefficient_d_eV": I2star-I1star,
                        "actual_value_eV_m3": None, "separate_from_literal_convention": True},
        "selected_balance_intercept_eV_m3": balance,
        "saved_energy_residual_eV_m3": saved_residual,
        "saved_energy_residual_definition": "Uinj-(dUactive+UC+QC+PH+PHe-IHRR*CH-IHeRR*CHe), exact lifts of saved scalars",
        "saved_kinetic_residual_as_stored_eV_m3": row["kinetic_energy_residual_eV_m3"],
        "saved_total_residual_as_stored_eV_m3": row["total_energy_residual_eV_m3"],
        "balance_residual_after_saved_eV_m3": balance-literal-saved_residual,
        "required_donor_work_symbolic": "L0+U_partner+I2src*p+(I2src-I1src)*d+residual_excitation",
        "branch_convention_residual_symbolic": "(I2src-I2star)*p+((I2src-I1src)-(I2star-I1star))*d",
        "actual_I2_source_eV": None, "actual_partner_energy_eV_m3": None,
        "actual_residual_excitation_eV_m3": None, "actual_required_donor_work_eV_m3": None,
        "actual_proton_debit": None, "actual_external_work": None,
        "literal_or_branch_residual_deposited_as_heat": False,
        "retained_photon_w_ext_contribution": 0, "scoped_projected_w_ext": 0,
        "eV_J_exact": "1.602176634e-19"})


def retained_photon_descriptor(retained, row, index):
    saved, identity = retained["saved"], retained["identity"]
    descriptor = saved["artifacts"]["ARRAYS.npz"]
    require(descriptor["sha256"] == RR_ARRAYS_SHA, "EXACT_PHOTON_ARRAY_FILE_REQUIRED")
    suffix = "prefix" if row["role"] == "nonadditive_cumulative_prefix" else "bins"
    result = {}
    for channel in ("H", "He"):
        count_member = "capture_"+channel+"_"+suffix+"_m3"
        energy_member = "photon_"+channel+"_energy_eV"
        members = descriptor["arrays"]
        require(members[count_member]["shape"] == [4, 3200]
                and members[energy_member]["shape"] == [3200], "SAVED_EXPLICIT_PHOTON_ATOM_SHAPE_CHANGED")
        result[channel] = {"arrays_file": identity["saved_response_arrays"],
            "count_member": count_member, "energy_member": energy_member, "row_index": index,
            "member_sha256": {"count": members[count_member]["sha256"], "energy": members[energy_member]["sha256"]},
            "saved_port": copy.deepcopy(row["retained_photon_ports"][channel]),
            "atom_count": 3200, "spectrum_kind": "reference_to_exact_saved_explicit_discrete_capture_atoms",
            "source_moments_inverted": False, "continuous_time_spectrum": None,
            "escape_or_absorption": None, "actual_physical_heating": None,
            "retained_photon_w_ext_contribution": 0, "absolute_worldtube_count": None}
    return result


@high_precision
def consume_selected_parent_event_window(retained, prepared, row, index, *, binding,
                                         previous_prefix=None, previous_prefix_packet=None):
    binding_status = validate_binding(binding)
    if binding_status["status"] == "UNBOUND_HISTORY_NO_INFERENCE":
        return {**binding_status, "source_H_N_E": None, "source_He_electron_N_E": None,
                "actual_full_native25": None, "actual_external_work": None,
                "actual_temperature_point": None, "physical_heating_complete": False}
    interval = row["interval_s"]
    require(row["role"] in ("nonadditive_cumulative_prefix", "disjoint_observation_bin"),
            "EXPLICIT_PREFIX_OR_OBSERVATION_BIN_ROLE_REQUIRED")
    require(type(index) is int and 0 <= index < 4, "EXACT_SAVED_WINDOW_INDEX_REQUIRED")
    prefix = row["role"] == "nonadditive_cumulative_prefix"
    source_collection = "prefixes" if prefix else "observation_bins"
    require(row == retained["saved"][source_collection][index], "SAVED_RESPONSE_ROW_CHANGED")
    expected_window = [0., TIMES[index]] if prefix else [0. if index == 0 else TIMES[index-1], TIMES[index]]
    require(interval == expected_window, "SAVED_RESPONSE_WINDOW_IDENTITY_MISMATCH")
    if prefix:
        require(previous_prefix is None and previous_prefix_packet is None, "PREFIX_USES_ORIGINAL_BASELINE")
    else:
        require(row.get("includes_prior_injected_survivors") is True, "BIN_MUST_INCLUDE_PRIOR_COHORTS")
        require((previous_prefix is None) == (index == 0)
                and (previous_prefix_packet is None) == (index == 0),
                "BIN_REQUIRES_ITS_PRIOR_PREFIX_BASELINE")
        if index:
            require(previous_prefix["interval_s"] == [0., interval[0]]
                    and previous_prefix_packet["interval_s"] == [0., interval[0]],
                    "WRONG_PRIOR_PREFIX_BASELINE")
            require(previous_prefix == retained["saved"]["prefixes"][index-1]
                    and previous_prefix_packet["saved_response_reference"]["row_as_saved"] == previous_prefix,
                    "PRIOR_PREFIX_MUST_BE_THE_SAME_PINNED_SAVED_RESPONSE")
    factor = finite_source_factor(*interval, binding["history_s"])
    totals = prepared["projection_validation"]["target_totals"]
    source_values = {}
    for target in ("H", "He"):
        coeff_n, coeff_u = D(totals[target]["number_coefficient_m3_s2"]), D(totals[target]["energy_coefficient_eV_m3_s2"])
        require(coeff_n >= 0 and coeff_u >= 0, "NONNEGATIVE_IDENTIFIED_SOURCE_REQUIRED")
        source_values[target] = to_json({"number_m3": factor*coeff_n, "energy_eV_m3": factor*coeff_u,
            "endpoint_number_rate_m3_s": D(interval[1])*coeff_n,
            "endpoint_energy_rate_eV_m3_s": D(interval[1])*coeff_u,
            "endpoint_side": "known_history_left_limit" if interval[1] == TIMES[-1] else "within_known_history",
            "proper_window_duration_s": D(interval[1])-D(interval[0]),
            "integrated_source_clock_factor_s2": factor,
            "source_time_factor_applied_count": 1})
    if binding_status["status"] != "BOUND_CONDITIONAL_SAME_STATE":
        return {**binding_status, "source_H_N_E": source_values["H"],
                "source_He_electron_N_E": source_values["He"], "native_affine_Y": None,
                "actual_full_native25": None, "actual_external_work": None,
                "actual_temperature_point": None, "physical_heating_complete": False}
    JH, NHe = D(source_values["H"]["number_m3"]), D(source_values["He"]["number_m3"])
    UH, UHe = D(source_values["H"]["energy_eV_m3"]), D(source_values["He"]["energy_eV_m3"])
    channels = row["channels"]
    event_terms = {
        "J_H": str(JH), "N_eHe": str(NHe),
        "C_H": channels["H"]["capture_number_m3"], "C_He": channels["He"]["capture_number_m3"],
        "K_H": channels["H"]["capture_kinetic_eV_m3"], "K_He": channels["He"]["capture_kinetic_eV_m3"],
        "RR_binding_H": channels["H"]["binding_energy_change_eV_m3"],
        "RR_binding_He": channels["He"]["binding_energy_change_eV_m3"],
        "retained_photon_H": channels["H"]["retained_photon_energy_eV_m3"],
        "retained_photon_He": channels["He"]["retained_photon_energy_eV_m3"],
        "cutoff_direct_N": row["cutoff_direct_number_m3"], "cutoff_drift_N": row["cutoff_drift_number_m3"],
        "cutoff_N": row["cutoff_number_m3"], "cutoff_U": row["cutoff_energy_eV_m3"],
        "Coulomb_Q": row["coulomb_energy_eV_m3"],
        "active_N_change": row["active_number_m3"] if prefix else row["active_number_change_m3"],
        "active_U_change": row["active_energy_eV_m3"] if prefix else row["active_energy_change_eV_m3"],
    }
    event_terms["saved_binary64_hex"] = {key: float(value).hex() for key, value in event_terms.items()
                                          if type(value) in (float, int)}
    event_terms["saved_channels"] = copy.deepcopy(channels)
    event_terms["saved_RR_recovered_by_source_subtraction"] = False
    event_terms["source_parent_target_is_capture_target"] = False
    for name in ("C_H", "C_He", "K_H", "K_He", "retained_photon_H", "retained_photon_He",
                 "cutoff_direct_N", "cutoff_drift_N", "cutoff_N", "cutoff_U", "Coulomb_Q"):
        require(D(event_terms[name]) >= 0, "NEGATIVE_SAVED_POSITIVE_EVENT_TERM:"+name)
    if prefix:
        require(D(event_terms["active_N_change"]) >= 0 and D(event_terms["active_U_change"]) >= 0,
                "NEGATIVE_CUMULATIVE_ACTIVE_POPULATION")
    CH, CHe = D(event_terms["C_H"]), D(event_terms["C_He"])
    canonical_n, canonical_u = D(row["injected_number_m3"]), D(row["injected_energy_eV_m3"])
    epsilon_n, epsilon_u = JH+NHe-canonical_n, UH+UHe-canonical_u
    split_n_error, split_u_error = own_scale_error(JH+NHe, canonical_n), own_scale_error(UH+UHe, canonical_u)
    affine = native_affine(JH, NHe, CH, CHe)
    nb = D("8750/47")
    active_n, active_u = D(event_terms["active_N_change"]), D(event_terms["active_U_change"])
    cut_n, cut_u = D(event_terms["cutoff_N"]), D(event_terms["cutoff_U"])
    selected = selected_nonthermal(active_n, active_u, cut_n, cut_u)
    sidecars = energy_sidecars(JH, NHe, row)
    event_terms["source_binding_H"] = sidecars["source_binding_H_eV_m3"]
    event_terms["source_binding_He_electron_equivalent"] = sidecars["source_binding_He_electron_equivalent_eV_m3"]
    event_terms["literal_convention_terms"] = copy.deepcopy(sidecars["literal_terms_eV_m3"])
    event_terms["symbolic_branch_lift_terms"] = copy.deepcopy(sidecars["branch_lift"])
    baseline = baseline_inventory()
    closed_family = []
    for label, fraction in (("single_selected_fixture", Fraction(0)),
                            ("mixed_single_double_closed_fixture", Fraction(1, 4)),
                            ("all_selected_pairs_fixture", Fraction(1, 2))):
        d = exact_terminating_decimal(Fraction(NHe)*fraction)
        base_y = [D(value) for value in baseline["Y_decimal"]]
        if previous_prefix_packet is not None:
            prior_affine = previous_prefix_packet["native_affine_Y"]
            prior_d = exact_terminating_decimal(Fraction(D(prior_affine["marginal_He_electron_count_m3"]))*fraction)
            prior_delta = evaluate_family(prior_affine, 0, prior_d, baseline_Y=base_y)
            base_y = [value+delta for value, delta in zip(base_y, prior_delta)]
        delta = evaluate_family(affine, 0, d, baseline_Y=base_y)
        closed_family.append(to_json({"label": label, "conditional": True,
            "p_m3": "0", "d_m3": d, "s_m3": exact_terminating_decimal(Fraction(NHe)-2*Fraction(d)),
            "d_fraction_of_selected_He": str(fraction), "delta_Y_decimal": delta,
            "baseline_Y_decimal": base_y,
            "rounded_endpoint_Y_diagnostic": [float(value+increment) for value, increment in zip(base_y, delta)],
            "branch_lift_eV_m3": D("29.83")*d,
            "actual_branch_measurement": False, "actual_full_native25": None,
            "branch_source_work": None, "hidden_excitation_thermal_transfer": False}))
    caloric = {}
    for mode in ("retention", "assimilation"):
        caloric[mode] = caloric_for_saved_row(row, previous_prefix, mode)
        caloric[mode]["baseline_prefix_index"] = None if previous_prefix is None else index-1
    density_delta = [D(value)*nb for value in affine["intercept_decimal"]]
    baryon_residual = dsum(D(a)*value for a, value in zip(MASSES, density_delta))
    charge_delta = dsum(D(q)*value for q, value in zip(CHARGES, density_delta))
    saved_count_residual = active_n+cut_n+CH+CHe-canonical_n
    retained_charge_gap = charge_delta-active_n-cut_n
    charge_residual = retained_charge_gap-(epsilon_n-saved_count_residual)
    energy_residual = D(sidecars["balance_residual_after_saved_eV_m3"])
    native_scale = dsum(abs(value) for value in density_delta)
    charge_scale = abs(JH)+abs(NHe)+abs(CH)+abs(CHe)+abs(active_n)+abs(cut_n)
    energy_scale = dsum(abs(D(sidecars[key])) for key in
                       ("L0_eV_m3", "chemical_intercept_eV_m3", "literal_convention_residual_eV_m3"))
    checklist = [
        checked("window_source_number_attribution", split_n_error <= Decimal("2e-11"), relative=str(split_n_error)),
        checked("window_source_energy_attribution", split_u_error <= Decimal("2e-11"), relative=str(split_u_error)),
        checked("native_increment_baryon", abs(baryon_residual) <= Decimal("1e-11")*native_scale,
                residual_m3=str(baryon_residual)),
        checked("native_charge_gap_with_separate_split_and_saved_residual", abs(charge_residual) <= Decimal("1e-11")*charge_scale,
                residual_m3=str(charge_residual)),
        checked("literal_branch_saved_energy_separation", abs(energy_residual) <= Decimal("1e-11")*energy_scale,
                residual_eV_m3=str(energy_residual)),
        checked("exact_affine_baryon_and_partner_coefficients", True,
                proof="integer stoichiometry checked in native_affine before per-baryon division"),
    ]
    pointer = ("/prefixes/" if prefix else "/observation_bins/")+str(index)
    return to_json({"index": index, "interval_s": interval, "role": row["role"],
        "status": "PARTIAL_AFFINE_RETURN_WITH_UNRESOLVED_HE_PARTNER",
        "source_H_N_E": source_values["H"], "source_He_electron_N_E": source_values["He"],
        "canonical_source_N_E": {"number_m3": row["injected_number_m3"], "energy_eV_m3": row["injected_energy_eV_m3"]},
        "split_residuals": {"number_m3": epsilon_n, "energy_eV_m3": epsilon_u,
                            "number_relative": split_n_error, "energy_relative": split_u_error,
                            "physical_thermal_count_or_heat": False},
        "saved_response_reference": {"result": {**retained["identity"]["saved_response"], "json_pointer": pointer},
            "arrays": retained["identity"]["saved_response_arrays"], "row_as_saved": copy.deepcopy(row)},
        "event_terms": event_terms, "native_affine_Y": affine,
        "selected_nonthermal_component": selected, "energy_sidecars": sidecars,
        "charge_bookkeeping": {"retention_charge_minus_selected_number_m3_intercept": retained_charge_gap,
            "coefficient_p": "1", "coefficient_d": "0", "actual_partner_pool": None,
            "attribution_residual_m3": epsilon_n,
            "saved_count_residual_exact_lift_m3": saved_count_residual,
            "saved_count_residual_as_stored_m3": row["count_residual_m3"],
            "actual_thermal_electron_increment": None,
            "numeric_residual_reclassified_as_thermal": False},
        "retained_photon_reference": retained_photon_descriptor(retained, row, index),
        "conditional_caloric": caloric, "conditional_closed_He_family": closed_family,
        "claim_identity": {"family_id": FAMILY, "birth_partition_id": PARTITION,
            "native_birth_support_eV": [.1, 10.], "recipient_identity": STATE,
            "selected_response_sha256": RR_RESULT_SHA,
            "producer_revision_alias_does_not_change_event": True},
        "response_cohort_birth_time_support_s": [0., interval[1]],
        "birth_interval_and_response_observation_interval_are_distinct": True,
        "includes_prior_injected_survivors": not prefix,
        "once_only_factor_owners": {"neutral_target_density": "original source, already included",
            "proper729": "original source, already included", "angle_integration": "original source, already included",
            "source_time_factor": "new finite source integration, once", "nb": "new same-state projection, once",
            "eV_J": "per output energy conversion, once", "absolute_volume": None},
        "checks": checklist, "actual_full_native25": None, "actual_external_work": None,
        "actual_temperature_point": None, "actual_He_parameters": {"s": None, "p": None, "d": None},
        "actual_partner_response": None, "actual_residual_HeII_excitation": None,
        "scoped_projected_w_ext": 0, "retained_photon_w_ext_contribution": 0,
        "physical_heating_complete": False, "absolute_worldtube_totals": None})


def validate_preparation_reuse(directory, preparation, preparation_raw, current_code_sha):
    """Accept one exact saved preparation only under a pinned root admission.

    Legacy same-producer use does not enter this path. A changed consumer is
    not permission to repeat or silently trust the preparation calculation.
    """
    old_code_sha = "69e7068573401db41f8c37797b47e455b684979b4094424d2156c05a126bcc81"
    old_preparation_sha = "da5c18c810f47d501648faf77c398f4f0f91c9da9066c7f38c196e989d2eb39f"
    old_arrays_sha = "1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47"

    def local_file(relative):
        require(isinstance(relative, str), "REUSE_UNIT_LOCAL_PATH_REQUIRED")
        part = Path(relative)
        require(not part.is_absolute() and ".." not in part.parts and str(part) == relative,
                "REUSE_UNIT_LOCAL_PATH_REQUIRED")
        path = UNIT / part
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(UNIT),
                "REUSE_REGULAR_UNIT_LOCAL_FILE_REQUIRED")
        return path

    def read_pin(pin, expected_path=None):
        require(isinstance(pin, dict) and set(pin) == {"path", "bytes", "sha256"}, "REUSE_EXACT_FILE_PIN_REQUIRED")
        if expected_path is not None:
            require(pin["path"] == expected_path, "REUSE_PIN_PATH_MISMATCH")
        raw = local_file(pin["path"]).read_bytes()
        require(type(pin["bytes"]) is int and len(raw) == pin["bytes"]
                and hashlib.sha256(raw).hexdigest() == pin["sha256"], "REUSE_FILE_BYTES_OR_SHA_MISMATCH")
        return raw

    budget_raw = (UNIT / "EXECUTION_BUDGET.json").read_bytes()
    budget = json.loads(budget_raw)
    require(budget.get("unit") == UNIT_ID and budget.get("status") == "FROZEN_C4_ADMITTED",
            "PREPARATION_REUSE_REQUIRES_ACTIVE_CURRENT_BUDGET")
    admission_path = local_file(budget.get("preparation_reuse_admission"))
    admission_raw = admission_path.read_bytes()
    require(hashlib.sha256(admission_raw).hexdigest() == budget.get("preparation_reuse_admission_sha256"),
            "PREPARATION_REUSE_ADMISSION_NOT_BUDGET_PINNED")
    admission = json.loads(admission_raw)
    require(admission.get("schema") == "CR_PARENT_EVENT_PREPARATION_REUSE_ADMISSION_V1"
            and admission.get("unit") == UNIT_ID and admission.get("template_only") is False
            and admission.get("decision") == "ADMIT_EXACT_SAVED_PREPARATION_AFTER_DOMAIN_ONLY_REPAIR"
            and admission.get("root_reviewed") is True,
            "EXPLICIT_ROOT_PREPARATION_REUSE_ADMISSION_REQUIRED")
    require(admission.get("change_scope") == "EXACT_FINITE_DECIMAL_HE_BOUNDARY_AND_PREPARATION_REUSE_ONLY"
            and admission.get("fit_projection_unchanged") is True
            and admission.get("tolerances_unchanged") is True
            and admission.get("preparation_reexecuted") is False
            and admission.get("old_science_replay") == 0, "REUSE_SCOPE_OR_REPLAY_NOT_ADMITTED")
    require(admission.get("contract_sha256") == CONTRACT_SHA
            and admission.get("input_manifest_sha256") == MANIFEST_SHA
            and admission.get("source_input_file_count") == 17
            and hashlib.sha256((UNIT / "CONTRACT.json").read_bytes()).hexdigest() == CONTRACT_SHA
            and hashlib.sha256((UNIT / "inputs/INPUT_MANIFEST.json").read_bytes()).hexdigest() == MANIFEST_SHA,
            "REUSE_FROZEN_CONTRACT_OR_INPUT_CHANGED")
    out = admitted_output(os.environ.get("CR_BOUNDED_OUTDIR", ""))
    require(admission.get("allowed_run_ids") == ["controls_v2", "primary_v2"]
            and out.name in admission["allowed_run_ids"], "REUSE_RUN_ID_NOT_EXPLICITLY_ADMITTED")
    expected_directory = str(directory.relative_to(UNIT))
    require(expected_directory == "runs/prepare_v1", "REUSE_ONLY_EXACT_PREPARE_V1")
    old_raw = read_pin(admission["old_producer"], "intake/primary_v1_code/parent_event.py")
    new_raw = read_pin(admission["new_consumer"], "implementation/parent_event.py")
    prepared_raw = read_pin(admission["preparation"], expected_directory + "/PREPARATION.json")
    arrays_raw = read_pin(admission["arrays"], expected_directory + "/ATTRIBUTION_ARRAYS.npz")
    prep_receipt_raw = read_pin(admission["preparation_receipt"], expected_directory + "/RECEIPT.json")
    require(hashlib.sha256(old_raw).hexdigest() == preparation.get("producer_code_sha256") == old_code_sha
            and hashlib.sha256(new_raw).hexdigest() == current_code_sha
            and prepared_raw == preparation_raw and hashlib.sha256(prepared_raw).hexdigest() == old_preparation_sha
            and hashlib.sha256(arrays_raw).hexdigest() == old_arrays_sha,
            "REUSE_EXACT_OLD_AND_NEW_IDENTITIES_REQUIRED")
    prep_receipt = json.loads(prep_receipt_raw)
    require(prep_receipt.get("unit") == UNIT_ID and prep_receipt.get("status") == "completed"
            and prep_receipt.get("worker_exit_code") == 0 and prep_receipt.get("worker_started") is True
            and prep_receipt.get("terminal_debit") is True and prep_receipt.get("cpu_accounting_complete") is True,
            "REUSE_PREPARATION_MUST_HAVE_COMPLETED_ACTUAL_RECEIPT")
    code_raw = read_pin(admission["code_manifest"])
    require(admission["code_manifest"]["path"] == budget.get("code_manifest")
            and hashlib.sha256(code_raw).hexdigest() == budget.get("code_manifest_sha256"),
            "REUSE_CODE_MANIFEST_NOT_ACTIVE_BUDGET_PIN")
    code_manifest = json.loads(code_raw)
    require(code_manifest.get("unit") == UNIT_ID and code_manifest.get("status") == "FROZEN"
            and code_manifest.get("template_only") is False, "REUSE_FROZEN_CODE_MANIFEST_REQUIRED")
    new_entries = [r for r in code_manifest["files"] if r["path"] == "implementation/parent_event.py"]
    require(new_entries == [admission["new_consumer"]], "REUSE_NEW_CONSUMER_NOT_FROZEN_CODE_ENTRY")
    executed = json.loads((out / "EXECUTED_SOURCE_MANIFEST.json").read_bytes())
    entries = [r for r in executed if r["path"] == "implementation/parent_event.py"]
    require(len(entries) == 1 and entries[0].get("snapshot") == "implementation_parent_event.py"
            and entries[0].get("bytes") == len(new_raw) and entries[0].get("sha256") == current_code_sha
            and (out / "EXECUTED_SOURCE/implementation_parent_event.py").read_bytes() == new_raw,
            "REUSE_EXECUTED_CONSUMER_SNAPSHOT_MISMATCH")
    review_raw = read_pin(admission["independent_review"])
    review = json.loads(review_raw)
    require(review.get("schema") == "CR_PARENT_EVENT_EXACT_BOUNDARY_REPAIR_REVIEW_V1"
            and review.get("unit") == UNIT_ID and review.get("verdict") == "PASS_SCOPED_EXACT_BOUNDARY_REPAIR"
            and review.get("blocking_findings") == []
            and review.get("old_producer_sha256") == old_code_sha
            and review.get("new_consumer_sha256") == current_code_sha
            and review.get("preparation_fit_projection_unchanged") is True
            and review.get("tolerances_unchanged") is True, "ACTUAL_INDEPENDENT_REUSE_REVIEW_REQUIRED")
    return {"admission": file_identity(admission_path, str(admission_path.relative_to(UNIT))),
            "active_budget_sha256": hashlib.sha256(budget_raw).hexdigest(),
            "code_manifest": admission["code_manifest"], "independent_review": admission["independent_review"],
            "old_producer_sha256": old_code_sha, "current_consumer_sha256": current_code_sha,
            "preparation_reexecuted": False, "fit_projection_unchanged": True}


def load_preparation(directory):
    directory = Path(directory).resolve()
    require(directory.parent == UNIT / "runs" and directory.is_dir(), "OWNED_PREPARATION_DIRECTORY_REQUIRED")
    preparation_path = directory / "PREPARATION.json"
    preparation_raw = preparation_path.read_bytes()
    preparation = json.loads(preparation_raw)
    require(preparation.get("unit") == UNIT_ID
            and preparation.get("status") == "PASS_SCOPED_MODEL_IDENTIFICATION"
            and all(row["pass"] is True for row in preparation["checks"]),
            "ACTUAL_ACCEPTED_PREPARATION_REQUIRED")
    current_code_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    reuse = None
    if preparation.get("producer_code_sha256") != current_code_sha:
        reuse = validate_preparation_reuse(directory, preparation, preparation_raw, current_code_sha)
    require(preparation["input_identity"]["input_manifest_sha256"] == MANIFEST_SHA,
            "PREPARATION_SOURCE_SCOPE_CHANGED")
    receipt = json.loads((directory / "RECEIPT.json").read_bytes())
    require(receipt.get("unit") == UNIT_ID and receipt.get("status") == "completed"
            and receipt.get("worker_started") is True and receipt.get("worker_exit_code") == 0
            and receipt.get("terminal_debit") is True and receipt.get("cpu_accounting_complete") is True,
            "PREPARATION_RUNTIME_FAILURE_REQUIRES_OWNER_RECONCILIATION")
    descriptor = preparation["artifacts"]["ATTRIBUTION_ARRAYS.npz"]
    raw = (directory / "ATTRIBUTION_ARRAYS.npz").read_bytes()
    require(len(raw) == descriptor["bytes"] and hashlib.sha256(raw).hexdigest() == descriptor["sha256"],
            "PREPARATION_ATTRIBUTION_ARRAY_BYTES_CHANGED")
    identity = file_identity(preparation_path, str(preparation_path.relative_to(UNIT)))
    if reuse is not None:
        identity["explicit_consumer_reuse_admission"] = reuse
    return preparation, raw, identity


@high_precision
def run_primary(out, prepared_directory):
    retained = load_retained_inputs()
    prepared, arrays_raw, preparation_identity = load_preparation(prepared_directory)
    require(prepared["input_identity"] == retained["identity"], "PREPARATION_INPUT_IDENTITY_MISMATCH")
    saved, binding = retained["saved"], actual_binding_context()
    prefixes = [consume_selected_parent_event_window(retained, prepared, row, index, binding=binding)
                for index, row in enumerate(saved["prefixes"])]
    bins = []
    for index, row in enumerate(saved["observation_bins"]):
        bins.append(consume_selected_parent_event_window(retained, prepared, row, index, binding=binding,
            previous_prefix=None if index == 0 else saved["prefixes"][index-1],
            previous_prefix_packet=None if index == 0 else prefixes[index-1]))
    checks = [item for row in prefixes+bins for item in row["checks"]]
    for target_key in ("source_H_N_E", "source_He_electron_N_E"):
        for name in ("number_m3", "energy_eV_m3"):
            total = dsum(D(row[target_key][name]) for row in bins)
            reference = D(prefixes[-1][target_key][name])
            error = own_scale_error(total, reference)
            checks.append(checked("disjoint_birth_bins_sum_"+target_key+"_"+name,
                                  error <= Decimal("1e-11"), relative=str(error)))
    for mode in ("retention", "assimilation"):
        for name in ("Q_J_m3", "thermal_count_m3", "delta_logT"):
            total = dsum(D(row["conditional_caloric"][mode][name]) for row in bins)
            reference = D(prefixes[-1]["conditional_caloric"][mode][name])
            error = own_scale_error(total, reference)
            checks.append(checked("conditional_bins_telescope_"+mode+"_"+name,
                                  error <= Decimal("1e-11"), relative=str(error)))
    registry = []
    if all(item["pass"] for item in checks):
        for row in bins:
            row["component_claims"] = claim_components(row, registry)
    arrays_path = out / "ATTRIBUTION_ARRAYS.npz"
    with arrays_path.open("xb") as stream:
        stream.write(arrays_raw)
    artifacts = {"ATTRIBUTION_ARRAYS.npz": {**prepared["artifacts"]["ATTRIBUTION_ARRAYS.npz"],
                                           "path": str(arrays_path.relative_to(UNIT)),
                                           "copied_from_preparation_without_recalculation": True}}
    passed = all(item["pass"] for item in checks)
    result = {"schema": "CR_PARENT_EVENT_RESULT_V1", "unit": UNIT_ID,
        "status": "PASS_SCOPED_PARENT_EVENT_PARTIAL_RETURN" if passed else "HOLD_SCOPED_PARENT_EVENT_RETURN",
        "input_identity": retained["identity"], "scope": source_scope(),
        "preparation": preparation_identity, "binding_contract": binding,
        "coefficient_identification": prepared["coefficient_identification"],
        "projection_validation": prepared["projection_validation"], "baseline": baseline_inventory(),
        "prefixes": prefixes, "observation_bins": bins,
        "adoption_registry": {"scope": "partial_bookkeeping_only_no_full_consumer_activation",
            "claims": registry, "claim_count": len(registry), "prefixes_additively_adopted": False,
            "aggregate_includes_prior_RR": True, "full_consumer_activation": False,
            "all_response_components_once": passed},
        "acceptance": {"internal_pass": passed, "checks": checks,
            "passed_checks": sum(item["pass"] for item in checks), "total_checks": len(checks),
            "independent_reference": "PENDING", "physical_error_certificate": False,
            "old_reference_or_controls_added_to_new_count": False},
        "unresolved_inputs": {"actual_s": None, "actual_p": None, "actual_d": None,
            "actual_HeII_residual_state": None, "partner_energy": None, "partner_history": None,
            "partner_pool": None, "partner_native_response": None, "actual_proton_work": None,
            "actual_full_physical_native25": None, "full9600_native25": None,
            "absolute_worldtube_totals": None},
        "artifacts": artifacts,
        "resource_receipt_reference": {"path": "RECEIPT.json", "created_by": "owned bounded runner after worker exit",
            "attempt_id": os.environ.get("CR_BOUNDED_ATTEMPT_ID"), "worker_reports_its_own_runtime_receipt": False}}
    write_json_new(out / "RESULT.json", result)
    return 0 if passed else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "primary"))
    parser.add_argument("--out", required=True)
    parser.add_argument("--prepared")
    args = parser.parse_args(argv)
    out = admitted_output(args.out)
    try:
        if args.phase == "prepare":
            require(args.prepared is None, "PREPARE_DOES_NOT_CONSUME_ANOTHER_PREPARATION")
            return run_prepare(out)
        require(args.prepared is not None, "PRIMARY_REQUIRES_ACTUAL_PREPARATION")
        return run_primary(out, args.prepared)
    except Exception as error:
        write_json_new(out / "FAILED.json", {"schema": "CR_PARENT_EVENT_WORKER_FAILURE_V1",
            "unit": UNIT_ID, "phase": args.phase, "status": "FAILED_WITHOUT_SCOPE_EXPANSION",
            "model_identification_status": "MODEL_IDENTIFICATION_UNRESOLVED" if args.phase == "prepare" else None,
            "exception_type": type(error).__name__, "reason": str(error),
            "model_identification_adopted_after_failure": False, "old_source_or_RR_replay": 0,
            "automatic_refit_or_renormalization": False,
            "actual_full_native25": None, "resource_debit_owned_by_runner": True})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
