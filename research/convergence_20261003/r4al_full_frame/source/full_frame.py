"""H1 full-frame certificates for the pinned finite s+p overlap.

No two-centre integral, propagation, fit, or numerical differentiation occurs
here. Bounds concern the exact finite candidate, not physical basis error.
All certificate arithmetic is integer/Fraction; float use is confined to
reading an explicitly stored binary64 datum in the input adapter.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import isqrt
from typing import Iterable


class ContractError(ValueError):
    pass


def rat(x) -> F:
    if isinstance(x, bool) or not isinstance(x, (int, str, F)):
        raise ContractError('exact int/string/Fraction required')
    try:
        return F(x)
    except (ValueError, ZeroDivisionError) as exc:
        raise ContractError('invalid rational') from exc


def nonnegative(x) -> F:
    y = rat(x)
    if y < 0:
        raise ContractError('negative bound')
    return y


def sqrt_bounds(x, bits: int = 256) -> tuple[F, F]:
    x = nonnegative(x)
    if isinstance(bits, bool) or not isinstance(bits, int) or not 32 <= bits <= 1024:
        raise ContractError('square-root precision outside contract')
    scale = 1 << bits
    k = isqrt((x.numerator * scale * scale) // x.denominator)
    lo = F(k, scale)
    hi = lo if lo * lo == x else F(k + 1, scale)
    return lo, hi


def gram_tube(glo, ghi, anchor_cross_norm, derivative_norm, halfwidth):
    lo, hi = rat(glo), rat(ghi)
    c, d, h = map(nonnegative, (anchor_cross_norm, derivative_norm, halfwidth))
    if lo <= 0 or hi < lo:
        raise ContractError('invalid single-centre Gram bounds')
    lower, upper = lo - c - h*d, hi + c + h*d
    if lower <= 0:
        raise ContractError('full-frame positivity not certified for this interval')
    return {'lower': lower, 'upper': upper, 'condition_upper': upper/lower,
            'anchor_cross_upper': c, 'motion_cost': h*d}


def symmetric_bounds(matrix):
    a = [[rat(x) for x in row] for row in matrix]
    n = len(a)
    if not n or any(len(row) != n for row in a):
        raise ContractError('nonempty square matrix required')
    if any(a[i][j] != a[j][i] for i in range(n) for j in range(n)):
        raise ContractError('matrix not exactly symmetric; no projection allowed')
    lo = min(a[i][i] - sum(abs(a[i][j]) for j in range(n) if j != i) for i in range(n))
    hi = max(a[i][i] + sum(abs(a[i][j]) for j in range(n) if j != i) for i in range(n))
    if lo <= 0:
        raise ContractError('positive Gram lower bound absent')
    return lo, hi


def angular_frame(radial_gram, radial_T, ells):
    """Complete m multiplets. Hardy: Q_l <= [1+4 l(l+1)] T_l.

    The trace in the z direction is Q_trace/3 because every m is retained.
    This is NOT a claim that every individual p_m has isotropic derivatives.
    """
    if tuple(ells) != (0, 0, 0, 1, 1):
        raise ContractError('only pinned complete s+p radial layout supported')
    G = [[rat(x) for x in row] for row in radial_gram]
    T = [[rat(x) for x in row] for row in radial_T]
    if len(G) != 5 or len(T) != 5 or any(len(r) != 5 for r in G + T):
        raise ContractError('five-by-five inherited moments required')
    if any(G[i][j] != G[j][i] or T[i][j] != T[j][i] for i in range(5) for j in range(5)):
        raise ContractError('inherited moments not symmetric')
    if any(G[i][i] <= 0 or T[i][i] < 0 for i in range(5)):
        raise ContractError('nonpositive norm or negative kinetic moment')
    ch = [(i, l, m) for i, l in enumerate(ells) for m in range(-l, l+1)]
    g = [[G[i][j] if (l, m) == (ll, mm) else F(0)
          for j, ll, mm in ch] for i, l, m in ch]
    low, high = symmetric_bounds(g)
    norm_trace = sum(G[i][i] for i, _, _ in ch)
    grad_trace = sum((1 + 4*l*(l+1))*T[i][i] for i, l, _ in ch)
    return {'channels': ch, 'G': g, 'G_lower': low, 'G_upper': high,
            'norm_trace': norm_trace, 'gradient_trace_upper': grad_trace,
            'z_gradient_trace_upper': grad_trace/F(3)}


def h1_motion(frame, speed):
    v = rat(speed)
    if v <= 0:
        raise ContractError('positive registered speed required')
    n, q = frame['norm_trace'], frame['gradient_trace_upper']
    beta = q/3 + v*v*n/4
    lip = sqrt_bounds(frame['G_upper']*beta)[1]
    return {'beta_z_derivative_trace': beta,
            'cross_z_Lipschitz_upper': lip,
            'full_Sdot_operator_upper': v*lip,
            'two_centre_gradient_trace_upper': 2*q + v*v*n,
            'projectile_time_derivative_trace_upper': v*v*beta}


def weak_operator_norms(gram_upper, gradient_trace, time_derivative_trace):
    """Atomic-unit numerical values: hbar=Eh*ta, kappa_T=kappa_P=Eh*a0.

    H_kin<=grad/2; Hardy bounds both Coulomb centres by
    4 sqrt(||S|| grad). D=F^* Fdot. K=H-i*hbar*D is not
    Hermitianized. These are coarse operator 2-norm bounds, not errors
    of any old stored H or D values.
    """
    s, a, t = map(nonnegative, (gram_upper, gradient_trace, time_derivative_trace))
    if s <= 0:
        raise ContractError('positive frame norm required')
    H = a/2 + 4*sqrt_bounds(s*a)[1]
    D = sqrt_bounds(s*t)[1]
    return {'H_operator_upper_Eh': H, 'D_operator_upper_per_ta': D,
            'K_operator_upper_Eh': H+D, 'reference_K': 'zero_matrix',
            'meaning': 'uniform absolute norm / zero-reference tube; not a sharp dynamical error'}


def interval_from_dict(x):
    if set(x) != {'denominator_power2', 'lower_numerator', 'upper_numerator'}:
        raise ContractError('unexpected interval schema')
    b = x['denominator_power2']
    if type(b) is not int or b != 256:
        raise ContractError('anchor must have its pinned 256-bit endpoint encoding')
    try:
        lo, hi = F(int(x['lower_numerator']), 1 << b), F(int(x['upper_numerator']), 1 << b)
    except (ValueError, TypeError) as exc:
        raise ContractError('bad interval endpoint') from exc
    if lo > hi:
        raise ContractError('reversed interval')
    return lo, hi


def anchor_matrix(enclosure):
    if enclosure['matrix_shape'] != [9, 9] or len(enclosure['entries']) != 81:
        raise ContractError('registered 9 by 9 cross matrix required')
    mid, sqmax, sqmid, sqradius = [], F(0), F(0), F(0)
    for entry in enclosure['entries']:
        if set(entry) != {'re', 'im'}:
            raise ContractError('complex rectangle required')
        vals = []
        for k in ('re', 'im'):
            lo, hi = interval_from_dict(entry[k])
            m, radius = (lo+hi)/2, (hi-lo)/2
            sqmax += max(abs(lo), abs(hi))**2
            sqmid += m*m
            sqradius += radius*radius
            vals.append(m)
        mid.append(tuple(vals))
    radius = sqrt_bounds(2*sqradius)[1]
    claimed = nonnegative(enclosure['full_cross_radius_upper'])
    # Compare squares, not two differently rounded square-root representations.
    if claimed*claimed < 2*sqradius:
        raise ContractError('parent claimed radius does not cover its entries')
    return {'C_mid': [mid[i:i+9] for i in range(0, 81, 9)],
            'C_norm_upper': sqrt_bounds(sqmax)[1],
            'C_norm_upper_square_raw': sqmax,
            'C_mid_full_X_norm_upper': sqrt_bounds(2*sqmid)[1],
            'radius_full_X_upper': claimed,
            'rectangle_radius_square_full_X': 2*sqradius}


def phase_correct(mid, speed, z, actual_time):
    """For real delta, e^(-i delta) = 1-i delta-delta^2/2 + R.

    |R|<=|delta|^3/6 by integral Taylor remainder and modulus-one
    derivatives, no complex exponential assumption or float exp.
    """
    v, z, t = map(rat, (speed, z, actual_time))
    delta = (v*z-v*v*t)/2
    if abs(delta) > F(1, 1000):
        raise ContractError('epoch correction outside the registered tiny-phase lane')
    qr, qi, err = 1-delta*delta/2, -delta, abs(delta)**3/6
    ans = [[(qr*x-qi*y, qr*y+qi*x) for x, y in row] for row in mid]
    return {'C_ideal_mid': ans, 'delta': delta, 'q_re': qr, 'q_im': qi, 'phase_error_upper': err}


def make_certificate(frame, anchor, speed, z, time, halfwidths):
    motion = h1_motion(frame, speed)
    phase = phase_correct(anchor['C_mid'], speed, z, time)
    anchor_error = anchor['radius_full_X_upper'] + phase['phase_error_upper']*anchor['C_mid_full_X_norm_upper']
    rows = []
    for h in halfwidths:
        h = rat(h)
        if h not in (F(1,64), F(1,128)):
            raise ContractError('only the two historical windows are admitted')
        g = gram_tube(frame['G_lower'], frame['G_upper'], anchor['C_norm_upper'], motion['cross_z_Lipschitz_upper'], h)
        ops = weak_operator_norms(g['upper'], motion['two_centre_gradient_trace_upper'], motion['projectile_time_derivative_trace_upper'])
        rows.append({'halfwidth_a0': h, 'z_interval_a0': [rat(z)-h, rat(z)+h],
                     'gram': g, 'S_constant_reference_error_operator_upper': anchor_error + h*motion['cross_z_Lipschitz_upper'],
                     'Sdot_zero_reference_error_operator_upper_per_ta': motion['full_Sdot_operator_upper'],
                     'K_zero_reference_error_operator_upper_Eh': ops['K_operator_upper_Eh'],
                     'operators': ops})
    if len(rows) != 2 or len({r['halfwidth_a0'] for r in rows}) != 2:
        raise ContractError('exactly the two distinct windows required')
    return {'schema': 'R4AL_FULL18_H1_CERTIFICATE_V1', 'norm': 'operator_2_except_explicit_full_X_Frobenius_fields',
            'single_centre': frame, 'motion': motion, 'anchor': anchor, 'epoch': phase,
            'anchor_error_to_ideal_operator_upper': anchor_error, 'windows': rows,
            'exact_model_metric_defect': 'zero_by_H1_Gram_derivative_and_Hermitian_weak_form_only',
            'old_numerical_metric_defect_certified_zero': False,
            'coarse_K_tube_accepted_as_small_bridge_error': False,
            'physical_bridge_upper': None, 'full_stencil_total_upper': [None,None],
            'physical_basis_discrepancy_included': False,
            'new_cross_integrals': 0, 'new_radial_integrals': 0, 'old_calculations_replayed': 0}


def json_safe(x):
    if isinstance(x, F): return str(x)
    if isinstance(x, dict): return {k: json_safe(v) for k,v in x.items()}
    if isinstance(x, (tuple,list)): return [json_safe(v) for v in x]
    return x
