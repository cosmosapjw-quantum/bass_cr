"""Focused, independent algebraic and boundary tests for the new diagnostics."""
import copy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diagnostics import (BIND_EV, KB_EV, DiagnosticInputError,
                         compare_endpoints, recompute_balances, signed_order,
                         reference_free_order, conditional_order_interval,
                         two_scale_coefficients)


def fixture(Y=0., amounts=(.1,)):
    x0 = math.log(.1)
    return {"x0": x0, "dx": .001, "nh0": 1e-7, "Y": Y,
            "gas0": [.2, .1 if Y else 0., .02 if Y else 0., 1.],
            "q": [2.] * len(amounts), "birth": [x0] * len(amounts),
            "amounts": list(amounts), "opacity_scale": 1.,
            "source_identity": "MANUFACTURED_DIAGNOSTIC_ALGEBRA_ONLY"}


def endpoint(f):
    return {"gas": list(f["gas0"]), "photons": list(f["amounts"])}


def empty_ledgers():
    return {"photo": [0., 0., 0.], "ci": [0., 0., 0.], "rr": [0., 0., 0.],
            "dr": 0., "heat": 0., "escape": 0., "cmb": 0., "photon_work": 0.,
            "gas_work": 0., "source_n": 0., "source_u": 0.}


class EndpointTests(unittest.TestCase):
    def test_strict_shapes_nonfinite_and_physical_domain(self):
        f = fixture()
        for field, value in (("gas", [.2, 0., 0.]), ("gas", [.2, 0., 0., float("nan")]),
                             ("gas", [.2, .01, 0., 1.]), ("gas", [1.01, 0., 0., 1.]),
                             ("gas", [.2, 0., 0., 0.]), ("photons", [-1e-30]),
                             ("photons", [.1, 0.]), ("photons", [float("inf")])):
            bad = endpoint(f)
            bad[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(DiagnosticInputError):
                compare_endpoints(f, bad, endpoint(f))
        for key, value in (("Y", -1.), ("Y", True), ("dx", 0.), ("q", [0.])):
            badf = copy.deepcopy(f)
            badf[key] = value
            with self.subTest(key=key), self.assertRaises(DiagnosticInputError):
                compare_endpoints(badf, endpoint(f), endpoint(f))

    def test_signed_gas_and_exact_eos_identity(self):
        f = fixture(Y=.1)
        left, right = endpoint(f), endpoint(f)
        left["gas"] = [.23, .11, .03, 1.00001]
        r = compare_endpoints(f, left, right)
        self.assertAlmostEqual(r["gas_signed"]["x_HII"], .03)
        self.assertEqual(r["active_gas_components"], ["x_HII"])
        # Direct rational EOS independently provides the same finite-state
        # difference; this tests composition as well as energy dependence.
        def T(g):
            x, y, z, w = g
            return (2 * w / (3 * KB_EV)) / (1.1 + x + .1 * y + .2 * z)
        expected = T(left["gas"]) - T(right["gas"])
        self.assertAlmostEqual(r["temperature"]["stable_identity_delta_K"], expected, delta=2e-12)
        self.assertIsNone(r["global_error_bound"])

    def test_optical_underflow_keeps_log_and_structural_zero(self):
        f = fixture(amounts=(.5, 0.))
        left, right = endpoint(f), endpoint(f)
        for r, tau in ((left, 801.), (right, 800.)):
            r.update(photons=[0., 0.], optical_depth=[tau, 20.],
                     log_survivor=[math.log(.5) - tau, None])
        p = compare_endpoints(f, left, right)["photons"]
        self.assertEqual(p["left_underflowed_positive_cohorts"], 1)
        self.assertEqual(p["right_underflowed_positive_cohorts"], 1)
        self.assertEqual(p["log_comparable_positive_weight_cohorts"], 1)
        self.assertEqual(p["max_absolute_log_delta"], 1.)
        self.assertEqual(p["max_absolute_count_delta_H"], 0.)
        self.assertIsNone(p["cohorts"][1]["log_survivor_delta"])
        unknown = endpoint(f)
        unknown["photons"] = [0., 0.]
        q = compare_endpoints(f, unknown, right)["photons"]
        self.assertEqual(q["left_underflowed_positive_cohorts"], 0)
        self.assertEqual(q["left_zero_count_unknown_log_cohorts"], 1)
        self.assertEqual(q["positive_weight_log_unavailable_pairs"], 1)
        self.assertIsNone(q["cohorts"][0]["stable_count_delta_H"])

    def test_common_amount_cancels_before_log_subtraction(self):
        f = fixture(amounts=(.5,))
        left, right = endpoint(f), endpoint(f)
        for r, tau in ((left, 1e-17), (right, 0.)):
            r.update(photons=[math.exp(math.log(.5) - tau)], optical_depth=[tau])
        row = compare_endpoints(f, left, right)["photons"]["cohorts"][0]
        self.assertEqual(row["count_delta_H"], 0.)
        self.assertEqual(row["log_survivor_delta"], -1e-17)
        self.assertAlmostEqual(row["stable_count_delta_H"], -5e-18, delta=1e-33)


class LedgerTests(unittest.TestCase):
    def test_number_binding_and_redshift_energy_recomputation(self):
        f = fixture()
        r = endpoint(f)
        absorbed = .01
        final_energy = f["q"][0] * math.exp(-(f["x0"] + f["dx"]))
        r["photons"] = [.1 - absorbed]
        r["gas"][0] += absorbed
        r["gas"][3] += absorbed * (final_energy - BIND_EV[0])
        r["ledgers"] = empty_ledgers()
        r["ledgers"]["photo"][0] = absorbed
        r["ledgers"]["heat"] = absorbed * (final_energy - BIND_EV[0])
        r["ledgers"]["photon_work"] = .1 * (20. - final_energy)
        r.update(number_defect_H=0., energy_defect_eV_H=0., species_defect=[0., 0., 0.])
        out = recompute_balances(f, r)
        self.assertAlmostEqual(out["computed"]["number_defect_H"], 0., delta=2e-17)
        self.assertAlmostEqual(out["computed"]["energy_defect_eV_H"], 0., delta=2e-15)
        self.assertAlmostEqual(out["species_stock_defect_H"][0], 0., delta=2e-17)
        self.assertEqual(out["species_stock_defect_H"][1:], [0., 0.])
        # A signed external CMB input is subtracted exactly once.
        r["ledgers"]["cmb"] = .25
        shifted = recompute_balances(f, r)
        self.assertAlmostEqual(shifted["computed"]["energy_defect_eV_H"], -.25, delta=2e-15)
        self.assertFalse(shifted["acceptance_gate_changed"])

    def test_absent_he_and_negative_ledgers_rejected(self):
        f = fixture()
        r = endpoint(f)
        r["ledgers"] = empty_ledgers()
        for key, value in (("dr", 1e-30), ("escape", -1e-30), ("source_n", float("inf"))):
            bad = copy.deepcopy(r)
            bad["ledgers"][key] = value
            with self.subTest(key=key), self.assertRaises(DiagnosticInputError):
                recompute_balances(f, bad)


class OrderTests(unittest.TestCase):
    def test_two_scale_exact_coefficients_and_cubic_contamination(self):
        n, A, B, C = 8, -3., 5., 2.
        def d(k, cubic):
            return A / k + B / k**2 + cubic / k**3
        exact = two_scale_coefficients(n, d(n, 0.), d(2 * n, 0.))
        self.assertEqual((exact["A_hat"], exact["B_hat"]), (A, B))
        cubic = two_scale_coefficients(n, d(n, C), d(2 * n, C))
        self.assertEqual(cubic["A_hat"], A - C / (2 * n**2))
        self.assertEqual(cubic["B_hat"], B + 3 * C / (2 * n))
        self.assertIsNone(cubic["zero_crossing_forecast"])
        with self.assertRaises(DiagnosticInputError):
            two_scale_coefficients(1.5, 1., .5)

    def test_orders_crossing_and_zero(self):
        self.assertAlmostEqual(signed_order(-4., -1.)["order"], 2.)
        self.assertAlmostEqual(reference_free_order(2., 1.25, 1.0625)["order"], 2.)
        for a, b in ((0., 1.), (1., 0.), (1., -1.)):
            out = signed_order(a, b)
            self.assertEqual(out["status"], "UNRESOLVED")
            self.assertIsNone(out["order"])
        self.assertEqual(reference_free_order(1., 1., 1.)["status"], "UNRESOLVED")

    def test_conditional_triangle_interval_and_truthful_scope(self):
        out = conditional_order_interval(4., 1., .1)
        for reference_error in (-.1, -.05, 0., .05, .1):
            actual = math.log2(abs(4. + reference_error) / abs(1. + reference_error))
            self.assertLessEqual(out["lower_order"], actual)
            self.assertGreaterEqual(out["upper_order"], actual)
        self.assertIsNone(out["global_error_bound"])
        self.assertFalse(out["bound_verified_by_this_function"])
        self.assertEqual(conditional_order_interval(4., 1., 1.)["status"], "UNRESOLVED")
        crossing = conditional_order_interval(4e-300, -1e-300, 0.)
        self.assertTrue(crossing["signed_error_crossing"])
        self.assertAlmostEqual(crossing["lower_order"], 2., delta=1e-12)
        with self.assertRaises(DiagnosticInputError):
            conditional_order_interval(4., 1., -1.)


if __name__ == "__main__":
    unittest.main()
