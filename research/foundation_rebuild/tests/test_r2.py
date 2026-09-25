"""R2: true two-center weak matrices and independent, non-unitarity-only checks."""
import importlib
import numpy as np
import pytest
from scipy import linalg, special, integrate

@pytest.fixture
def r2():
    try:
        return importlib.import_module('bass_foundations.two_center')
    except ImportError:
        pytest.fail('two-center R2 implementation is missing')

@pytest.mark.parametrize('ell,emm',[(l,m) for l in range(4) for m in range(-l,l+1)])
def test_solid_harmonics_and_direct_gradient(r2,ell,emm):
    xyz=np.random.default_rng(481).normal(size=(11,3))
    f,g=r2.solid_harmonic(xyz,ell,emm)
    rad=np.linalg.norm(xyz,axis=1)
    exact=rad**ell*special.sph_harm_y(ell,emm,np.arccos(xyz[:,2]/rad),np.arctan2(xyz[:,1],xyz[:,0]))
    assert np.max(abs(f-exact))<3e-13
    for j in range(3):
        d=np.eye(3)[j]*2e-6
        fd=(r2.solid_harmonic(xyz+d,ell,emm)[0]-r2.solid_harmonic(xyz-d,ell,emm)[0])/4e-6
        assert np.max(abs(g[:,j]-fd))<3e-8

@pytest.mark.parametrize('sep',[.5,2.,6.])
def test_stationary_1s_shd_analytic_oracle(r2,sep):
    tr=r2.Trajectory(((0,0,0),(sep,0,0)))
    basis=r2.hydrogen_channels(1)
    q=r2.Quadrature(40,32,24,2.)
    snap=r2.assemble(tr,basis,0.,q)
    overlap=np.exp(-sep)*(1+sep+sep**2/3)
    j=(1-(1+sep)*np.exp(-2*sep))/sep
    exchange=np.exp(-sep)*(1+sep)
    assert np.max(abs(snap.S-np.array([[1,overlap],[overlap,1]])))<3e-11
    assert np.max(abs(snap.H-np.array([[-.5-j,-.5*overlap-exchange],[-.5*overlap-exchange,-.5-j]])))<3e-10
    assert np.max(abs(snap.D))==0
    assert snap.metadata['production_admitted'] is False
    assert not snap.S.flags.writeable

def test_boost_overlap_independent_adaptive_integral(r2):
    sep=2.;v=1.7
    tr=r2.Trajectory(((0,0,0),(sep,0,0)),((0,0,0),(0,0,v)))
    s=r2.assemble(tr,r2.hydrogen_channels(1),0.,r2.Quadrature(56,48,48,2.))
    # Independent azimuth-integrated Bessel expression at closest approach.
    def outer(mu):
        val=integrate.quad(lambda eta:(mu*mu-eta*eta)*special.j0(v*sep/2*np.sqrt((mu*mu-1)*(1-eta*eta))),-1,1,epsabs=2e-11)[0]
        return np.exp(-sep*mu)*val*sep**3/4
    exact,err=integrate.quad(outer,1,35,epsabs=2e-11,epsrel=2e-11)
    assert abs(s.S[0,1]-exact)<2e-9
    assert abs(s.D[1,1]+.5j*v*v)<2e-9

def test_direct_basis_derivative_catches_skew_connection(r2):
    tr=r2.Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,1.4)))
    basis=r2.hydrogen_channels(2);t=.31
    points,w=r2.prolate_grid(tr,t,r2.Quadrature(24,20,24,1.))
    B,grad,dot=r2.basis_values(points,basis,tr,t)
    eps=2e-6
    fd=(r2.basis_values(points,basis,tr,t+eps)[0]-r2.basis_values(points,basis,tr,t-eps)[0])/(2*eps)
    assert np.max(abs(dot-fd))<2e-8
    D=B.conj().T@(w[:,None]*dot);Dfd=B.conj().T@(w[:,None]*fd)
    assert np.linalg.norm(D-Dfd)<2e-8
    wrong=D+.1j*np.eye(len(basis))
    assert np.linalg.norm((wrong+wrong.conj().T)-(D+D.conj().T))<1e-14
    assert np.linalg.norm(wrong-Dfd)>.1

def test_rigid_translation_and_center_exchange(r2):
    basis=r2.hydrogen_channels(1)
    tr=r2.Trajectory(((0,0,0),(2,0,.3)),((0,0,0),(0,0,1.1)))
    shift=np.array([.43,-.17,.21]);t=.2;q=r2.Quadrature(32,24,24,2.)
    a=r2.assemble(tr,basis,t,q)
    b=r2.assemble(r2.Trajectory(tr.origins+shift,tr.velocities),basis,t,q)
    phase=np.exp(1j*tr.velocities@shift)
    for name in ('S','H','D'):
        expected=np.conj(phase)[:,None]*getattr(a,name)*phase[None,:]
        assert np.max(abs(getattr(b,name)-expected))<2e-12
    c=r2.assemble(r2.Trajectory(tr.origins[::-1],tr.velocities[::-1]),basis,t,q)
    for name in ('S','H','D'):
        assert np.max(abs(getattr(c,name)-getattr(a,name)[::-1,::-1]))<2e-10

