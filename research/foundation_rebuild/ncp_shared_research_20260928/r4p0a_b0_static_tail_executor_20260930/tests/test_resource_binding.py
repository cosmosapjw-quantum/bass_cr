import json,os
import pytest
from resource_census import live_resource_census,verify_prior_pool_teardown,OwnPoolTeardownIncomplete

def peer(root,pid,pgid,cmd):
    r=root/str(pid);r.mkdir();(r/'stat').write_text(f'{pid} (python) S 1 {pgid} {pgid} 0 0 0 0\n');(r/'cmdline').write_bytes(cmd.encode()+b'\0');(r/'cgroup').write_text('0::/synthetic')

def sample(tmp_path,**changes):
    root=tmp_path/'proc';root.mkdir(exist_ok=True)
    if not (root/'30').exists():peer(root,30,300,'python BASS_HE peer --token synthetic-private-value')
    raw=''.join(f'cpu{i} 10 0 10 80 0 0 0 0\n' for i in range(4))
    kw=dict(receipt_path=tmp_path/'census.json',proc_root=root,affinity_lookup=lambda p:set(range(64)),self_pid=10,run_pgid=100,allowed=set(range(64)),mem_available_bytes=20<<30,quota_cores=64,sharing_policy='COOPERATIVE_SHARED_HOST',proc_stat_reader=lambda:raw,sleep_fn=lambda _:None,sample_interval=0.)
    kw.update(changes);return live_resource_census([0,1,2,3],4,1<<30,**kw)

def test_cooperative_peer_telemetry_never_mutates_peer(tmp_path,monkeypatch):
    def trap(*a,**k):raise AssertionError('peer mutation')
    for name in ('kill','killpg','sched_setaffinity','setpriority'):monkeypatch.setattr(os,name,trap)
    r=sample(tmp_path)
    assert r['status']=='PASS_SHARED_HOST_PEERS_PRESENT' and r['external_peer_pids']==[30]
    assert r['cpu_pressure']['approved_cpu_mean_busy']==0.
    assert 'synthetic-private-value' not in (tmp_path/'census.json').read_text()

@pytest.mark.parametrize('bad',['allowed','quota','RAM'])
def test_cooperative_hard_gates_still_block(tmp_path,bad):
    kw={'allowed':{0}} if bad=='allowed' else {'quota_cores':2} if bad=='quota' else {'mem_available_bytes':1<<30}
    with pytest.raises(ValueError):sample(tmp_path,**kw)
    assert (tmp_path/'census.json').is_file()

def test_own_worker_leak_distinct_from_external_peer(tmp_path):
    root=tmp_path/'proc';root.mkdir();peer(root,20,100,'python bass_cr worker')
    with pytest.raises(OwnPoolTeardownIncomplete):verify_prior_pool_teardown({20},run_pgid=100,receipt_path=tmp_path/'teardown.json',settle_seconds=0,proc_root=root,affinity_lookup=lambda p:{0,1})
    receipt=json.loads((tmp_path/'teardown.json').read_text());assert receipt['status']=='OWN_POOL_TEARDOWN_INCOMPLETE'
    assert receipt['lingering_workers'][0]['pgid']==100
