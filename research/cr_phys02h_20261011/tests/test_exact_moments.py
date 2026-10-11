"""Targeted exact arithmetic and representation isolation checks, stdlib only."""
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from exact_moments import (MomentError, bounds, comparison, construct_model, envelope,
                           horizon_bracket, identity, check_identity, load_exact, record)


def law(early, tail, p=F(1,4), H0=F(1), T=F(10)):
    """Independent literal finite-law moment oracle (conditional atom weights)."""
    pairs = [(t,p*w) for t,w in early]+[(t,(1-p)*w) for t,w in tail]
    return dict(H0=H0,p=p,
                R=sum((p*w*(1-t/T) for t,w in early),F(0)),
                S=sum((p*w*(1-t/T)**2 for t,w in early),F(0)),
                mu_s=sum((t*w for t,w in pairs),F(0)),
                m2_s2=sum((t*t*w for t,w in pairs),F(0)))


class ExactMomentTests(unittest.TestCase):
    def assertCode(self, code, callback):
        with self.assertRaises(MomentError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def test_original_tokens_and_source_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'tokens.json'
            path.write_text('{"x":0.10000000000000001,"n":9007199254740993,"e":1.2e3}')
            raw = load_exact(path)
            self.assertEqual(raw['x'], F('0.10000000000000001'))
            self.assertNotEqual(raw['x'], F(float('0.10000000000000001')))
            self.assertEqual(raw['n'], F(9007199254740993))
            self.assertEqual(raw['e'], F(1200))
            pin = identity(path)
            self.assertEqual(check_identity(path,pin),pin)
            path.write_text(path.read_text()+' ')
            self.assertCode('SOURCE_IDENTITY_MISMATCH',lambda:check_identity(path,pin))

    def test_bounds_branches_and_strict_deterministic_endpoint(self):
        self.assertEqual(bounds(2,4,2)['lower'],0)
        self.assertEqual(bounds(2,4,F(199,100))['upper'],1)
        self.assertEqual(bounds(0,0,0)['upper'],0)
        self.assertEqual(bounds(2,6,1)['lower'],F(1,3))
        self.assertEqual(bounds(2,6,2)['upper'],1)
        self.assertEqual(bounds(2,6,F(5,2))['upper'],F(4,5))
        self.assertEqual(bounds(2,6,3)['upper'],F(2,3))
        self.assertCode('ZERO_MEAN_POSITIVE_SECOND',lambda:bounds(0,1,0))
        self.assertCode('NEGATIVE_VARIANCE',lambda:bounds(2,3,0))
        self.assertCode('NONEXACT_INPUT',lambda:bounds(2.,4,0))
        self.assertCode('NEGATIVE_INPUT',lambda:bounds(1,2,-1))

    def test_cross_products_distinguish_strict_and_closed(self):
        proof = comparison(F(1,3)+F(1,10**80),F(1,3),'>')
        self.assertTrue(proof['passed'])
        self.assertGreater(proof['lhs_integer'],proof['rhs_integer'])
        self.assertFalse(comparison(F(1,3),F(1,3),'>')['passed'])
        self.assertTrue(comparison(F(1,3),F(1,3),'<=')['passed'])

    def test_witness_degenerate_and_nondegenerate(self):
        for early,tail,early_case,tail_case in (
            ([(F(10),F(1))],[(F(12),F(1))],'ZERO_U','DETERMINISTIC_POSITIVE_RESIDUAL'),
            ([(F(5),F(1))],[(F(12),F(1))],'DETERMINISTIC_U','DETERMINISTIC_POSITIVE_RESIDUAL'),
            ([(F(0),F(1,3)),(F(7),F(2,3))],[(F(12),F(1,2)),(F(20),F(1,2))],
             'TWO_ATOM_U','TWO_ATOM_POSITIVE_RESIDUAL')):
            r = record(law(early,tail),10)
            self.assertEqual(r['witness']['early_case'],early_case)
            self.assertEqual(r['witness']['tail_case'],tail_case)
            self.assertTrue(r['witness']['support_pass'])
            self.assertTrue(all(z['passed'] for z in r['witness']['reconstruction'].values()))

    def test_incompatible_early_and_tail(self):
        good = law([(F(5),F(1))],[(F(12),F(1))])
        for change in ({'H0':F(0)},{'p':F(0)},{'p':F(1)}, {'S':F(-1)},
                       {'S':F(1)}, {'R':F(1)}, {'S':F(1,1000)}):
            row = dict(good,**change)
            self.assertCode('INCOMPATIBLE_EARLY_MOMENTS',lambda row=row:record(row,10))
        row = dict(good,mu_s=F(1))
        self.assertCode('INCOMPATIBLE_POSITIVE_RESIDUAL',lambda:record(row,10))
        row = dict(good,m2_s2=F(1))
        self.assertCode('INCOMPATIBLE_POSITIVE_RESIDUAL',lambda:record(row,10))

    def test_representation_isolation_despite_inconsistent_selected(self):
        early = [(F(5),F(1))]
        s = law(early,[(F(12),F(1))])
        b = law(early,[(F(100),F(1))])
        model = construct_model(dict(selected=s,birth_columns=[b]),10)
        other = construct_model(dict(selected=s,birth_columns=[s]),10)
        selected = envelope(model,'selected_record',13)
        self.assertEqual(selected,envelope(other,'selected_record',13))
        self.assertEqual(set(selected['components']),{'unconditional','pooled_residual'})
        self.assertEqual(selected['intersection']['upper'],0)
        self.assertEqual(envelope(model,'birth_defined',13)['intersection']['upper'],F(3,4))
        self.assertNotEqual(model['exact_selected_vs_birth_differences']['mu_s']['selected_minus_birth_defined'],0)
        self.assertEqual(model['representations']['birth_defined']['pooled']['mu_s'],b['mu_s'])

    def test_birth_weights_and_pooled_primitives(self):
        early = [(F(5),F(1))]
        one = law(early,[(F(12),F(1))],H0=F(1))
        two = law(early,[(F(30),F(1))],H0=F(3))
        model = construct_model(dict(selected=one,birth_columns=[one,two]),10)
        rep = model['representations']['birth_defined']
        self.assertEqual(rep['weights'],[F(1,4),F(3,4)])
        self.assertEqual(rep['pooled']['mu_s'],(one['mu_s']+3*two['mu_s'])/4)
        self.assertEqual(rep['pooled']['H0'],4)
        self.assertEqual(envelope(model,'birth_defined',10)['intersection'],dict(lower=F(3,4),upper=F(3,4)))

    def test_integer_bracket_adjacent_endpoints_and_budget(self):
        row = law([(F(5),F(1))],[(F(12),F(1))])
        model = construct_model(dict(selected=row,birth_columns=[row]),10)
        for representation in ('selected_record','birth_defined'):
            c = horizon_bracket(model,representation,F(1,2))
            self.assertEqual((c['lower_s'],c['upper_s']),(11,12))
            self.assertTrue(c['lower_endpoint_proof']['passed'])
            self.assertTrue(c['upper_endpoint_proof']['passed'])
            for search in c['searches'].values():
                self.assertEqual(search['final_s'][1]-search['final_s'][0],1)
                self.assertLessEqual(search['doublings'],64)
                self.assertLessEqual(search['bisections'],80)
            self.assertCode('NO_STRICT_T_LOWER_ENDPOINT',lambda:horizon_bracket(model,representation,F(1,4)))
        self.assertCode('THRESHOLD_BEFORE_T',lambda:envelope(model,'selected_record',9))


if __name__=='__main__':
    unittest.main(verbosity=2)
