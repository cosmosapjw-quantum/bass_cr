"""Curvature-controlled source-specific two-cohort H/He photoevent and heat errors.

A same-ray, same-birth-owner positive merge conserves N and sum(N E).  Away
from all three Verner fit thresholds throughout a redshift tube, Taylor with
weighted first-moment cancellation yields a second-order *absolute* bound for
each frozen-neutral backward-Euler photoevent and direct photoelectron heat.

These are analytic real-domain sufficient inequalities evaluated in binary64;
float operations are NOT a correctly directed interval certificate.  They do
not bind the nonlinear gas/chemistry evolution or change a physical source ID.
"""
from __future__ import annotations
from math import sqrt, hypot, isfinite
from dataclasses import replace
from typing import Sequence

from threshold_rt import ATOMIC, ION_NAMES, C_CM_S, SOURCE_EDGES
from compressed_cohorts import (_validate_neutrals, _min_dist, _verner_derivative_bound,
                                CompressionHold, CompressionCertificate)
from fast_compression import HeapCompressedCohortTransport


NUMERICAL_CUSHION = 1.000000001


def verner_two_derivative_bounds(kind: str, lo: float, hi: float):
    """Safe analytic *real-valued* envelope of sigma, |sigma'|, |sigma''|.

    Equalities at fit thresholds are understood from the active side. Smooth
    open intervals must not straddle the He photoionization cutoff.
    """
    smax, dmax = _verner_derivative_bound(kind, lo, hi)
    eth, e0, s0, ya, p, yw, y0, y1 = ATOMIC[kind]
    if hi < eth:
        return (0., 0., 0.)
    if lo < eth <= hi:
        raise CompressionHold('HOLD_THRESHOLD_IN_CURVATURE_TUBE')
    x0, x1 = lo / e0 - y0, hi / e0 - y0
    xmax = max(abs(x0), abs(x1))
    xm1max = max(abs(x0 - 1.), abs(x1 - 1.))
    ymin = hypot(_min_dist(x0, x1, 0.), y1)
    amin = _min_dist(x0, x1, 1.)**2 + yw*yw
    if ymin <= 0 or amin <= 0:
        raise CompressionHold('HOLD_SINGULAR_VERNER_CURVATURE')
    v = p/2. - 5.5
    # d²(log sigma)/dE² follows from sigma = s0*((x-1)²+yw²)*
    #   y^v*(1+sqrt(y/ya))^-p, x=E/e0-y0, y=hypot(x,y1).
    # z/(1+z) <= 1; z/(1+z)^2 <=1/4 for z>=0.
    A = (2./amin + 4.*xm1max*xm1max/(amin*amin)) / (e0*e0)
    B = abs(v)*(y1*y1+xmax*xmax)/(e0*e0*ymin**4)
    C = (p/(2*e0*e0)) * ((y1*y1+xmax*xmax)/(ymin**4)
                              +xmax*xmax/(8*ymin**4))
    second_log = A + B + C
    # From sigma'' = sigma[(log sigma)'² + (log sigma)''].
    sigma_second = smax * ( (dmax/smax)**2 + second_log )
    if not (isfinite(sigma_second) and sigma_second>=0):
        raise CompressionHold('HOLD_NONFINITE_SECOND_DERIVATIVE')
    return (smax, dmax, sigma_second*NUMERICAL_CUSHION)


