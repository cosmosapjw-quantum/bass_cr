#!/usr/bin/env python3
"""C22D saved/accepted-mesh analysis. Cosmological ODE0 and model RHS0.

Completed raw bytes are immutable.  New accepted-mesh algebraic summaries are
computed only for the four new C22D runs.  Old C22C observables are reused from
their stored arrays.  CI on/off share the new registry; the separate registry
comparison uses old C22C against new-registry CI OFF.  All output is create-only.
"""
from __future__ import annotations
import os
import sys
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_key] = "1"
sys.dont_write_bytecode = True
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import tempfile
import time
import traceback
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
C22C = HERE.parent / "cr_c22c_h1_excitation_20261022"
MYR = 365.25 * 86400. * 1e6
LEDGERS = ("energy_relative_residual", "nucleus_max_relative_residual",
           "charge_photon_relative_residual", "photon_number_relative_residual")
COUNTERS = ("recombination_count_per_H", "absorption_count_per_H",
            "excitation_2s_events_per_H", "excitation_2p_events_per_H", "H1_CI_events_per_H")
CUMULATIVE_REFERENCE = {"bath_energy_received_eV_per_H", "excitation_escaped_energy_eV_per_H", "H1_CI_events_per_H"}
COMMON_COMPARISON = ("temperature_K", "n_e_cm3", "tau_T", "Sigma_F", "Pi_r_F", "H1_ionized_fraction",
                     "bath_energy_received_eV_per_H", "excitation_escaped_energy_eV_per_H")


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pin(path):
    path = Path(path)
    raw = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError("UNSUPPORTED_JSON_TYPE:" + type(value).__name__)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False,
                      default=json_default).encode("utf8")


def atomic_create(path, payload):
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix="pending_", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload); handle.flush(); os.fsync(handle.fileno())
        os.link(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def json_create(path, value):
    # Serialize fully before creating a destination; numpy types are explicit.
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False,
                      default=json_default) + "\n").encode("utf8")
    atomic_create(path, raw)


def npz_create(path, arrays):
    buffer = io.BytesIO()
    np.savez_compressed(buffer, **arrays)
    atomic_create(path, buffer.getvalue())


def csv_create(path, rows):
    if not rows:
        raise ValueError("EMPTY_CSV")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
    atomic_create(path, buffer.getvalue().encode("utf8"))


def finite_history(h):
    for key, value in h.items():
        value = np.asarray(value)
        if key == "cancellation_fraction":
            mask = h.get("cancellation_fraction_defined")
            if (mask is None or mask.dtype.kind != "b" or mask.shape != value.shape
                    or np.any(np.isinf(value)) or not np.array_equal(np.isfinite(value), mask)
                    or not np.all(np.isnan(value[~mask]))):
                return False
        elif value.dtype.kind in "fci" and not np.all(np.isfinite(value)):
            return False
    return True


def read_run(directory):
    """Byte-verified reader derived from immutable C22A read_run; no model call."""
    base = Path(directory).resolve()
    inputs = json.loads((base / "INPUT.json").read_bytes())
    source = json.loads((base / "SOURCE_IDENTITY.json").read_bytes())
    runtime = json.loads((base / "RUNTIME.json").read_bytes())
    payload = dict(source)
    identity = payload.pop("identity_sha256")
    if identity != hashlib.sha256(canonical(payload)).hexdigest():
        raise ValueError("SOURCE_IDENTITY_DIGEST_MISMATCH")
    input_sha = hashlib.sha256(canonical(inputs)).hexdigest()
    if runtime["input_sha256"] != input_sha or runtime["source_identity_sha256"] != identity:
        raise ValueError("RUN_BINDING_MISMATCH")
    summary = json.loads((base / "SUMMARY.json").read_bytes())
    if (summary.get("status") != "COMPLETE_SCOPED"
            or summary.get("source_identity_sha256") != identity
            or summary.get("input_sha256") != input_sha):
        raise ValueError("RUN_SUMMARY_NOT_COMPLETE_OR_UNBOUND")
    rows = {}
    for case in inputs["cases"]:
        folder = base / "cases" / case["name"]
        complete = json.loads((folder / "COMPLETE.json").read_bytes())
        receipt = json.loads((folder / "RECEIPT.json").read_bytes())
        raw = (folder / "history.npz").read_bytes()
        raw_sha = hashlib.sha256(raw).hexdigest()
        if (complete.get("status") != "COMPLETED_SCOPED"
                or receipt.get("status") != "COMPLETED_SCOPED"
                or complete["source_identity_sha256"] != identity
                or complete["input_sha256"] != input_sha
                or complete["history_sha256"] != raw_sha
                or complete["receipt_sha256"] != sha256(folder / "RECEIPT.json")
                or receipt["case"] != case or receipt["source_identity_sha256"] != identity
                or receipt["input_sha256"] != input_sha or receipt["history_sha256"] != raw_sha
                or receipt["history_bytes"] != len(raw)
                or receipt["model_metadata_sha256"] != sha256(folder / "MODEL.json")):
            raise ValueError("CASE_BYTES_OR_IDENTITY_MISMATCH:" + case["name"])
        with np.load(io.BytesIO(raw), allow_pickle=False) as data:
            h = {key: data[key] for key in data.files}
        if not finite_history(h):
            raise ValueError("NONFINITE_HISTORY:" + case["name"])
        rows[case["name"]] = {"case": case, "history": h, "receipt": receipt,
            "metadata": json.loads((folder / "MODEL.json").read_bytes()),
            "raw_pin": {"path": str(folder / "history.npz"), "sha256": raw_sha, "size_bytes": len(raw)}}
    return {"path": str(base), "input": inputs, "source": source, "runtime": runtime, "rows": rows}


