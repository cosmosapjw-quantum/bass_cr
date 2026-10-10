import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import endpoint_source as es


class EndpointSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = es.EndpointSource(96)

    def test_species_endpoints_exact_zero(self):
        for target in es.TARGETS:
            end = self.source.endpoint(target)
            values = self.source.spectrum_by_target(np.array([end, np.nextafter(end, np.inf), 1e300]))
            np.testing.assert_array_equal(values[target], np.zeros(3))

    def test_species_endpoint_order(self):
        # Between the endpoints only H can emit an electron.
        middle = .5*(self.source.endpoint("H")+self.source.endpoint("He"))
        values = self.source.spectrum_by_target(middle)
        self.assertGreater(float(values["H"]), 0.)
        self.assertEqual(float(values["He"]), 0.)

    def test_off_and_t0(self):
        energy = np.array([0., 10., 1000., 3000., 8000., 1e4])
        np.testing.assert_array_equal(es.EndpointSource(64, False).spectrum(energy), np.zeros(6))
        np.testing.assert_array_equal(self.source.rate(energy, 0.), np.zeros(6))

    def test_local_ramp_clock(self):
        first = self.source.rate(3000., .5*es.T_END)
        second = self.source.rate(3000., es.T_END)
        self.assertGreater(float(first), 0.)
        self.assertEqual(float(second), float(2*first))
        for t in (-1., es.T_END+1, np.inf, True):
            with self.assertRaises(ValueError):
                self.source.rate(3000., t)

    def test_source_domain(self):
        for energy in (-1., np.nan, np.inf):
            with self.assertRaises(ValueError):
                self.source.spectrum(energy)
        for energy in (0., 10., 1000.):
            with self.assertRaises(ValueError):
                self.source.above_1kev(energy)
        self.assertEqual(float(self.source.above_1kev(1e4)), 0.)

    def test_both_species_panel_edges(self):
        edges = self.source.energy_panels()
        for target in es.TARGETS:
            for proton in (es.K_MIN, es.K_MAX):
                self.assertIn(self.source.endpoint(target, proton), edges)
        self.assertIn(10., edges)
        self.assertIn(1000., edges)
        self.assertEqual(edges, sorted(set(edges)))

    def test_empty_interval(self):
        for interval in ((3000., 3000.), (1e4, 2e4)):
            result = self.source.moments(*interval)
            self.assertEqual(result["total"], dict.fromkeys(es.FIELDS, 0.))
        with self.assertRaises(ValueError):
            self.source.moments(10., 1.)

    def test_source_order_and_species(self):
        with self.assertRaises(ValueError):
            es.EndpointSource(32)
        with self.assertRaises(ValueError):
            self.source.endpoint("HeII")
        with self.assertRaises(ValueError):
            es.EndpointSource(64, 1)


if __name__ == "__main__":
    unittest.main()
