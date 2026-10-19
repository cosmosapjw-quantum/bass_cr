"""Separate C21G execution, reference sensitivity, ledgers and signed orders."""
from __future__ import annotations
import argparse
import math
from pathlib import Path
from campaign_contract import (HERE, POLICY, PILOT_BUDGETS, canonical_hash,
                               read_json, sha256, verify_files, write_new_json)
from diagnostics import (GAS_NAMES, compare_endpoints, recompute_balances,
                         signed_order, reference_free_order, two_scale_coefficients)

def completed_results(receipts, baseline_dir):
    """Bind completed payloads to the published manifest and frozen fixtures."""
    if not any(receipt.get('status') == 'COMPLETE' for receipt in receipts):
        return {}
    # Import lazily: the runner also invokes this analysis after its workers exit.
    from run_campaign import verify_payload_record
    manifest_path = HERE / 'EXECUTION_MANIFEST.json'
    manifest = read_json(manifest_path)
    verify_files(baseline_dir, manifest['baseline_files'])
    if manifest['policy_sha256'] != canonical_hash(POLICY):
        raise ValueError('ANALYSIS_POLICY_MISMATCH')
    expected_manifest = sha256(manifest_path)
    fixture_hashes = {name: canonical_hash(read_json(Path(baseline_dir) / name / 'fixture.json'))
                      for name in POLICY['fixtures']}
    results = {}
    binary_hash = None
    for receipt in receipts:
        if receipt.get('status') != 'COMPLETE':
            continue
        result = verify_payload_record(receipt)
        data = receipt['signature_data']; job = receipt['job']
        if data['micro'] != 'native' or data['fixture_sha256'] != fixture_hashes.get(job['fixture']):
            raise ValueError('ANALYSIS_FROZEN_NATIVE_FIXTURE_MISMATCH')
        if data['input_manifest_sha256'] != expected_manifest:
            raise ValueError('ANALYSIS_INPUT_MANIFEST_MISMATCH')
        if binary_hash is not None and data['binary_sha256'] != binary_hash:
            raise ValueError('ANALYSIS_MIXED_NATIVE_BINARIES')
        binary_hash = data['binary_sha256']
        if job['id'] in results:
            raise ValueError('ANALYSIS_DUPLICATE_JOB_ID')
        results[job['id']] = result
    return results

def metrics(comparison):
    return {'gas_normalized': comparison['gas_normalized_max'],
            'photon_max_abs_H': comparison['photons']['max_absolute_count_delta_H'],
            'log_survivor_max_abs': None if comparison['photons']['positive_weight_log_unavailable_pairs'] else comparison['photons']['max_absolute_log_delta']}

def grid_identity(result):
    rows = result.get('solver_diagnostics', {}).get('segments', [])
    if not rows or any(not row.get('accepted_grid_sha256') for row in rows):
        return None
    return [(row['x0'], row['x1'], row['accepted_grid_sha256']) for row in rows]

