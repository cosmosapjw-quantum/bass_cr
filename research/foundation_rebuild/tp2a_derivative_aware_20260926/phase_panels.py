"""Exploratory longitudinal-phase subdivision of integration panels only.

The FEM coefficient mesh and basis are never modified. The phase budget is a
resolution heuristic, not an error bound; independent order and D checks remain.
"""
from __future__ import annotations
import math
import numpy as np


def phase_split_edges(edges, separation, longitudinal_velocity, max_phase=24.):
    e=np.asarray(edges,float)
    if (e.ndim!=1 or len(e)<2 or e[0]!=0 or not np.isfinite(e).all()
            or np.any(np.diff(e)<=0)):
        raise ValueError('finite increasing radial edges from zero required')
    vals=np.asarray([separation,longitudinal_velocity,max_phase],float)
    if not np.isfinite(vals).all() or separation<=0 or max_phase<=0:
        raise ValueError('positive separation/phase budget and finite velocity required')
    coefficient=abs(float(longitudinal_velocity))/(2*float(separation))
    if coefficient==0:return e.copy()
    answer=[float(e[0])]
    for a,b in zip(e[:-1],e[1:]):
        n=max(1,math.ceil(coefficient*(b*b-a*a)/max_phase))
        if n>4096 or len(answer)+n>8192:
            raise ValueError('phase subdivision resource cap exceeded')
        inner=np.sqrt(np.linspace(a*a,b*b,n+1)[1:-1])
        answer.extend(inner.tolist());answer.append(float(b))
    return np.asarray(answer)
