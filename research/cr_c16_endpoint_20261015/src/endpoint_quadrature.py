"""C16 positive endpoint-weighted exponential photon source and sink.

Mathematical subproblem: proper interval dt, linearly interpolated
nonnegative species opacity lambda_j(t) and nonnegative endpoint-linear
source S(t). Existing photon packet undergoes exact attenuation under
the linear total rate.

Two paths:
- endpoint_weighted: positive exponential approximation, second order
  for smooth data and stiff-endpoint-consistent when final lambda>0.
- optical_quadrature: vectorized positive 64-node quadrature in retarded
  optical scale, near-exact photon survivor for piecewise-linear source
  and total opacity (no assumption that lambda(t) is frozen).

Species events are allocated with positive integrated/effective opacity
fractions; the TOTAL photon conservation is exact to roundoff. Species
branching under variable opacity is an approximation, not exact atomic
event kinetics. No full rei_bianchi spatial/angular flux is solved.
"""
from __future__ import annotations
import numpy as np
from numpy.polynomial.legendre import leggauss
from exponential_source import phi_neg
from linear_source import phi2_neg


def retarded_fraction(tau):
    """Mean retarded fraction (dt-t_birth)/dt in a constant-opacity measure."""
    x=np.asarray(tau,float)
    if np.any(x<0) or not np.all(np.isfinite(x)):
        raise ValueError("tau must be finite nonnegative")
    w=np.empty_like(x)
    sm=x<=1e-3
    z=x[sm]
    w[sm]=.5+z*(-1/12.+z*z*(1/720.-z*z/30240.))
    z=x[~sm]
    val=np.empty_like(z)
    high=z>50.
    val[high]=1/z[high]
    val[~high]=1/z[~high]-1/np.expm1(z[~high])
    w[~sm]=val
    return w


def source_moments(tau):
    """Positive survival and absorption weights for linear source endpoints.

    Survivor S0 weight = int_0^1 (1-u) exp[-tau(1-u)]du
    Survivor S1 weight = int_0^1 u exp[-tau(1-u)]du
    Their absorbed counterparts are (1/2 - survivor), evaluated stably.
    """
    x=np.asarray(tau,float)
    phi1=phi_neg(x)
    phi2=phi2_neg(x)
    w0=phi1-phi2
    w1=phi2
    l0=np.empty_like(x);l1=np.empty_like(x)
    sm=x<=1e-4
    z=x[sm]
    l0[sm]=z*(1/3.+z*(-1/8.+z*(1/30.+z*(-1/144.+z/840.))))
    l1[sm]=z*(1/6.+z*(-1/24.+z*(1/120.+z*(-1/720.+z/5040.))))
    l0[~sm]=.5-w0[~sm]
    l1[~sm]=.5-w1[~sm]
    return w0,w1,l0,l1


def _checked(photons,s0,s1,r0,r1,dt):
    N=np.asarray(photons,float)
    a=np.asarray(s0,float);b=np.asarray(s1,float)
    L0=np.asarray(r0,float);L1=np.asarray(r1,float)
    if N.ndim!=1 or a.shape!=N.shape or b.shape!=N.shape or L0.ndim!=2 or L1.shape!=L0.shape or L0.shape[0]!=len(N):
        raise ValueError("requires [packet] stock/source, [packet,species] endpoints")
    if dt<=0 or not np.isfinite(dt) or any(np.any(v<0) or not np.all(np.isfinite(v)) for v in (N,a,b,L0,L1)):
        raise ValueError("positive proper dt and nonnegative finite data")
    return N,a,b,L0,L1


