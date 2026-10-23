"""Clock, volume, and energy ownership for an explicitly specified decay yield.

The functions preserve a per-event ledger. Electron-only energy is never
identified with the parent/daughter/neutrino/recoil total source.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import fsum, isfinite
from boost_kernel import Boost, ElectronMeasure, Moments, finite_nonnegative


@dataclass(frozen=True)
class DecayClock:
    bath_parent_density_m3: float
    proper_mean_lifetime_s: float
    boost: Boost
    comoving_volume_factor: float
    dt_deta_s: float
    physical_reference_density_m3: float

    def __post_init__(self):
        for field in ("bath_parent_density_m3", "proper_mean_lifetime_s",
                      "comoving_volume_factor", "dt_deta_s",
                      "physical_reference_density_m3"):
            value = finite_nonnegative(getattr(self, field), field)
            if field != "bath_parent_density_m3" and value == 0:
                raise ValueError(field + " must be strictly positive")
            object.__setattr__(self, field, value)
        if not isinstance(self.boost, Boost):
            raise ValueError("explicit parent Boost is required")

    @property
    def events_per_m3_s(self) -> float:
        return self.bath_parent_density_m3 / self.boost.gamma / self.proper_mean_lifetime_s

    def electron_sources(self, rest_measure: ElectronMeasure, *, parent_directions: str) -> dict:
        if rest_measure.frame != "parent_rest" or rest_measure.units != "electrons_per_event":
            raise ValueError("decay clock requires a parent-rest per-event measure")
        if parent_directions not in ("isotropic", "equal_opposite_lrs_beams", "single_beam"):
            raise ValueError("parent direction distribution must be explicit")
        event = rest_measure.total(self.boost)
        rate = self.events_per_m3_s
        flux_factor = 1.0 if parent_directions == "single_beam" else 0.0
        ensemble_event = Moments(event.number, event.kinetic_ev, event.total_ev,
                                 event.parallel_pc_ev*flux_factor)
        physical = ensemble_event.scaled(rate)
        comoving = physical.scaled(self.comoving_volume_factor)
        reference_eta = physical.scaled(self.dt_deta_s/self.physical_reference_density_m3)
        return {
            "single_parent_axis_per_event_diagnostic": event.as_tuple(),
            "ensemble_per_event": ensemble_event.as_tuple(),
            "physical_number_kinetic_total_parallelpc_per_m3_s": physical.as_tuple(),
            "comoving_number_kinetic_total_parallelpc_per_m3com_s": comoving.as_tuple(),
            "reference_number_kinetic_total_parallelpc_per_ref_eta": reference_eta.as_tuple(),
            "net_parallel_pc_source_ev_m3_s": physical.parallel_pc_ev,
            "direction_contract": parent_directions,
            "scalar_isotropic_source_admitted": parent_directions == "isotropic",
            "stress_tensor": "isotropic_by_parent_direction_average" if parent_directions == "isotropic" else "NOT_COMPUTED",
            "electron_energy_only": True,
            "required_other_owners": ["daughter_rest_and_kinetic", "neutrino", "atomic_binding_if_applicable"],
            "events_per_m3_s": rate,
        }


def reaction_event_ledger(*, imported_photon_ev: float, primary_binding_ev: float,
                          electron_kinetic_ev: float, recoil_ev: float,
                          escaping_other_ev: float) -> dict:
    """Explicit photo-event ownership; never add an implicit missing zero term."""
    values = {name: finite_nonnegative(value, name) for name, value in (
        ("imported_photon_ev", imported_photon_ev),
        ("primary_binding_ev", primary_binding_ev),
        ("electron_kinetic_ev", electron_kinetic_ev),
        ("recoil_ev", recoil_ev), ("escaping_other_ev", escaping_other_ev))}
    residual = imported_photon_ev-fsum((primary_binding_ev, electron_kinetic_ev,
                                       recoil_ev, escaping_other_ev))
    return dict(values, residual_ev=residual,
                cascade_owner="electron_kinetic_ev only; binding is already debited",
                full_radiative_thermal_closure="OPEN")
