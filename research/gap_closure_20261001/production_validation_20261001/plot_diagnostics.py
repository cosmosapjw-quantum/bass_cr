"""Plot saved R4V JSON observations only; no evaluator or solver imports."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import NullLocator
import numpy as np


def make_figure(runs: Path, output: Path):
    paths = {'raw': runs/'G02_RESULT.json',
             'richardson': runs/'G02_RICHARDSON_RESULT.json',
             'g12': runs/'G12_ANALYSIS/RESULT.json'}
    docs = {key: json.loads(path.read_text()) for key, path in paths.items()}
    hashes = {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in paths.items()}
    raw, rich, g12 = docs['raw'], docs['richardson'], docs['g12']
    if (raw['status'] != 'FD_VALIDATION_UNRESOLVED'
            or rich['original_acceptance_changed'] is not False
            or g12['production_admission'] != 'HOLD'):
        raise ValueError('figure scope requires the recorded unresolved/HOLD R4V outcome')
    raw_rows = sorted(raw['results'], key=lambda r: r['z_a0'])
    rich_rows = sorted(rich['results'], key=lambda r: r['z_a0'])
    if [r['z_a0'] for r in raw_rows] != [r['z_a0'] for r in rich_rows]:
        raise ValueError('raw and Richardson coordinates differ')
    target = raw['acceptance']['relative_target']
    palette = {12: '#D55E00', 16: '#0072B2', 24: '#009E73', 32: '#7C5AA6'}
    table = []

    def record(dataset, metric, value, source, pointer, *, z='', h='', order='', n='',
               unit='1', plotted=True, derivation='none'):
        value = float(value)
        table.append({'dataset': dataset, 'metric': metric, 'z_a0': z,
                      'h_a0': h, 'order_label': order, 'nstep': n,
                      'value': repr(value), 'value_float64_hex': value.hex(),
                      'unit': unit, 'plotted': str(plotted).lower(),
                      'source_json': paths[source].relative_to(runs).as_posix(),
                      'source_sha256': hashes[source], 'json_pointer': pointer,
                      'derivation': derivation})

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10.5,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.labelsize': 11, 'axes.titlesize': 12,
                         'legend.fontsize': 9, 'savefig.facecolor': 'white'})
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 6.25))
    fig.subplots_adjust(left=.062, right=.985, bottom=.27, top=.80, wspace=.34)
    fig.suptitle('BASS CR  |  Saved physical diagnostics, archived B0',
                 x=.062, y=.965, ha='left', fontsize=17, fontweight='semibold')
    fig.text(.062, .916, '100 keV/u  ·  b = 2 a₀  ·  18 channels  ·  No scientific gate promotion',
             fontsize=11, color='#4D5662')
    for ax in axes:
        ax.grid(True, which='major', color='#E1E5EB', linewidth=.7)
        ax.set_axisbelow(True)

    for row in raw_rows:
        z = row['z_a0']; i = raw['results'].index(row)
        hs = [r['h_a0'] for r in row['rows']]
        vals = [r['spectral_relative'] for r in row['rows']]
        style = {'color': palette[abs(z)], 'ls': '--' if z < 0 else '-',
                 'marker': 'o', 'ms': 4.7, 'lw': 1.25,
                 'mfc': 'white' if z < 0 else palette[abs(z)]}
        axes[0].plot(hs, vals, **style)
        for j, r in enumerate(row['rows']):
            record('G02_raw', 'spectral_relative', r['spectral_relative'], 'raw',
                   f'/results/{i}/rows/{j}/spectral_relative', z=z, h=r['h_a0'], order='R2')
    record('G02_original_target', 'spectral_relative_target', target, 'raw',
           '/acceptance/relative_target')
    axes[0].axhline(target, color='#A52A2A', lw=1.35, ls=':')
    axes[0].text(.052, target*1.28, 'Original relative target: 10⁻⁶', color='#8B2525', fontsize=9)
    axes[0].set(xscale='log', yscale='log', xlim=(.043, .47), ylim=(6e-7, .06),
                xlabel=r'Central-difference step $h$ [$a_0$]',
                ylabel='Spectral relative disagreement', title='A  Raw FD — original gate unresolved')
    axes[0].set_xticks([.05, .1, .2, .4], ['0.05', '0.1', '0.2', '0.4'])
    handles = [Line2D([], [], color=palette[z], lw=2, label=f'|z| = {z} a₀')
               for z in (12, 16, 24, 32)]
    axes[0].legend(handles=handles, loc='upper left', ncol=2, frameon=False,
                   columnspacing=.75, handlelength=1.25, bbox_to_anchor=(-.02, 1.015))
    axes[0].text(.04, .38, '+z: solid / filled\n−z: dashed / open\nSigned pairs nearly overlap',
                 transform=axes[0].transAxes, fontsize=8.8, color='#555B65')

    for row in rich_rows:
        z = row['z_a0']; i = rich['results'].index(row)
        values = []
        for j, layer in enumerate(row['layers']):
            values.append(layer['rows'][-1]['disagreement_with_D_plus_Ddagger_relative']['spectral'])
            for k, item in enumerate(layer['rows']):
                record('G02_Richardson', 'spectral_relative',
                       item['disagreement_with_D_plus_Ddagger_relative']['spectral'],
                       'richardson',
                       f'/results/{i}/layers/{j}/rows/{k}/disagreement_with_D_plus_Ddagger_relative/spectral',
                       z=z, h=item['finest_h_a0'], order=layer['name'],
                       plotted=k == len(layer['rows'])-1)
        axes[1].plot([2, 4, 6, 8], values, color=palette[abs(z)],
                     ls='--' if z < 0 else '-', marker='o', ms=4.7, lw=1.25,
                     mfc='white' if z < 0 else palette[abs(z)])
    axes[1].set(yscale='log', xlim=(1.6, 8.4), ylim=(1e-12, 2e-3),
                xticks=[2, 4, 6, 8], xticklabels=['R2', 'R4', 'R6', 'R8'],
                xlabel='Fixed extrapolation order label',
                ylabel='Spectral relative disagreement', title='B  Richardson — observations only')
    axes[1].text(.03, .045, 'Finest available stencil in each layer\nAll use hₘᵢₙ = 0.05 a₀\nOne R8 estimate; no certified error bound',
                 transform=axes[1].transAxes, fontsize=8.8, color='#555B65')

    midpoint = sorted(g12['midpoint'], key=lambda r: r['nstep'])
    ns = np.array([r['nstep'] for r in midpoint])
    distances = [r['unaligned_metric_distance_to_dop853'] for r in midpoint]
    reference = distances[0]*(ns[0]/ns)**2
    axes[2].plot(ns, reference, ls=':', color='#9D6A12', lw=3., label=r'$n^{-2}$ guide (anchored at $n=1$)')
    axes[2].plot(ns, distances, '-o', color='#174A6E', lw=1.5, ms=6,
                 label='Midpoint vs DOP853')
    for i, (row, ref) in enumerate(zip(midpoint, reference)):
        actual_i = g12['midpoint'].index(row)
        record('G12_local', 'unaligned_S_metric_distance', row['unaligned_metric_distance_to_dop853'],
               'g12', f'/midpoint/{actual_i}/unaligned_metric_distance_to_dop853', n=row['nstep'])
        record('G12_guide', 'n_inverse_squared_reference', ref, 'g12',
               '/midpoint/0/unaligned_metric_distance_to_dop853', n=row['nstep'],
               derivation='distance_n1 / nstep**2; visual guide, not independent data')
    p = g12['midpoint_refinement']['observed_order']
    record('G12_local', 'observed_order_successive_midpoint_differences', p, 'g12',
           '/midpoint_refinement/observed_order', plotted=False)
    axes[2].set(xscale='log', yscale='log', xlim=(.88, 4.55), ylim=(4e-13, 2.4e-11),
                xlabel='Midpoint steps over the same interval, n',
                ylabel=r'Endpoint distance $\|c_n-c_{\rm DOP853}\|_{S_f}$',
                title='C  G12 — local integrator comparison')
    axes[2].set_xticks([1, 2, 4], ['1', '2', '4'])
    axes[2].xaxis.set_minor_locator(NullLocator())
    axes[2].legend(loc='upper right', frameon=False, fontsize=8.7)
    axes[2].text(.04, .09, f'Successive-difference order: {p:.6f}\nS-metric distance; no phase alignment\nDifferent metric from panels A and B',
                 transform=axes[2].transAxes, fontsize=8.8, color='#555B65')

    fig.text(.062, .158,
             r'A, B: $\|\dot S_{\rm estimate}-(D+D^\dagger)\|_2\,/\,\max(\|\dot S_{\rm estimate}\|_2,\|D+D^\dagger\|_2)$; dimensionless.',
             fontsize=10.3)
    fig.text(.062, .107,
             'Raw G02 remains UNRESOLVED. Richardson does not replace the frozen raw acceptance criteria or certify the operator error.',
             fontsize=10.2, color='#7D2929')
    fig.text(.062, .057,
             'G12: z = 32 → 32.02 a₀; explicit e₀ initial vector. Local pilot only. Production HOLD; no scattering/capture claim.',
             fontsize=10.2, color='#4D5662')
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output/'G02_G12_DIAGNOSTICS.csv'
    image_path = output/'G02_G12_DIAGNOSTICS.png'
    if csv_path.exists() or image_path.exists():
        raise FileExistsError('create-only figure output already exists')
    with csv_path.open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]))
        writer.writeheader(); writer.writerows(table)
    fig.savefig(image_path, dpi=220, metadata={'Description':
                'R4V saved JSON observations; raw G02 unresolved; production HOLD. '
                + '; '.join(f'{key} SHA256={value}' for key, value in hashes.items())})
    plt.close(fig)
    print(json.dumps({'png': str(image_path), 'csv': str(csv_path), 'csv_rows': len(table),
                      'source_sha256': hashes, 'new_native_calls': 0}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    make_figure(args.runs, args.output)
