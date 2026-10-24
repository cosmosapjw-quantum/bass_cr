"""C22D finite-source H1 total electron-impact ionization coefficient.

Source: exact CCC 1S->TICS 87-row table in a0**2, incident energies in eV.
The default is the positive piecewise-linear table model on [13.6058,968.61].
No physical extrapolation, isotope substitution, or omitted-tail bound is made.
The optional first-gap exponent is an explicitly different sensitivity model.
No temperature table or rate interpolation is introduced.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
import numpy as np
from scipy.special import gammainc, gamma

EV_J = 1.602176634e-19
KB_J_K = 1.380649e-23
KB_EV_K = KB_J_K / EV_J
ME_KG = 9.1093837139e-31
A0_M = 5.29177210544e-11
K_CM3_S = 1e6 * A0_M**2 * math.sqrt(8 * EV_J / (math.pi * ME_KG))
THRESHOLD_EV = 13.6058
EMAX_EV = 968.61
FIRST_POSITIVE_EV = 13.64
SOURCE_SHA256 = "7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae"
NUMERICAL_T_DOMAIN_K = (1.0, 1e8)
ACTIVE_T_DOMAIN_K = (3.0, 20000.0)
PROCESS = "h1_ground_finite_source_collisional_ionization"
LOG_MIN_SUBNORMAL = math.log(float(np.nextafter(0., 1.)))


def _immutable(values):
    a = np.asarray(values, dtype=np.float64)
    return np.frombuffer(a.tobytes(), dtype=np.float64).reshape(a.shape)


def _moments(y):
    """Positive integrals J_n(y)=int_0^1 t^n exp(-yt)dt, n=0,1,2.

    Same algebra/branch as frozen C22C; the source interval arrays differ.
    No C22C verification is rerun by using this already established identity.
    """
    y = np.asarray(y, dtype=float)
    out = np.empty((3, len(y)))
    small = y <= .5
    for n in range(3):
        term = np.ones(np.count_nonzero(small))
        value = term / (n + 1)
        for k in range(1, 19):
            term *= -y[small] / k
            value += term / (n + k + 1)
        out[n, small] = value
        z = y[~small]
        out[n, ~small] = math.factorial(n) * gammainc(n + 1, z) / z**(n + 1)
    return out


@dataclass(frozen=True)
class CIRate:
    temperature_K: float
    q_cm3_s: float
    log10_q_cm3_s: float
    float64_underflow: bool
    first_gap_power: float
    finite_source_only: bool = True


class CCCFiniteH1CI:
    def __init__(self, path=None):
        path = Path(path) if path is not None else Path(__file__).parent / "sources" / "CCC_TICS_1S.txt"
        blob = path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != SOURCE_SHA256:
            raise ValueError("CI_SOURCE_IDENTITY_MISMATCH")
        rows = []
        for line in blob.decode("utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                fields = line.split()
                rows.append((float(fields[0]), float(fields[1])))
        rows = np.asarray(rows, dtype=float)
        if rows.shape != (87, 2) or np.any(np.diff(rows[:, 0]) <= 0) or np.any(rows[:, 1] < 0):
            raise ValueError("INVALID_CI_SOURCE_TABLE")
        if tuple(rows[0]) != (THRESHOLD_EV, 0.) or rows[1, 0] != FIRST_POSITIVE_EV or rows[-1, 0] != EMAX_EV:
            raise ValueError("CI_SOURCE_ENDPOINT_MISMATCH")
        self.energy_eV = _immutable(rows[:, 0])
        self.sigma_a0sq = _immutable(rows[:, 1])
        self.left = _immutable(rows[:-1, 0])
        self.width = _immutable(np.diff(rows[:, 0]))
        self.sigma_l = _immutable(rows[:-1, 1])
        self.sigma_r = _immutable(rows[1:, 1])
        self.source_sha256 = SOURCE_SHA256

    @staticmethod
    def _temperature(temperature_K):
        if isinstance(temperature_K, (bool, np.bool_)):
            raise ValueError("CI_TEMPERATURE_MUST_NOT_BE_BOOL")
        t = float(temperature_K)
        if not math.isfinite(t) or not NUMERICAL_T_DOMAIN_K[0] <= t <= NUMERICAL_T_DOMAIN_K[1]:
            raise ValueError("CI_NUMERICAL_T_DOMAIN")
        return t

    def interval_scaled_integrals(self, temperature_K):
        """Contributions to int sigma*E*exp[-(E-Eth)/theta]dE."""
        t = self._temperature(temperature_K)
        theta = KB_EV_K * t
        j0, j1, j2 = _moments(self.width / theta)
        wl = self.left * (j0-j1) + self.width * (j1-j2)
        wr = self.left * j1 + self.width * j2
        ans = self.width * np.exp(-(self.left-THRESHOLD_EV)/theta) * (self.sigma_l*wl+self.sigma_r*wr)
        if np.any(ans < 0) or not np.all(np.isfinite(ans)):
            raise ArithmeticError("CI_NONPOSITIVE_OR_NONFINITE_MOMENT")
        return ans

    def gap_scaled_integral(self, temperature_K, power=1.127):
        """Only E0..E1: sigma=sigma1*((E-E0)/(E1-E0))**power."""
        t = self._temperature(temperature_K)
        if isinstance(power, (bool, np.bool_)):
            raise ValueError("FIRST_GAP_POWER_MUST_NOT_BE_BOOL")
        p = float(power)
        if not math.isfinite(p) or p <= 0:
            raise ValueError("FIRST_GAP_POWER_MUST_BE_POSITIVE")
        theta = KB_EV_K*t
        h, s1 = self.width[0], self.sigma_r[0]
        y = h/theta
        g1 = gamma(p+1)*gammainc(p+1,y)
        g2 = gamma(p+2)*gammainc(p+2,y)
        value = s1/h**p * (THRESHOLD_EV*theta**(p+1)*g1+theta**(p+2)*g2)
        if not np.isfinite(value) or value <= 0:
            raise ArithmeticError("CI_INVALID_FIRST_GAP_MOMENT")
        return float(value)

    def evaluate(self, temperature_K, *, first_gap_power=1.0,
                 species="H1", full_physical_rate=False):
        if species != "H1":
            raise ValueError("CI_SPECIES_COVERAGE_UNAVAILABLE")
        if not isinstance(full_physical_rate, (bool, np.bool_)):
            raise ValueError("FULL_PHYSICAL_RATE_FLAG_MUST_BE_BOOL")
        if full_physical_rate:
            raise ValueError("CI_FULL_PHYSICAL_RATE_UNAVAILABLE")
        t = self._temperature(temperature_K)
        if isinstance(first_gap_power, (bool, np.bool_)):
            raise ValueError("FIRST_GAP_POWER_MUST_NOT_BE_BOOL")
        p = float(first_gap_power)
        if not math.isfinite(p) or p <= 0:
            raise ValueError("FIRST_GAP_POWER_MUST_BE_POSITIVE")
        values = self.interval_scaled_integrals(t)
        if p != 1.0:
            values[0] = self.gap_scaled_integral(t, p)
        scaled = float(np.sum(values))
        if not math.isfinite(scaled) or scaled <= 0:
            raise ArithmeticError("CI_NONPOSITIVE_CORE_MOMENT")
        theta = KB_EV_K*t
        logq = math.log(K_CM3_S)-1.5*math.log(theta)-THRESHOLD_EV/theta+math.log(scaled)
        q = math.exp(logq)
        return CIRate(t, q, logq/math.log(10.), q == 0., p)

    def q_cm3_s(self, temperature_K):
        return self.evaluate(temperature_K).q_cm3_s

    def log10_conditional_tail_per_a0sq_cap(self, temperature_K):
        """Coefficient only; the premise sigma(E)<=cap for E>Emax is OPEN."""
        theta = KB_EV_K*self._temperature(temperature_K)
        return (math.log(K_CM3_S)-.5*math.log(theta)+math.log(EMAX_EV+theta)-EMAX_EV/theta)/math.log(10.)

    def conditional_tail(self, temperature_K, *, assumed_sigma_cap_a0sq):
        cap = float(assumed_sigma_cap_a0sq)
        if not math.isfinite(cap) or cap <= 0:
            raise ValueError("EXPLICIT_POSITIVE_HYPOTHETICAL_CAP_REQUIRED")
        return {"log10_conditional_q_tail_cap_cm3_s": self.log10_conditional_tail_per_a0sq_cap(temperature_K)+math.log10(cap),
                "assumption": "sigma_a0sq(E)<=assumed_cap for all E>968.61eV; NOT established by finite source table",
                "assumed_sigma_cap_a0sq": cap, "physical_tail_bound_established": False}

    def coverage(self):
        return {"species": "H1", "initial_state": "1S ground", "process": PROCESS,
                "table_sha256": SOURCE_SHA256, "rows": 87,
                "incident_energy_eV": [THRESHOLD_EV, EMAX_EV],
                "first_positive_eV": FIRST_POSITIVE_EV,
                "sigma_unit": "a0^2, no pi or multiplicity factor",
                "default_interpolation": "piecewise linear in incident E and sigma",
                "numerical_T_K": list(NUMERICAL_T_DOMAIN_K),
                "common_model_active_T_K": list(ACTIVE_T_DOMAIN_K),
                "physical_interpolation_error": "OPEN", "physical_omitted_tail": "OPEN",
                "physical_sigma_cap": None, "global_error_bound": None,
                "unsupported_species": "UNAVAILABLE, not zero-filled",
                "first_gap_power_variant": "sensitivity model, not physical error estimate"}
