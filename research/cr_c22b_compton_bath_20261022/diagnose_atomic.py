#!/usr/bin/env python3
"""Create-only HG excitation / SW91 H1 CI diagnostics on preserved histories.

This program never integrates an ODE. Accepted-mesh histories are derived by
the source-verified model.summarize method. Atomic processes remain omitted
from the executed model; these diagnostics are not alternate trajectories or
error bounds. Compton exchange is active in C22B, not an omitted process here.
"""
from __future__ import annotations

import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_key] = "1"

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import traceback

import numpy as np

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
REPO = RESEARCH.parent
C22A = RESEARCH / "cr_c22a_thermochemical_20261022"
PROVIDER = HERE / "diagnostics/atomic_h_sw91.py"
SW91_SHA256 = "f6417b6306f4190bb58e7063d78f3967b4b4d593627928a8bf5bf5d74310f7db"
HG_HELPER = C22A / "diagnose_omissions.py"
HG_HELPER_SHA256 = "8dc5b1653554b10fdd0745311eef80714e54d155d136201ea9eaf0ad6adf26e9"
EV_ERG = 1.602176634e-12
POPULATION_SCALED_LOWER_GATE = -2e-9


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf8")


def write_json(path, data):
    with Path(path).open("x", encoding="utf8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def write_npz(path, arrays):
    with Path(path).open("xb") as handle:
        np.savez_compressed(handle, **arrays)


def load_module(name, path, expected_sha=None):
    """Execute exactly the module bytes checked here; dependencies separately bound."""
    path = Path(path)
    raw = path.read_bytes()
    if expected_sha is not None and sha(raw) != expected_sha:
        raise RuntimeError("DIAGNOSTIC_PROVIDER_SOURCE_MISMATCH:" + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def diagnostic_dependencies():
    sys.path.insert(0, str(C22A))
    helper = load_module("c22b_atomic_hg_helper", HG_HELPER, HG_HELPER_SHA256)
    sw91 = load_module("c22b_atomic_sw91", PROVIDER, SW91_SHA256)
    return helper, sw91


def valid_integral(time_s, rate, valid):
    """Trapezoids on available adjacent endpoints, with no gap bridging."""
    dt = np.diff(time_s)
    adjacent = valid[:-1] & valid[1:] & np.isfinite(rate[:-1]) & np.isfinite(rate[1:])
    duration = float(np.sum(dt[adjacent]))
    total_duration = float(time_s[-1] - time_s[0])
    value = (float(np.sum((rate[:-1][adjacent] + rate[1:][adjacent])
                          * .5 * dt[adjacent])) if np.any(adjacent) else None)
    return {"value": value, "available_interval_duration_s": duration,
            "total_duration_s": total_duration,
            "available_duration_fraction": duration / total_duration,
            "available_adjacent_intervals": int(np.sum(adjacent)),
            "total_intervals": int(len(dt)),
            "availability": ("AVAILABLE_ON_ALL_MESH_INTERVALS" if np.all(adjacent)
                             else "OPEN_PARTIAL_TEMPERATURE_COVERAGE" if np.any(adjacent)
                             else "OPEN_NO_VALID_ADJACENT_INTERVALS"),
            "quadrature": "trapezoid_on_available_adjacent_samples; no_gap_bridging",
            "interior_coverage": "endpoint_mask_only; no_continuous_domain_or_quadrature_error_bound"}


def stats(values):
    values = np.asarray(values)
    finite = values[np.isfinite(values)]
    return ({"minimum": float(finite.min()), "maximum": float(finite.max()),
             "maximum_absolute": float(np.max(np.abs(finite)))} if finite.size
            else {"minimum": None, "maximum": None, "maximum_absolute": None})


def ratio(values, denominator):
    result = np.full(np.shape(values), np.nan)
    valid = np.isfinite(values) & np.isfinite(denominator) & (denominator > 0)
    np.divide(values, denominator, out=result, where=valid)
    return result


def normalized(value, denominator):
    return float(value / denominator) if (value is not None and denominator is not None
                                           and denominator > 0) else None


def diagnose_history(history, helper, sw91, cohort):
    required = ("eta", "z", "H", "nH_ref_cm3", "n_e_cm3", "temperature_K",
                "atomic_abundance_per_Href", "atomic_state_labels",
                "thermal_energy_eV_per_H", "proper_elapsed_s")
    missing = [key for key in required if key not in history]
    if missing:
        raise ValueError("HISTORY_FIELDS_MISSING:" + ",".join(missing))
    values = {key: np.asarray(history[key]) for key in required}
    time_s = np.asarray(values["proper_elapsed_s"], dtype=float)
    if (time_s.ndim != 1 or len(time_s) < 2 or not np.isfinite(time_s).all()
            or not np.all(np.diff(time_s) > 0)):
        raise ValueError("PROPER_TIME_MUST_BE_FINITE_STRICTLY_INCREASING")
    count = len(time_s)
    for key in ("eta", "z", "H", "nH_ref_cm3", "n_e_cm3", "temperature_K",
                "thermal_energy_eV_per_H"):
        if values[key].shape != (count,) or not np.isfinite(values[key]).all():
            raise ValueError("HISTORY_SHAPE_OR_FINITE:" + key)
    temp, ne, h, uth, nref = (np.asarray(values[key], dtype=float) for key in
        ("temperature_K", "n_e_cm3", "H", "thermal_energy_eV_per_H", "nH_ref_cm3"))
    if (np.any(temp <= 0) or np.any(ne < 0) or np.any(h <= 0)
            or np.any(uth <= 0) or np.any(nref <= 0)):
        raise ValueError("NONPHYSICAL_THERMAL_OR_DENSITY_INPUT")
    labels = [str(value) for value in values["atomic_state_labels"]]
    abundance = np.asarray(values["atomic_abundance_per_Href"], dtype=float)
    net = helper.AtomicNetwork21(electronic_isotope_equality=True)
    if (abundance.shape != (21, count) or len(labels) != 21
            or len(set(labels)) != 21 or set(labels) != set(net.state_labels)
            or not np.isfinite(abundance).all()):
        raise ValueError("ATOMIC_HISTORY_SHAPE_FINITE_OR_IDENTITY")
    ordered = abundance[[labels.index(label) for label in net.state_labels]]
    scaled = ordered / net.scales[:, None]
    if np.any(scaled < POPULATION_SCALED_LOWER_GATE):
        raise ValueError("POPULATION_BELOW_DECLARED_NUMERICAL_GATE;NO_CLIPPING")
    residual = {
        "minimum_abundance_per_Href": float(np.min(ordered)),
        "minimum_population_scaled": float(np.min(scaled)),
        "negative_population_samples": int(np.sum(ordered < 0)),
        "accepted_scaled_lower_bound": POPULATION_SCALED_LOWER_GATE,
        "policy": "signed_raw_values_retained; negative_contributions_are_numerical_residuals; no_clipping",
        "species_with_negative_residuals": [
            {"label": net.state_labels[i], "minimum_abundance_per_Href": float(ordered[i].min()),
             "minimum_population_scaled": float(scaled[i].min())}
            for i in range(21) if np.any(ordered[i] < 0)]}
    h1_neutral = ordered[net.blocks["H1"][0]]
    hg_neutral = sum(ordered[net.blocks[name][0]] for name in ("H1", "D", "T"))
    rr_valid = (temp >= 3) & (temp <= 1e9)
    rr = np.full(count, np.nan)
    rr[rr_valid] = 0.0
    for lower, upper, channel in net.edges:
        name = helper.CHANNEL_NAMES[channel]
        parameters = net.provider.rows[name]["RR"]
        alpha = np.asarray(net.provider.rr(name, temp[rr_valid]))
        capture_eV = (helper.KB_EV_K * temp[rr_valid]
                      * helper.rr_energy_factor(parameters, temp[rr_valid]))
        rr[rr_valid] += ne[rr_valid] * ordered[upper, rr_valid] * alpha * capture_eV
    ci_coeff, ci_valid = sw91.h_ci_cm3_s(temp)
    ci_events = ci_coeff * ne * h1_neutral
    ci_loss = sw91.RYDBERG_EV * ci_events
    excitation_coeff, excitation_valid = helper.h_excitation_cooling_erg_cm3_s(temp)
    excitation_loss = excitation_coeff * ne * hg_neutral / EV_ERG
    rr_full = valid_integral(time_s, rr, rr_valid)
    energy_keys = ("thermal_energy_eV_per_H", "ionization_energy_eV_per_H", "UV_energy_eV_per_H")
    if "energy_total_eV_per_H" in history:
        initial_energy = float(np.asarray(history["energy_total_eV_per_H"])[0])
        energy_definition = "energy_total_eV_per_H[0]; initial cumulative ledgers zero in registered inputs"
    elif all(key in history for key in energy_keys):
        initial_energy = sum(float(np.asarray(history[key])[0]) for key in energy_keys)
        energy_definition = "initial thermal + ionization + UV energy"
    else:
        initial_energy, energy_definition = None, "UNAVAILABLE"
    arrays = {"eta": values["eta"], "z": values["z"], "proper_elapsed_s": time_s,
              "temperature_K": temp, "n_e_cm3": ne, "nH_ref_cm3": nref,
              "H1_neutral_per_Href": h1_neutral,
              "HG_H1_D_T_neutral_per_Href": hg_neutral,
              "included_RR_cooling_eV_per_Href_s": rr, "RR_valid_temperature": rr_valid,
              "SW91_H1_CI_coefficient_cm3_s": ci_coeff, "SW91_H1_CI_valid_temperature": ci_valid,
              "SW91_H1_CI_events_per_Href_s": ci_events,
              "SW91_H1_CI_thermal_sink_eV_per_Href_s": ci_loss,
              "HG_H_excitation_coefficient_erg_cm3_s": excitation_coeff,
              "HG_H_excitation_valid_temperature": excitation_valid,
              "HG_H_excitation_thermal_sink_eV_per_Href_s": excitation_loss}
    diagnostics = {}
    for name, rate, valid in (("SW91_H1_CI", ci_loss, ci_valid),
                              ("HG_H_excitation", excitation_loss, excitation_valid)):
        signed = valid_integral(time_s, rate, valid)
        absolute = valid_integral(time_s, np.abs(rate), valid)
        matching_rr = valid_integral(time_s, rr, valid & rr_valid)
        over_hu, over_rr = ratio(rate, h * uth), ratio(rate, rr)
        arrays[name + "_over_H_Uthermal"] = over_hu
        arrays[name + "_over_included_RR"] = over_rr
        diagnostics[name] = {
            "availability": signed["availability"],
            "valid_sample_count": int(np.sum(valid)), "total_sample_count": count,
            "rate_eV_per_Href_s": stats(rate), "rate_over_H_Uthermal": stats(over_hu),
            "rate_over_included_RR_cooling": stats(over_rr),
            "integrated_signed_energy_eV_per_Href": signed,
            "integrated_absolute_energy_eV_per_Href": absolute,
            "integrated_absolute_over_initial_Uthermal": normalized(absolute["value"], float(uth[0])),
            "integrated_absolute_over_initial_total_energy": normalized(absolute["value"], initial_energy),
            "included_RR_integral_on_same_available_intervals_eV_per_Href": matching_rr,
            "integrated_absolute_over_included_RR_all_available_intervals": normalized(absolute["value"], rr_full["value"]),
            "integrated_absolute_over_included_RR_same_available_intervals": normalized(absolute["value"], matching_rr["value"]),
            "sign": "positive = gas thermal sink; tolerated negative abundance contributions retained as numerical residuals"}
    diagnostics["SW91_H1_CI"].update(
        temperature_domain_K=list(sw91.TEMPERATURE_DOMAIN_K),
        species=["H1_0"], isotope_approximation="NONE; NO_D_OR_T_EXTRAPOLATION",
        threshold_eV=sw91.RYDBERG_EV, C22A_C22B_chemical_increment_eV=13.6,
        threshold_policy="diagnostic uses source one-Ry threshold; active chemical increment13.6eV remains unchanged",
        energy_destination="ionization chemical energy; not an additional radiative sink",
        integrated_events_per_Href=valid_integral(time_s, ci_events, ci_valid),
        integrated_absolute_events_per_Href=valid_integral(time_s, np.abs(ci_events), ci_valid))
    diagnostics["HG_H_excitation"].update(
        temperature_domain_K=[5000.0, 500000.0], species=["H1_0", "D_0", "T_0"],
        isotope_approximation="same_H_electronic_excitation_rate_for_H1_D_T; inherited_C22A_diagnostic_profile; not isotope-resolved atomic certification",
        energy_destination="escaping excitation radiation under low-density escape assumption",
        source_function="C22A.diagnose_omissions.h_excitation_cooling_erg_cm3_s; unchanged source hash",
        SW91_excitation="UNAVAILABLE; Table3 column assignment unresolved; HG coefficient used explicitly")
    report = {
        "schema": "C22B_ATOMIC_OMISSION_TRAJECTORY_DIAGNOSTIC_V1",
        "EXECUTION": "COMPLETE_SCOPED_POSTPROCESSING;ODE0;RHS0",
        "PUBLICATION": "PENDING_PARENT", "BACKUP": "PENDING_PARENT",
        "DAG": "SELECTED_ATOMIC_OMISSIONS_ASSESSED_WITH_DOMAIN_MASKS;FULL_NETWORK_COVERAGE_OPEN",
        "cohort": cohort, "new_ODE_runs": 0, "RHS_evaluations": 0,
        "interpretation": "evaluated_on_executed_incomplete_trajectory;not_self_consistent_alternate_solution;not_error_bound",
        "Compton_scope": ("ACTIVE_C22B_OPEN_BATH;NOT_AN_OMISSION_DIAGNOSTIC" if cohort == "C22B"
                          else "BASELINE_C22A_MODEL_HAS_NO_ACTIVE_COMPTON;NOT_EVALUATED_BY_THIS_ATOMIC_DIAGNOSTIC"),
        "initial_thermal_energy_eV_per_Href": float(uth[0]),
        "initial_total_energy_eV_per_Href": initial_energy, "total_energy_denominator": energy_definition,
        "coverage_policy": "outside_fit_domain=NaN+false_mask;no_zero_substitution;no_extrapolation;available_adjacent_endpoint_intervals_only",
        "population_numerical_residuals": residual,
        "included_RR_cooling_integral_eV_per_Href": rr_full,
        "RR_moment_scope": "inherited_fit_derivative_energy_moment;not_independent_accuracy_certification",
        "diagnostics": diagnostics,
        "sources": {"HG1997": helper.SOURCES["HG1997"],
                    "Grackle_source_crosscheck": helper.SOURCES["Grackle_source_crosscheck"],
                    "VF_RR": helper.SOURCES["VF_RR"], "SW91": sw91.metadata()},
        "full_network_coverage": "OPEN", "global_error_bound": None}
    return report, arrays


def verify_run(run):
    manifest_raw = (run / "SOURCE_IDENTITY.json").read_bytes()
    manifest = json.loads(manifest_raw)
    payload = {key: value for key, value in manifest.items() if key != "identity_sha256"}
    if sha(canonical(payload)) != manifest["identity_sha256"]:
        raise RuntimeError("SOURCE_MANIFEST_IDENTITY_MISMATCH:" + str(run))
    for row in manifest["files"]:
        path = (REPO / row["path"]).resolve()
        if not path.is_relative_to(REPO.resolve()):
            raise ValueError("SOURCE_PATH_OUTSIDE_REPO")
        raw = path.read_bytes()
        if len(raw) != row["size_bytes"] or sha(raw) != row["sha256"]:
            raise RuntimeError("FROZEN_SOURCE_MISMATCH:" + row["path"])
    input_raw = (run / "INPUT.json").read_bytes()
    inputs = json.loads(input_raw)
    input_identity = sha(canonical(inputs))
    runtime_raw = (run / "RUNTIME.json").read_bytes()
    runtime = json.loads(runtime_raw)
    if (runtime["source_identity_sha256"] != manifest["identity_sha256"]
            or runtime["input_sha256"] != input_identity):
        raise RuntimeError("RUNTIME_SOURCE_INPUT_BINDING_MISMATCH:" + str(run))
    return manifest, inputs, {"source_manifest_sha256": sha(manifest_raw),
                              "input_file_sha256": sha(input_raw),
                              "input_identity_sha256": input_identity,
                              "runtime_file_sha256": sha(runtime_raw),
                              "source_identity_sha256": manifest["identity_sha256"],
                              "verified_frozen_source_files": len(manifest["files"])}


def forbid_rhs(*args, **kwargs):
    raise RuntimeError("RHS_FORBIDDEN_IN_SAVED_HISTORY_DIAGNOSTIC")


def summarize_without_rhs(model, eta, state):
    # Instance guards turn an accidental future summarize->RHS dependency into
    # an explicit failure instead of silently expanding this task's scope.
    model.rhs = forbid_rhs
    if hasattr(model, "solver_rhs"):
        model.solver_rhs = forbid_rhs
    if hasattr(model, "base"):
        model.base.rhs = forbid_rhs
    return model.summarize(eta, state)


def difference(saved, accepted):
    return {"saved": saved, "accepted": accepted,
            "saved_minus_accepted": None if saved is None or accepted is None else saved - accepted,
            "relative_saved_minus_accepted": (None if saved is None or accepted in (None, 0)
                                              else (saved - accepted) / abs(accepted))}


def compare_meshes(saved, accepted):
    result = {}
    for process, row in saved["diagnostics"].items():
        other = accepted["diagnostics"][process]
        values = {
            "signed_energy_eV_per_Href": (row["integrated_signed_energy_eV_per_Href"]["value"], other["integrated_signed_energy_eV_per_Href"]["value"]),
            "absolute_energy_eV_per_Href": (row["integrated_absolute_energy_eV_per_Href"]["value"], other["integrated_absolute_energy_eV_per_Href"]["value"]),
            "absolute_energy_over_initial_Uthermal": (row["integrated_absolute_over_initial_Uthermal"], other["integrated_absolute_over_initial_Uthermal"]),
            "absolute_energy_over_initial_total_energy": (row["integrated_absolute_over_initial_total_energy"], other["integrated_absolute_over_initial_total_energy"]),
            "available_time_fraction": (row["integrated_absolute_energy_eV_per_Href"]["available_duration_fraction"], other["integrated_absolute_energy_eV_per_Href"]["available_duration_fraction"]),
            "max_abs_rate_over_H_Uthermal": (row["rate_over_H_Uthermal"]["maximum_absolute"], other["rate_over_H_Uthermal"]["maximum_absolute"])}
        if "integrated_events_per_Href" in row:
            values["events_per_Href"] = (row["integrated_events_per_Href"]["value"], other["integrated_events_per_Href"]["value"])
        result[process] = {key: difference(*pair) for key, pair in values.items()}
    return {"processes": result,
            "included_RR_energy_eV_per_Href": difference(saved["included_RR_cooling_integral_eV_per_Href"]["value"], accepted["included_RR_cooling_integral_eV_per_Href"]["value"]),
            "interpretation": "two_finite_mesh_trapezoids;different_available_endpoint_intervals_may_contribute;accepted_mesh_not_exact_reference_or_error_bound"}


def resource_admission(run_paths, cpu, excluded):
    sys.path.insert(0, str(HERE))
    runner = load_module("c22b_atomic_resource_runner", HERE / "run_pilot.py")
    snapshot = runner.resource_control.observe_resources()
    reserved, leases = runner.lease_snapshot(snapshot["allowed_cpus"])
    protected = {55, *excluded}
    for run in run_paths:
        path = run / "RESOURCE.json"
        if path.exists():
            admission = json.loads(path.read_bytes()).get("admission", {})
            coordinator = admission.get("coordinator_cpu")
            if coordinator is not None:
                protected.add(int(coordinator))
            protected.update(int(value) for value in admission.get("selected_worker_cpus", []))
    eligible = [int(value) for value in snapshot["allowed_cpus"]
                if value not in protected and value not in reserved
                and snapshot["per_cpu_busy"].get(value, 1.0) <= .35]
    if cpu is not None and cpu not in eligible:
        raise RuntimeError("DIAGNOSTIC_CPU_BUSY_PROTECTED_OR_LEASED")
    if not eligible:
        raise RuntimeError("NO_AVAILABLE_DIAGNOSTIC_CPU")
    selected = int(cpu if cpu is not None else min(eligible, key=lambda value: (snapshot["per_cpu_busy"][value], value)))
    os.sched_setaffinity(0, {selected})
    return {"snapshot": snapshot, "lease_observation": leases,
            "protected_cpus": sorted(protected), "actual_affinity": sorted(os.sched_getaffinity(0)),
            "single_process": True, "numerical_threads": 1, "new_ODE_runs": 0,
            "exclusive_lease_claim": False}


def process_run(run, cohort, out, helper, sw91):
    manifest, inputs, binding = verify_run(run)
    unit = run.parent.parent
    if unit.resolve() != (HERE if cohort == "C22B" else C22A).resolve():
        raise ValueError("RUN_UNIT_DOES_NOT_MATCH_DECLARED_COHORT")
    sys.path.insert(0, str(unit))
    model_module = load_module("atomic_diagnostic_model_" + cohort, unit / "model.py")
    factories, results = {}, {}
    target = out / cohort
    target.mkdir(exist_ok=False)
    for case in inputs["cases"]:
        name = case["name"]
        if not isinstance(name, str) or Path(name).name != name or name in (".", ".."):
            raise ValueError("UNSAFE_CASE_NAME")
        folder = run / "cases" / name
        raw_path = folder / "history.npz"
        raw = raw_path.read_bytes()
        complete_raw = (folder / "COMPLETE.json").read_bytes()
        receipt_raw = (folder / "RECEIPT.json").read_bytes()
        metadata_raw = (folder / "MODEL.json").read_bytes()
        complete, receipt, metadata = map(json.loads, (complete_raw, receipt_raw, metadata_raw))
        if (complete["status"] != "COMPLETED_SCOPED" or receipt["status"] != "COMPLETED_SCOPED"
                or complete["receipt_sha256"] != sha(receipt_raw)
                or receipt["model_metadata_sha256"] != sha(metadata_raw)
                or receipt["case"] != case or metadata["case"] != case
                or receipt["source_identity_sha256"] != manifest["identity_sha256"]
                or receipt["input_sha256"] != binding["input_identity_sha256"]
                or sha(raw) != complete["history_sha256"] or sha(raw) != receipt["history_sha256"]
                or len(raw) != receipt["history_bytes"]
                or complete["source_identity_sha256"] != manifest["identity_sha256"]
                or complete["input_sha256"] != binding["input_identity_sha256"]):
            raise RuntimeError("RAW_OR_SOURCE_INPUT_BINDING_MISMATCH:" + name)
        with np.load(io.BytesIO(raw), allow_pickle=False) as npz:
            history = {key: np.array(npz[key], copy=True) for key in npz.files}
        raw_binding = {"path": str(raw_path), "sha256": sha(raw), "size_bytes": len(raw),
                       "complete_sha256": sha(complete_raw), "receipt_sha256": sha(receipt_raw),
                       "model_metadata_sha256": sha(metadata_raw),
                       "reader": "np.load(io.BytesIO(the_same_verified_bytes),allow_pickle=False)",
                       **binding}
        case_out = target / name
        case_out.mkdir(exist_ok=False)
        reports = {}
        for mesh in ("saved", "accepted"):
            mesh_out = case_out / mesh
            mesh_out.mkdir(exist_ok=False)
            if mesh == "saved":
                selected_history = history
                derivation = {"operation": "original_saved_history", "raw_unchanged": True,
                              "new_ODE_runs": 0, "RHS_evaluations": 0}
            else:
                ell = int(case.get("ellmax", 8))
                if ell not in factories:
                    factories[ell] = model_module.ThermochemicalFactory(ellmax=ell)
                model = factories[ell].build(case)
                selected_history = summarize_without_rhs(model, history["accepted_eta"], history["accepted_Y"])
                derived_path = mesh_out / "accepted_history.npz"
                write_npz(derived_path, selected_history)
                derived_raw = derived_path.read_bytes()
                with np.load(io.BytesIO(derived_raw), allow_pickle=False) as npz:
                    selected_history = {key: np.array(npz[key], copy=True) for key in npz.files}
                derivation = {"operation": "frozen_model.summarize(accepted_eta,accepted_Y)",
                              "source_raw_sha256": sha(raw), "source_identity_sha256": manifest["identity_sha256"],
                              "derived_history_sha256": sha(derived_raw), "derived_history_bytes": len(derived_raw),
                              "reader": "np.load(io.BytesIO(the_same_hashed_derived_bytes),allow_pickle=False)",
                              "population_clipping": False, "raw_unchanged": True,
                              "new_ODE_runs": 0, "new_solver_steps": 0, "RHS_evaluations": 0}
            report, arrays = diagnose_history(selected_history, helper, sw91, cohort)
            report.update(input=raw_binding, derivation=derivation, case=case, mesh=mesh)
            write_json(mesh_out / "DIAGNOSTICS.json", report)
            write_npz(mesh_out / "DIAGNOSTICS.npz", arrays)
            reports[mesh] = report
        comparison = compare_meshes(reports["saved"], reports["accepted"])
        comparison.update(case=case, raw_input=raw_binding,
                          saved_points=len(history["eta"]), accepted_points=len(history["accepted_eta"]))
        write_json(case_out / "MESH_COMPARISON.json", comparison)
        results[name] = comparison
        print(json.dumps({"cohort": cohort, "case": name, "status": "ATOMIC_DIAGNOSTICS_COMPLETE_SCOPED", "new_ODE_runs": 0}), flush=True)
    verify_run(run)  # Detect source mutation during accepted-history derivation.
    return {"run": str(run), "binding": binding, "cases": results}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True, help="completed C22B nominal run directory")
    parser.add_argument("--baseline-run", type=Path, help="optional preserved matched C22A run; ODE0")
    parser.add_argument("--out", type=Path, default=HERE / "atomic_diagnostics_v1")
    parser.add_argument("--cpu", type=int, help="available unleased single CPU; otherwise observed idle eligible CPU")
    parser.add_argument("--exclude-cpu", type=int, action="append", default=[], help="active coordinator/worker CPU to protect")
    args = parser.parse_args(argv)
    runs = [args.run.resolve()] + ([args.baseline_run.resolve()] if args.baseline_run else [])
    if args.out.exists():
        raise FileExistsError("CREATE_ONLY_OUTPUT_EXISTS:" + str(args.out))
    # Preflight all immutable input/source identities before any output creation.
    for run in runs:
        verify_run(run)
    resource = resource_admission(runs, args.cpu, args.exclude_cpu)
    helper, sw91 = diagnostic_dependencies()
    dependencies = [Path(__file__).resolve(), HG_HELPER, PROVIDER,
                    C22A / "rr_energy_moment.py", HERE / "diagnostics/SOURCE_BUNDLE.json"]
    source_records = []
    for path in dependencies:
        raw = path.read_bytes()
        source_records.append({"path": str(path.relative_to(REPO)),
                               "size_bytes": len(raw), "sha256": sha(raw)})
    args.out.mkdir(parents=True, exist_ok=False)
    write_json(args.out / "RESOURCE.json", resource)
    write_json(args.out / "DIAGNOSTIC_SOURCE.json", {"files": source_records,
               "source_scope": "diagnostic_only;outside_execution_source_freeze",
               "new_ODE_runs": 0, "RHS_evaluations": 0})
    try:
        results = {"C22B": process_run(runs[0], "C22B", args.out, helper, sw91)}
        if args.baseline_run:
            results["C22A"] = process_run(runs[1], "C22A", args.out, helper, sw91)
        summary = {"schema": "C22B_ATOMIC_DIAGNOSTICS_SAVED_ACCEPTED_V1",
                   "created_utc": datetime.now(timezone.utc).isoformat(),
                   "EXECUTION": "COMPLETE_SCOPED_POSTPROCESSING;ODE0;RHS0",
                   "PUBLICATION": "PENDING_PARENT", "BACKUP": "PENDING_PARENT",
                   "DAG": "SELECTED_OMISSIONS_DIAGNOSED_WITH_PARTIAL_TEMPERATURE_COVERAGE;FULL_NETWORK_OPEN",
                   "results": results, "new_ODE_runs": 0, "RHS_evaluations": 0,
                   "interpretation": "finite_mesh_diagnostics_on_existing_trajectories;not_self_consistent_alternate_runs;not_global_error_bound",
                   "Compton": "active_in_C22B;not_labeled_omitted",
                   "global_error_bound": None}
        write_json(args.out / "SUMMARY.json", summary)
    except Exception as exc:
        write_json(args.out / "FAILURE.json", {"status": "POSTPROCESSING_FAILURE_PRESERVED",
                   "exception": repr(exc), "traceback": traceback.format_exc(),
                   "new_ODE_runs": 0, "RHS_evaluations": 0, "raw_unchanged": True})
        raise
    print(json.dumps({"output": str(args.out), "status": "COMPLETE_SCOPED", "new_ODE_runs": 0}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
