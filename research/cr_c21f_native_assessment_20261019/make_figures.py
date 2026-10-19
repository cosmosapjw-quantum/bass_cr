#!/usr/bin/env python3
"""Plot immutable C21F terminal outputs; no solver invocation or fitted accuracy claim."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/c21f_matplotlib_config')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

MODES = ('BE', 'FULLMID', 'MIDPHOTO_ENDMICRO')
COLORS = {'BE': '#465366', 'FULLMID': '#1763a6', 'MIDPHOTO_ENDMICRO': '#d25a16'}
MARKERS = {'BE': 'o', 'FULLMID': 's', 'MIDPHOTO_ENDMICRO': '^'}
NS = np.array([8, 16, 32, 64])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    inputs = {}
    data = {}
    for lane in ('common_ic', 'native_source'):
        folder = args.evidence / lane
        names = ['fixture.json', 'radau.json'] + [f'{mode}_{n:04d}/result.json' for mode in MODES for n in NS]
        raw = {}
        for name in names:
            path = folder / name
            blob = path.read_bytes()
            inputs[f'{lane}/{name}'] = hashlib.sha256(blob).hexdigest()
            raw[name] = json.loads(blob)
        fixture = raw['fixture.json']
        reference = np.asarray(raw['radau.json']['gas'])
        scale = np.array([1., 1., 1., fixture['gas0'][3]])
        records = {}
        for mode in MODES:
            gas = np.asarray([raw[f'{mode}_{n:04d}/result.json']['gas'] for n in NS])
            errors = gas - reference
            records[mode] = {
                'gas': gas.tolist(), 'signed_thermal_eV_H': errors[:, 3].tolist(),
                'normalized_max_gas_error': np.max(np.abs(errors) / scale, axis=1).tolist(),
            }
        data[lane] = records

    plt.rcParams.update({
        'font.size': 10.5, 'axes.titlesize': 12, 'axes.labelsize': 11,
        'axes.spines.top': False, 'axes.spines.right': False,
        'savefig.dpi': 180, 'figure.facecolor': 'white',
    })
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), layout='constrained')
    for ax, lane, title in zip(axes, data, ('Common IC: opacity scale 0.001', 'Native 12-cell source: opacity scale 1')):
        for mode in MODES:
            ax.plot(NS, data[lane][mode]['normalized_max_gas_error'], color=COLORS[mode], marker=MARKERS[mode], lw=1.8, label=mode)
        ax.set_xscale('log', base=2)
        ax.set_yscale('log')
        ax.set_xticks(NS, [str(n) for n in NS])
        ax.set_xlabel('Subdivisions per event interval, n')
        ax.set_ylabel(r'$\max(|\delta x_{\rm HII}|,|\delta x_{\rm HeII}|,|\delta x_{\rm HeIII}|,|\delta w|/w_0)$')
        ax.set_title(title)
        ax.grid(True, which='major', alpha=.22)
    axes[0].legend(frameon=False, fontsize=9)
    fig.suptitle('C21F: gas error relative to the stored optical-depth Radau reference', fontsize=13)
    for ext in ('png', 'svg'):
        fig.savefig(args.out / f'time_refinement.{ext}')
    plt.close(fig)

    lane = data['native_source']
    full = np.asarray(lane['FULLMID']['signed_thermal_eV_H'])
    hybrid = np.asarray(lane['MIDPHOTO_ENDMICRO']['signed_thermal_eV_H'])
    delta = np.asarray(lane['MIDPHOTO_ENDMICRO']['gas'])[:, 3] - np.asarray(lane['FULLMID']['gas'])[:, 3]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.7), layout='constrained')
    ax = axes[0]
    for mode, values in [('FULLMID', full), ('MIDPHOTO_ENDMICRO', hybrid)]:
        ax.plot(NS, values, marker=MARKERS[mode], color=COLORS[mode], lw=1.8, label=mode)
    ax.axhline(0, color='#242424', lw=.9)
    ax.set_yscale('symlog', linthresh=2e-7)
    ax.set_xscale('log', base=2)
    ax.set_xticks(NS, [str(n) for n in NS])
    ax.set_xlabel('Subdivisions per event interval, n')
    ax.set_ylabel(r'Signed thermal error $w_n-w_{\rm Radau}$ [eV/H]')
    ax.set_title('Thermal cancellation and a sign change')
    ax.grid(True, alpha=.22)
    ax.legend(frameon=False, fontsize=9)
    ax.annotate('Hybrid error changes sign', xy=(64, hybrid[-1]), xytext=(16, -8e-7),
                arrowprops={'arrowstyle': '->', 'color': COLORS['MIDPHOTO_ENDMICRO']},
                color=COLORS['MIDPHOTO_ENDMICRO'], fontsize=9)
    ax = axes[1]
    ax.plot(NS, NS * delta * 1e5, 'o-', color='#754a97', lw=1.8)
    ax.set_xscale('log', base=2)
    ax.set_xticks(NS, [str(n) for n in NS])
    ax.set_xlabel('Subdivisions per event interval, n')
    ax.set_ylabel(r'$n(w_{\rm HYB}-w_{\rm FULL})$ [$10^{-5}$ eV/H]')
    ax.set_title('The leading difference scales as 1/n')
    ax.grid(True, alpha=.22)
    orders = np.log2(np.abs(delta[:-1] / delta[1:]))
    ax.text(.05, .16, 'Difference orders: ' + ', '.join(f'{p:.4f}' for p in orders) + '\nRadau cancels from this difference.',
            transform=ax.transAxes, fontsize=9, bbox={'facecolor':'white', 'alpha':.9, 'edgecolor':'none'})
    fig.suptitle('Native 12-cell source: why the hybrid method can appear unusually accurate', fontsize=13)
    for ext in ('png', 'svg'):
        fig.savefig(args.out / f'hybrid_signed_cancellation.{ext}')
    plt.close(fig)
    record = {'input_sha256': inputs, 'n': NS.tolist(), 'data': data,
              'native_thermal_difference_eV_H': delta.tolist(),
              'native_thermal_difference_orders': orders.tolist(),
              'scope': 'Existing fixed-source raw outputs only; no new native execution; stored-reference differences are not absolute error bounds.'}
    (args.out / 'FIGURE_DATA.json').write_text(json.dumps(record, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'status': 'FIGURES_CREATED', 'out': str(args.out), 'figures': 2}))


if __name__ == '__main__':
    main()
