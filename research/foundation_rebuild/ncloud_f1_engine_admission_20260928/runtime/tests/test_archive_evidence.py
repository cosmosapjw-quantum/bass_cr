import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pytest

from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.archive_evidence import open_evidence


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fixture_archive(tmp_path, *, mutate=None):
    context = 'frozen-context'
    time_hex = '0x0.0p+0'
    qid = sha(json.dumps({'schema': 'BASS_TP2D_RUNTIME_QUERY_V1', 'context_id': context,
                          'time_hex': time_hex}, sort_keys=True, separators=(',', ':')).encode())
    basis_io = io.BytesIO()
    np.savez_compressed(basis_io, edges=np.array([0., 1.]), coefficients=np.array([[1.]]))
    basis_json = json.dumps({'schema': 'BASIS', 'identity': 'frozen'}).encode()
    arrays = {'selected__S': np.eye(2), 'selected__H': np.eye(2), 'selected__D': np.zeros((2, 2))}
    for q in (32, 40):
        for key in ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt'):
            arrays[f'q{q}_h1__{key}'] = np.eye(1)
    npz_io = io.BytesIO()
    np.savez_compressed(npz_io, **arrays)
    npz = npz_io.getvalue()
    record = {'schema': 'BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1', 'query_id': qid,
              'context_id': context, 'time_hex': time_hex,
              'qualification': {'selected_resolution': {'order': 40, 'subdivisions': 1}},
              'attempts': [{'resolution': {'order': q, 'subdivisions': 1}} for q in (32, 40)],
              'payload_sha256': sha(npz)}
    files = {'BASIS.json': basis_json, 'BASIS.npz': basis_io.getvalue(),
             f'runtime_queries/{qid}.json': json.dumps(record).encode(),
             f'runtime_queries/{qid}.npz': npz}
    original_query_hashes = (sha(files[f'runtime_queries/{qid}.json']), sha(files[f'runtime_queries/{qid}.npz']))
    if mutate:
        mutate(files, record, qid)
    manifest = {k: {'bytes': len(v), 'sha256': sha(v)} for k, v in files.items()}
    path = tmp_path / 'archive.zip'
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w') as z:
        for name, data in files.items():
            if data is not None:
                z.writestr(name, data)
        z.writestr('MANIFEST.json', json.dumps(manifest))
    contract = {'historical_tp2d_archive': {'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}}
    rep = {'query_count': 1, 'queries': [{'query_id': qid, 'time_hex': time_hex,
           'selected_resolution': {'order': 40, 'subdivisions': 1},
           'json_sha256': original_query_hashes[0],
           'npz_sha256': original_query_hashes[1]}]}
    return path, contract, rep


def test_valid_archive_exposes_exact_basis_and_all_attempt_arrays(tmp_path):
    path, contract, reps = fixture_archive(tmp_path)
    evidence = open_evidence(path, contract, reps)
    basis = evidence.basis()
    assert basis['json_bytes'] and basis['npz_arrays']['coefficients'].shape == (1, 1)
    query = evidence.query(reps['queries'][0])
    assert len(query.arrays) == 15
    assert query.record['time_hex'] == '0x0.0p+0'


def test_archive_sha_mismatch_rejected_before_read(tmp_path):
    path, contract, reps = fixture_archive(tmp_path)
    contract['historical_tp2d_archive']['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='archive SHA'):
        open_evidence(path, contract, reps)


@pytest.mark.parametrize('name', ['../escape', '/absolute', 'BASIS.json'])
def test_unsafe_or_duplicate_zip_member_rejected(tmp_path, name):
    path, contract, reps = fixture_archive(tmp_path)
    with zipfile.ZipFile(path, 'a') as z:
        z.writestr(name, b'x')
    contract['historical_tp2d_archive'] = {'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}
    with pytest.raises(ValueError, match='unsafe|duplicate'):
        open_evidence(path, contract, reps)


def test_missing_basis_or_query_rejected(tmp_path):
    for missing in ('BASIS.npz', 'query'):
        def mutate(files, record, qid):
            files.pop('BASIS.npz' if missing == 'BASIS.npz' else f'runtime_queries/{qid}.npz')
        path, contract, reps = fixture_archive(tmp_path / missing.replace('.', '_'), mutate=mutate)
        with pytest.raises(ValueError, match='missing'):
            open_evidence(path, contract, reps)


def test_basis_byte_tamper_rejected_even_if_manifest_updated(tmp_path):
    def mutate(files, record, qid):
        files['BASIS.json'] += b' '
    path, contract, reps = fixture_archive(tmp_path, mutate=mutate)
    # The contract pins the historical basis bytes independently of the archive manifest.
    contract['basis_policy'] = {'json_sha256': sha(b'{"schema": "BASIS", "identity": "frozen"}')}
    with pytest.raises(ValueError, match='BASIS'):
        open_evidence(path, contract, reps)


@pytest.mark.parametrize('which', ['json', 'npz'])
def test_representative_query_hash_mismatch_rejected(tmp_path, which):
    path, contract, reps = fixture_archive(tmp_path)
    reps['queries'][0][which + '_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='representative'):
        open_evidence(path, contract, reps)


@pytest.mark.parametrize('field,value', [('time_hex', '0x1.0p+0'), ('selected_resolution', {'order': 48, 'subdivisions': 1})])
def test_query_time_or_resolution_drift_rejected(tmp_path, field, value):
    path, contract, reps = fixture_archive(tmp_path)
    reps['queries'][0][field] = value
    with pytest.raises(ValueError, match='time|resolution'):
        open_evidence(path, contract, reps)
