import importlib.util,math,pathlib,unittest
from fractions import Fraction as F
p=pathlib.Path(__file__).resolve().parents[1]/'src/endpoint_analysis.py';spec=importlib.util.spec_from_file_location('endpoint',p);e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
class Endpoints(unittest.TestCase):
 def test_exact_measure(self):
  atoms=[(F(0),F(1,4)),(F(1,2),F(1,2)),(F(2),F(1,4))];R=sum(w*max(F(0),1-x) for x,w in atoms);S=sum(w*max(F(0),1-x)**2 for x,w in atoms)
  self.assertEqual(R,F(1,2));self.assertEqual(S,F(3,8));r=e.moments(float(R),float(S),8)
  self.assertEqual(r['clipped_mean_s'],4);self.assertEqual(r['clipped_variance_s2'],8);self.assertEqual(r['current_heat_ancestry_mean_s'],2);self.assertEqual(r['cdf_T_lower'],float(F(2,3)))
  for u in (F(1,4),F(1,2),F(3,4)):
   c=1-u;lo=max(0,(S-c*R)/(1-c));hi=min(1,((1+c)*R-S)/c);actual=sum(w for x,w in atoms if x<=u);self.assertLessEqual(lo,actual);self.assertLessEqual(actual,hi)
   for x in (F(0),c/2,c, (1+c)/2,F(1)):
    indicator=int(x>=c);self.assertLessEqual((x*x-c*x)/(1-c),indicator);self.assertGreaterEqual(((1+c)*x-x*x)/c,indicator)
 def test_one_pole_independent_integrals(self):
  # K(tau)=lambda exp(-lambda*tau), T=2, lambda=1;
  # integration by parts gives ramp integrals P=T-1+exp(-T), Q=T^2/2-T+1-exp(-T).
  T=2.;P=1+math.exp(-2);Q=1-math.exp(-2);r=e.endpoint(P,Q,T,T)
  self.assertAlmostEqual(r['R'],(1+math.exp(-2))/2,15);self.assertAlmostEqual(r['S'],(1-math.exp(-2))/2,15)
  self.assertAlmostEqual(r['current_heat_ancestry_mean_s'],4*math.exp(-2)/(1+math.exp(-2)),14)
  for u,b in r['cdf_bounds'].items():self.assertLessEqual(b['lower'],1-math.exp(-float(u)*T));self.assertGreaterEqual(b['upper'],1-math.exp(-float(u)*T))
 def test_invalid_and_zero(self):
  for args in [(-1,0,1,1),(1,-1,1,1),(1,0,-1,1),(1,0,1,0),(math.inf,0,1,1),(1,math.nan,1,1),(0,1,1,1)]:
   with self.assertRaises(ValueError):e.endpoint(*args)
  self.assertEqual(e.endpoint(0,0,0,1)['status'],'UNDEFINED_ZERO_TERMINAL_YIELD');r=e.endpoint(0,0,1,1);self.assertIsNone(r['current_heat_ancestry_mean_s']);self.assertEqual(r['cdf_T_lower'],0)
  r=e.moments(.5,.25-1e-15,1);self.assertLess(r['clipped_variance_s2'],0);self.assertIsNone(r['clipped_std_s'])
  self.assertIsNone(e.moments(1,1,1)['condition_indicators']['mean'])
if __name__=='__main__':unittest.main()
