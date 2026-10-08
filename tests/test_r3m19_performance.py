"""Bounded performance candidates preserve the sampled split operator only."""
import copy
import importlib.util
import json
from pathlib import Path
from contextlib import nullcontext
from types import SimpleNamespace

import numpy as np
import pytest

from cr_repro.r3m11 import ControlledTDLRunner, source_digest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("r3m19_performance", ROOT / "scripts/r3m19_performance.py")
perf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(perf)


def inventory():
    return {"cpu": {"affinity_logical_count": 8, "physical_cores_in_affinity": 4,
                     "quota_logical_capacity": 4.0},
            "memory": {"available_bytes": 4 * 1024**3}, "gpu": {"status": "NOT_PROBED"}}


def plan(**kwargs):
    options = dict(shape=(8, 10, 12), backend="numpy", candidate="buffer_reuse",
                   steps=3, repeats=2, fft_workers=1, max_working_bytes=256 * 1024**2,
                   max_seconds=20.)
    options.update(kwargs)
    return perf.plan_benchmark(inventory(), **options)


@pytest.mark.parametrize("candidate,workers", [("buffer_reuse", 1), ("scipy_fft_workers", 2)])
def test_candidate_matches_frozen_step_without_changing_input(candidate, workers):
    selected = plan(candidate=candidate, fft_workers=workers)
    runner = ControlledTDLRunner(selected["config"])
    rng = np.random.default_rng(103)
    initial = (rng.normal(size=runner.spec.shape()) + 1j * rng.normal(size=runner.spec.shape())).astype(np.complex128)
    initial = runner.normalize(initial)
    saved = initial.copy()
    fast = perf.BufferedSplitStep(runner, candidate=candidate, fft_workers=workers)
    reference, result = initial.copy(), initial.copy()
    for step in range(3):
        time = runner.t0 + (step + .5) * runner.dt_actual
        reference = runner.step(reference, time)
        result = fast.step(result, time)
    np.testing.assert_array_equal(initial, saved)
    np.testing.assert_allclose(result, reference, rtol=5e-13, atol=1e-14)
    assert not np.shares_memory(result, initial)
    assert perf.accuracy_metrics(reference, result)["status"] == "PASS_SAME_DISCRETIZATION_PARITY"


@pytest.mark.parametrize("options,reason", [
    ({"shape": (350, 300, 600)}, "shape"),
    ({"shape": (7, 8, 8)}, "even"),
    ({"steps": 9}, "steps"),
    ({"repeats": 11}, "repeats"),
    ({"fft_workers": 8, "candidate": "scipy_fft_workers"}, "workers"),
    ({"fft_workers": 2}, "numpy.fft"),
    ({"backend": "auto"}, "backend"),
    ({"max_working_bytes": 2 * 1024**3}, "budget"),
    ({"max_working_bytes": 1024}, "memory"),
])
def test_planner_rejects_unbounded_or_misleading_cases_before_allocation(options, reason):
    with pytest.raises(ValueError, match=reason):
        plan(**options)


def test_gpu_request_has_no_cpu_fallback():
    with pytest.raises(ValueError, match="GPU"):
        perf.plan_benchmark(inventory(), shape=(8, 8, 8), backend="cupy")


def test_resource_preflight_rejects_available_memory():
    inv = inventory()
    inv["memory"]["available_bytes"] = 32 * 1024**2
    with pytest.raises(ValueError, match="available"):
        perf.plan_benchmark(inv, shape=(8, 8, 8))


def test_timing_and_accuracy_report_do_not_admit_production():
    selected = plan(steps=2, repeats=2)
    result = perf.benchmark(selected)
    assert result["status"] == "BENCHMARK_COMPLETE_PARITY_PASSED"
    assert result["production_admitted"] is False
    assert result["full_collision_executed"] is False
    assert result["numerical_source_digest"] == source_digest()
    assert len(result["timing"]["reference_wall_seconds"]) == 2
    assert len(result["timing"]["candidate_wall_seconds"]) == 2
    assert result["timing"]["reference_device_seconds"] == []
    assert result["plan"]["warmup_repeats"] == 2
    assert result["actual_dt"] != result["requested_dt"]
    assert result["accuracy"]["status"] == "PASS_SAME_DISCRETIZATION_PARITY"
    json.dumps(result, allow_nan=False)


