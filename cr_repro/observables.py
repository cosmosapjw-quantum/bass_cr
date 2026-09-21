from __future__ import annotations
import math, numpy as np
from .constants import HARTREE_EV,U_OVER_ME

def projectile_speed_au(E_keV_per_u):
    return math.sqrt(2*(1000*float(E_keV_per_u)/HARTREE_EV)/U_OVER_ME)

def finite_time_threshold_eV(E_keV_per_u): return 1000*float(E_keV_per_u)/(4*U_OVER_ME)
def capture_cross_section_a0sq(b,p):
    b=np.asarray(b,float); p=np.asarray(p,float)
    if b.size<2 or b.shape!=p.shape or np.any(np.diff(b)<=0): raise ValueError('bad b grid')
    return float(2*math.pi*np.trapezoid(b*p,b))
def metric_projector_probability(O,C,indices):
    ix=np.asarray(indices,int)
    if not len(ix): return 0.0
    v=O[np.ix_(ix,np.arange(O.shape[0]))]@C; G=O[np.ix_(ix,ix)]
    return float(np.real(np.vdot(v,np.linalg.solve(G,v))))
def estimator_gap_bound(pb,eps_b,eps_c):
    if pb<0 or eps_b<0 or eps_c<0 or eps_b>pb: raise ValueError('bad args')
    return eps_b+eps_c+2*math.sqrt(max(0,(pb-eps_b)*eps_c))
