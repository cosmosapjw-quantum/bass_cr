import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import endpoint_source as es
from repair import raw_integral


class ReferenceCoordinateRegression(unittest.TestCase):
    def test_near_endpoint_raw_sdcs(self):
        source = es.EndpointSource(96)
        for target in es.TARGETS:
            energy = source.endpoint(target)*(1-1e-6)
            actual = float(source.spectrum_by_target(energy)[target])
            direct, _ = raw_integral(source, energy, target)
            self.assertGreater(direct, 0.)
            self.assertLessEqual(float(es.relative(actual, direct)), 2e-10)
            self.assertEqual(raw_integral(source, source.endpoint(target), target)[0], 0.)


if __name__ == "__main__":
    unittest.main()
