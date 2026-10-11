"""Exact recorded-decimal moment certificates; no physical input accuracy claim.

All probability arithmetic is Fraction. Selected-record and birth-defined laws
are separate feasible probability representations and never share constraints.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

PRIMITIVES = ('H0', 'p', 'R', 'S', 'mu_s', 'm2_s2')


class MomentError(ValueError):
    def __init__(self, code, message, evidence=None):
        self.code, self.evidence = code, evidence
        super().__init__(f'{code}: {message}')


def rational(value):
    if isinstance(value, bool) or not isinstance(value, (int, F)):
        raise MomentError('NONEXACT_INPUT', repr(value))
    return F(value)


def load_exact(path):
    return json.loads(Path(path).read_text(), parse_float=F, parse_int=F,
                      parse_constant=lambda v: (_ for _ in ()).throw(
                          MomentError('NONFINITE_INPUT', v)))


def identity(path):
    payload = Path(path).read_bytes()
    return dict(bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())


def check_identity(path, pin):
    observed = identity(path)
    if observed != {k: pin[k] for k in ('bytes', 'sha256')}:
        raise MomentError('SOURCE_IDENTITY_MISMATCH', str(path), observed)
    return observed


def comparison(left, right, relation):
    """Integer cross-product proof, including exact signed rational margin."""
    left, right = rational(left), rational(right)
    lhs, rhs = left.numerator * right.denominator, right.numerator * left.denominator
    passed = {'>': lhs > rhs, '>=': lhs >= rhs, '<=': lhs <= rhs,
              '==': lhs == rhs}[relation]
    return dict(left=left, right=right, relation=relation,
                lhs_integer=lhs, rhs_integer=rhs, signed_integer=lhs-rhs,
                signed_margin=left-right, passed=passed)


def bounds(mean, second, x):
    """Generic sharp individual envelopes for strict P(X>x), X>=0."""
    a, b, x = map(rational, (mean, second, x))
    if min(a, b, x) < 0:
        raise MomentError('NEGATIVE_INPUT', 'a,b,x must be nonnegative')
    if a == 0 and b != 0:
        raise MomentError('ZERO_MEAN_POSITIVE_SECOND', 'nonnegative law impossible')
    v = b-a*a
    if v < 0:
        raise MomentError('NEGATIVE_VARIANCE', str(v))
    if v == 0:
        value = F(int(x < a))
        return dict(lower=value, upper=value, variance=v, branch='DETERMINISTIC_STRICT')
    lower = (a-x)**2 / (v+(a-x)**2) if x < a else F(0)
    if x <= a:
        upper, branch = F(1), 'UPPER_ONE'
    elif a*x < b:
        upper, branch = a/x, 'UPPER_MARKOV'
    else:
        upper, branch = v/(v+(x-a)**2), 'UPPER_CANTELLI'
    return dict(lower=lower, upper=upper, variance=v, branch=branch)


def record(row, T):
    T = rational(T)
    if T <= 0:
        raise MomentError('INVALID_T', 'T>0 required')
    r = {key: rational(row[key]) for key in PRIMITIVES}
    H, p, R, S, mu, m2 = (r[key] for key in PRIMITIVES)
    checks = {
        'H0_positive': comparison(H, 0, '>'),
        'p_positive': comparison(p, 0, '>'),
        'p_below_one': comparison(1, p, '>'),
        'S_nonnegative': comparison(S, 0, '>='),
        'S_le_R': comparison(R, S, '>='),
        'R_le_p': comparison(p, R, '>='),
        'R_squared_le_pS': comparison(p*S, R*R, '>='),
    }
    if not all(c['passed'] for c in checks.values()):
        raise MomentError('INCOMPATIBLE_EARLY_MOMENTS', 'bounded early-support conditions', checks)
    q = 1-p
    a = (mu-T*(1-R))/q
    b = (m2-2*T*mu+T*T*(1-S))/q
    checks.update(tail_mean_positive=comparison(a, 0, '>'),
                  tail_second_ge_mean_squared=comparison(b, a*a, '>='))
    if not all(c['passed'] for c in checks.values()):
        raise MomentError('INCOMPATIBLE_POSITIVE_RESIDUAL', 'strict positive tail-support conditions', checks)
    # Conditional early U=(T-tau)/T in [0,1]. Degenerate cases are explicit.
    early_a, early_b = R/p, S/p
    if early_a == 0:
        early = [(F(0), F(1))]
        early_case = 'ZERO_U'
    elif early_b == early_a*early_a:
        early = [(early_a, F(1))]
        early_case = 'DETERMINISTIC_U'
    else:
        high_weight = early_a*early_a/early_b
        early = [(F(0), 1-high_weight), (early_b/early_a, high_weight)]
        early_case = 'TWO_ATOM_U'
    v = b-a*a
    if v == 0:
        tail = [(a, F(1))]
        tail_case = 'DETERMINISTIC_POSITIVE_RESIDUAL'
    else:
        low, high = a/2, a+2*v/a
        high_weight = (a-low)/(high-low)
        tail = [(low, 1-high_weight), (high, high_weight)]
        tail_case = 'TWO_ATOM_POSITIVE_RESIDUAL'
    atoms = [dict(region='early', tau_s=T*(1-u), weight=p*w) for u,w in early]
    atoms += [dict(region='tail', tau_s=T+x, weight=q*w) for x,w in tail]
    reconstructed = dict(
        p=sum((z['weight'] for z in atoms if z['region']=='early'), F(0)),
        R=sum((z['weight']*(T-z['tau_s'])/T for z in atoms if z['region']=='early'), F(0)),
        S=sum((z['weight']*((T-z['tau_s'])/T)**2 for z in atoms if z['region']=='early'), F(0)),
        mu_s=sum((z['weight']*z['tau_s'] for z in atoms), F(0)),
        m2_s2=sum((z['weight']*z['tau_s']**2 for z in atoms), F(0)))
    witness_checks = {key: comparison(value, r[key], '==') for key,value in reconstructed.items()}
    witness_checks['normalization'] = comparison(sum((z['weight'] for z in atoms), F(0)), 1, '==')
    support_pass = all(z['weight'] >= 0 and
                       (0 <= z['tau_s'] <= T if z['region']=='early' else z['tau_s'] > T)
                       for z in atoms)
    if not support_pass or not all(c['passed'] for c in witness_checks.values()):
        raise MomentError('WITNESS_RECONSTRUCTION_FAILURE', 'exact moment/support identity')
    r.update(q=q, feasibility=dict(status='COMPATIBLE_EXACT_RECORDED_MOMENTS', checks=checks),
             tail_residual=dict(mean_s=a, second_s2=b, variance_s2=v),
             witness=dict(early_case=early_case, tail_case=tail_case, atoms=atoms,
                          support_pass=support_pass, reconstruction=witness_checks))
    return r


def construct_model(cached, T):
    T = rational(T)
    selected = record(cached['selected'], T)
    birth = [record(row, T) for row in cached['birth_columns']]
    if not birth:
        raise MomentError('EMPTY_BIRTH_MIXTURE', 'at least one row required')
    H = sum((r['H0'] for r in birth), F(0))
    weights = [r['H0']/H for r in birth]
    pooled = dict(H0=H, **{key: sum((w*r[key] for w,r in zip(weights,birth)), F(0))
                          for key in PRIMITIVES if key!='H0'})
    pooled = record(pooled, T)
    differences = {key: dict(selected=selected[key], birth_defined=pooled[key],
                             selected_minus_birth_defined=selected[key]-pooled[key],
                             exactly_equal=selected[key]==pooled[key]) for key in PRIMITIVES}
    return dict(T=T, representations={
        'selected_record': dict(pooled=selected, allowed_components=['unconditional', 'pooled_residual']),
        'birth_defined': dict(pooled=pooled, birth=birth, weights=weights,
                              allowed_components=['unconditional', 'pooled_residual', 'birth_residual'])},
                exact_selected_vs_birth_differences=differences)


def residual(r, x):
    if x == 0:
        return dict(lower=r['q'], upper=r['q'], branch='KNOWN_STRICT_POSITIVE_TAIL_AT_T')
    pair = bounds(r['tail_residual']['mean_s'], r['tail_residual']['second_s2'], x)
    return dict(lower=r['q']*pair['lower'], upper=r['q']*pair['upper'], branch=pair['branch'])


def envelope(model, representation, t):
    t = rational(t)
    T = model['T']
    if t < T:
        raise MomentError('THRESHOLD_BEFORE_T', 't>=T required')
    if representation not in model['representations']:
        raise MomentError('UNKNOWN_REPRESENTATION', representation)
    rep = model['representations'][representation]
    pooled = rep['pooled']
    components = dict(unconditional=bounds(pooled['mu_s'], pooled['m2_s2'], t),
                      pooled_residual=residual(pooled, t-T))
    if representation == 'birth_defined':
        parts = [residual(r, t-T) for r in rep['birth']]
        components['birth_residual'] = {key: sum((w*p[key] for w,p in zip(rep['weights'], parts)), F(0))
                                        for key in ('lower', 'upper')}
    intersect = (dict(lower=pooled['q'], upper=pooled['q']) if t == T else
                 dict(lower=max(c['lower'] for c in components.values()),
                      upper=min(c['upper'] for c in components.values())))
    if not 0 <= intersect['lower'] <= intersect['upper'] <= 1:
        raise MomentError('ENVELOPE_ORDER_FAILURE', representation)
    return dict(t_s=t, representation=representation, components=components, intersection=intersect)


def horizon_bracket(model, representation, fraction):
    f = rational(fraction)
    if not 0 < f < 1:
        raise MomentError('INVALID_FRACTION', '0<f<1 required')
    T = model['T']
    if T.denominator != 1:
        raise MomentError('NONINTEGER_T', 'integer-second certificate requires integer T')
    T = int(T)
    epsilon = 1-f
    pair = lambda t: envelope(model, representation, t)['intersection']
    if not comparison(pair(T)['lower'], epsilon, '>')['passed']:
        raise MomentError('NO_STRICT_T_LOWER_ENDPOINT', 'fraction must exceed pooled p')
    searches = {}
    for name, key, relation in (('lower', 'lower', '>'), ('upper', 'upper', '>')):
        low, high, doubles = T, max(T+1, 2*T), 0
        while comparison(pair(high)[key], epsilon, relation)['passed']:
            if doubles >= 64:
                raise MomentError('HORIZON_DOUBLING_EXHAUSTED', name)
            high *= 2
            doubles += 1
        initial = [low, high]
        iterations = 0
        while high-low > 1:
            if iterations >= 80:
                raise MomentError('HORIZON_BISECTION_EXHAUSTED', name)
            mid = (low+high)//2
            if comparison(pair(mid)[key], epsilon, relation)['passed']:
                low = mid
            else:
                high = mid
            iterations += 1
        searches[name] = dict(initial_s=initial, final_s=[low, high],
                              doublings=doubles, bisections=iterations,
                              strict_above_at_low=comparison(pair(low)[key], epsilon, '>'),
                              at_or_below_at_high=comparison(pair(high)[key], epsilon, '<='))
    lo, hi = searches['lower']['final_s'][0], searches['upper']['final_s'][1]
    lower_proof = comparison(pair(lo)['lower'], epsilon, '>')
    upper_proof = comparison(pair(hi)['upper'], epsilon, '<=')
    if not lower_proof['passed'] or not upper_proof['passed'] or lo > hi:
        raise MomentError('HORIZON_ENDPOINT_FAILURE', representation)
    return dict(status='EXACT_RECORDED_MOMENT_ENCLOSING_BRACKET', representation=representation,
                fraction=f, threshold=epsilon, lower_s=lo, upper_s=hi,
                lower_years=F(lo,31557600), upper_years=F(hi,31557600),
                lower_margin=lower_proof['signed_margin'], upper_margin=-upper_proof['signed_margin'],
                lower_endpoint_proof=lower_proof, upper_endpoint_proof=upper_proof,
                lower_endpoint=envelope(model,representation,lo),
                upper_endpoint=envelope(model,representation,hi), searches=searches)


def serializable(value):
    """Exact numerator/denominator data; decimal string is display convenience."""
    if isinstance(value, F):
        with localcontext() as context:
            context.prec = 24
            convenience = str(Decimal(value.numerator)/Decimal(value.denominator))
        return dict(numerator=value.numerator, denominator=value.denominator,
                    decimal_convenience=convenience)
    if isinstance(value, dict):
        return {key: serializable(item) for key,item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    return value
