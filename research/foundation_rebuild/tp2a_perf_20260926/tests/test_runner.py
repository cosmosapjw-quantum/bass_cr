from pathlib import Path
import os,subprocess,sys
import pytest
import run_tp2a

HERE=Path(__file__).resolve().parents[1]
def test_standalone_help_works_without_pythonpath(tmp_path):
    env=dict(os.environ);env.pop('PYTHONPATH',None)
    p=subprocess.run([sys.executable,'-E',str(HERE/'run_tp2a.py'),'--help'],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert p.returncode==0,p.stderr
    assert '--workers' in p.stdout and '--resume-from' in p.stdout
    assert '--capture' not in p.stdout and '--tolerance' not in p.stdout

def test_existing_directory_not_overwritten(tmp_path):
    p=subprocess.run([sys.executable,str(HERE/'run_tp2a.py'),'--out',str(tmp_path)],text=True,capture_output=True)
    assert p.returncode==2 and 'output exists' in p.stderr
    assert not list(tmp_path.iterdir())

def test_resource_budget_is_positive_and_bounded():
    r=run_tp2a.resource_limits()
    assert 1<=r['default_workers']<=r['max_safe_workers']<=r['affinity_cpu_count']
    assert r['per_worker_blas_threads']==1

def test_finish_claims_not_promoted(tmp_path):
    r={'status':'TP2A_OPERATOR_GEOMETRY_SCAN_PASS','capture_execution_allowed':False,'production_admission':'HOLD'}
    run_tp2a.finish(tmp_path,r)
    import json,zipfile
    saved=json.loads((tmp_path/'RETURN_REPORT.json').read_text());assert saved['capture_execution_allowed'] is False
    with zipfile.ZipFile(tmp_path.with_name(tmp_path.name+'_RETURN.zip')) as z:assert z.testzip() is None

def test_benchmark_parity_refuses_bad_or_nonfinite_matrix():
    import benchmark,numpy as np
    ref={k:np.ones((2,2),complex) for k in benchmark.KEYS}
    got={k:v.copy() for k,v in ref.items()};got['D_tp'][0,0]+=1e-3
    assert not benchmark.parity(got,ref)[0]
    got['D_tp'][0,0]=np.nan
    assert not benchmark.parity(got,ref)[0]

def test_benchmark_structural_zero_uses_absolute_error():
    import benchmark,numpy as np
    ref={k:np.zeros((2,2),complex) for k in benchmark.KEYS}
    got={k:np.full((2,2),1e-15,complex) for k in benchmark.KEYS}
    assert benchmark.parity(got,ref)[0]