def curvature_pair_bounds(e1:float,n1:float,e2:float,n2:float,
                          neutrals_cm3:Sequence[float],dt_s:float,
                          min_future_redshift_ratio:float,
                          binding_eV:Sequence[float] | None=None):
    """Second-order frozen-neutral bound on each species BE events and heat.

    For any r in [rmin,1], N=n1+n2, em=(n1*e1+n2*e2)/N,
    |n1*g(re1)+n2*g(re2)-N*g(r em)| <= .5 sup|g''| *
                              (n1*n2/N)*(e2-e1)^2*r^2.
    This is a smooth same-threshold-tube exact-real bound; no gas feedback.
    """
    nn=_validate_neutrals(neutrals_cm3,dt_s)
    binding=tuple(ATOMIC[i][0] for i in ION_NAMES) if binding_eV is None else tuple(binding_eV)
    if len(binding)!=3 or any(not isfinite(v) or not (0<=v<=ATOMIC[ion][0])
                              for ion,v in zip(ION_NAMES,binding)):
        raise ValueError('binding energies must be finite nonnegative and <= fit cutoffs')
    if not(isfinite(min_future_redshift_ratio) and
           0<min_future_redshift_ratio<=1):
        raise ValueError('invalid redshift tube')
    if not all(isfinite(x) for x in (e1,n1,e2,n2)) or not(
        0<e1<=e2<=50000 and n1>=0 and n2>=0):
        raise ValueError('invalid positive ordered cohorts')
    total=n1+n2
    if not total or e1==e2:
        return (0.,)*3,(0.,)*3
    lo=min_future_redshift_ratio*e1
    hi=e2
    if lo<SOURCE_EDGES[0]:
        raise CompressionHold('HOLD_FORECAST_BELOW_MIN_ENERGY')
    # Species-independent kinematics and threshold checks MUST be evaluated even
    # when current neutral density=0: future chemistry may activate that species.
    for ion in ION_NAMES:
        if lo<ATOMIC[ion][0]<=hi:
            raise CompressionHold('HOLD_THRESHOLD_IN_FORECAST_TUBE')
    B0=[];B1=[];B2=[];active=[]
    for ion,dens in zip(ION_NAMES,nn):
        is_active=(lo>=ATOMIC[ion][0])
        active.append(is_active)
        if not is_active:
            B0.append(0.);B1.append(0.);B2.append(0.)
            continue
        s0,s1,s2=verner_two_derivative_bounds(ion,lo,hi)
        factor=dt_s*C_CM_S*dens
        B0.append(factor*s0)
        B1.append(factor*s1)
        B2.append(factor*s2)
    T1=sum(B1);T2=sum(B2)
    # A generous but explicit derivative bound of beta_k/(1+sum beta_j).
    # The common denominator is >=1 throughout, all beta_j>=0.
    variance=(n1*n2/total)*(e2-e1)**2
    if not isfinite(variance):
        raise CompressionHold('HOLD_NONFINITE_MERGE_VARIANCE')
    events=[];heats=[]
    for k,is_active in enumerate(active):
        if not is_active:
            events.append(0.);heats.append(0.);continue
        f1=B1[k]+B0[k]*T1
        f2=B2[k]+2*B1[k]*T1+B0[k]*T2+2*B0[k]*T1*T1
        h2=2*f1+(hi-binding[k])*f2
        events.append(0.5*variance*f2*NUMERICAL_CUSHION)
        heats.append(0.5*variance*h2*NUMERICAL_CUSHION)
    if not all(isfinite(v) and v>=0 for v in [*events,*heats]):
        raise CompressionHold('HOLD_NONFINITE_CURVATURE_ENVELOPE')
    return tuple(events),tuple(heats)


class CurvatureHeapCompressedCohortTransport(HeapCompressedCohortTransport):
    """Curvature-gated heap with same owner-key policy as fast_compression.

    H>0 and long-term physical review must use independent source-side
    acceptance. This certificate is not directed and is only for frozen neutrals.
    """
    _pair_bounds=staticmethod(curvature_pair_bounds)

    def compress(self,*args,**kwargs):
        cert=super().compress(*args,**kwargs)
        upgraded=replace(cert, status='CURVATURE_FROZEN_NEUTRAL_BE_REAL_FORMULA_FLOAT_EVALUATED')
        self.last_certificate=upgraded
        return upgraded


def frozen_be_readout_binding(cohorts, neutrals_cm3, dt_s, ratio=1.,
                              binding_eV=(13.598434599702,24.587389011,54.41776)):
    """Distinct physical binding/fit-cutoff BE readout, source IGM owner adapter.

    Sigma Verner is always 0 below fit cutoff; event heats use binding energy.
    No source q Jacobian or nonlinear gas dynamics here.
    """
    from compressed_cohorts import frozen_be_readout
    from threshold_rt import verner, C_CM_S
    nn=_validate_neutrals(neutrals_cm3,dt_s)
    b=tuple(binding_eV)
    if len(b)!=3 or any(not isfinite(z) or z<0 or z>ATOMIC[k][0] for k,z in zip(ION_NAMES,b)):
        raise ValueError('invalid physical binding energies')
    if not isfinite(ratio) or ratio<=0: raise ValueError('invalid ratio')
    ev=[0.]*3;heat=[0.]*3
    for energy,n in cohorts:
        E=ratio*energy
        if E<SOURCE_EDGES[0]:continue
        if not(isfinite(E) and 0<E<=50000 and isfinite(n) and n>=0):
            raise ValueError('invalid photon')
        a=[dt_s*C_CM_S*rho*verner(ion,E) for rho,ion in zip(nn,ION_NAMES)]
        photons=n/(1+sum(a))
        for j,rate in enumerate(a):
            dn=photons*rate
            ev[j]+=dn
            heat[j]+=dn*(E-b[j])
    return tuple(ev),tuple(heat)
