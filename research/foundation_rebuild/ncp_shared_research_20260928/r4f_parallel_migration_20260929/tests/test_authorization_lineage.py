"""A stopped A1 parent can only be resumed by a distinct, linked A2 approval."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import zipfile

import pytest


HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import run_parallel_bridge as bridge
from run_parallel_bridge import _authorization_ids, _parent_receipt


PARENT = 'R4C-N768-BRIDGE-20260929-A1'
PRIOR = 'R4F-N768-MIGRATION-20260929-A1'
FRESH = 'R4F-N768-MIGRATION-REPAIR-20260929-A2'
SERIAL_COMMIT = '4c2c0be5171c74a52b4a6e96b04c33fa00c62481'
SERIAL_TREE = '2e1a3175a7d20cf9c0218fb15f07f72d4afcb425'
ARCHIVE_SHA = '630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35'


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def evidence(tmp_path):
    parent_root = tmp_path / 'parent'
    parent_out = parent_root / 'output'
    parent_out.mkdir(parents=True)
    (parent_root / 'START_UTC.txt').write_text('2026-09-29T02:25:08Z')
    write_json(parent_out / 'EXECUTION_ADMISSION.json', {
        'authorization_id': PARENT, 'execution_head': SERIAL_COMMIT,
        'execution_tree': SERIAL_TREE, 'source_archive_sha256': ARCHIVE_SHA,
        'max_wall_seconds': 36000, 'max_raw_attempts': 8470})
    write_json(parent_out / 'AUTHORIZATION_CONSUMED.json', {
        'authorization_id': PARENT, 'state': 'CONSUMED_BEFORE_NATIVE_LOAD',
        'out': str(parent_out), 'pid': 99999999})
    write_json(parent_out / 'RETURN_REPORT.json', {
        'status': 'R4C_BLOCKED', 'first_failure': {'type': 'InterruptedError'}})
    (parent_out / 'RAW_EVALUATION_LEDGER.jsonl').write_text(
        json.dumps({'event': 'attempt_started', 'attempt': 1}) + '\n')
    receipt = tmp_path / 'STOP_RECEIPT.json'
    write_json(receipt, {
        'parent_authorization_id': PARENT,
        'migration_authorization_id': PRIOR,
        'python_pid': 99999999, 'child_exited': True,
        'supervisor_exited': True,
        'parent_report_sha256': sha(parent_out / 'RETURN_REPORT.json'),
        'classification': 'PLANNED_SERIAL_TO_PARALLEL_MIGRATION'})
    prior_out = tmp_path / 'failed_migration' / 'output'
    prior_out.mkdir(parents=True)
    write_json(prior_out / 'EXECUTION_ADMISSION.json', {
        'authorization_id': PRIOR, 'parent_authorization_id': PARENT,
        'base_serial_commit': SERIAL_COMMIT, 'base_serial_tree': SERIAL_TREE,
        'original_archive_sha256': ARCHIVE_SHA, 'global_raw_attempt_cap': 8470,
        'execution_commit': 'failed-execution-commit',
        'execution_tree': 'failed-execution-tree'})
    write_json(prior_out / 'RETURN_REPORT.json', {
        'status': 'R4F_MIGRATION_BLOCKED',
        'execution_head': 'failed-execution-commit',
        'execution_tree': 'failed-execution-tree',
        'first_failure': {'type': 'AttributeError',
                          'message': "continue_temporal has no attribute 'restore_query_store'"}})
    (prior_out / 'STOP_RECEIPT.json').write_bytes(receipt.read_bytes())
    archive = prior_out.with_name('output_RETURN.zip')
    with zipfile.ZipFile(archive, 'x') as z:
        z.writestr('RETURN_REPORT.json', (prior_out / 'RETURN_REPORT.json').read_bytes())
    hashes = {'stop_receipt': sha(receipt),
              'prior_admission': sha(prior_out / 'EXECUTION_ADMISSION.json'),
              'prior_return': sha(prior_out / 'RETURN_REPORT.json'),
              'prior_archive': sha(archive)}
    return parent_out, receipt, prior_out, hashes


def lineage(evidence, *, prior=PRIOR, fresh=FRESH, hashes=None):
    parent_out, receipt, prior_out, frozen_hashes = evidence
    return _parent_receipt(parent_out, PARENT, prior, fresh, receipt,
                           prior_out, frozen_hashes if hashes is None else hashes,
                           1790684708)


def test_stopped_parent_prior_a1_allows_fresh_a2(evidence):
    result = lineage(evidence)
    assert result['parent_authorization_id'] == PARENT
    assert result['prior_migration_authorization_id'] == PRIOR
    assert result['fresh_migration_authorization_id'] == FRESH
    assert result['stop_receipt_sha256'] == evidence[3]['stop_receipt']
    assert result['prior_archive_sha256'] == evidence[3]['prior_archive']
    assert result['parent_raw_attempts'] == 1


def test_wrong_prior_id_rejected(evidence):
    with pytest.raises(ValueError, match='stopped parent lineage'):
        lineage(evidence, prior='R4F-N768-MIGRATION-WRONG-A1')


@pytest.mark.parametrize('fresh', [PRIOR, PARENT])
def test_fresh_id_must_differ_from_existing_ids(evidence, fresh):
    with pytest.raises(PermissionError, match='three distinct'):
        lineage(evidence, fresh=fresh)


def test_identity_guard_rejects_reuse_without_touching_evidence():
    with pytest.raises(PermissionError, match='three distinct'):
        _authorization_ids(PARENT, PRIOR, PRIOR)


def test_modified_stop_receipt_hash_rejected(evidence):
    _, receipt, _, _ = evidence
    obj = json.loads(receipt.read_text())
    obj['classification'] = 'ALTERED'
    write_json(receipt, obj)
    with pytest.raises(ValueError, match='STOP_RECEIPT SHA256'):
        lineage(evidence)


def test_wrong_supplied_stop_hash_rejected(evidence):
    hashes = dict(evidence[3]); hashes['stop_receipt'] = '0' * 64
    with pytest.raises(ValueError, match='STOP_RECEIPT SHA256'):
        lineage(evidence, hashes=hashes)


def test_parent_serial_evidence_mismatch_rejected(evidence):
    parent_out = evidence[0]
    obj = json.loads((parent_out / 'EXECUTION_ADMISSION.json').read_text())
    obj['execution_head'] = 'wrong'
    write_json(parent_out / 'EXECUTION_ADMISSION.json', obj)
    with pytest.raises(ValueError, match='stopped parent lineage'):
        lineage(evidence)


def test_failed_migration_evidence_hash_mismatch_rejected(evidence):
    prior_out = evidence[2]
    (prior_out / 'RETURN_REPORT.json').write_text('{}')
    with pytest.raises(ValueError, match='failed migration evidence SHA256'):
        lineage(evidence)


def test_prior_native_worker_evidence_rejected(evidence):
    (evidence[2] / 'worker_tasks').mkdir()
    with pytest.raises(ValueError, match='zero-native scope'):
        lineage(evidence)


def test_lineage_check_does_not_cross_native_boundary(evidence, monkeypatch):
    def forbid(*args, **kwargs):
        raise AssertionError('native boundary reached')

    monkeypatch.setattr(bridge, 'check_native_build', forbid)
    monkeypatch.setattr(bridge, '_run_pool', forbid)
    monkeypatch.setattr(bridge, 'initialize_worker', forbid)
    assert lineage(evidence)['fresh_migration_authorization_id'] == FRESH
