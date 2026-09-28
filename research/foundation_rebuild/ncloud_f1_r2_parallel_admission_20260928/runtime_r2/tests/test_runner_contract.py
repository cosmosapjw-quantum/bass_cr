import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pytest

from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.run_f1_r2_parallel import check_authorization, execute_precompute, main
from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_plan import task_id
from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_store import TaskStore


CONTEXT = {'engine_identity_sha256': 'e' * 64, 'historical_archive_sha256': 'a' * 64,
           'contract_sha256': 'c' * 64}


def tasks():
    return [{'task_id': task_id(CONTEXT, time_hex, 40, 1), 'time_hex': time_hex,
             'order': 40, 'subdivisions': 1, 'sector': 'full'}
            for time_hex in ('0x0.0p+0', '0x1.0000000000000p+0')]


def result(task):
    return {'task_id': task['task_id'], 'raw': {key: np.array([[1.]]) for key in ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')},
            'full': {'S': np.eye(1), 'H': np.eye(1), 'D': np.zeros((1, 1))}}


def test_old_f1_authorization_cannot_authorize_r2(tmp_path):
    old = {'schema': 'BASS_NCLOUD_F1_RUN_AUTHORIZATION_V1',
           'implementation_commit': '8236887dd8869de57522d5c87a48972f287969fe',
           'implementation_tree': 'd114060c6dc6bdc1aa10fc6d9ffe9de19da99fae',
           'native_admission_allowed': True, 'max_wall_seconds': 7200, 'spending_limit_krw': 8000}
    path = tmp_path / 'old_synthetic_auth.json'
    path.write_text(json.dumps(old))
    with pytest.raises(Exception, match='R2_EXECUTION_NOT_AUTHORIZED'):
        check_authorization(path, 'r' * 40, 't' * 40)


def test_new_authorization_requires_exact_r2_commit_tree_and_budget(tmp_path):
    row = {'schema': 'BASS_NCLOUD_F1_R2_RUN_AUTHORIZATION_V1',
           'implementation_commit': 'r' * 40, 'implementation_tree': 't' * 40,
           'native_admission_allowed': True, 'max_wall_seconds': 3600,
           'spending_limit_krw': 8000}
    path = tmp_path / 'synthetic_r2_authorization.json'
    path.write_text(json.dumps(row))
    assert check_authorization(path, 'r' * 40, 't' * 40)['max_wall_seconds'] == 3600
    with pytest.raises(Exception, match='R2_EXECUTION_NOT_AUTHORIZED'):
        check_authorization(path, 'r' * 40, 'u' * 40)
    row['spending_limit_krw'] = None
    path.write_text(json.dumps(row))
    with pytest.raises(Exception, match='R2_EXECUTION_NOT_AUTHORIZED'):
        check_authorization(path, 'r' * 40, 't' * 40)


def test_output_collision_fails_closed(tmp_path):
    out = tmp_path / 'existing'
    out.mkdir()
    (out / 'marker').write_bytes(b'original')
    assert main(['--out', str(out)]) != 0
    assert (out / 'marker').read_bytes() == b'original'


def test_missing_authorization_does_not_create_output(tmp_path):
    out = tmp_path / 'new'
    assert main(['--out', str(out)]) != 0
    assert not out.exists()


def test_cli_help_without_authorization():
    script = Path(__file__).resolve().parents[1] / 'run_f1_r2_parallel.py'
    proc = subprocess.run([sys.executable, str(script), '--help'], capture_output=True, text=True)
    assert proc.returncode == 0 and '--authorization' in proc.stdout


def test_default_pool_uses_spawn_without_submitting_science():
    from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.run_f1_r2_parallel import _pool_factory
    pool = _pool_factory(2, initializer=None, initargs=())
    try:
        assert pool._mp_context.get_start_method() == 'spawn'
    finally:
        pool.shutdown(wait=True)


def test_numeric_environment_rejects_pin_drift(tmp_path):
    from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.run_f1_r2_parallel import verify_numeric_environment
    pins = tmp_path / 'requirements-tested.txt'
    pins.write_text('numpy==0.0.0\nscipy==1.17.0\npytest==9.0.2\nmpmath==1.3.0\n')
    with pytest.raises(Exception, match='R2_ENVIRONMENT_BLOCKED'):
        verify_numeric_environment(pins)


@pytest.mark.parametrize('error', [TimeoutError('budget exhausted'), KeyboardInterrupt()])
def test_timeout_or_interrupt_keeps_first_task_and_writes_partial_receipts(tmp_path, error):
    store = TaskStore(tmp_path / 'run', CONTEXT)
    def worker(task):
        if task['time_hex'] == '0x1.0000000000000p+0':
            raise error
        return result(task)
    status = execute_precompute(tasks(), store, worker, 1,
        executor_factory=lambda workers, **kwargs: ThreadPoolExecutor(max_workers=workers))
    assert status == 'R2_INTERRUPTED'
    assert store.load(tasks()[0])[0]['S_tp'][0, 0] == 1.0
    summary = json.loads((store.root / 'PARTIAL_TASK_SUMMARY.json').read_text())
    report = json.loads((store.root / 'RETURN_REPORT.json').read_text())
    assert summary['persisted'] == 1 and report['status'] == 'R2_INTERRUPTED'
    assert report['scientific_admission_pass'] is False


def test_worker_failure_keeps_persisted_task_and_never_claims_pass(tmp_path):
    store = TaskStore(tmp_path / 'run', CONTEXT)
    def worker(task):
        if task['time_hex'] == '0x1.0000000000000p+0':
            raise RuntimeError('synthetic worker failure')
        return result(task)
    status = execute_precompute(tasks(), store, worker, 1,
        executor_factory=lambda workers, **kwargs: ThreadPoolExecutor(max_workers=workers))
    assert status == 'R2_OPERATOR_TASK_FAILED'
    assert store.load(tasks()[0])[0]['S_tp'][0, 0] == 1.0
    assert json.loads((store.root / 'RETURN_REPORT.json').read_text())['scientific_admission_pass'] is False


def test_timeout_before_first_submit_still_writes_partial_receipts(tmp_path):
    store = TaskStore(tmp_path / 'run', CONTEXT)
    def timeout_progress(row):
        raise TimeoutError('synthetic before submit')
    status = execute_precompute(tasks(), store, result, 1, progress=timeout_progress,
        executor_factory=lambda workers, **kwargs: ThreadPoolExecutor(max_workers=workers))
    assert status == 'R2_INTERRUPTED'
    assert json.loads((store.root / 'PARTIAL_TASK_SUMMARY.json').read_text())['persisted'] == 0
    assert json.loads((store.root / 'RETURN_REPORT.json').read_text())['status'] == 'R2_INTERRUPTED'
