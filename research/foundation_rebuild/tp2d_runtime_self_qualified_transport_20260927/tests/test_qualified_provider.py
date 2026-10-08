import numpy as np
import pytest
from qualified_provider import ResolutionQualifiedProvider, ResolutionQualificationError, OperatorQueryBudgetExceeded, restore_query_store

CROSS_KEYS=('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')

def packet(scale, *, metric_ratio=0.9, herm=0.0):
    raw={k: np.array([[scale]], complex) for k in CROSS_KEYS}
    S=np.diag([metric_ratio,1.0]).astype(complex)
    H=np.array([[1.0,0.0],[0.0,2.0]],complex)
    if herm:
        H[0,1]=herm
    D=np.zeros((2,2),complex)
    full={'S':S,'H':H,'D':D,'diagnostics':{'metric_ratio':metric_ratio}}
    return raw,full


def test_selects_first_converged_adjacent_pair_and_exact_time_cache(tmp_path):
    calls=[]
    values={(32,1):1.0,(40,1):1.0+2e-12,(48,1):1.2}
    def evaluate(t,order,subdivisions):
        calls.append((float(t),order,subdivisions))
        return packet(values[(order,subdivisions)])
    p=ResolutionQualifiedProvider(
        evaluate=evaluate,
        resolutions=[{'order':32,'subdivisions':1},{'order':40,'subdivisions':1},{'order':48,'subdivisions':1}],
        screens={'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
        context_id='ctx',out_dir=tmp_path,max_unique_queries=4,
    )
    s=p.at(0.125)
    assert s.qualification['selected_resolution']=={'order':40,'subdivisions':1}
    assert s.qualification['lower_resolution']=={'order':32,'subdivisions':1}
    assert s.qualification['evidence_relation']=='INDEPENDENT_NUMERICAL_RESOLUTION_COMPARISON'
    assert len(calls)==2
    assert p.unique_query_count==1
    assert p.raw_operator_evaluation_count==2
    s2=p.at(0.125)
    assert s2 is s
    assert len(calls)==2
    receipts=list((tmp_path/'runtime_queries').glob('*.json'))
    payloads=list((tmp_path/'runtime_queries').glob('*.npz'))
    assert len(receipts)==len(payloads)==1


def test_escalates_then_raises_when_finite_ladder_exhausted(tmp_path):
    def evaluate(t,order,subdivisions):
        return packet({32:1.0,40:1.1,48:1.3}[order])
    p=ResolutionQualifiedProvider(
        evaluate=evaluate,
        resolutions=[{'order':32,'subdivisions':1},{'order':40,'subdivisions':1},{'order':48,'subdivisions':1}],
        screens={'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
        context_id='ctx',out_dir=tmp_path,max_unique_queries=4,
    )
    with pytest.raises(ResolutionQualificationError,match='finite resolution ladder exhausted'):
        p.at(0.25)
    assert p.unique_query_count==1
    assert p.raw_operator_evaluation_count==3


def test_operator_screen_failure_cannot_form_qualified_pair(tmp_path):
    def evaluate(t,order,subdivisions):
        if order==32:
            return packet(1.0,metric_ratio=1e-12)
        return packet(1.0+1e-12)
    p=ResolutionQualifiedProvider(
        evaluate=evaluate,
        resolutions=[{'order':32,'subdivisions':1},{'order':40,'subdivisions':1}],
        screens={'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
        context_id='ctx',out_dir=tmp_path,max_unique_queries=4,
    )
    with pytest.raises(ResolutionQualificationError):
        p.at(0.5)


def test_query_budget_blocks_before_new_evaluation(tmp_path):
    calls=[]
    def evaluate(t,order,subdivisions):
        calls.append((t,order,subdivisions));return packet(1.0 + order*1e-14)
    p=ResolutionQualifiedProvider(
        evaluate=evaluate,
        resolutions=[{'order':32,'subdivisions':1},{'order':40,'subdivisions':1}],
        screens={'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
        context_id='ctx',out_dir=tmp_path,max_unique_queries=1,
    )
    p.at(0.0)
    with pytest.raises(OperatorQueryBudgetExceeded):
        p.at(1.0)
    assert len(calls)==2


def test_resume_restore_copies_only_hash_valid_matching_context(tmp_path):
    from qualified_provider import restore_query_store
    src=tmp_path/'src';dst=tmp_path/'dst'
    def evaluate(t,order,subdivisions):
        return packet(1.0 + order*1e-14)
    p=ResolutionQualifiedProvider(
        evaluate=evaluate,resolutions=[{'order':32,'subdivisions':1},{'order':40,'subdivisions':1}],
        screens={'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
        context_id='ctx',out_dir=src,max_unique_queries=4)
    expected=p.at(0.75)
    assert restore_query_store(src,dst,'ctx')==1
    calls=[]
    def must_not_run(*args):
        calls.append(args);raise AssertionError('restored query unexpectedly recomputed')
    q=ResolutionQualifiedProvider(
        evaluate=must_not_run,resolutions=[{'order':32,'subdivisions':1},{'order':40,'subdivisions':1}],
        screens={'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
        context_id='ctx',out_dir=dst,max_unique_queries=4)
    got=q.at(0.75)
    assert got.qualification==expected.qualification
    assert q.restored_query_reads==1
    assert calls==[]


def test_audit_summary_reports_only_qualified_runtime_queries(tmp_path):
    def evaluate(t,order,subdivisions):
        return packet(1.0 + (order+abs(t))*1e-14)
    p=ResolutionQualifiedProvider(
        evaluate=evaluate,resolutions=[{'order':32,'subdivisions':1},{'order':40,'subdivisions':1}],
        screens={'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
        context_id='ctx',out_dir=tmp_path,max_unique_queries=4)
    p.at(-1.0);p.at(1.0);p.at(-1.0)
    s=p.audit_summary()
    assert s['all_runtime_operator_queries_qualified'] is True
    assert s['unique_runtime_queries']==2
    assert s['raw_operator_evaluations']==4
    assert s['cache_hits']==1
    assert s['resolution_histogram']=={'q40_h1':2}
    assert s['continuous_global_supremum_bound'] is False


def test_provider_emits_progress_for_new_and_restored_qualified_queries(tmp_path):
    events=[]
    def evaluate(t,order,subdivisions): return packet(1.0+order*1e-14)
    p=ResolutionQualifiedProvider(
        evaluate=evaluate,resolutions=[{'order':32,'subdivisions':1},{'order':40,'subdivisions':1}],
        screens={'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
        context_id='ctx',out_dir=tmp_path/'a',max_unique_queries=4,on_qualified=events.append)
    p.at(0.2)
    assert events[-1]['event']=='runtime_query_qualified'
    assert events[-1]['restored'] is False
    assert events[-1]['selected_resolution']=={'order':40,'subdivisions':1}
    restore_query_store(tmp_path/'a',tmp_path/'b','ctx')
    q=ResolutionQualifiedProvider(
        evaluate=lambda *a: (_ for _ in ()).throw(AssertionError('should restore')),
        resolutions=[{'order':32,'subdivisions':1},{'order':40,'subdivisions':1}],
        screens={'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
        context_id='ctx',out_dir=tmp_path/'b',max_unique_queries=4,on_qualified=events.append)
    q.at(0.2)
    assert events[-1]['restored'] is True
