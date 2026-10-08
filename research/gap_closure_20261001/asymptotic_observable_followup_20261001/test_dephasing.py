import unittest
from fractions import Fraction as F
from dephasing import QComplex as Q, bohr_coefficients, ordinary_limit_exists

class DephasingTests(unittest.TestCase):
    def test_noninvariant_projector_has_exact_persistent_oscillation(self):
        c=bohr_coefficients([0,2],[[F(1,2)]*2 for _ in range(2)],[F(3,5),F(4,5)])
        self.assertEqual(c[F(0)],Q(F(1,2)))
        self.assertEqual(c[F(2)],Q(F(6,25)))
        self.assertFalse(ordinary_limit_exists(c))
    def test_noncommuting_observable_can_converge_for_eigenstate(self):
        c=bohr_coefficients([0,2],[[F(1,2)]*2 for _ in range(2)],[1,0])
        self.assertTrue(ordinary_limit_exists(c));self.assertEqual(c[F(0)],Q(F(1,2)))
    def test_degenerate_coherence_survives(self):
        c=bohr_coefficients([0,0,2],[[F(1,2),F(1,2),0],[F(1,2),F(1,2),0],[0,0,0]],[F(3,5),F(4,5),0])
        self.assertEqual(c[F(0)],Q(F(49,50)));self.assertTrue(ordinary_limit_exists(c))
    def test_equal_frequency_contributions_can_cancel(self):
        A=[[F(1,2),F(1,10),0],[F(1,10),F(1,2),-F(1,5)],[0,-F(1,5),F(1,2)]]
        c=bohr_coefficients([0,1,2],A,[F(2,3),F(2,3),F(1,3)])
        self.assertEqual(c[F(1)],Q());self.assertTrue(ordinary_limit_exists(c))
    def test_complex_conjugate_frequency_pair(self):
        c=bohr_coefficients([0,2],[[F(1,2)]*2 for _ in range(2)],[Q(F(3,5)),Q(0,F(4,5))])
        self.assertEqual(c[F(-2)],Q(0,F(6,25)));self.assertEqual(c[F(2)],Q(0,-F(6,25)))
    def test_no_floating_energy_tolerance_merges_distinct_levels(self):
        with self.assertRaises(TypeError):bohr_coefficients([0.0,1.0],[[1,0],[0,1]],[1,0])
        c=bohr_coefficients([0,F(1,10**30)],[[F(1,2)]*2 for _ in range(2)],[F(3,5),F(4,5)])
        self.assertFalse(ordinary_limit_exists(c))
if __name__=='__main__':unittest.main()
