#!/usr/bin/env python3
"""Analytic/finite-measure oracles only; no science G build or transport.

Standard-library Fraction exact arithmetic and Decimal 90-digit expressions.
These examples test the endpoint moment theorems; they do not fit bass_cr data.
"""
from __future__ import annotations
from decimal import Decimal as D, getcontext
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import time
import datetime

getcontext().prec = 90
ZERO, ONE, TWO = D(0), D(1), D(2)

def one_pole(x):
    e = (-x).exp()
    return ONE-(ONE-e)/x, ONE-TWO/x+TWO*(ONE-e)/(x*x)

def equal_two_poles(x):
    e = (-x).exp()
    return ONE-TWO/x+e*(ONE+TWO/x), ONE-D(4)/x+D(6)/(x*x)-e*(TWO/x+D(6)/(x*x))

def integral_series(x, order, moment):
    # E[(1-tau/T)^moment_+], normalized Erlang(order,lambda), order in {1,2}.
    # Taylor-expand exp(-xy) and integrate each monomial exactly on y in [0,1].
    term = ONE
    total = ZERO
    for k in range(2000):
        n = k+order
        if moment == 1:
            beta = ONE/(D(n)*D(n+1))
        else:
            beta = TWO/(D(n)*D(n+1)*D(n+2))
        addition = term*beta
        total += addition
        if k > 2*int(x)+50 and abs(addition) < D('1e-86'):
            return (x**order)*total
        term *= -x/D(k+1)
    raise ArithmeticError('SERIES_DID_NOT_CONVERGE')

def unequal_two_poles(x1, x2):
    a, b = one_pole(x1), one_pole(x2)
    return tuple((x2*a[k]-x1*b[k])/(x2-x1) for k in (0,1))

def envelope(r, s, c):
    v = s-r*r
    lo = max(ZERO, (r-c)/(ONE-c), (s-c*r)/(ONE-c))
    hi = min(ONE, r/c, s/(c*c), ((ONE+c)*r-s)/c)
    if c < r:
        lo = max(lo, (r-c)**2/(v+(r-c)**2))
    elif c > r:
        hi = min(hi, v/(v+(c-r)**2))
    return lo, hi

def mixture_with_moments(slow, r_target, s_target):
    rs, ss = one_pole(slow)
    def at_fast(fast):
        rf, sf = one_pole(fast)
        weight = (r_target-rs)/(rf-rs)
        return weight*sf+(ONE-weight)*ss, weight, rf, sf
    left, right = D('.1'), D(30)
    assert at_fast(left)[0] < s_target < at_fast(right)[0]
    for _ in range(240):
        mid = (left+right)/TWO
        if at_fast(mid)[0] < s_target:
            left = mid
        else:
            right = mid
    fast = (left+right)/TWO
    sm, w, rf, sf = at_fast(fast)
    rm = w*rf+(ONE-w)*rs
    assert ZERO < w < ONE and slow > ZERO and fast > ZERO
    return {'lambda_slow_times_T':str(slow), 'lambda_fast_times_T':str(fast),
            'fast_weight':str(w), 'R':str(rm), 'S':str(sm),
            'mean_uncapped_lag_over_T':str(w/fast+(ONE-w)/slow),
            'F_strict_T':str(w*(ONE-(-fast).exp())+(ONE-w)*(ONE-(-slow).exp())),
            'R_residual':str(rm-r_target), 'S_residual':str(sm-s_target)}

