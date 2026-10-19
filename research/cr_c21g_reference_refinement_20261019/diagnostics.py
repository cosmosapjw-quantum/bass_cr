"""Independent C21G endpoint diagnostics; no solver imports or accuracy promotion.

Differences always mean left minus right. All photon and energy inventories
are per total H nucleus. Frozen-fixture ownership is checked by the caller;
this module checks the numerical domain and recomputes physical inventories.
"""
from __future__ import annotations

import math
from numbers import Real

BIND_EV = (13.598434599702, 24.587389011, 54.41776)
KB_EV = 1.380649e-16 / 1.602176634e-12
GAS_NAMES = ("x_HII", "y_HeII", "z_HeIII", "thermal_eV_H")


class DiagnosticInputError(ValueError):
    """Malformed or out-of-domain input; never replaced with a floor."""


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise DiagnosticInputError(name + ": expected a real number")
    value = float(value)
    if not math.isfinite(value):
        raise DiagnosticInputError(name + ": nonfinite")
    return value


def _vector(value, length, name):
    if not isinstance(value, (list, tuple)) or len(value) != length:
        raise DiagnosticInputError(name + ": wrong vector shape")
    return [_number(x, name) for x in value]


def _gas(value, Y, name):
    g = _vector(value, 4, name)
    x, y, z, w = g
    if not (0 <= x <= 1 and y >= 0 and z >= 0 and y + z <= 1 and w > 0):
        raise DiagnosticInputError(name + ": physical gas domain")
    if Y == 0 and (y != 0 or z != 0):
        raise DiagnosticInputError(name + ": nonzero absent-helium fraction")
    return g


def _fixture(f):
    if not isinstance(f, dict):
        raise DiagnosticInputError("fixture: expected object")
    try:
        s = {k: _number(f[k], "fixture." + k)
             for k in ("x0", "dx", "nh0", "Y", "opacity_scale")}
        if not (0 < s["dx"] <= .1 and s["nh0"] > 0 and s["Y"] >= 0
                and s["opacity_scale"] >= 0):
            raise DiagnosticInputError("fixture: scalar domain")
        s["end"] = s["x0"] + s["dx"]
        if not (-math.log(21) <= s["x0"] < s["end"] <= math.log(.2)):
            raise DiagnosticInputError("fixture: frozen epoch domain")
        s["gas0"] = _gas(f["gas0"], s["Y"], "fixture.gas0")
        if not isinstance(f["q"], (list, tuple)) or not 1 <= len(f["q"]) <= 4096:
            raise DiagnosticInputError("fixture.q: packet count")
        count = len(f["q"])
        for k in ("q", "birth", "amounts"):
            s[k] = _vector(f[k], count, "fixture." + k)
        if any(q <= 0 for q in s["q"]) or any(a < 0 for a in s["amounts"]):
            raise DiagnosticInputError("fixture: packet domain")
        if any(not s["x0"] <= b <= s["end"] for b in s["birth"]):
            raise DiagnosticInputError("fixture: birth outside interval")
        if not isinstance(f.get("source_identity"), str) or not f["source_identity"]:
            raise DiagnosticInputError("fixture: missing source identity")
    except KeyError as exc:
        raise DiagnosticInputError("fixture: missing " + str(exc)) from exc
    return s


def _endpoint(f, result):
    if not isinstance(result, dict):
        raise DiagnosticInputError("endpoint: expected object")
    try:
        g = _gas(result["gas"], f["Y"], "endpoint.gas")
        n = _vector(result["photons"], len(f["q"]), "endpoint.photons")
    except KeyError as exc:
        raise DiagnosticInputError("endpoint: missing " + str(exc)) from exc
    if any(v < 0 for v in n):
        raise DiagnosticInputError("endpoint: negative photon count")
    if any(a == 0 and v != 0 for a, v in zip(f["amounts"], n)):
        raise DiagnosticInputError("endpoint: populated structural zero")
    return g, n


def _particle_factor(g, Y):
    return math.fsum((1., Y, g[0], Y * g[1], 2 * Y * g[2]))


def _temperature(g, Y):
    return g[3] / (1.5 * KB_EV * _particle_factor(g, Y))


