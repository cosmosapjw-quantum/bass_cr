"""Focused evidence-gate checks; no callbacks, native process, or IVP solve.

The saved segment is read from C21J_NATIVE_RETURN, defaulting to the matching
research/ return directory. No captured archive or native binary is embedded.
Run with unittest discover; see the accompanying independent-review command.
"""
from __future__ import annotations

from collections import Counter
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


UNIT = Path(__file__).resolve().parents[1]
REPO = Path(os.environ.get("C21J_REPO", str(UNIT.parents[1]))).resolve()
RETURN = Path(os.environ.get(
    "C21J_NATIVE_RETURN", str(REPO / "research/cr_c21ghi_native_execution_20261020")
)).resolve()
PINS_RAW_SHA256 = "ac339fc832ccc2e4b177034151a6adcf1510d82646b0c7e04d68bfc2be7aea90"
PINS_CANONICAL_SHA256 = "5c741dcaf415961d09bb4f1bf10c9dad600c0af3d0791e18750655b006957fea"
SEGMENT = Path("evidence/I_common_ic_vigilode_vectorized_base/segments/segment_000")

spec = importlib.util.spec_from_file_location("c21j_replay_contract_subject", UNIT / "replay_callbacks.py")
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class ReplayContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pins_raw = (UNIT / "INPUT_PINS.json").read_bytes()
        if hashlib.sha256(pins_raw).hexdigest() != PINS_RAW_SHA256:
            raise AssertionError("Test requires the reviewed fixed INPUT_PINS.json bytes")
        cls.pins = json.loads(pins_raw)
        canonical = json.dumps(cls.pins, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True, allow_nan=False).encode()
        if hashlib.sha256(canonical).hexdigest() != PINS_CANONICAL_SHA256:
            raise AssertionError("Test requires the reviewed canonical input-pin authority")
        cls.segment = RETURN / SEGMENT
        for name in ("config.json", "result.json", "rpc.jsonl"):
            path = cls.segment / name
            if not path.is_file():
                raise FileNotFoundError(
                    "Set C21J_NATIVE_RETURN to the extracted, verified PR87 return; missing " + str(path)
                )
            raw = path.read_bytes()
            expected = cls.pins["return_files"][str(SEGMENT / name)]
            if {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()} != expected:
                raise AssertionError("Frozen contract-test fixture identity differs: " + str(path))
        cls.config = json.loads((cls.segment / "config.json").read_text())
        cls.result = json.loads((cls.segment / "result.json").read_text())
        cls.rows = [json.loads(line) for line in (cls.segment / "rpc.jsonl").read_text().splitlines()]

    def setUp(self):
        # A regression must not turn a gate test into an execution test.
        self.process_guard = mock.patch.object(
            replay.subprocess, "Popen", side_effect=AssertionError("Native/process execution is outside test scope")
        )
        self.solve_guard = mock.patch.object(
            replay.scipy.integrate, "solve_ivp", side_effect=AssertionError("IVP integration is outside test scope")
        )
        self.process_guard.start()
        self.solve_guard.start()
        self.addCleanup(self.process_guard.stop)
        self.addCleanup(self.solve_guard.stop)

    def rpc_file(self, rows=None, *, text=None):
        temporary = tempfile.TemporaryDirectory(prefix="c21j_rpc_contract_")
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "rpc.jsonl"
        if text is None:
            text = "".join(json.dumps(row, allow_nan=True) + "\n" for row in rows)
        path.write_text(text)
        return path

    def reject_rows(self, rows, *, expected_result=None):
        with self.assertRaises(replay.ReplayError):
            replay.rpc_pairs(self.rpc_file(rows), self.config,
                             self.result if expected_result is None else expected_result)

    def test_authentic_pin_authority_verifies_the_complete_required_input_set(self):
        verified = replay.verify_inputs(REPO, RETURN, self.pins)
        expected = {"source:" + p for p in self.pins["source_files"]}
        expected.update("return:" + p for p in self.pins["return_files"])
        self.assertEqual(len(verified), 84)
        self.assertEqual(set(verified), expected)

    def test_missing_and_empty_required_maps_are_rejected(self):
        for which in ("source_files", "return_files"):
            for variant in ("empty", "one_missing"):
                with self.subTest(which=which, variant=variant):
                    pins = copy.deepcopy(self.pins)
                    if variant == "empty":
                        pins[which] = {}
                    else:
                        del pins[which][next(iter(pins[which]))]
                    with self.assertRaises(replay.ReplayError):
                        replay.verify_inputs(REPO, RETURN, pins)
        pins = copy.deepcopy(self.pins)
        pins["source_files"], pins["return_files"] = {}, {}
        with self.assertRaises(replay.ReplayError):
            replay.verify_inputs(REPO, RETURN, pins)

    def test_conflicting_provenance_metadata_is_rejected(self):
        replacements = {"schema": "UNPINNED", "source_content": "0" * 40,
                        "native_return_head": "1" * 40, "native_archive_sha256": "2" * 64,
                        "private_inventory_included": 0}
        for field, value in replacements.items():
            with self.subTest(field=field):
                pins = copy.deepcopy(self.pins)
                pins[field] = value
                with self.assertRaises(replay.ReplayError):
                    replay.verify_inputs(REPO, RETURN, pins)

    def test_rebinding_a_hash_or_path_cannot_redefine_pin_authority(self):
        for variant in ("changed_record", "extra_path", "extra_metadata"):
            with self.subTest(variant=variant):
                pins = copy.deepcopy(self.pins)
                first = next(iter(pins["source_files"]))
                if variant == "changed_record":
                    pins["source_files"][first] = {"bytes": 0, "sha256": hashlib.sha256(b"").hexdigest()}
                elif variant == "extra_path":
                    pins["source_files"]["unreviewed.py"] = pins["source_files"][first]
                else:
                    pins["unreviewed_claim"] = True
                with self.assertRaises(replay.ReplayError):
                    replay.verify_inputs(REPO, RETURN, pins)

    def test_real_same_size_source_byte_drift_is_rejected_after_authority_check(self):
        first = next(iter(self.pins["source_files"]))
        raw = bytearray((REPO / first).read_bytes())
        raw[0] ^= 1
        with tempfile.TemporaryDirectory(prefix="c21j_source_contract_") as directory:
            changed = Path(directory) / first
            changed.parent.mkdir(parents=True)
            changed.write_bytes(raw)
            with self.assertRaisesRegex(replay.ReplayError, "INPUT_IDENTITY_MISMATCH"):
                replay.verify_inputs(Path(directory), RETURN, self.pins)

    def test_run_rejects_reformatted_pin_bytes_before_any_execution(self):
        with tempfile.TemporaryDirectory(prefix="c21j_pin_contract_") as directory:
            path = Path(directory) / "INPUT_PINS.json"
            path.write_text(json.dumps(self.pins, sort_keys=True, separators=(",", ":")))
            self.assertNotEqual(hashlib.sha256(path.read_bytes()).hexdigest(), PINS_RAW_SHA256)
            args = SimpleNamespace(repo=REPO, native_return=RETURN, input_pins=path,
                                   out=Path(directory) / "must_not_be_created")
            with mock.patch.object(replay, "verify_inputs", side_effect=AssertionError("Raw pin gate must run first")):
                with self.assertRaisesRegex(replay.ReplayError, "INPUT_PIN_FILE_IDENTITY"):
                    replay.run(args)
            self.assertFalse(args.out.exists())

    def test_complete_frozen_rpc_is_accepted_with_sibling_config_and_result(self):
        pairs = replay.rpc_pairs(self.segment / "rpc.jsonl")
        self.assertEqual([request["id"] for request, _ in pairs], list(range(1, 156)))
        self.assertEqual(Counter(request["op"] for request, _ in pairs),
                         {"rhs": 131, "jacobian": 12, "partial_t": 12})
        self.assertEqual(replay.bits(pairs[0][1]), replay.bits(self.rows[3]["message"]["value"]))

    def test_complete_rpc_accepts_explicit_expected_records_without_siblings(self):
        path = self.rpc_file(self.rows)
        self.assertFalse(path.with_name("config.json").exists())
        self.assertFalse(path.with_name("result.json").exists())
        self.assertEqual(len(replay.rpc_pairs(path, self.config, self.result)), 155)

    def test_matched_prefix_and_missing_terminal_cannot_pass(self):
        for rows in (self.rows[:4], self.rows[:-1]):
            with self.subTest(rows=len(rows)):
                self.reject_rows(rows)

    def test_failed_or_incomplete_terminal_is_rejected_even_if_result_agrees(self):
        changes = (("ok", False), ("ok", 1), ("success", False),
                   ("complete_output", False), ("accepted_grid_complete", False),
                   ("callback_failure", "recorded callback failure"), ("pending_request", {"id": 156}))
        for field, value in changes:
            with self.subTest(field=field, value=value):
                rows = copy.deepcopy(self.rows)
                rows[-1]["message"][field] = value
                self.reject_rows(rows, expected_result=rows[-1]["message"])

    def test_hello_and_config_identity_and_order_are_required(self):
        for variant in ("missing_hello", "wrong_hello", "reordered_config", "config_drift", "config_signed_zero"):
            with self.subTest(variant=variant):
                rows = copy.deepcopy(self.rows)
                if variant == "missing_hello":
                    rows.pop(0)
                elif variant == "wrong_hello":
                    rows[0]["message"]["vigilode_commit"] = "0" * 40
                elif variant == "reordered_config":
                    rows[1], rows[2] = rows[2], rows[1]
                elif variant == "config_drift":
                    rows[1]["message"]["rtol"] = math.nextafter(self.config["rtol"], math.inf)
                else:
                    rows[1]["message"]["y0"][0] = -0.0
                self.reject_rows(rows)

    def test_terminal_must_match_result_including_signed_zero(self):
        rows = copy.deepcopy(self.rows)
        rows[-1]["message"]["accepted_states"][0][0] = -0.0
        self.reject_rows(rows)

    def test_duplicate_terminal_and_post_terminal_traffic_are_rejected(self):
        variants = (self.rows + [self.rows[-1]],
                    self.rows + self.rows[2:4],
                    self.rows + self.rows[2:4] + [self.rows[-1]])
        for index, rows in enumerate(variants):
            with self.subTest(variant=index):
                self.reject_rows(rows)

    def test_terminal_counters_must_account_for_every_observed_pair(self):
        for field in ("requests_attempted", "responses_validated", "rhs_requests", "jacobian_requests", "partial_t_requests"):
            with self.subTest(field=field):
                rows = copy.deepcopy(self.rows)
                rows[-1]["message"]["rpc_counters"][field] += 1
                self.reject_rows(rows, expected_result=rows[-1]["message"])

    def test_pairing_operation_id_and_dimension_failures_are_rejected(self):
        variants = ("unanswered", "response_before_request", "request_bool_id", "request_float_id",
                    "response_bool_id", "response_wrong_id", "unknown_operation", "state_shape", "time_shape", "reply_shape")
        for variant in variants:
            with self.subTest(variant=variant):
                rows = copy.deepcopy(self.rows)
                if variant == "unanswered":
                    rows.pop(3)
                elif variant == "response_before_request":
                    rows[2], rows[3] = rows[3], rows[2]
                elif variant == "request_bool_id":
                    rows[2]["message"]["id"] = True
                elif variant == "request_float_id":
                    rows[2]["message"]["id"] = 1.0
                elif variant == "response_bool_id":
                    rows[3]["message"]["id"] = True
                elif variant == "response_wrong_id":
                    rows[3]["message"]["id"] = 2
                elif variant == "unknown_operation":
                    rows[2]["message"]["op"] = "jvp"
                elif variant == "state_shape":
                    rows[2]["message"]["y"].pop()
                elif variant == "time_shape":
                    rows[2]["message"]["t"] = [rows[2]["message"]["t"]]
                else:
                    rows[3]["message"]["value"].pop()
                self.reject_rows(rows)

    def test_duplicate_json_keys_and_nonfinite_constants_are_rejected(self):
        for token in ("duplicate_key", "nan_time", "infinite_reply"):
            with self.subTest(token=token):
                rows = copy.deepcopy(self.rows)
                if token == "nan_time":
                    rows[2]["message"]["t"] = math.nan
                elif token == "infinite_reply":
                    rows[3]["message"]["value"][0][0] = math.inf
                text = "".join(json.dumps(row, allow_nan=True) + "\n" for row in rows)
                if token == "duplicate_key":
                    text = text.replace('"id": 1,', '"id": 1, "id": 1,', 1)
                with self.assertRaises(replay.ReplayError):
                    replay.rpc_pairs(self.rpc_file(text=text), self.config, self.result)


if __name__ == "__main__":
    unittest.main()
