"""Independent same-center B0 derivative reference from exact stored coefficients.

No native operator is imported or constructed. Decimal is a separate reference,
not a replacement for the archived binary64 operator or a rigorous enclosure.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'production_validation_20261001'))
import fresh_context_analysis as fresh


def dec(x):
    x = F(x)
    return Decimal(x.numerator) / Decimal(x.denominator)


def mul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def integral(poly):
    return sum((x/F(i+1) for i, x in enumerate(poly)), F(0))


def derivative_integral(a, b):
    """Integral_0^1 a(s) b'(s) ds: dr and d/dr cancel exactly."""
    if len(b) < 2:
        return F(0)
    return integral(mul(a, [F(i)*b[i] for i in range(1, len(b))]))


def trace_pair(a, b):
    if len(a) != len(b):
        raise ValueError('cell count mismatch')
    return sum((sum(x)*sum(y) - x[0]*y[0] for x, y in zip(a, b)), F(0))


def radial_inverse_integral(a, b, edges):
    """Integral u_a(r)u_b(r)/r dr via exact division plus Decimal log.

    For r=left+width*s, width cancels and denominator is s+left/width.
    Polynomial division is rational. Only the logarithm is rounded.
    """
    total = Decimal(0)
    for x, y, left, right in zip(a, b, edges[:-1], edges[1:]):
        poly = mul(x, y)
        q = left/(right-left)
        if q == 0:
            if poly[0] != 0:
                raise ValueError('nonintegrable origin trace in radial inverse integral')
            total += dec(sum((poly[k]/F(k) for k in range(1, len(poly))), F(0)))
            continue
        rem = poly[:]
        quotient = [F(0)] * (len(poly)-1)
        for k in range(len(poly)-1, 0, -1):
            quotient[k-1] = rem[k]
            rem[k-1] -= q*rem[k]
        total += dec(integral(quotient)) + dec(rem[0]) * (Decimal(1)+Decimal(1)/dec(q)).ln()
    return total


def coupling(a, b, edges, velocity, digits):
    """s,m0 -> p,m0 angular N=1/sqrt(3), with actual archived ETF sign."""
    trace = trace_pair(a, b)
    iab = sum((derivative_integral(x, y) for x, y in zip(a, b)), F(0))
    iba = sum((derivative_integral(y, x) for x, y in zip(a, b)), F(0))
    if iab + iba != trace:
        raise ArithmeticError('exact polynomial integration-by-parts identity failed')
    with localcontext() as ctx:
        ctx.prec = digits
        j = radial_inverse_integral(a, b, edges)
        prefactor = -dec(velocity)/Decimal(3).sqrt()
        forward = prefactor * (dec(iab)+j)
        reverse = prefactor * (dec(iba)-j)
        stable_sum = prefactor * dec(trace)
        return {'digits': digits, 'D_sp': str(forward), 'D_ps': str(reverse),
                'sum_individual_D': str(forward+reverse), 'trace_D_sum': str(stable_sum),
                'identity_residual': str(forward+reverse-stable_sum),
                'I_sp': str(dec(iab)), 'I_ps': str(dec(iba)), 'J_sp': str(j)}


def enforce_continuity_candidate(cells):
    """Separate exact-arithmetic candidate; NOT an in-place bank repair.

    Add delta_e*s per cell. The next cell's left value fixes a shared endpoint;
    the last right value is zero. At fixed endpoint changes, this affine lift
    minimizes the correction's unweighted radial derivative seminorm.
    """
    if any(len(c) < 2 for c in cells) or cells[0][0] != 0:
        raise ValueError('degree>=1 and exact zero origin required')
    out = [list(c) for c in cells]
    deltas = []
    for k, c in enumerate(cells):
        target = cells[k+1][0] if k+1 < len(cells) else F(0)
        delta = target-sum(c)
        out[k][1] += delta
        deltas.append(delta)
    if any(sum(out[k]) != out[k+1][0] for k in range(len(out)-1)) or sum(out[-1]) != 0:
        raise ArithmeticError('candidate did not restore exact continuity')
    return out, deltas


