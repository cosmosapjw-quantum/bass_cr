"""Independent foundation probes for BASS_CR, in atomic units.

No imports from or mutations to the historical cr_repro package. These are
bounded CPU research kernels, not an admitted charge-transfer solver.
"""
from __future__ import annotations
from itertools import product
import math
import numpy as np
from scipy import fft, linalg, signal
from scipy.sparse.linalg import LinearOperator, eigsh
from numpy.polynomial.legendre import leggauss
from numpy.polynomial import Polynomial


def _positive(x, name):
    if isinstance(x, (bool, np.bool_)) or not np.isfinite(x) or x <= 0:
        raise ValueError(f'{name} must be finite and positive')
    return float(x)


def _integer(x, name, minimum=1):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x,(int,np.integer)) or x<minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return int(x)


def cube_mean_inverse_radius(centers, width):
    """Exact cuboid corner formula evaluated in float64 for cubic cells.

    centers[...,3] are relative to the nucleus. Integral is finite even at a
    nuclear gridpoint. No soft core or fitted energy parameter. Far-field
    cancellation is not rigorously enclosed: scalar high-precision oracle
    comparisons are required before any production use.
    """
    h=_positive(width,'width'); c=np.asarray(centers,dtype=float)
    if c.ndim<1 or c.shape[-1]!=3 or not np.isfinite(c).all():
        raise ValueError('finite centers[...,3] required')
    c=c/h
    def primitive(q):
        a,b,d=np.moveaxis(abs(q),-1,0); sign=np.prod(np.sign(q),axis=-1)
        r=np.sqrt(a*a+b*b+d*d)
        def ratio(x,y):return np.divide(x,y,out=np.zeros_like(r),where=y!=0)
        logs=(a*b*np.arcsinh(ratio(d,np.hypot(a,b)))+
              b*d*np.arcsinh(ratio(a,np.hypot(b,d)))+
              d*a*np.arcsinh(ratio(b,np.hypot(d,a))))
        angles=(a*a*np.arctan(ratio(b*d,a*r))+b*b*np.arctan(ratio(a*d,b*r))+d*d*np.arctan(ratio(a*b,d*r)))/2
        return sign*(logs-angles)
    # Compensated summation of eight corners.
    total=np.zeros(c.shape[:-1]);corr=np.zeros_like(total)
    for s in product((-1,1),repeat=3):
        term=np.prod(s)*primitive(c+np.asarray(s)/2)
        y=term-corr; t=total+y;corr=(t-total)-y;total=t
    ans=total/h
    if not np.isfinite(ans).all() or np.any(ans<=0):
        raise ArithmeticError('unresolved positive cell integral')
    return ans


def atom_collocation(n, length, *, center=(0.,0.,0.), representation='point'):
    """One-center periodic-FFT kinetic with actual local -1/r sampled in box.

    No CAP. A shifted nucleus changes the boundary traces too; large-box
    checks are needed to separate boundary and grid-registration effects.
    Coefficients are sqrt(dv)*psi at the grid points, Euclidean norm one.
    """
    n=_integer(n,'n',4)
    if n>128:raise ValueError('bounded atom scout caps n at128')
    L=_positive(length,'length');h=L/n
    R=np.asarray(center,float)
    if R.shape!=(3,) or not np.isfinite(R).all():raise ValueError('finite center vector required')
    ax=(np.arange(n)+.5)*h-L/2
    xyz=np.stack(np.meshgrid(ax,ax,ax,indexing='ij'),axis=-1)-R
    if representation=='point':
        radius=np.linalg.norm(xyz,axis=-1)
        if np.any(radius==0):raise ValueError('point Coulomb is singular at a gridpoint; no epsilon floor')
        V=-1/radius
    elif representation=='cell':V=-cube_mean_inverse_radius(xyz,h)
    else:raise ValueError('representation must be point or cell')
    freq=2*np.pi*fft.fftfreq(n,d=h)
    k2=freq[:,None,None]**2+freq[None,:,None]**2+freq[None,None,:]**2
    init=np.exp(-np.linalg.norm(xyz,axis=-1));init/=np.linalg.norm(init)
    return dict(n=n,length=L,h=h,center=R,V=V,k2=k2,initial_guess=init,representation=representation)


