"""Focused static checks for the new conditional atomic network; no ODE runs."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import time

import numpy as np

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from atomic_network import AtomicNetwork21, SOURCE_FILES


# Literal author table rows, independent of the Provider's parsed structures.
# PH2: E0,sigma0,ya,P,yw,y0,y1; selected atomic tables' units eV/Mb.
PHOTO = (
    (0.4298, 54750., 32.88, 2.963, 0., 0., 0.),
    (13.61, 949.2, 1.469, 3.188, 2.039, .4434, 2.136),
    (1.720, 13690., 32.88, 2.963, 0., 0., 0.),
    (3.107, 62.45, 15.01, 4.895, 0., 0., 0.),
    (20.06, 320.1, 7.391, 2.916, 0., 0., 0.),
    (3.871, 6083., 32.88, 2.963, 0., 0., 0.),
)
RR = (
    (7.982e-11, .7480, 3.148, 7.036e5),
    (9.356e-10, .7892, .04266, 4.677e6),
    (1.891e-10, .7524, 9.370, 2.774e6),
    (1.036e-11, .3880, 107.7, 1.177e7),
    (1.112e-10, .6926, 24.37, 8.323e6),
    (3.039e-10, .7539, 18.71, 6.209e6),
)
THRESHOLDS = (13.6, 24.59, 54.42, 5.392, 75.64, 122.5)


def literal_sigma(channel, energy):
    if energy < THRESHOLDS[channel]:
        return 0.
    if channel == 3 and energy >= 64.39:
        # Author partial_table / PH1 LiI 2s: threshold,E0,sigma0,ya,P,yw.
        e0, s0, ya, p, yw = 3.466, 47.74, 20.35, 4.423, 0.
        v = energy / e0
        return s0 * ((v - 1.) ** 2 + yw * yw) * v ** (p / 2. - 5.5) * (1. + math.sqrt(v / ya)) ** (-p)
    e0, s0, ya, p, yw, y0, y1 = PHOTO[channel]
    x = energy / e0 - y0
    v = math.sqrt(x * x + y1 * y1)
    return s0 * ((x - 1.) ** 2 + yw * yw) * v ** (p / 2. - 5.5) * (1. + math.sqrt(v / ya)) ** (-p)


def literal_rr(channel, temperature):
    a, b, t0, t1 = RR[channel]
    x = math.sqrt(temperature / t0)
    return a / (x * (1. + x) ** (1. - b) * (1. + math.sqrt(temperature / t1)) ** (1. + b))


def run():
    began = time.perf_counter()
    n = AtomicNetwork21(electronic_isotope_equality=True)
    findings = []
    try:
        AtomicNetwork21()
    except ValueError:
        pass
    else:
        raise AssertionError("isotope equality was silently enabled")
    assert len(n.state_labels) == 21 and len(set(n.state_labels)) == 21
    assert n.state_labels[16] == "Li7_3" and n.state_labels[20] == "Li6_3"
    for a in (n.scales, n.A, n.q, n.sigma_cm2, n._photo_basis, n._rr_basis):
        assert not a.flags.writeable
        try:
            a.setflags(write=True)
        except ValueError:
            pass
        else:
            raise AssertionError("immutable backing can be changed")
    for name, sha in SOURCE_FILES.items():
        assert hashlib.sha256((BASE / 'vendor/atomic' / name).read_bytes()).hexdigest() == sha
    findings.append({"group": "registry_explicit_approximation_and_source_identity", "status": "PASS", "vendor_files": 7})

    sigma_reference = np.array([[literal_sigma(j, e) * 1e-18 for e in n.energies_eV] for j in range(6)])
    np.testing.assert_allclose(n.sigma_cm2, sigma_reference, rtol=2e-15, atol=0.)
    max_rr_rel = 0.
    for t in (4., 100., 1e4, 1e5):
        actual = np.array([n.provider.rr(name, t) for name in n.channel_names])
        reference = np.array([literal_rr(j, t) for j in range(6)])
        np.testing.assert_allclose(actual, reference, rtol=2e-15, atol=0.)
        max_rr_rel = max(max_rr_rel, float(np.max(np.abs(actual / reference - 1.))))
    # Both actual branch sides are checked; the test does not add the core row.
    assert literal_sigma(3, 100.) != 0 and literal_sigma(3, 150.) != 0
    assert n.provider.rows['HeI']['RR_table_label'] == 'HeI b'
    findings.append({"group": "literal_primary_coefficients", "status": "PASS", "photo_values": 36,
                     "RR_values": 24, "RR_max_relative_difference": max_rr_rel, "tolerance_relative": 2e-15})

    x = n.initial_state()
    y = n.physical_abundances(x)
    for name, indices in n.blocks.items():
        np.testing.assert_allclose(sum(y[list(indices)]), n.initial_nucleus_totals[name], rtol=2e-16, atol=0.)
    expected_e = 2e-4 * (1. + 2.5e-5) + 5e-10 + 1e-14
    np.testing.assert_allclose(n.electrons_per_H(x), expected_e, rtol=2e-16, atol=0.)
    np.testing.assert_array_equal(y, x * n.scales)
    assert x[n.blocks['T'][0]] == x[n.blocks['n'][0]] == 0.
    np.testing.assert_allclose(n.beta_rates_s['n_to_H1_1'], 1. / 877.75, rtol=0., atol=0.)
    np.testing.assert_allclose(n.beta_rates_s['T_to_He3_q_plus_1'], math.log(2.) / (12.33 * 31557600.), rtol=0., atol=0.)
    # Nonzero trial beta parents test the correct daughter isotope/charge, even
    # though the declared science initial conditions have exactly zero parents.
    for source, daughter, rate in n.beta_edges:
        assert n.A[source] == n.A[daughter]
        assert n.q[daughter] - n.q[source] == 1
        assert n._beta[daughter, source] == rate
    np.testing.assert_allclose(n.A @ n._beta, 0., rtol=0., atol=1e-24)
    np.testing.assert_allclose(np.ones(21) @ n._beta, 0., rtol=0., atol=0.)
    findings.append({"group": "initial_abundances_electrons_and_beta_mapping", "status": "PASS",
                     "initial_electrons_per_H": float(n.electrons_per_H(x)), "beta_edges": 3})

    temps, largest_energy_rel = [], 0.
    for z in (20., 14., 13.4, 8., 3.2, 2.):
        d = n.rate_data(z)
        temps.append(d.temperature_K)
        assert 3. < d.temperature_K < 1e9
        assert np.all(d.photo_rates_s >= 0.) and np.all(d.rr_cm3_s > 0.)
        assert np.all(d.diagnostic['primary_photoelectron_J_per_target_s'] >= 0.)
        absorbed = d.diagnostic['absorbed_energy_J_per_target_s']
        residual = d.diagnostic['energy_partition_residual_J_per_target_s']
        nonzero = absorbed > 0
        if np.any(nonzero):
            largest_energy_rel = max(largest_energy_rel, float(np.max(np.abs(residual[nonzero]) / absorbed[nonzero])))
        np.testing.assert_allclose(residual, 0., atol=max(absorbed) * 6e-16, rtol=0.)
        g = n.frozen_electron_generator(z, x, 1e-17, 1e-4)
        offdiag = g.copy()
        np.fill_diagonal(offdiag, 0.)
        assert np.min(offdiag) >= 0.
        # Relative roundoff budgets are needed because n beta/H ~1e14.
        np.testing.assert_allclose(np.ones(21) @ g, 0., rtol=0., atol=1e-10)
        np.testing.assert_allclose(n.A @ g, 0., rtol=0., atol=1e-9)
        # Atomic transitions preserve EACH isotope; beta preserves n+H and T+He3.
        p, r = n._operators(z)
        for indices in n.blocks.values():
            selector = np.zeros(21); selector[list(indices)] = 1.
            np.testing.assert_allclose(selector @ p, 0., rtol=0., atol=1e-28)
            np.testing.assert_allclose(selector @ r, 0., rtol=0., atol=1e-25)
        # Electron closure is independent event accounting, not another ODE.
        ne = 1e-4 * (n.q @ y)
        events = sum(d.photo_rates_s[c] * y[lo] - d.rr_cm3_s[c] * ne * y[hi] for lo, hi, c in n.edges)
        events += sum(rate * y[src] for src, _, rate in n.beta_edges)
        derivative = n.rhs(z, x, 1e-17, 1e-4)
        np.testing.assert_allclose(n.q @ (derivative * n.scales) * 1e-17, events, rtol=5e-15, atol=1e-35)
    for z in (1.9, 20.1, float('nan')):
        try: n.rate_data(z)
        except ValueError: pass
        else: raise AssertionError('domain guard failed')
    # LiII -> LiIII -> LiIV is a two-positive-edge path at z2, for BOTH isotopes.
    d = n.rate_data(2.)
    for name in ('Li7', 'Li6'):
        lo, mid, high = n.blocks[name][1:]
        g = n.frozen_electron_generator(2., x, 1., 1e-4)
        assert g[mid, lo] > 0. and g[high, mid] > 0.
        assert g[high, mid] * g[mid, lo] > 0.
    findings.append({"group": "positive_generator_invariants_domains_and_LiIV_reachability", "status": "PASS",
                     "redshifts": 6, "energy_partition_max_relative_residual": largest_energy_rel,
                     "LiIV_scope": "positive2-edgegraph_path_and_nonzero_second_Taylor_coefficient;ODE0"})

    # Complex-step differentiation is independent of the analytic rank-one
    # ne feedback formula and retains small isotope scales without subtraction.
    trial = np.linspace(.02, .7, 21)
    trial[n.blocks['n'][0]] = 0.
    trial[n.blocks['T'][0]] = .3
    trial[0] = -1e-30  # A finite signed Newton trial is accepted, never clipped.
    h = 1e-30
    j = n.jacobian(7., trial, 2e-17, 8e-5)
    numerical = np.empty((21, 21))
    for k in range(21):
        xc = trial.astype(complex); xc[k] += 1j * h
        numerical[:, k] = np.imag(n.rhs(7., xc, 2e-17, 8e-5)) / h
    difference = np.abs(j - numerical)
    scale = np.maximum(np.abs(j), np.abs(numerical))
    relative = np.divide(difference, scale, out=np.zeros_like(scale), where=scale > 0)
    assert np.max(relative) < 2e-13
    f0 = n.rhs(7., trial, 2e-17, 8e-5)
    saved = f0.copy()
    f1 = n.rhs(8., trial, 2e-17, 8e-5)
    assert not np.shares_memory(f0, f1)
    np.testing.assert_array_equal(saved, f0)
    findings.append({"group": "analytic_jacobian_and_signed_fresh_rhs", "status": "PASS",
                     "jacobian_entries": 441, "max_entrywise_relative_difference": float(np.max(relative)),
                     "max_absolute_difference": float(np.max(difference)), "method": "complex_step_h=1e-30",
                     "complex_step_scope": "fixedH,nHref,T(z),UV(z);all21population_derivatives"})
    return {
        "schema": "C21O_ATOMIC_FOCUSED_STATIC_v1", "status": "PASS_SCOPED",
        "groups": findings, "ODE_runs": 0, "benchmarks": 0,
        "runtime_seconds": time.perf_counter() - began,
        "source_sha256": {p.relative_to(BASE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in (BASE / 'atomic_network.py', BASE / 'ATOMIC_SOURCE_MANIFEST.json', Path(__file__))},
        "scope": "static coefficients, finitegenerator, conservation,charge,domain andlocalJacobian checks;not cosmological integration validation",
        "global_error_bound": None,
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--receipt', type=Path)
    args = p.parse_args()
    result = run()
    body = json.dumps(result, indent=2) + '\n'
    if args.receipt:
        with args.receipt.open('x') as f: f.write(body)
    print(body)
