#!/usr/bin/env python3
"""Bounded synthetic checks of the R3M26 numerical identities.

No production inputs, wavefunction arrays or propagators are used. The forced
2x2 example uses the Euclidean inner product; the separate Gram example uses
the explicitly declared diagonal mass matrix. Quadrature values are numerical
checks, never certified residual-integral bounds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.linalg import expm


A = np.array([[-.7 + .4j, .6 + .2j], [0., -1.2 - .3j]], dtype=complex)


def triangular_exponential(t: float) -> np.ndarray:
    """Closed-form reference, independent of SciPy's matrix exponential."""
    t = float(t)
    if not math.isfinite(t):
        raise ValueError('time must be finite')
    a, b, d = A[0, 0], A[0, 1], A[1, 1]
    ea, ed = np.exp(a * t), np.exp(d * t)
    return np.array([[ea, b * (ea - ed) / (a - d)], [0., ed]])


def _unit(v) -> np.ndarray:
    v = np.asarray(v, dtype=complex)
    return v / np.linalg.norm(v)


def forced_system_check(*, with_initial_error: bool = True, quadrature_nodes: int = 64) -> dict:
    """Check e=psi-y, r=y'-Ay, Duhamel and the terminal-projector goal identity.

    y(t)=exp(At)(u0-e0)+epsilon*sin(omega*t)*w. The exact convolution of r
    is epsilon*sin(omega*T)*w, an independent endpoint oracle obtained by
    integrating the derivative of exp[A(T-t)]*epsilon*sin(omega*t)*w.
    """
    if isinstance(quadrature_nodes, bool) or not isinstance(quadrature_nodes, int) or quadrature_nodes < 2:
        raise ValueError('quadrature_nodes must be an integer >= 2')
    horizon, epsilon, omega = 1.3, .007, 2.1
    u0 = _unit([1. + .1j, -.3 + .5j])
    w = _unit([.2 + .4j, .7 - .1j])
    e0 = .002 * np.array([1. - .5j, -.2 + .7j]) if with_initial_error else np.zeros(2, complex)
    channel = _unit([1. + .2j, .4 - .3j])
    projector = np.outer(channel, channel.conj())
    psi = expm(A * horizon) @ u0
    forcing_terminal = epsilon * math.sin(omega * horizon) * w
    y = expm(A * horizon) @ (u0 - e0) + forcing_terminal
    error = psi - y
    x, weights = np.polynomial.legendre.leggauss(quadrature_nodes)
    nodes, weights = (x + 1.) * horizon / 2., weights * horizon / 2.
    convolution = np.zeros(2, complex)
    goal_integral = 0j
    residual_integral = 0.
    for t, weight in zip(nodes, weights):
        residual = epsilon * (omega * math.cos(omega * t) * w - math.sin(omega * t) * (A @ w))
        propagator = triangular_exponential(horizon - t)
        # For the Euclidean adjoint z'=-A†z and z(T)=Qy(T).
        z = propagator.conj().T @ (projector @ y)
        convolution += weight * (propagator @ residual)
        goal_integral += weight * np.vdot(z, residual)
        residual_integral += weight * float(np.linalg.norm(residual))
    propagated_initial = triangular_exponential(horizon) @ e0
    reconstructed_error = propagated_initial - convolution
    delta = float(np.linalg.norm(e0)) + residual_integral
    p_y = float(np.linalg.norm(projector @ y) ** 2)
    direct_delta_q = float(np.linalg.norm(projector @ psi) ** 2 - p_y)
    z0 = triangular_exponential(horizon).conj().T @ (projector @ y)
    initial_term = float(2. * np.vdot(z0, e0).real)
    residual_term = float(-2. * goal_integral.real)
    quadratic_term = float(np.linalg.norm(projector @ error) ** 2)
    scalar_bound = 2. * math.sqrt(p_y) * delta + delta * delta
    hermitian_part = (A + A.conj().T) / 2.
    return {
        'inner_product': 'EUCLIDEAN_COMPLEX',
        'dimension': 2, 'horizon': horizon, 'epsilon': epsilon, 'omega': omega,
        'quadrature_nodes': quadrature_nodes,
        'hermitian_part_largest_eigenvalue': float(np.linalg.eigvalsh(hermitian_part)[-1]),
        'nonnormal_commutator_norm': float(np.linalg.norm(A.conj().T @ A - A @ A.conj().T)),
        'terminal_propagator_operator_norm': float(np.linalg.norm(expm(A * horizon), 2)),
        'closed_exponential_minus_pade_norm': float(np.linalg.norm(triangular_exponential(horizon) - expm(A * horizon))),
        'initial_error_norm': float(np.linalg.norm(e0)),
        'terminal_state_error_norm': float(np.linalg.norm(error)),
        'duhamel_error_norm': float(np.linalg.norm(error - reconstructed_error)),
        'convolution_minus_analytic_forcing_norm': float(np.linalg.norm(convolution - forcing_terminal)),
        'wrong_residual_sign_error_norm': float(np.linalg.norm(error - (propagated_initial + convolution))),
        'integral_residual_norm_quadrature': residual_integral,
        'contraction_expression_delta': delta,
        'contraction_bound_holds_in_this_example': bool(np.linalg.norm(error) <= delta),
        'certified_global_bound': False,
        'quadrature_semantics': 'NUMERIC_CHECK_OF_SUFFICIENT_BOUND_EXPRESSION_NOT_CERTIFIED_QUADRATURE',
        'goal': {
            'direct_delta_q': direct_delta_q,
            'initial_term': initial_term, 'residual_term': residual_term,
            'linear_terms': initial_term + residual_term,
            'quadratic_terminal_term': quadratic_term,
            'identity_absolute_residual': abs(direct_delta_q - initial_term - residual_term - quadratic_term),
            'adjoint_integral_minus_analytic_endpoint': float(abs(goal_integral - np.vdot(projector @ y, forcing_terminal))),
            'scalar_observable_bound': float(scalar_bound),
            'scalar_observable_bound_holds': bool(abs(direct_delta_q) <= scalar_bound),
        },
    }


