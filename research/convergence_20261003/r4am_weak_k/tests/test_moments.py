from fractions import Fraction as F
from math import factorial
import pytest
import mpmath as mp
from moments import moment,moment_upper,P,U,V
from complex_box import C
from dyadic import I,SCALE

AB=[(a,b) for a in range(5) for b in range(5-a)]
@pytest.mark.parametrize('a,b',AB)
def test_zero_phase_monomial_exact(a,b):
    q=F(3,2);m=moment(a,b,q,0)
    if a%2 or b%2:exact=F(0)
    else:
        r,s=a//2,b//2;exact=q**(r+s)*F(factorial(2*r)*factorial(2*s),4**(r+s)*factorial(r)*factorial(s)*factorial(r+s))
    assert m.re.contains(exact) and m.im.contains(0)

@pytest.mark.parametrize('a,b',AB)
def test_real_moment_matches_independent_angle_integral(a,b):
    with mp.workdps(70):
        Q=mp.mpf('1.7');k=mp.mpf('0.8');r=mp.sqrt(Q)
        ref=mp.quad(lambda th:(r*mp.cos(th))**a*(r*mp.sin(th))**b*mp.exp(1j*k*r*mp.cos(th)),[0,mp.pi,2*mp.pi])/(2*mp.pi)
        m=moment(a,b,F(17,10),F(4,5));mid=mp.mpc(str(m.re.mid()),str(m.im.mid())) if False else mp.mpc(mp.mpf(m.re.mid().numerator)/m.re.mid().denominator,mp.mpf(m.im.mid().numerator)/m.im.mid().denominator)
        assert abs(mid-ref)<mp.mpf('1e-60')

@pytest.mark.parametrize('a,b',AB)
def test_complex_majorant_exceeds_sampled_entire_series(a,b):
    with mp.workdps(60):
        Q=mp.mpc('1.3','0.4');k=mp.mpc('0.6','-0.1');r=mp.sqrt(Q)
        ref=mp.quad(lambda th:(r*mp.cos(th))**a*(r*mp.sin(th))**b*mp.exp(1j*k*r*mp.cos(th)),[0,mp.pi,2*mp.pi])/(2*mp.pi)
        bnd=moment_upper(a,b,C(F(13,10),F(2,5)),C(F(3,5),F(-1,10)))
        upper=mp.mpf(bnd.hi)/SCALE
        assert abs(ref)<=upper+mp.mpf('1e-55')

@pytest.mark.parametrize('args',[(5,0,1,0),(0,-1,1,0),(1,0,-1,0),(1.0,0,1,0)])
def test_unregistered_moment_inputs_rejected(args):
    with pytest.raises(ValueError):moment(*args)

def test_odd_transverse_sine_is_identically_zero():
    q=moment(1,3,I.bounds(0,100),I.bounds(-10,10));assert q.re.iszero() and q.im.iszero()

def test_collinear_limit_has_only_constant_moment():
    for a,b in AB:
        m=moment(a,b,0,F(17,3));assert m.re.contains(1 if a+b==0 else 0) and m.im.contains(0)
