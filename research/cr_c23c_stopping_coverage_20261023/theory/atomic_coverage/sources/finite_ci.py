"""Explicit finite-window electron-impact CI operators for PHYS81.

The original C22D provider remains H1-specific and byte-identical in vendor/.
This module reuses its J0, J1 and J2 integral kernel for caller-supplied PL
tables in cm^2.  It does not promote those tables to complete physical rates.
The chemical ionization defect is a separate input from the source window.

For a temperature-independent window and Maxwellian electrons,
    K = C theta^(-3/2) integral E sigma(E) exp(-E/theta) dE,
    dK/dT = K * (mean_incoming_E/theta - 3/2) / T,
with theta = k_B T in eV and C = 100 sqrt(8 eV_J / (pi m_e)).
Outside-window zero is the definition of the selected finite operator.
It is not a physical omitted-tail or source-interpolation error certificate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import math
from numbers import Real
from pathlib import Path

import numpy as np
from scipy.special import gammainc

if __package__:
    from .vendor.ci_finite_c22d import (
        A0_M, EV_J, KB_EV_K, ME_KG, _moments as _c22d_moments,
    )
else:
    from vendor.ci_finite_c22d import (
        A0_M, EV_J, KB_EV_K, ME_KG, _moments as _c22d_moments,
    )


NUMERICAL_T_DOMAIN_K = (255.0, 50000.0)
MAXWELL_CM3_S_PER_CM2 = 100.0 * math.sqrt(8.0 * EV_J / (math.pi * ME_KG))
C22D_H_TABLE_SHA256 = "7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae"


def _real_scalar(value, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{name}_MUST_BE_REAL_NOT_BOOL")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name}_MUST_BE_FINITE")
    return number


def _immutable(values: np.ndarray) -> np.ndarray:
    """Copy into an immutable bytes-backed binary64 array."""
    array = np.asarray(values, dtype=np.float64)
    return np.frombuffer(array.tobytes(), dtype=np.float64).reshape(array.shape)


def _real_vector(values, name: str) -> np.ndarray:
    # Inspect before coercion so a bool embedded in a numeric list is rejected.
    raw = np.asarray(values, dtype=object)
    if raw.ndim != 1 or raw.size < 2:
        raise ValueError(f"{name}_MUST_BE_VECTOR_WITH_AT_LEAST_TWO_POINTS")
    if any(isinstance(v, (bool, np.bool_)) or not isinstance(v, Real) for v in raw):
        raise ValueError(f"{name}_MUST_CONTAIN_REAL_NUMBERS_NOT_BOOL")
    array = np.asarray(raw, dtype=np.float64)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name}_MUST_BE_FINITE")
    return _immutable(array)


def _moment3(y: np.ndarray) -> np.ndarray:
    """J3(y) = integral_0^1 t^3 exp(-y*t) dt, y >= 0.

    The analytic positive integral is 6*P(4,y)/y^4.  At small y the
    removable singularity is evaluated by its Taylor series, using the
    same cutoff and orders 0..18 as the retained C22D J0..2 implementation.
    This is an analytic integral evaluated in binary64, not interval proof.
    """
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 1 or not np.all(np.isfinite(y)) or np.any(y < 0.0):
        raise ValueError("J3_NONNEGATIVE_FINITE_VECTOR_REQUIRED")
    out = np.empty_like(y)
    small = y <= 0.5
    term = np.ones(np.count_nonzero(small), dtype=np.float64)
    value = term / 4.0
    for k in range(1, 19):
        term *= -y[small] / k
        value += term / (k + 4)
    out[small] = value
    z = y[~small]
    # Sequential division avoids forming a potentially overflowing z**4.
    out[~small] = (((6.0 * gammainc(4.0, z) / z) / z) / z) / z
    if not np.all(np.isfinite(out)) or np.any(out < 0.0):
        raise ArithmeticError("J3_NONFINITE_OR_NEGATIVE")
    return out


@dataclass(frozen=True, slots=True)
class FiniteCIRate:
    """One finite-operator evaluation; logK is the natural logarithm."""

    temperature_K: float
    K_cm3_s: float
    logK_cm3_s: float
    mean_incoming_eV: float
    dK_dT_cm3_s_K: float
    dlogK_dT_per_K: float
    float64_underflow: bool
    species: str
    source_identity: str
    Ichemical_eV: float
    lower_eV: float
    upper_eV: float
    finite_window_only: bool = True

    @property
    def log10K_cm3_s(self) -> float:
        return self.logK_cm3_s / math.log(10.0)


@dataclass(frozen=True, slots=True, eq=False)
class FiniteWindowCI:
    """An immutable, explicitly sourced finite PL CI model.

    energy_eV and sigma_cm2 must describe the entire selected window, with
    their endpoints equal to lower_eV and upper_eV.  Cross sections are
    nonnegative, with at least one positive value; a zero threshold sample
    is allowed.  No extrapolation, hidden isotope substitution, or physical
    full-rate admission is supplied.  Ichemical_eV sets event heat loss;
    it is not replaced by the incident-energy mean or the window floor.
    """

    species: str
    energy_eV: np.ndarray
    sigma_cm2: np.ndarray
    source_identity: str
    Ichemical_eV: float
    lower_eV: float
    upper_eV: float
    _left: np.ndarray = field(init=False, repr=False)
    _width: np.ndarray = field(init=False, repr=False)
    _sigma_l: np.ndarray = field(init=False, repr=False)
    _sigma_r: np.ndarray = field(init=False, repr=False)
    _sigma_scale_cm2: float = field(init=False, repr=False)
    _reference_eV: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        for value, name in ((self.species, "SPECIES"), (self.source_identity, "SOURCE_IDENTITY")):
            if not isinstance(value, str) or not value.strip() or value != value.strip():
                raise ValueError(f"{name}_NONEMPTY_STRIPPED_STRING_REQUIRED")
        energy = _real_vector(self.energy_eV, "ENERGY_EV")
        sigma = _real_vector(self.sigma_cm2, "SIGMA_CM2")
        if energy.shape != sigma.shape:
            raise ValueError("ENERGY_SIGMA_SHAPE_MISMATCH")
        chemical = _real_scalar(self.Ichemical_eV, "ICHEMICAL_EV")
        lower = _real_scalar(self.lower_eV, "LOWER_EV")
        upper = _real_scalar(self.upper_eV, "UPPER_EV")
        if chemical <= 0.0:
            raise ValueError("ICHEMICAL_EV_MUST_BE_POSITIVE")
        if lower < chemical or upper <= lower:
            raise ValueError("WINDOW_REQUIRES_ICHEMICAL_LE_LOWER_LT_UPPER")
        if energy[0] != lower or energy[-1] != upper:
            raise ValueError("SOURCE_ENDPOINTS_MUST_EQUAL_SELECTED_WINDOW")
        widths = np.diff(energy)
        if not np.all(widths > 0.0):
            raise ValueError("ENERGY_EV_MUST_BE_STRICTLY_INCREASING")
        if np.any(sigma < 0.0) or not np.any(sigma > 0.0):
            raise ValueError("SIGMA_CM2_MUST_BE_NONNEGATIVE_AND_NOT_ALL_ZERO")

        # Removing zero-zero cells is exact for this PL operator.  Its first
        # nonzero cell is the exponential reference, including zero prefixes.
        active = (sigma[:-1] > 0.0) | (sigma[1:] > 0.0)
        left = energy[:-1][active]
        scale = float(np.max(sigma))
        object.__setattr__(self, "energy_eV", energy)
        object.__setattr__(self, "sigma_cm2", sigma)
        object.__setattr__(self, "Ichemical_eV", chemical)
        object.__setattr__(self, "lower_eV", lower)
        object.__setattr__(self, "upper_eV", upper)
        object.__setattr__(self, "_left", _immutable(left))
        object.__setattr__(self, "_width", _immutable(widths[active]))
        # Factoring one common positive cross-section scale changes neither
        # the rate nor its energy mean and avoids unnecessary overflow.
        object.__setattr__(self, "_sigma_l", _immutable(sigma[:-1][active] / scale))
        object.__setattr__(self, "_sigma_r", _immutable(sigma[1:][active] / scale))
        object.__setattr__(self, "_sigma_scale_cm2", scale)
        object.__setattr__(self, "_reference_eV", float(left[0]))

    @staticmethod
    def _temperature(temperature_K) -> float:
        temperature = _real_scalar(temperature_K, "TEMPERATURE_K")
        if not NUMERICAL_T_DOMAIN_K[0] <= temperature <= NUMERICAL_T_DOMAIN_K[1]:
            raise ValueError("FINITE_CI_TEMPERATURE_OUTSIDE_255_TO_50000_K")
        return temperature

    def evaluate(self, temperature_K, *, full_physical_rate: bool = False) -> FiniteCIRate:
        if not isinstance(full_physical_rate, (bool, np.bool_)):
            raise ValueError("FULL_PHYSICAL_RATE_FLAG_MUST_BE_BOOL")
        if full_physical_rate:
            raise ValueError("FULL_PHYSICAL_CI_RATE_UNAVAILABLE")
        temperature = self._temperature(temperature_K)
        theta = KB_EV_K * temperature
        left, width = self._left, self._width
        try:
            with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
                y = width / theta
                if not np.all(np.isfinite(y)):
                    raise ArithmeticError("FINITE_CI_INTERVAL_SCALE_OVERFLOW")
                j0, j1, j2 = _c22d_moments(y)
                j3 = _moment3(y)
                d01, d12, d23 = j0 - j1, j1 - j2, j2 - j3
                if any(np.any(x < 0.0) for x in (d01, d12, d23)):
                    raise ArithmeticError("FINITE_CI_ENDPOINT_MOMENT_NEGATIVE")
                first_l = left * d01 + width * d12
                first_r = left * j1 + width * j2
                second_l = left**2 * d01 + 2.0 * left * width * d12 + width**2 * d23
                second_r = left**2 * j1 + 2.0 * left * width * j2 + width**2 * j3
                weight = width * np.exp(-(left - self._reference_eV) / theta)
                first_cells = weight * (self._sigma_l * first_l + self._sigma_r * first_r)
                second_cells = weight * (self._sigma_l * second_l + self._sigma_r * second_r)
                first = float(np.sum(first_cells))
                second = float(np.sum(second_cells))
        except FloatingPointError as exc:
            raise ArithmeticError("FINITE_CI_MOMENT_ARITHMETIC_OUT_OF_RANGE") from exc
        if not all(math.isfinite(x) and x > 0.0 for x in (first, second)):
            raise ArithmeticError("FINITE_CI_NONPOSITIVE_OR_NONFINITE_SCALED_MOMENT")
        mean = second / first
        if not math.isfinite(mean) or not self.lower_eV <= mean <= self.upper_eV:
            raise ArithmeticError("FINITE_CI_MEAN_OUTSIDE_SOURCE_WINDOW")
        logK = (math.log(MAXWELL_CM3_S_PER_CM2) + math.log(self._sigma_scale_cm2)
                - 1.5 * math.log(theta) - self._reference_eV / theta + math.log(first))
        dlogK = (mean / theta - 1.5) / temperature
        if not math.isfinite(logK) or not math.isfinite(dlogK):
            raise ArithmeticError("FINITE_CI_NONFINITE_LOG_RATE_OR_DERIVATIVE")
        try:
            rate = math.exp(logK)
            # A derivative can remain representable when the rate underflows.
            derivative = (0.0 if dlogK == 0.0 else
                          math.copysign(math.exp(logK + math.log(abs(dlogK))), dlogK))
        except OverflowError as exc:
            raise ArithmeticError("FINITE_CI_RATE_OR_DERIVATIVE_OVERFLOW") from exc
        return FiniteCIRate(
            temperature_K=temperature,
            K_cm3_s=rate,
            logK_cm3_s=logK,
            mean_incoming_eV=mean,
            dK_dT_cm3_s_K=derivative,
            dlogK_dT_per_K=dlogK,
            float64_underflow=(rate == 0.0),
            species=self.species,
            source_identity=self.source_identity,
            Ichemical_eV=self.Ichemical_eV,
            lower_eV=self.lower_eV,
            upper_eV=self.upper_eV,
        )

    def coverage(self) -> dict:
        return {
            "species": self.species,
            "source_identity": self.source_identity,
            "source_rows": int(self.energy_eV.size),
            "sigma_unit": "cm^2",
            "electron_energy_window_eV": [self.lower_eV, self.upper_eV],
            "chemical_ionization_potential_eV": self.Ichemical_eV,
            "temperature_domain_K": list(NUMERICAL_T_DOMAIN_K),
            "interpolation": "piecewise linear in incident E and sigma",
            "outside_window": "zero by selected finite-operator definition only",
            "physical_interpolation_error": "OPEN",
            "physical_omitted_support": "OPEN; not asserted zero",
            "full_physical_rate_available": False,
            "isotope_substitution": "none; caller must bind the named source contract",
            "thermal_loss_per_event_eV": self.Ichemical_eV,
            "mean_incoming_energy_is_additional_heat_loss": False,
        }

    @classmethod
    def from_c22d_hydrogen(cls, *, Ichemical_eV: float) -> "FiniteWindowCI":
        """Load the pinned H1-only table and explicitly convert a0^2 to cm^2."""
        path = Path(__file__).parent / "vendor" / "CCC_TICS_1S.txt"
        blob = path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != C22D_H_TABLE_SHA256:
            raise ValueError("C22D_H_SOURCE_IDENTITY_MISMATCH")
        rows = []
        for raw in blob.decode("utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#"):
                fields = line.split()
                rows.append((float(fields[0]), float(fields[1])))
        data = np.asarray(rows, dtype=np.float64)
        if data.shape != (87, 2):
            raise ValueError("C22D_H_SOURCE_ROW_COUNT_MISMATCH")
        return cls(
            species="H1",
            energy_eV=data[:, 0],
            sigma_cm2=data[:, 1] * (100.0 * A0_M)**2,
            source_identity="sha256:" + C22D_H_TABLE_SHA256,
            Ichemical_eV=Ichemical_eV,
            lower_eV=13.6058,
            upper_eV=968.61,
        )
