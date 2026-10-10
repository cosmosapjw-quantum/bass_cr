import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from excitation_kernel import DELTAS_MEV, TARGET_CM3, make_graph, rates, sparse_evolve, uniformize


class KernelTests(unittest.TestCase):
    def test_integer_event_graph_and_absorption(self):
        graph = make_graph(1015)
        self.assertTrue(np.array_equal(graph.energies_meV,
                                      1015000 - graph.states @ np.array(DELTAS_MEV)))
        self.assertTrue(np.all(graph.generator[:, ~graph.active].toarray() == 0))
        self.assertLess(np.max(np.abs(np.asarray(graph.generator.sum(axis=0)))), 1e-25)

    def test_domain(self):
        for energy in [1000, 3000.001, float("nan"), 1000.0001]:
            with self.assertRaises(ValueError):
                make_graph(energy)
        for time in [-1, float("nan")]:
            with self.assertRaises(ValueError):
                sparse_evolve(make_graph(1015), time)

    def test_rate_units_and_density(self):
        self.assertAlmostEqual(TARGET_CM3[0], .0001386)
        self.assertAlmostEqual(TARGET_CM3[1], 1e-6 * 140 * .248 / (4 * .752) * .99)
        self.assertTrue(np.all(rates(1000) > 0))

    def test_t0_and_OFF(self):
        graph = make_graph(1500)
        state = sparse_evolve(graph, 0)
        self.assertEqual(state[0], 1)
        self.assertEqual(np.count_nonzero(state), 1)
        off = make_graph(1500, enabled=False)
        self.assertTrue(np.array_equal(sparse_evolve(off, 1e13), [1]))
        self.assertTrue(np.array_equal(uniformize(off, 1e13)[0], [1]))

    def test_one_event_oracle(self):
        graph = make_graph(1000.001)
        self.assertEqual(len(graph.states), 3)
        epoch = 1e12
        r = rates(1000.001)
        expected = np.r_[np.exp(-r.sum() * epoch), -np.expm1(-r.sum() * epoch) * r / r.sum()]
        np.testing.assert_allclose(sparse_evolve(graph, epoch), expected, atol=1e-14, rtol=1e-13)


if __name__ == "__main__":
    unittest.main()