def mode_record(cells, edges, digits=80):
    """The derivative change is cellwise/broken L2, not a global H1 norm.

    The original discontinuous polynomial has interface distributions in its
    weak derivative. Differentiating just the affine cell corrections does not
    measure those distributions or a global weak-derivative difference.
    """
    candidate, delta = enforce_continuity_candidate(cells)
    jumps = [cells[k+1][0]-sum(cells[k]) for k in range(len(cells)-1)]
    norm2 = sum(((b-a)*integral(mul(c, c)) for c, a, b in zip(cells, edges[:-1], edges[1:])), F(0))
    correction2 = sum(((b-a)*d*d/F(3) for d, a, b in zip(delta, edges[:-1], edges[1:])), F(0))
    derivative2 = sum((d*d/(b-a) for d, a, b in zip(delta, edges[:-1], edges[1:])), F(0))
    with localcontext() as ctx:
        ctx.prec = digits
        n, dn = dec(norm2).sqrt(), dec(correction2).sqrt()
        record = {'maximum_internal_jump': str(dec(max(map(abs, jumps), default=F(0)))),
                  'origin_trace': str(dec(cells[0][0])), 'outer_trace': str(dec(sum(cells[-1]))),
                  'candidate_maximum_radial_value_change_bound': str(dec(max(map(abs, delta)))),
                  'candidate_radial_L2_change': str(dn),
                  'candidate_relative_radial_L2_change': str(dn/n),
                  'candidate_cellwise_radial_derivative_L2_change': str(dec(derivative2).sqrt()),
                  'derivative_change_scope': 'cell-interior strong derivatives only; not a global weak-derivative/H1 difference',
                  'candidate_diagonal_overlap_change_bound': str(2*n*dn+dn*dn),
                  'candidate_exact_continuity': True}
    return record, candidate


def load_bank_exact(path):
    with np.load(path, allow_pickle=False) as bank:
        edges = np.array(bank['edges'])
        coeff = np.array(bank['coefficients'])
    if (edges.dtype != np.float64 or coeff.dtype != np.float64 or edges.ndim != 1
        or coeff.ndim != 3 or coeff.shape[1] != len(edges)-1 or coeff.shape[2] < 2
        or edges[0] != 0 or np.any(np.diff(edges) <= 0)
        or not np.isfinite(edges).all() or not np.isfinite(coeff).all()):
        raise ValueError('invalid binary64 polynomial bank')
    return [F.from_float(float(x)) for x in edges], [[[F.from_float(float(x)) for x in cell] for cell in mode] for mode in coeff]


def metadata_bound_to_context(path, context):
    if fresh.hp.sha(path) != context['input_files']['BASIS.json']:
        raise ValueError('basis metadata bytes differ from admitted context')
    return fresh.read(path)


