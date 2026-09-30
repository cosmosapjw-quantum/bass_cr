from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import bootstrap_tail

# This focused suite is preparation-only, even when approval-shaped fixtures exist.
import ctypes
import pytest
import execution_admission
import static_tail

@pytest.fixture(autouse=True)
def no_native_load_or_nonce_consumption(monkeypatch,tmp_path):
    events=[]
    def forbidden(*args,**kwargs):
        events.append('native loader or nonce-consumer called')
        raise AssertionError('NON_NATIVE_REPLAY_BOUNDARY_CROSSED')
    monkeypatch.setenv('HOME',str(tmp_path/'isolated_home'))
    monkeypatch.setattr(ctypes,'_dlopen',forbidden)
    monkeypatch.setattr(execution_admission,'consume_authorization',forbidden)
    monkeypatch.setattr(static_tail,'consume_authorization',forbidden)
    yield
    assert events==[], 'a swallowed exception cannot hide native/nonce activity'
