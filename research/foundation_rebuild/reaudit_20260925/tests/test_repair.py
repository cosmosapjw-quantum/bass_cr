import numpy as np
import pytest
from scipy.special import jv
from aligned_cross import phase_ring_weights

@pytest.mark.parametrize('kappa',[0.,21.03140453837353,128.5107882566547])
@pytest.mark.parametrize('m',[-4,-1,0,1,4])
def test_fourier_bessel_moments(kappa,m):
    degree=4;n=2*degree+1;phi=2*np.pi*np.arange(n)/n;phi0=.37
    w=phase_ring_weights(np.array([kappa]),np.array([phi0]),degree)[0]
    got=np.dot(w,np.exp(1j*m*phi))
    exact=2*np.pi*1j**m*jv(m,kappa)*np.exp(1j*m*phi0)
    assert abs(got-exact)<3e-12

from aligned_cross import geometry_pairs,intersection_volume,cross_blocks
from bass_foundations.radial_basis import RadialSpec,atomic_bank
from bass_foundations.two_center import Trajectory,symmetric_channels
from laguerre_reference import matrices

@pytest.mark.parametrize('R',[.3,2.,5.7,11.9,12.,13.])
def test_complete_intersection_measure(R):
    edges=np.array([0.,.17,1.2,2.1,4.,6.])
    got=2*np.pi*sum(float(np.sum(w)) for _,_,w in geometry_pairs(edges,R,4))
    exact=intersection_volume(6.,R)
    assert abs(got-exact)<2e-11*max(exact,1.)

@pytest.mark.parametrize('edges,R,order',[(np.array([0,2,1]),2.,4),(np.array([1,2]),2.,4),(np.array([0,2]),0.,4),(np.array([0,2]),1.,1)])
def test_invalid_geometry_rejected(edges,R,order):
    with pytest.raises(ValueError):list(geometry_pairs(edges,R,order))

@pytest.fixture(scope='module')
def small_channels():
    bank=atomic_bank(RadialSpec(radius=8.,elements=8,degree=4,lmax=1,bound_nmax=1,positive_per_l=1))
    return symmetric_channels(bank),bank[0].edges

def test_cross_backend_matches_independent_uniform_angular(small_channels):
    ch,edges=small_channels
    tr=Trajectory(((0,0,0),(2.,0,.3)),((0,0,0),(.2,.3,2.)))
    a=cross_blocks(tr,ch,edges,.2,order=4,angular='bessel')
    b=cross_blocks(tr,ch,edges,.2,order=4,angular='uniform',nphi=96)
    for k in ['S_tp','S_pt','H_tp','H_pt','D_tp','D_pt']:
        assert np.linalg.norm(a[k]-b[k])<2e-11
    assert np.linalg.norm(a['D_pt'])==0.
    assert np.linalg.norm(a['S_tp']-a['S_pt'].conj().T)<2e-13
    assert np.linalg.norm(a['H_tp']-a['H_pt'].conj().T)<2e-13

def test_disjoint_supports_are_exact_zero(small_channels):
    ch,edges=small_channels
    a=cross_blocks(Trajectory(((0,0,0),(20.,0,0))),ch,edges,0.,order=4)
    for k in ['S_tp','S_pt','H_tp','H_pt','D_tp','D_pt']:assert np.linalg.norm(a[k])==0.

@pytest.mark.parametrize('ell',[0,1,2])
def test_laguerre_mass_orthogonality_and_hydrogen_channels(ell):
    from scipy.linalg import eigh
    H,M=matrices(32,ell)
    assert np.linalg.norm(M-np.eye(32))<5e-12
    assert np.linalg.norm(H-H.T)<5e-11
    e=eigh(H,M,eigvals_only=True)
    for j in range(3-ell):assert abs(e[j]+.5/(j+ell+1)**2)<3e-10

@pytest.mark.parametrize('size,ell,zeta',[(1,0,1),(8,4,1),(8,0,0),(8,0,float('nan'))])
def test_laguerre_invalid_inputs(size,ell,zeta):
    with pytest.raises(ValueError):matrices(size,ell,zeta)
