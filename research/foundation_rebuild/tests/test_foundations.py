"""Invariant and independent-reference tests; no production collision tests."""
import importlib
import numpy as np
import pytest
from scipy.linalg import eigh

@pytest.fixture
def k():
    try:
        return importlib.import_module('bass_foundations.kernels')
    except ImportError:
        pytest.fail('foundation kernels are not implemented yet')

@pytest.mark.parametrize('phase,expected',[(0,1.1900386819897764),(.25,1.3689537864661967),(.5,1.4272601797003581)])
def test_cube_r3m29(k,phase,expected):
    # [0,1]^2 x [-phase,1-phase], center .5,.5,.5-phase.
    value=k.cube_mean_inverse_radius(np.array([.5,.5,.5-phase]),1.)
    assert float(value)==pytest.approx(expected,rel=2e-12)

@pytest.mark.parametrize('xyz',[[0,0,0],[.31,-.23,.18],[3.2,-4.1,2.1]])
def test_cube_reflection_scaling(k,xyz):
    q=np.asarray(xyz)
    v=k.cube_mean_inverse_radius(q,.7)
    assert np.isfinite(v) and v>0
    assert k.cube_mean_inverse_radius(-q,.7)==pytest.approx(v,rel=2e-11)
    assert k.cube_mean_inverse_radius(3*q,2.1)==pytest.approx(v/3,rel=2e-11)

def test_point_on_nucleus_is_rejected(k):
    with pytest.raises(ValueError):k.atom_collocation(8,8.,center=(.5,.5,.5),representation='point')

def test_coulomb_average_on_gridpoint_is_finite(k):
    A=k.atom_collocation(8,8.,center=(.5,.5,.5),representation='cell')
    assert np.isfinite(A['V']).all()

def test_fft_kinetic_eigenmode(k):
    A=k.atom_collocation(8,8.,representation='point')
    phase=np.exp(2j*np.pi*np.indices((8,8,8))[0]/8)
    expect=.5*(2*np.pi/8)**2*phase
    assert np.linalg.norm(k.kinetic_action(phase,A['k2'])-expect)<1e-11

def test_matrixfree_hermitian(k):
    A=k.atom_collocation(8,8.,representation='cell')
    rng=np.random.default_rng(2049); u=rng.normal(size=(8,8,8))+1j*rng.normal(size=(8,8,8));v=rng.normal(size=(8,8,8))+1j*rng.normal(size=(8,8,8))
    err=np.vdot(u,k.atom_action(v,A))-np.vdot(k.atom_action(u,A),v)
    assert abs(err)<1e-10

def test_eigensolver_true_residual(k):
    A=k.atom_collocation(12,12.,representation='point');e,p,res=k.ground_state(A,tol=1e-11)
    assert e<0 and res<1e-9 and np.linalg.norm(p)==pytest.approx(1)

@pytest.mark.parametrize('n',[3,5])
def test_toeplitz_matches_dense(k,n):
    a=k.cutoff_coulomb_galerkin(n,10.,4.)
    c=np.random.default_rng(n).normal(size=(n,n,n))+1j*np.random.default_rng(n+1).normal(size=(n,n,n))
    H=k.dense_galerkin(a)
    assert np.max(np.abs(k.galerkin_action(c,a).ravel()-H@c.ravel()))<2e-12

def test_galerkin_translation_covariance(k):
    a=k.cutoff_coulomb_galerkin(5,10.,4.);R=np.array([.27,-.41,.63]);d=k.translation_phase(a,R)
    c=np.random.default_rng(11).normal(size=(5,5,5))+1j*np.random.default_rng(12).normal(size=(5,5,5))
    left=k.galerkin_action(d*c,a,center=R);right=d*k.galerkin_action(c,a)
    assert np.linalg.norm(left-right)/np.linalg.norm(right)<2e-14

