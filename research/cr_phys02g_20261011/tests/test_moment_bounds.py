"""Targeted frozen-contract implementation tests, no actual cached analysis."""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from moment_bounds import bounds, construct_model, envelope, horizon_brackets, comparison, MomentError


def synthetic(p=.2, mu=4., second=24.):
    r=dict(H0=1.,p=p,R=.1,S=.05,mu_s=mu,m2_s2=second)
    return dict(birth_columns=[r.copy(),r.copy()],selected=dict(r,H0=2.))


class FrozenMomentTests(unittest.TestCase):
    def test_generic_strict_and_branches(self):
        self.assertEqual(bounds(2.,6.,0.)['lower'],2/3)
        self.assertEqual(bounds(2.,6.,2.)['upper'],1.)
        self.assertEqual(bounds(2.,6.,2.5)['upper'],.8)
        self.assertEqual(bounds(2.,6.,3.)['upper'],2/3)
        self.assertEqual(bounds(2.,6.,4.)['upper'],1/3)
        self.assertEqual(bounds(2.,4.,2.)['upper'],0.)
        self.assertEqual(bounds(2.,4.,math.nextafter(2.,0.))['lower'],1.)
        self.assertEqual(bounds(0.,0.,0.)['lower'],0.)

    def test_typed_invalid(self):
        for args,code in [((-1,1,0),'NEGATIVE_INPUT'),((1,.99,0),'NEGATIVE_VARIANCE'),
                          ((0,1,0),'ZERO_MEAN_POSITIVE_SECOND'),
                          ((math.nan,1,0),'NONFINITE_OR_NONSCALAR')]:
            with self.assertRaises(MomentError) as raised:bounds(*args)
            self.assertEqual(raised.exception.code,code)
        with self.assertRaises(MomentError):construct_model(synthetic(),0)

    def test_residual_endpoint_and_mixture(self):
        m=construct_model(synthetic(),1.)
        e=envelope(m,1.)
        self.assertEqual(e['intersection'],dict(lower=.8,upper=.8,branch='KNOWN_SELECTED_TAIL_MASS'))
        self.assertEqual(e['birth_residual']['upper'],.8)
        self.assertEqual(m['selected']['tail_residual']['mean_s'],3.875)
        self.assertTrue(comparison(m['selected']['tail_residual']['second_s2'],21.1875)['pass_check'])
        with self.assertRaises(MomentError):envelope(m,.5)
        bad=synthetic();bad['selected']['H0']=3.
        with self.assertRaises(MomentError):construct_model(bad,1.)

    def test_positive_residual_cannot_be_zero(self):
        r=dict(H0=1.,p=.5,R=.5,S=.5,mu_s=.5,m2_s2=.5)
        with self.assertRaises(MomentError) as raised:
            construct_model(dict(birth_columns=[r],selected=r.copy()),1.)
        self.assertEqual(raised.exception.code,'INCOMPATIBLE_POSITIVE_RESIDUAL')

    def test_zero_tail(self):
        r=dict(H0=1.,p=1.,R=.5,S=.3,mu_s=.5,m2_s2=.3)
        m=construct_model(dict(birth_columns=[r],selected=r.copy()),1.)
        self.assertEqual(m['selected']['tail_residual']['status'],'UNDEFINED_ZERO_TAIL')
        self.assertEqual(envelope(m,2.)['intersection']['upper'],0.)

    def test_monotonicity_and_intersection(self):
        m=construct_model(synthetic(),1.)
        previous={k:(1.,1.) for k in ('unconditional','pooled_residual','birth_residual','intersection')}
        for t in [1.,1.+1e-8]+[1.+i*.25 for i in range(1,160)]:
            e=envelope(m,t)
            for k in previous:
                l,u=e[k]['lower'],e[k]['upper']
                self.assertTrue(0<=l<=u<=1)
                self.assertLessEqual(l,previous[k][0]+2e-14)
                self.assertLessEqual(u,previous[k][1]+2e-14)
                previous[k]=(l,u)
            if t>1:
                self.assertGreaterEqual(e['intersection']['lower'],max(e[k]['lower'] for k in previous if k!='intersection'))
                self.assertLessEqual(e['intersection']['upper'],min(e[k]['upper'] for k in previous if k!='intersection'))

    def test_bracket_receipts(self):
        m=construct_model(synthetic(),1.)
        for f in (.5,.9,.95,.99,.999):
            b=horizon_brackets(m,f)
            self.assertGreater(b['lower_value'],1-f)
            self.assertLessEqual(b['upper_value'],1-f)
            self.assertLessEqual(b['lower_s'],b['upper_s'])
            for k in ('lower_bisection','upper_bisection'):
                self.assertLessEqual(b[k]['iterations'],80)
        self.assertEqual(horizon_brackets(m,.1)['upper_s'],1.)

if __name__=='__main__':unittest.main(verbosity=2)
