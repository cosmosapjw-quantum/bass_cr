"""Independent retrospective axis diagnostic check; no ODE or model fitting."""
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import numpy as np

HERE = Path('/workspace/scratch/10765dc22dcf/bass_cr/research/cr_c21m_independent_stress_20261021')
OUT = HERE / 'axis_response_diagnostic_results_v2'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
with np.load(HERE/'analysis_pilot27/components27.npz', allow_pickle=False) as archive:
    source = {key: archive[key] for key in archive.files}
with np.load(OUT/'axis_response_residuals.npz', allow_pickle=False) as archive:
    diagnostic = {key: archive[key] for key in archive.files}
summary = json.loads((OUT/'SUMMARY.json').read_text())
bindings = json.loads((OUT/'INPUT_BINDINGS.json').read_text())
channels = list(map(str, diagnostic['channels']))
assert channels == ['S_signed_F', 'P_m_signed_F', 'P_r_signed_F', 'P_tot_signed_F']
table = {tuple(key): (str(cid), np.stack([source[channel][i] for channel in channels], axis=-1))
         for i, (key, cid) in enumerate(zip(source['requested_signed_full'], source['case_id']))}
support = {key: values for key, (_, values) in table.items() if key[1] == 0 or key[2] == 0}
held = sorted(key for key in table if key[1] != 0 and key[2] != 0)
assert len(support) == 15 and len(held) == 12
assert set(bindings['support_case_ids']) == {table[k][0] for k in support}
assert set(bindings['held_out_case_ids']) == {table[k][0] for k in held}
assert set(bindings['support_case_ids']).isdisjoint(bindings['held_out_case_ids'])
actual = np.stack([table[key][1] for key in held])
predicted = np.empty_like(actual)
exact = np.empty_like(actual)
for i, key in enumerate(held):
    s, m, r = key
    am, ar, anchor = (support[k] for k in ((s, m, 0.), (s, 0., r), (s, 0., 0.)))
    for t, c in np.ndindex(101, 4):
        predicted[i, t, c] = math.fsum((float(am[t, c]), float(ar[t, c]), -float(anchor[t, c])))
        a, m1, r1, z = (Fraction.from_float(float(value[t, c])) for value in (actual[i], am, ar, anchor))
        exact[i, t, c] = float(a - m1 - r1 + z)
error = actual - predicted
assert diagnostic['actual'].tobytes() == actual.tobytes()
assert diagnostic['axis_prediction'].tobytes() == predicted.tobytes()
assert diagnostic['residual_actual_minus_prediction'].tobytes() == error.tobytes()
decimal_fraction_difference = diagnostic['stored_float_interaction_80digit'] - exact
decimal_fraction_different = diagnostic['stored_float_interaction_80digit'].view(np.uint64) != exact.view(np.uint64)
assert np.all(exact[decimal_fraction_different] == 0)
assert float(np.max(abs(decimal_fraction_difference))) < 1e-98
defined = actual != 0
assert np.array_equal(diagnostic['pointwise_relative_defined'], defined)
assert np.isnan(diagnostic['pointwise_relative_error'][~defined]).all()
np.testing.assert_array_equal(diagnostic['pointwise_relative_error'][defined], error[defined]/abs(actual[defined]))
support_values = np.stack(list(support.values()))
support_scale = np.max(abs(support_values), axis=(0, 1))
increment = np.stack([value-support[key[0],0.,0.] for key, value in support.items()])
increment_scale = np.max(abs(increment), axis=(0, 1))
np.testing.assert_array_equal(diagnostic['support_abs_scale'], support_scale)
np.testing.assert_array_equal(diagnostic['axis_increment_abs_scale'], increment_scale)
for c, channel in enumerate(channels):
    record = summary['observables'][channel]
    assert record['all_saved_max_abs_error'] == float(np.max(abs(error[:, :, c])))
    assert record['endpoint_max_abs_error'] == float(np.max(abs(error[:, -1, c])))
    assert record['all_saved_max_error_over_axis_increment_scale'] == float(np.max(abs(error[:, :, c]))/increment_scale[c])
    assert record['pointwise_relative_undefined_exact_zero_count'] == int(np.count_nonzero(~defined[:, :, c]))
for name, item in json.loads((OUT/'OUTPUT_MANIFEST.json').read_text())['files'].items():
    assert sha(OUT/name) == item['sha256'] and (OUT/name).stat().st_size == item['size']
assert bindings['source_code_sha256'] == sha(HERE/'axis_response_diagnostic.py')
result = {'status': 'PASS_SCOPED',
    'reviewer': 'independent theory_literature agent, not diagnostic implementer',
    'scope': '15 support and 12 disjoint held-out mixed trajectories; all 101 stored times and four signed channels; exact rational stored-float interaction checked independently of Decimal implementation.',
    'new_ODE_runs': 0, 'model_fits': 0, 'benchmark_runs': 0,
    'input_component_npz_sha256': sha(HERE/'analysis_pilot27/components27.npz'),
    'diagnostic_source_sha256': sha(HERE/'axis_response_diagnostic.py'),
    'diagnostic_npz_sha256': sha(OUT/'axis_response_residuals.npz'),
    'diagnostic_summary_sha256': sha(OUT/'SUMMARY.json'),
    'review_script_sha256': sha(Path(__file__)),
    'independent_fraction_vs_80digit_interaction': {
        'values_checked': int(exact.size),
        'byte_equal_values': int(np.count_nonzero(~decimal_fraction_different)),
        'finite_precision_residual_at_exact_zero_count': int(np.count_nonzero(decimal_fraction_different)),
        'maximum_absolute_difference': float(np.max(abs(decimal_fraction_difference))),
        'interpretation': 'The 80-digit Decimal channel has finite-precision residuals below 1e-98 at 12 exact rational zeros. The v2 source and summary now explicitly label high precision rather than exact arithmetic.'},
    'support_and_held_out_disjoint': True,
    'findings': [{'id': 'AXIS_V1_EXACT_LABEL', 'severity': 'minor nonblocking',
                  'status': 'RESOLVED_BY_V2_SCOPE_LABEL',
                  'resolution': 'V1 numerical outputs preserved. V2 explicitly labels finite-precision 80-digit arithmetic; no scientific solver or raw trajectory changed.'}],
    'interpretation': {'maximum_absolute_residuals': {channel: summary['observables'][channel]['all_saved_max_abs_error'] for channel in channels},
        'shear_residual_over_axis_increment_scale': summary['observables']['S_signed_F']['all_saved_max_error_over_axis_increment_scale'],
        'near_cancellation_total_pointwise_relative_max': summary['observables']['P_tot_signed_F']['pointwise_relative_max_abs_where_exact_actual_nonzero'],
        'relative_error_caveat': 'The total-stress pointwise relative maximum exceeds 5 near small actual stress. Do not replace this with a uniform small relative-error or cancellation-accuracy claim.',
        'shear_scale_caveat': 'The total shear-support scale includes initial |S0|=.012; use the separately recorded response-increment scale when discussing response accuracy.'},
    'claim_limits': ['Finite-grid retrospective diagnostic only, with all coupled ODE trajectories already present.',
        'No solver replacement, hidden fitting, new completed scientific trajectories, measured speedup, decoupling theorem, or prospective accuracy bound.',
        'Full scalar norms are not added; the additive diagnostic applies to signed observables.'],
    'global_error_bound': None}
with (HERE/'INDEPENDENT_AXIS_RESPONSE_REVIEW.json').open('x') as handle:
    json.dump(result, handle, indent=2, sort_keys=True)
    handle.write('\n')
print(json.dumps(result, indent=2, sort_keys=True))
