import random
import unittest
from fractions import Fraction as F
from sympy import Rational, symbols
from sympy.solvers.simplex import lpmax
from native_budget import Atom, certify, witness, hall_cut, exact


def full_event_lp(atoms, K, c):
    """Independent all-event formulation, including LL and diagonal events."""
    K, c = exact(K), exact(c)
    edges = [(i,j) for i in range(len(atoms)) for j in range(i,len(atoms))
             if atoms[i].energy+atoms[j].energy<=K]
    if not edges:
        return F(0)
    v = symbols('v0:'+str(len(edges)))
    cons = [x>=0 for x in v]
    for i,a in enumerate(atoms):
        cons.append(sum((v[t]*(2 if i==ii==jj else 1) for t,(ii,jj) in enumerate(edges)
                         if i==ii or i==jj),Rational(0)) <= Rational(a.mass.numerator,a.mass.denominator))
    cons.append(sum((v[t] for t,(i,j) in enumerate(edges) if atoms[i].bin!=atoms[j].bin),Rational(0))
                <= Rational(c.numerator,c.denominator))
    obj,_ = lpmax(sum(v,Rational(0)),cons)
    num,den = obj.as_numer_denom()
    return F(int(num),int(den))


def fixture():
    return (Atom.parse('L0','1/5',1,1),Atom.parse('L1','1/2',1,0),
            Atom.parse('L2','6/5',1,2),Atom.parse('H0','27/10',1,2),
            Atom.parse('H1','17/10',1,2),Atom.parse('H2','8/5',1,2))


class NativeBudgetTests(unittest.TestCase):
    def test_source_pattern_certification(self):
        c = certify(fixture(),3,expected_S=1,expected_M=3)
        self.assertEqual(c['R'],2)
        self.assertEqual(c['same_dual']['value'],1)
        self.assertEqual(c['full_dual']['value'],3)
        self.assertEqual(len(c['same_events']),1)
        for x in ['0','1/4','1/2','1','3/2','2','3']:
            z=witness(c,x)
            self.assertEqual(z['M_budget'],1+min(F(x),2))
            self.assertEqual(z['d_max'],2+min(F(x),2)/2)
            self.assertEqual(z['primal_dual_gap'],0)
            self.assertEqual(z['cross_used'],min(F(x),2))
            self.assertEqual(z['lambda'],int(F(x)<2))
            self.assertEqual(z['d_max'],full_event_lp(fixture(),3,x))

    def test_same_only(self):
        a=(Atom.parse('h','8/5',2,2),Atom.parse('l','6/5',1,2))
        c=certify(a,3,expected_S=1,expected_M=1)
        self.assertEqual(witness(c,0)['d_max'],1)

    def test_no_edges_and_zero_mass(self):
        a=(Atom.parse('high',4,2,3),Atom.parse('low',0,3,0),Atom.parse('zero',0,0,1))
        c=certify(a,3,expected_S=0,expected_M=0)
        self.assertEqual(witness(c,0)['d_max'],F(3,2))

    def test_zero_mass_dual_extension(self):
        # A zero-mass high can form a permitted edge to a positive low.
        # The dual must still cover the edge on the full original graph.
        a=(Atom.parse('low',0,1,2),Atom.parse('zero_high',2,0,2),
           Atom.parse('positive_high',4,1,3))
        cert=certify(a,3)
        self.assertEqual(cert['full_dual']['prices']['zero_high'],1)
        self.assertEqual(cert['full_dual']['value'],0)
        self.assertEqual(witness(cert,0)['primal_dual_gap'],0)

    def test_negative_and_float_refusal(self):
        with self.assertRaises(TypeError):Atom.parse('x',0.5,1,0)
        with self.assertRaises(TypeError):Atom('x',F(1),0.5,0)
        with self.assertRaises(ValueError):Atom.parse('x',-1,1,0)
        with self.assertRaises(ValueError):certify(fixture(),-1)
        with self.assertRaises(ValueError):witness(certify(fixture(),3),-1)

    def test_multi_eligible_high_bins_refused(self):
        a=(Atom.parse('h0',2,1,0),Atom.parse('h1',2,1,1),Atom.parse('l0',0,1,0),Atom.parse('l1',0,1,1))
        with self.assertRaisesRegex(ValueError,'ONE_ELIGIBLE_HIGH_BIN'):certify(a,3)

    def test_duplicated_atom_refused(self):
        a=fixture()
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):certify(a+(a[0],),3)

    def test_incorrect_expected_parent_refused(self):
        with self.assertRaisesRegex(AssertionError,'EXPECTED_M_MISMATCH'):
            certify(fixture(),3,expected_M=4)

    def test_random_full_event_oracle(self):
        rng=random.Random(20261029)
        checked=0
        for n in range(2,6):
            for case in range(4):
                highs=[Atom.parse(f'h{i}',F(rng.randint(16,18),10),F(rng.randint(1,6),4),2)
                       for i in range(n)]
                lows=[Atom.parse('ls',F(11,10),F(rng.randint(1,6),4),2),
                      Atom.parse('lc0',F(1,10),F(rng.randint(1,6),4),0),
                      Atom.parse('lc1',F(1,5),F(rng.randint(1,6),4),1)]
                a=tuple(highs+lows)
                cert=certify(a,3)
                for c in (F(0),F(1,2),F(2)):
                    out=witness(cert,c)
                    self.assertEqual(out['d_max'],full_event_lp(a,3,c))
                    checked+=1
        self.assertEqual(checked,48)

    def test_large_source_topology_synthetic(self):
        # 3201 positive atoms; source-like bin topology, not the original source.
        atoms=[]
        for i in range(3201):
            e=F(1,10)+F(99*i,32000)
            b=0 if i==0 else (1 if e<=1 else (2 if e<=3 else 3))
            atoms.append(Atom.parse(f'a{i}',e,F((i%13)+1,2**20),b))
        c=certify(atoms,3)
        self.assertEqual(len(c['atoms']),3201)
        self.assertEqual(witness(c,c['R'])['primal_dual_gap'],0)
        self.assertEqual(witness(c,c['R']/2)['primal_dual_gap'],0)

if __name__=='__main__':unittest.main(verbosity=2)
