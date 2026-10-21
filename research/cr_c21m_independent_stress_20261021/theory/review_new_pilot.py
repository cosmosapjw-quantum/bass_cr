#!/usr/bin/env python3
"""Independent saved-state review. Never calls an ODE integrator.

Construct full tensors directly, use SI kappa/(H/c)^2, reconstruct original
source fields and RHS at 3 stored states per new case, and inspect the L=8
radiation angular reconstruction at the original 64 Gauss-Legendre nodes.
"""
import os
for _key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_key] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import argparse
import copy
import csv
import datetime
import hashlib
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch
sys.dont_write_bytecode = True
import numpy as np
from numpy.polynomial.legendre import leggauss, legvander


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--c21m', type=Path, default=Path('/workspace/scratch/10765dc22dcf/bass_cr/research/cr_c21m_independent_stress_20261021'))
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--analysis', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    c21m, run = args.c21m.resolve(), args.run.resolve()
    c21l = c21m.parent / 'cr_c21l_rei_pilot_20261021'
    sys.path.insert(0, str(c21m))
    import builder
    parent = builder.parent
    manifest_path = run / 'MANIFEST.json'
    manifest_record = json.loads(manifest_path.read_text())
    manifest = manifest_record['manifest']
    identity = manifest_record['identity']
    assert canonical(manifest) == identity
    assert manifest['operational_test_double'] is False
    assert manifest['source']['source_commit'] == '3b85dedce84d37b3e165da00685a8a984950aafe'
    assert len(manifest['grid']['cases']) == 26
    assert manifest['source']['settings']['n'] == 101
    assert manifest['source']['settings']['rtol'] == 3e-11
    assert manifest['source']['settings']['atol'] == 3e-13
    for name, digest in manifest['code_sha256'].items():
        assert sha(c21m / name) == digest, ('frozen_code', name)
    parent.verify_source()
    template = parent.make_template(optimized=False)
    optimized_builder = builder.IndependentStressBuilder()
    assert optimized_builder.identity() == manifest['source']
    source_lock = template.source
    kappa = 8 * math.pi * 6.67430e-11 / 299792458.0**4
    mu, weights = leggauss(64)
    basis = legvander(mu, 8) * (2 * np.arange(9) + 1)
    angular_mins = {key: {'value': float('inf')} for key in ('E_gamma', 'N_gamma', 'E_nu', 'N_nu')}
    errors, records, raw_before = {}, [], {}
    source_states = 0
    bitwise_field_values = 0
    bitwise_rhs_values = 0
    all_times = 0
    maxdiag = dict(Hamiltonian_relative=0., massive_number_relative=0., radiation_number_abs=0.,
                   initial_target_abs=0., initial_Y_abs=0., independent_H2_relative=0.)
    all_derived = {}

    def compare(name, got, expected, rtol=2e-15, atol=0.):
        got, expected = np.asarray(got), np.asarray(expected)
        assert got.shape == expected.shape, (name, got.shape, expected.shape)
        np.testing.assert_allclose(got, expected, rtol=rtol, atol=atol,
                                   equal_nan=True, err_msg=name)
        finite = np.isfinite(got) & np.isfinite(expected)
        if got.dtype.kind == 'b':
            difference = float(np.any(got != expected))
        else:
            difference = float(np.max(abs(got[finite] - expected[finite]))) if finite.any() else 0.
        errors[name] = max(errors.get(name, 0.), difference)

    def tensor_derived(h):
        count = len(h['eta'])
        d = {k: h[k] for k in ('eta', 'Y', 'a', 'H', 's', 'E_gamma', 'N_gamma', 'E_nu', 'N_nu')}
        sigma = np.zeros((count, 3, 3))
        for j, fac in enumerate((-1., -1., 2.)):
            sigma[:, j, j] = fac * h['s']
        norm = np.sqrt(np.einsum('tij,tij->t', sigma, sigma))
        d['Sigma_F'] = norm / h['H']
        d['Sigma_half'] = norm / (math.sqrt(2) * h['H'])
        d['S_signed_F'] = np.sign(h['s']) * norm / h['H']
        p = {x: h[k] for x, k in (('m', 'Pi_matter_J_m3'),
                                   ('gamma', 'Pi_gamma_J_m3'), ('nu', 'Pi_nu_J_m3'))}
        p['r'] = p['gamma'] + p['nu']
        p['tot'] = p['m'] + p['r']
        tensors = {}
        for sector in ('m', 'gamma', 'nu', 'r', 'tot'):
            tensor = np.zeros((count, 3, 3))
            for j, fac in enumerate((-1., -1., 2.)):
                tensor[:, j, j] = fac * p[sector]
            tensors[sector] = tensor
            norm = np.sqrt(np.einsum('tij,tij->t', tensor, tensor))
            normalized = kappa * norm / (h['H'] / 299792458.0)**2
            d['pi_tensor_diag_' + sector + '_J_m3'] = np.diagonal(tensor, axis1=1, axis2=2)
            d['pi_norm_F_' + sector + '_J_m3'] = norm
            d['Pi_' + sector + '_F'] = normalized
            d['P_' + sector + '_signed_F'] = np.sign(p[sector]) * normalized
            d['Pi_' + sector + '_half'] = normalized / math.sqrt(2)
            d['delta_p_' + sector + '_J_m3'] = tensor[:, 2, 2] - tensor[:, 0, 0]
            d['sigma_dot_pi_' + sector + '_J_m3_s'] = np.einsum('tij,tij->t', sigma, tensor)
            compare('trace_' + sector, np.trace(tensor, axis1=1, axis2=2), np.zeros(count), rtol=0.)
        compare('tensor_radiation_addition', tensors['r'], tensors['gamma'] + tensors['nu'], rtol=0.)
        compare('tensor_total_addition', tensors['tot'], tensors['m'] + tensors['r'], rtol=0.)
        denominator = abs(p['m']) + abs(p['r'])
        valid = denominator > 0
        cancel = np.full(count, np.nan)
        cancel[valid] = 1 - abs(p['tot'][valid]) / denominator[valid]
        d['cancellation'] = cancel
        d['cancellation_defined'] = valid
        d['opposing_signs'] = p['m'] * p['r'] < 0
        assert np.all(d['Pi_tot_F'] <= d['Pi_m_F'] + d['Pi_r_F'] + 2e-18)
        assert np.all(cancel[valid] >= -5e-15) and np.all(cancel[valid] <= 1 + 5e-15)
        return d

    with patch.object(parent.CanonicalFVSpecies, 'integrate', side_effect=AssertionError('ODE PROHIBITED IN REVIEW')):
        for case in manifest['grid']['cases']:
            case_id = case['case_id']
            folder = run / 'cases' / case_id
            raw_path, receipt_path = folder / 'history.npz', folder / 'RESULT.json'
            receipt = json.loads(receipt_path.read_text())
            mark = json.loads((folder / 'COMPLETE.json').read_text())
            reservation = json.loads((folder / 'RESERVATION.json').read_text())
            assert receipt['status'] == 'COMPLETE' and receipt['case'] == case
            assert receipt['identity'] == mark['identity'] == reservation['identity'] == identity
            assert mark['case_id'] == case_id and reservation['case'] == case
            assert receipt['operational_test_double'] is False
            assert sha(raw_path) == receipt['history_sha256'] == mark['history_sha256']
            assert sha(receipt_path) == mark['result_sha256']
            raw_before[str(raw_path)] = sha(raw_path)
            raw_before[str(receipt_path)] = sha(receipt_path)
            with np.load(raw_path, allow_pickle=False) as archive:
                h = {k: archive[k] for k in archive.files}
            assert h['Y'].shape == (40, 101) and h['Y'].dtype == np.float64
            assert all(np.isfinite(v).all() for k, v in h.items() if k != 'cancellation_fraction')
            assert np.all(np.diff(h['eta']) > 0)
            compare('a_from_eta', h['a'], source_lock.aref * np.exp(h['eta']))
            compare('redshift_range', h['a'][[0, -1]], np.array([1/21, .2]))
            compare('proper_elapsed', h['proper_elapsed_s'], h['Y'][0] / source_lock.href, rtol=0.)
            assert np.all(h['GammaT'] == 0) and np.all(h['n_e_cm3'] == 0)
            assert np.all(h['thermal_energy_norm'] == 0)
            derived = tensor_derived(h)
            all_derived[case_id] = derived
            for key in ('Sigma_F', 'Sigma_half'):
                compare('stored_' + key, h[key], derived[key])
            compare('stored_signed_Sigma', h['signed_Sigma_F'], derived['S_signed_F'])
            for sector in ('m', 'gamma', 'nu', 'r', 'tot'):
                for suffix in ('F', 'half'):
                    key = 'Pi_' + sector + '_' + suffix
                    compare('stored_' + key, h[key], derived[key])
                compare('stored_signed_' + sector, h['signed_Pi_' + sector + '_F'], derived['P_' + sector + '_signed_F'])
                compare('stored_dp_' + sector, h['delta_p_' + sector + '_J_m3'], derived['delta_p_' + sector + '_J_m3'], rtol=0.)
            compare('stored_cancellation', h['cancellation_fraction'], derived['cancellation'], rtol=0.)
            mapping = receipt['mapping']
            original = copy.copy(template)
            original.momentum = parent.CanonicalMomentumFV(30., mapping['A_m'], 24, 12, gauss_order=3)
            original.Sigma_ref = mapping['source_Sigma_ref_half']
            original.orientation = mapping['source_orientation']
            original.k_gamma, original.k_nu = mapping['k_gamma'], mapping['k_nu']
            original._nfev = 0
            optimized, optimized_mapping = optimized_builder.build(case['S0'], case['Pm0'], case['Pr0'])
            compare('mapping_A', np.array(optimized_mapping['A_m']), np.array(mapping['A_m']), rtol=0.)
            compare('initial_source_Y', h['Y'][:, 0], original.initial_state(), rtol=0.)
            maxdiag['initial_Y_abs'] = max(maxdiag['initial_Y_abs'], float(np.max(abs(h['Y'][:, 0] - original.initial_state()))))
            target_error = max(abs(float(derived[name][0]) - case[target]) for name, target in
                               (('S_signed_F', 'S0'), ('P_m_signed_F', 'Pm0'), ('P_r_signed_F', 'Pr0')))
            maxdiag['initial_target_abs'] = max(maxdiag['initial_target_abs'], target_error)
            assert target_error < 2e-13
            hres = float(np.max(abs(h['Einstein_H2'] / h['H']**2 - 1)))
            number = float(np.max(abs(h['massive_physical_number_norm'] * np.exp(3*h['eta']) /
                                      original.momentum.total_cell_number - 1)))
            radnumber = max(float(np.max(abs(h[key][:, 0] - 1))) for key in ('N_gamma', 'N_nu'))
            recomputed_h2 = h['s']**2 + (8*math.pi*6.67430e-11/(3*299792458.0**2)) * source_lock.rhocrit_j_m3 * (
                h['dust_energy_norm'] + h['massive_energy_norm'] + h['rad_energy_norm'] + source_lock.omega_lambda)
            ihres = float(np.max(abs(recomputed_h2 / h['H']**2 - 1)))
            for key, value in (('Hamiltonian_relative', hres), ('massive_number_relative', number),
                               ('radiation_number_abs', radnumber), ('independent_H2_relative', ihres)):
                maxdiag[key] = max(maxdiag[key], value)
            assert hres <= 2e-13 and number <= 2e-13 and radnumber <= 2e-10 and ihres <= 2e-13
            assert np.min(h['massive_min_cell_population']) >= 0
            assert min(1 + mapping['A_m'], 1 - mapping['A_m']/2) >= 0
            assert max(abs(mapping['k_gamma']), abs(mapping['k_nu'])) <= .5
            for key in angular_mins:
                reconstructed = h[key] @ basis.T
                index = np.unravel_index(int(np.argmin(reconstructed)), reconstructed.shape)
                value = float(reconstructed[index])
                assert value >= 0, ('SAMPLED_L8_NEGATIVE', case_id, key, value, index)
                if value < angular_mins[key]['value']:
                    angular_mins[key] = dict(value=value, case_id=case_id,
                        saved_index=int(index[0]), mu_node=int(index[1]), mu=float(mu[index[1]]))
                # Orthogonality confirms the reconstruction convention at source nodes.
                compare('reconstructed_monopole_' + key, reconstructed @ (weights/2), h[key][:, 0], rtol=3e-15)
            for j in (0, 50, 100):
                eta, y = float(h['eta'][j]), h['Y'][:, j]
                fields = original.fields(eta, y)
                for key, value in fields.items():
                    if isinstance(value, (float, int, np.floating, np.integer)):
                        compare('original_field_' + key, np.asarray(h[key][j]), np.asarray(value), rtol=0.)
                        assert np.asarray(h[key][j]).tobytes() == np.asarray(value, dtype=h[key].dtype).tobytes(), ('FIELD_BYTES', case_id, j, key)
                        bitwise_field_values += 1
                    elif isinstance(value, np.ndarray):
                        compare('original_field_' + key, h[key][j], value, rtol=0.)
                        assert h[key][j].tobytes() == np.asarray(value, dtype=h[key].dtype).tobytes(), ('FIELD_BYTES', case_id, j, key)
                        bitwise_field_values += value.size
                original_rhs = original.rhs(eta, y)
                optimized_rhs = optimized.rhs(eta, y)
                compare('original_vs_reuse_RHS', optimized_rhs, original_rhs, rtol=0.)
                assert optimized_rhs.dtype == original_rhs.dtype == np.float64
                assert optimized_rhs.tobytes() == original_rhs.tobytes(), ('RHS_BYTES', case_id, j)
                bitwise_rhs_values += original_rhs.size
                # Independently express the proper-time shear equation in SI.
                d_s_dt = original_rhs[2] * source_lock.href * fields['H']
                pressure_sum = sum(fields[key] for key in ('Pi_gamma_J_m3', 'Pi_nu_J_m3', 'Pi_matter_J_m3'))
                physical_shear_rhs = -3 * fields['H'] * fields['s'] + kappa * 299792458.0**2 * pressure_sum
                compare('SI_shear_evolution', np.asarray(d_s_dt), np.asarray(physical_shear_rhs), rtol=4e-15, atol=2e-45)
                source_states += 1
            all_times += len(h['eta'])
            records.append({'case_id': case_id, 'raw_sha256': sha(raw_path), 'receipt_sha256': sha(receipt_path),
                            'A_m': mapping['A_m'], 'k_gamma': mapping['k_gamma'],
                            'target_max_abs_error': target_error})

    analysis_evidence = {'status': 'NOT_REVIEWED_NO_PATH'}
    if args.analysis:
        out = args.analysis.resolve()
        with np.load(out / 'components27.npz', allow_pickle=False) as archive:
            arrays = {k: archive[k] for k in archive.files}
        rows = list(csv.DictReader((out / 'endpoints27.csv').open()))
        assert len(rows) == len(arrays['case_id']) == 27
        sources = json.loads((out / 'INPUT_SOURCES.json').read_text())
        assert sources['run_identity'] == identity
        reference = json.loads((c21m / 'REFERENCE_REUSE.json').read_text())
        reference_paths = {key: c21l/path for key, path in reference['source_paths_relative_to_C21L'].items()}
        for key, path in reference_paths.items():
            assert sha(path) == reference['source_sha256'][key]
        with np.load(reference_paths['raw'], allow_pickle=False) as archive:
            refh = {k: archive[k] for k in archive.files}
        all_derived[reference['case_id']] = tensor_derived(refh)
        for i, case_id in enumerate(arrays['case_id']):
            case_id = str(case_id)
            assert rows[i]['case_id'] == case_id
            for key, value in all_derived[case_id].items():
                if key in arrays:
                    compare('analysis_' + key, arrays[key][i], value)
            for key in ('S_signed_F', 'Sigma_F', 'P_m_signed_F', 'P_r_signed_F', 'P_tot_signed_F',
                        'Pi_m_F', 'Pi_r_F', 'Pi_tot_F', 'cancellation'):
                compare('csv_endpoint_' + key, np.asarray(float(rows[i][key + '_end'])), np.asarray(all_derived[case_id][key][-1]))
        output_manifest = json.loads((out / 'OUTPUT_MANIFEST.json').read_text())
        for name, item in output_manifest['files'].items():
            assert sha(out/name) == item['sha256'] and (out/name).stat().st_size == item['size']
        analysis_evidence = {'status': 'PASS_SCOPED', 'plotted_cases': 27, 'new_cases': 26, 'reused_C21L_cases': 1,
            'all_saved_times': 2727, 'components27_sha256': sha(out/'components27.npz'),
            'endpoints27_sha256': sha(out/'endpoints27.csv'), 'output_manifest_sha256': sha(out/'OUTPUT_MANIFEST.json'),
            'visual_inspection': 'PENDING_SEPARATE_DIRECT_IMAGE_REVIEW'}

    assert all(sha(path) == digest for path, digest in raw_before.items())
    result = {'schema': 'C21M_INDEPENDENT_SAVED_STATE_REVIEW_V1',
        'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'PASS_SCOPED', 'findings': [],
        'reviewer': 'independent theory_literature agent, not scientific runner/analyzer implementer',
        'run_identity': identity, 'manifest_sha256': sha(manifest_path),
        'script_sha256': sha(__file__), 'source_code_sha256': manifest['code_sha256'],
        'source_commit': manifest['source']['source_commit'],
        'scope': {'new_cases': 26, 'saved_times_checked': all_times, 'original_field_RHS_states': source_states,
            'bitwise_original_field_scalar_values': bitwise_field_values,
            'bitwise_original_vs_reuse_RHS_scalar_values': bitwise_rhs_values,
            'new_ODE_integrations_by_review': 0, 'source_state_count': 40},
        'maximum_diagnostic_residuals': maxdiag, 'max_absolute_differences': errors,
        'radiation_angular_positivity': {'status': 'PASS_SCOPED_DISCRETE_SAMPLED',
            'reconstruction': 'sum_{ell=0}^8 (2ell+1) J_ell P_ell(mu)',
            'nodes': 'same 64 Gauss-Legendre nodes as source legendre_matrix default L=8',
            'samples_per_species': 26 * 101 * 64, 'total_angular_samples': 26 * 101 * 64 * 4,
            'minima': angular_mins, 'continuous_angle_positivity_theorem': False,
            'monopole_positivity_is_separate_from_angular_reconstruction': True},
        'analysis': analysis_evidence, 'raw_cases': records, 'inputs_unchanged': True,
        'claim_limits': ['No original ODE trajectory rerun or new global bitwise trajectory equivalence claim.',
            'Original-v-reuse equality is verified only at three stored states per new case for all source fields and all 40 RHS components.',
            'Hamiltonian residual is an algebraic consistency check, not an independent global error bound.',
            'Radiation positivity is discrete sampled L8 reconstruction at stored times and original angular nodes, not a continuum or between-time theorem.',
            'Preliminary non-tilted collisionless LRS Bianchi I; no full reionization or CMB Einstein-Boltzmann prediction.',
            'No performance benchmark, speedup, scaling or memory-improvement claim.'],
        'global_error_bound': None, 'performance_benchmark': False}
    with args.output.open('x') as handle:
        json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')
    print(json.dumps({k: result[k] for k in ('status', 'run_identity', 'scope', 'maximum_diagnostic_residuals', 'radiation_angular_positivity')}, indent=2))


if __name__ == '__main__':
    main()
