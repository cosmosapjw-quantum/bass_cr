"""Finite CCC H1 1s->2s/2p Maxwellian contribution, not a full physical rate.

The exact source bytes define a piecewise-linear sigma(E) on the tabulated
interval only. Continuum interpolation error and the physical high-energy tail
remain separate unknowns. Log rates distinguish supported-source float64
underflow from absent data. No isotope or unprovided process is filled with zero.
"""
from __future__ import annotations
import hashlib
import math
from pathlib import Path
import numpy as np
from scipy.special import gammainc

EV_J = 1.602176634e-19
KB_J_K = 1.380649e-23
KB_EV_K = KB_J_K / EV_J
ME_KG = 9.1093837139e-31
A0_M = 5.29177210544e-11
K_CM3_S = 1e6 * A0_M**2 * math.sqrt(8 * EV_J / (math.pi * ME_KG))
DELTA_E_EV = 10.20435
E_MAX_EV = 968.6058
PROVIDER_T_DOMAIN_K = (1.0, 1e8)
ACTIVE_T_DOMAIN_K = (1.0, 20000.0)
PROCESS = "H1_n2_CCC_finite_table_excitation_escape"
TABLES = (
    ("CCC_2S_1S.txt", "e8e0092e7be97abe4a90ce100e3101d1f6f225eee2d4ad1ba740f57de819997b"),
    ("CCC_2P_1S.txt", "12cf46fa0904a5b227092a0a6a3ae6d8a20c041cf11c2981d3bb8bd1f6ac313d"),
)


def moments(y):
    """J_n(y)=integral_0^1 t^n exp(-yt) dt for n=0,1,2; y>0.

    A convergent series avoids cancellation for small y. Normalized incomplete
    gamma gives the positive large-y moments without subtracting close numbers.
    """
    y = np.asarray(y, dtype=float)
    if np.any(~np.isfinite(y)) or np.any(y <= 0):
        raise ValueError("MOMENT_ARGUMENT_MUST_BE_POSITIVE_FINITE")
    result = np.empty((3,) + y.shape)
    small = y <= .5
    for n in range(3):
        z = y[small]
        term = np.ones_like(z)
        value = term / (n + 1)
        for k in range(1, 19):
            term *= -z / k
            value += term / (n + k + 1)
        result[n, small] = value
        z = y[~small]
        result[n, ~small] = math.factorial(n) * gammainc(n + 1, z) / z**(n + 1)
    return result


class CCCFiniteExcitation:
    def __init__(self, source_dir=None):
        source_dir = Path(source_dir or Path(__file__).resolve().parent / "sources")
        tables = []
        for name, expected in TABLES:
            raw = (source_dir / name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError("CCC_SOURCE_BYTES_MISMATCH:" + name)
            rows = []
            for line in raw.decode("ascii").splitlines():
                parts = line.split()
                if len(parts) < 2:
                    continue
                try:
                    row = [float(parts[0]), float(parts[1])]
                except ValueError:
                    continue
                rows.append(row)
            table = np.asarray(rows)
            if (table.shape != (452, 2) or not np.isfinite(table).all()
                    or np.any(np.diff(table[:, 0]) <= 0) or np.any(table[:, 1] < 0)
                    or table[0, 0] != DELTA_E_EV or table[-1, 0] != E_MAX_EV
                    or table[0, 1] != 0):
                raise ValueError("CCC_TABLE_CONTRACT_VIOLATION:" + name)
            tables.append(table)
        if not np.array_equal(tables[0][:, 0], tables[1][:, 0]):
            raise ValueError("CCC_EXCITATION_ENERGY_GRIDS_DIFFER")
        self.energy = tables[0][:, 0].copy()
        self.sigma = np.stack([t[:, 1] for t in tables])
        self.left = self.energy[:-1]
        self.width = np.diff(self.energy)
        for arr in (self.energy, self.sigma, self.left, self.width):
            arr.flags.writeable = False

    def evaluate(self, temperature_K, *, species="H1", full_physical_rate=False):
        if species != "H1" or full_physical_rate:
            raise ValueError("ATOMIC_RATE_COVERAGE_UNAVAILABLE")
        if isinstance(temperature_K, (bool, np.bool_)):
            raise ValueError("INVALID_TEMPERATURE")
        temperature_K = float(temperature_K)
        if (not math.isfinite(temperature_K)
                or not PROVIDER_T_DOMAIN_K[0] <= temperature_K <= PROVIDER_T_DOMAIN_K[1]):
            raise ValueError("FINITE_PROVIDER_NUMERICAL_T_DOMAIN")
        theta = KB_EV_K * temperature_K
        j0, j1, j2 = moments(self.width / theta)
        # Positive endpoint basis: avoids cancellation on falling sigma segments.
        wl = self.left * (j0 - j1) + self.width * (j1 - j2)
        wr = self.left * j1 + self.width * j2
        if np.any(wl < 0) or np.any(wr < 0):
            raise ArithmeticError("NEGATIVE_EXACT_ENDPOINT_WEIGHT")
        weight = self.width * np.exp(-(self.left - DELTA_E_EV) / theta)
        scaled = np.sum(weight * (self.sigma[:, :-1] * wl + self.sigma[:, 1:] * wr), axis=1)
        if np.any(~np.isfinite(scaled)) or np.any(scaled <= 0):
            raise ArithmeticError("FINITE_CORE_POSITIVE_SCALED_INTEGRAL_LOST")
        logq = math.log(K_CM3_S) - 1.5 * math.log(theta) - DELTA_E_EV / theta + np.log(scaled)
        with np.errstate(under="ignore"):
            rates = np.exp(logq)
        return {"q_cm3_s": rates, "log10_q_cm3_s": logq / math.log(10),
                "float64_underflow": rates == 0,
                "log10_conditional_tail_per_sigma_cap_a0sq":
                    (math.log(K_CM3_S) - .5 * math.log(theta)
                     + math.log(E_MAX_EV + theta) - E_MAX_EV / theta) / math.log(10)}

    def conditional_tail_log10(self, temperature_K, assumed_sigma_cap_a0sq):
        """A conditional expression only; this module does not establish the cap."""
        cap = float(assumed_sigma_cap_a0sq)
        if not math.isfinite(cap) or cap <= 0:
            raise ValueError("POSITIVE_EXPLICIT_ASSUMED_TAIL_CAP_REQUIRED")
        coefficient = self.evaluate(temperature_K)["log10_conditional_tail_per_sigma_cap_a0sq"]
        return coefficient + math.log10(cap)


def constants_record():
    return {"eV_J": EV_J, "kB_J_K": KB_J_K, "electron_mass_kg": ME_KG,
            "Bohr_radius_m": A0_M, "K_cm3_s_a0sq_eV_convention": K_CM3_S,
            "source": "NIST CODATA2022 RevModPhys.97.025002; SI->cm3 conversion explicit",
            "DeltaE_eV_from_CCC": DELTA_E_EV, "global_error_bound": None}
