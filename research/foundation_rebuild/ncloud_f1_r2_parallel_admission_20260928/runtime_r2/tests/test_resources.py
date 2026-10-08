import os
import pytest

from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.resources import enforce_thread_policy, select_workers


def test_affinity_64_uses_60_workers_and_reserves_four():
    assert select_workers(64, 128_000_000_000, 330) == 60
    assert select_workers(64, 128_000_000_000, 7) == 7


def test_under_64_affinity_or_under_memory_gate_blocks():
    with pytest.raises(Exception, match='R2_HOST_MISMATCH'):
        select_workers(63, 128_000_000_000, 330)
    with pytest.raises(Exception, match='R2_MEMORY_BLOCKED'):
        select_workers(64, 119_999_999_999, 330)


def test_worker_thread_policy_is_one_and_dynamic_disabled(monkeypatch):
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        monkeypatch.setenv(key, '8')
    result = enforce_thread_policy()
    assert all(os.environ[key] == '1' for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'))
    assert result['OMP_DYNAMIC'] == result['MKL_DYNAMIC'] == 'FALSE'
