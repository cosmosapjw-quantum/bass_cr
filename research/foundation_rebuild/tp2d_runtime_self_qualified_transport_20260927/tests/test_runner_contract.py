import hashlib,json,zipfile
from pathlib import Path
import pytest
import run_tp2d

HERE=Path(__file__).resolve().parents[1]
C=json.loads((HERE/'CONTRACT.json').read_text())


def test_contract_freezes_on_demand_reference_only_runtime_policy():
    assert C['runtime_phase_budget'] is None
    assert C['operator_interpolation_used'] is False
    assert C['qualification_sector']=='full'
    assert C['candidate_step_counts']==[24,48,96,192,384]
    assert C['max_unique_runtime_queries']==2048
    assert C['old_test_suite_reexecution'] is False
    assert C['legacy_ring_task_import_allowed'] is False


def test_contract_preserves_claim_ceiling():
    assert C['continuous_trajectory_error_bound'] is False
    assert C['continuous_global_supremum_bound'] is False
    assert C['capture_execution_allowed'] is False
    assert C['production_admission']=='HOLD'
    assert C['all_bound']=='OPEN'
    assert C['b_grid']=='NO_GO'
    assert C['original_capture_gap_resolved'] is False


def make_predecessor(tmp_path):
    report={
        'status':'TP2C_ANALYTIC_FULL13_STATIC_GEOMETRY_PASS',
        'execution_head':'head','execution_tree':'tree',
        'new_tests':{'returncode':0,'counts':{'tests':8,'failures':0,'errors':0,'skipped':0}},
        'full13_static_geometry_coverage':True,
        'full13_z_samples_a0':[-12.0,-10.0,-8.0,-6.0,-4.0,-2.0,0.0,2.0,4.0,6.0,8.0,10.0,12.0],
        'continuous_trajectory_error_bound':False,
        'capture_execution_allowed':False,'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO','original_capture_gap_resolved':False,
    }
    rp=tmp_path/'RETURN_REPORT.json';rp.write_text(json.dumps(report,separators=(',',':'))+'\n')
    zp=tmp_path/'RETURN.zip'
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:z.write(rp,'RETURN_REPORT.json')
    contract=dict(C,upstream_tp2c_commit='head',upstream_tp2c_tree='tree',
                  predecessor_return_report_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),
                  predecessor_return_archive_sha256=hashlib.sha256(zp.read_bytes()).hexdigest())
    return rp,zp,contract


def test_predecessor_verifier_accepts_exact_tp2c_scope_and_bytes(tmp_path):
    rp,zp,contract=make_predecessor(tmp_path)
    rec=run_tp2d.verify_predecessor(rp,zp,contract)
    assert rec['status']=='TP2C_ANALYTIC_FULL13_STATIC_GEOMETRY_PASS'
    assert rec['return_report_sha256']==contract['predecessor_return_report_sha256']
    assert rec['return_archive_sha256']==contract['predecessor_return_archive_sha256']


def test_predecessor_verifier_rejects_claim_ceiling_drift(tmp_path):
    rp,zp,contract=make_predecessor(tmp_path)
    report=json.loads(rp.read_text());report['capture_execution_allowed']=True
    rp.write_text(json.dumps(report,separators=(',',':'))+'\n')
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:z.write(rp,'RETURN_REPORT.json')
    contract['predecessor_return_report_sha256']=hashlib.sha256(rp.read_bytes()).hexdigest()
    contract['predecessor_return_archive_sha256']=hashlib.sha256(zp.read_bytes()).hexdigest()
    with pytest.raises(ValueError,match='claim ceiling'):
        run_tp2d.verify_predecessor(rp,zp,contract)


def test_run_cli_success_keeps_claim_ceiling_and_runtime_qualification_flags(monkeypatch,tmp_path):
    out=tmp_path/'run';pred=tmp_path/'pred.json';arc=tmp_path/'pred.zip'
    pred.write_text('{}');arc.write_bytes(b'x')
    monkeypatch.setattr(run_tp2d,'git_identity',lambda:('head','tree'))
    monkeypatch.setattr(run_tp2d,'verify_sources',lambda: {'self':'ok'})
    monkeypatch.setattr(run_tp2d,'verify_predecessor',lambda *a: {'status':C['predecessor_status'],'return_report_sha256':'a','return_archive_sha256':'b'})
    monkeypatch.setattr(run_tp2d,'run_new_tests',lambda out: {'tests':16,'failures':0,'errors':0,'skipped':0,'returncode':0,'command':['pytest']})
    def fake(contract,out,analytic_build,predecessor,resume_from,progress):
        return {'status':'TP2D_RUNTIME_SELF_QUALIFIED_FULL_WINDOW_TRANSPORT_PASS',
                'all_runtime_operator_queries_qualified':True,'full_window_transport_qualified':True,
                'continuous_global_supremum_bound':False,'continuous_trajectory_error_bound':False,'provider_audit':{'unique_runtime_queries':17}}
    rc=run_tp2d.run_cli([
        '--out',str(out),'--analytic-build',str(tmp_path/'build'),
        '--predecessor-report',str(pred),'--predecessor-archive',str(arc),'--expected-commit','head'],
        confirmatory_fn=fake)
    assert rc==0
    report=json.loads((out/'RETURN_REPORT.json').read_text())
    assert report['status']=='TP2D_RUNTIME_SELF_QUALIFIED_FULL_WINDOW_TRANSPORT_PASS'
    assert report['all_runtime_operator_queries_qualified'] is True
    assert report['full_window_transport_qualified'] is True
    assert report['continuous_global_supremum_bound'] is False
    assert report['continuous_trajectory_error_bound'] is False
    assert report['capture_execution_allowed'] is False
    assert report['production_admission']=='HOLD'
    assert (tmp_path/'run_RETURN.zip').is_file()


def test_run_cli_new_test_failure_is_not_scientific_failure(monkeypatch,tmp_path):
    out=tmp_path/'run';pred=tmp_path/'pred.json';arc=tmp_path/'pred.zip'
    pred.write_text('{}');arc.write_bytes(b'x')
    monkeypatch.setattr(run_tp2d,'git_identity',lambda:('head','tree'))
    monkeypatch.setattr(run_tp2d,'verify_sources',lambda: {'self':'ok'})
    monkeypatch.setattr(run_tp2d,'verify_predecessor',lambda *a: {'status':C['predecessor_status']})
    monkeypatch.setattr(run_tp2d,'run_new_tests',lambda out: {'tests':16,'failures':1,'errors':0,'skipped':0,'returncode':1,'command':['pytest']})
    rc=run_tp2d.run_cli([
        '--out',str(out),'--analytic-build',str(tmp_path/'build'),
        '--predecessor-report',str(pred),'--predecessor-archive',str(arc),'--expected-commit','head'],
        confirmatory_fn=lambda *a,**k: (_ for _ in ()).throw(AssertionError('science must not start')))
    assert rc==3
    report=json.loads((out/'RETURN_REPORT.json').read_text())
    assert report['status']=='NEW_TESTS_FAILED'
    assert report['first_failure']['phase']=='new_tests'
    assert report['all_runtime_operator_queries_qualified'] is False
