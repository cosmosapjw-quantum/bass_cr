"""Synthetic matrix tests only; no BASS evaluator or transport is imported."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from projector_rate_probe import rate_matrices, adj


def fixture():
    S=np.array([[2,1/3,1j/5],[1/3,3,1/4],[-1j/5,1/4,4]],complex)
    H=np.array([[1,1j/7,2/9],[-1j/7,2,1/8],[2/9,1/8,3]],complex)
    D=np.array([[1j/8,1/11,0],[1j/9,-1j/7,1/13],[1/15,0,1j/10]],complex)
    J=np.eye(3,dtype=complex)[:,[1,2]]
    return S,H,D,J


def test_moving_metric_sign_and_projector():
    S,H,D,J=fixture(); a=rate_matrices(S,H,D,J,hbar=1.)
    assert a['metric_identity_residual']<1e-14
    np.testing.assert_allclose(a['Q']@np.linalg.solve(S,a['Q']),a['Q'],atol=1e-14)
    np.testing.assert_allclose(a['W'],adj(a['W']),atol=1e-14)


def test_two_state_limit_and_nonzero_coupling_zero_instantaneous_population_rate():
    S=np.eye(2);H=np.array([[0,3],[3,0]],complex);D=np.zeros((2,2));J=np.eye(2)[:,[1]]
    a=rate_matrices(S,H,D,J,hbar=2.)
    np.testing.assert_allclose(a['W'],[[0,1.5j],[-1.5j,0]],atol=1e-14)
    assert a['rho']==pytest.approx(1.5)
    c=np.array([1.,0.]);assert np.vdot(c,a['W']@c)==0


def test_time_dependent_coordinate_covariance():
    S,H,D,J=fixture();a=rate_matrices(S,H,D,J,hbar=1.)
    R=np.array([[2,1/3,0],[0,1,1/5],[0,0,1.5]],complex)
    Rd=np.array([[1/7,0,1j/11],[0,-1/8,0],[0,0,1/10]],complex)
    Sp=adj(R)@S@R;Hp=adj(R)@H@R;Dp=adj(R)@D@R+adj(R)@S@Rd
    Jp=np.linalg.solve(R,J);Jdp=-np.linalg.solve(R,Rd@Jp)
    b=rate_matrices(Sp,Hp,Dp,Jp,hbar=1.,Jdot=Jdp)
    np.testing.assert_allclose(b['W'],adj(R)@a['W']@R,atol=2e-14)
    assert b['rho']==pytest.approx(a['rho'],rel=1e-13)


def test_projector_derivative_against_local_synthetic_difference():
    S,H,D,J=fixture();jd=np.array([[.2,0],[0,0],[.1,.3]])
    a=rate_matrices(S,H,D,J,hbar=1.,Jdot=jd);delta=1e-5;Sd=D+adj(D)
    qp=rate_matrices(S+delta*Sd,H,D,J+delta*jd,hbar=1.)['Q']
    qm=rate_matrices(S-delta*Sd,H,D,J-delta*jd,hbar=1.)['Q']
    np.testing.assert_allclose((qp-qm)/(2*delta),a['Qdot'],atol=2e-10)


def test_generalized_rate_envelope_for_complex_states():
    S,H,D,J=fixture();a=rate_matrices(S,H,D,J,hbar=1.)
    rng=np.random.default_rng(154)
    for _ in range(20):
        c=rng.normal(size=3)+1j*rng.normal(size=3)
        assert abs(np.vdot(c,a['W']@c)) <= np.vdot(c,S@c).real*a['rho']+1e-12


def test_subspace_relabeling_invariance():
    S,H,D,J=fixture();a=rate_matrices(S,H,D,J,hbar=1.)
    U=np.array([[2,1j],[0,3]],complex);b=rate_matrices(S,H,D,J@U,hbar=1.)
    np.testing.assert_allclose(a['Q'],b['Q'],atol=2e-14)
    assert a['rho']==pytest.approx(b['rho'],rel=1e-13)


def test_raw_generator_block_changes_under_scaling_but_rate_does_not():
    S=np.eye(2);H=np.array([[0,3],[3,0]],complex);D=np.zeros((2,2));J=np.eye(2)[:,[1]]
    R=np.diag([1.,100.]);a=rate_matrices(S,H,D,J,hbar=1.)
    Sp=adj(R)@S@R;Hp=adj(R)@H@R
    b=rate_matrices(Sp,Hp,D,np.linalg.solve(R,J),hbar=1.)
    assert np.linalg.solve(Sp,Hp)[0,1]==pytest.approx(300.)
    assert b['rho']==pytest.approx(a['rho'])


def test_global_phase_connection_changes_K_ratio_not_W():
    S,H,D,J=fixture();a=rate_matrices(S,H,D,J,hbar=1.)
    shifted=rate_matrices(S,H,D-1j*100*S,J,hbar=1.)
    np.testing.assert_allclose(a['W'],shifted['W'],atol=1e-12)
    assert shifted['rho']==pytest.approx(a['rho'],abs=1e-12)

@pytest.mark.parametrize('bad_hbar',[0,-1,float('nan'),float('inf'),True])
def test_invalid_hbar_rejected(bad_hbar):
    with pytest.raises(ValueError):rate_matrices(*fixture(),hbar=bad_hbar)

def test_indefinite_metric_rejected():
    S,H,D,J=fixture();S[0,0]=-1
    with pytest.raises(ValueError):rate_matrices(S,H,D,J,hbar=1.)

def test_nonhermitian_H_rejected():
    S,H,D,J=fixture();H[0,1]+=1
    with pytest.raises(ValueError):rate_matrices(S,H,D,J,hbar=1.)
