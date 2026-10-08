"""Rational enclosures of log of an exact positive number, with explicit tails."""
from fractions import Fraction as F
from functools import lru_cache

def _unit_log(x:F,terms:int)->tuple[F,F]:
    # 1 <= x <= 2 gives 0 <= y <= 1/3.
    y=(x-1)/(x+1);p=y;total=F(0);y2=y*y
    for k in range(terms):
        total+=2*p/(2*k+1);p*=y2
    tail=2*p/((2*terms+1)*(1-y2))
    return total,total+tail

@lru_cache(maxsize=32)
def log_interval(x:F,terms:int=90)->tuple[F,F]:
    if type(x) is not F or x<=0 or type(terms) is not int or terms<1:
        raise ValueError('POSITIVE_FRACTION_AND_POSITIVE_INTEGER_TERMS_REQUIRED')
    k=0;v=x
    while v>=2:v/=2;k+=1
    while v<1:v*=2;k-=1
    l,u=_unit_log(v,terms);a,b=_unit_log(F(2),terms)
    if k>=0:return l+k*a,u+k*b
    return l+k*b,u+k*a

def dyadic_enclose(box:tuple[F,F],bits:int=192)->tuple[F,F]:
    """Outward rounding only; proved bounds are never narrowed."""
    if (len(box)!=2 or any(type(v) is not F for v in box) or box[0]>box[1]
            or type(bits) is not int or bits<1):
        raise ValueError('DYADIC_ENCLOSURE_DOMAIN')
    d=1<<bits
    l=box[0]*d;u=box[1]*d
    return F(l.numerator//l.denominator,d),F(-((-u.numerator)//u.denominator),d)

@lru_cache(maxsize=32)
def compact_log(x:F,terms:int=90)->tuple[F,F]:
    return dyadic_enclose(log_interval(x,terms),192)

def event_interval(eta:F,energy:F,terms:int=90)->tuple[F,F]:
    if type(eta) is not F:raise ValueError('EXACT_ETA_REQUIRED')
    l,u=compact_log(energy,terms);return eta-u,eta-l
