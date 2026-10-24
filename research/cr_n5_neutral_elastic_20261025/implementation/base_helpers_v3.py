import csv, hashlib, json, math

from pathlib import Path

import numpy as np

from scipy.special import gammainc

from scipy.linalg import solve_banded

class InputError(ValueError): pass

def need(ok,msg):
    if not ok: raise InputError(msg)

def writej(path,obj):
    with Path(path).open('x') as f: json.dump(obj,f,indent=2,allow_nan=False); f.write('\n')

def apply(d,l,u,x):
    if x.ndim==1:
        y=d*x;y[1:]+=l*x[:-1];y[:-1]+=u*x[1:]
    else:
        y=d[:,None]*x;y[1:]+=l[:,None]*x[:-1];y[:-1]+=u[:,None]*x[1:]
    return y

def scaled_residual(d,l,u,x,rhs):
    res=abs(apply(d,l,u,x)-rhs); den=apply(abs(d),abs(l),abs(u),abs(x))+abs(rhs)
    need(np.all(res[den==0]==0),'ZERO_SCALE_RESIDUAL')
    return float(np.divide(res,den,out=np.zeros_like(res),where=den>0).max())

def solve(d,l,u,rhs):
    need(np.all(d>0) and np.all(l<=0) and np.all(u<=0) and np.all(np.isfinite(rhs)),'INVALID_OPERATOR_OR_RHS')
    ab=np.zeros((3,len(d)));ab[0,1:]=u;ab[1]=d;ab[2,:-1]=l
    x=solve_banded((1,1),ab,rhs);need(np.all(np.isfinite(x)),'NONFINITE_SOLUTION')
    return x,scaled_residual(d,l,u,x,rhs)

def generator_checks(g,pi):
    d=g['diag'];lo=g['lower'];up=g['upper']
    need(np.all(np.isfinite(d)) and np.all(np.isfinite(lo)) and np.all(np.isfinite(up)) and np.all(lo>0) and np.all(up>0) and np.all(d<=0),'GENERATOR_DOMAIN')
    sums=d.copy();sums[:-1]+=lo;sums[1:]+=up
    scale=abs(d);scale[:-1]+=lo;scale[1:]+=up
    left=lo*pi[:-1];right=up*pi[1:]
    return dict(column_scaled_defect=float(np.max(abs(sums)/scale)),detailed_balance_edge_defect=float(np.max(abs(left-right)/(abs(left)+abs(right)))))

def generator(c,pi):
    lo=c/pi[:-1];up=c/pi[1:];d=np.zeros(len(pi));d[:-1]-=lo;d[1:]-=up
    g={'diag':d,'lower':lo,'upper':up}
    return g,generator_checks(g,pi)

def electron_drift(E,g):
    """Q.T E from edge increments, including the q edge."""
    de=np.diff(E);v=np.zeros(len(E));v[:-1]+=g['lower']*de;v[1:]-=g['upper']*de
    return v

def mfpt(c,pi):return np.r_[0.,np.cumsum(np.cumsum(pi[:0:-1])[::-1]/c)]

def relative(a,b):
    scale=max(abs(a),abs(b));return abs(a-b)/scale if scale else 0.

def atoms(unit,z):
    with (unit/f'inputs/reused/c23d/ATOMS_{z}.csv').open(newline='') as f:r=list(csv.DictReader(f))
    out={k:np.array([float(row[k]) for row in r]) for k in r[0] if k!='channel'}
    need(len(r)==384 and np.all((out['W_eV']>0)&(out['W_eV']<10)),'SOURCE_DOMAIN')
    need(all(np.all(np.isfinite(a)) for a in out.values()),'NONFINITE_SOURCE')
    return out
