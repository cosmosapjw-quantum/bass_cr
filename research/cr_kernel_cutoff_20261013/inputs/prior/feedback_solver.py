"""Bounded Picard driver for the shared BASS_CR event-capacity map.

The caller supplies a contraction bound already verified on the named domain.
This module checks 0 <= q < 1 and domain membership; it does not prove q or
the global self-map property.  Certificates are conditional on that supplied
evidence, the scale bounds, and any declared map-evaluation error.

Each accepted iterate is exactly one capacity_step from the fixed initial
state.  No clipping or independent reservoir adjustment is performed.
Fractions retain the reference kernel's exact finite-input arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from types import MappingProxyType
from typing import Callable, Mapping

from event_capacity_step import (
    CapacityResult, K_B_SI, capacity_step, rational, thermal_count,
)

Q = Fraction
State = Mapping[str, Fraction]
Rates = Mapping[str, Fraction]


@dataclass(frozen=True)
class DomainContract:
    name: str
    contains: Callable[[State], bool]
    evidence: str


@dataclass(frozen=True)
class ThermalCertificate:
    count_lower_bound: Fraction
    count_scale_bound: Fraction
    count: Callable[[State], Fraction] = thermal_count
    energy_key: str = "U_th"
    k_B: Fraction = K_B_SI


@dataclass(frozen=True)
class IterationRecord:
    index: int
    state: dict[str, Fraction]
    map_residual_norm: Fraction
    discrete_state_error_bound: Fraction
    discrete_temperature_error_bound: Fraction


@dataclass(frozen=True)
class PhysicalEndpointDefect:
    components: dict[str, Fraction]
    weighted_norm: Fraction
    scope: str = "supplied continuous reaction vector field, endpoint rate defect"
    norm_units: str = "scaled state per proper second"


@dataclass(frozen=True)
class FeedbackResult:
    status: str
    state: dict[str, Fraction]
    event_extents: dict[str, Fraction]
    iterations: int
    map_evaluations: int
    temperature: Fraction
    map_residual_norm: Fraction
    discrete_state_error_bound: Fraction
    discrete_temperature_error_bound: Fraction
    contraction_bound: Fraction
    contraction_evidence: str
    domain_name: str
    domain_evidence: str
    map_error_bound: Fraction
    history: tuple[IterationRecord, ...]
    certifying_map_image: CapacityResult | None
    physical_ode_defect: PhysicalEndpointDefect | None
    certificate_authority: str = (
        "caller supplied verified contraction/domain/scale bounds; "
        "driver checks numeric range and visited-state membership"
    )
    certificate_target: str = "exact fixed point of the declared capacity map"


def weighted_norm(vector: State, scales: State) -> Fraction:
    return max((abs(rational(value)) / rational(scales[name])
                for name, value in vector.items()), default=Q(0))


def solve_feedback(
    initial_state: State,
    events: Mapping[str, State],
    proposal_evaluator: Callable[[State, State], Rates],
    step_size,
    *,
    scales: State,
    contraction_bound,
    contraction_evidence: str,
    domain: DomainContract,
    thermal: ThermalCertificate,
    temperature_tolerance,
    max_iterations: int,
    map_error_bound=Q(0),
    physical_rate_evaluator: Callable[[State], Rates] | None = None,
) -> FeedbackResult:
    """Solve y = y_n + S*xi(y;y_n) with a temperature stopping certificate.

    proposal_evaluator(base, trial) freezes donor factors at base and evaluates
    coefficient feedback at trial. It must guard zero reactants before calling
    singular coefficients. Its rate keys must equal the event keys.

    max_iterations counts accepted Picard updates. One extra map evaluation
    certifies the residual of the returned state. MAX_ITERATIONS returns that
    feasible state and its actual certificate without declaring convergence.

    map_error_bound bounds the computed map's distance from the reference map
    in weighted_norm; q belongs to that reference map on the same domain.
    Optional physical rates use endpoint donor factors. Their output is a
    separate dimensional rate defect; no continuous ODE solve is performed.
    """
    if not isinstance(max_iterations, int) or isinstance(max_iterations, bool) or max_iterations < 0:
        raise ValueError("max_iterations must be a nonnegative integer")
    if not contraction_evidence.strip() or not domain.name.strip() or not domain.evidence.strip():
        raise ValueError("Contraction and domain evidence identifiers are required")
    h = rational(step_size)
    q = rational(contraction_bound)
    tol = rational(temperature_tolerance)
    epsilon = rational(map_error_bound)
    n_min = rational(thermal.count_lower_bound)
    a_n = rational(thermal.count_scale_bound)
    c_v = Q(3, 2) * rational(thermal.k_B)
    if h < 0 or not Q(0) <= q < Q(1) or tol < 0 or epsilon < 0:
        raise ValueError("Require h>=0, 0<=q<1, tolerance>=0 and map error>=0")
    if n_min <= 0 or a_n < 0 or c_v <= 0:
        raise ValueError("EOS certificate requires positive count floor and k_B")
    names = tuple(dict.fromkeys((*initial_state, *(i for col in events.values() for i in col))))
    if not names or thermal.energy_key not in names:
        raise ValueError("State must contain the declared thermal-energy coordinate")
    base = {name: rational(initial_state.get(name, 0)) for name in names}
    scale = {name: rational(scales[name]) for name in names}
    if any(value <= 0 for value in scale.values()):
        raise ValueError("Every state scale must be positive")
    columns = {r: {i: rational(col.get(i, 0)) for i in names}
               for r, col in events.items()}
    base_view = MappingProxyType(base)

    def checked_temperature(state: State) -> Fraction:
        if any(state[i] < 0 for i in names):
            raise ValueError("A visited state is negative")
        view = MappingProxyType(dict(state))
        if not domain.contains(view):
            raise ValueError("Visited state violates domain contract: " + domain.name)
        count = rational(thermal.count(view))
        if count < n_min:
            raise ValueError("Visited state violates the supplied thermal-count floor")
        return state[thermal.energy_key] / (c_v * count)

    def rates_from(values: Rates) -> dict[str, Fraction]:
        if set(values) != set(columns):
            raise ValueError("Rate keys must equal the declared event keys")
        result = {r: rational(values[r]) for r in columns}
        if any(v < 0 for v in result.values()):
            raise ValueError("Reaction rates must be nonnegative")
        return result

    def physical_defect(state: State) -> PhysicalEndpointDefect | None:
        if physical_rate_evaluator is None or h == 0:
            return None
        rates = rates_from(physical_rate_evaluator(MappingProxyType(dict(state))))
        defect = {
            i: (state[i] - base[i]) / h
            - sum((columns[r][i] * rates[r] for r in columns), Q(0))
            for i in names
        }
        return PhysicalEndpointDefect(defect, weighted_norm(defect, scale))

    temperature = checked_temperature(base)
    state = dict(base)
    accepted_extents = {r: Q(0) for r in columns}
    records: list[IterationRecord] = []

    if h == 0:
        record = IterationRecord(0, dict(state), Q(0), Q(0), Q(0))
        return FeedbackResult(
            status="CONVERGED_ZERO_STEP", state=state,
            event_extents=accepted_extents, iterations=0, map_evaluations=0,
            temperature=temperature, map_residual_norm=Q(0),
            discrete_state_error_bound=Q(0),
            discrete_temperature_error_bound=Q(0), contraction_bound=q,
            contraction_evidence=contraction_evidence, domain_name=domain.name,
            domain_evidence=domain.evidence, map_error_bound=epsilon,
            history=(record,), certifying_map_image=None, physical_ode_defect=None,
        )

    for iteration in range(max_iterations + 1):
        temperature = checked_temperature(state)
        proposal = rates_from(proposal_evaluator(
            base_view, MappingProxyType(dict(state))))
        image = capacity_step(base, columns, proposal, h)
        checked_temperature(image.state)
        residual = weighted_norm(
            {i: image.state[i] - state[i] for i in names}, scale)
        state_bound = (residual + epsilon) / (1 - q)
        eos_factor = scale[thermal.energy_key] / (c_v * n_min) + temperature * a_n / n_min
        temperature_bound = eos_factor * state_bound
        records.append(IterationRecord(
            iteration, dict(state), residual, state_bound, temperature_bound))
        if temperature_bound <= tol or iteration == max_iterations:
            status = "CONVERGED" if temperature_bound <= tol else "MAX_ITERATIONS"
            return FeedbackResult(
                status=status, state=dict(state), event_extents=dict(accepted_extents),
                iterations=iteration, map_evaluations=iteration + 1,
                temperature=temperature, map_residual_norm=residual,
                discrete_state_error_bound=state_bound,
                discrete_temperature_error_bound=temperature_bound,
                contraction_bound=q, contraction_evidence=contraction_evidence,
                domain_name=domain.name, domain_evidence=domain.evidence,
                map_error_bound=epsilon, history=tuple(records),
                certifying_map_image=image,
                physical_ode_defect=physical_defect(state),
            )
        state = dict(image.state)
        accepted_extents = dict(image.extents)

    raise AssertionError("Finite Picard loop ended without a result")

