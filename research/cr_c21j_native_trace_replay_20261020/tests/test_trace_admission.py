"""Small archive-admission probes; no reconstruction or native execution.

C21J_NATIVE_RETURN points to the extracted, independently verified PR87 return.
Only its payload manifest and one public job receipt are needed by these tests.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


UNIT = Path(__file__).resolve().parents[1]
REPO = Path(os.environ.get("C21J_REPO", str(UNIT.parents[1]))).resolve()
RETURN = Path(os.environ.get(
    "C21J_NATIVE_RETURN", str(REPO / "research/cr_c21ghi_native_execution_20261020")
)).resolve()
MANIFEST_SHA256 = "40d61253fb5535435373c07150ff554ff708796902076168e171fb1f9301125a"
PUBLIC_RECEIPT = Path("evidence/I_common_ic_vigilode_vectorized_base/JOB_RECEIPT.json")

spec = importlib.util.spec_from_file_location("c21j_trace_admission_subject", UNIT / "analyze_native_trace.py")
trace = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = trace
spec.loader.exec_module(trace)


class TraceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = (RETURN / trace.PACKAGE_MANIFEST).read_bytes()
        if hashlib.sha256(cls.manifest).hexdigest() != MANIFEST_SHA256:
            raise AssertionError("Set C21J_NATIVE_RETURN to the verified frozen PR87 archive root")
        cls.receipt = (RETURN / PUBLIC_RECEIPT).read_bytes()

    def test_authentic_manifest_admits_the_pinned_public_receipt(self):
        inputs = trace.Inputs(RETURN, MANIFEST_SHA256)
        self.assertEqual(len(inputs.expected), 155)
        self.assertEqual(inputs.read(PUBLIC_RECEIPT), self.receipt)
        self.assertEqual(inputs.records[str(PUBLIC_RECEIPT)]["sha256"],
                         inputs.expected[str(PUBLIC_RECEIPT)])
        self.assertTrue(inputs.unchanged())

    def test_counterfeit_self_consistent_manifest_cannot_replace_authority(self):
        with tempfile.TemporaryDirectory(prefix="c21j_manifest_contract_") as directory:
            root = Path(directory)
            # This is self-consistent for empty bytes but has no frozen authority.
            (root / trace.PACKAGE_MANIFEST).write_text(hashlib.sha256(b"").hexdigest() + "  fake.json\n")
            (root / "fake.json").write_bytes(b"")
            with self.assertRaisesRegex(trace.TraceError, "PACKAGE_MANIFEST_AUTHORITY_MISMATCH"):
                trace.Inputs(root, MANIFEST_SHA256)

    def test_same_size_changed_job_receipt_is_rejected_before_json_parsing(self):
        changed = bytearray(self.receipt)
        changed[0] ^= 1
        with tempfile.TemporaryDirectory(prefix="c21j_receipt_contract_") as directory:
            root = Path(directory)
            (root / trace.PACKAGE_MANIFEST).write_bytes(self.manifest)
            payload = root / PUBLIC_RECEIPT
            payload.parent.mkdir(parents=True)
            payload.write_bytes(changed)
            inputs = trace.Inputs(root, MANIFEST_SHA256)
            with self.assertRaisesRegex(trace.TraceError, "RETURN_PAYLOAD_IDENTITY"):
                inputs.json(PUBLIC_RECEIPT)

    def test_unlisted_file_cannot_become_an_admitted_return_input(self):
        with tempfile.TemporaryDirectory(prefix="c21j_unlisted_contract_") as directory:
            root = Path(directory)
            (root / trace.PACKAGE_MANIFEST).write_bytes(self.manifest)
            (root / "unreviewed.json").write_text("{}")
            inputs = trace.Inputs(root, MANIFEST_SHA256)
            with self.assertRaisesRegex(trace.TraceError, "UNPINNED_RETURN_FILE"):
                inputs.json("unreviewed.json")

    def test_private_inventory_payload_is_rejected_before_opening(self):
        inputs = trace.Inputs(RETURN, MANIFEST_SHA256)
        private_names = [name for name in inputs.expected if Path(name).name == "LIVE_INVENTORY.json"]
        self.assertGreater(len(private_names), 0)
        with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("Private payload must not be opened")):
            for name in private_names:
                with self.subTest(path=name):
                    with self.assertRaisesRegex(trace.TraceError, "PRIVATE_PAYLOAD_EXCLUDED"):
                        inputs.read(name)

    def test_cli_rejects_replaced_manifest_before_any_job_analysis(self):
        with tempfile.TemporaryDirectory(prefix="c21j_cli_admission_") as directory:
            root = Path(directory)
            (root / trace.PACKAGE_MANIFEST).write_bytes(b"")
            with mock.patch.object(trace, "analyze_job", side_effect=AssertionError("Admission must precede analysis")):
                with self.assertRaisesRegex(trace.TraceError, "PACKAGE_MANIFEST_AUTHORITY_MISMATCH"):
                    trace.main(["--archive", str(root), "--source-root", str(REPO / "research"),
                                "--out", str(root / "rejected_run")])


if __name__ == "__main__":
    unittest.main()
