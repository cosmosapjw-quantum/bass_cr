import unittest
from fractions import Fraction as F
from angle_budget import sqrt_upper, rate_budget, population_interval, admitted_angle

class AngleBudgetTests(unittest.TestCase):
    def test_sqrt_outward(self):
        for x in [F(0), F(1, 3), F(1, 4), F(10001, 31)]:
            u = sqrt_upper(x, 50)
            self.assertGreaterEqual(u*u, x)
            if u:
                self.assertLess((u-F(1, 2**50))**2, x)

    def test_boundary_quadratic(self):
        for p in (F(0), F(1)):
            self.assertEqual(rate_budget(p,p,F(1,100)), F(1,10000))

    def test_exact_nonboundary(self):
        # p=9/25 gives sqrt(p(1-p))=12/25 exactly; dyadic rounding outward.
        a=F(1,1000)
        self.assertGreaterEqual(rate_budget(F(9,25),F(9,25),a), F(24,25)*a+a*a)
        self.assertLess(rate_budget(F(9,25),F(9,25),a), F(24,25)*a+a*a+F(1,2**70))

    def test_interval_crosses_half(self):
        self.assertEqual(rate_budget(F(1,3),F(2,3),F(1,100)),F(1,100))
        self.assertEqual(population_interval(F(0),F(1),F(3)),(F(0),F(1)))

    def test_admission_is_maximal_dyadic_for_polynomial(self):
        lo,hi,e=F(9,1000),F(1,100),F(5,10**6)
        a,r=admitted_angle(lo,hi,e,bits=70)
        self.assertLessEqual(a*a+2*r*a,e)
        b=a+F(1,2**70)
        self.assertGreater(b*b+2*r*b,e)

    def test_complement_symmetry(self):
        for lo,hi in [(F(0),F(0)),(F(1,9),F(2,9)),(F(2,3),F(4,5))]:
            a=F(3,100)
            self.assertEqual(rate_budget(lo,hi,a),rate_budget(1-hi,1-lo,a))

    def test_invalid_contract(self):
        for lo,hi,a in [(F(-1),F(0),F(0)),(F(0),F(2),F(0)),(F(1),F(0),F(0)),(F(0),F(1),F(-1))]:
            with self.assertRaises(ValueError): rate_budget(lo,hi,a)
        with self.assertRaises(TypeError): rate_budget(0.1,F(1),F(1))
        with self.assertRaises(ValueError): sqrt_upper(F(-1))
        with self.assertRaises(ValueError): admitted_angle(F(0),F(0),F(-1))

if __name__=='__main__': unittest.main()
