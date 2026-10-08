import json
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import time

import numpy as np

from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.engine_admission import run_admission
from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.cache_evaluator import cached_evaluator
from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_plan import plan_tasks
from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_store import TaskStore
from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.run_f1_r2_parallel import execute_precompute


KEYS = ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')
CONTEXT = {'engine_identity_sha256': 'e' * 64, 'historical_archive_sha256': 'a' * 64,
           'contract_sha256': 'c' * 64}


def contract():
    return {'runtime_reference_resolutions': [{'order': q, 'subdivisions': 1} for q in (32, 40, 48)],
            'parity_policy': {'numpy_allclose': {'rtol': 1e-11, 'atol': 1e-12},
                'raw_cross_keys': list(KEYS), 'compare_selected_full_arrays': ['S', 'H', 'D'],
                'operator_hermiticity_relative_max': 1e-11, 'metric_min_ratio': 1e-8,
                'runtime_raw_cross_convergence_max': 1e-9,
                'metric_connection_sentinels_z_a0': [-12, -6, 0, 6, 12],
                'epsilon_z_a0': 1e-4, 'metric_derivative_relative_max': 1e-6}}


def serial(t, q, h):
    return ({k: np.ones((1, 1), complex) for k in KEYS},
            {'S': np.eye(2) * (1 + .02 * t), 'H': np.eye(2), 'D': np.eye(2) * .01})


class Evidence:
    representative = {'query_id': 'exact-query', 'time_hex': '0x0.0p+0',
                      'selected_resolution': {'order': 40, 'subdivisions': 1}}
    representatives = {'query_count': 1, 'queries': [representative]}
    def query(self, rep):
        arrays = {'selected__S': np.eye(2), 'selected__H': np.eye(2), 'selected__D': np.eye(2) * .01}
        for q in (32, 40):
            for key in KEYS:
                arrays[f'q{q}_h1__{key}'] = np.ones((1, 1), complex)
        record = {'query_id': 'exact-query', 'context_id': 'historical', 'time_hex': '0x0.0p+0',
                  'qualification': {'selected_resolution': {'order': 40, 'subdivisions': 1}},
                  'attempts': [{'resolution': {'order': q, 'subdivisions': 1}} for q in (32, 40)]}
        return SimpleNamespace(record=record, representative=rep, arrays=arrays)


def test_serial_reducer_equals_precomputed_cache_for_out_of_order_tasks(tmp_path):
    evidence = Evidence()
    scientific = contract()
    reps = {'query_count': 1, 'queries': [evidence.representative]}
    plan = plan_tasks(reps, scientific, 1.0, CONTEXT['engine_identity_sha256'], CONTEXT['historical_archive_sha256'])
    serial_result = run_admission(evidence, serial, 1.0, scientific, 'engine')
    for order in (list(plan.tasks), list(reversed(plan.tasks))):
        store = TaskStore(tmp_path / ('forward' if order[0] == plan.tasks[0] else 'reverse'), CONTEXT)
        completion_order = []
        def synthetic_worker(task):
            if task['task_id'] == order[0]['task_id']:
                time.sleep(.05)
            raw, full = serial(float.fromhex(task['time_hex']), task['order'], task['subdivisions'])
            completion_order.append(task['task_id'])
            return {'task_id': task['task_id'], 'raw': raw, 'full': full}
        assert execute_precompute(order, store, synthetic_worker, 3,
            executor_factory=lambda workers, **kwargs: ThreadPoolExecutor(max_workers=workers)) == 'R2_TASK_PRECOMPUTE_COMPLETE'
        assert completion_order[0] != order[0]['task_id']
        cached_result = run_admission(evidence, cached_evaluator(store, CONTEXT), 1.0, scientific, 'engine')
        normalize = lambda value: json.dumps(value, sort_keys=True, allow_nan=False)
        assert normalize(cached_result) == normalize(serial_result)
