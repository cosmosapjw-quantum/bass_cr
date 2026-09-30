import copy
import json
import time
from pathlib import Path
from concurrent.futures import Future,ThreadPoolExecutor
import numpy as np
import pytest
import static_tail as s
from tail_plan_adapter import bind_runtime_plan,snapshot_diagnostics
from parallel_bridge import GlobalBudget,PlannedQuery,BudgetExceeded,MigrationCancelled
import worker_runtime
from bootstrap_tail import HERE

def plan():
    f=HERE/'fixtures/R4P0'
    return bind_runtime_plan(json.loads((f/'receipts/R4P0_TAIL_PREFLIGHT_CONTRACT.json').read_text()),json.loads((f/'inputs/SCIENCE_CONTEXT.json').read_text()))

def proposal():
    return {'execution_commit':'a'*40,'execution_tree':'b'*40,'source_pins_sha256':'c'*64,'query_plan_sha256':'d'*64,'binding_inputs_sha256':'e'*64,'authorization_id':'R4P0-TEST-STATIC-ONLY-A1','resource_sharing_policy':'COOPERATIVE_SHARED_HOST','workers':4,'hard_max_workers':8,'approved_cpu_list':[0,1,2,3],'worker_ram_bytes':1073741824,'total_worker_ram_cap_bytes':4294967296,'minimum_live_available_bytes':8589934592,'raw_operator_evaluation_cap':88,'operator_query_count':8,'wall_seconds':3600,'deadline_unix':time.time()+3600,'termination_grace_seconds':60,'cost_scope':'unapproved synthetic fixture only','native_parity':'NONE','derivative_fd_queries':0,'pilot_queries':0,'transport':False,'numerical_threads':1}

@pytest.mark.parametrize('bad',['approval','consumed','source','plan','basis','workers','raw','parity','fd','transport','deadline','ID'])
def test_authority_rejects_before_native_factory(bad):
    p=proposal();a={k:p[k] for k in ['execution_commit','execution_tree','source_pins_sha256','query_plan_sha256','binding_inputs_sha256']};approved=True;unused=True
    if bad=='approval':approved=False
    if bad=='consumed':unused=False
    if bad=='source':p['source_pins_sha256']='f'*64
    if bad=='plan':p['query_plan_sha256']='f'*64
    if bad=='basis':p['binding_inputs_sha256']='f'*64
    if bad=='workers':p['workers']=32
    if bad=='raw':p['raw_operator_evaluation_cap']=99
    if bad=='parity':p['native_parity']='TWO_QUERIES'
    if bad=='fd':p['derivative_fd_queries']=2
    if bad=='transport':p['transport']=True
    if bad=='deadline':p['deadline_unix']=time.time()-1
    if bad=='ID':p['authorization_id']='R4G-N1536-ADAPTIVE-SHARED-RESUME-20260930-A3'
    calls=[]
    with pytest.raises((ValueError,PermissionError)):
        s.validate_scope(p,a,approved=approved,unused=unused)
        calls.append('native factory')
    assert calls==[]

def test_exact8_runtime_items():
    p=plan();items=s.exact_items(p)
    assert len(items)==8
    assert [x.time_hex for x in items]==[r['time_hex'] for r in p['queries']]
    assert [x.query_id for x in items]==[r['runtime_query_id'] for r in p['queries']]
    assert not {x.query_id for x in items}.intersection(r['plan_query_id'] for r in p['queries'])
    bad=copy.deepcopy(p);bad['queries'][0]['time_hex']=float(1).hex()
    with pytest.raises(ValueError):s.exact_items(bad)

