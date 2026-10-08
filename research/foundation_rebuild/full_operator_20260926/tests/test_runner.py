import json,os,subprocess,sys
from pathlib import Path
import pytest

@pytest.mark.parametrize('case',['missing_cross','wrong_commit'])
def test_runner_preserves_preflight_failure_without_starting_tests(tmp_path,case):
    here=Path(__file__).resolve().parents[1]
    out=tmp_path/'return'
    command=[sys.executable,str(here/'run_validation.py'),'--cross-dir',str(tmp_path/'absent'),'--out',str(out)]
    if case=='wrong_commit':command+=['--expected-commit','0'*40]
    p=subprocess.run(command,capture_output=True,text=True,env=os.environ.copy(),timeout=30)
    assert p.returncode==3
    report=json.loads((out/'RETURN_REPORT.json').read_text())
    assert report['status']=='IDENTITY_OR_INPUT_BLOCKED'
    assert report['first_failure']['phase']=='preflight'
    assert report['steps']==[]
    assert not (out/'tests.xml').exists()
    assert report['capture_run_performed'] is False
    assert out.with_name(out.name+'_RETURN.zip').is_file()
    p2=subprocess.run(command,capture_output=True,text=True,timeout=30)
    assert p2.returncode==3
    assert 'OUTPUT_EXISTS' in p2.stderr