def _photon_logs(f, result, counts):
    count = len(counts)
    tau = None
    if "optical_depth" in result:
        tau = _vector(result["optical_depth"], count, "optical_depth")
        if any(v < 0 for v in tau):
            raise DiagnosticInputError("endpoint: negative accepted optical depth")
    supplied = result.get("log_survivor")
    if supplied is not None:
        if not isinstance(supplied, (list, tuple)) or len(supplied) != count:
            raise DiagnosticInputError("log_survivor: wrong vector shape")
        supplied = [None if v is None else _number(v, "log_survivor") for v in supplied]
    rows = []
    for i, (a, n) in enumerate(zip(f["amounts"], counts)):
        if a == 0:
            if supplied is not None and supplied[i] is not None:
                raise DiagnosticInputError("structural zero has a finite log survivor")
            rows.append({"log": None, "origin": "STRUCTURAL_ZERO", "underflow": False})
            continue
        if tau is not None:
            logn, origin = math.log(a) - tau[i], "FROZEN_AMOUNT_AND_OPTICAL_DEPTH"
        elif supplied is not None and supplied[i] is not None:
            logn, origin = supplied[i], "RECORDED_LOG_SURVIVOR"
        elif n > 0:
            logn, origin = math.log(n), "POSITIVE_RECORDED_COUNT"
        else:
            rows.append({"log": None, "origin": "ZERO_POSITIVE_WEIGHT_LOG_UNAVAILABLE", "underflow": None})
            continue
        try:
            reconstructed = math.exp(logn)
        except OverflowError as exc:
            raise DiagnosticInputError("log survivor overflows") from exc
        rows.append({"log": logn, "origin": origin,
                     "underflow": n == 0 and reconstructed == 0,
                     "reconstructed_count_H": reconstructed,
                     "recorded_minus_reconstructed_H": n - reconstructed,
                     "supplied_log_minus_recomputed": None if supplied is None or supplied[i] is None
                     else supplied[i] - logn})
    return tau, rows


def compare_endpoints(fixture_dict, left_result, right_result):
    """Signed endpoint differences, exact-EOS identity, count and log diagnostics.

    Optical coordinates retain survivor log differences after IEEE underflow.
    A zero count without a finite log is explicitly unavailable, not certified
    underflow. Values here are comparisons, never global accuracy bounds.
    """
    f = _fixture(fixture_dict)
    gl, nl = _endpoint(f, left_result)
    gr, nr = _endpoint(f, right_result)
    delta = [a - b for a, b in zip(gl, gr)]
    normalized = delta[:3] + [delta[3] / f["gas0"][3]]
    maximum = max(map(abs, normalized))
    Dl, Dr = _particle_factor(gl, f["Y"]), _particle_factor(gr, f["Y"])
    dD = math.fsum((delta[0], f["Y"] * delta[1], 2 * f["Y"] * delta[2]))
    stable_T = math.fsum((delta[3], -gr[3] * (dD / Dr))) / (1.5 * KB_EV * Dl)
    tl, logs_l = _photon_logs(f, left_result, nl)
    tr, logs_r = _photon_logs(f, right_result, nr)
    rows = []
    for i, (a, nleft, nright, ll, lr) in enumerate(zip(f["amounts"], nl, nr, logs_l, logs_r)):
        stable, dlog = None, None
        if a == 0:
            stable = 0.
        elif ll["log"] is not None and lr["log"] is not None:
            # Common A cancels before subtracting tau. Avoid subtracting two
            # rounded log(A)-tau values when both optical depths are available.
            dlog = tr[i] - tl[i] if tl is not None and tr is not None else ll["log"] - lr["log"]
            largest_log = math.log(a) - min(tl[i], tr[i]) if tl is not None and tr is not None else max(ll["log"], lr["log"])
            stable = math.copysign(math.exp(largest_log) * (-math.expm1(-abs(dlog))), dlog)
        rows.append({"cohort": i, "amount_H": a, "structural_zero": a == 0,
                     "left_count_H": nleft, "right_count_H": nright,
                     "count_delta_H": nleft - nright, "stable_count_delta_H": stable,
                     "log_survivor_delta": dlog, "left_log": ll, "right_log": lr})
    available = [r["log_survivor_delta"] for r in rows if r["log_survivor_delta"] is not None]
    stable_values = [r["stable_count_delta_H"] for r in rows if r["stable_count_delta_H"] is not None]
    return {"schema": "C21G_ENDPOINT_COMPARISON_V1", "orientation": "left_minus_right",
            "interpretation": "ENDPOINT_DIFFERENCES_NOT_ACCURACY_BOUNDS", "global_error_bound": None,
            "gas_signed": dict(zip(GAS_NAMES, delta)), "gas_normalized_signed": dict(zip(GAS_NAMES, normalized)),
            "gas_normalized_max": maximum,
            "active_gas_components": [name for name, v in zip(GAS_NAMES, normalized) if abs(v) == maximum],
            "temperature": {"left_K": _temperature(gl, f["Y"]), "right_K": _temperature(gr, f["Y"]),
                            "direct_delta_K": _temperature(gl, f["Y"]) - _temperature(gr, f["Y"]),
                            "stable_identity_delta_K": stable_T, "particle_factor_delta": dD},
            "photons": {"cohorts": rows, "count_total_delta_H": math.fsum(nl) - math.fsum(nr),
                        "max_absolute_count_delta_H": max(abs(a - b) for a, b in zip(nl, nr)),
                        "max_absolute_stable_count_delta_H": max(map(abs, stable_values), default=None),
                        "max_absolute_log_delta": max(map(abs, available), default=None),
                        "log_comparable_positive_weight_cohorts": len(available),
                        "positive_weight_log_unavailable_pairs": sum(a > 0 and r["log_survivor_delta"] is None for a, r in zip(f["amounts"], rows)),
                        "left_underflowed_positive_cohorts": sum(r["underflow"] is True for r in logs_l),
                        "right_underflowed_positive_cohorts": sum(r["underflow"] is True for r in logs_r),
                        "left_zero_count_unknown_log_cohorts": sum(r["underflow"] is None for r in logs_l),
                        "right_zero_count_unknown_log_cohorts": sum(r["underflow"] is None for r in logs_r)}}


