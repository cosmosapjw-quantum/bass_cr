"""Focused C21I runner contracts; no Rust, ODE or native process executes.

Git histories, published receipts, bridges and native identities in temporary
directories are explicitly synthetic. The pinned inherited source/fixtures are
read for routing checks; their historical scientific suites are not rerun.
"""
from __future__ import annotations

import contextlib
import copy
from dataclasses import asdict
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.dont_write_bytecode = True
UNIT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("c21i_runner_under_test", UNIT / "run_optimized_pilot.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
H = runner.C21H
SOURCE = UNIT.parent / "cr_c21e_event_native_20261018"
G = UNIT.parent / "cr_c21g_reference_refinement_20261019"
BASELINE = SOURCE / "evidence/C21F_NATIVE_NCP_20261018T1358Z"


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def copy_i(root):
    root = Path(root)
    root.mkdir()
    for name in (*runner.RUNTIME_FILES, "EXECUTION_MANIFEST.json"):
        shutil.copyfile(UNIT / name, root / name)
    return root


def git(root, *args):
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    result = subprocess.run(["git", "-C", str(root), *args], env=env,
                            capture_output=True, check=True, timeout=15)
    return result.stdout.decode().strip()


def publication_fixture(root):
    """Two tiny committed source units and external document receipts."""
    root = Path(root)
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.name", "C21I synthetic contract fixture")
    git(root, "config", "user.email", "synthetic@example.invalid")
    units, own, commits, receipts = [], [], [], []
    for label in ("h", "i"):
        unit = root / "research" / label
        unit.mkdir(parents=True)
        (unit / "code.py").write_text("# synthetic " + label + "\n")
        runtime = {"code.py": runner._record_bytes((unit / "code.py").read_bytes())}
        save(unit / "EXECUTION_MANIFEST.json", {"runtime_files": runtime})
        save(unit / "PUBLICATION_RECEIPT.json", {"status": "HISTORICAL_PENDING"})
        identity = {"runtime_files": runtime,
                    "manifest": runner._record_bytes((unit / "EXECUTION_MANIFEST.json").read_bytes())}
        git(root, "add", "research/" + label)
        git(root, "commit", "-q", "-m", "Synthetic " + label + " content")
        commit = git(root, "rev-parse", "HEAD")
        receipt = root.parent / (label + "_external_receipt.json")
        save(receipt, {"status": "PUBLISHED", "repository": runner.REPOSITORY,
            "unit": "research/" + label, "branch": "research/synthetic-" + label,
            "content_commit": commit, "execution_manifest_sha256": identity["manifest"]["sha256"]})
        units.append(unit); own.append(identity); commits.append(commit); receipts.append(receipt)
    git(root, "checkout", "--detach", "-q", commits[-1])
    return units, own, commits, receipts


def bind(mode="vectorized", *, unit=UNIT, optimizer=None, admission=None, context=None):
    h = runner.load_private_h()
    if context is not None:
        h.context = context
    optimizer = optimizer or SimpleNamespace(run_optimized_reference=mock.Mock())
    admission = admission or SimpleNamespace(admit_native_cache=mock.Mock())
    state = runner.bind_runner(h, optimizer, admission, mode, unit=unit)
    return h, state


class OptimizedPilotTests(unittest.TestCase):
    def test_private_h_import_precedes_numpy_and_preserves_public_module(self):
        script = """
import importlib.util,json,os,sys,types
path=sys.argv[1]
if sys.argv[2]=='preloaded': import numpy
spec=importlib.util.spec_from_file_location('runner',path)
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
before='numpy' in sys.modules
sentinel=types.ModuleType('optical_adapter');sys.modules['optical_adapter']=sentinel
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','RAYON_NUM_THREADS'):os.environ[name]='7'
h=runner.load_private_h()
print(json.dumps({'before':before,'flag':h.NUMPY_ALREADY_IMPORTED,'workers':h.THREAD_ENV,'actual':[os.environ[k] for k in h.THREAD_ENV],'public_preserved':sys.modules['optical_adapter'] is sentinel,'private_file':h.__file__}))
"""
        for preloaded in (False, True):
            with self.subTest(preloaded=preloaded):
                done = subprocess.run([sys.executable, "-B", "-c", script,
                    str(UNIT / "run_optimized_pilot.py"), "preloaded" if preloaded else "fresh"],
                    capture_output=True, text=True, timeout=30, check=True)
                value = json.loads(done.stdout)
                self.assertEqual(value["before"], preloaded)
                self.assertEqual(value["flag"], preloaded)
                self.assertTrue(value["public_preserved"])
                self.assertEqual(value["actual"], ["1"] * 5)
                self.assertEqual(value["private_file"], str(H / "run_pilot.py"))

    def test_mode_identity_preserves_all_eight_h_build_records(self):
        original = runner.load_private_h().verify_own_source()
        identities = []
        for mode in runner.OPTIMIZATIONS:
            h, _ = bind(mode)
            own = h.verify_own_source()
            self.assertEqual(own["runtime_files"], original["runtime_files"])
            self.assertEqual(own["manifest"], original["manifest"])
            self.assertEqual(len(own["runtime_files"]), 8)
            self.assertEqual(own["C21I_SOURCE_IDENTITY"]["optimization"], mode)
            identities.append(own)
        self.assertEqual(len({json.dumps(x, sort_keys=True) for x in identities}), 3)

    def test_i_runtime_and_manifest_drift_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            unit = copy_i(Path(temp) / "unit")
            h, _ = bind(unit=unit)
            path = unit / "native_cache_contract.py"
            path.write_bytes(path.read_bytes() + b"\n# synthetic drift\n")
            with self.assertRaisesRegex(runner.OptimizedPilotError, "RUNTIME_SOURCE_MISMATCH"):
                h.verify_own_source()
            manifest = json.loads((unit / "EXECUTION_MANIFEST.json").read_text())
            manifest["runtime_files"][path.name] = runner._record_bytes(path.read_bytes())
            save(unit / "EXECUTION_MANIFEST.json", manifest)
            with self.assertRaisesRegex(runner.OptimizedPilotError, "C21I_SOURCE_CHANGED_DURING_JOB"):
                h.verify_own_source()

    def test_h_source_drift_is_rejected_before_private_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            unit = Path(temp)
            manifest = json.loads((H / "EXECUTION_MANIFEST.json").read_text())
            for name in (*manifest["runtime_files"], "EXECUTION_MANIFEST.json"):
                (unit / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(H / name, unit / name)
            (unit / "run_pilot.py").write_text("raise AssertionError('must not execute')\n")
            with self.assertRaisesRegex(runner.OptimizedPilotError, "RUNTIME_SOURCE_MISMATCH"):
                runner.load_private_h(unit)

    def test_external_published_receipts_bind_real_commits_and_detached_head(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            units, own, commits, receipts = publication_fixture(root)
            value = runner.verify_publications(*receipts, *own, *units)
            self.assertEqual(value["c21i"]["content_commit"], commits[1])
            with self.assertRaisesRegex(runner.OptimizedPilotError, "PUBLISHED_RECEIPT"):
                runner.verify_publications(units[0] / "PUBLICATION_RECEIPT.json", receipts[1], *own, *units)
            git(root, "switch", "-c", "synthetic-attached")
            with self.assertRaisesRegex(runner.OptimizedPilotError, "DETACHED_PUBLISHED"):
                runner.verify_publications(*receipts, *own, *units)

    def test_publication_rejects_status_manifest_and_committed_source_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            units, own, commits, receipts = publication_fixture(Path(temp) / "repo")
            original = json.loads(receipts[1].read_text())
            for key, value in (("status", "PENDING"), ("content_commit", None),
                               ("execution_manifest_sha256", "0" * 64)):
                with self.subTest(field=key):
                    changed = dict(original); changed[key] = value; save(receipts[1], changed)
                    with self.assertRaisesRegex(runner.OptimizedPilotError, "PUBLISHED_RECEIPT"):
                        runner.verify_publications(*receipts, *own, *units)
            save(receipts[1], original)
            changed_own = copy.deepcopy(own)
            changed_own[1]["runtime_files"]["code.py"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(runner.OptimizedPilotError, "PUBLISHED_RUNTIME_CONTENT_MISMATCH"):
                runner.verify_publications(*receipts, *changed_own, *units)

    def test_original_fd_parent_guard_rejects_other_mode_or_i_source(self):
        h, _ = bind("vectorized")
        own = h.verify_own_source()
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp) / "base"; base.mkdir()
            save(base / "result.json", {"synthetic": True})
            expected = dict(command="smoke", fixture_name="synthetic", fixture_sha256="f" * 64,
                method=h.METHODS[0], input_identity={"synthetic": 1},
                binary_identity={"synthetic": 2}, native_identity=None, own=own)
            receipt = {"execution": "COMPLETE", "variant": "base",
                **{key: expected[key] for key in ("command", "fixture_name", "fixture_sha256", "method", "input_identity", "native_identity")},
                "bridge_identity": expected["binary_identity"], "source_identity": own,
                "payload_files": h.payload_inventory(base)}
            save(base / "JOB_RECEIPT.json", receipt)
            h.verified_base(base, **expected)
            for change in ("mode", "source"):
                revised = copy.deepcopy(expected)
                if change == "mode":
                    revised["own"]["C21I_SOURCE_IDENTITY"]["optimization"] = "vectorized_exact"
                else:
                    revised["own"]["C21I_SOURCE_IDENTITY"]["manifest"]["sha256"] = "a" * 64
                with self.assertRaisesRegex(h.AdapterError, "FD_FOLLOWUP_CONTEXT_MISMATCH"):
                    h.verified_base(base, **revised)

    def test_plan_allows_unpublished_and_is_create_only_with_mode_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "plan"
            args = ["plan", "--optimization", "vectorized_exact", "--out", str(out)]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main(args), 0)
            receipt = json.loads((out / "PLAN_RECEIPT.json").read_text())
            self.assertFalse(receipt["native_executed"])
            self.assertEqual(receipt["c21i_runner"]["optimization"], "vectorized_exact")
            before = {p.name: p.read_bytes() for p in out.iterdir()}
            with self.assertRaises(FileExistsError):
                runner.main(args)
            self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})

    def test_setup_consumes_original_deadline_and_nonexact_needs_no_admission(self):
        clock = [100.]
        observed = {}
        def original_context(args):
            return SOURCE, G, BASELINE, SimpleNamespace(), {"synthetic": True}
        def optimize(*args, **kwargs):
            observed.update(kwargs)
            return {"synthetic": True}
        optimizer = SimpleNamespace(run_optimized_reference=optimize)
        admission = SimpleNamespace(admit_native_cache=mock.Mock(side_effect=AssertionError("must not admit")))
        h, state = bind(optimizer=optimizer, admission=admission, context=original_context)
        args = SimpleNamespace(command="smoke")
        h.context(args)
        original_verify = h.verify_own_source
        def delayed_verify():
            clock[0] += 2.
            return original_verify()
        # The wrapper closes over its source verifier; inject delay in the
        # verified file read that it actually performs, not a mirror function.
        verified = runner._verified_h
        def delayed_h(*args, **kwargs):
            clock[0] += 2.
            return verified(*args, **kwargs)
        with mock.patch.object(runner.time, "monotonic", side_effect=lambda: clock[0]), \
             mock.patch.object(runner, "_verified_h", side_effect=delayed_h):
            h.run_rust_reference(None, SimpleNamespace(deadline=108.), SOURCE, "unused", "unused", {}, wall_s=10.)
        self.assertEqual(observed["wall_s"], 6.)
        self.assertEqual(observed["optimization"], "vectorized")
        admission.admit_native_cache.assert_not_called()

    def _native_stub(self, temp, *, reject_publication=False, terminal_error=False):
        """Run the actual H control flow with no process or numerical call."""
        events = []
        root = Path(temp); out = root / "out"
        native = root / "native"; native.write_bytes(b"synthetic native marker\n")
        bridge = root / "bridge"; bridge.write_bytes(b"synthetic bridge marker\n")
        h = runner.load_private_h()
        h.private_reference(SOURCE)
        sys.path.insert(0, str(G))
        import run_campaign, diagnostics, native_micro
        actual_own = h.verify_own_source()
        build = root / "build.json"
        save(build, {"binary_sha256": h.file_record(bridge)["sha256"],
            "vigilode_commit": h.VIGILODE_COMMIT, "diffsol_version": "0.17.1", "exit_code": 0,
            "source_files": {k: actual_own["runtime_files"][k] for k in
                ("rust_bridge/Cargo.toml", "rust_bridge/Cargo.lock", "rust_bridge/src/main.rs")}})
        identity = {"path": str(native), "synthetic": True}
        authority = SimpleNamespace(verify_native_binary=lambda *a, **k: identity,
            verify_inputs=lambda *a: {"synthetic_input": True}, fixture_scales=lambda f: {})
        h.context = lambda a: (SOURCE, G, BASELINE, authority, {"synthetic_input": True})
        class FakeProcess:
            def poll(self):
                return 0 if "closed" in events else None
        class FakeNative:
            kind = "SYNTHETIC_NATIVE_TEST_ONLY"
            def __init__(self, *args, **kwargs):
                events.append("constructed"); self.calls = 0; self.process = FakeProcess()
            def close(self):
                events.append("closed")
        def admit(provider, provenance, fixture_identity, source_identity):
            events.append("admitted")
            self.assertIs(provenance, identity)
            self.assertEqual(fixture_identity["sha256"], state["fixture_digest"])
            self.assertEqual(source_identity["own"]["C21I_SOURCE_IDENTITY"]["optimization"], "vectorized_exact")
            def guard(**kwargs):
                self.assertNotIn("closed", events)
                if kwargs.get("full_hash"):
                    events.append("terminal_hash")
                    self.assertIs(kwargs["current_provider"], provider)
                    if terminal_error:
                        raise runner.OptimizedPilotError("SYNTHETIC_TERMINAL_GUARD_FAILURE")
            return {"synthetic": True}, guard
        def optimize(fixture, provider, *args, **kwargs):
            events.append("optimizer")
            self.assertGreater(kwargs["wall_s"], 0.)
            self.assertLess(kwargs["wall_s"], 300.)
            kwargs["cache_guard"]()
            return {"rhs_evaluations": 0, "synthetic_numerical_result": True}
        optimizer = SimpleNamespace(run_optimized_reference=optimize)
        admission = SimpleNamespace(admit_native_cache=admit)
        state = runner.bind_runner(h, optimizer, admission, "vectorized_exact")
        from run_experiment import Fixture
        state["fixture_digest"] = Fixture(**json.loads((BASELINE / "common_ic/fixture.json").read_text())).validate().digest
        h.NUMPY_ALREADY_IMPORTED = False  # Explicit synthetic branch admission.
        publication = ({"synthetic_published": True} if not reject_publication else None)
        args = ["native", "--out", str(out), "--bridge", str(bridge),
                "--bridge-build-receipt", str(build), "--native", str(native), "--cpu", "0"]
        with mock.patch.object(runner, "verify_publications", return_value=publication,
                side_effect=runner.OptimizedPilotError("NATIVE_REQUIRES_MATCHING_PUBLISHED_RECEIPT") if reject_publication else None), \
             mock.patch.object(native_micro, "NativeMicro", FakeNative), \
             mock.patch.object(run_campaign, "snapshot", return_value={"synthetic": True}), \
             mock.patch.object(diagnostics, "recompute_balances", return_value={"synthetic": True}), \
             mock.patch.object(diagnostics, "compare_endpoints", return_value={"synthetic": True}), \
             mock.patch.object(h.os, "sched_getaffinity", return_value={0}), \
             mock.patch.object(h.os, "sched_setaffinity"), \
             mock.patch.object(subprocess, "Popen", side_effect=AssertionError("ACTUAL_PROCESS_FORBIDDEN_IN_STUB_TEST")), \
             contextlib.redirect_stdout(io.StringIO()):
            status = h.main(args)
        return status, events, json.loads((out / "JOB_RECEIPT.json").read_text()), out

    def test_exact_terminal_full_hash_precedes_original_h_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            status, events, receipt, _ = self._native_stub(temp)
            self.assertEqual(status, 0)
            self.assertEqual(events, ["constructed", "admitted", "optimizer", "terminal_hash", "closed"])
            self.assertEqual(receipt["execution"], "COMPLETE")
            self.assertFalse(receipt["native_executed"])

    def test_terminal_guard_failure_is_failed_raw_with_original_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            status, events, receipt, out = self._native_stub(temp, terminal_error=True)
            self.assertEqual(status, 1)
            self.assertEqual(events[-2:], ["terminal_hash", "closed"])
            self.assertEqual(receipt["execution"], "FAILED")
            self.assertIn("SYNTHETIC_TERMINAL_GUARD_FAILURE", receipt["error"])
            self.assertTrue((out / "failure_traceback.log").is_file())

    def test_native_publication_failure_records_raw_before_any_provider(self):
        with tempfile.TemporaryDirectory() as temp:
            status, events, receipt, out = self._native_stub(temp, reject_publication=True)
            self.assertEqual(status, 1)
            self.assertEqual(events, [])
            self.assertFalse(receipt["native_launch_attempted"])
            self.assertFalse(receipt["native_executed"])
            self.assertIn("PUBLISHED_RECEIPT", receipt["error"])
            self.assertTrue((out / "failure_traceback.log").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
