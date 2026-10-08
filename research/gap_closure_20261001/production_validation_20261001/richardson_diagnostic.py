"""Result-blind, offline Richardson supplement; never changes the raw G02 gate.

The extrapolation takes only saved overlap samples. Analytic D is used only
after construction to report disagreement, never to fit or select a stencil.
"""
from __future__ import annotations

import math
import numpy as np


def _matrix(value, shape=None):
    a = np.asarray(value, dtype=np.complex128)
    if (a.ndim != 2 or a.shape[0] == 0 or a.shape[0] != a.shape[1]
            or (shape is not None and a.shape != shape)
            or not np.isfinite(a).all()):
        raise ValueError('finite, nonempty, compatible square matrices required')
    return a


def _norms(value):
    with np.errstate(over='ignore', invalid='ignore'):
        scale = float(np.max(np.abs(value)))
    if not math.isfinite(scale):
        raise ValueError('nonfinite matrix magnitude in diagnostic')
    if scale == 0:
        return {'spectral': 0., 'frobenius': 0., 'elementwise_max': 0.}
    scaled = value / scale
    norms = {'spectral': scale * float(np.linalg.norm(scaled, ord=2)),
             'frobenius': scale * float(np.linalg.norm(scaled, ord='fro')),
             'elementwise_max': scale}
    if not all(math.isfinite(v) for v in norms.values()):
        raise ValueError('nonfinite norm in diagnostic')
    return norms


def _order(a, b):
    return math.log2(a) - math.log2(b) if a > 0 and b > 0 else None


def _ratio(a, b):
    if b <= 0:
        return None
    value = a / b
    return value if math.isfinite(value) else None


def build_table(ladder, velocity):
    """Return R2/R4/R6/R8 arrays and central-stencil weights, with no D input.

    ``ladder`` is exactly four (h, S_minus, S_plus) tuples, coarse to fine,
    with binary halving of h. Returned arrays are newly allocated complex128.
    """
    if not np.isscalar(velocity) or not np.isreal(velocity):
        raise ValueError('positive finite real velocity required')
    velocity = float(velocity)
    if not math.isfinite(velocity) or velocity <= 0:
        raise ValueError('positive finite real velocity required')
    ladder = list(ladder)
    if len(ladder) != 4 or any(len(row) != 3 for row in ladder):
        raise ValueError('exactly four (h, S_minus, S_plus) rows required')
    hs = np.asarray([row[0] for row in ladder], dtype=float)
    if (not np.isfinite(hs).all() or np.any(hs <= 0)
            or not np.array_equal(hs[:-1], 2 * hs[1:])):
        raise ValueError('positive finite h values must halve exactly')
    shape = _matrix(ladder[0][1]).shape
    minus = [_matrix(row[1], shape) for row in ladder]
    plus = [_matrix(row[2], shape) for row in ladder]
    try:
        with np.errstate(over='raise', invalid='raise', divide='raise'):
            raw = [velocity * (p - m) / (2 * h)
                   for h, m, p in zip(hs, minus, plus)]
            arrays = [raw]
            weights = [[np.eye(4, dtype=float)[i] for i in range(4)]]
            for j in range(1, 4):
                factor = 4 ** j
                arrays.append([(factor * b - a) / (factor - 1)
                               for a, b in zip(arrays[-1][:-1], arrays[-1][1:])])
                weights.append([(factor * b - a) / (factor - 1)
                                for a, b in zip(weights[-1][:-1], weights[-1][1:])])
    except FloatingPointError as exc:
        raise ValueError('nonfinite arithmetic in central/Richardson table') from exc
    if not all(np.isfinite(a).all() for layer in arrays for a in layer):
        raise ValueError('nonfinite derivative estimate')
    return {'h': hs, 'minus': minus, 'plus': plus, 'velocity': velocity,
            'arrays': arrays, 'central_weights': weights}