def analyze_references(baseline_dir, receipts):
    results = completed_results(receipts, baseline_dir)
    fixtures = {}
    for name in POLICY['fixtures']:
        f = read_json(Path(baseline_dir) / name / 'fixture.json')
        refs = {'L0': read_json(Path(baseline_dir) / name / 'radau.json')}
        missing = []
        for tier in ('L1', 'L2', 'L3', 'L3M'):
            result = results.get(name + '_reference_' + tier)
            if result is None:
                missing.append(tier)
            else:
                refs[tier] = result
        comparisons = {}
        for left, right in (('L1', 'L0'), ('L2', 'L1'), ('L3', 'L2'), ('L3M', 'L3')):
            if left in refs and right in refs:
                comparisons[left + '_minus_' + right] = compare_endpoints(f, refs[left], refs[right])
        budgets = PILOT_BUDGETS[name]
        checks = {}
        for key in ('L2_minus_L1', 'L3_minus_L2', 'L3M_minus_L3'):
            if key in comparisons:
                measured = metrics(comparisons[key])
                checks[key] = {quantity: {'value': measured[quantity], 'budget': budget,
                              'meets_pilot_resolution': measured[quantity] is not None and measured[quantity] <= budget}
                               for quantity, budget in budgets.items()}
        ready = not missing and all(c['meets_pilot_resolution'] for row in checks.values() for c in row.values())
        grid3, gridm = (grid_identity(refs[k]) if k in refs else None for k in ('L3', 'L3M'))
        mesh = 'NOT_AVAILABLE' if grid3 is None or gridm is None else 'MESH_CAP_INACTIVE' if grid3 == gridm else 'ACCEPTED_GRID_CHANGED'
        radius = None
        if 'L3_minus_L2' in comparisons and 'L3M_minus_L3' in comparisons:
            a, b = comparisons['L3_minus_L2'], comparisons['L3M_minus_L3']
            radius = {'gas_components': {k: max(abs(a['gas_signed'][k]), abs(b['gas_signed'][k])) for k in GAS_NAMES},
                      'gas_normalized_components': {k: max(abs(a['gas_normalized_signed'][k]), abs(b['gas_normalized_signed'][k])) for k in GAS_NAMES},
                      'temperature_K': max(abs(a['temperature']['stable_identity_delta_K']), abs(b['temperature']['stable_identity_delta_K'])),
                      'metrics': {k: max(metrics(a)[k], metrics(b)[k]) if metrics(a)[k] is not None and metrics(b)[k] is not None else None for k in budgets},
                      'interpretation': 'EMPIRICAL_SENSITIVITY_RADIUS_FROM_TWO_OBSERVED_DIFFERENCES',
                      'global_error_bound': None}
        balances = {tier: recompute_balances(f, r) for tier, r in refs.items() if tier != 'L0'}
        fixtures[name] = {'pilot_status': 'INCOMPLETE_REFERENCES' if missing else 'REF_READY_FOR_BOUNDED_REFINEMENT' if ready else 'HOLD_REFERENCE_SENSITIVITY',
                          'missing_or_failed_tiers': missing, 'comparisons': comparisons,
                          'pilot_resolution_checks': checks, 'empirical_sensitivity_radius': radius,
                          'mesh_check': mesh, 'balance_diagnostics': balances,
                          'reference_results': {tier: r for tier, r in refs.items() if tier != 'L0'},
                          'meaning': 'Cost-control diagnostic for a fixed pilot; successful execution and small pairwise variation do not certify a global error bound.'}
    complete = all(not row['missing_or_failed_tiers'] for row in fixtures.values())
    any_new = any(row['reference_results'] for row in fixtures.values())
    return {'schema': 'C21G_REFERENCE_LADDER_ASSESSMENT_V1', 'fixtures': fixtures,
            'execution_status': 'COMPLETE' if complete else 'PARTIAL' if any_new else 'NOT_RUN',
            'source_or_fixture_refinement': 'NOT_RUN_FIXED_INPUTS', 'global_error_bound': None,
            'execution_and_physics_are_separate': True, 'holds': POLICY['holds']}

def observables(result):
    return {**dict(zip(GAS_NAMES, result['gas'])), 'temperature_K': result['temperature_K'],
            'photon_number_H': result['photon_number'], 'photon_energy_eV_H': result['photon_energy_eV_H']}

def method_pairs(cases):
    modes = ('FULLMID', 'MIDPHOTO_ENDMICRO')
    mapping = {mode: {} for mode in modes}
    for result in cases:
        if result.get('mode') in modes:
            mapping[result['mode']][result['subdivisions_per_event_interval']] = result
    return mapping

def coefficient_sequences(cases):
    mapping = method_pairs(cases)
    common = sorted(set(mapping['FULLMID']) & set(mapping['MIDPHOTO_ENDMICRO']))
    differences = {}
    for n in common:
        left = observables(mapping['MIDPHOTO_ENDMICRO'][n]); right = observables(mapping['FULLMID'][n])
        differences[n] = {key: left[key] - right[key] for key in left}
    sequences = {}
    for n in common:
        if 2 * n in differences:
            sequences[n] = {key: two_scale_coefficients(n, differences[n][key], differences[2*n][key]) for key in differences[n]}
    return {'orientation': 'MIDPHOTO_ENDMICRO_minus_FULLMID', 'signed_differences': differences,
            'two_scale_coefficients': sequences, 'reference_used': False,
            'crossing_prediction': 'NOT_FORMED', 'asymptotic_expansion': 'CONDITIONAL_NOT_CERTIFIED'}

