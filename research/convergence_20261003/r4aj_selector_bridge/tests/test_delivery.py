import hashlib,importlib.util,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
def load(path):
 s=importlib.util.spec_from_file_location(path.stem,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
verify=load(ROOT/'verify_release.py').verify
paths=load(ROOT/'tools/apply_checked_patch.py').verify_paths

def fixture(tmp):
 (tmp/'x').write_bytes(b'abc')
 m={'schema':'R4AJ_RELEASE_MANIFEST_V1','files':[{'path':'x','bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()}]}
 (tmp/'RELEASE_MANIFEST.json').write_text(json.dumps(m));return m

def test_valid_release(tmp_path):
 fixture(tmp_path);assert verify(tmp_path)['files']==1
@pytest.mark.parametrize('case',['hash','size','duplicate','escape'])
def test_corrupt_release_refused(tmp_path,case):
 m=fixture(tmp_path)
 if case=='hash':m['files'][0]['sha256']='0'*64
 if case=='size':m['files'][0]['bytes']=9
 if case=='duplicate':m['files']*=2
 if case=='escape':m['files'][0]['path']='../x'
 (tmp_path/'RELEASE_MANIFEST.json').write_text(json.dumps(m))
 with pytest.raises(ValueError):verify(tmp_path)

def test_both_new_prefixes_admitted(tmp_path):
 p='research/convergence_20261003/'
 assert paths(tmp_path,[{'path':p+'r4ai_local_pre_codex/a'},{'path':p+'r4aj_selector_bridge/b'}])==2

def test_old_blocked_prefix_not_admitted(tmp_path):
 with pytest.raises(ValueError):paths(tmp_path,[{'path':'research/convergence_20261003/r4ad_s_only_error/a'}])

def test_existing_target_refused(tmp_path):
 f=tmp_path/'research/convergence_20261003/r4aj_selector_bridge/a';f.parent.mkdir(parents=True);f.write_text('keep')
 with pytest.raises(ValueError):paths(tmp_path,[{'path':str(f.relative_to(tmp_path))}])
