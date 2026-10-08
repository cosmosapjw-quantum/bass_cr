"""Host oracle for the bounded matrix-free full-H sidecar."""
import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from cr_repro.r3m11 import ControlledTDLRunner
from scripts.r3m17_reference import dense_fourier_hamiltonian
from scripts.r3m19_fullh_diagnostic import (
    CF_A, CF_B, CF_C1, CF_C2, generator as dense_generator,
    make_model, projectile_integral,
)
from scripts.r3m20_matrix_free import MatrixFreeFullH, arnoldi_expm_action
from scripts.r3m20_short_window import ProductionBufferedStep


def tiny_config(shape=(4, 4, 4), cap=True, b=.9):
    return dict(energy_keV_per_u=100., b=b, backend="numpy", dt=.025,
                grid=dict(xlim=[-shape[0]*.35, shape[0]*.35],
                          ylim=[-shape[1]*.35, shape[1]*.35],
                          zlim=[-shape[2]*.35, shape[2]*.35], dx=.7),
                z_start=-2., z_stop=2., initial_state="analytic", project_nmax=1,
                absorber_width=.7 if cap else 0., absorber_power=.125,
                absorber_reference_dt=.05, capture_plane=0.)


def dense_for_runner(runner):
    shape=runner.spec.shape()
    target=np.asarray(runner.Vtarget).reshape(shape)
    H=dense_fourier_hamiltonian(shape,runner.spec.dx,target)
    K=H-np.diag(target.ravel())
    X,Y,Z=np.meshgrid(*runner.spec.axes(),indexing="ij")
    rho=np.hypot(X-runner.b,Y).ravel()
    W=-np.log(np.asarray(runner.mask).ravel())/runner.cfg["absorber_reference_dt"]
    return make_model(K,target.ravel(),rho,Z.ravel(),runner.v,W)


@pytest.mark.parametrize("shape,cap,velocity_sign", [((4,4,4),False,1),((4,4,4),True,1),
                                                  ((4,4,4),True,-1),((4,4,6),True,0)])
def test_fft_generator_matches_independent_dense(shape,cap,velocity_sign):
    runner=ControlledTDLRunner(tiny_config(shape,cap))
    mf=MatrixFreeFullH(runner,velocity_override=runner.v*velocity_sign)
    dense=dense_for_runner(runner)
    dense["velocity"]=runner.v*velocity_sign
    rng=np.random.default_rng(20260923)
    psi=rng.normal(size=shape)+1j*rng.normal(size=shape)
    t=.137
    got=mf.generator_matvec(psi,t)
    want=(dense_generator(dense,t)@psi.ravel()).reshape(shape)
    assert np.linalg.norm(got-want)/np.linalg.norm(want)<2e-13
    dt=.071
    got_avg=mf.averaged_generator_matvec(psi,t,dt)
    phase=dt*dense["target"]+projectile_integral(dense["rho"],dense["z"],dense["velocity"],t,t+dt)
    integrated=-1j*(dt*dense["K"]+np.diag(phase))-np.diag(dt*dense["W"])
    want_avg=(integrated@psi.ravel()).reshape(shape)
    assert np.linalg.norm(got_avg-want_avg)/np.linalg.norm(want_avg)<2e-13


def test_nonhermitian_arnoldi_action_matches_dense_and_refines():
    A=np.array([[.1+.2j,.3-.4j,0],[.2+.1j,-.7+.3j,.4],[-.2j,.1,-.1-.5j]])
    psi=np.array([.7+.1j,-.3+.2j,.4-.8j]); dt=.13
    exact=expm(dt*A)@psi
    coarse,ci=arnoldi_expm_action(lambda x:A@x,psi,dt,tol=1e-3,max_basis=2)
    fine,fi=arnoldi_expm_action(lambda x:A@x,psi,dt,tol=1e-12,max_basis=3)
    assert np.linalg.norm(fine-exact)<2e-13
    assert np.linalg.norm(fine-exact)<np.linalg.norm(coarse-exact)
    assert fi["matvec_count"]<=3 and fi["converged"]
    assert ci["matvec_count"]<=2


