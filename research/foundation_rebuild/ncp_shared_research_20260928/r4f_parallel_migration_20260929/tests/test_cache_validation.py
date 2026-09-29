from __future__ import annotations

import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
from parallel_bridge import InvalidPair, PlannedQuery, publish_pair, validate_pair


@pytest.fixture
def real_pair(tmp_path):
    archive = REPO / 'research/foundation_rebuild/ncloud_c64g3_20260928/artifacts/tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip'
    with zipfile.ZipFile(archive) as z:
        context = json.loads(z.read('SCIENCE_CONTEXT.json'))
        name = next(n for n in z.namelist() if n.startswith('runtime_queries/') and n.endswith('.json'))
        rec = json.loads(z.read(name))
        qid = rec['query_id']
        (tmp_path / (qid + '.json')).write_bytes(z.read(name))
        (tmp_path / (qid + '.npz')).write_bytes(z.read('runtime_queries/' + qid + '.npz'))
    item = PlannedQuery(qid, rec['time_hex'], None, None)
    return tmp_path, item, context['context_id'], context['context']['contract']


def test_real_frozen_pair_validates(real_pair):
    directory, item, cid, contract = real_pair
    result = validate_pair(directory, item, cid, contract)
    assert result['query_id'] == item.query_id


@pytest.mark.parametrize('fault', ['orphan', 'hash', 'context', 'qualification', 'order', 'nan', 'duplicate_json_key'])
def test_invalid_pair_rejected(real_pair, fault):
    directory, item, cid, contract = real_pair
    jp = directory / (item.query_id + '.json')
    npz = directory / (item.query_id + '.npz')
    rec = json.loads(jp.read_text())
    if fault == 'orphan':
        jp.unlink()
    elif fault == 'hash':
        npz.write_bytes(npz.read_bytes() + b'altered')
    elif fault == 'context':
        rec['context_id'] = '0' * 64
    elif fault == 'qualification':
        rec['qualification']['status'] = 'FAILED'
    elif fault == 'order':
        rec['attempts'][0], rec['attempts'][1] = rec['attempts'][1], rec['attempts'][0]
    elif fault == 'nan':
        with np.load(npz, allow_pickle=False) as f:
            arrays = {k: np.array(f[k]) for k in f.files}
        arrays['selected__S'][0, 0] = np.nan
        buffer = io.BytesIO()
        np.savez_compressed(buffer, **arrays)
        npz.write_bytes(buffer.getvalue())
        rec['payload_sha256'] = hashlib.sha256(npz.read_bytes()).hexdigest()
    elif fault == 'duplicate_json_key':
        jp.write_text('{"x":1,"x":2}')
    if fault not in ('orphan', 'duplicate_json_key'):
        jp.write_text(json.dumps(rec))
    with pytest.raises(InvalidPair):
        validate_pair(directory, item, cid, contract)


def test_create_only_publish_rejects_duplicate_even_when_identical(real_pair, tmp_path):
    directory, item, cid, contract = real_pair
    target = tmp_path / 'canonical'
    publish_pair(directory, target, item, cid, contract)
    with pytest.raises(FileExistsError):
        publish_pair(directory, target, item, cid, contract)