def _output(N,s0,s1,r0,r1,dt,source_survived,source_effective_rates):
    rate_bar=.5*(r0+r1)
    lb=rate_bar.sum(axis=1)
    # Exact attenuation of the INITIAL photon stock for a linear rate.
    survivor_old=N*np.exp(-dt*lb)
    old_lost=N*(-np.expm1(-dt*lb))
    birth_lost=dt*.5*(s0+s1)-source_survived
    tolerance=1e-11*np.maximum(1.,dt*(s0+s1))
    if np.any(birth_lost < -tolerance):
        raise ArithmeticError("negative absorbed photon birth count")
    # Floating point cancellation can give tiny negative residual at tau~0,
    # but the owner event ledger is protected by tolerance and exact zero.
    birth_lost=np.maximum(birth_lost,0.)
    br_old=np.zeros_like(rate_bar)
    np.divide(rate_bar,lb[:,None],out=br_old,where=lb[:,None]>0)
    le=source_effective_rates.sum(axis=1)
    br_new=np.zeros_like(source_effective_rates)
    np.divide(source_effective_rates,le[:,None],out=br_new,where=le[:,None]>0)
    events=old_lost[:,None]*br_old+birth_lost[:,None]*br_new
    end=survivor_old+source_survived
    return end,events


def endpoint_weighted(photons,s0,s1,lambda_start,lambda_end,dt):
    """Fast endpoint-consistent positive exponential approximation."""
    N,a,b,r0,r1=_checked(photons,s0,s1,lambda_start,lambda_end,dt)
    total0=r0.sum(axis=1);total1=r1.sum(axis=1)
    tau=.5*dt*(total0+total1)
    w=retarded_fraction(tau)
    eff=r1+(r0-r1)*w[:,None]
    tw=dt*eff.sum(axis=1)
    survival0,survival1,_,_=source_moments(tw)
    new=dt*(a*survival0+b*survival1)
    return _output(N,a,b,r0,r1,dt,new,eff)


def optical_quadrature(photons,s0,s1,lambda_start,lambda_end,dt,nodes=64):
    """Positive integration of LINEAR time-variable opacity/source.

    Integration variable is the retarded optical scale x=scale*u,
    u=(dt-t_birth)/dt.  scale=max(1,dt*lambda_end,
    sqrt(dt*lambda_start)). For large tau integrate only x<=80:
    the nonnegative linear-rate integrand's unintegrated tail is
    exponentially small in this transformed variable. It is not an
    interval bound certified for all infinite opacities.
    """
    N,a,b,r0,r1=_checked(photons,s0,s1,lambda_start,lambda_end,dt)
    total0=r0.sum(axis=1);total1=r1.sum(axis=1)
    scale=np.maximum(1.,np.maximum(dt*total1,np.sqrt(dt*total0)))
    xmax=np.minimum(scale,80.)
    x,w=leggauss(nodes)
    z=.5*xmax[:,None]*(1+x[None,:])
    u=z/scale[:,None]
    exponent=dt*(total1[:,None]*u+
                 .5*(total0-total1)[:,None]*u*u)
    emitting=b[:,None]+(a-b)[:,None]*u
    integral=.5*xmax/scale*np.sum(
        w[None,:]*emitting*np.exp(-exponent),axis=1)
    source_survivor=dt*integral
    # Species allocation is approximate, but positive and conserves the
    # total event count. Reuse a weighted opacity approximant; changing
    # just this branch distribution never alters radiation stock.
    tw=.5*dt*(total0+total1)
    backward=retarded_fraction(tw)
    effective=r1+(r0-r1)*backward[:,None]
    return _output(N,a,b,r0,r1,dt,source_survivor,effective)


if __name__=="__main__":
    import json
    l0=np.array([[2000.,30.,5.]])
    l1=np.array([[1000.,10.,3.]])
    inp=(np.array([0.]),np.array([.2]),np.array([.3]),l0,l1,1.)
    for method in (endpoint_weighted,optical_quadrature):
        n,e=method(*inp)
        print(json.dumps({"method":method.__name__,
              "photon_stock":n.tolist(),"events":e.tolist(),
              "number_residual":(inp[0]+.5*(inp[1]+inp[2])-n-e.sum(axis=1)).tolist()}))