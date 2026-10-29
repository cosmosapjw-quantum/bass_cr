"""Independent full-event LP oracle for exact arbitrary-bin frontier."""
from fractions import Fraction as F
import random
import unittest
from native_budget import Atom
from generic_budget_flow import ExactBudgetFlow
from sympy import Rational, symbols
from sympy.solvers.simplex import lpmax


def oracle(atoms,K,c):
    K=F(K);c=F(c)
    edges=[(i,j) for i in range(len(atoms)) for j in range(i,len(atoms))
           if atoms[i].energy+atoms[j].energy<=K]
    if not edges:return F(0)
    x=symbols('x0:'+str(len(edges)))
    constraints=[v>=0 for v in x]
    for i,a in enumerate(atoms):
        constraints.append(sum((x[k]*(2 if i==j==i0 else 1)
                    for k,(i0,j) in enumerate(edges) if i==i0 or i==j),Rational(0))
                    <=Rational(a.mass.numerator,a.mass.denominator))
    constraints.append(sum((x[k] for k,(i,j) in enumerate(edges)
                 if atoms[i].bin!=atoms[j].bin),Rational(0))<=Rational(c.numerator,c.denominator))
    obj,_=lpmax(sum(x,Rational(0)),constraints)
    a,b=obj.as_numer_denom()
    return F(int(a),int(b))


def counterexample():
    return (Atom.parse('L0',0,1,0),Atom.parse('L1',1,1,1),
            Atom.parse('H0','5/2',1,0),Atom.parse('H1','19/5',1,1))


class ExactGenericTests(unittest.TestCase):
    def test_older_counterexample_strict_gap(self):
        o=ExactBudgetFlow(counterexample(),4)
        self.assertEqual(o.breakpoints(),((F(0),F(0),None),(F(0),F(1),0),(F(2),F(2),2)))
        for c,d in [(F(0),F(3,2)),(F(1,2),F(13,8)),(F(1),F(7,4)),
                    (F(3,2),F(15,8)),(F(2),F(2)),(F(5),F(2))]:
            r=o.witness(c)
            self.assertEqual(r['d_max'],d)
            self.assertEqual(r['dual']['gap'],0)
            self.assertEqual(d,oracle(counterexample(),4,c))

    def test_multi_eligible_high_bins_accepted(self):
        a=(Atom.parse('h0',2,1,0),Atom.parse('h1',2,1,1),
           Atom.parse('l0',0,1,0),Atom.parse('l1',0,1,1))
        o=ExactBudgetFlow(a,3)
        self.assertEqual(o.witness(0)['M_budget'],2)
        self.assertEqual(o.witness(1)['d_max'],2)

    def test_no_edges_and_zero_masses(self):
        a=(Atom.parse('high',5,1,1),Atom.parse('low',0,2,0),
           Atom.parse('ghost',0,0,1))
        o=ExactBudgetFlow(a,3)
        self.assertEqual(o.witness(0)['d_max'],1)
        self.assertEqual(o.witness(4)['dual']['gap'],0)
        b=(Atom.parse('h',2,0,0),Atom.parse('l',0,1,1))
        self.assertEqual(ExactBudgetFlow(b,3).witness(1)['d_max'],F(1,2))

    def test_three_positive_marginal_cost_slopes(self):
        # Source-independent 10-atom fixture: slopes 1,2,3 in C_min(m).
        rows=[('h0','19/2','1/2',1),('h1','7','2',0),
              ('h2','9','2',1),('h3','13/2','5/2',2),('h4','6','1/2',1),
              ('l0','0','1',0),('l1','7/2','1',1),('l2','3/2','5/2',2),
              ('l3','0','5/2',0),('l4','3/2','1/2',2)]
        atoms=tuple(Atom.parse(*r) for r in rows)
        o=ExactBudgetFlow(atoms,10)
        self.assertEqual(o.breakpoints(),((F(0),F(0),None),
             (F(0),F(5),0),(F(3,2),F(13,2),1),
             (F(5,2),F(7),2),(F(4),F(15,2),3)))
        for c,d,lam in [(F(1),F(27,4),F(1)),
                        (F(2),F(57,8),F(1,2)),
                        (F(3),F(22,3),F(1,3)),
                        (F(4),F(15,2),F(0))]:
            z=o.witness(c)
            self.assertEqual(z['d_max'],d)
            self.assertEqual(z['dual']['lambda'],lam)
            self.assertEqual(z['dual']['gap'],0)
            self.assertEqual(z['d_max'],oracle(atoms,10,c))

    def test_type_budget_size_and_source_guard(self):
        with self.assertRaises(TypeError):ExactBudgetFlow(counterexample(),3.0)
        with self.assertRaises(ValueError):ExactBudgetFlow(counterexample(),-1)
        with self.assertRaises(ValueError):ExactBudgetFlow(counterexample()*4,4)
        with self.assertRaises(ValueError):ExactBudgetFlow(counterexample(),4,max_edges=1)
        with self.assertRaises(ValueError):ExactBudgetFlow(counterexample(),4).witness(-1)

    def test_random_full_event_oracle(self):
        rng=random.Random(20261029)
        count=0
        for n in range(2,7):
            for trial in range(5):
                a=tuple(Atom.parse(f'a{i}',F(rng.randrange(0,11),2),
                                   F(rng.randrange(0,6),2),rng.randrange(4))
                        for i in range(n))
                K=F(rng.randrange(2,13),2)
                o=ExactBudgetFlow(a,K)
                last_slope=-1
                for c,m,s in o.breakpoints():
                    if s is not None:
                        self.assertGreaterEqual(s,last_slope)
                        last_slope=s
                for c in (F(0),F(1,2),F(2)):
                    z=o.witness(c)
                    self.assertEqual(z['d_max'],oracle(a,K,c),(n,trial,K,c))
                    self.assertEqual(z['dual']['gap'],0)
                    count+=1
        self.assertEqual(count,75)

if __name__=='__main__':unittest.main()
