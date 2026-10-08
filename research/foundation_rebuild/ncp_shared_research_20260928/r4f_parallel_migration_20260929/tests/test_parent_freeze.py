from __future__ import annotations

from pathlib import Path
import sys

import pytest

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import run_parallel_bridge as bridge
from run_parallel_bridge import _assert_frozen, _freeze_parent
from qualified_provider import restore_query_store


def test_runner_uses_frozen_provider_restore_api():
    assert bridge.restore_query_store is restore_query_store


def test_parent_freeze_covers_output_logs_exit_and_archive(tmp_path):
    root=tmp_path/'parent';root.mkdir()
    out=root/'output';out.mkdir()
    (out/'query.json').write_text('q')
    (root/'runner.log').write_text('log')
    (root/'EXIT_STATUS.txt').write_text('2')
    (root/'output_RETURN.zip').write_bytes(b'partial archive fixture')
    manifest=_freeze_parent(out,tmp_path/'manifest.json')
    assert set(manifest['files'])=={'output/query.json','runner.log',
                                   'EXIT_STATUS.txt','output_RETURN.zip'}
    _assert_frozen(out,manifest)
    (root/'new.log').write_text('late write')
    with pytest.raises(ValueError,match='membership'):
        _assert_frozen(out,manifest)
