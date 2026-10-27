#!/usr/bin/env python3
"""Independent Decimal70 qualification of the saved-K RR clock recurrence.

Preparation does not execute this file. Root must first freeze C4, the exact
input/code/output pins and a create-only bounded dispatcher lease. This worker
imports no production or microscopic-provider module. NumPy is used only for
immutable NPZ data, not linear algebra. Decimal70 approximate solves are enclosed
with independent directed Decimal100 residual/witness bounds. The production
certificate for its full campaign is still reviewed separately.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import time
import traceback

D = Decimal
ZERO = D(0)
PRECISION = 70
CERT_PRECISION = 100
DOWN = Context(prec=CERT_PRECISION, rounding=ROUND_FLOOR)
UP = Context(prec=CERT_PRECISION, rounding=ROUND_CEILING)
OWN_RELATIVE_LIMIT = D("5e-10")
MAX_CPU_S = 15.0
MEMORY_BYTES = 512 * 1024**2
Z_VALUES = ("2.316", "2.479", "2.649")
REWARDS = (("count", 10), ("kinetic", 11))
BASELINES = {
    "chi1.5_R80_N2048": {
        "T_s": 100000.0, "n": 2479,
        "heiii_sha256": "44171ed99a638bf33eb4ec969bb6b91eb61a6deec5aea4d1d809e63363c45f4e",
        "source_sha256": "883c2bb5fd658d3ecc1c7b423bc9d3282d7da08fd1763ffbb63733985c878f20",
    },
    "chi3_R80_N2048": {
        "T_s": 1000000.0, "n": 2479,
        "heiii_sha256": "7334e37ecf555a01dd83d769600166a7d8115a62a57f5646227ad2301e379aa3",
        "source_sha256": "46965a9669350f38ede9825ecb96e0b1b3ecec6c0a9fd4ad7541f1785c79ecff",
    },
}


class ReferenceFailure(RuntimeError):
    pass


class BudgetStop(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise ReferenceFailure(message)


def check_budget(state):
    if time.process_time() >= state["cpu_guard_s"]:
        raise BudgetStop("REFERENCE_CPU_GUARD")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path):
    with Path(path).open() as stream:
        return json.load(stream)


def write_new_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def binary64_decimal(value):
    """Exact real represented by one finite binary64 scalar."""
    require(not isinstance(value, bool), "BOOLEAN_NUMERIC_INPUT")
    number = float(value)
    require(math.isfinite(number), "NONFINITE_BINARY64_INPUT")
    return D.from_float(number)


def encoded_decimal(value):
    """Decode JSON float as binary64, hex as binary64, decimal text as exact text.

    JSON bounds must denote the actual exported outward endpoint. A producer
    converting a bound to decimal text must already have accounted for that
    serialization; this reader does not silently widen its declared bound.
    """
    require(not isinstance(value, bool), "BOOLEAN_ENCODED_NUMBER")
    if isinstance(value, float):
        return binary64_decimal(value)
    if isinstance(value, int):
        return D(value)
    require(isinstance(value, str), "ENCODED_NUMBER_TYPE")
    if "0x" in value.lower():
        return binary64_decimal(float.fromhex(value))
    result = D(value)
    require(result.is_finite(), "NONFINITE_DECIMAL_TEXT")
    return result


def file_pin(root, record, state, role):
    require(isinstance(record, dict), "FILE_PIN_OBJECT:" + role)
    path = Path(record["path"])
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    observed_sha = sha256(path)
    require(observed_sha == record["sha256"], "FILE_SHA256:" + role)
    if "bytes" in record:
        require(not isinstance(record["bytes"], bool)
                and path.stat().st_size == record["bytes"], "FILE_SIZE:" + role)
    state["input_pins"].append({"role": role, "path": str(path),
                                "bytes": path.stat().st_size,
                                "sha256": observed_sha})
    return path


def floating_array(np, archive, name, shape, nonnegative=False):
    require(name in archive, "MISSING_ARRAY:" + name)
    array = np.asarray(archive[name])
    require(array.dtype.kind == "f" and array.dtype.itemsize == 8,
            "BINARY64_REQUIRED:" + name)
    require(array.shape == shape, "ARRAY_SHAPE:" + name)
    require(bool(np.all(np.isfinite(array))), "NONFINITE_ARRAY:" + name)
    if nonnegative:
        require(bool(np.all(array >= 0)), "NEGATIVE_ARRAY:" + name)
    return array.copy()


def factor_decimal(diagonal, lower, upper, gamma, state):
    """Independent scalar Thomas factorization in the Decimal70 context."""
    check_budget(state)
    pivots = [value + gamma for value in diagonal]
    multipliers = []
    require(pivots[0] > 0, "NONPOSITIVE_REFERENCE_PIVOT:0")
    for i in range(1, len(pivots)):
        multiplier = lower[i - 1] / pivots[i - 1]
        multipliers.append(multiplier)
        pivots[i] -= multiplier * upper[i - 1]
        require(pivots[i] > 0, "NONPOSITIVE_REFERENCE_PIVOT:" + str(i))
    state["factorizations"] += 1
    check_budget(state)
    return pivots, multipliers, upper


def solve_decimal(factor, rhs, state):
    check_budget(state)
    pivots, multipliers, upper = factor
    work = list(rhs)
    for i in range(1, len(work)):
        work[i] -= multipliers[i - 1] * work[i - 1]
    work[-1] /= pivots[-1]
    for i in range(len(work) - 2, -1, -1):
        work[i] = (work[i] - upper[i] * work[i + 1]) / pivots[i]
    state["reference_rhs_solved"] += 1
    check_budget(state)
    return work


def reference_residual(diagonal, lower, upper, gamma, solution, rhs):
    """Decimal100 diagnostic of the Decimal70 solve, not an interval proof."""
    with localcontext() as context:
        context.prec = 100
        largest = ZERO
        for i, value in enumerate(solution):
            central = (diagonal[i] + gamma) * value
            scale = abs(central) + abs(rhs[i])
            ax = central
            if i:
                term = lower[i - 1] * solution[i - 1]
                ax += term
                scale += abs(term)
            if i + 1 < len(solution):
                term = upper[i] * solution[i + 1]
                ax += term
                scale += abs(term)
            residual = abs(rhs[i] - ax)
            ratio = residual / scale if scale else ZERO
            require(scale != 0 or residual == 0, "ZERO_REFERENCE_RESIDUAL_SCALE")
            largest = max(largest, ratio)
        return largest


def image_interval_at(diagonal, lower, upper, gamma, vector, i):
    """Outward enclosure of the exact row of (K+gamma I)*vector.

    Every operand is an exact Decimal value (including Decimal.from_float).
    Separate diagonal and gamma products preserve the unrounded target shift.
    """
    low = DOWN.multiply(diagonal[i], vector[i])
    high = UP.multiply(diagonal[i], vector[i])
    if gamma:
        low = DOWN.add(low, DOWN.multiply(gamma, vector[i]))
        high = UP.add(high, UP.multiply(gamma, vector[i]))
    if i:
        low = DOWN.add(low, DOWN.multiply(lower[i - 1], vector[i - 1]))
        high = UP.add(high, UP.multiply(lower[i - 1], vector[i - 1]))
    if i + 1 < len(vector):
        low = DOWN.add(low, DOWN.multiply(upper[i], vector[i + 1]))
        high = UP.add(high, UP.multiply(upper[i], vector[i + 1]))
    return low, high


def certify_witness(base, h):
    """Independent directed proof of Kh >= beta*h > 0 for exact stored K."""
    witness = [binary64_decimal(value) for value in h]
    require(all(value > 0 for value in witness), "REFERENCE_POSITIVE_WITNESS")
    beta = None
    for i, value in enumerate(witness):
        low, _ = image_interval_at(base["diagonal"], base["lower"], base["upper"],
                                  ZERO, witness, i)
        require(low > 0, "REFERENCE_WITNESS_KH_NOT_STRICT:" + str(i))
        ratio = DOWN.divide(low, value)
        beta = ratio if beta is None else min(beta, ratio)
    require(beta is not None and beta > 0, "REFERENCE_WITNESS_BETA")
    return witness, beta


def enclose_reference_step(base, gamma, witness, beta, solution, reward_index,
                           previous, previous_epsilon):
    """Enclose the exact recurrence, including inherited Decimal70 error.

    For j>0, gamma*previous is the exact intended right-hand side of the
    residual even though the numerical Decimal70 solve used a rounded product.
    """
    eta = ZERO
    for i, h_i in enumerate(witness):
        ax_low, ax_high = image_interval_at(base["diagonal"], base["lower"],
                                           base["upper"], gamma, solution, i)
        if previous is None:
            rhs_low = rhs_high = base["rhs"][reward_index][i]
        else:
            rhs_low = DOWN.multiply(gamma, previous[i])
            rhs_high = UP.multiply(gamma, previous[i])
        residual_low = DOWN.subtract(rhs_low, ax_high)
        residual_high = UP.subtract(rhs_high, ax_low)
        absolute_upper = max(residual_low.copy_abs(), residual_high.copy_abs())
        eta = max(eta, UP.divide(absolute_upper, h_i))
    alpha_lower = DOWN.add(beta, gamma)
    inherited_upper = UP.multiply(gamma, previous_epsilon)
    epsilon = UP.divide(UP.add(inherited_upper, eta), alpha_lower)
    lows, highs = [], []
    for value, h_i in zip(solution, witness):
        width = UP.multiply(epsilon, h_i)
        lows.append(max(ZERO, DOWN.subtract(value, width)))
        highs.append(UP.add(value, width))
    return epsilon, eta, lows, highs


def compare_vector(state, name, center, radius, reference, reference_low, reference_high,
                   *, epsilon=None, h=None):
    require(len(center) == len(reference) == len(radius), "COMPARE_VECTOR_SHAPE")
    norm = max(map(abs, reference), default=ZERO)
    largest_error = ZERO
    rigorous_error_upper = ZERO
    true_norm_lower = max(reference_low, default=ZERO)
    minimum_margin = None
    worst_index = 0
    outside = 0
    outside_epsilon = 0
    for i, (observed, width, expected) in enumerate(zip(center, radius, reference)):
        encoded_center = binary64_decimal(observed)
        error = abs(encoded_center - expected)
        difference_low = DOWN.subtract(encoded_center, reference_high[i])
        difference_high = UP.subtract(encoded_center, reference_low[i])
        exact_error_upper = max(difference_low.copy_abs(), difference_high.copy_abs())
        bound = binary64_decimal(width)
        require(bound >= 0, "NEGATIVE_PRODUCTION_RADIUS")
        margin = DOWN.subtract(bound, exact_error_upper)
        if minimum_margin is None or margin < minimum_margin:
            minimum_margin, worst_index = margin, i
        largest_error = max(largest_error, error)
        rigorous_error_upper = max(rigorous_error_upper, exact_error_upper)
        outside += int(margin < 0)
        if epsilon is not None:
            epsilon_radius_lower = DOWN.multiply(epsilon, binary64_decimal(h[i]))
            outside_epsilon += int(exact_error_upper > epsilon_radius_lower)
    relative_upper = UP.divide(rigorous_error_upper, true_norm_lower) if true_norm_lower else None
    own_relative_pass = (relative_upper <= OWN_RELATIVE_LIMIT if relative_upper is not None
                         else rigorous_error_upper == 0)
    passed = outside == 0 and outside_epsilon == 0 and own_relative_pass
    row = {"name": name, "components": len(reference), "pass_scoped": passed,
           "out_of_radius_components": outside, "worst_margin_index": worst_index,
           "out_of_epsilon_h_components": outside_epsilon if epsilon is not None else None,
           "minimum_radius_margin": str(minimum_margin),
           "own_reference_infinity_norm": str(norm),
           "absolute_infinity_error": str(largest_error),
           "relative_infinity_error": str(largest_error / norm) if norm else None,
           "exact_solution_error_upper": str(rigorous_error_upper),
           "exact_solution_norm_lower": str(true_norm_lower),
           "own_column_relative_upper": str(relative_upper) if relative_upper is not None else None,
           "own_column_relative_limit": str(OWN_RELATIVE_LIMIT),
           "own_column_relative_pass": own_relative_pass,
           "evidence_type": "independent directed reference enclosure inside exported production radius"}
    state["vector_comparisons"].append(row)
    if not passed:
        state["failures"].append(name)


def compare_scalar(state, name, fields, expected, reference_lower, reference_upper):
    lower = encoded_decimal(fields["A_lower"])
    upper = encoded_decimal(fields["A_upper"])
    nominal = encoded_decimal(fields["A_nominal"])
    require(lower <= upper, "INVERTED_PRODUCTION_SCALAR_INTERVAL:" + name)
    passed = lower <= reference_lower <= reference_upper <= upper
    row = {"name": name, "reference": str(expected), "lower": str(lower),
           "upper": str(upper), "nominal": str(nominal),
           "reference_lower": str(reference_lower), "reference_upper": str(reference_upper),
           "lower_margin": str(DOWN.subtract(reference_lower, lower)),
           "upper_margin": str(DOWN.subtract(upper, reference_upper)),
           "absolute_nominal_error": str(abs(nominal - expected)),
           "pass_scoped": passed,
           "evidence_type": "independent directed source-contraction interval inside exported A interval"}
    state["scalar_comparisons"].append(row)
    if not passed:
        state["failures"].append(name)


def dot_decimal(weights, values):
    return sum((left * right for left, right in zip(weights, values)), ZERO)


def read_case(np, root, case_record, state):
    case = case_record["case"]
    require(case in BASELINES, "UNFROZEN_REFERENCE_CASE")
    fixed = BASELINES[case]
    require(case_record["heiii_npz"]["sha256"] == fixed["heiii_sha256"],
            "SAVED_HEIII_BASELINE_PIN")
    require(case_record["source_npz"]["sha256"] == fixed["source_sha256"],
            "SAVED_SOURCE_BASELINE_PIN")
    matrix_file = file_pin(root, case_record["heiii_npz"], state, case + ":HeIII")
    source_file = file_pin(root, case_record["source_npz"], state, case + ":source")
    n = fixed["n"]
    with np.load(matrix_file, allow_pickle=False) as archive:
        diagonal = floating_array(np, archive, "K_diag", (n,))
        lower = floating_array(np, archive, "K_lower", (n - 1,))
        upper = floating_array(np, archive, "K_upper", (n - 1,))
        rhs = floating_array(np, archive, "rhs_physical18", (n, 18))
    require(bool(np.all(lower <= 0)) and bool(np.all(upper <= 0)), "K_Z_MATRIX_SIGN")
    require(bool(np.all(rhs[:, [10, 11]] >= 0)), "NEGATIVE_HEIII_REWARD")
    weights = {}
    boundary = {}
    with np.load(source_file, allow_pickle=False) as archive:
        for z in Z_VALUES:
            values = floating_array(np, archive, "source_" + z, (n + 1,), True)
            weights[z] = [binary64_decimal(value) for value in values[1:]]
            boundary[z] = str(binary64_decimal(values[0]))
    state["cases"].append({"case": case, "actual_n": n,
                           "boundary_projection0_retained": boundary,
                           "boundary_RR_reward": 0, "source_projection_replayed": False})
    return {
        "diagonal": [binary64_decimal(v) for v in diagonal],
        "lower": [binary64_decimal(v) for v in lower],
        "upper": [binary64_decimal(v) for v in upper],
        "rhs": [[binary64_decimal(v) for v in rhs[:, column]] for _, column in REWARDS],
        "weights": weights, "n": n,
    }


def review_clock(np, root, output, case_record, clock_record, base, state):
    check_budget(state)
    case = case_record["case"]
    label = clock_record["clock_label"]
    require(label in ("minus", "plus"), "CLOCK_LABEL")
    prefix = case + ":" + label
    metadata_file = file_pin(root, clock_record["metadata"], state, prefix + ":metadata")
    arrays_file = file_pin(root, clock_record["arrays"], state, prefix + ":arrays")
    metadata = load_json(metadata_file)
    require(metadata["case"] == case and metadata["clock_label"] == label, "CLOCK_IDENTITY")
    require(not isinstance(metadata["m"], bool) and metadata["m"] == 4, "REFERENCE_M4_ONLY")
    require(encoded_decimal(metadata["delta"]) == D("0.5"), "REFERENCE_DELTA_HALF")
    horizon = float(metadata["T_s"])
    require(horizon == BASELINES[case]["T_s"], "REFERENCE_HORIZON")
    gamma_float = float.fromhex(metadata["gamma_hex"])
    require(math.isfinite(gamma_float) and gamma_float > 0, "FINITE_POSITIVE_GAMMA")
    expected_gamma = 4.0 * (1.5 if label == "minus" else 0.5) / horizon
    require(gamma_float == expected_gamma, "ENCODED_GAMMA_FROZEN_DESIGN")
    gamma = binary64_decimal(gamma_float)
    a = gamma * binary64_decimal(horizon) / D(4)
    require(a > 1 if label == "minus" else ZERO < a < 1, "ACTUAL_CLOCK_DIRECTION")
    n = base["n"]
    with np.load(arrays_file, allow_pickle=False) as archive:
        centers = floating_array(np, archive, "z_steps", (4, n, 2))
        h = floating_array(np, archive, "h", (n,), True)
        eps = floating_array(np, archive, "epsilon_steps", (4, 2), True)
        radii = floating_array(np, archive, "step_radius", (4, n, 2), True)
        cumulative = floating_array(np, archive, "cumulative", (n, 2))
        cumulative_radius = floating_array(np, archive, "cumulative_radius", (n, 2), True)
    require(bool(np.all(h > 0)), "STRICT_POSITIVE_PRODUCTION_WITNESS")
    witness, beta = certify_witness(base, h)
    if "epsilon_steps_hex" in metadata:
        require(len(metadata["epsilon_steps_hex"]) == 4, "EPSILON_HEX_ROWS")
        for j in range(4):
            require(len(metadata["epsilon_steps_hex"][j]) == 2, "EPSILON_HEX_COLUMNS")
            for c in range(2):
                require(float.fromhex(metadata["epsilon_steps_hex"][j][c]) == float(eps[j, c]),
                        "EPSILON_HEX_NPZ_IDENTITY")
    # epsilon and step_radius can be separately rounded upper bounds. Do not
    # require step_radius >= encoded_epsilon*h: the product of the separately
    # rounded epsilon can be slightly larger than an independently valid radius.
    # Instead, compare the directed reference enclosure against both bounds.
    factor = factor_decimal(base["diagonal"], base["lower"], base["upper"], gamma, state)
    previous = None
    previous_epsilons = [ZERO, ZERO]
    reference_certificates = []
    sums = [[ZERO for _ in range(n)] for _ in REWARDS]
    sum_lows = [[ZERO for _ in range(n)] for _ in REWARDS]
    sum_highs = [[ZERO for _ in range(n)] for _ in REWARDS]
    dense_path = output / (case + "_" + label + "_DECIMAL70.csv")
    max_own_residual = ZERO
    with dense_path.open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("step", "index", "count_Decimal70", "kinetic_Decimal70"))
        for j in range(4):
            vectors = []
            next_epsilons = []
            for c, (reward, _) in enumerate(REWARDS):
                rhs = base["rhs"][c] if j == 0 else [gamma * value for value in previous[c]]
                solution = solve_decimal(factor, rhs, state)
                require(all(value >= 0 for value in solution), "NEGATIVE_REFERENCE_SOLUTION")
                own_residual = reference_residual(base["diagonal"], base["lower"],
                                                   base["upper"], gamma, solution, rhs)
                max_own_residual = max(max_own_residual, own_residual)
                require(own_residual <= D("1e-55"), "DECIMAL_REFERENCE_RESIDUAL")
                ref_eps, eta, ref_low, ref_high = enclose_reference_step(
                    base, gamma, witness, beta, solution, c,
                    None if previous is None else previous[c], previous_epsilons[c])
                compare_vector(state, prefix + ":step" + str(j) + ":" + reward,
                               centers[j, :, c], radii[j, :, c], solution, ref_low, ref_high,
                               epsilon=binary64_decimal(eps[j, c]), h=h)
                sums[c] = [left + right for left, right in zip(sums[c], solution)]
                sum_lows[c] = [DOWN.add(left, right) for left, right in zip(sum_lows[c], ref_low)]
                sum_highs[c] = [UP.add(left, right) for left, right in zip(sum_highs[c], ref_high)]
                reference_certificates.append({"step": j, "reward": reward,
                                               "eta_upper": str(eta), "epsilon_upper": str(ref_eps)})
                next_epsilons.append(ref_eps)
                vectors.append(solution)
            for i in range(n):
                writer.writerow((j, i, str(vectors[0][i]), str(vectors[1][i])))
            previous = vectors
            previous_epsilons = next_epsilons
            check_budget(state)
    for c, (reward, _) in enumerate(REWARDS):
        compare_vector(state, prefix + ":cumulative:" + reward,
                       cumulative[:, c], cumulative_radius[:, c], sums[c], sum_lows[c], sum_highs[c])
    source_rows = metadata["source_rows"]
    require(isinstance(source_rows, list) and len(source_rows) == 3, "THREE_SOURCE_ROWS")
    keyed_rows = {str(row["z"]): row for row in source_rows}
    require(set(keyed_rows) == set(Z_VALUES), "SOURCE_Z_IDENTITY")
    source_results = []
    for z in Z_VALUES:
        values = {}
        for c, (reward, _) in enumerate(REWARDS):
            expected = dot_decimal(base["weights"][z], sums[c])
            ref_lower = ref_upper = ZERO
            for weight, low, high in zip(base["weights"][z], sum_lows[c], sum_highs[c]):
                ref_lower = DOWN.add(ref_lower, DOWN.multiply(weight, low))
                ref_upper = UP.add(ref_upper, UP.multiply(weight, high))
            compare_scalar(state, prefix + ":z" + z + ":" + reward,
                           keyed_rows[z][reward], expected, ref_lower, ref_upper)
            values[reward] = str(expected)
        source_results.append({"z": z, **values})
    state["clock_results"].append({"case": case, "clock_label": label,
                                    "T_s": horizon, "m": 4, "delta": 0.5,
                                    "gamma_hex": gamma_float.hex(), "gamma_exact": str(gamma),
                                    "actual_a": str(a), "reference_sources": source_results,
                                    "reference_witness_beta_lower": str(beta),
                                    "reference_directed_certificates": reference_certificates,
                                    "max_Decimal100_own_scaled_residual": str(max_own_residual),
                                    "reference_file": dense_path.name,
                                    "reference_bytes": dense_path.stat().st_size,
                                    "reference_sha256": sha256(dense_path)})
    check_budget(state)


def execute(args, state):
    root = args.root_dir.resolve()
    plan = load_json(args.plan)
    require(plan["schema"] == "CR_RR_CLOCK_C9_REFERENCE_PLAN_V1", "PLAN_SCHEMA")
    require(plan.get("root_C4_authorized") is True, "ROOT_C4_AUTHORIZATION_REQUIRED")
    require(plan["authorized_run_id"] == args.run_id, "REFERENCE_RUN_ID")
    require(plan["precision_decimal_digits"] == PRECISION, "DECIMAL70_FROZEN")
    require(plan["expected_reference_sha256"] == sha256(__file__), "REFERENCE_CODE_PIN")
    require(plan["expected_rhs_count"] == 32 and plan["expected_factorizations"] == 4,
            "REFERENCE_FOOTPRINT")
    file_pin(root, plan["frozen_contract"], state, "frozen_contract")
    require(isinstance(plan["production_sources"], list) and plan["production_sources"],
            "PRODUCTION_SOURCE_PINS_REQUIRED")
    for index, entry in enumerate(plan["production_sources"]):
        file_pin(root, entry, state, "production_code:" + str(index))
    cases = plan["cases"]
    require(isinstance(cases, list) and len(cases) == 2, "TWO_FINEST_CASES_ONLY")
    require({entry["case"] for entry in cases} == set(BASELINES), "EXACT_REFERENCE_CASE_SET")
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
        os.environ[name] = "1"
    os.environ.update(OMP_DYNAMIC="FALSE", OMP_NESTED="FALSE", OMP_MAX_ACTIVE_LEVELS="1")
    _, hard = resource.getrlimit(resource.RLIMIT_AS)
    memory_limit = MEMORY_BYTES if hard == resource.RLIM_INFINITY else min(hard, MEMORY_BYTES)
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
    state["memory_limit_bytes"] = memory_limit
    import numpy as np
    state["numpy_version"] = np.__version__
    state["affinity"] = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None
    check_budget(state)
    with localcontext() as context:
        context.prec = PRECISION
        for case_record in cases:
            base = read_case(np, root, case_record, state)
            clocks = case_record["clocks"]
            require(isinstance(clocks, list) and len(clocks) == 2
                    and {row["clock_label"] for row in clocks} == {"minus", "plus"},
                    "TWO_OPPOSITE_CLOCKS")
            for clock_record in clocks:
                state["scientific_work_started"] = True
                review_clock(np, root, args.out_dir, case_record, clock_record, base, state)
    require(state["reference_rhs_solved"] == 32, "ACTUAL_REFERENCE_RHS_COUNT")
    require(state["factorizations"] == 4, "ACTUAL_REFERENCE_FACTOR_COUNT")
    require(len(state["vector_comparisons"]) == 40, "ALL_VECTOR_COMPARISONS")
    require(len(state["scalar_comparisons"]) == 24, "ALL_SCALAR_COMPARISONS")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root-dir", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--cpu-limit-s", type=float, required=True)
    args = parser.parse_args()
    require(math.isfinite(args.cpu_limit_s) and 1 <= args.cpu_limit_s <= MAX_CPU_S,
            "BOUNDED_REFERENCE_CPU_LIMIT")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.out_dir / "C9_REFERENCE_RESULT.json"
    require(not result_path.exists() and not any(args.out_dir.glob("*_DECIMAL70.csv")),
            "CREATE_ONLY_REFERENCE_OUTPUTS")
    wall_start = time.monotonic()
    state = {
        "schema": "CR_RR_CLOCK_C9_DECIMAL70_RESULT_V1", "run_id": args.run_id,
        "status": "RUNNING", "decision": "NOT_ADMITTED",
        "utc_start": datetime.now(timezone.utc).isoformat(),
        "precision_decimal_digits": PRECISION,
        "certificate_precision_decimal_digits": CERT_PRECISION,
        "reference_rounding_modes": ["ROUND_FLOOR", "ROUND_CEILING"],
        "baseline": "EXACT_STORED_HEIII_BINARY64_K_AND_SAVED_RHS10_11",
        "source": "exact original3 saved source projections; no re-projection",
        "reference_scope": "2 finest full grids; one horizon per case; 2 clocks; m4; 2 rewards",
        "actual_continuous_source_history": None,
        "scientific_work_started": False, "reference_rhs_solved": 0, "factorizations": 0,
        "input_pins": [], "cases": [], "clock_results": [],
        "vector_comparisons": [], "scalar_comparisons": [], "failures": [],
        "production_imports": 0, "provider_imports": 0, "old_science_replays": 0,
        "new_all_time_solves": 0, "new_provider_evaluations": 0,
        "evidence_type": "Decimal70 solves plus independently directed Decimal100 residual/witness enclosures",
        "formal_floating_certificate_admission": "SEPARATE_C9_CODE_AND_ARITHMETIC_REVIEW",
        "primary_orders_64_256_1024_replayed": False,
        "executed_reference_sha256": sha256(__file__), "plan_sha256": sha256(args.plan),
        "cpu_limit_s": args.cpu_limit_s,
        "cpu_guard_s": args.cpu_limit_s - max(0.3, args.cpu_limit_s * 0.03),
        "process_cpu_accounting": "worker samples process CPU including imports and dense outputs; root dispatcher records whole-child and coordinator costs",
        "N6_N7": "PREDECESSOR_GATED", "caloric_partition_promoted_to_heating": False,
        "central_count_effect": 0, "central_completed": 27, "central_total": 88,
    }
    exit_code = 1
    try:
        execute(args, state)
        state["status"] = "COMPLETED"
        state["decision"] = "PASS_SCOPED_DECIMAL70_QUALIFICATION" if not state["failures"] else "FAIL_SCOPED"
        exit_code = 0 if not state["failures"] else 1
    except Exception as error:
        state["status"] = "ERROR_RETAINED"
        state["decision"] = "NOT_ADMITTED"
        state["error"] = {"type": type(error).__name__, "message": str(error),
                           "traceback": traceback.format_exc()}
    state["process_cpu_s"] = time.process_time()
    state["process_cpu_observation"] = "before final receipt serialization; authoritative whole-child cost is the root dispatcher receipt"
    state["wall_s_since_main"] = time.monotonic() - wall_start
    state["peak_RSS_KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if state["process_cpu_s"] > args.cpu_limit_s:
        state["failures"].append("REFERENCE_CPU_LIMIT_EXCEEDED")
        state["decision"] = "NOT_ADMITTED"
        exit_code = 1
    write_new_json(result_path, state)
    print(json.dumps({"status": state["status"], "decision": state["decision"],
                      "reference_rhs_solved": state["reference_rhs_solved"],
                      "vector_comparisons": len(state["vector_comparisons"]),
                      "scalar_comparisons": len(state["scalar_comparisons"]),
                      "failures": len(state["failures"]),
                      "process_cpu_s": state["process_cpu_s"], "result": str(result_path)}, allow_nan=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
