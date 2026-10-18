import json
from pathlib import Path
import pytest
import campaign
from event_coupler import ZeroMicro,StepRejected
from run_experiment import make_fixture


def test_one_rejected_lane_does_not_discard_a_completed_independent_case(tmp_path,monkeypatch):
    f=make_fixture(a0=.09,dx=.00002,opacity_scale=.001)
    original=campaign.run_history
    def fail_one(f,n,provider,mode,**kwargs):
        if mode=='BE':raise StepRejected('CONTROL_FLOW_ONLY_INJECTED_REJECTION')
        return original(f,n,provider,mode,**kwargs)
    monkeypatch.setattr(campaign,'run_history',fail_one)
    out=tmp_path/'matrix'
    s=campaign.run_matrix(f,[('BE',2),('FULLMID',2)],lambda path:ZeroMicro(),out,with_reference=False)
    assert [c['status'] for c in s['cases']]==['FAILED','COMPLETED']
    assert s['status']=='PARTIAL_WITH_FAILURES'
    assert (out/'BE_0002/FAILURE.json').is_file()
    assert (out/'FULLMID_0002/result.json').is_file()
    assert (out/'SUMMARY.json').is_file()


def test_actual_number_reference_failure_still_preserves_hazard_independent_cases(tmp_path):
    f=make_fixture(a0=.09,dx=.0001,opacity_scale=1.)
    s=campaign.run_matrix(f,[('BE',4),('FULLMID',4)],lambda path:ZeroMicro(),tmp_path/'r',reference_coordinate='number')
    assert s['reference']['status']=='FAILED'
    assert 'RADAU_INTERNAL_NEGATIVE_PHOTON' in s['reference']['error']
    assert s['completed_cases']==2
    assert all(c['errors'] is None for c in s['cases'])
    assert s['status']=='PARTIAL_WITH_FAILURES'


def test_all_successful_cases_share_exact_fixture_and_reference(tmp_path):
    f=make_fixture(a0=.09,dx=.00002,opacity_scale=.001)
    s=campaign.run_matrix(f,[('BE',2),('FULLMID',2)],lambda path:ZeroMicro(),tmp_path/'ok')
    assert s['status']=='COMPLETE_SCOPED'
    assert {c['fixture_sha256'] for c in s['cases']}=={f.digest}
    assert all(c['errors']['normalized_state']>0 for c in s['cases'])


def test_new_runner_never_overwrites_existing_case(tmp_path):
    f=make_fixture();out=tmp_path/'old';out.mkdir();marker=out/'user.txt';marker.write_text('keep')
    with pytest.raises(FileExistsError):campaign.run_matrix(f,[('BE',1)],lambda p:ZeroMicro(),out,with_reference=False)
    assert marker.read_text()=='keep'


def test_provider_closed_on_failed_reference_and_cases(tmp_path):
    instances=[]
    class Broken:
        kind='CONTROL_FLOW_ONLY_PROVIDER'
        closed=False
        def __call__(self,*args):raise RuntimeError('injected provider failure')
        def close(self):self.closed=True
    def factory(path):
        obj=Broken();instances.append(obj);return obj
    r=campaign.run_matrix(make_fixture(),[('BE',2),('FULLMID',2)],factory,tmp_path/'fail')
    assert r['completed_cases']==0 and r['status']=='PARTIAL_WITH_FAILURES'
    assert len(instances)==3 and all(p.closed for p in instances)


def test_cli_native_without_binary_is_a_preflight_error(tmp_path):
    with pytest.raises(SystemExit) as e:campaign.main(['--micro','native','--out',str(tmp_path/'absent')])
    assert e.value.code==2 and not (tmp_path/'absent').exists()


def test_actual_cli_uses_new_hazard_reference(tmp_path):
    rc=campaign.main(['--out',str(tmp_path/'cli'),'--micro','zero','--steps','2','--modes','FULLMID','--dx','.0001','--opacity-scale','1'])
    assert rc==0
    r=json.loads((tmp_path/'cli/radau.json').read_text())
    assert r['reference_coordinate']=='TAU_WITH_EXACT_BIRTH_AMPLITUDES'
