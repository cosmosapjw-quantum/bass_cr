import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import coulomb_ledger as loss


class CoulombTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coarse = loss.build_ledger(48, 8, 8)
        cls.fine = loss.build_ledger(64, 12, 12)

    def test_exact_source_bytes(self):
        identity = loss.source_identity()
        self.assertEqual(len(identity), 6)

    def test_cgs_si_positive_parity(self):
        energies = np.geomspace(1e6, 1e7, 17)
        ne = loss.electron_density()
        si = loss.proton_loss_si_J_s(energies, ne)
        cgs = loss.proton_loss_cgs_J_s(energies, ne)
        self.assertTrue(np.all(np.isfinite(si) & (si > 0)))
        self.assertLessEqual(float(np.max(np.abs(cgs/si-1))), 3e-14)

    def test_upstream_mks_is_negative_control(self):
        energy = np.array([1e6, 4e6, 1e7])
        ne = loss.electron_density()
        corrected = loss.proton_loss_si_J_s(energy, ne)
        raw = loss.upstream_mks_loss_negative_control_J_s(energy, ne)
        expected = (4*math.pi*loss.EPS0)**2
        self.assertLess(float(np.max(np.abs(raw/corrected/expected-1))), 8e-16)
        self.assertTrue(np.all(raw/corrected < 2e-20))

    def test_zero_ne_age_and_off(self):
        self.assertEqual(float(loss.proton_loss_si_J_s(1e6, 0)), 0.0)
        self.assertEqual(float(loss.proton_loss_cgs_J_s(1e6, 0)), 0.0)
        with patch.object(loss, "proton_loss_si_J_s", side_effect=AssertionError("kernel called")):
            for kw in ({"dt_s": 0}, {"enabled": False}):
                ledger = loss.build_ledger(**kw)
                self.assertEqual(ledger["plasma_transferred_energy_j_m3_s"], 0.0)
                self.assertEqual(ledger["active_cr_energy_j_m3"], 0.0)
                self.assertEqual(ledger["population_node_count"], 0)

    def test_charge_neutrality_includes_he_electrons(self):
        n_he = 140*.248/(4*(1-.248))
        ne = loss.electron_density()
        self.assertAlmostEqual(ne, 1.4 + .01*n_he, delta=3e-15)
        self.assertAlmostEqual(loss.electron_density(x_heii=0, x_heiii=.01),
                               1.4+.02*n_he, delta=3e-15)
        complete = float(loss.proton_loss_si_J_s(4e6, ne))
        hydrogen_only = float(loss.proton_loss_si_J_s(4e6, 1.4))
        self.assertGreater(complete/hydrogen_only-1, .07)

    def test_interval_additivity_and_refinement(self):
        key = "plasma_transferred_energy_j_m3_s"
        low = loss.build_ledger(64, 12, 12, window_eV=(1e6, 4e6))
        high = loss.build_ledger(64, 12, 12, window_eV=(4e6, 1e7))
        self.assertLess(abs(math.fsum([low[key], high[key]])/self.fine[key]-1), 3e-13)
        self.assertLessEqual(abs(self.coarse[key]/self.fine[key]-1), 2e-6)
        self.assertEqual(self.fine["solver_intervals"], 0)
        self.assertEqual(self.fine["deposition_status"], "NOT_COMPUTED")
        self.assertTrue(math.isfinite(self.fine[key]) and self.fine[key] > 0)

    def test_domain_fail_closed(self):
        for energy in (0, 9e5, 1.1e7, math.nan, math.inf):
            with self.assertRaises(ValueError):
                loss.proton_loss_si_J_s(energy, 1.0)
        for ne in (-1, math.inf, math.nan, True):
            with self.assertRaises(ValueError):
                loss.proton_loss_si_J_s(1e6, ne)
        for kw in ({"x_heiii": 1.0, "x_heii": .1}, {"n_h_m3": -1}, {"y_he": 1}):
            with self.assertRaises(ValueError):
                loss.electron_density(**kw)
        for kw in ({"dt_s": -1}, {"enabled": 1}, {"energy_order": 1}):
            with self.assertRaises(ValueError):
                loss.build_ledger(**kw)


if __name__ == "__main__":
    unittest.main()
