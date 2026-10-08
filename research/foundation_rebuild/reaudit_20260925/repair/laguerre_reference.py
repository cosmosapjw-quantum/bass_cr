"""Exploratory non-FEM radial L2 Laguerre basis, with infinite support.

u_n(r) = sqrt(2*zeta*n!/Gamma(n+2*l+3)) * x**(l+1)
         * exp(-x/2) * L_n^(2*l+2)(x), x=2*zeta*r.
This is not a wavepacket continuum quadrature or a collision solver.
"""
from __future__ import annotations
import numpy as np
from scipy import special,linalg

def matrices(size,l,zeta=1.):
    if type(size) is not int or not 2<=size<=96:raise ValueError('size must be 2..96')
    if type(l) is not int or not 0<=l<=3:raise ValueError('l must be 0..3')
    if not np.isfinite(zeta) or zeta<=0:raise ValueError('positive finite zeta required')
    # Standard Laguerre quadrature: after multiplying x powers the integrands
    # are polynomials times e^-x, including the apparent 1/x and 1/x^2 factors.
    x,w=special.roots_laguerre(size+l+4)
    n=np.arange(size);beta=np.exp(.5*(special.gammaln(n+1)-special.gammaln(n+2*l+3)))
    L=np.column_stack([special.eval_genlaguerre(j,2*l+2,x) for j in n])*beta
    dL=np.column_stack([np.zeros_like(x) if j==0 else -special.eval_genlaguerre(j-1,2*l+3,x) for j in n])*beta
    B=x[:,None]**(l+1)*L
    dB=x[:,None]**(l+1)*(dL-.5*L)+(l+1)*x[:,None]**l*L
    M=B.T@(w[:,None]*B)
    T=2*zeta*zeta*dB.T@(w[:,None]*dB)
    V=B.T@((w*(-2*zeta/x+2*zeta*zeta*l*(l+1)/x**2))[:,None]*B)
    return T+V,M

def spectrum(size,l,zeta=1.):
    H,M=matrices(size,l,zeta);e,c=linalg.eigh(H,M)
    return {'size':size,'l':l,'zeta_a0_inv':zeta,'mass_identity_error_fro':float(np.linalg.norm(M-np.eye(size))),
            'energies_Eh':e.tolist(),'negative_count':int(np.sum(e<0)),
            'first_positive_Eh':float(e[e>0][0]),
            'first_three_bound_errors':[float(abs(e[j]+.5/(j+l+1)**2)) for j in range(3)],
            'scope':'ATOMIC_INFINITE_SUPPORT_L2_BASIS_NOT_CAPTURE_OR_CONTINUUM_COMPLETENESS'}
