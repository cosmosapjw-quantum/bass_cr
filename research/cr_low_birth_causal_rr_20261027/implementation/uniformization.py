#!/usr/bin/env python3
"""Positive ramp/occupancy uniformization; no computation occurs on import."""
from decimal import Decimal, localcontext
import math

import numpy as np

from model import need


DECIMAL_PRECISION = 80
POISSON_TAIL_DESIGN_TARGET = 1e-30
MAX_POISSON_CUTOFF = 50000


def choose_cutoff(nu, maximum_time):
    """Choose an integer then verify the positive Poisson Chernoff upper bound."""
    need(math.isfinite(nu) and nu >= 0 and math.isfinite(maximum_time)
         and maximum_time > 0, "FINITE_NONNEGATIVE_UNIFORMIZATION_SCALE_REQUIRED")
    x = nu * maximum_time
    if x == 0:
        return 3, {"x_max": 0., "cutoff_M": 3, "chernoff_upper_bound": 0.}
    need(x < MAX_POISSON_CUTOFF - 256, "STIFFNESS_EXCEEDS_FROZEN_LOCAL_TERM_LIMIT")
    cutoff = math.ceil(x + 16 * math.sqrt(x + 1) + 128) + 3
    log_target = math.log(POISSON_TAIL_DESIGN_TARGET)
    while True:
        need(cutoff <= MAX_POISSON_CUTOFF, "POISSON_CUTOFF_EXCEEDS_FROZEN_LIMIT")
        k = cutoff - 2
        log_bound = -x + k * (1 + math.log(x / k))
        if k > x and log_bound <= log_target:
            break
        cutoff += max(16, math.ceil(math.sqrt(x + 1)))
    return cutoff, {"x_max": x, "cutoff_M": cutoff,
                    "tail_threshold_for_Chernoff": cutoff - 2,
                    "chernoff_log_upper_bound": log_bound,
                    "chernoff_upper_bound": math.exp(log_bound),
                    "design_target": POISSON_TAIL_DESIGN_TARGET,
                    "maximum_frozen_cutoff": MAX_POISSON_CUTOFF}


def positive_tail(x, first_index, first_probability):
    """Positive tail summation with a separately recorded geometric remainder.

    The caller supplies a threshold above the Poisson mean. Decimal arithmetic
    reduces cancellation; returned float values are not outward enclosures.
    """
    need(Decimal(first_index) > x, "TAIL_THRESHOLD_MUST_EXCEED_POISSON_MEAN")
    n = first_index
    term = first_probability
    total = term
    remainder = term
    for _ in range(MAX_POISSON_CUTOFF):
        n += 1
        term *= x / Decimal(n)
        total += term
        ratio = x / Decimal(n + 1)
        remainder = term * ratio / (1 - ratio)
        if remainder <= total * Decimal("1e-65"):
            return total, remainder
    raise ArithmeticError("POSITIVE_POISSON_TAIL_DID_NOT_FINISH")


def ramp_occupancy_weights(nu, times, cutoff):
    """Return t²*w_k^M and t³*v_k^M for shared active P powers.

    w uses n<=M and k<=M-2; v uses n<=M and k<=M-3. We pad the
    last occupancy weight with exact zero. No weights are renormalized.
    """
    need(type(cutoff) is int and 3 <= cutoff <= MAX_POISSON_CUTOFF,
         "FINITE_FROZEN_INTEGER_CUTOFF_REQUIRED")
    times = np.asarray(times, dtype=float)
    need(times.ndim == 1 and times.size > 0 and np.all(np.isfinite(times))
         and np.all(times > 0) and np.all(np.diff(times) > 0), "ORDERED_POSITIVE_TIMES_REQUIRED")
    if nu == 0:
        return (times[:, None] ** 2 / 2, times[:, None] ** 3 / 6,
                [{"time_s": float(t), "x": 0., "tail_count_fraction": 0.,
                  "tail_occupancy_fraction": 0., "tail_evaluation": "exact zero operator"}
                 for t in times])
    need(math.isfinite(nu) and nu > 0, "POSITIVE_UNIFORMIZATION_RATE_REQUIRED")
    state_rows, occupancy_rows, diagnostics = [], [], []
    with localcontext() as ctx:
        ctx.prec = DECIMAL_PRECISION
        nd = Decimal.from_float(float(nu))
        for time_value in times:
            td = Decimal.from_float(float(time_value))
            x = nd * td
            need(Decimal(cutoff - 2) > x, "CUTOFF_BELOW_WEIGHT_TAIL_THRESHOLD")
            p = [(-x).exp()]
            for n in range(1, cutoff + 1):
                p.append(p[-1] * x / Decimal(n))
            # Positive backward summation avoids near-one CDF subtraction.
            tail1 = [Decimal(0)] * (cutoff + 2)
            tail2 = [Decimal(0)] * (cutoff + 2)
            tail3 = [Decimal(0)] * (cutoff + 2)
            for j in range(cutoff, -1, -1):
                tail1[j] = tail1[j + 1] + p[j]
                tail2[j] = tail2[j + 1] + tail1[j]
                tail3[j] = tail3[j + 1] + tail2[j]
            w = [tail2[k + 2] / (x * x) for k in range(cutoff - 1)]
            v = [tail3[k + 3] / (x * x * x) for k in range(cutoff - 2)] + [Decimal(0)]
            tc, rc = positive_tail(x, cutoff - 1, p[cutoff - 1])
            to, ro = positive_tail(x, cutoff - 2, p[cutoff - 2])
            mass_w = sum(w, Decimal(0))
            mass_v = sum(v, Decimal(0))
            defect_w = mass_w - (1 - tc) / 2
            defect_v = mass_v - (1 - to) / 6
            need(abs(defect_w) < Decimal("1e-60")
                 and abs(defect_v) < Decimal("1e-60"), "DECIMAL_WEIGHT_IDENTITIES_FAILED")
            state_rows.append([float(td * td * value) for value in w])
            occupancy_rows.append([float(td * td * td * value) for value in v])
            diagnostics.append({
                "time_s": float(time_value), "x": float(x), "x_decimal": str(x),
                "cutoff_M": cutoff, "maximum_P_power": cutoff - 2,
                "decimal_precision": DECIMAL_PRECISION,
                "tail_count_fraction": float(tc + rc),
                "tail_occupancy_fraction": float(to + ro),
                "tail_count_fraction_decimal": str(tc + rc),
                "tail_occupancy_fraction_decimal": str(to + ro),
                "poisson_tail_subtotal_count_decimal": str(tc),
                "poisson_tail_subtotal_occupancy_decimal": str(to),
                "omitted_tail_summation_remainder_count": str(rc),
                "omitted_tail_summation_remainder_occupancy": str(ro),
                "decimal_weight_mass_residual_phi2": str(defect_w),
                "decimal_weight_mass_residual_phi3": str(defect_v),
                "weights_renormalized": False,
                "tail_evaluation": "exact-arithmetic bound evaluated with Decimal80 then ordinary float; not outward enclosure",
            })
    weights_n = np.asarray(state_rows, dtype=np.float64)
    weights_o = np.asarray(occupancy_rows, dtype=np.float64)
    need(np.all(np.isfinite(weights_n)) and np.all(weights_n >= 0)
         and np.all(np.isfinite(weights_o)) and np.all(weights_o >= 0),
         "FINITE_POSITIVE_WEIGHTS_REQUIRED")
    return weights_n, weights_o, diagnostics


