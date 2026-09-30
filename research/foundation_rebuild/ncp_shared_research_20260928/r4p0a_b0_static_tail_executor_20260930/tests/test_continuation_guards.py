"""Bounded continuation regressions. All evaluator calls are synthetic."""
import copy
import ctypes
import json
import os
from pathlib import Path
import shutil
import stat
import time

import numpy as np
import pytest
import static_tail as s
import tail_worker
import worker_runtime
from parallel_bridge import GlobalBudget
from test_static_binding import evaluator, proposal, ImmediateExecutor
from bootstrap_tail import HERE


def synthetic(tmp_path, monkeypatch, maximum=88, parent=0):
    plan=s.binding_plan()
    budget=GlobalBudget.create(tmp_path/'budget',parent_attempts=parent,
        maximum=maximum,deadline_unix=time.time()+30)
    contract=json.loads((HERE/'fixtures/R4P0/inputs/SCIENCE_CONTEXT.json').read_text())['context']['contract']
    contract['screens']=plan['active_screens']
    tasks=tmp_path/'tasks';tasks.mkdir()
    monkeypatch.setattr(worker_runtime,'_STATE',dict(evaluator=evaluator,contract=contract,
        context_id=plan['context_id'],budget=budget,tasks_dir=tasks,native={'synthetic':True}))
    return plan,budget,ImmediateExecutor()


@pytest.mark.parametrize('maximum,parent,inflight',[(89,0,1),(87,0,1),(88,1,1),(88,0,9),(88,0,True)])
def test_dispatch_rejects_noncanonical_budget_or_workers(tmp_path,monkeypatch,maximum,parent,inflight):
    plan,budget,pool=synthetic(tmp_path,monkeypatch,maximum,parent)
    with pytest.raises(ValueError,match='static-tail budget/worker'):
        s.execute_plan(plan,tmp_path/'out',budget,pool,worker_runtime.compute_query,inflight)
    assert pool.calls==[] and budget.reservations()==0
    assert (tmp_path/'out/FIRST_FAILURE.json').is_file()


def test_worker_rejects_wrong_global_budget_before_native_initializer(tmp_path,monkeypatch):
    plan,budget,pool=synthetic(tmp_path,monkeypatch,maximum=89)
    monkeypatch.setattr(tail_worker,'verify_source',lambda *_:None)
    monkeypatch.setattr(tail_worker,'verify_inputs',lambda *_:({},plan,{}))
    calls=[]
    monkeypatch.setattr(worker_runtime,'initialize_worker',lambda *a:calls.append(a))
    with pytest.raises(ValueError,match='static-tail budget/worker'):
        tail_worker.initialize('inputs','build',{},str(tmp_path/'out'),str(budget.root),[0],1<<30)
    assert calls==[]


def test_publication_conflict_stops_before_dispatch_and_preserves_bytes(tmp_path,monkeypatch):
    plan,budget,pool=synthetic(tmp_path,monkeypatch)
    first=plan['queries'][0]['runtime_query_id']
    path=tmp_path/'out/runtime_queries'/(first+'.json')
    path.parent.mkdir(parents=True);path.write_bytes(b'preserve previous evidence\n')
    with pytest.raises(FileExistsError):
        s.execute_plan(plan,tmp_path/'out',budget,pool,worker_runtime.compute_query,1)
    assert path.read_bytes()==b'preserve previous evidence\n'
    assert pool.calls==[] and budget.used()==0


def test_new_json_fsyncs_parent_directory(tmp_path,monkeypatch):
    real=os.fsync;seen=[]
    def observe(fd):
        seen.append(stat.S_ISDIR(os.fstat(fd).st_mode));return real(fd)
    monkeypatch.setattr(os,'fsync',observe)
    s.write_new(tmp_path/'evidence'/'record.json',{'value':1})
    assert seen==[False,True]
    with pytest.raises(FileExistsError):s.write_new(tmp_path/'evidence'/'record.json',{'value':2})
    assert json.loads((tmp_path/'evidence/record.json').read_text())=={'value':1}


def test_each_signed_sample_has_explicit_unavailable_state_status(tmp_path,monkeypatch):
    plan,budget,pool=synthetic(tmp_path,monkeypatch)
    calls=[]
    def signed(t,q,h):
        calls.append(float(t).hex());raw,full=evaluator(t,q,h)
        scale=1.0 if t<0 else 2.0
        return {k:v*scale for k,v in raw.items()},{**full,'H':full['H']*scale}
    monkeypatch.setitem(worker_runtime._STATE,'evaluator',signed)
    audit=s.execute_plan(plan,tmp_path/'out',budget,pool,worker_runtime.compute_query,1)
    rows=[json.loads((tmp_path/'out/diagnostics'/(r['runtime_query_id']+'.json')).read_text()) for r in plan['queries']]
    assert all(d.get('P_selected_status')=='unavailable_without_state' and d.get('Pdot_status')=='unavailable_without_state' for d in rows)
    assert set(calls)=={r['time_hex'] for r in plan['queries']} and len(calls)==16
    assert len({r['runtime_query_id'] for r in plan['queries']})==8
    assert all(d['rho_per_atomic_time']>=0 and np.isfinite(d['rho_per_atomic_time']) for d in rows)
    assert audit['completed_queries']==8
    for i in range(0,8,2):
        assert rows[i+1]['rho_per_atomic_time']==pytest.approx(2*rows[i]['rho_per_atomic_time'])


