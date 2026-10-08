"""Exact radial-mass / exclusive-cap certificate. No physical operator query.

The polynomial coefficients are interpreted as their exact binary rational
values. This proves an L2 Gram statement, not H1 conformity or any native
quadrature error bound. Display decimals are non-authoritative conveniences.
"""
from fractions import Fraction as F
from decimal import Decimal, localcontext
from pathlib import Path
import argparse
import hashlib
import json


def poly_product(a, b):
    result = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i+j] += x*y
    return result


def radial_mass(coefficients, edges, indices, lower):
    """Integrate products using local coordinates, with exact partial cells."""
    n = len(indices)
    result = [[F(0) for _ in range(n)] for _ in range(n)]
    for cell in range(len(edges)-1):
        a, b = map(F, edges[cell:cell+2])
        if b <= lower:
            continue
        h = b-a
        u = max(F(0), (lower-a)/h)
        for i, ii in enumerate(indices):
            for j in range(i, n):
                jj = indices[j]
                product = poly_product(coefficients[ii][cell], coefficients[jj][cell])
                value = h*sum(c*(1-u**(k+1))/F(k+1) for k, c in enumerate(product))
                result[i][j] += value
                if i != j:
                    result[j][i] += value
    return result


def ldl_pivots(matrix):
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError('nonempty square matrix required')
    if any(matrix[i][j] != matrix[j][i] for i in range(n) for j in range(n)):
        raise ValueError('symmetric matrix required')
    l = [[F(i == j) for j in range(n)] for i in range(n)]
    d = []
    for i in range(n):
        pivot = matrix[i][i] - sum(l[i][k]**2*d[k] for k in range(i))
        if pivot <= 0:
            raise ValueError('positive definiteness not established')
        d.append(pivot)
        for j in range(i+1, n):
            l[j][i] = (matrix[j][i]-sum(l[j][k]*l[i][k]*d[k] for k in range(i)))/pivot
    return d


def eigenvalue_lower(matrix):
    pivots = ldl_pivots(matrix)
    determinant = F(1)
    for x in pivots:
        determinant *= x
    trace = sum(matrix[i][i] for i in range(len(matrix)))
    # Each of the other n-1 positive eigenvalues is at most trace.
    return determinant/trace**(len(matrix)-1), pivots


def cap_lower(cosine):
    """Lower eigenvalue bound for l=0,1 harmonics restricted to mu>=c."""
    c = F(cosine)
    if not 0 <= c < 1:
        raise ValueError('0<=cap cosine<1 required')
    trace = (2-c-c**3)/2
    determinant = (1-c)**4/16
    transverse = (2-3*c+c**3)/4
    return min(determinant/trace, transverse)


def geometry_margin(radius, minimum_separation, shell_start, cosine):
    a, rmin, shell, c = map(F, (radius, minimum_separation, shell_start, cosine))
    if not (a > 0 and rmin > 0 and 0 < shell < a and 0 <= c < 1):
        raise ValueError('invalid cap geometry')
    margin = rmin*rmin+shell*shell+2*rmin*shell*c-a*a
    if margin <= 0:
        raise ValueError('exclusive support region is not established')
    return margin


def display(x):
    with localcontext() as context:
        context.prec = 18
        return str(Decimal(x.numerator)/Decimal(x.denominator))


def main():
    import numpy as np
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('certificate output is create-only')
    meta = json.loads((args.inputs/'BASIS.json').read_text())
    with np.load(args.inputs/'BASIS.npz', allow_pickle=False) as archive:
        coefficients = [[[F(float(x)) for x in row] for row in mode] for mode in archive['coefficients']]
        edges = [F(float(x)) for x in archive['edges']]
    groups = {ell: [i for i, row in enumerate(meta['modes']) if row['l'] == ell] for ell in (0, 1)}
    if set(row['l'] for row in meta['modes']) != {0, 1} or edges[-1] != 64:
        raise ValueError('this certificate is scoped to B0 l=0,1 radius64')
    shell, cosine, minimum_r = F(48), F(1, 2), F(32)
    margin = geometry_margin(edges[-1], minimum_r, shell, cosine)
    angular = cap_lower(cosine)
    records, radial_lower, mass_upper = [], [], []
    for ell, indices in groups.items():
        tail = radial_mass(coefficients, edges, indices, shell)
        full = radial_mass(coefficients, edges, indices, F(0))
        lower, pivots = eigenvalue_lower(tail)
        ldl_pivots(full)
        upper = max(sum(map(abs, row)) for row in full)
        radial_lower.append(lower)
        mass_upper.append(upper)
        records.append({'l': ell, 'mode_indices': indices,
            'radial_tail_gram_exact': [[str(x) for x in row] for row in tail],
            'ldl_pivots_exact': [str(x) for x in pivots],
            'lambda_lower_exact': str(lower), 'lambda_lower_display': display(lower),
            'full_mass_norm_upper_exact': str(upper)})
    raw_lower = angular*min(radial_lower)
    normalized_lower = raw_lower/max(mass_upper)
    result = {'schema': 'BASS_EXCLUSIVE_CAP_L2_METRIC_CERTIFICATE_V1',
        'status': 'EXACT_RATIONAL_CONTINUUM_L2_GRAM_CERTIFIED',
        'scope': 'LITERAL_ARCHIVED_POLYNOMIAL_L2_SPAN_NOT_NATIVE_QUADRATURE_OR_H1_REFERENCE',
        'basis_identity': meta['identity'], 'separation_domain': 'all R>=32 a0; any orientation',
        'hypotheses': ['both centers use the five recorded radial modes',
            'l=1 includes all m=-1,0,1', 'center ETF factors have unit modulus',
            'Gram entries mean exact physical L2 inner products'],
        'radius_exact': '64', 'shell_start_exact': str(shell), 'cap_cosine_exact': str(cosine),
        'geometry_margin_exact': str(margin), 'angular_lower_exact': str(angular),
        'radial_blocks': records,
        'full_18_channel_raw_metric_lower_exact': str(raw_lower),
        'full_18_channel_raw_metric_lower_display': display(raw_lower),
        'same_center_normalized_metric_lower_exact': str(normalized_lower),
        'same_center_normalized_metric_lower_display': display(normalized_lower),
        'input_pins': {n: {'sha256': hashlib.sha256((args.inputs/n).read_bytes()).hexdigest(),
            'bytes': (args.inputs/n).stat().st_size} for n in ('BASIS.json', 'BASIS.npz')},
        'new_native_calls': 0, 'new_physical_operator_queries': 0,
        'physical_rate_majorant_certified': False, 'tail_probability_bound_certified': False}
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('status', 'angular_lower_exact',
        'geometry_margin_exact', 'full_18_channel_raw_metric_lower_display',
        'same_center_normalized_metric_lower_display')}))


if __name__ == '__main__':
    main()
