"""Create-only pressure-derivative diagnostics on the accepted 125 histories.

No integrator is called. Source parameters are read from original receipts,
not reconstructed by inverse target mapping. The C21M baseline is imported
under an explicit alias, so a newer C21N builder cannot replace its source.
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
import tempfile

for _key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_key] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ.setdefault('MPLBACKEND', 'Agg')

import numpy as np

from mass_shell_derivatives import packet_derivatives, source_derivatives, initial_cancellation_jet

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
M = RESEARCH / 'cr_c21m_independent_stress_20261021'
L = RESEARCH / 'cr_c21l_rei_pilot_20261021'
SOURCE_COMMIT = '3b85dedce84d37b3e165da00685a8a984950aafe'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def alias_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    with Path(path).open('x') as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')


def write_csv(path, rows):
    with Path(path).open('x', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def relative(path):
    return str(Path(path).resolve().relative_to(RESEARCH.parent))


def byte_equal(a, b):
    return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()


def load_inputs(campaign):
    loader = alias_module('c21m_readonly_input_loader_for_c21n', M / 'analyze_pilot.py')
    entries, bindings = {}, []
    for run in (M / 'runs/pilot26', M / 'runs/ncp_refinement98_20261021'):
        sealed = json.loads((run / 'MANIFEST.json').read_text())
        mp, manifest, loaded = loader.load_new(run, sealed['manifest']['grid'])
        identity = manifest['identity']
        bindings.append({'kind': 'RUN_MANIFEST', 'path': relative(mp),
                         'sha256': sha(mp), 'identity': identity})
        for case, raw, receipt, data, origin in loaded:
            entries[identity, case['case_id']] = (case, raw, receipt, data, origin)
    reference, entry = loader.load_reference(M / 'REFERENCE_REUSE.json', L)
    entries[reference['source_input_identity'], reference['case_id']] = entry
    bindings.append({'kind': 'REFERENCE_REUSE', 'path': relative(M / 'REFERENCE_REUSE.json'),
                     'sha256': sha(M / 'REFERENCE_REUSE.json')})
    campaign_path = campaign / 'components_campaign.npz'
    bindings.append({'kind': 'COMBINED_ANALYSIS', 'path': relative(campaign_path),
                     'sha256': sha(campaign_path)})
    with np.load(campaign_path, allow_pickle=False) as archive:
        arrays = {key: archive[key] for key in archive.files}
    if arrays['Y'].shape != (125, 40, 101) or arrays['requested_signed_full'].shape != (125, 3):
        raise ValueError('ACCEPTED_125_FULL_STATE_CAMPAIGN_REQUIRED')
    if len(entries) != 125 or len(set(map(str, arrays['campaign_case_key']))) != 125:
        raise ValueError('NONUNIQUE_OR_INCOMPLETE_CAMPAIGN')
    ordered = []
    for i in range(125):
        key = str(arrays['source_identity'][i]), str(arrays['case_id'][i])
        case, raw, receipt, data, origin = entries.pop(key)
        with np.load(raw, allow_pickle=False) as history:
            for name in ('eta', 'Y'):
                if not byte_equal(history[name], arrays[name][i]):
                    raise ValueError('COMBINED_RAW_BYTES_DIFFER:' + str(key) + ':' + name)
        if (origin != str(arrays['origin'][i]) or
                [case[k] for k in ('S0', 'Pm0', 'Pr0')] != arrays['requested_signed_full'][i].tolist()):
            raise ValueError('CAMPAIGN_COORDINATE_OR_ORIGIN_MISMATCH')
        ordered.append((case, data, origin))
        bindings.append({'kind': 'RAW_AND_RECEIPT', 'case_key': str(arrays['campaign_case_key'][i]),
                         'source_identity': key[0], 'raw_path': relative(raw), 'raw_sha256': sha(raw),
                         'receipt_path': relative(receipt), 'receipt_sha256': sha(receipt)})
    if entries:
        raise ValueError('UNUSED_ACCEPTED_RAW')
    return arrays, ordered, reference, bindings


def reconstruct(baseline, template, receipt, origin, reference):
    obj = copy.copy(template)
    mapping = reference['original_mapping'] if origin == 'REUSED_C21L_TRAJECTORY' else receipt['mapping']
    amplitude = 0. if origin == 'REUSED_C21L_TRAJECTORY' else float(mapping['A_m'])
    obj.momentum = baseline.parent.CanonicalMomentumFV(30., amplitude, 24, 12, gauss_order=3)
    obj.k_gamma, obj.k_nu = float(mapping['k_gamma']), float(mapping['k_nu'])
    if origin == 'REUSED_C21L_TRAJECTORY':
        obj.Sigma_ref, obj.orientation = float(mapping['source_Sigma_ref']), int(mapping['orientation'])
    else:
        obj.Sigma_ref = float(mapping['source_Sigma_ref_half'])
        obj.orientation = int(mapping['source_orientation'])
    obj._nfev = 0
    return obj, amplitude


def make_plots(out, arrays, selected, jets, early):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10, 'axes.titlesize': 11, 'pdf.fonttype': 42})
    colors = ['#2166ac', '#67a9cf', '#ef8a62', '#b2182b']
    fig, axes = plt.subplots(1, 3, figsize=(15.4, 4.8), constrained_layout=True)
    for color, index in zip(colors, selected):
        eta = arrays['eta'][index, :early]
        saved = arrays['S_signed_F'][index, :early]
        jet = jets[index]
        local = jet['actual_Sprime0'] * eta + jet['actual_S_eta2_coefficient'] * eta**2
        pm = arrays['requested_signed_full'][index, 1]
        label = rf'$P_{{m,0}}={pm / 1e-4:+.0f}\times10^{{-4}}$'
        axes[0].plot(eta, saved * 1e6, 'o', color=color, ms=4, label=label)
        axes[0].plot(eta, local * 1e6, '--', color=color, lw=1.3)
        axes[1].plot(eta[1:], (saved[1:] - local[1:]) * 1e9, 'o-', color=color, ms=4)
        # eta=0 is excluded mathematically; no floor or artificial replacement.
        axes[2].plot(eta[1:], saved[1:] / eta[1:]**2 * 1e5, 'o-', color=color, ms=4)
        axes[2].axhline(jet['ideal_exact_cancellation_S_eta2_coefficient'] * 1e5,
                        color=color, linestyle='--', linewidth=1.1)
    axes[0].set(title='Saved signed shear and actual local jet',
                xlabel=r'$\eta=\ln(a/a_0)$', ylabel=r'$S=\sqrt{6}s/H_t$ ($10^{-6}$)')
    axes[0].legend(fontsize=8.5, loc='best')
    axes[1].set(title='Measured residual at existing saved times',
                xlabel=r'$\eta$', ylabel=r'$S_{\rm saved}-[S_0^{\prime}\eta+\frac{1}{2} S_0^{\prime\prime}\eta^2]$ ($10^{-9}$)')
    axes[2].set(title='Local quadratic response; zero excluded',
                xlabel=r'$\eta>0$', ylabel=r'$S_{\rm saved}/\eta^2$ ($10^{-5}$)')
    for ax in axes:
        ax.axhline(0, color='0.6', linewidth=.5)
        ax.grid(alpha=.2)
    fig.suptitle('C21N: initial opposing matter/radiation stress, zero initial shear\n'
                 'Existing 4 of 125 trajectories; circles = saved data, dashes = local coefficients; no new ODE',
                 fontsize=12)
    fig.savefig(out / 'initial_cancellation_release.png', dpi=180)
    fig.savefig(out / 'initial_cancellation_release.pdf', metadata={'CreationDate': None, 'ModDate': None})
    plt.close(fig)


def run(campaign, out):
    if out.exists():
        raise FileExistsError('CREATE_ONLY_ANALYSIS_DIRECTORY:' + str(out))
    baseline = alias_module('c21m_original_builder_for_mass_shell_analysis', M / 'builder.py')
    builder = baseline.IndependentStressBuilder(optimized=False)
    source_identity = builder.identity()
    if source_identity['source_commit'] != SOURCE_COMMIT:
        raise ValueError('IMMUTABLE_PR147_SOURCE_REQUIRED')
    arrays, entries, reference, bindings = load_inputs(campaign)
    initial_rows, sampled_rows, jet_rows, jets = [], [], [], {}
    packet_conservation = np.empty((125, 101))
    packet_release = np.empty((125, 101))
    derivative_arrays = {name: np.empty(125) for name in
        ('S_prime0', 'Pm_prime0', 'Pr_prime0', 'Ptot_prime0', 'H_log_eta0', 'mass_release0')}
    maxima = dict(source_signed_fields_abs=0., packet_energy_conservation_abs=0.,
                  radiation_energy_conservation_abs=0., source_shear_identity_abs=0.,
                  source_forcing_vs_SI_abs=0., initial_Pprime_formula_abs=0.,
                  initial_Ssecond_formula_abs=0.)
    source_compare_count = 0
    for i, (case, receipt, origin) in enumerate(entries):
        obj, amplitude = reconstruct(baseline, builder.template, receipt, origin, reference)
        if not byte_equal(obj.initial_state(), arrays['Y'][i, :, 0]):
            raise ValueError('RECORDED_SOURCE_PARAMETERS_DO_NOT_RECREATE_Y0:' + case['case_id'])
        pre_arrays = {name: getattr(obj.momentum, name).tobytes()
                      for name in ('_q', '_mu2', '_numbers', '_cell_numbers')}
        initial = None
        for j, eta in enumerate(arrays['eta'][i]):
            b = float(arrays['Y'][i, 1, j])
            velocity = float(arrays['s'][i, j] / arrays['H'][i, j])
            packet = packet_derivatives(obj.momentum, eta, b, velocity)
            packet_conservation[i, j] = packet['energy_conservation_residual']
            packet_release[i, j] = packet['mass_release_pi_s_at_zero_shear']
            maxima['packet_energy_conservation_abs'] = max(maxima['packet_energy_conservation_abs'],
                abs(packet['energy_conservation_residual']))
            if j not in (0, 50, 100):
                continue
            d = source_derivatives(obj, eta, arrays['Y'][i, :, j])
            if j == 0:
                initial = d
            row = {'case_key': str(arrays['campaign_case_key'][i]), 'sample_index': j,
                   'eta': float(eta), 'b': b, 'b_eta': velocity,
                   'massive_energy_conservation_residual': packet['energy_conservation_residual'],
                   'radiation_energy_conservation_residual': d['radiation_energy_conservation_residual'],
                   'signed_S_identity_residual': d['signed_S_identity_residual'],
                   'source_forcing_minus_SI_sum': d['source_forcing_minus_SI_component_sum']}
            comparisons = [('signed_S', 'S_signed_F')]
            for dkey, akey in comparisons:
                delta = abs(d[dkey] - float(arrays[akey][i, j]))
                maxima['source_signed_fields_abs'] = max(maxima['source_signed_fields_abs'], delta)
                source_compare_count += 1
            for sector in ('m', 'gamma', 'nu', 'r', 'tot'):
                delta = abs(d['signed_P'][sector] - float(arrays['P_' + sector + '_signed_F'][i, j]))
                maxima['source_signed_fields_abs'] = max(maxima['source_signed_fields_abs'], delta)
                source_compare_count += 1
            maxima['radiation_energy_conservation_abs'] = max(maxima['radiation_energy_conservation_abs'],
                abs(d['radiation_energy_conservation_residual']))
            maxima['source_shear_identity_abs'] = max(maxima['source_shear_identity_abs'],
                abs(d['signed_S_identity_residual']))
            maxima['source_forcing_vs_SI_abs'] = max(maxima['source_forcing_vs_SI_abs'],
                abs(d['source_forcing_minus_SI_component_sum']))
            sampled_rows.append(row)
        if obj._nfev != 0 or any(getattr(obj.momentum, name).tobytes() != value
                                for name, value in pre_arrays.items()):
            raise ValueError('SOURCE_OR_MOMENTUM_MUTATION')
        row = {'case_key': str(arrays['campaign_case_key'][i]), 'case_id': case['case_id'],
               'source_run_id': str(arrays['source_run_id'][i]), 'source_identity': str(arrays['source_identity'][i]),
               'requested_S0': case['S0'], 'requested_Pm0': case['Pm0'], 'requested_Pr0': case['Pr0'],
               'A_m': amplitude, 'k_gamma': obj.k_gamma, 'k_nu': obj.k_nu,
               'actual_S0': initial['signed_S'], 'actual_Pm0': initial['signed_P']['m'],
               'actual_Pr0': initial['signed_P']['r'], 'actual_Ptot0': initial['signed_P']['tot'],
               'S_prime0': initial['signed_S_eta'], 'Pm_prime0': initial['signed_P_eta']['m'],
               'Pr_prime0': initial['signed_P_eta']['r'], 'Ptot_prime0': initial['signed_P_eta']['tot'],
               'H_log_eta0': initial['H_log_eta'], 'mass_release0': initial['mass_release_P_at_zero_shear'],
               'source_forcing_minus_SI_component_sum': initial['source_forcing_minus_SI_component_sum']}
        for name, target in derivative_arrays.items():
            target[i] = row[name]
        initial_rows.append(row)
        if float(arrays['Y'][i, 1, 0]) == 0. and float(arrays['Y'][i, 2, 0]) == 0.:
            jet = initial_cancellation_jet(obj, arrays['Y'][i, :, 0])
            jets[i] = jet
            jet_rows.append({'case_key': row['case_key'], 'case_id': row['case_id'],
                             'requested_Pm0': case['Pm0'], 'requested_Pr0': case['Pr0'], **jet})
            maxima['initial_Pprime_formula_abs'] = max(maxima['initial_Pprime_formula_abs'],
                abs(jet['actual_offset_Pprime_formula_residual']))
            maxima['initial_Ssecond_formula_abs'] = max(maxima['initial_Ssecond_formula_abs'],
                abs(jet['actual_offset_Ssecond_formula_residual']))
    if len(jets) != 25:
        raise ValueError('ZERO_SHEAR_SLICE_NOT_25')
    selected = [i for i in jets if arrays['requested_signed_full'][i, 1] != 0 and
                arrays['requested_signed_full'][i, 1] == -arrays['requested_signed_full'][i, 2]]
    if len(selected) != 4:
        raise ValueError('NONZERO_OPPOSING_SUBSET_NOT_4')
    center = [i for i in jets if np.all(arrays['requested_signed_full'][i] == 0.)]
    if len(center) != 1:
        raise ValueError('ISOTROPIC_REFERENCE_NOT_UNIQUE')
    early = 8  # eta=0 plus the first seven existing positive sampling times.
    compare_rows = []
    for i in selected:
        jet = jets[i]
        for j in range(early):
            eta = float(arrays['eta'][i, j])
            local = jet['actual_Sprime0'] * eta + jet['actual_S_eta2_coefficient'] * eta**2
            saved = float(arrays['S_signed_F'][i, j])
            residual = saved - local
            compare_rows.append({'case_key': str(arrays['campaign_case_key'][i]),
                'requested_Pm0': float(arrays['requested_signed_full'][i, 1]),
                'requested_Pr0': float(arrays['requested_signed_full'][i, 2]),
                'sample_index': j, 'eta': eta, 'z': float(1 / arrays['a'][i, j] - 1),
                'saved_signed_S': saved, 'actual_second_order_jet': local,
                'saved_minus_jet': residual,
                'relative_residual_to_saved': None if saved == 0 else residual / saved,
                'saved_S_over_eta2': None if eta == 0 else saved / eta**2,
                'ideal_eta2_coefficient': jet['ideal_exact_cancellation_S_eta2_coefficient']})
    # These gates assess algebra and source reconstruction, not ODE accuracy.
    if (maxima['source_signed_fields_abs'] > 2e-15 or
            maxima['packet_energy_conservation_abs'] > 2e-13 or
            maxima['radiation_energy_conservation_abs'] > 2e-10 or
            maxima['source_shear_identity_abs'] > 2e-15 or
            maxima['initial_Pprime_formula_abs'] > 2e-14 or
            maxima['initial_Ssecond_formula_abs'] > 2e-14):
        raise ArithmeticError('STATIC_DERIVATIVE_GATE_FAILED:' + repr(maxima))
    out.mkdir(parents=True, exist_ok=False)
    write_csv(out / 'initial_derivatives_125.csv', initial_rows)
    write_csv(out / 'zero_shear_jets_25.csv', jet_rows)
    write_csv(out / 'source_derivative_samples_375.csv', sampled_rows)
    write_csv(out / 'opposing_stress_local_comparison.csv', compare_rows)
    with (out / 'mass_shell_diagnostics.npz').open('xb') as handle:
        np.savez_compressed(handle, case_key=arrays['campaign_case_key'], eta=arrays['eta'],
            requested_signed_full=arrays['requested_signed_full'],
            massive_energy_conservation_residual=packet_conservation,
            packet_mass_release_pi_s_at_zero_shear=packet_release, **derivative_arrays)
    make_plots(out, arrays, selected, jets, early)
    first = [r for r in compare_rows if r['sample_index'] == 1]
    last = [r for r in compare_rows if r['sample_index'] == early - 1]
    summary = {'schema': 'C21N_MASS_SHELL_125_STATIC_ANALYSIS_V1', 'status': 'PASS_SCOPED',
        'scope': 'Original PR147 collisionless non-tilted LRS; derivative analysis of accepted existing trajectories',
        'source': source_identity, 'case_count': 125, 'source_rhs_states': 375,
        'source_signed_field_comparisons': source_compare_count,
        'massive_packet_states': 12625, 'zero_shear_initial_jets': 25,
        'nonzero_opposing_initial_stress_cases': 4,
        'new_ODE_integrations': 0, 'source_initial_state_FP64_bytes': 'IDENTICAL_ALL_125',
        'combined_eta_and_Y_match_raw_FP64_bytes': 'IDENTICAL_ALL_125',
        'original_RHS_used_for_local_derivative_only': True, 'source_and_input_arrays_unchanged': True,
        'maxima': maxima, 'opposing_case_jets': [jet_rows[list(jets).index(i)] for i in selected],
        'existing_local_samples_per_case': early,
        'local_eta_last': last[0]['eta'],
        'local_first_positive_sample_max_absolute_relative_residual': max(abs(r['relative_residual_to_saved']) for r in first),
        'local_last_sample_max_absolute_relative_residual': max(abs(r['relative_residual_to_saved']) for r in last),
        'local_last_sample_max_absolute_residual': max(abs(r['saved_minus_jet']) for r in last),
        'center_case_jet': jets[center[0]],
        'actual_FP_offsets_preserved': True, 'norm_derivative_at_zero': 'NOT_DEFINED_OR_USED; signed amplitudes only',
        'third_order_coefficient': None, 'finite_window_remainder_bound': None, 'global_error_bound': None,
        'PNG_visual_audit': 'PENDING_INDEPENDENT_REVIEW', 'PDF_separate_raster_audit': 'NOT_RUN',
        'code_sha256': {p.name: sha(p) for p in
                        (Path(__file__), HERE / 'mass_shell_derivatives.py')}}
    write_json(out / 'SUMMARY.json', summary)
    write_json(out / 'INPUT_BINDINGS.json', {'source_commit': SOURCE_COMMIT, 'bindings': bindings})
    write_json(out / 'OUTPUT_MANIFEST.json', {'files': [
        {'path': p.name, 'size': p.stat().st_size, 'sha256': sha(p)}
        for p in sorted(out.iterdir()) if p.is_file()]})
    print(json.dumps({'status': summary['status'], 'cases': 125, 'new_ODE_integrations': 0,
                      'maxima': maxima, 'output': str(out)}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--campaign', type=Path, default=M / 'analysis_campaign125_20261021')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    old_mpl = os.environ.get('MPLCONFIGDIR')
    with tempfile.TemporaryDirectory(prefix='c21n-derivative-mpl-') as temp:
        os.environ['MPLCONFIGDIR'] = temp
        try:
            run(args.campaign.resolve(), args.output.resolve())
        finally:
            if old_mpl is None:
                os.environ.pop('MPLCONFIGDIR', None)
            else:
                os.environ['MPLCONFIGDIR'] = old_mpl


if __name__ == '__main__':
    main()
