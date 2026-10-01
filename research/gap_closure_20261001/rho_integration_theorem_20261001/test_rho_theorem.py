"""Synthetic finite-model tests; no B0 physical trajectory is represented here."""
import unittest
import numpy as np
from numpy.testing import assert_allclose
from scipy.linalg import expm, eigh

from rho_theorem import rate_forms


def fixture(t=0.3):
    b = np.array([[1, t + 0.2j, 0], [0, 1.3, 0.1j*t], [0, 0, 0.8]], complex)
    bd = np.array([[0, 1, 0], [0, 0, 0.1j], [0, 0, 0]], complex)
    h = np.array([[0.2, 0.3j, 0.1], [-0.3j, -0.4, 0], [0.1, 0, 0.7]], complex)
    s, d, H = b.conj().T@b, b.conj().T@bd, b.conj().T@h@b
    j = np.array([[1, 0], [0.3j, 1], [0.1, 0.2j]], complex)
    return b, h, s, H, d, d+d.conj().T, j


class TheoremTests(unittest.TestCase):
    def test_projector_and_quadratic_form_are_distinct(self):
        _, _, s, h, d, sd, j = fixture()
        f = rate_forms(s, h, d, sd, j)
        assert_allclose(f.Pi@f.Pi, f.Pi, atol=2e-14)
        assert_allclose(f.Pi.conj().T@s, s@f.Pi, atol=2e-14)
        assert_allclose(f.Q.conj().T, f.Q, atol=2e-14)
        assert_allclose(f.Q@np.linalg.solve(s, f.Q), f.Q, atol=2e-14)
        self.assertGreater(np.linalg.norm(f.Q@f.Q-f.Q), 0.1)

    def test_metric_norm_generator_identity(self):
        _, _, s, h, d, sd, j = fixture()
        f = rate_forms(s, h, d, sd, j)
        assert_allclose(sd+f.A.conj().T@s+s@f.A, 0, atol=2e-14)

    def test_qdot_independent_centered_difference_order(self):
        _, _, s, h, d, sd, j = fixture()
        f = rate_forms(s, h, d, sd, j)
        errors = []
        for step in (0.04, 0.02, 0.01):
            qs = []
            for t in (0.3-step, 0.3+step):
                _, _, st, ht, dt, sdt, jt = fixture(t)
                qs.append(rate_forms(st, ht, dt, sdt, jt).Q)
            errors.append(np.linalg.norm((qs[1]-qs[0])/(2*step)-f.Qdot))
        self.assertTrue(all(3.8 < a/b < 4.2 for a, b in zip(errors, errors[1:])))

    def test_probability_derivative_of_exact_synthetic_trajectory(self):
        t = 0.3
        b, hp, s, h, d, sd, j = fixture(t)
        y0 = np.array([1, 2j, -0.5], complex)
        y0 /= np.linalg.norm(y0)
        c = np.linalg.solve(b, expm(-1j*hp*t)@y0)
        f = rate_forms(s, h, d, sd, j)
        expected = np.vdot(c, f.W@c).real
        probs = []
        for tt in (t-1e-5, t+1e-5):
            bt, ht, st, Ht, dt, sdt, jt = fixture(tt)
            ct = np.linalg.solve(bt, expm(-1j*ht*tt)@y0)
            ft = rate_forms(st, Ht, dt, sdt, jt)
            probs.append(np.vdot(ct, ft.Q@ct).real)
            self.assertAlmostEqual(np.vdot(ct, st@ct).real, 1, places=13)
        self.assertAlmostEqual((probs[1]-probs[0])/2e-5, expected, places=9)

    def test_pointwise_bound_and_unnormalized_saturation(self):
        _, _, s, h, d, sd, j = fixture()
        f = rate_forms(s, h, d, sd, j)
        values, vectors = eigh(f.W, s)
        c = 3*vectors[:, np.argmax(abs(values))]
        norm = np.vdot(c, s@c).real
        self.assertAlmostEqual(norm, 9, places=12)
        self.assertAlmostEqual(abs(np.vdot(c, f.W@c)), norm*f.rho, places=11)
        rng = np.random.default_rng(2031)
        for _ in range(20):
            c = rng.normal(size=3)+1j*rng.normal(size=3)
            self.assertLessEqual(abs(np.vdot(c, f.W@c)), np.vdot(c, s@c).real*f.rho+1e-12)

    def test_selected_probability_bounds(self):
        _, _, s, h, d, sd, j = fixture()
        f = rate_forms(s, h, d, sd, j)
        lam = eigh(f.Q, s, eigvals_only=True)
        assert_allclose(lam, [0, 1, 1], atol=2e-14)

    def test_finite_interval_analytic_example(self):
        g = 0.7
        f = rate_forms(np.eye(2), [[0,g],[g,0]], np.zeros((2,2)), np.zeros((2,2)), [[1],[0]])
        self.assertAlmostEqual(f.rho, g)
        for a, b in ((0,0.2),(0.4,1.8),(1,4)):
            change = abs(np.cos(g*b)**2-np.cos(g*a)**2)
            self.assertLessEqual(change, g*(b-a))

    def test_integrable_tail_exact_example(self):
        alpha = 0.8
        pinf = np.cos(alpha)**2
        for t in (0,1,2,10,100):
            g = alpha/(1+t)**2
            f = rate_forms(np.eye(2), [[0,g],[g,0]], np.zeros((2,2)), np.zeros((2,2)), [[1],[0]])
            self.assertAlmostEqual(f.rho, g)
            p = np.cos(alpha*t/(1+t))**2
            self.assertLessEqual(abs(pinf-p), alpha/(1+t))

    def test_nonintegrable_rho_does_not_force_a_limit(self):
        # Constant H=sigma_x gives rho=1 and P=cos(t)^2 with two subsequence limits.
        f = rate_forms(np.eye(2), [[0,1],[1,0]], np.zeros((2,2)), np.zeros((2,2)), [[1],[0]])
        self.assertEqual(f.rho, 1)
        assert_allclose([np.cos(10*np.pi)**2, np.cos(10*np.pi+np.pi/2)**2], [1,0], atol=1e-28)

    def test_constant_nonunitary_basis_covariance(self):
        _, _, s, h, d, sd, j = fixture()
        f = rate_forms(s, h, d, sd, j)
        T = np.array([[1.2,0.1j,0.2],[0.1,0.7,0],[0,0.1j,1.1]], complex)
        change = lambda x: T.conj().T@x@T
        fp = rate_forms(change(s), change(h), change(d), change(sd), np.linalg.solve(T,j))
        assert_allclose(fp.Pi, np.linalg.solve(T,f.Pi@T), atol=3e-14)
        assert_allclose(fp.Q, change(f.Q), atol=3e-14)
        assert_allclose(fp.W, change(f.W), atol=3e-14)
        assert_allclose(fp.eigenvalues, f.eigenvalues, atol=3e-14)
        c = np.array([0.2j,0.3,0.4]); cp = np.linalg.solve(T,c)
        assert_allclose(np.vdot(cp, change(s)@cp), np.vdot(c,s@c), atol=2e-14)
        assert_allclose(np.vdot(cp, fp.Q@cp), np.vdot(c,f.Q@c), atol=2e-14)

    def test_incompatible_derivative_rejected_and_norm_failure_exposed(self):
        s = np.eye(2); h = np.zeros((2,2)); d = np.zeros((2,2)); sd = 2*np.eye(2)
        with self.assertRaisesRegex(ValueError, 'compatibility'):
            rate_forms(s,h,d,sd,[[1],[0]])
        # c is constant because A=0; c^dag S(t)c=exp(2t) for S(t)=exp(2t)I.
        self.assertEqual(float(np.array([1,0])@sd@np.array([1,0])), 2)

    def test_invalid_metric_selector_and_hermiticity_are_not_repaired(self):
        z = np.zeros((2,2))
        for s in (np.diag([1,0]), np.diag([1,-1])):
            with self.assertRaises(np.linalg.LinAlgError):
                rate_forms(s,z,z,z,[[1],[0]])
        with self.assertRaises(np.linalg.LinAlgError):
            rate_forms(np.eye(2),z,z,z,[[1,1],[0,0]])
        with self.assertRaisesRegex(ValueError, 'Hermitian'):
            rate_forms(np.eye(2),[[0,1],[0,0]],z,z,[[1],[0]])


if __name__ == '__main__':
    unittest.main(verbosity=2)