def _gram_probability(basis: np.ndarray, state: np.ndarray, mass: np.ndarray):
    gram = basis.conj().T @ (mass[:, None] * basis)
    overlap = basis.conj().T @ (mass * state)
    probability = float(np.vdot(overlap, np.linalg.solve(gram, overlap)).real)
    projector = basis @ np.linalg.solve(gram, basis.conj().T * mass[None, :])
    return probability, projector


def projector_check() -> dict:
    """Compare weighted Gram solve with independent whitened QR geometry."""
    mass = np.array([.4, 1.1, .7, 1.8])
    basis = np.array([[1., .3 + .2j], [.2 - .1j, .8], [.4j, -.2 + .3j], [.3, .5j]])
    state = np.array([.4 + .1j, -.2 + .5j, .3 - .2j, -.1 + .3j])
    p, projector = _gram_probability(basis, state, mass)
    orth, _ = np.linalg.qr(np.sqrt(mass)[:, None] * basis, mode='reduced')
    whitened_state = np.sqrt(mass) * state
    qr_probability = float(np.linalg.norm(orth.conj().T @ whitened_state) ** 2)
    qr_projector = orth @ orth.conj().T
    whitened_projector = np.sqrt(mass)[:, None] * projector / np.sqrt(mass)[None, :]
    transform = np.array([[1.4 + .2j, .5 - .1j], [.2 + .1j, .8 - .3j]])
    p_changed, _ = _gram_probability(basis @ transform, state, mass)
    p_phased, _ = _gram_probability(basis @ np.diag(np.exp(1j * np.array([.37, -1.2]))), state, mass)
    # Both columns are normalized. Their overlap still double-counts e1.
    bad_basis = np.array([[1., 1. / math.sqrt(2.)], [0., 1. / math.sqrt(2.)], [0., 0.]])
    bad_state = np.array([1., 0., 0.])
    bad_p, _ = _gram_probability(bad_basis, bad_state, np.ones(3))
    changed_bad = bad_basis @ np.array([[1., .4], [.2, 1.1]])
    changed_p, _ = _gram_probability(changed_bad, bad_state, np.ones(3))
    return {
        'dimension': 4, 'span_rank': 2, 'mass_diagonal': mass.tolist(),
        'state_weighted_norm_squared': float(np.vdot(state, mass * state).real),
        'gram_probability': p, 'qr_probability': qr_probability,
        'weighted_gram_minus_qr_probability': abs(p - qr_probability),
        'weighted_projector_minus_qr_norm': float(np.linalg.norm(whitened_projector - qr_projector)),
        'basis_change_probability_difference': abs(p - p_changed),
        'channel_phase_probability_difference': abs(p - p_phased),
        'projector_idempotence_norm': float(np.linalg.norm(projector @ projector - projector)),
        'whitened_hermiticity_norm': float(np.linalg.norm(whitened_projector.conj().T - whitened_projector)),
        'weighted_operator_norm': float(np.linalg.norm(whitened_projector, 2)),
        'nonorthogonal_counterexample': {
            'each_basis_vector_norm_squared': np.sum(bad_basis ** 2, axis=0).tolist(),
            'state_norm_squared': 1.,
            'raw_overlap_sum': float(np.linalg.norm(bad_basis.T @ bad_state) ** 2),
            'correct_projected_probability': bad_p,
            'changed_basis_raw_overlap_sum': float(np.linalg.norm(changed_bad.T @ bad_state) ** 2),
            'changed_basis_correct_probability': changed_p,
        },
    }