def test_real_consumed_authorization_file_blocks_request_before_source_or_native(tmp_path,monkeypatch):
    monkeypatch.setenv('HOME',str(tmp_path/'home'))
    p=proposal();pins={'execution_commit':p['execution_commit'],'execution_tree':p['execution_tree'],'source_files':{}}
    pinfile=tmp_path/'pins.json';pinfile.write_text(json.dumps(pins))
    p.update(source_pins_sha256=s.sha(pinfile),query_plan_sha256=s.sha(HERE/'BOUND_B0_TAIL_QUERY_PLAN.json'),binding_inputs_sha256=s.sha(HERE/'BINDING_INPUTS.json'))
    nonce=Path.home()/'.local/state/bass_r4c/authorizations'/(p['authorization_id']+'.json')
    nonce.parent.mkdir(parents=True);nonce.write_text('{"synthetic_preexisting_receipt":true}\n')
    saved=nonce.read_bytes();pp=tmp_path/'proposal.json';pp.write_text(json.dumps(p))
    monkeypatch.setenv('ALLOW_NEW_NATIVE_R4P0',s.APPROVAL)
    def forbidden(*a,**k):raise AssertionError('source/native boundary crossed')
    monkeypatch.setattr(s,'verify_source',forbidden)
    with pytest.raises(PermissionError,match='already consumed'):
        s.request(pp,pinfile,tmp_path/'inputs',tmp_path/'build',tmp_path/'out',approved_sha=s.sha(pp),pool_factory=forbidden)
    assert nonce.read_bytes()==saved and not (tmp_path/'out').exists()


@pytest.mark.parametrize('name',['BASIS.npz','BASIS.json','SCIENCE_CONTEXT.json','BUILD.json','libmoments.so','plan'])
def test_mutated_frozen_input_rejected_without_dlopen(tmp_path,monkeypatch,name):
    inp=Path(os.environ['R4P0A_RUNTIME_INPUTS']);build=Path(os.environ['R4P0A_NATIVE_BUILD'])
    shutil.copytree(inp,tmp_path/'inputs');shutil.copytree(build,tmp_path/'build')
    calls=[]
    def forbidden(*a,**k):calls.append(a);raise AssertionError('dlopen prohibited')
    monkeypatch.setattr(ctypes,'CDLL',forbidden)
    if name=='plan':
        p=copy.deepcopy(s.binding_plan());p['queries'][0]['z_a0']=-17
        monkeypatch.setattr(s,'binding_plan',lambda:p)
    else:
        path=tmp_path/('build' if name in ('BUILD.json','libmoments.so') else 'inputs')/name
        path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises(ValueError):s.verify_inputs(tmp_path/'inputs',tmp_path/'build')
    assert calls==[]


def test_wrong_source_bytes_and_ninth_query_rejected(tmp_path):
    f=tmp_path/'source.py';f.write_text('original\n')
    pins={'source_files':{'source.py':s.sha(f)}};f.write_text('changed\n')
    with pytest.raises(ValueError,match='pinned source mismatch'):s.verify_source(pins,tmp_path)
    p=copy.deepcopy(s.binding_plan());p['queries'].append(copy.deepcopy(p['queries'][0]))
    with pytest.raises(ValueError,match='exact frozen eight'):s.exact_items(p)


def test_resource_policy_has_explicit_machine_pin():
    path=HERE/'RESOURCE_POLICY.json'
    assert path.is_file(), 'machine-readable resource policy required'
    policy=json.loads(path.read_text())
    assert policy['policy']=='COOPERATIVE_SHARED_HOST'
    assert (policy['preferred_workers'],policy['maximum_workers'],policy['numerical_threads'])==(4,8,1)
    assert policy['global_raw_attempt_cap']==88 and policy['mutate_other_jobs'] is False


def test_wrong_resource_policy_pin_rejected_before_source(tmp_path,monkeypatch):
    p=proposal();pins={'execution_commit':p['execution_commit'],'execution_tree':p['execution_tree'],'source_files':{}}
    pinfile=tmp_path/'pins.json';pinfile.write_text(json.dumps(pins))
    p.update(source_pins_sha256=s.sha(pinfile),query_plan_sha256=s.sha(HERE/'BOUND_B0_TAIL_QUERY_PLAN.json'),binding_inputs_sha256=s.sha(HERE/'BINDING_INPUTS.json'),resource_policy_sha256='0'*64)
    pp=tmp_path/'proposal.json';pp.write_text(json.dumps(p))
    monkeypatch.setenv('ALLOW_NEW_NATIVE_R4P0',s.APPROVAL)
    def forbidden(*a,**k):raise AssertionError('source/native boundary crossed')
    monkeypatch.setattr(s,'verify_source',forbidden)
    with pytest.raises(ValueError,match='approved resource policy pin mismatch'):
        s.request(pp,pinfile,tmp_path/'inputs',tmp_path/'build',tmp_path/'out',approved_sha=s.sha(pp),pool_factory=forbidden)
