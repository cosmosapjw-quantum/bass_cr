#!/usr/bin/env python3
"""Independent, bounded Decimal70 reference for the selected HeIII RR consumer.

Preparation does not execute this module. Run only on the root C9 dispatch.
No production or microscopic-provider module is imported. Immutable NPZ/CSV/table
bytes are data; old generator construction, projection, and old reward solves
are never replayed. K0 is the exact stored PR106 HeI matrix, not its old real sum.
"""
from __future__ import annotations

import os
for _thread_var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_thread_var] = "1"

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import resource
import time
import traceback
from decimal import Decimal, localcontext

# This is an independent reference process, not a production process.
_AS_LIMIT = 512 * 1024 * 1024
_soft_as, _hard_as = resource.getrlimit(resource.RLIMIT_AS)
if _hard_as != resource.RLIM_INFINITY and _hard_as < _AS_LIMIT:
    _AS_LIMIT = _hard_as
resource.setrlimit(resource.RLIMIT_AS, (_AS_LIMIT, _AS_LIMIT))

import numpy as np

D = Decimal
ZERO = D(0)
ONE = D(1)
EV_J = D("1.602176634e-19")
ME_KG = D("9.1093837015e-31")
C_MS = D("299792458")
I_HEII = D("54.42")
N_HEIII_CM3 = D("0.01")
OWN_TOL = D("5e-10")
COEFFICIENT_TOL = D("5e-13")
EVENT_TOL = D("5e-13")
INTEGRATED_EVENT_TOL = D("2e-13")
BACKWARD_TOL = 2e-12
BUDGET_CPU_S = 10.0
BUDGET_STOP_CPU_S = 9.8
Z_VALUES = ("2.316", "2.479", "2.649")
CASES = ("chi1.5_R80_N2048", "chi3_R80_N2048")
FRAME = "bath_frame_rest_target"
UNIT = "CR_HEIII_GROUND_RR_ON_HEI_SAVED_CHAIN_V1"
SOURCE_COMMIT = "b11b2e9255f2b10fb5582376412e045bd1e9151c"
THEORY_SHA = "3e5f31d271c32efcd1ee9a1eb23625c2ead0dc0b6c4a78732de34ef4a696ceae"
TABLE_SHA = "a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389"
PROVIDER_SHA = "71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d"
ENERGY_KEYS = ("fast_kinetic", "binding", "radiation", "thermal_kinetic",
               "recoil", "escaped", "external")
SPECIES_KEYS = ("He4:2", "He4:1", "e:fast", "photon")
PHYSICAL_NAMES = (
    "CE_s_probability", "CE_p_probability", "entry_probability", "stop_time_s",
    "CE_s_kinetic_eV", "CE_p_kinetic_eV", "H1_probability", "H1_kinetic_eV",
    "HeI_probability", "HeI_kinetic_eV", "HeII_probability", "HeII_kinetic_eV",
    "bath0", "bath1", "bath2", "bath3", "bath4", "bath5",
)
CONDITIONAL_NAMES = ("CE_s_time_moment", "CE_p_time_moment", "H1_time_moment",
                     "HeI_time_moment", "HeII_time_moment")
RESPONSE_NAMES = ("stored_CE_response", "stored_time_response",
                  "stored_H1_response", "stored_HeI_response")


class InputFailure(ValueError):
    pass


class BudgetStop(RuntimeError):
    pass


def need(condition, message):
    if not condition:
        raise InputFailure(message)


def budget_check():
    if time.process_time() >= BUDGET_STOP_CPU_S:
        raise BudgetStop("C9_REFERENCE_CPU_BUDGET_GUARD")


def dec(value):
    """Exact value of a stored binary64 operand."""
    if isinstance(value, (bool, np.bool_)):
        raise InputFailure("BOOLEAN_NUMERIC_OPERAND")
    value = float(value)
    if not math.isfinite(value):
        raise InputFailure("NONFINITE_NUMERIC_OPERAND")
    return D.from_float(value)


def decimals(values):
    return [D.from_float(float(v)) for v in values]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    with Path(path).open() as stream:
        return json.load(stream)


def write_json_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def record(state, name, passed, **detail):
    item = {"name": name, "pass_scoped": bool(passed), **detail}
    state["checks"].append(item)
    if not passed:
        state["failures"].append(name)


def scalar_check(state, name, actual, expected, tolerance=OWN_TOL):
    if expected is None:
        record(state, name, actual is None, expected=None, actual=actual)
        return
    try:
        observed = dec(actual)
    except (ValueError, TypeError, InputFailure) as exc:
        record(state, name, False, error=str(exc))
        return
    if expected == 0:
        record(state, name, observed == 0, actual=str(observed),
               expected="0", zero_rule="exact zero")
        return
    relative = abs(observed - expected) / abs(expected)
    record(state, name, relative <= tolerance, relative_error=str(relative),
           limit=str(tolerance), expected=str(expected), actual=str(observed))


def compare_column(state, name, actual, reference):
    need(len(actual) == len(reference), "COLUMN_LENGTH:" + name)
    maximum = max((abs(x) for x in reference), default=ZERO)
    error = max((abs(dec(v) - ref) for v, ref in zip(actual, reference)),
                default=ZERO)
    if maximum == 0:
        passed = error == 0
        relative = None
    else:
        relative = error / maximum
        passed = relative <= OWN_TOL
    item = {
        "name": name, "own_infinity_norm": str(maximum),
        "absolute_infinity_error": str(error),
        "relative_error": None if relative is None else str(relative),
        "criterion": str(OWN_TOL), "pass_scoped": bool(passed),
    }
    state["column_comparisons"].append(item)
    if not passed:
        state["failures"].append(name)


