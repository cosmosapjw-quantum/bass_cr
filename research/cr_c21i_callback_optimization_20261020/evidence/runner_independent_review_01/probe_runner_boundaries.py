"""Independent C9 integration probes only; no native/Rust/ODE execution.

Reuses the frozen source and reads the existing focused test evidence.  These
new probes cover the actual private H class binding and native admission time
consumption, which are absent from the already completed 12 runner contracts.
Synthetic providers/publication authority are explicit local test doubles.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest import mock

sys.dont_write_bytecode = True
OUTPUT = Path(__file__).resolve().parent
UNIT = OUTPUT.parents[1]
spec = importlib.util.spec_from_file_location("c21i_independent_runner_review", UNIT / "run_optimized_pilot.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
SOURCE = UNIT.parent / "cr_c21e_event_native_20261018"
G = UNIT.parent / "cr_c21g_reference_refinement_20261019"
BASELINE = SOURCE / "evidence/C21F_NATIVE_NCP_20261018T1358Z"


def identity(path):
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


@dataclass
class SyntheticFixture:
    digest: str = "synthetic-fixture-only"


def private_budget_binding():
    h = runner.load_private_h()
    helper = runner._private_module(UNIT / "native_cache_contract.py", (UNIT / "native_cache_contract.py").read_bytes())
    native = SimpleNamespace(kind=helper.NATIVE_KIND, calls=0, process=None)
    provider = h.BudgetedNativeMicro(native, 1e300)
    before = helper._ClassBinding(provider, "BudgetedNativeMicro", helper.BUDGET_SOURCE_SHA256)
    # Check again after the new runner changes the actual private H bindings.
    runner.bind_runner(h, SimpleNamespace(run_optimized_reference=None),
                       SimpleNamespace(admit_native_cache=None), "vectorized_exact")
    before.check()
    after = helper._ClassBinding(provider, "BudgetedNativeMicro", helper.BUDGET_SOURCE_SHA256)
    after.check()
    assert h.__name__ not in sys.modules
    return {"status": "PASS_SCOPED", "private_module_absent_from_sys_modules": True,
            "source_sha256": helper.BUDGET_SOURCE_SHA256,
            "source_defined_class_check_before_and_after_bind": True,
            "native_constructor_calls": 0, "native_calls": 0}


def native_setup_budget(*, setup_elapsed, full_hash_elapsed=0.0, expected_success):
    clock, events, observed = [100.0], [], {}
    with tempfile.TemporaryDirectory(prefix="c21i-review-runner-clock-") as temp:
        h = runner.load_private_h()
        native_identity = {"synthetic": "no binary or native process"}
        authority = SimpleNamespace(verify_native_binary=lambda *a, **k: native_identity)
        h.context = lambda args: (SOURCE, G, BASELINE, authority, {"synthetic": "input"})
        provider = SimpleNamespace(deadline=108.0)

        def admit(actual_provider, actual_identity, fixture_identity, source_identity):
            assert actual_provider is provider and actual_identity is native_identity
            assert fixture_identity["sha256"] == "synthetic-fixture-only"
            assert source_identity["own"]["C21I_SOURCE_IDENTITY"]["optimization"] == "vectorized_exact"
            events.append("admission")
            clock[0] += setup_elapsed

            def guard(**kwargs):
                assert kwargs["full_hash"] is True and kwargs["current_provider"] is provider
                events.append("terminal_full_hash")
                clock[0] += full_hash_elapsed

            return {"synthetic": "admission contract"}, guard

        def optimize(*args, **kwargs):
            events.append("optimizer_stub")
            observed["wall_s"] = kwargs["wall_s"]
            return {"synthetic": "no ODE result"}

        runner.bind_runner(h, SimpleNamespace(run_optimized_reference=optimize),
                           SimpleNamespace(admit_native_cache=admit), "vectorized_exact")
        args = SimpleNamespace(command="native", native="synthetic-unused",
                               build_dir=None, out=Path(temp))
        h.context(args)
        error = None
        with mock.patch.object(runner.time, "monotonic", side_effect=lambda: clock[0]), \
             mock.patch.object(runner, "verify_publications", return_value={"synthetic": "published receipt"}), \
             mock.patch.object(runner.subprocess, "Popen", side_effect=AssertionError("PROCESS_FORBIDDEN")):
            try:
                h.run_rust_reference(SyntheticFixture(), provider, SOURCE, "unused-bridge",
                                     "unused-output", {}, wall_s=10.0)
            except runner.OptimizedPilotError as caught:
                error = {"class": type(caught).__name__, "message": str(caught)}
        assert (error is None) is expected_success
        assert events[0] == "admission" and events[-1] == "terminal_full_hash"
        if setup_elapsed >= 8.0:
            assert "optimizer_stub" not in events
        else:
            assert observed["wall_s"] == 8.0 - setup_elapsed
        if error is not None:
            assert "ORIGINAL_JOB_WALL_EXCEEDED" in error["message"]
        return {"status": "PASS_SCOPED", "initial_time": 100.0, "original_provider_deadline": 108.0,
                "supplied_remaining_wall_s": 10.0, "setup_elapsed": setup_elapsed,
                "terminal_full_hash_elapsed": full_hash_elapsed, "final_time": clock[0],
                "events": events, "observed_optimizer_wall_s": observed.get("wall_s"),
                "expected_success": expected_success, "error": error,
                "native_processes": 0, "native_calls": 0, "ODE_calls": 0}


paths = [UNIT / name for name in ("run_optimized_pilot.py", "optimized_adapter.py", "native_cache_contract.py", "EXECUTION_MANIFEST.json")]
paths.append(runner.C21H / "run_pilot.py")
before = [identity(path) for path in paths]
result = {
    "schema": "C21I_RUNNER_INDEPENDENT_BOUNDARY_PROBES_V1",
    "started_at_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "New runner integration only; previous 12 runner contracts reused without rerun; no native/Rust/ODE",
    "private_h_budgeted_class": private_budget_binding(),
    "admission_consumes_remaining_budget": native_setup_budget(setup_elapsed=3.0, expected_success=True),
    "admission_exhaustion_rejects_before_optimizer": native_setup_budget(setup_elapsed=9.0, expected_success=False),
    "terminal_hash_cannot_cross_original_deadline": native_setup_budget(setup_elapsed=3.0, full_hash_elapsed=5.0, expected_success=False),
}
after = [identity(path) for path in paths]
assert before == after
result.update(source_before=before, source_after=after, source_identity_unchanged=True,
              finished_at_utc=datetime.now(timezone.utc).isoformat(), status="PASS_SCOPED")
with (OUTPUT / "BOUNDARY_PROBES.json").open("x") as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write("\n")
print(json.dumps({"status": result["status"], "checks": 4, "native_calls": 0,
                  "ODE_calls": 0, "output": str(OUTPUT / "BOUNDARY_PROBES.json")}))
