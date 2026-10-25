"""Manufactured interface controls, separate from the saved physical input bridge."""
from dataclasses import replace
from math import fsum
from pathlib import Path
import tempfile
import unittest

from contracts import (EV_J, KB_J_K, CaloricDerivative, ContractError, Domain,
                       Event, EventBook, IntegratedSource, IsotopeMapping, NativeMeasure, ProperSource, Scaling,
                       SourcePin, Species, boundary_flux, caloric_partition,
                       distribution_moments, normalize, require_physical_provider)


def electron(normalization="per_target_per_proper_s"):
    return NativeMeasure("MANUFACTURED_ONLY", "electron", "e:fast", "kinetic", 510998.95069,
                         (1.0, 2.0), (2.0, 3.0), normalization, "bath", "isotropic")


def photo():
    return Event("manufactured_photo_1", "manufactured_PI", "test_only", "test_only", 7.0,
                 ((Species("H1:0", 0, (("H1", 1),)), -1),
                  (Species("H1:1", 1, (("H1", 1),)), 1),
                  (Species("e:fast", -1, ()), 1)),
                 (("binding", 13.6 * EV_J), ("thermal_kinetic", 0.0),
                  ("fast_kinetic", 5.0 * EV_J), ("radiation", -18.6 * EV_J),
                  ("recoil", 0.0), ("escaped", 0.0), ("external", 0.0)),
                 "bath", "photoionization")


