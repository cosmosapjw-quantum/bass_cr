"""Conservative angular marginal of an isotropic massive-electron event yield.

Energies are kinetic eV; momentum outputs are p*c in eV. Input u = gamma*beta
is dimensionless. This is a per-event measure, not a decay rate or an IGM
thermalization prescription. See source_ledger.py for explicit rate clocks.

For each rest-energy atom, K_bath = A + B*mu and mu is uniform on [-1, 1].
The angular integral is analytic. Finite rest atoms are exact inputs; a
quadrature representation of a continuous spectrum has a separate error.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import copysign, fsum, hypot, inf, isfinite, sqrt
from typing import Sequence

# Same electron rest-energy convention used in the C23A illustrative spectra.
# This is a declared model constant, not a new measurement of m_e.
ELECTRON_REST_EV = 510998.95


def finite_nonnegative(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(name + " must be a real numeric value, not bool")
    value = float(value)
    if not isfinite(value) or value < 0:
        raise ValueError(name + " must be finite and nonnegative")
    return value


@dataclass(frozen=True)
class Boost:
    """Nonnegative speed magnitude; parent direction is a separate contract."""
    u: float

    def __post_init__(self):
        object.__setattr__(self, "u", finite_nonnegative(self.u, "gamma*beta"))

    @property
    def gamma(self) -> float:
        return hypot(1.0, self.u)

    @property
    def gamma_minus_one(self) -> float:
        return self.u * (self.u / (self.gamma + 1.0))

    @property
    def beta(self) -> float:
        return self.u / self.gamma


@dataclass(frozen=True)
class Moments:
    number: float
    kinetic_ev: float
    total_ev: float
    parallel_pc_ev: float

    def scaled(self, factor: float) -> "Moments":
        factor = finite_nonnegative(factor, "measure weight")
        return Moments(*(factor * value for value in self.as_tuple()))

    def as_tuple(self) -> tuple[float, float, float, float]:
        return self.number, self.kinetic_ev, self.total_ev, self.parallel_pc_ev


def sum_moments(items: Sequence[Moments]) -> Moments:
    return Moments(*(fsum(row.as_tuple()[i] for row in items) for i in range(4)))


ZERO = Moments(0.0, 0.0, 0.0, 0.0)


@dataclass(frozen=True)
class AngularBox:
    rest_kinetic_ev: float
    rest_mass_ev: float
    boost: Boost
    center_ev: float
    half_width_ev: float
    lower_ev: float
    upper_ev: float
    rest_pc_ev: float

    @classmethod
    def from_energy(cls, kinetic_ev: float, boost: Boost,
                    rest_mass_ev: float = ELECTRON_REST_EV) -> "AngularBox":
        k = finite_nonnegative(kinetic_ev, "rest kinetic energy")
        m = finite_nonnegative(rest_mass_ev, "rest mass energy")
        if m == 0:
            raise ValueError("this massive-particle kernel requires m*c^2 > 0")
        if not isinstance(boost, Boost):
            raise ValueError("explicit Boost object required")
        g, dm, u = boost.gamma, boost.gamma_minus_one, boost.u
        q = sqrt(k) * sqrt(k + 2*m)
        a, b = fsum((g*k, dm*m)), u*q
        high = a+b
        if not all(isfinite(v) for v in (q, a, b, high, 2*b)):
            raise ValueError("energy/boost combination overflows finite FP64")
        if b == 0:
            low = high = a
        else:
            # Exact identity: (A-B)(A+B) = (K-(gamma-1)*M)^2.
            # This avoids catastrophic subtraction when the backward electron
            # is nearly at rest in the bath frame. No negative-value clipping.
            d = k - dm*m
            low = d * (d/high)
        return cls(k, m, boost, a, b, low, high, q)

    def full(self) -> Moments:
        return Moments(1.0, self.center_ev,
                       fsum((self.center_ev, self.rest_mass_ev)),
                       self.boost.u * (self.rest_kinetic_ev+self.rest_mass_ev))

    def interval(self, low_ev: float, high_ev: float, *,
                 lower_closed: bool = True, upper_closed: bool = False) -> Moments:
        """Unnormalized moments on a declared interval.

        End-point ownership matters only for Dirac atoms (K=0 or u=0).
        Positive-width boxes are absolutely continuous. An infinity upper
        bound is allowed; negative/nonfinite lower edges are rejected.
        """
        lo = finite_nonnegative(low_ev, "interval lower edge")
        hi = float(high_ev)
        if hi <= lo or (not isfinite(hi) and hi != inf):
            raise ValueError("interval needs finite ordered edges or upper +inf")
        if self.half_width_ev == 0:
            x = self.center_ev
            inside = (x > lo or (lower_closed and x == lo)) and (
                x < hi or (upper_closed and x == hi))
            return self.full() if inside else ZERO
        if hi <= self.lower_ev or lo >= self.upper_ev:
            return ZERO
        if lo <= self.lower_ev and hi >= self.upper_ev:
            return self.full()
        a, b = max(lo, self.lower_ev), min(hi, self.upper_ev)
        width = 2*self.half_width_ev
        delta = b-a
        if delta <= 0:
            raise ArithmeticError("overlap interval collapsed in FP64")
        fraction = delta/width
        middle = a+delta/2
        kinetic = fraction*middle
        # Use the endpoint distance nearest to the clipped interval's midpoint.
        # This protects a small fraction near the stable lower endpoint.
        if middle <= self.center_ev:
            mu_mid = -1 + (middle-self.lower_ev)/self.half_width_ev
        else:
            mu_mid = 1 - (self.upper_ev-middle)/self.half_width_ev
        pc_mid = fsum((self.boost.u*(self.rest_kinetic_ev+self.rest_mass_ev),
                       self.boost.gamma*self.rest_pc_ev*mu_mid))
        return Moments(fraction, kinetic,
                       fsum((kinetic, fraction*self.rest_mass_ev)),
                       fraction*pc_mid)


@dataclass(frozen=True)
class ElectronMeasure:
    """Finite positive atoms with explicit frame and measure normalization."""
    kinetic_ev: tuple[float, ...]
    number: tuple[float, ...]
    frame: str
    units: str
    identity: str

    def __post_init__(self):
        if len(self.kinetic_ev) == 0 or len(self.kinetic_ev) != len(self.number):
            raise ValueError("a nonempty matching positive atomic measure is required")
        if self.frame not in ("parent_rest", "bath"):
            raise ValueError("source frame must be parent_rest or bath")
        if self.units not in ("electrons_per_event", "electrons_per_target_per_second"):
            raise ValueError("unknown spectral measure normalization")
        if not isinstance(self.identity, str) or not self.identity.strip():
            raise ValueError("source identity is required")
        object.__setattr__(self, "kinetic_ev", tuple(finite_nonnegative(x, "atom energy") for x in self.kinetic_ev))
        object.__setattr__(self, "number", tuple(finite_nonnegative(x, "atom number") for x in self.number))
        if not isfinite(fsum(self.number)):
            raise ValueError("measure sum overflows")

    def require_boost(self, boost: Boost):
        if self.frame == "bath" and boost.u != 0:
            raise ValueError("bath-frame sources cannot receive a parent-rest boost")

    def total(self, boost: Boost) -> Moments:
        self.require_boost(boost)
        return sum_moments([AngularBox.from_energy(k, boost).full().scaled(w)
                            for k, w in zip(self.kinetic_ev, self.number)])

    def interval(self, boost: Boost, low_ev: float, high_ev: float, **kwargs) -> Moments:
        self.require_boost(boost)
        return sum_moments([AngularBox.from_energy(k, boost).interval(
            low_ev, high_ev, **kwargs).scaled(w)
            for k, w in zip(self.kinetic_ev, self.number)])

    def finite_domain(self, boost: Boost, lower_ev: float, upper_ev: float) -> dict[str, Moments]:
        """Partition all electrons without dropping unresolved energy tails."""
        if not 0 < lower_ev < upper_ev < inf:
            raise ValueError("finite response domain must satisfy 0 < L < U")
        return {
            "below": self.interval(boost, 0, lower_ev),
            "covered": self.interval(boost, lower_ev, upper_ev, upper_closed=True),
            "above": self.interval(boost, upper_ev, inf, lower_closed=False),
            "all": self.total(boost),
        }
