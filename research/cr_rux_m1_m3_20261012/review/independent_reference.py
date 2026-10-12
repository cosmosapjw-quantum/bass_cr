"""One independent exact reference: direct atomic measures + retained packets.

Independent reviewer: /root/independent_review.  Only the new closure module is
loaded as the subject under test.  No old evaluator or test suite is imported.
The reference uses direct delay-atom sums and separate closed-form arithmetic.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path


HERE = Path(__file__).resolve().parent
UNIT = HERE.parent
CHECKS: list[dict] = []


def check(name: str, condition: bool, **detail) -> None:
    if not condition:
        raise AssertionError(name)
    CHECKS.append({"id": name, "status": "PASS", **detail})


def rat(packet: dict) -> Q:
    numerator = int(packet["numerator"])
    denominator = int(packet["denominator"])
    if denominator <= 0:
        raise ValueError("NONPOSITIVE_PACKET_DENOMINATOR")
    return Q(numerator, denominator)


def eq(name: str, actual, expected) -> None:
    check(name, actual == expected)


def rejects(name: str, error_type, callback) -> None:
    try:
        callback()
    except error_type:
        check(name, True)
    else:
        raise AssertionError(name + ": not rejected")


def polynomial(coefficients: tuple[Q, ...], x: Q) -> Q:
    return sum((coefficient * x ** degree
                for degree, coefficient in enumerate(coefficients)), Q(0))


def direct_measure_check(subject, label: str, atoms, age: Q, coefficients):
    """Atoms are (delay in seconds, probability), including explicit late mass."""
    eq(label + "/total_mass", sum((weight for _, weight in atoms), Q(0)), Q(1))
    inside = [(delay, weight) for delay, weight in atoms if Q(0) <= delay <= age]
    mass = sum((weight for _, weight in inside), Q(0))
    if not mass:
        raise AssertionError("Use separate zero-mass check")
    mean_delay = sum((delay * weight for delay, weight in inside), Q(0)) / mass
    r = sum((weight * (age - delay) / age for delay, weight in inside), Q(0))
    s = sum((weight * ((age - delay) / age) ** 2 for delay, weight in inside), Q(0))
    central_second = sum((weight * ((delay - mean_delay) / age) ** 2
                          for delay, weight in inside), Q(0))
    end_second = sum((weight * (delay / age) ** 2 for delay, weight in inside), Q(0))
    parameters = subject.parameters(mass, r, s)
    eq(label + "/conditional_time", parameters["source_time_over_T"], (age - mean_delay) / age)
    eq(label + "/variance", parameters["conditional_variance_over_T2"], central_second / mass)
    eq(label + "/positive_coefficient", parameters["C_positive"], central_second / 2)
    eq(label + "/first_coefficient", parameters["C_first"], end_second / 2)
    eq(label + "/coefficient_improvement", parameters["coefficient_improvement"], mass * (mean_delay / age) ** 2 / 2)
    for name, coefficients in coefficients.items():
        q = lambda x, coefficients=coefficients: polynomial(coefficients, x)
        direct = sum((weight * q((age - delay) / age) for delay, weight in inside), Q(0))
        compressed = mass * q((age - mean_delay) / age)
        endpoint_derivative = sum((degree * coefficient
                                   for degree, coefficient in enumerate(coefficients)), Q(0))
        tangent_direct = sum((weight * (q(Q(1)) - (delay / age) * endpoint_derivative)
                              for delay, weight in inside), Q(0))
        positive = subject.positive_response(mass, r, s, q)
        first = subject.first_response(mass, r, s, q(Q(1)), endpoint_derivative)
        eq(label + "/" + name + "/positive", positive, compressed)
        eq(label + "/" + name + "/first", first, tangent_direct)
        curvature = sum((degree * (degree - 1) * abs(coefficient)
                         for degree, coefficient in enumerate(coefficients) if degree >= 2), Q(0))
        check(label + "/" + name + "/bound_positive", abs(direct - positive) <= curvature * central_second / 2)
        check(label + "/" + name + "/bound_first", abs(direct - first) <= curvature * end_second / 2)
        if len(coefficients) <= 3:
            eq(label + "/" + name + "/sharp_positive", abs(direct - positive), curvature * central_second / 2)
            eq(label + "/" + name + "/sharp_first", abs(direct - first), curvature * end_second / 2)
        check(label + "/" + name + "/nonnegative", positive >= 0)
        if name == "shutoff":
            eq(label + "/shutoff/current_source", q(Q(1)), Q(0))
            check(label + "/shutoff/nonzero_delayed_heat", direct > 0 and positive > 0)
    return mass, r, s


def main() -> None:
    contract = json.loads((HERE / "REFERENCE_CONTRACT.json").read_text())
    for relative, expected in contract["fixed_sources_sha256"].items():
        actual = hashlib.sha256((UNIT / relative).read_bytes()).hexdigest()
        eq("source_identity/" + relative, actual, expected)
    spec = importlib.util.spec_from_file_location("independent_subject_finite_age", UNIT / "finite_age_closure.py")
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)

    # Separate dimensional toy: both endpoints, asymmetric interior atoms, late mass.
    age = Q(12, 5)
    atoms = [(Q(0), Q(1, 7)), (age / 4, Q(2, 7)),
             (3 * age / 4, Q(1, 7)), (age, Q(1, 7)), (7 * age / 5, Q(2, 7))]
    histories = {
        "constant": (Q(4, 3),), "affine": (Q(2), Q(3)),
        "shutoff": (Q(1), Q(-2), Q(1)), "concave": (Q(1), Q(2), Q(-1)),
        "cubic": (Q(0), Q(0), Q(0), Q(1)),
        "quartic_shutoff": (Q(1), Q(-4), Q(6), Q(-4), Q(1))}
    p, r, s = direct_measure_check(subject, "atomic_measure", atoms, age, histories)

    def forbidden(_):
        raise AssertionError("ZERO_MASS_CALLED_HISTORY")
    eq("degenerate/no_early_mass", subject.positive_response(Q(0), Q(0), Q(0), forbidden), Q(0))
    eq("degenerate/no_early_status", subject.parameters(Q(0), Q(0), Q(0))["status"], "ZERO_EARLY_MASS")
    q0 = lambda x: Q(9, 4) + x ** 5
    eq("degenerate/source_initial_endpoint", subject.positive_response(Q(3, 8), Q(0), Q(0), q0), Q(27, 32))
    direct_measure_check(subject, "one_delay", [(2 * age / 3, Q(1, 6)), (2 * age, Q(5, 6))], age,
                         {"quintic": (Q(2), Q(-1), Q(0), Q(0), Q(0), Q(1))})
    eq("degenerate/instantaneous", subject.positive_response(Q(1), Q(1), Q(1), q0), q0(Q(1)))
    eq("source_off/zero_history_positive_qstar", subject.positive_response(p, r, s, lambda _: Q(0)), Q(0))
    eq("source_off/zero_history_first", subject.first_response(p, r, s, Q(0), Q(0)), Q(0))
    rejects("invalid/negative_measure", ValueError, lambda: subject.parameters(Q(-1, 2), Q(0), Q(0)))
    rejects("invalid/negative_variance", ValueError, lambda: subject.parameters(Q(1), Q(3, 4), Q(1, 3)))
    rejects("invalid/negative_source", ValueError, lambda: subject.positive_response(p, r, s, lambda _: Q(-1)))

    # Equal p,R,S do not determine a cubic response: two explicit probability laws.
    measure_a = [(Q(1, 4), Q(1, 2)), (Q(3, 4), Q(1, 2))]
    measure_b = [(Q(0), Q(1, 5)), (Q(5, 8), Q(4, 5))]
    for degree in (0, 1, 2):
        eq("nonunique/moment_" + str(degree), sum(w * x ** degree for x, w in measure_a),
           sum(w * x ** degree for x, w in measure_b))
    cubic_a = sum(w * x ** 3 for x, w in measure_a)
    cubic_b = sum(w * x ** 3 for x, w in measure_b)
    check("nonunique/cubic_differs", cubic_a != cubic_b)

    # Budget boundary, nonzero normalization on a zero history, typed missing data.
    coefficient = sum((weight * ((delay - Q(1) * age * (1-r/p)) / age) ** 2
                       for delay, weight in atoms if delay <= age), Q(0)) / 2
    curvature, ratio = Q(3, 2), Q(7, 5)
    threshold = coefficient * curvature * ratio
    eq("budget/equality_sufficient", subject.closure_budget(coefficient, curvature, ratio, threshold)["status"],
       "FIXED_KERNEL_HEATING_CLOSURE_SUFFICIENT")
    eq("budget/strict_failure", subject.closure_budget(coefficient, curvature, ratio, threshold / 2)["status"], "BOUND_NOT_SUFFICIENT")
    eq("budget/source_off_curvature_zero", subject.closure_budget(coefficient, Q(0), ratio, Q(1, 10**8))["bound_over_reference"], Q(0))
    rejects("budget/missing_not_zero", TypeError, lambda: subject.closure_budget(coefficient, None, Q(0), Q(1)))
    rejects("budget/float_not_exact", TypeError, lambda: subject.closure_budget(coefficient, Q(1), 0.1, Q(1)))
    rejects("budget/no_reference_tolerance", ValueError, lambda: subject.closure_budget(coefficient, Q(1), ratio, Q(0)))
    rejects("budget/negative_reference_ratio", ValueError, lambda: subject.closure_budget(coefficient, Q(1), Q(-1), Q(1)))

    cached = json.loads((UNIT / "inputs/CACHED_RESPONSE.json").read_text())
    quadratic = json.loads((UNIT / "inputs/QUADRATIC_RESPONSE.json").read_text())
    new = json.loads((UNIT / "results/RESPONSE_ERROR_MAP.json").read_text())
    by_key = lambda data: {(row["model"], row["representation"]): row for row in data["rows"]}
    cache_rows, old_rows, new_rows = map(by_key, (cached, quadratic, new))
    eq("retained/key_identity", set(cache_rows), set(old_rows))
    eq("new/key_identity", set(cache_rows), set(new_rows))
    eq("new/unique_rows", len(new_rows), len(new["rows"]))
    eq("new/age_identity", rat(new["T_s"]), rat(cached["T_s"]))
    packet_comparisons = 0
    for key, source_row in cache_rows.items():
        m = {name: rat(value) for name, value in source_row["moments"].items()}
        p, r, s = m["p"], m["R"], m["S"]
        cp = (p * s - r * r) / (2 * p)
        c1 = (p - 2 * r + s) / 2
        prefix = "saved/" + "/".join(key)
        row = new_rows[key]
        pars = row["parameters"]
        expected_parameters = {
            "source_time_over_T": r / p, "conditional_delay_over_T": (p - r) / p,
            "conditional_variance_over_T2": (p * s - r * r) / (p * p),
            "C_positive": cp, "C_first": c1, "coefficient_improvement": (p - r) ** 2 / (2 * p)}
        for name, expected in expected_parameters.items():
            eq(prefix + "/" + name, rat(pars[name]), expected)
        eq(prefix + "/yield_normalization", rat(row["H0_original_normalization"]), m["H0"])
        eq(prefix + "/source_time_seconds", rat(row["source_evaluation_time_s"]), rat(cached["T_s"]) * r / p)
        eq(prefix + "/delay_seconds", rat(row["conditional_delay_s"]), rat(cached["T_s"]) * (p-r) / p)
        eq(prefix + "/global_delay_ratio", rat(row["global_mean_delay_over_T"]), m["mu_s"] / rat(cached["T_s"]))
        eq(prefix + "/reduction", rat(row["bound_coefficient_reduction_factor"]), c1 / cp)
        for name, coefficients in quadratic["polynomials_power_basis"].items():
            a, b, c = map(Q, coefficients)
            retained = rat(old_rows[key]["response_over_H0_qstar"][name])
            hp = a * p + b * r + c * r * r / p
            h1 = (a + b + c) * p - (b + 2 * c) * (p-r)
            profile = row["controlled_histories"][name]
            expected_values = {
                "exact": retained, "instantaneous": a + b + c,
                "finite_age_positive": hp, "finite_age_first": h1,
                "kappa": 2 * abs(c), "positive_abs_error_over_H0_qstar": abs(retained-hp),
                "first_abs_error_over_H0_qstar": abs(retained-h1),
                "positive_abs_error_over_actual_CR_heat": abs(retained-hp) / retained,
                "positive_bound": 2 * abs(c) * cp, "first_bound": 2 * abs(c) * c1}
            for field, expected in expected_values.items():
                eq(prefix + "/" + name + "/" + field, rat(profile[field]), expected)
            eq(prefix + "/" + name + "/positive_bound_sharp", abs(retained-hp), 2 * abs(c) * cp)
            eq(prefix + "/" + name + "/first_bound_sharp", abs(retained-h1), 2 * abs(c) * c1)
            check(prefix + "/" + name + "/jensen", (c >= 0 and retained >= hp) or (c < 0 and retained <= hp))
            packet_comparisons += 1
        counterexample = row["cubic_first_correction_counterexample"]
        eq(prefix + "/cubic_first_value", rat(counterexample["first_response"]), 3*r - 2*p)
        check(prefix + "/cubic_first_negative", rat(counterexample["first_response"]) < 0)
        eq(prefix + "/cubic_true_response_uncomputed", counterexample["actual_response"], None)
    for index, budget in enumerate(new["conditional_budget_grid"]):
        key = budget["model"], budget["representation"]
        m = {name: rat(value) for name, value in cache_rows[key]["moments"].items()}
        coefficient = (m["p"]*m["S"]-m["R"]**2)/(2*m["p"])
        expected = coefficient * rat(budget["kappa"]) * rat(budget["reference_ratio"])
        eq("budget_packet/" + str(index) + "/value", rat(budget["bound_over_reference"]), expected)
        expected_status = "FIXED_KERNEL_HEATING_CLOSURE_SUFFICIENT" if expected <= rat(budget["tolerance_over_reference"]) else "BOUND_NOT_SUFFICIENT"
        eq("budget_packet/" + str(index) + "/status", budget["status"], expected_status)
        eq("budget_packet/" + str(index) + "/scope", budget["physical_scenario"], False)
    eq("new/comparison_count", packet_comparisons, new["counts"]["new_closure_comparisons"])
    eq("new/budget_count", len(new["conditional_budget_grid"]), new["counts"]["conditional_budget_cases"])
    for name in ("new_G", "propagation", "old_evaluator_calls", "NCP_calls"):
        eq("new/zero_disallowed_" + name, new["counts"][name], 0)

    output = {
        "status": "PASS_BOUNDED_INDEPENDENT_REFERENCE", "reviewer": "/root/independent_review",
        "reference_invocations": 1, "check_count": len(CHECKS), "checks": CHECKS,
        "saved_record_rows": len(new_rows), "saved_new_closure_comparisons": packet_comparisons,
        "conditional_budget_cases": len(new["conditional_budget_grid"]),
        "nonunique_cubic_example": {"measure_a": str(cubic_a), "measure_b": str(cubic_b)},
        "imports": {"subject_under_test": "finite_age_closure.py", "old_evaluators": [], "owner_tests": []},
        "scope": "Exact recorded-input arithmetic, direct discrete-measure closure bounds, degenerate and reference-budget handling",
        "not_certified": ["numerical or physical input error", "actual kernel uniqueness", "evolving bath", "EoR observables", "production", "F/H promotion", "NCP scaling"]}
    with (HERE / "INDEPENDENT_REFERENCE_RESULT.json").open("x") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")
    print(json.dumps({key: output[key] for key in ("status", "reference_invocations", "check_count", "saved_record_rows", "saved_new_closure_comparisons", "conditional_budget_cases")}, sort_keys=True))


if __name__ == "__main__":
    main()