def evaluator(t,order,subdivisions):
    S=np.eye(18,dtype=complex);H=np.diag(np.arange(1,19)).astype(complex);D=np.zeros_like(S)
    H[:9,9:]=.01;H[9:,:9]=.01
    raw={k:np.ones((9,9),complex)*.01 for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')}
    return raw,{'S':S,'H':H,'D':D}

def test_synthetic_existing_worker_provider_to_durable_diagnostics(tmp_path,monkeypatch):
    p=plan();budget=GlobalBudget.create(tmp_path/'budget',parent_attempts=0,maximum=88,deadline_unix=time.time()+30)
    tasks=tmp_path/'tasks';tasks.mkdir()
    contract=json.loads((HERE/'fixtures/R4P0/inputs/SCIENCE_CONTEXT.json').read_text())['context']['contract'];contract['screens']=p['active_screens']
    monkeypatch.setattr(worker_runtime,'_STATE',{'evaluator':evaluator,'contract':contract,'context_id':p['context_id'],'budget':budget,'tasks_dir':tasks,'native':{'synthetic':True,'native_loaded':False}})
    with ThreadPoolExecutor(max_workers=2) as pool:
        audit=s.execute_plan(p,tmp_path/'out',budget,pool,worker_runtime.compute_query,2)
    assert audit['completed_queries']==8 and budget.used()==16
    assert len(list((tmp_path/'out/runtime_queries').glob('*.json')))==8
    assert len(list((tmp_path/'out/runtime_queries').glob('*.npz')))==8
    for row in p['queries']:
        d=json.loads((tmp_path/'out/diagnostics'/ (row['runtime_query_id']+'.json')).read_text())
        assert d['z_a0']==row['z_a0'] and d['R_a0']==row['R_a0'] and d['time_hex']==row['time_hex']
        assert d['P_selected_at_this_tail_sample'] is None and d['Pdot_at_this_tail_sample'] is None
        assert not d['independent_metric_derivative_validation'] and not d['tail_error_bound_certified']
    assert set(audit['static_screens_executed'])=={'raw_cross_relative_max','operator_hermiticity_relative_max','metric_min_ratio'}
    assert audit['independent_derivative_screen_executed'] is False

def test_unapproved_proposal_shape_can_be_valid_but_is_not_approval():
    p=proposal();a={k:p[k] for k in ['execution_commit','execution_tree','source_pins_sha256','query_plan_sha256','binding_inputs_sha256']}
    assert s.validate_scope(p,a,approved=True)==p
    with pytest.raises(PermissionError):s.validate_scope(p,a,approved=False)

@pytest.mark.parametrize('bad',['no_approval','wrong_proposal_sha','wrong_source_pin','consumed_ID'])
def test_real_request_native_factory_zero_before_invalid_admission(tmp_path,monkeypatch,bad):
    p=proposal();pins={'execution_commit':p['execution_commit'],'execution_tree':p['execution_tree'],'source_files':{}}
    pinfile=tmp_path/'pins.json';pinfile.write_text(json.dumps(pins));p['source_pins_sha256']=s.sha(pinfile)
    p['query_plan_sha256']=s.sha(HERE/'BOUND_B0_TAIL_QUERY_PLAN.json');p['binding_inputs_sha256']=s.sha(HERE/'BINDING_INPUTS.json')
    if bad=='wrong_source_pin':p['source_pins_sha256']='0'*64
    if bad=='consumed_ID':p['authorization_id']='R4G-N1536-ADAPTIVE-SHARED-RESUME-20260930-A3'
    path=tmp_path/'proposal.json';path.write_text(json.dumps(p));calls=[]
    def factory(*a,**k):calls.append('native');raise AssertionError('native factory crossed')
    monkeypatch.setenv('ALLOW_NEW_NATIVE_R4P0',s.APPROVAL if bad!='no_approval' else '')
    approved='0'*64 if bad=='wrong_proposal_sha' else s.sha(path)
    with pytest.raises((ValueError,PermissionError)):
        s.request(path,pinfile,tmp_path/'inputs',tmp_path/'build',tmp_path/'out',approved_sha=approved,pool_factory=factory)
    assert calls==[] and not (tmp_path/'out').exists()

def test_worker_whitelist_rejects_unexpected_time_before_existing_worker(monkeypatch):
    import tail_worker
    items=s.exact_items(plan());monkeypatch.setattr(tail_worker,'_STATE_ITEMS',{i.query_id:i for i in items});calls=[]
    monkeypatch.setattr(worker_runtime,'compute_query',lambda *a:calls.append(a))
    with pytest.raises(ValueError):tail_worker.compute(PlannedQuery(items[0].query_id,float(1).hex(),None,None))
    assert not calls

class ImmediateExecutor:
    def __init__(self,fail=False):self.calls=[];self.fail=fail
    def submit(self,fn,item):
        self.calls.append(item);future=Future()
        if self.fail:future.set_exception(RuntimeError('synthetic worker failure'))
        else:future.set_result(fn(item))
        return future

def test_failure_and_deadline_stop_additional_dispatch(tmp_path):
    p=plan();b=GlobalBudget.create(tmp_path/'budget',parent_attempts=0,maximum=88,deadline_unix=time.time()+30);pool=ImmediateExecutor(fail=True)
    with pytest.raises(RuntimeError,match='synthetic worker failure'):s.execute_plan(p,tmp_path/'failure',b,pool,None,1)
    assert len(pool.calls)==1 and (b.root/'CANCELLED.json').is_file()
    assert json.loads((tmp_path/'failure/FIRST_FAILURE.json').read_text())['type']=='RuntimeError'
    b2=GlobalBudget.create(tmp_path/'expired',parent_attempts=0,maximum=88,deadline_unix=time.time()-1);pool2=ImmediateExecutor()
    with pytest.raises(MigrationCancelled):s.execute_plan(p,tmp_path/'timeout',b2,pool2,None,1)
    assert not pool2.calls and b2.used()==0

def test_88_global_durable_reservations_are_atomic(tmp_path):
    b=GlobalBudget.create(tmp_path/'budget',parent_attempts=0,maximum=88,deadline_unix=time.time()+30)
    def reserve(_):
        try:return GlobalBudget(b.root).reserve('synthetic',32,1)
        except BudgetExceeded:return None
    with ThreadPoolExecutor(max_workers=8) as pool:values=list(pool.map(reserve,range(100)))
    assert sorted(v for v in values if v is not None)==list(range(1,89))
    assert b.used()==88 and len((b.root/'RESERVATIONS.jsonl').read_text().splitlines())==88

def test_diagnostic_failure_preserves_qualified_pair_and_first_failure(tmp_path,monkeypatch):
    p=plan();budget=GlobalBudget.create(tmp_path/'budget',parent_attempts=0,maximum=88,deadline_unix=time.time()+30);tasks=tmp_path/'tasks';tasks.mkdir()
    contract=json.loads((HERE/'fixtures/R4P0/inputs/SCIENCE_CONTEXT.json').read_text())['context']['contract'];contract['screens']=p['active_screens']
    monkeypatch.setattr(worker_runtime,'_STATE',{'evaluator':evaluator,'contract':contract,'context_id':p['context_id'],'budget':budget,'tasks_dir':tasks,'native':{'synthetic':True}})
    def fail(*a,**k):raise ValueError('synthetic diagnostic failure')
    monkeypatch.setattr(s,'snapshot_diagnostics',fail);pool=ImmediateExecutor()
    with pytest.raises(ValueError,match='synthetic diagnostic failure'):s.execute_plan(p,tmp_path/'out',budget,pool,worker_runtime.compute_query,1)
    assert len(pool.calls)==1 and budget.used()==2
    assert len(list((tmp_path/'out/runtime_queries').glob('*.npz')))==1
    assert len(list((tmp_path/'out/runtime_queries').glob('*.json')))==1
    assert 'synthetic diagnostic failure' in (tmp_path/'out/FIRST_FAILURE.json').read_text()

def test_qualification_failure_is_not_relaxed_or_fallback(tmp_path,monkeypatch):
    p=plan();budget=GlobalBudget.create(tmp_path/'budget',parent_attempts=0,maximum=88,deadline_unix=time.time()+30);tasks=tmp_path/'tasks';tasks.mkdir()
    contract=json.loads((HERE/'fixtures/R4P0/inputs/SCIENCE_CONTEXT.json').read_text())['context']['contract'];contract['screens']=p['active_screens']
    def unstable(t,q,h):
        raw,full=evaluator(t,q,h)
        return {k:a*q*h for k,a in raw.items()},full
    monkeypatch.setattr(worker_runtime,'_STATE',{'evaluator':unstable,'contract':contract,'context_id':p['context_id'],'budget':budget,'tasks_dir':tasks,'native':{'synthetic':True}})
    pool=ImmediateExecutor()
    with pytest.raises(Exception):s.execute_plan(p,tmp_path/'out',budget,pool,worker_runtime.compute_query,1)
    assert len(pool.calls)==1 and budget.used()==11
    assert list(tasks.glob('*/TASK_FAILURE.json'))
    assert not list((tmp_path/'out/runtime_queries').glob('*.json'))
    assert contract['screens']['raw_cross_relative_max']==1e-9
