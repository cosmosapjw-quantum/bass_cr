from pathlib import Path
import hashlib,json
import pytest
from run_r4al import validate_lock,run
from full_frame import ContractError

def setup(tmp):
    (tmp/'f').write_text('x')
    c={'pins':[{'path':'f','sha256':hashlib.sha256(b'x').hexdigest()}],
       'caps':{'new_cross':0,'new_radial':0,'old_science_replay':0,'stage_attempts':1},
       'halfwidths_a0':['1/64','1/128'],'output':'out'}
    p=tmp/'contract.json';p.write_text(json.dumps(c));return p,c

def test_input_mutation_rejected(tmp_path):
    _,c=setup(tmp_path);(tmp_path/'f').write_text('y')
    with pytest.raises(ContractError):validate_lock(tmp_path,c)

def test_unapproved_scope_rejected(tmp_path):
    _,c=setup(tmp_path);c['caps']['new_cross']=1
    with pytest.raises(ContractError):validate_lock(tmp_path,c)

def test_misbound_output_not_created(tmp_path):
    p,_=setup(tmp_path)
    with pytest.raises(ContractError):run(tmp_path,p,tmp_path/'other')
    assert not (tmp_path/'other').exists()

def test_consumed_output_not_reexecuted(tmp_path,monkeypatch):
    p,_=setup(tmp_path);(tmp_path/'out').mkdir()
    monkeypatch.setattr('run_r4al.load_inputs',lambda *_: (_ for _ in ()).throw(AssertionError('science called')))
    with pytest.raises(ContractError):run(tmp_path,p,tmp_path/'out')

def test_escape_pin_rejected(tmp_path):
    _,c=setup(tmp_path);c['pins'][0]['path']='../unknown'
    with pytest.raises(ContractError):validate_lock(tmp_path,c)

def test_window_change_rejected(tmp_path):
    _,c=setup(tmp_path);c['halfwidths_a0']=['1/32','1/64']
    with pytest.raises(ContractError):validate_lock(tmp_path,c)

def test_valid_lock_is_read_only(tmp_path):
    _,c=setup(tmp_path);before=set(tmp_path.iterdir());validate_lock(tmp_path,c)
    assert set(tmp_path.iterdir())==before
