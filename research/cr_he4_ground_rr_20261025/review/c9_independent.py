"""Independent Decimal70 check of the NEW HeI consumer, without production imports.

Saved binary operands define K_H1.  The reference uses the real sum of those
operands with the new He hazard, independent Thomas elimination, exact-product
RHS, and conditional-time RHS formed from independent probability solutions.
Only two selected R80,N2048 cases are solved; no historical baseline is rerun.
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
ZERO, ONE = D(0), D(1)
CONTRACT_SHA = "74e40fd91b5e409e7d785380dbf04cbc7416dbf9e8500e626c589946f35e133a"
NORM_TOL, COEF_TOL, LINEAR_TOL = D("5e-10"), D("5e-13"), D("2e-12")
CASES = ("chi1.5_R80_N2048", "chi3_R80_N2048")
NAMES = ("CE_s", "CE_p", "entry", "time", "CE_s_energy", "CE_p_energy",
         "H1_probability", "H1_kinetic", "He_probability", "He_kinetic",
         "bath_EE", "bath_H1plus", "bath_He4plus", "bath_He4doubleplus",
         "bath_H1neutral", "bath_He4neutral", "time_CE_s", "time_CE_p",
         "time_H1", "time_He", "delta_CE", "delta_time", "delta_H1", "w_He")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def exact(x):
    return D.from_float(float(x))


def pin(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), ZERO)


def relative(a, b):
    need(b != ZERO, "REFERENCE_SCALE_ZERO")
    return abs(a-b)/abs(b)


def factor(diag, lower, upper):
    pivots, multipliers = list(diag), []
    need(all(x > ZERO for x in diag), "REFERENCE_NONPOSITIVE_DIAGONAL")
    need(all(x <= ZERO for x in lower+upper), "REFERENCE_NOT_Z_MATRIX")
    for j, value in enumerate(lower):
        multiplier = value/pivots[j]
        multipliers.append(multiplier)
        pivots[j+1] -= multiplier*upper[j]
        need(pivots[j+1] > ZERO, "REFERENCE_NONPOSITIVE_PIVOT")
    return pivots, multipliers


def solve(factors, upper, rhs):
    pivots, multipliers = factors
    values = list(rhs)
    for j, multiplier in enumerate(multipliers):
        values[j+1] -= multiplier*values[j]
    values[-1] /= pivots[-1]
    for j in range(len(values)-2, -1, -1):
        values[j] = (values[j]-upper[j]*values[j+1])/pivots[j]
    return values


def backward(diag, lower, upper, solution, rhs):
    maximum = ZERO
    for j, value in enumerate(solution):
        terms = [diag[j]*value]
        if j:
            terms.append(lower[j-1]*solution[j-1])
        if j+1 < len(diag):
            terms.append(upper[j]*solution[j+1])
        residual = abs(sum(terms, ZERO)-rhs[j])
        scale = sum(map(abs, terms), ZERO)+abs(rhs[j])
        need(scale > ZERO or residual == ZERO, "ZERO_BACKWARD_SCALE")
        if scale:
            maximum = max(maximum, residual/scale)
    return maximum


def load_arrays(path):
    with np.load(path, allow_pickle=False) as stream:
        return {key: stream[key] for key in stream.files}


def native_he_row(path):
    rows = []
    for line in path.read_text().splitlines():
        fields = line.split()
        if fields[:2] == ["2", "2"]:
            rows.append(tuple(D(v) for v in fields[2:]))
    expected = tuple(map(D, ("24.59", "50000", "13.61", "949.2", "1.469",
                            "3.188", "2.039", ".4434", "2.136")))
    need(rows == [expected], "EXACT_HEI_NATIVE_ROW_REQUIRED")
    return rows[0]


def native_coefficient(energy, row):
    threshold, maximum, e0, sigma0, ya, power, yw, y0, y1 = row
    photon = energy+threshold
    need(energy > ZERO and threshold <= photon <= maximum, "REFERENCE_SOURCE_DOMAIN")
    x = photon/e0-y0
    y = (x*x+y1*y1).sqrt()
    sigma_pi = (D("1e-18")*sigma0*((x-ONE)**2+yw*yw)
                *((power/2-D("5.5"))*y.ln()).exp()
                *(-power*(ONE+(y/ya).sqrt()).ln()).exp())
    mass, ev, light = D("9.1093837015e-31"), D("1.602176634e-19"), D(299792458)
    sigma_rr = sigma_pi*photon*photon/(4*(mass*light*light/ev)*energy)
    speed = D(100)*(2*energy*ev/mass).sqrt()
    return sigma_pi, sigma_rr, D(".02")*speed*sigma_rr


def source_checks(unit, base, vectors, case, saved_rows):
    results = []
    q, gap, ih, ihe = exact(base["E_eV"][0]), D("10.20435"), D("13.60"), D("24.59")
    for z in ("2.316", "2.479", "2.649"):
        population = [exact(v) for v in base["source_"+z]]
        with (unit/f"inputs/reused/c23d/ATOMS_{z}.csv").open() as stream:
            atoms = list(csv.DictReader(stream))
        energy = [exact(float(row["W_eV"])) for row in atoms]
        masses = [exact(float(row["pulse_count_cm3"])) for row in atoms]
        mask = base["active_mask_"+z]
        need(len(atoms) == 384 and all(bool(flag) == (e > q) for e, flag in zip(energy, mask)), "FROZEN_SOURCE_MASK")
        selected = sum(masses, ZERO)
        active = sum((m for m, flag in zip(masses, mask) if flag), ZERO)
        active_energy = sum((m*e for m, e, flag in zip(masses, energy, mask) if flag), ZERO)
        need(relative(sum(population, ZERO), active) <= D("2e-12"), "SAVED_PROJECTED_MASS")
        need(relative(dot(population, [exact(v) for v in base["E_eV"]]), active_energy) <= D("2e-12"), "SAVED_PROJECTED_ENERGY")
        moments = [dot(population[1:], column) for column in vectors]
        ph, rh, pe, re = moments[6:10]
        h_photon, h_internal = rh+ih*ph, -ih*ph
        he_photon, he_internal = re+ihe*pe, -ihe*pe
        ce, ce_in = moments[0]+moments[1], moments[4]+moments[5]
        inactive = sum((m*e for m, e, flag in zip(masses, energy, mask) if not flag), ZERO)
        entry = q*(moments[2]+population[0])
        terms = moments[10:16]+[entry, inactive, ce_in-gap*ce, gap*ce,
                                h_photon, h_internal, he_photon, he_internal]
        initial = dot(masses, energy)
        residual = abs(sum(terms, ZERO)-initial)/(sum(map(abs, terms), ZERO)+initial)
        need(residual <= D("2e-8"), "INDEPENDENT_SOURCE_ENERGY")
        eta = max(vectors[23])
        values = {"P_He_RR_active": pe/active, "P_He_RR_selected": pe/selected,
                  "conditional_He_RR_kinetic_eV": re/pe,
                  "conditional_He_RR_photon_eV": he_photon/pe,
                  "conditional_He_RR_time_s": moments[19]/pe,
                  "He_RR_photon_eV_per_selected": he_photon/selected,
                  "He_RR_internal_eV_per_selected": he_internal/selected,
                  "P_H1_RR_active": ph/active, "P_CE_active": ce/active,
                  "mean_stop_s_active": moments[3]/active,
                  "delta_CE_active": moments[20]/active,
                  "delta_time_s_active": moments[21]/active,
                  "delta_H1_RR_active": moments[22]/active,
                  "source_bound_lower": moments[23]/(ONE+eta)/active,
                  "source_bound_upper": moments[23]/active}
        primary = next(row for row in saved_rows if row["case"] == case and row["z"] == z)
        errors = {name: float(relative(exact(primary[name]), value)) for name, value in values.items()}
        need(max(errors.values()) <= float(NORM_TOL), "INDEPENDENT_SOURCE_OBSERVABLE")
        need(values["source_bound_lower"] <= values["P_He_RR_active"] <= values["source_bound_upper"], "INDEPENDENT_SOURCE_RARE_BOUND")
        results.append({"case": case, "z": z, "reference_decimal": {k: str(v) for k, v in values.items()},
                        "primary_relative_differences": errors, "scaled_energy_residual": float(residual),
                        "photon_H1_eV_cm3": str(h_photon), "internal_H1_eV_cm3": str(h_internal),
                        "photon_He_eV_cm3": str(he_photon), "internal_He_eV_cm3": str(he_internal),
                        "source_projection_reused_without_reprojection": True})
    return results


def run(unit, output, run_id):
    start = time.process_time()
    actual, comparisons, coef_rows, cases, source_rows, primary_pins = 0, [], [], [], [], []
    try:
        config = json.loads((unit/"inputs/CONFIG.json").read_text())
        manifest = json.loads((unit/"inputs/INPUT_MANIFEST.json").read_text())
        need(run_id == config["review_run_id"], "REVIEW_RUN_ID")
        need(pin(unit/"FROZEN_CONTRACT.md")["sha256"] == CONTRACT_SHA, "CONTRACT_IDENTITY")
        need(pin(unit/"inputs/CONFIG.json")["sha256"] == manifest["config_sha256"], "CONFIG_IDENTITY")
        for row in manifest["files"]:
            need(pin(unit/row["path"]) == {"bytes": row["bytes"], "sha256": row["sha256"]}, "IMMUTABLE_INPUT:"+row["path"])
        primary = unit/"runs"/config["primary_run_id"]
        primary_result = json.loads((primary/"RESULT.json").read_text())
        need(primary_result["status"] == "PASS" and primary_result["actual_primary_RHS"] == 192, "PRIMARY_NOT_READY")
        saved_rows = json.loads((primary/"SOURCE_WEIGHTED_RESULTS.json").read_text())["rows"]
        row = native_he_row(unit/"inputs/reused/c23b/data/verner_photo.dat")
        for case in CASES:
            base = load_arrays(unit/"inputs/reused/pr104"/(case+".npz"))
            h1 = load_arrays(unit/"inputs/reused/pr105"/(case+".npz"))
            new = load_arrays(primary/(case+".npz"))
            primary_pins.append({"case": case, **pin(primary/(case+".npz"))})
            for key in ("E_eV", "K_lower", "K_upper"):
                need(np.array_equal(new[key], h1[key]) and np.array_equal(h1[key], base[key]), "INHERITED_ARRAY:"+key)
            need(np.array_equal(new["K_H1_diag"], h1["K_diag"]), "EXACT_STORED_H1_BASELINE")
            need(np.array_equal(new["lambda_H1"], h1["lambda_RR"]), "H1_HAZARD_REUSED")
            need(np.array_equal(new["rhs_physical16"][:, :6], base["rhs_first6"]), "FIRST6_REUSE")
            need(np.array_equal(new["rhs_physical16"][:, 10:16], base["rhs_bath6"]), "BATH6_REUSE")
            energies = [exact(v) for v in base["E_eV"][1:]]
            d0, lower, upper = [[exact(v) for v in h1["K_"+key]] for key in ("diag", "lower", "upper")]
            lam = [exact(v) for v in new["lambda_He"]]
            h = [exact(v) for v in h1["lambda_RR"]]
            diag = [a+b for a, b in zip(d0, lam)]
            need(all(v > ZERO for v in lam), "POSITIVE_HE_RATE")
            for j in (k*(len(diag)-1)//35 for k in range(36)):
                references = native_coefficient(energies[j], row)
                values = {}
                for key, reference in zip(("sigma_PI_He_cm2", "sigma_RR_He_cm2", "lambda_He"), references):
                    error = relative(exact(new[key][j]), reference)
                    need(error <= COEF_TOL, "INDEPENDENT_COEFFICIENT:"+case+":"+key)
                    values[key] = {"reference_decimal": str(reference), "relative_difference": float(error)}
                coef_rows.append({"case": case, "active_index": j, "energy_eV_exact": str(energies[j]), "values": values})
            fnew, f0 = factor(diag, lower, upper), factor(d0, lower, upper)
            rhs = [[exact(v) for v in base["rhs_first6"][:, k]] for k in range(6)]
            rhs += [h, [x*e for x, e in zip(h, energies)], lam, [x*e for x, e in zip(lam, energies)]]
            rhs += [[exact(v) for v in base["rhs_bath6"][:, k]] for k in range(6)]
            reference = []
            for b in rhs:
                actual += 1
                reference.append(solve(fnew, upper, b))
            for k in (0, 1, 6, 8):
                rhs.append(list(reference[k]))
                actual += 1
                reference.append(solve(fnew, upper, rhs[-1]))
            old_vectors = [[exact(a)+exact(b) for a, b in zip(h1["u_s"], h1["u_p"])],
                           [exact(v) for v in h1["t"]], [exact(v) for v in h1["p_RR"]]]
            for old in old_vectors:
                rhs.append([-a*x for a, x in zip(lam, old)])
                actual += 1
                reference.append(solve(fnew, upper, rhs[-1]))
            rhs.append(lam)
            actual += 1
            reference.append(solve(f0, upper, lam))
            production = [new["solution_physical16"][:, k] for k in range(16)]
            production += [new["solution_conditional4"][:, k] for k in range(4)]
            production += [new["solution_response3"][:, k] for k in range(3)]+[new["w"]]
            for k, name in enumerate(NAMES):
                values = [exact(v) for v in production[k]]
                scale = max(map(abs, reference[k]))
                need(scale > ZERO, "OWN_COLUMN_NORM_ZERO:"+name)
                difference = max(abs(a-b) for a, b in zip(values, reference[k]))/scale
                matrix = d0 if k == 23 else diag
                pb = backward(matrix, lower, upper, values, rhs[k])
                rb = backward(matrix, lower, upper, reference[k], rhs[k])
                comparisons.append({"case": case, "rhs": name, "reference_infinity_norm": str(scale),
                                    "relative_infinity_norm_difference": float(difference),
                                    "primary_intended_scaled_backward": float(pb), "reference_scaled_backward": float(rb),
                                    "pass_scoped": bool(difference <= NORM_TOL and pb <= LINEAR_TOL and rb <= LINEAR_TOL)})
            eta = max(reference[23])
            partition = energy_error = event_error = loss_rate = loss_abs = upper_v = lower_v = ZERO
            q, gap, ih, ihe = exact(base["E_eV"][0]), D("10.20435"), D("13.60"), D("24.59")
            for j, energy in enumerate(energies):
                ce = reference[0][j]+reference[1][j]
                ph, rh, pe, re = [reference[k][j] for k in (6, 7, 8, 9)]
                w = reference[23][j]
                need(pe > ZERO and w > ZERO, "REFERENCE_HE_POSITIVITY")
                need(all(reference[k][j] <= ZERO for k in (20, 21, 22)), "REFERENCE_RESPONSE_SIGN")
                pvals = [reference[k][j] for k in (0, 1, 2, 6, 8)]
                need(min(pvals) >= -D("2e-10") and max(pvals) <= ONE+D("2e-10"), "REFERENCE_PROBABILITY_RANGE")
                partition = max(partition, abs(sum(pvals, ZERO)-ONE))
                lower_bound = w/(ONE+eta)
                upper_v, lower_v = max(upper_v, (pe-w)/w), max(lower_v, (lower_bound-pe)/lower_bound)
                ce_in = reference[4][j]+reference[5][j]
                terms = [reference[k][j] for k in range(10, 16)]+[q*reference[2][j], ce_in-gap*ce, gap*ce,
                        rh+ih*ph, -ih*ph, re+ihe*pe, -ihe*pe]
                energy_error = max(energy_error, abs(sum(terms, ZERO)-energy)/(sum(map(abs, terms), ZERO)+energy))
                for label in ("H1", "He"):
                    photon, internal, kinetic = [exact(new[prefix+label][j]) for prefix in ("photon_", "internal_", "r_")]
                    need(photon > ZERO and internal < ZERO, "PRIMARY_REWARD_SIGNS")
                    event_error = max(event_error, abs(photon+internal-kinetic)/(abs(photon)+abs(internal)+abs(kinetic)))
                loss = abs(exact(new["K_diag"][j])-diag[j])
                loss_abs, loss_rate = max(loss_abs, loss), max(loss_rate, loss/lam[j])
            need(partition <= D("2e-8") and energy_error <= D("2e-8"), "REFERENCE_PARTITION_ENERGY")
            need(event_error <= D("5e-13"), "RR_EVENT_SCALE_ENERGY")
            need(max(upper_v, lower_v) <= NORM_TOL, "REFERENCE_RARE_BOUND")
            with (output/(case+"_DECIMAL70.csv")).open("x", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(("active_index", "E_eV_exact")+NAMES)
                writer.writerows([j, str(energy)]+[str(v[j]) for v in reference] for j, energy in enumerate(energies))
            source_rows.extend(source_checks(unit, base, reference, case, saved_rows))
            cases.append({"case": case, "independent_RHS": 24, "active_nodes": len(diag), "eta": str(eta),
                          "stored_H1_positive_pivot_min": str(min(f0[0])), "new_positive_pivot_min": str(min(fnew[0])),
                          "partition_maxabs": float(partition), "energy_scaled_residual": float(energy_error),
                          "RR_event_scale_energy_residual": float(event_error), "rare_upper_violation": float(upper_v),
                          "rare_lower_violation": float(lower_v), "new_diagonal_addition_loss_abs": float(loss_abs),
                          "new_diagonal_addition_loss_relative_to_He": float(loss_rate)})
            print(case+" independent_RHS="+str(actual), flush=True)
        need(actual == 48 and len(comparisons) == 48 and len(coef_rows) == 72, "EXPECTED_REVIEW_COUNTS")
        passed = all(row["pass_scoped"] for row in comparisons)
        write(output/"COLUMN_COMPARISONS.json", comparisons)
        write(output/"SELECTED_COEFFICIENTS.json", coef_rows)
        write(output/"INDEPENDENT_SOURCE_ROWS.json", source_rows)
        result = {"schema": "CR_HE4_INDEPENDENT_DECIMAL70_C9_V1", "status": "PASS" if passed else "FAILED_RETAINED",
                  "reviewer": "independent he4_source_audit agent", "run_id": run_id, "arithmetic": "Decimal70",
                  "baseline": "exact Decimal.from_float stored PR105 K_diag; new diagonal adds Decimal(lambda_He)",
                  "RHS": "independent exact products and independent probability conditional-time RHS",
                  "contract_sha256": CONTRACT_SHA, "planned_RHS": 48, "actual_RHS": actual,
                  "coefficient_nodes": len(coef_rows), "source_rows": len(source_rows), "cases": cases,
                  "primary_input_pins": primary_pins, "per_RHS_own_norm_tolerance": float(NORM_TOL),
                  "coefficient_relative_tolerance": float(COEF_TOL), "RR_event_relative_tolerance": 5e-13,
                  "max_per_RHS_relative_infinity_norm_difference": max(v["relative_infinity_norm_difference"] for v in comparisons),
                  "max_primary_intended_backward_residual": max(v["primary_intended_scaled_backward"] for v in comparisons),
                  "max_reference_backward_residual": max(v["reference_scaled_backward"] for v in comparisons),
                  "max_coefficient_relative_difference": max(x["relative_difference"] for v in coef_rows for x in v["values"].values()),
                  "max_source_observable_relative_difference": max(max(v["primary_relative_differences"].values()) for v in source_rows),
                  "failed_columns": [v for v in comparisons if not v["pass_scoped"]],
                  "production_module_imports": 0, "old_primary_replay": 0, "old_generator_calls": 0,
                  "source_projection_calls": 0, "source_quadrature": 0, "thermal_rate_quadrature": 0, "new_ODE": 0,
                  "process_cpu_s": time.process_time()-start, "observed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "global_error_bound": None, "global_completion_percent": None,
                  "N6": "PREDECESSOR_GATED", "N7": "PREDECESSOR_GATED"}
        write(output/"RESULT.json", result)
        return 0 if passed else 1
    except Exception as error:
        write(output/"FAILURE.json", {"status": "FAILED_RETAINED", "type": type(error).__name__, "message": str(error),
                                     "attempted_RHS": actual, "completed_cases": cases, "comparisons": comparisons,
                                     "coefficient_nodes_completed": len(coef_rows), "process_cpu_s": time.process_time()-start})
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.unit, args.output, args.run_id))
