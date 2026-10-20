"""Focused harness failures; Python stub processes only, no Rust/ODE/native.

The synthetic COMPLETE rows test aggregation gates, not scientific acceptance.
The real timeout test owns its Python launcher, detached child and an unrelated
control process; only those test processes are started or cleaned up here.
"""
from __future__ import annotations
import copy
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("paired_pilot_failure_contracts", HERE / "benchmarks/paired_pilot.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def synthetic_rows():
    rows = []
    for round_id in range(4):
        for method in pilot.METHODS:
            for mode in pilot.MODES:
                rows.append({"round": round_id, "method": method, "mode": mode,
                    "execution": "COMPLETE", "exit_code": 0, "timed_out": False,
                    "process_started": True, "native_executed": False,
                    "native_process_started": False, "native_launch_attempted": False,
                    "complete_accepted_trace": True, "global_error_bound": None,
                    "cleanup": {"complete": True},
                    "process_exits": [{"exit_code": 0, "process_started": True}],
                    "fixture_sha256": "TEST_ONLY", "input_identity": {"test": True},
                    "bridge_identity": {"test": True}, "physical_bits": {"test": True},
                    "trace_bits": {"test": True}, "fd_nodes_bits": {"test": True},
                    "independent_balances_bits": {"test": True}, "rust_counters": [{"test": 1}],
                    "runtime": {"test": True}, "process_wall_s": .125,
                    "job_wall_s": .0625, "reference_wall_s": .03125, "rhs_evaluations": 1})
    return rows


class PairedPilotFailureTests(unittest.TestCase):
    def setUp(self):
        retained = os.environ.get("C21I_PAIRED_FAILURE_ARTIFACTS")
        if retained:
            self.root = Path(retained) / self._testMethodName
            self.root.mkdir(parents=True, exist_ok=False)
        else:
            self.temp = tempfile.TemporaryDirectory(prefix="c21i-paired-failure-")
            self.addCleanup(self.temp.cleanup)
            self.root = Path(self.temp.name)
        self.cpu = next(cpu for cpu in sorted(os.sched_getaffinity(0)) if cpu != 55)
        self.env = os.environ.copy()
        self.env.update(pilot.THREAD_ENV)

    def test_successful_stub_process_retains_initial_and_terminal_identity(self):
        prefix = self.root / "success"
        result = pilot.run_attempt([sys.executable, "-c", "print('PYTHON_STUB_ONLY')"],
                                   self.env, self.cpu, prefix, timeout=3.)
        self.assertTrue(result["process_started"])
        self.assertEqual(result["exit_code"], 0)
        self.assertFalse(result["timed_out"])
        self.assertTrue(result["cleanup"]["complete"])
        self.assertEqual(result["cleanup"]["signals"], [])
        self.assertGreater(result["process_wall_s"], 0.)
        self.assertTrue(Path(str(prefix)+".ATTEMPT.json").is_file())
        self.assertTrue(Path(str(prefix)+".PROCESS_RECEIPT.json").is_file())
        self.assertEqual(Path(str(prefix)+".stdout").read_text().strip(), "PYTHON_STUB_ONLY")

    def test_launch_failure_is_an_attempt_with_nonzero_cost(self):
        prefix = self.root / "launch_failure"
        result = pilot.run_attempt([str(self.root / "nonexistent_executable")],
                                   self.env, self.cpu, prefix, timeout=3.)
        self.assertFalse(result["process_started"])
        self.assertEqual(result["error_class"], "FileNotFoundError")
        self.assertGreater(result["process_wall_s"], 0.)
        self.assertTrue(result["cleanup"]["complete"])
        self.assertTrue(Path(str(prefix)+".ATTEMPT.json").is_file())
        self.assertTrue(Path(str(prefix)+".PROCESS_FAILURE.log").is_file())

    def test_timeout_cleans_detached_owned_child_and_spares_control(self):
        marker = self.root / "stub_child.json"
        script = self.root / "launcher.py"
        script.write_text("import json,os,signal,subprocess,sys,time\n"
            "signal.signal(signal.SIGTERM,signal.SIG_IGN)\n"
            "child=subprocess.Popen([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)'],start_new_session=True)\n"
            f"open({str(marker)!r},'w').write(json.dumps({{'pid':child.pid,'parent':os.getpid()}}))\n"
            "time.sleep(30)\n")
        control = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(30)"], start_new_session=True)
        try:
            result = pilot.run_attempt([sys.executable, str(script)], self.env, self.cpu,
                                       self.root / "timeout", timeout=.25)
            self.assertTrue(result["timed_out"])
            self.assertTrue(result["cleanup"]["complete"])
            self.assertGreaterEqual(result["process_wall_s"], .25)
            child = json.loads(marker.read_text())["pid"]
            owned = {row["pid"]: row for row in result["cleanup"]["observed_owned"]}
            self.assertIn(child, owned)
            self.assertNotEqual(owned[child]["session"], owned[result["pid"]]["session"])
            self.assertNotIn(control.pid, owned)
            self.assertIsNone(control.poll())
            self.assertEqual(pilot.owned_running(owned), [])
            signaled = {row["pid"] for row in result["cleanup"]["signals"] if row["outcome"] == "SIGNALED_OWNED_PIDFD"}
            self.assertIn(child, signaled)
            self.assertIn(result["pid"], signaled)
            self.assertNotIn(control.pid, signaled)
        finally:
            control.terminate()
            control.wait(timeout=3.)

    def test_recycled_identity_is_not_signaled(self):
        current = pilot.proc_identity(os.getpid())
        changed = {**current, "start_ticks": current["start_ticks"]+1}
        with mock.patch.object(pilot.signal, "pidfd_send_signal") as send:
            result = pilot.signal_owned(changed, signal.SIGTERM)
        send.assert_not_called()
        self.assertEqual(result["outcome"], "GONE_OR_IDENTITY_CHANGED_NOT_SIGNALED")

    def test_complete_receipt_cannot_override_operational_failure(self):
        rows = synthetic_rows()
        control = pilot.summary(rows)
        self.assertTrue(control["all_jobs_complete"])
        self.assertTrue(control["all_comparisons_pass"])
        changes = ({"exit_code": 7}, {"native_executed": True},
                   {"native_process_started": True}, {"complete_accepted_trace": False},
                   {"cleanup": {"complete": False}},
                   {"process_exits": [{"process_started": True, "exit_code": 2}]})
        for change in changes:
            candidate = copy.deepcopy(rows)
            candidate[-1].update(change)
            with self.subTest(change=change):
                result = pilot.summary(candidate)
                self.assertFalse(result["all_jobs_complete"])
                self.assertFalse(result["all_comparisons_pass"])
                self.assertEqual(result["total_process_wall_s_including_failures"], 4.)

    def test_cardinality_duplicate_and_empty_results_fail(self):
        rows = synthetic_rows()
        expected = {(row["round"], row["method"], row["mode"]) for row in rows}
        for candidate in ([], rows[:-1], rows[:-1]+[rows[0]]):
            with self.subTest(size=len(candidate)):
                result = pilot.summary(candidate, expected)
                self.assertFalse(result["planned_attempt_cardinality_and_uniqueness"])
                self.assertFalse(result["all_jobs_complete"])
                self.assertFalse(result["all_comparisons_pass"])

    def test_post_identity_failure_retains_summary_receipt_and_cost(self):
        rows = synthetic_rows()
        expected = {(row["round"], row["method"], row["mode"]) for row in rows}
        output = self.root / "terminal_failure"
        output.mkdir()
        with mock.patch.object(pilot, "identity", side_effect=ValueError("TEST_POST_SOURCE_DRIFT")):
            result = pilot.finish_run(output, {"test": True}, rows, Path("stub"), Path("stub"), expected, time.monotonic())
        self.assertFalse(result["accepted"])
        self.assertFalse(result["sources_unchanged"])
        self.assertEqual(result["total_process_wall_s_including_failures"], 4.)
        for name in ("SOURCE_AFTER_FAILURE.json", "SUMMARY.json", "HARNESS_RECEIPT.json", "PAYLOAD_MANIFEST.json"):
            self.assertTrue((output / name).is_file())

    def test_main_retains_collection_and_timeout_failure_attempts(self):
        for failure in ("collection", "timeout"):
            output = self.root / failure

            def fake_attempt(cmd, env, cpu, prefix):
                # Stub fixture for outer accounting; no command executes.
                if failure == "collection":
                    prefix.mkdir()
                    pilot.new(prefix / "JOB_RECEIPT.json", {"execution": "COMPLETE", "test_only": True})
                result = {"process_started": False, "exit_code": -9 if failure == "timeout" else 0,
                          "timed_out": failure == "timeout", "interrupted": False,
                          "cleanup": {"complete": True}, "process_wall_s": .125}
                pilot.new(Path(str(prefix)+".ATTEMPT.json"), {"test_only": True, "command": cmd})
                pilot.new(Path(str(prefix)+".PROCESS_RECEIPT.json"), result)
                return result

            with self.subTest(failure=failure), \
                 mock.patch.object(pilot, "identity", return_value={"test_source": True}), \
                 mock.patch.object(pilot, "METHODS", ("vigilode-rodas5p",)), \
                 mock.patch.object(pilot, "MODES", ("c21h_original",)), \
                 mock.patch.object(pilot, "run_attempt", side_effect=fake_attempt), \
                 mock.patch.object(pilot, "collect", side_effect=ValueError("TEST_BAD_RESULT_JSON")):
                code = pilot.main(["--bridge", "stub", "--build-receipt", "stub", "--out", str(output),
                                   "--cpu", str(self.cpu), "--later-repeats", "1"])
            self.assertEqual(code, 1)
            result = json.loads((output / "SUMMARY.json").read_text())
            receipt = json.loads((output / "HARNESS_RECEIPT.json").read_text())
            self.assertEqual(receipt["attempted_rows"], 1)
            self.assertEqual(receipt["total_process_wall_s_including_failures"], .125)
            self.assertEqual(len(list(output.glob("*.OBSERVATION.json"))), 1)
            self.assertFalse(result["accepted"])
            self.assertEqual(len(result["not_attempted_keys"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
