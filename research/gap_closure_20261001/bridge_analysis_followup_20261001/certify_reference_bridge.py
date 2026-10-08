"""Exact conservative [32,128] bridge for a separately named H1 reference.

This reads the reference-agent's create-only coefficient artifact. It does not
adopt that model, invoke native quadrature, or transfer historical trajectories.
"""
from fractions import Fraction as F
from pathlib import Path
from math import isqrt
import argparse
import hashlib
import json
from bridge_mass_certificate import radial_mass, eigenvalue_lower, cap_lower, geometry_margin, poly_product, display


def integer_sqrt_upper(x):
    x = F(x)
    if x < 0:
        raise ValueError('nonnegative argument required')
    lower = isqrt(x.numerator//x.denominator)
    return F(lower if F(lower*lower) == x else lower+1)


def check_conforming(coefficients):
    for mode in coefficients:
        if mode[0][0] != 0 or sum(mode[-1]) != 0:
            raise ValueError('nonzero radial boundary trace')
        if any(sum(mode[i]) != mode[i+1][0] for i in range(len(mode)-1)):
            raise ValueError('nonconforming radial interior trace')


def gradient_diagonal_upper(mode, edges, ell):
    total = F(0)
    for coefficients, (a, b) in zip(mode, zip(edges, edges[1:])):
        h = b-a
        derivative = [k*coefficients[k] for k in range(1, len(coefficients))]
        total += sum(x/F(k+1) for k, x in enumerate(poly_product(derivative, derivative)))/h
        if not ell:
            continue
        if a == 0:
            if coefficients[0] != 0:
                raise ValueError('singular origin gradient')
            angular = sum(x/F(k+1) for k, x in enumerate(poly_product(coefficients[1:], coefficients[1:])))/h
        else:
            angular = h*sum(x/F(k+1) for k, x in enumerate(poly_product(coefficients, coefficients)))/a**2
        total += ell*(ell+1)*angular
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('create-only certificate')
    raw = json.loads(args.reference.read_text())
    edges = list(map(F, raw['edges']))
    ell = raw['l']
    coeff = [[[F(x) for x in row] for row in mode] for mode in raw['coefficients']]
    if edges[-1] != 64 or ell != [0, 0, 0, 1, 1]:
        raise ValueError('B0 reference scope mismatch')
    check_conforming(coeff)
    angle = cap_lower(F(1, 2))
    geometry_margin(64, 32, 48, F(1, 2))
    radial_lower, mass_upper, gradient_upper = [], [], []
    records = []
    for l in (0, 1):
        indices = [i for i, value in enumerate(ell) if value == l]
        tail = radial_mass(coeff, edges, indices, F(48))
        full = radial_mass(coeff, edges, indices, F(0))
        lower, pivots = eigenvalue_lower(tail)
        upper = max(sum(map(abs, row)) for row in full)
        mass_min = min(row[i]-sum(abs(x) for j, x in enumerate(row) if j != i) for i, row in enumerate(full))
        if mass_min <= 0:
            raise ValueError('same-center metric lower unresolved')
        kinetic_trace = sum(gradient_diagonal_upper(coeff[i], edges, l) for i in indices)
        gradient = kinetic_trace/mass_min
        radial_lower.append(lower); mass_upper.append(upper); gradient_upper.append(gradient)
        records.append({'l': l, 'radial_tail_gram_exact': [[str(x) for x in row] for row in tail],
            'tail_ldl_pivots_exact': list(map(str, pivots)), 'tail_lambda_lower_exact': str(lower),
            'same_center_mass_lower_exact': str(mass_min), 'same_center_mass_upper_exact': str(upper),
            'same_center_gradient_norm_squared_upper_exact': str(gradient)})
    s0 = angle*min(radial_lower)/max(mass_upper)
    kappa = max(gradient_upper)
    orbital_gradient = integer_sqrt_upper(kappa)
    # Scope: stationary target, straight projectile, 1<=v<=3 atomic units.
    # These deliberately broad rational bounds enclose the declared B0 speed.
    vmax, vmin, charges, width = F(3), F(1), F(2), F(96)
    Lt, Lp = orbital_gradient, orbital_gradient+vmax
    K = (Lt*Lt+Lp*Lp)/s0
    gradient = integer_sqrt_upper(K)
    basis_derivative = vmax*orbital_gradient+vmax*vmax/2
    connection = basis_derivative*integer_sqrt_upper(1/s0)
    rate = K/2+2*charges*gradient+connection
    integrated = width*rate/vmin
    result = {'schema': 'BASS_NAMED_REFERENCE_CONSERVATIVE_BRIDGE_V1',
        'status': 'EXACT_RATIONAL_BOUND_FOR_NAMED_REFERENCE_NOT_ARCHIVED_NATIVE_MODEL',
        'reference_coefficients_sha256': hashlib.sha256(args.reference.read_bytes()).hexdigest(),
        'reference_artifact': str(args.reference.name),
        'domain': 'z in [32,128] or z in [-128,-32], b=2, all separations R>=32',
        'model': 'exact weak Coulomb Galerkin H on the exact H1-conforming reference; exact moving-basis D',
        'required_channel_semantics': 'same radial bank on both centers; complete l=1 multiplets; fixed selected J',
        'velocity_assumption_exact': {'minimum': str(vmin), 'maximum': str(vmax)},
        'unit_charges': [1, 1], 'hbar_atomic_units': 1,
        'radial_certificates': records,
        'same_center_normalized_metric_lower_exact': str(s0),
        'same_center_normalized_metric_lower_display': display(s0),
        'unboosted_same_center_gradient_squared_upper_exact': str(kappa),
        'unboosted_same_center_gradient_squared_upper_display': display(kappa),
        'full_span_gradient_squared_upper_exact': str(K),
        'full_span_gradient_squared_upper_display': display(K),
        'constant_rho_majorant_exact': str(rate), 'constant_rho_majorant_display': display(rate),
        'integrated_majorant_per_side_exact': str(integrated),
        'integrated_majorant_per_side_display': display(integrated),
        'research_target_per_side_exact': '1/200000',
        'target_certified': integrated <= F(1, 200000),
        'reference_model_adopted': False, 'historical_state_or_temporal_gate_transferred': False,
        'new_native_calls': 0, 'new_physical_operator_queries': 0,
        'existing_physical_claim_ceiling_changed': False}
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('status', 'same_center_normalized_metric_lower_display',
        'unboosted_same_center_gradient_squared_upper_display', 'constant_rho_majorant_display',
        'integrated_majorant_per_side_display', 'target_certified')}))


if __name__ == '__main__':
    main()
