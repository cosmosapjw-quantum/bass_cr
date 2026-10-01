import unittest
import numpy as np
from rank_policy import (canonical_truncation, pivoted_cholesky_selection,
                         new_basis_identity, synthetic_case, run_case)


class RankPolicyTest(unittest.TestCase):
    def test_diagonal_decisions_and_no_shift(self):
        S=np.diag([1.,.1,1e-9,0.]); old=S.copy()
        for method in (canonical_truncation,pivoted_cholesky_selection):
            r=method(S,1e-8)
            self.assertEqual(r['rank'],2)
            self.assertEqual(r['diagonal_shift'],0.)
            self.assertLess(np.linalg.norm(r['T'].conj().T@S@r['T']-np.eye(2)),1e-12)
        np.testing.assert_array_equal(S,old)

    def test_indefinite_and_nonhermitian_inputs_rejected(self):
        for method in (canonical_truncation,pivoted_cholesky_selection):
            with self.assertRaises(ValueError): method(np.diag([1.,-.01]),1e-8)
            with self.assertRaises(ValueError): method(np.array([[1.,.1],[0.,1.]]),1e-8)
            with self.assertRaises(ValueError): method(np.zeros((2,2)),1e-8)
            with self.assertRaises(ValueError): method(np.eye(2),0.)

    def test_declared_synthetic_rank_plateau(self):
        for case in ('near_spd','exact_psd'):
            rows=run_case(case)
            for method in ('canonical','pivoted_cholesky'):
                plateau=[r for r in rows if r['method']==method and r['relative_cutoff']>=1e-8]
                self.assertEqual([r['rank'] for r in plateau],[4,4])
                self.assertLess(abs(plateau[0]['rho']-plateau[1]['rho']),1e-10)
                self.assertLess(abs(plateau[0]['P_regular_unnormalized']-plateau[1]['P_regular_unnormalized']),1e-10)

    def test_svd_rank_audit_and_weak_state_loss(self):
        rows=run_case('near_spd')
        for row in rows:
            if row['method']=='canonical': self.assertEqual(row['rank'],row['svd_rank_audit'])
        truncated=[r for r in rows if r['method']=='canonical' and r['relative_cutoff']==1e-8][0]
        self.assertGreater(truncated['weak_state_norm_loss'],.99)

    def test_basis_identity_blocks_certificate_and_index_reuse(self):
        S=synthetic_case('near_spd')['S'];r=canonical_truncation(S,1e-8)
        a=new_basis_identity('SYNTHETIC',S,r);b=new_basis_identity('SYNTHETIC',S,r)
        self.assertEqual(a['new_hash'],b['new_hash'])
        self.assertTrue(a['new_operator_qualification_required'])
        self.assertTrue(a['new_temporal_certificate_required'])
        self.assertFalse(a['old_selected_indices_inheritable'])
        self.assertEqual(a['semantic_selection_status'],'REQUIRES_NEW_SEMANTIC_SUBSPACE_DEFINITION')
        c=new_basis_identity('SYNTHETIC',S,canonical_truncation(S,1e-6))
        self.assertNotEqual(a['new_hash'],c['new_hash'])

    def test_rank_policy_is_coordinate_dependent_and_disclosed(self):
        S=np.eye(2);T=np.diag([1.,1e-5]);Sp=T.T@S@T
        self.assertEqual(canonical_truncation(S,1e-8)['rank'],2)
        self.assertEqual(canonical_truncation(Sp,1e-8)['rank'],1)

    def test_tiny_negative_sign_is_uncertain_not_certified_psd(self):
        r=canonical_truncation(np.diag([1.,-1e-16]),1e-8)
        self.assertTrue(r['diagnostics']['negative_within_roundoff_uncertainty'])
        self.assertTrue(r['diagnostics']['high_precision_sign_audit_required_if_material'])
        self.assertEqual(r['diagnostics']['PSD_status'],'NUMERICAL_PSD_SCREEN_ONLY_NOT_CERTIFIED')

    def test_trace_residual_and_dimension_change_are_reported(self):
        S=synthetic_case('near_spd')['S'];r=pivoted_cholesky_selection(S,1e-8)
        self.assertLess(r['diagnostics']['residual_spectral_norm'],
                        r['absolute_threshold']+2*r['diagnostics']['numerical_psd_tolerance'])
        rows=run_case('near_spd')
        change=[x for x in rows if x['method']=='canonical' and x['relative_cutoff']==1e-10][0]
        self.assertGreater(change['retained_projector_distance_to_previous'],.99)


if __name__=='__main__':unittest.main()
