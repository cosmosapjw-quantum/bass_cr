"""Create component diagnostics for exactly four C21N off-grid histories.

This is postprocessing only: it loads sealed raw outputs and the immutable
accepted 125-case component archive; it never imports or invokes a solver.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUN = Path('/root/bass_cr_c21n_offgrid4_runs/runs/offgrid4_20261021131011')
BASE = REPO / 'research/cr_c21m_independent_stress_20261021/analysis_campaign125_20261021/components_campaign.npz'
OUT = Path('/root/c21n_offgrid4_20261021/analysis_offgrid4_20261021')
GRID = HERE / 'prepared_offgrid4/grid_offgrid4.json'
EXPECTED_ID = 'a07a95f85042f9db7df2e3e465288524b458bcb6f190e9d4f01db1869c139360'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canon(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def write_json(path: Path, obj):
    with path.open('x') as f:
        json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def load_component_module():
    path = REPO / 'research/cr_c21l_rei_pilot_20261021/component_split_20261021/analyze_components.py'
    spec = importlib.util.spec_from_file_location('c21n_offgrid4_component_decomposition', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, path


def main():
    if OUT.exists():
        raise FileExistsError(f'CREATE_ONLY:{OUT}')
    grid = json.loads(GRID.read_text())
    envelope = json.loads((RUN / 'MANIFEST.json').read_text())
    manifest = envelope['manifest']
    frozen_grid = {k: grid[k] for k in ('schema', 'run_id', 'cases')}
    if (envelope['identity'] != EXPECTED_ID or canon(manifest) != EXPECTED_ID
            or manifest['grid'] != frozen_grid or manifest['grid_file_sha256'] != sha(GRID)
            or manifest['operational_test_double'] is not False
            or manifest['source']['source_commit'] != '3b85dedce84d37b3e165da00685a8a984950aafe'):
        raise ValueError('FIXED_SOURCE_OR_GRID_IDENTITY_MISMATCH')
    if manifest['source']['settings'] != {
        'Tcmb0_K': 2.7255, 'angular_cells': 12, 'atol': 3e-13, 'donor': None,
        'ellmax': 8, 'mass_fraction': 0.1, 'mass_over_Tref': 30.0,
        'massive_A': 'independently inverted in [-1,2]', 'n': 101, 'rtol': 3e-11,
        'radial_cells': 24, 'subcell_gauss_order': 3
    }:
        raise ValueError('SOLVER_OR_PHYSICS_SETTINGS_MISMATCH')
    if len(grid['cases']) != 4:
        raise ValueError('EXPECTED_EXACTLY_FOUR_NEW_CASES')
    original_base_sha = sha(BASE)
    with np.load(BASE, allow_pickle=False) as archive:
        base = {k: archive[k] for k in archive.files}
    if base['Y'].shape != (125, 40, 101) or base['requested_signed_full'].shape != (125, 3):
        raise ValueError('ACCEPTED_125_BASE_REQUIRED')
    decomp, component_source = load_component_module()
    derived_rows, physics, history_hashes, result_hashes = [], [], [], []
    new_arrays = []
    for case in grid['cases']:
        folder = RUN / 'cases' / case['case_id']
        rp, hp = folder / 'RESULT.json', folder / 'history.npz'
        result = json.loads(rp.read_text())
        seal = json.loads((folder / 'COMPLETE.json').read_text())
        reservation = json.loads((folder / 'RESERVATION.json').read_text())
        digest = sha(hp)
        if (result.get('identity') != EXPECTED_ID or result.get('status') != 'COMPLETE'
                or result.get('case') != case or result.get('state_shape') != [40, 101]
                or result.get('dtype') != 'float64' or seal.get('identity') != EXPECTED_ID
                or seal.get('case_id') != case['case_id'] or seal.get('history_sha256') != digest
                or result.get('history_sha256') != digest or seal.get('result_sha256') != sha(rp)
                or reservation.get('identity') != EXPECTED_ID or reservation.get('case') != case):
            raise ValueError('RAW_RESULT_COMPLETE_RESERVATION_SEAL_MISMATCH:' + case['case_id'])
        with np.load(hp, allow_pickle=False) as z:
            h = {k: z[k] for k in z.files}
        if h['Y'].shape != (40, 101) or h['Y'].dtype != np.float64 or not np.isfinite(h['Y']).all():
            raise ValueError('NONFINITE_OR_WRONG_STATE_ARRAY:' + case['case_id'])
        d = decomp.components(h)
        eta = np.asarray(h['eta'])
        if (eta.shape != (101,) or not np.all(np.diff(eta) > 0)
                or abs(float(h['a'][0]) - 1/21) > 2e-15 or abs(float(h['a'][-1]) - .2) > 2e-15):
            raise ValueError('SAVED_GRID_NOT_Z20_TO_Z4:' + case['case_id'])
        if np.max(np.abs(d['P_tot_signed_F'] - d['P_m_signed_F'] - d['P_r_signed_F'])) > 2e-15:
            raise ValueError('SIGNED_COMPONENT_SUM_GATE:' + case['case_id'])
        if np.max(np.abs(d['S_signed_F'] - np.sqrt(6.) * h['s'] / h['H'])) > 2e-15:
            raise ValueError('SHEAR_DEFINITION_GATE:' + case['case_id'])
        ham = float(np.max(np.abs(h['Einstein_H2'] / h['H']**2 - 1)))
        number = h['massive_physical_number_norm'] * np.exp(3 * eta)
        number_res = float(np.max(np.abs(number / number[0] - 1)))
        radiation_zero = max(float(np.max(np.abs(h[k][:, 0] - 1))) for k in ('N_gamma', 'N_nu'))
        min_cell = float(np.min(h['massive_min_cell_population']))
        if ham > 2e-13 or number_res > 2e-13 or radiation_zero > 2e-10 or min_cell < 0:
            raise ValueError('PHYSICS_INVARIANT_GATE:' + case['case_id'])
        row = {'case_id': case['case_id'], 'S0': case['S0'], 'Pm0': case['Pm0'], 'Pr0': case['Pr0'],
               'source_identity': EXPECTED_ID, 'run_id': grid['run_id'],
               'history_sha256': digest, 'result_sha256': sha(rp),
               'Hamiltonian_max_relative': ham, 'massive_comoving_number_max_relative': number_res,
               'radiation_number_max_abs': radiation_zero, 'minimum_massive_cell_population': min_cell,
               'initial_axis_max_abs_error': max(abs(float(d[k][0]) - case[v]) for v, k in
                   (('S0', 'S_signed_F'), ('Pm0', 'P_m_signed_F'), ('Pr0', 'P_r_signed_F')))}
        for key in ('S_signed_F', 'Sigma_F', 'P_m_signed_F', 'P_gamma_signed_F', 'P_nu_signed_F',
                    'P_r_signed_F', 'P_tot_signed_F', 'Pi_m_F', 'Pi_gamma_F', 'Pi_nu_F', 'Pi_r_F',
                    'Pi_tot_F', 'cancellation'):
            row[key + '_initial'] = float(d[key][0]) if np.isfinite(d[key][0]) else None
            row[key + '_z4'] = float(d[key][-1]) if np.isfinite(d[key][-1]) else None
        physics.append({k: row[k] for k in ('case_id', 'Hamiltonian_max_relative',
            'massive_comoving_number_max_relative', 'radiation_number_max_abs',
            'minimum_massive_cell_population', 'initial_axis_max_abs_error')})
        history_hashes.append({'case_id': case['case_id'], 'path': str(hp), 'sha256': digest, 'bytes': hp.stat().st_size})
        result_hashes.append({'case_id': case['case_id'], 'path': str(rp), 'sha256': sha(rp), 'bytes': rp.stat().st_size})
        d.update({k: h[k] for k in ('Y', 'E_gamma', 'N_gamma', 'E_nu', 'N_nu')})
        new_arrays.append((case, d))
        derived_rows.append(row)
    # Extend the accepted 125 arrays in-memory; verify the original block is unchanged.
    merged = {}
    meta = {'case_id': [], 'origin': [], 'source_run_id': [], 'source_identity': [], 'campaign_case_key': []}
    for k, arr in base.items():
        if k in meta or k == 'requested_signed_full':
            continue
        tails = []
        for case, d in new_arrays:
            if k not in d:
                raise ValueError('COMPONENT_FIELD_UNAVAILABLE:' + k)
            v = np.asarray(d[k])
            expected_shape = arr.shape[1:]
            if v.shape != expected_shape:
                raise ValueError(f'COMPONENT_SHAPE_MISMATCH:{k}:{v.shape}:{expected_shape}')
            tails.append(v)
        merged[k] = np.concatenate((arr, np.stack(tails)), axis=0)
        if not np.array_equal(merged[k][:125], arr):
            raise ValueError('ACCEPTED_125_BYTES_CHANGED:' + k)
    for k in ('case_id', 'origin', 'source_run_id', 'source_identity', 'campaign_case_key'):
        meta[k] = list(base[k].tolist())
    for case, _ in new_arrays:
        meta['case_id'].append(case['case_id'])
        meta['origin'].append('NEW_OFFGRID4_NCP')
        meta['source_run_id'].append(grid['run_id'])
        meta['source_identity'].append(EXPECTED_ID)
        meta['campaign_case_key'].append(grid['run_id'] + '::' + case['case_id'])
    merged.update({k: np.asarray(v) for k, v in meta.items()})
    merged['requested_signed_full'] = np.vstack((base['requested_signed_full'],
        np.asarray([[c['S0'], c['Pm0'], c['Pr0']] for c, _ in new_arrays], dtype=np.float64)))
    if sha(BASE) != original_base_sha:
        raise ValueError('ACCEPTED_125_SOURCE_FILE_CHANGED')
    OUT.mkdir(parents=True, exist_ok=False)
    decomp.deterministic_npz(OUT / 'components_campaign129.npz', merged)
    with (OUT / 'offgrid4_endpoints.csv').open('x', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(derived_rows[0]))
        w.writeheader(); w.writerows(derived_rows)
    checks = {'schema': 'C21N_OFFGRID4_PHYSICS_CHECKS_V1', 'status': 'PASS_SCOPED',
              'cases': physics, 'accepted_125_prefix_array_equal': True,
              'signed_component_sum_max_abs': max(float(np.max(np.abs(d['P_tot_signed_F']-d['P_m_signed_F']-d['P_r_signed_F']))) for _,d in new_arrays),
              'component_norm_equals_abs_signed_max_abs': max(float(np.max(np.abs(d['Pi_tot_F']-np.abs(d['P_tot_signed_F'])))) for _,d in new_arrays),
              'new_ODE_integrations': 0, 'global_error_bound': None}
    write_json(OUT / 'PHYSICS_CHECKS.json', checks)
    summary = {'schema': 'C21N_OFFGRID4_COMPONENT_ANALYSIS_V1', 'status': 'PASS_SCOPED',
       'new_cases': 4, 'combined_unique_actual_cases': 129, 'accepted_125_ODE_replays': 0,
       'new_ODE_integrations_by_analysis': 0, 'interpolation': False,
       'saved_samples_per_case': 101, 'state_count': 40, 'dtype': 'float64',
       'solver': 'DOP853 rtol=3e-11 atol=3e-13; z=20 to z=4',
       'component_convention': 'full Frobenius; signed S, P_m, P_gamma, P_nu, P_r, P_tot; norms are absolute values',
       'endpoint_ranges': {k: [min(r[k+'_z4'] for r in derived_rows), max(r[k+'_z4'] for r in derived_rows)]
                           for k in ('S_signed_F','P_m_signed_F','P_gamma_signed_F','P_nu_signed_F','P_r_signed_F','P_tot_signed_F')},
       'global_error_bound': None, 'triaxial': 'HOLD', 'full_reionization': 'HOLD', 'CMB': 'HOLD'}
    write_json(OUT / 'SUMMARY.json', summary)
    run_summary = json.loads(next(RUN.glob('SUMMARY_*.json')).read_text())
    write_json(OUT / 'INPUT_BINDINGS.json', {'content_commit': '5ecb8a6c4961302b7066b06278e72ecd2d77f8c9',
       'content_tree': EXPECTED_ID, 'grid_path': str(GRID), 'grid_sha256': sha(GRID),
       'run_path': str(RUN), 'run_manifest_sha256': sha(RUN/'MANIFEST.json'),
       'run_identity': EXPECTED_ID, 'base125_path': str(BASE), 'base125_sha256': original_base_sha,
       'component_source_path': str(component_source), 'component_source_sha256': sha(component_source),
       'history_files': history_hashes, 'result_files': result_hashes,
       'software': manifest['software'], 'host': {'hostname': run_summary['observed_hostname'], 'platform': run_summary['observed_platform']},
       'global_error_bound': None})
    write_json(OUT / 'OUTPUT_MANIFEST.json', {'status': 'PASS_SCOPED', 'original_125_source_unchanged': True,
       'files': [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(OUT.iterdir()) if p.is_file()],
       'global_error_bound': None})
    print(json.dumps({'status': 'PASS_SCOPED', 'new_cases': 4, 'combined_cases': 129,
                      'output': str(OUT), 'physics_checks': physics}, indent=2))


if __name__ == '__main__':
    main()
