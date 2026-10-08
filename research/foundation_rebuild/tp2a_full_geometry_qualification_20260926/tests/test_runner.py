from pathlib import Path
import json,os,subprocess,sys
import pytest
import run_full_geometry_qualification as runner

HERE=Path(__file__).resolve().parents[1]

def test_help_exposes_only_fixed_execution_controls(tmp_path):
    env=dict(os.environ);env.pop('PYTHONPATH',None)
    p=subprocess.run([sys.executable,'-E',str(HERE/'run_full_geometry_qualification.py'),'--help'],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert p.returncode==0,p.stderr
    for flag in ('--out','--native-build','--workers','--expected-commit','--resume-from'): assert flag in p.stdout
    for forbidden in ('--epsilon','--order','--phase-budget','--capture','--geometry','--tolerance','--gpu'): assert forbidden not in p.stdout


def test_declared_task_specs_are_six_and_exact():
    c=json.loads((HERE/'CONTRACT.json').read_text())
    specs=runner.geometry_task_specs(-4.,c)
    assert len(specs)==6
    assert [(x['method'],x['dz_a0']) for x in specs]==[
        ('phase24',-1e-4),('phase24',0.),('phase24',1e-4),
        ('reference32',-1e-4),('reference32',0.),('reference32',1e-4)]


def test_sequence_stops_before_submitting_later_geometry_after_first_failure():
    seen=[]
    def fake(z):
        seen.append(z)
        return {'z_a0':z,'failed_screens':(['x'] if z==-2 else [])}
    rows,first=runner.sequence_geometries([-4.,-2.,0.,2.],fake)
    assert seen==[-4.,-2.]
    assert [r['z_a0'] for r in rows]==[-4.,-2.]
    assert first['z_a0']==-2.


def test_sequence_runs_all_when_clean():
    seen=[]
    rows,first=runner.sequence_geometries([-4.,-2.,0.],lambda z:(seen.append(z) or {'z_a0':z,'failed_screens':[]}))
    assert seen==[-4.,-2.,0.] and first is None and len(rows)==3


def test_existing_output_is_rejected_without_mutation(tmp_path):
    before=list(tmp_path.iterdir())
    p=subprocess.run([sys.executable,str(HERE/'run_full_geometry_qualification.py'),'--out',str(tmp_path),'--native-build',str(tmp_path/'x')],text=True,capture_output=True)
    assert p.returncode==2
    assert list(tmp_path.iterdir())==before
