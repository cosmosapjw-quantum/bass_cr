import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import convolution as c


class TestConvolution(unittest.TestCase):
    def test_exact_source_modules_load(self):
        injection, rudd, kernel = c.modules()
        self.assertEqual(injection.MODEL_ID, "CRP_L17_MD14_v1")
        self.assertEqual(rudd.SOURCE_COMMIT, "e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92")
        self.assertEqual(kernel.Gas().temperature_k, 100)

    def test_source_partitions_number_energy(self):
        parts = c.DirectSource().partitions()
        for field in parts["all"]:
            summed = sum(parts[band][field] for band in
                         ("below_10", "selected_10_1000", "above_1000"))
            self.assertLess(float(c.relative(summed, parts["all"][field])), 2e-12)

    def test_projection_preserves_source_number_and_energy(self):
        source = c.DirectSource()
        generator = c.modules()[-1].assemble(16)
        state, norm = source.projected(generator)
        obs = generator.observe(state)
        moments = source.moments(10, 1000)
        self.assertLess(float(c.relative(obs["number_ledger"]*norm, moments["number_m3_s2"])), 2e-11)
        self.assertLess(float(c.relative(obs["energy_ledger_eV"]*norm, moments["kinetic_eV_m3_s2"])), 2e-11)
        self.assertGreaterEqual(state.min(), 0)

    def test_birth_rule_and_causal_ages(self):
        for order in (8, 16, 32):
            births, ages, weights = c.birth_rule(c.T_END, order)
            np.testing.assert_allclose(births+ages, c.T_END, rtol=0, atol=0)
            self.assertTrue(np.all(ages >= 0))
            self.assertTrue(np.all(births >= 0))
            self.assertLess(float(c.relative(weights @ births, .5*c.T_END**2)), 1e-14)

    def test_zero_time_and_source_off(self):
        for result in (c.convolve(0, 16, 8), c.convolve(c.T_END, 16, 8, False)):
            self.assertEqual(len(result["cohorts"]), 0)
            self.assertTrue(all(value == 0 for obs in result["observables"] for value in obs.values()))
            self.assertTrue(all(value == 0 for row in result["injected"] for value in row.values()))

    def test_nonfinite_out_of_domain(self):
        for value in (-1, float("nan"), float("inf"), c.T_END+1, True):
            with self.assertRaises(ValueError):
                c.birth_rule(value, 8)
        with self.assertRaises(ValueError):
            c.birth_rule(1, 64)
        for value in (-1, 1000.1, float("nan")):
            with self.assertRaises(ValueError):
                c.DirectSource().spectrum(value)

    def test_observation_uses_cohort_grid(self):
        kernel = c.modules()[-1]
        generator = kernel.assemble(16)
        initial = generator.impulse(20)
        evolved = kernel.evolve(generator, initial, 1e10)
        correct = c.observation_vector(generator, evolved)
        wrong = c.observation_vector(generator, np.asarray(evolved))
        self.assertGreater(abs(correct[c.OBSERVABLES.index("active_energy_eV")]
                               - wrong[c.OBSERVABLES.index("active_energy_eV")]), .1)
        self.assertLess(float(c.relative(correct[c.OBSERVABLES.index("energy_ledger_eV")], 20.0)), 2e-11)

    def test_arrival_paneling_has_exact_cutoff_step_integral(self):
        kernel = c.modules()[-1]
        generator = kernel.assemble(128)
        birth, ages, weights, boundaries = c.arrival_birth_rule(c.T_END, 16, generator)
        self.assertEqual(len(boundaries)-1, 5)
        arrivals = kernel.cooling_time(generator.grid, generator.gas)
        selected = arrivals[(arrivals > 0) & (arrivals < c.T_END)]
        np.testing.assert_array_equal(boundaries[1:-1], np.sort(c.T_END-selected))
        for tau in selected:
            got = np.dot(weights, birth*(ages >= tau))
            expected = .5*(c.T_END-tau)**2
            self.assertLess(float(c.relative(got, expected)), 1e-14)


if __name__ == "__main__":
    unittest.main()
