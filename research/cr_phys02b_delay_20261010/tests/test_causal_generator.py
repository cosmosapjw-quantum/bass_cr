"""Focused acceptance tests for the conditional fixed-gas causal sidecar."""

import ast
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import causal_generator as c


def upstream_rates():
    tree = ast.parse((c.ROOT / "vendor/darkhistory/physics.py").read_text())
    names = {"coll_exc_xsec", "coll_ion_xsec", "elec_heating_engloss_rate"}
    funcs = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name in names]
    if len(funcs) != 3:
        raise AssertionError("UPSTREAM_FUNCTION_IDENTITIES")
    gas = c.Gas()
    env = dict(np=np, rydberg=c.RYDBERG, He_ion_eng=c.ION[1],
               lya_eng=c.LYA, He_exc_eng={"23s": c.EXC[1]},
               bohr_rad=c.BOHR, me=c.ME, hbar=c.HBAR, c=c.C,
               alpha=c.ALPHA, nH=gas.n_h_m3 * 1e-6)
    exec(compile(ast.Module(body=funcs, type_ignores=[]), "pinned_physics_rates", "exec"), env)
    return env


class CausalGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = c.assemble(32)

    def test_source_bytes_and_raw_rate_parity(self):
        c.verify_sources()
        raw = upstream_rates()
        e = np.unique(np.r_[np.geomspace(10, 1000, 61), c.ION, c.EXC])
        for sp in c.SPECIES:
            np.testing.assert_allclose(c.ionization_xsec(e, sp),
                                       raw["coll_ion_xsec"](e, sp), rtol=3e-15, atol=0)
            np.testing.assert_allclose(c.excitation_xsec(e, sp),
                                       raw["coll_exc_xsec"](e, sp), rtol=3e-15, atol=0)
        gas = c.Gas()
        xe = gas.electron_cm3 / (gas.n_h_m3 * 1e-6)
        np.testing.assert_allclose(c.coulomb_loss(e, gas),
                                   raw["elec_heating_engloss_rate"](e, xe, 1),
                                   rtol=3e-15, atol=0)

    def test_density_helium_and_clock_units(self):
        gas = c.Gas()
        self.assertAlmostEqual(gas.n_he_m3, 11.542553191489361)
        self.assertAlmostEqual(gas.electron_cm3, (1.4 + 0.11542553191489361) * 1e-6)
        n_hii_per_h = gas.x_hii_per_h
        n_heii_per_h = gas.n_he_m3 / gas.n_h_m3 * gas.x_heii_per_he
        self.assertAlmostEqual(gas.electron_cm3 / (gas.n_h_m3 * 1e-6),
                               n_hii_per_h + n_heii_per_h)
        # One column's ion event rate is the absolute n_target sigma v in s^-1.
        j = np.where(self.g.grid == 100.0)[0][0]
        expected = gas.target_cm3[0] * c.ionization_xsec(100., "HI") * c.velocity(100.)
        self.assertAlmostEqual(self.g.matrix[self.g.n, j] / expected, 1.0)

    def test_pair_branching_and_cutoff_moments(self):
        for e in (20., 100., 1000.):
            for k in range(3):
                if e > c.ION[k]:
                    n, cut_n, cut_e = c.ionization_daughters(self.g.grid, e, k, 8)
                    self.assertAlmostEqual(float(n.sum() + cut_n), 2.0, places=13)
                    self.assertAlmostEqual(float(self.g.grid @ n + cut_e),
                                           e - c.ION[k], places=10)
                    self.assertGreaterEqual(n.min(), 0)
                    self.assertGreater(cut_n, 0)

    def test_generator_number_energy_and_metzler(self):
        a = self.g.matrix.toarray()
        np.fill_diagonal(a, 0)
        self.assertGreaterEqual(a.min(), 0)
        wn, we = self.g.weights()
        scale_n = np.asarray(abs(self.g.matrix).sum(axis=0)).ravel()
        scale_e = np.asarray(abs(self.g.matrix).T @ abs(we)).ravel()
        for weights, scale in ((wn, scale_n), (we, scale_e)):
            residual = np.abs(weights @ self.g.matrix)
            self.assertLess(np.max(residual[scale > 0] / scale[scale > 0]), 2e-14)

    def test_impulse_causality_positive_evolution_and_ledgers(self):
        for e in (20., 100., 1000.):
            y0 = self.g.impulse(e)
            self.assertTrue(np.array_equal(c.evolve(self.g, y0, 0), y0))
            self.assertEqual(float(y0[self.g.n:].sum()), 0.0)
            for t in (1e10, 1e11):
                y = c.evolve(self.g, y0, t)
                self.assertGreaterEqual(y.min(), 0)
                obs = self.g.observe(y)
                self.assertAlmostEqual(obs["number_ledger"], 1., places=11)
                self.assertLess(abs(obs["energy_ledger_eV"] / e - 1), 2e-11)
                if e == 20. and t > 9.456523330348772e10:
                    self.assertEqual(obs["active_energy_eV"], 0.)
                else:
                    self.assertGreater(obs["active_energy_eV"], 0)
                self.assertGreater(obs["binding_energy_eV"] + obs["excitation_energy_eV"]
                                   + obs["coulomb_heat_eV"], 0)
        # Small-t collision populations agree with the dimensional generator;
        # the continuous energy change is separately accounted as drag heat.
        y0 = self.g.impulse(100.)
        dt = 1e-5 / self.g.rho
        first = self.g.matrix @ y0
        slope = (c.evolve(self.g, y0, dt) - y0) / dt
        self.assertLess(np.max(np.abs(slope[:self.g.n + 6] - first[:self.g.n + 6]))
                        / np.max(np.abs(first)), 1e-5)
        self.assertAlmostEqual(float(slope[-3] / c.coulomb_loss(100., self.g.gas)),
                               1., places=5)

    def test_characteristic_continuum_arrival_and_drag_moments(self):
        tau = 9.456523330348772e10
        self.assertLess(abs(float(c.cooling_time(20., self.g.gas)) / tau - 1), 2e-11)
        for t in (0.5 * tau, tau * (1 + 1e-12), 1e11):
            grid = c.characteristic_grid(self.g.grid, self.g.gas, t)
            self.assertTrue(np.all(np.diff(grid) >= 0))
            self.assertTrue(np.all(grid <= self.g.grid))
            y = c.evolve(self.g, self.g.impulse(20.), t)
            obs = self.g.observe(y)
            self.assertLess(abs(obs["energy_ledger_eV"] / 20 - 1), 2e-11)
            self.assertLess(abs(obs["number_ledger"] - 1), 2e-11)
            if t > tau:
                self.assertEqual(obs["active_energy_eV"], 0.)
                self.assertEqual(obs["active_electron_number"], 0.)

    def test_off_is_exact_and_cutoff_is_not_heat(self):
        y0 = self.g.impulse(100.)
        self.assertTrue(np.array_equal(c.evolve(self.g, y0, 1e13, enabled=False), y0))
        cutoff = self.g.impulse(10.)
        y = c.evolve(self.g, cutoff, 1e13)
        self.assertTrue(np.array_equal(y, cutoff))
        obs = self.g.observe(y)
        self.assertEqual(obs["cutoff_energy_eV"], 10.)
        self.assertEqual(obs["coulomb_heat_eV"], 0.)

    def test_domain_fail_closed(self):
        for e in (9.99, 1000.01, np.nan):
            with self.assertRaises(ValueError):
                c.ionization_xsec(e, "HI")
            with self.assertRaises(ValueError):
                self.g.impulse(e)
        with self.assertRaises(ValueError):
            c.evolve(self.g, self.g.impulse(100.), -1)
        with self.assertRaises(ValueError):
            c.evolve_ssprk2(self.g, self.g.impulse(100.), 1e13, 1)
        with self.assertRaises(ValueError):
            c.Gas(temperature_k=50000)

    def test_nested_grid(self):
        for n in (128, 256):
            g1, g2 = c.make_grid(n), c.make_grid(2 * n)
            self.assertLess(np.max(np.abs(g1 - g2[::2])), 2e-12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