def kinetic_action(c,k2):
    return fft.ifftn(.5*k2*fft.fftn(c,workers=1),workers=1)


def atom_action(c,atom):return kinetic_action(c,atom['k2'])+atom['V']*c


def ground_state(atom, *, tol=2e-11,maxiter=2000):
    shape=atom['V'].shape; size=atom['V'].size
    def act(v):return atom_action(v.reshape(shape),atom).real.ravel()
    A=LinearOperator((size,size),matvec=act,dtype=np.float64)
    val,vec=eigsh(A,k=1,which='SA',tol=tol,maxiter=maxiter,v0=atom['initial_guess'].ravel(),ncv=24)
    c=vec[:,0].reshape(shape)
    if np.sum(c)<0:c=-c
    residual=float(np.linalg.norm(atom_action(c,atom)-val[0]*c))
    return float(val[0]),c,residual


def split_fixed_point(atom,tau, *, tol=2e-12,maxiter=2000):
    """Dominant eigenvector of the split imaginary-time operator, not H.

    Diagonalizing S_tau removes iteration-length uncertainty and exposes the
    finite-tau bias. Its own eigenresidual and the true-H residual differ.
    """
    tau=_positive(tau,'tau'); shape=atom['V'].shape;size=atom['V'].size
    vh=np.exp(-.5*tau*atom['V']);kt=np.exp(-.5*tau*atom['k2'])
    def act(v):
        q=vh*v.reshape(shape)
        return (vh*fft.ifftn(kt*fft.fftn(q,workers=1),workers=1).real).ravel()
    A=LinearOperator((size,size),matvec=act,dtype=np.float64)
    val,vec=eigsh(A,k=1,which='LA',tol=tol,maxiter=maxiter,v0=atom['initial_guess'].ravel(),ncv=24)
    c=vec[:,0].reshape(shape)
    if np.sum(c)<0:c=-c
    Hc=atom_action(c,atom);e=float(np.vdot(c,Hc).real)
    return {'tau':tau,'S_eigenvalue':float(val[0]),'S_residual':float(np.linalg.norm(act(c.ravel())-val[0]*c.ravel())),
            'H_energy':e,'H_residual':float(np.linalg.norm(Hc-e*c)),'state':c}


