"""Interface-aligned, phase-exact TP/PT Coulomb quadrature in a0, Eh, ta.

Uses the unchanged bass_foundations basis evaluator. Only cross-center blocks
are integrated over the intersection of compact supports. No same-center block
or capture dynamics is implemented here. Weak gradients are used, without
replacing a hard-wall eigenvalue by a full-space differential eigenvalue.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import jv
from bass_foundations.two_center import Trajectory,basis_values


def phase_ring_weights(kappa,phi0,degree):
    """Integrate exp(i*k*cos(phi-phi0)) times any trig polynomial |m|<=degree.

    Function values are sampled on 2*degree+1 nodes; the exponential is NOT
    sampled/aliased. Complex integration weights encode exact Bessel moments.
    """
    if type(degree) is not int or degree<0:raise ValueError('degree must be a nonnegative integer')
    k,a=np.broadcast_arrays(np.asarray(kappa,float),np.asarray(phi0,float))
    if not np.isfinite(k).all() or not np.isfinite(a).all():raise ValueError('nonfinite phase')
    n=2*degree+1;m=np.arange(-degree,degree+1);phi=2*np.pi*np.arange(n)/n
    moments=1j**m*jv(m,k[...,None])*np.exp(1j*a[...,None]*m)
    return (2*np.pi/n)*(moments@np.exp(-1j*m[:,None]*phi[None,:]))


def intersection_volume(radius,separation):
    a=float(radius);R=float(separation)
    if a<=0 or R<0 or not np.isfinite([a,R]).all():raise ValueError('invalid radius/separation')
    if R>=2*a:return 0.
    return math.pi*(2*a-R)**2*(4*a+R)/12


def geometry_pairs(edges,R,order):
    """Positive distance quadrature on each element/triangle subcell.

    Outer cells include ALL intersections of triangle boundaries with inner
    FEM edges. Emitted weights omit dphi. This generator has bounded batches.
    """
    edges=np.asarray(edges,float)
    if (edges.ndim!=1 or len(edges)<2 or edges[0]!=0 or
        not np.isfinite(edges).all() or np.any(np.diff(edges)<=0)):
        raise ValueError('strictly increasing finite edges starting at zero required')
    if not np.isfinite(R) or R<=0:raise ValueError('positive resolved separation required')
    if type(order) is not int or not 2<=order<=64:raise ValueError('order must be 2..64')
    L=float(edges[-1])
    if R>=2*L:return
    v=np.r_[edges,abs(R-edges),R+edges,0.,L]
    outer=np.unique(v[(v>=0)&(v<=L)])
    x,w=leggauss(order)
    for a,b in zip(outer[:-1],outer[1:]):
        if b-a<=64*np.finfo(float).eps*max(1.,L):continue
        r0s=(b+a)/2+(b-a)*x/2;w0s=(b-a)*w/2
        for r0,w0 in zip(r0s,w0s):
            lo=abs(R-r0);hi=min(R+r0,L)
            if hi<=lo:continue
            inner=np.r_[lo,edges[(edges>lo)&(edges<hi)],hi]
            aa,bb=inner[:-1],inner[1:]
            r1=((bb+aa)[:,None]/2+(bb-aa)[:,None]*x/2).ravel()
            w1=((bb-aa)[:,None]*w/2).ravel()
            yield np.full_like(r1,r0),r1,w0*w1*r0*r1/R


def _groups(channels):
    ti=np.array([i for i,c in enumerate(channels) if c.center==0],int)
    pi=np.array([i for i,c in enumerate(channels) if c.center==1],int)
    if not len(ti) or not len(pi):raise ValueError('both centers required')
    return ti,pi


def cross_blocks(trajectory,channels,edges,t,*,order=20,angular='bessel',nphi=128,batch=128,callback=None):
    """No softening, amplitude taper, discarded mode, fitted energy, or symmetrization.

    angular='uniform' is an independent, adequately sampled phi cross-check.
    All radial coefficients are held fixed across runs by the caller.
    """
    channels=tuple(channels);ti,pi=_groups(channels)
    if type(batch) is not int or not 1<=batch<=1024:raise ValueError('batch must be 1..1024')
    if angular not in ('bessel','uniform'):raise ValueError('unknown angular rule')
    centers=trajectory.centers(t);dr=centers[1]-centers[0];R=float(np.linalg.norm(dr))
    if R<=1e-7:raise ValueError('unresolved coincident foci: separate chart required')
    L=float(np.asarray(edges)[-1])
    shape=(len(ti),len(pi));acc={k:np.zeros(shape if k.endswith('tp') else shape[::-1],complex) for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')}
    if R>=2*L:
        return {**acc,'metadata':{'zero_reason':'DISJOINT_SUPPORTS','radial_pairs':0,'basis_points':0,'volume_relative_error':0.}}
    ez=dr/R;axis=np.eye(3)[np.argmin(abs(ez))];e1=np.cross(ez,axis);e1/=np.linalg.norm(e1);e2=np.cross(ez,e1)
    vmax=max(c.radial.l for c in channels);degree=2*vmax+2
    if angular=='bessel':n=2*degree+1
    else:
        if type(nphi) is not int or nphi<2*degree+1:raise ValueError('undersampled amplitude in uniform phi oracle')
        n=nphi
    phi=2*np.pi*np.arange(n)/n;circle=np.cos(phi)[:,None]*e1+np.sin(phi)[:,None]*e2
    vt,vp=trajectory.velocities;dv=vp-vt
    phase_const=-.5*(vp@vp-vt@vt)*t
    # Stationary evaluator at the ACTUAL centers; ETF added explicitly below.
    unboosted=Trajectory(centers,((0.,0.,0.),(0.,0.,0.)),trajectory.charges)
    radial_count=0;volparts=[];batch_count=0
    for r0vec,r1vec,wvec in geometry_pairs(edges,R,order):
        volparts.append(float(np.sum(wvec))*2*np.pi)
        for start in range(0,len(r0vec),batch):
            r0,r1,wr=(x[start:start+batch] for x in (r0vec,r1vec,wvec))
            axial=(r0*r0-r1*r1+R*R)/(2*R)
            # Factored Heron expression avoids subtracting nearly equal squares.
            perpsq=((r0+r1+R)*(r0+r1-R)*(R+r0-r1)*(R-r0+r1))/(4*R*R)
            if np.any(perpsq < -1e-10*max(1.,L*L)):raise ArithmeticError('invalid distance triangle')
            perp=np.sqrt(np.maximum(perpsq,0.));base=centers[0]+axial[:,None]*ez
            points=base[:,None,:]+perp[:,None,None]*circle[None,:,:]
            B,g,_=basis_values(points.reshape(-1,3),channels,unboosted,0.)
            vel=np.array([trajectory.velocities[c.center] for c in channels])
            dot=-np.einsum('ncj,cj->nc',g,vel)-.5j*np.sum(vel*vel,axis=1)[None,:]*B
            g=g+1j*B[:,:,None]*vel[None,:,:]
            if angular=='bessel':
                aa=perp*(dv@e1);bb=perp*(dv@e2)
                wa=phase_ring_weights(np.hypot(aa,bb),np.arctan2(bb,aa),degree)
                wp=wr[:,None]*np.exp(1j*(base@dv+phase_const))[:,None]*wa
            else:
                wp=wr[:,None]*(2*np.pi/n)*np.exp(1j*(points@dv+phase_const))
            wtp=wp.ravel();wpt=wtp.conj()
            V=np.repeat(-trajectory.charges[0]/r0-trajectory.charges[1]/r1,n)
            BT,BP=B[:,ti],B[:,pi]
            acc['S_tp']+=BT.conj().T@(wtp[:,None]*BP)
            acc['S_pt']+=BP.conj().T@(wpt[:,None]*BT)
            acc['H_tp']+=BT.conj().T@((wtp*V)[:,None]*BP)
            acc['H_pt']+=BP.conj().T@((wpt*V)[:,None]*BT)
            for j in range(3):
                gT,gP=g[:,ti,j],g[:,pi,j]
                acc['H_tp']+=.5*gT.conj().T@(wtp[:,None]*gP)
                acc['H_pt']+=.5*gP.conj().T@(wpt[:,None]*gT)
            acc['D_tp']+=BT.conj().T@(wtp[:,None]*dot[:,pi])
            acc['D_pt']+=BP.conj().T@(wpt[:,None]*dot[:,ti])
            radial_count+=len(r0);batch_count+=1
        if callback and batch_count%100==0:callback({'radial_pairs':radial_count})
    volume=math.fsum(volparts);exact=intersection_volume(L,R)
    return {**acc,'metadata':{'angular':angular,'amplitude_degree_bound':degree,'angular_samples':n,'radial_order':order,'radial_pairs':radial_count,'basis_points':radial_count*n,'volume':volume,'volume_exact':exact,'volume_relative_error':abs(volume-exact)/exact,'same_center_computed':False,'production_admission':'HOLD'}}
