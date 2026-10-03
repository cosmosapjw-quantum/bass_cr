import importlib.util,io,hashlib
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
def module(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def test_patch_paths_must_stay_in_new_prefix(tmp_path):
    m=module('apply_checked_patch')
    for p in ['../x','/x','README.md','research/convergence_20261003/r4ai_local_pre_codex/../../x']:
        with pytest.raises(ValueError):m.verify_paths(tmp_path,[{'path':p}])

def test_patch_path_existing_and_duplicate_refused(tmp_path):
    m=module('apply_checked_patch');p='research/convergence_20261003/r4ai_local_pre_codex/x'
    assert m.verify_paths(tmp_path,[{'path':p}])==1
    with pytest.raises(ValueError):m.verify_paths(tmp_path,[{'path':p},{'path':p}])
    (tmp_path/p).parent.mkdir(parents=True);(tmp_path/p).write_text('old')
    with pytest.raises(ValueError):m.verify_paths(tmp_path,[{'path':p}])

def test_runtime_archive_identity_is_checked_before_extraction(tmp_path):
    m=module('unpack_runtime');p=tmp_path/'bad.zip';p.write_bytes(b'bad')
    with pytest.raises(ValueError,match='identity'):m.unpack(p,tmp_path/'out')
    assert not (tmp_path/'out').exists()

def test_download_uses_receipt_identity_and_never_overwrites(tmp_path,monkeypatch):
    m=module('download_dropbox');raw=b'patch-data';h=hashlib.sha256(raw).hexdigest();calls=[]
    monkeypatch.setenv('DROPBOX_ACCESS_TOKEN','TEST_ONLY_TOKEN')
    def open_(req,**kwargs):calls.append(req);return io.BytesIO(raw)
    monkeypatch.setattr(m.urllib.request,'urlopen',open_)
    out=tmp_path/'x';r=m.download('id:test',h,len(raw),out)
    assert out.read_bytes()==raw and r['status']=='DOWNLOAD_BYTES_VERIFIED'
    assert calls[0].full_url=='https://content.dropboxapi.com/2/files/download'
    with pytest.raises(FileExistsError):m.download('id:test',h,len(raw),out)

def test_download_bad_hash_preserves_part(tmp_path,monkeypatch):
    m=module('download_dropbox');monkeypatch.setenv('DROPBOX_ACCESS_TOKEN','TEST_ONLY_TOKEN')
    monkeypatch.setattr(m.urllib.request,'urlopen',lambda *a,**k:io.BytesIO(b'bad'))
    with pytest.raises(ValueError,match='identity'):m.download('id:test','0'*64,3,tmp_path/'x')
    assert not (tmp_path/'x').exists() and (tmp_path/'x.part').read_bytes()==b'bad'

def test_download_without_existing_auth_does_not_make_network_request(tmp_path,monkeypatch):
    m=module('download_dropbox');monkeypatch.delenv('DROPBOX_ACCESS_TOKEN',raising=False)
    def forbidden(*a,**k):pytest.fail('unexpected network')
    monkeypatch.setattr(m.urllib.request,'urlopen',forbidden)
    with pytest.raises(ValueError,match='configured'):m.download('id:test','0'*64,3,tmp_path/'x')
