from fractions import Fraction as F
import unittest,random
from native_budget import Atom
from prefix_bridge import run_prefix
from generic_budget_flow import ExactBudgetFlow
from sympy import Rational,symbols
from sympy.solvers.simplex import lpmax

def independent_oracle(atoms,K,c):
  # All-event LP includes same-low and low-low diagonal variables: independent of compressed construction.
  edges=[(i,j) for i in range(len(atoms)) for j in range(i,len(atoms)) if atoms[i].energy+atoms[j].energy<=K]
  if not edges:return F(0)
  vars=symbols('z:'+str(len(edges)))
  cons=[v>=0 for v in vars]
  for i,a in enumerate(atoms):
    cons.append(sum((vars[q]*(2 if ii==jj==i else 1) for q,(ii,jj) in enumerate(edges) if i==ii or i==jj),Rational(0))<=Rational(a.mass.numerator,a.mass.denominator))
  cons.append(sum((vars[q] for q,(ii,jj) in enumerate(edges) if atoms[ii].bin!=atoms[jj].bin),Rational(0))<=Rational(c.numerator,c.denominator))
  opt,_=lpmax(sum(vars,Rational(0)),cons);return F(opt)

class FactorTests(unittest.TestCase):
 def test_multikink(self):
  rows=[('h0','19/2','1/2',1),('h1','7','2',0),('h2','9','2',1),('h3','13/2','5/2',2),('h4','6','1/2',1),('l0','0','1',0),('l1','7/2','1',1),('l2','3/2','5/2',2),('l3','0','5/2',0),('l4','3/2','1/2',2)]
  a=tuple(Atom.parse(*r) for r in rows)
  qs=[F(3),F(0),F(4),F(5,2),F(1),F(3,2),F(2),F(3)]
  z=run_prefix(a,F(10),qs)
  self.assertEqual([v['M'] for v in z],[F(43,6),F(5),F(15,2),F(7),F(6),F(13,2),F(27,4),F(43,6)])
  for v in z:self.assertEqual(v['gap'],0)
 def test_small_full_event_oracle(self):
  rng=random.Random(20261029);nrun=0
  for n in range(2,7):
   for trial in range(5):
    a=tuple(Atom.parse(f'a{i}',F(rng.randrange(11),2),F(rng.randrange(6),2),rng.randrange(4)) for i in range(n))
    K=F(rng.randrange(2,13),2);qs=[F(0),F(1,2),F(2)]
    z=run_prefix(a,K,qs)
    for c,v in zip(qs,z):
     self.assertEqual(v['d_max'],independent_oracle(a,K,c),(n,trial,c))
     self.assertEqual(v['gap'],0);nrun+=1
  self.assertEqual(nrun,75)
 def test_all_isolated_high(self):
  a=(Atom.parse('h',9,2,3),Atom.parse('l',1,1,2),Atom.parse('zero',0,0,0))
  z=run_prefix(a,F(3),[F(0),F(3)])
  self.assertEqual([v['d_max'] for v in z],[F(1,2),F(1,2)])
  self.assertEqual(z[0]['pruned_high'],1)
 def test_fraction_budget_mismatched_bin(self):
  a=(Atom.parse('h',2,1,0),Atom.parse('l',0,1,1),Atom.parse('ghost',0,0,2))
  z=run_prefix(a,F(3),[F(1,3),F(0),F(1),F(1,3)])
  self.assertEqual([v['M'] for v in z],[F(1,3),F(0),F(1),F(1,3)])
 def test_bad_input(self):
  a=(Atom.parse('h',2,1,0),Atom.parse('l',0,1,1))
  for B in ([],[-1],[0]*129):
   with self.assertRaises(ValueError):run_prefix(a,3,B)
  with self.assertRaises(TypeError):run_prefix(a,3.,[1])
 def test_many_prefixes_no_physical_source(self):
  a=[Atom.parse('h'+str(i),F(201+i,100),F(1,2),i%3) for i in range(7)]+[Atom.parse('l'+str(i),F(i,10),F(1),i%2) for i in range(12)]
  qs=[F(0),F(1),F(4),F(10)]
  z=run_prefix(a,F(3),qs)
  ref=ExactBudgetFlow(tuple(a),F(3),max_atoms=40,max_edges=300)
  for c,r in zip(qs,z):self.assertEqual(r['M'],ref.witness(c,certify_dual=False)['M_budget'])
if __name__=='__main__':unittest.main()
