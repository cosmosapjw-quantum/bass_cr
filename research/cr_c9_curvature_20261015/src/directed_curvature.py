"""High-precision upward Decimal evaluation of analytic Verner curvature bounds.

Input floats are treated as EXACT DYADIC fixed-source data. All rational
arithmetic uses 85-digit Decimal directed ceilings/floors. Decimal.exp/ln/sqrt
are correctly rounded to half even by the Python decimal context; outward
next_plus/next_minus brackets them. The returned binary64 is nextafter toward
+inf. This encloses the stated *analytic sufficient bound* with this arithmetic
model. It is not a validated native IVP/coupled history, nor a proof of an
uncertainty interval for measured physical atomic constants.
"""
from __future__ import annotations
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN, localcontext
from math import isfinite, nextafter, inf
from typing import Sequence
from dataclasses import replace
from functools import lru_cache
from compressed_cohorts import _validate_neutrals, CompressionHold
from threshold_rt import ATOMIC, ION_NAMES, C_CM_S, SOURCE_EDGES
from curvature_bounds import CurvatureHeapCompressedCohortTransport

PREC=85
D=Decimal.from_float
ZERO=Decimal(0)
ONE=Decimal(1)
TWO=Decimal(2)
FOUR=Decimal(4)
EIGHT=Decimal(8)
HALF=Decimal('0.5')
VERNER_SCALE=max(D(1e-18),Decimal('1e-18'))


def plus(a:Decimal,b:Decimal):
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_CEILING
        return a+b


def subup(a:Decimal,b:Decimal):
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_CEILING
        return a-b


def adddown(a:Decimal,b:Decimal):
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_FLOOR
        return a+b


def minus(a:Decimal,b:Decimal):
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_FLOOR
        return a-b


def times(a:Decimal,b:Decimal):
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_CEILING
        return a*b


def divup(a:Decimal,b:Decimal):
    if b<=0 or a<0:raise ValueError('upper quotient requires nonnegative numerator, positive denominator')
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_CEILING
        return a/b


def divlow(a:Decimal,b:Decimal):
    if b<=0 or a<0:raise ValueError('lower quotient requires nonnegative numerator, positive denominator')
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_FLOOR
        return a/b


def muldown(a:Decimal,b:Decimal):
    if a<0 or b<0:raise ValueError('lower product of positives required')
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_FLOOR
        return a*b


def sqrtbound(x:Decimal, upper:bool):
    if x<0:raise ValueError('negative sqrt')
    with localcontext() as c:
        c.prec=PREC
        v=x.sqrt()
        return v.next_plus(c) if upper else v.next_minus(c)


def xbounds(energy:Decimal,e0:Decimal,y0:Decimal):
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_FLOOR
        left=energy/e0-y0
        c.rounding=ROUND_CEILING
        right=energy/e0-y0
    return left,right


def scalar_upper_power(base_lower:Decimal, exponent:Decimal):
    if base_lower<=0:raise CompressionHold('HOLD_LOG_BASE')
    # Only used for negative powers, so the monotone upper is the lower base.
    if exponent>=0:raise ValueError('negative power expected')
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_HALF_EVEN
        lv=base_lower.ln()
        lowlog=lv.next_minus(c)
        c.rounding=ROUND_CEILING
        hi_exp=exponent*lowlog
        c.rounding=ROUND_HALF_EVEN
        value=hi_exp.exp()
        return value.next_plus(c)


