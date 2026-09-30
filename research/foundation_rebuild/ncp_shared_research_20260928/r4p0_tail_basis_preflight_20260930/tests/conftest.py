from pathlib import Path
import os
import sys
import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

@pytest.fixture
def inputs():
    root = Path(os.environ.get('R4P0_INPUT_DIR', str(HERE / 'inputs')))
    assert root.is_dir(), 'Exact pinned R4O fixture bytes required, not an external source dependency'
    return root
