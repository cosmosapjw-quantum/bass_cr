import numpy as np
import pytest

from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.cache_evaluator import cached_evaluator
from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_plan import task_id
from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_store import TaskStore


CONTEXT = {'engine_identity_sha256': 'e' * 64, 'historical_archive_sha256': 'a' * 64,
           'contract_sha256': 'c' * 64}


def test_exact_cache_hit_and_nearby_time_hard_miss(tmp_path):
    store = TaskStore(tmp_path / 'run', CONTEXT)
    row = {'task_id': task_id(CONTEXT, '0x0.0p+0', 40, 1), 'time_hex': '0x0.0p+0',
           'order': 40, 'subdivisions': 1, 'sector': 'full'}
    raw = {key: np.array([[1.]]) for key in ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')}
    full = {'S': np.eye(1), 'H': np.eye(1), 'D': np.zeros((1, 1))}
    store.save(row, raw, full)
    evaluator = cached_evaluator(store, CONTEXT)
    assert evaluator(0.0, 40, 1)[0]['S_tp'][0, 0] == 1.0
    with pytest.raises(Exception, match='R2_CACHE_MISS_NO_FALLBACK'):
        evaluator(np.nextafter(0.0, 1.0), 40, 1)
    with pytest.raises(Exception, match='R2_CACHE_MISS_NO_FALLBACK'):
        evaluator(0.0, 48, 1)
