"""Stateless, bounded independent-bin multiprocessing for shape-free moment bounds.

Returns the exact same dyadic-Fraction global sums and outgoing upper/lower floats
as serial enclose_q_bins. Parallelism is across disjoint reference-q bins only;
source ages/angles must already have been resolved by the owner (not merged).
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from math import inf, isfinite, nextafter
from multiprocessing import get_context
import numpy as np
from moment_envelopes import cached_template, enclose_q_bins, _radius, _positive_finite


def _one_bin(args):
    lo,hi,n,u,ratio,gas,dt,order=args
    r=Fraction.from_float(ratio)
    left=nextafter(float(Fraction.from_float(lo)*r),-inf)
    right=nextafter(float(Fraction.from_float(hi)*r),inf)
    temp=cached_template(left,right,gas,dt,order)
    nF=Fraction.from_float(n);uF=Fraction.from_float(u)
    return temp.evaluate(nF,uF*r/nF)


def parallel_enclose_q_bins(edges,number,moment_ref_ev,ratio,neutrals,dt,order=4,workers=2):
    if workers not in (1,2,4):raise ValueError('max four independent worker processes')
    if workers==1:return enclose_q_bins(edges,number,moment_ref_ev,ratio,neutrals,dt,order)
    ed=np.asarray(edges,dtype=float);ns=np.asarray(number,dtype=float);us=np.asarray(moment_ref_ev,dtype=float)
    if ed.ndim!=1 or len(ed)!=len(ns)+1 or us.shape!=ns.shape or not np.all(np.isfinite(ed)) or not np.all(np.diff(ed)>0):
        raise ValueError('fixed q support/data mismatch')
    if not(isfinite(ratio) and ratio>0 and isfinite(dt) and dt>=0) or np.any(~np.isfinite(ns)) or np.any(~np.isfinite(us)) or np.any(ns<0):
        raise ValueError('nonphysical optical input')
    if np.any((ns==0)&(us!=0)) or np.any((ns>0)&((us/np.maximum(ns,np.finfo(float).tiny)<ed[:-1]) | (us/np.maximum(ns,np.finfo(float).tiny)>ed[1:]))):
        raise ValueError('mean outside q support')
    rho=_positive_finite(neutrals,3)
    tasks=[(float(ed[i]),float(ed[i+1]),float(ns[i]),float(us[i]),float(ratio),rho,float(dt),order)
           for i in np.flatnonzero(ns>0)]
    if not tasks:
        return {'event':np.zeros((3,2)), 'heat':np.zeros((3,2)),
                'number':0.,'physical_energy_ev':0.,'support_bins':0,
                'numerics':'empty_q_state'}
    with ProcessPoolExecutor(max_workers=workers,mp_context=get_context('forkserver')) as pool:
        rows=pool.map(_one_bin,tasks,chunksize=max(1,len(tasks)//(workers*4)))
        totals=[[Fraction(0),Fraction(0)] for _ in range(6)]
        for v in rows:
            for j in range(3):
                for k,w in enumerate((v['event'][j],v['heat'][j])):
                    totals[j+3*k][0]+=Fraction.from_float(w[0])
                    totals[j+3*k][1]+=Fraction.from_float(w[1])
    A=np.asarray([[0. if v[0]==0 else _radius(float(v[0]),False),
                   0. if v[1]==0 else _radius(float(v[1]),True)] for v in totals])
    return {'event':A[:3],'heat':A[3:], 'number':float(ns.sum()),
            'physical_energy_ev':float((us*ratio).sum()),'support_bins':len(tasks),
            'numerics':'parallel_certified_dyadic_Fraction_exact_global_sum'}
