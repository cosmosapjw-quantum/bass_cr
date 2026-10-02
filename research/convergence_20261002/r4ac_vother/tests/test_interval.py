from fractions import Fraction as F
import dyadic_interval as di

def test_sqrt2_encloses_and_resolves():
    lo,hi=di.sqrt_bounds(F(2))
    assert lo*lo <= 2 <= hi*hi
    assert hi-lo < F(1,10**80)

def test_log2_between_known_rational_bounds():
    lo,hi=di.log_bounds(F(2))
    assert F(69,100) < lo <= hi < F(7,10)
    assert hi-lo < F(1,10**80)

def test_rational_arithmetic_and_negative_division():
    I=di.Interval
    for a in (F(-7,3),F(1,7),F(23,19)):
        for b in (F(-11,5),F(3,17)):
            x,y=I.point(a),I.point(b)
            for r,q in ((x+y,a+b),(x-y,a-b),(x*y,a*b),(x/y,a/b)):
                assert r.contains(q)
    import pytest
    with pytest.raises(ZeroDivisionError):1/I.bounds(-1,1)
    with pytest.raises(ValueError):I.point(-1).sqrt()
    with pytest.raises(ValueError):I.point(3).log()

def test_log_sqrt_against_high_precision_synthetic_oracle():
    import mpmath as mp
    with mp.workdps(130):
        for q in (F(1,2),F(3,4),F(1),F(13,8),F(2)):
            for fn,oracle in ((di.sqrt_bounds,mp.sqrt),(di.log_bounds,mp.log)):
                lo,hi=fn(q);r=F(mp.nstr(oracle(mp.mpf(q.numerator)/q.denominator),125))
                assert lo<=r<=hi
