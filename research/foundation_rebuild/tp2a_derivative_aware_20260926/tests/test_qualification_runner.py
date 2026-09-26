import json
from pathlib import Path
import subprocess,sys


def test_runner_help_exposes_only_fixed_zminus6_qualification():
    runner=Path(__file__).resolve().parents[1]/'run_zminus6_qualification.py'
    p=subprocess.run([sys.executable,str(runner),'--help'],text=True,capture_output=True)
    assert p.returncode==0,p.stderr
    assert '--out' in p.stdout and '--native-build' in p.stdout
    assert '--phase-budget' not in p.stdout and '--epsilon' not in p.stdout and '--capture' not in p.stdout


def test_contract_is_fixed_and_nonpromoting():
    c=json.loads((Path(__file__).resolve().parents[1]/'CONTRACT.json').read_text())
    assert c['z_a0']==-6.0 and c['epsilon_z_a0']==1e-4
    assert c['phase_budget_rad']==24.0 and c['phase_order']==24 and c['reference_order']==32
    assert c['connection_screen']==1e-6
    assert c['capture_execution_allowed'] is False
    assert c['production_admission']=='HOLD' and c['all_bound']=='OPEN' and c['b_grid']=='NO_GO'
