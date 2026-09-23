"""Full-H temporal decomposition tests; bounded same-grid oracles only."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("r3m19_fullh", ROOT / "scripts/r3m19_fullh_diagnostic.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


@pytest.mark.parametrize("velocity", [0.0, 1e-12, 2.0, -2.0])
def test_projectile_integral_matches_independent_quadrature(velocity):
    rho=np.array([0.3,0.8,2.]); z=np.array([-1.2,0.1,1.3]); a,b=-.21,.37
    result=MOD.projectile_integral(rho,z,velocity,a,b)
    oracle=np.array([quad(lambda t:-1/np.sqrt(r*r+(q-velocity*t)**2),a,b,epsabs=1e-13)[0] for r,q in zip(rho,z)])
    assert np.max(abs(result-oracle)) < 2e-13


def test_potential_integral_rejects_nuclear_singularity():
    with pytest.raises(ValueError,match="rho"):
        MOD.projectile_integral([0],[1],1,-1,1)


def test_constant_nonhermitian_H_has_exact_mid_avg_cf4():
    K=np.array([[.7,.2],[.2,1.2]],complex); target=np.array([-.3,-.6])
    rho=np.array([.5,.8]); z=np.array([.2,-.4]); W=np.array([.1,.3])
    model=MOD.make_model(K,target,rho,z,0.,W)
    psi=np.array([.7,.2+.3j]); dt=.13
    exact=expm(dt*MOD.generator(model,0))@psi
    for method in [MOD.midpoint_step,MOD.averaged_step,MOD.cf4_step]:
        assert np.max(abs(method(model,psi,-.07,dt)-exact)) < 3e-15
    assert np.vdot(exact,exact).real < np.vdot(psi,psi).real


def test_diagonal_moving_generator_average_is_exact():
    model=MOD.make_model(np.zeros((2,2)),[-.2,-.4],[.3,.8],[.2,-.4],2.,[.1,.3])
    psi=np.array([.7,.2+.3j]); start=-.1; dt=.2
    ref=MOD.dop853_reference(model,psi,start,start+dt,dv=.2)
    exact=MOD.averaged_step(model,psi,start,dt)
    assert np.linalg.norm(exact-ref["state"]) < 3e-12
    assert abs(ref["cap_balance_residual"]) < 2e-12


def test_vector_cross_terms_restore_squared_error_before_alignment():
    rng=np.random.default_rng(19)
    states=[rng.normal(size=4)+1j*rng.normal(size=4) for _ in range(4)]
    result=MOD.decompose_vectors(*states,dv=.3)
    assert result["vector_closure_norm"] < 3e-15
    assert abs(result["squared_norm_closure_residual"]) < 5e-14
    assert result["phase_alignment_used_for_decomposition"] is False
    assert any(abs(v[1])>1e-5 for v in result["complex_gram"].values())


def test_cap_derivative_sign_and_augmented_loss_balance():
    model=MOD.make_model(np.array([[0,.4],[.4,1.]]),[-.2,-.4],[.3,.8],[.2,-.4],2.,[.1,.3])
    psi=np.array([.7,.2+.3j]); dv=.2
    A=MOD.generator(model,.05)
    direct=2*np.vdot(psi,A@psi).real*dv
    expected=-2*np.sum(model["W"]*abs(psi)**2)*dv
    assert direct == pytest.approx(expected,abs=1e-15)
    ref=MOD.dop853_reference(model,psi,-.1,.1,dv=dv)
    assert ref["absorbed_probability"]>0
    assert ref["norm_final"]<ref["norm_initial"]
    assert abs(ref["cap_balance_residual"])<2e-12


@pytest.mark.parametrize("kwargs", [
    {"shape":(10,8,8)}, {"shape":(0,4,4)}, {"shape":(True,4,4)},
    {"shape":(4,4,4),"spacing":np.nan}, {"steps":(4,8,65)},
    {"horizon":np.inf}, {"horizon":-1}, {"center":np.nan},
])
def test_invalid_or_excessive_budget_rejected_before_dense_allocation(monkeypatch,kwargs):
    monkeypatch.setattr(MOD,"dense_fourier_hamiltonian",lambda *a,**k:(_ for _ in ()).throw(AssertionError("allocated before gate")))
    with pytest.raises((ValueError,MemoryError)):
        MOD.run_case(**kwargs)


def test_nonfinite_or_antidamping_model_rejected():
    with pytest.raises(ValueError):
        MOD.make_model(np.eye(2),[1,np.nan],[.2,.3],[0,0],1,[0,0])
    with pytest.raises(ValueError,match="CAP"):
        MOD.make_model(np.eye(2),[1,2],[.2,.3],[0,0],1,[-.1,0])


def test_fullh_cf4_is_fourth_order_and_decomposition_closes():
    result=MOD.run_case(shape=(4,4,4),spacing=.7,horizon=.2,steps=(4,8,16),center=0.,cap_on=False)
    assert result["reference_refinement_resolved"]
    assert all(3.7<p<4.3 for p in result["observed_orders"]["CF4_fullH"])
    assert all(1.8<p<2.2 for p in result["observed_orders"]["S_mid"])
    assert all(row["decomposition"]["vector_closure_norm"]<1e-14 for row in result["ladder"])
    assert result["production_admission"] is False
    assert result["continuum_spatial_validation"] is False


def test_moving_cap_case_is_contractive_and_ledger_closed():
    result=MOD.run_case(shape=(2,2,2),spacing=.7,horizon=.2,steps=(2,4,8),center=-.3,cap_on=True)
    assert result["reference"]["absorbed_probability"]>0
    assert abs(result["reference"]["cap_balance_residual"])<2e-11
    for row in result["ladder"]:
        for method in row["methods"].values():
            assert method["norm_final"]<=method["norm_initial"]+1e-13
            assert method["maximum_step_norm_increase"]<1e-13


def test_create_only_output_preserves_bytes(tmp_path):
    path=tmp_path/"report.json"; MOD.write_new(path,{"v":1}); before=path.read_bytes()
    with pytest.raises(FileExistsError):MOD.write_new(path,{"v":2})
    assert path.read_bytes()==before
