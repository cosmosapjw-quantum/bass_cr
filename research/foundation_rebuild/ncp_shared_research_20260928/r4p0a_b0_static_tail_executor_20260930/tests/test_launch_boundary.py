import ctypes,json,os,subprocess
from pathlib import Path
import pytest
import static_tail as s
from bootstrap_tail import HERE,REPO

def test_exact_verified_bank_native_preflight_crosses_no_load(monkeypatch):
    calls=[]
    def trap(*a,**k):calls.append(a);raise AssertionError('native load crossed')
    monkeypatch.setattr(ctypes,'CDLL',trap)
    inputs=Path(os.environ.get('R4P0A_RUNTIME_INPUTS',str(REPO.parent/'runtime_inputs')))
    build=Path(os.environ.get('R4P0A_NATIVE_BUILD',str(REPO.parent/'native_build')))
    contract,plan,native=s.verify_inputs(inputs,build)
    assert len(s.exact_items(plan))==8 and native['native_loaded_by_check'] is False
    assert set(contract['screens'])=={'raw_cross_relative_max','operator_hermiticity_relative_max','metric_min_ratio'}
    assert contract['same_center_order']==20 and not calls
    for n,pin in s.BINDING['delivered_source_sha256'].items():assert s.sha(HERE/n)==pin

@pytest.mark.parametrize('flag',['--nstep','--capture','--b-grid','--full-window'])
def test_parser_rejects_transport_extensions(flag,tmp_path):
    import run_tail
    with pytest.raises(SystemExit) as error:run_tail.main(['--proposal','x','--source-pins','x','--inputs','x','--build','x','--out',str(tmp_path/'out'),flag])
    assert error.value.code==2 and not (tmp_path/'out').exists()

def test_supervisor_cannot_spawn_without_approval(tmp_path,monkeypatch):
    import supervise_tail
    p=tmp_path/'proposal.json';p.write_text('{}');calls=[]
    monkeypatch.setenv('ALLOW_NEW_NATIVE_R4P0','')
    monkeypatch.setattr(subprocess,'Popen',lambda *a,**k:calls.append(a))
    with pytest.raises(PermissionError):supervise_tail.main(['--proposal',str(p),'--source-pins','x','--inputs','x','--build','x','--out',str(tmp_path/'out'),'--approved-proposal-sha256','0'*64])
    assert not calls

def test_bash_launcher_missing_approval_does_not_launch_science(tmp_path):
    env=os.environ.copy()
    for k in ('ALLOW_NEW_NATIVE_R4P0','R4P0_APPROVED_PROPOSAL_SHA256','R4P0_PROPOSAL'):env.pop(k,None)
    r=subprocess.run(['bash',str(HERE/'run_b0_tail_science.sh'),str(tmp_path/'out')],env=env,capture_output=True,text=True)
    assert r.returncode!=0 and not (tmp_path/'out').exists()
    assert not (HERE/'run_b0_tail_science.sh').stat().st_mode&0o111

def test_supervisor_first_failure_terminates_only_dedicated_group(tmp_path,monkeypatch):
    import supervise_tail as v
    proposal={'out_path':str(tmp_path/'out'),'deadline_unix':s.time.time()+30,'wall_seconds':30,'termination_grace_seconds':60}
    path=tmp_path/'proposal.json';path.write_text(json.dumps(proposal));out=tmp_path/'out';out.mkdir();(out/'FIRST_FAILURE.json').write_text('{"type":"SyntheticQualificationFailure"}')
    calls=[]
    class Child:
        pid=987654
        def poll(self):return None
        def wait(self):return 2
    def popen(command,**kw):assert kw=={'start_new_session':True};calls.append(('spawn',command));return Child()
    def terminate(pgid,grace):calls.append(('terminate',pgid,grace));return {'term_sent':True,'kill_sent':False,'group_exited':True}
    monkeypatch.setenv('ALLOW_NEW_NATIVE_R4P0',s.APPROVAL);monkeypatch.setattr(v,'request',lambda *a,**k:None)
    monkeypatch.setattr(v.subprocess,'Popen',popen);monkeypatch.setattr(v,'_terminate_group',terminate)
    monkeypatch.setattr(v,'_exists',lambda pgid:False);monkeypatch.setattr(v,'_package',lambda *a:None)
    rc=v.main(['--proposal',str(path),'--source-pins','x','--inputs','x','--build','x','--out',str(out),'--approved-proposal-sha256',s.sha(path)])
    assert rc==2 and ('terminate',987654,60) in calls
    assert not (out/'AUTHORIZATION_CONSUMED.json').exists()
    assert json.loads((tmp_path/'out_SUPERVISOR.json').read_text())['first_failure_seen']

def test_supervisor_lingering_own_group_is_hard_failure(tmp_path,monkeypatch):
    import supervise_tail as v
    out=tmp_path/'out';out.mkdir()
    child_report=b'{"status":"R4P0_B0_EIGHT_STATIC_SNAPSHOTS_COMPLETE__TAIL_GATE_UNRESOLVED"}'
    (out/'RETURN_REPORT.json').write_bytes(child_report)
    proposal={'out_path':str(out),'deadline_unix':s.time.time()+30,'wall_seconds':30,'termination_grace_seconds':60}
    path=tmp_path/'proposal.json';path.write_text(json.dumps(proposal));calls=[]
    class Child:
        pid=987654
        def poll(self):return 0
        def wait(self):return 0
    monkeypatch.setenv('ALLOW_NEW_NATIVE_R4P0',s.APPROVAL)
    monkeypatch.setattr(v,'request',lambda *a,**k:None)
    monkeypatch.setattr(v.subprocess,'Popen',lambda *a,**k:Child())
    monkeypatch.setattr(v,'_exists',lambda pgid:True)
    def terminate(pgid,grace):
        calls.append(pgid)
        return {'term_sent':True,'kill_sent':True,'group_exited':False}
    monkeypatch.setattr(v,'_terminate_group',terminate)
    monkeypatch.setattr(v,'_package',lambda *a:None)
    rc=v.main(['--proposal',str(path),'--source-pins','x','--inputs','x','--build','x','--out',str(out),'--approved-proposal-sha256',s.sha(path)])
    assert rc==2
    receipt=json.loads((tmp_path/'out_SUPERVISOR.json').read_text())
    assert receipt['failure_type']=='OWN_POOL_TEARDOWN_INCOMPLETE'
    assert receipt['effective_status']=='R4P0_B0_STATIC_EXECUTION_BLOCKED'
    assert receipt['descendants_exited'] is False
    assert json.loads((out/'FIRST_FAILURE.json').read_text())['type']=='OWN_POOL_TEARDOWN_INCOMPLETE'
    assert (out/'RETURN_REPORT.json').read_bytes()==child_report
    assert set(calls)=={987654} and not (out/'AUTHORIZATION_CONSUMED.json').exists()
