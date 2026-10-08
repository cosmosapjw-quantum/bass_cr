import unittest
import numpy as np
from numerical_audit import (covariance_case, metric_projected_coupling_norm,
                             raw_block_counterexample)


class BasisCovarianceTest(unittest.TestCase):
    def test_twelve_complex_changes_preserve_quantities_and_projectors(self):
        for seed in range(12):
            r = covariance_case(seed)
            self.assertLess(r['T_condition'], 5.1)
            for name, defect in r['relative_defects'].items():
                with self.subTest(seed=seed, quantity=name): self.assertLess(defect, 2e-11)

    def test_raw_block_is_not_basis_invariant(self):
        r = raw_block_counterexample()
        self.assertEqual(r['raw_block_before'], 1.)
        self.assertAlmostEqual(r['raw_block_after'], .1)
        self.assertAlmostEqual(r['metric_coupling_before'], 1.)
        self.assertAlmostEqual(r['metric_coupling_after'], 1.)

    def test_metric_coupling_is_subspace_basis_invariant(self):
        rng = np.random.default_rng(809); n=5
        Z=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))
        S=Z.conj().T@Z+np.eye(n)
        K=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))
        U=np.eye(n,dtype=complex)[:,:2]; V=np.eye(n,dtype=complex)[:,2:]
        left=np.array([[2., .3j], [.2, 1.]])
        right=np.array([[1., .2j, 0.], [0., 2., .1], [.2, 0., .7]])
        a=metric_projected_coupling_norm(S,K,U,V)
        b=metric_projected_coupling_norm(S,K,U@left,V@right)
        self.assertAlmostEqual(a,b,places=12)


if __name__ == '__main__': unittest.main()
