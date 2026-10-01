"""Offline fit and diagnostic contracts; no native operator evaluations."""
import unittest
import numpy as np
from asymptotic_models import fit_model, predict, analyze, load_samples, branch_switch_example, evaluate_return

class ModelTests(unittest.TestCase):
    def test_exact_models_recover_predictions(self):
        r=np.array([16.,20.,24.,32.,48.,64.])
        cases={
            'M1':2.3/r**2,
            'M2':1.8/r**2.35,
            'M3':2.3/r**2-3.7/r**3,
            'M4':2.3/r**2-3.7/r**3+5.1/r**4,
        }
        for name,y in cases.items():
            with self.subTest(name=name):
                fit=fit_model(name,r,y)
                np.testing.assert_allclose(predict(fit,r),y,rtol=1e-7,atol=1e-15)
                self.assertLess(fit['max_relative_training_residual'],1e-7)
        self.assertAlmostEqual(fit_model('M2',r,cases['M2'])['exponent'],2.35,places=6)

    def test_reject_nonpositive_and_underdetermined(self):
        for r,y in [([1,2],[1,0]),([1,2],[1,np.nan]),([0,2],[1,2])]:
            with self.assertRaises(ValueError):fit_model('M1',r,y)
        with self.assertRaises(ValueError):fit_model('M4',[16,32],[.1,.2])
        with self.assertRaises(ValueError):fit_model('M4',[16,16,32],[.1,.1,.2])

    def test_signed_rows_remain_separate_and_effective_radius_count_is_four(self):
        report=analyze(load_samples())
        self.assertEqual(report['sample_count'],8)
        self.assertEqual(report['unique_absolute_z_count'],4)
        self.assertEqual(len(report['signed_fits']['incoming']['M1']['training_radii_a0']),4)
        self.assertLess(report['signed_symmetry_max_relative_difference'],1e-12)
        self.assertGreater(report['signed_fits']['outgoing']['M2']['exponent'],2.1)
        self.assertLess(abs(report['outer_sensitivity']['outgoing']['drop_abs_z_16']['M2']['exponent']-2),.01)
        self.assertFalse(report['continuous_certificate'])

    def test_parity_only_removes_linear_term_for_smooth_dominant_branch(self):
        B2=np.array([[0.,2.],[1.,0.]])
        B3=np.diag([.3,.7]);U=np.diag([1.,-1.])
        np.testing.assert_allclose(U@B2@U,-B2)
        np.testing.assert_allclose(U@B3@U,B3)
        norm=lambda e:np.linalg.norm(B2+e*B3,2)
        self.assertAlmostEqual(norm(.01),norm(-.01),places=14)
        ratio=(norm(.001)-2)/(norm(.0005)-2)
        self.assertAlmostEqual(ratio,4.,places=5)
        degenerate=np.array([[0.,1.],[1.,0.]])
        self.assertAlmostEqual(np.linalg.norm(degenerate+.001*np.eye(2),2),1.001,places=14)

    def test_branch_switch_is_possible_despite_smooth_matrix(self):
        v=branch_switch_example(np.array([2.,3.,4.]))
        np.testing.assert_allclose(v,[3/8,1/9,1/16])

class ReturnTests(unittest.TestCase):
    def make_return(self):
        baseline=load_samples(); report=analyze(baseline); rows=[]
        for sign,name in [(-1,'incoming'),(1,'outgoing')]:
            fit=report['outer_sensitivity'][name]['drop_abs_z_16']['M1']
            rows.append({'z_a0':sign*48.,'R_a0':float(np.hypot(48,2)),
                         'rho_per_atomic_time':float(predict(fit,np.hypot(48,2))),
                         'qualified':True,'adjacent_relative_rho_discrepancy':1e-10})
        return baseline,{'samples':rows}

    def test_return_scores_frozen_predictions_before_refit(self):
        baseline,returned=self.make_return();r=evaluate_return(baseline,returned)
        for sign in ('incoming','outgoing'):
            self.assertLess(r['per_sign'][sign]['outer_three_frozen_holdout']['M1']['relative_residual'],1e-12)
            self.assertEqual(r['per_sign'][sign]['recommended_next_pair_abs_z_a0'],44)
        self.assertFalse(r['execution_authorized'])
        self.assertFalse(r['continuous_certificate'])

    def test_return_rejects_wrong_scope_or_unqualified(self):
        baseline,returned=self.make_return()
        returned['samples'][0]['qualified']=False
        with self.assertRaises(ValueError):evaluate_return(baseline,returned)
        baseline,returned=self.make_return()
        returned['samples'][0]['z_a0']=-64
        with self.assertRaises(ValueError):evaluate_return(baseline,returned)

if __name__=='__main__':unittest.main()
