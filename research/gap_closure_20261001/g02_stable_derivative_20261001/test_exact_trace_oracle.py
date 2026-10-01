import unittest
import hashlib
import json
from pathlib import Path
import tempfile
from decimal import Decimal, localcontext
from fractions import Fraction as F
import exact_trace_oracle as oracle


class ExactTraceTests(unittest.TestCase):
    def test_polynomial_ibp_is_exact_with_nonzero_trace(self):
        a=[F(2),F(-3),F(5)];b=[F(-1),F(4),F(0),F(2)]
        self.assertEqual(oracle.derivative_integral(a,b)+oracle.derivative_integral(b,a),sum(a)*sum(b)-a[0]*b[0])

    def test_continuous_dirichlet_two_cell_pair_has_zero_trace(self):
        a=[[F(0),F(2)],[F(2),F(-2)]]
        b=[[F(0),F(3)],[F(3),F(-3)]]
        self.assertEqual(oracle.trace_pair(a,b),0)

    def test_internal_jump_and_outer_boundary_both_enter(self):
        a=[[F(0),F(2)],[F(3),F(-2)]]
        b=[[F(0),F(5)],[F(7),F(-4)]]
        self.assertEqual(oracle.trace_pair(a,b),F(10)+F(3)-F(21))

    def test_inverse_radial_integral_known_origin_and_log(self):
        with localcontext() as c:
            c.prec=80
            self.assertEqual(oracle.radial_inverse_integral([[F(0),F(1)]],[[F(0),F(1)]],[F(0),F(2)]),Decimal('0.5'))
            got=oracle.radial_inverse_integral([[F(1)]],[[F(1)]],[F(1),F(2)])
            self.assertEqual(got,Decimal(2).ln())

    def test_sp_angular_sign_with_linear_example(self):
        r=oracle.coupling([[F(0),F(1)]],[[F(0),F(1)]],[F(0),F(1)],F(2),80)
        with localcontext() as c:
            c.prec=80
            self.assertLess(abs(Decimal(r['D_sp'])+Decimal(2)/Decimal(3).sqrt()),Decimal('1e-75'))
            self.assertEqual(Decimal(r['D_ps']),0)

    def test_candidate_is_separate_exact_and_has_known_l2_change(self):
        a=[[F(0),F(2)],[F(3),F(-2)]];saved=[x[:] for x in a]
        r,candidate=oracle.mode_record(a,[F(0),F(1),F(2)])
        self.assertEqual(a,saved)
        self.assertEqual(candidate,[[F(0),F(3)],[F(3),F(-3)]])
        self.assertEqual(oracle.trace_pair(candidate,candidate),0)
        with localcontext() as c:
            c.prec=80
            self.assertLess(abs(Decimal(r['candidate_radial_L2_change'])-(Decimal(2)/3).sqrt()),Decimal('1e-75'))

    def test_nonintegrable_origin_is_rejected(self):
        with self.assertRaises(ValueError):
            oracle.radial_inverse_integral([[F(1)]],[[F(1)]],[F(0),F(1)])

    def test_metadata_semantic_identity_does_not_replace_byte_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'BASIS.json'
            p.write_text('{"identity":"same", "modes":[]}')
            context={'input_files':{'BASIS.json':hashlib.sha256(p.read_bytes()).hexdigest()}}
            self.assertEqual(oracle.metadata_bound_to_context(p,context)['identity'],'same')
            p.write_text('{"identity":"same", "modes":[{"l":1}]}')
            with self.assertRaisesRegex(ValueError,'metadata bytes'):
                oracle.metadata_bound_to_context(p,context)


if __name__=='__main__':
    unittest.main()
