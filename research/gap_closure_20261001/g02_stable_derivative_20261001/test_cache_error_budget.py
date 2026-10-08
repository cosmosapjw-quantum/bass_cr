import unittest
import json
import numpy as np
from cache_error_budget import block_budget, block_indices, channels_from_basis, sensitivity


class CacheBudgetTests(unittest.TestCase):
    def test_basis_order_and_cross_binding(self):
        channels = channels_from_basis({'modes': [{'l': 0, 'identity': 's'}, {'l': 1, 'identity': 'p'}]})
        self.assertEqual([(c['center'], c['l'], c['m']) for c in channels],
                         [(c, l, m) for c in (0, 1) for l in (0, 1) for m in range(-l, l+1)])
        blocks = block_indices(channels)
        self.assertEqual(blocks['TP'], ([0, 1, 2, 3], [4, 5, 6, 7]))
        self.assertEqual(blocks['PT'], ([4, 5, 6, 7], [0, 1, 2, 3]))
        channels[0]['index'] = 7
        with self.assertRaises(ValueError):
            block_indices(channels)

    def test_exact_affine_derivative_and_global_indices(self):
        slope = np.array([[1+2j, 3], [4, 5-1j]])
        minus, plus = 2-.25*slope, 2+.25*slope
        target = 2*slope
        result = block_budget(target/2, target/2, minus, plus, .25, 2, [8, 10], [2, 4])
        self.assertEqual(result['residual']['max_absolute'], 0)
        self.assertEqual(result['dominating_absolute_element']['global_index'], [8, 2])
        self.assertEqual(result['absolute_sample_error_gain_sum'], 8)

    def test_near_cancelled_D_and_floor_preserved(self):
        d = np.array([[-.5]])
        dd = np.array([[.5-2**-46]])
        result = block_budget(d, dd, np.ones((1, 1)), np.ones((1, 1)), .05, 2, [9], [13])
        elem = result['dominating_normalized_element']
        self.assertEqual(elem['global_index'], [9, 13])
        self.assertEqual(elem['D_plus_Ddagger'], [-2**-46, 0.])
        self.assertAlmostEqual(elem['residual_normalized'], 2**-46/1e-12)
        self.assertTrue(elem['denominator_is_floor'])
        self.assertEqual(elem['D_cancellation_ratio'], (1-2**-46)/2**-46)
        self.assertTrue(result['S_plus_minus_bitwise_equal'])
        self.assertEqual(json.loads(json.dumps(result, allow_nan=False)), result)

    def test_perturbation_amplification_is_algebraic(self):
        shape = (1, 1)
        minus, plus = np.array([[3.]]), np.array([[3.]])
        d = np.zeros(shape)
        h, velocity, delta = .125, 2., 2**-30
        base = block_budget(d, d, minus, plus, h, velocity, [0], [1])
        changed = block_budget(d, d, minus-delta, plus+delta, h, velocity, [0], [1])
        self.assertEqual(changed['finite_difference']['max_absolute'], velocity/h*delta)
        self.assertEqual(base['absolute_sample_error_gain_sum'], velocity/h)
        gains = sensitivity(minus, plus, d, d, h, velocity)
        self.assertEqual(gains['fd_epsilon_relative_sample_surrogate'][0, 0], np.finfo(float).eps*velocity/(2*h)*6)

    def test_exact_cancellation_is_explicit_not_infinity(self):
        d = np.array([[1j]])
        result = block_budget(d, -d, d, d, .2, 2, [0], [0])
        elem = result['dominating_normalized_element']
        self.assertTrue(elem['D_cancellation_exact_zero'])
        self.assertIsNone(elem['D_cancellation_ratio'])
        self.assertEqual(result['D_exact_cancellation_count'], 1)

    def test_shape_finiteness_and_h_rejected(self):
        z = np.zeros((1, 1))
        for invalid in (np.ones((2, 1)), np.array([[np.nan]])):
            with self.assertRaises(ValueError):
                block_budget(z, z, z, invalid, .1, 2, [0], [1])
        for h in (0, -.1, np.inf):
            with self.assertRaises(ValueError):
                block_budget(z, z, z, z, h, 2, [0], [1])


if __name__ == '__main__':
    unittest.main()