def test_frozen_generalized_evolution_and_projector(r2):
    s=r2.assemble(r2.Trajectory(((0,0,0),(2,0,0))),r2.hydrogen_channels(1),0.,r2.Quadrature(32,24,24,2.))
    c=np.array([1,0],complex);dt=.13
    e,U=linalg.eigh(s.H,s.S)
    expected=linalg.expm(-1j*linalg.solve(s.S,s.H)*dt)@c
    actual=U@(np.exp(-1j*e*dt)*(U.conj().T@s.S@c))
    assert np.linalg.norm(actual-expected)<1e-12
    assert abs(np.vdot(actual,s.S@actual)-np.vdot(c,s.S@c))<1e-12
    p=r2.selected_population(actual,s.S,[1])
    assert 0<=p<=1
    with pytest.raises(ValueError):r2.selected_population(actual,s.S,[1,1])

def test_fem_bank_spectrum_positive_states_and_full_m(r2):
    from bass_foundations.radial_basis import RadialSpec, atomic_bank
    spec=RadialSpec(radius=128.,elements=40,degree=4,lmax=3,bound_nmax=4,positive_per_l=1,positive_emax=2.)
    bank=atomic_bank(spec)
    assert len(bank)==14
    assert sum(x.energy>0 for x in bank)==4
    for mode in bank:
        if mode.principal_n is not None:assert abs(mode.energy+.5/mode.principal_n**2)<2e-7
    channels=r2.symmetric_channels(bank)
    assert len(channels)==92
    for mode in bank:
        for center in (0,1):
            assert [c.m for c in channels if c.center==center and c.radial.identity==mode.identity]==list(range(-mode.l,mode.l+1))
    with pytest.raises(ValueError):atomic_bank(RadialSpec(positive_per_l=1,positive_emax=1e-8))

def test_fem_basis_values_and_cross_center_bridge(r2):
    from bass_foundations.radial_basis import RadialSpec, atomic_bank
    bank=atomic_bank(RadialSpec(radius=32.,elements=36,degree=4,lmax=0,bound_nmax=1))
    tr=r2.Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,.4)))
    b=r2.symmetric_channels(bank);p=np.array([[.23,.31,.19],[1.3,.3,1.7]])
    B,g,d=r2.basis_values(p,b,tr,.1)
    for j in range(3):
        dx=np.eye(3)[j]*1e-6
        fd=(r2.basis_values(p+dx,b,tr,.1)[0]-r2.basis_values(p-dx,b,tr,.1)[0])/2e-6
        assert np.max(abs(g[:,:,j]-fd))<2e-8
    q=r2.Quadrature(64,48,32,2.)
    actual=r2.assemble(tr,b,.1,q)
    ref=r2.assemble(tr,r2.hydrogen_channels(1),.1,q)
    assert np.max(abs(actual.S-ref.S))<3e-5
    assert np.max(abs(actual.H-ref.H))<3e-5
    assert np.max(abs(actual.D-ref.D))<3e-5

@pytest.mark.parametrize('kwargs',[{'nrad':True},{'nrad':129},{'neta':0},{'nphi':3},{'scale':0.},{'scale':float('nan')}])
def test_quadrature_guard_before_allocation(r2,kwargs):
    with pytest.raises(ValueError):r2.Quadrature(**kwargs)

def test_nonfinite_geometry_coincident_and_rank_loss_rejected(r2):
    with pytest.raises(ValueError):r2.Trajectory(((0,0,0),(float('nan'),0,0)))
    with pytest.raises(ValueError):r2.prolate_grid(r2.Trajectory(((0,0,0),(0,0,0))),0.,r2.Quadrature())
    with pytest.raises(ValueError):r2.selected_population(np.ones(2),np.ones((2,2)),[0,1])
    with pytest.raises(ValueError):r2.solid_harmonic(np.ones((2,3)),4,0)

def test_two_center_basis_identity_changes(r2):
    tr=r2.Trajectory(((0,0,0),(2,0,0)))
    q=r2.Quadrature(16,16,16,2.)
    a=r2.assemble(tr,r2.hydrogen_channels(1),0.,q)
    b=r2.assemble(tr,r2.hydrogen_channels(1),.1,q)
    assert a.identity!=b.identity
    assert a.metadata['basis_kind']=='FINITE_TWO_CENTER_SELECTED_BASIS'
