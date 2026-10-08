"""Parent-only, create-only operator task store with exact-context readback."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile

import numpy as np

from .task_plan import task_id


RAW_KEYS = ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')
FULL_KEYS = ('S', 'H', 'D')


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _sync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _create_atomic(path, writer):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix='.partial_', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            writer(stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        _sync_dir(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class TaskStore:
    def __init__(self, directory, context, *, read_only=False):
        self.root = Path(directory).resolve()
        self.context = dict(context)
        if not {'engine_identity_sha256', 'historical_archive_sha256', 'contract_sha256'} <= set(context):
            raise ValueError('R2_TASK_CONTEXT_BLOCKED: incomplete context')
        self.task_dir = self.root / 'operator_tasks'
        context_path = self.root / 'TASK_CONTEXT.json'
        if read_only:
            if not self.root.is_dir() or not self.task_dir.is_dir() or not context_path.is_file():
                raise ValueError('R2_RESUME_BLOCKED: incomplete read-only source')
        else:
            self.root.mkdir(parents=True, exist_ok=True)
            self.task_dir.mkdir(exist_ok=True)
        if context_path.exists():
            if json.loads(context_path.read_text()) != self.context:
                raise ValueError('R2_TASK_CONTEXT_BLOCKED: existing context mismatch')
        elif not read_only:
            _create_atomic(context_path, lambda stream: stream.write(_canonical(self.context) + b'\n'))

    def _paths(self, spec):
        identity = task_id(self.context, spec['time_hex'], spec['order'], spec['subdivisions'],
                           spec.get('sector', 'full'))
        if spec['task_id'] != identity:
            raise ValueError('R2_TASK_IDENTITY_BLOCKED: task digest mismatch')
        return self.task_dir / (identity + '.npz'), self.task_dir / (identity + '.json')

    def has(self, spec):
        payload, receipt = self._paths(spec)
        if payload.exists() != receipt.exists():
            raise ValueError('R2_TASK_INCOMPLETE: missing pair member')
        return payload.exists()

    def save(self, spec, raw, full):
        payload, receipt = self._paths(spec)
        if payload.exists() or receipt.exists():
            raise FileExistsError('R2_TASK_COLLISION: create-only task already exists')
        if set(raw) != set(RAW_KEYS) or set(full) != set(FULL_KEYS):
            raise ValueError('R2_TASK_PAYLOAD_BLOCKED: required arrays missing or extra')
        arrays = {('raw__' if group == 'raw' else 'full__') + key: np.asarray(value)
                  for group, section in (('raw', raw), ('full', full)) for key, value in section.items()}
        if any(not np.isfinite(value).all() for value in arrays.values()):
            raise ValueError('R2_TASK_PAYLOAD_BLOCKED: nonfinite array')
        _create_atomic(payload, lambda stream: np.savez_compressed(stream, **arrays))
        data = payload.read_bytes()
        record = {'schema': 'BASS_NCLOUD_F1_R2_OPERATOR_TASK_V1',
                  'task_id': spec['task_id'], 'context': self.context,
                  'engine_identity_sha256': self.context['engine_identity_sha256'],
                  'historical_archive_sha256': self.context['historical_archive_sha256'],
                  'time_hex': spec['time_hex'], 'order': spec['order'],
                  'subdivisions': spec['subdivisions'], 'sector': spec.get('sector', 'full'),
                  'payload_sha256': _sha(data), 'payload_bytes': len(data),
                  'arrays': {key: {'shape': list(value.shape), 'dtype': str(value.dtype)}
                             for key, value in sorted(arrays.items())}}
        record['receipt_sha256'] = _sha(_canonical(record))
        _create_atomic(receipt, lambda stream: stream.write(_canonical(record) + b'\n'))
        return record

    def load(self, spec):
        payload, receipt = self._paths(spec)
        if not payload.is_file() or not receipt.is_file():
            raise FileNotFoundError('R2_CACHE_MISS_NO_FALLBACK: task pair absent')
        record = json.loads(receipt.read_text())
        digest = record.pop('receipt_sha256', None)
        if digest != _sha(_canonical(record)):
            raise ValueError('R2_TASK_RECEIPT_TAMPER: digest mismatch')
        record['receipt_sha256'] = digest
        if (record.get('schema') != 'BASS_NCLOUD_F1_R2_OPERATOR_TASK_V1'
                or record.get('context') != self.context or record.get('task_id') != spec['task_id']
                or record.get('time_hex') != spec['time_hex'] or record.get('order') != spec['order']
                or record.get('subdivisions') != spec['subdivisions']
                or record.get('sector') != spec.get('sector', 'full')
                or record.get('engine_identity_sha256') != self.context['engine_identity_sha256']
                or record.get('historical_archive_sha256') != self.context['historical_archive_sha256']):
            raise ValueError('R2_TASK_RECEIPT_TAMPER: context or task mismatch')
        data = payload.read_bytes()
        if _sha(data) != record['payload_sha256'] or len(data) != record['payload_bytes']:
            raise ValueError('R2_TASK_PAYLOAD_TAMPER: digest/size mismatch')
        with np.load(payload, allow_pickle=False) as loaded:
            arrays = {key: np.array(loaded[key]) for key in loaded.files}
        if set(arrays) != set(record['arrays']):
            raise ValueError('R2_TASK_PAYLOAD_TAMPER: array keys mismatch')
        for key, value in arrays.items():
            if (list(value.shape) != record['arrays'][key]['shape']
                    or str(value.dtype) != record['arrays'][key]['dtype']
                    or not np.isfinite(value).all()):
                raise ValueError('R2_TASK_PAYLOAD_TAMPER: array metadata mismatch')
        return ({key: arrays['raw__' + key] for key in RAW_KEYS},
                {key: arrays['full__' + key] for key in FULL_KEYS})

    def import_valid(self, source_root, specs):
        source = Path(source_root).resolve()
        if source == self.root:
            raise ValueError('R2_RESUME_BLOCKED: source and destination equal')
        if json.loads((source / 'TASK_CONTEXT.json').read_text()) != self.context:
            raise ValueError('R2_RESUME_BLOCKED: exact context mismatch')
        report_path = source / 'RETURN_REPORT.json'
        if report_path.exists():
            status = json.loads(report_path.read_text()).get('status')
            if status not in ('R2_INTERRUPTED', 'F1_INTERRUPTED'):
                raise ValueError('R2_RESUME_BLOCKED: scientific/final result cannot migrate')
        old = TaskStore(source, self.context, read_only=True)
        count = 0
        for spec in specs:
            if not old.has(spec):
                continue
            old.load(spec)
            if self.has(spec):
                raise FileExistsError('R2_RESUME_BLOCKED: destination task collision')
            old_payload, old_receipt = old._paths(spec)
            new_payload, new_receipt = self._paths(spec)
            _create_atomic(new_payload, lambda stream, p=old_payload: stream.write(p.read_bytes()))
            _create_atomic(new_receipt, lambda stream, p=old_receipt: stream.write(p.read_bytes()))
            self.load(spec)
            count += 1
        return count
