from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
from parallel_bridge import InvalidPair, PlannedQuery, import_parent_extra


@pytest.fixture
def cache_fixture(tmp_path):
    archive = REPO/'research/foundation_rebuild/ncloud_c64g3_20260928/artifacts/tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip'
    base = tmp_path/'base'; base.mkdir()
    parent = tmp_path/'parent'; parent.mkdir()
    canonical = tmp_path/'canonical'; canonical.mkdir()
    with zipfile.ZipFile(archive) as z:
        sc = json.loads(z.read('SCIENCE_CONTEXT.json'))
        names = [n for n in z.namelist() if n.startswith('runtime_queries/') and n.endswith('.json')][:2]
        items = []
        for n in names:
            rec = json.loads(z.read(n)); qid = rec['query_id']
            for dst in (base, parent):
                (dst/(qid+'.json')).write_bytes(z.read(n))
                (dst/(qid+'.npz')).write_bytes(z.read('runtime_queries/'+qid+'.npz'))
            items.append(PlannedQuery(qid, rec['time_hex'], None, None))
    return base, parent, canonical, items, sc['context_id'], sc['context']['contract']


def test_import_valid_nonprefix_and_skip_identical_base(cache_fixture):
    base, parent, canonical, items, cid, contract = cache_fixture
    # One identity is already in base. The other stands in for a new required ID.
    for ext in ('.json','.npz'):
        (base/(items[1].query_id+ext)).unlink()
    result = import_parent_extra(parent, base, canonical, items, cid, contract)
    assert result['imported_ids'] == [items[1].query_id]
    assert result['base_duplicates'] == 1
    assert (canonical/(items[1].query_id+'.json')).is_file()


def test_parent_conflict_blocks(cache_fixture):
    base, parent, canonical, items, cid, contract = cache_fixture
    (parent/(items[0].query_id+'.npz')).write_bytes(b'conflict')
    with pytest.raises(InvalidPair):
        import_parent_extra(parent, base, canonical, items, cid, contract)


def test_orphan_is_reported_and_not_imported(cache_fixture):
    base, parent, canonical, items, cid, contract = cache_fixture
    (parent/(items[0].query_id+'.json')).unlink()
    result = import_parent_extra(parent, base, canonical, items, cid, contract)
    assert items[0].query_id in result['orphan_ids']
    assert not any(canonical.iterdir())
