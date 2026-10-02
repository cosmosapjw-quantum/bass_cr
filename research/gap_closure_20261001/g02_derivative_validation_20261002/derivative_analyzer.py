"""Read-only R4Z central derivative experiment analysis; no physical evaluation.

The derivative builder accepts shifted S matrices and velocity only. Direct D
is read separately after that construction. All failed original R2 diagnostics
are retained. R8 is a polynomial-exact extrapolation, not a regularity theorem
or an operator-error bound for the piecewise C0/H1 physical radial basis.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
H_LADDER = (.4, .2, .1, .05, .025, .0125)
RULES = ((40, 24), (48, 24), (48, 12))
R8_WEIGHTS = tuple(Fraction(x, 2835) for x in (-1, 84, -1344, 4096))
REQUIRED_Z = tuple(sorted({0., *H_LADDER, *(-h for h in H_LADDER)}))
ATOL = 1e-12


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_file_binding(path, expected):
    if sha(path) != expected:
        raise ValueError('analysis file hash binding mismatch: ' + str(path))


def matrix_sha(matrix):
    matrix = np.ascontiguousarray(matrix, dtype='<c16')
    prefix = json.dumps({'shape': list(matrix.shape), 'dtype': '<c16'}, sort_keys=True).encode()
    return hashlib.sha256(prefix + b'\n' + matrix.tobytes()).hexdigest()


def exact_weight_certificate():
    cancellation = [sum(w * Fraction(1, 4**(i*k)) for i, w in enumerate(R8_WEIGHTS)) for k in range(5)]
    # Exact monomial derivatives on the eight centered nodes +/- (1,1/2,1/4,1/8).
    moments = []
    for degree in range(9):
        val = sum(w * (Fraction(1, 2**i)**degree - (-Fraction(1, 2**i))**degree) /
                  (2*Fraction(1, 2**i)) for i, w in enumerate(R8_WEIGHTS))
        moments.append(val)
    return {'weights_coarse_to_fine': [str(x) for x in R8_WEIGHTS],
            'even_error_moments_k0_through_k4': [str(x) for x in cancellation],
            'monomial_degrees_0_through_8': [str(x) for x in moments],
            'monomial_exactness_pass': moments == [Fraction(int(k == 1)) for k in range(9)],
            'formal_order_on_sufficiently_smooth_functions_only': 8,
            'physical_order8_regularity_established': False}


def _matrix(value, shape=None):
    a = np.asarray(value, dtype=np.complex128)
    if a.ndim != 2 or a.shape[0] != a.shape[1] or not np.isfinite(a).all():
        raise ValueError('finite square matrix required')
    if shape is not None and a.shape != shape:
        raise ValueError('shifted matrix shape mismatch')
    return a


def s_only_r8(ladder, velocity):
    """Return raw v*dS/dz estimate. No argument, import or callback can supply D."""
    if len(ladder) != 4:
        raise ValueError('R8 requires exactly four centered S pairs')
    if not math.isfinite(velocity) or velocity <= 0:
        raise ValueError('positive finite velocity required')
    hs = [float(row[0]) for row in ladder]
    if not all(math.isfinite(h) and h > 0 for h in hs):
        raise ValueError('positive finite h required')
    if any(hs[i+1]*2 != hs[i] for i in range(3)):
        raise ValueError('exact halving h ladder required')
    shape = _matrix(ladder[0][1]).shape
    terms = []
    for w, (h, minus, plus) in zip(R8_WEIGHTS, ladder):
        minus, plus = _matrix(minus, shape), _matrix(plus, shape)
        terms.append(float(w) * (velocity * (plus-minus) / (2*h)))
    # Per-component compensated summation avoids an arbitrary vector reduction
    # tree. These are independent FP64 centered differences, not projected data.
    result = np.empty(shape, dtype=np.complex128)
    for index in np.ndindex(shape):
        result[index] = complex(math.fsum(a[index].real for a in terms),
                                math.fsum(a[index].imag for a in terms))
    if not np.isfinite(result).all():
        raise ValueError('R8 derivative overflow')
    return result


def shifted_ladder(samples, hs=H_LADDER):
    """samples is keyed by canonical z.hex() and contains S arrays only."""
    missing = [z for h in hs for z in (-h, h) if float(z).hex() not in samples]
    if missing:
        raise ValueError('missing required shifted S: ' + repr(missing))
    return [(h, samples[float(-h).hex()], samples[float(h).hex()]) for h in hs]


def norms(a):
    a = _matrix(a)
    return {'spectral_absolute': float(np.linalg.norm(a, ord=2)),
            'frobenius_absolute': float(np.linalg.norm(a, ord='fro')),
            'elementwise_max_absolute': float(np.max(np.abs(a)))}


def comparison(estimate, reference, absolute_target=ATOL):
    estimate, reference = _matrix(estimate), _matrix(reference)
    if estimate.shape != reference.shape:
        raise ValueError('comparison matrix shapes differ')
    error = estimate-reference
    values = norms(error)
    scale = max(float(np.linalg.norm(estimate, 2)), float(np.linalg.norm(reference, 2)), 1e-300)
    floor = max(absolute_target, np.finfo(float).eps*scale)
    denominator = np.maximum(np.maximum(abs(estimate), abs(reference)), floor)
    index = tuple(int(x) for x in np.unravel_index(np.argmax(abs(error)), error.shape))
    normalized_index = tuple(int(x) for x in np.unravel_index(np.argmax(abs(error)/denominator), error.shape))
    encode = lambda x: {'real': float(x.real), 'imag': float(x.imag)}
    return {**values, 'pass': all(x <= absolute_target for x in values.values()),
            'absolute_target': absolute_target, 'units': 'atomic_time^-1',
            'derivative_spectral_scale': scale, 'elementwise_denominator_floor': floor,
            'elementwise_max_normalized': float(np.max(abs(error)/denominator)),
            'max_absolute_index_0_based': list(index),
            'max_normalized_index_0_based': list(normalized_index),
            'max_absolute_entry': {'estimate': encode(estimate[index]), 'reference': encode(reference[index]),
                                   'error': encode(error[index])},
            'reference_sha256': matrix_sha(reference), 'estimate_sha256': matrix_sha(estimate)}


def residual_blocks(estimate, direct):
    if estimate.shape != (18, 18) or direct.shape != (18, 18):
        raise ValueError('eighteen-channel block report required')
    return {name: comparison(estimate[sl], direct[sl]) for name, sl in
            [('TT', (slice(0, 9), slice(0, 9))), ('TP', (slice(0, 9), slice(9, 18))),
             ('PT', (slice(9, 18), slice(0, 9))), ('PP', (slice(9, 18), slice(9, 18)))]}


def _original_compare_ladder():
    path = HERE.parent/'static_validation_20261001/static_validation.py'
    spec = importlib.util.spec_from_file_location('r4z_unchanged_static_validation', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.compare_ladder


def rule_label(rule):
    return f'q{rule[0]}_beta{rule[1]}'


def task_label(task):
    return f"z{float(task['z_a0']).hex()}_{rule_label((task['order'],task['inner_phase_budget']))}_{task['moment_backend']}_{task['radial_backend']}"


def _runner():
    sys.path.insert(0, str(HERE))
    import runner
    if Path(runner.__file__).resolve().parent != HERE:
        raise ValueError('wrong stage runner module imported')
    return runner


def collect(root, context_sha):
    """Consume every reserved completed payload, binding bytes and identities."""
    r = _runner()
    root, context = r.load_context(root, context_sha)
    contract = r.read_json(context['contract'])
    if tuple(contract['h_ladder_a0']) != H_LADDER or tuple(contract['required_z_a0']) != REQUIRED_Z:
        raise ValueError('analysis requires the frozen six-h central contract')
    if contract['derivative_validation']['absolute_residual_ta_inverse_max'] != ATOL:
        raise ValueError('contract derivative threshold changed')
    workspace = HERE.parents[4]
    evidence_pins = {str((workspace/Path(path)).resolve()): expected
                     for path, expected in contract['evidence_pins'].items()}
    for path, expected in evidence_pins.items():
        verify_file_binding(path, expected)
    original = HERE.parent/'static_validation_20261001/static_validation.py'
    if sha(original) != evidence_pins[str(original.resolve())]:
        raise ValueError('original R2 analyzer source identity mismatch')
    ledger = r.reservations(root, context)
    observations = {}
    batches, bindings = [], []
    for dest in sorted((root/'batches').iterdir()):
        if not dest.is_dir():
            continue
        manifest_sha = r.sha(dest/'MANIFEST.json')
        _, manifest = r.load_batch(root, context, dest.name, manifest_sha)
        if manifest['context_sha256'] != context_sha:
            raise ValueError('batch context hash mismatch')
        completed, summary = r.read_json(dest/'COMPLETED.json'), r.read_json(dest/'SUMMARY.json')
        started = r.read_json(dest/'STARTED.json')
        for record in (completed, summary, started):
            if record['context_id'] != context['context_id'] or record['manifest_id'] != manifest['manifest_id']:
                raise ValueError('batch completion/start/summary identity mismatch')
        if completed['summary_sha256'] != r.sha(dest/'SUMMARY.json'):
            raise ValueError('batch summary hash mismatch')
        if completed['actual_cross_calls'] != len(manifest['tasks']) or completed['owned_worker_processes_remaining'] != 0:
            raise ValueError('batch is not completely terminal')
        for task in manifest['tasks']:
            target = dest/'attempts'/f"{task['index']:03}"
            rec, raw, full = r.load_payload(target, context, manifest, task)
            if (rec['status'] != 'COMPLETED_SHIFTED_SPATIAL_DIAGNOSTIC' or
                    rec['candidate_basis_identity'] != context['candidate_basis_identity']):
                raise ValueError('completed status/candidate identity mismatch')
            reservation = rec['reservation']
            if reservation not in ledger or reservation['task'] != task or reservation['manifest_id'] != manifest['manifest_id']:
                raise ValueError('completed task global reservation mismatch')
            if rec['source_pins_digest'] != r.digest(context['source_pins']) or rec['input_pins'] != context['input_pins']:
                raise ValueError('worker source/input binding mismatch')
            rawrec = r.read_json(target/'RAW.json')
            if rawrec['sha256'] != rec['raw_sha256']:
                raise ValueError('raw record/payload hash mismatch')
            screens = r._screen_full(full, context['screens'])
            control = r.central_s_control(raw, task['z_a0'])
            if screens != rec['qualification_screens'] or control != rec['central_s_diagonal_control']:
                raise ValueError('stored screen differs from recomputed payload screen')
            meta = rawrec['metadata']
            if meta['candidate_basis_identity'] != context['candidate_basis_identity']:
                raise ValueError('raw metadata candidate identity mismatch')
            for key in ('order', 'subdivisions', 'inner_phase_budget'):
                if meta[key] != task[key]:
                    raise ValueError('raw metadata numerical task mismatch')
            if rec['moment_call_evidence']['radial_pairs'] != meta['radial_pairs']:
                raise ValueError('native evidence radial pair mismatch')
            name = task_label(task)
            if name in observations:
                raise ValueError('duplicate completed numerical task')
            observations[name] = {'label': name, 'task': task, 'batch': dest.name,
                'global_attempt': reservation['global_attempt'], 'screens': screens,
                'central_control': control, 'raw_sha256': rec['raw_sha256'],
                'full_sha256': rec['full_sha256'], 'record_sha256': r.sha(target/'COMPLETED.json'),
                'radial_pairs': meta['radial_pairs'], 'wall_seconds': rec['wall_seconds'],
                'peak_rss_kib': rec['peak_rss_kib'], 'geometry_identity': rec['geometry_identity'],
                'moment_call_evidence': rec['moment_call_evidence'],
                'radial_total_call_evidence': rec['radial_total_call_evidence'], 'raw': raw, 'full': full}
            for filename in ('RAW.npz', 'RAW.json', 'FULL.npz', 'COMPLETED.json'):
                bindings.append({'path': str(target/filename), 'sha256': r.sha(target/filename)})
        batches.append({'name': dest.name, 'manifest_id': manifest['manifest_id'],
            'manifest_sha256': manifest_sha, 'summary_sha256': r.sha(dest/'SUMMARY.json'),
            'completed_sha256': r.sha(dest/'COMPLETED.json'),
            'actual_cross_calls': completed['actual_cross_calls'],
            'wall_seconds': summary['batch_wall_seconds']})
    if not observations or len(observations) != len(ledger) or sorted(x['global_attempt'] for x in observations.values()) != list(range(1, len(ledger)+1)):
        raise ValueError('global attempts do not have a complete unique payload inventory')
    return root, context, contract, observations, batches, bindings


def spatial_pair(a, b, r, screens):
    if a['task']['z_hex'] != b['task']['z_hex'] or a['task']['time_hex'] != b['task']['time_hex']:
        raise ValueError('spatial comparison requires identical geometry/time')
    rawmax, detail = r._raw_difference(a['raw'], b['raw'])
    screenpass = all(x['screens']['hermiticity_pass'] and x['screens']['metric_pass'] for x in (a,b))
    rawpass = rawmax <= screens['raw_cross_relative_max']
    return {'a': a['label'], 'b': b['label'], 'z_a0': a['task']['z_a0'],
        'max_six_raw_relative_difference': rawmax, 'six_raw_relative_differences': detail,
        'raw_difference_pass': rawpass, 'both_full_screens_pass': screenpass,
        'pass': rawpass and screenpass,
        'six_raw_bitwise_equal': all(np.array_equal(a['raw'][k], b['raw'][k]) for k in r.RAW_KEYS),
        'full_bitwise_equal': all(np.array_equal(a['full'][k], b['full'][k]) for k in ('S','H','D'))}


def analyze(root, context_sha):
    root, context, contract, observations, batches, bindings = collect(root, context_sha)
    r = _runner()
    def get(z, rule, backend=('fortran','fortran')):
        name = task_label({'z_a0': z, 'order': rule[0], 'inner_phase_budget': rule[1],
                           'moment_backend': backend[0], 'radial_backend': backend[1]})
        if name not in observations:
            raise ValueError('missing required completed task: '+name)
        return observations[name]
    qualification = []
    for z in REQUIRED_Z:
        coarse, fine, probe = [get(z, rule) for rule in RULES]
        qualification.append({'z_a0': z,
            'adjacent_order': spatial_pair(coarse, fine, r, context['screens']),
            'independent_panel_probe': spatial_pair(fine, probe, r, context['screens'])})
    parity = spatial_pair(get(.4, RULES[0], ('reference','python')), get(.4, RULES[0]), r, context['screens'])
    paritypass = parity['six_raw_bitwise_equal'] and parity['full_bitwise_equal']
    speed = context['speed_a0_per_ta']
    originals, windows, matrices, center_controls = {}, {}, {}, {}
    original_compare = _original_compare_ladder()
    for rule in RULES:
        name = rule_label(rule)
        samples = {float(z).hex(): get(z,rule)['full']['S'] for z in REQUIRED_Z}
        ladder = shifted_ladder(samples)
        # Construct every S-only estimate before reading the central D matrix.
        estimates = [s_only_r8(ladder[i:i+4], speed) for i in range(3)]
        D = get(0., rule)['full']['D']
        direct = D+D.conj().T
        originals[name] = {'all_six_h': original_compare(D, ladder, speed),
                           'original_first_four_h': original_compare(D, ladder[:4], speed),
                           'original_diagnostic_modified': False}
        windows[name] = []
        for i, estimate in enumerate(estimates):
            row = {'window_index': i, 'h_values_a0': list(H_LADDER[i:i+4]),
                   'accepted_window': i in (1,2), **comparison(estimate,direct),
                   'residual_blocks': residual_blocks(estimate,direct),
                   'input_S_absolute_error_amplification_coefficient': speed*473/(35*H_LADDER[i]),
                   'amplification_is_error_bound_without_input_bounds': False}
            windows[name].append(row)
            matrices[(name,i)] = estimate
        center_controls[name] = get(0.,rule)['central_control']
    window_agreement = [{'rule': rule_label(rule), **comparison(matrices[(rule_label(rule),1)], matrices[(rule_label(rule),2)])} for rule in RULES]
    crossrule = [{'a': rule_label(a), 'b': rule_label(b), 'window_index':i,
                 **comparison(matrices[(rule_label(a),i)], matrices[(rule_label(b),i)])}
                for a,b in itertools.combinations(RULES,2) for i in range(3)]
    checks = {'backend_bitwise_parity': paritypass,
              'all_13_adjacent_spatial_qualifications': all(x['adjacent_order']['pass'] for x in qualification),
              'all_13_independent_panel_probes': all(x['independent_panel_probe']['pass'] for x in qualification),
              'two_finest_residuals_all_three_rules': all(windows[rule_label(rule)][i]['pass'] for rule in RULES for i in (1,2)),
              'two_finest_window_agreement_all_three_rules': all(row['pass'] for row in window_agreement),
              'two_finest_cross_rule_derivative_agreement': all(row['pass'] for row in crossrule if row['window_index'] in (1,2)),
              'central_exact_zero_controls': all(x['pass'] for x in center_controls.values()),
              'exact_polynomial_weight_certificate': exact_weight_certificate()['monomial_exactness_pass']}
    passed = all(checks.values())
    return {'schema':'BASS_R4Z_CENTRAL_DERIVATIVE_RESULT_V1',
        'status': 'CENTRAL_DERIVATIVE_NUMERICAL_CHECK_PASS' if passed else 'CENTRAL_DERIVATIVE_NUMERICAL_CHECK_UNRESOLVED',
        'selected_checks_pass': passed, 'required_derivative_checks':checks,
        'context_id':context['context_id'], 'context_sha256':context_sha,
        'source_pins':context['source_pins'], 'input_pins':context['input_pins'],
        'analysis_source':{'path':str(Path(__file__).resolve()), 'sha256':sha(__file__),
                          'execution_context_source_pin_member':str(Path(__file__).resolve()) in context['source_pins']},
        'weight_certificate':exact_weight_certificate(), 'spatial_qualifications':qualification,
        'backend_parity':parity, 'central_exact_zero_controls':center_controls,
        'R8_windows':windows, 'two_finest_window_agreement':window_agreement,
        'cross_rule_derivative_agreement':crossrule, 'unchanged_original_R2_diagnostics':originals,
        'all_original_R2_checks_pass':all(x['passed'] for item in originals.values() for key,x in item.items() if isinstance(x,dict)),
        'original_R2_failure_does_not_silently_become_pass':True,
        'rows':[{k:v for k,v in row.items() if k not in ('raw','full')} for row in observations.values()],
        'batch_records':batches, 'payload_bindings':bindings, 'actual_raw_operator_calls':len(observations),
        'global_reserved_attempts':len(observations), 'maximum_raw_attempt_budget':context['raw_attempt_budget'],
        'physical_calls_by_this_analysis':0, 'automatic_retries':0,
        'batch_wall_seconds_sum':sum(x['wall_seconds'] for x in batches),
        'S_only_construction_uses_D':False, 'raw_projection':False,
        'formal_order8_on_physical_candidate_established':False,
        'qualification_scope':'CENTRAL_CANDIDATE_DERIVATIVE_NUMERICAL_CHECK_ONLY',
        'observed_differences_are_certified_bounds':False, 'same_center_refinement':'NOT_RUN',
        'whole_trajectory_derivative_test':False, 'original_eight_center_gate':'UNCHANGED_UNRESOLVED',
        'G02':'UNRESOLVED', 'production_admission':'HOLD', 'capture_execution_allowed':False,
        'all_bound':'OPEN', 'b_grid':'NO_GO', 'MPI_execution':False, 'NCP64_scaling':'NOT_RUN'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True)
    parser.add_argument('--context-sha256',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    if Path(args.out).exists():
        raise FileExistsError('analysis output is create-only')
    result=analyze(args.root,args.context_sha256)
    with Path(args.out).open('x') as stream:
        json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({'status':result['status'], 'required_derivative_checks':result['required_derivative_checks'],
                      'actual_raw_operator_calls':result['actual_raw_operator_calls'],
                      'result_sha256':sha(args.out), 'failed_original_R2_diagnostics_retained':True},indent=2))
    if not result['selected_checks_pass']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
