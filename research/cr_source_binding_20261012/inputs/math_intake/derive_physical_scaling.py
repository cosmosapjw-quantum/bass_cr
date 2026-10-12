"""Exact arithmetic of saved scalar coefficients; no physics imports or runs.

Candidate derivation only. Source values are recorded decimals, not intervals
for continuum/input error. The frozen source and finite-kernel scope persists.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1] / 'bass_cr'
COMMIT = '4ca5a90de79c8fb82a25fd9e83615bec0dfa870b'
INPUTS = {
    'cached': ('research/cr_rux_m1_m3_20261012/inputs/CACHED_RESPONSE.json',
               '60747f9da89e3596bfeb93a4ec14a1bb58a33bca3a09629fc092f254839f3b7b'),
    'source_coverage': ('research/cr_phys02c_20261011/evidence/runs/R001/NUMERICAL_RESULT.json',
                        '36ea403320bcc711c4955de55e2a7e9f65c2deaf851a882bd9581585fb857624'),
    'actual_fullBED': ('research/cr_phys02e_ncp_return_20261011/actual_run/RESULT_fullBED.json',
                       '96942b80ff6ac2aea261cfdd71fec216c2099c4afece173b225fa6cebcc321f1'),
    'actual_legacy': ('research/cr_phys02e_ncp_return_20261011/actual_run/RESULT_legacy.json',
                      '7ed2533a1dd3999713c9d5e676971719a59231f6cda1315ee2d276d9c0cb5d82'),
}


def read_source(name):
    path, expected = INPUTS[name]
    raw = subprocess.check_output(['git', 'show', COMMIT + ':' + path], cwd=REPO)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise ValueError('SOURCE_IDENTITY_MISMATCH: ' + path)
    return json.loads(raw, parse_float=str, parse_int=str), {
        'path': path, 'commit': COMMIT, 'sha256': digest, 'bytes': len(raw)}


def rational(record):
    return F(int(record['numerator']), int(record['denominator']))


def render(value):
    with localcontext() as context:
        context.prec = 60
        decimal = str(Decimal(value.numerator) / Decimal(value.denominator))
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator),
            'decimal60': decimal}


def main():
    start = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat()
    loaded = {key: read_source(key) for key in INPUTS}
    cache = loaded['cached'][0]
    coverage = loaded['source_coverage'][0]['coverage']
    actual = {model: loaded['actual_' + model][0] for model in ('fullBED', 'legacy')}
    T = rational(cache['T_s'])
    scales = {model: F(data['physical_energy_scale_eV_m3']) for model, data in actual.items()}
    if T != 10**10 or scales['fullBED'] != scales['legacy']:
        raise ValueError('SOURCE_TIME_OR_SCALE_IDENTITY_MISMATCH')
    scale = scales['fullBED']
    ev_j = F('1.602176634e-19')
    kb = F('1.380649e-23')
    n_h, y_he, xi = F(140), F('0.248'), F('0.01')
    n_he = n_h * y_he / (4 * (1 - y_he))
    n_e = xi * (n_h + n_he)
    cv = F(3, 2) * kb * (n_h + n_he + n_e)
    a_selected = scale / T**2
    a_all = F(coverage['all_direct_A_energy_eV_m3_s2'])
    a_outside = a_all - a_selected
    if a_outside < 0:
        raise ValueError('NEGATIVE_OUTSIDE_SOURCE_ENERGY')
    q_star = ev_j * scale / T
    selected_injected = ev_j * scale / 2
    all_injected = ev_j * T**2 * a_all / 2
    outside_injected = ev_j * T**2 * a_outside / 2
    outside_endpoint_source_power = ev_j * T * a_outside
    rows = []
    for row in cache['rows']:
        h0, p, r, s = [rational(row['moments'][key]) for key in ('H0', 'p', 'R', 'S')]
        power = q_star * h0 * r
        heat = selected_injected * h0 * s
        reference = actual[row['model']]
        old_power, old_heat = F(reference['SI_J1']), F(reference['SI_J2'])
        rows.append({
            'model': row['model'], 'representation': row['representation'],
            'H0': render(h0), 'p': render(p), 'R': render(r), 'S': render(s),
            'selected_heat_power_J_m3_s': render(power),
            'selected_cumulative_heat_J_m3': render(heat),
            'same_kernel_eventual_yield_proxy_power_J_m3_s': render(q_star * h0),
            'frozen_composition_calorimetric_delta_T_K': render(heat / cv),
            'outside_energy_only_conditional_heat_interval_J_m3': [render(heat), render(heat + outside_injected)],
            'outside_energy_only_conditional_delta_T_interval_K': [render(heat / cv), render((heat + outside_injected) / cv)],
            'stationary_nonnegative_outside_kernel_conditional_power_upper_J_m3_s': render(power + outside_endpoint_source_power),
            'recorded_same_kernel_SI_J1': reference['SI_J1'],
            'recorded_same_kernel_SI_J2': reference['SI_J2'],
            'decimal_representation_comparison_only': {
                'power_relative_difference': render((power - old_power) / old_power),
                'heat_relative_difference': render((heat - old_heat) / old_heat),
                'is_physical_error_bound': False,
            },
        })
    output = {
        'schema': 'cr-source-binding-physical-scaling-candidate.v1',
        'role': 'CANDIDATE_DERIVATION_AND_SAVED_SCALAR_ARITHMETIC; NOT_FINAL_DECISION_REVIEW',
        'evidence_status': ['derived', 'numerically_checked_saved_scalar_arithmetic'],
        'inputs': {key: item[1] for key, item in loaded.items()},
        'representation_policy': 'Every recorded decimal is treated as an exact arithmetic input; selected_record and birth_defined stay separate.',
        'fixed_scope': {'time_s': render(T), 'xi': render(xi), 'n_h_m3': render(n_h),
                        'n_he_m3': render(n_he), 'n_e_m3': render(n_e), 'Y_He': render(y_he),
                        'temperature_K': 100, 'proton_collision_window_eV': [1000000, 4000000],
                        'selected_direct_electron_birth_window_eV': ['0.1', '900'],
                        'source': 'Q_e(W,t)=t*A(W), zero initial nonthermal population, leading local source, frozen bath'},
        'constants': {'eV_in_J': render(ev_j), 'k_B_J_K': render(kb),
                      'basis': 'Exact SI defining constants; hbar, c, and k_B are not set to one.'},
        'source_normalization': {
            'physical_energy_scale_eV_m3': render(scale),
            'selected_A_energy_eV_m3_s2': render(a_selected),
            'all_secondary_A_energy_eV_m3_s2': render(a_all),
            'outside_selected_A_energy_eV_m3_s2': render(a_outside),
            'selected_fraction_from_recorded_scale_and_full_A': render(a_selected / a_all),
            'recorded_source_coverage_fraction': coverage['selected_fraction_of_all_direct'],
            'fraction_difference_due_to_separate_recorded_rounding': render(a_selected / a_all - F(coverage['selected_fraction_of_all_direct'])),
            'q_star_selected_J_m3_s': render(q_star),
            'nominal_selected_cumulative_injected_energy_J_m3': render(selected_injected),
            'all_secondary_cumulative_injected_energy_J_m3': render(all_injected),
            'outside_selected_cumulative_injected_energy_J_m3': render(outside_injected),
            'all_secondary_endpoint_injection_power_J_m3_s': render(ev_j * T * a_all),
            'outside_selected_endpoint_injection_power_J_m3_s': render(outside_endpoint_source_power),
            'normalization_note': 'Uses the saved global source amplitude and original b columns, without rescaling b by a separately rounded injected-energy total.'},
        'heat_capacity_J_m3_K': render(cv),
        'all_secondary_kinetic_energy_calorimetric_upper_K': render(all_injected / cv),
        'rows': rows,
        'envelope_conditions': [
            'Full means all direct secondary kinetic energy born from the same active 1--4 MeV proton window; it is not the full 10 keV--1 PeV CR injection budget.',
            'The outside energy interval assumes nonnegative heat and no contribution beyond the outside cohort kinetic energy; all outside energy is allowed to thermalize by T.',
            'The lower endpoint retains the selected fixed finite-model heat and treats outside heat as zero; it does not certify the selected physical-model error.',
            'The optional instantaneous-power upper additionally requires a stationary causal nonnegative outside response of eventual heat yield at most one and the same monotone linear onset.',
            'Delta T is E_heat/Cv at fixed composition, density and volume; no expansion, changing particle number, cooling, feedback, or coupled cosmological integration is included.',
            'The stored full source integral comes from the same execution-bound source constructor before the 2400/4800 mesh loop; the scalar is reused, not newly integrated on 9600.',
        ],
        'counts': {'exact_scalar_postprocessing': 1, 'G': 0, 'pulse': 0, 'expm': 0,
                   'resolvent': 0, 'linear_solve': 0, 'source_quadrature': 0, 'old_suite': 0, 'F_retry': 0, 'H': 0},
    }
    target = ROOT / 'PHYSICAL_SCALING_CANDIDATE.json'
    if target.exists():
        raise FileExistsError('Candidate already exists; preserve it instead of silent rerun.')
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    receipt = {'schema': 'cr-source-binding-exact-arithmetic-receipt.v1', 'started_utc': started_utc,
               'finished_utc': datetime.now(timezone.utc).isoformat(), 'wall_s': time.monotonic() - start,
               'source_commit': COMMIT, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'result_path': str(target), 'result_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
               'counts': output['counts'], 'final_scientific_decision': 'NOT_REQUESTED_FROM_CANDIDATE_AUTHOR'}
    (ROOT / 'ARITHMETIC_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': 'CANDIDATE_SAVED', 'result': str(target), 'sha256': receipt['result_sha256'],
                      'q_star_J_m3_s': render(q_star)['decimal60'], 'Cv_J_m3_K': render(cv)['decimal60'],
                      'selected_fullBED': {key: rows[0][key]['decimal60'] for key in
                       ('selected_heat_power_J_m3_s', 'selected_cumulative_heat_J_m3', 'frozen_composition_calorimetric_delta_T_K')},
                      'outside_energy_J_m3': render(outside_injected)['decimal60'],
                      'outside_envelope_fullBED_delta_T_upper_K': rows[0]['outside_energy_only_conditional_delta_T_interval_K'][1]['decimal60']}, indent=2))


if __name__ == '__main__':
    main()