def analyze_ladder(D, ladder, velocity):
    """JSON-compatible supplemental observations, with no acceptance decision.

    Caller must independently admit source/cache identities before passing
    saved arrays. This function does not replace the production cache loader.
    """
    table = build_table(ladder, velocity)
    D = _matrix(D, table['arrays'][0][0].shape)
    with np.errstate(over='raise', invalid='raise'):
        try:
            target = D + D.conj().T
        except FloatingPointError as exc:
            raise ValueError('nonfinite analytic target') from exc
    target_norms = _norms(target)
    sample_norms = [(_norms(m), _norms(p))
                    for m, p in zip(table['minus'], table['plus'])]
    eps = float(np.finfo(np.float64).eps)
    layers = []
    for j, (arrays, weights) in enumerate(zip(table['arrays'], table['central_weights'])):
        rows = []
        for i, (estimate, weight) in enumerate(zip(arrays, weights)):
            norms = _norms(estimate)
            errors = _norms(estimate - target)
            sample_weights = np.abs(weight) * table['velocity'] / (2 * table['h'])
            eps_surrogate = {
                key: float(eps * sum(w * (nm[key] + np_[key])
                                    for w, (nm, np_) in zip(sample_weights, sample_norms)))
                for key in ('spectral', 'frobenius', 'elementwise_max')}
            sample_l1 = float(2 * np.sum(sample_weights))
            if (not math.isfinite(sample_l1)
                    or not all(math.isfinite(v) for v in eps_surrogate.values())):
                raise ValueError('nonfinite sensitivity diagnostic')
            rows.append({
                'finest_h_a0': float(table['h'][i+j]),
                'coarsest_h_a0': float(table['h'][i]),
                'central_difference_coefficients_coarse_to_fine': weight.tolist(),
                'central_difference_coefficient_l1': float(np.sum(np.abs(weight))),
                'signed_sample_coefficient_l1_atomic_time_inverse': sample_l1,
                'estimate_norms': norms,
                'disagreement_with_D_plus_Ddagger_absolute': errors,
                'disagreement_with_D_plus_Ddagger_relative': {
                    key: errors[key] / max(norms[key], target_norms[key], 1e-300)
                    for key in norms},
                'heuristic_epsilon_relative_sample_perturbation_surrogate': eps_surrogate,
            })
        deltas = [_norms(b - a) for a, b in zip(arrays[:-1], arrays[1:])]
        contraction = []
        for a, b in zip(deltas[:-1], deltas[1:]):
            contraction.append({key: {'fine_over_coarse': _ratio(b[key], a[key]),
                                      'observed_order': _order(a[key], b[key])}
                                for key in a})
        layers.append({'name': 'R'+str(2*j+2),
                       'formal_order_if_smooth_even_power_asymptotics': 2*j+2,
                       'rows': rows,
                       'successive_estimate_difference_norms_independent_of_D': deltas,
                       'successive_difference_contraction_independent_of_D': contraction,
                       'observed_orders_against_D_spectral': [
                           _order(a['disagreement_with_D_plus_Ddagger_absolute']['spectral'],
                                  b['disagreement_with_D_plus_Ddagger_absolute']['spectral'])
                           for a, b in zip(rows[:-1], rows[1:])]})
    return {'schema': 'BASS_R4V_RICHARDSON_SUPPLEMENT_V1',
            'status': 'SUPPLEMENTAL_OBSERVATIONS_ONLY',
            'velocity_a0_per_atomic_time': table['velocity'],
            'target_norms': target_norms, 'layers': layers,
            'extrapolation_uses_analytic_D': False,
            'original_G02_acceptance_changed': False,
            'physical_G02_closed': False,
            'rigorous_operator_error_bound': False,
            'new_native_calls': 0,
            'roundoff_surrogate_interpretation':
                'Heuristic unit-epsilon relative perturbation of saved S samples only; '
                'not a bound on quadrature, cancellation, arithmetic, analytic D, '
                'or total derivative error. Actual S errors need independent evidence.',
            'claim_ceilings': {'production': 'HOLD', 'capture': False,
                              'all_bound': 'OPEN', 'b_grid': 'NO_GO'}}
