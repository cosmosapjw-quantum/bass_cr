"""Exact-arithmetic reference for the BASS_CR shared event-capacity map.

All state entries are nonnegative counts or energies.  A fixed event column
has units state-unit / event, and a proposal rate is events / proper second.
The map is a first-order reaction integrator with exact linear invariants.
It is not the closed-form solution of the nonlinear kinetic ODE.

Only Python's standard library is required.  Fraction arithmetic certifies
algebraic conservation for the finite inputs.  A supplied float is interpreted
as its exact binary rational value.  This small reference kernel is intended
for formula/interface verification; large finite grids use the same formulas
with a separately specified floating-point error policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite
from typing import Mapping


Q = Fraction
K_B_SI = Q("1.380649e-23")
STATE_ORDER = (
    "A_H", "A_HeI", "A_HeII", "A_L",
    "HI", "HII", "HeI", "HeII", "HeIII", "e_th", "U_th", "E_rad",
)


def rational(value) -> Fraction:
    if isinstance(value, float) and not isfinite(value):
        raise ValueError("Every input must be finite")
    return Q(value)


@dataclass(frozen=True)
class EventFamily:
    state_order: tuple[str, ...]
    events: dict[str, dict[str, Fraction]]
    invariant_rows: dict[str, dict[str, Fraction]]
    energies: dict[str, Fraction]
    thresholds: dict[str, Fraction]
    capture_energies: dict[str, Fraction]
    secondary_energy: Fraction


@dataclass(frozen=True)
class CapacityResult:
    state: dict[str, Fraction]
    extents: dict[str, Fraction]
    effective_rates: dict[str, Fraction]
    donor_loads: dict[str, Fraction]
    denominators: dict[str, Fraction]
    retained_lower_bounds: dict[str, Fraction]
    inactive_zero_donor_events: tuple[str, ...]


def build_h_he_family(*, cutoff_energy, I_H, I_HeI, I_HeII,
                      capture_H, capture_HeI, capture_HeII) -> EventFamily:
    """Construct three ionization stages with fixed SI-energy event columns.

    The active daughter energy is 2 E_c.  Each active parent has energy
    2 E_c + I_r + E_c/2, so its secondary electron is below cutoff.
    The terminal A_L channel represents an integrated stopping/thermalization
    event.  Radiative capture nodes are fixed positive kinetic energies.
    """
    ec = rational(cutoff_energy)
    thresholds = {"H": rational(I_H), "HeI": rational(I_HeI),
                  "HeII": rational(I_HeII)}
    captures = {"H": rational(capture_H), "HeI": rational(capture_HeI),
                "HeII": rational(capture_HeII)}
    if ec <= 0 or any(v <= 0 for v in (*thresholds.values(), *captures.values())):
        raise ValueError("Cutoff, ionization thresholds and capture nodes must be positive")
    eps = ec / 2
    energies = {"A_L": 2 * ec}
    for stage, ionization_energy in thresholds.items():
        energies[f"A_{stage}"] = energies["A_L"] + ionization_energy + eps
    pairs = {"H": ("HI", "HII"), "HeI": ("HeI", "HeII"),
             "HeII": ("HeII", "HeIII")}
    events: dict[str, dict[str, Fraction]] = {}
    for stage, (low, high) in pairs.items():
        events[f"impact_{stage}"] = {
            f"A_{stage}": Q(-1), "A_L": Q(1), low: Q(-1), high: Q(1),
            "e_th": Q(1), "U_th": eps,
        }
    events["thermalize_L"] = {"A_L": Q(-1), "e_th": Q(1),
                               "U_th": energies["A_L"]}
    for stage, (low, high) in pairs.items():
        events[f"thermal_ionize_{stage}"] = {
            low: Q(-1), high: Q(1), "e_th": Q(1), "U_th": -thresholds[stage],
        }
    for stage, (low, high) in pairs.items():
        events[f"recombine_{stage}"] = {
            high: Q(-1), "e_th": Q(-1), low: Q(1),
            "U_th": -captures[stage],
            "E_rad": thresholds[stage] + captures[stage],
        }
    invariant_rows = {
        "H_nuclei": {"HI": Q(1), "HII": Q(1)},
        "He_nuclei": {"HeI": Q(1), "HeII": Q(1), "HeIII": Q(1)},
        "charge_over_e": {"HII": Q(1), "HeII": Q(1), "HeIII": Q(2),
                          "e_th": Q(-1), **{name: Q(-1) for name in energies}},
        "kinetic_chemical_radiative_energy": {
            **energies, "U_th": Q(1), "E_rad": Q(1), "HII": thresholds["H"],
            "HeII": thresholds["HeI"], "HeIII": thresholds["HeI"] + thresholds["HeII"],
        },
    }
    return EventFamily(STATE_ORDER, events, invariant_rows, energies,
                       thresholds, captures, eps)


def dot_state(row: Mapping[str, Fraction], state: Mapping[str, Fraction]) -> Fraction:
    return sum((rational(a) * rational(state.get(i, 0)) for i, a in row.items()), Q(0))


def column_invariant_residuals(family: EventFamily) -> dict[str, dict[str, Fraction]]:
    return {name: {r: dot_state(row, column) for r, column in family.events.items()}
            for name, row in family.invariant_rows.items()}


def base_mass_action_proposals(family: EventFamily, state: Mapping[str, Fraction],
                               coefficients: Mapping[str, Fraction], volume) -> dict[str, Fraction]:
    """Evaluate base-stock factors; coefficients may come from a trial T/composition.

    Impact, thermal ionization and capture coefficients have units m^3/s.
    The terminal thermalization coefficient has units 1/s.
    A coefficient is required for every event, including explicitly zero rates.
    """
    v = rational(volume)
    if v <= 0:
        raise ValueError("Physical volume must be positive")
    y = {i: rational(state.get(i, 0)) for i in family.state_order}
    if any(a < 0 for a in y.values()):
        raise ValueError("Base state must be nonnegative")
    k = {r: rational(coefficients[r]) for r in family.events}
    if any(a < 0 for a in k.values()):
        raise ValueError("Coefficients must be nonnegative")
    pairs = {"H": ("HI", "HII"), "HeI": ("HeI", "HeII"),
             "HeII": ("HeII", "HeIII")}
    rates = {"thermalize_L": k["thermalize_L"] * y["A_L"]}
    for stage, (low, high) in pairs.items():
        rates[f"impact_{stage}"] = k[f"impact_{stage}"] * y[f"A_{stage}"] * y[low] / v
        rates[f"thermal_ionize_{stage}"] = k[f"thermal_ionize_{stage}"] * y["e_th"] * y[low] / v
        rates[f"recombine_{stage}"] = k[f"recombine_{stage}"] * y["e_th"] * y[high] / v
    return {r: rates[r] for r in family.events}


def capacity_step(state: Mapping[str, Fraction], events: Mapping[str, Mapping[str, Fraction]],
                  proposal_rates: Mapping[str, Fraction], step_size) -> CapacityResult:
    """Apply equations ES.13--ES.16 using one shared extent per event.

    Zero base stocks disable only events with a negative increment in that
    stock.  Reactant/catalyst availability also belongs in proposal_rates.
    No clipping, renormalization or independent reservoir correction is used.
    """
    h = rational(step_size)
    if h < 0:
        raise ValueError("Step size must be nonnegative")
    names = tuple(dict.fromkeys((*state.keys(), *(i for col in events.values() for i in col))))
    y = {i: rational(state.get(i, 0)) for i in names}
    if any(v < 0 for v in y.values()):
        raise ValueError("Base state must be nonnegative")
    s = {r: {i: rational(col.get(i, 0)) for i in names} for r, col in events.items()}
    rates = {r: rational(proposal_rates[r]) for r in events}
    if any(v < 0 for v in rates.values()):
        raise ValueError("Proposal rates must be nonnegative")
    c = {r: {i: max(-s[r][i], Q(0)) for i in names} for r in events}
    inactive = tuple(r for r in events if any(c[r][i] > 0 and y[i] == 0 for i in names))
    for r in inactive:
        rates[r] = Q(0)
    loads = {i: sum((c[r][i] * rates[r] for r in events), Q(0)) for i in names}
    denominators = {}
    extents = {}
    for r in events:
        if r in inactive:
            denominators[r] = Q(1)
            extents[r] = Q(0)
        else:
            d = sum((loads[i] / y[i] for i in names if c[r][i] > 0), Q(0))
            denominators[r] = 1 + h * d
            extents[r] = h * rates[r] / denominators[r]
    result = {i: y[i] + sum((s[r][i] * extents[r] for r in events), Q(0)) for i in names}
    lower = {i: y[i] / (1 + h * loads[i] / y[i]) if y[i] > 0 else Q(0) for i in names}
    if any(result[i] < lower[i] for i in names):
        raise ArithmeticError("Internal capacity inequality violated")
    return CapacityResult(result, extents, rates, loads, denominators, lower, inactive)


def thermal_count(state: Mapping[str, Fraction]) -> Fraction:
    return sum((rational(state.get(i, 0)) for i in ("HI", "HII", "HeI", "HeII", "HeIII", "e_th")), Q(0))


def temperature(state: Mapping[str, Fraction], k_B=K_B_SI) -> Fraction:
    n = thermal_count(state)
    kb = rational(k_B)
    u = rational(state["U_th"])
    if n <= 0 or kb <= 0 or u < 0:
        raise ValueError("Temperature requires N_th > 0, k_B > 0 and U_th >= 0")
    return u / (Q(3, 2) * kb * n)
