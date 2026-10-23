"""Two negative operational fixtures. All scientific imports are test doubles.

No ODE, constructor, worker process or resource-admission execution is allowed.
The artificial history bytes are deliberately not a scientific NPZ artifact.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


def load_runner_with_science_forbidden():
    modules = {}
    for name in ("numpy", "scipy", "coupled_model", "atomic_network", "resource_control"):
        modules[name] = types.ModuleType(name)
    modules["numpy"].__version__ = "fixture-numpy"
    modules["scipy"].__version__ = "fixture-scipy"
    factory = Mock(side_effect=AssertionError("SCIENCE_CONSTRUCTOR_FORBIDDEN_IN_OPS_FIXTURE"))
    modules["coupled_model"].CoupledFactory = factory
    modules["atomic_network"].AtomicNetwork21 = Mock(
        side_effect=AssertionError("ATOMIC_CONSTRUCTOR_FORBIDDEN_IN_OPS_FIXTURE"))
    for name, value in {"RTOL": 3e-11, "ATOL": 3e-13, "N_OUTPUT": 201,
                        "Z_START": 20., "Z_END": 2.}.items():
        setattr(modules["coupled_model"], name, value)
    for name in ("choose_workers", "observe_resources", "dispatch_allowed"):
        setattr(modules["resource_control"], name,
                Mock(side_effect=AssertionError("ADMISSION_FORBIDDEN_BEFORE_NEGATIVE_REJECTION")))
    path = Path(__file__).resolve().parents[1] / "run_sandbox.py"
    spec = importlib.util.spec_from_file_location("c21o_runner_operational_fixture", path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules), patch.dict(os.environ):
        spec.loader.exec_module(module)
    return module, factory


class RunnerNegativeFixtures(unittest.TestCase):
    def test_swapped_completed_case_is_rejected_before_any_dispatch(self):
        runner, factory = load_runner_with_science_forbidden()
        identity = {"identity_sha256": "FIXTURE_SOURCE_NO_SCIENCE"}
        target = {"case_id": "case0", "signed_sigma": 0., "signed_pi_m": 0.,
                  "signed_pi_r": 0., "ellmax": 8, "method": "BDF", "thomson": True}
        wrong_case = dict(target, case_id="case1", signed_sigma=.2)
        grid = {"schema": "C21O_CASE_GRID_V1", "cases": [target]}
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            output = base / "run"
            case_dir = output / "cases" / "case0"
            case_dir.mkdir(parents=True)
            (base / "grid.json").write_text(json.dumps(grid))
            (output / "MANIFEST.json").write_text(json.dumps({
                "source": identity, "grid": grid, "python": sys.version,
                "numpy": "fixture-numpy", "scipy": "fixture-scipy"}))
            raw = b"EXPLICIT_TEST_DOUBLE_NOT_A_SCIENTIFIC_NPZ"
            (case_dir / "history.npz").write_bytes(raw)
            raw_sha = hashlib.sha256(raw).hexdigest()
            receipt = {"case": wrong_case, "source_identity_sha256": identity["identity_sha256"],
                       "history_sha256": raw_sha}
            (case_dir / "RECEIPT.json").write_text(json.dumps(receipt))
            (case_dir / "COMPLETE.json").write_text(json.dumps({
                "source_identity_sha256": identity["identity_sha256"],
                "history_sha256": raw_sha,
                "receipt_sha256": runner.sha256(case_dir / "RECEIPT.json")}))
            before = {str(p.relative_to(base)): p.read_bytes() for p in base.rglob("*") if p.is_file()}
            with patch.object(runner, "identity", return_value=identity):
                with self.assertRaisesRegex(RuntimeError, "COMPLETED_CASE_BYTE_MISMATCH:case0"):
                    runner.run(base / "grid.json", output, requested=2, resume=True)
            after = {str(p.relative_to(base)): p.read_bytes() for p in base.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            runner.choose_workers.assert_not_called()
            factory.assert_not_called()
            runner.AtomicNetwork21.assert_not_called()

    def test_worker_identity_mismatch_is_rejected_before_affinity_or_science(self):
        runner, factory = load_runner_with_science_forbidden()
        with patch.object(runner, "identity", return_value={"identity_sha256": "ACTUAL_FIXTURE_SOURCE"}), \
                patch.object(runner.os, "sched_setaffinity") as affinity:
            with self.assertRaisesRegex(RuntimeError, "WORKER_SOURCE_IDENTITY_MISMATCH"):
                runner.worker_init([0, 1], "DIFFERENT_EXPECTED_FIXTURE_SOURCE")
            affinity.assert_not_called()
        factory.assert_not_called()
        runner.AtomicNetwork21.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
