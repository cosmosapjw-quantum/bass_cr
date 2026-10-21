"""Prepared exp((b-b_i) M) E_i for a fixed real collisionless moment matrix.

This is the exact representation of the SAME finite moment equations, not a
new angular closure. It is NOT valid with unrepresented collision/source terms.
The spectral floating evaluation has a direct-expm fallback, not a certificate.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm

class RadiationFlow:
    def __init__(self,matrix):
        if np.iscomplexobj(matrix): raise ValueError("REAL_MATRIX_REQUIRED")
        self.matrix=np.array(matrix,dtype=np.float64,copy=True)
        M=self.matrix
        if M.ndim!=2 or M.shape[0]!=M.shape[1] or M.shape[0]==0 or not np.isfinite(M).all():
            raise ValueError('FINITE_SQUARE_REAL_MATRIX_REQUIRED')
        M.flags.writeable=False
        self.eigenvalues,self.eigenvectors=np.linalg.eig(M)
        self.condition=float(np.linalg.cond(self.eigenvectors))
        self.residual=float(np.linalg.norm(M@self.eigenvectors-self.eigenvectors*self.eigenvalues,np.inf))
        self.spectral=(np.isfinite(self.condition) and self.condition<1e5 and
                       self.residual<=1e-12*max(1.,np.linalg.norm(M,np.inf)))
        self.inverse=np.linalg.inv(self.eigenvectors) if self.spectral else None
        for a in (self.eigenvalues,self.eigenvectors,self.inverse):
            if a is not None:a.flags.writeable=False

    def at(self,b,initial):
        if np.iscomplexobj(b) or np.iscomplexobj(initial): raise ValueError("REAL_FLOW_INPUTS_REQUIRED")
        b=float(b); y=np.asarray(initial,dtype=np.float64)
        if y.shape!=(self.matrix.shape[0],) or not np.isfinite(y).all() or not np.isfinite(b):
            raise ValueError('FINITE_DISPLACEMENT_AND_MATCHING_VECTOR_REQUIRED')
        if b==0:return y.copy()
        if self.spectral and abs(b)<=.05:
            # expm1 preserves the exact initial vector at tiny displacement.
            z=y+self.eigenvectors@(np.expm1(self.eigenvalues*b)*(self.inverse@y))
            if np.isfinite(z).all() and np.max(abs(z.imag))<=64*np.finfo(float).eps*max(1.,np.max(abs(z.real))):
                return z.real.copy()
        with np.errstate(over='raise',invalid='raise'):
            z=expm(b*self.matrix)@y
        if not np.isfinite(z).all():raise FloatingPointError('NONFINITE_RADIATION_FLOW')
        return z

    def history(self,b,initial):
        if np.iscomplexobj(b): raise ValueError("REAL_HISTORY_REQUIRED")
        b=np.asarray(b,dtype=np.float64)
        if b.ndim!=1:raise ValueError('ONE_DIMENSIONAL_HISTORY_REQUIRED')
        return np.stack([self.at(x,initial) for x in b],axis=1)

def solve_three_state(owner,targets,flow=None):
    """Use the original owner's physical RHS; eliminate only five E ODE slots.

    owner is a process-local immutable-physics ComponentReduced instance from
    pinned REI PR198. Its case initialization owns A_m and angular amplitudes.
    The original 8-state RHS is called on a reconstructed state and its first
    three entries are returned. No copied Einstein/Vlasov formula is substituted.
    """
    from scipy.integrate import solve_ivp
    y0,initial=owner.initial(*targets)
    if y0.size!=8 or owner.mat.shape!=(5,5):raise ValueError('ONLY_PINNED_EVEN_L8_SCOPE')
    flow=flow or RadiationFlow(owner.mat)
    if not np.array_equal(flow.matrix,owner.mat):raise ValueError('FLOW_MATRIX_SOURCE_MISMATCH')
    e0=y0[3:].copy(); b0=float(y0[1])
    def rhs(x,z):
        full=np.concatenate((z,flow.at(z[1]-b0,e0)))
        return owner.rhs(x,full)[:3]
    t_eval=np.linspace(0,owner.src.xmax,65)
    # These values are the read original owner settings, not widened tolerances.
    sol=solve_ivp(rhs,(0,owner.src.xmax),y0[:3],method='DOP853',
                  rtol=3e-11,atol=3e-13,t_eval=t_eval)
    if not sol.success:raise RuntimeError(sol.message)
    full=np.vstack((sol.y,flow.history(sol.y[1]-b0,e0)))
    d=owner.diagnostics(sol.t,full)
    return sol,full,d,initial
