import sys,unittest
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from interval_backend import I,Jet
from ad2 import D2
from interval_rhs import full_blocks,EB
from homotopy import compute,continuum_integral
class VariationTests(unittest.TestCase):
 def test_true_second_derivative_no_factorial(self):
  x=D2.var(I(2),0);v=x*x*x
  self.assertTrue(v.h[0][0].contains(12));self.assertTrue(v.g[0].contains(12))
 def test_cross_Hessian(self):
  x=D2.var(I(2),0);y=D2.var(I(3),1);f=x*y
  self.assertTrue(f.h[0][1].contains(1));self.assertTrue(f.h[1][0].contains(1))
 def test_photon_count_coordinates_and_feedback(self):
  _,J=full_blocks(I('.5'),[I(.9),I(.3),I(.6),I(1)],[I('.05')],[I(0)],I(*EB))
  self.assertGreater(J[4][0].lo,0);self.assertLess(J[0][0].hi,0);self.assertGreater(J[0][4].lo,0)
 def test_true_continuous_source_mass(self):
  out=continuum_integral(1250000000,I(1),lambda b:[I(1)])[0]
  self.assertLessEqual(out.lo,(I(5e-15)*1250000000).lo);self.assertGreaterEqual(out.hi,(I(5e-15)*1250000000).hi)
 def test_direct_eta_bound_does_not_adopt_nominal(self):
  r=compute();self.assertEqual(r['eta_domain'],[0,1]);self.assertGreater(I(*r['source_nonlinearity_nominal_tangent_remainder_radius']).lo,0)
  self.assertFalse(r['narrower_than_fallback']);self.assertEqual(r['replacement_count'],0)
 def test_missing_J3_is_not_toy_value_or_zero(self):
  r=compute();self.assertIsNone(r['known_atom_J3']);self.assertIsNone(r['regular_K4'])
if __name__=='__main__':unittest.main()
