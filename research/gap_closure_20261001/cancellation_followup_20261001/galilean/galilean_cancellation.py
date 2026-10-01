"""Small exact rational algebra for the weak Galilean cancellation theorem.

No physical operators, quadrature, native libraries, or propagation are called.
The matrix helper is a real-rational demonstrator; the theorem is complex and
arbitrary-dimensional. These tiny exact operations are not an HPC hot path.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json


def rational(x):
    if isinstance(x, float):
        raise TypeError('exact rational input required')
    return F(x)


def weak_boost_difference(va, vb):
    """Coefficients of Hkin-iD minus the unboosted column weak kinetic form.

Keys name a'*b', a'*b, a*b', a*b; values are (real,imaginary) rationals.
The common exp(i(vb-va)x) factor is omitted.
"""
    va, vb = map(rational, (va, vb))
    h = {'dadb': (F(1, 2), F(0)), 'dab': (F(0), vb/2),
         'adb': (F(0), -va/2), 'ab': (va*vb/2, F(0))}
    minus_i_d = {'dadb': (F(0), F(0)), 'dab': (F(0), F(0)),
                 'adb': (F(0), vb), 'ab': (-vb*vb/2, F(0))}
    column_form = {'dadb': (F(1, 2), F(0)), 'dab': (F(0), F(0)),
                   'adb': (F(0), (vb-va)/2), 'ab': (F(0), F(0))}
    return {k: tuple(h[k][j]+minus_i_d[k][j]-column_form[k][j] for j in range(2)) for k in h}


def weak_boundary_term(va, vb):
    """Coefficients of (i vb/2) d_x[exp(i(vb-va)x) conj(a)b]."""
    va, vb = map(rational, (va, vb))
    return {'dadb': (F(0), F(0)), 'dab': (F(0), vb/2),
        'adb': (F(0), vb/2), 'ab': (-vb*(vb-va)/2, F(0))}


def matmul(a, b):
    if not a or not b or any(len(row) != len(b) for row in a):
        raise ValueError('incompatible matrix dimensions')
    return [[sum(rational(a[i][k])*rational(b[k][j]) for k in range(len(b)))
        for j in range(len(b[0]))] for i in range(len(a))]


def matrix_add(a, b):
    if len(a) != len(b) or any(len(x) != len(y) for x, y in zip(a, b)):
        raise ValueError('matrix shape mismatch')
    return [[rational(x)+rational(y) for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def matrix_scale(a, factor):
    factor = rational(factor)
    return [[factor*rational(x) for x in row] for row in a]


def inverse(a):
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError('nonempty square matrix required')
    work = [[rational(x) for x in row]+[F(i == j) for j in range(n)] for i, row in enumerate(a)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if work[i][k]), None)
        if pivot is None:
            raise ValueError('singular selected Gram')
        work[k], work[pivot] = work[pivot], work[k]
        diagonal = work[k][k]
        work[k] = [x/diagonal for x in work[k]]
        for i in range(n):
            if i == k:
                continue
            factor = work[i][k]
            work[i] = [x-factor*y for x, y in zip(work[i], work[k])]
    return [row[n:] for row in work]


def schur_numerator(G, B, Kss, Kcs):
    """Return Kcs-B G^-1 Kss; no whitened norm or SPD certificate is inferred."""
    return matrix_add(Kcs, matrix_scale(matmul(matmul(B, inverse(G)), Kss), -1))


def coarse_rate_bound(L, Lz, vmax, isolated_norm, s0, inverse_sqrt_upper):
    """Unit-charge named reference bound; exact 96/v_min with v_min=2."""
    L, Lz, vmax, M, s0, inv = map(rational, (L, Lz, vmax, isolated_norm, s0, inverse_sqrt_upper))
    if min(L, Lz, vmax, M) < 0 or s0 <= 0 or inv <= 0 or inv*inv*s0 < 1:
        raise ValueError('invalid norm or metric inverse bound')
    weak = L*L/2+vmax*Lz/2+2*L+M
    potential = 2*L
    rate = inv*weak+potential
    return {'weak_target_residual_upper': weak, 'weak_metric_weighted_upper': inv*weak,
        'potential_upper_without_metric_penalty': potential, 'rho_upper': rate,
        'bridge_upper': 48*rate, 'probability_change_upper': min(F(1), 48*rate)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--research-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('create-only result')
    ref_path = args.research_root/'reference_certificate_followup_20261001/actual_certificate/REFERENCE_CERTIFICATE.json'
    grad_path = args.research_root/'bridge_analysis_followup_20261001/NAMED_REFERENCE_BRIDGE_CERTIFICATE.json'
    etf_path = args.research_root/'bridge_analysis_followup_20261001/ETF_METRIC_CERTIFICATE.json'
    reference_file = args.research_root/'reference_certificate_followup_20261001/actual_certificate/EXACT_REPAIRED_REFERENCE.json'
    ref, grad, etf = [json.loads(p.read_text()) for p in (ref_path, grad_path, etf_path)]
    reference_bytes = reference_file.read_bytes()
    reference_file_sha = hashlib.sha256(reference_bytes).hexdigest()
    reference_canonical_sha = hashlib.sha256(json.dumps(json.loads(reference_bytes), sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    # The old reference certificate pins canonical JSON; old bridge and ETF
    # certificates pin the pretty JSON file bytes under the same field name.
    if (ref['reference_coefficients_sha256'] != reference_canonical_sha
            or any(x['reference_coefficients_sha256'] != reference_file_sha for x in (grad, etf))):
        raise ValueError('reference coefficient identity mismatch')
    kappa = max(F(x['same_center_gradient_norm_squared_upper_exact']) for x in grad['radial_certificates'])
    L, Lz, vmax, M, s0, inv = F(6, 5), F(67, 100), F(3), F(51, 100), F(33, 100), F(7, 4)
    if kappa > L*L or F(etf['directional_derivative_squared_upper_exact']) > Lz*Lz:
        raise ValueError('gradient constants not certified')
    if F(etf['full_center_normalized_metric_lower_exact']) < s0:
        raise ValueError('metric constant not certified')
    speed = F(etf['speed_binding']['frozen_source_binary_speed_exact'])
    if not 2 <= speed <= vmax:
        raise ValueError('speed outside scope')
    mass_min = F(ref['reference_gram_spectral_bounds'][0]['rational'])
    H = ref['reference_isolated_H_interval']
    H_upper = max(sum(max(abs(F(x['lower'])), abs(F(x['upper']))) for x in row) for row in H)
    isolated_upper = H_upper/mass_min
    if mass_min <= 0 or isolated_upper > M:
        raise ValueError('isolated reference operator norm is not bounded by 51/100')
    bound = coarse_rate_bound(L, Lz, vmax, M, s0, inv)
    result = {'schema': 'BASS_R4T_WEAK_GALILEAN_CANCELLED_BRIDGE_V1',
        'status': 'EXACT_NAMED_REFERENCE_RAW_RATE_BOUND_TARGET_FAIL',
        'reference_coefficients_sha256': reference_canonical_sha,
        'reference_coefficients_canonical_sha256': reference_canonical_sha,
        'reference_artifact_file_sha256': reference_file_sha,
        'scope': 'same named exact weak H1 reference, invariant isolated negative projectile selector, unit charges, v in [2,3]',
        'support_of_weak_residual_rows': 'target rows only; all same-projectile test rows annihilate exact Galerkin residual',
        'bounds_exact': {k: str(v) for k, v in bound.items()},
        'input_comparisons_exact': {'unboosted_gradient_squared_upper': str(kappa), 'L': str(L), 'Lz': str(Lz),
            'vmax': str(vmax), 'isolated_operator_norm_upper_from_saved_intervals': str(isolated_upper),
            'isolated_operator_norm_relaxed_upper': str(M), 'metric_lower': str(s0), 'inverse_sqrt_metric_upper': str(inv)},
        'domain_per_side': '[32,128] and [-128,-32]', 'target_per_side_exact': '1/200000',
        'target_certified': bound['bridge_upper'] <= F(1, 200000),
        'comparison': {'previous_raw_integrated_rate_upper': '55408/11', 'new_raw_integrated_rate_upper': str(bound['bridge_upper']),
            'both_trivially_capped_probability_bounds': '1',
            'interpretation': 'raw integrated-rate majorant improves; certified probability bound remains 1 and target remains open'},
        'source_certificate_pins': {str(p.relative_to(args.research_root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ref_path, grad_path, etf_path, reference_file)},
        'new_native_calls': 0, 'new_physical_operator_queries': 0, 'new_physical_propagations': 0,
        'reference_model_adopted': False, 'global_L2_weak_residual_norm_claimed': False,
        'existing_physical_claim_ceilings_changed': False}
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'bounds_exact': result['bounds_exact'], 'target_certified': result['target_certified']}))


if __name__ == '__main__':
    main()
