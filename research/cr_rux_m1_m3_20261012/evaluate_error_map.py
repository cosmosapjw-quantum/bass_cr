"""One create-only postprocess of saved M0 values; old evaluators are not imported."""
from __future__ import annotations

import csv
import hashlib
import json
import time
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path

from finite_age_closure import closure_budget, first_response, parameters, positive_response

BASE = Path(__file__).resolve().parent
CACHE_SHA = "60747f9da89e3596bfeb93a4ec14a1bb58a33bca3a09629fc092f254839f3b7b"


def unpack(x):
    denominator = int(x["denominator"])
    if denominator <= 0:
        raise ValueError("INVALID_EXACT_PACKET")
    return F(int(x["numerator"]), denominator)


def packet(x):
    if x is None:
        return None
    x = F(x)
    with localcontext() as ctx:
        ctx.prec = 60
        decimal = str(Decimal(x.numerator) / Decimal(x.denominator))
    return {"numerator": str(x.numerator), "denominator": str(x.denominator), "decimal60": decimal}


def polynomial(coefficients, x):
    a, b, c = (F(v) for v in coefficients)
    return a + x * (b + c * x)


def main():
    started = time.monotonic()
    out = BASE / "results"
    if out.exists():
        raise FileExistsError("Reuse completed M2 output; do not rerun or overwrite")
    manifest = json.loads((BASE / "inputs/SOURCE_MANIFEST.json").read_text())
    pins = {x["local_path"]: x["sha256"] for x in manifest["sources"]}
    raw = (BASE / "inputs/CACHED_RESPONSE.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != CACHE_SHA:
        raise ValueError("CACHE_IDENTITY_MISMATCH")
    quad_raw = (BASE / "inputs/QUADRATIC_RESPONSE.json").read_bytes()
    if hashlib.sha256(quad_raw).hexdigest() != pins["inputs/QUADRATIC_RESPONSE.json"]:
        raise ValueError("QUADRATIC_RESULT_IDENTITY_MISMATCH")
    source, quadratic = json.loads(raw), json.loads(quad_raw)
    T = unpack(source["T_s"])
    truth = {(r["model"], r["representation"]): r for r in quadratic["rows"]}
    rows, table, budgets = [], [], []
    for row in source["rows"]:
        m = {k: unpack(v) for k, v in row["moments"].items()}
        p, r, s = m["p"], m["R"], m["S"]
        if m["H0"] <= 0 or T <= 0:
            raise ValueError("POSITIVE_NORMALIZATION_REQUIRED")
        info = parameters(p, r, s)
        if info["status"] != "DEFINED":
            raise ValueError("STORED_MODEL_HAS_NO_EARLY_HEAT")
        c1, cp = info["C_first"], info["C_positive"]
        if c1 - cp != (p - r) ** 2 / (2 * p):
            raise ArithmeticError("COEFFICIENT_IDENTITY_FAILED")
        comparisons = {}
        key = (row["model"], row["representation"])
        for name, coefficients in quadratic["polynomials_power_basis"].items():
            a, b, c = (F(v) for v in coefficients)
            exact = unpack(truth[key]["response_over_H0_qstar"][name])
            endpoint, derivative = a + b + c, b + 2 * c
            h1 = first_response(p, r, s, endpoint, derivative)
            hp = positive_response(p, r, s, lambda x: polynomial(coefficients, x))
            kappa = 2 * abs(c)
            # This is a new comparison to a retained exact value, not old evaluation.
            if abs(exact - hp) != cp * kappa or abs(exact - h1) != c1 * kappa:
                raise ArithmeticError("QUADRATIC_BOUND_SATURATION_FAILED")
            if (c > 0 and exact < hp) or (c < 0 and exact > hp):
                raise ArithmeticError("JENSEN_SIGN_FAILED")
            if exact <= 0:
                raise ValueError("RETAINED_REFERENCE_DENOMINATOR_NOT_POSITIVE")
            comparisons[name] = {
                "reference": "retained M0 QUADRATIC_RESPONSE.json, no old evaluator rerun",
                "exact": packet(exact), "instantaneous": packet(endpoint),
                "finite_age_first": packet(h1), "finite_age_positive": packet(hp),
                "kappa": packet(kappa), "positive_abs_error_over_H0_qstar": packet(abs(exact - hp)),
                "positive_abs_error_over_actual_CR_heat": packet(abs(exact - hp) / exact),
                "first_abs_error_over_H0_qstar": packet(abs(exact - h1)),
                "positive_bound": packet(cp * kappa), "first_bound": packet(c1 * kappa),
                "positive_lower_bound_for_convex": c >= 0,
                "quadratic_saturation_exact": True}
            table.append({"model": key[0], "representation": key[1], "source": name,
                          "retained_exact": float(exact), "instantaneous": float(endpoint),
                          "finite_age_first": float(h1), "finite_age_positive": float(hp),
                          "positive_absolute_error_over_H0_qstar": float(abs(exact - hp)),
                          "first_absolute_error_over_H0_qstar": float(abs(exact - h1)),
                          "positive_error_over_actual_CR_heat": float(abs(exact - hp) / exact)})
        counterexample = first_response(p, r, s, F(1), F(3))
        if counterexample >= 0:
            raise ArithmeticError("EXPECTED_CUBIC_SIGN_COUNTEREXAMPLE_ABSENT")
        for kappa in (F(0), F(1, 10), F(1), F(2), F(10)):
            for ratio in (F(1, 100), F(1, 10), F(1)):
                for tolerance in (F(1, 10000), F(1, 1000), F(1, 100)):
                    decision = closure_budget(cp, kappa, ratio, tolerance)
                    budgets.append({"model": key[0], "representation": key[1],
                                    "kappa": packet(kappa), "reference_ratio": packet(ratio),
                                    "bound_over_reference": packet(decision["bound_over_reference"]),
                                    "tolerance_over_reference": packet(tolerance), "status": decision["status"],
                                    "physical_scenario": False})
        rows.append({"model": key[0], "representation": key[1],
                     "parameters": {k: packet(v) if k != "status" else v for k, v in info.items()},
                     "H0_original_normalization": packet(m["H0"]),
                     "conditional_delay_s": packet(T * info["conditional_delay_over_T"]),
                     "source_evaluation_time_s": packet(T * info["source_time_over_T"]),
                     "global_mean_delay_over_T": packet(m["mu_s"] / T),
                     "bound_coefficient_reduction_factor": packet(c1 / cp) if cp else None,
                     "controlled_histories": comparisons,
                     "cubic_first_correction_counterexample": {
                         "source": "x^3 on [0,1], zero prehistory",
                         "first_response": packet(counterexample),
                         "positive_response": packet(positive_response(p, r, s, lambda x: x ** 3)),
                         "actual_response": None, "actual_status": "POSITIVE_BUT_NOT_EVALUATED_REQUIRES_U3",
                         "purpose": "first-order positivity failure only; no cubic true-error claim"}})
    result = {"schema": "cr-finite-age-error-map.v1", "status": "EXACT_RECORDED_MODEL_DIAGNOSTIC",
              "T_s": packet(T), "input_sha256": {"cache": CACHE_SHA, "quadratic": hashlib.sha256(quad_raw).hexdigest()},
              "rows": rows, "conditional_budget_grid": budgets,
              "normalization": "P/(H0*qstar); actual-CR-heat relative errors appear only in explicitly named fields",
              "grid_status": "CONTROLLED_DIAGNOSTIC_NOT_ACTUAL_CONSUMER_BUDGET",
              "claim_ceiling": "Fixed kernel, bath, spectrum and age; no physical input or mesh error certification",
              "counts": {"record_rows": len(rows), "new_closure_comparisons": len(table), "conditional_budget_cases": len(budgets),
                         "new_G": 0, "propagation": 0, "old_evaluator_calls": 0, "NCP_calls": 0},
              "arithmetic_wall_s": time.monotonic() - started}
    out.mkdir()
    (out / "RESPONSE_ERROR_MAP.json").write_text(json.dumps(result, indent=2) + "\n")
    with (out / "RESPONSE_ERROR_MAP.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(table)
    print(json.dumps({"status": result["status"], **result["counts"], "arithmetic_wall_s": result["arithmetic_wall_s"]}))


if __name__ == "__main__":
    main()
