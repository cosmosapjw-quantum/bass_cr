import importlib.util
import math
from pathlib import Path
import numpy as np
import pytest

def api():
    assert importlib.util.find_spec('cr_repro.r3m11') is not None, 'R3M11 controlled implementation is missing'
    from cr_repro import r3m11
    return r3m11

def config():
    return dict(energy_keV_per_u=100,b=2,backend='numpy',grid=dict(xlim=[-4,4],ylim=[-4,4],zlim=[-4,8],dx=1),z_start=-2,z_stop=2,dt=.1,absorber_width=1,absorber_power=.125,initial_state='analytic',project_nmax=1,checkpoint_stride=4,absorber_reference_dt=.05)

def test_mask_semigroup():
    m=api(); ref=np.array([.1,.7,1.]);a=m.scale_mask(ref,.03,.05,np)
    b=m.scale_mask(ref,.01,.05,np)
    np.testing.assert_allclose(a,b**3,rtol=2e-15)

@pytest.mark.parametrize('dt,refdt',[(0,.1),(.1,0),(-1,.1),(float('nan'),.1)])
def test_mask_invalid(dt,refdt):
    with pytest.raises(ValueError):api().scale_mask(np.array([.7]),dt,refdt,np)

def test_weighted_projector_exact_and_invariant():
    m=api(); B=np.array([[1,1],[0,2],[0,0]],complex);w=np.array([.5,2.,1.]);psi=np.array([.2,.3,.4j]);region=np.array([0,1,1],bool)
    G=B.conj().T@(w[:,None]*B);c=B.conj().T@(w*psi); Gr=B.conj().T@((w*region)[:,None]*B);cr=B.conj().T@(w*region*psi);nr=np.vdot(psi,w*region*psi).real
    d=m.projector_diagnostics(G,c,Gr,cr,nr)
    assert d['P_selected_bound_gram']==pytest.approx(.02+.18)
    assert d['gap_bound_valid']
    assert not d['complement_is_pure_continuum']
    A=np.array([[1,3j],[.5,2]],complex)
    e=m.projector_diagnostics(A.conj().T@G@A,A.conj().T@c,A.conj().T@Gr@A,A.conj().T@cr,nr)
    assert e['P_selected_bound_gram']==pytest.approx(d['P_selected_bound_gram'])

def test_rank_deficiency_rejected():
    with pytest.raises(ValueError,match='Gram'):api().projector_diagnostics(np.ones((2,2)),np.ones(2),np.eye(2),np.zeros(2),0.)

def test_nonhermitian_gram_rejected():
    with pytest.raises(ValueError,match='Hermitian'):api().projector_diagnostics(np.array([[1,2],[0,1]]),np.ones(2),np.eye(2),np.zeros(2),0.)

def test_controlled_dt_changes_not_absorber():
    m=api();cfg=config();r=m.ControlledTDL(cfg);q=m.ControlledTDL(dict(cfg,dt=.05))
    # Remove kinetic/potential evolution to isolate the absorption semigroup.
    for z in (r,q):z.kin=np.ones(z.spec.shape());z.Vmid=lambda t:np.zeros(r.spec.shape())
    x=np.ones(r.spec.shape(),complex);y=x.copy()
    for j in range(r.nstep):x=r.step(x,0)
    for j in range(q.nstep):y=q.step(y,0)
    np.testing.assert_allclose(x,y,atol=3e-14,rtol=3e-14)

def test_checkpoint_resume_and_code_identity(tmp_path):
    m=api();cfg=config();a=m.run_tdl(cfg,tmp_path/'chunk',max_steps=3)
    assert a['status']=='checkpoint'
    b=m.run_tdl(cfg,tmp_path/'chunk',resume=True);c=m.run_tdl(cfg,tmp_path/'whole')
    assert b['analysis']['P_selected_bound_gram']==pytest.approx(c['analysis']['P_selected_bound_gram'],rel=1e-13)
    with pytest.raises(ValueError):m.run_tdl(dict(cfg,dt=.05),tmp_path/'chunk',resume=True)
    with pytest.raises(FileExistsError):m.run_tdl(cfg,tmp_path/'whole')

def test_gram_analysis_chunk_invariance():
    m=api();r=m.ControlledTDL(config());psi,_=r.relaxed_initial()
    a=r.analyze_streaming(psi,block_size=71);b=r.analyze_streaming(psi,block_size=222)
    assert a['P_selected_bound_gram']==pytest.approx(b['P_selected_bound_gram'],rel=1e-12)
    assert a['selected_subspace']==[[1,0,0]]

def test_spectrum_labels_and_generator_identity():
    m=api();from cr_repro.aocc import OneElectronAOCC
    cfg=dict(energy_keV_per_u=100,b=2,zmax=2,dt=.2,ns=4,np=0,alpha_min=.01,alpha_max=10,eps_max=3)
    a=OneElectronAOCC(cfg);d=m.audit_aocc_matrix(a,.3)
    assert d['generator_identity_residual']<1e-12
    assert 'not_a_covariance' in d['claim']

def test_nonfinite_energy_rejected():
    with pytest.raises(ValueError):api().ControlledTDL(dict(config(),energy_keV_per_u=float('nan')))

def test_boys_complex_fixture_against_independent_erf():
    m=api()
    assert hasattr(m,'controlled_boys'), 'controlled Boys evaluation missing'
    z=-3.3168887925160937+21.984297833631878j
    want=[.047936095313431064-.7593991202631057j,-.10535885154387058-.6123186022153199j,-.12809952794526364-.6006086708083358j]
    for n,w in enumerate(want):
        assert abs(m.controlled_boys(n,z)-w)<2e-13
        assert abs(m.controlled_boys(n,z.conjugate())-m.controlled_boys(n,z).conjugate())<1e-14

def test_controlled_aocc_keeps_vendor_bytes_and_restores_matrix_hermiticity():
    m=api()
    assert hasattr(m,'ControlledAOCC'), 'controlled AOCC missing'
    import gaussian_cartesian as original
    before=original.boys
    cfg=dict(energy_keV_per_u=100,b=2,zmax=30,dt=.05,ns=16,np=12,alpha_min=.001,alpha_max=1000.,pmin=.001,pmax=10.,eps_max=5.)
    a=m.ControlledAOCC(cfg);d=m.audit_aocc_matrix(a,6.474164630741937)
    assert original.boys is before
    assert d['generator_antihermitian_relative_defect']<1e-10

def test_controlled_boys_small_real_matches_integral_reference():
    m=api()
    assert hasattr(m,'controlled_boys'), 'controlled Boys evaluation missing'
    from scipy.integrate import quad
    for n in range(3):
        for z in [-3.,0.,.1,3.,19.,21.,100.]:
            ref=quad(lambda u:u**(2*n)*math.exp(-z*u*u),0,1,epsabs=1e-12)[0]
            assert abs(m.controlled_boys(n,z)-ref)<1e-11*max(1.,abs(ref))

def test_ready_plan_keeps_absorber_and_imaginary_duration_fixed(tmp_path):
    import runpy,json
    ns=runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/r3m11_plan.py'))
    rows=ns['build_plan'](tmp_path/'plan','numpy')
    assert len(rows)==20
    for row in rows:
        c=json.loads(Path(row['config']).read_text())
        if row['action'] in ('initial','tdl'):
            assert c['absorber_reference_dt']==.05
            assert c['imag_dt']*c['imag_steps']==15.
    assert not json.loads((tmp_path/'plan/PLAN.json').read_text())['bgrid_admitted']
