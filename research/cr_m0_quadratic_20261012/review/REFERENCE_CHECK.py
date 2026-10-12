"""Single-use independent review of the frozen M0 quadratic response.

Stdlib only. Arithmetic uses Fraction, with Decimal for output formatting only.
Never import or execute either producer. No CR or historical suite execution.
The source basis here is (1-x, x), not the producer's (1, x).
"""
from __future__ import annotations

import csv
import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
REVIEW = Path(__file__).resolve().parent
INPUT_SHA = '60747f9da89e3596bfeb93a4ec14a1bb58a33bca3a09629fc092f254839f3b7b'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_packet(packet):
    return Q(int(packet['numerator']), int(packet['denominator']))


def decimal(value, digits=70):
    with localcontext() as context:
        context.prec = digits
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def packet(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator),
            'decimal70': decimal(value)}


def determinant(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[1][0] * matrix[0][1]


def difference(left, scale, right):
    return [[left[i][j] - scale * right[i][j] for j in range(2)] for i in range(2)]


def psd(matrix):
    assert matrix[0][1] == matrix[1][0]
    diagonal = [matrix[0][0], matrix[1][1]]
    det = determinant(matrix)
    assert all(value >= 0 for value in diagonal) and det >= 0
    return {'matrix_Bernstein_basis': [[packet(value) for value in row] for row in matrix],
            'diagonal': [packet(value) for value in diagonal],
            'determinant': packet(det), 'exact_PSD': True}


def from_power_matrix(matrix):
    """C^T A C for C=((1,0),(-1,1)); validates stored certificates only."""
    aa, ab, bb = matrix[0][0], matrix[0][1], matrix[1][1]
    assert ab == matrix[1][0]
    return [[aa - 2 * ab + bb, ab - bb], [ab - bb, bb]]


def functional(bernstein, matrix):
    a, b, c = bernstein
    return a * matrix[0][0] + 2 * b * matrix[0][1] + c * matrix[1][1]


def validate_display(bounds, lower, upper):
    shown_lower, shown_upper = map(Q, bounds)
    true_lower, true_upper = 100 * (lower - 1), 100 * (upper - 1)
    assert shown_lower <= true_lower <= true_upper <= shown_upper
    assert true_lower - shown_lower < Q(1, 10**6)
    assert shown_upper - true_upper < Q(1, 10**6)
    return {'percent_strings': bounds, 'outward_exact': True,
            'lower_percent': packet(true_lower), 'upper_percent': packet(true_upper)}


def main():
    manifest_path = UNIT / 'REVIEW_INPUT_MANIFEST.json'
    manifest = json.loads(manifest_path.read_text())
    assert len(manifest['files']) == 31
    paths = [item['path'] for item in manifest['files']]
    assert len(set(paths)) == 31
    assert manifest['base_commit'] == 'ae2d246d7e9037e000b00cd89991beb6f837f2ee'
    for item in manifest['files']:
        path = REPO / item['path']
        assert path.stat().st_size == item['bytes'], item['path']
        assert sha(path) == item['sha256'], item['path']

    input_path = UNIT / 'inputs/CACHED_RESPONSE.json'
    result_path = UNIT / 'results/QUADRATIC_RESPONSE.json'
    assert sha(input_path) == INPUT_SHA
    source = json.loads(input_path.read_text())
    candidate = json.loads(result_path.read_text())
    assert candidate['input_sha256'] == INPUT_SHA
    assert read_packet(source['T_s']) == Q(10**10)
    assert candidate['T_s'] == source['T_s']
    assert read_packet(source['T_years']) == Q(10**10, 31557600)

    profiles = {
        'constant': (Q(1), Q(1), Q(1)),
        'linear_rise': (Q(0), Q(1, 2), Q(1)),
        'convex_rise': (Q(0), Q(0), Q(1)),
        'concave_rise': (Q(0), Q(1), Q(1)),
        'quadratic_decline': (Q(1), Q(0), Q(0)),
        'parabolic_pulse': (Q(0), Q(2), Q(0)),
    }
    candidate_rows = {(row['model'], row['representation']): row for row in candidate['rows']}
    assert len(candidate_rows) == 4
    data = {}
    row_checks = []
    for row in source['rows']:
        key = row['model'], row['representation']
        h, p, r, s = [read_packet(row['moments'][name]) for name in ('H0', 'p', 'R', 'S')]
        # Direct integration of (1-z)^2, z(1-z), z^2 against the cached measure.
        gram = [[p - 2*r + s, r - s], [r - s, s]]
        matrix = [[h * value for value in line] for line in gram]
        assert h > 0 and 0 <= s <= r <= p <= 1
        assert matrix[0][0] > 0 and determinant(matrix) > 0
        assert matrix[0][1] > 0
        saved = candidate_rows[key]
        assert saved['positive_definite_A'] and saved['positive_B']
        stored_matrix = [[read_packet(value) for value in line] for line in saved['A']]
        assert from_power_matrix(stored_matrix) == matrix
        assert read_packet(saved['det_A']) == determinant(matrix)
        assert read_packet(saved['B']) == matrix[0][1]
        named = {}
        for name, bernstein in profiles.items():
            response = functional(bernstein, gram)
            heating = functional(bernstein, matrix)
            a, b, c = bernstein
            assert candidate['polynomials_power_basis'][name] == [a, 2*(b-a), a-2*b+c]
            assert response > 0 and heating == h*response
            assert read_packet(saved['response_over_H0_qstar'][name]) == response
            assert read_packet(saved['heating_coefficient_per_qstar'][name]) == heating
            named[name] = {'response': response, 'heat': heating}
        data[key] = {'gram': gram, 'matrix': matrix, 'named': named}
        row_checks.append({'model': key[0], 'representation': key[1],
                           'det_Bernstein_matrix': packet(determinant(matrix)),
                           'bubble': packet(matrix[0][1]),
                           'six_named_responses_match_exactly': True})

    comparisons = {}
    for representation in ('selected_record', 'birth_defined'):
        full = data['fullBED', representation]
        legacy = data['legacy', representation]
        mf, ml = full['matrix'], legacy['matrix']
        saved = candidate['comparison'][representation]
        named_ratios = {name: full['named'][name]['heat']/legacy['named'][name]['heat']
                        for name in profiles}
        for name, ratio in named_ratios.items():
            assert read_packet(saved['named_heating_fullBED_over_legacy_minus1'][name]) == ratio-1

        rising = saved['rising_class']
        vertices = ('constant', 'concave_rise', 'convex_rise')
        minimum = min(vertices, key=named_ratios.get)
        maximum = max(vertices, key=named_ratios.get)
        assert minimum == rising['minimum_vertex'] == 'convex_rise'
        assert maximum == rising['maximum_vertex'] == 'constant'
        assert read_packet(rising['ratio_minimum']) == named_ratios[minimum]
        assert read_packet(rising['ratio_maximum']) == named_ratios[maximum]
        rising_display = validate_display(rising['percent_outward_6dp'], named_ratios[minimum], named_ratios[maximum])

        broad = saved['all_nonnegative_quadratics']
        lower, upper = [read_packet(broad[name]) for name in ('outer_ratio_lower', 'outer_ratio_upper')]
        lower_matrix = difference(mf, lower, ml)
        upper_matrix = difference([[upper*x for x in line] for line in ml], Q(1), mf)
        lower_check, upper_check = psd(lower_matrix), psd(upper_matrix)
        bubble = mf[0][1] / ml[0][1]
        bubble_slacks = (mf[0][1]-lower*ml[0][1], upper*ml[0][1]-mf[0][1])
        assert all(value >= 0 for value in bubble_slacks)
        assert bubble == read_packet(broad['bubble_ratio'])
        for label, matrix, slack in [('lower', lower_matrix, bubble_slacks[0]),
                                      ('upper', upper_matrix, bubble_slacks[1])]:
            certificate = broad[label+'_PSD_certificate']
            stored = [[read_packet(value) for value in line] for line in certificate['matrix']]
            assert from_power_matrix(stored) == matrix
            assert read_packet(certificate['determinant']) == determinant(matrix)
            assert read_packet(broad['bubble_'+label+'_slack']) == slack

        # Check the provided algebraic-root enclosures by determinant signs.
        # Do not repeat the producer's isqrt-based root construction.
        brackets = [[read_packet(item[name]) for name in ('lower', 'upper')]
                    for item in broad['generalized_eigenvalue_intervals']]
        (l0, l1), (u0, u1) = brackets
        assert l0 < l1 < u0 < u1
        pencil = lambda value: determinant(difference(mf, value, ml))
        signs = [pencil(value) for value in (l0, l1, u0, u1)]
        assert signs[0] >= 0 and signs[1] <= 0 and signs[2] <= 0 and signs[3] >= 0
        assert lower == l0 and upper == u1
        assert l1 < bubble < u0 and broad['bubble_within_eigenvalue_range'] is True
        # Recover polynomial coefficients from values at 0, +1, -1.
        p0, pp, pm = pencil(Q(0)), pencil(Q(1)), pencil(Q(-1))
        coeff = ((pp+pm-2*p0)/2, (pp-pm)/2, p0)
        polynomial = broad['generalized_characteristic_polynomial']
        assert [read_packet(polynomial[name]) for name in ('a', 'b', 'c')] == list(coeff)
        discriminant = coeff[1]**2-4*coeff[0]*coeff[2]
        assert discriminant > 0 and discriminant == read_packet(polynomial['discriminant'])
        sqlo, sqhi = [read_packet(polynomial[name]) for name in ('sqrt_lower', 'sqrt_upper')]
        assert 0 <= sqlo < sqhi and sqlo**2 <= discriminant < sqhi**2

        witnesses = {}
        for side, bracket in [('lower', brackets[0]), ('upper', brackets[1])]:
            witness = broad[side+'_square_witness']
            alpha, beta, gamma = map(read_packet, witness['coefficients_power_basis'])
            assert alpha >= 0 and gamma > 0 and beta**2 == 4*alpha*gamma
            bernstein = (alpha, alpha+beta/2, alpha+beta+gamma)
            assert max(bernstein[0], bernstein[2]) == 1
            node = -beta/(2*gamma)
            assert 0 < node < 1 and node == read_packet(witness['node_x'])
            denominator = functional(bernstein, ml)
            assert denominator > 0
            ratio = functional(bernstein, mf)/denominator
            assert ratio == read_packet(witness['heating_ratio'])
            assert lower <= ratio <= upper
            gap = ratio-lower if side == 'lower' else upper-ratio
            # Much finer than the claimed six-decimal percent display;
            # the uniform certificate above remains exact and tolerance-free.
            assert gap < Q(1, 10**50)
            witnesses[side] = {'admissible_exact_square': True, 'max_source': '1',
                               'node_x': packet(node), 'legacy_denominator': packet(denominator),
                               'ratio': packet(ratio), 'gap_to_outer_boundary': packet(gap),
                               'inside_own_algebraic_root_bracket': bracket[0] <= ratio <= bracket[1]}
        comparisons[representation] = {
            'all_quadratic_display': validate_display(broad['percent_outward_6dp'], lower, upper),
            'rising_display': rising_display, 'rising_extrema': [minimum, maximum],
            'lower_Bernstein_certificate': lower_check, 'upper_Bernstein_certificate': upper_check,
            'root_brackets_checked_without_sqrt_evaluation': True,
            'root_bracket_determinants': [packet(value) for value in signs],
            'bubble_strictly_inside_eigenvalue_range': True, 'witnesses': witnesses,
            'named_percent_differences': {name: packet(100*(value-1)) for name, value in named_ratios.items()}}

    # All 24 TSV records: direct Bernstein functionals and original normalization.
    with (UNIT/'results/QUADRATIC_RESPONSE.tsv').open() as handle:
        tsv_rows = list(csv.DictReader(handle, delimiter='\t'))
    assert len(tsv_rows) == 24
    for row in tsv_rows:
        key = row['model'], row['representation']
        name = row['source']
        expected = data[key]['named'][name]
        assert Q(row['f_at_T']) == profiles[name][2]
        for field, value in [('P_over_H0_qstar', expected['response']), ('P_per_qstar', expected['heat'])]:
            assert abs(Q(row[field])-value) < Q(1, 10**58)
        full = data['fullBED', key[1]]['named'][name]['heat']
        legacy = data['legacy', key[1]]['named'][name]['heat']
        assert abs(Q(row['model_difference_percent'])-100*(full/legacy-1)) < Q(1, 10**58)

    # Exact toy counterexample concerns only missing U3, not a CR replacement kernel.
    locations = (Q(0), Q(1,3), Q(2,3), Q(1))
    weights = ((Q(1,6), Q(1,2), Q(0), Q(1,3)),
               (Q(1,3), Q(0), Q(1,2), Q(1,6)))
    toy_moments = [[sum((weight*location**degree for weight, location in zip(w, locations)), Q(0))
                    for degree in range(4)] for w in weights]
    assert toy_moments[0][:3] == toy_moments[1][:3] == [Q(1), Q(1,2), Q(7,18)]
    assert [row[3] for row in toy_moments] == [Q(19,54), Q(17,54)]
    # Delay tau=T maps to source x=0; tau=0 maps to source x=1.
    assert functional(profiles['constant'], [[Q(1),Q(0)],[Q(0),Q(0)]]) == 1
    assert functional(profiles['quadratic_decline'], [[Q(1),Q(0)],[Q(0),Q(0)]]) == 1
    assert functional(profiles['parabolic_pulse'], [[Q(1),Q(0)],[Q(0),Q(1)]]) == 0

    # Preserve and check the failed execution rather than promoting its exit code.
    original = UNIT/'evidence/attempt01/evaluate_quadratic_response.py'
    current = UNIT/'evaluate_quadratic_response.py'
    split = '    arithmetic_wall = time.monotonic()-start\n'
    before = original.read_text().split(split)
    after = current.read_text().split(split)
    assert len(before) == len(after) == 2 and before[0] == after[0]
    receipt_marker = "    receipt={'schema':'cr-m0-quadratic-execution.v1'"
    assert before[1].split(receipt_marker)[1] == after[1].split(receipt_marker)[1]
    assert "fig.savefig(out/'QUADRATIC_RESPONSE.png',dpi=170)" in original.read_text().splitlines()[254]
    actual = json.loads((UNIT/'evidence/ACTUAL_EXECUTION.json').read_text())
    first = json.loads((UNIT/'evidence/attempt01/ACTUAL_EXECUTION.json').read_text())
    graphics = json.loads((UNIT/'evidence/GRAPHICS_ACTUAL_EXECUTION.json').read_text())
    complete = json.loads((UNIT/'evidence/COMPLETION_RECEIPT.json').read_text())
    failure = json.loads((UNIT/'evidence/attempt01/FAILURE.json').read_text())
    recovery = json.loads((UNIT/'evidence/GRAPHICS_RECOVERY_RECEIPT.json').read_text())
    assert actual == first == complete['original_postprocess']
    assert actual['actual_exit_code'] == failure['actual_process_exit_code'] == 1
    assert graphics == complete['graphics_recovery'] and graphics['actual_exit_code'] == 0
    assert graphics['mode'] == recovery['mode'] == 'RENDER_EXISTING_RESULTS_ONLY'
    assert graphics['exact_calculation_reruns'] == complete['exact_calculation_reruns'] == recovery['exact_calculation_reruns'] == 0
    assert complete['root_arithmetic_wall_s'] is None
    assert recovery['source_sha256'] == INPUT_SHA
    assert recovery['result_sha256'] == sha(result_path)
    assert recovery['renderer_sha256'] == sha(UNIT/'render_quadratic_response.py')
    for receipt in (failure, complete, recovery):
        for output in receipt.get('outputs', receipt.get('preserved_outputs', [])):
            path = UNIT/'results'/output['path']
            assert sha(path) == output['sha256'] and path.stat().st_size == output['bytes']
    assert (UNIT/'evidence/POSTPROCESS.stderr.txt').read_bytes() == (UNIT/'evidence/attempt01/POSTPROCESS.stderr.txt').read_bytes()
    assert (UNIT/'evidence/POSTPROCESS.stdout.txt').read_bytes() == (UNIT/'evidence/attempt01/POSTPROCESS.stdout.txt').read_bytes() == b''
    assert (UNIT/'evidence/GRAPHICS.stderr.txt').read_bytes() == b''

    summary = {'schema': 'cr-m0-independent-reference.v1', 'status': 'PASS',
               'basis': '(1-x,x); direct Bernstein Gram functional',
               'input_sha256': INPUT_SHA, 'candidate_result_sha256': sha(result_path),
               'review_input_manifest_sha256': sha(manifest_path), 'manifest_files_checked': 31,
               'record_checks': row_checks, 'comparison': comparisons,
               'TSV_records_checked': 24, 'U3_counterexample_exact': [[packet(v) for v in row] for row in toy_moments],
               'endpoint_atom_controls': 'PASS',
               'execution_provenance': {'first_exit': 1, 'graphics_exit': 0,
                                        'arithmetic_prefix_unchanged': True, 'receipt_tail_unchanged': True,
                                        'output_hashes_preserved': True,
                                        'final_full_evaluator_execution_not_claimed': True},
               'excluded': ['physical input accuracy', 'old 96-packet suite', 'CR generator', 'CR linear solve',
                            'propagation', 'expm', 'resolvent', 'F retry', 'NCP', 'remote publication', 'backup']}
    output = REVIEW/'REFERENCE_RESULT.json'
    with output.open('x') as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'status': 'PASS', 'manifest_files_checked': 31,
                      'representations_checked': 2, 'Bernstein_PSD_certificates': 4,
                      'algebraic_root_brackets': 4, 'rational_square_witnesses': 4,
                      'named_responses': 24, 'TSV_rows': 24,
                      'U3_counterexample': 'PASS', 'original_failed_execution_preserved': True,
                      'producer_imports': 0, 'producer_reruns': 0,
                      'NCP_dispatch': 0, 'old_suite_runs': 0}))


if __name__ == '__main__':
    main()
