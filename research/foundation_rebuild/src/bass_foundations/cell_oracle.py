#!/usr/bin/env python3
"""Arbitrary-position rectangular-cell Coulomb average, scalar reference only.

This computes integral_C 1/|r-R| d^3r / volume(C), without softening.
It does NOT discretize a wavefunction, propagate a state, or establish that
cell averaging improves an FFT-collocation Hamiltonian's continuum error.
The high-precision corner sum is an oracle for testing a future fast kernel,
NOT a 63-million-cell production implementation or an interval certificate.
"""
from __future__ import annotations
import argparse
import json
from itertools import product
from typing import Sequence
import mpmath as mp


def cell_mean_inverse_radius(lower: Sequence, upper: Sequence, *,
                             nucleus: Sequence=(0,0,0), digits: int=50):
    """Return a positive mpmath number, using Cartesian bounds in any units.

    Inputs are interpreted from their decimal strings; input uncertainty is
    not enclosed. Working precision includes a far-field cancellation guard.
    Invalid/collapsed cells, nonfinite numbers, and excessive conditioning
    are rejected. The singularity is integrable, including at a cell center.
    """
    if isinstance(digits,bool) or not isinstance(digits,int) or not 20<=digits<=150:
        raise ValueError('digits must be an integer in [20,150]')
    ctx=mp.mp.clone();ctx.dps=max(80,digits+30)
    def vector(v):
        if len(v)!=3:raise ValueError('exactly three Cartesian coordinates required')
        if any(isinstance(x,bool) for x in v):raise ValueError('Boolean coordinate')
        try: a=tuple(ctx.mpf(str(x)) for x in v)
        except (ValueError,TypeError) as exc:raise ValueError('invalid coordinate') from exc
        if not all(ctx.isfinite(x) for x in a):raise ValueError('finite coordinates required')
        return a
    lo,hi,R=vector(lower),vector(upper),vector(nucleus)
    widths=tuple(b-a for a,b in zip(lo,hi))
    if not all(w>0 for w in widths):raise ValueError('strictly ordered cell bounds required')
    radius=max([abs(x-r) for v in (lo,hi) for x,r in zip(v,R)]+list(widths))
    dynamic=max(0,int(ctx.ceil(ctx.log10(max(1,radius/min(widths))))))
    # A corner primitive is O(r^2); its eight-term difference is O(h^3/r).
    working=max(80,digits+3*dynamic+25)
    if working>600:raise ValueError('geometry conditioning exceeds reference precision cap')
    ctx.dps=working
    lo,hi,R=vector(lower),vector(upper),vector(nucleus)
    lo=tuple(x-r for x,r in zip(lo,R));hi=tuple(x-r for x,r in zip(hi,R))
    volume=ctx.fprod(b-a for a,b in zip(lo,hi))
    def primitive(x,y,z):
        if x==0 or y==0 or z==0:return ctx.zero
        sign=ctx.sign(x)*ctx.sign(y)*ctx.sign(z)
        a,b,c=abs(x),abs(y),abs(z);r=ctx.sqrt(a*a+b*b+c*c)
        logs=(a*b*ctx.asinh(c/ctx.sqrt(a*a+b*b))+
              b*c*ctx.asinh(a/ctx.sqrt(b*b+c*c))+
              c*a*ctx.asinh(b/ctx.sqrt(c*c+a*a)))
        angles=(a*a*ctx.atan(b*c/(a*r))+
                b*b*ctx.atan(a*c/(b*r))+
                c*c*ctx.atan(a*b/(c*r)))/2
        return sign*(logs-angles)
    terms=[]
    for ix in product((0,1),repeat=3):
        xyz=[(lo[j],hi[j])[ix[j]] for j in range(3)]
        terms.append((-1)**(3-sum(ix))*primitive(*xyz))
    answer=ctx.fsum(terms)/volume
    if not ctx.isfinite(answer) or answer<=0:
        raise ArithmeticError('positive finite Coulomb average not resolved')
    return answer


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lower',nargs=3,type=str,required=True)
    p.add_argument('--upper',nargs=3,type=str,required=True)
    p.add_argument('--nucleus',nargs=3,type=str,default=['0','0','0'])
    p.add_argument('--digits',type=int,default=50)
    args=p.parse_args()
    v=cell_mean_inverse_radius(args.lower,args.upper,nucleus=args.nucleus,digits=args.digits)
    print(json.dumps({'cell_mean_inverse_radius':mp.nstr(v,args.digits),
                      'scope':'SCALAR_MATHEMATICAL_REFERENCE_ONLY',
                      'interval_certified':False,'production_admitted':False},indent=2))
if __name__=='__main__':main()
