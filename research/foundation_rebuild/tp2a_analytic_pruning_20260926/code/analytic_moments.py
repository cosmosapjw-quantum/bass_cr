"""Exact six ring moments using stable integer-Bessel recurrences.

J0,J1 use real-argument specialized evaluation. Forward recurrence is applied
only for k>=4 (orders <=3); near k=0 the unscaled J2,J3 are evaluated directly.
No division by k is made in the small-k branch. No angular sampling occurs.
"""
import numpy as np
from scipy.special import jv,j0,j1

def moments(kappa):
    k=np.asarray(kappa,float)
    if k.ndim!=1 or not np.isfinite(k).all() or np.any(k<0):
        raise ValueError('finite nonnegative one-dimensional kappa required')
    b0,b1=j0(k),j1(k);b2=np.empty_like(k);b3=np.empty_like(k);large=k>=4.
    b2[large]=2*b1[large]/k[large]-b0[large]
    b3[large]=4*b2[large]/k[large]-b1[large]
    b2[~large]=jv(2,k[~large]);b3[~large]=jv(3,k[~large])
    return np.ascontiguousarray(np.array([2*np.pi*b0,2j*np.pi*b1,np.pi*(b0-b2),np.pi*(b0+b2),.5j*np.pi*(3*b1-b3),.5j*np.pi*(b1+b3)]).T)