def finite_array(archive, name, shape=None):
    need(name in archive, "MISSING_ARRAY:" + name)
    value = np.asarray(archive[name])
    need(value.dtype.kind == "f" and value.dtype.itemsize == 8,
         "BINARY64_ARRAY_REQUIRED:" + name)
    need(np.all(np.isfinite(value)), "NONFINITE_ARRAY:" + name)
    if shape is not None:
        need(value.shape == shape, "ARRAY_SHAPE:" + name)
    return value


def same_array(state, name, a, b):
    record(state, name, a.shape == b.shape and np.array_equal(a, b))


def frozen_inputs(unit, state):
    manifest_path = unit / "inputs/INPUT_MANIFEST.json"
    manifest = read_json(manifest_path)
    expected_paths = set()
    for chi in ("1.5", "3"):
        for upper in ("40", "80"):
            for nominal in ("1024", "2048"):
                case = "chi" + chi + "_R" + upper + "_N" + nominal + ".npz"
                expected_paths.add("inputs/reused/pr104/" + case)
                expected_paths.add("inputs/reused/pr106/" + case)
    expected_paths.update("inputs/reused/c23d/ATOMS_" + z + ".csv" for z in Z_VALUES)
    expected_paths.update(("inputs/reused/c23b/spectral_photo_source.py",
                           "inputs/reused/c23b/data/verner_photo.dat"))
    entries = manifest["files"]
    paths = [entry["path"] for entry in entries]
    need(len(paths) == len(set(paths)), "DUPLICATE_INPUT_MANIFEST_PATH")
    need(expected_paths.issubset(paths), "IMMUTABLE_INPUT_SET_INCOMPLETE")
    observed = []
    for entry in entries:
        path = unit / entry["path"]
        size = path.stat().st_size
        sha = digest(path)
        need(not isinstance(entry["bytes"], bool) and size == entry["bytes"] and
             sha == entry["sha256"], "INPUT_IDENTITY:" + entry["path"])
        observed.append({"path": entry["path"], "bytes": size, "sha256": sha})
    for relative, key in (
        ("FROZEN_CONTRACT.md", "frozen_contract_sha256"),
        ("inputs/CONFIG.json", "config_sha256"),
        ("THEORY_KO.md", "theory_sha256"),
    ):
        need(digest(unit / relative) == manifest[key], "CONTRACT_IDENTITY:" + relative)
    table = unit / "inputs/reused/c23b/data/verner_photo.dat"
    provider = unit / "inputs/reused/c23b/spectral_photo_source.py"
    need(digest(table) == TABLE_SHA, "NATIVE_TABLE_IDENTITY")
    need(digest(provider) == PROVIDER_SHA, "FIXED_PROVIDER_IDENTITY")
    state["input_manifest_sha256"] = digest(manifest_path)
    state["verified_inputs"] = observed
    state["frozen_contract_sha256"] = manifest["frozen_contract_sha256"]
    state["theory_sha256"] = manifest["theory_sha256"]
    need(manifest["theory_sha256"] == THEORY_SHA, "REVIEWED_FINAL_THEORY_IDENTITY")
    authorities = {}
    for entry in manifest["authority_files"]:
        path = unit / entry["path"]
        need(path.stat().st_size == entry["bytes"] and digest(path) == entry["sha256"],
             "AUTHORITY_FILE_IDENTITY:" + entry["path"])
        need(entry["path"] not in authorities, "DUPLICATE_AUTHORITY_FILE")
        authorities[entry["path"]] = entry["sha256"]
    need({"review/R6_THEORY.json", "intake/HEIII_NATIVE25_MAP_R5.json"}.issubset(authorities),
         "R6_NATIVE_MAP_AUTHORITIES_REQUIRED")
    review = read_json(unit / "review/R6_THEORY.json")
    need(review["decision"] == "PASS_SCOPED_AFTER_TARGETED_REPAIR" and
         review["identity"]["reviewed_final_THEORY_sha256"] == THEORY_SHA,
         "R6_DECISION_BINDING")
    config = read_json(unit / "inputs/CONFIG.json")
    fixed_config = {
        "consumer": UNIT, "I_HeII_eV": 54.42, "d_HeII": 1,
        "g_HeII_bound": 2, "g_HeIII_ion": 1, "n_HeIII_cm3": 0.01,
        "electron_mass_kg": 9.1093837015e-31, "c_m_s": 299792458.0,
        "eV_J": 1.602176634e-19, "frame": FRAME, "native_nb_m3": None,
        "operator_baseline": "EXACT_STORED_PR106_HEI_K_DIAG",
        "isotope_assignment": "CONDITIONAL_ELEMENTAL_HE_TO_HE4",
        "component": "ground_spontaneous_only",
    }
    for key, expected in fixed_config.items():
        actual = config.get(key)
        need(key in config and actual == expected and not isinstance(actual, bool),
             "FROZEN_CONFIG:" + key)
    fixed_tolerances = {
        "linear": 2e-12, "partition": 2e-8, "energy": 2e-8,
        "probability": 2e-10, "rare_bound": 5e-10, "grid": 0.005,
        "boundary": 1e-5, "paired_grid": 0.01, "paired_boundary": 1e-5,
        "independent": 5e-10, "event_energy": 5e-13, "coefficient": 5e-13,
        "integrated_event_energy": 2e-13,
    }
    need(all(config["tolerances"].get(k) == v for k, v in fixed_tolerances.items()),
         "FROZEN_ACCEPTANCE_UNCHANGED")
    state["expected_export_qualification"] = {
        "source_contract": UNIT, "source_commit": SOURCE_COMMIT,
        "native_channel": "HeII", "native_threshold_eV": 54.42,
        "native_maximum_eV": 50000.0, "table_sha256": TABLE_SHA,
        "provider_sha256": PROVIDER_SHA, "theory_sha256": THEORY_SHA,
        "isotope_assignment": "CONDITIONAL_ELEMENTAL_HE_TO_HE4",
        "component": "ground_spontaneous_only",
        "mass_model": "stationary_heavy_target_zero_recoil",
        "angular_scope": "SCALAR_ISOTROPIC_ENSEMBLE_ONLY",
        "review_decision": "PASS_SCOPED_AFTER_TARGETED_REPAIR",
        "review_path": "review/R6_THEORY.json",
        "review_sha256": authorities["review/R6_THEORY.json"],
        "native25_map_path": "intake/HEIII_NATIVE25_MAP_R5.json",
        "native25_map_sha256": authorities["intake/HEIII_NATIVE25_MAP_R5.json"],
        "input_manifest_sha256": state["input_manifest_sha256"],
    }
    matches = []
    for line in table.read_text().splitlines():
        tokens = line.split()
        if len(tokens) >= 11 and tokens[0] == "2" and tokens[1] == "1":
            matches.append(tuple(D(s) for s in tokens[2:11]))
    need(len(matches) == 1, "UNIQUE_NATIVE_HEII_ROW")
    row = matches[0]
    need(row == tuple(map(D, ("54.42", "50000", "1.720", "13690", "32.88",
                             "2.963", "0", "0", "0"))), "FROZEN_HEII_ROW")
    state["native_table_row"] = [str(x) for x in row]
    record(state, "immutable_input_and_contract_identity", True)
    return row


