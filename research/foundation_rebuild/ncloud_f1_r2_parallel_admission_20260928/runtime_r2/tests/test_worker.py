import numpy as np
import pytest
import os

from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2 import worker


def test_initializer_binds_once_and_task_uses_exact_hex(monkeypatch):
    observed = []
    def factory(*args):
        assert all(os.environ[key] == '1' for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'))
        observed.append('init')
        return lambda t, q, h: ({key: np.array([[t]]) for key in ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')},
                                {'S': np.array([[q + h]]), 'H': np.eye(1), 'D': np.zeros((1, 1))})
    worker.initialize_worker('repo', 'build', 'basis', {}, evaluator_factory=factory)
    a = worker.evaluate_task({'task_id': 'one', 'time_hex': '0x1.8000000000000p+1', 'order': 40, 'subdivisions': 2})
    b = worker.evaluate_task({'task_id': 'two', 'time_hex': '-0x1.0000000000000p+0', 'order': 48, 'subdivisions': 1})
    assert observed == ['init']
    assert a['raw']['S_tp'][0, 0] == 3.0 and b['raw']['S_tp'][0, 0] == -1.0


def test_nonfinite_worker_result_fails_closed():
    worker.initialize_worker('repo', 'build', 'basis', {},
        evaluator_factory=lambda *args: lambda t, q, h: ({key: np.array([[np.nan if key == 'S_tp' else 1.]]) for key in ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')},
                                                     {'S': np.eye(1), 'H': np.eye(1), 'D': np.zeros((1, 1))}))
    with pytest.raises(Exception, match='R2_WORKER_NONFINITE'):
        worker.evaluate_task({'task_id': 'x', 'time_hex': '0x0.0p+0', 'order': 40, 'subdivisions': 1})


def test_worker_keeps_scientific_arrays_and_excludes_metadata():
    keys = ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')
    def factory(*args):
        return lambda t, q, h: ({**{key: np.ones((1, 1)) for key in keys}, 'metadata': {'sector': 'full'}},
                                {'S': np.eye(1), 'H': np.eye(1), 'D': np.zeros((1, 1)), 'diagnostics': {'ok': True}})
    worker.initialize_worker('repo', 'build', 'basis', {}, evaluator_factory=factory)
    result = worker.evaluate_task({'task_id': 'x', 'time_hex': '0x0.0p+0', 'order': 40, 'subdivisions': 1})
    assert set(result['raw']) == set(keys)
    assert set(result['full']) == {'S', 'H', 'D'}