def test_tampered_plan_does_not_allocate_runner(monkeypatch):
    selected = plan()
    selected["config"]["grid"]["dx"] = .0001
    def prohibited(*args, **kwargs):
        raise AssertionError("runner allocated before plan validation")
    monkeypatch.setattr(perf, "ControlledTDLRunner", prohibited)
    with pytest.raises(ValueError, match="plan"):
        perf.benchmark(selected)


def test_parity_failure_cannot_be_sold_as_speedup():
    ref = np.ones((2, 2, 2), dtype=np.complex128)
    result = perf.accuracy_metrics(ref, ref * 1.00001)
    assert result["status"] == "FAIL_SAME_DISCRETIZATION_PARITY"
    with pytest.raises(ValueError, match="finite"):
        perf.accuracy_metrics(ref, ref * np.nan)


def test_output_is_exclusive_and_failure_evidence_is_retained(tmp_path):
    out = tmp_path / "run"
    perf.execute_benchmark(plan(steps=1, repeats=1), out)
    saved = (out / "RESULT.json").read_bytes()
    with pytest.raises(FileExistsError):
        perf.execute_benchmark(plan(), out)
    assert (out / "RESULT.json").read_bytes() == saved


def test_failed_benchmark_retains_first_failure_without_retry(tmp_path, monkeypatch):
    out = tmp_path / "interrupted"
    def fail(value):
        raise TimeoutError("injected work-budget stop")
    monkeypatch.setattr(perf, "benchmark", fail)
    with pytest.raises(TimeoutError):
        perf.execute_benchmark(plan(), out)
    failure = json.loads((out / "FIRST_FAILURE.json").read_text())
    assert failure["type"] == "TimeoutError"
    assert failure["automatic_retry"] is False
    assert (out / "PLAN.json").is_file()
    assert not (out / "RESULT.json").exists()


def test_gpu_candidate_optional():
    cp = pytest.importorskip("cupy", reason="CuPy/GPU unavailable; GPU performance unverified")
    try:
        if cp.cuda.runtime.getDeviceCount() < 1:
            pytest.skip("No CUDA device; GPU performance unverified")
    except cp.cuda.runtime.CUDARuntimeError:
        pytest.skip("CUDA runtime/device unavailable; GPU performance unverified")
    selected = perf.plan_benchmark(perf.hardware_inventory(include_gpu=True),
                                   shape=(8, 8, 8), backend="cupy", steps=2, repeats=2)
    result = perf.benchmark(selected)
    assert result["status"] == "BENCHMARK_COMPLETE_PARITY_PASSED"
    assert len(result["timing"]["candidate_device_seconds"]) == 2


def test_gpu_monitors_stay_outside_event_timed_trajectory(monkeypatch):
    """Fake event boundary tests instrumentation scope, not GPU execution/speed."""
    inv = inventory()
    inv["gpu"] = dict(status="AVAILABLE", device_free_bytes=8 * 1024**3,
                      pool_reserved_bytes=0)
    selected = perf.plan_benchmark(inv, shape=(8, 8, 8), backend="cupy", steps=3, repeats=2)
    event_state = {"timed": False, "created": 0, "counter_calls": 0}

    class Event:
        def __init__(self):
            self.start = event_state["created"] % 2 == 0
            event_state["created"] += 1
        def record(self):
            event_state["timed"] = self.start
        def synchronize(self):
            pass

    fake_cp = SimpleNamespace(asnumpy=np.asarray,
        cuda=SimpleNamespace(Event=Event, get_elapsed_time=lambda *args: 1.,
                             get_current_stream=lambda: SimpleNamespace(synchronize=lambda: None)))
    original_import = perf.importlib.import_module
    monkeypatch.setattr(perf.importlib, "import_module",
                        lambda name: fake_cp if name == "cupy" else original_import(name))
    monkeypatch.setattr(perf, "hardware_inventory", lambda **kwargs: inv)
    monkeypatch.setattr(perf, "ControlledTDLRunner",
                        lambda cfg: ControlledTDLRunner(dict(cfg, backend="numpy")))
    monkeypatch.setattr(perf, "_gpu_limits", lambda *args: nullcontext())

    def counters(cp):
        assert not event_state["timed"], "memory monitoring contaminated CUDA event interval"
        event_state["counter_calls"] += 1
        return dict(device_free_bytes=8 * 1024**3)

    monkeypatch.setattr(perf, "_gpu_counters", counters)
    result = perf.benchmark(selected)
    assert result["status"] == "BENCHMARK_COMPLETE_PARITY_PASSED"
    assert event_state["counter_calls"] == 1 + 2 * 2 * (2 + selected["request"]["repeats"])