def factor_tridiagonal(diagonal, lower, upper):
    """Independent scalar Decimal LU factorization for a tridiagonal Z-matrix."""
    n = len(diagonal)
    need(n > 0 and len(lower) == n - 1 and len(upper) == n - 1,
         "TRIDIAGONAL_DIMENSIONS")
    need(all(x <= 0 for x in lower) and all(x <= 0 for x in upper),
         "TRIDIAGONAL_OFFDIAGONAL_SIGN")
    pivots = list(diagonal)
    multipliers = []
    need(pivots[0] > 0, "NONPOSITIVE_FIRST_PIVOT")
    for i in range(1, n):
        multiplier = lower[i - 1] / pivots[i - 1]
        multipliers.append(multiplier)
        pivots[i] = diagonal[i] - multiplier * upper[i - 1]
        need(pivots[i] > 0, "NONPOSITIVE_PIVOT:" + str(i))
    return pivots, multipliers, upper


def solve_column(factor, rhs, state):
    budget_check()
    pivots, multipliers, upper = factor
    n = len(pivots)
    need(len(rhs) == n, "RHS_DIMENSION")
    work = list(rhs)
    for i in range(1, n):
        work[i] -= multipliers[i - 1] * work[i - 1]
    work[-1] /= pivots[-1]
    for i in range(n - 2, -1, -1):
        work[i] = (work[i] - upper[i] * work[i + 1]) / pivots[i]
    state["reference_rhs_solved"] += 1
    budget_check()
    return work


def coefficient_reference(energy, row):
    threshold, maximum, e0, s0, ya, power, yw, y0, y1 = row
    photon = energy + threshold
    need(energy > 0 and photon <= maximum, "REFERENCE_COEFFICIENT_DOMAIN")
    x = photon / e0 - y0
    y = (x * x + y1 * y1).sqrt()
    polynomial = (x - 1) * (x - 1) + yw * yw
    shape = ((power / 2 - D("5.5")) * y.ln()
             - power * (1 + (y / ya).sqrt()).ln()).exp()
    pi = s0 * polynomial * shape * D("1e-18")
    rest_eV = ME_KG * C_MS * C_MS / EV_J
    rr = pi * photon * photon / (rest_eV * energy)  # d = 1
    speed = D(100) * (2 * energy * EV_J / ME_KG).sqrt()
    hazard = N_HEIII_CM3 * speed * rr
    return {"sigma_PI_HeII_cm2": pi, "sigma_RR_HeII_cm2": rr,
            "v_cm_s": speed, "lambda_HeII": hazard}


def componentwise_backward(state, prefix, diagonal, lower, upper, solution, rhs):
    """Independent componentwise residual of the stored binary64 solve."""
    x = np.asarray(solution, dtype=np.longdouble)
    b = np.asarray(rhs, dtype=np.longdouble)
    d = np.asarray(diagonal, dtype=np.longdouble)
    lo = np.asarray(lower, dtype=np.longdouble)
    up = np.asarray(upper, dtype=np.longdouble)
    if x.ndim == 1:
        x = x[:, None]
    if b.ndim == 1:
        b = b[:, None]
    ax = d[:, None] * x
    scale = abs(d[:, None]) * abs(x) + abs(b)
    ax[1:] += lo[:, None] * x[:-1]
    ax[:-1] += up[:, None] * x[1:]
    scale[1:] += abs(lo[:, None]) * abs(x[:-1])
    scale[:-1] += abs(up[:, None]) * abs(x[1:])
    residual = abs(ax - b)
    need(np.all(residual[scale == 0] == 0), "ZERO_BACKWARD_SCALE")
    ratio = np.divide(residual, scale, out=np.zeros_like(residual), where=scale > 0)
    for column, value in enumerate(np.max(ratio, axis=0)):
        record(state, prefix + ":" + str(column), value <= BACKWARD_TOL,
               scaled_backward_residual=float(value), limit=BACKWARD_TOL)


