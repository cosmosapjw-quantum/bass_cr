import hashlib
import json

import numpy as np
import pytest

from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_plan import task_id
from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_store import TaskStore


CONTEXT = {'engine_identity_sha256': 'e' * 64, 'historical_archive_sha256': 'a' * 64,
           'contract_sha256': 'c' * 64}


def spec(context=CONTEXT, time_hex='0x0.0p+0'):
    return {'task_id': task_id(context, time_hex, 40, 1), 'time_hex': time_hex,
            'order': 40, 'subdivisions': 1, 'sector': 'full'}


def arrays():
    return ({key: np.ones((1, 1), complex) for key in ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')},
            {'S': np.eye(2), 'H': np.eye(2), 'D': np.zeros((2, 2))})


def test_persist_receipt_pins_payload_context_shape_dtype_and_is_create_only(tmp_path):
    store = TaskStore(tmp_path / 'run', CONTEXT)
    row = spec()
    store.save(row, *arrays())
    receipt = json.loads((store.root / 'operator_tasks' / (row['task_id'] + '.json')).read_text())
    payload = store.root / 'operator_tasks' / (row['task_id'] + '.npz')
    assert receipt['payload_sha256'] == hashlib.sha256(payload.read_bytes()).hexdigest()
    assert receipt['context'] == CONTEXT and receipt['time_hex'] == '0x0.0p+0'
    assert receipt['arrays']['raw__S_tp']['shape'] == [1, 1]
    assert receipt['arrays']['raw__S_tp']['dtype'] == 'complex128'
    assert store.load(row)[0]['S_tp'].shape == (1, 1)
    with pytest.raises(FileExistsError):
        store.save(row, *arrays())


@pytest.mark.parametrize('which', ['payload', 'receipt', 'missing_pair'])
def test_payload_receipt_or_missing_member_tamper_rejected(tmp_path, which):
    store = TaskStore(tmp_path / 'run', CONTEXT)
    row = spec()
    store.save(row, *arrays())
    base = store.root / 'operator_tasks' / row['task_id']
    if which == 'payload':
        base.with_suffix('.npz').write_bytes(b'tampered')
    elif which == 'receipt':
        record = json.loads(base.with_suffix('.json').read_text())
        record['order'] = 99
        base.with_suffix('.json').write_text(json.dumps(record))
    else:
        base.with_suffix('.json').unlink()
    with pytest.raises(Exception):
        store.load(row)


def test_exact_context_resume_to_fresh_output_preserves_old_bytes(tmp_path):
    old = TaskStore(tmp_path / 'old', CONTEXT)
    row = spec()
    old.save(row, *arrays())
    source_payload = (old.root / 'operator_tasks' / (row['task_id'] + '.npz')).read_bytes()
    new = TaskStore(tmp_path / 'new', CONTEXT)
    assert new.import_valid(old.root, [row]) == 1
    assert (new.root / 'operator_tasks' / (row['task_id'] + '.npz')).read_bytes() == source_payload
    assert (old.root / 'operator_tasks' / (row['task_id'] + '.npz')).read_bytes() == source_payload


def test_resume_rejects_context_or_scientific_failure(tmp_path):
    old = TaskStore(tmp_path / 'old', CONTEXT)
    row = spec()
    old.save(row, *arrays())
    changed = dict(CONTEXT, contract_sha256='d' * 64)
    new = TaskStore(tmp_path / 'new', changed)
    with pytest.raises(Exception):
        new.import_valid(old.root, [row])
    (old.root / 'RETURN_REPORT.json').write_text(json.dumps({'status': 'F1_RAW_PARITY_FAILED'}))
    later = TaskStore(tmp_path / 'later', CONTEXT)
    with pytest.raises(Exception):
        later.import_valid(old.root, [row])


def test_resume_does_not_create_missing_source_task_directory(tmp_path):
    source = tmp_path / 'incomplete_old'
    source.mkdir()
    (source / 'TASK_CONTEXT.json').write_text(json.dumps(CONTEXT))
    new = TaskStore(tmp_path / 'new', CONTEXT)
    with pytest.raises(Exception):
        new.import_valid(source, [spec()])
    assert not (source / 'operator_tasks').exists()