def recompute_balances(fixture_dict, result):
    """Recompute endpoint stocks and ledger closure without importing totals()."""
    f = _fixture(fixture_dict)
    g, n = _endpoint(f, result)
    try:
        raw = result["ledgers"]
        led = {k: _vector(raw[k], 3, "ledgers." + k) for k in ("photo", "ci", "rr")}
        for k in ("dr", "escape", "cmb", "photon_work", "gas_work", "source_n", "source_u", "heat"):
            led[k] = _number(raw[k], "ledgers." + k)
    except (KeyError, TypeError) as exc:
        raise DiagnosticInputError("missing or malformed ledgers") from exc
    if any(v < 0 for k in ("photo", "ci", "rr") for v in led[k]):
        raise DiagnosticInputError("negative cumulative event ledger")
    if any(led[k] < 0 for k in ("dr", "escape", "photon_work", "gas_work", "source_n", "source_u", "heat")):
        raise DiagnosticInputError("negative nonnegative cumulative ledger")
    if f["Y"] == 0 and (led["dr"] != 0 or any(v != 0 for k in ("photo", "ci", "rr") for v in led[k][1:])):
        raise DiagnosticInputError("helium events with absent helium")
    n0 = [a if b == f["x0"] else 0. for a, b in zip(f["amounts"], f["birth"])]
    u0 = math.fsum(a * q * math.exp(-f["x0"]) for a, q in zip(n0, f["q"]))
    u1 = math.fsum(a * q * math.exp(-f["end"]) for a, q in zip(n, f["q"]))
    dg = [a - b for a, b in zip(g, f["gas0"])]
    net = [math.fsum((led["photo"][j], led["ci"][j], -led["rr"][j], -led["dr"] if j == 1 else 0.)) for j in range(3)]
    stocks = [dg[0], f["Y"] * dg[1], f["Y"] * dg[2]]
    expected = [net[0], net[1] - net[2], net[2]]
    defects = [a - b for a, b in zip(stocks, expected)]
    fractions = [defects[0]] + ([defects[1] / f["Y"], defects[2] / f["Y"]] if f["Y"] else [0., 0.])
    binding = math.fsum((BIND_EV[0] * dg[0], f["Y"] * BIND_EV[1] * dg[1], f["Y"] * (BIND_EV[1] + BIND_EV[2]) * dg[2]))
    energy_terms = {"photon_change": u1 - u0, "thermal_change": dg[3], "binding_change": binding,
                    "escape": led["escape"], "minus_cmb": -led["cmb"], "photon_work": led["photon_work"],
                    "gas_work": led["gas_work"], "minus_source": -led["source_u"]}
    computed = {"number_defect_H": math.fsum((*n0, led["source_n"], *(-v for v in n), *(-v for v in led["photo"]))),
                "energy_defect_eV_H": math.fsum(energy_terms.values()), "species_defect": fractions,
                "photon_number": math.fsum(n), "photon_energy_eV_H": u1, "temperature_K": _temperature(g, f["Y"])}
    agreement = {}
    for k, value in computed.items():
        if k not in result:
            agreement[k] = {"status": "NOT_REPORTED"}
            continue
        reported = _vector(result[k], 3, k) if isinstance(value, list) else _number(result[k], k)
        difference = [a - b for a, b in zip(value, reported)] if isinstance(value, list) else value - reported
        agreement[k] = {"computed_minus_reported": difference, "exact_binary64_equality": value == reported}
    source_n = math.fsum(a for a, b in zip(f["amounts"], f["birth"]) if b > f["x0"])
    source_u = math.fsum(a * q * math.exp(-b) for a, q, b in zip(f["amounts"], f["q"], f["birth"]) if b > f["x0"])
    return {"schema": "C21G_INDEPENDENT_LEDGER_RECOMPUTATION_V1", "computed": computed,
            "species_stock_defect_H": defects, "species_stock_change_H": stocks,
            "species_expected_change_H": expected, "energy_terms_eV_H": energy_terms,
            "source_from_frozen_fixture": {"number_H": source_n, "energy_eV_H": source_u,
                                          "ledger_minus_fixture_number_H": led["source_n"] - source_n,
                                          "ledger_minus_fixture_energy_eV_H": led["source_u"] - source_u},
            "reported_agreement": agreement, "acceptance_gate_changed": False,
            "interpretation": "LEDGER_CLOSURE_DIAGNOSTIC_NOT_TRAJECTORY_ERROR_BOUND"}


