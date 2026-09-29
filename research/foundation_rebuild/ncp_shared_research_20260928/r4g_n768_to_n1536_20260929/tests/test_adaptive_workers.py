from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import pytest
from adaptive_workers import (
    DEFAULT_STAGES,
    HARD_MAX_WORKERS,
    StageObservation,
    build_useful_pilot_plan,
    fastest_healthy_stage,
    normalize_stages,
    summarize_scaling,
    validate_resource_scope,
)


def qids(n):
    return [f"q{i:04d}" for i in range(n)]


def test_default_plan_is_8_16_32_and_retains_every_query_once():
    stages, remainder = build_useful_pilot_plan(qids(1536))
    assert [s.workers for s in stages] == [8, 16, 32]
    assert [len(s.query_ids) for s in stages] == [8, 16, 32]
    assert len(remainder) == 1480
    used = [q for s in stages for q in s.query_ids]
    assert len(set(used)) == 56
    assert set(used).isdisjoint(remainder)
    assert set(used) | set(remainder) == set(qids(1536))


def test_stratified_plan_samples_domain_not_just_prefix():
    stages, _ = build_useful_pilot_plan(qids(1536), stages=(8,))
    picked = [int(x[1:]) for x in stages[0].query_ids]
    assert min(picked) > 0
    assert max(picked) > 1400
    assert picked == sorted(picked)


def test_custom_stage_count_and_queries_per_worker_are_supported():
    stages, remainder = build_useful_pilot_plan(qids(100), stages=(4, 12), queries_per_worker=2)
    assert [len(s.query_ids) for s in stages] == [8, 24]
    assert len(remainder) == 68


def test_stage_validation_rejects_nonincreasing_and_above_hard_cap():
    with pytest.raises(ValueError):
        normalize_stages((8, 8, 16))
    with pytest.raises(ValueError):
        normalize_stages((8, 16, HARD_MAX_WORKERS + 1))


def test_resource_scope_accepts_32_workers_with_32_cpus_and_32_gib_cap():
    result = validate_resource_scope(
        stages=DEFAULT_STAGES,
        cpu_ids=range(32),
        worker_ram_bytes=1 << 30,
        total_worker_ram_cap_bytes=32 << 30,
    )
    assert result["worst_stage_ram_bytes"] == 32 << 30


def test_resource_scope_rejects_too_few_cpus_or_too_little_ram():
    with pytest.raises(ValueError, match="CPU scope"):
        validate_resource_scope(
            stages=DEFAULT_STAGES,
            cpu_ids=range(16),
            worker_ram_bytes=1 << 30,
            total_worker_ram_cap_bytes=64 << 30,
        )
    with pytest.raises(ValueError, match="RAM cap"):
        validate_resource_scope(
            stages=DEFAULT_STAGES,
            cpu_ids=range(32),
            worker_ram_bytes=1 << 30,
            total_worker_ram_cap_bytes=24 << 30,
        )


def test_scaling_summary_and_fastest_stage_use_observed_throughput():
    obs = [
        StageObservation(8, 8, 80.0),
        StageObservation(16, 16, 90.0),
        StageObservation(32, 32, 100.0),
    ]
    rows = summarize_scaling(obs)
    assert rows[0]["queries_per_second"] == pytest.approx(0.1)
    assert rows[1]["speedup_vs_first_stage"] == pytest.approx((16/90)/0.1)
    assert fastest_healthy_stage(obs) == 32


def test_failed_faster_stage_is_not_selected():
    obs = [
        StageObservation(8, 8, 80.0),
        StageObservation(16, 16, 70.0),
        StageObservation(32, 32, 60.0, failed_queries=1),
    ]
    assert fastest_healthy_stage(obs) == 16


def test_no_healthy_stage_is_rejected():
    with pytest.raises(ValueError, match="no healthy"):
        fastest_healthy_stage([StageObservation(8, 8, 80.0, failed_queries=1)])
