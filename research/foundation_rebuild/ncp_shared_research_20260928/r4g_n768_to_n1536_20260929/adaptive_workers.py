"""Deterministic, non-native worker-scaling policy for the R4G N1536 successor.

This module plans useful pilot queries only.  It does not launch workers, load the
native operator library, or authorize science execution.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

DEFAULT_STAGES = (8, 16, 32)
HARD_MAX_WORKERS = 32
DEFAULT_WORKER_RAM_BYTES = 1 << 30


@dataclass(frozen=True)
class PilotStage:
    workers: int
    query_ids: tuple[str, ...]


@dataclass(frozen=True)
class StageObservation:
    workers: int
    completed_queries: int
    wall_seconds: float
    failed_queries: int = 0
    peak_rss_bytes: int | None = None

    @property
    def queries_per_second(self) -> float:
        if self.completed_queries < 1 or not math.isfinite(self.wall_seconds) or self.wall_seconds <= 0:
            raise ValueError("positive finite wall time and completed queries required")
        return self.completed_queries / self.wall_seconds


def normalize_stages(stages: Iterable[int], *, hard_max: int = HARD_MAX_WORKERS) -> tuple[int, ...]:
    values = tuple(int(x) for x in stages)
    if not values:
        raise ValueError("at least one worker stage required")
    if hard_max < 1:
        raise ValueError("positive hard worker cap required")
    if any(x < 1 or x > hard_max for x in values):
        raise ValueError("worker stage exceeds allowed range")
    if any(b <= a for a, b in zip(values, values[1:])):
        raise ValueError("worker stages must be strictly increasing")
    return values


def _stratified_indices(length: int, count: int) -> tuple[int, ...]:
    if length < 0 or count < 0 or count > length:
        raise ValueError("invalid stratified sample size")
    if count == 0:
        return ()
    # Mid-cell positions give deterministic coverage across the whole remaining set.
    result = tuple(((2 * k + 1) * length) // (2 * count) for k in range(count))
    if len(set(result)) != count or result[0] < 0 or result[-1] >= length:
        raise ArithmeticError("stratified index construction is not unique/in-range")
    return result


def build_useful_pilot_plan(
    missing_query_ids: Sequence[str],
    *,
    stages: Iterable[int] = DEFAULT_STAGES,
    queries_per_worker: int = 1,
    hard_max: int = HARD_MAX_WORKERS,
) -> tuple[tuple[PilotStage, ...], tuple[str, ...]]:
    """Assign disjoint, retained useful queries to scaling stages.

    Each stage receives ``workers * queries_per_worker`` distinct queries sampled
    deterministically across the then-remaining query set.  All selected queries
    remain part of the scientific cache; no benchmark-only recomputation is planned.
    """
    ids = tuple(str(x) for x in missing_query_ids)
    if len(set(ids)) != len(ids):
        raise ValueError("missing query IDs must be unique")
    if queries_per_worker < 1:
        raise ValueError("positive queries_per_worker required")
    worker_stages = normalize_stages(stages, hard_max=hard_max)
    remaining = list(ids)
    planned: list[PilotStage] = []
    for workers in worker_stages:
        count = min(len(remaining), workers * queries_per_worker)
        if count == 0:
            break
        indices = _stratified_indices(len(remaining), count)
        selected = tuple(remaining[i] for i in indices)
        selected_set = set(selected)
        remaining = [qid for qid in remaining if qid not in selected_set]
        planned.append(PilotStage(workers=workers, query_ids=selected))
    used = [qid for stage in planned for qid in stage.query_ids]
    if len(used) != len(set(used)) or set(used) & set(remaining):
        raise ArithmeticError("pilot plan contains duplicate or overlapping work")
    if len(used) + len(remaining) != len(ids):
        raise ArithmeticError("pilot plan does not partition missing queries")
    return tuple(planned), tuple(remaining)


def validate_resource_scope(
    *,
    stages: Iterable[int],
    cpu_ids: Sequence[int],
    worker_ram_bytes: int,
    total_worker_ram_cap_bytes: int,
    hard_max: int = HARD_MAX_WORKERS,
) -> dict:
    worker_stages = normalize_stages(stages, hard_max=hard_max)
    cpus = tuple(int(x) for x in cpu_ids)
    if len(set(cpus)) != len(cpus) or any(x < 0 for x in cpus):
        raise ValueError("CPU IDs must be unique nonnegative integers")
    maximum = max(worker_stages)
    if len(cpus) < maximum:
        raise ValueError("CPU scope is smaller than maximum worker stage")
    if worker_ram_bytes < 1 or total_worker_ram_cap_bytes < 1:
        raise ValueError("positive RAM limits required")
    worst_ram = maximum * worker_ram_bytes
    if worst_ram > total_worker_ram_cap_bytes:
        raise ValueError("maximum worker stage exceeds total worker RAM cap")
    return {
        "stages": list(worker_stages),
        "cpu_ids": list(cpus),
        "worker_ram_bytes": int(worker_ram_bytes),
        "worst_stage_ram_bytes": int(worst_ram),
        "total_worker_ram_cap_bytes": int(total_worker_ram_cap_bytes),
    }


def summarize_scaling(observations: Sequence[StageObservation]) -> tuple[dict, ...]:
    """Return comparable throughput metrics without automatically authorizing a stage."""
    if not observations:
        raise ValueError("at least one scaling observation required")
    rows = []
    baseline = observations[0]
    base_qps = baseline.queries_per_second
    base_workers = baseline.workers
    for obs in observations:
        if obs.workers < 1 or obs.completed_queries < 1 or obs.failed_queries < 0:
            raise ValueError("invalid stage observation")
        qps = obs.queries_per_second
        speedup = qps / base_qps
        efficiency = speedup * base_workers / obs.workers
        rows.append({
            "workers": obs.workers,
            "completed_queries": obs.completed_queries,
            "failed_queries": obs.failed_queries,
            "wall_seconds": float(obs.wall_seconds),
            "queries_per_second": qps,
            "speedup_vs_first_stage": speedup,
            "parallel_efficiency_vs_first_stage": efficiency,
            "peak_rss_bytes": obs.peak_rss_bytes,
        })
    return tuple(rows)


def fastest_healthy_stage(observations: Sequence[StageObservation]) -> int:
    """Choose maximum measured throughput among zero-failure stages; tie -> fewer workers.

    This is a scheduling decision only.  It does not extend CPU/RAM/authorization scope.
    """
    healthy = [obs for obs in observations if obs.failed_queries == 0]
    if not healthy:
        raise ValueError("no healthy worker stage observation")
    ranked = sorted(healthy, key=lambda obs: (-obs.queries_per_second, obs.workers))
    return ranked[0].workers