def cutoff_coulomb_galerkin(n,length,radius):
    """True finite Fourier-Galerkin matrix for a PERIODIZED cutoff potential.

    V(r)=-1/r for r<Rc and zero beyond Rc, with Rc<L/2. This is a diagnostic
    boundary model, NOT the full free-space two-center Coulomb Hamiltonian.
    Vhat_q=-4*pi*(1-cos(q*Rc))/(L^3*q^2), Vhat_0=-2*pi*Rc^2/L^3.
    Differences k-l are NOT reduced modulo n (no aliasing).
    """
    n=_integer(n,'n',3);L=_positive(length,'length');Rc=_positive(radius,'radius')
    if n%2!=1 or Rc>=L/2:raise ValueError('odd mode count and radius < length/2 required')
    m=np.arange(-(n//2),n//2+1)
    ks=np.stack(np.meshgrid(m,m,m,indexing='ij'),axis=-1)*(2*np.pi/L)
    ds=np.arange(-n+1,n); q=np.stack(np.meshgrid(ds,ds,ds,indexing='ij'),axis=-1)*(2*np.pi/L)
    qmag=np.linalg.norm(q,axis=-1)
    # 1-cos(qR)=2 sin(qR/2)^2; safe q=0 limit via sinc.
    kernel=-2*np.pi*Rc**2/L**3*np.sinc(qmag*Rc/(2*np.pi))**2
    k2=np.sum(ks**2,axis=-1)
    for arr in (ks,k2,kernel):arr.setflags(write=False)
    return dict(n=n,length=L,radius=Rc,ks=ks,k2=k2,kernel=kernel)


def translation_phase(g,center):
    R=np.asarray(center,float)
    if R.shape!=(3,) or not np.isfinite(R).all():raise ValueError('center shape or finiteness')
    return np.exp(-1j*np.einsum('...i,i->...',g['ks'],R))


def galerkin_action(c,g, *, center=(0.,0.,0.)):
    n=g['n'];c=np.asarray(c)
    if c.shape!=(n,n,n):raise ValueError('coefficient shape mismatch')
    d=translation_phase(g,center);u=np.conj(d)*c
    full=signal.fftconvolve(u,g['kernel'],mode='full')
    v=full[n-1:2*n-1,n-1:2*n-1,n-1:2*n-1]
    return .5*g['k2']*c+d*v


def dense_galerkin(g, *, center=(0.,0.,0.)):
    n=g['n']
    if n>9:raise ValueError('dense diagnostic capped at 9^3 modes')
    inds=np.stack(np.meshgrid(np.arange(n),np.arange(n),np.arange(n),indexing='ij'),axis=-1).reshape(-1,3)
    diff=inds[:,None,:]-inds[None,:,:]+(n-1)
    V=g['kernel'][diff[:,:,0],diff[:,:,1],diff[:,:,2]].astype(complex)
    d=translation_phase(g,center).ravel();V=d[:,None]*V*np.conj(d)[None,:]
    return V+np.diag(.5*g['k2'].ravel())


def radial_fem(radius,elements,degree, *, l=0,quad_order=None,grading=2.):
    """High-order conforming radial weak form for u(r)=r*R_l(r).

    u(0)=u(R)=0, mass M_ij=int phi_i phi_j dr,
    H_ij=.5 int phi_i' phi_j' + [l(l+1)/(2r^2)-1/r] phi_i phi_j.
    Endpoint basis DOFs are removed. Gauss nodes avoid singular evaluations;
    this does NOT soften the potential. Matrices are dense CPU references.
    """
    R=_positive(radius,'radius');ne=_integer(elements,'elements',2);p=_integer(degree,'degree')
    ell=_integer(l,'l',0);grading=_positive(grading,'grading')
    if p>8 or ne*p>1500:raise ValueError('bounded dense prototype cap exceeded')
    nq=quad_order if quad_order is not None else 2*p+4
    nq=_integer(nq,'quad_order',p+1)
    q,w=leggauss(nq);q=(q+1)/2;w=w/2
    nodes=np.linspace(0,1,p+1)
    polys=[Polynomial.fromroots(np.delete(nodes,j))/np.prod(nodes[j]-np.delete(nodes,j)) for j in range(p+1)]
    B=np.array([f(q) for f in polys]).T;D=np.array([f.deriv()(q) for f in polys]).T
    edges=R*(np.arange(ne+1)/ne)**grading
    nd=ne*p+1;M=np.zeros((nd,nd));T=np.zeros_like(M);V=np.zeros_like(M)
    for e in range(ne):
        h=edges[e+1]-edges[e];r=edges[e]+h*q;ww=w*h
        ids=np.arange(e*p,e*p+p+1);ix=np.ix_(ids,ids)
        M[ix]+=B.T@(ww[:,None]*B)
        T[ix]+=.5*D.T@((w/h)[:,None]*D)
        pot=ell*(ell+1)/(2*r*r)-1/r
        V[ix]+=B.T@((ww*pot)[:,None]*B)
    sl=np.s_[1:-1,1:-1];M=M[sl];T=T[sl];V=V[sl]
    return T+V,M,{'kinetic':T,'potential':V,'ndof':nd-2,'edges':edges,'l':ell,'degree':p,'quad_order':nq,'radius':R}


def moving_basis_negative_control(angle):
    """Unitary rotating basis, zero physical H. Missing D preserves norm but
    rotates the physical solution. No relation to actual BASS magnitude."""
    J=np.array([[0.,-1.],[1.,0.]]); B=linalg.expm(angle*J);c0=np.array([1.,0.])
    c_good=linalg.expm(-angle*J)@c0;c_bad=c0.copy()
    return {'correct_physical_error':float(np.linalg.norm(B@c_good-c0)),
            'wrong_coefficient_norm_error':float(abs(np.linalg.norm(c_bad)-1)),
            'wrong_physical_error':float(np.linalg.norm(B@c_bad-c0)),
            'wrong_state_projector_probability':float(abs((B@c_bad)[0])**2)}


def galilean_identity_residual(p,v,energy):
    # t derivative of exp[i*v*z-i*v^2*t/2-i*E*t]*exp[i*p*(z-v*t)]
    # against kinetic (p+v)^2/2, adding a constant V=E-p^2/2.
    lhs=.5*v*v+energy+p*v;rhs=.5*(p+v)**2+energy-.5*p*p
    return lhs-rhs


def ground_state_preconditioned(atom, *, tol=1e-10,maxiter=150):
    """Residual-stopped LOBPCG; preconditioner changes solver, never H.

    A negative Rayleigh value and a small residual do not by themselves prove
    the global ground branch. Independent ARPACK and the positive hydrogenic
    start provide the branch cross-checks in these bounded probes.
    """
    from scipy.sparse.linalg import lobpcg
    tol=_positive(tol,'tol');maxiter=_integer(maxiter,'maxiter')
    shape=atom['V'].shape;size=atom['V'].size
    def act(v):return atom_action(v.reshape(shape),atom).real.ravel()
    def prec(v):
        return fft.ifftn(fft.fftn(v.reshape(shape),workers=1)/(.5*atom['k2']+.5),workers=1).real.ravel()
    A=LinearOperator((size,size),matvec=act,dtype=np.float64)
    M=LinearOperator((size,size),matvec=prec,dtype=np.float64)
    val,vec,history=lobpcg(A,atom['initial_guess'].reshape(-1,1),M=M,
          largest=False,tol=tol/4,maxiter=maxiter,retResidualNormsHistory=True)
    c=vec[:,0].reshape(shape)
    if np.sum(c)<0:c=-c
    e=float(val[0]);res=float(np.linalg.norm(atom_action(c,atom)-e*c))
    if res>tol:raise ArithmeticError(f'LOBPCG physical H residual {res} exceeds {tol}')
    return e,c,res,{'iterations':len(history)-2,'residual_history':[float(np.asarray(z).ravel()[0]) for z in history]}


def split_fixed_point_preconditioned(atom,tau, *, tol=1e-10,maxiter=180):
    """Solve the *same* S_tau eigenproblem through (I-S_tau)/tau.

    This is a diagnostic, not a proposal to prepare physical H eigenstates
    from S_tau. A saturated kinetic preconditioner improves conditioning.
    """
    from scipy.sparse.linalg import lobpcg
    tau=_positive(tau,'tau');tol=_positive(tol,'tol');maxiter=_integer(maxiter,'maxiter')
    shape=atom['V'].shape;size=atom['V'].size
    vh=np.exp(-.5*tau*atom['V']);kt=np.exp(-.5*tau*atom['k2'])
    def sact(v):
        q=vh*v.reshape(shape)
        return (vh*fft.ifftn(kt*fft.fftn(q,workers=1),workers=1).real).ravel()
    def act(v):return (v.ravel()-sact(v))/tau
    denom=-np.expm1(-.5*tau*atom['k2'])/tau+.5
    def prec(v):return fft.ifftn(fft.fftn(v.reshape(shape),workers=1)/denom,workers=1).real.ravel()
    A=LinearOperator((size,size),matvec=act,dtype=np.float64);M=LinearOperator((size,size),matvec=prec,dtype=np.float64)
    val,vec,hist=lobpcg(A,atom['initial_guess'].reshape(-1,1),M=M,largest=False,
        tol=tol/4,maxiter=maxiter,retResidualNormsHistory=True)
    c=vec[:,0].reshape(shape)
    if np.sum(c)<0:c=-c
    eig=1-tau*float(val[0]);sres=float(np.linalg.norm(sact(c)-eig*c.ravel()))
    effective_residual=sres/tau
    if effective_residual>tol:raise ArithmeticError(f'effective split eigenresidual {effective_residual} exceeds {tol}')
    Hc=atom_action(c,atom);e=float(np.vdot(c,Hc).real)
    return {'tau':tau,'S_eigenvalue':eig,'S_residual':sres,'effective_S_residual':effective_residual,
        'H_energy':e,'H_residual':float(np.linalg.norm(Hc-e*c)),'state':c,'iterations':len(hist)-2}


def galerkin_ground_preconditioned(g, *, tol=1e-10,maxiter=160,embedded=False):
    """Ground branch of the exact finite Toeplitz operator, center zero.

    Fourier coefficients of infinite-space 1s supply only an initial guess.
    They are not used as a calibration target or potential correction.
    """
    from scipy.sparse.linalg import lobpcg
    tol=_positive(tol,'tol');maxiter=_integer(maxiter,'maxiter');n=g['n'];shape=(n,n,n);size=n**3
    action=galerkin_action_embedded if embedded else galerkin_action
    def act(v):return action(v.reshape(shape),g).real.ravel()
    def prec(v):return (v.reshape(shape)/(.5*g['k2']+.5)).ravel()
    A=LinearOperator((size,size),matvec=act,dtype=np.float64);M=LinearOperator((size,size),matvec=prec,dtype=np.float64)
    guess=1/(1+g['k2'])**2;guess/=np.linalg.norm(guess)
    val,vec,hist=lobpcg(A,guess.reshape(-1,1),M=M,largest=False,tol=tol/4,
        maxiter=maxiter,retResidualNormsHistory=True)
    c=vec[:,0].reshape(shape)
    if np.sum(c)<0:c=-c
    e=float(val[0]);res=float(np.linalg.norm(action(c,g)-e*c))
    if res>tol:raise ArithmeticError(f'Galerkin H residual {res} exceeds {tol}')
    return e,c,res,{'iterations':len(hist)-2,'residual_history':[float(np.asarray(z).ravel()[0]) for z in hist]}


def moving_galerkin_probe(g,velocity,horizon,step_counts):
    """Exact finite-dimensional translating-potential benchmark.

    H(t)=D(vt) H0 D(vt)^dagger gives
    U(t,0)=D(vt) exp[-i(H0-v Kz)t]. This is coordinate-translation covariance
    at fixed bandlimit, NOT full finite-basis Galilean boost invariance.
    The initial state is the H0 ground state, not an asymptotic boosted 1s.
    """
    T=_positive(horizon,'horizon');v=float(velocity)
    if not np.isfinite(v):raise ValueError('finite velocity required')
    counts=[_integer(n,'step_count') for n in step_counts]
    if not counts:raise ValueError('step count ladder required')
    H=dense_galerkin(g);kz=g['ks'][...,2].ravel();e,U=linalg.eigh(H);c0=U[:,0]
    Hcom=H-np.diag(v*kz);ec,Uc=linalg.eigh(Hcom)
    endphase=translation_phase(g,(0,0,v*T)).ravel()
    exact=endphase*(Uc@(np.exp(-1j*T*ec)*(Uc.conj().T@c0)))
    wrong=endphase*(U@(np.exp(-1j*T*e)*(U.conj().T@c0)))
    rows=[]
    for ns in counts:
        dt=T/ns;prop=(U*np.exp(-1j*dt*e))@U.conj().T;c=c0.copy()
        for j in range(ns):
            phase=translation_phase(g,(0,0,v*(j+.5)*dt)).ravel()
            c=phase*(prop@(np.conj(phase)*c))
        rows.append({'steps':ns,'dt':dt,'error_to_exact_comoving':float(np.linalg.norm(c-exact)),
            'norm_error':float(abs(np.linalg.norm(c)-1)),
            'translated_ground_projection':float(abs(np.vdot(endphase*c0,c))**2)})
    return {'n':g['n'],'L':g['length'],'Rc':g['radius'],'velocity_au':v,'T_au':T,
        'midpoint_ladder':rows,'exact_translated_ground_projection':float(abs(np.vdot(endphase*c0,exact))**2),
        'missing_advection_state_error':float(np.linalg.norm(wrong-exact)),
        'missing_advection_norm_error':float(abs(np.linalg.norm(wrong)-1)),
        'missing_advection_projection':float(abs(np.vdot(endphase*c0,wrong))**2),
        'scope':'EXACT_FINITE_BASIS_TRANSLATING_CUTOFF_COULOMB_NOT_CAPTURE_COLLISION'}


def galerkin_action_embedded(c,g, *, center=(0.,0.,0.)):
    """Exact Toeplitz action through a >=(2n-1)^3 circulant embedding.

    Only differences i-j in [-(n-1),n-1]^3 are used. This padding removes
    circular wrap aliasing. It is not a physical periodic-image correction.
    Treat g['kernel'] as immutable after its first use: this bounded scout
    caches its transform. A production implementation needs a frozen typed
    operator identity rather than a mutable dictionary cache.
    """
    n=g['n'];c=np.asarray(c)
    if c.shape!=(n,n,n) or not np.isfinite(c).all():raise ValueError('finite coefficient cube required')
    if '_embedding_fft' not in g or g.get('_embedding_kernel_ref') is not g['kernel']:
        m=fft.next_fast_len(2*n-1);idx=np.arange(-n+1,n)%m
        circ=np.zeros((m,m,m));circ[np.ix_(idx,idx,idx)]=g['kernel']
        g['_embedding_fft']=fft.fftn(circ,workers=1);g['embedding_length']=m
        g['_embedding_fft'].setflags(write=False);g['_embedding_kernel_ref']=g['kernel']
    m=g['embedding_length'];d=translation_phase(g,center)
    padded=np.zeros((m,m,m),complex);padded[:n,:n,:n]=np.conj(d)*c
    conv=fft.ifftn(fft.fftn(padded,workers=1)*g['_embedding_fft'],workers=1)[:n,:n,:n]
    return .5*g['k2']*c+d*conv


def direct_connection_negative_control(omega,t,epsilon):
    """Show that dot(S)=D+D* cannot test the skew part of D.

    R3M17 already tests dot(S); this counterexample motivates an additional
    basis-derivative or exact physical transport test, not a claim that
    the existing AOCC implementation has a demonstrated D defect.
    """
    eps=_positive(epsilon,'epsilon');J=np.array([[0.,-1.],[1.,0.]])
    B=lambda x:linalg.expm(omega*x*J)
    basis=B(t);dotB=(B(t+eps)-B(t-eps))/(2*eps)
    D_fd=basis.T@dotB;D_true=omega*J;D_bad=np.zeros((2,2))
    S=lambda x:B(x).T@B(x)
    dotS=(S(t+eps)-S(t-eps))/(2*eps)
    return {'omega':float(omega),'t':float(t),'epsilon':eps,
        'correct_direct_basis_derivative_residual':float(np.linalg.norm(D_fd-D_true)),
        'wrong_direct_basis_derivative_residual':float(np.linalg.norm(D_fd-D_bad)),
        'wrong_metric_identity_residual':float(np.linalg.norm(dotS-D_bad-D_bad.T)),
        'wrong_generator_skew_residual':float(np.linalg.norm(-D_bad-D_bad.T)),
        'scope':'CONNECTION_IDENTIFIABILITY_COUNTEREXAMPLE_NOT_MEASURED_BASS_DEFECT'}
