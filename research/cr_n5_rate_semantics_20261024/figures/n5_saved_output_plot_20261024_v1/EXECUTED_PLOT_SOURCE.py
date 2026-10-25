"""Render saved outputs only; no provider evaluation or scientific integration."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start = time.process_time()
    unit = Path(__file__).resolve().parents[1]
    run = unit / 'implementation/runs/n5_ce_envelope_primary_20261024t031906828z_v1'
    names = ['CE_PATH_ENDPOINT_SAMPLES.json', 'CE_FIRST_EVENT_ESTIMATES.json', 'CE_ENVELOPES.json']
    values = {name: json.loads((run / name).read_text()) for name in names}
    pins = [{'path': str((run / name).relative_to(unit)), 'sha256': hashlib.sha256((run / name).read_bytes()).hexdigest()} for name in names]
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.titleweight': 'bold', 'savefig.facecolor': 'white'})
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(11.5, 8.8), gridspec_kw={'height_ratios': [1.1, 1]})
    fig.subplots_adjust(top=.84, bottom=.12, left=.09, right=.97, hspace=.43)
    fig.suptitle('Hydrogen CE before EE first entry', x=.09, y=.965, ha='left', fontsize=21, fontweight='bold')
    fig.text(.09, .915, r'Conditional frozen bath: $T=10{,}000$ K, $n_{\mathrm{H1},1s}=0.9\ \mathrm{cm}^{-3}$, reflecting boundary $R=80\theta$', fontsize=12)
    samples = values[names[0]][0]['samples']
    energy = [row['energy_eV'] for row in samples]
    ax.axvspan(0, 10, color='#e5e7eb', alpha=.9, label='Initial source: 0 < W < 10 eV')
    for channel, color, label in [('2S', '#bc650c', '2s'), ('2P', '#008f85', '2p')]:
        ax.plot(energy, [1e8 * row['channel_hazards_per_proper_s'][channel] for row in samples], color=color, lw=1.6, label=label)
    ax.plot(energy, [1e8 * row['h_total_per_proper_s'] for row in samples], color='#17365d', lw=2, label='2s + 2p')
    ax.axvline(10.20435, color='#6b7280', ls=':', lw=1)
    ax.text(11.3, 2.95, 'Source CE threshold\n10.20435 eV', fontsize=10, color='#4b5563')
    env = next(row for row in values[names[2]] if row['selection'] == '2S+2P' and row['chi'] == 1.5)
    ax.scatter([env['maximizing_energy_eV']], [1e8 * env['hmax_per_proper_s']], color='#17365d', zorder=6)
    ax.annotate(r'$h_{\max}=2.919\times10^{-8}\ \mathrm{s}^{-1}$',
                xy=(env['maximizing_energy_eV'], 1e8 * env['hmax_per_proper_s']),
                xytext=(43, 2.15), arrowprops={'arrowstyle': '->', 'color': '#17365d'}, color='#17365d')
    ax.set(xlim=(0, 71), ylim=(0, 3.45), xlabel='Tagged electron energy W (eV)', ylabel=r'CE hazard ($10^{-8}$ proper s$^{-1}$)')
    ax.set_title('A. The reachable EE path extends beyond the initial source', loc='left', fontsize=12, pad=13)
    ax.grid(axis='y', alpha=.17)
    ax.legend(loc='upper center', bbox_to_anchor=(.53, 1.0), ncol=4, frameon=False, fontsize=9)
    rows = [row for row in values[names[1]] if row['channel_selection'] == '2S+2P']
    positions = list(range(len(rows)))
    bx.bar([i-.18 for i in positions], [100*r['active_first_event_upper_estimate'] for r in rows], width=.34, color='#17365d', label='Active population')
    bx.bar([i+.18 for i in positions], [100*r['whole_selected_first_event_upper_estimate'] for r in rows], width=.34, color='#008f85', label='Whole selected source')
    bx.axhline(1.0, color='#9ca3af', linestyle='--', lw=1)
    bx.text(5.58, 1.015, '1% target', ha='right', fontsize=9, color='#6b7280')
    for i, row in enumerate(rows):
        for dx, key in [(-.18, 'active_first_event_upper_estimate'), (.18, 'whole_selected_first_event_upper_estimate')]:
            val = 100 * row[key]
            bx.text(i+dx, val+.022, f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    bx.set_xticks(positions, [f"z={r['redshift']}\n" + r'$\chi$=' + f"{r['chi']:g}" for r in rows])
    bx.set(ylim=(0, 1.12), ylabel='Conditional upper estimate (%)')
    bx.set_title('B. CE-only first-event estimates using saved R80 first-entry means', loc='left', fontsize=12, pad=13)
    bx.grid(axis='y', alpha=.17)
    bx.set_axisbelow(True)
    bx.legend(loc='upper left', ncol=2, frameon=False, fontsize=9)
    fig.text(.09, .045, 'Saved C23D MFPTs + PHYS83 W-PL source. Lines join stored union endpoints.\nGround-state closure is explicit; missing channels and physical-model error certificates remain null.', fontsize=10, color='#4b5563')
    for suffix in ['png', 'svg']:
        path = args.output / ('N5_CE_FIRST_ENTRY.' + suffix)
        if path.exists():
            raise FileExistsError(path)
        fig.savefig(path, dpi=190)
    plt.close(fig)
    result = {'status': 'PASS', 'source_pins': pins, 'science_recomputed': False,
              'cpu_s': time.process_time()-start, 'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'EXECUTION': 'PLOT_FROM_SAVED_OUTPUT_ONLY', 'PUBLICATION': 'PENDING',
              'BACKUP': 'PENDING', 'DAG': 'NO_GATE_CHANGE'}
    with (args.output/'PLOT_RESULT.json').open('x') as out:
        json.dump(result, out, indent=2);out.write('\n')


if __name__ == '__main__':
    main()