@lru_cache(maxsize=4096)
def second_sigma_up(ion:str,lo:Decimal,hi:Decimal):
    eth_f,e0_f,s0_f,ya_f,p_f,yw_f,y0_f,y1_f=ATOMIC[ion]
    eth,e0,s0,ya,p,yw,y0,y1=map(D,(eth_f,e0_f,s0_f,ya_f,p_f,yw_f,y0_f,y1_f))
    if hi<eth:return ZERO,ZERO,ZERO
    if lo<eth<=hi:raise CompressionHold('HOLD_THRESHOLD_IN_DIRECTED_TUBE')
    x0l,x0r=xbounds(lo,e0,y0);x1l,x1r=xbounds(hi,e0,y0)
    X=max(abs(z) for z in (x0l,x0r,x1l,x1r))
    Xa=max(abs(z-ONE) for z in (x0l,x0r,x1l,x1r))
    dist0= -x1r if x1r<0 else x0l if x0l>0 else ZERO
    dist1= ONE-x1r if x1r<ONE else x0l-ONE if x0l>ONE else ZERO
    ymin=sqrtbound(plus(muldown(dist0,dist0),muldown(y1,y1)),False)
    amin=plus(muldown(dist1,dist1),muldown(yw,yw))
    # amin sum for lower must itself be downward, not upward.
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_FLOOR
        amin=dist1*dist1+yw*yw
        yarg=dist0*dist0+y1*y1
    ymin=sqrtbound(yarg,False)
    if ymin<=0 or amin<=0:raise CompressionHold('HOLD_SINGULAR_DIRECTED')
    amax=plus(times(Xa,Xa),times(yw,yw))
    with localcontext() as c:
        c.prec=PREC;c.rounding=ROUND_HALF_EVEN
        v=p/TWO-Decimal('5.5')
    if v>=0:
        ymax=sqrtbound(plus(times(X,X),times(y1,y1)),True)
        with localcontext() as c:
            c.prec=PREC;c.rounding=ROUND_HALF_EVEN
            logv=ymax.ln().next_plus(c)
            c.rounding=ROUND_CEILING;vlog=v*logv
            c.rounding=ROUND_HALF_EVEN
            power=vlog.exp().next_plus(c)
    else:
        power=scalar_upper_power(ymin,v)
    # (1+sqrt(y/ya))^-p <=1 (p>0). Original fit 1e-18 factor bounded.
    smax=times(times(times(s0,amax),power),VERNER_SCALE)
    # 1/e0 and 1/e0² upper bounds in positive directed context.
    e0inv=divup(ONE,e0)
    t1=divup(times(TWO,Xa),amin)
    t2=divup(times(plus(abs(v),divup(p,TWO)),X),muldown(ymin,ymin))
    log1=times(plus(t1,t2),e0inv)
    deriv1=times(smax,log1)
    A=plus(divup(TWO,amin),divup(times(FOUR,times(Xa,Xa)),muldown(amin,amin)))
    yp2=plus(times(y1,y1),times(X,X))
    ymin4=muldown(muldown(ymin,ymin),muldown(ymin,ymin))
    B=divup(times(abs(v),yp2),ymin4)
    C=times(divup(p,TWO),plus(divup(yp2,ymin4),divup(times(X,X),muldown(EIGHT,ymin4))))
    log2=times(plus(plus(A,B),C),times(e0inv,e0inv))
    deriv2=times(smax,plus(times(log1,log1),log2))
    return smax,deriv1,deriv2


