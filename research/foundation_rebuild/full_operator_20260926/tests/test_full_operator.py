from functools import lru_cache
import numpy as np
import pytest
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from bass_foundations.radial_basis import FEMRadial,RadialSpec,atomic_bank
from bass_foundations.two_center import Channel,Trajectory,symmetric_channels,basis_values
import full_operator as fo

# Compact normalized manufactured mode u(r)=sqrt(30/L^5) r(L-r).
# It is zero outside its own ball, continuous at the boundary, with nonzero slope.
def compact_mode(L=4.,ell=0):
    from numpy.polynomial import Polynomial
    u=Polynomial([0,1])**(ell+1)*Polynomial([L,-1])
    norm=np.sqrt(u.__mul__(u).integ()(L))
    u=u/norm
    coeff=u(Polynomial([0.,L])).coef[None,:]
    return FEMRadial(ell,None,123.,np.array([0.,L]),coeff,'manufactured_'+str((L,ell)),0.)

def ch1(L=4.):
    return (Channel(0,compact_mode(L),0),)

def test_same_center_sphere_not_intersection():
    L=4.;R=1.5;ch=ch1(L)
    tr=Trajectory(((0,0,0),(0,0,R)))
    x=fo.same_center_blocks(tr,ch,0.,0,order=20)
    assert abs(x['S'][0,0]-1)<2e-13
    # The D3 intersection bug would omit a positive part of the radial mass.
    u=lambda r:np.sqrt(30/L**5)*r*(L-r)
    def fraction(r):
        if r+R<=L:return 1.
        return np.clip((1+(L*L-r*r-R*R)/(2*r*R))/2,0,1)
    lost=1-quad(lambda r:u(r)**2*fraction(r),0,L,points=[L-R],epsabs=1e-13)[0]
    assert lost>0.01

def test_s_wave_shell_theorem_inside_support():
    L=4.;R=1.5;u=lambda r:np.sqrt(30/L**5)*r*(L-r)
    x=fo.same_center_blocks(Trajectory(((0,0,0),(R,0,0))),ch1(L),0.,0,order=20)
    oracle=-quad(lambda r:u(r)**2/max(r,R),0,L,points=[R],epsabs=1e-13)[0]
    assert abs(x['V_other'][0,0]-oracle)<2e-13
    # eigenvalue label is deliberately bogus and must not enter the weak form.
    h0=quad(lambda r:0.5*(np.sqrt(30/L**5)*(L-2*r))**2-u(r)**2/r,0,L,epsabs=1e-13)[0]
    assert abs(x['H0'][0,0]-h0)<2e-13

def test_same_center_boost_cancellation_and_nonhermitian_D():
    ch=ch1();v=(.2,-.3,1.7)
    tr=Trajectory(((0,0,0),(1,0,2)),(v,(0,0,0)))
    x=fo.same_center_blocks(tr,ch,.15,0,order=20)
    assert np.linalg.norm(x['H']-1j*x['D']-x['H0']-x['V_other'])<2e-13
    assert np.linalg.norm(x['D']-x['D'].conj().T)>1.

@pytest.mark.parametrize('R',[1.5,7.])
def test_projected_p_multipoles_inside_and_outside(R):
    L=4.;s=compact_mode(L,0);p=compact_mode(L,1)
    ch=(Channel(0,s,0),Channel(0,p,0),Channel(0,p,1),Channel(0,p,-1))
    x=fo.same_center_blocks(Trajectory(((0,0,0),(0,0,R))),ch,0.,0,order=24)
    us=lambda r:s.evaluate(np.array(r))[0].item()
    up=lambda r:p.evaluate(np.array(r))[0].item()
    f=lambda r,n:min(r,R)**n/max(r,R)**(n+1)
    opts=dict(epsabs=2e-13,points=[R] if R<L else [])
    sp=-quad(lambda r:us(r)*up(r)*f(r,1)/np.sqrt(3),0,L,**opts)[0]
    pp0=-quad(lambda r:up(r)**2*(f(r,0)+.4*f(r,2)),0,L,**opts)[0]
    pp1=-quad(lambda r:up(r)**2*(f(r,0)-.2*f(r,2)),0,L,**opts)[0]
    assert abs(x['V_other'][0,1]-sp)<5e-13
    assert abs(x['V_other'][1,1]-pp0)<5e-13
    assert abs(x['V_other'][2,2]-pp1)<5e-13
    assert abs(x['V_other'][3,3]-pp1)<5e-13
    assert abs(x['V_other'][0,2])<1e-13


