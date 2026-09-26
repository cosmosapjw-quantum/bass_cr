from pathlib import Path
import subprocess,sys,os,json
import pytest

ROOT=Path(__file__).resolve().parents[1]

def test_standalone_entry_does_not_depend_on_pytest_bootstrap(tmp_path):
    env=dict(os.environ);env.pop('PYTHONPATH',None)
    r=subprocess.run([sys.executable,'-E',str(ROOT/'code/run_validation.py'),'--help'],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert r.returncode==0,r.stderr
    assert '--workers' in r.stdout and '--out' in r.stdout
    assert '--capture' not in r.stdout and '--tolerance' not in r.stdout

def test_create_only_qualifier_does_not_delete_existing_files(tmp_path):
    p=tmp_path/'keep.txt';p.write_text('untouched')
    r=subprocess.run([sys.executable,str(ROOT/'code/run_validation.py'),'--out',str(tmp_path),'--native-build','nonexistent'],capture_output=True,text=True)
    assert r.returncode==2
    assert p.read_text()=='untouched'
