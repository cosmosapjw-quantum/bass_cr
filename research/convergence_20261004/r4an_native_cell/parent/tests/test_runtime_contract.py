from pathlib import Path
from copy import deepcopy
import json
import pytest
import run_reference as rr

def env(fixture=False):
    return {'python_sha256':'0'*64,'platform':'test-boundary-only','dependencies':{'numpy':'TEST','scipy':'TEST','mpmath':'TEST'},'fixture':fixture,'available_bytes':3*2**30,'cpu_quota':4}

def prepared(tmp_path,monkeypatch):
    # The OS boundary is a fixture. No runtime admission or physics is claimed.
    monkeypatch.setattr(rr,'observe',lambda:env(True))
    path=tmp_path/'contract.json';out=tmp_path/'not_started'
    rr.prepare(path,out)
    return path,out,json.loads(path.read_text())

def save(p,c):p.write_text(json.dumps(c,sort_keys=True))

def test_prepare_records_no_approval_or_atomic_output(tmp_path,monkeypatch):
    p,o,c=prepared(tmp_path,monkeypatch)
    assert not o.exists() and c['approval_created'] is False
    assert c['scope']=='ONE_GEOMETRY_ONE_ENTRY_REFERENCE' and c['entry']==[0,0,0,0]

def test_test_resource_fixture_is_not_atomic_authorization(tmp_path,monkeypatch):
    p,o,c=prepared(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match='fixture'):rr.validate(c,p,o,rr.sha(p))
    assert not o.exists()

@pytest.mark.parametrize('key,value,pattern',[
    ('source_root','/wrong','root/output'),('output','/wrong','root/output'),
    ('units',{'energy':'J'},'unit'),('scope','ALL_CHANNELS','scope'),
    ('entry',[1,0,0,0],'1s'),('automatic_expansion',True,'scope'),
    ('max_geometry',10,'scope'),('attempt_cap',2,'scope'),
    ('context',{'z':'-32'},'geometry/epoch')])
def test_invalid_bound_contract_rejected_before_observation(tmp_path,monkeypatch,key,value,pattern):
    p,o,c=prepared(tmp_path,monkeypatch);c['environment']=env(False);c[key]=value;save(p,c)
    monkeypatch.setattr(rr,'observe',lambda:pytest.fail('must reject before observing host'))
    with pytest.raises(ValueError,match=pattern):rr.validate(c,p,o,rr.sha(p))

@pytest.mark.parametrize('section,key,value',[
    ('method','degree',40),('method','rho','3'),('method','max_depth',7),
    ('method','absolute_target_Eh','1/1000'),('resource','wall_seconds',3600),
    ('resource','max_evaluations',3000001),('resource','minimum_available_bytes',1),
    ('resource','minimum_cpu_quota',1)])
def test_no_silent_method_or_resource_relaxation(tmp_path,monkeypatch,section,key,value):
    p,o,c=prepared(tmp_path,monkeypatch);c['environment']=env(False);c[section][key]=value;save(p,c)
    monkeypatch.setattr(rr,'observe',lambda:pytest.fail('must reject before observing host'))
    with pytest.raises(ValueError):rr.validate(c,p,o,rr.sha(p))

def test_wrong_sha_cannot_authorize(tmp_path,monkeypatch):
    p,o,c=prepared(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match='approval'):rr.validate(c,p,o,'a'*64)

def test_changed_source_pin_cannot_authorize(tmp_path,monkeypatch):
    p,o,c=prepared(tmp_path,monkeypatch);c['source_input_pins']['source/weak_kernel.py']='a'*64;save(p,c)
    with pytest.raises(ValueError,match='identity'):rr.validate(c,p,o,rr.sha(p))

def test_consumed_output_is_never_replayed(tmp_path,monkeypatch):
    p,o,c=prepared(tmp_path,monkeypatch);c['environment']=env(False);save(p,c);o.mkdir()
    with pytest.raises(FileExistsError,match='consumed'):rr.validate(c,p,o,rr.sha(p))

@pytest.mark.parametrize('changed', [{'available_bytes':2000000000},{'cpu_quota':1}])
def test_resource_shortage_not_a_science_failure(tmp_path,monkeypatch,changed):
    p,o,c=prepared(tmp_path,monkeypatch);c['environment']=env(False);save(p,c)
    observed=env(False);observed.update(changed);monkeypatch.setattr(rr,'observe',lambda:observed)
    with pytest.raises(RuntimeError,match='resource'):rr.validate(c,p,o,rr.sha(p))
    assert not o.exists()

@pytest.mark.parametrize('key,value',[('python_sha256','1'*64),('platform','other'),('dependencies',{})])
def test_new_runtime_identity_requires_new_contract(tmp_path,monkeypatch,key,value):
    p,o,c=prepared(tmp_path,monkeypatch);c['environment']=env(False);save(p,c)
    observed=env(False);observed[key]=value;monkeypatch.setattr(rr,'observe',lambda:observed)
    with pytest.raises(ValueError,match='runtime identity'):rr.validate(c,p,o,rr.sha(p))

def test_prepare_is_create_only(tmp_path,monkeypatch):
    p,o,c=prepared(tmp_path,monkeypatch)
    with pytest.raises(FileExistsError):rr.prepare(p,o)