def direct_spherical(tr,ch,t,center,order=22,ntheta=24,nphi=48):
    edges=ch[0].radial.edges;xr,wr=leggauss(order)
    r=((edges[1:]+edges[:-1])[:,None]/2+np.diff(edges)[:,None]*xr/2).ravel()
    rw=(np.diff(edges)[:,None]*wr/2).ravel()
    x,wx=leggauss(ntheta);phi=2*np.pi*np.arange(nphi)/nphi
    dirs=np.stack(np.broadcast_arrays(np.sqrt(1-x*x)[:,None]*np.cos(phi),np.sqrt(1-x*x)[:,None]*np.sin(phi),x[:,None]),-1).reshape(-1,3)
    aw=np.broadcast_to(wx[:,None]*(2*np.pi/nphi),(len(x),nphi)).ravel()
    p=(tr.centers(t)[center]+r[:,None,None]*dirs[None,:,:]).reshape(-1,3)
    w=((rw*r*r)[:,None]*aw).ravel()
    B,g,dot=basis_values(p,ch,tr,t)
    V=-sum(tr.charges[j]/np.linalg.norm(p-tr.centers(t)[j],axis=1) for j in (0,1))
    S=B.conj().T@(w[:,None]*B);H=B.conj().T@((w*V)[:,None]*B)
    for j in range(3):H+=.5*g[:,:,j].conj().T@(w[:,None]*g[:,:,j])
    D=B.conj().T@(w[:,None]*dot)
    return dict(S=S,H=H,D=D)


def test_same_center_matches_independent_full_spherical_weak_form():
    ch=tuple(Channel(1,compact_mode(4,l),m) for l,m in [(0,0),(1,-1),(1,0),(1,1),(2,1),(3,-2)])
    tr=Trajectory(((9.,3.,-4.),(.3,-.2,.1)),((.2,0,0),(.3,-.2,1.9)),(1.3,.8))
    got=fo.same_center_blocks(tr,ch,.2,1,order=24)
    ref=direct_spherical(tr,ch,.2,1)
    for name in ('S','H','D'):
        assert np.linalg.norm(got[name]-ref[name])<3e-11
    assert max(np.linalg.norm(a+a.conj().T) for a in got['A'])<2e-12


@lru_cache(maxsize=1)
def small_basis():
    spec=RadialSpec(radius=6.,elements=6,degree=4,lmax=1,bound_nmax=1,positive_per_l=1)
    return symmetric_channels(atomic_bank(spec))


def test_full_assembly_retains_same_center_mass_and_frozen_cross():
    ch=small_basis();tr=Trajectory(((0,0,0),(1.7,0,1.2)),((0,0,0),(.1,.2,.7)))
    snap=fo.assemble_full(tr,ch,.1,same_order=20,cross_order=12)
    assert snap['S'].shape==(len(ch),len(ch))
    for center in (0,1):
        ix=[i for i,c in enumerate(ch) if c.center==center]
        assert np.linalg.norm(snap['S'][np.ix_(ix,ix)]-np.eye(len(ix)))<1e-10
    assert snap['diagnostics']['metric_ratio']>1e-8
    assert snap['metadata']['capture_execution_allowed'] is False
    assert np.linalg.norm(snap['D'][:,[i for i,c in enumerate(ch) if c.center==0]])==0.