def dot(weights, vector):
    return sum((a * b for a, b in zip(weights, vector)), ZERO)


def source_reference(unit, case, base, physical, conditional, response, w):
    rows = []
    n = len(w)
    eta = max(w)
    for z in Z_VALUES:
        budget_check()
        with (unit / ("inputs/reused/c23d/ATOMS_" + z + ".csv")).open() as stream:
            atoms = list(csv.DictReader(stream))
        need(len(atoms) == 384, "SOURCE_ATOM_COUNT")
        source = finite_array(base, "source_" + z, (n + 1,))
        need(np.all(source >= 0), "NEGATIVE_STORED_SOURCE_WEIGHT")
        mask = np.asarray(base["active_mask_" + z])
        need(mask.dtype.kind == "b" and mask.shape == (384,), "SOURCE_MASK_HEADER")
        count = [dec(row["pulse_count_cm3"]) for row in atoms]
        nselected = sum(count, ZERO)
        nactive = sum((a for a, active in zip(count, mask) if active), ZERO)
        need(nselected > 0 and nactive > 0, "EMPTY_SELECTED_SOURCE")
        weights = decimals(source[1:])
        p = [dot(weights, column) for column in physical]
        vnew = dot(weights, conditional[4])
        dr = [dot(weights, column) for column in response]
        sw = dot(weights, w)
        ncap, kinetic = p[10], p[11]
        photon = kinetic + I_HEII * ncap
        internal = -I_HEII * ncap
        expected = {
            "P_HeII_RR_active": ncap / nactive,
            "P_HeII_RR_selected": ncap / nselected,
            "conditional_HeII_RR_kinetic_eV": kinetic / ncap if ncap else None,
            "conditional_HeII_RR_photon_eV": photon / ncap if ncap else None,
            "conditional_HeII_RR_time_s": vnew / ncap if ncap else None,
            "HeII_RR_photon_eV_per_selected": photon / nselected,
            "HeII_RR_internal_eV_per_selected": internal / nselected,
            "P_H1_RR_active": p[6] / nactive,
            "P_HeI_RR_active": p[8] / nactive,
            "P_CE_active": (p[0] + p[1]) / nactive,
            "mean_stop_s_active": p[3] / nactive,
            "delta_CE_active": dr[0] / nactive,
            "delta_time_s_active": dr[1] / nactive,
            "delta_H1_RR_active": dr[2] / nactive,
            "delta_HeI_RR_active": dr[3] / nactive,
            "expected_HeII_events_cm3": ncap,
            "expected_HeII_kinetic_eV_cm3": kinetic,
            "source_bound_lower": sw / ((1 + eta) * nactive),
            "source_bound_upper": sw / nactive,
        }
        rows.append({"case": case, "z": z, "expected": expected,
                     "count_m3": ncap * D("1e6"),
                     "kinetic_J_m3": kinetic * D("1e6") * EV_J,
                     "photon_J_m3": photon * D("1e6") * EV_J,
                     "internal_J_m3": internal * D("1e6") * EV_J})
    return rows