def run(basis_npz, basis_json, manifests, output):
    started = time.monotonic()
    declaration = fresh.read(HERE/'TASK_CONTRACT.json')
    if fresh.hp.sha(basis_npz) != declaration['basis_npz_sha256']:
        raise ValueError('basis bytes differ from declared bank')
    plan = fresh._fixed(fresh.FD_PLAN, fresh.FD_PLAN_SHA)
    samples, provenance, context = fresh._load_lanes(manifests, [q['time_hex'] for q in plan['queries']])
    info = metadata_bound_to_context(basis_json, context)
    if info['matrix_sha256'] != fresh.hp.sha(basis_npz) or info['identity'] != context['basis_identity']:
        raise ValueError('basis metadata/context binding mismatch')
    modes = info['modes']
    if [m['l'] for m in modes] != [0, 0, 0, 1, 1]:
        raise ValueError('oracle scope is the archived B0 s/p bank only')
    edges, coeff = load_bank_exact(basis_npz)
    velocity = F.from_float(float(plan['identity']['velocity_au']))
    mode_results, corrected = [], []
    for meta, cells in zip(modes, coeff):
        r, c = mode_record(cells, edges)
        mode_results.append({'radial_identity':meta['identity'], 'l':meta['l'], **r})
        corrected.append(c)
    # Match symmetric_channels actual ordering: centers, modes, then -l..l.
    channels = [(center, mode, m) for center in (0, 1) for mode, meta in enumerate(modes) for m in range(-meta['l'], meta['l']+1)]
    by_z = {q['z_hex']: samples[q['time_hex']] for q in plan['queries']}
    centers = {z: by_z[float(z).hex()] for z in plan['centers']}
    pairs = []
    for s in range(3):
        for p in range(3, 5):
            low = coupling(coeff[s], coeff[p], edges, velocity, 80)
            high = coupling(coeff[s], coeff[p], edges, velocity, 120)
            candidate = coupling(corrected[s], corrected[p], edges, velocity, 80)
            with localcontext() as ctx:
                ctx.prec = 160
                precision_difference = max(abs(Decimal(low[k])-Decimal(high[k])) for k in ('D_sp', 'D_ps', 'trace_D_sum'))
            if precision_difference >= Decimal('1e-65'):
                raise ArithmeticError('declared precision comparison failed')
            if trace_pair(corrected[s], corrected[p]) != 0:
                raise ArithmeticError('candidate exact trace does not vanish')
            row = channels.index((1, s, 0)); col = channels.index((1, p, 0))
            archived = []
            for z, sample in sorted(centers.items()):
                forward = complex(sample['D'][row, col]); reverse = complex(sample['D'][col, row]).conjugate()
                if forward.imag != 0 or reverse.imag != 0:
                    raise ValueError('unexpected complex s/p_z samecenter entry')
                cache_sum = F.from_float(forward.real)+F.from_float(reverse.real)
                with localcontext() as ctx:
                    ctx.prec = 120
                    reference = Decimal(high['trace_D_sum'])
                    archived.append({'z_a0':z, 'D_sp':forward.real, 'conjugate_D_ps':reverse.real,
                        'exact_sum_of_stored_D':str(dec(cache_sum)),
                        'stored_sum_minus_coefficient_trace_reference':str(dec(cache_sum)-reference),
                        'D_sp_minus_reference':str(dec(F.from_float(forward.real))-Decimal(high['D_sp'])),
                        'D_ps_minus_reference':str(dec(F.from_float(reverse.real))-Decimal(high['D_ps']))})
            trace = trace_pair(coeff[s], coeff[p])
            pairs.append({'s_mode':s, 'p_mode':p, 'projectile_global_indices':[row,col],
                'exact_rational_product_trace':{'numerator':str(trace.numerator),'denominator':str(trace.denominator)},
                'reference80':low, 'reference120':high, 'precision_max_absolute_difference':str(precision_difference),
                'continuity_candidate80':candidate, 'candidate_exact_trace_zero':True, 'archived_comparisons':archived})
    result = {'schema':'BASS_R4W_EXACT_TRACE_ORACLE_V1', 'status':'REFERENCE_CALCULATION_COMPLETED',
        'basis_sha256':fresh.hp.sha(basis_npz),'basis_metadata_sha256':fresh.hp.sha(basis_json),
        'source_sha256':fresh.hp.sha(__file__),'contract_sha256':fresh.hp.sha(HERE/'TASK_CONTRACT.json'),
        'context_id':context['context_id'],'provenance':provenance,'velocity_au':float(velocity),
        'modes':mode_results,'pairs':pairs,'wall_seconds':time.monotonic()-started,
        'reference_scope':'Exact rational cell polynomials with80/120digit Decimal log/sqrt; no quadrature or angular numerical rule',
        'candidate_scope':'Different exact piecewise-polynomial representation; not exported/adopted as a production bank or the original nodal FEM',
        'original_raw_FD_acceptance_changed':False,'physical_G02_closed':False,'native_calls':0,
        'production_admission':'HOLD','capture':False,'rigorous_total_operator_error_bound':False}
    fresh.hp.write_new(output,result)
    return result


if __name__ == '__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--basis-npz',required=True);a.add_argument('--basis-json',required=True)
    a.add_argument('--manifests',nargs='+',required=True);a.add_argument('--output',required=True)
    v=a.parse_args();r=run(v.basis_npz,v.basis_json,v.manifests,v.output)
    print(json.dumps({'status':r['status'],'pairs':len(r['pairs']),'wall_seconds':r['wall_seconds'],'native_calls':0}))
