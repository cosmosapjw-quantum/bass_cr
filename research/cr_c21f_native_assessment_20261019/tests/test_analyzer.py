"""Small adversarial checks of intake and signed-error interpretation."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze_native_evidence import (EvidenceError, EvidenceReader, hashes, fit_inverse_powers,
                                     summary_matches_result, three_level_differences, validate_fixture,
                                     write_products)


def fixture():
    return {"x0": -2.4, "dx": 0.0001, "nh0": 1e-7, "Y": 0.08,
            "gas0": [0.2, 0.15, 0.01, 1.4], "q": [1.3], "birth": [-2.4],
            "amounts": [0.01], "opacity_scale": 1.0, "source_identity": "explicit_test",
            "scope": "FLRW_EXPLICIT_TEST_IC_NOT_CHECKPOINT"}


class IntakeContractTests(unittest.TestCase):
    def test_fixture_shape_and_digest_are_separate_from_file_serialization(self):
        f = fixture()
        semantic = validate_fixture(f)
        raw_hash = hashlib.sha256(json.dumps(f, indent=2).encode()).hexdigest()
        self.assertNotEqual(semantic, raw_hash)
        with self.assertRaisesRegex(EvidenceError, "CANONICAL_DIGEST"):
            validate_fixture(f, raw_hash)
        changed = copy.deepcopy(f)
        changed["amounts"] = []
        with self.assertRaisesRegex(EvidenceError, "SHAPE"):
            validate_fixture(changed)
        changed = copy.deepcopy(f)
        changed["gas0"][2] = float("nan")
        with self.assertRaisesRegex(EvidenceError, "NONFINITE"):
            validate_fixture(changed)

    def test_missing_and_corrupted_raw_evidence_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            e = root / "evidence"
            e.mkdir()
            manifest = e / "MANIFEST.sha256"
            manifest.write_text(hashlib.sha256(b"valid").hexdigest() + "  ./result.json\n")
            receipts = {"evidence/MANIFEST.sha256": {"path": "evidence/MANIFEST.sha256", **hashes(manifest.read_bytes()), "source_ref": "test"},
                        "evidence/result.json": {"path": "evidence/result.json", **hashes(b"valid"), "source_ref": "test"}}
            reader = EvidenceReader(root, e, receipts)
            with self.assertRaisesRegex(EvidenceError, "MISSING_RAW"):
                reader.read(e / "result.json")
            (e / "result.json").write_bytes(b"other")
            with self.assertRaisesRegex(EvidenceError, "GITHUB_SHA256_MISMATCH"):
                reader.read(e / "result.json")

    def test_summary_cannot_replace_or_change_underlying_run(self):
        result = {"mode": "BE", "gas": [0.2, 0.15, 0.01, 1.4], "status": "completed"}
        summary = dict(result, fraction_max_abs_error=0.0, thermal_abs_error_eV_H=0.0,
                       normalized_state_error=0.0, photon_max_abs_error=0.0)
        summary_matches_result(summary, result)
        summary["gas"] = [0.2, 0.15, 0.01, 1.5]
        with self.assertRaisesRegex(EvidenceError, "SUMMARY_RESULT_MISMATCH"):
            summary_matches_result(summary, result)

    def test_sign_cancellation_does_not_become_an_order_certificate(self):
        ns = [8, 16, 32, 64]
        # A first-order term cancels a second-order term at n=32 exactly.
        values = [1 / n - 32 / n**2 for n in ns]
        fit = fit_inverse_powers(ns, values)
        self.assertAlmostEqual(fit["A"], 1.0, places=12)
        self.assertAlmostEqual(fit["B"], -32.0, places=10)
        self.assertAlmostEqual(fit["zero_crossing_n_positive"], 32.0, places=10)
        self.assertEqual(values[2], 0.0)
        diagnostics = three_level_differences(dict(zip(ns, values)))
        self.assertTrue(all(r["status"] == "DIAGNOSTIC_REFERENCE_FREE_NOT_ORDER_PROOF" for r in diagnostics))
        # Direct signed sequences with a refinement-difference reversal must flag it.
        reversal = three_level_differences({8: 0.0, 16: 1.0, 32: 0.0, 64: -0.5})
        self.assertFalse(reversal[0]["same_difference_sign"])
        # A fit that gets an observed endpoint sign wrong cannot locate a crossing.
        empirical = [5.361474715859238e-05, 1.21930600605058e-05,
                     1.9392700445486355e-06, -1.0751923973373323e-07]
        bad_crossing_fit = fit_inverse_powers(ns, empirical)["crossing_fit_assessment"]
        self.assertEqual(bad_crossing_fit["status"], "INADEQUATE_FOR_CROSSING_PREDICTION")
        self.assertEqual(bad_crossing_fit["fitted_sign_mismatch_levels"], [64])
        self.assertEqual(bad_crossing_fit["observed_sign_change_brackets"], [[32, 64]])
        self.assertIsNone(bad_crossing_fit["certified_crossing_prediction"])

    def test_create_only_output_preserves_existing_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "existing"
            out.mkdir()
            payload = out / "keep.txt"
            payload.write_text("immutable")
            with self.assertRaisesRegex(EvidenceError, "OUTPUT_ALREADY_EXISTS"):
                write_products(out, {}, {})
            self.assertEqual(payload.read_text(), "immutable")


if __name__ == "__main__":
    unittest.main()
