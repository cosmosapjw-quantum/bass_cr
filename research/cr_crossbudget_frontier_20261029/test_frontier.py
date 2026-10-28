import unittest
from fractions import Fraction as Q
from frontier import Atom,solve,example_atoms,verify_certificate

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
        atoms=[Atom.parse('low',0,3,0)]
        z=solve(atoms,4,0)
        self.assertEqual(z['d_max'],Q(3,2))
        self.assertEqual(z['M_budget'],0)
        self.assertEqual(z['low_diagonal'],(('low',Q(3,2)),))
        self.assertTrue(verify_certificate(atoms,4,0,z))
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


class CertificateTests(unittest.TestCase):
    def test_zero_mass_full_graph_dual(self):
        atoms=[Atom.parse('zero_low',0,0,0),Atom.parse('high',3,1,0)]
        out=solve(atoms,4,0)
        prices=dict(out['dual_prices'])
        self.assertGreaterEqual(prices['zero_low']+prices['high'],1)
        bad=dict(out);bad['dual_prices']=(('zero_low',Q(0)),('high',Q(0)))
        with self.assertRaises(ValueError):verify_certificate(atoms,4,0,bad)

    def test_uniform_empty_zero_and_unmatched_schema(self):
        expected=set(solve(example_atoms(),4,1))
        for atoms in ([],[Atom.parse('zero',0,0,0)],
                      [Atom.parse('high',5,2,1)],
                      [Atom.parse('low',0,3,0),Atom.parse('high',5,2,1)]):
            result=solve(atoms,4,0)
            self.assertEqual(set(result),expected)
            self.assertTrue(verify_certificate(atoms,4,0,result))
    def test_type_precedes_attribute_access(self):
        with self.assertRaises(TypeError):solve([object()],4,0)
        with self.assertRaises(ValueError):solve([Atom.parse('x',0,1,0)]*2,4,0)
    def test_dual_namespace(self):
        atoms=[Atom.parse('lambda',0,1,0),Atom.parse('high',3,1,1)]
        out=solve(atoms,4,1)
        self.assertEqual(set(dict(out['dual_prices'])),{'lambda','high'})
        self.assertIsInstance(out['budget_multiplier'],Q)
        self.assertTrue(verify_certificate(atoms,4,1,out))
    def test_caller_cannot_raise_size_guards(self):
        for kwargs in ({'max_atoms':13},{'max_edges':49},{'max_atoms':True}):
            with self.assertRaises(ValueError):solve([],4,0,**kwargs)
    def test_budget_curve_shape_and_scale(self):
        points=[solve(example_atoms(),4,c)['d_max'] for c in (0,1,2,3)]
        slopes=[b-a for a,b in zip(points,points[1:])]
        self.assertTrue(all(x>=0 for x in slopes))
        self.assertTrue(all(a>=b for a,b in zip(slopes,slopes[1:])))
        atoms=[Atom.parse(a.key,a.energy,3*a.mass,a.bin) for a in example_atoms()]
        self.assertEqual(solve(atoms,4,3)['d_max'],3*Q(7,4))
    def test_tampered_certificates_rejected(self):
        import copy
        atoms=example_atoms();out=solve(atoms,4,1)
        wrong=[]
        for key,value in [('d_max',Q(2)),('gap',Q(1)),('cross_used',Q(0)),
                          ('budget_multiplier',Q(-1))]:
            z=copy.deepcopy(out);z[key]=value;wrong.append(z)
        z=copy.deepcopy(out);z['primal']=tuple((h,l,-v) for h,l,v in z['primal']);wrong.append(z)
        z=copy.deepcopy(out);z['singles']=();wrong.append(z)
        z=copy.deepcopy(out);z['dual_prices']=();wrong.append(z)
        z=copy.deepcopy(out);del z['low_diagonal'];wrong.append(z)
        for z in wrong:
            with self.assertRaises(ValueError):verify_certificate(atoms,4,1,z)


if __name__=='__main__':unittest.main()
