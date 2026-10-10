# SPDX-License-Identifier: GPL-3.0-only
"""Independent mathematical checks for the fixed PHYS02B candidate.

The branching toy constructs its own small count-space operator.  DOP853
shares the supplied production generator and therefore checks propagation,
not atomic physics or generator construction.  Conservation functionals are
assembled here from the documented state meanings; Cascade.functionals,
Cascade.project, and Cascade._generator are never called by these checks.

Public integration point: run_oracles(cascade, source_vectors).
Importing this module needs no atomic tables and constructs no Cascade.
Running it as a script executes the standalone branching toy only.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
import scipy
from scipy import sparse
from scipy.integrate import solve_ivp
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / 'state' / 'SCIENTIFIC_CONTRACT.json'
FIXED_TOLERANCES = {
    'exact_branching_toy_relative': 2.e-11,
    'time_oracle_normalized_linf': 2.e-9,
    'generator_energy_number_relative': 5.e-12,
}
DOP853_RTOL = 1.e-10
DOP853_ATOL = 1.e-13
T_END_S = 1.e10


def _contract_identity():
    raw = CONTRACT_PATH.read_bytes()
    contract = json.loads(raw)
    for name, value in FIXED_TOLERANCES.items():
        if contract['tolerances'][name] != value:
            raise ValueError('FROZEN_ORACLE_TOLERANCE_MISMATCH: ' + name)
    return {
        'contract_sha256': hashlib.sha256(raw).hexdigest(),
        'contract_tolerances': dict(FIXED_TOLERANCES),
        'numpy_version': np.__version__,
        'scipy_version': scipy.__version__,
        'oracle_role': 'verification implementation participant; not final decision reviewer',
    }


def _exact_ramp_parent_and_events(rate, amplitude, u):
    """Solve P'=-rate*P+amplitude*u, J'=rate*P from zero.

