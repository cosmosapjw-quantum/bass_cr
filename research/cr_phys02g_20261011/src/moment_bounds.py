"""Frozen nonnegative two-moment survival envelopes; scalar stdlib only.

Bounds apply to the strict event X>x. Raw FP64 results are never clipped.
"""
import math

ABS_TOL = 2e-14
REL_TOL = 2e-12
TIME_SCALE = 1e10


class MomentError(ValueError):
    """Typed rejection of a scalar probability representation."""
    def __init__(self, code, message):
        self.code = code
        super().__init__(f'{code}: {message}')


def _finite(value, name):
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise MomentError('NONFINITE_OR_NONSCALAR', name)
    return value


def bounds(mean, second, x):
    """Generic L/U for a nonnegative law with exact supplied first two moments."""
    a, b, x = (_finite(v, n) for v, n in
               ((mean, 'mean'), (second, 'second'), (x, 'x')))
    if a < 0 or b < 0 or x < 0:
        raise MomentError('NEGATIVE_INPUT', 'mean, second and threshold must be nonnegative')
    if a == 0 and b != 0:
        raise MomentError('ZERO_MEAN_POSITIVE_SECOND', 'nonnegative law impossible')
    v = b - a * a
    if not math.isfinite(v):
        raise MomentError('NONFINITE_ARITHMETIC', 'variance overflow')
    if v < 0:
        raise MomentError('NEGATIVE_VARIANCE', repr(v))
    if v == 0:
        value = 1.0 if x < a else 0.0
        return dict(lower=value, upper=value, variance=v, branch='DETERMINISTIC')
    lower = (a-x)**2 / (v+(a-x)**2) if x < a else 0.0
    if x <= a:
        upper, branch = 1.0, 'UPPER_ONE'
    elif x < b/a:
        upper, branch = a/x, 'UPPER_MARKOV'
    else:
        upper, branch = v/(v+(x-a)**2), 'UPPER_CANTELLI'
    if not all(math.isfinite(z) for z in (lower, upper)):
        raise MomentError('NONFINITE_ARITHMETIC', 'bound overflow')
    return dict(lower=lower, upper=upper, variance=v, branch=branch)


def comparison(actual, reference, scale=1.0, absolute=ABS_TOL, relative=REL_TOL):
    """Signed normalized residual; reports tolerance without changing values."""
    difference = (actual-reference)/scale
    reference_normalized = reference/scale
    limit = absolute + relative*abs(reference_normalized)
    return dict(actual=actual, reference=reference, scale=scale,
                signed_normalized=difference, tolerance=limit,
                pass_check=abs(difference) <= limit)


def _record(row, T):
    r = {k: _finite(row[k], k) for k in ('H0','p','R','S','mu_s','m2_s2')}
    if r['H0'] <= 0 or not 0 <= r['p'] <= 1:
        raise MomentError('INVALID_NORMALIZATION', 'H0>0 and p in[0,1] required')
    if r['R'] < 0 or r['S'] < 0:
        raise MomentError('NEGATIVE_INPUT', 'R/S')
    total = bounds(r['mu_s'], r['m2_s2'], 0)
    q = 1-r['p']
    r['q'] = q
    r['variance_s2'] = total['variance']
    if q == 0:
        r['tail_residual'] = dict(status='UNDEFINED_ZERO_TAIL', probability=0.0)
    else:
        raw1 = r['mu_s']-T*(1-r['R'])
        raw2 = r['m2_s2']-2*T*r['mu_s']+T*T*(1-r['S'])
        a, b = raw1/q, raw2/q
        if a <= 0:
            raise MomentError('INCOMPATIBLE_POSITIVE_RESIDUAL', 'q>0 requires strictly positive conditional mean')
        v = bounds(a,b,0)['variance']
        r['tail_residual'] = dict(status='DEFINED', probability=q, raw_m1_s=raw1,
                                  raw_m2_s2=raw2, mean_s=a, second_s2=b,
                                  variance_s2=v)
    r['saved_tail_checks'] = {}
    saved = row.get('tail_residual')
    if saved and q:
        for k, scale in (('probability',1),('raw_m1_s',TIME_SCALE),
                         ('raw_m2_s2',TIME_SCALE**2),('mean_s',TIME_SCALE),
                         ('second_s2',TIME_SCALE**2),('variance_s2',TIME_SCALE**2)):
            r['saved_tail_checks'][k] = comparison(r['tail_residual'][k],saved[k],scale)
            if not r['saved_tail_checks'][k]['pass_check']:
                raise MomentError('CACHED_RESIDUAL_MISMATCH', k)
    return r


