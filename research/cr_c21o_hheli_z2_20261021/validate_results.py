#!/usr/bin/env python3
"""Read-only validation of completed C21O grid45 and controls6.

No solver, RHS, moment-field reconstruction, old campaign or benchmark is run.
Identity and saved-array algebra/invariants have explicit scoped criteria.
Solver, angular-truncation and Thomson-model differences are measurements;
none is promoted to a continuous/global error bound or an arbitrary PASS.
"""
from __future__ import annotations

import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_key] = "1"

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy
from scipy.constants import atomic_mass

from atomic_network import AtomicNetwork21

HERE = Path(__file__).resolve().parent
EPS = np.finfo(np.float64).eps
G_SI = 6.67430e-11  # Frozen lrs_boltzmann.py/source convention.
C_SI = 299792458.0
KAPPA_TIME = 8. * math.pi * G_SI / C_SI**2
CRITERIA = {
    "source_history_receipt_case_bindings": "exact SHA256/bytes/JSON values",
    "state_dtype": "float64", "L8_shape": [62, 201], "L12_shape": [78, 201],
    "saved_time_coordinate_absolute_tolerance": 64 * EPS,
    "derived_array_roundoff_budget": "64*eps*(abs(left)+abs(right)); exact when both zero",
    "initial_signed_axis_absolute_tolerance": 2e-13,
    "isotope_total_relative_tolerance": 2e-9,
    "baryon_relative_tolerance": 2e-9,
    "shared_electronic_isotope_fraction_absolute_tolerance": 2e-9,
    "n_and_T": "exact zero at all saved times; declared zero initial parents/no production",
    "minimum_scaled_atomic_population": -2e-10,
    "radiation_number_l0_absolute_tolerance": 2e-10,
    "angular_sample_minimum": -2e-10,
    "angular_grid": "1025 equally spaced mu in[-1,1], at every201 saved time; not global positivity",
    "solver_L_and_model_comparisons": "reported differences only; no acceptance threshold/error bound",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def canonical_sha(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def max_abs(values):
    return float(np.max(np.abs(values)))


def array_relation(left, right):
    """Measured floating algebra difference with a dimensionally local budget."""
    left, right = np.asarray(left), np.asarray(right)
    require(left.shape == right.shape, "ALGEBRA_SHAPE_MISMATCH")
    delta = np.abs(left - right)
    scale = np.abs(left) + np.abs(right)
    allowed = 64. * EPS * scale
    ratio = np.divide(delta, scale, out=np.zeros_like(delta, dtype=float), where=scale > 0)
    return {"pass": bool(np.all(delta <= allowed)), "max_absolute_difference": float(np.max(delta)),
            "max_relative_to_sum_absolute": float(np.max(ratio))}


def source_binding(manifest):
    src = manifest["source"]
    payload = {k: v for k, v in src.items() if k != "identity_sha256"}
    require(canonical_sha(payload) == src["identity_sha256"], "SOURCE_CANONICAL_IDENTITY_MISMATCH")
    require(src["original_LRS_source_commit"] == "3b85dedce84d37b3e165da00685a8a984950aafe", "UNEXPECTED_LRS_SOURCE")
    require(src["rtol"] == 3e-11 and src["atol"] == 3e-13, "UNEXPECTED_TOLERANCES")
    require(src["default_n_output"] == 201 and src["z_start"] == 20. and src["z_end"] == 2., "UNEXPECTED_DOMAIN")
    records = []
    for record in src["files"]:
        relative = Path(record["path"])
        require(not relative.is_absolute() and ".." not in relative.parts, "UNSAFE_SOURCE_PATH")
        path = HERE.parent / relative
        require(path.stat().st_size == record["size"] and sha(path) == record["sha256"], "SOURCE_FILE_MISMATCH:" + str(relative))
        records.append({"path": str(relative), "sha256": record["sha256"], "size": record["size"]})
    # The source manifest pins the entire original kinetic closure, including
    # its supplier lock. Verify those bytes without rebuilding old FV fields.
    ancestor = HERE.parent / "cr_c21l_rei_pilot_20261021"
    old = read_json(ancestor / "SOURCE_MANIFEST.json")
    for record in old["files"]:
        path = ancestor / "vendor/rei" / record["path"]
        require(path.stat().st_size == record["size"] and sha(path) == record["sha256"], "ORIGINAL_KINETIC_DEPENDENCY_MISMATCH:" + record["path"])
    return {"identity_sha256": src["identity_sha256"], "source_files_verified": records,
            "original_dependency_files_verified": len(old["files"]), "execution_build": {
                k: manifest[k] for k in ("python", "numpy", "scipy", "host")}}


def load_run(directory, expected_count):
    directory = Path(directory).resolve()
    manifest_path = directory / "MANIFEST.json"
    manifest = read_json(manifest_path)
    binding = source_binding(manifest)
    cases = manifest["grid"]["cases"]
    require(len(cases) == expected_count, "UNEXPECTED_CASE_COUNT")
    ids = [case["case_id"] for case in cases]
    require(len(set(ids)) == len(ids), "DUPLICATE_CASE_IDS")
    result = {}
    for case in cases:
        case_id = case["case_id"]
        require(case_id.replace("_", "").isalnum(), "UNSAFE_CASE_ID")
        path = directory / "cases" / case_id
        for name in ("history.npz", "RECEIPT.json", "COMPLETE.json", "STARTED.json"):
            require((path / name).is_file(), "CASE_NOT_COMPLETED:" + case_id + ":" + name)
        receipt, complete, started = (read_json(path / name) for name in ("RECEIPT.json", "COMPLETE.json", "STARTED.json"))
        raw_hash = sha(path / "history.npz")
        receipt_hash = sha(path / "RECEIPT.json")
        for record in (receipt, complete, started):
            require(record["source_identity_sha256"] == binding["identity_sha256"], "CASE_SOURCE_BINDING:" + case_id)
        require(receipt["case"] == started["case"] == case, "CASE_INPUT_BINDING:" + case_id)
        require(complete["receipt_sha256"] == receipt_hash, "RECEIPT_HASH:" + case_id)
        require(complete["history_sha256"] == receipt["history_sha256"] == raw_hash, "RAW_HASH:" + case_id)
        require(receipt["history_bytes"] == (path / "history.npz").stat().st_size, "RAW_SIZE:" + case_id)
        require(receipt["status"] == complete["status"] == "PASS_SCOPED", "CASE_NOT_PASS:" + case_id)
        require(receipt["method"] == case["method"] and receipt["ellmax"] == case["ellmax"], "SOLVER_OR_ELL_BINDING:" + case_id)
        require(receipt["rtol"] == manifest["source"]["rtol"] and receipt["atol"] == manifest["source"]["atol"], "CASE_TOLERANCE:" + case_id)
        require(receipt["thomson_moment_feedback"] == case["thomson"] and receipt["analytic_jacobian"] is True, "MODEL_BINDING:" + case_id)
        with np.load(path / "history.npz", allow_pickle=False) as loaded:
            arrays = {k: loaded[k] for k in loaded.files}
        result[case_id] = {"case": case, "receipt": receipt, "arrays": arrays,
                           "input_files": {"history_sha256": raw_hash, "history_bytes": receipt["history_bytes"],
                                           "receipt_sha256": receipt_hash, "complete_sha256": sha(path / "COMPLETE.json"),
                                           "started_sha256": sha(path / "STARTED.json")},
                           "raw_path": path / "history.npz"}
    return manifest, binding, result, {"path": str(directory), "manifest_sha256": sha(manifest_path),
                                      "cases": len(cases), "grid_canonical_sha256": canonical_sha(manifest["grid"])}


def cosmology_constants():
    path = HERE.parent / "cr_c21l_rei_pilot_20261021/vendor/rei/research/rei_bass_hierarchy_backreaction_20261015/suppliers/bass/rei_axbi_background_supplier_20261015/source/REI_BACKGROUND_FAMILY_LOCK.json"
    lock = read_json(path)
    cosmo, clock = lock["cosmology"], lock["clock"]
    h0, aref = cosmo["H0_per_s"], clock["a_ref"]
    href = h0 * math.sqrt(cosmo["Omega_m"] / aref**3 + cosmo["Omega_r"] / aref**4 + cosmo["Omega_lambda"])
    return {"lock_sha256": sha(path), "h0_s_inverse": h0, "href_s_inverse": href,
            "Omega_b": cosmo["Omega_b"], "a_ref": aref,
            "rhocrit_J_m3": 3. * C_SI**2 * h0**2 / (8. * math.pi * G_SI),
            "atomic_mass_kg": float(atomic_mass), "mass_approximation": "A*m_u", "cm3_to_m3": 1e6}


def validate_case(record, network, cosmo, basis_by_ell):
    h, case, receipt = record["arrays"], record["case"], record["receipt"]
    ell, nsaved = case["ellmax"], 201
    n, nk = ell + 1, 4 + 4 * (ell + 1)
    require(ell in (8, 12), "UNEXPECTED_ELL")
    require(h["Y"].shape == (nk + 22, nsaved) and h["Y"].dtype == np.float64, "FULL_STATE_SHAPE_OR_DTYPE")
    require(receipt["state_shape"] == [nk + 22, nsaved], "RECEIPT_STATE_SHAPE")
    require(tuple(h["atomic_state_labels"].tolist()) == network.state_labels, "ATOMIC_REGISTRY")
    finite_count = 0
    for name, array in h.items():
        if array.dtype.kind in "fc":
            require(array.dtype == np.float64, "NON_FP64_SAVED_ARRAY:" + name)
            if name != "cancellation_fraction":
                require(np.all(np.isfinite(array)), "NONFINITE_SAVED_ARRAY:" + name)
            finite_count += array.size
    require(h["atomic_scaled"].shape == h["atomic_abundance_per_Href"].shape == (21, nsaved), "ATOMIC_SHAPE")
    require(np.array_equal(h["atomic_scaled"], h["Y"][nk:-1]), "ATOMIC_Y_BINDING")
    require(np.array_equal(h["tau_T"], h["Y"][-1]), "TAU_Y_BINDING")
    for j, name in enumerate(("E_gamma", "N_gamma", "E_nu", "N_nu")):
        require(h[name].shape == (nsaved, n), "MOMENT_SHAPE:" + name)
        require(np.array_equal(h[name].T, h["Y"][4 + j*n:4 + (j+1)*n]), "MOMENT_Y_BINDING:" + name)
    eta_expected = np.linspace(0., math.log(7.), nsaved)
    time_error = max_abs(h["eta"] - eta_expected)
    endpoint_error = max(abs(float(h["z"][0]) - 20.), abs(float(h["z"][-1]) - 2.))
    criteria = {"time_grid": time_error <= 64 * EPS, "redshift_endpoints": endpoint_error <= 64 * EPS,
                "positive_expansion": bool(np.all(h["H"] > 0.))}
    relations = {}
    def rel(name, left, right):
        relation = array_relation(left, right)
        relations[name] = relation
        criteria[name] = relation["pass"]
    rel("redshift_scale_factor", h["z"], 1. / h["a"] - 1.)
    rel("scale_factor_eta", h["a"], cosmo["a_ref"] * np.exp(h["eta"]))
    rel("proper_elapsed_time", h["proper_elapsed_s"], h["Y"][0] / cosmo["href_s_inverse"])
    rel("source_shear_clock", h["s"], h["Y"][2] * cosmo["href_s_inverse"])
    rel("shear_tensor", h["sigma_orthonormal_diagonal_s_inverse"], np.stack((-h["s"], -h["s"], 2*h["s"]), axis=1))
    rel("signed_full_shear", h["signed_Sigma_F"], math.sqrt(6) * h["s"] / h["H"])
    rel("full_shear_norm", h["Sigma_F"], np.linalg.norm(h["sigma_orthonormal_diagonal_s_inverse"], axis=1) / h["H"])
    rel("shear_full_half", h["Sigma_F"], math.sqrt(2.) * h["Sigma_half"])
    for sector in ("m", "gamma", "nu", "r", "tot"):
        pressure = h[f"p_{sector}_J_m3"]
        tensor = h[f"pi_{sector}_orthonormal_diagonal_J_m3"]
        signed, norm = h[f"signed_Pi_{sector}_F"], h[f"Pi_{sector}_F"]
        rel(sector + "_tensor", tensor, np.stack((-pressure, -pressure, 2*pressure), axis=1))
        rel(sector + "_pressure_difference", h[f"delta_p_{sector}_J_m3"], 3. * pressure)
        rel(sector + "_signed_full", signed, math.sqrt(6.) * KAPPA_TIME * pressure / h["H"]**2)
        rel(sector + "_norm_sign", norm, np.abs(signed))
        rel(sector + "_tensor_norm", norm, KAPPA_TIME * np.linalg.norm(tensor, axis=1) / h["H"]**2)
        rel(sector + "_full_half", norm, math.sqrt(2.) * h[f"Pi_{sector}_half"])
    rel("radiation_tensor_sum", h["pi_r_orthonormal_diagonal_J_m3"], h["pi_gamma_orthonormal_diagonal_J_m3"] + h["pi_nu_orthonormal_diagonal_J_m3"])
    rel("total_tensor_sum", h["pi_tot_orthonormal_diagonal_J_m3"], h["pi_m_orthonormal_diagonal_J_m3"] + h["pi_r_orthonormal_diagonal_J_m3"])
    # Cancellation may amplify relative roundoff in signed normalized sums.
    # Test the identity against the component magnitude, not its near-zero sum.
    normalized_residual = h["signed_Pi_tot_F"] - (h["signed_Pi_m_F"] + h["signed_Pi_r_F"])
    normalized_scale = np.abs(h["signed_Pi_m_F"]) + np.abs(h["signed_Pi_r_F"])
    criteria["signed_total_component_sum"] = bool(np.all(np.abs(normalized_residual) <= 64*EPS*normalized_scale))
    denominator = np.abs(h["p_m_J_m3"]) + np.abs(h["p_r_J_m3"])
    defined = denominator > 0.
    cancellation = np.full(nsaved, np.nan)
    cancellation[defined] = 1. - np.abs(h["p_tot_J_m3"][defined]) / denominator[defined]
    criteria["cancellation_defined_mask"] = bool(np.array_equal(np.isnan(h["cancellation_fraction"]), ~defined))
    criteria["cancellation_values"] = bool(np.allclose(h["cancellation_fraction"][defined], cancellation[defined], atol=64*EPS, rtol=0.))
    abundance = network.scales[:, None] * h["atomic_scaled"]
    require(np.array_equal(abundance, h["atomic_abundance_per_Href"]), "ATOMIC_PHYSICAL_SCALE_BINDING")
    isotope = {}
    for name, indices in network.blocks.items():
        total = np.sum(abundance[list(indices)], axis=0)
        expected = network.initial_nucleus_totals[name]
        if expected == 0.:
            offset = max_abs(total)
            passed = bool(np.all(abundance[list(indices)] == 0.))
            isotope[name] = {"initial_total": 0., "max_absolute_total": offset, "all_states_exact_zero": passed}
        else:
            offset = max_abs(total / expected - 1.)
            passed = offset <= 2e-9
            isotope[name] = {"initial_total": expected, "max_relative_total_residual": offset}
        criteria["isotope_" + name] = passed
    baryons = network.A @ abundance
    bref = float(network.A @ network.physical_abundances(network.initial_state()))
    baryon_res = max_abs(baryons / bref - 1.)
    criteria["baryon_conservation"] = baryon_res <= 2e-9
    li_difference = max_abs(h["atomic_scaled"][list(network.blocks["Li6"])] - h["atomic_scaled"][list(network.blocks["Li7"])])
    criteria["Li6_Li7_shared_electronic_fraction"] = li_difference <= 2e-9
    ne_reconstructed = h["nH_ref_cm3"] * (network.q @ abundance)
    rel("algebraic_electron_closure", h["n_e_cm3"], ne_reconstructed)
    nref0 = cosmo["Omega_b"] * cosmo["rhocrit_J_m3"] / C_SI**2 / atomic_mass / bref / 1e6
    rel("proper_reference_mass_units", h["nH_ref_cm3"], nref0 / h["a"]**3)
    minimum_atomic = float(np.min(h["atomic_scaled"]))
    criteria["atomic_positivity_scoped"] = minimum_atomic >= -2e-10
    number_res = max(max_abs(h[key][:, 0] - 1.) for key in ("N_gamma", "N_nu"))
    criteria["radiation_number"] = number_res <= 2e-10
    weights = 2 * np.arange(n) + 1
    angular_min = min(float(np.min((h[key] * weights) @ basis_by_ell[ell].T)) for key in ("E_gamma", "N_gamma", "E_nu", "N_nu"))
    criteria["radiation_angular_sample_positivity"] = angular_min >= -2e-10
    initial_errors = {field: abs(float(h[field][0]) - case[target]) for field, target in
                      (("signed_Sigma_F", "signed_sigma"), ("signed_Pi_m_F", "signed_pi_m"), ("signed_Pi_r_F", "signed_pi_r"))}
    criteria["initial_physical_targets"] = max(initial_errors.values()) <= 2e-13
    mapping = receipt["initial_mapping"]
    for field in ("signed_Sigma_F", "signed_Pi_m_F", "signed_Pi_r_F", "signed_Pi_tot_F"):
        require(float(h[field][0]).hex() == float(mapping["actual"][field]).hex(), "INITIAL_ACTUAL_MAPPING_BYTES:" + field)
    norm_sum_excess = h["Pi_m_F"] + h["Pi_r_F"] - h["Pi_tot_F"]
    return {"case_id": case["case_id"], "status": "PASS_SCOPED" if all(criteria.values()) else "FAIL_SCOPED",
            "failed_criteria": [key for key, passed in criteria.items() if not passed],
            "input_files": record["input_files"], "state_shape": list(h["Y"].shape),
            "finite_FP64_values_inspected": finite_count, "derived_relations": relations,
            "checks": {"time_grid_max_absolute": time_error, "redshift_endpoint_max_absolute": endpoint_error,
                       "isotope_totals": isotope, "baryon_max_relative": baryon_res,
                       "Li6_Li7_max_absolute_fraction_difference": li_difference,
                       "minimum_scaled_atomic_state": minimum_atomic,
                       "radiation_number_max_absolute": number_res,
                       "minimum_radiation_on_1025_mu_samples": angular_min,
                       "angular_values_inspected": 4 * 201 * 1025,
                       "initial_target_absolute_errors": initial_errors,
                       "initial_signed_total_offset_preserved": float(h["signed_Pi_tot_F"][0]),
                       "largest_norm_sum_minus_total_norm": float(np.max(norm_sum_excess)),
                       "signed_total_roundoff_max_absolute": max_abs(normalized_residual)},
            "source_receipt_diagnostics_reused": receipt["diagnostics"],
            "reuse_scope": "Hamiltonian and massive-packet number/normalization use bound execution receipt; no RHS/moment fields reevaluation"}


def difference_summary(a, b, atol, rtol, names=None):
    a, b = np.asarray(a), np.asarray(b)
    require(a.shape == b.shape and np.all(np.isfinite(a)) and np.all(np.isfinite(b)), "COMPARISON_SHAPE_OR_FINITE")
    delta = np.abs(a - b)
    scale = atol + rtol * np.maximum(np.abs(a), np.abs(b))
    out = {"max_absolute_difference": float(np.max(delta)),
           "max_scaled_by_local_atol_plus_rtol_state": float(np.max(delta / scale)),
           "atol": atol, "rtol": rtol,
           "criterion": "DIAGNOSTIC_ONLY;local_solver_tolerances_are_not_global_error_bounds"}
    if names is not None:
        out["by_state"] = [{"name": name, "max_absolute_difference": float(np.max(delta[j])),
                            "endpoint_absolute_difference": float(delta[j, -1]),
                            "max_scaled_difference": float(np.max(delta[j] / scale[j]))}
                           for j, name in enumerate(names)]
    return out


def state_names(network, ell=8):
    return (["elapsed_time_times_href", "b", "s_over_href", "unused_u"]
            + [f"{sector}_ell{j}" for sector in ("E_gamma", "N_gamma", "E_nu", "N_nu") for j in range(ell + 1)]
            + list(network.state_labels) + ["tau_T"])


def comparisons(grid, controls, network):
    for collection in (grid, controls):
        for record in collection.values():
            require(np.array_equal(record["arrays"]["eta"], grid["grid022"]["arrays"]["eta"]), "COMPARISON_TIME_GRID_MISMATCH")
    flrw = difference_summary(grid["grid022"]["arrays"]["Y"], controls["flrw_radau"]["arrays"]["Y"], 3e-13, 3e-11, state_names(network))
    flrw["pair"] = ["grid022_BDF_L8", "flrw_radau_L8"]
    fields = ("H", "b", "s", "signed_Sigma_F", "Sigma_F", "signed_Pi_m_F", "signed_Pi_r_F", "signed_Pi_tot_F",
              "Pi_m_F", "Pi_r_F", "Pi_tot_F", "n_e_cm3", "tau_T", "proper_elapsed_s", "atomic_scaled")
    angular = {}
    for grid_id, control_id in (("grid000", "negative_extreme_L12"), ("grid044", "positive_extreme_L12")):
        a, b = grid[grid_id]["arrays"], controls[control_id]["arrays"]
        common = {key: difference_summary(a[key], b[key], 3e-13, 3e-11) for key in fields}
        for key in ("E_gamma", "N_gamma", "E_nu", "N_nu"):
            common[key + "_first9"] = difference_summary(a[key], b[key][:, :9], 3e-13, 3e-11)
        angular[control_id] = {"pair": [grid_id + "_L8", control_id], "status": "TRUNCATION_SENSITIVITY_REPORTED",
                               "not_established": "No infinite-hierarchy convergence or global truncation bound", "differences": common}
    on, off = grid["grid044"]["arrays"], controls["positive_extreme_thomson_off"]["arrays"]
    thomson = {"pair": ["grid044_Thomson_on", "positive_extreme_thomson_off"],
               "status": "CHANGED_PHYSICAL_MODEL_DIFFERENCE;not_an_accuracy_verdict",
               "differences": {key: difference_summary(on[key], off[key], 3e-13, 3e-11) for key in fields},
               "physical_tau_retained_in_off_case": True}
    cancellation = {}
    for case_id in ("cancellation_mplus", "cancellation_mminus"):
        a = controls[case_id]["arrays"]
        cancellation[case_id] = {
            "requested": {k: controls[case_id]["case"][k] for k in ("signed_sigma", "signed_pi_m", "signed_pi_r")},
            "actual_initial": {k: float(a[k][0]) for k in ("signed_Sigma_F", "signed_Pi_m_F", "signed_Pi_r_F", "signed_Pi_tot_F", "cancellation_fraction")},
            "endpoint": {k: float(a[k][-1]) for k in ("signed_Sigma_F", "signed_Pi_m_F", "signed_Pi_r_F", "signed_Pi_tot_F", "cancellation_fraction")},
            "max_total_norm": float(np.max(a["Pi_tot_F"])),
            "scope": "actual tiny signed initial offsets retained;no forced zero or exact persistent cancellation"}
    return {"FLRW_BDF_vs_Radau": flrw, "L8_vs_L12": angular, "Thomson_on_vs_off": thomson,
            "initial_cancellation_controls": cancellation}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--grid-run", type=Path, required=True)
    p.add_argument("--control-run", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    require(not args.output.exists(), "CREATE_ONLY_OUTPUT_ALREADY_EXISTS")
    began = time.perf_counter()
    grid_manifest, grid_binding, grid, grid_meta = load_run(args.grid_run, 45)
    ctl_manifest, ctl_binding, controls, ctl_meta = load_run(args.control_run, 6)
    require(grid_binding["identity_sha256"] == ctl_binding["identity_sha256"], "GRID_CONTROL_SOURCE_MISMATCH")
    require(grid_manifest["source"] == ctl_manifest["source"], "GRID_CONTROL_FULL_SOURCE_MISMATCH")
    network = AtomicNetwork21(electronic_isotope_equality=True)
    cosmo = cosmology_constants()
    basis = {ell: np.polynomial.legendre.legvander(np.linspace(-1, 1, 1025), ell) for ell in (8, 12)}
    case_results = [validate_case(record, network, cosmo, basis) for record in [*grid.values(), *controls.values()]]
    failed = [r["case_id"] for r in case_results if r["status"] != "PASS_SCOPED"]
    result = {"schema": "C21O_SAVED_TRAJECTORY_VALIDATION_V1", "status": "PASS_SCOPED" if not failed else "FAIL_SCOPED",
              "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "criteria_declared_in_validator_source": CRITERIA,
              "validator_sha256": sha(__file__), "atomic_module_sha256": sha(HERE / "atomic_network.py"),
              "physical_contract_sha256": sha(HERE / "PHYSICAL_CONTRACT_KO.md"),
              "execution_source_binding": grid_binding, "control_execution_build": ctl_binding["execution_build"],
              "validator_runtime": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__, "host": platform.node()},
              "run_inputs": [grid_meta, ctl_meta], "cosmology_and_mass_conversion": cosmo,
              "case_count": 51, "grid_cases": 45, "control_cases": 6, "failed_cases": failed,
              "case_results": case_results, "comparisons": comparisons(grid, controls, network),
              "ODE_runs": 0, "RHS_evaluations": 0, "old_campaign_replays": 0, "benchmarks": 0,
              "source_and_raw_mutations": 0,
              "normalization": "full Frobenius; K_time=8piG/c^2 with H[s^-1],pressure[J/m^3];K_energy=8piG/c^4 with H_geom=H/c",
              "radiation_positivity_scope": "1025mu samples times201savedtimes times4moments percase;not continuous angular positivity proof",
              "physics_scope": "conditional prescribedUV/T photo+CaseA_RR+tracegas_ne_to_Thomson;not full nuclear/thermochemical history",
              "inherited_mapping_scope": "receipt.initial_mapping describes kinetic initialization only;its original_RHS/UVabsent/state_count are inherited subcertificate labels. Top-levelC21O source,62or78states,BDF/Radau and externalUV model are authoritative.",
              "global_error_bound": None,
              "wall_seconds_validation_only": time.perf_counter() - began}
    # Verify every consumed raw container remained byte-identical after reading.
    for record in [*grid.values(), *controls.values()]:
        require(sha(record["raw_path"]) == record["input_files"]["history_sha256"], "RAW_CHANGED_DURING_VALIDATION")
    with args.output.open("x", encoding="utf8") as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(json.dumps({"status": result["status"], "case_count": 51, "failed_cases": failed,
                      "output": str(args.output), "output_sha256": sha(args.output),
                      "validator_sha256": result["validator_sha256"],
                      "FLRW_comparison": {k: v for k, v in result["comparisons"]["FLRW_BDF_vs_Radau"].items() if k != "by_state"}}, indent=2))
    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
