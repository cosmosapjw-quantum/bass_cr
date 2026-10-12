"""Targeted checks with explicit discrete delay measures, not prior CR suites."""
from fractions import Fraction as F
import unittest

from finite_age_closure import closure_budget, first_response, parameters, positive_response


class ClosureChecks(unittest.TestCase):
    def test_discrete_measure_affine_exact_and_quadratic_bound(self):
        # Delay atoms 0, 1/2 and 2. The late atom is excluded at T=1.
        early = [(F(1, 5), F(0)), (F(3, 10), F(1, 2))]
        p = sum((w for w, _ in early), F(0))
        r = sum((w * (1 - tau) for w, tau in early), F(0))
        s = sum((w * (1 - tau) ** 2 for w, tau in early), F(0))
        for coeff in [(F(1), F(0), F(0)), (F(2), F(3), F(0)), (F(0), F(0), F(1)), (F(0), F(2), F(-1))]:
            a, b, c = coeff
            q = lambda x: a + b * x + c * x * x
            exact = sum((w * q(1 - tau) for w, tau in early), F(0))
            approx = positive_response(p, r, s, q)
            self.assertEqual(abs(exact - approx), parameters(p, r, s)["C_positive"] * 2 * abs(c))
            self.assertGreaterEqual(approx, 0)

    def test_instantaneous_and_single_delay_limits(self):
        q = lambda x: 1 + x ** 4
        self.assertEqual(positive_response(F(1), F(1), F(1), q), q(F(1)))
        p, z = F(2, 5), F(1, 3)
        info = parameters(p, p * z, p * z * z)
        self.assertEqual(info["C_positive"], 0)
        self.assertEqual(positive_response(p, p * z, p * z * z, q), p * q(z))

    def test_no_early_mass_does_not_call_history(self):
        def forbidden(_):
            raise AssertionError("history must not be called")
        self.assertEqual(positive_response(F(0), F(0), F(0), forbidden), 0)

    def test_initial_endpoint_atom_preserved(self):
        self.assertEqual(positive_response(F(1, 2), F(0), F(0), lambda x: 7 if x == 0 else 0), F(7, 2))

    def test_invalid_moments_and_negative_source_rejected(self):
        for triple in [(F(-1), F(0), F(0)), (F(1), F(3, 4), F(1, 4)), (F(0), F(0), F(1)), (F(2), F(0), F(0))]:
            with self.assertRaises(ValueError):
                parameters(*triple)
        with self.assertRaises(ValueError):
            positive_response(F(1), F(1), F(1), lambda x: F(-1))

    def test_nonquadratic_curvature_bound_and_first_sign_failure(self):
        early = [(F(1, 5), F(1, 4)), (F(1, 5), F(3, 4))]
        p = F(2, 5)
        r = sum(w * x for w, x in early)
        s = sum(w * x * x for w, x in early)
        q = lambda x: x ** 3
        exact = sum(w * q(x) for w, x in early)
        approx = positive_response(p, r, s, q)
        self.assertLessEqual(abs(exact - approx), 6 * parameters(p, r, s)["C_positive"])
        self.assertGreater(exact, 0)
        self.assertLess(first_response(p, r, s, F(1), F(3)), 0)

    def test_budget_denominator_and_missing_input_contract(self):
        self.assertEqual(closure_budget(F(1, 10), F(1), F(1, 100), F(1, 1000))["status"], "FIXED_KERNEL_HEATING_CLOSURE_SUFFICIENT")
        self.assertEqual(closure_budget(F(1, 10), F(1), F(1), F(1, 1000))["status"], "BOUND_NOT_SUFFICIENT")
        with self.assertRaises(TypeError):
            closure_budget(F(1, 10), None, F(0), F(1))
        with self.assertRaises(ValueError):
            closure_budget(F(1, 10), F(1), F(1), F(0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