def validate_chain(amplitude, drift, lambda_h, lambda_he):
    arrays = [np.asarray(x, dtype=np.float64) for x in (amplitude, drift, lambda_h, lambda_he)]
    shape = arrays[0].shape
    need(len(shape) == 1 and shape[0] > 0 and all(a.shape == shape for a in arrays),
         "MATCHING_NONEMPTY_CHAIN_ARRAYS_REQUIRED")
    need(all(np.all(np.isfinite(a)) and np.all(a >= 0) for a in arrays),
         "NONNEGATIVE_FINITE_CHAIN_REQUIRED")
    return arrays


def uniformization_rate(drift, lambda_h, lambda_he):
    drift, lambda_h, lambda_he = [np.asarray(x, dtype=np.float64)
                                 for x in (drift, lambda_h, lambda_he)]
    exits = (drift + lambda_h) + lambda_he
    largest = float(np.max(exits))
    return 0. if largest == 0 else float(np.nextafter(largest, math.inf))


def propagate(amplitude, drift, lambda_h, lambda_he, times, nu, weights_n, weights_o):
    amplitude, drift, lambda_h, lambda_he = validate_chain(amplitude, drift, lambda_h, lambda_he)
    times = np.asarray(times, dtype=np.float64)
    if nu == 0:
        need(np.all(drift == 0) and np.all(lambda_h == 0) and np.all(lambda_he == 0),
             "ZERO_NU_REQUIRES_ZERO_GENERATOR")
        return np.outer(times ** 2 / 2, amplitude), np.outer(times ** 3 / 6, amplitude), {
            "P_applications": 0, "summation": "exact zero-generator polynomial"}
    need(math.isfinite(nu) and nu > 0, "POSITIVE_UNIFORMIZATION_RATE_REQUIRED")
    exits = (drift + lambda_h) + lambda_he
    diagonal = 1. - exits / nu
    down = drift[1:] / nu
    need(np.all(diagonal >= 0) and np.all(diagonal <= 1), "NONNEGATIVE_SUBSTOCHASTIC_P_REQUIRED")
    need(weights_n.shape == weights_o.shape and weights_n.shape[0] == len(times),
         "MATCHING_STATE_OCCUPANCY_WEIGHTS_REQUIRED")
    need(np.all(np.isfinite(weights_n)) and np.all(weights_n >= 0)
         and np.all(np.isfinite(weights_o)) and np.all(weights_o >= 0),
         "INVALID_PROPAGATION_WEIGHTS")
    state = np.zeros((len(times), len(amplitude)), dtype=np.float64)
    occupied = np.zeros_like(state)
    comp_n, comp_o = np.zeros_like(state), np.zeros_like(state)
    power = amplitude.copy()
    for k in range(weights_n.shape[1]):
        term_n = weights_n[:, k, None] * power[None, :] - comp_n
        next_n = state + term_n
        comp_n = (next_n - state) - term_n
        state = next_n
        term_o = weights_o[:, k, None] * power[None, :] - comp_o
        next_o = occupied + term_o
        comp_o = (next_o - occupied) - term_o
        occupied = next_o
        if k + 1 < weights_n.shape[1]:
            successor = diagonal * power
            successor[:-1] += down * power[1:]
            power = successor
    need(np.all(np.isfinite(state)) and np.all(state >= 0)
         and np.all(np.isfinite(occupied)) and np.all(occupied >= 0),
         "POSITIVE_FINITE_RESPONSE_REQUIRED")
    return state, occupied, {
        "P_applications": weights_n.shape[1] - 1,
        "shared_prefixes": len(times), "active_states": len(amplitude),
        "summation": "componentwise compensated binary64; positive terms",
        "P_diagonal_min": float(np.min(diagonal)),
        "P_diagonal_max": float(np.max(diagonal)),
        "P_column_sum_roundoff_diagnostic_max": float(np.max(np.abs(
            diagonal + drift / nu + lambda_h / nu + lambda_he / nu - 1.))),
        "renormalized": False, "clipped_negative_values": False,
    }
