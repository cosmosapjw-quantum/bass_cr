"""Bounded synthetic regression; never starts an operator/native evaluation."""
import unittest
import numpy as np
import scipy
from numerical_audit import (audit_pencil, decimal_pencil_eigenvalues,
                             conditioning_cases, load_historical_probe, saved_physical_audit)


class GeneralizedRhoSolverTest(unittest.TestCase):
    def test_eight_archived_physical_matrices_no_native_execution(self):
        rows=saved_physical_audit()
        self.assertEqual([r['z_a0'] for r in rows],[-32.,-24.,-20.,-16.,16.,20.,24.,32.])
        for row in rows:
            with self.subTest(z=row['z_a0']):
                r=row['pencil_audit']
                self.assertLess(r['S_condition'],1.02)
                self.assertLess(row['archived_rho_relative_discrepancy'],1e-12)
                self.assertLess(r['rho_relative_discrepancy'],1e-12)
                for path in ('path_a','path_b'):
                    self.assertLess(r[path]['max_normwise_backward_error'],2e-13)

    def test_project_scipy_version(self):
        self.assertEqual(scipy.__version__, '1.17.0')

    def test_conditioning_sweep_independent_paths(self):
        for case in conditioning_cases():
            with self.subTest(case=case['name']):
                r = audit_pencil(case['S'], case['W'])
                for path in ('path_a','path_b'):
                    # Stress regression, not a uniform theorem/certificate.
                    # Other eigenpairs can deteriorate despite accurate rho.
                    self.assertLess(r[path]['max_normwise_backward_error'],
                                    max(2e-13,64*np.finfo(float).eps*r['S_condition']))
                    self.assertLess(r[path]['rho_eigenpair_normwise_backward_error'],2e-13)
                self.assertLess(r['rho_relative_discrepancy'],
                                max(2e-13, 32*np.finfo(float).eps*r['S_condition']))

    def test_decimal_reference_uses_rounded_input_pencil(self):
        for case in conditioning_cases(dimension=2):
            r = audit_pencil(case['S'], case['W'])
            ref = decimal_pencil_eigenvalues(case['S'], case['W'])
            reference_rho = max(abs(float(x)) for x in ref)
            for path in ('path_a', 'path_b'):
                rel = abs(r[path]['rho']-reference_rho)/reference_rho
                self.assertLess(rel, max(2e-13, 32*np.finfo(float).eps*r['S_condition']))

    def test_exact_diagonal_reference(self):
        ref = decimal_pencil_eigenvalues(np.diag([1., .25]), np.diag([2., -.75]))
        self.assertEqual([float(x) for x in ref], [-3., 2.])

    def test_singular_indefinite_and_nonhermitian_fail_without_mutation(self):
        for S in [np.diag([1., 0.]), np.diag([1., -1e-14]),
                  np.array([[1., 1.], [1., 1.]])]:
            old = S.copy()
            with self.assertRaises((ValueError, np.linalg.LinAlgError)):
                audit_pencil(S, np.eye(2))
            np.testing.assert_array_equal(S, old)
        with self.assertRaises(ValueError):
            audit_pencil(np.eye(2), np.array([[1., .01], [0., 1.]]))

    def test_scale_relative_hermiticity_and_nonfinite_guard(self):
        with self.assertRaises(ValueError):
            audit_pencil(np.eye(2), 1e-20*np.array([[1., .01], [0., 1.]]))
        with self.assertRaises(ValueError):
            audit_pencil(np.eye(2), np.array([[np.nan, 0.], [0., 1.]]))

    def test_existing_rate_probe_matches_both_solver_paths(self):
        probe = load_historical_probe()
        for kappa in [1., 1e4]:
            case = next(c for c in conditioning_cases() if c['target_condition'] == kappa)
            n = len(case['S']); rng = np.random.default_rng(702)
            z = rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))
            H = (z+z.conj().T)/2
            D = (rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))*.01
            J = np.eye(n, dtype=complex)[:, [0,2]]
            output = probe.rate_matrices(case['S'], H, D, J, hbar=1.)
            defect=np.linalg.norm(output['W']-output['W'].conj().T,2)/np.linalg.norm(output['W'],2)
            self.assertLess(defect,1e-11)
            # Disclose projection instead of relaxing guarded input admission.
            r = audit_pencil(case['S'], (output['W']+output['W'].conj().T)/2)
            self.assertLess(abs(output['rho']-r['path_a']['rho'])/r['path_a']['rho'], 1e-10)


if __name__ == '__main__': unittest.main()
