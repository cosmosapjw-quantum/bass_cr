"""Source-independent and original-program differential checks, exact rational only."""
from fractions import Fraction as F
import random, unittest
from native_budget import Atom
from test_generic_budget_flow import oracle, counterexample
from generic_budget_flow import ExactBudgetFlow
from batch_bridge import run_batch

class TestBatch(unittest.TestCase):
    def test_multikink_seven_exact(self):
        rows=[('h0','19/2','1/2',1),('h1','7','2',0),('h2','9','2',1),('h3','13/2','5/2',2),('h4','6','1/2',1),('l0','0','1',0),('l1','7/2','1',1),('l2','3/2','5/2',2),('l3','0','5/2',0),('l4','3/2','1/2',2)]
        atoms=tuple(Atom.parse(*a) for a in rows)
        budgets=[F(4),F(0),F(3,2),F(5,2),F(1),F(2),F(3),F(2),F(10)]
        expected={F(0):F(5),F(1):F(6),F(3,2):F(13,2),F(2):F(27,4),F(5,2):F(7),F(3):F(43,6),F(4):F(15,2),F(10):F(15,2)}
        got=run_batch(atoms,F(10),budgets)
        self.assertEqual(len(got),len(budgets))
        for c,z in zip(budgets,got):
            self.assertEqual(z['M'],expected[c]);self.assertEqual(z['d_max'],oracle(atoms,F(10),c));self.assertEqual(z['gap'],0)
        self.assertEqual(got[0]['state'],'PARTIAL')
        self.assertEqual(got[-1]['state'],'SATURATED')
        self.assertEqual(got[3]['lambda_dual'],F(1,2))
        self.assertEqual(got[6]['lambda_dual'],F(1,3))
        self.assertEqual(got[4]['lambda_dual'],F(1))
    def test_zero_edges_and_null_caps(self):
        a=(Atom.parse('high',5,1,1),Atom.parse('low',0,2,0),Atom.parse('ghost',0,0,1))
        for z in run_batch(a,F(3),[F(0),F(0),F(1,3),F(4)]):
            self.assertEqual(z['M'],0);self.assertEqual(z['d_max'],1);self.assertEqual(z['gap'],0)
    def test_fraction_budget_kink_4atoms(self):
        a=counterexample()
        cs=[F(5),F(0),F(1,3),F(1,2),F(1),F(2),F(2)]
        zs=run_batch(a,F(4),cs)
        for c,z in zip(cs,zs):
            self.assertEqual(z['d_max'],ExactBudgetFlow(a,4).witness(c)['d_max'])
            self.assertEqual(z['d_max'],oracle(a,F(4),c))
    def test_seeded_75_oracles(self):
        rng=random.Random(20261029);ncases=0
        for n in range(2,7):
            for trial in range(5):
                a=tuple(Atom.parse(f'a{i}',F(rng.randrange(0,11),2),F(rng.randrange(0,6),2),rng.randrange(4)) for i in range(n))
                K=F(rng.randrange(2,13),2)
                cs=[F(2),F(0),F(1,2)]
                zs=run_batch(a,K,cs)
                for c,z in zip(cs,zs):
                    self.assertEqual(z['d_max'],oracle(a,K,c),(n,trial,K,c));ncases+=1
        self.assertEqual(ncases,75)
    def test_errors(self):
        a=counterexample()
        with self.assertRaises(TypeError):run_batch(a,4.,[F(1)])
        with self.assertRaises(TypeError):run_batch(a,F(4),[0.1])
        with self.assertRaises(ValueError):run_batch(a,F(4),[])
        with self.assertRaises(ValueError):run_batch(a,F(4),[F(0)]*129)
        with self.assertRaises(ValueError):run_batch(a,F(4),[F(-1)])
        with self.assertRaises(OverflowError):run_batch((Atom.parse('h',3,F(2)**108,0),Atom.parse('l',1,1,0)),F(5),[F(1)])
    def test_small_repeat_zero_cost(self):
        a=tuple(Atom.parse(*row) for row in [('h0',4,1,0),('h1',4,1,1),('l0',0,1,0),('l1',0,1,1)])
        zs=run_batch(a,F(5),[F(0),F(0),F(1),F(100)])
        for z in zs:self.assertEqual(z['M'],2)
        self.assertEqual(zs[-1]['state'],'SATURATED')

if __name__=='__main__':unittest.main()