def verify_registered(run, contract, role):
    expected = contract["new_runs"][role]
    cases = expected["cases"] if role == "nominal" else [expected["case"]]
    for key in ("method", "rtol", "atol"):
        if run["input"][key] != expected[key]:
            raise ValueError("REGISTERED_" + role + "_" + key + "_MISMATCH")
    if (run["input"]["cases"] != cases or set(run["rows"]) != {c["name"] for c in cases}
            or run["input"].get("schema") != "C22D_INPUT_V1"
            or run["input"]["saved_times"] != contract["new_runs"]["saved_times"]):
        raise ValueError("REGISTERED_CASE_OR_INPUT_SCHEMA_MISMATCH")
    for row in run["rows"].values():
        h, meta, receipt = row["history"], row["metadata"], row["receipt"]
        n = contract["new_runs"]["saved_times"]
        if (meta["schema"] != "C22D_H1_FINITE_CI_ALIGNED_ENERGY_V1"
                or meta["case"] != row["case"] or meta["state_size"] != 78
                or meta["solver_state_size"] != 75
                or meta["energy_registry"] != contract["energy_registry"]["name"]
                or meta["hydrogen_family_chi_eV"] != contract["energy_registry"]["new_Hfamily_chi_eV"]
                or h["Y"].shape != (78, n) or len(h["eta"]) != n
                or h["accepted_Y"].shape != (78, len(h["accepted_eta"]))
                or receipt["accepted_mesh_points"] != len(h["accepted_eta"])):
            raise ValueError("C22D_MODEL_OR_ARRAY_CONTRACT_MISMATCH")
        if any(receipt[k] != expected[k] for k in ("method", "rtol", "atol")):
            raise ValueError("RECEIPT_METHOD_OR_TOLERANCE_MISMATCH")


def verify_old_baseline(old, nominal):
    """Bind registry-only attribution to the stored old input, not code alone."""
    path = C22C/"CONTRACT.json"
    old_contract = json.loads(path.read_bytes())
    registered = old_contract["new_cosmological_runs"]["nominal"]
    for key in ("method", "rtol", "atol"):
        if old["input"][key] != registered[key]:
            raise ValueError("OLD_BASELINE_REGISTERED_"+key.upper()+"_MISMATCH")
    if (old["input"]["cases"] != registered["cases"]
            or old["input"]["saved_times"] != old_contract["new_cosmological_runs"]["saved_times"]
            or old["input"].get("schema") != "C22C_INPUT_V1"):
        raise ValueError("OLD_BASELINE_REGISTERED_INPUT_MISMATCH")
    old_case = old["rows"]["finite_uv_excitation_lrs"]["case"]
    off_case = nominal["rows"]["registry_control_lrs"]["case"]
    def common(case):
        data = {k: v for k, v in case.items()
                if k not in ("name", "energy_registry", "h1_ci_enabled")}
        data.setdefault("ellmax", 8)
        return data
    if common(old_case) != common(off_case):
        raise ValueError("REGISTRY_ONLY_COMPARISON_IC_OR_COMMON_MODEL_MISMATCH")
    on_case = nominal["rows"]["ci_lrs"]["case"]
    if (common(on_case) != common(off_case) or on_case["energy_registry"] != off_case["energy_registry"]
            or on_case["h1_ci_enabled"] is not True or off_case["h1_ci_enabled"] is not False):
        raise ValueError("SAME_REGISTRY_CI_COMPARISON_BINDING_MISMATCH")
    return {"status": "PASS_INPUT_BINDING", "old_contract_pin": pin(path),
        "old_input_pin": pin(Path(old["path"])/"INPUT.json"),
        "common_case_normalized": common(old_case), "default_normalization": {"ellmax": 8},
        "registry_effect": "identical common IC/model inputs; old registered solver settings retained",
        "CI_effect": "identical common IC/model inputs and energy registry; only CI switch differs"}


def summarize_without_rhs(model, eta, states):
    objects, obj = [], model
    while obj is not None and not any(obj is x for x in objects):
        objects.append(obj); obj = getattr(obj, "base", None)
    changes, attempts = [], []
    def forbidden(*args, **kwargs):
        attempts.append(True)
        raise RuntimeError("ANALYSIS_RHS_FORBIDDEN")
    try:
        for obj in objects:
            for key in ("rhs", "solver_rhs", "rhs_energy_residual"):
                if hasattr(obj, key):
                    changes.append((obj, key, key in obj.__dict__, getattr(obj, key)))
                    setattr(obj, key, forbidden)
        h = {k: np.asarray(v) for k, v in model.summarize(eta, states).items()}
    finally:
        for obj, key, owned, original in reversed(changes):
            if owned:
                setattr(obj, key, original)
            else:
                delattr(obj, key)
    if attempts:
        raise RuntimeError("ANALYSIS_RHS_ATTEMPTED")
    return h


def cumulative_trapezoid(values, eta):
    return np.r_[0., np.cumsum(.5 * (values[1:] + values[:-1]) * np.diff(eta))]


def additional_diagnostics(h, model, ci):
    """New accepted/saved-path diagnostics; no modified trajectory integration.

    Conditional K3 uses ground Saha g_H=2, g_p=1, electron-spin2 -> d=1,
    R3=K3*n_e**2*n_p.  It is not an all-level inverse provider or omission bound.
    Formula provenance: c22d/theory/check_ci_delta.py; stable Boltzmann cancellation.
    """
    t = h["temperature_K"]
    provider = model.ci_provider
    planck = 6.62607015e-34
    pl_scaled, alt_scaled, gap_fraction = [], [], []
    for value in t:
        parts = provider.interval_scaled_integrals(value)
        total = float(np.sum(parts))
        gap_fraction.append(float(parts[0] / total))
        parts[0] = provider.gap_scaled_integral(value, 1.127)
        pl_scaled.append(total); alt_scaled.append(float(np.sum(parts)))
    pl_scaled, alt_scaled = np.asarray(pl_scaled), np.asarray(alt_scaled)
    theta = ci.KB_EV_K * t
    logD = 1.5*np.log(2*math.pi*ci.ME_KG*ci.KB_J_K*t/planck**2) - math.log(1e6)
    logK3 = math.log(ci.K_CM3_S)-1.5*np.log(theta)+np.log(pl_scaled)-logD
    alpha = np.asarray(model.atomic.provider.rr("HI", t))
    k3 = np.exp(logK3)
    ratio = alt_scaled/pl_scaled  # positive scaled moments avoid q_underflow /0.
    abundance = h["atomic_abundance_per_Href"]
    particles = np.sum(abundance, axis=0) + model.atomic.q @ abundance
    events = h["H1_CI_events_per_H_per_eta"]
    h.update({
        "gas_particles_per_Href": particles,
        "H1_minus_D_ionized_fraction": h["atomic_scaled"][model.atomic.blocks["H1"][1]]
                                      - h["atomic_scaled"][model.atomic.blocks["D"][1]],
        "CI_implied_temperature_prime_K_per_eta": -(2*ci.THRESHOLD_EV/(3*ci.KB_EV_K)+t)*events/particles,
        "CI_ground_conditional_K3_cm6_s": k3,
        "CI_ground_conditional_log10_K3_cm6_s": logK3/math.log(10.),
        "HI_RR_alpha_cm3_s": alpha,
        "CI_ground_conditional_threebody_over_RR": h["n_e_cm3"]*k3/alpha,
        "CI_first_gap_PL_fraction": np.asarray(gap_fraction),
        "CI_first_gap_p1127_to_PL_rate_ratio": ratio,
        "CI_first_gap_p1127_log10_q_cm3_s": h["H1_CI_core_log10_q_cm3_s"]+np.log10(ratio),
        "CI_fixed_path_PL_trapezoid_events_per_H": cumulative_trapezoid(events, h["eta"]),
        "CI_fixed_path_p1127_trapezoid_events_per_H": cumulative_trapezoid(events*ratio, h["eta"]),
    })
    return h


