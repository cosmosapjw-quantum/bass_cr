"""Matched finite CCC H I 1s <-> {2s, 2p} Maxwell collision kernels.

The raw source-native gap is 10.20435 eV.  W(epsilon) =
(epsilon + gap) * sigma_up(epsilon + gap) is piecewise linear on the
source knots.  The reverse flux is W * g_ground / g_upper on the same
shifted finite support.  This module owns no population evolution,
radiative event, source callback, profiler, or automatic scientific run.

This is a new implementation of the preserved PHYS83 S0 contract.  The
historical static-only implementation SHA 4adfa426319574ac0a62e9083f5d09ce
6261585f2aa860b00fc41b92bf2c08ef is provenance, not this file's identity.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import importlib.util
import math
import numbers
from pathlib import Path
import sys
from types import MappingProxyType
from typing import Mapping

import numpy as np


VENDOR_SHA256 = "859cdf616ffa165c9fb3c3372d2202f5449e4b9a74a289a725fe456e26eb55b2"
_VENDOR_PATH = Path(__file__).resolve().parent / "vendor" / "ci_finite_c22d.py"
if hashlib.sha256(_VENDOR_PATH.read_bytes()).hexdigest() != VENDOR_SHA256:
    raise ValueError("CE_VENDOR_IDENTITY_MISMATCH")
_vendor_name = "_phys83_ce_pinned_c22d_859cdf616ffa"
_spec = importlib.util.spec_from_file_location(_vendor_name, _VENDOR_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError("CE_PINNED_VENDOR_IMPORT_UNAVAILABLE")
_vendor = importlib.util.module_from_spec(_spec)
sys.modules[_vendor_name] = _vendor
_spec.loader.exec_module(_vendor)
# Only constants and the already established positive J0/J1/J2 helper are reused.
A0_M = _vendor.A0_M
EV_J = _vendor.EV_J
KB_EV_K = _vendor.KB_EV_K
ME_KG = _vendor.ME_KG
_moments = _vendor._moments

GAP_EV = 10.20435
INCIDENT_MAX_EV = 968.6058
EXCESS_MAX_EV = 958.40145
T_DOMAIN_K = (255.0, 50000.0)
MAXWELL_FACTOR = 100.0 * math.sqrt(8.0 * EV_J / (math.pi * ME_KG))
AREA_CM2_PER_A0SQ = (100.0 * A0_M) ** 2
DEFAULT_SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / "source_data"
PROCESS = "h1_ls_finite_matched_collisional_excitation_deexcitation"
SOURCE_SHA256: Mapping[str, str] = MappingProxyType({
    "CCC_2S.1S": "e8e0092e7be97abe4a90ce100e3101d1f6f225eee2d4ad1ba740f57de819997b",
    "CCC_2P.1S": "12cf46fa0904a5b227092a0a6a3ae6d8a20c041cf11c2981d3bb8bd1f6ac313d",
    "CCC_1S.2S": "f4afdbdeccc49a58055ab86750b14ce10dd2091da55bd380a19f3d7a13c337d0",
    "CCC_1S.2P": "00857e46838c5538da8b047363105b306bc1ba5c827700161749d5d712fa0e5a",
})


def _immutable(values) -> np.ndarray:
    """Read-only float64 view whose immutable bytes owner forbids setflags(True)."""
    array = np.asarray(values, dtype=np.float64)
    return np.frombuffer(array.tobytes(order="C"), dtype=np.float64).reshape(array.shape)


def _temperature(T_K) -> float:
    if isinstance(T_K, (bool, np.bool_)) or not isinstance(T_K, numbers.Real):
        raise ValueError("CE_TEMPERATURE_REQUIRES_REAL_NONBOOL_SCALAR")
    try:
        temperature = float(T_K)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError("CE_TEMPERATURE_REQUIRES_FINITE_SCALAR") from exc
    if not math.isfinite(temperature) or not T_DOMAIN_K[0] <= temperature <= T_DOMAIN_K[1]:
        raise ValueError("CE_TEMPERATURE_OUTSIDE_DECLARED_DOMAIN")
    return temperature


def _load_pinned_blobs(directory: Path) -> dict[str, bytes]:
    """Check all four raw identities; do not replay source reciprocity calculations."""
    blobs = {}
    for name, expected in SOURCE_SHA256.items():
        blob = (directory / name).read_bytes()
        if hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError(f"CE_SOURCE_IDENTITY_MISMATCH:{name}")
        blobs[name] = blob
    return blobs


def _parse_table(blob: bytes, initial: str, final: str, count: int) -> np.ndarray:
    lines = blob.decode("utf-8").splitlines()
    if len(lines) < 2:
        raise ValueError("CE_SOURCE_HEADER_MISSING")
    first = " ".join(lines[0].split())
    if f"{initial} -> {final};" not in first or "a0^2" not in first or "electron - H I" not in first:
        raise ValueError("CE_SOURCE_CHANNEL_OR_AREA_UNIT_MISMATCH")
    if "E(eV)" not in lines[1] or "sig" not in lines[1]:
        raise ValueError("CE_SOURCE_ENERGY_OR_SIG_COLUMN_MISMATCH")
    rows = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) < 2:
            raise ValueError("CE_SOURCE_INCOMPLETE_ROW")
        rows.append((float(fields[0]), float(fields[1])))
    data = np.asarray(rows, dtype=np.float64)
    if data.shape != (count, 2) or not np.all(np.isfinite(data)):
        raise ValueError("CE_SOURCE_SHAPE_OR_FINITE_VALUE_MISMATCH")
    if np.any(np.diff(data[:, 0]) <= 0.0) or np.any(data[:, 1] < 0.0):
        raise ValueError("CE_SOURCE_NONMONOTONE_ENERGY_OR_NEGATIVE_SIGMA")
    return data


@dataclass(frozen=True, slots=True)
class MomentPair:
    temperature_K: float
    M0_eV2_cm2: float
    M1_eV3_cm2: float
    log_M0_eV2_cm2: float
    mean_excess_eV: float
    finite_source_only: bool = True

    @property
    def M0(self) -> float:
        return self.M0_eV2_cm2

    @property
    def M1(self) -> float:
        return self.M1_eV3_cm2

    @property
    def log_M0(self) -> float:
        return self.log_M0_eV2_cm2


@dataclass(frozen=True, slots=True)
class RatePair:
    upper_level: str
    temperature_K: float
    q_up_cm3_s: float
    q_down_cm3_s: float
    log_q_up_cm3_s: float
    log_q_down_cm3_s: float
    log10_q_up_cm3_s: float
    log10_q_down_cm3_s: float
    float64_underflow_up: bool
    float64_underflow_down: bool
    M0_eV2_cm2: float
    M1_eV3_cm2: float
    mean_excess_eV: float
    mean_incoming_up_eV: float
    mean_incoming_down_eV: float
    dlogq_up_dT_K_inv: float
    dlogq_down_dT_K_inv: float
    dq_up_dT_cm3_s_K: float
    dq_down_dT_cm3_s_K: float
    finite_source_only: bool = True


@dataclass(frozen=True, slots=True, eq=False, init=False)
class MatchedCEChannel:
    upper_level: str
    gap_eV: float
    g_ground: int
    g_upper: int
    source_sha256: str
    reverse_source_sha256: str
    source_directory: str
    energy_eV: np.ndarray = field(repr=False)
    sigma_a0sq: np.ndarray = field(repr=False)
    sigma_cm2: np.ndarray = field(repr=False)
    epsilon_eV: np.ndarray = field(repr=False)
    W_eV_cm2: np.ndarray = field(repr=False)
    reverse_energy_eV: np.ndarray = field(repr=False)
    reverse_sigma_a0sq: np.ndarray = field(repr=False)
    _left_eV: np.ndarray = field(repr=False)
    _width_eV: np.ndarray = field(repr=False)
    _W_left_scaled: np.ndarray = field(repr=False)
    _W_right_scaled: np.ndarray = field(repr=False)
    _W_scale: float = field(repr=False)

    def __init__(self, upper_level: str, source_directory=None):
        if not isinstance(upper_level, str) or upper_level not in ("2S", "2P"):
            raise ValueError("CE_UPPER_LEVEL_UNAVAILABLE")
        directory = Path(source_directory) if source_directory is not None else DEFAULT_SOURCE_DIRECTORY
        blobs = _load_pinned_blobs(directory)
        forward_name, reverse_name = f"CCC_{upper_level}.1S", f"CCC_1S.{upper_level}"
        forward = _parse_table(blobs[forward_name], "1S", upper_level, 452)
        reverse = _parse_table(blobs[reverse_name], upper_level, "1S", 451)
        if (tuple(forward[0]) != (GAP_EV, 0.0)
                or forward[1, 0] != 10.2043885
                or forward[-1, 0] != INCIDENT_MAX_EV
                or reverse[0, 0] != 0.0000385
                or reverse[-1, 0] != EXCESS_MAX_EV
                or np.any(forward[1:, 1] <= 0.0)
                or np.any(reverse[:, 1] <= 0.0)):
            raise ValueError("CE_SOURCE_ENDPOINT_OR_POSITIVITY_MISMATCH")

        energy = forward[:, 0]
        epsilon = energy - GAP_EV
        sigma = forward[:, 1] * AREA_CM2_PER_A0SQ
        flux = energy * sigma
        scale = float(np.max(flux))
        if epsilon[0] != 0.0 or not math.isfinite(scale) or scale <= 0.0:
            raise ValueError("CE_INVALID_SOURCE_FLUX_SCALE")
        values = {
            "upper_level": upper_level,
            "gap_eV": GAP_EV,
            "g_ground": 2,
            "g_upper": 2 if upper_level == "2S" else 6,
            "source_sha256": SOURCE_SHA256[forward_name],
            "reverse_source_sha256": SOURCE_SHA256[reverse_name],
            "source_directory": str(directory.resolve()),
            "energy_eV": _immutable(energy),
            "sigma_a0sq": _immutable(forward[:, 1]),
            "sigma_cm2": _immutable(sigma),
            "epsilon_eV": _immutable(epsilon),
            "W_eV_cm2": _immutable(flux),
            "reverse_energy_eV": _immutable(reverse[:, 0]),
            "reverse_sigma_a0sq": _immutable(reverse[:, 1]),
            "_left_eV": _immutable(epsilon[:-1]),
            "_width_eV": _immutable(np.diff(epsilon)),
            "_W_left_scaled": _immutable(flux[:-1] / scale),
            "_W_right_scaled": _immutable(flux[1:] / scale),
            "_W_scale": scale,
        }
        for name, value in values.items():
            object.__setattr__(self, name, value)

    def moments(self, T_K) -> MomentPair:
        """Evaluate M_n = integral epsilon^n W exp(-epsilon/theta) d epsilon."""
        temperature = _temperature(T_K)
        theta = KB_EV_K * temperature
        left, width = self._left_eV, self._width_eV
        j0, j1, j2 = _moments(width / theta)
        left0, right0 = j0 - j1, j1
        left1, right1 = left * left0 + width * (j1 - j2), left * j1 + width * j2
        factor = width * np.exp(-left / theta)
        cells0 = factor * (self._W_left_scaled * left0 + self._W_right_scaled * right0)
        cells1 = factor * (self._W_left_scaled * left1 + self._W_right_scaled * right1)
        if (np.any(cells0 < 0.0) or np.any(cells1 < 0.0)
                or not np.all(np.isfinite(cells0)) or not np.all(np.isfinite(cells1))):
            raise ArithmeticError("CE_INVALID_POSITIVE_CELL_MOMENTS")
        scaled0 = math.fsum(float(x) for x in cells0)
        scaled1 = math.fsum(float(x) for x in cells1)
        if not math.isfinite(scaled0) or not math.isfinite(scaled1) or scaled0 <= 0.0 or scaled1 <= 0.0:
            raise ArithmeticError("CE_INVALID_TOTAL_MOMENTS")
        m0, m1 = self._W_scale * scaled0, self._W_scale * scaled1
        mean_excess = scaled1 / scaled0
        log_m0 = math.log(self._W_scale) + math.log(scaled0)
        if (not all(math.isfinite(x) for x in (m0, m1, mean_excess, log_m0))
                or m0 <= 0.0 or m1 <= 0.0 or not 0.0 < mean_excess < EXCESS_MAX_EV):
            raise ArithmeticError("CE_NONFINITE_OR_OUT_OF_SUPPORT_MOMENT")
        return MomentPair(temperature, m0, m1, log_m0, mean_excess)

    def evaluate(self, T_K, *, species="H1", full_physical_rate=False) -> RatePair:
        if not isinstance(species, str) or species != "H1":
            raise ValueError("CE_SPECIES_COVERAGE_UNAVAILABLE")
        if not isinstance(full_physical_rate, (bool, np.bool_)):
            raise ValueError("CE_FULL_PHYSICAL_RATE_FLAG_REQUIRES_BOOL")
        if full_physical_rate:
            raise ValueError("CE_FULL_PHYSICAL_RATE_UNAVAILABLE")
        moment = self.moments(T_K)
        temperature = moment.temperature_K
        theta = KB_EV_K * temperature
        common_log = math.fsum((math.log(MAXWELL_FACTOR), -1.5 * math.log(theta), moment.log_M0_eV2_cm2))
        log_up = common_log - self.gap_eV / theta
        log_down = common_log + math.log(self.g_ground / self.g_upper)
        q_up, q_down = math.exp(log_up), math.exp(log_down)
        mean_up = self.gap_eV + moment.mean_excess_eV
        dlog_up = (mean_up / theta - 1.5) / temperature
        dlog_down = (moment.mean_excess_eV / theta - 1.5) / temperature
        dq_up, dq_down = q_up * dlog_up, q_down * dlog_down
        if (q_up < 0.0 or q_down < 0.0
                or not all(math.isfinite(x) for x in
                           (q_up, q_down, log_up, log_down, mean_up, dlog_up, dlog_down, dq_up, dq_down))):
            raise ArithmeticError("CE_INVALID_RATE_OR_TEMPERATURE_DERIVATIVE")
        log10_scale = math.log(10.0)
        return RatePair(
            upper_level=self.upper_level,
            temperature_K=temperature,
            q_up_cm3_s=q_up,
            q_down_cm3_s=q_down,
            log_q_up_cm3_s=log_up,
            log_q_down_cm3_s=log_down,
            log10_q_up_cm3_s=log_up / log10_scale,
            log10_q_down_cm3_s=log_down / log10_scale,
            float64_underflow_up=q_up == 0.0,
            float64_underflow_down=q_down == 0.0,
            M0_eV2_cm2=moment.M0_eV2_cm2,
            M1_eV3_cm2=moment.M1_eV3_cm2,
            mean_excess_eV=moment.mean_excess_eV,
            mean_incoming_up_eV=mean_up,
            mean_incoming_down_eV=moment.mean_excess_eV,
            dlogq_up_dT_K_inv=dlog_up,
            dlogq_down_dT_K_inv=dlog_down,
            dq_up_dT_cm3_s_K=dq_up,
            dq_down_dT_cm3_s_K=dq_down,
        )

    def coverage(self) -> dict:
        return {
            "process": PROCESS,
            "species": "H1",
            "initial_state_up": "1S",
            "initial_state_down": self.upper_level,
            "target_convention": "stationary-heavy-target; unpolarized LS term",
            "gap_eV": self.gap_eV,
            "ground_degeneracy": self.g_ground,
            "upper_degeneracy": self.g_upper,
            "temperature_domain_K": list(T_DOMAIN_K),
            "forward_rows": len(self.energy_eV),
            "reverse_source_rows": len(self.reverse_energy_eV),
            "incident_support_eV": [GAP_EV, INCIDENT_MAX_EV],
            "matched_excess_support_eV": [0.0, EXCESS_MAX_EV],
            "raw_reverse_support_eV": [0.0000385, EXCESS_MAX_EV],
            "source_sha256": self.source_sha256,
            "reverse_source_sha256": self.reverse_source_sha256,
            "all_source_pins": dict(SOURCE_SHA256),
            "vendor_sha256": VENDOR_SHA256,
            "interpolation": "piecewise linear W=(epsilon+gap)*sigma_up in epsilon",
            "reverse_interpolation": "same W divided by epsilon and degeneracy ratio",
            "source_cross_section_unit": "a0^2; no extra pi or multiplicity factor",
            "computed_rate_unit": "cm^3/s",
            "finite_source_only": True,
            "physical_tail_bound_established": False,
            "physical_interpolation_uncertainty_established": False,
            "isotope_resolved": False,
            "radiative_owner": None,
            "production_admission": "NOT_ISSUED",
        }


def load_channels(source_directory=None) -> dict[str, MatchedCEChannel]:
    """Load immutable, source-pinned channels without evaluating a rate."""
    return {
        "2S": MatchedCEChannel("2S", source_directory),
        "2P": MatchedCEChannel("2P", source_directory),
    }
