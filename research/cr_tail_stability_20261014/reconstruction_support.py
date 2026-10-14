"""Read-only exact arithmetic support for REI history comparisons.

No ODE, mutation, launch authorization or source-specific curvature is inferred.
Fraction values are exact; float inputs mean their stored binary64 values.
LN_A knots are the supplied numbers, not an assertion about exact transcendental
logarithms. A norm of reconstructions is not an IVP error certificate.
"""
from fractions import Fraction
from math import isfinite
from typing import Iterable, Sequence


def q(value) -> Fraction:
    if isinstance(value, bool): raise ValueError('boolean is not a numeric witness')
    if isinstance(value, float):
        if not isfinite(value): raise ValueError('finite number required')
        return Fraction.from_float(value)
    try: return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as e:
        raise ValueError('finite rational-compatible number required') from e


def interpolation_envelope(a,b,x,curvature,eps_left,eps_right,jumps=()):
    """Peano/Green bound conditional on a genuine SAME-SOURCE whole-cell witness.

    curvature bounds |d^2 O/d coordinate^2| away from the explicitly listed
    slope jumps. (location,magnitude) jump entries are nonnegative upper bounds.
    Missing node errors or curvature remain UNKNOWN, never silently zero.
    """
    a,b,x=map(q,(a,b,x))
    if not a<b or not a<=x<=b:raise ValueError('ordered cell, no extrapolation')
    if curvature is None:return {'status':'UNKNOWN_MISSING_CURVATURE_WITNESS','radius':None,'cell_integral_radius':None}
    if eps_left is None or eps_right is None:return {'status':'UNKNOWN_MISSING_NODE_WITNESS','radius':None,'cell_integral_radius':None}
    M,el,er=map(q,(curvature,eps_left,eps_right))
    if min(M,el,er)<0:raise ValueError('negative upper bound')
    h=b-a;t=(x-a)/h
    radius=(1-t)*el+t*er+M*(x-a)*(b-x)/2
    integrated=h*(el+er)/2+M*h**3/12
    for location,magnitude in jumps:
        s,J=q(location),q(magnitude)
        if not a<s<b or J<0:raise ValueError('jump must be interior with nonnegative bound')
        radius+=J*(min(x,s)-a)*(b-max(x,s))/h
        integrated+=J*(s-a)*(b-s)/2
    return {'status':'CONDITIONAL_SAME_SOURCE_WITNESS_BOUND','radius':radius,'cell_integral_radius':integrated}


def curvature_in_ln_a(max_abs_Ott,max_abs_Ot,min_H,max_abs_Ht):
    """H=d ln(a)/dt; output conditional bound in ln(a), no change of age origin."""
    if any(v is None for v in (max_abs_Ott,max_abs_Ot,min_H,max_abs_Ht)):return None
    ott,ot,h,ht=map(q,(max_abs_Ott,max_abs_Ot,min_H,max_abs_Ht))
    if h<=0 or min(ott,ot,ht)<0:raise ValueError('H>0 and nonnegative bounds required')
    return ott/h**2+ot*ht/h**3


def _points(points):
    out=[(q(x),q(y)) for x,y in points]
    if len(out)<2 or any(x1>=x2 for (x1,_),(x2,_) in zip(out,out[1:])):
        raise ValueError('at least two strictly increasing knots required')
    return out


def reconstruction_norm(reference:Sequence, candidate:Sequence, coordinate:str):
    """Exact sup of two PL reconstructions over equal represented endpoints.

    The extremum occurs at the union of the knots, so a 1001-point sampling grid
    is unnecessary. Runtime O(n+m), output does not duplicate full input arrays.
    Caller owns actual file hashes, completion, source/clock identity and species
    normalization. This helper never substitutes for those owner validations.
    """
    if coordinate not in ('LN_A','PROPER_TIME'):
        raise ValueError('choose one explicit coordinate: LN_A or PROPER_TIME')
    r,c=_points(reference),_points(candidate)
    if r[0][0]!=c[0][0] or r[-1][0]!=c[-1][0]:
        raise ValueError('same represented endpoints required; no extrapolation or silent overlap')
    i=j=0;nr=nc=0;maximum=Fraction(-1);arg=None;signed=None;visited=0
    while nr<len(r) or nc<len(c):
        xr=r[nr][0] if nr<len(r) else None;xc=c[nc][0] if nc<len(c) else None
        x=xc if xr is None else xr if xc is None else min(xr,xc)
        if xr==x:nr+=1
        if xc==x:nc+=1
        while i+1<len(r)-1 and r[i+1][0]<x:i+=1
        while j+1<len(c)-1 and c[j+1][0]<x:j+=1
        def interp(p,k):
            a,u=p[k];b,v=p[k+1]
            if not a<=x<=b:raise ArithmeticError('internal bracket failure')
            return u+(v-u)*(x-a)/(b-a)
        delta=interp(c,j)-interp(r,i);visited+=1
        if abs(delta)>maximum:maximum,arg,signed=abs(delta),x,delta
    return dict(status='EXACT_DYADIC_RECONSTRUCTION_NORM_ONLY',coordinate=coordinate,
        sup_absolute_difference=maximum,coordinate_at_sup=arg,signed_difference_at_sup=signed,
        endpoint_difference=c[-1][1]-r[-1][1],union_knots=visited,
        true_ivp_error=None,interpolation_error=None,solver_launch_authorized=False)


def readiness(owner_snapshot:dict):
    """Availability of this supplier is not permission to change an owner DAG."""
    blockers=[]
    if owner_snapshot.get('live_owner_or_workers') is not False:blockers.append('OWNER_LIFECYCLE_NOT_CLOSED')
    if owner_snapshot.get('five_baselines_complete') is not True:blockers.append('BASELINE_FAMILY_INCOMPLETE')
    if owner_snapshot.get('owner_execution_authorized') is not True:blockers.append('OWNER_EXECUTION_AUTHORIZATION_ABSENT')
    return dict(supplier_interface_ready=True,owner_dispatch_ready=not blockers,blockers=blockers,
                owner_state_mutated=False,launch_performed=False)