def test_full_metric_derivative_from_independent_time_difference():
    ch=small_basis()
    tr=Trajectory(((0,0,0),(1.7,.4,1.2)),((.1,0,.1),(.3,-.2,1.2)))
    t=.15;h=.001
    a=fo.assemble_full(tr,ch,t,same_order=20,cross_order=20)
    plus=fo.assemble_full(tr,ch,t+h,same_order=20,cross_order=20)
    minus=fo.assemble_full(tr,ch,t-h,same_order=20,cross_order=20)
    deriv=(plus['S']-minus['S'])/(2*h)
    expected=a['D']+a['D'].conj().T
    err=np.linalg.norm(deriv-expected)/max(1.,np.linalg.norm(expected))
    assert err<2e-7, err
    # Raw generalized evolution preserves the declared metric derivative.
    gen=np.linalg.solve(a['S'],-1j*a['H']-a['D'])
    residual=gen.conj().T@a['S']+a['S']@gen+deriv
    assert np.linalg.norm(residual)<2e-7
    # Sdot alone cannot detect a skew perturbation of the connection.
    wrong=a['D']+1j*np.eye(len(ch))*.1
    assert np.linalg.norm(wrong+wrong.conj().T-expected)<1e-15
    assert np.linalg.norm(wrong-a['D'])>.1


def test_direct_basis_time_derivative_same_center_independent_of_Sdot():
    ch=tuple(Channel(1,compact_mode(4,l),m) for l,m in [(0,0),(1,-1),(1,0),(1,1)])
    tr=Trajectory(((8,0,0),(.2,-.3,.1)),((0,0,0),(.2,.1,1.3)))
    t=.2;eps=1e-6
    x,w=leggauss(24);r=2*(x+1);rw=2*w
    eta,we=leggauss(14);phi=2*np.pi*np.arange(32)/32
    dirs=np.stack(np.broadcast_arrays(np.sqrt(1-eta*eta)[:,None]*np.cos(phi),np.sqrt(1-eta*eta)[:,None]*np.sin(phi),eta[:,None]),-1).reshape(-1,3)
    p=(tr.centers(t)[1]+r[:,None,None]*dirs[None,:,:]).reshape(-1,3)
    weights=((rw*r*r)[:,None]*np.broadcast_to(we[:,None]*(2*np.pi/32),(14,32)).ravel()).ravel()
    B=basis_values(p,ch,tr,t)[0]
    bp=basis_values(p,ch,tr,t+eps)[0];bm=basis_values(p,ch,tr,t-eps)[0]
    oracle=B.conj().T@(weights[:,None]*(bp-bm)/(2*eps))
    got=fo.same_center_blocks(tr,ch,t,1,order=24)['D']
    assert np.linalg.norm(got-oracle)<3e-9
    bad=.5*(got+got.conj().T)
    assert np.linalg.norm(bad-oracle)>.1


def test_full_channel_permutation_and_unmodified_cross_arrays():
    ch=small_basis();tr=Trajectory(((0,0,0),(1.7,.3,.9)),((0,0,0),(0,0,1.1)))
    c=fo.compute_cross_snapshot(tr,ch,.1,order=12)
    a=fo.assemble_full(tr,ch,.1,cross=c)
    ti=[i for i,q in enumerate(ch) if q.center==0];pi=[i for i,q in enumerate(ch) if q.center==1]
    for k in ('S','H','D'):
        np.testing.assert_array_equal(a[k][np.ix_(ti,pi)],c.arrays[k+'_tp'])
        np.testing.assert_array_equal(a[k][np.ix_(pi,ti)],c.arrays[k+'_pt'])
    perm=np.array([len(ch)-1,*range(len(ch)-1)])
    b=fo.assemble_full(tr,[ch[i] for i in perm],.1,cross_order=12)
    for name in ('S','H','D'):
        assert np.linalg.norm(b[name]-a[name][np.ix_(perm,perm)])<3e-12
    with pytest.raises(ValueError,match='identity'):
        fo.assemble_full(tr,ch,.2,cross=c)


