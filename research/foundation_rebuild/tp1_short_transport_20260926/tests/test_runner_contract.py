import json
from pathlib import Path
import pytest


def test_parser_exposes_no_capture_gpu_or_tolerance_relaxation_flags():
    import run_tp1
    parser=run_tp1.build_parser()
    opts={s for a in parser._actions for s in a.option_strings}
    assert '--out' in opts and '--expected-commit' in opts
    forbidden=('capture','gpu','rtol','atol','tolerance','z-final','z_initial','nstep','epsilon')
    assert not any(any(word in opt.lower() for word in forbidden) for opt in opts)


def test_existing_output_path_is_refused_without_overwrite(tmp_path):
    import run_tp1
    out=tmp_path/'exists';out.mkdir()
    rc=run_tp1.run_cli(['--out',str(out)],confirmatory_fn=lambda *a,**k: {})
    assert rc==3
    assert list(out.iterdir())==[]


def test_wrong_expected_head_is_identity_blocked_and_preserved(tmp_path,monkeypatch):
    import run_tp1
    monkeypatch.setattr(run_tp1,'git_identity',lambda:('abc','tree'))
    out=tmp_path/'run'
    rc=run_tp1.run_cli(['--out',str(out),'--expected-commit','def'],confirmatory_fn=lambda *a,**k: {})
    assert rc==3
    report=json.loads((out/'RETURN_REPORT.json').read_text())
    assert report['status']=='IDENTITY_OR_INPUT_BLOCKED'
    assert report['first_failure']['phase']=='preflight'
    assert out.with_name(out.name+'_RETURN.zip').exists()


def test_status_precedence_is_phase_specific():
    import run_tp1
    assert run_tp1.status_for_phase('operator_diagnostics')=='OPERATOR_TIME_NODE_FAILED'
    assert run_tp1.status_for_phase('metric_connection')=='METRIC_CONNECTION_FAILED'
    assert run_tp1.status_for_phase('reference_transport')=='REFERENCE_TRANSPORT_FAILED'
    assert run_tp1.status_for_phase('candidate_transport')=='CANDIDATE_TRANSPORT_FAILED'
    assert run_tp1.status_for_phase('temporal_refinement')=='TEMPORAL_REFINEMENT_FAILED'


def test_success_report_cannot_promote_claims(tmp_path,monkeypatch):
    import run_tp1
    monkeypatch.setattr(run_tp1,'git_identity',lambda:(None,None))
    monkeypatch.setattr(run_tp1,'verify_sources',lambda:{'ok':'test'})
    monkeypatch.setattr(run_tp1,'run_new_tests',lambda out:{'tests':1,'failures':0,'errors':0,'skipped':0,'returncode':0})
    def fake(contract,out,progress):
        return {'status':'TP1_SHORT_TRANSPORT_PASS','operator_evaluation_count':7}
    out=tmp_path/'ok'
    rc=run_tp1.run_cli(['--out',str(out)],confirmatory_fn=fake)
    assert rc==0
    report=json.loads((out/'RETURN_REPORT.json').read_text())
    assert report['status']=='TP1_SHORT_TRANSPORT_PASS'
    assert report['capture_execution_allowed'] is False
    assert report['production_admission']=='HOLD'
    assert report['all_bound']=='OPEN'
    assert report['b_grid']=='NO_GO'
    assert report['original_capture_gap_resolved'] is False


def test_confirmatory_contract_is_copied_to_intake(tmp_path,monkeypatch):
    import run_tp1
    monkeypatch.setattr(run_tp1,'git_identity',lambda:(None,None))
    monkeypatch.setattr(run_tp1,'verify_sources',lambda:{'ok':'test'})
    monkeypatch.setattr(run_tp1,'run_new_tests',lambda out:{'tests':1,'failures':0,'errors':0,'skipped':0,'returncode':0})
    out=tmp_path/'ok'
    run_tp1.run_cli(['--out',str(out)],confirmatory_fn=lambda c,o,p:{'status':'TP1_SHORT_TRANSPORT_PASS'})
    intake=json.loads((out/'INTAKE.json').read_text())
    c=intake['contract']
    assert c['z_initial_a0']==-12. and c['z_final_a0']==-10.
    assert c['candidate_step_counts']==[8,16,32,64]
    assert c['epsilon_z_a0']==1e-4
    assert c['capture_execution_allowed'] is False


def test_source_manifest_mismatch_blocks_before_science(tmp_path):
    import run_tp1
    bad=tmp_path/'manifest.json'
    bad.write_text(json.dumps({'files':{'CONTRACT.json':'0'*64}}))
    with pytest.raises(ValueError,match='source mismatch'):
        run_tp1.verify_sources(manifest_path=bad,dependency_path=None)


def test_runner_bootstraps_repo_import_paths_outside_pytest_conftest(tmp_path):
    import os, subprocess, sys
    runner=Path(__file__).resolve().parents[1]/'run_tp1.py'
    code=(
        "import runpy; "
        + "runpy.run_path(%r, run_name='tp1_bootstrap_probe'); " % str(runner)
        + "import bass_foundations, full_operator, aligned_cross; print('TP1_BOOTSTRAP_OK')"
    )
    env=dict(os.environ)
    env.pop('PYTHONPATH',None)
    proc=subprocess.run([sys.executable,'-I','-c',code],cwd=tmp_path,env=env,
                        text=True,capture_output=True)
    assert proc.returncode==0, proc.stderr
    assert 'TP1_BOOTSTRAP_OK' in proc.stdout
