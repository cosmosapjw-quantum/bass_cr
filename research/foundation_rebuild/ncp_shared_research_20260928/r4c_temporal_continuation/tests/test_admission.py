"""Focused non-native safety tests. Fake native bytes are never dlopened."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
from types import SimpleNamespace
import numpy as np
import pytest

SIDE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SIDE))
import execution_admission as a

@pytest.mark.parametrize('text',['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}','{"x":-Infinity}'])
def test_strict_json_rejects_bad_tokens(tmp_path,text):
    p=tmp_path/'bad.json';p.write_text(text)
    with pytest.raises(ValueError): a.strict_json(p)

def test_strict_json_accepts_valid(tmp_path):
    p=tmp_path/'good.json';p.write_text('{"x":0.125}')
    assert a.strict_json(p)=={'x':0.125}

@pytest.fixture
def native_fixture(tmp_path):
    source=tmp_path/'moment_kernel.cpp';source.write_bytes(b'fake source for digest test only')
    lib=tmp_path/'libmoments.so';lib.write_bytes(b'NOT AN ELF; NEVER LOAD')
    contract={'analytic_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'analytic_library_sha256':hashlib.sha256(lib.read_bytes()).hexdigest()}
    rec={'schema':'BASS_ANALYTIC_MOMENTS_BUILD_V1',
         'source_sha256':contract['analytic_source_sha256'],
         'library_sha256':contract['analytic_library_sha256'],
         'machine':platform.machine(),'system':platform.system()}
    (tmp_path/'BUILD.json').write_text(json.dumps(rec))
    return tmp_path,source,contract

def test_native_bytes_checked_without_loading(native_fixture):
    directory,source,contract=native_fixture
    result=a.check_native_build(directory,contract,source)
    assert result['native_loaded_by_check'] is False
    assert result['library_sha256']==contract['analytic_library_sha256']

@pytest.mark.parametrize('what',['library','source','receipt','architecture','symlink'])
def test_native_mismatch_rejected_before_load(native_fixture,what):
    directory,source,contract=native_fixture
    p=directory/'BUILD.json'
    if what=='library': (directory/'libmoments.so').write_bytes(b'altered')
    elif what=='source': source.write_bytes(b'altered')
    elif what=='receipt':
        rec=json.loads(p.read_text());rec['library_sha256']='0'*64;p.write_text(json.dumps(rec))
    elif what=='architecture':
        rec=json.loads(p.read_text());rec['machine']='not-this-CPU';p.write_text(json.dumps(rec))
    else:
        lib=directory/'libmoments.so';lib.rename(directory/'other.so');lib.symlink_to(directory/'other.so')
    with pytest.raises(ValueError): a.check_native_build(directory,contract,source)

@pytest.fixture
def clean_request(tmp_path,monkeypatch):
    repo=tmp_path/'repo';repo.mkdir()
    subprocess.run(['git','init','-q',str(repo)],check=True)
    subprocess.run(['git','-C',str(repo),'config','user.name','AuditFixture'],check=True)
    subprocess.run(['git','-C',str(repo),'config','user.email','audit@example.invalid'],check=True)
    (repo/'source.txt').write_text('test fixture only')
    subprocess.run(['git','-C',str(repo),'add','source.txt'],check=True)
    subprocess.run(['git','-C',str(repo),'commit','-qm','fixture'],check=True)
    head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    tree=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD^{tree}'],text=True).strip()
    args=SimpleNamespace(previous_nstep=384,next_nstep=768,expected_resume_archive_sha256=a.ARCHIVE_SHA256,
        expected_commit=head,expected_tree=tree,out=str(tmp_path/'out'))
    for k in a.THREAD_KEYS: monkeypatch.setenv(k,'1')
    monkeypatch.setenv('ALLOW_NEW_NATIVE_R4C','YES_I_AUTHORIZE_ONE_RUNG')
    monkeypatch.setenv('R4C_AUTHORIZATION_ID','synthetic-test-authorization-0001')
    monkeypatch.setenv('R4C_MAX_WALL_SECONDS','60')
    return repo,args,head,tree

def test_valid_request_not_an_execution(clean_request):
    repo,args,head,tree=clean_request
    rec=a.check_request(args,repo,head,tree)
    assert rec['next_nstep']==768 and rec['max_raw_attempts']==8470
    assert not Path(args.out).exists()

@pytest.mark.parametrize('fault',['no_token','other_rung','wrong_tree','wrong_input','dirty','threads','no_budget','bad_nonce','out_in_repo'])
def test_request_fails_closed(clean_request,monkeypatch,fault):
    repo,args,head,tree=clean_request
    if fault=='no_token':monkeypatch.delenv('ALLOW_NEW_NATIVE_R4C')
    elif fault=='other_rung':args.previous_nstep=768;args.next_nstep=1536
    elif fault=='wrong_tree':args.expected_tree='0'*40
    elif fault=='wrong_input':args.expected_resume_archive_sha256='0'*64
    elif fault=='dirty':(repo/'source.txt').write_text('changed')
    elif fault=='threads':monkeypatch.setenv('OMP_NUM_THREADS','8')
    elif fault=='no_budget':monkeypatch.delenv('R4C_MAX_WALL_SECONDS')
    elif fault=='bad_nonce':monkeypatch.setenv('R4C_AUTHORIZATION_ID','../escape')
    elif fault=='out_in_repo':args.out=str(repo/'runs')
    with pytest.raises((PermissionError,ValueError)):a.check_request(args,repo,head,tree)

def test_one_shot_cannot_be_reused(tmp_path,monkeypatch):
    monkeypatch.setattr(Path,'home',classmethod(lambda cls:tmp_path/'fake_home'))
    out=tmp_path/'out';out.mkdir();other=tmp_path/'other';other.mkdir()
    admission={'authorization_id':'synthetic-one-shot-0001','next_nstep':768}
    a.consume_authorization(out,admission)
    with pytest.raises(FileExistsError):a.consume_authorization(other,admission)
    records=list((tmp_path/'fake_home/.local/state/bass_r4c/authorizations').glob('*.json'))
    assert len(records)==1
    assert json.loads(records[0].read_text())['state']=='CONSUMED_BEFORE_NATIVE_LOAD'

def test_ledger_preserves_success_identity(tmp_path):
    expected=(object(),object())
    ledger=a.EvaluationLedger(lambda *args:expected,tmp_path)
    assert ledger(0.,32,1) is expected
    rows=[json.loads(x) for x in (tmp_path/'RAW_EVALUATION_LEDGER.jsonl').read_text().splitlines()]
    assert ledger.attempts==1
    assert [r['event'] for r in rows]==['attempt_started','attempt_completed']

def test_ledger_preserves_failed_attempt(tmp_path):
    def fail(*args):raise ArithmeticError('synthetic failed evaluation')
    ledger=a.EvaluationLedger(fail,tmp_path)
    with pytest.raises(ArithmeticError):ledger(0.,32,1)
    rows=[json.loads(x) for x in (tmp_path/'RAW_EVALUATION_LEDGER.jsonl').read_text().splitlines()]
    assert ledger.attempts==1 and rows[-1]['event']=='attempt_failed'

def test_ledger_bound_before_call(tmp_path):
    calls=[];ledger=a.EvaluationLedger(lambda *x:calls.append(x),tmp_path)
    ledger.attempts=a.MAX_RAW_ATTEMPTS
    with pytest.raises(RuntimeError):ledger(0.,32,1)
    assert calls==[]

def test_signal_classification():
    import signal
    with pytest.raises(TimeoutError):a.interrupted(signal.SIGALRM,None)
    with pytest.raises(InterruptedError):a.interrupted(signal.SIGTERM,None)

def test_770_access_bound_with_real_candidate_algorithm():
    # Exact existing candidate algorithm on identity matrices: query planner test only.
    spec=importlib.util.spec_from_file_location('r4c_count',SIDE/'continue_temporal.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    from metric_transport import run_candidate
    calls=[]
    class ToyProvider:
        def at(self,t):
            calls.append(float(t).hex())
            return SimpleNamespace(S=np.eye(2),H=np.zeros((2,2)),D=np.zeros((2,2)))
    result=run_candidate(ToyProvider(),np.array([1.,0.]),-1.,1.,768)
    assert len(calls)==len(set(calls))==770
    assert np.array_equal(result.final_state,np.array([1.,0.]))

def test_json_exponent_overflow_rejected(tmp_path):
    p=tmp_path/'overflow.json';p.write_text('{"x":1e999}')
    with pytest.raises(ValueError):a.strict_json(p)

def test_launchers_disable_tracked_bytecode_writes():
    for name in ('run_r4c_science.sh','run_r4c_preflight.sh'):
        assert '"$BASS_R4C_PYTHON" -I -B ' in (SIDE/name).read_text()