def signed_order(error_coarse, error_fine, refinement_ratio=2.):
    """Order for a same-sign, nonzero error pair; crossing is unresolved."""
    ec, ef = _number(error_coarse, "coarse error"), _number(error_fine, "fine error")
    ratio = _number(refinement_ratio, "refinement ratio")
    if ratio <= 1:
        raise DiagnosticInputError("refinement ratio must exceed one")
    reason = "ZERO_ERROR" if ec == 0 or ef == 0 else "SIGNED_ERROR_CROSSING" if (ec > 0) != (ef > 0) else None
    return {"status": "UNRESOLVED" if reason else "RESOLVED_SIGNED_RATIO", "reason": reason,
            "order": None if reason else (math.log(abs(ec)) - math.log(abs(ef))) / math.log(ratio),
            "coarse_error": ec, "fine_error": ef, "refinement_ratio": ratio,
            "accuracy_bound": False}


def reference_free_order(coarse, medium, fine, refinement_ratio=2.):
    """Three-level signed successive-difference order; no reference is used."""
    levels = [_number(v, "refinement level") for v in (coarse, medium, fine)]
    out = signed_order(levels[0] - levels[1], levels[1] - levels[2], refinement_ratio)
    return {**out, "method": "REFERENCE_FREE_SUCCESSIVE_DIFFERENCES", "levels": levels}


def two_scale_coefficients(n, d_n, d_2n):
    """Conditional A/n+B/n² decomposition; not a crossing forecast."""
    n = _number(n, "subdivision count")
    d1, d2 = _number(d_n, "d_n"), _number(d_2n, "d_2n")
    if n <= 0 or not n.is_integer():
        raise DiagnosticInputError("subdivision count must be a positive integer")
    A = n * (4 * d2 - d1)
    B = 2 * n * n * (d1 - 2 * d2)
    if not (math.isfinite(A) and math.isfinite(B)):
        raise DiagnosticInputError("two-scale coefficient overflow")
    return {"A_hat": A, "B_hat": B, "n": n, "d_n": d1, "d_2n": d2,
            "interpretation": "CONDITIONAL_TWO_SCALE_COEFFICIENT_DIAGNOSTIC",
            "assumption": "d_n=A/n+B/n^2+O(n^-3), same fixture and method pair",
            "with_C_over_n3": {"A_hat_minus_A": "-C/(2*n^2)", "B_hat_minus_B": "3*C/(2*n)"},
            "zero_crossing_forecast": None, "accuracy_bound": False}


def conditional_order_interval(error_coarse, error_fine, rho, refinement_ratio=2.):
    """Triangle-inequality order interval CONDITIONAL on a true reference bound.

    rho is not established by this function. Substituting an empirical radius
    gives a sensitivity calculation only. Binary64 evaluation is not validated
    interval arithmetic. Mixed signs do not invalidate the magnitude theorem.
    """
    ec, ef = _number(error_coarse, "coarse error"), _number(error_fine, "fine error")
    radius, ratio = _number(rho, "reference radius"), _number(refinement_ratio, "refinement ratio")
    if radius < 0 or ratio <= 1:
        raise DiagnosticInputError("conditional interval domain")
    lc, lf = max(abs(ec) - radius, 0.), max(abs(ef) - radius, 0.)
    uc, uf = abs(ec) + radius, abs(ef) + radius
    if not (math.isfinite(uc) and math.isfinite(uf)):
        raise DiagnosticInputError("conditional interval overflow")
    resolved = lc > 0 and lf > 0
    return {"status": "CONDITIONAL_INTERVAL" if resolved else "UNRESOLVED",
            "reason": None if resolved else "REFERENCE_RADIUS_REACHES_ZERO_ERROR",
            "lower_order": (math.log(lc) - math.log(uf)) / math.log(ratio) if resolved else None,
            "upper_order": (math.log(uc) - math.log(lf)) / math.log(ratio) if resolved else None,
            "conditional_on_bound": "reference error norm <= rho for both compared endpoints",
            "bound_verified_by_this_function": False, "global_error_bound": None,
            "rho": radius, "refinement_ratio": ratio, "coarse_magnitude_interval": [lc, uc],
            "fine_magnitude_interval": [lf, uf],
            "signed_error_crossing": ec != 0 and ef != 0 and (ec > 0) != (ef > 0),
            "evaluation": "binary64 formula; not a validated interval-arithmetic certificate"}