def mesh_audit(h, model, gates, ci):
    n = len(h["eta"])
    if (h["Y"].shape != (78, n) or h["atomic_scaled"].shape != (21, n)
            or h["UV_photons_per_H"].shape != (n, 6)
            or any(h[k].shape != (n,) for k in (*LEDGERS, *COUNTERS, "temperature_K",
                   "H1_CI_core_q_cm3_s", "H1_CI_core_log10_q_cm3_s", "H1_CI_source_underflow"))):
        raise ValueError("C22D_SUMMARY_SHAPE_MISMATCH")
    formula_tol = 64*np.finfo(float).eps
    energy_keys = ("thermal_energy_eV_per_H", "ionization_energy_eV_per_H", "UV_energy_eV_per_H",
        "escaped_energy_eV_per_H", "gas_work_eV_per_H", "UV_work_eV_per_H",
        "bath_energy_received_eV_per_H", "excitation_escaped_energy_eV_per_H")
    total = sum(h[k] for k in energy_keys)
    count = h["H1_CI_events_per_H"]
    charge = (h["n_e_cm3"]/h["nH_ref_cm3"] + h["recombination_count_per_H"]
              - h["absorption_count_per_H"] - count-model.initial_electrons)/max(model.initial_photons, 1.)
    temperature = 2*h["thermal_energy_eV_per_H"]/(3*ci.KB_EV_K*h["gas_particles_per_Href"])
    v = {k: float(np.max(abs(h[k]))) for k in LEDGERS}
    v.update(minimum_scaled_population=float(np.min(h["atomic_scaled"])),
        minimum_UV_count_per_H=float(np.min(h["UV_photons_per_H"])),
        minimum_temperature_K=float(np.min(h["temperature_K"])),
        maximum_temperature_K=float(np.max(h["temperature_K"])),
        maximum_nHref_cm3=float(np.max(h["nH_ref_cm3"])),
        maximum_ne_cm3=float(np.max(h["n_e_cm3"])),
        minimum_event_count_per_H=min(float(np.min(h[k])) for k in COUNTERS),
        minimum_event_increment_per_H=min(float(np.min(np.diff(h[k]))) for k in COUNTERS),
        declared_n_T_exact_zero=bool(np.all(h["Y"][model.invariant_indices] == 0)),
        CI_initial_count=float(count[0]), CI_final_count=float(count[-1]),
        CI_min_log10_q=float(np.min(h["H1_CI_core_log10_q_cm3_s"])),
        CI_max_log10_q=float(np.max(h["H1_CI_core_log10_q_cm3_s"])),
        CI_underflow_samples=int(np.count_nonzero(h["H1_CI_source_underflow"])),
        maximum_ground_conditional_threebody_over_RR=float(np.max(h["CI_ground_conditional_threebody_over_RR"])),
        maximum_first_gap_PL_fraction=float(np.max(h["CI_first_gap_PL_fraction"])),
        minimum_first_gap_p1127_to_PL_ratio=float(np.min(h["CI_first_gap_p1127_to_PL_rate_ratio"])),
        maximum_first_gap_p1127_to_PL_ratio=float(np.max(h["CI_first_gap_p1127_to_PL_rate_ratio"])),
        fixed_path_PL_integral=float(h["CI_fixed_path_PL_trapezoid_events_per_H"][-1]),
        fixed_path_p1127_integral=float(h["CI_fixed_path_p1127_trapezoid_events_per_H"][-1]),
        fixed_path_PL_minus_ODE_count=float(h["CI_fixed_path_PL_trapezoid_events_per_H"][-1]-count[-1]),
        max_abs_H1_minus_D_ionized_fraction=float(np.max(abs(h["H1_minus_D_ionized_fraction"]))),
        maximum_omitted_trace_energy_H2_fraction=float(np.max(h["omitted_trace_energy_H2_fraction"])),
        energy_sum_formula_difference=float(np.max(abs(total-h["energy_total_eV_per_H"]))),
        charge_formula_difference=float(np.max(abs(charge-h["charge_photon_relative_residual"]))),
        temperature_particle_formula_max_relative=float(np.max(abs(temperature/h["temperature_K"]-1))))
    ci_binding = ci.THRESHOLD_EV*count
    initial_sum = model.initial_energy
    checks = {
        "energy": v["energy_relative_residual"] <= gates["energy_relative_saved_and_accepted_max_abs"],
        "nuclei": v["nucleus_max_relative_residual"] <= gates["nucleus_max_relative_residual"],
        "charge": v["charge_photon_relative_residual"] <= gates["charge_and_photon_absolute_normalized"],
        "photon_number": v["photon_number_relative_residual"] <= gates["charge_and_photon_absolute_normalized"],
        "population": v["minimum_scaled_population"] >= gates["minimum_scaled_population"],
        "UV_population": v["minimum_UV_count_per_H"] >= gates["minimum_UV_count_per_H"],
        "event_count": v["minimum_event_count_per_H"] >= gates["minimum_event_count_per_H"],
        "event_monotonic_with_same_absolute_allowance": v["minimum_event_increment_per_H"] >= gates["minimum_event_count_per_H"],
        "declared_n_T": v["declared_n_T_exact_zero"],
        "T_domain": gates["temperature_strict_min_K"] < v["minimum_temperature_K"]
                    and v["maximum_temperature_K"] <= gates["temperature_max_K"],
        "density_selector": v["maximum_nHref_cm3"] <= gates["nHref_max_cm3"],
        "state_dimensions": model.size == 78 and model.solver_size == 75,
        "finite_or_explicit_undefined": finite_history(h),
        "monotone_eta_time_redshift": bool(np.all(np.diff(h["eta"]) > 0)
            and np.all(np.diff(h["proper_elapsed_s"]) > 0) and np.all(np.diff(h["z"]) < 0)),
        "CI_counter_state_binding": np.array_equal(count, h["Y"][model.ici]),
        "CI_initial_exact_zero": count[0] == 0,
        "CI_off_exact_zero": model.ci_enabled or bool(np.all(count == 0) and np.all(h["H1_CI_events_per_H_per_eta"] == 0)),
        "CI_binding_transfer_formula": bool(np.array_equal(ci_binding, h["H1_CI_thermal_to_binding_eV_per_H"])),
        "CI_rate_nonnegative": bool(np.all(h["H1_CI_core_q_cm3_s"] >= 0)),
        "CI_underflow_mask": h["H1_CI_source_underflow"].dtype.kind == "b" and np.array_equal(
            h["H1_CI_source_underflow"], h["H1_CI_core_q_cm3_s"] == 0),
        "CI_logq_finite": bool(np.all(np.isfinite(h["H1_CI_core_log10_q_cm3_s"]))),
        "no_extra_CI_escape_energy": v["energy_sum_formula_difference"] <= formula_tol*max(abs(initial_sum),1.),
        "charge_formula": v["charge_formula_difference"] <= formula_tol,
        "particle_temperature_formula": v["temperature_particle_formula_max_relative"] <= formula_tol,
        "signed_radiation_sum": bool(np.max(abs(h["signed_Pi_r_F"]-h["signed_Pi_gamma_F"]-h["signed_Pi_nu_F"])) <= 1e-15),
        "radiation_norm": bool(np.max(abs(h["Pi_r_F"]-abs(h["signed_Pi_r_F"]))) <= 1e-15),
        "total_norm": bool(np.max(abs(h["Pi_tot_F"]-abs(h["signed_Pi_m_F"]+h["signed_Pi_r_F"]))) <= 1e-15),
        "first_gap_variant_same_path_order": v["minimum_first_gap_p1127_to_PL_ratio"] > 0
                    and v["maximum_first_gap_p1127_to_PL_ratio"] <= 1+formula_tol,
    }
    checks = {k: bool(value) for k, value in checks.items()}
    pl, alt = v["fixed_path_PL_integral"], v["fixed_path_p1127_integral"]
    v["fixed_path_p1127_fractional_integral_change"] = alt/pl-1 if pl > 0 else None
    v["fixed_path_PL_quadrature_relative_difference_from_ODE_counter"] = pl/count[-1]-1 if count[-1] > 0 else None
    return {"status": "PASS_SCOPED" if all(checks.values()) else "FAIL_PRESERVED",
        "mesh_points": n, "measurements": v, "checks": checks,
        "scope": "finite saved or solver-returned accepted mesh; no continuous extrema or global/physical error bound",
        "inverse_scope": "ground-only inverse of adopted finite model, actual ne; not an all-level inverse or omission bound",
        "first_gap_scope": "same-path functional sensitivity; trapezoid quadrature; no trajectory feedback reintegration"}


