import numpy as np
import pytest
from scipy.linalg import expm

from scripts.r3m22_inner_action import bounded_arnoldi_action
from scripts.r3m22_cpu_oracle import case as cpu_oracle_case


@pytest.mark.parametrize("seed", [21, 47, 83])
def test_contractively_bounded_arnoldi_against_independent_dense_expm(seed):
    rng = np.random.default_rng(seed)
    raw = rng.normal(size=(6, 6)) + 1j * rng.normal(size=(6, 6))
    hamiltonian = (raw + raw.conj().T) / 2
    absorber = np.diag(np.linspace(.01, .5, 6))
    generator = -1j * hamiltonian - absorber
    initial = rng.normal(size=6) + 1j * rng.normal(size=6)
    initial = initial.astype(np.complex128)
    initial /= np.linalg.norm(initial)
    dt = .08
    observed, info = bounded_arnoldi_action(lambda x: generator @ x, initial, dt,
                                            physical_scale=1., physical_budget=2e-8,
                                            max_basis=6)
    independent = expm(dt * generator) @ initial
    true_error = np.linalg.norm(observed - independent)
    assert info["converged"] and info["physical_upper_bound"] <= 2e-8
    assert true_error <= info["physical_upper_bound"] + 2e-14
    assert np.linalg.norm(observed) <= 1 + 2e-14


def test_insufficient_basis_fails_closed_even_with_finite_action():
    generator = np.array([[-.1-1j, .2j], [.2j, -.3+2j]], dtype=np.complex128)
    initial = np.array([1., .2j], dtype=np.complex128)
    with pytest.raises(RuntimeError, match="inner action unresolved"):
        bounded_arnoldi_action(lambda x: generator @ x, initial, .3,
                               physical_scale=1., physical_budget=1e-18,
                               max_basis=1)


def test_tiny_oracle_strict_gate_uses_finest_ode_error_and_n32_repeats():
    result = cpu_oracle_case((4, 4, 4), True, 1, strict=True)
    finest = min(result["methods"][str(n)]["error_to_ode"] for n in (4, 8, 16, 32))
    assert result["gate_semantics"] == "ONE_PERCENT_OF_MINIMUM_ERROR_TO_INDEPENDENT_ODE_N32_REPEATS"
    assert np.isclose(result["one_percent_threshold"], .01 * finest,
                      rtol=1e-14, atol=0)
    assert not np.isclose(result["one_percent_threshold"],
                          .01 * result["distances"]["outer_4_to_8"],
                          rtol=1e-14, atol=0)
    assert result["oracle_resolved_at_one_percent"]
    assert result["distances"]["inner_32_repeat"] < result["one_percent_threshold"]
    assert result["distances"]["substep_32_repeat"] < result["one_percent_threshold"]
