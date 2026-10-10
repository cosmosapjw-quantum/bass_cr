import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from interval_backend import I,Jet
from source_kernel import tangent_functional,continuum_rhs,load_pins,T,EB
from birth_measure import integrate_previous,PositiveSurvivalTube
class FunctionalTests(unittest.TestCase):
 def test_companion_current_response_participates(self):
  z=[I(.9),I(.3),I(.6),I(1)];d=[I(0)]*4
  zero=lambda f:(I(0),I(0))
  companion=lambda f:f(I('.1'),I('.03'),I('.02'),I(*EB))
  a=tangent_functional(.5,z,d,I('.2'),I('.99'),(I('.05'),I(0)),zero)
  b=tangent_functional(.5,z,d,I('.2'),I('.99'),(I('.05'),I(0)),companion)
  self.assertGreater(b[0].lo,a[0].hi)
 def test_full_companion_measure_in_primal_rhs(self):
  field=PositiveSurvivalTube();plan=load_pins()['BIRTH_PLAN.json'];atoms={str(b):field for b in plan['same_births']}
  u=I('.5');z=[I(.9),I(.3),I(.6),I(1)]
  def integrator(fields,eta,weights):
   return integrate_previous(u*T,lambda b,p:fields(b/T,p,I(*EB)),eta,field,atoms,trace='right')
  full,_=continuum_rhs(u,z,I(0,.05),integrator,I(0,1),None)
  empty,_=continuum_rhs(u,z,I(0,.05),lambda *a:(I(0),I(0)),I(0,1),None)
  self.assertGreater(full[0].hi,empty[0].hi)
 def test_local_factorials_restored_once(self):
  from source_kernel import local_derivatives
  j=Jet.variable(I(2))**3
  r=local_derivatives(j.derivatives(),2,10)
  self.assertTrue(r[3].contains('.048')) # 6*(2/10)^3, no second factorial
if __name__=='__main__':unittest.main()
