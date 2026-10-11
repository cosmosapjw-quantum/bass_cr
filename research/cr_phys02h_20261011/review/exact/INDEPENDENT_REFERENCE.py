"""One bounded scalar review; no producer imports, numerical libraries or physics.

The upper envelope is recomputed as the minimum of independently applicable
Markov and one-sided Chebyshev inequalities, rather than the producer branch.
Persisted atomic witnesses are evaluated from their literal times and weights.
"""
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import platform
import signal
import sys
import time

HERE = Path(__file__).resolve().parent
H = HERE.parents[1]
REPO = H.parents[1]
SOURCE = REPO / 'research/cr_phys02g_20261011/inputs/F_CACHED_NUMERICAL_ARTIFACT.json'
ARTIFACT = H / 'evidence/exact/EXACT_CERTIFICATES.json'
KEYS = ('H0', 'p', 'R', 'S', 'mu_s', 'm2_s2')
T = Q(10_000_000_000)
YEAR = Q(31_557_600)
COUNTS = dict(canonical_rationals=0, integer_proofs=0, source_records=0,
              feasible_witnesses=0, certificates=0, endpoint_component_pairs=0,
              adjacent_search_pairs=0, finite_law_survival_checks=0)


def ident(path):
    b = path.read_bytes()
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def decode(value):
    if isinstance(value, dict):
        if 'numerator' in value and 'denominator' in value:
            n, d = value['numerator'], value['denominator']
            assert type(n) is int and type(d) is int and d > 0
            q = Q(n, d)
            assert (q.numerator, q.denominator) == (n, d)
            COUNTS['canonical_rationals'] += 1
            return q
        return {k: decode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [decode(v) for v in value]
    return value


def walk_proofs(value):
    if isinstance(value, dict):
        if {'left', 'right', 'relation', 'lhs_integer', 'rhs_integer', 'passed'} <= value.keys():
            l, r = Q(value['left']), Q(value['right'])
            li, ri = l.numerator*r.denominator, r.numerator*l.denominator
            assert value['lhs_integer'] == li and value['rhs_integer'] == ri
            assert value['signed_integer'] == li-ri
            assert value['signed_margin'] == l-r
            relation = value['relation']
            actual = {'>': l > r, '>=': l >= r, '<=': l <= r, '==': l == r}[relation]
            assert actual and value['passed'] is True
            COUNTS['integer_proofs'] += 1
        for child in value.values():
            walk_proofs(child)
    elif isinstance(value, list):
        for child in value:
            walk_proofs(child)


def derived_tail(row):
    # Expand the positive-part moments directly in powers of tau.
    early_m1 = T*(row['p']-row['R'])
    early_m2 = T*T*(row['p']-2*row['R']+row['S'])
    q = 1-row['p']
    tail_tau1 = (row['mu_s']-early_m1)/q
    tail_tau2 = (row['m2_s2']-early_m2)/q
    return q, tail_tau1-T, tail_tau2-2*T*tail_tau1+T*T


def check_record(raw, saved):
    assert {k: saved[k] for k in KEYS} == raw
    assert raw['H0'] > 0 and 0 < raw['p'] < 1
    assert 0 <= raw['S'] <= raw['R'] <= raw['p']
    assert raw['R']**2 <= raw['p']*raw['S']
    q, a, b = derived_tail(raw)
    assert a > 0 and b >= a*a
    assert saved['q'] == q
    assert saved['tail_residual'] == {'mean_s': a, 'second_s2': b, 'variance_s2': b-a*a}
    atoms = saved['witness']['atoms']
    assert atoms and all(z['weight'] >= 0 and z['tau_s'] >= 0 for z in atoms)
    assert all((z['tau_s'] <= T) == (z['region'] == 'early') for z in atoms)
    weights = [z['weight'] for z in atoms]
    assert sum(weights, Q()) == 1
    recovered = {
        'p': sum((z['weight'] for z in atoms if z['tau_s'] <= T), Q()),
        'R': sum((z['weight']*max(1-z['tau_s']/T, Q()) for z in atoms), Q()),
        'S': sum((z['weight']*max(1-z['tau_s']/T, Q())**2 for z in atoms), Q()),
        'mu_s': sum((z['weight']*z['tau_s'] for z in atoms), Q()),
        'm2_s2': sum((z['weight']*z['tau_s']**2 for z in atoms), Q()),
    }
    assert recovered == {k: raw[k] for k in recovered}
    assert saved['witness']['support_pass'] is True
    assert saved['feasibility']['status'] == 'COMPATIBLE_EXACT_RECORDED_MOMENTS'
    COUNTS['source_records'] += 1
    COUNTS['feasible_witnesses'] += 1


def generic(a, b, x):
    assert x >= 0 and a >= 0 and b >= a*a and (a != 0 or b == 0)
    v = b-a*a
    if v == 0:
        return (Q(x < a), Q(x < a))
    lower = Q() if x >= a else 1-v/(v+(a-x)*(a-x))
    candidates = [Q(1)]
    if x > 0:
        candidates.append(a/x)
    if x > a:
        candidates.append(v/(v+(x-a)*(x-a)))
    return lower, min(candidates)


def envelope(rows, weights, pooled, t, allow_birth):
    assert t >= T
    pairs = {'unconditional': generic(pooled['mu_s'], pooled['m2_s2'], t)}
    q, a, b = derived_tail(pooled)
    pairs['pooled_residual'] = (q, q) if t == T else tuple(q*y for y in generic(a, b, t-T))
    if allow_birth:
        birth_pairs = []
        for row in rows:
            qi, ai, bi = derived_tail(row)
            birth_pairs.append((qi, qi) if t == T else tuple(qi*y for y in generic(ai, bi, t-T)))
        pairs['birth_residual'] = tuple(sum((w*pair[k] for w, pair in zip(weights, birth_pairs)), Q()) for k in (0, 1))
    result = (q, q) if t == T else (max(z[0] for z in pairs.values()), min(z[1] for z in pairs.values()))
    assert 0 <= result[0] <= result[1] <= 1
    return result, pairs


def run():
    assert ident(H/'state/SCIENTIFIC_CONTRACT.json')['sha256'] == 'a49b1fa88c86d46c4e37cdb7ba37fbd44e5fa05511febc3a3089ab5ed5331dc4'
    assert ident(SOURCE) == {'bytes': 48626, 'sha256': 'dfdca59ca0b4131c6143fe3cf0e402a7b18efb113a9af9bcc82a66696f5ec6f5'}
    assert ident(ARTIFACT) == {'bytes': 462720, 'sha256': '246cf5d53381380b5eef15debdad53d7d3dcae91cb1db2dcc74a4029b8202113'}
    raw = json.loads(SOURCE.read_text(), parse_float=Q, parse_int=Q)
    out = decode(json.loads(ARTIFACT.read_text()))
    assert raw['T_s'] == out['T_s'] == T and out['year_s'] == YEAR
    assert out['certificate_count'] == 20
    walk_proofs(out)
    endpoint_results, discrepancy_results = [], {}
    for model_name in ('fullBED', 'legacy'):
        inp = raw['models'][model_name]
        selected = {k: inp['selected'][k] for k in KEYS}
        births = [{k: row[k] for k in KEYS} for row in inp['birth_columns']]
        total_h = sum((row['H0'] for row in births), Q())
        weights = [row['H0']/total_h for row in births]
        assert sum(weights, Q()) == 1
        pooled = {'H0': total_h, **{k: sum((w*row[k] for w, row in zip(weights, births)), Q()) for k in KEYS if k != 'H0'}}
        saved_model = out['models'][model_name]['model']
        assert saved_model['T'] == T
        reps = saved_model['representations']
        assert set(reps) == {'selected_record', 'birth_defined'}
        assert reps['selected_record']['allowed_components'] == ['unconditional', 'pooled_residual']
        assert reps['birth_defined']['allowed_components'] == ['unconditional', 'pooled_residual', 'birth_residual']
        assert reps['birth_defined']['weights'] == weights
        assert len(reps['birth_defined']['birth']) == len(births)
        check_record(selected, reps['selected_record']['pooled'])
        check_record(pooled, reps['birth_defined']['pooled'])
        for r, s in zip(births, reps['birth_defined']['birth']):
            check_record(r, s)
        differences = saved_model['exact_selected_vs_birth_differences']
        for key in KEYS:
            assert differences[key] == {'selected': selected[key], 'birth_defined': pooled[key],
                'selected_minus_birth_defined': selected[key]-pooled[key], 'exactly_equal': selected[key] == pooled[key]}
        discrepancy_results[model_name] = {k: str(selected[k]-pooled[k]) for k in KEYS}
        certs = out['models'][model_name]['certificates']
        assert {(c['representation'], c['fraction']) for c in certs} == {
            (r, Q(f)) for r in reps for f in ('0.5', '0.9', '0.95', '0.99', '0.999')}
        for c in certs:
            rep = c['representation']
            is_birth = rep == 'birth_defined'
            record = pooled if is_birth else selected
            at = lambda t: envelope(births, weights, record, t, is_birth)
            epsilon = 1-c['fraction']
            assert c['threshold'] == epsilon
            lo, hi = c['lower_s'], c['upper_s']
            assert type(lo) is int and type(hi) is int and T <= lo <= hi
            assert c['lower_years'] == lo/YEAR and c['upper_years'] == hi/YEAR
            bounds_lo, _ = at(lo)
            bounds_hi, _ = at(hi)
            assert bounds_lo[0] > epsilon and bounds_hi[1] <= epsilon
            assert c['lower_margin'] == bounds_lo[0]-epsilon
            assert c['upper_margin'] == epsilon-bounds_hi[1]
            assert c['lower_endpoint_proof']['left'] == bounds_lo[0]
            assert c['lower_endpoint_proof']['right'] == epsilon
            assert c['lower_endpoint_proof']['relation'] == '>'
            assert c['upper_endpoint_proof']['left'] == bounds_hi[1]
            assert c['upper_endpoint_proof']['right'] == epsilon
            assert c['upper_endpoint_proof']['relation'] == '<='
            for endpoint, t in (('lower_endpoint', lo), ('upper_endpoint', hi)):
                values, parts = at(t)
                saved = c[endpoint]
                assert saved['t_s'] == t and saved['representation'] == rep
                assert saved['intersection'] == {'lower': values[0], 'upper': values[1]}
                assert set(saved['components']) == set(parts)
                for name, pair in parts.items():
                    assert saved['components'][name]['lower'] == pair[0]
                    assert saved['components'][name]['upper'] == pair[1]
                    COUNTS['endpoint_component_pairs'] += 1
            for name, index in (('lower', 0), ('upper', 1)):
                s = c['searches'][name]
                left, right = s['final_s']
                assert right-left == 1 and left >= T
                assert at(left)[0][index] > epsilon and at(right)[0][index] <= epsilon
                assert s['initial_s'][0] == T and s['initial_s'][1] == 2*T*2**s['doublings']
                assert 0 <= s['doublings'] <= 64 and 0 <= s['bisections'] <= 80
                assert s['strict_above_at_low']['left'] == at(left)[0][index]
                assert s['at_or_below_at_high']['left'] == at(right)[0][index]
                COUNTS['adjacent_search_pairs'] += 1
            assert lo == c['searches']['lower']['final_s'][0]
            assert hi == c['searches']['upper']['final_s'][1]
            endpoint_results.append({'model': model_name, 'representation': rep,
                'fraction': str(c['fraction']), 'lower_s': lo, 'upper_s': hi,
                'strict_lower_margin': str(c['lower_margin']), 'closed_upper_margin': str(c['upper_margin'])})
            COUNTS['certificates'] += 1
    # Independent literal finite laws include delta0, deterministic thresholds,
    # zeros, skew tails and points at branch/equality boundaries.
    laws = [[(Q(0), Q(1))], [(Q(2), Q(1))],
            [(Q(0), Q(1, 3)), (Q(3), Q(2, 3))],
            [(Q(1), Q(7, 8)), (Q(9), Q(1, 8))],
            [(Q(0), Q(1, 4)), (Q(1), Q(1, 4)), (Q(5), Q(1, 2))]]
    for law in laws:
        a = sum((x*w for x, w in law), Q())
        b = sum((x*x*w for x, w in law), Q())
        probes = {Q(i, 4) for i in range(45)} | {x for x, _ in law} | {a}
        if a:
            probes.add(b/a)
        for x in probes:
            actual = sum((w for point, w in law if point > x), Q())
            l, u = generic(a, b, x)
            assert l <= actual <= u
            COUNTS['finite_law_survival_checks'] += 1
    assert COUNTS['certificates'] == 20 and COUNTS['feasible_witnesses'] == 8
    return {'checks': COUNTS, 'certificates': endpoint_results,
            'exact_selected_minus_birth_defined': discrepancy_results,
            'producer_imports': [], 'physical_calls': {'G': 0, 'F_retry': 0, 'pulse': 0,
                'expm': 0, 'resolvent': 0, 'linear_solve': 0, 'old_suite_reruns': 0}}


if __name__ == '__main__':
    start = datetime.now(timezone.utc).isoformat()
    t0 = time.monotonic()
    signal.signal(signal.SIGALRM, lambda signum, frame: (_ for _ in ()).throw(TimeoutError('60s independent scalar reference budget')))
    signal.alarm(60)
    receipt = {'schema': 'cr-phys02h-independent-exact-reference.v1', 'command': sys.argv,
               'start_utc': start, 'timeout_s': 60, 'source': ident(SOURCE),
               'artifact': ident(ARTIFACT), 'reviewer_script': ident(Path(__file__)),
               'runtime': {'python': sys.version, 'platform': platform.platform()},
               'execution_count': 1, 'independent_of_implementation': True}
    try:
        receipt.update(run(), actual_exit=0, status='PASS_EXACT_SCALAR_REFERENCE')
    except BaseException as exc:
        receipt.update(actual_exit=1, status='FAIL_PRESERVED', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        signal.alarm(0)
        receipt.update(end_utc=datetime.now(timezone.utc).isoformat(), wall_s=time.monotonic()-t0)
        with (HERE/'INDEPENDENT_REFERENCE_RECEIPT.json').open('x') as f:
            json.dump(receipt, f, indent=2, ensure_ascii=False, allow_nan=False)
            f.write('\n')
        print(json.dumps({k: receipt[k] for k in ('status', 'actual_exit', 'wall_s')}, ensure_ascii=False))
