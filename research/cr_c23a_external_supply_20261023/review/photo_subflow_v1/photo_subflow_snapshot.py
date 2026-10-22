"""Positive frozen-UVB H/He photoionization subflow, with explicit event ledgers.

This is one source-only reaction component at fixed redshift/proper volume.
It is not an IGM history. Recombination, collisions, expansion, transport and
secondary degradation belong to separately admitted components. An explicit
five-population H/He input is required; no missing isotope is filled by zero.
All populations, events and energies are per the caller's fixed reference.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping
import numpy as np

POPULATIONS = ("HI", "HII", "HeI", "HeII", "HeIII")
CHANNELS = ("HI", "HeI", "HeII")
KB_EV_K = 1.380649e-23 / 1.602176634e-19
POISSON_TERMS = 32
MAX_RATE_TIME = 1.0e6


def _finite_values(values, labels, *, positive=False):
    if set(values) != set(labels):
        raise ValueError("EXPLICIT_COMPONENT_INVENTORY_REQUIRED")
    out = np.array([float(values[k]) for k in labels], dtype=np.float64)
    if not np.all(np.isfinite(out)) or np.any(out <= 0 if positive else out < 0):
        raise ValueError("NONFINITE_OR_NEGATIVE_COMPONENT_INPUT")
    return out


def _birth_kernel(first: float, second: float, dt: float):
    """Three-stage pure-birth semigroup by nonnegative uniformization.

    G columns conserve a nucleus. exp(dt G) is evaluated with a scaled Poisson
    series through k=32 at theta<=1, followed by squaring. At every stage the
    mathematically exact absorbing column (0,0,1) is assigned explicitly.
    This is not a normalization or clipping of source data or populations.
    """
    rate = max(first, second)
    theta = rate * dt
    if not math.isfinite(theta) or theta > MAX_RATE_TIME:
        raise ValueError("PHOTO_SUBFLOW_RATE_TIME_OUTSIDE_NUMERICAL_CONTRACT")
    if theta == 0:
        return np.eye(3), {"squarings": 0, "scaled_theta": 0.0,
                           "poisson_terms": 0, "series_tail_upper": 0.0}
    squarings = max(0, math.ceil(math.log2(theta)))
    scaled = math.ldexp(theta, -squarings)
    p = np.array([[1-first/rate, 0, 0],
                  [first/rate, 1-second/rate, 0],
                  [0, second/rate, 1]], dtype=np.float64)
    term = np.eye(3)
    weight = math.exp(-scaled)
    kernel = weight * term
    for k in range(1, POISSON_TERMS + 1):
        term = term @ p
        weight *= scaled / k
        kernel += weight * term
    kernel[:, 2] = (0.0, 0.0, 1.0)
    for _ in range(squarings):
        kernel = kernel @ kernel
        kernel[:, 2] = (0.0, 0.0, 1.0)
    # These diagonal/one-transition entries have elementary exact formulas.
    a, b = first*dt, second*dt
    kernel[0, 0] = math.exp(-a)
    kernel[1, 1] = math.exp(-b)
    kernel[2, 1] = -math.expm1(-b)
    d = abs(b-a)
    divided = math.exp(-min(a, b)) * (-math.expm1(-d)/d if d else 1.0)
    kernel[1, 0] = a * divided
    if not np.all(np.isfinite(kernel)) or np.any(kernel < 0):
        raise ArithmeticError("NONPOSITIVE_BIRTH_KERNEL")
    # Positive Poisson tail of ONE scaled exact-arithmetic series. Rounding is
    # not included. The total truncation norm bound is <=2**squarings * tail.
    next_weight = math.exp(-scaled) * scaled**(POISSON_TERMS+1) / math.factorial(POISSON_TERMS+1)
    tail = next_weight / (1.0-scaled/(POISSON_TERMS+2))
    return kernel, {"squarings": squarings, "scaled_theta": scaled,
                    "poisson_terms": POISSON_TERMS,
                    "series_tail_upper": math.ldexp(tail, squarings),
                    "tail_scope": "exact_arithmetic_truncation_only; rounding and physical errors separate"}


@dataclass(frozen=True)
class SubflowResult:
    populations: dict[str, float]
    events: dict[str, float]
    thermal_energy_ev: float
    imported_energy_ev: float
    binding_increment_ev: float
    heat_increment_ev: float
    electron_increment: float
    temperature_K: float
    diagnostics: dict


def advance(populations: Mapping[str, float], thermal_energy_ev: float,
            duration_s: float, gamma_s_inv: Mapping[str, float],
            heat_ev_s_inv: Mapping[str, float], binding_ev: Mapping[str, float]) -> SubflowResult:
    """Advance an explicit H/He source subflow with constant externally supplied rates.

    Gamma has units s^-1 per target, heat eV s^-1 per target; the target number
    cancels in heat/Gamma. The external energy is defined by the caller's
    binding registry plus those heat moments. The source table alone does not
    identify a photon/secondary spectrum or its exact threshold convention.
    """
    x = _finite_values(populations, POPULATIONS)
    g = _finite_values(gamma_s_inv, CHANNELS)
    h = _finite_values(heat_ev_s_inv, CHANNELS)
    chi = _finite_values(binding_ev, CHANNELS, positive=True)
    u, dt = float(thermal_energy_ev), float(duration_s)
    if not math.isfinite(u) or u < 0 or not math.isfinite(dt) or dt < 0:
        raise ValueError("PHOTO_SUBFLOW_INVALID_ENERGY_OR_DURATION")
    if np.any((g == 0) & (h != 0)):
        raise ValueError("HEAT_WITHOUT_PHOTOIONIZATION_IS_A_DIFFERENT_PROCESS")
    if not math.isfinite(max(g)*dt) or max(g)*dt > MAX_RATE_TIME:
        raise ValueError("PHOTO_SUBFLOW_RATE_TIME_OUTSIDE_NUMERICAL_CONTRACT")
    nuclei = math.fsum(x)
    if nuclei <= 0:
        raise ValueError("EMPTY_COMPONENT_INVENTORY")
    kernel, info = _birth_kernel(g[1], g[2], dt)
    counts = np.array([x[0] * -math.expm1(-g[0]*dt),
                       x[2] * -math.expm1(-g[1]*dt),
                       math.fsum((x[2]*kernel[2, 0], x[3]*kernel[2, 1]))])
    out = np.array([x[0]*math.exp(-g[0]*dt), x[1]+counts[0],
                    x[2]*kernel[0, 0], math.fsum((x[2]*kernel[1, 0], x[3]*kernel[1, 1])),
                    x[4]+counts[2]])
    heat = math.fsum(float(c)*float(hh/gg) for c, hh, gg in zip(counts, h, g) if gg > 0)
    bound = math.fsum(float(c)*float(ch) for c, ch in zip(counts, chi))
    imported = math.fsum((heat, bound))
    final_u = u + heat
    electrons_before = math.fsum((x[1], x[3], 2*x[4]))
    electrons_after = math.fsum((out[1], out[3], 2*out[4]))
    particles = math.fsum(out) + electrons_after
    temp = 2*final_u/(3*KB_EV_K*particles)
    if not np.all(np.isfinite(out)) or not all(map(math.isfinite, (heat, bound, imported, final_u, temp))):
        raise ArithmeticError("PHOTO_SUBFLOW_NONFINITE_RESULT")
    diagnostics = dict(info)
    diagnostics.update({
        "hydrogen_inventory_residual": math.fsum(out[:2])-math.fsum(x[:2]),
        "helium_inventory_residual": math.fsum(out[2:])-math.fsum(x[2:]),
        "charge_event_residual": electrons_after-electrons_before-math.fsum(counts),
        "energy_event_residual_ev": math.fsum((heat, bound, -imported)),
        "nonnegative": bool(np.all(out >= 0) and np.all(counts >= 0)),
        "source_binding_convention": "explicit_model_registry; source_numeric_thresholds_unresolved",
        "source_scope": "frozen_redshift_external_H_He_photoionization_subflow",
        "full_21_population_adoption": "NOT_ADMITTED_BY_THIS_COMPONENT",
        "global_error_bound": None,
    })
    return SubflowResult(dict(zip(POPULATIONS, map(float, out))), dict(zip(CHANNELS, map(float, counts))),
                         final_u, imported, bound, heat, math.fsum(counts), temp, diagnostics)
