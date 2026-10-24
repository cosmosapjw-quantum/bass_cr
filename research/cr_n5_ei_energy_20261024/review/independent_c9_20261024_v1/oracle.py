"""Independent C9: read saved artifacts; never import production or old solvers."""
import argparse
import csv
import datetime
import hashlib
import json
import os
import resource
import time
from decimal import Decimal, getcontext
from pathlib import Path

import mpmath as mp
import numpy as np

getcontext().prec = 80
mp.mp.dps = 80
ZERO = Decimal(0)
ONE = Decimal(1)


def df(x):
    return Decimal.from_float(float(x))


def writej(path, obj):
    with path.open("x") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n")


def readj(path):
    return json.loads(path.read_text())


def digest(path):
    b = path.read_bytes()
    return {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}


def npz(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def rel_dec(actual, expected, scale=None):
    scale = abs(expected) if scale is None else abs(scale)
    if scale == 0:
        return ZERO if actual == expected else Decimal("Infinity")
    return abs(actual - expected) / scale


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), ZERO)


def main(unit, out):
    start = time.process_time()
    c = readj(unit / "inputs/CASE.json")
    primary = unit / "runs" / c["primary_run_id"]
    scope = readj(Path(__file__).resolve().parent / "REVIEW_SCOPE.json")
    checks = []
    findings = []
    def check(label, passed, evidence=None):
        item = {"id": label, "pass_scoped": bool(passed)}
        if evidence is not None:
            item["evidence"] = evidence
        checks.append(item)
        if not passed:
            findings.append(item)

    prep = readj(unit / "implementation/PREPARED_V4.json")
    actual_manifest = hashlib.sha256(json.dumps(prep["sources"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    check("prepared_source_manifest_digest", actual_manifest == scope["prepared_source_manifest_digest"] == prep["source_manifest_digest"])
    pins = []
    for group in (prep["sources"], prep["inputs"]):
        for pin in group:
            observed = digest(unit / pin["path"])
            ok = all(observed[k] == pin[k] for k in ("bytes", "sha256"))
            pins.append({"path": pin["path"], **observed, "pass": ok})
    check("all_frozen_sources_and_inputs", all(x["pass"] for x in pins), {"count": len(pins)})
    snapshot_pins = []
    production_receipts = []
    for runkey in ("test_run_id", "primary_run_id", "plot_run_id"):
        run = unit / "runs" / c[runkey]
        for pin in prep["sources"] + [p for p in prep["inputs"] if p["path"] in ("inputs/CASE.json", "inputs/INPUT_MANIFEST.json")]:
            actual = digest(run / "EXECUTED_SOURCE" / Path(pin["path"]).name)
            snapshot_pins.append({"run": c[runkey], "path": pin["path"], **actual, "pass": all(actual[k] == pin[k] for k in ("bytes", "sha256"))})
        receipt = readj(run / "DISPATCH_RECEIPT.json")
        production_receipts.append(receipt)
    check("actual_executed_source_snapshots", all(x["pass"] for x in snapshot_pins), {"count": len(snapshot_pins)})
    check("production_dispatch_success", all(x["status"] == "PASS" and x["returncode"] == 0 for x in production_receipts))
    writej(out / "IDENTITIES.json", {"prepared_manifest_sha256": actual_manifest, "pins": pins, "executed_snapshots": snapshot_pins})

    # Exact declared decimal charge convention, distinct from IEEE conversion.
    declared = json.loads((unit / "inputs/CASE.json").read_text(), parse_float=Decimal)
    net_charge = sum((s["n_cm3"] * s["Z"] for s in declared["species"]), ZERO) - declared["ne_cm3"]
    check("charge_identity_exact_declared_decimals", net_charge == 0, {"net_charge_cm3": str(net_charge)})
    check("missing_isotopes_and_event_counts_remain_null", all(v is None for v in c["missing_isotope_densities"].values()) and c["elastic_event_hazard"] is None and c["elastic_event_count"] is None)
    check("same_temperature_and_proper_pulse_scope", all(s["T_K"] == c["T_K"] and s["theta_eV"] == c["theta_eV"] for s in c["species"]) and c["closed_box"] and c["clock"] == "proper seconds" and c["pulse_exposure_s"] == 10000)

    curve = npz(primary / "COEFFICIENT_PLOT_DATA.npz")
    species = {s["label"]: s for s in c["species"]}
    species["EE"] = {"r": 1.0, "n_cm3": c["ne_cm3"], "Z": 1.0, "lnLambda": c["lnLambda_ee"], "theta_eV": c["theta_eV"]}
    coeff_rows = []
    def coefficient_sample(label, E, observed_mu, observed_D, origin):
        s = species[label]
        E, r, theta = mp.mpf(float(E)), mp.mpf(s["r"]), mp.mpf(s["theta_eV"])
        eta = mp.mpf(s["n_cm3"]) * mp.mpf(s["Z"])**2 / mp.mpf(c["ne_cm3"]) * mp.mpf(s["lnLambda"]) / mp.mpf(c["lnLambda_ee"])
        b = mp.mpf(c["b_anchor_eV_s"]) * mp.sqrt(mp.mpf(c["anchor_energy_eV"]) / E) * eta
        x = r * E / theta
        A = mp.gammainc(mp.mpf("1.5"), 0, x) / mp.gamma(mp.mpf("1.5"))
        Aprime = 2 * mp.sqrt(x) * mp.exp(-x) / mp.sqrt(mp.pi)
        positive, negative = b * Aprime, b * A / r
        mu, D = positive - negative, theta * b * A / r
        mu_err = abs(mp.mpf(float(observed_mu)) - mu) / (abs(positive) + abs(negative))
        D_err = abs(mp.mpf(float(observed_D)) - D) / abs(D)
        coeff_rows.append({"origin": origin, "label": label, "E_eV": float(E), "mu_reference_80d": mp.nstr(mu, 80), "D_reference_80d": mp.nstr(D, 80), "mu_noncancelling_scale_80d": mp.nstr(abs(positive) + abs(negative), 80), "mu_error_scaled": float(mu_err), "D_relative_error": float(D_err)})
    for i in scope["curve_indices"]:
        for label in scope["curve_labels"]:
            coefficient_sample(label, curve["plot_E_eV"][i], curve["plot_" + label + "_mu"][i], curve["plot_" + label + "_D"][i], "curve_index_" + str(i))
    with (primary / "PER_ATOM_COEFFICIENTS.csv").open(newline="") as f:
        atoms = list(csv.DictReader(f))
    for row in atoms:
        if int(row["atom"]) in scope["source_atom_indices"]:
            for label in [s["label"] for s in c["species"]]:
                coefficient_sample(label, float(row["W_eV"]), float(row[label + "_mu_eV_s"]), float(row[label + "_D_eV2_s"]), "z" + row["z"] + "_atom_" + row["atom"])
    coefficient_error = max(max(x["mu_error_scaled"], x["D_relative_error"]) for x in coeff_rows)
    check("independent_80d_coefficients", len(coeff_rows) == 55 and coefficient_error <= c["tolerances"]["independent"], {"pairs": len(coeff_rows), "maximum_error": coefficient_error})
    writej(out / "COEFFICIENTS_80D.json", coeff_rows)
    del curve

    source_records = readj(primary / "SOURCE_WEIGHTED_RESULTS.json")
    source_csv = {}
    for z in c["source_z"]:
        with (unit / "inputs/reused/c23d" / ("ATOMS_" + z + ".csv")).open(newline="") as f:
            source_csv[z] = list(csv.DictReader(f))
    matrix_results = []
    source_results = []
    reference_rhs = 0
    for name in scope["matrix_cases"]:
        raw = npz(primary / (name + ".npz"))
        old = npz(unit / "inputs/reused/native_v3" / (name + ".npz"))
        check(name + "_stored_EE_geometry_reused", all(np.array_equal(raw[k], old[ok]) for k, ok in [("E_eV", "E_eV"), ("pi", "pi"), ("conductance_EE", "conductance")]))
        E = [df(v) for v in raw["E_eV"]]
        pi = [df(v) for v in raw["pi"]]
        n = len(E) - 1
        hs = [df(v) for v in old["hazard_2S_s_inv"]]
        hp = [df(v) for v in old["hazard_2P_s_inv"]]
        labels = ["EE", "H1+", "He4+", "He4++"]
        lower_by, upper_by = {}, {}
        conductances = {}
        drift_error = ZERO
        bath_rhs_error = ZERO
        for j, label in enumerate(labels):
            suffix = label.replace("+", "p")
            conductances[label] = [df(v) for v in raw["conductance_" + suffix]]
            if label == "EE":
                lower_by[label] = [df(v) for v in old["Q_lower"]]
                upper_by[label] = [df(v) for v in old["Q_upper"]]
            else:
                lower_by[label] = [conductances[label][i] / pi[i] for i in range(n)]
                upper_by[label] = [conductances[label][i] / pi[i + 1] for i in range(n)]
            for i in range(n + 1):
                gain = lower_by[label][i] * (E[i + 1] - E[i]) if i < n else ZERO
                loss = upper_by[label][i - 1] * (E[i] - E[i - 1]) if i > 0 else ZERO
                drift = gain - loss
                scale = abs(gain) + abs(loss)
                drift_error = max(drift_error, rel_dec(df(raw["electron_drift_" + suffix][i]), drift, scale))
                if i > 0:
                    bath_rhs_error = max(bath_rhs_error, rel_dec(df(raw["rhs_bath4"][i - 1, j]), -drift, scale))
        qlo = [sum((lower_by[k][i] for k in labels), ZERO) for i in range(n)]
        qup = [sum((upper_by[k][i] for k in labels), ZERO) for i in range(n)]
        qdiag = [-(qlo[i] if i < n else ZERO) - (qup[i - 1] if i > 0 else ZERO) for i in range(n + 1)]
        matrix_assembly_error = ZERO
        for field, ref in [("Q_total_lower", qlo), ("Q_total_upper", qup), ("Q_total_diag", qdiag), ("conductance_total", [sum((conductances[k][i] for k in labels), ZERO) for i in range(n)]), ("K_lower", [-x for x in qup[1:]]), ("K_upper", [-x for x in qlo[1:]]), ("K_diag", [hs[i] + hp[i] - qdiag[i + 1] for i in range(n)])]:
            matrix_assembly_error = max(matrix_assembly_error, max(rel_dec(df(a), b) for a, b in zip(raw[field], ref)))
        physical_rhs_error = ZERO
        for i in range(n):
            refs = [hs[i], hp[i], qup[0] if i == 0 else ZERO, ONE, E[i + 1] * hs[i], E[i + 1] * hp[i]]
            for j, ref in enumerate(refs):
                physical_rhs_error = max(physical_rhs_error, rel_dec(df(raw["rhs_first6"][i, j]), ref))
        check(name + "_raw_edge_K_and_RHS_assembly", max(drift_error, bath_rhs_error, matrix_assembly_error, physical_rhs_error) <= Decimal(str(c["tolerances"]["generator"])), {"edge_drift_noncancelling_scaled": float(drift_error), "bath_RHS_noncancelling_scaled": float(bath_rhs_error), "matrix_assembly_relative": float(matrix_assembly_error), "physical_RHS_relative": float(physical_rhs_error)})

        # Factor exact saved binary64 K once, solve 8 physical and 4 absolute RHS.
        d = [df(v) for v in raw["K_diag"]]
        l = [df(v) for v in raw["K_lower"]]
        u = [df(v) for v in raw["K_upper"]]
        pivots = [d[0]]
        multipliers = []
        for i in range(1, n):
            multiplier = l[i - 1] / pivots[-1]
            multipliers.append(multiplier)
            pivots.append(d[i] - multiplier * u[i - 1])
        check(name + "_positive_80d_pivots", all(p > 0 for p in pivots))
        y = []
        for i in range(n):
            bath = [df(v) for v in raw["rhs_bath4"][i]]
            rhs = [df(raw["rhs_first6"][i, j]) for j in range(3)] + [df(raw["rhs_first6"][i, 4]) + df(raw["rhs_first6"][i, 5])] + bath + [abs(v) for v in bath]
            if i:
                rhs = [rhs[j] - multipliers[i - 1] * y[-1][j] for j in range(12)]
            y.append(rhs)
        x = [[ZERO] * 12 for _ in range(n)]
        x[-1] = [v / pivots[-1] for v in y[-1]]
        for i in range(n - 2, -1, -1):
            x[i] = [(y[i][j] - u[i] * x[i + 1][j]) / pivots[i] for j in range(12)]
        reference_rhs += 12
        with (out / ("MP80_REFERENCE_" + name + ".csv")).open("x", newline="") as f:
            w = csv.writer(f)
            w.writerow(["state_index", "E_eV_exact_binary64"] + ["u_s", "u_p", "u_entry", "CE_incoming_E", "H_EE", "H_H1p", "H_He4p", "H_He4pp", "bound_EE", "bound_H1p", "bound_He4p", "bound_He4pp"])
            for i in range(n):
                w.writerow([i + 1, str(E[i + 1])] + [str(v) for v in x[i]])
        component_errors = [ZERO] * 8
        state_energy_error = ZERO
        raw_state_energy_error = ZERO
        gap = df(c["gap_eV"])
        for i in range(n):
            target = [df(raw[k][i]) for k in ("u_s", "u_p", "u_entry")] + [df(raw["r_s"][i]) + df(raw["r_p"][i])] + [df(v) for v in raw["H"][i]]
            for j in range(8):
                scale = abs(x[i][j]) if j < 4 else x[i][j + 4]
                component_errors[j] = max(component_errors[j], rel_dec(target[j], x[i][j], scale))
            # Exact binary64 target comparisons retain a separate noncancelling ledger scale.
            for vals, which in ((x[i], "reference"), (target, "raw")):
                probability = vals[0] + vals[1]
                internal = gap * probability
                terms = vals[4:8] + [E[0] * vals[2], vals[3] - internal, internal]
                err = abs(sum(terms, ZERO) - E[i + 1]) / (sum((abs(v) for v in terms), ZERO) + abs(E[i + 1]))
                if which == "reference":
                    state_energy_error = max(state_energy_error, err)
                else:
                    raw_state_energy_error = max(raw_state_energy_error, err)
        bound_check = all(x[i][j + 8] >= abs(x[i][j + 4]) - Decimal("1e-70") for i in range(n) for j in range(4))
        check(name + "_independent_80d_solves", max(component_errors) <= Decimal(str(c["tolerances"]["independent"])) and bound_check, {"RHS_count": 12, "physical_RHS": 8, "absolute_bound_RHS": 4, "component_errors": [float(v) for v in component_errors], "absolute_reward_bound_holds": bound_check})
        check(name + "_independent_state_energy_ledger", max(state_energy_error, raw_state_energy_error) <= Decimal(str(c["tolerances"]["energy"])), {"reference_scaled_residual": float(state_energy_error), "raw_scaled_residual": float(raw_state_energy_error)})
        matrix_results.append({"case": name, "full_nodes": n + 1, "RHS": 12, "minimum_pivot_80d": str(min(pivots)), "component_errors": [float(v) for v in component_errors], "reference_energy_ledger_scaled": float(state_energy_error), "raw_energy_ledger_scaled": float(raw_state_energy_error), "raw_edge_drift_scaled": float(drift_error), "raw_bath_RHS_scaled": float(bath_rhs_error), "raw_matrix_assembly_scaled": float(matrix_assembly_error)})

        for z in c["source_z"]:
            p = [df(v) for v in raw["source_" + z]]
            check(name + "_z" + z + "_source_and_active_mask_reused", np.array_equal(raw["source_" + z], old["source_" + z]) and np.array_equal(raw["active_mask_" + z], old["active_mask_" + z]))
            weights = [df(float(row["pulse_count_cm3"])) for row in source_csv[z]]
            energies = [df(float(row["W_eV"])) for row in source_csv[z]]
            active_mask = [W > E[0] for W in energies]
            check(name + "_z" + z + "_original_atom_active_mask", active_mask == list(raw["active_mask_" + z]))
            total = sum(weights, ZERO)
            active = sum((m for m, act in zip(weights, active_mask) if act), ZERO)
            inactive_energy = sum((m * W for m, W, act in zip(weights, energies, active_mask) if not act), ZERO)
            initial = dot(weights, energies)
            source_vals = [dot(p[1:], [row[j] for row in x]) for j in range(12)]
            ce_mass = source_vals[0] + source_vals[1]
            Pactive = ce_mass / active
            Pselected = ce_mass / total
            entryP = (source_vals[2] + p[0]) / active
            eventE = source_vals[3] / ce_mass
            heat = source_vals[4:8]
            bound_heat = source_vals[8:12]
            internal = gap * ce_mass
            entryE = E[0] * (source_vals[2] + p[0])
            post = source_vals[3] - internal
            terms = heat + [entryE, inactive_energy, post, internal]
            ledger_error = abs(sum(terms, ZERO) - initial) / (sum((abs(v) for v in terms), ZERO) + abs(initial))
            recorded = next(row for row in source_records if row["case"] == name and row["z"] == z)
            comparison = {}
            for key, ref in [("P_CE_active", Pactive), ("P_CE_selected", Pselected), ("entry_P_active", entryP), ("conditional_CE_energy_eV", eventE)]:
                comparison[key] = float(rel_dec(df(recorded["new"][key]), ref))
            for j, label in enumerate(labels):
                comparison["bath_heat_" + label] = float(rel_dec(df(recorded["new"]["bath_heat_eV_per_selected"][label]), heat[j] / total, bound_heat[j] / total))
                comparison["ledger_bath_" + label] = float(rel_dec(df(recorded["ledger"]["bath_gain_eV_cm3"][label]), heat[j], bound_heat[j]))
            for key, ref in [("entry_energy_eV_cm3", entryE), ("inactive_energy_eV_cm3", inactive_energy), ("CE_post_kinetic_eV_cm3", post), ("CE_internal_eV_cm3", internal), ("initial_selected_eV_cm3", initial)]:
                # The CE post subtraction uses its two noncancelling terms.
                scale = abs(source_vals[3]) + abs(internal) if key == "CE_post_kinetic_eV_cm3" else abs(ref)
                comparison["ledger_" + key] = float(rel_dec(df(recorded["ledger"][key]), ref, scale))
            check(name + "_z" + z + "_independent_source_energy_and_rewards", ledger_error <= Decimal(str(c["tolerances"]["energy"])) and max(comparison.values()) <= c["tolerances"]["independent"], {"ledger_scaled_residual": float(ledger_error), "maximum_comparison_error": max(comparison.values())})
            source_results.append({"case": name, "z": z, "P_CE_active_80d": str(Pactive), "P_CE_selected_80d": str(Pselected), "conditional_CE_energy_eV_80d": str(eventE), "bath_gain_eV_cm3_80d": {label: str(heat[j]) for j, label in enumerate(labels)}, "bath_noncancelling_bound_eV_cm3_80d": {label: str(bound_heat[j]) for j, label in enumerate(labels)}, "initial_selected_eV_cm3_80d": str(initial), "entry_eV_cm3_80d": str(entryE), "inactive_eV_cm3_80d": str(inactive_energy), "CE_post_kinetic_eV_cm3_80d": str(post), "CE_internal_eV_cm3_80d": str(internal), "ledger_scaled_residual": float(ledger_error), "comparison_errors": comparison})
        writej(out / (name + "_REVIEW.json"), matrix_results[-1])
    writej(out / "SOURCE_LEDGER_80D.json", source_results)

    controls = readj(unit / "runs" / c["test_run_id"] / "TEST_RESULT.json")
    result = readj(primary / "RESULT.json")
    matrix_metadata = readj(primary / "MATRIX_CASES.json")
    finite = readj(primary / "FINITE_COMPARISONS.json")
    check("saved_controls_pass_without_replay", controls["status"] == "PASS" and len(controls["checks"]) == 25 and all(x["pass_scoped"] for x in controls["checks"]))
    check("primary_work_count_and_scope", result["status"] == "PASS" and result["matrix_count"] == 8 and result["primary_RHS_count"] == 96 and result["source_rows"] == 24 and all(result[k] == 0 for k in ["old_generator_calls", "old_source_projection_calls", "old_primary_replay", "source_quadrature", "thermal_rate_quadrature", "new_ODE"]) and result["global_error_bound"] is None and result["global_completion_percent"] is None)
    check("all_saved_matrix_and_finite_gates_pass", len(matrix_metadata) == 8 and len(finite) == 18 and all(x["pass_scoped"] for x in matrix_metadata + finite) and all(x["source_MFPT_comparison_bound_pass"] for x in source_records))
    review = {"schema": "N5_EI_INDEPENDENT_C9_RAW_V1", "run_id": scope["run_id"], "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "status": "PASS" if not findings else "FAILED_RETAINED", "blocking_findings": len(findings), "findings": findings, "checks": checks, "coefficient_reference_pairs": len(coeff_rows), "coefficient_max_error": coefficient_error, "matrix_cases": matrix_results, "matrix_reference_RHS": reference_rhs, "source_ledger_rows": len(source_results), "precision_decimal_digits": 80, "production_imports": 0, "old_science_replay": 0, "new_ODE": 0, "source_quadrature": 0, "thermal_rate_quadrature": 0, "process_cpu_s": time.process_time() - start, "affinity": sorted(os.sched_getaffinity(0)), "native_thread_environment": {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")}, "max_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "actual_plot_inspection": "SEPARATE_REVIEWER_REPORT_REQUIRED", "global_error_bound": None, "global_completion_percent": None, "EXECUTION": "COMPLETED", "PUBLICATION": "ROOT_OWNED", "BACKUP": "ROOT_PENDING", "DAG": "N5_PARTIAL_OPEN_N6_N7_NOT_ACTIVATED"}
    writej(out / "RESULT.json", review)
    print(json.dumps({k: review[k] for k in ["status", "blocking_findings", "coefficient_reference_pairs", "coefficient_max_error", "matrix_reference_RHS", "process_cpu_s"]}))
    return 0 if not findings else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.unit.resolve(), args.output.resolve()))