def run():
    checks, examples = [], {}
    r, s = F(1,8), F(1,10)
    p, x = r*r/s, s/r
    atomic = []
    for tail in (F(2),F(100),F(1000000)):
        points = [(p, ONE-D(x.numerator)/D(x.denominator)),
                  (1-p,D(tail.numerator)/D(tail.denominator))]
        # Exact Fraction check uses delays in units T.
        delays = [(p,1-x),(1-p,tail)]
        mr = sum(w*max(F(0),1-t) for w,t in delays)
        ms = sum(w*max(F(0),1-t)**2 for w,t in delays)
        assert mr == r and ms == s
        atomic.append({'delay_atoms_over_T':[str(t) for _,t in delays],
                       'weights':[str(w) for w,_ in delays],
                       'R':str(mr),'S':str(ms),'F_strict_T':str(p),
                       'mean_uncapped_lag_over_T':str(sum(w*t for w,t in delays))})
    xa = (r-s)/(1-r)
    w1 = (s-r*r)/(1-2*r+s)
    assert w1+(1-w1)*xa == r
    assert w1+(1-w1)*xa*xa == s
    assert 0 < xa < 1 and 0 < w1 < 1
    checks.append({'id':'exact_atomic_same_moments_arbitrary_tail','status':'PASS_EXACT'})
    examples['atomic_counterexample']={'R':str(r),'S':str(s),'minimum_reached_fraction':str(p),
        'tail_families':atomic,'no_tail_equivalent':{'X_atoms':['1',str(xa)],
        'weights':[str(w1),str(1-w1)],'F_strict_T':'1',
        'mean_uncapped_lag_over_T':str(1-r)}}

    diffs = []
    oracle_rows = []
    for order, analytic in ((1,one_pole),(2,equal_two_poles)):
        for x in map(D,('0.000001','0.1','1','10')):
            rr, ss = analytic(x)
            assert ZERO < rr < ONE and rr*rr < ss < rr
            err = max(abs(rr-integral_series(x,order,1)),abs(ss-integral_series(x,order,2)))
            diffs.append(err)
            assert err < D('1e-65')
            oracle_rows.append({'order':order,'lambda_times_T':str(x),'R':str(rr),'S':str(ss),
                                'analytic_vs_series_absolute_max':str(err)})
    checks.append({'id':'pole_closed_forms_vs_independent_integrated_series','status':'PASS_NUMERICAL_90_DIGIT',
                   'max_abs_error':str(max(diffs)),'tolerance':'1e-65'})
    near = unequal_two_poles(ONE,ONE+D('1e-20'))
    eq = equal_two_poles(ONE)
    nd = max(abs(a-b) for a,b in zip(near,eq))
    assert nd < D('1e-20')
    checks.append({'id':'two_stage_equal_rate_limit','status':'PASS_NUMERICAL_90_DIGIT',
                   'rate_relative_separation':'1e-20','max_abs_difference':str(nd),'tolerance':'1e-20'})
    examples['pole_oracles'] = oracle_rows

    mixture = [mixture_with_moments(D(z),D(1)/8,D(1)/10) for z in ('1e-2','1e-5','1e-8')]
    max_moment_resid = max(max(abs(D(row['R_residual'])),abs(D(row['S_residual']))) for row in mixture)
    assert max_moment_resid < D('1e-60')
    mean_span = D(mixture[-1]['mean_uncapped_lag_over_T'])/D(mixture[0]['mean_uncapped_lag_over_T'])
    assert mean_span > D('1e5')
    checks.append({'id':'positive_stable_two_parallel_poles_same_endpoint_moments','status':'PASS_NUMERICAL_90_DIGIT',
                   'max_abs_moment_residual':str(max_moment_resid),'tolerance':'1e-60',
                   'uncapped_mean_ratio_last_to_first':str(mean_span)})
    examples['positive_two_pole_counterexample'] = mixture

    bounds_count = 0
    for row in oracle_rows:
        x,rr,ss = D(row['lambda_times_T']),D(row['R']),D(row['S'])
        for c in map(D,('.1','.25','.5','.75','.9')):
            lo,hi = envelope(rr,ss,c)
            y = x*(ONE-c)
            actual = ONE-(-y).exp()*(ONE+y if row['order']==2 else ONE)
            assert lo-D('1e-65') <= actual <= hi+D('1e-65')
            bounds_count += 1
    checks.append({'id':'quadratic_and_cantelli_cdf_envelopes_on_pole_oracles',
                   'status':'PASS_NUMERICAL_90_DIGIT','rows':bounds_count})
    return {'schema':'CR_PHYS02D_ENDPOINT_THEORY_ORACLES_V1',
            'scope':'Analytic toy models and exact finite measures only; no bass_cr scientific rerun.',
            'science_operator_builds':0,'science_transport_calls':0,
            'decimal_precision':getcontext().prec,'checks':checks,'examples':examples,
            'final_scientific_decision':'NOT_THIS_THEORY_CONTRIBUTOR_ROLE'}

if __name__ == '__main__':
    start = time.perf_counter()
    out = run()
    out['completed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out['wall_seconds'] = time.perf_counter()-start
    out['code_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    path = Path(__file__).with_name('ORACLE_RESULT.json')
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks':len(out['checks']),'status':'PASS_SCOPED_ORACLES',
                      'wall_seconds':out['wall_seconds'],'output':str(path)},ensure_ascii=False))
