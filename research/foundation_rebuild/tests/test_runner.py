"""The local validator records failures; it never edits science to make tests pass."""
import importlib.util
from pathlib import Path
import json,hashlib,sys
import pytest

@pytest.fixture
def runner():
    path=Path(__file__).resolve().parents[1]/'run_validation.py'
    if not path.is_file():pytest.fail('fixed validation runner missing')
    spec=importlib.util.spec_from_file_location('fnd_fixed_runner',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def test_runner_preserves_failure_output(runner,tmp_path):
    result=runner.run_step('failing',[sys.executable,'-c','import sys;print("first failure");sys.exit(7)'],tmp_path,tmp_path,timeout=5)
    assert result['returncode']==7 and result['status']=='FAILED'
    assert 'first failure' in (tmp_path/'failing.stdout.txt').read_text()
    assert json.loads((tmp_path/'failing.receipt.json').read_text())['returncode']==7

def test_runner_preserves_timeout(runner,tmp_path):
    result=runner.run_step('timeout',[sys.executable,'-u','-c','import time;print("started",flush=True);time.sleep(5)'],tmp_path,tmp_path,timeout=.05)
    assert result['status']=='TIMEOUT' and result['returncode']==124
    assert (tmp_path/'timeout.receipt.json').is_file()

def test_runner_rejects_existing_output(runner,tmp_path):
    with pytest.raises(FileExistsError):runner.prepare_output(tmp_path)

def test_runner_manifest_detects_changed_source(runner,tmp_path):
    (tmp_path/'test.py').write_text('print(1)\n')
    manifest={'files':{'test.py':hashlib.sha256((tmp_path/'test.py').read_bytes()).hexdigest()}}
    (tmp_path/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest))
    assert runner.verify_sources(tmp_path)==1
    (tmp_path/'test.py').write_text('print(2)\n')
    with pytest.raises(ValueError,match='identity'):runner.verify_sources(tmp_path)

def test_runner_manifest_rejects_escape(runner,tmp_path):
    (tmp_path/'SOURCE_MANIFEST.json').write_text(json.dumps({'files':{'../escape':'bad'}}))
    with pytest.raises(ValueError):runner.verify_sources(tmp_path)

def test_runner_manifest_rejects_empty(runner,tmp_path):
    (tmp_path/'SOURCE_MANIFEST.json').write_text('{"files":{}}')
    with pytest.raises(ValueError):runner.verify_sources(tmp_path)

def test_runner_junit_reports_skips_without_promoting(runner,tmp_path):
    p=tmp_path/'suite.xml';p.write_text('<testsuites><testsuite tests="3" failures="0" errors="0" skipped="1"/></testsuites>')
    assert runner.junit_counts(p)=={'tests':3,'failures':0,'errors':0,'skipped':1}

def test_runner_rejects_untracked_python_in_source_tree(runner,tmp_path):
    source=tmp_path/'a.py';source.write_text('pass\n')
    (tmp_path/'SOURCE_MANIFEST.json').write_text(json.dumps({'files':{'a.py':hashlib.sha256(source.read_bytes()).hexdigest()}}))
    (tmp_path/'extra.py').write_text('pass\n')
    with pytest.raises(ValueError,match='undeclared'):runner.verify_sources(tmp_path)

def test_runner_failure_files_are_create_only(runner,tmp_path):
    (tmp_path/'same.stdout.txt').write_text('original')
    with pytest.raises(FileExistsError):runner.run_step('same',[sys.executable,'-c','print("new")'],tmp_path,tmp_path,timeout=5)
    assert (tmp_path/'same.stdout.txt').read_text()=='original'