P = amplitude*(rate*u + exp(-rate*u) - 1)/rate**2.
J = amplitude*u**2/2 - P.  A short Taylor form avoids subtraction
of nearly equal injected and surviving populations at small rate*u.
This calculation does not use a matrix exponential or the supplied G.
"""
    injected = amplitude * u * u / 2
    if rate == 0 or u == 0:
        return injected, 0.
    x = rate * u
    if x < .1:
        parent = amplitude * u * u * math.fsum(
            (-x)**k / math.factorial(k + 2) for k in range(19))
        events = amplitude * u * u * math.fsum(
            -(-x)**k / math.factorial(k + 2) for k in range(1, 19))
    else:
        parent = amplitude * (x + math.expm1(-x)) / rate**2
        events = injected - parent
    return parent, events


def exact_single_event_ramp_oracle():
    """Single ionization P(E) -> S(W) + F(E-B-W), with inert daughters."""
    tolerance = FIXED_TOLERANCES['exact_branching_toy_relative']
    # Arbitrary exact toy energies, not a fitted HI or HeI atomic model.
    energy, binding, slow = 80., 20., 15.
    fast = energy - binding - slow
    amplitude = .7
    # State: parent count, slow count, fast count, binding energy, event count.
    energy_functional = np.array([energy, slow, fast, 1., 0.])
    number_functional = np.array([1., 1., 1., 0., -1.])
    rows = []
    maximum_relative = 0.
    maximum_energy_residual = 0.
    maximum_number_residual = 0.
    maximum_binding_residual = 0.
    zero_time_or_rate_ok = True
    toy_column_energy_error = 0.
    toy_column_number_error = 0.

    for rate in (0., .125, 2., 16.):
        toy_generator = np.zeros((5, 5))
        toy_generator[:, 0] = rate * np.array([-1., 1., 1., binding, 1.])
        toy_column_energy_error = max(toy_column_energy_error,
            float(np.max(np.abs(energy_functional @ toy_generator))))
        toy_column_number_error = max(toy_column_number_error,
            float(np.max(np.abs(number_functional @ toy_generator))))
        # Independent 7x7 augmentation; no production constructor/augmentation.
        augmented = np.zeros((7, 7))
        augmented[:5, :5] = toy_generator
        augmented[0, 5] = amplitude
        augmented[5, 6] = 1.
        initial = np.zeros(7)
        initial[6] = 1.
        for u in (0., .125, .5, 1.):
            parent, events = _exact_ramp_parent_and_events(rate, amplitude, u)
            exact = np.array([parent, events, events, binding * events, events])
            observed = (expm(u * augmented) @ initial)[:5]
            if not np.all(np.isfinite(observed)):
                raise ArithmeticError('NONFINITE_TOY_EXPONENTIAL')
            injected = amplitude * u * u / 2
            difference = np.abs(observed - exact)
            nonzero = exact != 0
            relative = float(np.max(difference[nonzero] / np.abs(exact[nonzero]))) if np.any(nonzero) else 0.
            if np.any(~nonzero):
                zero_time_or_rate_ok = zero_time_or_rate_ok and bool(np.all(observed[~nonzero] == 0.))
            count_scale = injected if injected > 0 else 1.
            energy_scale = energy * count_scale
            energy_error = abs(float(energy_functional @ observed) - energy * injected) / energy_scale
            number_error = abs(float(number_functional @ observed) - injected) / count_scale
            binding_error = abs(float(observed[3] - binding * observed[4])) / (binding * count_scale)
            maximum_relative = max(maximum_relative, relative)
            maximum_energy_residual = max(maximum_energy_residual, energy_error)
            maximum_number_residual = max(maximum_number_residual, number_error)
            maximum_binding_residual = max(maximum_binding_residual, binding_error)
            rows.append({
                'rate_per_u': rate, 'u': u,
                'injected_electrons': injected,
                'exact_parent': parent, 'exact_events': events,
                'expm_parent': float(observed[0]),
                'expm_slow': float(observed[1]),
                'expm_fast': float(observed[2]),
                'expm_binding_energy_eV': float(observed[3]),
                'expm_events': float(observed[4]),
                'expm_free_electron_count': float(np.sum(observed[:3])),
                'expected_free_electron_count': injected + events,
                'max_component_relative_error': relative,
            })

    passed = (maximum_relative <= tolerance and zero_time_or_rate_ok
              and maximum_energy_residual <= tolerance
              and maximum_number_residual <= tolerance
              and maximum_binding_residual <= tolerance
              and toy_column_energy_error == 0.
              and toy_column_number_error == 0.)
    return {
        'passed': bool(passed), 'status': 'PASS' if passed else 'FAIL',
        'tolerance': tolerance,
        'max_component_relative_error': maximum_relative,
        'max_energy_ledger_relative_residual': maximum_energy_residual,
        'max_number_ledger_relative_residual': maximum_number_residual,
        'max_binding_per_event_relative_residual': maximum_binding_residual,
        'zero_time_and_zero_rate_exact': bool(zero_time_or_rate_ok),
        'toy_energy_column_identity_absolute': toy_column_energy_error,
        'toy_number_column_identity_absolute': toy_column_number_error,
        'toy_energies_eV': {'parent': energy, 'binding': binding, 'slow': slow, 'fast': fast},
        'source': 'q_parent(u)=0.7*u; initially empty; daughters do not react',
        'event_electron_multiplicity': {'removed': 1, 'created': 2, 'net_added': 1},
        'binding_is_separate_from_free_electron_energy': True,
        'analytic_solution': 'P=a*(lambda*u+expm1(-lambda*u))/lambda^2; J=a*u^2/2-P; Ns=Nf=J; Ubind=B*J. At lambda=0: P=a*u^2/2, J=0.',
        'independence': 'Separate count-space toy generator and hand-derived ramp solution; no Cascade constructor, G, projection, functional, or augmented routine reused.',
        'scope_limit': 'Checks branching and ramp mathematics; does not certify the production generator or atomic cross sections.',
        'cases': rows,
    }


def _independent_functionals(cascade):
    """Build conserved left vectors from state definitions, not implementation."""
    energies = np.asarray(cascade.E, dtype=float)
    size, count = int(cascade.size), int(cascade.n)
    if energies.shape != (count,) or np.any(~np.isfinite(energies)) or np.any(energies <= 0):
        raise ValueError('INVALID_ORACLE_ENERGY_COORDINATES')
    if size < count or cascade.G.shape != (size, size):
        raise ValueError('INVALID_ORACLE_GENERATOR_SHAPE')
    names = ('heat', 'binding_HI', 'binding_HeI', 'excitation_HI',
             'excitation_HeI', 'cutoff_energy', 'ionizations_HI',
             'ionizations_HeI', 'cutoff_number', 'low_cross_energy',
             'low_cross_number')
    indices = [int(cascade.ix[name]) for name in names]
    if len(set(indices)) != len(indices) or any(not count <= i < size for i in indices):
        raise ValueError('INVALID_ORACLE_LEDGER_INDICES')
    # First six are disjoint energies. Last two are diagnostic crossing counters.
    energy = np.zeros(size)
    energy[:count] = 1.
    for name in ('heat', 'binding_HI', 'binding_HeI', 'excitation_HI',
                 'excitation_HeI', 'cutoff_energy'):
        energy[cascade.ix[name]] = 1.
    # Active coordinates are E_j*N_j, so division by E_j recovers counts.
    # Each ionization creates one extra free electron; subtract its event count.
    number = np.zeros(size)
    number[:count] = 1. / energies
    number[cascade.ix['cutoff_number']] = 1.
    number[cascade.ix['ionizations_HI']] = -1.
    number[cascade.ix['ionizations_HeI']] = -1.
    return energy, number


def generator_functional_oracle(cascade):
    energy, number = _independent_functionals(cascade)
    generator = sparse.csc_matrix(cascade.G, copy=False)
    if np.any(~np.isfinite(generator.data)):
        raise ValueError('NONFINITE_SUPPLIED_GENERATOR')
    absolute_generator = abs(generator)
    tolerance = FIXED_TOLERANCES['generator_energy_number_relative']
    metrics = {}
    for name, functional in (('energy', energy), ('number', number)):
        residual = np.asarray(generator.T @ functional).ravel()
        scale = np.asarray(absolute_generator.T @ np.abs(functional)).ravel()
        relative = np.zeros_like(residual)
        nonzero = scale > 0
        relative[nonzero] = np.abs(residual[nonzero]) / scale[nonzero]
        if np.any(residual[~nonzero] != 0) or np.any(~np.isfinite(relative)):
            raise ArithmeticError('INVALID_COLUMN_IDENTITY_NORMALIZATION')
        worst = int(np.argmax(relative))
        metrics[name] = {
            'max_column_relative_residual': float(np.max(relative)),
            'max_column_absolute_residual': float(np.max(np.abs(residual))),
            'worst_relative_column': worst,
            'worst_column_residual': float(residual[worst]),
            'worst_column_absolute_flux_scale': float(scale[worst]),
            'nonzero_flux_columns': int(np.count_nonzero(nonzero)),
            'zero_flux_columns': int(np.count_nonzero(~nonzero)),
        }
    passed = all(metrics[name]['max_column_relative_residual'] <= tolerance for name in metrics)
    return {
        'passed': bool(passed), 'status': 'PASS' if passed else 'FAIL',
        'tolerance': tolerance, 'columns_checked': int(cascade.size),
        'energy': metrics['energy'], 'number': metrics['number'],
        'relative_normalizer': 'For each column j: sum_i |f_i|*|G_ij|. An identically zero column has zero residual.',
        'energy_functional': 'sum active E_j*N_j + heat + HI/HeI binding + HI/HeI excitation + cutoff kinetic energy',
        'number_functional': 'sum active (E_j*N_j)/E_j + cutoff count - HI ionization count - HeI ionization count',
        'excluded_diagnostic_ledgers': ['low_cross_energy', 'low_cross_number'],
        'independence': 'Left functionals independently assembled from documented meanings. Supplied G and its ledger-index mapping are shared; Cascade.functionals is not called.',
        'scope_limit': 'Tests stoichiometric column identities, not cross-section magnitude or complete physical-channel coverage.',
    }


def independent_time_propagator_oracle(cascade, source_vectors):
    energy_functional, _ = _independent_functionals(cascade)
    generator = sparse.csc_matrix(cascade.G, copy=False)
    forcing = np.asarray(source_vectors, dtype=float)
    if forcing.ndim != 2 or forcing.shape[0] != cascade.size or forcing.shape[1] < 1:
        raise ValueError('INVALID_ORACLE_SOURCE_SHAPE')
    if np.any(~np.isfinite(forcing)) or np.any(~np.isfinite(generator.data)):
        raise ValueError('NONFINITE_ORACLE_INPUT')
    if np.any(forcing < 0):
        raise ValueError('NEGATIVE_ORACLE_SOURCE')
    shape = forcing.shape
    injected = .5 * np.asarray(energy_functional @ forcing).ravel()
    zero_source = np.all(forcing == 0., axis=0)
    if np.any((injected <= 0) & ~zero_source):
        raise ValueError('NONPOSITIVE_INJECTED_ENERGY_NORMALIZER')
    normalizers = np.where(zero_source, 1., injected)

    # Independent explicit-time forcing: no augmented matrix or ramp states.
    def rhs(u, flat_state):
        state = flat_state.reshape(shape)
        return np.asarray(generator @ state + u * forcing).ravel()

    started = time.perf_counter()
    solution = solve_ivp(rhs, (0., 1.), np.zeros(forcing.size),
                         method='DOP853', rtol=DOP853_RTOL, atol=DOP853_ATOL,
                         t_eval=[1.])
    ivp_elapsed = time.perf_counter() - started
    if not solution.success or solution.t.size != 1 or solution.t[-1] != 1.:
        return {
            'passed': False, 'status': 'FAIL_DOP853_INTEGRATION',
            'message': str(solution.message), 'nfev': int(solution.nfev),
            'rtol': DOP853_RTOL, 'atol': DOP853_ATOL,
            'elapsed_s': ivp_elapsed,
            'independence': 'Same supplied G; independent explicit-time RHS and DOP853 propagation.',
        }
    independent_final = solution.y[:, -1].reshape(shape)
    started = time.perf_counter()
    reference_all = np.asarray(cascade.evolve(forcing, time_s=T_END_S, samples=2))
    expm_elapsed = time.perf_counter() - started
    if reference_all.shape != (2, *shape):
        raise ValueError('UNEXPECTED_EXPONENTIAL_REFERENCE_SHAPE')
    reference_final = reference_all[-1]
    if np.any(~np.isfinite(reference_final)) or np.any(~np.isfinite(independent_final)):
        raise ArithmeticError('NONFINITE_PROPAGATED_ORACLE_STATE')
    absolute_error = np.abs(independent_final - reference_final)
    errors_per_tag = np.max(absolute_error, axis=0)
    normalized_per_tag = errors_per_tag / normalizers
    reference_norm = np.max(np.abs(reference_final), axis=0)
    reference_relative = errors_per_tag / np.where(reference_norm > 0, reference_norm, 1.)
    tolerance = FIXED_TOLERANCES['time_oracle_normalized_linf']
    maximum = float(np.max(normalized_per_tag))
    passed = maximum <= tolerance
    return {
        'passed': bool(passed), 'status': 'PASS' if passed else 'FAIL',
        'tolerance': tolerance, 'u_interval': [0., 1.],
        'method': 'solve_ivp DOP853', 'rtol': DOP853_RTOL, 'atol': DOP853_ATOL,
        'nfev': int(solution.nfev), 'message': str(solution.message),
        'dop853_elapsed_s': ivp_elapsed, 'sparse_expm_elapsed_s': expm_elapsed,
        'max_normalized_linf': maximum,
        'normalized_linf_per_tag': normalized_per_tag.tolist(),
        'absolute_linf_per_tag': errors_per_tag.tolist(),
        'injected_energy_normalizer_per_tag': injected.tolist(),
        'reference_linf_relative_per_tag': reference_relative.tolist(),
        'reference_state_linf_per_tag': reference_norm.tolist(),
        'zero_source_tags': np.flatnonzero(zero_source).tolist(),
        'state_shape': list(shape),
        'normalization': 'Each source tag: ||DOP853(1)-sparse_expm(1)||_inf / (0.5*energy_functional dot A_tag). All-zero source tags use unit normalizer and report absolute error.',
        'reference': 'Supplied Cascade.evolve at physical time 1e10 s, with its sparse matrix exponential.',
        'independence': 'Shares supplied G and source A. Explicit dX/du=G*X+u*A uses DOP853, without production source augmentation. Certifies time propagation agreement only.',
        'scope_limit': 'Cannot detect a physical or algebraic mistake shared by the supplied generator/source; does not independently validate cross sections or energy-grid construction.',
    }


def _record_check(function, identity, *args):
    started = time.perf_counter()
    try:
        result = function(*args)
    except Exception as error:
        result = {'passed': False, 'status': 'ERROR',
                  'error_type': type(error).__name__, 'error': str(error)}
    result['total_elapsed_s'] = time.perf_counter() - started
    result.update(identity)
    return result


def run_oracles(cascade, source_vectors):
    """Return JSON-serializable named checks for the root verification runner."""
    identity = _contract_identity()
    return {
        'EXACT_SINGLE_EVENT_RAMP_ORACLE': _record_check(
            exact_single_event_ramp_oracle, identity),
        'INDEPENDENT_TIME_PROPAGATOR': _record_check(
            independent_time_propagator_oracle, identity, cascade, source_vectors),
        'INDEPENDENT_GENERATOR_FUNCTIONALS': _record_check(
            generator_functional_oracle, identity, cascade),
    }


def main():
    parser = argparse.ArgumentParser(description='Run the standalone exact branching toy; no atomic constructor.')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    identity = _contract_identity()
    result = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'module_import': 'SUCCESS_WITHOUT_ATOMIC_CONSTRUCTOR',
        'EXACT_SINGLE_EVENT_RAMP_ORACLE': _record_check(exact_single_event_ramp_oracle, identity),
        'INDEPENDENT_TIME_PROPAGATOR': {'status': 'NOT_RUN_PENDING_SUPPLIED_OPERATOR_AND_SOURCE'},
        'INDEPENDENT_GENERATOR_FUNCTIONALS': {'status': 'NOT_RUN_PENDING_SUPPLIED_OPERATOR'},
    }
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end='')
    return 0 if result['EXACT_SINGLE_EVENT_RAMP_ORACLE']['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