def analyze_refinement(baseline_dir, receipts, references):
    native = 'native_source'
    baseline = read_json(Path(baseline_dir) / native / 'SUMMARY.json')['cases']
    f = read_json(Path(baseline_dir) / native / 'fixture.json')
    loaded = completed_results(receipts, baseline_dir)
    expected = [native + '_' + mode + '_' + str(n) for n in (128, 256) for mode in POLICY['new_native_modes']]
    new = [loaded[key] for key in expected if key in loaded]
    cases = baseline + new
    methods = method_pairs(cases)
    chosen_refs = references['fixtures'][native]['reference_results']
    ref_free = {}
    signed = {}
    for mode, levels in methods.items():
        if all(n in levels for n in (64, 128, 256)):
            v = {n: observables(levels[n]) for n in (64, 128, 256)}
            ref_free[mode] = {key: reference_free_order(v[64][key], v[128][key], v[256][key]) for key in v[64]}
        signed[mode] = {}
        for coarse in (32, 64, 128):
            if coarse not in levels or 2*coarse not in levels:
                continue
            co = observables(levels[coarse]); fi = observables(levels[2*coarse])
            by_ref = {}
            for tier, reference in chosen_refs.items():
                target = observables(reference)
                by_ref[tier] = {key: signed_order(co[key]-target[key], fi[key]-target[key]) for key in co}
            ranges = {}
            for key in co:
                rows = [r[key] for r in by_ref.values()]
                values = [r['order'] for r in rows if r['order'] is not None]
                ranges[key] = {'minimum': min(values) if values else None, 'maximum': max(values) if values else None,
                               'unresolved_reference_choices': sum(r['order'] is None for r in rows),
                               'interpretation': 'Observed reference-choice range, not a confidence interval or proof of asymptotic order.'}
            signed[mode][coarse] = {'by_reference': by_ref, 'observed_reference_choice_ranges': ranges}
    endpoint_comparisons = {}
    for result in new:
        key = result['mode'] + '_' + str(result['subdivisions_per_event_interval'])
        endpoint_comparisons[key] = {tier: compare_endpoints(f, result, reference) for tier, reference in chosen_refs.items()}
    return {'schema': 'C21G_POST_CANCELLATION_REFINEMENT_V1',
            'execution_status': 'COMPLETE' if len(new) == 4 else 'NOT_RUN' if not new else 'PARTIAL',
            'missing_or_failed_jobs': [key for key in expected if key not in loaded],
            'new_cases': new, 'reference_free_orders_64_128_256': ref_free,
            'signed_component_orders': signed, 'endpoint_comparisons': endpoint_comparisons,
            'reference_free_hybrid_fullmid_coefficients': coefficient_sequences(cases),
            'new_balance_diagnostics': {r['mode']+'_'+str(r['subdivisions_per_event_interval']): recompute_balances(f, r) for r in new},
            'order_claim': 'EMPIRICAL_SCOPED_DIAGNOSTICS_ONLY', 'global_error_bound': None,
            'holds': POLICY['holds']}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline-dir', type=Path, required=True)
    p.add_argument('--run-dir', type=Path)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    receipts = [read_json(path) for path in sorted((args.run_dir / 'job_receipts').glob('*.json'))] if args.run_dir else []
    references = analyze_references(args.baseline_dir, receipts)
    refinement = analyze_refinement(args.baseline_dir, receipts, references)
    write_new_json(args.out / 'REFERENCE_ASSESSMENT.json', references)
    write_new_json(args.out / 'REFINEMENT_ASSESSMENT.json', refinement)
    if not args.run_dir:
        probe = {name: coefficient_sequences(read_json(args.baseline_dir / name / 'SUMMARY.json')['cases']) for name in POLICY['fixtures']}
        write_new_json(args.out / 'BASELINE_COEFFICIENT_DIAGNOSTIC.json', {
            'schema': 'C21G_NEW_REFERENCE_FREE_COEFFICIENT_DIAGNOSTIC_ON_REUSED_BASELINE_V1',
            'new_native_execution': False, 'old_source_execution_unchanged': True,
            'interpretation': 'New algebraic diagnostic applied to already-published endpoint evidence; no old matrix or full raw audit repeated.',
            'fixtures': probe})

if __name__ == '__main__':
    main()
