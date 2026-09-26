import numpy as np
import qualification_runtime as runtime


def _row(method, order, dz, *, connection_good=True, cross_shift=0.0):
    eps_t=1e-3
    sign={-1e-4:-1.,0.:0.,1e-4:1.}[dz]
    S=np.array([[1., .1+sign*eps_t*.1],[.1+sign*eps_t*.1,1.]],complex)
    H=np.array([[.4,.03],[.03,.8]],complex)
    D=np.array([[0.,.05],[.05,0.]],complex) if connection_good else np.zeros((2,2),complex)
    cross={k:np.array([[1.+cross_shift+0j]]) for k in runtime.CROSS_KEYS}
    return {'method':method,'reference_order':order,'dz_a0':dz,
            'full':{'S':S,'H':H,'D':D},'cross':cross,
            'diagnostics':{'S_hermiticity_relative':0.,'H_hermiticity_relative':0.,'metric_ratio':.8}}


def test_reference_ladder_skips_unconverged_q32_and_qualifies_q48():
    rows=[]
    # q32 fails its own connection and is far from q40.
    for dz in (-1e-4,0.,1e-4): rows.append(_row('reference',32,dz,connection_good=False,cross_shift=5e-5))
    # q40 and q48 both pass connection and agree under raw-cross screen.
    for dz in (-1e-4,0.,1e-4): rows.append(_row('reference',40,dz,connection_good=True,cross_shift=3e-10))
    for dz in (-1e-4,0.,1e-4): rows.append(_row('reference',48,dz,connection_good=True,cross_shift=0.0))
    contract={'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,
                         'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
              'reference_orders':[32,40,48,56,64]}
    result=runtime.qualify_reference_ladder(rows,1e-3,contract)
    assert result['status']=='REFERENCE_QUALIFIED'
    assert result['qualified_order']==48
    assert result['attempted_orders']==[32,40,48]
    assert result['orders']['32']['connection_pass'] is False
    assert result['orders']['40']['connection_pass'] is True
    assert result['orders']['48']['previous_raw_cross_relative_max']<1e-9


def test_reference_ladder_exhaustion_is_not_candidate_failure():
    rows=[]
    for order in (32,40,48,56,64):
        for dz in (-1e-4,0.,1e-4): rows.append(_row('reference',order,dz,connection_good=True,cross_shift=order*1e-4))
    contract={'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,
                         'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
              'reference_orders':[32,40,48,56,64]}
    result=runtime.qualify_reference_ladder(rows,1e-3,contract)
    assert result['status']=='REFERENCE_CONVERGENCE_UNRESOLVED'
    assert result['qualified_order'] is None
    assert result['candidate_evaluated'] is False


def test_candidate_is_only_judged_after_qualified_reference():
    eps_t=1e-3
    candidate=[];reference=[]
    for dz in (-1e-4,0.,1e-4):
        candidate.append(_row('phase24',None,dz,connection_good=True,cross_shift=0.0))
        reference.append(_row('reference',48,dz,connection_good=True,cross_shift=2e-11))
    contract={'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,
                         'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8}}
    r=runtime.qualify_candidate_against_reference(-4.,candidate,reference,eps_t,contract,48)
    assert r['status']=='GEOMETRY_QUALIFIED'
    assert r['qualified_reference_order']==48
    assert r['candidate']['connection_pass'] is True
    assert r['candidate_vs_reference']['max_raw_cross_relative_difference']<1e-9


def test_reference_task_identity_binds_quadrature_order():
    c={'basis':'abc','backend':'native'}
    a=runtime.task_identity('reference',-4.,0.,c,reference_order=32)
    b=runtime.task_identity('reference',-4.,0.,c,reference_order=40)
    assert a!=b
    assert a==runtime.task_identity('reference',-4.,0.,c,reference_order=32)
