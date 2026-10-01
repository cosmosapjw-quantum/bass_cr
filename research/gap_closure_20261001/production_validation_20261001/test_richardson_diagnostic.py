import json
import unittest
import numpy as np
import richardson_diagnostic as rd


class RichardsonTests(unittest.TestCase):
    def ladder(self, function, h=.4, z=.3):
        return [(h / 2**i, function(z-h/2**i), function(z+h/2**i)) for i in range(4)]

    def test_r8_exact_for_polynomials_through_degree_eight(self):
        A = np.array([[1+2j, -3j], [2., -1j]])
        for degree in range(9):
            with self.subTest(degree=degree):
                f = lambda z: A * z**degree
                table = rd.build_table(self.ladder(f), 1.7)
                exact = A * (1.7 * degree * .3**(degree-1) if degree else 0)
                np.testing.assert_allclose(table['arrays'][3][0], exact, rtol=2e-12, atol=2e-13)

    def test_complex_oscillatory_formal_rates(self):
        f = lambda z: np.array([[np.exp(1.3j*z)]])
        exact = 1.3j * np.exp(1.3j*.3)
        errors = []
        for h in (.8, .4):
            table = rd.build_table(self.ladder(f, h=h), 1.)
            errors.append([abs(layer[0][0, 0]-exact) for layer in table['arrays']])
        rates = np.log2(np.array(errors[0]) / errors[1])
        np.testing.assert_allclose(rates, [2, 4, 6, 8], atol=.12, rtol=0)

    def test_D_used_for_comparison_only(self):
        f = lambda z: np.array([[np.cos(z), np.exp(1j*z)], [np.exp(-1j*z), np.sin(z)]])
        ladder = self.ladder(f)
        a = rd.analyze_ladder(np.zeros((2, 2)), ladder, 1.)
        b = rd.analyze_ladder(np.eye(2)*100, ladder, 1.)
        for la, lb in zip(a['layers'], b['layers']):
            self.assertEqual(la['successive_estimate_difference_norms_independent_of_D'],
                             lb['successive_estimate_difference_norms_independent_of_D'])
            for ra, rb in zip(la['rows'], lb['rows']):
                self.assertEqual(ra['estimate_norms'], rb['estimate_norms'])
                self.assertEqual(ra['central_difference_coefficients_coarse_to_fine'],
                                 rb['central_difference_coefficients_coarse_to_fine'])
        self.assertNotEqual(a['layers'][0]['rows'][0]['disagreement_with_D_plus_Ddagger_absolute'],
                            b['layers'][0]['rows'][0]['disagreement_with_D_plus_Ddagger_absolute'])

    def test_coefficients_and_constant_perturbation_amplification(self):
        ladder = self.ladder(lambda z: np.eye(1)*np.sin(z))
        table = rd.build_table(ladder, 1.)
        expected = np.array([-1/2835, 4/135, -64/135, 4096/2835])
        np.testing.assert_allclose(table['central_weights'][3][0], expected, rtol=1e-15)
        self.assertAlmostEqual(sum(expected), 1.)
        report = rd.analyze_ladder(np.zeros((1, 1)), ladder, 1.)
        row = report['layers'][3]['rows'][0]
        self.assertAlmostEqual(row['central_difference_coefficient_l1'], np.abs(expected).sum())
        self.assertGreater(row['signed_sample_coefficient_l1_atomic_time_inverse'], 1/.05)

    def test_raw_central_ratio_and_unmodified_gate(self):
        k, h, z = 2., .4, .3
        f = lambda x: np.array([[np.exp(1j*k*x)]])
        table = rd.build_table(self.ladder(f, h=h, z=z), 1.)
        ratio = table['arrays'][0][0][0, 0] / (1j*k*np.exp(1j*k*z))
        self.assertAlmostEqual(abs(ratio-np.sin(k*h)/(k*h)), 0, places=14)
        report = rd.analyze_ladder(np.zeros((1, 1)), self.ladder(f), 1.)
        self.assertFalse(report['original_G02_acceptance_changed'])
        self.assertFalse(report['physical_G02_closed'])
        self.assertFalse(report['rigorous_operator_error_bound'])
        json.dumps(report, allow_nan=False)

    def test_zero_differences_report_null_order(self):
        report = rd.analyze_ladder(np.zeros((1, 1)), self.ladder(lambda z: np.eye(1)), 1.)
        for layer in report['layers']:
            self.assertTrue(all(v is None for v in layer['observed_orders_against_D_spectral']))
        json.dumps(report, allow_nan=False)

    def test_bad_ladders_matrices_velocity_and_arithmetic(self):
        good = self.ladder(lambda z: np.eye(1)*z)
        bads = [[], good[:3], [(h*1.01 if i == 2 else h, m, p)
                              for i, (h, m, p) in enumerate(good)],
                [(0., m, p) for h, m, p in good],
                [(h, np.full((1, 1), np.nan), p) for h, m, p in good],
                [(h, np.ones((1, 2)), p) for h, m, p in good],
                [(h, np.zeros((0, 0)), np.zeros((0, 0))) for h, m, p in good],
                [(h, np.full((1, 1), -1e308), np.full((1, 1), 1e308)) for h, m, p in good]]
        for bad in bads:
            with self.assertRaises(ValueError): rd.build_table(bad, 1.)
        for velocity in (0, -1, np.nan, np.inf, 1j):
            with self.assertRaises(ValueError): rd.build_table(good, velocity)
        with self.assertRaises(ValueError): rd.analyze_ladder(np.array([[np.inf]]), good, 1.)
        with self.assertRaises(ValueError): rd.analyze_ladder(np.eye(2), good, 1.)


if __name__ == '__main__':
    unittest.main()
