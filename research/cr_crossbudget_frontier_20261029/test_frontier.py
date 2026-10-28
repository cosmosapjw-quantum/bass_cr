import unittest
from fractions import Fraction as Q
from frontier import Atom,solve,example_atoms

class FrontierTests(unittest.TestCase):
    def test_counterexample_exact(self):
        for c,expected in [('0','3/2'),('1/2','13/8'),('1','7/4'),('3/2','15/8'),('2','2')]:
            z=solve(example_atoms(),4,c)
            self.assertEqual(z['d_max'],Q(expected))
            self.assertEqual(z['M_budget'],Q(1)+Q(c)/2)
            self.assertEqual(z['gap'],0)
            self.assertLessEqual(z['cross_used'],Q(c))
            self.assertEqual(z['d_max'],z['M_budget']+sum((v for _,v in z['low_diagonal']),Q(0)))
    def test_saturation(self):
        z=solve(example_atoms(),4,5)
        self.assertEqual(z['d_max'],2)
    def test_no_edges(self):
        z=solve([Atom.parse('low',0,3,0)],4,0)
        self.assertEqual(z['d_max'],Q(3,2))
        self.assertEqual(z['M_budget'],0)
    def test_cross_only(self):
        a=[Atom.parse('low',0,1,0),Atom.parse('high',3,1,1)]
        self.assertEqual(solve(a,4,0)['d_max'],Q(1,2))
        self.assertEqual(solve(a,4,1)['d_max'],1)
    def test_same_only(self):
        a=[Atom.parse('low',0,1,0),Atom.parse('high',3,1,0)]
        self.assertEqual(solve(a,4,0)['d_max'],1)
    def test_exact_type_and_domain(self):
        for v in [1.0,True]:
            with self.assertRaises(TypeError):Atom.parse('x',v,1,0)
        with self.assertRaises(ValueError):solve(example_atoms(),4,-1)
        with self.assertRaises(ValueError):solve(example_atoms()*4,4,1)
        with self.assertRaises(ValueError):Atom.parse('x',0,-1,0)
    def test_energy_threshold_equality(self):
        a=[Atom.parse('half',2,2,0),Atom.parse('high',3,1,0)]
        self.assertEqual(solve(a,4,0)['M_budget'],0)
        self.assertEqual(solve(a,5,0)['M_budget'],1)

if __name__=='__main__':unittest.main()

class FullEventIndependentOracle(unittest.TestCase):
    """A different LP: all low-low loops and cross-bin low-low pairs included."""
    def reference(self, atoms, cap, cross_budget):
        from sympy import symbols, Rational
        from sympy.solvers.simplex import lpmax
        K=Q(cap); c=Q(cross_budget)
        edges=[(i,j) for i in range(len(atoms)) for j in range(i,len(atoms))
               if atoms[i].energy+atoms[j].energy<=K]
        if not edges:return Q(0)
        z=symbols('z0:'+str(len(edges)))
        cons=[u>=0 for u in z]
        for i,a in enumerate(atoms):
            cons.append(sum((z[e]*(2 if i==j==i0 else 1) for e,(i0,j) in enumerate(edges)
                             if i==i0 or i==j),Rational(0))<=Rational(a.mass.numerator,a.mass.denominator))
        cons.append(sum((z[e] for e,(i,j) in enumerate(edges) if atoms[i].bin!=atoms[j].bin),Rational(0))<=Rational(c.numerator,c.denominator))
        value,_=lpmax(sum(z,Rational(0)),cons)
        p,q=value.as_numer_denom()
        return Q(int(p),int(q))

    def test_full_event_model(self):
        import random
        rg=random.Random(20261029)
        cases=0
        for n in (2,3,4,5):
            for t in range(4):
                atoms=[Atom.parse(f'a{i}',Q(rg.randrange(0,10),2),Q(rg.randrange(0,5),2),rg.randrange(3)) for i in range(n)]
                K=Q(rg.randrange(2,11),2);c=Q(rg.randrange(0,5),2)
                out=solve(atoms,K,c)
                self.assertEqual(out['d_max'],self.reference(atoms,K,c), (n,t,K,c))
                cases+=1
        self.assertEqual(cases,16)
