"""Geometry-only checks; no physical operator or trajectory evaluations."""
from pathlib import Path
import math
import sys
import unittest
import numpy as np
from numpy.polynomial import Polynomial as P

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for path in (HERE, ROOT/'research/foundation_rebuild/src',
             ROOT/'research/foundation_rebuild/reaudit_20260925/repair'):
    sys.path.insert(0, str(path))
from phase_pairs import arc_inner_edges, phase_pairs
from aligned_cross import geometry_pairs, intersection_volume


def polynomial_moment(L, R, p, q):
    """Analytic piecewise-polynomial distance moment, without Gauss nodes."""
    cuts = sorted(set(x for x in (0., L, abs(R-L), R, R+L) if 0 <= x <= L))
    total = 0.
    for a, b in zip(cuts[:-1], cuts[1:]):
        midpoint = (a+b)/2
        if abs(R-midpoint) >= min(R+midpoint, L):
            continue
        lower = P([R, -1]) if midpoint < R else P([-R, 1])
        upper = P([R, 1]) if R+midpoint < L else P([L])
        integrand = P([0, 1])**(p+1)*(upper**(q+2)-lower**(q+2))/(R*(q+2))
        primitive = integrand.integ()
        total += primitive(b)-primitive(a)
    return total


class PhasePairsTests(unittest.TestCase):
    edges = np.array([0., .12, .4, 1., 2.])

    def assert_packets_equal(self, left, right):
        self.assertEqual(len(left), len(right))
        for one, two in zip(left, right):
            for a, b in zip(one, two):
                np.testing.assert_array_equal(a, b)

    def test_zero_speed_bitwise_baseline(self):
        for R in (.2, .75, 2.7):
            self.assert_packets_equal(list(geometry_pairs(self.edges, R, 6)),
                                      list(phase_pairs(self.edges, R, 6, 0.)))

    def test_large_budget_bitwise_baseline(self):
        self.assert_packets_equal(list(geometry_pairs(self.edges, .75, 6)),
                                  list(phase_pairs(self.edges, .75, 6, 2., phase_budget=1000.)))

    def test_preserved_boundaries_and_phase_bound(self):
        r0, R, speed, beta = 3., 2., 7., .7
        original = np.array([1., 1.3, 2., 3.1, 5.])
        panel = arc_inner_edges(original, r0, R, speed, beta=beta)
        self.assertTrue(np.all(np.diff(panel) > 0))
        self.assertEqual(panel[0], original[0]); self.assertEqual(panel[-1], original[-1])
        for edge in original:
            self.assertEqual(np.count_nonzero(panel == edge), 1)
        theta = np.arccos(np.clip((r0*r0+R*R-panel*panel)/(2*R*r0), -1, 1))
        self.assertLessEqual(float(max(np.diff(theta))*speed*r0), beta*(1+2e-12))
        self.assertAlmostEqual(float(np.diff(panel).sum()), original[-1]-original[0], places=14)
        # Actual-bank dry-run regression: r0/R small loses acos endpoint digits.
        tiny = 3.5245805788817336e-5
        endpoints = np.array([2.-tiny, 2.+tiny])
        np.testing.assert_array_equal(arc_inner_edges(endpoints, tiny, 2., 2.), endpoints)

    def test_volume_and_polynomial_moments(self):
        for R in (.3, .75, 2.7):
            packets = list(phase_pairs(self.edges, R, 8, 9., phase_budget=.7))
            r0, r1, w = np.concatenate(packets, axis=1)
            volume = 2*np.pi*math.fsum(w)
            self.assertAlmostEqual(volume/intersection_volume(2., R), 1., places=13)
            for p, q in ((2, 0), (0, 2), (2, 2)):
                actual = math.fsum(w*r0**p*r1**q)
                expected = polynomial_moment(2., R, p, q)
                self.assertAlmostEqual(actual/expected, 1., places=12)

    def test_outer_nodes_unchanged_positive_no_duplicates(self):
        baseline = list(geometry_pairs(self.edges, .75, 8))
        refined = list(phase_pairs(self.edges, .75, 8, 7., phase_budget=.8))
        self.assertEqual(len(baseline), len(refined))
        for old, (r0, r1, w) in zip(baseline, refined):
            self.assertEqual(old[0][0], r0[0])
            self.assertTrue(np.all(r0 == r0[0]))
            self.assertTrue(np.all(np.diff(r1) > 0)); self.assertTrue(np.all(w > 0))
            self.assertTrue(np.all(abs(r0-r1) < .75)); self.assertTrue(np.all(r0+r1 > .75))

    def test_invalid_inputs(self):
        for kwargs in ({'R': 0.}, {'R': np.nan}, {'speed': -1.}, {'speed': np.inf},
                       {'phase_budget': 0.}, {'phase_budget': np.nan},
                       {'order': True}, {'order': 65}, {'max_segments': 0},
                       {'max_segments': 65537}, {'edges': [0., 1., 1.]},
                       {'edges': [0., np.inf]}, {'edges': [.1, 1.]}):
            arguments = dict(edges=self.edges, R=.75, order=4, speed=2.)
            arguments.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                list(phase_pairs(**arguments))

    def test_arc_geometry_and_caps_rejected(self):
        for inner in ([.9, 4.], [1., 5.1], [1., 2., 2.], [1., np.nan]):
            with self.subTest(inner=inner), self.assertRaises(ValueError):
                arc_inner_edges(inner, 3., 2., 7.)
        with self.assertRaises(ValueError):
            arc_inner_edges([1., 5.], 3., 2., 7., beta=.01, max_segments=5)
        with self.assertRaises(ValueError):
            list(phase_pairs(self.edges, .75, 4, 1e308, phase_budget=1e-308))

    def test_disjoint_supports(self):
        self.assertEqual(list(phase_pairs(self.edges, 4., 6, 2.)), [])


if __name__ == '__main__':
    unittest.main()
