from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from types import SimpleNamespace
import os
import subprocess
import sys
import time

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import successor as s
import run_n1536 as runner
from adaptive_workers import (StageObservation, build_useful_pilot_plan,
                              fastest_healthy_stage, summarize_scaling)
from parallel_bridge import CacheMiss, CacheOnlyProvider, PlannedQuery
from metric_transport import CandidateResult, phase_aligned_metric_distance
from transport_policy import assess_temporal_pair


def test_n1536_exact_traversal_and_active_union_counts():
    t0, tf = -1.234567890123, 1.234567890123
    required = s.plan_n1536(s.CONTEXT_ID, t0, tf)
    dt = (tf - t0) / 1536
    assert len(required) == 1538
    assert required[0].time_hex == t0.hex()
    assert required[-1].time_hex == tf.hex()
    for j, item in enumerate(required[1:-1]):
        ta = t0 + j * dt
        tb = ta + dt
        assert item.time_hex == float(0.5 * (ta + tb)).hex()
        assert item.width_hex == float(tb - ta).hex()
    present = {required[0].query_id, required[-1].query_id}
    present.update(f"unrelated-{j}" for j in range(2045))
    missing = s.required_missing(required, present)
    assert len(missing) == 1536
    assert len(present | {q.query_id for q in required}) == 3583
    stages, remainder = build_useful_pilot_plan([q.query_id for q in missing])
    plan, pilot = s.plan_receipts(required, missing, stages, remainder, "a" * 40, "b" * 40)
    assert plan["active_required_count"] == 1538
    assert [len(row["query_ids"]) for row in pilot["stages"]] == [16, 32, 64]
    assert len(pilot["remaining_ids"]) == 1424


