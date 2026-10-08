from fractions import Fraction as F
import math
import unittest
from etf_metric import etf_metric_bound


class ETFMetricTests(unittest.TestCase):
    def test_directional_block_bound_and_strict_admission(self):
        result = etf_metric_bound(F(4, 3), F(4, 9), 2)
        self.assertEqual(result['directional_squared_upper'], F(4, 9))
        self.assertEqual(result['cross_overlap_norm_upper'], F(67, 100))
        self.assertEqual(result['full_center_normalized_gram_lower'], F(33, 100))
        with self.assertRaises(ValueError):
            etf_metric_bound(2, 1, 2)
        with self.assertRaises(ValueError):
            etf_metric_bound(1, F(1, 3), 0)
        with self.assertRaises(ValueError):
            etf_metric_bound(1, F(1, 3), 1)

    def test_gaussian_oscillatory_gram_and_zero_phase_counterexample(self):
        # Unit L2 Gaussian phi~exp(-alpha*r^2/2), alpha=1/2:
        # ||partial_z phi||=1/2, cross ETF overlap at v=2 is exp(-2).
        # Analytic integration supplies the independent Gram eigenvalue.
        result = etf_metric_bound(F(3, 4), F(1, 4), 2, F(1, 2))
        true_minimum = 1-math.exp(-2)
        self.assertGreater(true_minimum, float(result['full_center_normalized_gram_lower']))
        # At v=0, coincident translated spans give C=1 and singular Gram;
        # there can be no unconditional displacement-only lower bound.
        self.assertEqual(1-math.exp(0), 0)
        with self.assertRaises(ValueError):
            etf_metric_bound(F(3, 4), F(1, 4), 0, F(1, 2))


if __name__ == '__main__':
    unittest.main()