def check_integrated_event(state, name, event, count, kinetic, *, nb=None,
                           source_qualification_required=True):
    need(isinstance(event, dict), "EVENT_OBJECT_REQUIRED:" + name)
    scalar_check(state, name + ":count_SI", event.get("integrated_count_m3"), count)
    energy = event.get("integrated_energy_J_m3")
    need(isinstance(energy, dict) and set(energy) == set(ENERGY_KEYS),
         "EXACT_ENERGY_RESERVOIRS:" + name)
    binding = -I_HEII * EV_J * count
    photon = kinetic - binding
    expected_energy = {
        "fast_kinetic": -kinetic, "binding": binding, "radiation": photon,
        "thermal_kinetic": ZERO, "recoil": ZERO, "escaped": ZERO, "external": ZERO,
    }
    for key, expected in expected_energy.items():
        scalar_check(state, name + ":energy:" + key, energy[key], expected)
    observed_energy = [dec(energy[key]) for key in ENERGY_KEYS]
    scale = sum((abs(v) for v in observed_energy), ZERO)
    closure = abs(sum(observed_energy, ZERO))
    record(state, name + ":event_energy_closure",
           closure == 0 if scale == 0 else closure / scale <= INTEGRATED_EVENT_TOL,
           scaled_residual=None if scale == 0 else str(closure / scale),
           criterion=str(INTEGRATED_EVENT_TOL))
    density = event.get("density_delta_m3")
    need(isinstance(density, dict) and set(density) == set(SPECIES_KEYS),
         "EXACT_EVENT_STOICHIOMETRY:" + name)
    for key, expected in (("He4:2", -count), ("He4:1", count),
                          ("e:fast", -count), ("photon", count)):
        scalar_check(state, name + ":density:" + key, density[key], expected)
    record(state, name + ":frame", event.get("frame") == FRAME,
           expected=FRAME, actual=event.get("frame"))
    for key in ("event_rate_m3_s", "exposure_s", "instantaneous_rhs",
                "emission_time_history", "emission_spectrum", "physical_heating_J_m3"):
        record(state, name + ":null:" + key, key in event and event[key] is None)
    for key in ("irreversible_assimilation", "finite_coupled_abundance_update"):
        record(state, name + ":unpromoted:" + key, event.get(key) is False)
    scalar_check(state, name + ":selected_thermal_source_zero",
                 event.get("thermal_source_in_selected_model_J_m3"), ZERO)
    if source_qualification_required:
        q = event.get("source_qualification")
        record(state, name + ":source_qualification_present",
               isinstance(q, dict) and bool(q))
        if isinstance(q, dict):
            for key, expected in state["expected_export_qualification"].items():
                record(state, name + ":qualification:" + key, q.get(key) == expected)
        record(state, name + ":source_id_present",
               isinstance(event.get("source_id"), str) and bool(event["source_id"]))
    port = event.get("retained_photon_port")
    need(isinstance(port, dict), "RETAINED_PORT_REQUIRED:" + name)
    need({"integrated_count_m3", "integrated_energy_J_m3", "count_per_baryon",
          "energy_J_per_baryon"}.issubset(port), "RETAINED_PORT_FIELDS:" + name)
    scalar_check(state, name + ":photon_count_SI",
                 port.get("integrated_count_m3"), count)
    scalar_check(state, name + ":photon_energy_SI",
                 port.get("integrated_energy_J_m3"), photon)
    record(state, name + ":retained_not_external", port.get("native_w_ext_owner") is False)
    template = event.get("per_event_template")
    need(isinstance(template, dict), "PER_EVENT_TEMPLATE_REQUIRED:" + name)
    record(state, name + ":template_stoichiometry",
           template.get("number_per_event") ==
           {"He4:2": -1, "He4:1": 1, "e:fast": -1, "photon": 1})
    for key, expected in (("process", "radiative_recombination"),
                          ("initial_ion", "He4III"), ("final_ion", "He4II"),
                          ("final_state", "1s ground"), ("frame", FRAME)):
        record(state, name + ":template:" + key, template.get(key) == expected)
    scalar_check(state, name + ":template_physical_heating_null",
                 template.get("physical_heating_J_per_event"), None)
    if count:
        scalar_check(state, name + ":template_mean_kinetic",
                     template.get("conditional_mean_kinetic_eV"), kinetic / (EV_J * count))
        record(state, name + ":not_monochromatic_claim",
               template.get("energy_representation") ==
               "MOMENT_EQUIVALENT_NOT_MONOENERGETIC_SPECTRUM")
        per_event = template.get("energy_J_per_event")
        need(isinstance(per_event, dict) and set(per_event) == set(ENERGY_KEYS),
             "PER_EVENT_ENERGY_RESERVOIRS:" + name)
        for key, expected in expected_energy.items():
            scalar_check(state, name + ":per_event_energy:" + key,
                         per_event[key], expected / count)
    else:
        record(state, name + ":zero_count_template_null",
               template.get("conditional_mean_kinetic_eV") is None and
               template.get("energy_J_per_event") is None)
    native = event.get("native25")
    if nb is None:
        record(state, name + ":no_implicit_native_density",
               "native25" in event and native is None)
        scalar_check(state, name + ":null_photon_count_per_baryon",
                     port.get("count_per_baryon"), None)
        scalar_check(state, name + ":null_photon_energy_per_baryon",
                     port.get("energy_J_per_baryon"), None)
    else:
        need(isinstance(native, dict), "NATIVE25_CONTROL_REQUIRED")
        scalar_check(state, name + ":explicit_nb", native.get("nb_m3"), nb)
        delta = native.get("delta")
        need(isinstance(delta, list) and len(delta) == 25, "NATIVE25_LENGTH")
        a = count / nb
        expected_delta = [ZERO] * 25
        expected_delta[11] = a
        expected_delta[12] = -a
        expected_delta[21] = -a
        expected_delta[22] = -kinetic / nb
        for index, expected in enumerate(expected_delta):
            scalar_check(state, name + ":native25:" + str(index),
                         delta[index], expected, COEFFICIENT_TOL)
        scalar_check(state, name + ":photon_count_per_baryon",
                     port.get("count_per_baryon"), a, COEFFICIENT_TOL)
        scalar_check(state, name + ":photon_energy_per_baryon",
                     port.get("energy_J_per_baryon"), photon / nb, COEFFICIENT_TOL)
        ionic_charge_delta = dec(delta[11]) + 2 * dec(delta[12])
        thermal_electron_delta = ionic_charge_delta - dec(delta[21])
        thermal_particle_delta = (2 * dec(delta[11]) + 3 * dec(delta[12])
                                  - dec(delta[21]))
        record(state, name + ":native_thermal_electron_count",
               thermal_electron_delta == 0)
        record(state, name + ":native_thermal_particle_count",
               thermal_particle_delta == 0)


def controls_review(controls_dir, state):
    results = read_json(controls_dir / "CONTROL_RESULTS.json")
    checks = results["checks"]
    need(isinstance(checks, list), "C6_CHECK_LIST")
    by_name = {item["name"]: item for item in checks}
    need(len(by_name) == len(checks), "DUPLICATE_C6_CHECK_NAME")
    for required in ("integrated_duplicate_event_id_rejected",
                     "integrated_cross_frame_rejected"):
        observed = by_name.get(required, {})
        record(state, "C6:" + required, observed.get("pass_scoped") is True,
               source=str(controls_dir / "CONTROL_RESULTS.json"))
    control_path = controls_dir / "NATIVE25_POSITIVE_NB_CONTROL.json"
    control = read_json(control_path)
    need(isinstance(control.get("event"), dict), "C6_POSITIVE_NB_EVENT_MISSING")
    record(state, "C6:positive_nb_control_status",
           control.get("status") in ("PASS", "PASS_SCOPED"),
           observed_status=control.get("status"))
    # Inputs were frozen with the implementer before either C6 or C9 execution.
    check_integrated_event(state, "C6_independent_positive_nb",
                           control["event"], D("1.25e6"),
                           D("2.5e6") * EV_J, nb=D("2.5e6"))
    state["controls_read"] = {
        "control_results_sha256": digest(controls_dir / "CONTROL_RESULTS.json"),
        "native25_control_sha256": digest(control_path),
        "positive_nb_inputs_frozen_before_run": {
            "count_cm3": 1.25, "kinetic_eV_cm3": 2.5, "nb_m3": 2500000.0,
        },
        "note": "Read actual returned C6 event; no production imports or C6 rerun.",
    }


