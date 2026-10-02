"""Offline controls for direct S-only differentiation and evidence admission."""
from fractions import Fraction
import hashlib
from pathlib import Path
import tempfile
import unittest
import numpy as np
import derivative_analyzer as a


class DerivativeAnalyzerTests(unittest.TestCase):
    def test_exact_rational_polynomial_moments_degrees_zero_through_eight(self):
        certificate=a.exact_weight_certificate()
        self.assertTrue(certificate['monomial_exactness_pass'])
        self.assertEqual(certificate['even_error_moments_k0_through_k4'],['1','0','0','0','-1/4096'])
        self.assertEqual(sum(a.R8_WEIGHTS),Fraction(1))

    def test_numeric_polynomial_on_each_actual_window(self):
        coefficients=np.array([[1+2j,-.5j],[3.,-2+1j]])
        for start in range(3):
            for degree in range(9):
                hs=a.H_LADDER[start:start+4]
                ladder=[(h,coefficients*(-h)**degree,coefficients*h**degree) for h in hs]
                fd=a.s_only_r8(ladder,2.)
                wanted=2*coefficients if degree==1 else np.zeros_like(coefficients)
                np.testing.assert_allclose(fd,wanted,atol=4e-15,rtol=0)

    def test_perturbed_D_changes_residual_but_not_S_only_derivative(self):
        samples={float(z).hex():np.eye(2,dtype=complex)*np.exp((.2+.1j)*z) for z in a.REQUIRED_Z}
        ladder=a.shifted_ladder(samples)[2:6]
        before=a.s_only_r8(ladder,1.)
        direct=np.eye(2,dtype=complex)*(.2+.1j)
        first=a.comparison(before,direct)
        altered_direct=direct+np.eye(2)*.1
        after=a.s_only_r8(ladder,1.)
        second=a.comparison(after,altered_direct)
        self.assertEqual(a.matrix_sha(before),a.matrix_sha(after))
        self.assertTrue(np.array_equal(before,after))
        self.assertTrue(first['pass'])
        self.assertFalse(second['pass'])

    def test_complex_smooth_control_two_finest_windows(self):
        coefficient=np.array([[.5+.2j,-.25+.1j],[.1-.2j,.3]])
        rate=.6+.3j
        samples={float(z).hex():coefficient*np.exp(rate*z) for z in a.REQUIRED_Z}
        ladder=a.shifted_ladder(samples)
        estimates=[a.s_only_r8(ladder[i:i+4],1.75) for i in (1,2)]
        exact=1.75*rate*coefficient
        for value in estimates:
            self.assertTrue(a.comparison(value,exact)['pass'])
        self.assertTrue(a.comparison(*estimates)['pass'])

    def test_missing_positive_or_negative_shift_is_rejected(self):
        values={float(z).hex():np.eye(2) for z in a.REQUIRED_Z}
        for z in (.025,-.0125):
            incomplete=dict(values);del incomplete[float(z).hex()]
            with self.assertRaisesRegex(ValueError,'missing required shifted S'):
                a.shifted_ladder(incomplete)

    def test_invalid_stencil_and_nonfinite_input_are_rejected(self):
        valid=[(h,np.eye(2),np.eye(2)) for h in a.H_LADDER[:4]]
        with self.assertRaisesRegex(ValueError,'exactly four'):
            a.s_only_r8(valid[:3],1.)
        bad=list(valid);bad[2]=(.12,np.eye(2),np.eye(2))
        with self.assertRaisesRegex(ValueError,'exact halving'):
            a.s_only_r8(bad,1.)
        bad=list(valid);bad[2]=(.1,np.eye(2),np.full((2,2),np.nan))
        with self.assertRaisesRegex(ValueError,'finite square'):
            a.s_only_r8(bad,1.)
        with self.assertRaisesRegex(ValueError,'positive finite velocity'):
            a.s_only_r8(valid,0.)

    def test_nonhermitian_data_are_preserved_without_projection(self):
        coefficient=np.array([[1j,2+3j],[4-2j,-1j]])
        ladder=[(h,-h*coefficient,h*coefficient) for h in a.H_LADDER[2:6]]
        result=a.s_only_r8(ladder,1.)
        np.testing.assert_allclose(result,coefficient,atol=2e-15,rtol=0)
        self.assertGreater(np.linalg.norm(result-result.conj().T),1.)

    def test_byte_tamper_rejected_before_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'payload.bin';path.write_bytes(b'raw-matrix-original')
            expected=hashlib.sha256(path.read_bytes()).hexdigest()
            a.verify_file_binding(path,expected)
            path.write_bytes(b'raw-matrix-altered!')
            with self.assertRaisesRegex(ValueError,'hash binding mismatch'):
                a.verify_file_binding(path,expected)

    def test_block_and_component_diagnostics_locate_error(self):
        fd=np.zeros((18,18),complex);direct=np.zeros_like(fd)
        fd[13,3]=2e-12+1e-12j
        blocks=a.residual_blocks(fd,direct)
        self.assertFalse(blocks['PT']['pass'])
        self.assertTrue(all(blocks[key]['pass'] for key in ('TT','TP','PP')))
        result=a.comparison(fd,direct)
        self.assertEqual(result['max_absolute_index_0_based'],[13,3])
        self.assertEqual(result['elementwise_denominator_floor'],1e-12)

    def test_original_R2_diagnostic_retains_failure(self):
        compare=a._original_compare_ladder()
        coefficient=np.eye(2,dtype=complex)
        ladder=[(h,coefficient*np.exp(-h),coefficient*np.exp(h)) for h in a.H_LADDER]
        D=.5*coefficient
        for subset in (ladder,ladder[:4]):
            result=compare(D,subset,1.)
            self.assertFalse(result['passed'])
            self.assertTrue(result['visible_second_order'])
            self.assertEqual(result['status'],'RESIDUAL_TARGET_NOT_MET')
        fine=a.s_only_r8(ladder[2:6],1.)
        self.assertTrue(a.comparison(fine,coefficient)['pass'])


if __name__=='__main__':
    unittest.main()
