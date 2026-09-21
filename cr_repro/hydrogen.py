from __future__ import annotations
import math
import numpy as np
from scipy.special import eval_genlaguerre,gammaln
try:
    from scipy.special import sph_harm_y
    def _Y(l,m,theta,phi): return sph_harm_y(l,m,theta,phi)
except Exception:
    from scipy.special import sph_harm
    def _Y(l,m,theta,phi): return sph_harm(m,l,phi,theta)

def radial(n,l,r):
    if n<1 or l<0 or l>=n: raise ValueError('invalid n,l')
    rho=2.0*np.asarray(r)/n
    lognorm=math.log(2.0/n**2)+0.5*(gammaln(n-l)-gammaln(n+l+1))
    return math.exp(lognorm)*np.exp(-rho/2)*rho**l*eval_genlaguerre(n-l-1,2*l+1,rho)

def orbital(n,l,m,x,y,z):
    r=np.sqrt(x*x+y*y+z*z)
    theta=np.arccos(np.clip(np.where(r>0,z/r,1.0),-1,1)); phi=np.arctan2(y,x)
    return radial(n,l,r)*_Y(l,m,theta,phi)

def one_s(x,y,z):
    r=np.sqrt(x*x+y*y+z*z); return np.exp(-r)/math.sqrt(math.pi)

def bound_quantum_numbers(nmax):
    return [(n,l,m) for n in range(1,nmax+1) for l in range(n) for m in range(-l,l+1)]