def reference_comparison(nominal, reference, contract):
    if not np.array_equal(nominal["eta"], reference["eta"]):
        raise ValueError("REFERENCE_ETA_GRIDS_DIFFER_NO_INTERPOLATION_ALLOWED")
    tolerance = contract["preregistered_gates"]["reference_scaled_max_difference"]
    rows, arrays = [], {"eta": nominal["eta"]}
    for key in contract["preregistered_gates"]["reference_fields"]:
        a, b = nominal[key], reference[key]
        peak = float(np.max(abs(b)))
        scale = np.full_like(b, max(peak, 1e-30)) if key in CUMULATIVE_REFERENCE else np.maximum(abs(b), max(1e-8*peak, 1e-30))
        delta = abs(a-b)/scale
        i = int(np.argmax(delta))
        rows.append({"field": key, "scaled_max_difference": float(delta[i]),
            "index": i, "eta": float(nominal["eta"][i]), "absolute_max_difference": float(np.max(abs(a-b))),
            "reference_peak": peak, "scale": "uniform peak floor1e-30" if key in CUMULATIVE_REFERENCE
             else "max(abs(reference),1e-8*reference_peak,1e-30)", "tolerance": tolerance,
            "passed": bool(delta[i] <= tolerance)})
        arrays[key+"_scaled_abs_difference"] = delta
    return {"status": "PASS_SCOPED" if all(r["passed"] for r in rows) else "FAIL_PRESERVED",
        "fields": rows, "saved_points": len(nominal["eta"]),
        "interpretation": "BDF vs tighter Radau at the same eta, finite9-field check; no global error certificate"}, arrays


def effect_comparison(actual, baseline, label):
    if not np.array_equal(actual["eta"], baseline["eta"]):
        raise ValueError("MATCHED_EFFECT_ETA_GRIDS_DIFFER:"+label)
    rows = []
    for key in COMMON_COMPARISON:
        difference = actual[key]-baseline[key]
        peak = max(float(np.max(abs(baseline[key]))), 1e-30)
        rows.append({"field": key, "final_actual": float(actual[key][-1]),
            "final_baseline": float(baseline[key][-1]), "final_absolute_change": float(difference[-1]),
            "max_abs_change": float(np.max(abs(difference))),
            "max_abs_change_over_baseline_peak": float(np.max(abs(difference))/peak),
            "final_fractional_change": float(difference[-1]/baseline[key][-1]) if baseline[key][-1] != 0 else None})
    return {"label": label, "fields": rows, "grid": "identical eta; no interpolation",
        "interpretation": "conditional model difference; not an uncertainty bound or numerical acceptance test"}


