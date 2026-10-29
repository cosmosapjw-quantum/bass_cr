"""Fresh tests for the exact integer-scaled reduced-cost potentials backend.

The old Python exact SSP and full-event SymPy LP are independent control paths.
No endpoint physics, cosmological IVP or measured He kernel is claimed.
"""
from __future__ import annotations
import random
import unittest
from fractions import Fraction as F
from native_budget import Atom
from generic_budget_flow import ExactBudgetFlow
from test_generic_budget_flow import oracle, counterexample
from potentials_bridge import run_exact, BIN

class TestPotentialsBridge(unittest.TestCase):
    def test_zero_mass_and_admissible_edges(self):
        atoms=(Atom.parse('high',5,1,1),Atom.parse('low',0,2,0),Atom.parse('ghost',0,0,1))
        for c in [F(0), F(4)]:
            z=run_exact(atoms,F(3),c)
            self.assertEqual(z['M'],0)
            self.assertEqual(z['gap'],0)
            self.assertEqual(z['d_max'],1)

    def test_integer_scaled_nondyadic_budget(self):
        a=counterexample()
        for c in [F(0),F(1,3),F(1,2),F(2),F(5)]:
            z=run_exact(a,F(4),c)
            self.assertEqual(z['d_max'],ExactBudgetFlow(a,4).witness(c)['d_max'])
            self.assertEqual(z['d_max'],oracle(a,4,c))

    def test_ten_atom_all_kinks(self):
        rows=[('h0','19/2','1/2',1),('h1','7','2',0),('h2','9','2',1),('h3','13/2','5/2',2),('h4','6','1/2',1),('l0','0','1',0),('l1','7/2','1',1),('l2','3/2','5/2',2),('l3','0','5/2',0),('l4','3/2','1/2',2)]
        a=tuple(Atom.parse(*r) for r in rows)
        cases=[(0,5),(1,6),(F(3,2),F(13,2)),(2,F(27,4)),(F(5,2),7),(3,F(43,6)),(4,F(15,2)),(10,F(15,2))]
        for c,m in cases:
            z=run_exact(a,F(10),F(c))
            self.assertEqual(z['M'],m)
            self.assertEqual(z['gap'],0)
            self.assertEqual(z['d_max'],oracle(a,10,F(c)))

    def test_seeded_random_75_lps(self):
        rng=random.Random(20261029)
        num=0
        for n in range(2,7):
            for trial in range(5):
                a=tuple(Atom.parse(f'a{i}',F(rng.randrange(0,11),2),F(rng.randrange(0,6),2),rng.randrange(4)) for i in range(n))
                K=F(rng.randrange(2,13),2)
                for c in (F(0),F(1,2),F(2)):
                    z=run_exact(a,K,c)
                    self.assertEqual(z['d_max'],oracle(a,K,c))
                    self.assertEqual(z['gap'],0)
                    num+=1
        self.assertEqual(num,75)

    def test_hard_errors(self):
        a=counterexample()
        with self.assertRaises(TypeError):run_exact(a,4.,F(1))
        with self.assertRaises(ValueError):run_exact(a,F(4),F(-1))
        with self.assertRaises(OverflowError):run_exact((Atom.parse('h',3,F(2)**108,0),Atom.parse('l',1,1,0)),F(5),F(1))

    def test_ubsan_separate_binary(self):
        san=BIN.with_name('potentials_ssp_ubsan')
        if san.exists():
            a=counterexample()
            z=run_exact(a,F(4),F(1,3),executable=san)
            self.assertEqual(z['gap'],0)
            self.assertEqual(z['M'],F(7,6))

if __name__=='__main__':unittest.main()