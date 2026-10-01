from fractions import Fraction as F
import unittest
from galilean_cancellation import (weak_boost_difference, weak_boundary_term,
    schur_numerator, matmul, matrix_add, matrix_scale, coarse_rate_bound)


class GalileanCancellationTests(unittest.TestCase):
    def test_cross_velocity_identity_is_exact_boundary_derivative(self):
        for va, vb in ((F(0), F(2)), (F(3, 7), F(-5, 4)), (F(2), F(2))):
            self.assertEqual(weak_boost_difference(va, vb), weak_boundary_term(va, vb))
        # Omitting the source -i*v_b^2*t/2 phase leaves a scalar defect.
        full = weak_boost_difference(F(0), F(2))
        missing_phase = dict(full)
        re, im = missing_phase['ab']
        missing_phase['ab'] = (re+2, im)
        self.assertNotEqual(missing_phase, weak_boundary_term(F(0), F(2)))

    def test_isolated_matrix_and_scalar_potential_cancel_in_schur_residual(self):
        G = [[F(2), F(1)], [F(1), F(3)]]
        B = [[F(1), F(0)], [F(0), F(1)]]
        Lambda = [[F(-2), F(1)], [F(0), F(-1)]]
        Vss = [[F(1, 2), F(1, 7)], [F(1, 7), F(-1, 3)]]
        Vcs = [[F(2, 5), F(-1, 6)], [F(1, 9), F(3, 4)]]
        Rcs = [[F(1, 11), F(0)], [F(0), F(-1, 13)]]
        Kss = matrix_add(matmul(G, Lambda), Vss)
        Kcs = matrix_add(matrix_add(matmul(B, Lambda), Vcs), Rcs)
        reduced = schur_numerator(G, B, Kss, Kcs)
        self.assertEqual(reduced, matrix_add(schur_numerator(G, B, Vss, Vcs), Rcs))
        self.assertEqual(reduced, schur_numerator(G, B,
            matrix_add(Kss, matrix_scale(G, F(17, 3))),
            matrix_add(Kcs, matrix_scale(B, F(17, 3)))))

    def test_potential_norm_does_not_inherit_metric_condition_factor(self):
        # Physical basis columns e1 and e1+epsilon*e2; V=q*sigma_x.
        epsilon, q = F(1, 100), F(3, 7)
        E = schur_numerator([[F(1)]], [[F(1)]], [[F(0)]], [[epsilon*q]])[0][0]
        T = epsilon**2
        self.assertEqual(E**2/T, q**2)

    def test_weak_galerkin_zero_is_not_global_residual_zero(self):
        # f=1-|x| on [-1,1], h=-1/2 d²/dx². One-function lambda=3/2.
        mass_ff, kinetic_ff = F(2, 3), F(1)
        lam = kinetic_ff/mass_ff
        self.assertEqual(kinetic_ff-lam*mass_ff, 0)
        # For the H1 test eta=1-x² on [-1,1], <eta,f>=5/6 and h(eta,f)=1.
        residual_other = F(1)-lam*F(5, 6)
        self.assertEqual(residual_other, F(-1, 4))

    def test_bounded_weak_residual_and_potential_arithmetic(self):
        result = coarse_rate_bound(F(6, 5), F(67, 100), F(3), F(51, 100), F(33, 100), F(7, 4))
        self.assertEqual(result['weak_target_residual_upper'], F(927, 200))
        self.assertEqual(result['rho_upper'], F(8409, 800))
        self.assertEqual(result['bridge_upper'], F(25227, 50))
        with self.assertRaises(ValueError):
            coarse_rate_bound(F(6, 5), F(67, 100), F(3), F(51, 100), F(33, 100), F(3, 2))


if __name__ == '__main__':
    unittest.main()
