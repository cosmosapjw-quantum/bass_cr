"""Focused numerical checks for new coupling and analytic Jacobian, no ODEs."""
import copy
import math
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from coupled_model import CoupledFactory
from mass_shell_derivatives import packet_derivatives


class ConstantElectron:
    def __init__(self, value):
        self.value = value
    def density(self, a):
        return self.value


class CouplingChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = CoupledFactory()
        cls.metrics = {}

    def test_kinetic_rhs_unchanged_at_same_electron_density(self):
        model = self.factory.build(.3, -5e-4, 1.2e-3)
        y = model.initial_state()
        for eta in (0., .4, 1.4):
            y[1] = .06 * eta
            y[model.nk + 1] = .7
            y[model.nk + 2] = .3
            f = model.fields(eta, y)
            old = copy.copy(model.kinetic)
            old.ne_source = ConstantElectron(f["n_e_cm3"])
            np.testing.assert_array_equal(model.rhs(eta, y)[:model.nk], old.rhs(eta, y[:model.nk]))
        self.metrics["original_RHS_bitwise_equal_points"] = 3
        self.metrics["original_RHS_equal_scalar_values"] = 120

    def test_full_block_jacobian_against_central_difference(self):
        model = self.factory.build(-.3, 4e-4, -1e-3)
        y = model.initial_state()
        y[1] = -.04
        # Not an ODE trajectory: a finite, admissible warm ionized check state.
        for lo, hi in ((1, 3), (3, 5), (5, 7), (7, 10), (10, 13), (13, 17), (17, 21)):
            if lo == 5:  # T has zero population in the actual late-time input.
                continue
            y[model.nk + lo:model.nk + hi] = 1.0 / (hi-lo)
        eta = math.log(21 / 7)
        jac = model.jacobian(eta, y)
        columns = list(range(model.size))
        columns.remove(3)  # Invariant u=0 slot: negative trial violates original source domain.
        worst = 0.
        for j in columns:
            delta = 2e-6 * max(1., abs(y[j]))
            yp, ym = y.copy(), y.copy()
            yp[j] += delta
            ym[j] -= delta
            finite = (model.rhs(eta, yp)-model.rhs(eta, ym))/(2*delta)
            scale = np.maximum(1., np.maximum(abs(finite), abs(jac[:, j])))
            worst = max(worst, float(np.max(abs(finite-jac[:, j])/scale)))
        self.assertLess(worst, 3e-6)
        self.metrics["jacobian_finite_difference_max_scaled_difference"] = worst
        self.metrics["jacobian_tested_entries"] = model.size * len(columns)

    def test_packet_and_radiation_energy_identities(self):
        model = self.factory.build(.6, -.0005, .0012)
        y = model.initial_state()
        eta = .5
        y[1] = .1
        q = model.fields(eta, y)
        dy = model.rhs(eta, y)
        shell = packet_derivatives(model.kinetic.momentum, eta, q["b"], q["s"]/q["H"])
        self.assertLess(abs(shell["energy_conservation_residual"]), 2e-15)
        n = model.kinetic.n
        obj = model.kinetic
        rad_deriv = (obj.omega_gamma*(dy[4]-4*y[4])
                     +obj.omega_nu*(dy[4+2*n]-4*y[4+2*n]))/q["a"]**4
        res = rad_deriv+4*q["rad_energy_norm"]+6*q["s"]/q["H"]*q["Pi_radiation_norm"]
        self.assertLess(abs(res)/q["rad_energy_norm"], 2e-13)

    def test_z2_domain_does_not_mutate_original_lock(self):
        self.assertAlmostEqual(self.factory.builder.template.source.aend, 1/3)
        from builder import IndependentStressBuilder
        original = IndependentStressBuilder()
        self.assertAlmostEqual(original.template.source.aend, 1/5)

    def test_initial_realizability_and_no_false_species_zero(self):
        model = self.factory.build(-.6, -.0005, -.0012)
        y = model.initial_state()
        self.assertEqual(y.size, 62)
        self.assertEqual(model.atomic.physical_abundances(y[model.nk:-1]).size, 21)
        self.assertGreater(model.mapping["continuum_min_W_m"], 0)
        self.assertGreater(model.mapping["continuum_min_W_r"], 0)
        self.assertGreater(model.fields(0., y)["n_e_cm3"], 0)


if __name__ == "__main__":
    unittest.main()
