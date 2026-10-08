"""Bounded R3M11 controls; no physical convergence or rate claims."""
import importlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest
from cr_repro.tdl import TDLRunner


def api():
    assert importlib.util.find_spec('cr_repro.r3m11') is not None, 'R3M11 controls not implemented'
    return importlib.import_module('cr_repro.r3m11')


def cfg():
    return dict(energy_keV_per_u=100.,b=2.,backend='numpy',grid=dict(xlim=[-4,4],ylim=[-4,4],zlim=[-4,8],dx=1.),dt=.12,z_start=-3.,z_stop=3.,imag_steps=10,project_nmax=1,capture_plane=1.,absorber_width=1.,absorber_power=.25,absorber_reference_dt=.05,projection_slab_x=2)


def test_mask_fixed_time_semigroup():
    m=np.array([1.,.8,.2]);mod=api()
    a=mod.fixed_rate_mask(m,.1,.05);b=mod.fixed_rate_mask(m,.05,.05)
    np.testing.assert_allclose(a,b*b,rtol=1e-15,atol=1e-16)
    np.testing.assert_allclose(a**10,b**20,rtol=2e-14,atol=1e-16)


@pytest.mark.parametrize('dt,ref',[(0.,.05),(.05,0.),(float('nan'),.05),(-.01,.05)])
def test_mask_invalid_time(dt,ref):
    with pytest.raises(ValueError):api().fixed_rate_mask(np.array([.5]),dt,ref)


def test_nonorthogonal_projector_not_naive_sum():
    B=np.array([[1.,.2],[0.,np.sqrt(.96)],[0.,0.]])
    G=B.T@B;c=B.T@np.array([1.,0.,0.]);r=api().gram_projection(G,c,1.)
    assert float(c@c)>1
    assert r['probability']==pytest.approx(1.)
    np.testing.assert_allclose(B@r['coefficients'],[1,0,0],atol=2e-15)


def test_complex_projector_basis_invariant():
    B=np.array([[1,1j],[.3,2.],[0.,1.]],complex);v=np.array([.2,.1j,.5]);A=np.array([[2,1j],[.5,1]],complex)
    def p(C):return api().gram_projection(C.conj().T@C,C.conj().T@v,float(np.vdot(v,v).real))['probability']
    assert p(B)==pytest.approx(p(B@A),abs=1e-14)


def test_gram_rejects_nonhermitian():
    with pytest.raises(ValueError):api().gram_projection(np.array([[1,1],[0,1.]]),np.ones(2),1.)


def test_gram_rejects_rank_loss():
    with pytest.raises(ValueError):api().gram_projection(np.ones((2,2)),np.ones(2),1.)


def test_gram_rejects_probability_above_norm():
    with pytest.raises(ValueError):api().gram_projection(np.eye(2),np.ones(2),1.)


def test_projector_streaming_matches_dense():
    mod=api();r=TDLRunner(cfg());p,_=r.relaxed_initial()
    states=[r._project_state(p,n,l,m,r.tf)[2].ravel() for n,l,m in [(1,0,0),(2,0,0),(2,1,-1),(2,1,0),(2,1,1)]]
    B=np.stack(states,axis=1);G=B.conj().T@B*r.dv;c=B.conj().T@p.ravel()*r.dv
    exact=mod.gram_projection(G,c,r.norm(p))['probability']
    got=mod.projector_audit(p,r.spec,r.b,r.v,r.tf,nmax=2,capture_plane=1.,slab_x=1)
    assert got['P_span_nmax']==pytest.approx(exact,rel=5e-13)
    assert got['gap_identity_residual']<1e-12
    assert abs(got['region_minus_span'])<=got['gap_bound']+1e-12
    assert got['continuum_probability'] is None
    assert got['remainder_semantics']=='ORTHOGONAL_COMPLEMENT_OF_FINITE_SELECTED_SPAN_NOT_CONTINUUM'


def test_controlled_step_reference_no_absorber():
    mod=api();c=cfg();c['absorber_width']=0
    old=TDLRunner(c);new=mod.ControlledTDLRunner(c);p,_=old.relaxed_initial()
    np.testing.assert_allclose(old.step(p,0.),new.step(p,0.),rtol=0,atol=1e-15)


def test_controlled_pure_absorber_no_hidden_dt_change():
    mod=api();a=mod.ControlledTDLRunner(cfg());b=mod.ControlledTDLRunner(dict(cfg(),dt=.06))
    for obj in [a,b]:obj.kin=np.ones_like(obj.kin);obj.Vmid=lambda t:0.
    p=np.ones(a.spec.shape(),complex)
    pa=a.step(p,0.);pb=b.step(p,0.)
    # Use each exact dt_actual rather than requested dt.
    wa=-np.log(np.maximum(abs(pa),1e-300))/a.dt_actual
    wb=-np.log(np.maximum(abs(pb),1e-300))/b.dt_actual
    np.testing.assert_allclose(wa,wb,rtol=2e-13,atol=2e-13)


def test_controlled_runner_resume(tmp_path):
    mod=api();c=cfg();r=mod.ControlledTDLRunner(c)
    first=r.run(tmp_path/'split',max_steps=3);assert first['status']=='checkpoint'
    final=mod.ControlledTDLRunner(c).run(tmp_path/'split');full=mod.ControlledTDLRunner(c).run(tmp_path/'full')
    np.testing.assert_array_equal(np.load(tmp_path/'split/state.npy'),np.load(tmp_path/'full/state.npy'))
    assert 'stationary_residual_Eh' in final['initial']
    assert final['analysis']['gram_audit']['P_span_nmax']==pytest.approx(full['analysis']['gram_audit']['P_span_nmax'])
    assert final['analysis']['production_admitted'] is False


def test_controlled_resume_rejects_mutation(tmp_path):
    mod=api();c=cfg();r=mod.ControlledTDLRunner(c);r.run(tmp_path,max_steps=2)
    p=tmp_path/'state.npy';a=np.load(p);a.flat[0]+=1.;np.save(p,a)
    with pytest.raises(ValueError,match='checkpoint'):mod.ControlledTDLRunner(c).run(tmp_path)


def test_controlled_refuses_legacy_checkpoint(tmp_path):
    TDLRunner(cfg()).run(tmp_path,max_steps=2)
    with pytest.raises(ValueError,match='checkpoint'):api().ControlledTDLRunner(cfg()).run(tmp_path)


def test_saved_audit_refuses_incomplete(tmp_path):
    c=cfg();TDLRunner(c).run(tmp_path,max_steps=2)
    with pytest.raises(ValueError,match='incomplete'):api().audit_saved(tmp_path,nmax=1,slab_x=2)