def test_galerkin_translation_energy(k):
    a=k.cutoff_coulomb_galerkin(5,10.,4.)
    e0=eigh(k.dense_galerkin(a),eigvals_only=True,subset_by_index=[0,0])[0]
    e1=eigh(k.dense_galerkin(a,center=(.3,.5,.7)),eigvals_only=True,subset_by_index=[0,0])[0]
    assert abs(e0-e1)<5e-14

@pytest.mark.parametrize('l',[0,1,2])
def test_radial_hydrogen_spectrum(k,l):
    # R=64 was insufficient for n=5; retain that measured negative control below.
    H,M,meta=k.radial_fem(128.,40,4,l=l,quad_order=12)
    e,c=eigh(H,M,subset_by_index=[0,2])
    exact=np.array([-.5/n**2 for n in range(l+1,l+4)])
    assert np.max(abs(e-exact))<2e-7
    assert np.max(abs(c.T@M@c-np.eye(3)))<5e-12
    for j in range(3):assert np.linalg.norm(H@c[:,j]-e[j]*M@c[:,j])<5e-10

def test_radial_mesh_reject(k):
    with pytest.raises(ValueError):k.radial_fem(30.,2,1,l=-1)
    with pytest.raises(ValueError):k.radial_fem(30.,2,1,quad_order=1)

def test_metric_unitarity_does_not_validate_connection(k):
    r=k.moving_basis_negative_control(.8)
    assert r['correct_physical_error']<1e-13
    assert r['wrong_coefficient_norm_error']<1e-13
    assert r['wrong_physical_error']>.5

def test_cutoff_fourier_zero_mode(k):
    a=k.cutoff_coulomb_galerkin(3,10.,4.)
    assert a['kernel'][2,2,2]==pytest.approx(-2*np.pi*4**2/10**3)

def test_boost_residual_plane_wave(k):
    # This tests signs/algebra only, not finite-grid Galilean covariance.
    assert k.galilean_identity_residual(1.3,2.1,.7)==pytest.approx(0.,abs=1e-14)

def test_preconditioned_ground_matches_independent_arpack(k):
    a=k.atom_collocation(20,12.,representation='cell')
    e0,c0,r0=k.ground_state(a)
    e1,c1,r1,history=k.ground_state_preconditioned(a,tol=1e-10)
    assert r1<1e-10
    assert abs(e0-e1)<1e-10
    assert abs(np.vdot(c0,c1))>1-1e-10
    assert history['iterations']<150

def test_preconditioned_split_matches_independent_arpack(k):
    a=k.atom_collocation(16,12.,representation='point')
    b0=k.split_fixed_point(a,.0125)
    b1=k.split_fixed_point_preconditioned(a,.0125,tol=1e-10)
    assert abs(b0['S_eigenvalue']-b1['S_eigenvalue'])<1e-11
    assert abs(np.vdot(b0['state'],b1['state']))>1-1e-10
    assert b1['S_residual']<1e-10

def test_tiny_eigenresidual_does_not_establish_infinite_box_spectrum(k):
    H,M,_=k.radial_fem(64.,40,4,l=2,quad_order=12)
    e,c=eigh(H,M,subset_by_index=[2,2])
    assert np.linalg.norm(H@c[:,0]-e[0]*M@c[:,0])<1e-9
    assert abs(e[0]+.5/25)>1e-5  # finite-R n=5 bias, NOT a solver failure

@pytest.mark.parametrize('xyz',[[0,0,0],[.5,.5,0],[.13,-.37,.08],[10.2,-7.7,2.5],[72.7,61.2,-58.3]])
def test_cell_kernel_roundoff_against_high_precision_formula(k,xyz):
    from bass_foundations.cell_oracle import cell_mean_inverse_radius
    q=np.asarray(xyz);ref=float(cell_mean_inverse_radius(q-.5,q+.5,digits=60))
    fast=float(k.cube_mean_inverse_radius(q,1.))
    assert fast==pytest.approx(ref,rel=2e-8,abs=1e-13)

