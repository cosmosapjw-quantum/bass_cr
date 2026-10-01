from fractions import Fraction as F
import unittest
from bridge_mass_certificate import cap_lower, eigenvalue_lower, geometry_margin, radial_mass
from certify_reference_bridge import check_conforming, gradient_diagonal_upper, integer_sqrt_upper


class BridgeCertificateTests(unittest.TestCase):
    def test_exact_angular_cap_and_exclusive_geometry(self):
        self.assertEqual(cap_lower(F(1, 2)), F(1, 176))
        self.assertEqual(geometry_margin(64, 32, 48, F(1, 2)), 768)
        with self.assertRaises(ValueError):
            geometry_margin(64, 1, 48, F(1, 2))

    def test_partial_cell_and_linearly_independent_radial_modes(self):
        # u1(s)=1-s, u2(s)=s(1-s), one unit cell; tail starts at 1/2.
        coeff = [[[F(1), F(-1), F(0)]], [[F(0), F(1), F(-1)]]]
        gram = radial_mass(coeff, [F(0), F(1)], [0, 1], F(1, 2))
        self.assertEqual(gram[0][0], F(1, 24))
        self.assertEqual(gram[0][1], F(5, 192))
        self.assertEqual(gram[1][1], F(1, 60))
        lower, pivots = eigenvalue_lower(gram)
        self.assertTrue(all(x > 0 for x in pivots))
        self.assertGreater(lower, 0)
        # Independently prove the returned lower through exact 2x2 minors.
        shifted = [[gram[i][j]-(lower if i == j else 0) for j in range(2)] for i in range(2)]
        self.assertGreater(shifted[0][0], 0)
        self.assertGreaterEqual(shifted[0][0]*shifted[1][1]-shifted[0][1]**2, 0)

    def test_duplicate_radial_modes_fail_positive_metric_claim(self):
        with self.assertRaises(ValueError):
            eigenvalue_lower([[F(1), F(1)], [F(1), F(1)]])

    def test_conforming_origin_and_rational_gradient_bound(self):
        # u=r(1-r) on [0,1]; exact radial gradient terms are both 1/3.
        mode = [[F(0), F(1), F(-1)]]
        check_conforming([mode])
        self.assertEqual(gradient_diagonal_upper(mode, [F(0), F(1)], 0), F(1, 3))
        self.assertEqual(gradient_diagonal_upper(mode, [F(0), F(1)], 1), F(1))
        with self.assertRaises(ValueError):
            check_conforming([[[F(0), F(1)]]])
        for x in (F(0), F(4), F(5), F(1, 10), F(10**80+1)):
            upper = integer_sqrt_upper(x)
            self.assertGreaterEqual(upper*upper, x)


if __name__ == '__main__':
    unittest.main()
