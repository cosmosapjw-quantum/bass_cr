"""Pinned Puchwein arXiv:1801.04931v1 fiducial UVB rate moments.

This adapter is an imposed-background moment operator, not a photon reservoir,
emissivity reconstruction, spectrum, or secondary-electron deposition model.
Inputs and outputs use proper seconds; heat is eV/s per absorbing target.
No isotope mapping is performed. No rate is supplied for a missing species.
"""
from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
from typing import Mapping

SOURCE_SHA256 = "5b4cca58fcc46e821970c0a5a8cbb188cf2b5e6c00f56d6942588c86806662fe"
SOURCE_URL = "https://arxiv.org/src/1801.04931v1/anc/rates_fiducial.txt"
CHANNELS = ("HI", "HeI", "HeII")


@dataclass(frozen=True)
class RateMoments:
    redshift: float
    gamma_s_inv: tuple[float, float, float]
    heat_ev_s_inv: tuple[float, float, float]
    model: str = "Puchwein_arXiv_1801.04931v1_fiducial"
    source_sha256: str = SOURCE_SHA256
    compton_convention: str = "REQUIRED_INPUT_UNAVAILABLE_NOT_USED"


class P19Fiducial:
    """59 source nodes, positive log rates linear in log(1+z), no extrapolation."""

    def __init__(self, source: str | Path | None = None):
        path = Path(source) if source is not None else Path(__file__).parent / "sources" / "P19V1_rates_fiducial.txt"
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
            raise ValueError("UVB_SOURCE_IDENTITY_MISMATCH")
        rows = tuple(tuple(map(float, line.split())) for line in data.decode("ascii").splitlines()
                     if line.strip() and not line.lstrip().startswith("#"))
        if len(rows) != 59 or any(len(row) != 8 for row in rows):
            raise ValueError("UVB_SOURCE_SHAPE_MISMATCH")
        if any(not all(map(math.isfinite, row)) for row in rows):
            raise ValueError("UVB_SOURCE_NONFINITE")
        if any(b[0] <= a[0] for a, b in zip(rows, rows[1:])):
            raise ValueError("UVB_SOURCE_REDSHIFT_NOT_STRICT")
        if any(value <= 0 for row in rows for value in row[1:7]):
            raise ValueError("UVB_SOURCE_NONPOSITIVE_PROCESS_RATE")
        self.rows = rows
        self.z_nodes = tuple(row[0] for row in rows)
        self.x_nodes = tuple(math.log1p(z) for z in self.z_nodes)
        self.log_rates = tuple(tuple(math.log(v) for v in row[1:7]) for row in rows)
        self.redshift_domain = (self.z_nodes[0], self.z_nodes[-1])

    def evaluate(self, redshift: float) -> RateMoments:
        z = float(redshift)
        if not math.isfinite(z) or not self.z_nodes[0] <= z <= self.z_nodes[-1]:
            raise ValueError("UVB_REDSHIFT_OUTSIDE_SOURCE_DOMAIN")
        j = bisect_left(self.z_nodes, z)
        if j < len(self.z_nodes) and self.z_nodes[j] == z:
            values = self.rows[j][1:7]  # Preserve the exact parsed node values.
        else:
            i = j - 1
            w = (math.log1p(z) - self.x_nodes[i]) / (self.x_nodes[j] - self.x_nodes[i])
            values = tuple(raw_a if raw_a == raw_b else math.exp((1.0-w)*a+w*b)
                           for raw_a, raw_b, a, b in zip(self.rows[i][1:7], self.rows[j][1:7],
                                                        self.log_rates[i], self.log_rates[j]))
        return RateMoments(z, tuple(values[k] for k in (0, 2, 4)), tuple(values[k] for k in (1, 3, 5)))

    def source_budget(self, redshift: float, target_abundances: Mapping[str, float],
                      binding_ev: Mapping[str, float]) -> dict:
        """Return a moment-defined external energy ledger per caller reference.

        X_i must be the explicit number of absorbing targets per the caller's
        fixed reference. binding_ev is the caller's explicit registry. The
        source does not numerically state its threshold convention; no exact
        incident-spectrum equivalence is claimed by this accounting operation.
        """
        if set(target_abundances) != set(CHANNELS) or set(binding_ev) != set(CHANNELS):
            raise ValueError("UVB_EXPLICIT_HI_HEI_HEII_CHANNEL_CONTRACT_REQUIRED")
        xs = tuple(float(target_abundances[k]) for k in CHANNELS)
        chis = tuple(float(binding_ev[k]) for k in CHANNELS)
        if any(not math.isfinite(x) or x < 0 for x in xs):
            raise ValueError("UVB_TARGET_ABUNDANCE_INVALID")
        if any(not math.isfinite(x) or x <= 0 for x in chis):
            raise ValueError("UVB_BINDING_REGISTRY_INVALID")
        r = self.evaluate(redshift)
        events = tuple(x*g for x, g in zip(xs, r.gamma_s_inv))
        heat = math.fsum(x*h for x, h in zip(xs, r.heat_ev_s_inv))
        binding = math.fsum(chi*v for chi, v in zip(chis, events))
        imported = math.fsum((heat, binding))
        return {
            "events_per_reference_s": dict(zip(CHANNELS, events)),
            "electron_creation_per_reference_s": math.fsum(events),
            "thermal_ev_per_reference_s": heat,
            "binding_ev_per_reference_s": binding,
            "external_energy_ev_per_reference_s": imported,
            "external_energy_definition": "sum X_i (binding_model_i Gamma_i + heat_source_i)",
            "source_binding_convention": "NUMERIC_THRESHOLDS_NOT_EXPLICIT_IN_RETRIEVED_SOURCE",
            "incident_spectrum": "NOT_RECONSTRUCTED",
            "secondary_deposition": "REQUIRES_ENERGY_RESOLVED_INPUT",
            "global_error_bound": None,
        }