@pytest.mark.parametrize('ell',[0,1,2])
def test_radial_quadrature_refinement(k,ell):
    H0,M0,_=k.radial_fem(96.,40,4,l=ell,quad_order=12)
    H1,M1,_=k.radial_fem(96.,40,4,l=ell,quad_order=16)
    e0=eigh(H0,M0,subset_by_index=[0,2],eigvals_only=True)
    e1=eigh(H1,M1,subset_by_index=[0,2],eigvals_only=True)
    assert np.max(abs(e0-e1))<1e-9
    assert np.max(abs(M0-M1))<1e-11

def test_galerkin_preconditioned_ground_dense_oracle(k):
    a=k.cutoff_coulomb_galerkin(7,10.,4.)
    e,c,res,meta=k.galerkin_ground_preconditioned(a)
    ed=eigh(k.dense_galerkin(a),eigvals_only=True,subset_by_index=[0,0])[0]
    assert abs(e-ed)<1e-10 and res<1e-10

def test_translating_coulomb_exact_comoving_identity(k):
    a=k.cutoff_coulomb_galerkin(5,10.,4.);v=1.25;T=1.3
    r=k.moving_galerkin_probe(a,v,T,[8,16,32,64])
    errs=np.array([x['error_to_exact_comoving'] for x in r['midpoint_ladder']])
    assert np.all(errs>0) and np.all(errs[1:]<errs[:-1])
    assert np.all(np.log2(errs[:-1]/errs[1:])>1.9)
    assert r['missing_advection_norm_error']<1e-12
    assert r['missing_advection_state_error']>.1

@pytest.mark.parametrize('n',[3,5,7])
def test_minimal_embedding_matches_dense_and_full_convolution(k,n):
    a=k.cutoff_coulomb_galerkin(n,10.,4.)
    c=np.random.default_rng(n).normal(size=(n,n,n))+1j*np.random.default_rng(n+2).normal(size=(n,n,n));R=(.17,-.31,.22)
    actual=k.galerkin_action_embedded(c,a,center=R)
    assert np.max(abs(actual.ravel()-k.dense_galerkin(a,center=R)@c.ravel()))<1e-11
    assert np.max(abs(actual-k.galerkin_action(c,a,center=R)))<1e-11
    assert a['embedding_length']>=2*n-1

def test_metric_identity_does_not_determine_antihermitian_connection(k):
    r=k.direct_connection_negative_control(.7,.43,1e-5)
    assert r['wrong_metric_identity_residual']<1e-9
    assert r['wrong_generator_skew_residual']<1e-14
    assert r['wrong_direct_basis_derivative_residual']>.5
    assert r['correct_direct_basis_derivative_residual']<1e-9

def test_heavy_grid_is_rejected_before_allocating(k,monkeypatch):
    def fail(*args,**kwargs):pytest.fail('allocation attempted before bounded-grid guard')
    monkeypatch.setattr(k.np,'meshgrid',fail)
    with pytest.raises(ValueError,match='bounded'):
        k.atom_collocation(129,16.)

def test_galerkin_kernel_factory_is_readonly(k):
    a=k.cutoff_coulomb_galerkin(5,10.,4.)
    assert not a['kernel'].flags.writeable
    assert not a['ks'].flags.writeable
    assert not a['k2'].flags.writeable

def test_cli_creates_fresh_output_parent(tmp_path):
    import subprocess,sys,os,json
    from pathlib import Path
    root=Path(__file__).resolve().parents[1];target=tmp_path/'new'/'nested'/'atom.json'
    env=dict(os.environ,PYTHONPATH=str(root/'src'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    call=[sys.executable,str(root/'run_probes.py'),'atom','--n','8','--length','8',
          '--solver','lobpcg','--out',str(target)]
    p=subprocess.run(call,capture_output=True,text=True,env=env,timeout=20)
    assert p.returncode==0,p.stderr
    assert json.loads(target.read_text())['production_admitted'] is False
    old=target.read_bytes()
    p2=subprocess.run(call,capture_output=True,text=True,env=env,timeout=20)
    assert p2.returncode!=0 and target.read_bytes()==old
