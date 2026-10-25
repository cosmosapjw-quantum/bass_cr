"""Independent Decimal70 review of two frozen PR104+ground-RR finite chains.

No production module imports, no quadrature, no baseline replay. Numpy is used
only for loading immutable binary arrays and inspecting exact array identity.
"""
import argparse
import csv
import datetime
import hashlib
import json
import time
from decimal import Decimal, getcontext
from pathlib import Path

import numpy as np

getcontext().prec = 70
D = Decimal
ZERO = D(0)
ONE = D(1)
CONTRACT_SHA = "f98edd820926fcf4432858f8bdeafdd782a7bc97e9f274e0f849f7c8c5114cd2"
NAMES = ["u_s", "u_p", "u_entry", "t", "r_s", "r_p", "p_RR", "r_RR",
         "H_EE", "H_H1plus", "H_He4plus", "H_He4doubleplus", "H_H1neutral", "H_He4neutral",
         "v_s", "v_p", "v_RR", "delta_CE", "delta_time", "w"]
CASES = ["chi1.5_R80_N2048", "chi3_R80_N2048"]
COEF_TOL = D("5e-13")
NORM_TOL = D("5e-10")
LINEAR_TOL = D("2e-12")


def exact(value):
    return D.from_float(float(value))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def write_json(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def file_pin(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def factor(diag, lower, upper):
    pivots = list(diag)
    multipliers = []
    need(all(v > ZERO for v in pivots), "NONPOSITIVE_DIAGONAL")
    need(all(v <= ZERO for v in lower + upper), "NOT_Z_MATRIX")
    for j, below in enumerate(lower):
        multiplier = below / pivots[j]
        multipliers.append(multiplier)
        pivots[j + 1] -= multiplier * upper[j]
        need(pivots[j + 1] > ZERO, "NONPOSITIVE_DECIMAL_THOMAS_PIVOT")
    return pivots, multipliers


def solve(factors, upper, rhs):
    pivots, multipliers = factors
    work = list(rhs)
    for j, multiplier in enumerate(multipliers):
        work[j + 1] -= multiplier * work[j]
    work[-1] /= pivots[-1]
    for j in range(len(work) - 2, -1, -1):
        work[j] = (work[j] - upper[j] * work[j + 1]) / pivots[j]
    return work


def backward(diag, lower, upper, x, rhs):
    largest = ZERO
    n = len(diag)
    for j in range(n):
        a = diag[j] * x[j]
        value = a
        scale = abs(a) + abs(rhs[j])
        if j:
            term = lower[j - 1] * x[j - 1]
            value += term
            scale += abs(term)
        if j + 1 < n:
            term = upper[j] * x[j + 1]
            value += term
            scale += abs(term)
        error = abs(value - rhs[j])
        need(scale > ZERO or error == ZERO, "ZERO_BACKWARD_SCALE")
        if scale:
            largest = max(largest, error / scale)
    return largest


def relative(a, b):
    need(b != ZERO, "ZERO_REFERENCE_NORM")
    return abs(a - b) / abs(b)


def table_row(path):
    for line in path.read_text().splitlines():
        fields = line.split()
        if len(fields) == 11 and fields[0:2] == ["1", "1"]:
            return [D(v) for v in fields[2:]]
    raise ValueError("NATIVE_HI_ROW_MISSING")


def coefficient(energy, row):
    threshold, maximum, e0, sigma0, ya, power, yw, y0, y1 = row
    photon = energy + D("13.60")
    need(energy > ZERO and threshold <= photon <= maximum, "INDEPENDENT_SOURCE_SUPPORT")
    x = photon / e0 - y0
    y = (x * x + y1 * y1).sqrt()
    shape1 = ((power / 2 - D("5.5")) * y.ln()).exp()
    shape2 = (-power * (ONE + (y / ya).sqrt()).ln()).exp()
    sigma_pi = D("1e-18") * sigma0 * ((x - ONE) ** 2 + yw * yw) * shape1 * shape2
    me, ev, light = D("9.1093837015e-31"), D("1.602176634e-19"), D("299792458")
    mec2 = me * light * light / ev
    sigma_rr = sigma_pi * photon * photon / (mec2 * energy)
    velocity = D(100) * (2 * energy * ev / me).sqrt()
    hazard = D("0.1") * velocity * sigma_rr
    return sigma_pi, sigma_rr, hazard


def dot(a, b):
    return sum((v * w for v, w in zip(a, b)), ZERO)


def source_rows(unit, old, ref, source_primary, case):
    rows = []
    for z in ["2.316", "2.479", "2.649"]:
        frozen = [exact(v) for v in old["source_" + z]]
        pop = frozen[1:]
        with (unit / f"inputs/reused/c23d/ATOMS_{z}.csv").open() as stream:
            atoms = list(csv.DictReader(stream))
        energies = [exact(float(v["W_eV"])) for v in atoms]
        masses = [exact(float(v["pulse_count_cm3"])) for v in atoms]
        q = exact(old["E_eV"][0])
        active_mask = old["active_mask_" + z]
        need(len(atoms) == 384, "SOURCE_ATOM_COUNT")
        need(all(bool(mask) == (e > q) for mask, e in zip(active_mask, energies)), "FROZEN_ACTIVE_MASK")
        active = sum((m for m, flag in zip(masses, active_mask) if flag), ZERO)
        selected = sum(masses, ZERO)
        projected_mass = sum(frozen, ZERO)
        original_energy = dot(masses, energies)
        active_energy = sum((m * e for m, e, flag in zip(masses, energies, active_mask) if flag), ZERO)
        projected_energy = dot(frozen, [exact(e) for e in old["E_eV"]])
        need(relative(projected_mass, active) <= D("2e-12") and relative(projected_energy, active_energy) <= D("2e-12"), "SAVED_SOURCE_IDENTITY")
        moments = [dot(pop, vector) for vector in ref]
        rr, rr_e, rr_time = moments[6], moments[7], moments[16]
        eta = max(ref[19])
        photon, internal = rr_e + D("13.60") * rr, -D("13.60") * rr
        ce = moments[0] + moments[1]
        old_ce = dot(pop, [exact(a) + exact(b) for a, b in zip(old["u_s"], old["u_p"])])
        old_time = dot(pop, [exact(v) for v in old["t"]])
        entry = q * (moments[2] + frozen[0])
        inactive = sum((m * e for m, e, flag in zip(masses, energies, active_mask) if not flag), ZERO)
        ce_in = moments[4] + moments[5]
        gap = D("10.20435")
        final_terms = moments[8:14] + [entry, inactive, ce_in - gap * ce, gap * ce, photon, internal]
        energy_residual = abs(sum(final_terms, ZERO) - original_energy) / (sum(map(abs, final_terms), ZERO) + original_energy)
        vals = {"P_RR_active": rr / active, "P_RR_selected": rr / selected,
                "conditional_RR_kinetic_eV": rr_e / rr, "conditional_RR_photon_eV": photon / rr,
                "conditional_RR_time_s": rr_time / rr,
                "RR_photon_eV_per_selected": photon / selected, "RR_internal_eV_per_selected": internal / selected,
                "P_CE_active": ce / active, "mean_stop_s_active": moments[3] / active,
                "delta_CE_active": moments[17] / active, "delta_time_s_active": moments[18] / active,
                "paired_CE_relative_to_old": moments[17] / old_ce,
                "paired_time_relative_to_old": moments[18] / old_time,
                "source_bound_lower": moments[19] / (ONE + eta) / active,
                "source_bound_upper": moments[19] / active}
        production = next(v for v in source_primary if v["case"] == case and v["z"] == z)
        differences = {k: float(relative(exact(production[k]), v)) for k, v in vals.items()}
        need(energy_residual <= D("2e-8"), "INDEPENDENT_SOURCE_ENERGY")
        need(vals["source_bound_lower"] <= vals["P_RR_active"] <= vals["source_bound_upper"], "INDEPENDENT_SOURCE_RARE_BOUND")
        rows.append({"case": case, "z": z, "reference_decimal": {k: str(v) for k, v in vals.items()},
                     "primary_relative_differences": differences,
                     "source_projection_reused_without_reprojection": True,
                     "scaled_energy_residual": float(energy_residual),
                     "six_bath_signed_gains_eV_cm3": [str(v) for v in moments[8:14]],
                     "RR_photon_eV_cm3": str(photon), "RR_internal_eV_cm3": str(internal),
                     "diagnostic_removed_electron_eV_cm3": str(rr_e)})
    return rows


def run(unit, output, run_id):
    started = time.process_time()
    actual = 0
    completed_cases = []
    comparisons = []
    coefficient_rows = []
    sources = []
    pins = []
    try:
        config = json.loads((unit / "inputs/CONFIG.json").read_text())
        need(run_id == config["review_run_id"], "REVIEW_RUN_ID")
        need(file_pin(unit / "FROZEN_CONTRACT.md")["sha256"] == CONTRACT_SHA, "CONTRACT_PIN")
        manifest = json.loads((unit / "inputs/INPUT_MANIFEST.json").read_text())
        for row in manifest["files"]:
            pin = file_pin(unit / row["path"])
            need(pin["bytes"] == row["bytes"] and pin["sha256"] == row["sha256"], "INPUT_PIN:" + row["path"])
        addendum = json.loads((unit / "review/R6_ADDENDUM_COEFFICIENT_CRITERION.json").read_text())
        need(addendum["status"] == "FROZEN_PREEXECUTION" and addendum["coefficient_relative_tolerance"] == 5e-13, "COEFFICIENT_CRITERION")
        for k, v in {"I_eV": 13.6, "n_HII_cm3": 0.1, "d": 1, "g_H": 2, "g_p": 1,
                     "electron_mass_kg": 9.1093837015e-31, "eV_J": 1.602176634e-19,
                     "c_m_s": 299792458.0, "gap_eV": 10.20435}.items():
            need(config[k] == v, "CONSTANT_PIN:" + k)
        primary = unit / "runs" / config["primary_run_id"]
        primary_result = json.loads((primary / "RESULT.json").read_text())
        need(primary_result["status"] == "PASS" and primary_result["actual_primary_RHS"] == 160, "PRIMARY_NOT_READY")
        primary_sources = json.loads((primary / "SOURCE_WEIGHTED_RESULTS.json").read_text())["rows"]
        row = table_row(unit / "inputs/reused/c23b/data/verner_photo.dat")
        for case in CASES:
            primary_file = primary / (case + ".npz")
            pins.append({"case": case, "primary_npz": file_pin(primary_file)})
            with np.load(unit / "inputs/reused/pr104" / (case + ".npz"), allow_pickle=False) as loaded:
                old = {k: loaded[k] for k in loaded.files}
            with np.load(primary_file, allow_pickle=False) as loaded:
                new = {k: loaded[k] for k in loaded.files}
            for new_key, old_key in [("E_eV", "E_eV"), ("K0_diag", "K_diag"), ("K_lower", "K_lower"), ("K_upper", "K_upper")]:
                need(np.array_equal(new[new_key], old[old_key]), "FROZEN_ARRAY:" + new_key)
            need(np.array_equal(new["rhs_physical14"][:, :6], old["rhs_first6"]), "FIRST6_CHANGED")
            need(np.array_equal(new["rhs_physical14"][:, 8:14], old["rhs_bath6"]), "BATH6_CHANGED")
            need(np.array_equal(new["lambda_RR"], new["lambda_RR_s_inverse"]), "LAMBDA_ALIAS")
            energy = [exact(v) for v in old["E_eV"][1:]]
            d0, lower, upper = [[exact(v) for v in old["K_" + k]] for k in ["diag", "lower", "upper"]]
            lam = [exact(v) for v in new["lambda_RR"]]
            diag = [a + b for a, b in zip(d0, lam)]
            n = len(diag)
            need(all(v > ZERO for v in lam), "POSITIVE_RATE")
            indices = [j * (n - 1) // 35 for j in range(36)]
            need(len(set(indices)) == 36, "COEFFICIENT_SAMPLE_COUNT")
            for j in indices:
                independent = coefficient(energy[j], row)
                values = {}
                for key, reference in zip(["sigma_PI_cm2", "sigma_RR_cm2", "lambda_RR_s_inverse"], independent):
                    error = relative(exact(new[key][j]), reference)
                    need(error <= COEF_TOL, "INDEPENDENT_COEFFICIENT:" + case + ":" + key)
                    values[key] = {"reference_decimal": str(reference), "primary": float(new[key][j]), "relative_difference": float(error)}
                coefficient_rows.append({"case": case, "active_index": j, "energy_eV_exact": str(energy[j]), "values": values})
            fnew = factor(diag, lower, upper)
            f0 = factor(d0, lower, upper)
            rhs = [[exact(v) for v in old["rhs_first6"][:, k]] for k in range(6)]
            rhs += [lam, [a * b for a, b in zip(lam, energy)]]
            rhs += [[exact(v) for v in old["rhs_bath6"][:, k]] for k in range(6)]
            ref = []
            for b in rhs:
                actual += 1
                ref.append(solve(fnew, upper, b))
            # Recompute marked-time RHS from independent probabilities, not primary.
            for idx in [0, 1, 6]:
                b = list(ref[idx])
                rhs.append(b)
                actual += 1
                ref.append(solve(fnew, upper, b))
            old_ce = [exact(a) + exact(b) for a, b in zip(old["u_s"], old["u_p"])]
            old_time = [exact(v) for v in old["t"]]
            for old_vector in [old_ce, old_time]:
                b = [-a * v for a, v in zip(lam, old_vector)]
                rhs.append(b)
                actual += 1
                ref.append(solve(fnew, upper, b))
            rhs.append(lam)
            actual += 1
            ref.append(solve(f0, upper, lam))
            primary_cols = [new["solution_physical14"][:, k] for k in range(14)]
            primary_cols += [new["solution_conditional3"][:, k] for k in range(3)]
            primary_cols += [new["solution_response2"][:, k] for k in range(2)] + [new["w"]]
            for k, name in enumerate(NAMES):
                x = [exact(v) for v in primary_cols[k]]
                scale = max(map(abs, ref[k]))
                need(scale > ZERO, "ZERO_COLUMN_NORM:" + name)
                difference = max(abs(a - b) for a, b in zip(x, ref[k])) / scale
                matrix_diag = d0 if k == 19 else diag
                primary_backward = backward(matrix_diag, lower, upper, x, rhs[k])
                independent_backward = backward(matrix_diag, lower, upper, ref[k], rhs[k])
                ok = difference <= NORM_TOL and primary_backward <= LINEAR_TOL and independent_backward <= LINEAR_TOL
                comparisons.append({"case": case, "rhs": name, "relative_infinity_norm_difference": float(difference),
                                    "reference_infinity_norm": str(scale), "primary_scaled_backward_intended_operator": float(primary_backward),
                                    "reference_scaled_backward": float(independent_backward), "pass_scoped": ok})
            q, gap, binding = exact(old["E_eV"][0]), D("10.20435"), D("13.60")
            eta = max(ref[19])
            partition = energy_error = event_error = ZERO
            loss_abs = loss_rate = ZERO
            upper_violation = lower_violation = ZERO
            for j in range(n):
                ce = ref[0][j] + ref[1][j]
                rr, rre = ref[6][j], ref[7][j]
                need(rr > ZERO and ref[19][j] > ZERO, "REFERENCE_RR_POSITIVITY")
                need(ref[17][j] <= ZERO and ref[18][j] <= ZERO, "REFERENCE_RESPONSE_SIGN")
                lower_bound = ref[19][j] / (ONE + eta)
                upper_violation = max(upper_violation, (rr - ref[19][j]) / ref[19][j])
                lower_violation = max(lower_violation, (lower_bound - rr) / lower_bound)
                partition = max(partition, abs(ce + ref[2][j] + rr - ONE))
                ce_in = ref[4][j] + ref[5][j]
                photon, internal = rre + binding * rr, -binding * rr
                terms = [ref[k][j] for k in range(8, 14)] + [q * ref[2][j], ce_in - gap * ce, gap * ce, photon, internal]
                energy_error = max(energy_error, abs(sum(terms, ZERO) - energy[j]) / (sum(map(abs, terms), ZERO) + energy[j]))
                primary_photon, primary_internal, primary_rr_e = exact(new["photon_RR"][j]), exact(new["internal_RR"][j]), exact(new["r_RR"][j])
                event_error = max(event_error, abs(primary_photon + primary_internal - primary_rr_e) / (abs(primary_photon) + abs(primary_internal) + abs(primary_rr_e)))
                need(primary_photon > ZERO and primary_internal < ZERO, "PRIMARY_RR_REWARD_SIGN")
                lost = abs(exact(new["K_diag"][j]) - diag[j])
                loss_abs, loss_rate = max(loss_abs, lost), max(loss_rate, lost / lam[j])
            need(partition <= D("2e-8") and energy_error <= D("2e-8"), "REFERENCE_PARTITION_OR_ENERGY")
            need(event_error <= D("5e-13"), "RR_EVENT_SCALE_ENERGY")
            need(max(upper_violation, lower_violation) <= NORM_TOL, "REFERENCE_RARE_BOUND")
            need(min(ref[k][j] for k in [0, 1, 2, 6] for j in range(n)) >= -D("2e-10"), "REFERENCE_PROBABILITY_MIN")
            need(max(ref[k][j] for k in [0, 1, 2, 6] for j in range(n)) <= ONE + D("2e-10"), "REFERENCE_PROBABILITY_MAX")
            with (output / (case + "_DECIMAL70.csv")).open("x", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["active_index", "E_eV_exact"] + NAMES)
                writer.writerows([j, str(energy[j])] + [str(vector[j]) for vector in ref] for j in range(n))
            sources.extend(source_rows(unit, old, ref, primary_sources, case))
            completed_cases.append({"case": case, "active_nodes": n, "independent_RHS": 20,
                                    "new_operator_positive_pivot_min": str(min(fnew[0])), "old_operator_positive_pivot_min": str(min(f0[0])),
                                    "eta": str(eta), "partition_maxabs": float(partition), "energy_scaled_residual": float(energy_error),
                                    "primary_RR_event_energy_relative": float(event_error),
                                    "rare_upper_relative_violation": float(upper_violation), "rare_lower_relative_violation": float(lower_violation),
                                    "diagonal_addition_lost_rate_max_abs": float(loss_abs), "diagonal_addition_loss_relative_to_lambda_max": float(loss_rate)})
            print(case + " independent_RHS=" + str(actual), flush=True)
        need(actual == 40 and len(comparisons) == 40 and len(coefficient_rows) == 72, "PLANNED_REVIEW_COUNTS")
        passed = all(v["pass_scoped"] for v in comparisons)
        write_json(output / "COLUMN_COMPARISONS.json", comparisons)
        write_json(output / "SELECTED_COEFFICIENTS.json", coefficient_rows)
        write_json(output / "INDEPENDENT_SOURCE_ROWS.json", sources)
        result = {"schema": "N5_RR_INDEPENDENT_DECIMAL70_C9_V1", "status": "PASS" if passed else "FAILED_RETAINED",
                  "run_id": run_id, "reviewer": "independent Astra current_provider_census", "delegated_lower_tier": False,
                  "arithmetic": "Python standard Decimal precision70; exact Decimal.from_float saved operands; intended unrounded K0+lambda",
                  "contract_sha256": CONTRACT_SHA, "criteria_frozen_before_execution": True,
                  "per_RHS_own_norm_tolerance": float(NORM_TOL), "coefficient_relative_tolerance": float(COEF_TOL),
                  "planned_RHS": 40, "actual_RHS": actual, "cases": completed_cases, "primary_input_pins": pins,
                  "independent_selected_coefficient_nodes": len(coefficient_rows), "independent_source_rows": len(sources),
                  "max_per_RHS_relative_infinity_norm_difference": max(v["relative_infinity_norm_difference"] for v in comparisons),
                  "max_primary_intended_backward_residual": max(v["primary_scaled_backward_intended_operator"] for v in comparisons),
                  "max_reference_backward_residual": max(v["reference_scaled_backward"] for v in comparisons),
                  "max_selected_coefficient_relative_difference": max(a["relative_difference"] for v in coefficient_rows for a in v["values"].values()),
                  "failed_columns": [v for v in comparisons if not v["pass_scoped"]],
                  "conditional_time_rhs": "independent probability solutions", "response_old_vectors": "immutable saved PR104 vectors; their uncertainty remains inherited",
                  "old_primary_replay": 0, "production_module_imports": 0, "old_generator_calls": 0, "source_projection_calls": 0,
                  "source_quadrature": 0, "thermal_rate_quadrature": 0, "new_ODE": 0,
                  "process_cpu_s": time.process_time() - started, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "global_error_bound": None, "global_model_error_bound": None, "global_completion_percent": None,
                  "EXECUTION": "COMPLETED", "PUBLICATION": "ROOT_OWNED", "BACKUP": "ROOT_PENDING", "DAG": "N5_PARTIAL_OPEN_N6_N7_NOT_ACTIVATED"}
        write_json(output / "RESULT.json", result)
        return 0 if passed else 1
    except Exception as error:
        write_json(output / "FAILURE.json", {"status": "FAILED_RETAINED", "type": type(error).__name__, "message": str(error),
                                             "attempted_RHS": actual, "completed_cases": completed_cases, "comparisons": comparisons,
                                             "coefficient_nodes_completed": len(coefficient_rows), "process_cpu_s": time.process_time() - started})
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.unit, args.output, args.run_id))
