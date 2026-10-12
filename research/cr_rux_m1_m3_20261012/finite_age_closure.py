"""Finite-age heating diagnostics; no CR generator or time propagator.

Fractions certify arithmetic of the recorded moment model, not its input error.
The positive closure is a one-time functional, not a reconstructed kernel.
"""
from __future__ import annotations

from fractions import Fraction as F


def validate_moments(p: F, r: F, s: F) -> None:
    if not (0 <= s <= r <= p <= 1 and r * r <= p * s):
        raise ValueError("MOMENT_DOMAIN_INVALID: require 0<=S<=R<=p<=1 and R^2<=pS")


def parameters(p: F, r: F, s: F) -> dict:
    validate_moments(p, r, s)
    c1 = (p - 2 * r + s) / 2
    if p == 0:
        return {"status": "ZERO_EARLY_MASS", "source_time_over_T": None,
                "conditional_delay_over_T": None, "conditional_variance_over_T2": None,
                "C_first": F(0), "C_positive": F(0), "coefficient_improvement": F(0)}
    z = r / p
    variance = s / p - z * z
    cp = p * variance / 2
    return {"status": "DEFINED", "source_time_over_T": z,
            "conditional_delay_over_T": 1 - z,
            "conditional_variance_over_T2": variance,
            "C_first": c1, "C_positive": cp,
            "coefficient_improvement": c1 - cp}


def positive_response(p: F, r: F, s: F, history) -> F:
    """Return P/(H0*qstar); history takes dimensionless source time in [0,1]."""
    info = parameters(p, r, s)
    if p == 0:
        return F(0)  # Do not evaluate an irrelevant callback.
    value = F(history(info["source_time_over_T"]))
    if value < 0:
        raise ValueError("NEGATIVE_SOURCE: positivity contract violated")
    return p * value


def first_response(p: F, r: F, s: F, endpoint: F, derivative_x: F) -> F:
    validate_moments(p, r, s)
    return p * endpoint - (p - r) * derivative_x


def closure_budget(c_positive: F, kappa: F, reference_ratio: F, tolerance: F) -> dict:
    """Conditional heating budget only; reference_ratio = H0*qstar/P_ref.

All four arguments are explicitly supplied. No missing-data-to-zero default.
"""
    values = (c_positive, kappa, reference_ratio, tolerance)
    if any(not isinstance(x, F) for x in values):
        raise TypeError("EXPLICIT_EXACT_BUDGET_REQUIRED")
    if min(c_positive, kappa, reference_ratio) < 0 or tolerance <= 0:
        raise ValueError("INVALID_HEATING_BUDGET")
    bound = c_positive * kappa * reference_ratio
    return {"bound_over_reference": bound, "tolerance_over_reference": tolerance,
            "status": "FIXED_KERNEL_HEATING_CLOSURE_SUFFICIENT" if bound <= tolerance
                      else "BOUND_NOT_SUFFICIENT"}
