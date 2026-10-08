import numpy as np
import qualification_runtime as qr
import run_full_geometry_qualification as runner


def row(spec,bad=False):
    sign=np.sign(spec['dz_a0']);S=np.array([[1.,.1+sign*1e-4],[.1+sign*1e-4,1.]],complex)
    cross={k:np.array([[1.+(2e-8 if bad else 0.)]],complex) for k in qr.CROSS_KEYS}
    return {**spec,'full':{'S':S,'H':np.eye(2,dtype=complex),'D':np.array([[0.,.05],[.05,0.]],complex)},'cross':cross,
        'diagnostics':{'S_hermiticity_relative':0.,'H_hermiticity_relative':0.,'metric_ratio':.8}}


def test_failed_q24_candidate_refines_under_a_frozen_budget_without_changing_reference():
    calls=[]
    contract={'epsilon_z_a0':1e-4,'reference_orders':[32,40], 'candidate_orders':[24,32,40],
       'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8}}
    def ensure(specs):
        calls.extend(specs)
        return [row(s,bad=s['method']!='reference' and s.get('candidate_order',24)==24) for s in specs]
    got=runner.execute_geometry_policy(-2.,contract,1e-3,ensure)
    assert got['status']=='GEOMETRY_QUALIFIED'
    assert got['qualified_candidate_order']==32
    assert got['qualified_reference_order']==40
    assert [r['candidate_order'] for r in got['candidate_attempts']]==[24,32]
    assert sum(s['method']=='reference' for s in calls)==6
    assert len(calls)==12


def contract():
    return {'epsilon_z_a0':1e-4,'reference_orders':[32,40], 'candidate_orders':[24,32,40],
       'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8}}


def test_candidate_budget_exhaustion_is_separate_and_stops_later_geometries():
    calls=[]
    def ensure(specs):
        calls.extend(specs)
        return [row(s,bad=s['method']!='reference') for s in specs]
    seen=[]
    def execute(z):
        seen.append(z)
        return runner.execute_geometry_policy(z,contract(),1e-3,ensure)
    rows,first=runner.sequence_geometries([-2.,0.,2.],execute)
    assert first['kind']=='candidate'
    assert rows[0]['status']=='CANDIDATE_CONVERGENCE_UNRESOLVED'
    assert seen==[-2.]
    assert [a['candidate_order'] for a in rows[0]['candidate_attempts']]==[24,32,40]
    assert rows[0]['capture_execution_allowed'] is False


def test_candidate_order_is_part_of_task_identity():
    context={'x':1}
    a=qr.task_identity('candidate',-2.,0.,context,candidate_order=32)
    b=qr.task_identity('candidate',-2.,0.,context,candidate_order=40)
    assert a!=b
    assert a!=qr.task_identity('phase24',-2.,0.,context)


def test_nonfinite_candidate_is_never_silently_accepted():
    import pytest
    specs=runner.candidate_task_specs(-2.,contract())
    rows=[row(s) for s in specs]
    rows[0]['cross']['D_tp'][0,0]=np.nan
    with pytest.raises(ValueError,match='nonfinite'):
        qr._connection_receipt(rows,1e-3,contract()['screens'])


def test_duplicate_or_asymmetric_stencil_is_rejected():
    import pytest
    rows=[row(s) for s in runner.candidate_task_specs(-2.,contract())]
    rows[0]['dz_a0']=0.
    with pytest.raises(ValueError,match='stencil'):
        qr._connection_receipt(rows,1e-3,contract()['screens'])


def test_zero_reference_cannot_hide_a_nonzero_raw_block():
    import pytest
    with pytest.raises(ValueError,match='zero reference'):
        qr._relative(np.ones((1,1)),np.zeros((1,1)))


def test_cli_import_and_resume_are_mutually_exclusive():
    import pytest
    parser=runner.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(['--out','x','--native-build','y','--import-from','old','--resume-from','new'])
