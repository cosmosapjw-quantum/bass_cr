"""Focused initial-condition/source-algebra checks; zero ODE solves."""
import hashlib
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import builder as b

RECORD = {'scope': 'initial conditions, original source fields/RHS, no ODE',
          'new_ODE_solves': 0, 'checks': {}, 'cases': {}}


class BuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = b.IndependentStressBuilder()

    def test_01_radiation_matter_opposing_and_flrw_targets(self):
        cases = {'flrw': (0., 0., 0.), 'radiation_only': (.013, 0., -.000213),
                 'matter_only': (-.013, .000217, 0.),
                 'opposing': (0., .000219, -.000219),
                 'mixed_same_sign': (.009, -.000223, -.000211)}
        with patch.object(b.parent.CanonicalFVSpecies, 'integrate',
                          side_effect=AssertionError('ODE forbidden in focused builder checks')):
            for name, values in cases.items():
                obj, receipt = self.builder.build(*values)
                state = obj.initial_state(); d = obj.fields(0., state)
                self.assertEqual(state.shape, (40,))
                self.assertLess(max(receipt['axis_absolute_errors'].values()), 2e-13)
                self.assertGreaterEqual(receipt['continuum_min_W_m'], 0)
                self.assertGreater(receipt['continuum_min_W_r'], 0)
                self.assertLess(receipt['Hamiltonian_relative_residual'], 2e-13)
                self.assertLess(abs(receipt['massive_initial_rho_normalized']-1), 2e-13)
                self.assertEqual(d['N_gamma'][0], 1)
                self.assertEqual(d['N_nu'][0], 1)
                self.assertEqual(obj.ne_source, None)
                if name == 'flrw':
                    rhs = obj.rhs(0., state)
                    self.assertEqual(state[1], 0)
                    self.assertEqual(state[2], 0)
                    self.assertLess(abs(rhs[2]), 2e-13)
                    self.assertLess(np.max(abs(rhs[4:])), 2e-13)
                if name == 'opposing':
                    a = receipt['actual']
                    self.assertLess(a['Pi_tot_F'], 2e-13)
                    self.assertGreater(a['Pi_m_F']+a['Pi_r_F'], 4e-4)
                RECORD['cases'][name] = receipt
        RECORD['checks']['initial_targets_and_flrw'] = True

    def test_02_fresh_weight_and_energy_norm_match_original_constructor(self):
        for A in (-1., -.43, 0., .61, 2.):
            fast = b._new_momentum(A, True)
            slow = b.parent.CanonicalMomentumFV(30., A, 24, 12, gauss_order=3)
            self.assertEqual(fast.reference_energy_norm, slow.reference_energy_norm)
            self.assertEqual(fast.total_cell_number, slow.total_cell_number)
            np.testing.assert_array_equal(fast.cell_numbers, slow.cell_numbers)
            np.testing.assert_array_equal(fast._numbers, slow._numbers)
            for eta, bb in ((0., 0.), (.3, -.007), (1.2, .009)):
                self.assertEqual(fast.moments(eta, bb), slow.moments(eta, bb))
                m = fast.moments(eta, bb)
                self.assertAlmostEqual(m.ncell_number*math.exp(3*eta)/fast.total_cell_number, 1., places=14)
            self.assertTrue(np.all(fast.distribution_change_deta() == 0))
            self.assertFalse(fast._numbers.flags.writeable)
        RECORD['checks']['fresh_original_distribution_and_exact_reuse'] = True

    def test_03_original_full_source_rhs_identity(self):
        for targets in ((.013, .000213, -.000217), (-.009, -.000219, .000211), (0., .000223, 0.)):
            obj, r = self.builder.build(*targets)
            original = b.parent.CanonicalFVSpecies(
                obj.source, 2.7255, 8, Sigma_ref=r['source_Sigma_ref_half'],
                orientation=r['source_orientation'], kappa_gamma=r['k_gamma'],
                kappa_nu=r['k_nu'], ne_source=None, mass_fraction=.1,
                massive_A=r['A_m'], mass_over_Tref=30., radial_cells=24,
                angular_cells=12, subcell_gauss_order=3)
            np.testing.assert_array_equal(obj.initial_state(), original.initial_state())
            for eta, bb in ((0., 0.), (.4, .003), (1.1, -.004)):
                y = obj.initial_state(); y[1] = bb
                np.testing.assert_array_equal(obj.rhs(eta, y), original.rhs(eta, y))
        RECORD['checks']['original_40_state_rhs_bitwise_at_9_states'] = True

    def test_04_tensor_normalization_units_and_gamma_nu_sum(self):
        obj, r = self.builder.build(.017, .000231, -.000227)
        d = obj.fields(0., obj.initial_state()); a = r['actual']
        shear_tensor = np.diag([-d['s'], -d['s'], 2*d['s']])
        self.assertAlmostEqual(np.linalg.norm(shear_tensor)/d['H'], a['Sigma_F'], places=14)
        tensors = {}
        for sector, key in (('m', 'Pi_matter_J_m3'), ('gamma', 'Pi_gamma_J_m3'), ('nu', 'Pi_nu_J_m3')):
            p = d[key]; tensors[sector] = np.diag([-p, -p, 2*p])
        tensors['r'] = tensors['gamma'] + tensors['nu']
        tensors['tot'] = tensors['m'] + tensors['r']
        for sector, tensor in tensors.items():
            value = b.KAPPA_ENERGY_SI*np.linalg.norm(tensor)/(d['H']/b.parent.C_SI)**2
            self.assertAlmostEqual(value, a['Pi_'+sector+'_F'], places=14)
            self.assertAlmostEqual(a['Pi_'+sector+'_F']/a['Pi_'+sector+'_half'], math.sqrt(2), places=14)
        self.assertAlmostEqual(a['signed_Pi_r_F'], a['signed_Pi_gamma_F']+a['signed_Pi_nu_F'], places=14)
        RECORD['checks']['direct_tensor_frobenius_SI_time_conversion'] = True

    def test_05_source_domain_refusals_and_endpoints(self):
        for vals in ((0., .1, 0.), (0., 0., .1), (math.sqrt(6), 0., 0.), (0., math.nan, 0.)):
            with self.assertRaises((ValueError, ArithmeticError)):
                self.builder.build(*vals)
        _, r = self.builder.build(.013, 0., 0.)
        for target in r['attainable_matter_signed_full']:
            obj, rr = self.builder.build(.013, target, 0.)
            self.assertIn(rr['A_m'], (-1., 2.))
            self.assertGreaterEqual(rr['continuum_min_W_m'], 0)
        RECORD['checks']['finite_domain_informative_refusals_and_boundary_weights'] = True

    def test_06_shared_parent_is_immutable(self):
        template = self.builder.template
        before = hashlib.sha256(template.momentum._numbers.tobytes()).hexdigest()
        for params in ((.01, .0001, 0.), (-.01, -.0001, .0002)):
            obj, _ = self.builder.build(*params)
            self.assertIs(obj.energy_matrix, template.energy_matrix)
            self.assertIs(obj.number_matrix, template.number_matrix)
            self.assertIsNot(obj.momentum, template.momentum)
        self.assertEqual(before, hashlib.sha256(template.momentum._numbers.tobytes()).hexdigest())
        self.assertEqual(template.momentum.amplitude, 0.)
        self.assertFalse(template.energy_matrix.flags.writeable)
        b.parent.verify_source()
        RECORD['checks']['parent_source_template_and_immutable_matrix_reuse'] = True


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BuilderTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    RECORD['status'] = 'PASS_SCOPED' if result.wasSuccessful() else 'FAIL'
    RECORD['groups_run'] = result.testsRun
    RECORD['failures'] = len(result.failures)
    RECORD['errors'] = len(result.errors)
    RECORD['identity'] = BuilderTests.builder.identity()
    out = Path(__file__).resolve().parent / 'checks'
    out.mkdir(exist_ok=True)
    (out/'builder_checks.json').write_text(json.dumps(RECORD, indent=2, allow_nan=False)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