def construct_model(cached_model, T):
    """Recompute residual moments from native F cached primitives, not saved tail."""
    T = _finite(T,'T')
    if T <= 0:
        raise MomentError('INVALID_T', 'T>0 required')
    birth = [_record(r,T) for r in cached_model['birth_columns']]
    if not birth:
        raise MomentError('EMPTY_BIRTH_MIXTURE', 'at least one birth required')
    selected = _record(cached_model['selected'],T)
    total_H0 = sum(r['H0'] for r in birth)
    weights = [r['H0']/total_H0 for r in birth]
    checks = {'H0': comparison(total_H0,selected['H0'],selected['H0'])}
    for key, scale in (('p',1),('R',1),('S',1),('mu_s',TIME_SCALE),('m2_s2',TIME_SCALE**2),('q',1)):
        checks[key] = comparison(sum(w*r[key] for w,r in zip(weights,birth)),selected[key],scale)
    if not all(c['pass_check'] for c in checks.values()):
        raise MomentError('BIRTH_MIXTURE_MISMATCH', 'cached selected primitives')
    return dict(T=T, birth_columns=birth, selected=selected, weights=weights,
                mixture_checks=checks)


def _residual(record, x):
    q = record['q']
    if q == 0:
        return dict(lower=0.0, upper=0.0, branch='UNDEFINED_ZERO_TAIL')
    if x == 0:
        return dict(lower=q, upper=q, branch='KNOWN_POSITIVE_RESIDUAL_ENDPOINT')
    r = record['tail_residual']
    b = bounds(r['mean_s'],r['second_s2'],x)
    return dict(lower=q*b['lower'],upper=q*b['upper'],branch=b['branch'])


def envelope(model, t):
    t = _finite(t,'t')
    T, s = model['T'], model['selected']
    if t < T:
        raise MomentError('THRESHOLD_BEFORE_CACHED_T', 'residual envelope requires t>=T')
    unconditional = bounds(s['mu_s'],s['m2_s2'],t)
    pooled = _residual(s,t-T)
    birth_parts = [_residual(r,t-T) for r in model['birth_columns']]
    birth = {key:sum(w*b[key] for w,b in zip(model['weights'],birth_parts))
             for key in ('lower','upper')}
    if t == T:
        intersection = dict(lower=s['q'],upper=s['q'],branch='KNOWN_SELECTED_TAIL_MASS')
    else:
        intersection = dict(lower=max(unconditional['lower'],pooled['lower'],birth['lower']),
                            upper=min(unconditional['upper'],pooled['upper'],birth['upper']))
    return dict(t_s=t, unconditional=unconditional, pooled_residual=pooled,
                birth_residual=birth, birth_components=birth_parts,
                intersection=intersection)


def horizon_brackets(model, f):
    """Conservative Q_f interval and certified bisection endpoint receipts."""
    f = _finite(f,'fraction')
    if not 0 < f < 1:
        raise MomentError('INVALID_FRACTION','0<f<1 required')
    T, s, eps = model['T'], model['selected'], 1-f
    if f <= s['p']:
        return dict(fraction=f, status='KNOWN_T_ANCHOR_ONLY', lower_s=0.0,upper_s=T,
                    threshold=eps, reason='No early-time curve supplied')
    get = lambda t,key:envelope(model,t)['intersection'][key]
    lower_low = T
    means = [s['mu_s']]+[r['tail_residual'].get('mean_s',0)+T for r in
                                     [s]+model['birth_columns']]
    lower_high = max(means+[T])*2
    lower_doubles = 0
    while get(lower_high,'lower') > eps:
        if lower_doubles >= 64:
            raise MomentError('HORIZON_SEARCH_EXHAUSTED','lower')
        lower_high *= 2
        lower_doubles += 1
    lower_initial = [lower_low,lower_high]
    lower_iterations = 0
    for _ in range(80):
        mid = (lower_low+lower_high)/2
        if mid in (lower_low,lower_high): break
        if get(mid,'lower') > eps: lower_low = mid
        else: lower_high = mid
        lower_iterations += 1
    upper_low = T
    upper_high = max(2*s['mu_s']/eps,math.nextafter(T,math.inf))
    upper_doubles = 0
    while get(upper_high,'upper') > eps:
        if upper_doubles >= 64:
            raise MomentError('HORIZON_SEARCH_EXHAUSTED','upper')
        upper_high *= 2
        upper_doubles += 1
    upper_initial = [upper_low,upper_high]
    upper_iterations = 0
    for _ in range(80):
        mid = (upper_low+upper_high)/2
        if mid in (upper_low,upper_high): break
        if get(mid,'upper') <= eps: upper_high = mid
        else: upper_low = mid
        upper_iterations += 1
    receipt = dict(fraction=f,status='ENCLOSING_MOMENT_BRACKET',threshold=eps,
                   lower_s=lower_low,upper_s=upper_high,
                   lower_value=get(lower_low,'lower'),upper_value=get(upper_high,'upper'),
                   lower_bisection=dict(initial=lower_initial,final=[lower_low,lower_high],
                       iterations=lower_iterations,doublings=lower_doubles,
                       endpoint_values=[get(lower_low,'lower'),get(lower_high,'lower')]),
                   upper_bisection=dict(initial=upper_initial,final=[upper_low,upper_high],
                       iterations=upper_iterations,doublings=upper_doubles,
                       endpoint_values=[get(upper_low,'upper'),get(upper_high,'upper')]))
    if not(receipt['lower_value']>eps and receipt['upper_value']<=eps and lower_low<=upper_high):
        raise MomentError('HORIZON_ENDPOINT_FAILURE',repr(receipt))
    return receipt
