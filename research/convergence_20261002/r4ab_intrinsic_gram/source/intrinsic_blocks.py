"""Intrinsic real s+p radial blocks and direct Condon-Shortley angular moments.

No geometric quadrature partition, projection, eigenvalue substitution or
antisymmetrization is used. Matrices returned from the cache are immutable.
"""
from __future__ import annotations
import math
import numpy as np
from gram_exact import frozen

def angular_sp(lm):
    lm=tuple(lm)
    if not lm or any(l not in (0,1) or m not in range(-l,l+1) for l,m in lm):raise ValueError('only s+p channels supported')
    n=len(lm);N=np.zeros((3,n,n),complex);G=np.zeros_like(N)
    vectors={0:np.array([0.,0.,1/math.sqrt(3)],complex),1:np.array([-1/math.sqrt(6),-1j/math.sqrt(6),0.]),-1:np.array([1/math.sqrt(6),-1j/math.sqrt(6),0.])}
    grad_vectors={0:np.array([0.,0.,math.sqrt(3)],complex),1:np.array([-math.sqrt(1.5),-1j*math.sqrt(1.5),0.]),-1:np.array([math.sqrt(1.5),-1j*math.sqrt(1.5),0.])}
    for a,(la,ma) in enumerate(lm):
        for b,(lb,mb) in enumerate(lm):
            if la==0 and lb==1:
                N[:,a,b]=vectors[mb];G[:,a,b]=grad_vectors[mb]
            elif la==1 and lb==0:N[:,a,b]=vectors[ma].conj()
    return frozen(N),frozen(G)

def assemble_intrinsic(moments,mode_indices,lm,charge=1.):
    ix=np.asarray(mode_indices,int);lm=tuple(lm);nm=len(moments['G'])
    if ix.ndim!=1 or len(lm)!=len(ix) or np.any(ix<0) or np.any(ix>=nm) or not math.isfinite(charge) or charge<=0:raise ValueError('invalid channel map or charge')
    blocks={}
    for k in ('G','J','T','R1','R2'):
        x=np.asarray(moments[k],float)
        if x.shape!=(nm,nm) or not np.isfinite(x).all():raise ValueError('radial moment shape/finiteness mismatch')
        blocks[k]=x[np.ix_(ix,ix)]
    l=np.array([v[0] for v in lm]);m=np.array([v[1] for v in lm]);delta=(l[:,None]==l)&(m[:,None]==m)
    S=blocks['G']*delta
    H0=(.5*blocks['T']+.5*(l*(l+1))[None,:]*blocks['R2']-charge*blocks['R1'])*delta
    N,G=angular_sp(lm)
    A=blocks['J'][None,:,:]*N+blocks['R1'][None,:,:]*(G-(l+1)[None,None,:]*N)
    return {k:frozen(v) for k,v in {'S':S,'H0':H0,'A':A}.items()}

def boost_blocks(S,H0,A,V,velocity):
    S,H0,A,V=[np.asarray(x,dtype=complex) for x in (S,H0,A,V)];v=np.asarray(velocity,float)
    n=len(S)
    if S.shape!=(n,n) or H0.shape!=(n,n) or V.shape!=(n,n) or A.shape!=(3,n,n) or v.shape!=(3,) or any(not np.isfinite(x).all() for x in (S,H0,A,V,v)):raise ValueError('finite intrinsic/boost shapes required')
    vA=np.tensordot(v,A,axes=(0,0));v2=float(v@v)
    H=H0+V+.5j*(vA.conj().T-vA)+.5*v2*S
    D=-vA-.5j*v2*S
    return {k:frozen(a) for k,a in {'S':S,'H':H,'D':D,'H0':H0,'A':A,'V_other':V}.items()}
