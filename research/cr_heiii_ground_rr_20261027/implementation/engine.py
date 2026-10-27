"""Add one source-qualified HeIII ground-RR hazard to exact stored HeI chains.

Every old and new reward uses one shared K1.  No inherited rate generator,
source projection, quadrature, completed primary solve or ODE is replayed.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import solve_banded

import export_adapter as export


class InputError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise InputError(message)


def writej(path, obj):
    with Path(path).open("x") as stream:
        json.dump(obj, stream, indent=2, allow_nan=False)
        stream.write("\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_config(c):
    expected = {
        "schema": "CR_HEIII_RR_ON_SAVED_HEI_V1",
        "consumer": export.UNIT,
        "I_HeII_eV": 54.42, "g_HeII_bound": 2, "g_HeIII_ion": 1,
        "d_HeII": 1, "n_HeIII_cm3": 0.01,
        "I_HeI_eV": 24.59, "I_eV": 13.6, "n_HII_cm3": 0.1,
        "n_HeII_cm3": 0.02, "ne_cm3": 0.14,
        "electron_mass_kg": 9.1093837015e-31, "eV_J": 1.602176634e-19,
        "c_m_s": 299792458.0, "PI_maximum_eV": 50000.0,
        "T_K": 10000.0, "theta_eV": 0.8617333262145178,
        "gap_eV": 10.20435, "finite_mass": False,
        "component": "ground_spontaneous_only",
        "operator_baseline": "EXACT_STORED_PR106_HEI_K_DIAG",
        "isotope_assignment": "CONDITIONAL_ELEMENTAL_HE_TO_HE4",
        "source_residual_state_resolution": "CONDITIONAL_SMOOTH_GROUND_CHANNEL_MODEL",
        "frame": export.FRAME, "native_nb_m3": None,
        "planned_primary_cases": 8, "planned_primary_rhs": 224,
        "planned_source_rows": 24, "planned_independent_rhs": 56,
    }
    for key, value in expected.items():
        need(key in c and c[key] == value, "FROZEN_HEIII_CONTRACT_MISMATCH:" + key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            need(not isinstance(c[key], bool), "BOOLEAN_PHYSICAL_INPUT:" + key)
    need(c["d_HeII"] == 2 * c["g_HeIII_ion"] / c["g_HeII_bound"], "ELECTRONIC_WEIGHTS")
    need(c["source_z"] == ["2.316", "2.479", "2.649"]
         and c["chi"] == [1.5, 3] and c["R"] == [40, 80]
         and c["grid_N"] == [1024, 2048], "FROZEN_CASE_SOURCE_SET")
    need(c["bath_labels"] == ["EE", "H1+", "He4+", "He4++", "H1neutral", "He4neutral"],
         "FROZEN_BATH_ORDER")
    tolerances = {"linear": 2e-12, "partition": 2e-8, "energy": 2e-8,
                  "probability": 2e-10, "rare_bound": 5e-10,
                  "grid": .005, "boundary": 1e-5, "paired_grid": .01,
                  "paired_boundary": 1e-5, "independent": 5e-10,
                  "coefficient": 5e-13, "event_energy": 5e-13,
                  "integrated_event_energy": 2e-13}
    need(c["tolerances"] == tolerances, "FROZEN_ACCEPTANCE_MISMATCH")


def verify(unit):
    c = json.loads((unit / "inputs/CONFIG.json").read_text())
    m = json.loads((unit / "inputs/INPUT_MANIFEST.json").read_text())
    validate_config(c)
    executed = Path(__file__).resolve().parent
    for filename, current in (("CONFIG.json", unit / "inputs/CONFIG.json"),
                              ("INPUT_MANIFEST.json", unit / "inputs/INPUT_MANIFEST.json"),
                              ("FROZEN_CONTRACT.md", unit / "FROZEN_CONTRACT.md"),
                              ("THEORY_KO.md", unit / "THEORY_KO.md")):
        if (executed / filename).is_file():
            need(digest(executed / filename) == digest(current),
                 "EXECUTED_SNAPSHOT_IDENTITY:" + filename)
    for rel, key in (("FROZEN_CONTRACT.md", "frozen_contract_sha256"),
                     ("THEORY_KO.md", "theory_sha256"),
                     ("inputs/CONFIG.json", "config_sha256")):
        need(digest(unit / rel) == m[key], "FROZEN_IDENTITY:" + rel)
    need(m["theory_sha256"] == export.THEORY_SHA, "REVIEWED_THEORY_IDENTITY")
    need(len(m["files"]) == 21 and len({row["path"] for row in m["files"]}) == 21,
         "EXACT_21_INPUT_CLOSURE_REQUIRED")
    for row in m["files"] + m["authority_files"]:
        p = (unit / row["path"]).resolve()
        need(p.is_relative_to(unit.resolve()), "MANIFEST_PATH_ESCAPE")
        raw = p.read_bytes()
        need(len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"],
             "INPUT_IDENTITY:" + row["path"])
    required = {"review/R6_THEORY.json", "intake/HEIII_NATIVE25_MAP_R5.json"}
    need(required.issubset({row["path"] for row in m["authority_files"]}), "AUTHORITY_CLOSURE")
    review = json.loads((unit / "review/R6_THEORY.json").read_text())
    export.qualification(c, m, review, digest(unit / "inputs/INPUT_MANIFEST.json"))
    return c


def source_qualification(unit, c):
    return export.qualification(c,
        json.loads((unit / "inputs/INPUT_MANIFEST.json").read_text()),
        json.loads((unit / "review/R6_THEORY.json").read_text()),
        digest(unit / "inputs/INPUT_MANIFEST.json"))


def provider(unit):
    path = unit / "inputs/reused/c23b/spectral_photo_source.py"
    need(digest(path) == export.PROVIDER_SHA
         and digest(path.parent / "data/verner_photo.dat") == export.TABLE_SHA,
         "NATIVE_POINT_PROVIDER_BYTES")
    spec = importlib.util.spec_from_file_location("heiii_exact_c23b", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    # Only a table constructor and point evaluations are admitted.
    return module.Verner96.from_table("HeII", path.parent / "data")


def coefficients(energy, c, atom, density):
    need(not isinstance(density, bool) and isinstance(density, (int, float))
         and math.isfinite(density) and density >= 0, "FINITE_EXPLICIT_TARGET_DENSITY_REQUIRED")
    if isinstance(energy, (list, tuple)):
        need(not any(isinstance(value, (bool, np.bool_)) for value in energy),
             "REAL_NONBOOLEAN_ENERGY_REQUIRED")
    raw = np.asarray(energy)
    need(raw.dtype.kind in "fiu" and raw.dtype.kind != "b", "REAL_NONBOOLEAN_ENERGY_REQUIRED")
    energy = np.atleast_1d(np.asarray(energy, dtype=float))
    need(energy.size > 0 and energy.ndim == 1 and np.all(np.isfinite(energy))
         and np.all(energy > 0), "POSITIVE_FINITE_KINETIC_ENERGY_REQUIRED")
    need(c["I_HeII_eV"] == 54.42 and c["d_HeII"] == 1
         and c["g_HeII_bound"] == 2 and c["g_HeIII_ion"] == 1
         and atom.channel == "HeII" and atom.threshold_eV == 54.42
         and atom.maximum_eV == 50000.0, "NATIVE_HEII_GROUND_SOURCE_IDENTITY")
    photon = energy + c["I_HeII_eV"]
    need(np.all(photon >= atom.threshold_eV) and np.all(photon <= atom.maximum_eV),
         "FINITE_PI_SUPPORT_REQUIRED")
    pi = np.array([atom.sigma_cm2(float(v)) for v in photon])
    mec2 = c["electron_mass_kg"] * c["c_m_s"] ** 2 / c["eV_J"]
    sigma = pi * photon ** 2 / (c["d_HeII"] * mec2 * energy)
    speed = 100 * np.sqrt(2 * energy * c["eV_J"] / c["electron_mass_kg"])
    lam = density * speed * sigma
    need(np.all(np.isfinite(pi)) and np.all(pi > 0) and np.all(np.isfinite(speed))
         and np.all(np.isfinite(lam)) and np.all(lam >= 0)
         and np.all(np.isfinite(sigma)) and np.all(sigma > 0), "INVALID_HEII_RR_COEFFICIENT")
    return {"sigma_PI_HeII_cm2": pi, "sigma_RR_HeII_cm2": sigma,
            "v_cm_s": speed, "lambda_HeII": lam}


def apply(d, lower, upper, x):
    y = d[:, None] * x if x.ndim == 2 else d * x
    if x.ndim == 2:
        y[1:] += lower[:, None] * x[:-1]
        y[:-1] += upper[:, None] * x[1:]
    else:
        y[1:] += lower * x[:-1]
        y[:-1] += upper * x[1:]
    return y


def positive_pivots(d, lower, upper):
    need(d.ndim == lower.ndim == upper.ndim == 1 and len(d) > 0
         and len(lower) == len(upper) == len(d) - 1, "TRIDIAGONAL_SHAPE")
    need(np.all(np.isfinite(d)) and np.all(d > 0)
         and np.all(np.isfinite(lower)) and np.all(lower <= 0)
         and np.all(np.isfinite(upper)) and np.all(upper <= 0), "VALID_Z_MATRIX_REQUIRED")
    pivot = float(d[0])
    minimum = pivot
    for index in range(1, len(d)):
        pivot = float(d[index]) - float(lower[index - 1]) / pivot * float(upper[index - 1])
        need(math.isfinite(pivot) and pivot > 0, "STRICT_POSITIVE_THOMAS_PIVOT_REQUIRED")
        minimum = min(minimum, pivot)
    return minimum


def solve(d, lower, upper, rhs):
    positive_pivots(d, lower, upper)
    need(rhs.ndim in (1, 2) and rhs.shape[0] == len(d)
         and np.all(np.isfinite(rhs)), "FINITE_COMPATIBLE_RHS_REQUIRED")
    ab = np.zeros((3, len(d)))
    ab[0, 1:], ab[1], ab[2, :-1] = upper, d, lower
    solution = solve_banded((1, 1), ab, rhs, check_finite=False)
    need(np.all(np.isfinite(solution)), "NONFINITE_SOLUTION")
    residual = abs(apply(d, lower, upper, solution) - rhs)
    denominator = apply(abs(d), abs(lower), abs(upper), abs(solution)) + abs(rhs)
    need(np.all(residual[denominator == 0] == 0), "ZERO_RESIDUAL_SCALE")
    scaled = np.divide(residual, denominator, out=np.zeros_like(residual), where=denominator > 0)
    return solution, np.atleast_1d(scaled.max(axis=0)).tolist()


def atoms(unit, z):
    with (unit / f"inputs/reused/c23d/ATOMS_{z}.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    need(len(rows) == 384, "EXACT_SAVED_384_ATOMS_REQUIRED")
    values = {key: np.array([float(row[key]) for row in rows])
              for key in rows[0] if key != "channel"}
    need(np.all((values["W_eV"] > 0) & (values["W_eV"] < 10))
         and np.all(values["pulse_count_cm3"] > 0)
         and all(np.all(np.isfinite(v)) for v in values.values()), "SAVED_SOURCE_DOMAIN")
    return values


def consume(base, old, c, atom, count):
    for key in ("E_eV", "K_lower", "K_upper"):
        need(np.array_equal(base[key], old[key]), "PARENT_IDENTITY:" + key)
    need(np.array_equal(old["rhs_physical16"][:, :6], base["rhs_first6"]), "FIRST6_EXACT_REUSE")
    need(np.array_equal(old["rhs_physical16"][:, 10:16], base["rhs_bath6"]), "BATH6_EXACT_REUSE")
    need(np.array_equal(old["rhs_physical16"][:, 6], old["lambda_H1"])
         and np.array_equal(old["rhs_physical16"][:, 8], old["lambda_He"]), "INHERITED_RR_HAZARDS")
    energy = base["E_eV"][1:]
    d0, lower, upper = old["K_diag"], old["K_lower"], old["K_upper"]
    need(len(energy) == len(d0) and old["rhs_physical16"].shape == (len(d0), 16),
         "ACTUAL_ACTIVE_GRID_SHAPE")
    coef = coefficients(energy, c, atom, c["n_HeIII_cm3"])
    lam = coef["lambda_HeII"]
    d = d0 + lam
    rhs = np.column_stack((old["rhs_physical16"][:, :10], lam, lam * energy,
                           old["rhs_physical16"][:, 10:16]))
    count(18)
    physical, residuals = solve(d, lower, upper, rhs)
    conditional_rhs = physical[:, [0, 1, 6, 8, 10]]
    count(5)
    conditional, conditional_residuals = solve(d, lower, upper, conditional_rhs)
    old_responses = np.column_stack((old["u_s"] + old["u_p"], old["t"], old["p_H1"], old["p_He"]))
    need(np.all(old_responses >= 0) and np.all(np.isfinite(old_responses)), "NONNEGATIVE_STORED_RESPONSE_COLUMNS")
    response_rhs = -lam[:, None] * old_responses
    count(4)
    responses, response_residuals = solve(d, lower, upper, response_rhs)
    count(1)
    w, w_residuals = solve(d0, lower, upper, lam)
    pnew = physical[:, 10]
    need(np.all(w >= 0) and np.all(pnew >= 0), "NONNEGATIVE_NEW_CAPTURE")
    if np.any(lam > 0):
        need(np.all(w > 0) and np.all(pnew > 0), "STRICT_NEW_CAPTURE_POSITIVITY")
    eta = float(w.max())
    bound_lower = w / (1 + eta)
    upper_violation = float(np.divide(np.maximum(pnew - w, 0), w,
                            out=np.zeros_like(w), where=w > 0).max())
    lower_violation = float(np.divide(np.maximum(bound_lower - pnew, 0), bound_lower,
                            out=np.zeros_like(w), where=bound_lower > 0).max())
    photons, internals = [], []
    for j, ionization in ((6, c["I_eV"]), (8, c["I_HeI_eV"]), (10, c["I_HeII_eV"])):
        photons.append(physical[:, j + 1] + ionization * physical[:, j])
        internals.append(-ionization * physical[:, j])
    partition = physical[:, [0, 1, 2, 6, 8, 10]].sum(axis=1)
    ce = physical[:, 0] + physical[:, 1]
    ce_in = physical[:, 4] + physical[:, 5]
    terms = np.column_stack((physical[:, 12:18], base["E_eV"][0] * physical[:, 2],
             ce_in - c["gap_eV"] * ce, c["gap_eV"] * ce,
             photons[0], internals[0], photons[1], internals[1], photons[2], internals[2]))
    energy_error = abs(terms.sum(axis=1) - energy) / (abs(terms).sum(axis=1) + energy)
    event_errors = []
    for k, j in enumerate((7, 9, 11)):
        residual = abs(photons[k] + internals[k] - physical[:, j])
        scale = abs(photons[k]) + abs(internals[k]) + abs(physical[:, j])
        event_errors.append(float(np.divide(residual, scale, out=np.zeros_like(scale), where=scale > 0).max()))
    addition_loss = (d.astype(np.longdouble) - d0.astype(np.longdouble)) - lam.astype(np.longdouble)
    loss_fraction = np.divide(abs(addition_loss), lam.astype(np.longdouble),
                             out=np.zeros_like(addition_loss), where=lam > 0)
    metrics = {
        "rhs_scaled_backward_residuals": residuals + conditional_residuals + response_residuals + w_residuals,
        "partition_maxabs": float(abs(partition - 1).max()),
        "energy_scaled_residual": float(energy_error.max()),
        "RR_own_energy_residuals": dict(zip(("H1", "HeI", "HeII"), event_errors)),
        "probability_min": float(physical[:, [0, 1, 2, 6, 8, 10]].min()),
        "probability_max": float(physical[:, [0, 1, 2, 6, 8, 10]].max()),
        "stored_HeI_positive_pivot_min": positive_pivots(d0, lower, upper),
        "new_positive_pivot_min": positive_pivots(d, lower, upper),
        "eta": eta, "rare_upper_relative_violation": upper_violation,
        "rare_lower_relative_violation": lower_violation,
        "stable_response_maxima": dict(zip(("CE", "time", "H1_RR", "HeI_RR"), responses.max(axis=0).tolist())),
        "diagonal_addition_lost_rate_max_abs": float(abs(addition_loss).max()),
        "diagonal_addition_loss_relative_to_HeII_rate_max": float(loss_fraction.max()),
        "addition_loss_diagnostic_precision_bits": int(np.finfo(np.longdouble).nmant + 1),
        "independent_intended_sum": "Decimal.from_float(stored_HeI_diag)+Decimal.from_float(lambda_HeII)",
        "baseline": "EXACT_STORED_PR106_HEI_K_DIAG", "old_offdiagonal_exact_reuse": True,
        "old_generator_replay": 0, "old_source_projection_replay": 0,
        "physical_columns": 18, "conditional_columns": 5, "response_columns": 4, "w_columns": 1,
    }
    tol = c["tolerances"]
    passed = (max(metrics["rhs_scaled_backward_residuals"]) <= tol["linear"]
              and metrics["partition_maxabs"] <= tol["partition"]
              and metrics["energy_scaled_residual"] <= tol["energy"]
              and max(event_errors) <= tol["event_energy"]
              and metrics["probability_min"] >= -tol["probability"]
              and metrics["probability_max"] <= 1 + tol["probability"]
              and max(upper_violation, lower_violation) <= tol["rare_bound"]
              and np.all(responses <= 0))
    new = dict(E_eV=base["E_eV"], K_HeI_diag=d0, K_diag=d, K_lower=lower, K_upper=upper,
        lambda_H1=old["lambda_H1"], lambda_HeI=old["lambda_He"],
        rhs_physical18=rhs, rhs_conditional5=conditional_rhs,
        rhs_response4=response_rhs, rhs_w=lam,
        solution_physical18=physical, solution_conditional5=conditional,
        solution_response4=responses, w=w,
        p_H1=physical[:, 6], r_H1=physical[:, 7], v_H1=conditional[:, 2],
        p_HeI=physical[:, 8], r_HeI=physical[:, 9], v_HeI=conditional[:, 3],
        p_HeII=pnew, r_HeII=physical[:, 11], v_HeII=conditional[:, 4],
        u_s=physical[:, 0], u_p=physical[:, 1], u_entry=physical[:, 2], t=physical[:, 3],
        r_s=physical[:, 4], r_p=physical[:, 5], H=physical[:, 12:18],
        photon_H1=photons[0], internal_H1=internals[0],
        photon_HeI=photons[1], internal_HeI=internals[1],
        photon_HeII=photons[2], internal_HeII=internals[2],
        delta_CE=responses[:, 0], delta_time=responses[:, 1],
        delta_H1_RR=responses[:, 2], delta_HeI_RR=responses[:, 3],
        energy_terms=terms, diagonal_addition_loss=addition_loss.astype(float), **coef)
    return new, metrics, bool(passed)


def source_average(base, old, new, src, z, c):
    projection = base["source_" + z]
    mask = base["active_mask_" + z]
    raw_energy, masses, grid = src["W_eV"], src["pulse_count_cm3"], base["E_eV"]
    population = projection[1:]
    need(mask.dtype.kind == "b" and np.array_equal(mask, raw_energy > grid[0]), "SOURCE_ACTIVE_MASK_IDENTITY")
    need(len(projection) == len(grid) and np.all(projection >= 0), "SAVED_NONNEGATIVE_SOURCE")
    active, selected = float(masses[mask].sum()), float(masses.sum())
    active_energy = float(masses[mask] @ raw_energy[mask])
    need(active > 0 and selected > 0 and active_energy > 0, "NONEMPTY_SAVED_SOURCE")
    need(abs(float(projection.sum()) - active) / active < 2e-12
         and abs(float(projection @ grid) - active_energy) / active_energy < 2e-12,
         "SAVED_PROJECTION_IDENTITY")
    moments = {label: (float(population @ new["p_" + label]),
                      float(population @ new["r_" + label]),
                      float(population @ new["v_" + label])) for label in ("H1", "HeI", "HeII")}
    ce = float(population @ (new["u_s"] + new["u_p"]))
    incident = float(population @ (new["r_s"] + new["r_p"]))
    gains, stop = population @ new["H"], float(population @ new["t"])
    changes = {key: float(population @ new[key]) for key in ("delta_CE", "delta_time", "delta_H1_RR", "delta_HeI_RR")}
    old_moments = {"CE": float(population @ (old["u_s"] + old["u_p"])),
                   "time": float(population @ old["t"]),
                   "H1_RR": float(population @ old["p_H1"]),
                   "HeI_RR": float(population @ old["p_He"])}
    sw, eta = float(population @ new["w"]), float(new["w"].max())
    entry_count = float(population @ new["u_entry"]) + float(projection[0])
    ledger = {
        "bath_gain_eV_cm3": {label: float(gains[j]) for j, label in enumerate(c["bath_labels"])},
        "entry_energy_eV_cm3": float(grid[0] * entry_count),
        "inactive_own_energy_eV_cm3": float(masses[~mask] @ raw_energy[~mask]),
        "CE_outgoing_kinetic_eV_cm3": incident - c["gap_eV"] * ce,
        "CE_internal_eV_cm3": c["gap_eV"] * ce,
        "initial_kinetic_eV_cm3": float(masses @ raw_energy),
    }
    row = {"P_CE_active": ce / active, "mean_stop_s_active": stop / active,
           "delta_CE_active": changes["delta_CE"] / active,
           "delta_time_s_active": changes["delta_time"] / active,
           "delta_H1_RR_active": changes["delta_H1_RR"] / active,
           "delta_HeI_RR_active": changes["delta_HeI_RR"] / active,
           "old_P_CE_active": old_moments["CE"] / active,
           "old_mean_stop_s_active": old_moments["time"] / active,
           "old_P_H1_RR_active": old_moments["H1_RR"] / active,
           "old_P_HeI_RR_active": old_moments["HeI_RR"] / active,
           "source_bound_lower": sw / (1 + eta) / active,
           "source_bound_upper": sw / active,
           "selected_count_cm3": selected, "active_count_cm3": active,
           "source_q_count_cm3": float(projection[0]),
           "source_partition_active": (entry_count + ce + sum(v[0] for v in moments.values())) / active,
           "stored_column_response_semantics": "-K1^-1 D stored_HeI_column; subtraction contains baseline residual",
           "event_rate_m3_s": None, "exposure_s": None, "instantaneous_rhs": None,
           "physical_heating_J_m3": None, "irreversible_assimilation": False}
    final_keys = ["entry_energy_eV_cm3", "inactive_own_energy_eV_cm3",
                  "CE_outgoing_kinetic_eV_cm3", "CE_internal_eV_cm3"]
    for label, ionization in (("H1", c["I_eV"]), ("HeI", c["I_HeI_eV"]), ("HeII", c["I_HeII_eV"])):
        count, kinetic, time_moment = moments[label]
        photon = kinetic + ionization * count
        internal = -ionization * count
        row.update({"P_" + label + "_RR_active": count / active,
                    "P_" + label + "_RR_selected": count / selected,
                    "conditional_" + label + "_RR_kinetic_eV": kinetic / count if count > 0 else None,
                    "conditional_" + label + "_RR_photon_eV": photon / count if count > 0 else None,
                    "conditional_" + label + "_RR_time_s": time_moment / count if count > 0 else None,
                    label + "_RR_photon_eV_per_selected": photon / selected,
                    label + "_RR_internal_eV_per_selected": internal / selected,
                    "expected_" + label + "_events_cm3": count,
                    "expected_" + label + "_kinetic_eV_cm3": kinetic})
        pk, ik = label + "_RR_photon_retained_eV_cm3", label + "_RR_atomic_internal_eV_cm3"
        ledger[pk], ledger[ik] = photon, internal
        final_keys.extend((pk, ik))
    values = list(ledger["bath_gain_eV_cm3"].values()) + [ledger[k] for k in final_keys]
    ledger["scaled_residual"] = abs(math.fsum(values) - ledger["initial_kinetic_eV_cm3"]) / (
        math.fsum(abs(v) for v in values) + ledger["initial_kinetic_eV_cm3"])
    h, he1, he2 = (moments[k][0] for k in ("H1", "HeI", "HeII"))
    row["expected_population_delta_cm3"] = {
        "fast_electron": -h - he1 - he2, "HeIII": -he2, "HeII": he2 - he1,
        "HeI": he1, "HII": -h, "HI": h, "photon": h + he1 + he2}
    row["diagnostic_electron_removed_energy_eV_cm3"] = math.fsum(v[1] for v in moments.values())
    row["subtraction_diagnostic_delta_H1"] = (h - old_moments["H1_RR"]) / active
    row["subtraction_diagnostic_delta_HeI"] = (he1 - old_moments["HeI_RR"]) / active
    row["ledger"] = ledger
    return row