def test_cf4_uses_two_full_nonhermitian_actions():
    runner=ControlledTDLRunner(tiny_config((2,2,4),True))
    mf=MatrixFreeFullH(runner)
    dense=dense_for_runner(runner)
    psi=np.arange(16,dtype=float).reshape(2,2,4).astype(complex)+.3j
    psi/=np.linalg.norm(psi)
    t=-.09;dt=.04
    got,info=mf.step(psi,t,dt,method="cf4",tol=1e-12,max_basis=16)
    A1,A2=dense_generator(dense,t+CF_C1*dt),dense_generator(dense,t+CF_C2*dt)
    want=expm(dt*(CF_B*A1+CF_A*A2))@expm(dt*(CF_A*A1+CF_B*A2))@psi.ravel()
    assert np.linalg.norm(got.ravel()-want)<2e-11
    assert len(info["actions"])==2
    assert all(action["converged"] for action in info["actions"])
    scaled,scaled_info=mf.step(psi,t,dt,method="cf4",tol=1e-12,
                               max_basis=12,action_substeps=4)
    assert np.linalg.norm(scaled.ravel()-want)<2e-11
    assert scaled_info["action_substeps"]==4 and len(scaled_info["actions"])==8


def test_moving_cap_cf4_outer_and_oracle_refinement_are_separate():
    runner=ControlledTDLRunner(tiny_config((2,2,4),True))
    mf=MatrixFreeFullH(runner)
    dense=dense_for_runner(runner)
    psi=np.arange(16,dtype=float).astype(complex)+.4j
    psi/=np.linalg.norm(psi)
    t0=-.08;horizon=.16
    def ode(max_step):
        return solve_ivp(lambda t,y:dense_generator(dense,t)@y,(t0,t0+horizon),psi,
                         method="DOP853",rtol=2e-13,atol=2e-15,
                         max_step=max_step,t_eval=[t0+horizon]).y[:,-1]
    ref,ref_fine=ode(.01),ode(.005)
    errors=[]
    for n in (2,4,8):
        state=psi.reshape(2,2,4).copy()
        for j in range(n):
            state,info=mf.step(state,t0+j*horizon/n,horizon/n,method="cf4",
                               tol=1e-12,max_basis=16)
            assert all(x["converged"] for x in info["actions"])
        errors.append(np.linalg.norm(state.ravel()-ref_fine))
    assert np.linalg.norm(ref-ref_fine)<.01*min(errors)
    assert errors[0]>8*errors[1] and errors[1]>8*errors[2]
    state_lo=psi.reshape(2,2,4).copy();state_hi=state_lo.copy()
    for j in range(4):
        start=t0+j*horizon/4
        state_lo,_=mf.step(state_lo,start,horizon/4,method="cf4",tol=1e-9,max_basis=16)
        state_hi,_=mf.step(state_hi,start,horizon/4,method="cf4",tol=1e-12,max_basis=16)
    assert np.linalg.norm(state_lo-state_hi)<.01*errors[1]


def test_action_limits_reject_before_large_allocation():
    A=np.eye(4,dtype=complex);psi=np.ones(4,dtype=complex)
    with pytest.raises(ValueError):
        arnoldi_expm_action(lambda x:A@x,psi,.1,tol=0,max_basis=4)
    with pytest.raises(ValueError):
        arnoldi_expm_action(lambda x:A@x,psi,.1,tol=1e-12,max_basis=0)


def test_production_buffer_sidecar_matches_frozen_step_on_tiny_grid():
    runner=ControlledTDLRunner(tiny_config((4,4,4),True))
    rng=np.random.default_rng(20)
    state=(rng.normal(size=runner.spec.shape())+1j*rng.normal(size=runner.spec.shape())).astype(complex)
    candidate=ProductionBufferedStep(runner)
    frozen=runner.step(state.copy(),.13)
    buffered=candidate.step(state.copy(),.13)
    assert np.linalg.norm(frozen-buffered)/np.linalg.norm(frozen)<5e-13


def test_actual_gpu_matrix_free_action_matches_cpu():
    cp=pytest.importorskip("cupy",reason="CuPy/GPU unavailable")
    try:
        if cp.cuda.runtime.getDeviceCount()<1:
            pytest.skip("No CUDA device")
        gpu_runner=ControlledTDLRunner(dict(tiny_config((2,2,4),True),backend="cupy"))
        cpu_runner=ControlledTDLRunner(tiny_config((2,2,4),True))
        state=np.arange(16,dtype=np.float64).reshape(2,2,4).astype(complex)+.2j
        state/=np.linalg.norm(state)
        gpu=MatrixFreeFullH(gpu_runner)
        cpu=MatrixFreeFullH(cpu_runner)
        got,gi=gpu.step(cp.asarray(state),-.04,.03,method="cf4",tol=1e-12,max_basis=16)
        want,ci=cpu.step(state,-.04,.03,method="cf4",tol=1e-12,max_basis=16)
        assert np.linalg.norm(cp.asnumpy(got)-want)<2e-11
        assert gi["total_fft_matvec"]<=32 and ci["total_fft_matvec"]<=32
    except (ImportError,cp.cuda.runtime.CUDARuntimeError) as exc:
        pytest.skip(f"CUDA runtime/FFT unavailable: {exc}")
