import copy
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tail_plan_adapter as t

FIXTURE=Path(__file__).resolve().parents[1]/'fixtures/R4P0'

def data():
    return (json.loads((FIXTURE/'receipts/R4P0_TAIL_PREFLIGHT_CONTRACT.json').read_text()),
            json.loads((FIXTURE/'inputs/SCIENCE_CONTEXT.json').read_text()))

def test_binding_implements_signed_eight_plan():
    assert hasattr(t,'bind_runtime_plan'), 'missing exact runtime-plan binding'
    tail,old=data();p=t.bind_runtime_plan(tail,old)
    assert [r['z_a0'] for r in p['queries']]==[-16.,16.,-20.,20.,-24.,24.,-32.,32.]
    assert len(p['queries'])==8 and p['max_raw_operator_evaluations']==88
    assert len({r['runtime_query_id'] for r in p['queries']})==8
    assert p['context_id'] != old['context_id']
    assert not p['native_authorized']
    for r,s in zip(p['queries'],tail['samples']):
        assert r['time_hex']==s['time_hex'] and r['plan_query_id']==s['query_id']
        assert r['runtime_query_id'] != s['query_id']
        assert r['runtime_query_id']==t.runtime_query_id(p['context_id'],r['time_hex'])

@pytest.mark.parametrize('mutation',['higher_l','time','duplicate','gate','count','native'])
def test_corrupted_plan_is_rejected(mutation):
    a,c=data()
    if mutation=='higher_l':a['radial_spec']['lmax']=2
    if mutation=='time':a['samples'][0]['time_hex']=float(1).hex()
    if mutation=='duplicate':a['samples'][1]=copy.deepcopy(a['samples'][0])
    if mutation=='gate':a['qualification_screens']['raw_cross_relative_max']=1e-4
    if mutation=='count':a['maximum_future_raw_attempts']=96
    if mutation=='native':a['new_native_samples_authorized']=True
    with pytest.raises(ValueError):t.bind_runtime_plan(a,c)

def test_bound_plan_qualification_scope_does_not_claim_derivative_or_transport():
    p=t.bind_runtime_plan(*data())
    assert set(p['active_screens'])=={'raw_cross_relative_max','operator_hermiticity_relative_max','metric_min_ratio'}
    assert p['independent_metric_derivative_validation'] is False
    assert p['temporal_gate_inherited'] is False
    assert p['tail_error_bound_certified'] is False

def test_no_hardcoded_z12_in_snapshot_diagnostics():
    p=t.bind_runtime_plan(*data()); row=p['queries'][3]
    S=np.eye(18,dtype=complex);H=np.diag(np.arange(18)).astype(complex);D=np.zeros((18,18),complex)
    H[0,9]=H[9,0]=.03
    m=t.snapshot_diagnostics(S,H,D,row)
    assert m['z_a0']==20. and m['time_hex']==row['time_hex']
    assert m['R_a0']==row['R_a0']
    assert m['K_tp_2norm']==pytest.approx(.03)
    assert m['rho_per_atomic_time']==pytest.approx(.03)
    assert m['Pdot_at_this_tail_sample'] is None
    assert not m['tail_error_bound_certified']

def test_no_time_averaging_or_positive_negative_inference():
    p=t.bind_runtime_plan(*data())
    assert p['positive_negative_reuse_allowed'] is False
    assert p['interpolation_allowed'] is False
    assert p['baseline_new_evaluation_allowed'] is False
