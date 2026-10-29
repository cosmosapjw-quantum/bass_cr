"""Differential and adversarial checks of exact compressed original-dual audit."""
from fractions import Fraction as F
import random
import unittest
from native_budget import Atom
from prefix_dual_oracle import DualPrefixOracle, explicit_original_dual_check
from prefix_bridge import run_prefix

class DualPrefixTests(unittest.TestCase):
    def test_random_raw_inequalities_include_zeros_and_ties(self):
        r=random.Random(261029)
        for it in range(300):
            n=r.randint(1,24)
            rows=tuple(Atom.parse(f'k{i}',F(r.randrange(0,26),4),F(r.randrange(0,7),5),r.randrange(1,6)) for i in range(n))
            K=F(r.randint(0,35),4)
            prices={a.key:F(r.randint(0,12),r.randint(1,7)) for a in rows}
            lam=F(r.randint(0,6),r.randint(1,5))
            fast=DualPrefixOracle(rows,K)
            try:
                count=explicit_original_dual_check(rows,K,prices,lam)
                slow_ok=True
            except AssertionError:
                slow_ok=False
            try:
                count_fast, grouped=fast.verify(prices,lam)
                fast_ok=True
            except AssertionError as exc:
                fast_ok=False
                _,h,l=exc.args[0]
                ha=next(a for a in rows if a.key==h)
                la=next(a for a in rows if a.key==l)
                self.assertGreater(2*ha.energy,K)
                self.assertLessEqual(2*la.energy,K)
                self.assertLessEqual(ha.energy+la.energy,K)
                self.assertLess(prices[h]+prices[l]+lam*int(ha.bin!=la.bin),1)
            self.assertEqual(fast_ok,slow_ok,(it,K,rows,prices,lam))
            if slow_ok:
                self.assertEqual(count_fast,count)
                self.assertLessEqual(grouped,count)

    def test_structured_tamper_and_duplicate_energies(self):
        a=tuple(Atom.parse(*row) for row in [
            ('h0',2,1,0),('h1',F(5,2),0,1),('l0',0,0,0),
            ('l1',0,1,1),('l2',0,1,1),('l3',1,0,2)])
        k=F(3); z=DualPrefixOracle(a,k)
        p={x.key:F(1) for x in a}
        self.assertEqual(z.verify(p,F(0))[0],explicit_original_dual_check(a,k,p,F(0)))
        p={x.key:F(0) for x in a}
        with self.assertRaisesRegex(AssertionError,'UNCOMPRESSED_DUAL_EDGE_FAIL'):
            z.verify(p,F(0))
        with self.assertRaises(AssertionError):
            explicit_original_dual_check(a,k,p,F(0))

    def test_opt_in_integration_matches_original_and_invalid_mode(self):
        a=tuple(Atom.parse(*r) for r in [
            ('h0',F(5,2),2,0),('h1',F(9,4),1,2),
            ('l0',0,2,1),('l1',F(1,4),1,0),('zero',0,0,3)])
        qs=[F(0),F(1,3),F(1),F(7)]
        slow=run_prefix(a,F(3),qs,dual_check='explicit')
        fast=run_prefix(a,F(3),qs,dual_check='prefix_exact')
        for aa,bb in zip(slow,fast):
            for field in ('M','C','d_max','lambda_dual','flow','prices','gap','checked_edges','source_scale'):
                self.assertEqual(aa[field],bb[field],field)
            self.assertEqual(bb['dual_check_mode'],'prefix_exact')
            self.assertIsNotNone(bb['grouped_dual_constraints'])
        with self.assertRaisesRegex(ValueError,'INVALID_DUAL_CHECK_MODE'):
            run_prefix(a,F(3),qs,dual_check='unsafe')

if __name__=='__main__':unittest.main()
