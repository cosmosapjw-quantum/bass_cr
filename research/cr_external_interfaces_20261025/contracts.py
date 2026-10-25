"""Finite source/ledger interfaces. No transport, quadrature, or thermalization.

All particle weights are masses of a *discrete measure*, not density samples.
This module deliberately distinguishes native source, canonical proper source,
integrated exposure, and a diagnostic cutoff partition.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import fsum, isfinite
from pathlib import Path
from typing import Mapping
import hashlib
import re

EV_J = 1.602176634e-19
KB_J_K = 1.380649e-23
ENERGY_RTOL = 2e-13  # inherited C23E shared-event ledger criterion
RESERVOIRS = ("binding", "thermal_kinetic", "fast_kinetic", "radiation",
              "recoil", "escaped", "external")


class ContractError(ValueError):
    pass


def number(value: float, name: str, *, nonnegative: bool = False,
           positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{name}: explicit real scalar required")
    v = float(value)
    if not isfinite(v) or (nonnegative and v < 0) or (positive and v <= 0):
        raise ContractError(f"{name}: invalid finite domain")
    return v


def closed_sum(values: tuple[float, ...], name: str,
               rtol: float = ENERGY_RTOL) -> float:
    vals = tuple(number(x, name) for x in values)
    residual, scale = fsum(vals), fsum(abs(x) for x in vals)
    if abs(residual) > rtol * scale or (scale == 0 and residual != 0):
        raise ContractError(f"{name}: closure failed ({residual}, scale {scale})")
    return residual


@dataclass(frozen=True)
class SourcePin:
    repository: str
    commit: str
    path: str
    sha256: str

    def verify(self, root: Path) -> bytes:
        if not self.repository or "/" not in self.repository or not self.path:
            raise ContractError("source repository/path identity required")
        if not re.fullmatch(r"[0-9a-f]{40}", self.commit):
            raise ContractError("full immutable source commit required")
        if not re.fullmatch(r"[0-9a-f]{64}", self.sha256):
            raise ContractError("full SHA256 required")
        p = (root / self.path).resolve()
        if not p.is_relative_to(root.resolve()):
            raise ContractError("source path escapes checkout")
        raw = p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != self.sha256:
            raise ContractError(f"source digest mismatch: {self.path}")
        return raw


@dataclass(frozen=True)
class IsotopeMapping:
    source_label: str
    isotope_species: str
    status: str
    evidence: str

    def require(self, label: str, species: str) -> None:
        if (label, species) != (self.source_label, self.isotope_species):
            raise ContractError("source-label/isotope mapping mismatch")
        if self.status not in ("CONDITIONAL_ELEMENTAL_ASSIGNMENT",
                               "SOURCE_RESOLVED") or not self.evidence:
            raise ContractError("unqualified isotope mapping")


@dataclass(frozen=True)
class Domain:
    energy_coordinate: str
    support_eV: tuple[float, float]
    redshifts: tuple[float, ...]
    frame: str
    angular: str
    mass_model: str

    def __post_init__(self):
        if (type(self.support_eV) is not tuple or type(self.redshifts) is not tuple
                or len(self.support_eV) != 2 or not self.redshifts):
            raise ContractError("finite ordered support and explicit epochs required")
        lo, hi = (number(v, "support", nonnegative=True) for v in self.support_eV)
        if lo >= hi or not self.frame or not self.angular or not self.mass_model:
            raise ContractError("nondegenerate support/frame/angular/mass declaration required")
        for z in self.redshifts:
            number(z, "redshift", nonnegative=True)

    def require(self, *, energy_coordinate: str, energies_eV: tuple[float, ...],
                redshift: float, frame: str, angular: str, mass_model: str) -> None:
        if energy_coordinate != self.energy_coordinate:
            raise ContractError("kinetic/total/photon energy coordinate mismatch")
        if number(redshift, "redshift", nonnegative=True) not in self.redshifts:
            raise ContractError("redshift interpolation/extrapolation requires new admission")
        if (frame, angular, mass_model) != (self.frame, self.angular, self.mass_model):
            raise ContractError("frame/angular/finite-mass scope mismatch")
        lo, hi = self.support_eV
        for x in energies_eV:
            e = number(x, "energy", nonnegative=True)
            if not lo <= e <= hi:
                raise ContractError("energy support extension requires new admission")


@dataclass(frozen=True)
class NativeMeasure:
    source_id: str
    particle_kind: str
    species: str
    energy_coordinate: str
    rest_energy_eV: float
    energies_eV: tuple[float, ...]
    weights: tuple[float, ...]
    normalization: str
    frame: str
    angular: str
    measure: str = "finite_atomic_dK"

    def __post_init__(self):
        if not self.source_id or not self.species:
            raise ContractError("source and species identities required")
        if self.particle_kind not in ("photon", "electron", "baryon"):
            raise ContractError("unsupported particle kind")
        if self.measure != "finite_atomic_dK":
            raise ContractError("explicit conversion from d3p/dlogK/occupation required")
        if self.angular != "isotropic" or not self.frame:
            raise ContractError("this scalar consumer needs an explicit isotropic frame")
        m = number(self.rest_energy_eV, "rest energy", nonnegative=True)
        if self.particle_kind == "photon":
            if m != 0 or self.energy_coordinate != "total":
                raise ContractError("photon requires total energy and zero rest energy")
        elif self.energy_coordinate != "kinetic" or m <= 0:
            raise ContractError("massive particle requires kinetic coordinate and rest energy")
        if (type(self.energies_eV) is not tuple or type(self.weights) is not tuple
                or not self.energies_eV or len(self.energies_eV) != len(self.weights)):
            raise ContractError("nonempty paired atomic energy/weight arrays required")
        for e, w in zip(self.energies_eV, self.weights):
            number(e, "atom energy", nonnegative=True)
            number(w, "atom weight", nonnegative=True)


@dataclass(frozen=True)
class Scaling:
    target_density_m3: float | None = None
    reference_density_m3: float | None = None
    proper_volume_per_comoving_volume: float | None = None
    proper_seconds_per_coordinate_second: float | None = None

    def factor(self, normalization: str) -> float:
        values = {k: getattr(self, k) for k in self.__dataclass_fields__}
        required = {
            "per_target_per_proper_s": {"target_density_m3"},
            "per_proper_m3_per_proper_s": set(),
            "per_comoving_m3_per_coordinate_s": {
                "proper_volume_per_comoving_volume", "proper_seconds_per_coordinate_second"},
            "per_reference_per_coordinate_s": {
                "reference_density_m3", "proper_seconds_per_coordinate_second"},
        }
        if normalization not in required:
            raise ContractError("normalization/clock/volume must be explicitly converted")
        if {k for k, v in values.items() if v is not None} != required[normalization]:
            raise ContractError("density, volume and clock factors must occur exactly once")
        v = {k: number(x, k, nonnegative=True) for k, x in values.items() if x is not None}
        for key in ("proper_volume_per_comoving_volume", "proper_seconds_per_coordinate_second"):
            if key in v and v[key] == 0:
                raise ContractError("positive volume/clock Jacobian required")
        if normalization == "per_target_per_proper_s":
            return v["target_density_m3"]
        if normalization == "per_proper_m3_per_proper_s":
            return 1.0
        if normalization == "per_comoving_m3_per_coordinate_s":
            return 1 / v["proper_volume_per_comoving_volume"] / v["proper_seconds_per_coordinate_second"]
        return v["reference_density_m3"] / v["proper_seconds_per_coordinate_second"]


@dataclass(frozen=True)
class ProperSource:
    native: NativeMeasure
    atom_rates_m3_s: tuple[float, ...]
    scaling: Scaling

    def __post_init__(self):
        if type(self.native) is not NativeMeasure or type(self.scaling) is not Scaling:
            raise ContractError("proper source must retain native measure and scaling")
        if type(self.atom_rates_m3_s) is not tuple or len(self.atom_rates_m3_s) != len(self.native.weights):
            raise ContractError("canonical rate/native measure length mismatch")
        factor = self.scaling.factor(self.native.normalization)
        for rate, weight in zip(self.atom_rates_m3_s, self.native.weights):
            if number(rate, "canonical rate", nonnegative=True) != factor * weight:
                raise ContractError("canonical rate does not match exactly one normalization")

    def moments(self) -> dict:
        n = fsum(self.atom_rates_m3_s)
        k = fsum(w * e * EV_J for w, e in zip(self.atom_rates_m3_s, self.native.energies_eV))
        return {"number_m3_s": n, "coordinate_energy_J_m3_s": k,
                "total_energy_J_m3_s": k + n * self.native.rest_energy_eV * EV_J,
                "momentum_status": "ISOTROPIC_ENSEMBLE_NET_ZERO_ONLY",
                "physical_thermal_heating_J_m3_s": None}

    def integrate_constant_exposure(self, proper_seconds: float) -> IntegratedSource:
        t = number(proper_seconds, "constant proper exposure", nonnegative=True)
        return IntegratedSource(self, t, tuple(t * x for x in self.atom_rates_m3_s))


@dataclass(frozen=True)
class IntegratedSource:
    source: ProperSource
    proper_seconds: float
    counts_m3: tuple[float, ...]

    def __post_init__(self):
        if type(self.source) is not ProperSource:
            raise ContractError("integrated exposure must retain its canonical proper source")
        t = number(self.proper_seconds, "proper exposure", nonnegative=True)
        if type(self.counts_m3) is not tuple or len(self.counts_m3) != len(self.source.atom_rates_m3_s):
            raise ContractError("integrated count/source length mismatch")
        for count, rate in zip(self.counts_m3, self.source.atom_rates_m3_s):
            if number(count, "integrated count", nonnegative=True) != t * rate:
                raise ContractError("integrated counts do not match exactly one constant exposure")


def normalize(source: NativeMeasure, scaling: Scaling) -> ProperSource:
    if type(source) is not NativeMeasure:
        raise ContractError("only a native source may be normalized; repeated conversion rejected")
    factor = scaling.factor(source.normalization)
    rates = tuple(number(factor * w, "canonical atom rate", nonnegative=True) for w in source.weights)
    return ProperSource(source, rates, scaling)


def distribution_moments(distribution: NativeMeasure) -> dict:
    """A phase-space population has no implicit time factor or injection history."""
    if type(distribution) is not NativeMeasure or distribution.normalization != "number_per_proper_m3":
        raise ContractError("population and injection source have different dimensions")
    n = fsum(distribution.weights)
    u = fsum(e * w * EV_J for e, w in zip(distribution.energies_eV, distribution.weights))
    return {"number_m3": n, "coordinate_energy_J_m3": u,
            "total_energy_J_m3": u + n * distribution.rest_energy_eV * EV_J,
            "injection_rate": None, "history": "NOT_SUPPLIED"}


def caloric_partition(source: ProperSource, cutoff_eV: float) -> dict:
    """Finite measure split only. It does not move particles to a thermal pool."""
    if type(source) is not ProperSource or source.native.energy_coordinate != "kinetic":
        raise ContractError("proper kinetic source required")
    cutoff = number(cutoff_eV, "cutoff", nonnegative=True)
    low = [(e, w) for e, w in zip(source.native.energies_eV, source.atom_rates_m3_s) if e <= cutoff]
    high = [(e, w) for e, w in zip(source.native.energies_eV, source.atom_rates_m3_s) if e > cutoff]
    moment = lambda rows: {"number_m3_s": fsum(w for _, w in rows),
                           "kinetic_J_m3_s": fsum(e * w * EV_J for e, w in rows)}
    return {"low_closed": moment(low), "high_open": moment(high),
            "thermal_particle_transfer_m3_s": None, "physical_heating_J_m3_s": None,
            "irreversible_assimilation": False, "status": "CALORIC_PARTITION_ONLY"}


@dataclass(frozen=True)
class Species:
    name: str
    charge_e: int
    nuclei: tuple[tuple[str, int], ...]

    def __post_init__(self):
        if not self.name or type(self.charge_e) is not int:
            raise ContractError("explicit species name/integer charge required")
        if type(self.nuclei) is not tuple or any(type(x) is not tuple for x in self.nuclei):
            raise ContractError("immutable nuclear composition required")
        if len({x for x, _ in self.nuclei}) != len(self.nuclei):
            raise ContractError("duplicate nuclear constituent")
        if any(not key or type(n) is not int or n <= 0 for key, n in self.nuclei):
            raise ContractError("positive integer nuclear constituent counts required")


@dataclass(frozen=True)
class Event:
    event_id: str
    source_contract: str
    microscopic_owner: str
    transport_owner: str
    extent_m3_s: float
    number_per_event: tuple[tuple[Species, float], ...]
    energy_J_per_event: tuple[tuple[str, float], ...]
    frame: str
    process: str
    # No directional claim is inferred from scalar ground-state source inputs.
    momentum_status: str = "SCALAR_ENSEMBLE_ONLY"

    def validate(self) -> dict:
        if not all((self.event_id, self.source_contract, self.microscopic_owner,
                    self.transport_owner, self.frame)):
            raise ContractError("event/source/owner/frame identity is required")
        number(self.extent_m3_s, "shared event extent", nonnegative=True)
        if (type(self.number_per_event) is not tuple or type(self.energy_J_per_event) is not tuple
                or any(type(x) is not tuple for x in (*self.number_per_event, *self.energy_J_per_event))
                or any(type(s) is not Species for s, _ in self.number_per_event)):
            raise ContractError("immutable typed event payload required")
        if len({s.name for s, _ in self.number_per_event}) != len(self.number_per_event):
            raise ContractError("species pool may occur only once per event")
        entries = dict(self.energy_J_per_event)
        if len(entries) != len(self.energy_J_per_event) or set(entries) != set(RESERVOIRS):
            raise ContractError("one explicit owner per energy reservoir is required")
        residual = closed_sum(tuple(entries.values()), "energy")
        if self.process == "photoionization":
            if (entries["thermal_kinetic"] != 0 or entries["fast_kinetic"] < 0
                    or entries["binding"] < 0 or entries["radiation"] > 0
                    or entries["external"] != 0 or entries["escaped"] != 0):
                raise ContractError("primary photoelectron energy has one fast-pool owner")
        elif self.process == "radiative_recombination":
            if (entries["binding"] > 0 or entries["thermal_kinetic"] > 0
                    or entries["fast_kinetic"] > 0 or entries["external"] != 0
                    or entries["radiation"] < 0 or entries["escaped"] < 0 or entries["recoil"] < 0):
                raise ContractError("RR removes electron/internal energy with separate photon owner")
        elif self.process == "charge_exchange":
            if any(entries[k] != 0 for k in ("fast_kinetic", "radiation", "escaped", "external")):
                raise ContractError("C23E charge exchange keeps electron/photon pools unchanged")
        elif self.process == "electron_cascade":
            if entries["external"] != 0 or entries["radiation"] < 0:
                raise ContractError("cascade consumes its electron budget, not the original photon twice")
        elif self.process == "stopping_exchange":
            if any(entries[k] != 0 for k in ("binding", "radiation", "recoil", "escaped", "external")):
                raise ContractError("stopping exchange requires paired thermal/fast ownership")
        else:
            raise ContractError("explicit admitted event process required")
        nuclear = {key for species, _ in self.number_per_event for key, _ in species.nuclei}
        nr = {}
        for key in nuclear:
            nr[key] = closed_sum(tuple(number(x, "stoichiometry") * dict(s.nuclei).get(key, 0)
                                       for s, x in self.number_per_event), f"nucleus {key}")
        cr = closed_sum(tuple(s.charge_e * number(x, "stoichiometry")
                              for s, x in self.number_per_event), "electric charge")
        if self.momentum_status != "SCALAR_ENSEMBLE_ONLY":
            raise ContractError("directional momentum needs a separately qualified angular interface")
        return {"energy_residual_J_per_event": residual, "charge_residual": cr,
                "nuclide_residuals": nr, "momentum_status": self.momentum_status}


class EventBook:
    """Append-only consumer prevents repeated absorption or source event identity."""
    def __init__(self, frame: str):
        if not frame:
            raise ContractError("explicit common frame required")
        self.frame = frame
        self._events: dict[str, Event] = {}

    def append(self, event: Event) -> dict:
        if event.event_id in self._events:
            raise ContractError("duplicate event ID: source/absorption already consumed")
        if event.frame != self.frame:
            raise ContractError("mixed-frame ledgers require an explicit transformation")
        result = event.validate()
        self._events[event.event_id] = event
        return result

    def energy_rates(self) -> dict[str, float]:
        return {key: fsum(e.extent_m3_s * dict(e.energy_J_per_event)[key]
                          for e in self._events.values()) for key in RESERVOIRS}


@dataclass(frozen=True)
class CaloricDerivative:
    """dU_th=C_V dT+sum(mu_thermal,s dn_s), independent of binding energy."""
    heat_capacity_J_m3_K: float
    particle_energy_derivatives_J: tuple[tuple[str, float], ...]
    equation_of_state_source: str

    def temperature_rate(self, thermal_energy_rate_J_m3_s: float,
                         particle_rates_m3_s: Mapping[str, float]) -> float:
        cv = number(self.heat_capacity_J_m3_K, "heat capacity", positive=True)
        mu = dict(self.particle_energy_derivatives_J)
        if not self.equation_of_state_source or len(mu) != len(self.particle_energy_derivatives_J):
            raise ContractError("unique EOS derivative definitions required")
        if set(mu) != set(particle_rates_m3_s):
            raise ContractError("thermal particle-number/composition derivatives must be explicit")
        terms = tuple(number(mu[k], "thermal derivative") * number(particle_rates_m3_s[k], "particle rate")
                      for k in mu)
        return fsum((number(thermal_energy_rate_J_m3_s, "thermal energy rate"), -fsum(terms))) / cv


def require_physical_provider(card: Mapping, *, process: str, species: str,
                              energy_eV: float, frame: str, mass_model: str,
                              root: Path | None = None) -> None:
    """Verify declared source/review identity and compatibility, not scientific proof.

    A reviewed supplier's admission must already exist. This function cannot
    turn a payload or a self-asserted status string into that scientific review.
    All providers registered by this unit for beta/cascade/stopping remain open.
    """
    if card.get("status") != "ADMITTED_SCOPED" or not card.get("source_pins"):
        raise ContractError("SOURCE_INPUT_PENDING: no source-qualified provider")
    pins = card["source_pins"]
    review = card.get("admission_review_pin")
    if (root is None or not isinstance(pins, (tuple, list)) or not pins
            or any(type(p) is not SourcePin for p in pins) or type(review) is not SourcePin):
        raise ContractError("verified immutable source pins and independent admission-review pin required")
    for pin in (*pins, review):
        pin.verify(root)
    if card.get("process") != process or species not in card.get("species", ()):
        raise ContractError("provider process/species mismatch")
    if (card.get("frame"), card.get("mass_model")) != (frame, mass_model):
        raise ContractError("provider frame/finite-mass scope mismatch")
    support = card.get("energy_support_eV")
    if not isinstance(support, (tuple, list)) or len(support) != 2:
        raise ContractError("explicit provider support required")
    e = number(energy_eV, "energy", nonnegative=True)
    lo, hi = (number(v, "provider support", nonnegative=True) for v in support)
    if lo > hi or not lo <= e <= hi:
        raise ContractError("provider extrapolation is not admitted")
    if process == "beta_injection":
        required = ("evaluated_spectrum", "evaluated_Q", "evaluated_branching", "parent_isomer_charge",
                    "daughter", "neutrino", "recoil", "proper_lifetime", "mass_convention")
        if any(type(card.get(k)) is not SourcePin for k in required):
            raise ContractError("evaluated beta spectrum/Q/branch/owners/clock are incomplete")
        for key in required:
            card[key].verify(root)


def boundary_flux(*, cutoff_eV: float, number_flux_m3_s: float,
                  kinetic_flux_J_m3_s: float) -> dict:
    """Same signed boundary flux supplies count and kinetic energy, no irreversibility claim."""
    e = number(cutoff_eV, "cutoff", nonnegative=True)
    j = number(number_flux_m3_s, "number flux")
    q = number(kinetic_flux_J_m3_s, "kinetic flux")
    closed_sum((q, -e * EV_J * j), "shared cutoff flux")
    return {"thermal_particle_flux_m3_s": j, "fast_particle_flux_m3_s": -j,
            "thermal_kinetic_flux_J_m3_s": q, "fast_kinetic_flux_J_m3_s": -q,
            "irreversible_assimilation": False, "physical_stopping_status": "PROVIDER_REQUIRED"}
