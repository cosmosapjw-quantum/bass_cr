"""New synthetic-family checks; no physical B0 trajectory is implied."""
import unittest
import numpy as np
from numpy.testing import assert_allclose
from independent_propagator import SyntheticTrajectory, whitened_generator, propagate_cf4, benchmark


class IndependentPropagatorTests(unittest.TestCase):
    def test_cholesky_derivative_matches_independent_difference(self):
        p = SyntheticTrajectory(); t = 0.6; s = p.at(t)
        g = whitened_generator(s.S,s.H,s.D,s.Sdot)
        errors = []
        for h in (0.02,0.01,0.005):
            rp = np.linalg.cholesky(p.at(t+h).S).conj().T
            rm = np.linalg.cholesky(p.at(t-h).S).conj().T
            errors.append(np.linalg.norm((rp-rm)/(2*h)-g.X@g.R))
        self.assertTrue(all(3.9 < a/b < 4.1 for a,b in zip(errors,errors[1:])))

    def test_whitened_generator_antihermitian_and_same_ode(self):
        p = SyntheticTrajectory()
        for t in (0,0.4,1.3,3):
            s = p.at(t); g = whitened_generator(s.S,s.H,s.D,s.Sdot)
            assert_allclose(g.B+g.B.conj().T,0,atol=2e-14)
            h = 1e-5
            yp = np.linalg.cholesky(p.at(t+h).S).conj().T@p.exact(t+h)
            ym = np.linalg.cholesky(p.at(t-h).S).conj().T@p.exact(t-h)
            assert_allclose((yp-ym)/(2*h),g.B@g.R@p.exact(t),atol=3e-10)

    def test_connection_term_is_required(self):
        p = SyntheticTrajectory();s=p.at(0.6);g=whitened_generator(s.S,s.H,s.D,s.Sdot)
        A=np.linalg.solve(s.S,-1j*s.H-s.D)
        naive=g.R@A@np.linalg.solve(g.R,np.eye(2))
        self.assertGreater(np.linalg.norm(naive+naive.conj().T),0.1)
        self.assertLess(np.linalg.norm(g.B+g.B.conj().T),1e-13)

    def test_bad_compatibility_and_non_spd_are_rejected(self):
        p=SyntheticTrajectory();s=p.at(0.6)
        with self.assertRaisesRegex(ValueError,'compatibility'):
            whitened_generator(s.S,s.H,s.D,s.Sdot+0.01*np.eye(2))
        with self.assertRaises(np.linalg.LinAlgError):
            whitened_generator(np.diag([1,-1]),np.eye(2),np.zeros((2,2)),np.zeros((2,2)))

    def test_cf4_fourth_order_and_metric_norm(self):
        p=SyntheticTrajectory(); c0=p.exact(0); errors=[]
        for n in (8,16,32):
            out=propagate_cf4(p,c0,0,3,n)
            d=out['final_state']-p.exact(3);s=p.at(3).S
            errors.append(np.sqrt(np.vdot(d,s@d).real))
            self.assertLess(out['max_norm_drift'],2e-13)
        self.assertTrue(all(14 < a/b < 18 for a,b in zip(errors,errors[1:])))

    def test_benchmark_existing_families_same_trajectory(self):
        result=benchmark()
        self.assertLess(result['direct_dop853']['metric_state_error'],2e-11)
        self.assertLess(result['cf4'][-1]['metric_state_error'],2e-9)
        self.assertTrue(all(3.7 < x < 4.3 for x in result['midpoint_error_ratios']))
        self.assertTrue(all(14 < x < 18 for x in result['cf4_error_ratios']))
        self.assertFalse(result['physical_parity_certified'])


if __name__=='__main__': unittest.main(verbosity=2)
