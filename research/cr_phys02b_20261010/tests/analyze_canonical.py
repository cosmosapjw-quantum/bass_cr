# SPDX-License-Identifier: GPL-3.0-only
"""Postprocess an actually completed PHYS02B canonical run.

Build the canonical generator exactly once, reuse its saved trajectory, and
recover active-state occupation by integrating the frozen linear equation:
    J = solve(Gaa, x_active(1) - A_active/2).
This is a diagnostic of the same conditional model, not an independent
physical validation or final admission decision. No source or runner files
are modified. --render-only reuses saved diagnostic arrays without a G build.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from scipy.sparse.linalg import spsolve


ROOT = Path(__file__).resolve().parents[1]
TAGS = ('direct_0p1_10', 'direct_10_900')
ENERGY_NAMES = ('heat', 'binding_HI', 'binding_HeI', 'excitation_HI',
                'excitation_HeI', 'cutoff_energy')


def file_identity(path):
    path = Path(path)
    raw = path.read_bytes()
    return {'path': str(path.resolve()), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}


def relative_array(observed, expected):
    observed, expected = np.broadcast_arrays(observed, expected)
    difference = np.abs(observed - expected)
    result = np.zeros_like(difference, dtype=float)
    nonzero = expected != 0.
    result[nonzero] = difference[nonzero] / np.abs(expected[nonzero])
    if np.any(difference[~nonzero] != 0.):
        raise ArithmeticError('NONZERO_DIAGNOSTIC_WHERE_REFERENCE_IS_EXACT_ZERO')
    return result


def completion_gate(run_dir):
    required = ('NUMERICAL_RESULT.json', 'CANONICAL_SPECTRUM.npz',
                'ACTUAL_EXIT.json', 'stdout.log', 'stderr.log')
    missing = [name for name in required if not (run_dir / name).is_file()]
    if missing:
        raise RuntimeError('CANONICAL_RUN_NOT_COMPLETE: ' + ', '.join(missing))
    result = json.loads((run_dir / 'NUMERICAL_RESULT.json').read_text())
    actual_exit = json.loads((run_dir / 'ACTUAL_EXIT.json').read_text())
    if result.get('status') != 'PASS_SCOPED' or not result.get('end_utc'):
        raise RuntimeError('CANONICAL_RUN_NOT_SUCCESSFULLY_FINISHED')
    if actual_exit.get('actual_process_exit_code') != 0:
        raise RuntimeError('CANONICAL_ACTUAL_EXIT_NOT_ZERO')
    stdout = (run_dir / 'stdout.log').read_text()
    if not stdout.rstrip().endswith('FINAL_STATUS PASS_SCOPED'):
        raise RuntimeError('CANONICAL_FINAL_STDOUT_MARKER_MISSING')
    if result.get('canonical_mesh') != [1600, 3200]:
        raise RuntimeError('EXPECTED_FINAL_1600_3200_CANONICAL_MESH')
    for relative_path, expected in result['source_identities'].items():
        actual = file_identity(ROOT / relative_path)
        if actual['sha256'] != expected['sha256'] or actual['bytes'] != expected['bytes']:
            raise RuntimeError('SOURCE_CHANGED_SINCE_CANONICAL_RUN: ' + relative_path)
    return result, actual_exit, {name: file_identity(run_dir / name) for name in required}


def render_figure(output_dir):
    """Render saved diagnostic values only; never construct the generator."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import LogLocator, PercentFormatter

    result = json.loads((output_dir / 'DIAGNOSTIC_RESULT.json').read_text())
    with np.load(output_dir / 'OCCUPANCY_AND_PLOT_DATA.npz', allow_pickle=False) as data:
        years = data['time_s'] / 31557600.
        heat_rates = data['heat_rate_by_birth_tag_J_m3_s']
        rate_energy = data['rate_energy_eV']
        atomic_rates = data['rate_curves_s_inverse']

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.titlesize': 12, 'axes.labelsize': 10,
                         'legend.fontsize': 9, 'axes.spines.top': False,
                         'axes.spines.right': False, 'savefig.facecolor': 'white'})
    fig, axes = plt.subplots(2, 2, figsize=(14.4, 10.5))
    fig.subplots_adjust(left=.14, right=.98, bottom=.12, top=.835,
                        wspace=.30, hspace=.47)
    selected_percent = 100 * result['source_coverage']['selected_fraction_of_all_direct']
    title = 'CR-PHYS02B  |  Prescribed fixed bath, conditional hybrid model'
    if result['status'] != 'DIAGNOSTIC_CONSISTENCY_PASS':
        title += '  |  DIAGNOSTIC CHECK FAILED'
    fig.suptitle(title, fontsize=15, fontweight='bold', y=.982)
    fig.text(.5, .945,
             f'0.1–900 eV retains {selected_percent:.2f}% of this proton-born electron-source energy',
             ha='center', fontsize=12)
    fig.text(.5, .917,
             r'$n_{\rm H}=140\ {\rm m}^{-3}$, $Y_{\rm He}=0.248$, $x_i=0.01$, $T=100\ {\rm K}$'
             '   |   4800 active nodes   |   source ramp to 317 years',
             ha='center', fontsize=10, color='#444444')

    low_color, high_color, total_color = '#2166ac', '#d47719', '#17222c'

    ax = axes[0, 0]
    power_exponent = int(np.floor(np.log10(np.max(heat_rates.sum(axis=1)))))
    power_unit = 10.**power_exponent
    ax.plot(years, heat_rates.sum(axis=1) / power_unit, color=total_color,
            linewidth=2.3, label='Selected total')
    ax.plot(years, heat_rates[:, 0] / power_unit, color=low_color,
            linewidth=2., label='Birth 0.1–10 eV')
    ax.plot(years, heat_rates[:, 1] / power_unit, color=high_color,
            linewidth=2., linestyle='--', label='Birth 10–900 eV')
    ax.set_title('A   Causal heat power by birth tag', loc='left', pad=12)
    ax.set_xlabel('Time since source turn-on [years]')
    ax.set_ylabel(r'Heat power [$10^{%d}$ J m$^{-3}$ s$^{-1}$]' % power_exponent)
    ax.set_xlim(0, years[-1])
    ax.set_ylim(bottom=0)
    ax.grid(alpha=.2)
    ax.legend(loc='upper left', frameon=False)

    ax = axes[0, 1]
    fractions = result['energy_fractions_of_selected_injected_energy']
    labels = ['Coulomb heat', 'Ion binding', 'Atomic excitation',
              'Cutoff kinetic', 'Active electrons']
    keys = ['heat', 'binding_total', 'excitation_total', 'cutoff_energy', 'active_energy']
    finite = np.array([fractions['finite_time'][key] for key in keys])
    terminal = np.array([fractions['fixed_bath_terminal'][key] for key in keys])
    y = np.arange(len(keys))
    ax.barh(y - .18, finite, height=.32, color=low_color, label='Finite time: 317 years')
    ax.barh(y + .18, terminal, height=.32, color='#ddab6b', label='Fixed bath terminal reference')
    for dy, values in ((-.18, finite), (.18, terminal)):
        for j, value in enumerate(values):
            if value > .93:
                ax.text(value - .018, j + dy, f'{100*value:.2f}%', ha='right', va='center', fontsize=8, color='white')
            else:
                ax.text(value + .012, j + dy, f'{100*value:.2f}%', ha='left', va='center', fontsize=8)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.05)
    ax.xaxis.set_major_formatter(PercentFormatter(1.))
    ax.set_xlabel('Fraction of selected injected energy')
    ax.set_title('B   Finite storage and terminal reference', loc='left', pad=12)
    ax.grid(axis='x', alpha=.18)
    ax.legend(loc='lower center', bbox_to_anchor=(.5, -.33), frameon=False)

    ax = axes[1, 0]
    coverage = result['source_coverage']['band_fractions_of_all_direct']
    coverage_keys = ['below_cutoff', 'direct_low', 'direct_high_selected',
                     'unselected_900_1000', 'unselected_above_1000']
    coverage_labels = ['<0.1 eV  excluded', '0.1–10 eV  selected', '10–900 eV  selected',
                       '900–1000 eV  excluded', '>1000 eV  excluded']
    values = np.array([coverage[key] for key in coverage_keys])
    y = np.arange(len(values))
    ax.barh(y, values, color=['#aeb3b9', low_color, high_color, '#aeb3b9', '#aeb3b9'], height=.60)
    for j, value in enumerate(values):
        label = f'{100*value:.4f}%' if value < 1.e-4 else f'{100*value:.2f}%'
        ax.text(value + .011, j, label, va='center', fontsize=9)
    ax.set_yticks(y, coverage_labels)
    ax.invert_yaxis()
    ax.set_xlim(0, .8)
    ax.xaxis.set_major_formatter(PercentFormatter(1.))
    ax.set_xlabel('Fraction of all direct electron-source energy')
    ax.set_title('C   Source-energy coverage', loc='left', pad=12)
    ax.grid(axis='x', alpha=.18)
    ax.text(.99, .05, f'Selected: {selected_percent:.2f}%\nExcluded: {100-selected_percent:.2f}%',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=10,
            bbox={'facecolor': 'white', 'edgecolor': '#dddddd', 'alpha': .95})

    ax = axes[1, 1]
    rate_labels = [r'Coulomb $b(E)/E$', 'HI ionization', 'HeI ionization',
                   'HI excitation (n=2–4)', 'HeI excitation (n=2–4)']
    rate_colors = [total_color, '#2166ac', '#5b9dce', '#d47719', '#aa336a']
    for k, (label, color) in enumerate(zip(rate_labels, rate_colors)):
        positive = atomic_rates[k] > 0.
        ax.loglog(rate_energy[positive], atomic_rates[k, positive], label=label,
                  color=color, linewidth=1.6, linestyle='--' if k in (2, 4) else '-')
    ax.set_title('D   Fixed-bath rate scales', loc='left', pad=12)
    ax.set_xlabel('Electron kinetic energy [eV]')
    ax.set_ylabel(r'Rate scale [s$^{-1}$]')
    ax.set_xlim(.1, 900)
    ax.axvline(10., color='#777777', alpha=.45, linewidth=.8)
    ax.xaxis.set_major_locator(LogLocator(base=10., numticks=5))
    ax.grid(which='major', alpha=.18)
    ax.legend(loc='lower left', fontsize=8, frameon=False)

    fig.text(.5, .041,
             'HI/HeI only. Excitation remains an energy reservoir; photon transport and gas feedback are outside this model.',
             ha='center', fontsize=9, color='#444444')
    fig.text(.5, .020,
             'Terminal = mathematical reference of the same frozen operator, not a future physical trajectory. Coulomb b/E is a fractional-loss scale.',
             ha='center', fontsize=9, color='#444444')
    png = output_dir / 'canonical_diagnostics.png'
    fig.savefig(png, dpi=200)
    plt.close(fig)
    return file_identity(png)


