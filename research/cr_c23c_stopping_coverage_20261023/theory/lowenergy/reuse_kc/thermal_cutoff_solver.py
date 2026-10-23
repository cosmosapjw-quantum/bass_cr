"""Exact finite thermal-cutoff closure on fixed common count/energy inventories.

This is a reference for TCF.4--TCF.46, not an ODE integrator or physical-kernel
qualification. Continuous box spectra and finite atomic spectra are separate
representations. Every candidate is evaluated from immutable inventory data.

The continuous solver proves a slope bound for its supplied finite box model;
it does not verify that the model approximates a physical spectrum. All inputs
must be Fraction, int, or a Fraction-compatible string. Floats are rejected to
avoid an undocumented conversion from approximate physical data to exact data.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from fractions import Fraction

Exact = Fraction | int | str


def as_fraction(value: Exact) -> Fraction:
    if isinstance(value, float):
        raise TypeError("Use an explicit Fraction or decimal/rational string.")
    return Fraction(value)


@dataclass(frozen=True)
class Box:
    lower: Fraction
    upper: Fraction
    density: Fraction

    def __post_init__(self) -> None:
        for name in ("lower", "upper", "density"):
            object.__setattr__(self, name, as_fraction(getattr(self, name)))
        if self.lower < 0 or self.upper <= self.lower or self.density < 0:
            raise ValueError("A box requires 0 <= lower < upper and density >= 0.")

    def below(self, cutoff: Fraction) -> tuple[Fraction, Fraction]:
        # Interval intersection only; this does not clip a physical state.
        upper = min(self.upper, cutoff)
        if upper <= self.lower:
            return Fraction(0), Fraction(0)
        count = self.density * (upper - self.lower)
        energy = self.density * (upper * upper - self.lower * self.lower) / 2
        return count, energy


@dataclass(frozen=True)
class BoxSpectrum:
    boxes: tuple[Box, ...]

    def __post_init__(self) -> None:
        boxes = tuple(self.boxes)
        if not all(isinstance(box, Box) for box in boxes):
            raise TypeError("boxes must contain Box instances.")
        object.__setattr__(self, "boxes", boxes)

    @property
    def total_count(self) -> Fraction:
        return sum((box.density * (box.upper - box.lower)
                    for box in self.boxes), Fraction(0))

    @property
    def total_energy(self) -> Fraction:
        return sum((box.density * (box.upper**2 - box.lower**2) / 2
                    for box in self.boxes), Fraction(0))

    def below(self, cutoff: Fraction) -> tuple[Fraction, Fraction]:
        moments = tuple(box.below(cutoff) for box in self.boxes)
        return (sum((count for count, _ in moments), Fraction(0)),
                sum((energy for _, energy in moments), Fraction(0)))

    def interior_density(self, energy: Fraction) -> Fraction:
        """Only used away from all box endpoints in slope certification."""
        return sum((box.density for box in self.boxes
                    if box.lower < energy < box.upper), Fraction(0))


@dataclass(frozen=True)
class BoundaryState:
    temperature: Fraction
    cutoff: Fraction
    thermal_count: Fraction
    thermal_energy: Fraction
    active_count: Fraction
    active_energy: Fraction
    transferred_count: Fraction
    transferred_energy: Fraction
    eos_residual: Fraction


@dataclass(frozen=True)
class ContinuousCutoffProblem:
    spectrum: BoxSpectrum
    common_count: Fraction
    common_energy: Fraction
    nucleus_count: Fraction
    reference_cutoff: Fraction
    k_b: Fraction
    chi: Fraction
    temperature_lower: Fraction
    temperature_upper: Fraction

    def __post_init__(self) -> None:
        for name in ("common_count", "common_energy", "nucleus_count",
                     "reference_cutoff", "k_b", "chi", "temperature_lower",
                     "temperature_upper"):
            object.__setattr__(self, name, as_fraction(getattr(self, name)))
        if self.k_b <= 0 or self.chi <= 0 or self.nucleus_count <= 0:
            raise ValueError("k_b, chi and nucleus_count must be positive.")
        if not 0 < self.temperature_lower < self.temperature_upper:
            raise ValueError("A strictly positive, nondegenerate bracket is required.")
        if not self.temperature_lower <= self.reference_temperature <= self.temperature_upper:
            raise ValueError("The reference temperature must lie in the bracket.")
        if self.base_count < self.nucleus_count:
            raise ValueError("The unresolved base count must contain all nuclei.")
        if self.base_energy < 0:
            raise ValueError("Resolved spectral energy exceeds common energy.")

    @property
    def c_v(self) -> Fraction:
        return Fraction(3, 2) * self.k_b

    @property
    def alpha(self) -> Fraction:
        return self.chi * self.k_b

    @property
    def reference_temperature(self) -> Fraction:
        return self.reference_cutoff / self.alpha

    @property
    def base_count(self) -> Fraction:
        return self.common_count - self.spectrum.total_count

    @property
    def base_energy(self) -> Fraction:
        return self.common_energy - self.spectrum.total_energy

    def evaluate(self, temperature: Exact) -> BoundaryState:
        temperature = as_fraction(temperature)
        if not self.temperature_lower <= temperature <= self.temperature_upper:
            raise ValueError("Candidate temperature lies outside the admitted bracket.")
        cutoff = self.alpha * temperature
        low_count, low_energy = self.spectrum.below(cutoff)
        ref_count, ref_energy = self.spectrum.below(self.reference_cutoff)
        count = self.base_count + low_count
        energy = self.base_energy + low_energy
        active_count = self.spectrum.total_count - low_count
        active_energy = self.spectrum.total_energy - low_energy
        if count <= 0 or min(energy, active_count, active_energy) < 0:
            raise ValueError("A nonpositive EOS count or negative inventory was produced.")
        return BoundaryState(
            temperature, cutoff, count, energy, active_count, active_energy,
            low_count - ref_count, low_energy - ref_energy,
            self.c_v * temperature * count - energy,
        )

    def derivative_lower_bound(self) -> Fraction:
        """Exact essential infimum of F_T on the finite box bracket.

        At each density knot F is continuous and piecewise quadratic. Between
        knots F_T is affine, so both one-sided interval endpoint values suffice.
        Density jumps do not receive a fictitious classical two-sided derivative.
        """
        knots = {self.temperature_lower, self.temperature_upper}
        for box in self.spectrum.boxes:
            for energy in (box.lower, box.upper):
                temperature = energy / self.alpha
                if self.temperature_lower < temperature < self.temperature_upper:
                    knots.add(temperature)
        ordered = sorted(knots)
        bounds: list[Fraction] = []
        for left, right in zip(ordered, ordered[1:]):
            density = self.spectrum.interior_density(
                self.alpha * (left + right) / 2
            )
            for temperature in (left, right):
                state = self.evaluate(temperature)
                bounds.append(
                    self.c_v * state.thermal_count
                    + self.alpha * (self.c_v * temperature - state.cutoff) * density
                )
        return min(bounds)


@dataclass(frozen=True)
class BisectionResult:
    status: str
    converged: bool
    state: BoundaryState
    bracket: tuple[Fraction, Fraction]
    derivative_lower_bound: Fraction
    temperature_error_bound: Fraction
    iterations: int
    evaluations: tuple[BoundaryState, ...]
    certificate_scope: str = "Exact finite-box endpoint; no ODE or representation error."


def solve_continuous_cutoff(
    problem: ContinuousCutoffProblem,
    *,
    temperature_tolerance: Exact,
    max_iterations: int = 128,
) -> BisectionResult:
    """Bounded exact bisection with verified finite-box monotonicity.

    MAX_ITERATIONS is an honest incomplete result. Returned evaluations include
    endpoint and reference evaluations, making conservation auditable throughout.
    The source cap prevents an accidentally unbounded exact-rational solve.
    """
    tolerance = as_fraction(temperature_tolerance)
    if tolerance <= 0:
        raise ValueError("temperature_tolerance must be positive.")
    if not isinstance(max_iterations, int) or not 0 <= max_iterations <= 4096:
        raise ValueError("max_iterations must be an integer in [0, 4096].")
    slope = problem.derivative_lower_bound()
    if slope <= 0:
        raise ValueError("The finite-box EOS does not have a positive verified slope.")

    left, right = problem.temperature_lower, problem.temperature_upper
    left_state, right_state = problem.evaluate(left), problem.evaluate(right)
    trace = [left_state, right_state]
    if left_state.eos_residual > 0 or right_state.eos_residual < 0:
        raise ValueError("EOS endpoint signs do not bracket a root.")

    def result(state: BoundaryState, bracket: tuple[Fraction, Fraction],
               iterations: int) -> BisectionResult:
        lower, upper = bracket
        interval_bound = max(state.temperature - lower, upper - state.temperature)
        error = min(abs(state.eos_residual) / slope, interval_bound)
        converged = error <= tolerance
        status = ("EXACT_ROOT" if state.eos_residual == 0 else
                  "CERTIFIED_INTERVAL" if converged else "MAX_ITERATIONS")
        return BisectionResult(status, converged, state, bracket, slope, error,
                               iterations, tuple(trace))

    # This fixed-reference evaluation preserves exact h=0 identity, even when
    # the old physical temperature is not the midpoint of the new bracket.
    initial = problem.evaluate(problem.reference_temperature)
    trace.append(initial)
    current = result(initial, (left, right), 0)
    if current.converged:
        return current
    for boundary in (left_state, right_state):
        if boundary.eos_residual == 0:
            return result(boundary, (left, right), 0)

    for iteration in range(1, max_iterations + 1):
        state = problem.evaluate((left + right) / 2)
        trace.append(state)
        current = result(state, (left, right), iteration)
        if current.converged:
            return current
        if state.eos_residual < 0:
            left = state.temperature
        else:
            right = state.temperature
    return current


@dataclass(frozen=True)
class Atom:
    energy: Fraction
    count: Fraction

    def __post_init__(self) -> None:
        object.__setattr__(self, "energy", as_fraction(self.energy))
        object.__setattr__(self, "count", as_fraction(self.count))
        if self.energy < 0 or self.count < 0:
            raise ValueError("Atom energies and counts must be nonnegative.")


@dataclass(frozen=True)
class AtomicState:
    thermal_groups: int
    temperature: Fraction
    cutoff: Fraction
    thermal_count: Fraction
    thermal_energy: Fraction
    active_count: Fraction
    active_energy: Fraction
    threshold_consistent: bool


@dataclass(frozen=True)
class AtomicInventory:
    atoms: tuple[Atom, ...]
    base_count: Fraction
    base_energy: Fraction
    nucleus_count: Fraction
    k_b: Fraction
    chi: Fraction
    _prefix_count: tuple[Fraction, ...] = field(init=False, repr=False)
    _prefix_energy: tuple[Fraction, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        for name in ("base_count", "base_energy", "nucleus_count", "k_b", "chi"):
            object.__setattr__(self, name, as_fraction(getattr(self, name)))
        if self.nucleus_count <= 0 or self.base_count < self.nucleus_count:
            raise ValueError("The positive base count must contain all nuclei.")
        if self.base_energy <= 0 or self.k_b <= 0 or self.chi <= 0:
            raise ValueError("The atomic positive-temperature branch requires U_B,k_b,chi>0.")
        groups: dict[Fraction, Fraction] = {}
        for atom in self.atoms:
            if not isinstance(atom, Atom):
                raise TypeError("atoms must contain Atom instances.")
            if atom.count:
                groups[atom.energy] = groups.get(atom.energy, Fraction(0)) + atom.count
        atoms = tuple(Atom(energy, count) for energy, count in sorted(groups.items()))
        object.__setattr__(self, "atoms", atoms)
        counts, energies = [Fraction(0)], [Fraction(0)]
        for atom in atoms:
            counts.append(counts[-1] + atom.count)
            energies.append(energies[-1] + atom.energy * atom.count)
        object.__setattr__(self, "_prefix_count", tuple(counts))
        object.__setattr__(self, "_prefix_energy", tuple(energies))

    @property
    def c_v(self) -> Fraction:
        return Fraction(3, 2) * self.k_b

    @property
    def alpha(self) -> Fraction:
        return self.chi * self.k_b

    @property
    def common_count(self) -> Fraction:
        return self.base_count + self._prefix_count[-1]

    @property
    def common_energy(self) -> Fraction:
        return self.base_energy + self._prefix_energy[-1]

    def state(self, thermal_groups: int) -> AtomicState:
        if (not isinstance(thermal_groups, int)
                or not 0 <= thermal_groups <= len(self.atoms)):
            raise ValueError("thermal_groups must index the distinct sorted energy groups.")
        count = self.base_count + self._prefix_count[thermal_groups]
        energy = self.base_energy + self._prefix_energy[thermal_groups]
        temperature = energy / (self.c_v * count)
        cutoff = self.alpha * temperature
        lower_ok = (thermal_groups == 0
                    or self.atoms[thermal_groups - 1].energy <= cutoff)
        upper_ok = (thermal_groups == len(self.atoms)
                    or cutoff < self.atoms[thermal_groups].energy)
        return AtomicState(
            thermal_groups, temperature, cutoff, count, energy,
            self._prefix_count[-1] - self._prefix_count[thermal_groups],
            self._prefix_energy[-1] - self._prefix_energy[thermal_groups],
            lower_ok and upper_ok,
        )


@dataclass(frozen=True)
class AtomicScanResult:
    inventory: AtomicInventory
    state: AtomicState
    path: tuple[AtomicState, ...]
    crossing_count: int
    direction: str
    status: str = "BRANCH_CONTINUATION_COMPLETE"
    scope: str = "Fixed atom spectrum and base count; only base energy changes."


def enumerate_atomic_roots(inventory: AtomicInventory) -> tuple[AtomicState, ...]:
    """Return every threshold-consistent branch, without choosing among roots."""
    candidates = (inventory.state(index) for index in range(len(inventory.atoms) + 1))
    return tuple(state for state in candidates if state.threshold_consistent)


def construct_atomic_root(inventory: AtomicInventory) -> AtomicScanResult:
    """Finite existence construction for chi>=3/2, starting with no thermal atoms.

    This policy need not select the inherited branch. Use continuation below
    when h=0 identity relative to a previous consistent index is required.
    """
    if inventory.alpha < inventory.c_v:
        raise ValueError("The forward existence theorem requires chi>=3/2.")
    index = 0
    state = inventory.state(index)
    path = [state]
    while index < len(inventory.atoms) and inventory.atoms[index].energy <= state.cutoff:
        index += 1
        state = inventory.state(index)
        path.append(state)
    if not state.threshold_consistent:
        raise AssertionError("Finite forward construction failed its threshold contract.")
    return AtomicScanResult(inventory, state, tuple(path), len(path) - 1, "FORWARD_FROM_ZERO")


def continue_atomic_energy(
    reference: AtomicInventory,
    initial_thermal_groups: int,
    delta_base_energy: Exact,
) -> AtomicScanResult:
    """Deterministic finite scan from an inherited consistent atomic branch.

    Thermal owns equality. No physical state is clipped, and all path states use
    one new base energy and the same canonical prefix moments.
    """
    if reference.alpha < reference.c_v:
        raise ValueError("The continuation theorem requires chi>=3/2.")
    original = reference.state(initial_thermal_groups)
    if not original.threshold_consistent:
        raise ValueError("The inherited atomic branch violates threshold ownership.")
    delta = as_fraction(delta_base_energy)
    inventory = replace(reference, base_energy=reference.base_energy + delta)
    index = initial_thermal_groups
    state = inventory.state(index)
    path = [state]
    if delta >= 0:
        direction = "HEATING" if delta > 0 else "ZERO_STEP"
        while index < len(inventory.atoms) and inventory.atoms[index].energy <= state.cutoff:
            index += 1
            state = inventory.state(index)
            path.append(state)
    else:
        direction = "COOLING"
        while index > 0 and inventory.atoms[index - 1].energy > state.cutoff:
            index -= 1
            state = inventory.state(index)
            path.append(state)
    if not state.threshold_consistent:
        raise AssertionError("Atomic continuation failed its threshold contract.")
    return AtomicScanResult(inventory, state, tuple(path), len(path) - 1, direction)

