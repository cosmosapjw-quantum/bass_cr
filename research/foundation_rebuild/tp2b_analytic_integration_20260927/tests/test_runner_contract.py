from pathlib import Path
import subprocess,sys,os
HERE=Path(__file__).resolve().parents[1]

def test_cli_exposes_analytic_build_not_legacy_native_or_science_tuning(tmp_path):
    env=dict(os.environ);env.pop('PYTHONPATH',None)
    p=subprocess.run([sys.executable,'-E',str(HERE/'run_analytic_geometry_qualification.py'),'--help'],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert p.returncode==0,p.stderr
    for x in ('--out','--analytic-build','--workers','--expected-commit','--resume-from'): assert x in p.stdout
    for x in ('--native-build','--order','--epsilon','--tolerance','--sector','--capture','--gpu'): assert x not in p.stdout
