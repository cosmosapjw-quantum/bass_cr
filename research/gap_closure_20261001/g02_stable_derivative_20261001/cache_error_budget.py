"""Read-only, component-resolved G02 cache diagnostics; no solver/native calls.

The original all-matrix gate is copied, never replaced by block-wise screens.
Epsilon and adjacent-resolution quantities are sensitivity observations, not
certified errors. Pure array helpers below do not import physical evaluators.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
GAP = HERE.parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def channels_from_basis(basis):
    """Exactly the center/radial/m ordering in symmetric_channels()."""
    channels = []
    for center in (0, 1):
        for mode in basis['modes']:
            ell = mode['l']
            if type(ell) is not int or ell < 0:
                raise ValueError('nonnegative integral l required')
            for m in range(-ell, ell+1):
                channels.append({'index': len(channels), 'center': center,
                                 'label': 'T' if center == 0 else 'P',
                                 'l': ell, 'm': m, 'radial_identity': mode['identity']})
    if not channels:
        raise ValueError('nonempty channel bank required')
    return channels


def block_indices(channels):
    if [c['index'] for c in channels] != list(range(len(channels))):
        raise ValueError('channel index ordering mismatch')
    centers = [c['center'] for c in channels]
    if set(centers) != {0, 1}:
        raise ValueError('both target and projectile channels required')
    groups = {label: [i for i, center in enumerate(centers) if center == c]
              for label, c in [('T', 0), ('P', 1)]}
    return {a+b: (groups[a], groups[b]) for a in 'TP' for b in 'TP'}


def pair(z):
    return [float(np.real(z)), float(np.imag(z))]


def norms(matrix):
    return {'spectral': float(np.linalg.norm(matrix, 2)),
            'frobenius': float(np.linalg.norm(matrix, 'fro')),
            'max_absolute': float(np.max(abs(matrix)))}


def sensitivity(minus, plus, D, Ddagger, h, velocity):
    """Linear data perturbation gains and explicit epsilon-scaled heuristics."""
    if not np.isfinite([h, velocity]).all() or h <= 0 or velocity <= 0:
        raise ValueError('positive finite h and velocity required')
    factor = velocity/(2*h)
    eps = np.finfo(np.float64).eps
    return {'absolute_sample_error_gain_each': factor,
            'absolute_sample_error_gain_sum': 2*factor,
            'fd_epsilon_relative_sample_surrogate': eps*factor*(abs(minus)+abs(plus)),
            'D_sum_epsilon_relative_operand_surrogate': eps*(abs(D)+abs(Ddagger))}


def block_budget(D, Ddagger, minus, plus, h, velocity, rows, columns,
                 denominator_floor=1e-12):
    """Summarize one bound block without discarding exact/near-zero entries."""
    D, Ddagger, minus, plus = [np.asarray(a, complex) for a in (D, Ddagger, minus, plus)]
    if (D.ndim != 2 or D.shape != (len(rows), len(columns))
            or any(a.shape != D.shape or not np.isfinite(a).all()
                   for a in (Ddagger, minus, plus)) or not np.isfinite(D).all()
            or not np.isfinite(denominator_floor) or denominator_floor <= 0):
        raise ValueError('finite bound matrices and positive floor required')
    gains = sensitivity(minus, plus, D, Ddagger, h, velocity)
    direct = D+Ddagger
    finite_difference = velocity*(plus-minus)/(2*h)
    error = finite_difference-direct
    denominator = np.maximum(np.maximum(abs(finite_difference), abs(direct)), denominator_floor)
    normalized = abs(error)/denominator
    def element(i, j):
        scale = float(abs(D[i, j])+abs(Ddagger[i, j]))
        target = float(abs(direct[i, j]))
        difference = float(abs(plus[i, j]-minus[i, j]))
        sample_scale = float(abs(plus[i, j])+abs(minus[i, j]))
        return {'global_index': [int(rows[i]), int(columns[j])], 'block_index': [int(i), int(j)],
                'D': pair(D[i, j]), 'Ddagger': pair(Ddagger[i, j]),
                'D_plus_Ddagger': pair(direct[i, j]),
                'S_minus': pair(minus[i, j]), 'S_plus': pair(plus[i, j]),
                'finite_difference': pair(finite_difference[i, j]),
                'residual_absolute': float(abs(error[i, j])),
                'residual_normalized': float(normalized[i, j]),
                'denominator': float(denominator[i, j]),
                'denominator_is_floor': bool(denominator[i, j] == denominator_floor),
                'D_operand_absolute_sum': scale,
                'D_cancellation_ratio': scale/target if target else None,
                'D_cancellation_exact_zero': target == 0 and scale > 0,
                'S_subtraction_condition': sample_scale/difference if difference else None,
                'S_equal_value': bool(plus[i, j] == minus[i, j]),
                'fd_epsilon_relative_sample_surrogate': float(gains['fd_epsilon_relative_sample_surrogate'][i, j]),
                'D_sum_epsilon_relative_operand_surrogate': float(gains['D_sum_epsilon_relative_operand_surrogate'][i, j])}
    absolute_index = np.unravel_index(np.argmax(abs(error)), error.shape)
    normalized_index = np.unravel_index(np.argmax(normalized), error.shape)
    en, dn, fn = norms(error), norms(direct), norms(finite_difference)
    nonzero_target = abs(direct) > 0
    cancellation = np.divide(abs(D)+abs(Ddagger), abs(direct),
                             out=np.zeros_like(abs(direct)), where=nonzero_target)
    return {'residual': en,
            'residual_relative': {k: en[k]/max(dn[k], fn[k], 1e-300) for k in en},
            'target': dn, 'finite_difference': fn,
            'elementwise_max_normalized': float(normalized.max()),
            'denominator_floor': float(denominator_floor),
            'floor_entry_count': int(np.count_nonzero(denominator == denominator_floor)),
            'dominating_absolute_element': element(*absolute_index),
            'dominating_normalized_element': element(*normalized_index),
            'maximum_finite_D_cancellation_ratio': float(cancellation.max()),
            'D_exact_cancellation_count': int(np.count_nonzero((abs(direct) == 0) & ((abs(D)+abs(Ddagger)) > 0))),
            'S_plus_minus_bitwise_equal': minus.tobytes() == plus.tobytes(),
            'S_plus_minus_numerically_equal': bool(np.array_equal(minus, plus)),
            'S_plus_minus_difference': norms(plus-minus),
            'absolute_sample_error_gain_each': gains['absolute_sample_error_gain_each'],
            'absolute_sample_error_gain_sum': gains['absolute_sample_error_gain_sum'],
            'fd_epsilon_relative_sample_surrogate': norms(gains['fd_epsilon_relative_sample_surrogate']),
            'D_sum_epsilon_relative_operand_surrogate': norms(gains['D_sum_epsilon_relative_operand_surrogate'])}


def _raw(sample, order, key):
    path = sample['cache']/(sample['item'].query_id+'.npz')
    with np.load(path, allow_pickle=False) as data:
        return np.array(data[f'q{order}_h1__{key}'])


def analyze_budget(manifests, output_json, output_csv):
    for output in (output_json, output_csv):
        if Path(output).exists():
            raise FileExistsError(output)
    sys.path.insert(0, str(GAP/'production_validation_20261001'))
    import fresh_context_analysis as fresh
    plan = fresh._fixed(fresh.FD_PLAN, fresh.FD_PLAN_SHA)
    samples, provenance, context = fresh._load_lanes(manifests, [q['time_hex'] for q in plan['queries']])
    by_z = {q['z_hex']: samples[q['time_hex']] for q in plan['queries']}
    inputs = Path(fresh.read(manifests[0])['inputs'])
    basis = fresh.read(inputs/'BASIS.json')
    if basis['identity'] != context['basis_identity']:
        raise ValueError('basis identity changed')
    channels = channels_from_basis(basis)
    blocks = block_indices(channels)
    if len(channels) != context['physics']['channels']:
        raise ValueError('bound channel count mismatch')
    records = []; csv_rows = []; resolution_rows = []
    velocity = plan['identity']['velocity_au']
    atol = plan['acceptance']['absolute_target_atomic_time_inverse']
    for z in plan['centers']:
        center = by_z[float(z).hex()]
        D = center['D']; direct = D+D.conj().T
        for h in plan['h_ladder']:
            lo, hi = [by_z[float(z+s*h).hex()] for s in (-1, 1)]
            fd = velocity*(hi['S']-lo['S'])/(2*h)
            floor = max(atol, np.finfo(float).eps*max(norms(fd)['spectral'], norms(direct)['spectral']))
            for label, (rows, columns) in blocks.items():
                index = np.ix_(rows, columns)
                budget = block_budget(D[index], D.conj().T[index], lo['S'][index], hi['S'][index],
                                      h, velocity, rows, columns, floor)
                row = {'z_a0': z, 'h_a0': h, 'block': label,
                       'cross_resolution': 40 if label in ('TP', 'PT') else None,
                       'same_center_order': 20 if label in ('TT', 'PP') else None,
                       **budget}
                records.append(row)
                dom = budget['dominating_normalized_element']
                csv_rows.append({'z_a0': z, 'h_a0': h, 'block': label,
                    'spectral_absolute': budget['residual']['spectral'],
                    'spectral_relative': budget['residual_relative']['spectral'],
                    'max_absolute': budget['residual']['max_absolute'],
                    'max_normalized': budget['elementwise_max_normalized'],
                    'dominating_i': dom['global_index'][0], 'dominating_j': dom['global_index'][1],
                    'dominating_absolute': dom['residual_absolute'],
                    'dominating_denominator': dom['denominator'],
                    'dominating_D_cancellation_ratio': dom['D_cancellation_ratio'],
                    'sample_error_gain_sum': budget['absolute_sample_error_gain_sum'],
                    'fd_epsilon_surrogate_max': budget['fd_epsilon_relative_sample_surrogate']['max_absolute']})
            for label, reverse in [('TP', 'PT'), ('PT', 'TP')]:
                rows, columns = blocks[label]; budgets = {}; arrays = {}
                for order in (32, 40):
                    dc = _raw(center, order, 'D_'+label.lower())
                    dd = _raw(center, order, 'D_'+reverse.lower()).conj().T
                    sm, sp = [_raw(item, order, 'S_'+label.lower()) for item in (lo, hi)]
                    budgets[str(order)] = block_budget(dc, dd, sm, sp, h, velocity, rows, columns, floor)
                    arrays[order] = (dc+dd, velocity*(sp-sm)/(2*h), sm, sp)
                d32, f32, sm32, sp32 = arrays[32]; d40, f40, sm40, sp40 = arrays[40]
                proxy = velocity/(2*h)*(abs(sm40-sm32)+abs(sp40-sp32))
                resolution_rows.append({'z_a0': z, 'h_a0': h, 'block': label,
                    'raw_cross_order_budgets': budgets,
                    'adjacent_D_sum_difference': norms(d40-d32),
                    'adjacent_FD_difference': norms(f40-f32),
                    'adjacent_residual_difference': norms((f40-d40)-(f32-d32)),
                    'adjacent_sample_difference_amplified_proxy': norms(proxy),
                    'proxy_is_certified_error': False})
    same_center = {}
    reference = by_z[float(plan['centers'][0]).hex()]['S']
    for label in ('TT', 'PP'):
        rows, columns = blocks[label]; index = np.ix_(rows, columns)
        diffs = [norms(sample['S'][index]-reference[index]) for sample in samples.values()]
        same_center[label] = {'max_difference_from_first_center_across_72':
                              {key: max(x[key] for x in diffs) for key in diffs[0]},
                              'analytical_time_independence': 'same rigidly translated center; boost phases cancel in overlap',
                              'implementation_roundoff_path': 'own-sphere radial rule is repartitioned at nuclear distance R'}
    sources = [Path(__file__), Path(fresh.__file__), fresh.FD_PLAN,
               fresh.hp.REPO/'research/foundation_rebuild/full_operator_20260926/full_operator.py',
               fresh.hp.REPO/'research/foundation_rebuild/src/bass_foundations/two_center.py',
               inputs/'BASIS.json']
    report = {'schema': 'BASS_R4W_G02_COMPONENT_BUDGET_V1',
        'status': 'OBSERVATIONS_ONLY_ORIGINAL_GATE_UNCHANGED', 'context_id': context['context_id'],
        'source_hashes': {str(p): sha(p) for p in sources},
        'provenance': provenance, 'snapshots': 72, 'new_native_calls': 0,
        'channel_ordering': channels, 'block_indices': blocks,
        'original_acceptance': plan['acceptance'],
        'original_gate': 'all-matrix spectral AND Frobenius AND component screens with original global OR semantics; unchanged',
        'units': {'S': 'dimensionless', 'D_and_derivative': 'atomic_time^-1', 'h': 'a0'},
        'sensitivity_interpretation': [
            'Absolute perturbations |delta S+|,|delta S-| propagate with coefficient velocity/(2h) each.',
            'Epsilon-scaled surrogates assume operand-relative perturbations and are not bounds on computed quadrature, FEM, or full arithmetic error.',
            'Adjacent quadrature-order differences are observed sensitivities, not certified discretization errors.',
            'Only cross blocks exist at both orders32/40; same-center order20 is common and was not rerun.'],
        'same_center_overlap_observation': same_center,
        'selected_block_budgets': records, 'cross_resolution_budgets': resolution_rows,
        'capture': False, 'production_admission': 'HOLD', 'all_bound': 'OPEN', 'b_grid': 'NO_GO'}
    serialized = json.dumps(report, indent=2, allow_nan=False)+'\n'
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(output_json).open('x') as stream:
        stream.write(serialized)
    with Path(output_csv).open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(csv_rows[0])); writer.writeheader(); writer.writerows(csv_rows)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifests', nargs='+', required=True)
    parser.add_argument('--output-json', required=True)
    parser.add_argument('--output-csv', required=True)
    args = parser.parse_args()
    report = analyze_budget(args.manifests, args.output_json, args.output_csv)
    print(json.dumps({'status': report['status'], 'rows': len(report['selected_block_budgets']),
                      'cross_resolution_rows': len(report['cross_resolution_budgets']), 'new_native_calls': 0}))


if __name__ == '__main__':
    main()
