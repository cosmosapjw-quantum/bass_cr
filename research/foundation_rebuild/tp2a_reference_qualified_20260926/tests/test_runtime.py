from pathlib import Path
import json
import numpy as np
import pytest
import qualification_runtime as runtime


def _payload(scale=1.0):
    S=np.array([[1.,0.1],[0.1,1.]],complex)
    H=np.array([[.4,.03],[.03,.8]],complex)
    D=np.array([[0.,.05],[-.05,0.]],complex)*scale
    cross={k:np.array([[scale+0j]]) for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')}
    return {'full':{'S':S,'H':H,'D':D},'cross':cross,
            'diagnostics':{'S_hermiticity_relative':0.,'H_hermiticity_relative':0.,'metric_ratio':.8}}


def test_task_identity_is_exact_context_and_float_bound():
    c={'basis':'abc','backend':'native'}
    a=runtime.task_identity('phase24',-4.,-1e-4,c)
    assert a==runtime.task_identity('phase24',-4.,-1e-4,c)
    assert a!=runtime.task_identity('phase24',-4.,1e-4,c)
    assert a!=runtime.task_identity('reference',-4.,-1e-4,c,reference_order=32)
    assert a!=runtime.task_identity('phase24',-4.,-1e-4,{**c,'basis':'def'})


def test_checkpoint_roundtrip_and_corruption_rejection(tmp_path):
    identity=runtime.task_identity('phase24',-4.,0.,{'x':1})
    result={'task_id':identity,'context_id':'ctx','method':'phase24','z_center_a0':-4.,'dz_a0':0.,'channel_count':2,
            'diagnostics':_payload()['diagnostics'],'metadata':{'x':1}}
    runtime.save_task(tmp_path,result,_payload())
    got,arrays=runtime.load_task(tmp_path,identity,'ctx')
    assert got['task_id']==identity and arrays['S'].shape==(2,2)
    p=tmp_path/'tasks'/f'{identity}.npz';p.write_bytes(p.read_bytes()+b'x')
    with pytest.raises(ValueError,match='hash'):
        runtime.load_task(tmp_path,identity,'ctx')


def test_checkpoint_is_create_only(tmp_path):
    identity=runtime.task_identity('phase24',-4.,0.,{'x':1})
    result={'task_id':identity,'context_id':'ctx','method':'phase24','z_center_a0':-4.,'dz_a0':0.,'channel_count':2,
            'diagnostics':_payload()['diagnostics'],'metadata':{}}
    runtime.save_task(tmp_path,result,_payload())
    with pytest.raises(FileExistsError):
        runtime.save_task(tmp_path,result,_payload())


def test_geometry_receipt_calculates_connection_parity_and_screens():
    eps_t=1e-3
    rows=[]
    for method,offset in [('phase24',0.),('reference32',1e-12)]:
        for dz,ss in [(-1e-4,-1.),(0.,0.),(1e-4,1.)]:
            p=_payload(1.)
            p['full']['S']=np.array([[1.,.1+ss*eps_t*.1],[.1+ss*eps_t*.1,1.]],complex)
            p['full']['D']=np.array([[0.,.05],[.05,0.]],complex)
            for k in p['cross']: p['cross'][k]=p['cross'][k]+offset
            rows.append({'method':method,'dz_a0':dz,**p})
    c={'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,
                  'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8}}
    r=runtime.qualify_geometry_from_tasks(-4.,rows,eps_t,c)
    assert r['failed_screens']==[]
    assert r['connection_residuals']['phase24']<1e-12
    assert r['max_raw_cross_relative_difference']<1e-9


def test_geometry_receipt_fails_exact_screen_without_relaxation():
    eps_t=1e-3;rows=[]
    for method in ('phase24','reference32'):
        for dz,ss in [(-1e-4,-1.),(0.,0.),(1e-4,1.)]:
            p=_payload(1.)
            p['full']['S']=np.array([[1.,.1+ss*eps_t*.1],[.1+ss*eps_t*.1,1.]],complex)
            p['full']['D']=np.zeros((2,2),complex)
            rows.append({'method':method,'dz_a0':dz,**p})
    c={'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,
                  'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8}}
    r=runtime.qualify_geometry_from_tasks(-4.,rows,eps_t,c)
    assert 'phase24 connection' in r['failed_screens']
    assert 'reference32 connection' in r['failed_screens']


def test_restore_tasks_copies_only_exact_context(tmp_path):
    old=tmp_path/'old';new=tmp_path/'new';bad=tmp_path/'bad'
    identity=runtime.task_identity('phase24',-4.,0.,{'x':1})
    result={'task_id':identity,'context_id':'ctx','method':'phase24','z_center_a0':-4.,'dz_a0':0.,'channel_count':2,
            'diagnostics':_payload()['diagnostics'],'metadata':{}}
    runtime.save_task(old,result,_payload())
    assert runtime.restore_tasks(old,new,'ctx',{identity})==1
    got,_=runtime.load_task(new,identity,'ctx');assert got['task_id']==identity
    with pytest.raises(ValueError,match='context'):
        runtime.restore_tasks(old,bad,'different',{identity})
