import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from interval_backend import I,Jet
from source_kernel import linear_tangent_rhs,linear_adjoint_rhs,photon_adjoint_rhs,adjoint_functional,EB
class AdjointTests(unittest.TestCase):
 def test_algebraic_duality_independent_inner_products(self):
  A=[[I(1),I(2)],[I(-3),I(4)]];v=[I(5),I(-2)];l=[I(7),I(9)];f=[I('.3'),I('-.4')];g=[I('.1'),I('.2')]
  fw=linear_tangent_rhs(A,v,f);bw=linear_adjoint_rhs(A,l,g)
  lhs=sum((x*y for x,y in zip(l,fw)),I(0))+sum((x*y for x,y in zip(bw,v)),I(0))
  rhs=sum((x*y for x,y in zip(l,f)),I(0))-sum((x*y for x,y in zip(g,v)),I(0))
  self.assertEqual(lhs.data(),rhs.data())
 def test_adjoint_companion_memory_is_required(self):
  z=[I(.9),I(.3),I(.6),I(1)];l=[I(1),I(2),I(3),I(4)]
  a=adjoint_functional(.5,z,l,(I('.05'),I('.1')),lambda f:I(0))
  b=adjoint_functional(.5,z,l,(I('.05'),I('.1')),lambda f:f(I('.1'),I('.001'),I('.2'),I(*EB)))
  self.assertGreater(b[0].lo,a[0].hi)
 def test_birth_derivative_backend_not_nominal_scalar(self):
  z=[I(.9),I(.3),I(.6),I(1)];l=[I(1),I(0),I(0),I(0)]
  f=photon_adjoint_rhs(I('.5'),Jet.variable(I('.1')),z,l,Jet([I(0)]),Jet([I(*EB)]))
  self.assertEqual(len(f.derivatives()),5);self.assertNotEqual(f.derivatives()[1].lo,0)
if __name__=='__main__':unittest.main()
