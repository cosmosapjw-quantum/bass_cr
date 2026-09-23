import numpy as np
import pytest
from scipy.linalg import expm

from scripts.r3m22_inner_action import bounded_arnoldi_action


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