class InterfaceControls(unittest.TestCase):
    def test_per_target_density_once(self):
        source = normalize(electron(), Scaling(target_density_m3=4.0))
        self.assertEqual(source.moments()["number_m3_s"], 20.0)
        self.assertAlmostEqual(source.moments()["coordinate_energy_J_m3_s"] / EV_J, 32.0)
        with self.assertRaises(ContractError):
            normalize(source, Scaling(target_density_m3=4.0))

    def test_density_and_reference_cannot_both_apply(self):
        with self.assertRaises(ContractError):
            normalize(electron(), Scaling(target_density_m3=4, reference_density_m3=4))

    def test_direct_source_and_exposure_construction_cannot_bypass_contract(self):
        for rates in ((8.0,), (-8.0, 12.0), (16.0, 24.0)):
            with self.assertRaises(ContractError):
                ProperSource(electron(), rates, Scaling(target_density_m3=4.0))
        s = normalize(electron(), Scaling(target_density_m3=4.0))
        with self.assertRaises(ContractError):
            IntegratedSource(s, 2.0, (16.0,))
        with self.assertRaises(ContractError):
            IntegratedSource(s, 2.0, (16.0, -24.0))

    def test_already_volumetric_source_rejects_density(self):
        with self.assertRaises(ContractError):
            normalize(electron("per_proper_m3_per_proper_s"), Scaling(target_density_m3=4))

    def test_comoving_volume_and_clock_divide_once(self):
        # dVproper=8*dVcom, dtau=2*deta: raw40 -> proper2.5.
        raw = replace(electron("per_comoving_m3_per_coordinate_s"), weights=(16.0, 24.0))
        s = normalize(raw, Scaling(proper_volume_per_comoving_volume=8,
                                   proper_seconds_per_coordinate_second=2))
        self.assertEqual(s.moments()["number_m3_s"], 2.5)

    def test_reference_density_and_clock(self):
        s = normalize(electron("per_reference_per_coordinate_s"),
                      Scaling(reference_density_m3=10, proper_seconds_per_coordinate_second=2))
        self.assertEqual(s.moments()["number_m3_s"], 25)

    def test_invalid_clock_and_missing_density(self):
        for scaling in (Scaling(), Scaling(target_density_m3=float("nan"))):
            with self.assertRaises(ContractError):
                normalize(electron(), scaling)
        with self.assertRaises(ContractError):
            normalize(electron("per_reference_per_coordinate_s"),
                      Scaling(reference_density_m3=1, proper_seconds_per_coordinate_second=0))

    def test_exposure_is_a_different_type(self):
        s = normalize(electron(), Scaling(target_density_m3=4))
        integrated = s.integrate_constant_exposure(3)
        self.assertEqual(fsum(integrated.counts_m3), 60)
        self.assertFalse(hasattr(integrated, "integrate_constant_exposure"))
        with self.assertRaises(ContractError):
            normalize(integrated, Scaling())

    def test_population_does_not_imply_injection(self):
        pop = electron("number_per_proper_m3")
        m = distribution_moments(pop)
        self.assertEqual(m["number_m3"], 5)
        self.assertIsNone(m["injection_rate"])
        with self.assertRaises(ContractError):
            normalize(pop, Scaling())
        with self.assertRaises(ContractError):
            distribution_moments(electron())

    def test_photon_and_baryon_rest_energy_coordinates(self):
        photons = NativeMeasure("test", "photon", "gamma", "total", 0, (3.0,), (2.0,),
                                "number_per_proper_m3", "bath", "isotropic")
        baryons = NativeMeasure("test", "baryon", "H1:1", "kinetic", 938e6, (3.0,), (2.0,),
                                "number_per_proper_m3", "bath", "isotropic")
        self.assertEqual(distribution_moments(photons)["total_energy_J_m3"], 6 * EV_J)
        self.assertAlmostEqual(distribution_moments(baryons)["total_energy_J_m3"] / EV_J,
                               2 * 938e6 + 6, places=6)
        with self.assertRaises(ContractError):
            replace(photons, energy_coordinate="kinetic")
        with self.assertRaises(ContractError):
            replace(baryons, rest_energy_eV=0)

    def test_nonfinite_negative_and_measure_confusion(self):
        for kwargs in ({"energies_eV": (-1, 2)}, {"weights": (1, float("nan"))},
                       {"weights": (1,)}, {"measure": "occupation_d3p"}, {"angular": "beam"}):
            with self.assertRaises(ContractError):
                replace(electron(), **kwargs)

    def test_source_domain_refuses_redshift_frame_mass_extension(self):
        d = Domain("kinetic", (0, 10), (2.316, 2.479, 2.649), "bath", "isotropic", "zero_recoil")
        good = dict(energy_coordinate="kinetic", energies_eV=(0, 10), redshift=2.479,
                    frame="bath", angular="isotropic", mass_model="zero_recoil")
        d.require(**good)
        for key, value in (("redshift", 2.5), ("frame", "parent_rest"), ("energies_eV", (10.01,)),
                           ("angular", "beam"), ("mass_model", "finite_mass"), ("energy_coordinate", "total")):
            bad = dict(good, **{key: value})
            with self.assertRaises(ContractError):
                d.require(**bad)

    def test_mapping_remains_conditional_and_specific(self):
        m = IsotopeMapping("HeI", "He4:0", "CONDITIONAL_ELEMENTAL_ASSIGNMENT", "declared model")
        m.require("HeI", "He4:0")
        with self.assertRaises(ContractError):
            m.require("HeI", "He3:0")
        with self.assertRaises(ContractError):
            replace(m, status="UNKNOWN").require("HeI", "He4:0")

    def test_invalid_domain_definition_rejected(self):
        for support in ((10, 0), (0, float("inf")), (0, 0)):
            with self.assertRaises(ContractError):
                Domain("kinetic", support, (2.479,), "bath", "isotropic", "zero_recoil")
        d = Domain("kinetic", (0, 1), (0.0,), "bath", "isotropic", "zero_recoil")
        with self.assertRaises(ContractError):
            d.require(energy_coordinate="kinetic", energies_eV=(0,), redshift=False,
                      frame="bath", angular="isotropic", mass_model="zero_recoil")

    def test_source_digest_and_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").write_text("data")
            pin = SourcePin("test/example", "a" * 40, "data", "0" * 64)
            with self.assertRaises(ContractError):
                pin.verify(root)
            with self.assertRaises(ContractError):
                replace(pin, path="../outside").verify(root)

    def test_single_event_energy_number_charge(self):
        e = photo()
        self.assertEqual(e.validate()["charge_residual"], 0)
        self.assertEqual(e.validate()["nuclide_residuals"], {"H1": 0})
        book = EventBook("bath")
        book.append(e)
        self.assertAlmostEqual(book.energy_rates()["fast_kinetic"] / EV_J, 35)

    def test_same_absorption_cannot_be_consumed_twice(self):
        b = EventBook("bath")
        b.append(photo())
        with self.assertRaises(ContractError):
            b.append(photo())

    def test_full_fast_source_plus_full_photoheat_rejected(self):
        e = photo()
        entries = dict(e.energy_J_per_event)
        entries["thermal_kinetic"] = entries["fast_kinetic"]
        with self.assertRaises(ContractError):
            replace(e, energy_J_per_event=tuple(entries.items())).validate()
        # Even a compensating extra photon debit cannot change the primary owner.
        entries["radiation"] -= entries["thermal_kinetic"]
        with self.assertRaises(ContractError):
            replace(e, energy_J_per_event=tuple(entries.items())).validate()

    def test_charge_nucleus_and_duplicate_reservoir_fail(self):
        e = photo()
        wrong = ((Species("He4:0", 0, (("He4", 1),)), -1),) + e.number_per_event[1:]
        with self.assertRaises(ContractError):
            replace(e, number_per_event=wrong).validate()
        with self.assertRaises(ContractError):
            replace(e, number_per_event=e.number_per_event[:-1]).validate()
        with self.assertRaises(ContractError):
            replace(e, energy_J_per_event=e.energy_J_per_event + (("fast_kinetic", 0),)).validate()

    def test_frame_mismatch_and_directional_claim_fail(self):
        with self.assertRaises(ContractError):
            EventBook("different_frame").append(photo())
        with self.assertRaises(ContractError):
            replace(photo(), momentum_status="FULL_ANGULAR_CERTIFIED").validate()

    def test_caloric_partition_preserves_count_energy_without_heat(self):
        s = normalize(electron(), Scaling(target_density_m3=4))
        p = caloric_partition(s, 1)
        self.assertEqual(p["low_closed"]["number_m3_s"], 8)
        self.assertEqual(p["high_open"]["number_m3_s"], 12)
        self.assertAlmostEqual(fsum(p[k]["kinetic_J_m3_s"] for k in ("low_closed", "high_open")) / EV_J, 32)
        self.assertIsNone(p["physical_heating_J_m3_s"])
        self.assertIsNone(p["thermal_particle_transfer_m3_s"])
        self.assertFalse(p["irreversible_assimilation"])

    def test_count_change_is_distinct_from_heat_capacity(self):
        # Monatomic U=(3/2)nkBT. At Q=0 and dn/dt=1, dT/dt=-T/n.
        n, t = 100.0, 10000.0
        eos = CaloricDerivative(1.5 * n * KB_J_K, (("thermal_particles", 1.5 * KB_J_K * t),),
                                "manufactured monatomic ideal gas")
        self.assertAlmostEqual(eos.temperature_rate(0, {"thermal_particles": 1}), -100)
        with self.assertRaises(ContractError):
            eos.temperature_rate(0, {})

    def test_missing_physical_provider_stays_missing(self):
        for process in ("beta_injection", "stopping", "electron_cascade"):
            with self.assertRaises(ContractError):
                require_physical_provider({"status": "SOURCE_INPUT_PENDING"}, process=process,
                                          species="H1:1", energy_eV=1, frame="bath", mass_model="finite_mass")

    def test_beta_requires_evaluated_full_event_inputs(self):
        card = dict(status="ADMITTED_SCOPED", source_pins=["manufactured_test_pin"],
                    process="beta_injection", species=["T:0"], energy_support_eV=[0, 100],
                    frame="parent_rest", mass_model="evaluated")
        with self.assertRaises(ContractError):
            require_physical_provider(card, process="beta_injection", species="T:0", energy_eV=1,
                                      frame="parent_rest", mass_model="evaluated")

    def test_shared_cutoff_flux_is_signed_and_not_assimilation(self):
        x = boundary_flux(cutoff_eV=2, number_flux_m3_s=-3, kinetic_flux_J_m3_s=-6 * EV_J)
        self.assertEqual(x["fast_particle_flux_m3_s"], 3)
        self.assertFalse(x["irreversible_assimilation"])
        with self.assertRaises(ContractError):
            boundary_flux(cutoff_eV=2, number_flux_m3_s=3, kinetic_flux_J_m3_s=3 * EV_J)

    def test_molecular_species_are_explicit_compositions(self):
        hd = Species("HD:0:v0:J0", 0, (("H1", 1), ("D", 1)))
        self.assertEqual(dict(hd.nuclei), {"H1": 1, "D": 1})
        with self.assertRaises(ContractError):
            Species("bad", 0, (("H1", 1), ("H1", 1)))


if __name__ == "__main__":
    unittest.main()