def figures(out, histories, baseline, ref_arrays, contract):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.titlesize": 11})
    on = histories["nominal:ci_lrs"]["saved"]
    off = histories["nominal:registry_control_lrs"]["saved"]
    acc = histories["nominal:ci_lrs"]["accepted"]
    flrw = histories["nominal:ci_flrw"]["saved"]
    figures_written = []
    def save(fig, stem):
        for suffix in ("png", "pdf"):
            buffer = io.BytesIO()
            fig.savefig(buffer, format=suffix, dpi=170, bbox_inches="tight", facecolor="white")
            path = out/(stem+"."+suffix)
            atomic_create(path, buffer.getvalue()); figures_written.append(pin(path))
        plt.close(fig)
    def axis(ax, eta=False):
        ax.set_xscale("symlog", linthresh=1e-6 if eta else 1e-5, linscale=.6)
        ax.set_xlabel(r"$\eta=\ln(a/a_i)$; symlog" if eta else "Elapsed proper time from z=20 [Myr]; symlog")
        ax.grid(alpha=.2)
    def plot_time(ax, h, key, **kwargs):
        ax.plot(h["proper_elapsed_s"]/MYR, h[key], **kwargs)
    def percent(actual, base):
        result = np.full_like(base, np.nan)
        np.divide(100*(actual-base), base, out=result, where=base != 0)
        return result
    fig, axes = plt.subplots(2, 3, figsize=(15.2, 8.7), layout="constrained")
    labels = (("temperature_K", "Gas temperature [K]"), ("n_e_cm3", r"Free electrons [cm$^{-3}$]"),
              ("tau_T", r"Cumulative Thomson depth $\tau_T$"), ("H1_ionized_fraction", "H1 ionized fraction"))
    for ax, (key, label) in zip(axes.flat, labels):
        for h, name, color, ls in ((baseline, "C22C stored: old registry", ".45", ":"),
                (off, "C22D new registry: CI OFF", "#c36c2d", "--"),
                (on, "C22D new registry: CI ON", "#087b8c", "-")):
            plot_time(ax, h, key, label=name, color=color, ls=ls)
        if all(np.all(h[key] > 0) for h in (baseline, off, on)):
            ax.set_yscale("log")
        ax.set_ylabel(label); ax.set_title(label); ax.legend(fontsize=7)
    for ax, actual, base, title in ((axes[1,1], on, off, "CI effect: same new registry"),
                                   (axes[1,2], off, baseline, "Registry effect: both CI OFF")):
        for key, label in (("temperature_K", "T"), ("n_e_cm3", "n_e"), ("tau_T", "tau_T")):
            ax.plot(actual["eta"], percent(actual[key], base[key]), label=label)
        ax.axhline(0, color=".5", lw=.7); ax.set_ylabel("Matched-eta change [%]")
        ax.set_title(title); ax.legend(); axis(ax, eta=True)
    for ax in list(axes.flat)[:4]:
        axis(ax)
    fig.suptitle("C22D: separate the matched CI effect from the energy-registry change")
    save(fig, "MATCHED_EFFECTS_AND_REGISTRY")

    fig, axes = plt.subplots(2, 3, figsize=(15.2, 8.8), layout="constrained")
    ax = axes[0,0]
    for key, label in (("thermal_energy_eV_per_H", "thermal"), ("ionization_energy_eV_per_H", "binding"),
        ("UV_energy_eV_per_H", "resident UV"), ("escaped_energy_eV_per_H", "escaped RR"),
        ("gas_work_eV_per_H", "gas work"), ("UV_work_eV_per_H", "UV work"),
        ("bath_energy_received_eV_per_H", "CMB bath"), ("excitation_escaped_energy_eV_per_H", "escaped n2")):
        plot_time(ax, on, key, label=label, lw=1)
    ax.set_yscale("symlog", linthresh=1e-8); ax.set_ylabel("Energy [eV/Href]")
    ax.set_title("Adopted energy ledger; CI exchanges U and binding")
    ax.legend(fontsize=7, ncol=2)
    ax = axes[0,1]
    for name, row in histories.items():
        plot_time(ax, row["accepted"], "energy_relative_residual", label=name, lw=.9)
    lim = contract["preregistered_gates"]["energy_relative_saved_and_accepted_max_abs"]
    ax.axhline(lim, color=".5", ls="--"); ax.axhline(-lim, color=".5", ls="--")
    ax.set_yscale("symlog", linthresh=1e-13); ax.set_ylabel("Signed energy residual / initial energy")
    ax.set_title("Solver-accepted mesh energy gate"); ax.legend(fontsize=7)
    ax = axes[0,2]
    for key, label in ((LEDGERS[1], "nuclei"), (LEDGERS[2], "charge with CI"), (LEDGERS[3], "UV photon count")):
        plot_time(ax, acc, key, label=label)
    ax.set_yscale("symlog", linthresh=1e-15); ax.set_ylabel("Normalized residual")
    ax.set_title("LRS accepted mesh conservation"); ax.legend(fontsize=7)
    ax = axes[1,0]
    for key, label in (("signed_Pi_gamma_F", "P_gamma"), ("signed_Pi_nu_F", "P_nu"),
                      ("signed_Pi_m_F", "P_m"), ("signed_Pi_r_F", "P_gamma+P_nu")):
        plot_time(ax, on, key, label=label)
    ax.set_yscale("symlog", linthresh=1e-12); ax.set_ylabel("Signed Frobenius amplitudes")
    ax.set_title("Signed amplitudes before norms"); ax.legend(fontsize=7)
    ax = axes[1,1]
    for key, label in (("Sigma_F", "Sigma"), ("Pi_r_F", "abs(P_gamma+P_nu)"),
                      ("Pi_tot_F", "abs(P_m+P_r)")):
        plot_time(ax, on, key, label=label)
    ax.set_yscale("symlog", linthresh=1e-12); ax.set_ylabel("Full Frobenius norm")
    ax.set_title("Non-tilted LRS scalar norms"); ax.legend(fontsize=7)
    ax = axes[1,2]
    for key, label in ((COUNTERS[0], "RR"), (COUNTERS[1], "PI"), (COUNTERS[4], "H1 CI"),
                      (COUNTERS[2], "2s"), (COUNTERS[3], "2p")):
        plot_time(ax, on, key, label=label)
    ax.set_yscale("symlog", linthresh=1e-12); ax.set_ylabel("Cumulative events / Href")
    ax.set_title("Independent event counters"); ax.legend(fontsize=7)
    for ax in axes.flat:
        axis(ax)
    fig.suptitle("C22D LRS: conservation, signed stresses and counters; finite-mesh checks")
    save(fig, "ENERGY_STRESS_AND_CONSERVATION")

    fig, axes = plt.subplots(3, 3, figsize=(14.8, 11), layout="constrained")
    limit = contract["preregistered_gates"]["reference_scaled_max_difference"]
    for ax, key in zip(axes.flat, contract["preregistered_gates"]["reference_fields"]):
        error = ref_arrays[key+"_scaled_abs_difference"]
        ax.plot(ref_arrays["eta"], error, color="#087b8c")
        ax.axhline(limit, color="#ad3e32", ls="--", label="fixed gate2e-7")
        ax.set_yscale("symlog", linthresh=1e-12)
        ax.set_title(key.replace("_", "\n") if len(key)>35 else key)
        ax.set_ylabel("Scaled absolute difference")
        ax.text(.03, .88, f"max={np.max(error):.4g}", transform=ax.transAxes, fontsize=8)
        axis(ax, eta=True)
    axes[0,0].legend(fontsize=7)
    fig.suptitle("New C22D LRS: BDF versus tighter Radau at201 identical eta values\n"
                 "Cumulative bath/n2/CI use uniform reference-peak scale; other fields use registered local scale")
    save(fig, "STRICT_NINE_FIELD_REFERENCE")

    fig, axes = plt.subplots(2, 3, figsize=(15.2, 8.8), layout="constrained")
    ax = axes[0,0]
    for h, label in ((acc, "LRS accepted"), (histories["nominal:ci_flrw"]["accepted"], "FLRW accepted")):
        plot_time(ax, h, "H1_CI_core_log10_q_cm3_s", label=label)
    ax.axhline(math.log10(float(np.nextafter(0.,1.))), color=".5", ls="--", label="float64 min subnormal")
    ax.set_ylabel(r"$\log_{10}(q_{CI,finite}/[cm^3s^{-1}])$")
    ax.set_title("Finite source log rates survive underflow"); ax.legend(fontsize=7)
    ax = axes[0,1]
    plot_time(ax, acc, "H1_CI_events_per_H_per_eta", label="PL on observed LRS path", color="#087b8c")
    ax.set_yscale("symlog", linthresh=1e-20); ax.set_ylabel("CI events / Href / eta")
    ax.set_title("New CI event activity"); ax.legend(fontsize=7)
    ax = axes[0,2]
    plot_time(ax, acc, "CI_first_gap_PL_fraction", label="first gap fraction in PL integral")
    plot_time(ax, acc, "CI_first_gap_p1127_to_PL_rate_ratio", label="p1.127 / PL rate")
    ax.set_ylabel("Dimensionless ratio"); ax.set_title("First0.0342eV shape sensitivity")
    ax.legend(fontsize=7)
    ax = axes[1,0]
    for name in ("ci_lrs", "ci_flrw"):
        plot_time(ax, histories["nominal:"+name]["accepted"], "CI_ground_conditional_threebody_over_RR", label=name)
    ax.set_yscale("log"); ax.set_ylabel(r"Actual $n_e K_3/\alpha_{RR}$")
    ax.set_title("Conditional ground inverse; no all-level bound"); ax.legend(fontsize=7)
    ax = axes[1,1]
    for key, label in (("H1_CI_events_per_H", "ODE event counter"),
        ("CI_fixed_path_PL_trapezoid_events_per_H", "same-path PL trapezoid"),
        ("CI_fixed_path_p1127_trapezoid_events_per_H", "same-path p1.127 trapezoid")):
        plot_time(ax, acc, key, label=label)
    ax.set_ylabel("CI events / Href"); ax.set_title("Fixed path only; no sensitivity reintegration")
    ax.legend(fontsize=7)
    ax = axes[1,2]
    plot_time(ax, acc, "CI_implied_temperature_prime_K_per_eta", label="implied CI contribution")
    ax.set_yscale("symlog", linthresh=1e-10)
    ax.set_ylabel("CI temperature derivative [K / eta]")
    ax.set_title("Includes particle-count term exactly once"); ax.legend(fontsize=7)
    for ax in axes.flat:
        axis(ax)
    fig.suptitle("C22D finite CI diagnostics: source-model sensitivity and conditional inverse scale\n"
                 "Neither curve supplies physical tail/interpolation bounds or a complete thermochemical/radiative closure")
    save(fig, "CI_SOURCE_AND_CONDITIONAL_DIAGNOSTICS")
    return figures_written


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nominal", type=Path, default=HERE/"runs/c22d_h1_ci_bdf_20261022_v1")
    parser.add_argument("--reference", type=Path, default=HERE/"runs/c22d_h1_ci_radau_20261022_v1")
    parser.add_argument("--baseline", type=Path, default=C22C/"runs/c22c_h1_excitation_bdf_20261022_v1")
    parser.add_argument("--output", type=Path, default=HERE/"analysis_v1")
    args = parser.parse_args()
    started_utc, wall0, cpu0 = utc(), time.perf_counter(), time.process_time()
    contract = json.loads((HERE/"CONTRACT.json").read_bytes())
    nominal, reference, old = read_run(args.nominal), read_run(args.reference), read_run(args.baseline)
    verify_registered(nominal, contract, "nominal"); verify_registered(reference, contract, "reference")
    identity = nominal["source"]["identity_sha256"]
    if reference["source"]["identity_sha256"] != identity:
        raise ValueError("NOMINAL_REFERENCE_SOURCE_IDENTITIES_DIFFER")
    if old["source"]["identity_sha256"] != contract["parent_C22C_source_identity"]:
        raise ValueError("OLD_C22C_SOURCE_IDENTITY_MISMATCH")
    comparison_binding = verify_old_baseline(old, nominal)
    for row in nominal["source"]["files"]:
        path = REPO / row["path"]
        if path.stat().st_size != row["size_bytes"] or sha256(path) != row["sha256"]:
            raise ValueError("CURRENT_MODEL_NOT_THE_RUN_SOURCE:"+row["path"])
    raw_pins = [r["raw_pin"] for run in (nominal, reference) for r in run["rows"].values()]
    baseline = old["rows"]["finite_uv_excitation_lrs"]["history"]
    raw_pins.append(old["rows"]["finite_uv_excitation_lrs"]["raw_pin"])
    out = args.output.resolve()
    lease_records = []
    for lease_path in sorted(Path("/tmp/rei-bianchi-cooperative-leases").glob("*.json")):
        data = json.loads(lease_path.read_bytes())
        lease_records.append({"path": str(lease_path), "sha256": sha256(lease_path),
            "cpus": data.get("cpus", data.get("reserved_cpus", data.get("allocated_cpus"))),
            "status": data.get("status"), "expires_utc": data.get("expires_utc")})
    # Parent allocates CPU3 explicitly.  A nonempty changed registry is surfaced
    # for reconciliation, never silently expired or overridden by this analyzer.
    if lease_records:
        raise RuntimeError("ANALYSIS_LEASE_REGISTRY_CHANGED_RECONCILE_WITH_COORDINATOR:"+
                           json.dumps(lease_records, sort_keys=True))
    resource = {"started_utc": started_utc, "affinity_before": sorted(os.sched_getaffinity(0)),
        "thread_env": {k: os.environ[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")},
        "cpu_max": Path("/sys/fs/cgroup/cpu.max").read_text().strip(),
        "memory_max_bytes": int(Path("/sys/fs/cgroup/memory.max").read_text()),
        "memory_current_start_bytes": int(Path("/sys/fs/cgroup/memory.current").read_text()),
        "lease_records_observed": lease_records,
        "parent_allocation": "CPU3 single-thread post-run analysis; no new ODE"}
    if 3 not in os.sched_getaffinity(0):
        raise RuntimeError("CPU3_ANALYSIS_ALLOCATION_UNAVAILABLE")
    if resource["memory_max_bytes"]-resource["memory_current_start_bytes"] < 512*1024**2:
        raise RuntimeError("ANALYSIS_MEMORY_HEADROOM_BELOW512MIB")
    os.sched_setaffinity(0, {3}); resource["affinity_during"] = sorted(os.sched_getaffinity(0))
    out.mkdir(parents=True, exist_ok=False)
    os.environ["MPLCONFIGDIR"] = str(out/"matplotlib_cache")
    analyzer_pin = pin(__file__)
    theory_source = REPO.parents[3]/"c22d_20261022/theory/check_ci_delta.py"
    theory_pin = pin(theory_source) if theory_source.exists() else {"status": "UNAVAILABLE", "path": str(theory_source)}
    json_create(out/"STARTED.json", {"schema": "C22D_ANALYSIS_START_V1", "resource": resource,
        "analyzer_pin": analyzer_pin, "contract_pin": pin(HERE/"CONTRACT.json"), "raw_pins": raw_pins,
        "conditional_diagnostic_formula_source": theory_pin,
        "comparison_input_binding": comparison_binding,
        "source_identity_sha256": identity, "global_error_bound": None})
    try:
        import scipy.integrate
        solver_attempts = []
        def forbidden_solver(*args, **kwargs):
            solver_attempts.append(True); raise RuntimeError("ANALYSIS_ODE_FORBIDDEN")
        scipy.integrate.solve_ivp = forbidden_solver
        spec = importlib.util.spec_from_file_location("c22d_analysis_model", HERE/"model.py")
        module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
        factory = module.ThermochemicalFactory()
        histories, audits, endpoint_rows, history_rows = {}, {}, [], []
        for role, run in (("nominal", nominal), ("reference", reference)):
            for name, row in run["rows"].items():
                model = factory.build(row["case"])
                saved = {k: v for k, v in row["history"].items() if not k.startswith("accepted_")}
                accepted = summarize_without_rhs(model, row["history"]["accepted_eta"], row["history"]["accepted_Y"])
                saved = additional_diagnostics(saved, model, module._ci)
                accepted = additional_diagnostics(accepted, model, module._ci)
                key = role+":"+name
                histories[key] = {"saved": saved, "accepted": accepted}
                audits[key] = {"saved": mesh_audit(saved, model, contract["preregistered_gates"], module._ci),
                               "accepted": mesh_audit(accepted, model, contract["preregistered_gates"], module._ci)}
                npz_create(out/(role+"_"+name+"_ACCEPTED.npz"), accepted)
                npz_create(out/(role+"_"+name+"_SAVED_DIAGNOSTICS.npz"), {
                    k: v for k, v in saved.items() if k.startswith("CI_") or k in ("eta", "H1_minus_D_ionized_fraction", "gas_particles_per_Href")})
                selected = (*COMMON_COMPARISON, "H1_CI_events_per_H", "H1_CI_core_log10_q_cm3_s",
                    "CI_ground_conditional_threebody_over_RR", "CI_first_gap_p1127_to_PL_rate_ratio",
                    "CI_fixed_path_PL_trapezoid_events_per_H", "CI_fixed_path_p1127_trapezoid_events_per_H",
                    "H1_minus_D_ionized_fraction", *LEDGERS)
                for i in range(len(saved["eta"])):
                    history_rows.append({"role": role, "case": name, "index": i, "eta": float(saved["eta"][i]),
                        "z": float(saved["z"][i]), "proper_elapsed_Myr": float(saved["proper_elapsed_s"][i]/MYR),
                        **{k: float(saved[k][i]) for k in selected}})
                endpoint_rows.append({"role": role, "case": name,
                    **{k: float(saved[k][-1]) for k in selected}})
                json_create(out/(role+"_"+name+"_AUDIT.json"), audits[key])
                print(json.dumps({"case_analyzed": key, "saved": len(saved["eta"]), "accepted": len(accepted["eta"]),
                    "status": {k: v["status"] for k, v in audits[key].items()}}, default=json_default), flush=True)
        on = histories["nominal:ci_lrs"]["saved"]
        off = histories["nominal:registry_control_lrs"]["saved"]
        ref = histories["reference:ci_lrs"]["saved"]
        ref_report, ref_arrays = reference_comparison(on, ref, contract)
        effects = {"CI_same_registry": effect_comparison(on, off, "CI ON minus CI OFF; same new energy registry"),
                   "registry_only": effect_comparison(off, baseline, "new-registry CI OFF minus old C22C stored LRS")}
        json_create(out/"STRICT_REFERENCE.json", ref_report)
        json_create(out/"MATCHED_EFFECTS.json", effects)
        npz_create(out/"STRICT_REFERENCE_ARRAYS.npz", ref_arrays)
        csv_create(out/"HISTORY.csv", history_rows); csv_create(out/"ENDPOINTS.csv", endpoint_rows)
        csv_create(out/"STRICT_REFERENCE.csv", [
            {"eta": float(ref_arrays["eta"][i]), **{k: float(v[i]) for k, v in ref_arrays.items() if k != "eta"}}
            for i in range(len(ref_arrays["eta"]))])
        plots = figures(out, histories, baseline, ref_arrays, contract)
        raw_unchanged = all(pin(row["path"]) == row for row in raw_pins)
        sources_unchanged = all(sha256(REPO/r["path"]) == r["sha256"] for r in nominal["source"]["files"])
        analyzer_unchanged = analyzer_pin == pin(__file__)
        mesh_pass = all(a[mesh]["status"] == "PASS_SCOPED" for a in audits.values() for mesh in ("saved", "accepted"))
        passed = mesh_pass and ref_report["status"] == "PASS_SCOPED" and raw_unchanged and sources_unchanged and analyzer_unchanged and not solver_attempts
        resource.update(finished_utc=utc(), wall_seconds=time.perf_counter()-wall0,
            cpu_seconds=time.process_time()-cpu0,
            actual_native_threads=int(next(x.split(":",1)[1] for x in Path("/proc/self/status").read_text().splitlines() if x.startswith("Threads:"))),
            memory_current_finish_bytes=int(Path("/sys/fs/cgroup/memory.current").read_text()))
        summary = {"schema": "C22D_ANALYSIS_V1", "status": "PASS_SCOPED" if passed else "FAIL_PRESERVED",
            "analyzer_pin": analyzer_pin, "analyzer_bytes_unchanged": analyzer_unchanged,
            "conditional_diagnostic_formula_source": theory_pin, "contract_pin": pin(HERE/"CONTRACT.json"),
            "comparison_input_binding": comparison_binding,
            "source_identity_sha256": identity, "parent_C22C_source_identity": old["source"]["identity_sha256"],
            "audits": audits, "reference": ref_report, "effects": effects, "resource": resource,
            "raw_pins": raw_pins, "raw_bytes_unchanged": raw_unchanged, "runtime_source_bytes_unchanged": sources_unchanged,
            "new_accepted_summaries": 4, "old_C22C_summary_recomputations": 0, "model_RHS_calls": 0,
            "analysis_ODE_calls": 0, "old_ODE_reruns": 0, "new_ODE_in_this_analysis": 0,
            "figures": plots, "figure_visual_inspection": "PENDING_ACTUAL_IMAGE_VIEW",
            "numerical_acceptance": "finite saved+accepted meshes and nine-field tighter Radau comparison; no gate relaxed",
            "fixed_path_sensitivity": "Only first-gap cross-section shape changes on the same observed path; trapezoid quadrature; not a feedback trajectory or error bound",
            "conditional_inverse": "Ground finite-source Saha inverse with d=1 and R3=K3*ne^2*np; uses actual ne; all-level inverse and omission bound OPEN",
            "failure_scope": {"all_gate_failures_preserved": not passed,
                "historical_external127_JSON_reintegration": "PRESERVED", "VigilODE_P02_C6": "FAIL_PRESERVED",
                "inaccessible_conversations": "UNAVAILABLE", "original_nuclear_network_png": "NOT_RECOVERED_NOT_READ"},
            "global_error_bound": None, "stage": {"EXECUTION": "NEW_RUN_ARRAY_ANALYSIS_COMPLETE_SCOPED",
                "PUBLICATION": "PENDING_PARENT_PACKAGE", "BACKUP": "PENDING_PARENT_PACKAGE",
                "DAG": "C22D scoped acceptance depends on recorded gates; full thermochemical/radiative closure OPEN; nuclear/general geometry HOLD"}}
        json_create(out/"SUMMARY.json", summary)
        json_create(out/"ARTIFACT_MANIFEST.json", {"analyzer_sha256": sha256(__file__),
            "source_identity_sha256": identity, "files": [pin(p) for p in sorted(out.iterdir()) if p.is_file()],
            "global_error_bound": None})
        print(json.dumps({"status": summary["status"], "reference": ref_report,
            "mesh_gate_failures": {name+":"+mesh: [k for k,v in a[mesh]["checks"].items() if not v]
                for name,a in audits.items() for mesh in ("saved","accepted") if a[mesh]["status"] != "PASS_SCOPED"},
            "resource": resource}, default=json_default), flush=True)
        return 0 if passed else 2
    except Exception as exc:
        json_create(out/"FAILURE.json", {"status": "FAILED_PRESERVED", "utc": utc(),
            "analyzer_pin": pin(__file__), "exception_type": type(exc).__name__, "message": str(exc),
            "traceback": traceback.format_exc(), "raw_pins": raw_pins,
            "created_files": [str(p.name) for p in sorted(out.iterdir()) if p.is_file()],
            "analysis_ODE_calls": 0, "old_ODE_reruns": 0, "global_error_bound": None,
            "stage": {"EXECUTION": "ANALYSIS_FAILED_PRESERVED", "PUBLICATION": "NOT_ATTEMPTED",
                      "BACKUP": "PENDING_PARENT_PACKAGE", "DAG": "REPAIR_ANALYSIS_ONLY; do not rerun completed ODE"}})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
