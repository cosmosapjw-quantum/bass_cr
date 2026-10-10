import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from interval_backend import I
from source_kernel import load_pins,T,probe
from birth_measure import integrate_previous,PositiveSurvivalTube

class MeasureTests(unittest.TestCase):
 def setUp(self):self.plan=load_pins()['BIRTH_PLAN.json'];self.field=PositiveSurvivalTube();self.atoms={str(b):self.field for b in self.plan['same_births']}
 def test_actual_mass_interval(self):
  q=integrate_previous(I(T),lambda b,p:[I(1)],I(0),self.field,self.atoms,trace='right')[0]
  s=integrate_previous(I(T),lambda b,p:[I(1)],I(1),self.field,self.atoms,trace='right')[0]
  self.assertGreater(s.lo-q.hi,0) # mass mismatch is retained, not renormalized
 def test_previous_births_only(self):
  b=self.plan['same_births'][0];fn=lambda b,p:[I(1)]
  right=integrate_previous(I(b),fn,I(0),self.field,self.atoms,trace='right')[0]
  left=integrate_previous(I(b),fn,I(0),self.field,self.atoms,trace='left')[0]
  self.assertEqual(left.hi,0);self.assertGreater(right.lo,0)
 def test_eta_convex_source(self):
  val=integrate_previous(I(T),lambda b,p:[I(1)],I('.5'),self.field,self.atoms,trace='right')[0]
  q=integrate_previous(I(T),lambda b,p:[I(1)],I(0),self.field,self.atoms,trace='right')[0]
  s=I(5e-15)*T;expected=(q+s)/2
  self.assertLessEqual(val.lo,expected.hi);self.assertLessEqual(expected.lo,val.hi)
 def test_atom_trace_required(self):
  with self.assertRaises(ValueError):integrate_previous(I(T),lambda b,p:[I(1)],I(0),self.field,self.atoms,trace='unspecified')
 def test_point_callable_rejected(self):
  with self.assertRaises(TypeError):integrate_previous(I(T),lambda b,p:[I(1)],I(1),lambda b:1,self.atoms,trace='right')
 def test_memory_cannot_be_negative(self):
  with self.assertRaises(ValueError):probe(I(2),I(1),I('-0.1'))
if __name__=='__main__':unittest.main()
