import numpy as np
import policy_adapter as pa


def _row(family,order,subdivisions,dz,key,shift=0.):
    eps_t=1e-3;sign={-1e-4:-1.,0.:0.,1e-4:1.}[dz]
    S=np.array([[1.,.1+sign*eps_t*.1],[.1+sign*eps_t*.1,1.]],complex)
    H=np.array([[.4,.03],[.03,.8]],complex);D=np.array([[0.,.05],[.05,0.]],complex)
    cross={k:np.array([[1.+shift+0j]]) for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')}
    return {'method':'reference' if family=='reference' else ('phase24' if order==24 else 'candidate'),
      'reference_order':order if family=='reference' else None,'candidate_order':order if family=='candidate' and order!=24 else None,
      'integration_subdivisions':subdivisions,'dz_a0':dz,'full':{'S':S,'H':H,'D':D},'cross':cross,
      'diagnostics':{'S_hermiticity_relative':0.,'H_hermiticity_relative':0.,'metric_ratio':.8},
      'numerical_task_id':key,'alias_reuse':False}


def test_aliased_candidate_is_admitted_only_after_independently_qualified_reference():
    contract={'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
      'reference_orders':[56,64],'candidate_orders':[56],
      'reference_resolutions':[{'order':56,'subdivisions':2},{'order':64,'subdivisions':2}],
      'candidate_resolutions':[{'order':56,'subdivisions':2}]}
    by={}
    def ensure(specs):
      out=[]
      for s in specs:
        fam=s['family'];order=s['order'];h=s['integration_subdivisions'];dz=s['dz_a0']
        key='r56' if order==56 else 'r64'
        shift=2e-10 if order==56 else 0.
        r=_row(fam,order,h,dz,key,shift)
        # candidate56 aliases reference56
        if fam=='candidate': r['alias_reuse']=True;r['evidence_relation']='ALIASED_SAME_NUMERICAL_TASK_NOT_INDEPENDENT_CROSSCHECK'
        out.append(r)
      return out
    got=pa.execute_geometry_policy(0.,contract,1e-3,ensure)
    assert got['status']=='GEOMETRY_QUALIFIED'
    assert got['qualified_reference_order']==64
    # candidate56 does not alias qualified reference64, therefore it still needs raw comparison and fails at 2e-10? It passes threshold.
    assert got['qualified_candidate_order']==56
    assert got['candidate_vs_reference']['max_raw_cross_relative_difference']<1e-9


def test_exact_alias_to_qualified_reference_is_marked_not_independent():
    contract={'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8},
      'reference_orders':[48,56],'candidate_orders':[56],
      'reference_resolutions':[{'order':48,'subdivisions':2},{'order':56,'subdivisions':2}],
      'candidate_resolutions':[{'order':56,'subdivisions':2}]}
    def ensure(specs):
      out=[]
      for s in specs:
        fam=s['family'];order=s['order'];dz=s['dz_a0'];shift=2e-10 if order==48 else 0.
        r=_row(fam,order,2,dz,'shared56' if order==56 else 'r48',shift)
        if fam=='candidate':r['alias_reuse']=True;r['evidence_relation']='ALIASED_SAME_NUMERICAL_TASK_NOT_INDEPENDENT_CROSSCHECK'
        out.append(r)
      return out
    got=pa.execute_geometry_policy(0.,contract,1e-3,ensure)
    assert got['status']=='GEOMETRY_QUALIFIED'
    assert got['candidate_reference_alias'] is True
    assert got['candidate_vs_reference']['evidence_relation']=='ALIASED_SAME_NUMERICAL_TASK_NOT_INDEPENDENT_CROSSCHECK'


def test_resolution_plan_is_owned_by_tp2b_not_upstream_runtime():
    assert not hasattr(pa.qr,'resolution_plan')
    contract={
      'reference_orders':[32,40],
      'candidate_orders':[24,32],
      'reference_resolutions':[{'order':32,'subdivisions':1},{'order':40,'subdivisions':2}],
      'candidate_resolutions':[{'order':24,'subdivisions':1},{'order':32,'subdivisions':2}]
    }
    assert pa.resolution_plan(contract,'reference')==[
      {'order':32,'subdivisions':1},{'order':40,'subdivisions':2}]
    assert pa.resolution_plan(contract,'candidate')==[
      {'order':24,'subdivisions':1},{'order':32,'subdivisions':2}]