def bounds_decimal(e1:float,n1:float,e2:float,n2:float,
                   neutrals_cm3:Sequence[float],dt_s:float,
                   min_future_redshift_ratio:float,
                   binding_eV:Sequence[float] | None=None):
    nn=_validate_neutrals(neutrals_cm3,dt_s)
    binding=tuple(ATOMIC[i][0] for i in ION_NAMES) if binding_eV is None else tuple(binding_eV)
    if len(binding)!=3 or any(not isfinite(v) or not (0<=v<=ATOMIC[ion][0])
                              for ion,v in zip(ION_NAMES,binding)):
        raise ValueError('binding energies must lie below fit cutoffs')
    if not(isfinite(min_future_redshift_ratio) and 0<min_future_redshift_ratio<=1):
        raise ValueError('invalid redshift factor')
    if not(all(isfinite(x) for x in (e1,n1,e2,n2)) and 0<e1<=e2<=50000 and n1>=0 and n2>=0):
        raise ValueError('invalid photon state')
    if n1+n2==0 or e1==e2:return (ZERO,)*3,(ZERO,)*3
    E1,E2,N1,N2=map(D,(e1,e2,n1,n2))
    lo=muldown(D(min_future_redshift_ratio),E1);hi=E2
    if lo<D(SOURCE_EDGES[0]):raise CompressionHold('HOLD_LOWER_BOUNDARY')
    for ion in ION_NAMES:
        if lo<D(ATOMIC[ion][0])<=hi:raise CompressionHold('HOLD_MOVING_THRESHOLD')
    B0=[];B1=[];B2=[];active=[]
    for ion,n in zip(ION_NAMES,nn):
        valid=lo>=D(ATOMIC[ion][0]);active.append(valid)
        if not valid:
            B0.append(ZERO);B1.append(ZERO);B2.append(ZERO);continue
        s0,s1,s2=second_sigma_up(ion,lo,hi)
        alpha=times(times(D(dt_s),D(C_CM_S)),D(n))
        B0.append(times(alpha,s0));B1.append(times(alpha,s1));B2.append(times(alpha,s2))
    T1=ZERO;T2=ZERO
    for x,y in zip(B1,B2):T1=plus(T1,x);T2=plus(T2,y)
    variance=times(divup(times(N1,N2),adddown(N1,N2)),times(subup(E2,E1),subup(E2,E1)))
    ev=[];heat=[]
    for k,valid in enumerate(active):
        if not valid:
            ev.append(ZERO);heat.append(ZERO);continue
        f1=plus(B1[k],times(B0[k],T1))
        f2=plus(plus(B2[k],times(TWO,times(B1[k],T1))),
                plus(times(B0[k],T2),times(TWO,times(B0[k],times(T1,T1)))))
        heat2=plus(times(TWO,f1),times(subup(hi,D(binding[k])),f2))
        ev.append(times(HALF,times(variance,f2)))
        heat.append(times(HALF,times(variance,heat2)))
    return tuple(ev),tuple(heat)


def bounds_up_f64(*args,**kwargs):
    ev,heat=bounds_decimal(*args,**kwargs)
    return (tuple((0.0 if e==ZERO else nextafter(float(e),inf)) for e in ev),
            tuple((0.0 if h==ZERO else nextafter(float(h),inf)) for h in heat))


class DirectedCurvatureHeap(CurvatureHeapCompressedCohortTransport):
    def __init__(self,cohorts,max_cohorts=32,binding_eV=None):
        super().__init__(cohorts,max_cohorts)
        self.binding_eV=None if binding_eV is None else tuple(binding_eV)

    def _pair_bounds(self,e1,n1,e2,n2,neutrals,dt_s,redshift):
        return bounds_up_f64(e1,n1,e2,n2,neutrals,dt_s,redshift,
                             binding_eV=self.binding_eV)
    _accum=staticmethod(lambda a,b: 0.0 if a+b==0 else nextafter(a+b,inf))
    def compress(self,*args,**kwargs):
        result=super().compress(*args,**kwargs)
        cert=replace(result,status='DYADIC_INPUT_DECIMAL85_UPPER_ENVELOPES_FROZEN_NEUTRAL_LOCAL')
        self.last_certificate=cert
        return cert

    def inject_and_compress(self,injection,neutrals_cm3,dt_s,
                            min_future_redshift_ratio=1.,event_abs_budget=.01,
                            heat_abs_budget_eV=.1):
        trial=type(self)([*self.cohorts,*injection],self.max_cohorts,
                         binding_eV=self.binding_eV)
        cert=trial.compress(neutrals_cm3,dt_s,min_future_redshift_ratio,
                            event_abs_budget,heat_abs_budget_eV)
        self.cohorts=trial.cohorts
        self.last_certificate=cert
        return cert