def case_reference(unit, primary_dir, out_dir, case, table_row, state):
    budget_check()
    paths = {
        "pr104": unit / ("inputs/reused/pr104/" + case + ".npz"),
        "pr106": unit / ("inputs/reused/pr106/" + case + ".npz"),
        "production": primary_dir / (case + ".npz"),
    }
    with np.load(paths["pr104"], allow_pickle=False) as base, \
            np.load(paths["pr106"], allow_pickle=False) as old, \
            np.load(paths["production"], allow_pickle=False) as new:
        d0f = finite_array(old, "K_diag")
        n = len(d0f)
        need(d0f.shape == (n,), "OLD_DIAGONAL_VECTOR")
        lowerf = finite_array(old, "K_lower", (n - 1,))
        upperf = finite_array(old, "K_upper", (n - 1,))
        energies_full = finite_array(base, "E_eV", (n + 1,))
        energyf = energies_full[1:]
        old_rhs = finite_array(old, "rhs_physical16", (n, 16))
        same_array(state, case + ":old_grid", finite_array(old, "E_eV"), energies_full)
        same_array(state, case + ":new_grid", finite_array(new, "E_eV"), energies_full)
        same_array(state, case + ":new_exact_baseline",
                   finite_array(new, "K_HeI_diag", (n,)), d0f)
        same_array(state, case + ":new_lower", finite_array(new, "K_lower"), lowerf)
        same_array(state, case + ":new_upper", finite_array(new, "K_upper"), upperf)
        same_array(state, case + ":immutable_first6",
                   old_rhs[:, :6], finite_array(base, "rhs_first6", (n, 6)))
        same_array(state, case + ":immutable_bath6",
                   old_rhs[:, 10:16], finite_array(base, "rhs_bath6", (n, 6)))
        lamf = finite_array(new, "lambda_HeII", (n,))
        need(np.all(lamf > 0), "POSITIVE_NEW_HAZARD")
        need(np.all(energyf > 0) and np.all(energyf + 54.42 <= 50000),
             "NEW_KINETIC_DOMAIN")
        same_array(state, case + ":H1_hazard_reuse",
                   finite_array(new, "lambda_H1"), finite_array(old, "lambda_H1"))
        same_array(state, case + ":HeI_hazard_reuse",
                   finite_array(new, "lambda_HeI"), finite_array(old, "lambda_He"))
        diagf = finite_array(new, "K_diag", (n,))
        same_array(state, case + ":rounded_K1_is_K0_plus_new", diagf, d0f + lamf)
        d0 = decimals(d0f)
        lower = decimals(lowerf)
        upper = decimals(upperf)
        energy = decimals(energyf)
        lam = decimals(lamf)
        diagonal = [a + b for a, b in zip(d0, lam)]
        state["scientific_work_started"] = True
        factor = factor_tridiagonal(diagonal, lower, upper)
        samples = sorted({0, n // 4, n // 2, 3 * n // 4, n - 1})
        for index in samples:
            independent = coefficient_reference(energy[index], table_row)
            for field, expected in independent.items():
                observed = finite_array(new, field, (n,))[index]
                scalar_check(state, case + ":coefficient:" + field + ":" + str(index),
                             observed, expected, COEFFICIENT_TOL)
        state["coefficient_sample_indices"][case] = samples
        rhs = [decimals(old_rhs[:, j]) for j in range(10)]
        rhs += [lam, [a * e for a, e in zip(lam, energy)]]
        rhs += [decimals(old_rhs[:, j]) for j in range(10, 16)]
        physical = [solve_column(factor, column, state) for column in rhs]
        conditional = [solve_column(factor, physical[j], state)
                       for j in (0, 1, 6, 8, 10)]
        old_ce = [a + b for a, b in zip(decimals(finite_array(old, "u_s", (n,))),
                                       decimals(finite_array(old, "u_p", (n,))))]
        stored_columns = [old_ce] + [
            decimals(finite_array(old, key, (n,))) for key in ("t", "p_H1", "p_He")
        ]
        response_rhs = [[-a * h for a, h in zip(lam, stored)]
                        for stored in stored_columns]
        response = [solve_column(factor, column, state) for column in response_rhs]
        old_factor = factor_tridiagonal(d0, lower, upper)
        w = solve_column(old_factor, lam, state)
        x = finite_array(new, "solution_physical18", (n, 18))
        v = finite_array(new, "solution_conditional5", (n, 5))
        response_stored = finite_array(new, "solution_response4", (n, 4))
        w_stored = finite_array(new, "w", (n,))
        for j, label in enumerate(PHYSICAL_NAMES):
            compare_column(state, case + ":physical:" + label, x[:, j], physical[j])
        for j, label in enumerate(CONDITIONAL_NAMES):
            compare_column(state, case + ":conditional:" + label, v[:, j], conditional[j])
        for j, label in enumerate(RESPONSE_NAMES):
            compare_column(state, case + ":response:" + label,
                           response_stored[:, j], response[j])
        compare_column(state, case + ":diagnostic:w", w_stored, w)
        saved_rhs = finite_array(new, "rhs_physical18", (n, 18))
        same_array(state, case + ":new_rhs_old_first10", saved_rhs[:, :10], old_rhs[:, :10])
        same_array(state, case + ":new_rhs_bath6", saved_rhs[:, 12:], old_rhs[:, 10:])
        same_array(state, case + ":new_count_rhs", saved_rhs[:, 10], lamf)
        same_array(state, case + ":new_kinetic_rhs", saved_rhs[:, 11], lamf * energyf)
        conditional_rhs = finite_array(new, "rhs_conditional5", (n, 5))
        same_array(state, case + ":production_conditional_rhs",
                   conditional_rhs, x[:, [0, 1, 6, 8, 10]])
        stable_rhs = finite_array(new, "rhs_response4", (n, 4))
        stable_float_expected = -lamf[:, None] * np.column_stack(
            (finite_array(old, "u_s") + finite_array(old, "u_p"),
             finite_array(old, "t"), finite_array(old, "p_H1"), finite_array(old, "p_He")))
        same_array(state, case + ":production_stored_response_rhs",
                   stable_rhs, stable_float_expected)
        same_array(state, case + ":w_rhs", finite_array(new, "rhs_w", (n,)), lamf)
        for name, actual, expected in (
            ("p_H1", finite_array(new, "p_H1"), x[:, 6]),
            ("r_H1", finite_array(new, "r_H1"), x[:, 7]),
            ("v_H1", finite_array(new, "v_H1"), v[:, 2]),
            ("p_HeI", finite_array(new, "p_HeI"), x[:, 8]),
            ("r_HeI", finite_array(new, "r_HeI"), x[:, 9]),
            ("v_HeI", finite_array(new, "v_HeI"), v[:, 3]),
            ("p_HeII", finite_array(new, "p_HeII"), x[:, 10]),
            ("r_HeII", finite_array(new, "r_HeII"), x[:, 11]),
            ("v_HeII", finite_array(new, "v_HeII"), v[:, 4]),
        ):
            same_array(state, case + ":alias:" + name, actual, expected)
        componentwise_backward(state, case + ":backward_physical",
                               diagf, lowerf, upperf, x, saved_rhs)
        componentwise_backward(state, case + ":backward_conditional",
                               diagf, lowerf, upperf, v, conditional_rhs)
        componentwise_backward(state, case + ":backward_response",
                               diagf, lowerf, upperf, response_stored, stable_rhs)
        componentwise_backward(state, case + ":backward_w",
                               d0f, lowerf, upperf, w_stored, lamf)
        eta = max(w)
        lower_bound = [q / (1 + eta) for q in w]
        bound_error = max(
            (max((lo - p) / lo if lo else ZERO,
                 (p - hi) / hi if hi else ZERO, ZERO)
             for lo, p, hi in zip(lower_bound, physical[10], w)), default=ZERO)
        record(state, case + ":independent_single_hazard_bound",
               bound_error <= OWN_TOL, relative_violation=str(bound_error))
        record(state, case + ":independent_stable_signs",
               all(value <= 0 for column in response for value in column))
        references = physical + conditional + response + [w]
        names = list(PHYSICAL_NAMES) + list(CONDITIONAL_NAMES) + list(RESPONSE_NAMES) + ["w"]
        dense_path = out_dir / (case + "_DECIMAL70.csv")
        with dense_path.open("x", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["row_index", "E_eV_binary64"] + names)
            for index in range(n):
                writer.writerow([index, format(float(energyf[index]), ".17g")] +
                                [str(column[index]) for column in references])
        state["reference_artifacts"].append(
            {"path": dense_path.name, "bytes": dense_path.stat().st_size,
             "sha256": digest(dense_path), "columns": 28, "rows": n})
        state["reviewed_cases"].append({
            "case": case, "actual_n": n, "nominal_n": 2048, "R": 80,
            "primary_sha256": digest(paths["production"]),
            "old_PR106_sha256": digest(paths["pr106"]),
            "old_PR104_sha256": digest(paths["pr104"]),
            "new_reference_RHS": 28,
        })
        return source_reference(unit, case, base, physical, conditional, response, w)


def canonical_z(value):
    if isinstance(value, bool):
        raise InputFailure("BOOLEAN_REDSHIFT")
    return format(float(value), ".3f")


def index_rows(rows, label):
    need(isinstance(rows, list) and len(rows) == 24, label + ":EXPECTED_24")
    indexed = {}
    for row in rows:
        key = (str(row["case"]), canonical_z(row["z"]))
        need(key not in indexed, label + ":DUPLICATE_CASE_Z")
        indexed[key] = row
    expected = {
        ("chi" + chi + "_R" + r + "_N" + n, z)
        for chi in ("1.5", "3") for r in ("40", "80")
        for n in ("1024", "2048") for z in Z_VALUES
    }
    need(set(indexed) == expected, label + ":CASE_Z_SET")
    return indexed


def run(args, state):
    unit = args.unit_dir.resolve()
    primary = args.primary_dir.resolve()
    out = args.out_dir.resolve()
    table = frozen_inputs(unit, state)
    weighted_path = primary / "SOURCE_WEIGHTED_RESULTS.json"
    export_path = primary / "INTEGRATED_EVENT_EXPORTS.json"
    weighted = index_rows(read_json(weighted_path)["rows"], "SOURCE_WEIGHTED_RESULTS")
    events = index_rows(read_json(export_path)["events"], "INTEGRATED_EVENT_EXPORTS")
    ids = [event.get("canonical_event_id") for event in events.values()]
    record(state, "integrated_event_id_uniqueness",
           all(isinstance(v, str) and v for v in ids) and len(set(ids)) == 24)
    record(state, "integrated_event_frame_set",
           {event.get("frame") for event in events.values()} == {FRAME})
    state["production_source_rows_sha256"] = digest(weighted_path)
    state["production_event_exports_sha256"] = digest(export_path)
    with localcontext() as context:
        context.prec = 70
        controls_review(args.controls_dir.resolve(), state)
        independent_sources = []
        for case in CASES:
            independent_sources.extend(case_reference(unit, primary, out, case, table, state))
        need(state["reference_rhs_solved"] == 56, "REFERENCE_RHS_COUNT")
        need(len(state["column_comparisons"]) == 56, "OWN_COLUMN_COMPARISON_COUNT")
        for ref in independent_sources:
            case, z = ref["case"], ref["z"]
            row = weighted[(case, z)]
            for key, expected in ref["expected"].items():
                scalar_check(state, case + ":" + z + ":source:" + key,
                             row.get(key), expected)
            check_integrated_event(state, case + ":" + z + ":export",
                                   events[(case, z)], ref["count_m3"],
                                   ref["kinetic_J_m3"], nb=None)
            state["independent_source_rows"].append({
                "case": case, "z": z,
                "expected": {k: None if v is None else str(v)
                             for k, v in ref["expected"].items()},
                "integrated_count_m3": str(ref["count_m3"]),
                "integrated_kinetic_J_m3": str(ref["kinetic_J_m3"]),
                "integrated_photon_J_m3": str(ref["photon_J_m3"]),
                "integrated_internal_J_m3": str(ref["internal_J_m3"]),
            })
        budget_check()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit-dir", type=Path, required=True)
    parser.add_argument("--primary-dir", type=Path, required=True)
    parser.add_argument("--controls-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.out_dir / "C9_INDEPENDENT_RESULT.json"
    need(not result_path.exists(), "C9_RESULT_ALREADY_EXISTS")
    need(not any(args.out_dir.glob("*_DECIMAL70.csv")), "C9_DENSE_REFERENCE_ALREADY_EXISTS")
    started_wall = time.monotonic()
    state = {
        "schema": "CR_HEIII_C9_INDEPENDENT_REFERENCE_V1",
        "status": "RUNNING",
        "decision": "NOT_ADMITTED",
        "precision_decimal_digits": 70,
        "baseline": "EXACT_STORED_PR106_HEI_K_DIAG_PLUS_NEW_DECIMAL_HAZARD",
        "old_RHS": "exact stored binary64 operands",
        "new_products": "exact Decimal-context products",
        "conditional_RHS": "own independent Decimal probabilities",
        "stable_RHS": "exact products with stored HeI CE/time/H1/HeI columns",
        "science_scope": "two finest cases, all56 own-column references and six source rows",
        "scientific_work_started": False,
        "reference_rhs_solved": 0,
        "checks": [], "failures": [], "column_comparisons": [],
        "coefficient_sample_indices": {}, "reviewed_cases": [],
        "reference_artifacts": [], "independent_source_rows": [],
        "production_imports": 0, "provider_imports": 0,
        "old_reward_solves": 0, "old_generator_replays": 0,
        "old_projection_replays": 0, "old_quadrature_replays": 0,
        "C9_full_admission": "REQUIRES_FINAL_INDEPENDENT_CODE_AND_OUTPUT_REVIEW",
        "global_physical_error_bound": None,
        "N6_N7_changed": False, "physical_heating_completion": False,
        "resource_contract": {
            "CPU_cap_s": BUDGET_CPU_S, "internal_guard_s": BUDGET_STOP_CPU_S,
            "address_space_bytes": _AS_LIMIT, "native_threads": 1,
        },
        "executed_checker_sha256": digest(__file__),
        "executed_checker_path": str(Path(__file__).resolve()),
    }
    exit_code = 1
    try:
        run(args, state)
        state["status"] = "COMPLETED"
        state["decision"] = ("PASS_SCOPED_INDEPENDENT_REFERENCE"
                             if not state["failures"] else "FAIL_SCOPED")
        exit_code = 0 if not state["failures"] else 1
    except Exception as exc:
        state["status"] = "ERROR"
        state["decision"] = "NOT_ADMITTED"
        state["error_type"] = type(exc).__name__
        state["error"] = str(exc)
        state["traceback"] = traceback.format_exc()
    state["process_cpu_s"] = time.process_time()
    state["wall_s_since_main"] = time.monotonic() - started_wall
    if state["process_cpu_s"] > BUDGET_CPU_S:
        state["failures"].append("C9_CPU_CAP_EXCEEDED")
        state["decision"] = "NOT_ADMITTED"
        exit_code = 1
    write_json_new(result_path, state)
    print(json.dumps({
        "status": state["status"], "decision": state["decision"],
        "reference_rhs_solved": state["reference_rhs_solved"],
        "own_columns_compared": len(state["column_comparisons"]),
        "source_rows_compared": len(state["independent_source_rows"]),
        "failure_count": len(state["failures"]),
        "process_cpu_s": state["process_cpu_s"],
        "result": str(result_path),
    }, allow_nan=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