def test_disjoint_full_operator_keeps_unit_same_center_mass():
    ch=small_basis();tr=Trajectory(((0,0,0),(20,0,0)),((0,0,0),(0,0,1.)))
    x=fo.assemble_full(tr,ch,0.,cross_order=12)
    assert np.linalg.norm(x['S']-np.eye(len(ch)))<1e-10
    assert x['metadata']['cross_metadata']['zero_reason']=='DISJOINT_SUPPORTS'
    assert np.linalg.norm(x['H'])>0.1


@pytest.mark.parametrize('center,order',[(2,12),(0,True),(0,5)])
def test_invalid_new_same_center_inputs(center,order):
    with pytest.raises(ValueError):
        fo.same_center_blocks(Trajectory(((0,0,0),(2,0,0))),ch1(),0.,center,order=order)


def test_reject_unequal_meshes_and_duplicate_channels():
    tr=Trajectory(((0,0,0),(2,0,0)))
    bad=(Channel(0,compact_mode(4),0),Channel(1,compact_mode(5),0))
    with pytest.raises(ValueError,match='identical'):
        fo.assemble_full(tr,bad,0.)
    with pytest.raises(ValueError,match='duplicate'):
        fo.same_center_blocks(tr,ch1()*2,0.,0)


@pytest.fixture
def saved_cross(tmp_path):
    import json,hashlib,aligned_cross
    from pathlib import Path
    from cr_repro.observables import projectile_speed_au
    ch=small_basis();v=projectile_speed_au(100.)
    tr=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,v)))
    t=-2./v;x=fo.compute_cross_snapshot(tr,ch,t,order=12)
    path=tmp_path/'cross';path.mkdir()
    np.savez_compressed(path/'matrices.npz',**dict(x.arrays))
    meta={'schema':'REAUDIT_STATIC_CROSS_PROBE_V1','status':'COMPLETED_STATIC_PROBE',
          'z':-2.,'order':12,'angular':'bessel','channel_identities':[c.record() for c in ch],
          'kernel_sha256':hashlib.sha256(Path(aligned_cross.__file__).read_bytes()).hexdigest(),
          'matrix_sha256':hashlib.sha256((path/'matrices.npz').read_bytes()).hexdigest(),
          'production_admission':'HOLD','capture_execution_allowed':False,'metadata':x.metadata}
    (path/'RESULT.json').write_text(json.dumps(meta))
    return path,ch,tr,t,x


def test_saved_cross_reader_reuses_exact_matrices(saved_cross):
    path,ch,tr,t,x=saved_cross
    loaded=fo.load_cross_archive(path,tr,ch,t)
    got=fo.assemble_full(tr,ch,t,cross=loaded)
    ti=[i for i,c in enumerate(ch) if c.center==0];pi=[i for i,c in enumerate(ch) if c.center==1]
    np.testing.assert_array_equal(got['S'][np.ix_(ti,pi)],x.arrays['S_tp'])
    assert loaded.metadata['reused_without_cross_reintegration'] is True


@pytest.mark.parametrize('case',['matrix_hash','kernel_hash','channels','time','schema'])
def test_saved_cross_identity_mismatch_fails_closed(saved_cross,case):
    import json
    path,ch,tr,t,_=saved_cross;meta=json.loads((path/'RESULT.json').read_text())
    if case=='matrix_hash':meta['matrix_sha256']='0'*64
    if case=='kernel_hash':meta['kernel_sha256']='0'*64
    if case=='channels':meta['channel_identities'][0]['radial']='wrong'
    if case=='time':t+=.1
    if case=='schema':meta['schema']='UNBOUND_MATRIX_FILES'
    (path/'RESULT.json').write_text(json.dumps(meta))
    with pytest.raises(ValueError):fo.load_cross_archive(path,tr,ch,t)