def assumption_counterexamples() -> dict:
    """Eigenvalue stability is weaker than dissipation; weighted != Euclidean."""
    stable = np.array([[-1., 4.], [0., -1.]])
    mass = np.array([1., 4.])
    _, q = _gram_probability(np.ones((2, 1)), np.array([1., 0.]), mass)
    qw = np.sqrt(mass)[:, None] * q / np.sqrt(mass)[None, :]
    return {
        'stable_nondissipative': {
            'eigenvalue_real_parts': np.linalg.eigvals(stable).real.tolist(),
            'hermitian_part_largest_eigenvalue': float(np.linalg.eigvalsh((stable + stable.T) / 2)[-1]),
            'propagator_norm_at_t_point3': float(np.linalg.norm(expm(.3 * stable), 2)),
        },
        'weighted_projector': {
            'mass_diagonal': mass.tolist(),
            'euclidean_operator_norm': float(np.linalg.norm(q, 2)),
            'weighted_operator_norm': float(np.linalg.norm(qw, 2)),
            'euclidean_nonhermiticity_norm': float(np.linalg.norm(q - q.T)),
        },
    }


def run_foundation_checks() -> dict:
    forced = [forced_system_check(with_initial_error=flag) for flag in (False, True)]
    gram = projector_check()
    counter = assumption_counterexamples()
    checks = [
        all(x['hermitian_part_largest_eigenvalue'] < 0. and x['nonnormal_commutator_norm'] > .1
            and x['closed_exponential_minus_pade_norm'] < 2e-14
            and x['duhamel_error_norm'] < 2e-14 and x['convolution_minus_analytic_forcing_norm'] < 2e-14
            and x['goal']['identity_absolute_residual'] < 2e-14
            and x['goal']['adjoint_integral_minus_analytic_endpoint'] < 2e-14
            and x['contraction_bound_holds_in_this_example']
            and x['goal']['scalar_observable_bound_holds'] for x in forced),
        all(gram[key] < 2e-14 for key in ('weighted_gram_minus_qr_probability',
            'weighted_projector_minus_qr_norm', 'basis_change_probability_difference',
            'channel_phase_probability_difference', 'projector_idempotence_norm', 'whitened_hermiticity_norm')),
        abs(gram['weighted_operator_norm'] - 1.) < 2e-14,
        counter['stable_nondissipative']['propagator_norm_at_t_point3'] > 1.,
        counter['weighted_projector']['euclidean_operator_norm'] > 1.,
        abs(counter['weighted_projector']['weighted_operator_norm'] - 1.) < 2e-14,
    ]
    return {
        'schema': 'R3M26_FOUNDATION_SYNTHETIC_V1',
        'evidence_scope': 'SYNTHETIC_SMALL_MATRIX_ALGEBRA_ONLY',
        'algebra_checks_passed': all(checks),
        'production_admitted': False, 'production_global_error_evaluated': False,
        'full_collision_count': 0, 'production_array_inputs': False,
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'forced_systems': forced, 'weighted_gram_projector': gram,
        'assumption_counterexamples': counter,
    }


def write_new(path: Path, result: dict) -> None:
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        stream.write(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run_foundation_checks()
    write_new(args.output, result)
    print(json.dumps({'output': str(args.output), 'algebra_checks_passed': result['algebra_checks_passed'],
                      'production_admitted': False}))
    return 0 if result['algebra_checks_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