def test_predecessor_hash_rejected_before_extraction(tmp_path):
    archive = tmp_path / "archive.zip"
    archive.write_bytes(b"not a predecessor")
    with pytest.raises(ValueError, match="SHA256"):
        s.validate_predecessor(archive, s.PREDECESSOR_SHA256, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_successor_admission_has_native_authorization_gate(monkeypatch):
    monkeypatch.delenv("ALLOW_NEW_NATIVE_R4G", raising=False)
    with pytest.raises(PermissionError, match="N1536_NATIVE_NOT_AUTHORIZED"):
        s.admission_scope(SimpleNamespace())


def test_pilot_authority_matches_policy_and_exact_plan(monkeypatch, tmp_path):
    policy = json.loads((HERE / "ADAPTIVE_WORKER_POLICY.json").read_text())
    ids = [f"missing-{i}" for i in range(1536)]
    stages, remainder = build_useful_pilot_plan(ids)
    pilot = {"stages": [{"workers": x.workers, "query_ids": list(x.query_ids)}
                        for x in stages], "remaining_ids": list(remainder)}
    expected = {"worker_stages": [8, 16, 32],
                "pilot_query_counts": [16, 32, 64],
                "pilot_query_total": 112,
                "post_pilot_remaining": 1424}
    assert s.pilot_authority_fields(policy, pilot) == expected
    assert expected["worker_stages"] == policy["stages"]
    assert expected["pilot_query_counts"] == [len(x["query_ids"]) for x in pilot["stages"]]
    bad_pilot = {**pilot, "stages": [dict(row) for row in pilot["stages"]]}
    bad_pilot["stages"][1]["query_ids"] = bad_pilot["stages"][1]["query_ids"][:-1]
    with pytest.raises(ValueError, match="plan mismatch"):
        s.pilot_authority_fields(policy, bad_pilot)

    monkeypatch.setenv("ALLOW_NEW_NATIVE_R4G", "YES_I_AUTHORIZE_N1536")
    for key in s.THREAD_KEYS:
        monkeypatch.setenv(key, "1")
    monkeypatch.setattr(s.serial, "git_identity", lambda: ("a" * 40, "b" * 40))
    monkeypatch.setattr(s.subprocess, "check_output", lambda *a, **k: "")
    monkeypatch.setattr(s.os, "sched_getaffinity", lambda _: set(range(32)))
    monkeypatch.setattr(s, "live_resource_census", lambda *a: {"synthetic": True})
    monkeypatch.setattr(s, "sys", SimpleNamespace(flags=SimpleNamespace(isolated=1),
                     version_info=(3, 11), version="synthetic"))
    args = SimpleNamespace(
        expected_commit="a" * 40, expected_tree="b" * 40,
        out=tmp_path / "out", authorization_id="R4G-N1536-SYNTHETIC-ADMISSION",
        expected_predecessor_sha256=s.PREDECESSOR_SHA256,
        expected_source_pins_sha256="c" * 64,
        expected_query_plan_sha256="d" * 64,
        expected_useful_pilot_plan_sha256="e" * 64,
        stages="8,16,32", hard_max_workers=32,
        cpus=",".join(map(str, range(32))), worker_ram_bytes=1 << 30,
        total_worker_ram_cap_bytes=32 << 30, global_raw_attempt_cap=16896,
        deadline_unix=time.time() + 60, max_wall_seconds=120,
        cost_scope="synthetic non-native scope")
    admission = s.admission_scope(args)
    assert {key: admission[key] for key in expected} == expected
    assert "pilot_queries" not in admission


def test_cache_only_miss_has_no_evaluator_boundary(tmp_path):
    provider = CacheOnlyProvider(tmp_path, s.CONTEXT_ID, {}, set())
    with pytest.raises(CacheMiss, match="CACHE_MISS_UNEXPECTED"):
        provider.at(0.0)
    assert provider.native_calls == 0


def test_n1536_dual_pass_is_valid_synthetic_gate():
    initial = np.zeros(18, complex)
    previous_final = initial.copy()
    previous_final[0] = 1.0
    current_final = initial.copy()
    current_final[0] = 1.0
    current_final[1] = 2e-7
    reference = initial.copy()
    reference[0] = 1.0
    reference[1] = 3e-7
    previous = CandidateResult(True, 768, 1.0, initial, previous_final,
                               np.ones(769), 1e-14, 0.0)
    current = CandidateResult(True, 1536, 0.5, initial, current_final,
                              np.ones(1537), 1e-14, 0.0)
    screens = {"candidate_norm_drift_max": 1e-8,
               "candidate_reference_metric_distance_max": 1e-6,
               "candidate_refinement_metric_distance_max": 1e-6}
    pair = assess_temporal_pair(previous, current, reference, np.eye(18),
                                phase_aligned_metric_distance, screens)
    assert pair["reference_pass"] and pair["refinement_pass"] and pair["qualified"]


def test_resource_invalid_stage_excluded_and_first_healthy_is_baseline():
    rows = [StageObservation(8, 8, 80.0, resource_valid=False),
            StageObservation(16, 16, 80.0),
            StageObservation(32, 32, 160.0)]
    assert fastest_healthy_stage(rows) == 16
    summary = summarize_scaling(rows)
    assert summary[1]["speedup_vs_first_stage"] == 1.0


def test_live_cpu_quota_and_ram_admission(monkeypatch):
    original_read = Path.read_text
    original_iter = Path.iterdir
    original_is_file = Path.is_file
    state = {"quota": "1600000 100000", "memory": "64000000000"}
    def read_text(path, *args, **kwargs):
        key = str(path)
        if key == "/proc/meminfo":
            return "MemAvailable: 100000000 kB\n"
        if key == "/sys/fs/cgroup/cpu.max":
            return state["quota"]
        if key == "/sys/fs/cgroup/memory.max":
            return state["memory"]
        if key == "/sys/fs/cgroup/memory.current":
            return "0"
        return original_read(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", read_text)
    monkeypatch.setattr(Path, "is_file",
                        lambda path: True if str(path) in (
                            "/sys/fs/cgroup/cpu.max", "/sys/fs/cgroup/memory.max",
                            "/sys/fs/cgroup/memory.current") else original_is_file(path))
    monkeypatch.setattr(Path, "iterdir",
                        lambda path: iter(()) if str(path) == "/proc" else original_iter(path))
    monkeypatch.setattr(s.os, "sched_getaffinity", lambda pid: set(range(32)))
    assert s.live_resource_census(list(range(32)), 16, 1 << 30)["cpu_quota_cores"] == 16
    with pytest.raises(ValueError, match="CPU quota"):
        s.live_resource_census(list(range(32)), 32, 1 << 30)
    state["quota"] = "max 100000"
    state["memory"] = str(16 << 30)
    with pytest.raises(ValueError, match="RAM"):
        s.live_resource_census(list(range(32)), 16, 1 << 30)


class _Budget:
    def __init__(self):
        self.cancelled = []
    def used(self):
        return 0
    def cancel(self, reason):
        self.cancelled.append(reason)
    @property
    def root(self):
        return Path("/unused")


class _NonNativePool(ThreadPoolExecutor):
    def __init__(self, *, mp_context=None, **kwargs):
        super().__init__(**kwargs)


def _stage_args(tmp_path):
    return SimpleNamespace(cpus="0,1,2,3,4,5,6,7", worker_ram_bytes=1 << 30,
                           analytic_build=str(tmp_path), deadline_unix=time.time() + 60)


def test_stage_pool_boundary_retains_unique_useful_queries_without_native(monkeypatch, tmp_path):
    items = [PlannedQuery(f"q{i}", "0x0.0p+0", i, "0x1.0p-4") for i in range(8)]
    published = []
    monkeypatch.setattr(runner, "ProcessPoolExecutor", _NonNativePool)
    monkeypatch.setattr(runner, "initialize_worker", lambda *args: None)
    monkeypatch.setattr(runner, "live_resource_census", lambda *args: {"cpus": list(range(8))})
    monkeypatch.setattr(runner, "_worker_with_rss",
                        lambda item: {"query_id": item.query_id, "raw_attempts": 2,
                                      "task_dir": str(tmp_path), "worker_peak_rss_bytes": 1024,
                                      "task_wall_seconds": 0.5,
                                      "selected_resolution": {"order": 8, "subdivisions": 4}})
    monkeypatch.setattr(runner, "publish_pair",
                        lambda source, destination, item, context, contract: published.append(item.query_id))
    rec = runner._run_stage(items, source=tmp_path, args=_stage_args(tmp_path),
                            contract={"runtime_reference_resolutions": [{}, {}]},
                            budget=_Budget(), out=tmp_path, canonical=tmp_path,
                            workers=8)
    assert len(published) == len(set(published)) == 8
    assert set(published) == {x.query_id for x in items}
    assert rec["workers"] == 8 and rec["queries_per_second"] > 0
    assert rec["completed_query_count"] == 8 and rec["failed_query_count"] == 0
    assert rec["raw_attempts_per_completed_query"] == 0
    assert rec["selected_resolution_histogram"] == {"q8_h4": 8}
    assert len(rec["per_query_task_wall_seconds"]) == 8


def test_worker_telemetry_wrapper_reads_selected_rule_without_native(monkeypatch, tmp_path):
    item = PlannedQuery("synthetic-q", "0x0.0p+0", 0, "0x1.0p-4")
    query_dir = tmp_path / "runtime_queries"
    query_dir.mkdir()
    (query_dir / "synthetic-q.json").write_text(
        '{"qualification":{"selected_resolution":{"order":9,"subdivisions":8}}}')
    monkeypatch.setattr(runner, "compute_query",
                        lambda q: {"query_id": q.query_id, "task_dir": str(tmp_path),
                                   "raw_attempts": 3})
    rec = runner._worker_with_rss(item)
    assert rec["selected_resolution"] == {"order": 9, "subdivisions": 8}
    assert rec["task_wall_seconds"] > 0
    assert rec["worker_peak_rss_bytes"] > 0


def test_stage_failure_cancels_budget_and_preserves_failure_receipt(monkeypatch, tmp_path):
    item = PlannedQuery("failed-q", "0x0.0p+0", 0, "0x1.0p-4")
    budget = _Budget()
    monkeypatch.setattr(runner, "ProcessPoolExecutor", _NonNativePool)
    monkeypatch.setattr(runner, "initialize_worker", lambda *args: None)
    monkeypatch.setattr(runner, "live_resource_census", lambda *args: {"cpus": [0]})
    def fail(_):
        raise RuntimeError("synthetic worker failure")
    monkeypatch.setattr(runner, "_worker_with_rss", fail)
    with pytest.raises(RuntimeError, match="synthetic worker failure"):
        runner._run_stage([item], source=tmp_path, args=_stage_args(tmp_path),
                          contract={"runtime_reference_resolutions": [{}, {}]},
                          budget=budget, out=tmp_path, canonical=tmp_path, workers=1)
    assert budget.cancelled
    assert (tmp_path / "STAGE_1_FAILURE.json").is_file()


def test_launcher_parser_native_trap_smoke(tmp_path):
    launcher = HERE / "run_n1536_science.sh"
    env = os.environ.copy()
    env.pop("ALLOW_NEW_NATIVE_R4G", None)
    result = subprocess.run(["bash", str(launcher), str(tmp_path / "out")],
                            env=env, text=True, capture_output=True)
    assert result.returncode == 64
    assert "N1536_NATIVE_NOT_AUTHORIZED" in result.stderr
    parsed = runner.parse_args([
        "--out", str(tmp_path / "out"), "--predecessor-archive", "/unused.zip",
        "--expected-predecessor-sha256", s.PREDECESSOR_SHA256,
        "--source-pins", "/unused-source-pins.json",
        "--expected-source-pins-sha256", "a" * 64,
        "--expected-query-plan-sha256", "b" * 64,
        "--expected-useful-pilot-plan-sha256", "c" * 64,
        "--authorization-id", "R4G-N1536-FUTURE-A1",
        "--expected-commit", "a" * 40, "--expected-tree", "b" * 40,
        "--analytic-build", "/unused", "--deadline-unix", "9999999999",
        "--max-wall-seconds", "3600",
        "--stages", "8,16,32", "--hard-max-workers", "32",
        "--cpus", ",".join(map(str, range(32))),
        "--worker-ram-bytes", str(1 << 30),
        "--total-worker-ram-cap-bytes", str(32 << 30),
        "--global-raw-attempt-cap", "16896", "--cost-scope", "future explicit scope"])
    assert parsed.stages == "8,16,32" and parsed.hard_max_workers == 32


def test_launcher_to_parser_identity_trap_before_native_or_nonce(tmp_path):
    env = os.environ.copy()
    env.update({
        "ALLOW_NEW_NATIVE_R4G": "YES_I_AUTHORIZE_N1536",
        "BASS_R4G_PYTHON": sys.executable,
        "PREDECESSOR_ARCHIVE": "/not-opened.zip",
        "EXPECTED_PREDECESSOR_SHA256": s.PREDECESSOR_SHA256,
        "SOURCE_PINS": "/not-opened-source-pins.json",
        "EXPECTED_SOURCE_PINS_SHA256": "a" * 64,
        "EXPECTED_QUERY_PLAN_SHA256": "b" * 64,
        "EXPECTED_USEFUL_PILOT_PLAN_SHA256": "c" * 64,
        "R4G_AUTHORIZATION_ID": "R4G-N1536-SYNTHETIC-TRAP",
        "EXPECTED_COMMIT": "0" * 40,
        "EXPECTED_TREE": "0" * 40,
        "ANALYTIC_BUILD": "/not-loaded",
        "R4G_DEADLINE_UNIX": str(time.time() + 60),
        "R4G_MAX_WALL_SECONDS": "120",
        "R4G_TERMINATION_GRACE_SECONDS": "1",
        "R4G_WORKER_STAGES": "8,16,32",
        "R4G_HARD_MAX_WORKERS": "32",
        "R4G_CPUS": ",".join(map(str, range(32))),
        "R4G_WORKER_RAM_BYTES": str(1 << 30),
        "R4G_TOTAL_WORKER_RAM_CAP_BYTES": str(32 << 30),
        "R4G_GLOBAL_RAW_ATTEMPT_CAP": "16896",
        "R4G_COST_SCOPE": "synthetic non-native trap",
    })
    out = tmp_path / "trap"
    result = subprocess.run(["bash", str(HERE / "run_n1536_science.sh"), str(out)],
                            env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode != 0
    assert "successor execution commit/tree mismatch" in result.stderr
    assert not out.exists()
    assert not (Path.home() / ".local/state/bass_r4g/authorizations" /
                "R4G-N1536-SYNTHETIC-TRAP.json").exists()


def test_isolated_preparation_packager_import_smoke():
    script = HERE / "make_preparation_package.py"
    result = subprocess.run([sys.executable, "-I", "-B", str(script), "--help"],
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0
    assert "--predecessor-archive" in result.stdout
