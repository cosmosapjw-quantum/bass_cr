#!/usr/bin/env python3
"""Small exact photon/thermal IVP for C21G tolerance diagnostics, not native.

tau'=k, N=A exp(-tau), P'=kN, w'=QkN-mu*w, L'=mu*w.
Number N+P=A and energy QN+w+L=QA+w0 hold continuously.
Time here is a dimensionless manufactured coordinate, not the FLRW fixture.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import math
from pathlib import Path
import time
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from campaign_contract import TIERS, write_new_json

AMOUNT = .032
W0 = 1.4
HEAT = 6.
MU = .3

def exact(kappa, end=1.):
    tau = kappa * end
    log_n = math.log(AMOUNT) - tau
    n = math.exp(log_n)
    d = kappa - MU
    exposure = end if d == 0 else -math.expm1(-d * end) / d
    w = math.exp(-MU * end) * (W0 + HEAT*kappa*AMOUNT*exposure)
    photo = AMOUNT * (-math.expm1(-tau))
    loss = math.fsum((W0, HEAT*photo, -w))
    return {'tau': tau, 'log_survivor': log_n, 'photon_H': n,
            'thermal_eV_H': w, 'photo_H': photo, 'loss_eV_H': loss,
            'formula_branch': 'EXACT_RESONANT_LIMIT' if d == 0 else 'EXPONENTIAL_CONVOLUTION'}

def integrate(kappa, tier):
    calls = 0
    def rhs(t, state):
        nonlocal calls
        calls += 1
        if calls > 50000:
            raise RuntimeError('ANALYTIC_BENCH_RHS_BUDGET')
        n = math.exp(math.log(AMOUNT) - state[0])
        absorption = kappa * n
        return (kappa, HEAT*absorption-MU*state[1], absorption, MU*state[1])
    scales = np.array((1., W0, 1., W0+HEAT*AMOUNT))
    start = time.monotonic()
    sol = solve_ivp(rhs, (0., 1.), (0., W0, 0., 0.), method='Radau',
                    rtol=tier['rtol'], atol=tier['atol_scale']*scales,
                    max_step=1./tier['max_step_divisor'])
    if not sol.success or not np.isfinite(sol.y).all():
        raise RuntimeError('ANALYTIC_BENCH_RADAU_FAILED ' + sol.message)
    state = sol.y[:, -1]; target = exact(kappa)
    log_n = math.log(AMOUNT) - state[0]
    n = math.exp(log_n)
    errors = {'optical_depth': float(state[0]-target['tau']),
              'log_survivor': float(target['tau']-state[0]),
              'photon_absolute_H': abs(n-target['photon_H']),
              'thermal_eV_H': float(state[1]-target['thermal_eV_H']),
              'photo_H': float(state[2]-target['photo_H']),
              'loss_eV_H': float(state[3]-target['loss_eV_H'])}
    budget_number = 64*np.finfo(float).eps*AMOUNT
    budget_energy = 64*np.finfo(float).eps*(W0+HEAT*AMOUNT)
    number = math.fsum((n, float(state[2]), -AMOUNT))
    energy = math.fsum((HEAT*n, float(state[1]), float(state[3]), -HEAT*AMOUNT, -W0))
    # The known analytic formula is evaluated in binary64. Differences near
    # roundoff do not measure a certified error relative to exact real values.
    checks = {'number_closure': abs(number) <= max(budget_number, 1e-11),
              'energy_closure': abs(energy) <= max(budget_energy, 1e-10),
              'thermal_accuracy': abs(errors['thermal_eV_H']) <= 2e-10,
              'log_accuracy': abs(errors['log_survivor']) <= 2e-9}
    return {'kappa': kappa, 'mu': MU, 'tier': tier, 'exact': target,
            'actual': {'optical_depth': float(state[0]), 'log_survivor': float(log_n),
                       'photon_H': n, 'thermal_eV_H': float(state[1]),
                       'photo_H': float(state[2]), 'loss_eV_H': float(state[3])},
            'difference_from_binary64_analytic_evaluation': errors,
            'analytic_evaluation_precision': 'binary64; a difference near machine precision is not a certified real-arithmetic error bound',
            'number_defect_H': number, 'energy_defect_eV_H': energy,
            'underflowed_positive_cohort': n == 0, 'finite_log_survivor_retained': math.isfinite(log_n),
            'accepted_steps': len(sol.t)-1, 'nfev': sol.nfev, 'njev': sol.njev, 'nlu': sol.nlu,
            'actual_rhs_evaluations': calls, 'wall_s': time.monotonic()-start,
            'grid_sha256': hashlib.sha256(np.ascontiguousarray(sol.t, dtype='<f8').tobytes()).hexdigest(),
            'test_budgets': {'number_H': max(budget_number, 1e-11), 'energy_eV_H': max(budget_energy, 1e-10),
                             'thermal_eV_H': 2e-10, 'log_survivor': 2e-9},
            'checks': checks, 'status': 'PASS_EXACT_MANUFACTURED_CHECKS' if all(checks.values()) else 'FAILED',
            'native_science': False}

def make_plot(rows, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.2), layout='constrained')
    for kappa, marker in ((80., 'o'), (800., 's')):
        selected = [r for r in rows if r['kappa'] == kappa and r['tier']['name'] != 'L3M']
        x = [r['tier']['rtol'] for r in selected]
        errors = [abs(r['difference_from_binary64_analytic_evaluation']['thermal_eV_H']) for r in selected]
        nonzero = [(a, b) for a, b in zip(x, errors) if b > 0]
        axes[0].loglog([v[0] for v in nonzero], [v[1] for v in nonzero], marker=marker, label=f'kappa={kappa:g}')
    axes[0].invert_xaxis(); axes[0].set_xlabel('Requested local relative tolerance')
    axes[0].set_ylabel('Thermal difference vs\nanalytic solution [eV/H]')
    axes[0].set_title('(a) Exact manufactured IVP', fontsize=10)
    axes[0].legend(fontsize=8); axes[0].grid(alpha=.2, which='both')
    axes[0].annotate('Coincident finest points', xy=(2e-13, 4.440892098500626e-16),
                     xytext=(0.40, 0.25), textcoords='axes fraction', fontsize=7,
                     arrowprops={'arrowstyle': '->', 'lw': .7})
    delta = np.linspace(-.24, .24, 600)
    coarse, fine = 1., .25
    order = np.log2(np.abs((coarse-delta)/(fine-delta)))
    axes[1].plot(delta, order, color='#7b3294')
    axes[1].axhline(2, color='black', lw=.8, ls='--')
    axes[1].axvline(0, color='grey', lw=.8)
    axes[1].set_xlabel('Reference shift / coarse true error')
    axes[1].set_ylabel('Inferred two-level order')
    axes[1].set_title('(b) Synthetic reference sensitivity', fontsize=10)
    axes[1].grid(alpha=.2)
    fig.savefig(output / 'analytic_reference_diagnostics.png', dpi=300)
    fig.savefig(output / 'analytic_reference_diagnostics.svg')
    plt.close(fig)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    start = datetime.now(timezone.utc).isoformat(); clock = time.monotonic()
    rows = [integrate(kappa, dict(tier)) for kappa in (80., 800.) for tier in TIERS]
    rows.append(integrate(MU, dict(TIERS[2])))
    meshes = {str(kappa): 'MESH_CAP_INACTIVE' if next(r for r in rows if r['kappa']==kappa and r['tier']['name']=='L3')['grid_sha256'] == next(r for r in rows if r['kappa']==kappa and r['tier']['name']=='L3M')['grid_sha256'] else 'ACCEPTED_GRID_CHANGED' for kappa in (80.,800.)}
    report = {'schema': 'C21G_EXACT_MANUFACTURED_REFERENCE_CHECK_V1',
              'status': 'PASS' if all(r['status']=='PASS_EXACT_MANUFACTURED_CHECKS' for r in rows) else 'FAILED',
              'started_at_utc': start, 'wall_s': time.monotonic()-clock,
              'runtime': {'numpy': np.__version__, 'scipy': scipy.__version__},
              'native_science': False, 'C21F_reexecution': False,
              'model': 'tau prime=k; N=A exp(-tau); photo prime=kN; thermal prime=QkN-mu*w; escape prime=mu*w. Dimensionless manufactured time.',
              'scope': 'Exact numerical workbench; no H/He absorber feedback, cosmology, source births or native microphysics.',
              'cases': rows, 'mesh_cap_checks': meshes,
              'figure': {'width_mm': 181.864, 'layout': 'two columns', 'zero_error_floor': False,
                         'panel_b': 'Synthetic true errors coarse=1,fine=0.25; shifted reference changes their apparent order.'}}
    write_new_json(args.out / 'ANALYTIC_REFERENCE_CHECK.json', report)
    make_plot(rows, args.out)
    print(__import__('json').dumps({'status': report['status'], 'cases': len(rows), 'wall_s': report['wall_s'],
                                  'native_science': False, 'mesh_cap_checks': meshes}))
    if report['status'] != 'PASS':
        raise SystemExit(1)

if __name__ == '__main__':
    main()
