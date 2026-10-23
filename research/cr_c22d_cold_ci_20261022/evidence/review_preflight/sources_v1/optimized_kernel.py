"""C22D exact-arithmetic rearrangements of the frozen C22C finite kernel.

No trajectory integration, rate interpolation cache, isotope quotient, state
deletion or closure extension is performed here.  ``baseline_module`` is the
byte-pinned C22C excitation module supplied by the caller.  ``baseline_provider``
has already validated the two finite CCC tables.  Constants, coverage failures,
positive endpoint weights and finite-tail semantics are inherited unchanged.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.special import gammainc


# J_n(z) = sum_{k=0}^{18} (-z)^k/[k! (n+k+1)] + R_n(z).
# This is the same degree and switch as C22C; only its evaluation order changes.
SERIES_COEFFICIENTS = np.array([
    [(-1.0)**k / (math.factorial(k) * (n + k + 1)) for n in range(3)]
    for k in range(19)
], dtype=float)
SERIES_COEFFICIENTS.flags.writeable = False


def moments_ordered(y):
    """Share identical Taylor terms while preserving each entry's operations.

    Each J_n receives term/(n+k+1), in k=0,...,18 order, exactly as in C22C.
    The common term sequence is independent of n and is computed once.  No
    reassociation, new coefficient approximation, fitted rate or changed switch
    is introduced.  The positive-y gamma branch retains its original arithmetic.
    """
    y = np.asarray(y, dtype=float)
    if np.any(~np.isfinite(y)) or np.any(y <= 0):
        raise ValueError("MOMENT_ARGUMENT_MUST_BE_POSITIVE_FINITE")
    shape = y.shape
    flat = y.reshape(-1)
    result = np.empty((3, flat.size), dtype=float)
    small = flat <= 0.5
    if np.any(small):
        z = flat[small]
        term = np.ones_like(z)
        n_plus_one = np.arange(1, 4, dtype=float)[:, None]
        value = term[None, :] / n_plus_one
        for k in range(1, 19):
            term *= -z / k
            value += term[None, :] / (n_plus_one + k)
        result[:, small] = value
    if np.any(~small):
        z = flat[~small]
        for n in range(3):
            result[n, ~small] = math.factorial(n) * gammainc(n + 1, z) / z**(n + 1)
    return result.reshape((3,) + shape)


def moments_horner(y):
    """The same three positive moments with 18 fused Horner stages.

    On 0 < y <= 1/2 the alternating-series remainder of the unchanged degree-18
    polynomial is at most y**19/[19! (n+20)].  This analytic truncation statement
    is distinct from the measured float64 reassociation error.  The y > 1/2
    incomplete-gamma branch is unchanged, and an empty branch performs no work.
    """
    y = np.asarray(y, dtype=float)
    if np.any(~np.isfinite(y)) or np.any(y <= 0):
        raise ValueError("MOMENT_ARGUMENT_MUST_BE_POSITIVE_FINITE")
    shape = y.shape
    flat = y.reshape(-1)
    result = np.empty((3, flat.size), dtype=float)
    small = flat <= 0.5
    if np.any(small):
        z = flat[small][None, :]
        value = np.broadcast_to(SERIES_COEFFICIENTS[18, :, None], (3, z.size)).copy()
        for k in range(17, -1, -1):
            value *= z
            value += SERIES_COEFFICIENTS[k, :, None]
        result[:, small] = value
    if np.any(~small):
        z = flat[~small]
        for n in range(3):
            result[n, ~small] = math.factorial(n) * gammainc(n + 1, z) / z**(n + 1)
    return result.reshape((3,) + shape)


class OptimizedExcitation:
    """Adapter preserving the baseline provider API and source arrays.

    The default moments_ordered preserves per-entry arithmetic.  moments_horner
    is an explicitly separate research candidate.  No temperature rounding or memoized
    rate is used; every new temperature is evaluated at its original float64
    value.  Coefficient precomputation is independent of temperature or state.
    """
    def __init__(self, baseline_provider, baseline_module, *, moment_function=moments_ordered):
        self.source = baseline_provider
        self.constants = baseline_module
        self.moment_function = moment_function
        for name in ("energy", "sigma", "left", "width"):
            setattr(self, name, getattr(baseline_provider, name))

    def evaluate(self, temperature_K, *, species="H1", full_physical_rate=False):
        b = self.constants
        if species != "H1" or full_physical_rate:
            raise ValueError("ATOMIC_RATE_COVERAGE_UNAVAILABLE")
        if isinstance(temperature_K, (bool, np.bool_)):
            raise ValueError("INVALID_TEMPERATURE")
        temperature_K = float(temperature_K)
        if (not math.isfinite(temperature_K)
                or not b.PROVIDER_T_DOMAIN_K[0] <= temperature_K <= b.PROVIDER_T_DOMAIN_K[1]):
            raise ValueError("FINITE_PROVIDER_NUMERICAL_T_DOMAIN")
        theta = b.KB_EV_K * temperature_K
        j0, j1, j2 = self.moment_function(self.width / theta)
        wl = self.left * (j0 - j1) + self.width * (j1 - j2)
        wr = self.left * j1 + self.width * j2
        if np.any(wl < 0) or np.any(wr < 0):
            raise ArithmeticError("NEGATIVE_EXACT_ENDPOINT_WEIGHT")
        weight = self.width * np.exp(-(self.left - b.DELTA_E_EV) / theta)
        scaled = np.sum(weight * (self.sigma[:, :-1] * wl + self.sigma[:, 1:] * wr), axis=1)
        if np.any(~np.isfinite(scaled)) or np.any(scaled <= 0):
            raise ArithmeticError("FINITE_CORE_POSITIVE_SCALED_INTEGRAL_LOST")
        logq = (math.log(b.K_CM3_S) - 1.5 * math.log(theta)
                - b.DELTA_E_EV / theta + np.log(scaled))
        with np.errstate(under="ignore"):
            rates = np.exp(logq)
        return {"q_cm3_s": rates, "log10_q_cm3_s": logq / math.log(10),
                "float64_underflow": rates == 0,
                "log10_conditional_tail_per_sigma_cap_a0sq":
                    (math.log(b.K_CM3_S) - .5 * math.log(theta)
                     + math.log(b.E_MAX_EV + theta) - b.E_MAX_EV / theta) / math.log(10)}

    def conditional_tail_log10(self, temperature_K, assumed_sigma_cap_a0sq):
        cap = float(assumed_sigma_cap_a0sq)
        if not math.isfinite(cap) or cap <= 0:
            raise ValueError("POSITIVE_EXPLICIT_ASSUMED_TAIL_CAP_REQUIRED")
        coefficient = self.evaluate(temperature_K)["log10_conditional_tail_per_sigma_cap_a0sq"]
        return coefficient + math.log10(cap)


def c22a_rhs_from_fields(model, eta, y, q):
    """Frozen C22A RHS with caller-supplied fields for exactly this (eta,y).

    Required provenance: q = model.fields(eta,y).  Passing stale fields is an
    invalid internal API use.  This function makes no cross-call state cache.
    All state coordinates and summation orders below are retained from C22A.
    """
    obj = model.kinetic
    h, s = q["H"], q["s"]
    v, gamma = s / h, q["GammaT"] / h
    dy = np.zeros(model.size)
    dy[:4] = (obj.source.href / h, v,
               -3*y[2] + 3*obj.source.h0**2/(obj.source.href*h)
               * (q["Pi_radiation_norm"] + q["Pi_matter_norm"]), 0.0)
    n = obj.n
    for i, (key, matrix) in enumerate((("E_gamma", obj.energy_matrix),
                                      ("N_gamma", obj.number_matrix),
                                      ("E_nu", obj.energy_matrix),
                                      ("N_nu", obj.number_matrix))):
        sl = slice(4+i*n, 4+(i+1)*n)
        dy[sl] = v * (matrix @ q[key])
        if i < 2:
            dy[sl] -= gamma * obj.thomson * q[key]
    photo, rr, capture, energy = model.events(eta, y, q)
    dx, dg = dy[model.ax], dy[model.gx]
    dy[model.iu] = -2.0 * y[model.iu]
    dy[model.iwg] = 2.0 * y[model.iu]
    dy[model.iwr] = float(energy @ y[model.gx])
    for edge, (lower, upper, ch) in enumerate(model.atomic.edges):
        p = photo[edge]
        ionizations = float(np.sum(p))
        r = rr[edge]
        net = ionizations - r
        dx[lower] -= net / model.atomic.scales[lower]
        dx[upper] += net / model.atomic.scales[upper]
        dg -= p
        dy[model.iu] += float((energy-model.thresholds[ch]) @ p) - capture[ch]*r
        dy[model.iesc] += (model.thresholds[ch] + capture[ch])*r
        dy[model.irr] += r
        dy[model.iabs] += ionizations
    dy[model.itau] = q["GammaT_physical"] / h
    return dy


def c22c_rhs_from_fields(model, eta, full, q, *, excitation_provider=None):
    """Combine unchanged A/B/C contributions using one fields dictionary.

    model is an immutable C22C model, not a C22D model.  New physics must be
    accumulated separately by the caller.  This helper retains all 77 output
    coordinates, the two event counters and the Compton bath ledger.
    """
    b = model.base
    a = b.base
    full = np.asarray(full)
    derivative = np.zeros(model.size)
    derivative[:a.size] = c22a_rhs_from_fields(a, eta, full[:a.size], q)
    rate, _ = model.compton(eta, full, q)
    flux = rate / q["H"]
    derivative[model.iu] += flux
    derivative[model.ibath] = -flux
    if excitation_provider is None:
        events = model.excitation_events(eta, full, q)
        # C22C fixes this source-table threshold; no binding energy is changed.
        delta_e = 10.20435
    else:
        delta_e = excitation_provider.constants.DELTA_E_EV
        if not model.excitation_enabled:
            events = np.zeros(2)
        else:
            t = q["temperature_K"]
            lo, hi = excitation_provider.constants.ACTIVE_T_DOMAIN_K
            if not lo <= t <= hi:
                raise ValueError("C22C_ACTIVE_TEMPERATURE_SELECTOR")
            rates = excitation_provider.evaluate(t)["q_cm3_s"]
            h0 = model.atomic.physical_abundances(full[model.ax])[model.h1_ground]
            events = q["n_e_cm3"] * h0 * rates / q["H"]
    derivative[model.iu] -= delta_e * float(np.sum(events))
    derivative[model.ic2s:model.ic2p + 1] = events
    return derivative


def c22c_rhs_shared_fields(model, eta, full, *, excitation_provider=None):
    """Public wrapper computing one fresh q and retaining input validation."""
    q = model.fields(eta, full)
    return c22c_rhs_from_fields(model, eta, full, q,
                                excitation_provider=excitation_provider)
