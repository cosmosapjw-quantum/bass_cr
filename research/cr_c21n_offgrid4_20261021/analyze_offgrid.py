"""Read-only, source-pinned analysis of four new C21N off-grid trajectories.

No ODE solver is called. Legacy source modules supply static fields/RHS only.
The original C21L decomposition and C21M physics checks are reused unchanged.
Source/input/output paths are explicit; analysis output is create-only.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile

for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
              'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_name] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ.setdefault('MPLBACKEND', 'Agg')
sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_REPO = HERE.parent.parent
SOURCE_COMMIT = '3b85dedce84d37b3e165da00685a8a984950aafe'
EXECUTION_CONTENT = '5ecb8a6c4961302b7066b06278e72ecd2d77f8c9'
EXPECTED_IDENTITY = 'f42cb88bea0ebc3ed6114f092751ea9343dee9c46fbf474215fef2c9375c9023'
EXPECTED_GRID_SHA = '2a74af40c5508fc332dd3671955ad2dda6fc3e8de51bc61dcc3730a6798913b5'
CONTEXT125_SHA = 'd73ab77a1304ee566c3dad3a12bf2f2123f7a70e5b5a6a66e1efd7e375ab992b'
CONTEXT_JETS_SHA = '3efd07691647eb01e15c2e57ff3afe04d3bd250b0acceefe7be43628abd2d1d7'
RUN_ID = 'c21n_offgrid4_opposing_z20_z4_20261021'
CASES = [dict(case_id=key, S0=0., Pm0=value, Pr0=-value) for key, value in
         [('opp_mn175_rp175', -1.75e-4), ('opp_mn075_rp075', -7.5e-5),
          ('opp_mp075_rn075', 7.5e-5), ('opp_mp175_rn175', 1.75e-4)]]
SECTORS = ('m', 'gamma', 'nu', 'r', 'tot')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def load_alias(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def same_bytes(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    return a.shape == b.shape and a.tobytes() == b.tobytes()


def number(value):
    value = float(value)
    return value if math.isfinite(value) else None


def write_json(path, value):
    with Path(path).open('x') as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')


def write_csv(path, rows):
    with Path(path).open('x', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class Bindings:
    def __init__(self):
        self.values = {}

    def add(self, path, expected=None, role='input'):
        path = Path(path).resolve()
        digest = sha(path)
        if expected is not None and digest != expected:
            raise ValueError('INPUT_SOURCE_HASH_MISMATCH:' + str(path))
        self.values[str(path)] = {'path': str(path), 'sha256': digest,
                                  'bytes': path.stat().st_size, 'role': role}
        return digest

    def verify_unchanged(self):
        for value in self.values.values():
            path = Path(value['path'])
            if sha(path) != value['sha256'] or path.stat().st_size != value['bytes']:
                raise ValueError('INPUT_CHANGED_DURING_READONLY_ANALYSIS:' + str(path))


def load_new_run(run, repo, bindings, expected_identity):
    n = repo / 'research/cr_c21n_mass_shell_cache_20261021'
    l = repo / 'research/cr_c21l_rei_pilot_20261021'
    manifest_path = run / 'MANIFEST.json'
    bindings.add(manifest_path, role='run_manifest')
    envelope = json.loads(manifest_path.read_text())
    identity, manifest = envelope['identity'], envelope['manifest']
    if identity != expected_identity or canonical_sha(manifest) != identity:
        raise ValueError('EXPECTED_RUN_CANONICAL_IDENTITY_MISMATCH')
    expected_grid = {'schema': 'C21N_GRID_V1', 'run_id': RUN_ID, 'cases': CASES}
    if (manifest.get('schema') != 'C21N_INDEPENDENT_STRESS_RUN_V1' or
            manifest.get('grid') != expected_grid or
            manifest.get('grid_file_sha256') != EXPECTED_GRID_SHA or
            manifest.get('operational_test_double') is not False or
            manifest.get('execution_site') != 'sandbox'):
        raise ValueError('NOT_THE_FOUR_PINNED_REAL_SANDBOX_CASES')
    source = manifest['source']
    if source['source_commit'] != SOURCE_COMMIT or not source['optimized_exact_reuse_moments']:
        raise ValueError('ORIGINAL_PHYSICS_OR_PREPARED_EXECUTION_CHANGED')
    settings = {'n': 101, 'rtol': 3e-11, 'atol': 3e-13, 'ellmax': 8,
                'mass_fraction': .1, 'mass_over_Tref': 30., 'radial_cells': 24,
                'angular_cells': 12, 'subcell_gauss_order': 3, 'donor': None}
    if any(source['settings'].get(k) != v for k, v in settings.items()):
        raise ValueError('SOURCE_DISCRETIZATION_OR_SOLVER_CONTRACT_CHANGED')
    for name, digest in manifest['code_sha256'].items():
        path = (n / name).resolve()
        if not path.is_relative_to(n):
            raise ValueError('CODE_BINDING_OUTSIDE_FROZEN_C21N')
        bindings.add(path, digest, 'frozen_execution_code')
    for name, key in [('builder.py', 'builder_sha256'),
                      ('prepared_momentum.py', 'prepared_momentum_sha256')]:
        bindings.add(n / name, source[key], 'frozen_source')
    for name, key in [('adapter.py', 'parent_adapter_sha256'),
                      ('SOURCE_MANIFEST.json', 'source_manifest_sha256')]:
        bindings.add(l / name, source[key], 'original_source')
    for item in source['source_files']:
        bindings.add(l / 'vendor/rei' / item['path'], item['sha256'], 'vendor_source')
    bindings.add(n / 'prepared_offgrid4/grid_offgrid4.json', EXPECTED_GRID_SHA, 'prepared_grid')
    bindings.add(n / 'prepared_offgrid4/INITIAL_CONDITION_CERTIFICATES.json', role='initial_certificate')
    if {p.name for p in (run / 'cases').iterdir() if p.is_dir()} != {c['case_id'] for c in CASES}:
        raise ValueError('UNEXPECTED_RUN_CASE_DIRECTORY_SET')
    loaded = []
    for case in CASES:
        folder = run / 'cases' / case['case_id']
        receipt = json.loads((folder / 'RESULT.json').read_text())
        seal = json.loads((folder / 'COMPLETE.json').read_text())
        reservation = json.loads((folder / 'RESERVATION.json').read_text())
        started = json.loads((folder / 'STARTED.json').read_text())
        if (receipt.get('identity') != identity or receipt.get('case') != case or
                receipt.get('status') != 'COMPLETE' or receipt.get('operational_test_double') is not False or
                seal.get('identity') != identity or seal.get('case_id') != case['case_id'] or
                reservation.get('identity') != identity or reservation.get('case') != case or
                started.get('identity') != identity or started.get('case') != case or
                receipt.get('history_sha256') != seal['history_sha256']):
            raise ValueError('CASE_IDENTITY_OR_REAL_EXECUTION_SEAL_MISMATCH:' + case['case_id'])
        bindings.add(folder / 'RESULT.json', seal['result_sha256'], 'case_receipt')
        bindings.add(folder / 'history.npz', seal['history_sha256'], 'case_raw')
        for name in ('COMPLETE.json', 'RESERVATION.json', 'STARTED.json'):
            bindings.add(folder / name, role='case_lifecycle')
        with np.load(folder / 'history.npz', allow_pickle=False) as archive:
            history = {key: archive[key] for key in archive.files}
        loaded.append((case, receipt, history))
    # Include actual run lifecycle/resource receipts without interpreting old plan as execution.
    for pattern in ('RETURN_*.json', 'SUMMARY_*.json', 'RESOURCES_*.json',
                    'STORAGE_*.json', 'EVENTS_*.jsonl'):
        for path in sorted(run.glob(pattern)):
            bindings.add(path, role='actual_run_lifecycle')
    return manifest, loaded


def read_context(repo, path, bindings):
    bindings.add(path, CONTEXT125_SHA, 'existing125_context_only')
    with np.load(path, allow_pickle=False) as archive:
        keys = ('requested_signed_full', 'campaign_case_key', 'eta', 'S_signed_F',
                'P_m_signed_F', 'P_r_signed_F', 'P_tot_signed_F',
                'Sigma_F', 'Pi_m_F', 'Pi_r_F', 'Pi_tot_F')
        data = {key: archive[key] for key in keys}
    selected = [i for i, x in enumerate(data['requested_signed_full'])
                if x[0] == 0 and x[1] != 0 and x[1] == -x[2]]
    if len(selected) != 4 or [float(data['requested_signed_full'][i, 1]) for i in selected] != [-.0002, -.0001, .0001, .0002]:
        raise ValueError('EXPECTED_EXISTING_FOUR_OPPOSING_CONTEXT_CASES')
    jet_dir = repo / 'research/cr_c21n_mass_shell_cache_20261021/analysis_mass_shell125_v2'
    seal_path = jet_dir / 'OUTPUT_MANIFEST.json'
    bindings.add(seal_path, role='existing_jet_output_manifest')
    seal = json.loads(seal_path.read_text())
    jet_item = next(x for x in seal['files'] if x['path'] == 'zero_shear_jets_25.csv')
    if jet_item['sha256'] != CONTEXT_JETS_SHA:
        raise ValueError('EXISTING_JET_CONTEXT_SEAL_CHANGED')
    jet_path = jet_dir / jet_item['path']
    bindings.add(jet_path, jet_item['sha256'], 'existing_jet_csv_readonly')
    with jet_path.open() as handle:
        jet_rows = {row['case_key']: row for row in csv.DictReader(handle)}
    out = {key: value[selected] for key, value in data.items()}
    out['jets'] = [{name: float(jet_rows[str(key)][name]) for name in
                   ('actual_Sprime0', 'actual_S_eta2_coefficient',
                    'ideal_exact_cancellation_S_eta2_coefficient')}
                  for key in out['campaign_case_key']]
    return out


def original_from_recorded(baseline, template, mapping):
    original = copy.copy(template)
    original.momentum = baseline.parent.CanonicalMomentumFV(
        30., float(mapping['A_m']), 24, 12, gauss_order=3)
    original.Sigma_ref = float(mapping['source_Sigma_ref_half'])
    original.orientation = int(mapping['source_orientation'])
    original.k_gamma, original.k_nu = float(mapping['k_gamma']), float(mapping['k_nu'])
    original._nfev = 0
    return original


def compare_fields(a, b, history, sample):
    if set(a) != set(b):
        raise ValueError('CACHED_UNCACHED_FIELD_KEYSET')
    fields, raw_fields, raw_bytes = 0, 0, True
    for key in sorted(a):
        if isinstance(a[key], (float, int, np.floating, np.integer, np.ndarray)):
            aa, bb = np.asarray(a[key], dtype=np.float64), np.asarray(b[key], dtype=np.float64)
            if not same_bytes(aa, bb):
                raise ArithmeticError('CACHED_UNCACHED_FIELD_FP64_BYTES:' + key)
            fields += aa.size
            if key in history:
                actual = np.asarray(history[key][sample], dtype=np.float64)
                if not np.array_equal(aa, actual):
                    raise ArithmeticError('ORIGINAL_SOURCE_VS_SAVED_FIELD_NUMERIC_MISMATCH:' + key)
                raw_fields += aa.size
                raw_bytes = raw_bytes and same_bytes(aa, actual)
        elif a[key] != b[key]:
            raise ValueError('CACHED_UNCACHED_NONNUMERIC_FIELD:' + key)
    return fields, raw_fields, raw_bytes


def plot_all(out, arrays, rows, jets, context):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10, 'axes.titlesize': 10, 'pdf.fonttype': 42})
    colors = ['#2166ac', '#67a9cf', '#ef8a62', '#b2182b']
    labels = [rf'$P_{{m,0}}={r["Pm0"] / 1e-4:+g}\times10^{{-4}}$' for r in rows]
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.5), constrained_layout=True,
                             sharex=True, sharey=True)
    for i, ax in enumerate(axes.flat):
        for key, label, color, style in (
            ('S_signed_F', r'$S$', '#87652a', ':'),
            ('P_m_signed_F', r'$P_m$', '#a23b8c', '-'),
            ('P_r_signed_F', r'$P_r=P_\gamma+P_\nu$', '#147ba3', '-'),
            ('P_tot_signed_F', r'$P_{\rm tot}$', '#222222', '--')):
            ax.plot(arrays['eta'][i], arrays[key][i] * 1e4, color=color, ls=style,
                    label=label, lw=1.5)
        ax.axhline(0, color='.6', lw=.5)
        ax.set(title=labels[i] + r', $P_{r,0}=-P_{m,0}$', xlabel=r'$\eta=\ln(a/a_0)$',
               ylabel=r'Signed full-Frobenius coordinates ($10^{-4}$)')
        ax.grid(alpha=.2)
        ax.legend(fontsize=8.5, loc='best', ncol=2)
    fig.suptitle('Four new off-grid trajectories: zero initial shear, opposing stresses\n'
                 'Collisionless LRS, z=20 to 4; lines connect 101 stored samples', fontsize=12)
    save_figure(fig, out, 'signed_components_offgrid4')
    plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(13.4, 7.6), constrained_layout=True)
    panels = [('Sigma_F', r'$\Sigma=|S|$'), ('Pi_m_F', r'$\Pi_m=|P_m|$'),
              ('Pi_r_F', r'$\Pi_r=|P_r|$'), ('Pi_tot_F', r'$\Pi_{\rm tot}=|P_m+P_r|$'),
              ('cancellation', r'$C=1-|P_m+P_r|/(|P_m|+|P_r|)$')]
    for ax, (key, label) in zip(axes.flat, panels):
        for i, color in enumerate(colors):
            ax.plot(arrays['eta'][i], arrays[key][i], color=color, label=labels[i], lw=1.5)
        ax.set(xlabel=r'$\eta$', ylabel=label)
        ax.set_ylim(bottom=0)
        if key == 'cancellation':
            ax.set_ylim(-.015, 1.015)
        ax.grid(alpha=.2)
    axes[0, 0].legend(fontsize=8, loc='best')
    ax = axes[1, 2]
    for key, color, marker, label in (
        ('S_signed_F', '#87652a', 'o', r'$S_f$'),
        ('P_m_signed_F', '#a23b8c', 's', r'$P_{m,f}$'),
        ('P_r_signed_F', '#147ba3', '^', r'$P_{r,f}$'),
        ('P_tot_signed_F', '#222222', 'D', r'$P_{\mathrm{tot},f}$')):
        ax.scatter(np.array([r['Pm0'] for r in rows]) * 1e4, arrays[key][:, -1] * 1e5,
                   color=color, marker=marker, s=32, label=label)
        ax.scatter(context['requested_signed_full'][:, 1] * 1e4, context[key][:, -1] * 1e5,
                   edgecolors=color, facecolors='none', marker=marker, s=44, linewidths=1.)
    ax.axhline(0, color='.6', lw=.5)
    ax.set(xlabel=r'Initial $P_{m,0}$ ($10^{-4}$)', ylabel=r'Signed endpoint ($10^{-5}$)',
           title='Filled: new 4; hollow: existing 4')
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=.2)
    fig.suptitle('New four: nonnegative norms and cancellation; endpoint context uses exact sampled inputs\n'
                 'Radiation = photon + massless neutrino; context is read-only, no interpolated parameter grid',
                 fontsize=11)
    save_figure(fig, out, 'norms_cancellation_offgrid4')
    plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(14.5, 8.1), constrained_layout=True, sharex=True, sharey='col')
    for row_index, (data, local_jets, prefix) in enumerate(
            ((arrays, jets, 'New off-grid 4'), (context, context['jets'], 'Existing opposing 4'))):
        for i, color in enumerate(colors):
            eta, saved = data['eta'][i, :8], data['S_signed_F'][i, :8]
            jet = local_jets[i]
            approx = jet['actual_Sprime0'] * eta + jet['actual_S_eta2_coefficient'] * eta**2
            pm = rows[i]['Pm0'] if row_index == 0 else context['requested_signed_full'][i, 1]
            label = rf'$P_{{m,0}}={pm / 1e-4:+g}\times10^{{-4}}$'
            axes[row_index, 0].plot(eta, saved * 1e6, 'o', color=color, ms=4, label=label)
            axes[row_index, 0].plot(eta, approx * 1e6, '--', color=color, lw=1.)
            axes[row_index, 1].plot(eta[1:], (saved[1:] - approx[1:]) * 1e9, 'o-', color=color, ms=3.5)
            axes[row_index, 2].plot(eta[1:], saved[1:] / eta[1:]**2 * 1e5, 'o-', color=color, ms=3.5)
            axes[row_index, 2].axhline(jet['ideal_exact_cancellation_S_eta2_coefficient'] * 1e5,
                                       color=color, ls='--', lw=1.)
        axes[row_index, 0].set_ylabel(prefix + '\n' + r'Signed $S$ ($10^{-6}$)')
        axes[row_index, 0].legend(fontsize=7.8, loc='best', ncol=2)
        axes[row_index, 1].set_ylabel(r'$S_{\rm saved}-S_{\rm jet}$ ($10^{-9}$)')
        axes[row_index, 2].set_ylabel(r'$S_{\rm saved}/\eta^2$ ($10^{-5}$)')
        for ax in axes[row_index]:
            ax.axhline(0, color='.6', lw=.5)
            ax.set_xlabel(r'$\eta=\ln(a/a_0)$')
            ax.grid(alpha=.2)
    for ax, title in zip(axes[0], ('Saved samples and actual second-order jet',
                                  'Measured local residual; no error bound',
                                  'Ideal quadratic coefficient; zero excluded')):
        ax.set_title(title)
    fig.suptitle('Initial cancellation release: new 4 versus existing 4 (separate rows, shared column scales)\n'
                 'Circles: stored trajectories; dashed left: actual jet; dashed right: ideal initial coefficient',
                 fontsize=11)
    save_figure(fig, out, 'local_jet_new_existing')
    plt.close(fig)


def save_figure(fig, out, stem):
    fig.savefig(out / (stem + '.png'), dpi=180)
    fig.savefig(out / (stem + '.pdf'), metadata={'CreationDate': None, 'ModDate': None})


def analyze(args):
    run, out, repo = args.input.resolve(), args.output.resolve(), args.repo.resolve()
    if out.exists():
        raise FileExistsError('CREATE_ONLY_ANALYSIS_OUTPUT:' + str(out))
    research = repo / 'research'
    n, m, l = [research / name for name in ('cr_c21n_mass_shell_cache_20261021',
               'cr_c21m_independent_stress_20261021', 'cr_c21l_rei_pilot_20261021')]
    bindings = Bindings()
    bindings.add(Path(__file__), role='new_analysis_code')
    manifest, loaded = load_new_run(run, repo, bindings, args.expected_identity)
    # Explicit aliases keep the frozen M and N builders distinct.
    sys.path.insert(0, str(n))
    current = load_alias('frozen_c21n_builder_offgrid_analysis', n / 'builder.py')
    original = load_alias('original_c21m_builder_offgrid_analysis', m / 'builder.py')
    decomp = load_alias('original_c21l_decomposition_offgrid_analysis',
                        l / 'component_split_20261021/analyze_components.py')
    previous = load_alias('original_c21m_physics_checks_offgrid_analysis', m / 'analyze_pilot.py')
    derivative = load_alias('frozen_c21n_derivative_offgrid_analysis', n / 'mass_shell_derivatives.py')
    for path in (m / 'builder.py', m / 'analyze_pilot.py',
                 l / 'component_split_20261021/analyze_components.py', n / 'mass_shell_derivatives.py'):
        bindings.add(path, role='reused_analysis_or_original_comparator')
    cached_builder = current.IndependentStressBuilder()
    baseline = original.IndependentStressBuilder(optimized=False)
    if cached_builder.identity() != manifest['source']:
        raise ValueError('CURRENT_FROZEN_C21N_IDENTITY_DIFFERS_FROM_EXECUTED_SOURCE')
    context = read_context(repo, args.context.resolve(), bindings)
    decomposed, rows, jets, sample_rows, local_rows = [], [], [], [], []
    counts = dict(cases=4, saved_states=0, cached_uncached_field_FP64_values=0,
                  cached_uncached_RHS_FP64_values=0, original_vs_saved_field_values=0,
                  sampled_angular_values=0)
    raw_fields_byte_equal = True
    conservation = {key: np.empty((4, 101)) for key in
        ('massive_energy_identity', 'radiation_energy_identity', 'signed_shear_identity',
         'source_forcing_minus_SI_sum')}
    original_rhs = np.empty((4, 40, 101))
    physics, held_objects, initial_bytes = [], [], []
    mu, _ = np.polynomial.legendre.leggauss(64)
    angular_basis = np.polynomial.legendre.legvander(mu, 8) * (2 * np.arange(9) + 1)
    angular_min = {key: math.inf for key in ('E_gamma', 'N_gamma', 'E_nu', 'N_nu')}
    for i, (case, receipt, history) in enumerate(loaded):
        data = decomp.components(history)
        data.update({key: history[key] for key in ('Y', 'E_gamma', 'N_gamma', 'E_nu', 'N_nu')})
        physics.append({'case_id': case['case_id'], **previous.physics_checks(history, data, case)})
        cached, reconstructed_mapping = cached_builder.build(case['S0'], case['Pm0'], case['Pr0'])
        if reconstructed_mapping != receipt['mapping']:
            raise ValueError('CACHED_INITIAL_MAPPING_VALUES_DIFFER:' + case['case_id'])
        uncached = original_from_recorded(original, baseline.template, receipt['mapping'])
        if (not same_bytes(cached.initial_state(), history['Y'][:, 0]) or
                not same_bytes(uncached.initial_state(), history['Y'][:, 0])):
            raise ValueError('NEW_INITIAL_STATE_BYTES_NOT_REPRODUCED:' + case['case_id'])
        initial_bytes.append(hashlib.sha256(history['Y'][:, 0].tobytes()).hexdigest())
        state_bytes = history['Y'].tobytes()
        held_objects.append((cached, {key: getattr(cached.momentum, key).tobytes()
                                      for key in ('_q', '_mu2', '_numbers', '_cell_numbers')}))
        for key in angular_min:
            reconstructed = history[key] @ angular_basis.T
            angular_min[key] = min(angular_min[key], float(np.min(reconstructed)))
            counts['sampled_angular_values'] += reconstructed.size
        for j, eta in enumerate(history['eta']):
            state = history['Y'][:, j]
            cf, of = cached.fields(float(eta), state), uncached.fields(float(eta), state)
            nf, nr, rb = compare_fields(cf, of, history, j)
            counts['cached_uncached_field_FP64_values'] += nf
            counts['original_vs_saved_field_values'] += nr
            raw_fields_byte_equal = raw_fields_byte_equal and rb
            cr = copy.copy(cached).rhs(float(eta), state)
            diagnostic = derivative.source_derivatives(uncached, float(eta), state)
            ur = diagnostic['source_rhs']
            if not same_bytes(cr, ur):
                raise ArithmeticError('CACHED_UNCACHED_RHS_FP64_BYTES:' + case['case_id'])
            counts['cached_uncached_RHS_FP64_values'] += ur.size
            counts['saved_states'] += 1
            original_rhs[i, :, j] = ur
            conservation['massive_energy_identity'][i, j] = diagnostic['packet']['energy_conservation_residual']
            conservation['radiation_energy_identity'][i, j] = diagnostic['radiation_energy_conservation_residual']
            conservation['signed_shear_identity'][i, j] = diagnostic['signed_S_identity_residual']
            conservation['source_forcing_minus_SI_sum'][i, j] = diagnostic['source_forcing_minus_SI_component_sum']
            sample_rows.append({'case_id': case['case_id'], 'sample': j, 'eta': float(eta),
                                **{key: value[i, j] for key, value in conservation.items()}})
        if history['Y'].tobytes() != state_bytes:
            raise ValueError('SAVED_STATE_MUTATED_IN_MEMORY')
        jet = derivative.initial_cancellation_jet(uncached, history['Y'][:, 0])
        jets.append(jet)
        for j in range(8):
            eta = float(data['eta'][j])
            actual = float(data['S_signed_F'][j])
            approx = jet['actual_Sprime0'] * eta + jet['actual_S_eta2_coefficient'] * eta**2
            local_rows.append({'case_id': case['case_id'], 'Pm0': case['Pm0'], 'Pr0': case['Pr0'],
                'sample': j, 'eta': eta, 'stored_signed_S': actual, 'actual_second_order_jet': approx,
                'stored_minus_jet': actual - approx,
                'relative_residual_to_saved': None if actual == 0 else (actual - approx) / actual,
                'stored_S_over_eta2': None if eta == 0 else actual / eta**2,
                'ideal_eta2_coefficient': jet['ideal_exact_cancellation_S_eta2_coefficient']})
        row = {**case, 'A_m': receipt['mapping']['A_m'], 'k_gamma': receipt['mapping']['k_gamma'],
               'k_nu': receipt['mapping']['k_nu'], 'solver_wall_s_recorded': receipt['solver_wall_s'],
               'nfev_recorded': receipt['nfev']}
        for key in ('S_signed_F', 'Sigma_F', 'P_m_signed_F', 'Pi_m_F', 'P_gamma_signed_F',
                    'Pi_gamma_F', 'P_nu_signed_F', 'Pi_nu_F', 'P_r_signed_F', 'Pi_r_F',
                    'P_tot_signed_F', 'Pi_tot_F', 'cancellation'):
            row[key + '_initial'], row[key + '_end'] = number(data[key][0]), number(data[key][-1])
        row['cancellation_defined_end'] = bool(data['cancellation_defined'][-1])
        rows.append(row)
        decomposed.append(data)
    for obj, before in held_objects:
        if any(getattr(obj.momentum, key).tobytes() != value for key, value in before.items()):
            raise ValueError('PREPARED_CASE_ARRAY_CHANGED_AFTER_OTHER_A_BUILDS')
    maxima = {key: float(np.max(abs(value))) for key, value in conservation.items()}
    if (maxima['massive_energy_identity'] > 2e-13 or
            maxima['radiation_energy_identity'] > 2e-10 or
            maxima['signed_shear_identity'] > 2e-15 or min(angular_min.values()) < 0):
        raise ArithmeticError('NEW_SAVED_STATE_SCOPED_PHYSICS_CHECK_FAILED')
    for jet in jets:
        if max(abs(jet['actual_offset_Pprime_formula_residual']),
               abs(jet['actual_offset_Ssecond_formula_residual'])) > 2e-14:
            raise ArithmeticError('ACTUAL_OFFSET_JET_IDENTITY_FAILED')
    arrays = {key: np.stack([d[key] for d in decomposed]) for key in decomposed[0]}
    arrays.update(case_id=np.array([x['case_id'] for x in CASES]),
                  requested_signed_full=np.array([[c[k] for k in ('S0', 'Pm0', 'Pr0')] for c in CASES]),
                  uncached_RHS_at_saved_states=original_rhs, **conservation)
    bindings.verify_unchanged()
    out.mkdir(parents=True, exist_ok=False)
    decomp.deterministic_npz(out / 'components_offgrid4.npz', arrays)
    write_csv(out / 'endpoints_offgrid4.csv', rows)
    write_csv(out / 'initial_jets_offgrid4.csv', [{'case_id': c['case_id'], **j} for c, j in zip(CASES, jets)])
    write_csv(out / 'conservation_404.csv', sample_rows)
    write_csv(out / 'early_jet_residuals.csv', local_rows)
    context_rows = [{'case_key': str(context['campaign_case_key'][i]),
                     'Pm0': float(context['requested_signed_full'][i, 1]),
                     'Pr0': float(context['requested_signed_full'][i, 2]),
                     **{key + '_end': float(context[key][i, -1]) for key in
                        ('S_signed_F', 'Sigma_F', 'P_m_signed_F', 'Pi_m_F',
                         'P_r_signed_F', 'Pi_r_F', 'P_tot_signed_F', 'Pi_tot_F')}} for i in range(4)]
    write_csv(out / 'existing4_context_endpoints.csv', context_rows)
    plot_all(out, arrays, rows, jets, context)
    bindings.verify_unchanged()
    first = [x for x in local_rows if x['sample'] == 1]
    last = [x for x in local_rows if x['sample'] == 7]
    summary = {'schema': 'C21N_OFFGRID4_RETURN_ANALYSIS_V1', 'status': 'PASS_SCOPED',
        'source_commit': SOURCE_COMMIT, 'execution_content_commit': EXECUTION_CONTENT,
        'run_identity': args.expected_identity, 'run_id': RUN_ID,
        'science_execution_count_in_input': 4, 'new_ODE_calls_by_analyzer': 0,
        'existing_context_trajectories_reintegrated': 0, 'execution_site': manifest['execution_site'],
        'recorded_software': manifest['software'], 'counts': counts,
        'initial_state_FP64_bytes': 'IDENTICAL: stored, prepared builder, original recorded-parameter reconstruction',
        'initial_mapping_values': 'DICTIONARY_EQUAL_TO_EXECUTION_RECEIPT',
        'cached_vs_uncached_fields_and_RHS': 'FP64_BYTES_IDENTICAL_ON_ALL_404_SAVED_STATES',
        'original_vs_saved_fields': 'EXACT_NUMERIC_EQUALITY',
        'original_vs_saved_field_FP64_bytes_also_equal': raw_fields_byte_equal,
        'paired_original_full_trajectory_replay': 'NOT_RUN',
        'continuum_or_every_adaptive_step_equivalence': 'NOT_ESTABLISHED_BY_THIS_STATIC_CHECK',
        'initial_state_sha256': dict(zip([c['case_id'] for c in CASES], initial_bytes)),
        'maximum_absolute_identity_residuals': maxima,
        'radiation_discrete_L8_reconstruction': {'nodes': 64, 'minimum': angular_min,
            'scope': 'Original angular quadrature nodes only; no continuous positivity theorem'},
        'endpoint_maxima_new4_only': {k: max(r[k + '_end'] for r in rows)
                                     for k in ('Sigma_F', 'Pi_m_F', 'Pi_r_F', 'Pi_tot_F')},
        'early_comparison': {'samples_per_case': 8, 'first_positive_eta': first[0]['eta'],
            'last_eta': last[0]['eta'],
            'first_positive_max_absolute_relative_residual': max(abs(r['relative_residual_to_saved']) for r in first),
            'last_max_absolute_relative_residual': max(abs(r['relative_residual_to_saved']) for r in last),
            'last_max_absolute_residual': max(abs(r['stored_minus_jet']) for r in last),
            'interpretation': 'Measured residual against stored numerical samples, not an error bound'},
        'species': loaded[0][1]['mapping']['species'],
        'conventions': {'signed_S': 'sqrt(6)*s/H_t',
            'signed_P_X': 'sqrt(6)*(8*pi*G/c^2)*pi_s_X/H_t^2; pi_s=Delta_p/3',
            'norms': 'Sigma=abs(S), Pi_X=abs(P_X); full Frobenius, sqrt(2)*half',
            'radiation': 'pi_gamma+pi_nu before norm', 'total': 'pi_m+pi_r before norm',
            'SI': 'H_t in s^-1; kappa_E=8*pi*G/c^4 with H_geom=H_t/c is equivalent',
            'FP_offsets': 'Preserved; no stress clipping or zero substitution'},
        'readonly_inputs_verified_unchanged': True, 'prepared_case_arrays_preserved_across_A_builds': True,
        'new4_plus_existing125': '129 irregularly sampled trajectories; not a new Cartesian sweep',
        'performance_benchmark': False, 'speedup': None, 'memory_improvement': None,
        'third_order_coefficient': None, 'finite_window_error_bound': None, 'global_error_bound': None,
        'PNG_visual_review': 'PENDING_INDEPENDENT_REVIEW', 'PDF_separate_raster_review': 'NOT_RUN_BY_ANALYZER'}
    write_json(out / 'SUMMARY.json', summary)
    write_json(out / 'PHYSICS_CHECKS.json', {'cases': physics, 'counts': counts,
        'derivative_maxima': maxima, 'angular_minima': angular_min, 'global_error_bound': None})
    write_json(out / 'INPUT_BINDINGS.json', {'verified_unchanged_after_analysis': True,
                                           'files': list(bindings.values.values())})
    write_json(out / 'OUTPUT_MANIFEST.json', {'analyzer_sha256': sha(__file__), 'files': [
        {'path': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)}
        for p in sorted(out.iterdir()) if p.is_file()]})
    print(json.dumps({'status': summary['status'], 'new_ODE_calls_by_analyzer': 0,
                      'counts': counts, 'output': str(out)}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repo', type=Path, default=DEFAULT_REPO)
    parser.add_argument('--context', type=Path,
        default=DEFAULT_REPO / 'research/cr_c21m_independent_stress_20261021/analysis_campaign125_20261021/components_campaign.npz')
    parser.add_argument('--expected-identity', default=EXPECTED_IDENTITY)
    args = parser.parse_args()
    old_mpl = os.environ.get('MPLCONFIGDIR')
    with tempfile.TemporaryDirectory(prefix='c21n-offgrid-analysis-mpl-') as temp:
        os.environ['MPLCONFIGDIR'] = temp
        try:
            analyze(args)
        finally:
            if old_mpl is None:
                os.environ.pop('MPLCONFIGDIR', None)
            else:
                os.environ['MPLCONFIGDIR'] = old_mpl


if __name__ == '__main__':
    main()