def analyze(run_dir, output_dir):
    started = time.perf_counter()
    canonical, actual_exit, input_files = completion_gate(run_dir)
    print('CANONICAL_COMPLETION_CONFIRMED ' + json.dumps({
        'run': run_dir.name, 'status': canonical['status'],
        'mesh': canonical['canonical_mesh'],
        'actual_process_exit_code': actual_exit['actual_process_exit_code']}), flush=True)
    if (output_dir / 'DIAGNOSTIC_RESULT.json').exists():
        raise FileExistsError('PRESERVE_EXISTING_DIAGNOSTIC_RESULT')
    output_dir.mkdir(parents=True, exist_ok=True)
    with np.load(run_dir / 'CANONICAL_SPECTRUM.npz', allow_pickle=False) as data:
        energy = np.array(data['energy_eV'])
        states = np.array(data['state_normalized'])
        forcing = np.array(data['source_vectors'])
        physical_scale_eV_m3 = float(data['physical_energy_scale_eV_m3'])
        times = np.array(data['time_s'])
    sys.path.insert(0, str(ROOT / 'src'))
    import causal_cascade as cc
    contract = json.loads((ROOT / 'state/SCIENTIFIC_CONTRACT.json').read_text())
    ledger_tolerance = contract['tolerances']['propagated_ledger_relative']
    positivity_tolerance = contract['tolerances']['positivity_absolute_normalized']
    if times.shape != (21,) or times[0] != 0. or times[-1] != cc.T_END:
        raise ValueError('UNEXPECTED_CANONICAL_TIME_COORDINATES')
    if states.shape != (21, energy.size + 11, 2) or forcing.shape != (energy.size + 11, 2):
        raise ValueError('UNEXPECTED_CANONICAL_STATE_SHAPES')
    if np.any(states[0] != 0.) or np.any(~np.isfinite(states)) or np.any(~np.isfinite(forcing)):
        raise ValueError('INVALID_CANONICAL_INITIAL_OR_FINITE_STATE')

    print('BUILD_CANONICAL_GENERATOR_ONCE', flush=True)
    build_started = time.perf_counter()
    atomic = cc.AtomicData()
    model = cc.Cascade(*canonical['canonical_mesh'], sharing_order=4,
                       quantum_constant=0., atomic=atomic)
    build_seconds = time.perf_counter() - build_started
    if not np.array_equal(model.E, energy):
        raise ValueError('RECONSTRUCTED_GRID_DIFFERS_FROM_CANONICAL')
    if model.G.nnz != canonical['grid_results'][-1]['nnz']:
        raise ValueError('RECONSTRUCTED_GENERATOR_NNZ_DIFFERS')
    if model.G[:model.n, model.n:].nnz:
        raise ValueError('PASSIVE_LEDGERS_FEED_ACTIVE_STATES')
    heat_index = model.ix['heat']
    if np.any(forcing[heat_index] != 0.):
        raise ValueError('UNEXPECTED_DIRECT_HEAT_SOURCE_PREVENTS_REQUESTED_PARTITION')
    print('GENERATOR_READY ' + json.dumps({'seconds': build_seconds,
          'nodes': model.n, 'nnz': int(model.G.nnz)}), flush=True)

    # Exact integrated equation for this frozen discrete operator; no time rerun.
    active_generator = model.G[:model.n, :model.n]
    rhs = states[-1, :model.n, :] - .5 * forcing[:model.n, :]
    solve_started = time.perf_counter()
    occupation = np.asarray(spsolve(active_generator, rhs))
    if occupation.shape != rhs.shape or np.any(~np.isfinite(occupation)):
        raise ArithmeticError('INVALID_ACTIVE_OCCUPATION_SOLUTION')
    solve_seconds = time.perf_counter() - solve_started
    residual = np.asarray(active_generator @ occupation - rhs)
    residual_per_tag = np.max(np.abs(residual), axis=0) / np.max(np.abs(rhs), axis=0)
    heat_row = np.asarray(model.G[heat_index, :model.n].toarray()).ravel()
    low = energy <= cc.SPLIT
    high = energy > cc.SPLIT
    accumulated = np.vstack([heat_row[low] @ occupation[low], heat_row[high] @ occupation[high]])
    final_power_u = np.vstack([heat_row[low] @ states[-1, :model.n, :][low],
                               heat_row[high] @ states[-1, :model.n, :][high]])
    saved_heat = states[-1, heat_index, :]
    cumulative_relative = relative_array(accumulated.sum(axis=0), saved_heat)
    energy_scale_J_m3 = physical_scale_eV_m3 * cc.EV_J
    power_scale = energy_scale_J_m3 / cc.T_END
    heat_rate_by_tag = np.einsum('j,tjk->tk', heat_row, states[:, :model.n, :]) * power_scale
    recorded_power = np.array([[row['components'][tag]['heat_power_J_m3_s'] for tag in TAGS]
                               for row in canonical['time_series']])
    trajectory_power_relative = relative_array(heat_rate_by_tag, recorded_power)
    final_power_reference = np.array([canonical['final']['components'][tag]['heat_power_J_m3_s'] for tag in TAGS])
    final_power_relative = relative_array(final_power_u.sum(axis=0) * power_scale, final_power_reference)

    partition = {}
    for k, tag in enumerate(TAGS):
        h = accumulated[:, k] * energy_scale_J_m3
        rate = final_power_u[:, k] * power_scale
        partition[tag] = {
            'cumulative_heat_at_electron_E_le_10_J_m3': float(h[0]),
            'cumulative_heat_at_electron_E_gt_10_J_m3': float(h[1]),
            'cumulative_heat_total_J_m3': float(h.sum()),
            'instantaneous_heat_at_electron_E_le_10_J_m3_s': float(rate[0]),
            'instantaneous_heat_at_electron_E_gt_10_J_m3_s': float(rate[1]),
            'instantaneous_heat_total_J_m3_s': float(rate.sum()),
            'cumulative_low_energy_share_of_tag_heat': float(h[0] / h.sum()),
            'instantaneous_low_energy_share_of_tag_heat': float(rate[0] / rate.sum()),
        }
    total_h = accumulated.sum(axis=1) * energy_scale_J_m3
    total_rate = final_power_u.sum(axis=1) * power_scale
    partition['selected_total'] = {
        'cumulative_heat_at_electron_E_le_10_J_m3': float(total_h[0]),
        'cumulative_heat_at_electron_E_gt_10_J_m3': float(total_h[1]),
        'cumulative_heat_total_J_m3': float(total_h.sum()),
        'instantaneous_heat_at_electron_E_le_10_J_m3_s': float(total_rate[0]),
        'instantaneous_heat_at_electron_E_gt_10_J_m3_s': float(total_rate[1]),
        'instantaneous_heat_total_J_m3_s': float(total_rate.sum()),
        'cumulative_low_energy_share_of_total_heat': float(total_h[0] / total_h.sum()),
        'instantaneous_low_energy_share_of_total_heat': float(total_rate[0] / total_rate.sum()),
    }

    input_energy_normalized = .5 * (float(forcing[:model.n].sum())
        + sum(float(forcing[model.ix[name]].sum()) for name in ENERGY_NAMES))
    finite = {name: float(states[-1, model.ix[name], :].sum() / input_energy_normalized)
              for name in ENERGY_NAMES}
    finite['active_energy'] = float(states[-1, :model.n, :].sum() / input_energy_normalized)
    finite['binding_total'] = finite['binding_HI'] + finite['binding_HeI']
    finite['excitation_total'] = finite['excitation_HI'] + finite['excitation_HeI']
    terminal = dict(canonical['same_operator_terminal']['energy_fractions_of_selected_input'])
    terminal['active_energy'] = 0.
    terminal['binding_total'] = terminal['binding_HI'] + terminal['binding_HeI']
    terminal['excitation_total'] = terminal['excitation_HI'] + terminal['excitation_HeI']
    closure_keys = (*ENERGY_NAMES, 'active_energy')
    finite_closure = abs(sum(finite[key] for key in closure_keys) - 1.)
    terminal_closure = abs(sum(terminal[key] for key in closure_keys) - 1.)
    low_birth_high_heat = bool(np.all(accumulated[1, 0] == 0.) and np.all(final_power_u[1, 0] == 0.))
    checks = {
        'occupation_linear_solve': {'passed': bool(np.max(residual_per_tag) <= ledger_tolerance),
            'relative_residual_per_tag': residual_per_tag.tolist(), 'tolerance': ledger_tolerance},
        'occupation_nonnegative': {'passed': bool(np.min(occupation) >= -positivity_tolerance),
            'minimum_normalized_occupation': float(np.min(occupation)), 'tolerance': positivity_tolerance},
        'cumulative_heat_matches_saved_ledger': {'passed': bool(np.max(cumulative_relative) <= ledger_tolerance),
            'relative_error_per_tag': cumulative_relative.tolist(), 'tolerance': ledger_tolerance},
        'instantaneous_heat_matches_final_result': {'passed': bool(np.max(final_power_relative) <= ledger_tolerance),
            'relative_error_per_tag': final_power_relative.tolist(), 'tolerance': ledger_tolerance},
        'saved_trajectory_heat_power_matches_JSON': {'passed': bool(np.max(trajectory_power_relative) <= ledger_tolerance),
            'maximum_relative_error': float(np.max(trajectory_power_relative)), 'tolerance': ledger_tolerance},
        'finite_and_terminal_energy_partition_closure': {'passed': bool(max(finite_closure, terminal_closure) <= ledger_tolerance),
            'finite_absolute_residual': finite_closure, 'terminal_absolute_residual': terminal_closure,
            'tolerance': ledger_tolerance},
        'low_birth_tag_has_no_heat_above_10_eV': {'passed': low_birth_high_heat,
            'cumulative_normalized': float(accumulated[1, 0]), 'instantaneous_normalized_per_u': float(final_power_u[1, 0])},
    }
    source_stable = all(file_identity(run_dir / name)['sha256'] == identity['sha256']
                        for name, identity in input_files.items())
    if not source_stable:
        raise RuntimeError('CANONICAL_ARTIFACT_CHANGED_DURING_DIAGNOSTICS')
    result = {
        'schema': 'cr-phys02b-canonical-diagnostics.v1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'DIAGNOSTIC_CONSISTENCY_PASS' if all(check['passed'] for check in checks.values()) else 'DIAGNOSTIC_CONSISTENCY_FAIL',
        'role': 'Additional same-model physical diagnostics by verification participant; no final PROMOTE/admission decision.',
        'run_directory': str(run_dir.resolve()), 'canonical_mesh': canonical['canonical_mesh'],
        'canonical_run_status': canonical['status'], 'canonical_actual_exit': actual_exit,
        'input_files': input_files, 'analysis_script_identity': file_identity(__file__),
        'source_identities_verified': canonical['source_identities'],
        'scope': {'model': 'conditional hybrid; prescribed fixed bath',
                  'active_electron_interval_eV': [.1, 900.], 'birth_tags_eV': [[.1, 10.], [10., 900.]],
                  'heat_partition_coordinate': 'Electron energy immediately before Coulomb energy loss, separate from birth-source energy.',
                  'bath': contract['bath'], 'HeII_channels': False,
                  'photon_semantics': 'Excitation energy reservoir; no branching, transport, or reabsorption calculation.',
                  'terminal': 'Mathematical resolvent of the same frozen operator; not a physical continuation of the local source.',
                  'interpretation_limit': 'Postprocessing shares the canonical generator, source and saved trajectory. No independent physical error certificate.'},
        'source_coverage': canonical['coverage'],
        'occupation': {'equation': 'Gaa*J = x_active(u=1) - A_active/2; J=int_0^1 x_active(u)du; x(0)=0',
                       'basis': 'Energy-weighted electron nodes E_j*N_j normalized by energy_scale_eV_m3.',
                       'canonical_generators_constructed': 1, 'trajectory_recomputed': False,
                       'generator_build_seconds': build_seconds, 'occupation_solve_seconds': solve_seconds,
                       'generator_nnz': int(model.G.nnz), 'active_nodes': model.n},
        'checks': checks, 'heat_partition_by_birth_tag': partition,
        'energy_fractions_of_selected_injected_energy': {'finite_time': finite, 'fixed_bath_terminal': terminal},
        'finite_to_terminal_heat_power_ratio': canonical['same_operator_terminal']['finite_to_terminal_heat_power_ratio'],
        'heat_rate_time_series': {'time_s': times.tolist(), 'birth_tags': list(TAGS),
                                'values_J_m3_s': heat_rate_by_tag.tolist()},
        'energy_scale_J_m3': energy_scale_J_m3,
        'selected_injected_energy_at_T_J_m3': input_energy_normalized * energy_scale_J_m3,
        'diagnostic_elapsed_before_render_s': time.perf_counter() - started,
        'scientific_suites_rerun': 0, 'external_mutations': 0,
    }
    np.savez_compressed(output_dir / 'OCCUPANCY_AND_PLOT_DATA.npz',
        occupation_normalized=occupation, energy_eV=energy, heat_row_per_u=heat_row,
        time_s=times, heat_rate_by_birth_tag_J_m3_s=heat_rate_by_tag,
        rate_energy_eV=model.E,
        rate_curves_s_inverse=np.vstack([model.rates['stopping_eV_s'] / model.E,
            model.rates['ion_HI'], model.rates['ion_HeI'], model.rates['exc_HI'], model.rates['exc_HeI']]))
    result['saved_diagnostic_array_identity'] = file_identity(output_dir / 'OCCUPANCY_AND_PLOT_DATA.npz')
    (output_dir / 'DIAGNOSTIC_RESULT.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    png_identity = render_figure(output_dir)
    print('HEAT_PARTITION ' + json.dumps(partition), flush=True)
    print('DIAGNOSTIC_CHECKS ' + json.dumps(checks), flush=True)
    print('FIGURE ' + json.dumps(png_identity), flush=True)
    print('FINAL_DIAGNOSTIC_STATUS ' + result['status'], flush=True)
    return 0 if result['status'] == 'DIAGNOSTIC_CONSISTENCY_PASS' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, default=ROOT / 'evidence/runs/R002')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'evidence/diagnostics')
    parser.add_argument('--render-only', action='store_true')
    args = parser.parse_args()
    if args.render_only:
        print(json.dumps(render_figure(args.output_dir), indent=2), flush=True)
        return 0
    return analyze(args.run_dir, args.output_dir)


if __name__ == '__main__':
    raise SystemExit(main())
