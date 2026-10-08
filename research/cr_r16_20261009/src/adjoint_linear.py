"""Opt-in, finite-dimensional, piecewise-linear goal/adjoint identity.

This is an exact *algebraic* dual-weighted residual relation when the specified
piecewise A(s), forcing r(s), goal g(s), and affine jumps are a matched model.
It is NOT an interval certificate for the nonlinear FT03 ODE: that would require
validated Jacobian enclosures and quadratic remainder control on the physical tube.

State and residual rates are normalized to individual cell coordinate s in [0,1].
A, g, r are hence defined per normalized s, NOT per proper second.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import numpy as np
from scipy.integrate import solve_ivp

Array = np.ndarray

@dataclass(frozen=True)
class Cell:
    A: Array
    g: Callable[[float], Array]
    r: Callable[[float], Array]

@dataclass(frozen=True)
class Link:
    """e_next_start = B @ e_prev_end + delta (birth/nominal interface)."""
    B: Array
    delta: Array

def _inputs(cells: list[Cell],links:list[Link],e0:Array):
    if not cells:raise ValueError('EMPTY_CELL_SEQUENCE')
    if len(links)!=len(cells)-1:raise ValueError('LINK_COUNT')
    if not np.isfinite(e0).all() or e0.shape!=(len(cells[0].A),):
        raise ValueError('INITIAL_DIMENSION')
    for i,c in enumerate(cells):
        n=c.A.shape[0]
        if c.A.shape!=(n,n) or n==0 or not np.isfinite(c.A).all():
            raise ValueError('MATRIX_SHAPE_OR_FINITE')
        for label,fn in [('g',c.g),('r',c.r)]:
            v=np.asarray(fn(.5),dtype=float)
            if v.shape!=(n,) or not np.isfinite(v).all():
                raise ValueError('FUNCTION_DIMENSION_'+label)
        if i:
            b=links[i-1]
            if b.B.shape!=(n,len(cells[i-1].A)) or b.delta.shape!=(n,):
                raise ValueError('LINK_DIMENSION')
            if not (np.isfinite(b.B).all() and np.isfinite(b.delta).all()):
                raise ValueError('NONFINITE_LINK')

def forward_error(cells:list[Cell],links:list[Link],e0:Array,
                  *,rtol:float=2e-11):
    """Independent forward linearized error and optical goal solution."""
    _inputs(cells,links,e0)
    e=np.array(e0,dtype=float);goal=0.;parts=[]
    for i,cell in enumerate(cells):
        n=len(e);A=cell.A
        def fun(s,x):
            ev=x[:n]
            return np.concatenate((A@ev-np.asarray(cell.r(s)),
                                   [float(np.dot(cell.g(s),ev))]))
        y0=np.concatenate([e,[0.]])
        sol=solve_ivp(fun,(0.,1.),y0,method='DOP853',rtol=rtol,
                      atol=np.concatenate((np.full(n,1e-18),[1e-27])),max_step=.125)
        if not sol.success or sol.t[-1]!=1.:raise RuntimeError('FORWARD_IVP_FAIL')
        e=sol.y[:n,-1];goal+=float(sol.y[-1,-1]);parts.append(float(sol.y[-1,-1]))
        if i<len(links):e=links[i].B@e+links[i].delta
    return {'goal':goal,'cell_goal_contributions':parts,'final_error':e,'method':'forward_piecewise_linear'}

def backward_dual(cells:list[Cell],links:list[Link],e0:Array,
                  *,rtol:float=2e-11):
    """Backward adjoint DWR with correct transpose jump map and explicit delta.

    -lambda' = A.T lambda + g, lambda(final)=0,
    lambda_before = B.T lambda_after.
    Goal = lambda_initial.e0 - integral lambda.r + sum lambda_after.delta.
    """
    _inputs(cells,links,e0)
    nlast=len(cells[-1].A)
    lam=np.zeros(nlast)
    residual=[0.]*len(cells);events=[0.]*len(links)
    for i in reversed(range(len(cells))):
        c=cells[i];n=len(c.A)
        def fun(s,x):
            l=x[:n]
            return np.concatenate((-c.A.T@l-np.asarray(c.g(s)),
                                   [float(np.dot(l,c.r(s)))]))
        y0=np.concatenate((lam,[0.]))
        sol=solve_ivp(fun,(1.,0.),y0,method='DOP853',rtol=rtol,
                      atol=np.concatenate((np.full(n,1e-18),[1e-27])),max_step=.125)
        if not sol.success or sol.t[-1]!=0.:raise RuntimeError('ADJOINT_IVP_FAIL')
        lam=sol.y[:n,-1]
        residual[i]=float(sol.y[-1,-1])  # -int_0^1 lambda^T r ds
        if i:
            events[i-1]=float(np.dot(lam,links[i-1].delta))
            lam=links[i-1].B.T@lam
    initial=float(np.dot(lam,e0));goal=initial+sum(residual)+sum(events)
    return {'goal':goal,'lambda_initial':lam,'initial_contribution':initial,
            'residual_contributions':residual,'interface_contributions':events,
            'method':'backward_piecewise_linear_adjoint'}
