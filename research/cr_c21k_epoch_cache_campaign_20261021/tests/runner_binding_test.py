"""Focused K binding checks with explicit doubles; no native/ODE execution."""
from __future__ import annotations

import copy
from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

UNIT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("c21k_runner_binding_test_subject", UNIT / "run_epoch_pilot.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


@dataclass(frozen=True)
class FixtureDouble:
    digest: str = "test-fixture-only"


class Bindings(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="c21k-bind-gate-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.research = self.root / "research"
        self.unit = self.research / Path(R.contract.UNIT).name
        self.i_unit = self.research / R.contract.I_NAME
        self.h_identity = {"manifest": {"sha256": "h"}, "runtime_files": {"h": "unchanged"}}
        self.i_identity = {"manifest": {"sha256": "i"}, "runtime_files": {"i": "unchanged"},
                           "optimization": "vectorized_exact"}
        self.k_identity = {"manifest": {"sha256": "k"}, "runtime_files": {"k": "unchanged"},
                           "optimization": "vectorized_exact"}
        self.published = {"schema": "C21K_NATIVE_PUBLICATION_IDENTITY_V1",
                          "c21h": {"content_commit": R.contract.H_CONTENT},
                          "c21i": {"content_commit": R.contract.I_CONTENT},
                          "c21k": {"content_commit": "a" * 40}}
        self.raw_authority = SimpleNamespace(verify_native_binary=Mock(return_value={"path": "unused-native"}))
        self.args = SimpleNamespace(command="native", out=self.root / "job",
            source_dir=self.research / R.contract.F_NAME,
            c21g_unit=self.research / R.contract.G_NAME,
            native=self.root / "unused-native", build_dir=None)
        self.args.out.mkdir()
        self.h = SimpleNamespace(
            context=Mock(return_value=(self.args.source_dir, self.args.c21g_unit,
                                      self.root / "baseline", self.raw_authority, {"inputs": "pinned"})),
            verify_own_source=Mock(side_effect=lambda: copy.deepcopy(self.h_identity)),
            write_new_json=self.write,
            verified_base=Mock(return_value={"original_H_base_gate": "called"}),
            payload_inventory=self.inventory,
            BudgetedNativeMicro=object())
        self.original_base = self.h.verified_base
        self.original_provider_class = self.h.BudgetedNativeMicro
        self.inherited = SimpleNamespace(verify_i_source=Mock(
            side_effect=lambda mode, unit: (copy.deepcopy(self.i_identity), {})))
        self.optimizer = SimpleNamespace(run_optimized_reference=Mock(return_value={"rhs_evaluations": 0}))
        self.guard = Mock()
        self.admission = SimpleNamespace(admit_native_cache=Mock(return_value=({"admission": "double"}, self.guard)))
        self.patchers = [
            patch.object(R.contract, "verify_inherited_sources", side_effect=lambda unit:
                         (copy.deepcopy(self.h_identity), {}, {})),
            patch.object(R.contract, "verify_k_source", side_effect=lambda mode, unit:
                         (copy.deepcopy(self.k_identity), {})),
            patch.object(R.contract, "verify_publications", side_effect=lambda *a, **k:
                         copy.deepcopy(self.published))]
        for p in self.patchers:
            p.start()
            self.addCleanup(p.stop)
        self.state = R.bind_runner(self.h, self.inherited, self.optimizer, self.admission,
                                  "vectorized_exact", unit=self.unit, i_unit=self.i_unit,
                                  publication_receipt=self.root / "K.json",
                                  c21i_publication_receipt=self.root / "I.json",
                                  c21h_publication_receipt=self.root / "H.json")
        self.h.context(self.args)

    def write(self, path, value):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as stream:
            json.dump(value, stream)

    def inventory(self, root):
        return {p.name: R.contract.record(p.read_bytes()) for p in Path(root).iterdir()
                if p.is_file() and p.name != "JOB_RECEIPT.json"}

    def run_double(self, provider=None):
        provider = provider or SimpleNamespace(deadline=time.monotonic() + 10)
        return self.h.run_rust_reference(FixtureDouble(), provider, self.args.source_dir,
                                        self.root / "unused-bridge", self.root / "segments", {},
                                        wall_s=300.0, max_evaluations=200000)

    def parent(self):
        parent = self.root / "parent"
        parent.mkdir()
        self.write(parent / "JOB_RECEIPT.json", {"schema": "C21K_JOB_RECEIPT_V1",
                   "c21k_runner": self.state["runner_identity"]})
        self.write(parent / "C21K_SOURCE_IDENTITY.json", self.k_identity)
        return parent

    def test_native_guard_and_provider_are_forwarded_without_a_new_deadline(self):
        provider = SimpleNamespace(deadline=time.monotonic() + 10)
        self.run_double(provider)
        self.admission.admit_native_cache.assert_called_once()
        self.assertIs(self.admission.admit_native_cache.call_args.args[0], provider)
        kwargs = self.optimizer.run_optimized_reference.call_args.kwargs
        self.assertLessEqual(kwargs["wall_s"], 10)
        self.assertGreater(kwargs["wall_s"], 0)
        self.assertEqual(kwargs["max_evaluations"], 200000)
        self.assertIs(kwargs["cache_guard"], self.guard)
        self.assertEqual(kwargs["c21i_dir"], self.i_unit)
        self.assertEqual(kwargs["optimization"], "vectorized_exact")
        self.guard.assert_called_once_with(full_hash=True, current_provider=provider)
        self.assertIs(self.h.BudgetedNativeMicro, self.original_provider_class)
        self.assertTrue((self.args.out / "C21K_PUBLICATION_IDENTITY.json").is_file())
        self.assertFalse((self.args.out / "C21I_PUBLICATION_IDENTITY.json").exists())

    def test_terminal_full_hash_guard_runs_when_optimizer_raises(self):
        self.optimizer.run_optimized_reference.side_effect = ValueError("optimizer fixture failure")
        provider = SimpleNamespace(deadline=time.monotonic() + 10)
        with self.assertRaisesRegex(ValueError, "optimizer fixture failure"):
            self.run_double(provider)
        self.guard.assert_called_once_with(full_hash=True, current_provider=provider)

    def test_guard_failure_propagates_instead_of_returning_success(self):
        self.guard.side_effect = R.EpochPilotError("terminal guard fixture failure")
        with self.assertRaisesRegex(R.EpochPilotError, "terminal guard fixture failure"):
            self.run_double()

    def test_expired_original_epoch_prevents_optimizer_call(self):
        provider = SimpleNamespace(deadline=time.monotonic() - 1)
        with self.assertRaisesRegex(R.EpochPilotError, "ORIGINAL_JOB_WALL"):
            self.run_double(provider)
        self.optimizer.run_optimized_reference.assert_not_called()

    def test_old_i_and_wrong_k_mode_parents_do_not_reach_original_base_gate(self):
        parent = self.parent()
        path = parent / "JOB_RECEIPT.json"
        for value in ({"schema": "C21H_JOB_RECEIPT_V1", "c21i_runner": {"optimization": "vectorized_exact"}},
                      {"schema": "C21K_JOB_RECEIPT_V1", "c21k_runner": {
                          **self.state["runner_identity"], "optimization": "vectorized"}}):
            with self.subTest(value=value):
                path.write_text(json.dumps(value))
                with self.assertRaisesRegex(R.EpochPilotError, "MATCHING_C21K_MODE_AND_RUNTIME"):
                    self.h.verified_base(parent, "smoke", "remaining-H-identities")
                self.original_base.assert_not_called()

    def test_matching_k_parent_still_requires_original_h_validator(self):
        parent = self.parent()
        self.original_base.side_effect = ValueError("original H payload changed")
        with self.assertRaisesRegex(ValueError, "original H payload changed"):
            self.h.verified_base(parent, "smoke", "fixture", "sha", "method", {}, {}, None, {})
        self.original_base.assert_called_once_with(parent, "smoke", "fixture", "sha", "method", {}, {}, None, {})

    def test_native_fd_parent_must_match_current_k_publication(self):
        parent = self.parent()
        self.state["publication"] = self.published
        self.write(parent / "C21K_PUBLICATION_IDENTITY.json", {"c21k": {"content_commit": "b" * 40}})
        with self.assertRaisesRegex(R.EpochPilotError, "C21K_PUBLICATION_MISMATCH"):
            self.h.verified_base(parent, "native", "remaining-H-identities")
        self.original_base.assert_not_called()

    def test_postcheck_source_drift_marks_terminal_failed_and_preserves_raw(self):
        self.k_identity["manifest"]["sha256"] = "changed"
        receipt = {"schema": "C21H_JOB_RECEIPT_V1", "execution": "COMPLETE", "payload_files": {}}
        self.h.write_new_json(self.args.out / "JOB_RECEIPT.json", receipt)
        self.assertEqual(receipt["execution"], "FAILED")
        self.assertEqual(receipt["schema"], "C21K_JOB_RECEIPT_V1")
        self.assertEqual(receipt["inherited_receipt_schema"], "C21H_JOB_RECEIPT_V1")
        self.assertTrue((self.args.out / "C21K_POSTCHECK_ERROR.json").is_file())
        self.assertIn("C21K_POSTCHECK_ERROR.json", receipt["payload_files"])

    def test_context_rejects_other_checkout_before_original_context_imports(self):
        self.args.source_dir = self.root / "another_source"
        with self.assertRaisesRegex(R.EpochPilotError, "SAME_INHERITED_RESEARCH_CHECKOUT"):
            self.h.context(self.args)


class FreshImportTests(unittest.TestCase):
    def test_runner_import_is_scientific_package_free(self):
        script = ("import importlib.util,sys,json,builtins;"
                  "before=builtins.__import__;"
                  "s=importlib.util.spec_from_file_location('runner_fresh',sys.argv[1]);"
                  "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
                  "print(json.dumps({'numpy':'numpy' in sys.modules,'scipy':'scipy' in sys.modules,"
                  "'importer_unchanged':builtins.__import__ is before}))")
        p = subprocess.run([sys.executable, "-c", script, str(UNIT / "run_epoch_pilot.py")],
                           capture_output=True, text=True, timeout=10, check=True)
        self.assertEqual(json.loads(p.stdout), {"numpy": False, "scipy": False, "importer_unchanged": True})


if __name__ == "__main__":
    unittest.main()
