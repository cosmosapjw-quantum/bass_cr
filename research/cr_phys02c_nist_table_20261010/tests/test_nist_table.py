"""Independent literals from NIST Tables 1 and 2, not provider-derived fixtures."""

from dataclasses import FrozenInstanceError
from decimal import Decimal
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nist_table import EnergyDomainError, NistTableProvider, UnknownTransitionError, verify_sources


ENERGIES = (1000, 1500, 2000, 3000)
FIXTURES = {
    "HI_1s_2p": ("0.12463", "0.09094", "0.07236", "0.05214"),
    "HeI_1s2_1S_1s2p_1P": ("0.03116", "0.02333", "0.01885", "0.01383"),
}


class TestNistTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provider = NistTableProvider.from_local_sources()

    def assert_relative(self, actual, reference):
        self.assertTrue(math.isclose(actual, float(reference), rel_tol=1e-14, abs_tol=0),
                        (actual, reference))

    def test_local_source_identities(self):
        observed = verify_sources()
        self.assertEqual(observed["sources/j74sto.pdf"],
                         "2492e6923503515bc6bf310da043eb64f72f3b2e609991fa037065a8afc966d1")
        self.assertEqual(observed["sources/table.json"],
                         "68ed530440bedd7c91851fd941c82857786126d8a4f358d5cad4dcb8c9ef9a54")

    def test_all_eight_source_entries(self):
        for transition, values in FIXTURES.items():
            for energy, expected in zip(ENERGIES, values):
                with self.subTest(transition=transition, energy=energy):
                    result = self.provider.evaluate(transition, energy)
                    self.assertEqual(result.cross_section_angstrom2, float(expected))
                    self.assert_relative(result.cross_section_cm2, Decimal(expected) * Decimal("1e-16"))

    def test_all_six_linear_midpoints(self):
        for transition, values in FIXTURES.items():
            for index in range(3):
                energy = (ENERGIES[index] + ENERGIES[index + 1]) / 2
                expected = (Decimal(values[index]) + Decimal(values[index + 1])) / 2
                with self.subTest(transition=transition, energy=energy):
                    result = self.provider.evaluate(transition, energy)
                    self.assert_relative(result.cross_section_angstrom2, expected)
                    self.assert_relative(result.cross_section_cm2, expected * Decimal("1e-16"))

    def test_units_and_explicit_channel_energies(self):
        expected_channels = {
            "HI_1s_2p": ("H I 1s 2S", "H I 2p 2P", 10.204),
            "HeI_1s2_1S_1s2p_1P": ("He I 1s2 1S", "He I 1s2p 1P", 21.218),
        }
        for transition, (initial, final, delta_e) in expected_channels.items():
            with self.subTest(transition=transition):
                result = self.provider.evaluate(transition, 1500)
                self.assertEqual((result.transition_id, result.initial_state, result.final_state,
                                  result.excitation_energy_eV), (transition, initial, final, delta_e))
                self.assertEqual(result.cross_section_unit, "cm^2")
                self.assertEqual(result.incident_energy_eV, 1500)
                self.assertEqual(result.claim, "SOURCE_BACKED_ATOMIC_COMPONENT_ONLY")
                self.assertNotEqual(result.excitation_energy_eV, 19.819614683951094)

    def test_inclusive_endpoints_and_adjacent_rejection(self):
        for transition in FIXTURES:
            for endpoint in (1000.0, 3000.0):
                self.assertGreater(self.provider.evaluate(transition, endpoint).cross_section_cm2, 0)
            for energy in (math.nextafter(1000, -math.inf), math.nextafter(3000, math.inf), 0, 1e5):
                with self.subTest(transition=transition, energy=energy):
                    with self.assertRaises(EnergyDomainError):
                        self.provider.evaluate(transition, energy)

    def test_nonfinite_and_nonnumeric_rejection(self):
        for energy in (math.nan, math.inf, -math.inf, "1000", None, True, 1000 + 0j, 10**400):
            with self.subTest(energy=energy):
                with self.assertRaises(EnergyDomainError):
                    self.provider.evaluate("HI_1s_2p", energy)

    def test_unknown_and_old_transition_rejection(self):
        for transition in ("HI", "HeI", "HeI_23s", "HeII", ""):
            with self.subTest(transition=transition):
                with self.assertRaises(UnknownTransitionError):
                    self.provider.evaluate(transition, 2000)

    def test_checked_values_positive_and_interpolation_is_convex(self):
        for transition, values in FIXTURES.items():
            for index in range(3):
                result = self.provider.evaluate(transition, (ENERGIES[index] + ENERGIES[index + 1]) / 2)
                endpoints = (float(values[index]), float(values[index + 1]))
                self.assertGreater(result.cross_section_cm2, 0)
                self.assertGreaterEqual(result.cross_section_angstrom2, min(endpoints))
                self.assertLessEqual(result.cross_section_angstrom2, max(endpoints))

    def test_returned_channel_cannot_be_silently_relabelled(self):
        result = self.provider.evaluate("HeI_1s2_1S_1s2p_1P", 1500)
        with self.assertRaises(FrozenInstanceError):
            result.transition_id = "HeI_23s"


if __name__ == "__main__":
    unittest.main(verbosity=2)
