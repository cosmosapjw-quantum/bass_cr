"""Focused fixed-manifold FS10 composition-knot checks.

These tests deliberately do not turn the two acquired table knots into a
composition interpolation or a causal secondary-cascade solution.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fs10 import FS10Table
from provider import build_packet


class FS10CompositionTests(unittest.TestCase):
    def test_xi010_source_is_exact_pinned_knot(self):
        table = FS10Table(0.1)
        self.assertEqual(
            table.audit["source_sha256"],
            "3a83d09a3741d11f7d667156d8bd2a6d026fb7f624cbea98e58b789b0a9deea5",
        )
        self.assertEqual(table.audit["source_xHII"], 0.1)
        self.assertEqual(table.audit["source_xHeII_per_He"], 0.1)
        self.assertEqual(table.audit["source_xHeIII"], 0.0)
        self.assertLess(table.audit["max_event_relative_energy_defect"], 1.0e-4)

    def test_xi010_packet_remains_explicitly_source_bound(self):
        packet, manifest, audit = build_packet(xi=0.1)
        self.assertEqual(packet["provider_id"], "CRP_L17_MD14_RUDD_FS10_XI010_CONDITIONAL_V1")
        self.assertEqual(packet["gas"]["xi"], 0.1)
        self.assertEqual(audit["table"]["source_xHII"], 0.1)
        self.assertTrue(
            any(path.endswith("/log_xi_-1.0.dat") for path in manifest["files"])
        )
        self.assertNotEqual(packet["packet_sha256"], "")

    def test_no_unacquired_composition_is_interpolated(self):
        for xi in (0.001, 0.02, 0.05, 0.5):
            with self.assertRaisesRegex(ValueError, "OUT_OF_DOMAIN"):
                FS10Table(xi)


if __name__ == "__main__":
    unittest.main()
