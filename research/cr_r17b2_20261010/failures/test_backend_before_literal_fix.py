import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from interval_backend import I,Jet,AD
from source_kernel import load_pins,local_derivatives,require_proof,MissingProof,probe,memory_response

class BackendTests(unittest.TestCase):
 def test_interval_zero_division(self):
  with self.assertRaises(ValueError): I(1)/I(-1,1)
 def test_fourth_derivative(self):
  j=Jet.variable(I(2));self.assertTrue((j**4).derivatives()[4].contains(24))
 def test_exp_derivatives(self):
  j=Jet.variable(I(0));self.assertTrue(all(v.contains(1) for v in j.exp().derivatives()))
 def test_local_global(self):
  self.assertEqual([float(v.lo) for v in local_derivatives([I(1)]*5,2,10)],[1,.2,.04,.008,.0016])
 def test_source_bytes(self):
  with self.assertRaises(ValueError):load_pins(overrides={'BIRTH_PLAN.json':b'{}'})
 def test_clock(self):
  with self.assertRaises(ValueError):load_pins(clock=1)
 def test_mass_mismatch(self):
  p=load_pins();self.assertNotEqual(p['mass_mismatch'],0)
 def test_unreported_kink(self):
  with self.assertRaises(MissingProof):require_proof({'partition_complete':True,'homotopy_uniform':True})
 def test_nominal_only(self):
  with self.assertRaises(MissingProof):require_proof({'eta':[0,0],'tube':True})
 def test_frozen_gas(self):
  with self.assertRaises(MissingProof):require_proof({'frozen_gas':True})
 def test_causal_survival(self):
  with self.assertRaises(ValueError):probe(I(1),I(2),I(0))
  e,p=probe(I(2),I(1),I('0.1'));self.assertTrue(p.contains(I('-0.1').exp().lo));self.assertLess(float(e.hi),13.7)
 def test_memory_feedback(self):
  self.assertTrue(memory_response(I(2),I('0.3')).contains(-.6))

if __name__=='__main__':unittest.main()
