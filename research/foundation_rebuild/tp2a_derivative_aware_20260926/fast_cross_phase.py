"""Batched s+p cross integration with unchanged FEM nodes and Bessel moments.

Only repeated evaluation and array layout change. All six raw blocks are
accumulated independently in complex128; no symmetrization, interpolation,
mode deletion or physics approximation. l>1 is explicitly unsupported here.
"""
from __future__ import annotations
import math
import time
import numpy as np
import paths
from bass_foundations.radial_basis import FEMRadial
from aligned_cross import geometry_pairs, phase_ring_weights, intersection_volume

_KEYS = ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')
_Y00 = 1/math.sqrt(4*math.pi)
_P = {-1: np.array([1.,-1j,0.])*math.sqrt(3/(8*math.pi)),
       0: np.array([0.,0.,1.])*math.sqrt(3/(4*math.pi)),
       1: np.array([-1.,-1j,0.])*math.sqrt(3/(8*math.pi))}


def _validate(channels, edges, order, batch):
    ch = tuple(channels)
    if not ch or len(ch)>128 or not all(isinstance(c.radial,FEMRadial) for c in ch):
        raise ValueError('finite FEM channels required')
    if any(c.radial.l not in (0,1) for c in ch):
        raise ValueError('optimized kernel admits s+p only; use reference for l>1')
    e=np.asarray(edges,float)
    if (e.ndim!=1 or len(e)<2 or e[0]!=0 or not np.isfinite(e).all() or np.any(np.diff(e)<=0)
        or any(not np.array_equal(c.radial.edges,e) for c in ch)):
        raise ValueError('identical strictly increasing radial edges required')
    if isinstance(order,bool) or not isinstance(order,int) or not 2<=order<=64:
        raise ValueError('order must be 2..64')
    if isinstance(batch,bool) or not isinstance(batch,int) or not 1<=batch<=4096:
        raise ValueError('batch must be 1..4096')
    if len({(c.center,c.radial.identity,c.m) for c in ch})!=len(ch):
        raise ValueError('duplicate channels')
    groups=[tuple(c for c in ch if c.center==j) for j in (0,1)]
    if not all(groups):raise ValueError('both centers required')
    return groups,e


def _batches(edges,R,order,batch):
    """Keep reference node order, combine small generator packets."""
    buf=np.empty((3,batch));used=0
    for row in geometry_pairs(edges,R,order):
        n=len(row[0]);start=0
        while start<n:
            take=min(n-start,batch-used)
            for k in range(3):buf[k,used:used+take]=row[k][start:start+take]
            start+=take;used+=take
            if used==batch:
                yield buf
                used=0
    if used:yield buf[:,:used]


def ring_basis(r, xyz, channels, velocity):
    """Unphased chi/boosted gradients/direct time derivative on all ring nodes.

    r is the exact distance coordinate, independent of phi. Each distinct
    radial mode is evaluated once per distance batch, not once per m or phi.
    xyz has shape (distance_pairs, ring_points, 3)."""
    r=np.asarray(r,float);xyz=np.asarray(xyz,float);v=np.asarray(velocity,float)
    npair,nphi,_=xyz.shape;nch=len(channels);npts=npair*nphi
    B=np.empty((npts,nch),complex);grad=np.empty((3,npts,nch),complex)
    radial={}
    for i,c in enumerate(channels):
        key=c.radial.identity
        if key not in radial:radial[key]=c.radial.evaluate(r)
        u,du=radial[key];l=c.radial.l
        a=u/r**(l+1)
        ar=(du/r**(l+1)-(l+1)*u/r**(l+2))/r
        if l==0:
            solid=_Y00
            B[:,i]=np.broadcast_to((a*solid)[:,None],(npair,nphi)).ravel()
            g=ar[:,None,None]*solid*xyz
        else:
            coeff=_P[c.m];solid=xyz@coeff
            B[:,i]=(a[:,None]*solid).ravel()
            g=a[:,None,None]*coeff+ar[:,None,None]*solid[:,:,None]*xyz
        for j in range(3):grad[j,:,i]=g[:,:,j].ravel()
    dot=-(v[0]*grad[0]+v[1]*grad[1]+v[2]*grad[2])-.5j*float(v@v)*B
    for j in range(3):grad[j]+=1j*v[j]*B
    return B,grad,dot


def fast_cross(trajectory, channels, edges, t, *, order=24, batch=1024, progress=None, evaluator=None, phase_budget=None):
    groups,edges=_validate(channels,edges,order,batch)
    if not np.isfinite(t):raise ValueError('finite time required')
    centers=trajectory.centers(t);delta=centers[1]-centers[0];R=float(np.linalg.norm(delta));L=float(edges[-1])
    if R<=1e-7:raise ValueError('unresolved coincident foci')
    nt,np_=map(len,groups)
    acc={k:np.zeros((nt,np_) if k.endswith('tp') else (np_,nt),complex) for k in _KEYS}
    if R>=2*L:return {**acc,'metadata':{'zero_reason':'DISJOINT_SUPPORTS','radial_pairs':0,'basis_points':0,'same_center_computed':False}}
    ez=delta/R;axis=np.eye(3)[np.argmin(abs(ez))];e1=np.cross(ez,axis);e1/=np.linalg.norm(e1);e2=np.cross(ez,e1)
    lmax=max(c.radial.l for ch in groups for c in ch);degree=2*lmax+2;n=2*degree+1
    phi=2*np.pi*np.arange(n)/n;circle=np.cos(phi)[:,None]*e1+np.sin(phi)[:,None]*e2
    vt,vp=trajectory.velocities;dv=vp-vt;constant=-.5*float(vp@vp-vt@vt)*t
    integration_edges=edges
    if phase_budget is not None:
        from phase_panels import phase_split_edges
        integration_edges=phase_split_edges(edges,R,float(dv@ez),phase_budget)
    count=0;vol=[];last=time.monotonic()
    for r0,r1,wr in _batches(integration_edges,R,order,batch):
        axial=(r0*r0-r1*r1+R*R)/(2*R)
        pp=((r0+r1+R)*(r0+r1-R)*(R+r0-r1)*(R-r0+r1))/(4*R*R)
        if np.min(pp)<-1e-10*max(1.,L*L):raise ArithmeticError('invalid triangle')
        perp=np.sqrt(np.maximum(pp,0.));base=centers[0]+axial[:,None]*ez
        xyz0=axial[:,None,None]*ez+perp[:,None,None]*circle
        xyz1=xyz0-delta
        evaluate=ring_basis if evaluator is None else evaluator
        BT,gT,dT=evaluate(r0,xyz0,groups[0],vt)
        BP,gP,dP=evaluate(r1,xyz1,groups[1],vp)
        aa=perp*float(dv@e1);bb=perp*float(dv@e2)
        weights=phase_ring_weights(np.hypot(aa,bb),np.arctan2(bb,aa),degree)
        wp=(wr[:,None]*np.exp(1j*(base@dv+constant))[:,None]*weights).ravel();wm=wp.conj()
        V=np.repeat(-trajectory.charges[0]/r0-trajectory.charges[1]/r1,n)
        TB=BT.conj().T;PB=BP.conj().T
        acc['S_tp']+=TB@(wp[:,None]*BP);acc['S_pt']+=PB@(wm[:,None]*BT)
        acc['H_tp']+=TB@((wp*V)[:,None]*BP);acc['H_pt']+=PB@((wm*V)[:,None]*BT)
        for j in range(3):
            acc['H_tp']+=.5*gT[j].conj().T@(wp[:,None]*gP[j])
            acc['H_pt']+=.5*gP[j].conj().T@(wm[:,None]*gT[j])
        acc['D_tp']+=TB@(wp[:,None]*dP);acc['D_pt']+=PB@(wm[:,None]*dT)
        count+=len(r0);vol.append(float(np.sum(wr))*2*np.pi)
        if progress and time.monotonic()-last>=2.:
            progress({'radial_pairs':count});last=time.monotonic()
    if not all(np.isfinite(a).all() for a in acc.values()):raise ArithmeticError('nonfinite raw cross block')
    volume=math.fsum(vol);exact=intersection_volume(L,R)
    return {**acc,'metadata':{'backend':('native_sp_batched_v1' if evaluator is not None else 'numpy_sp_batched_v1'),'angular':'bessel','angular_samples':n,'amplitude_degree_bound':degree,
            'radial_order':order,'radial_pairs':count,'basis_points':n*count,'batch_pairs':batch,'phase_budget_rad':phase_budget,'integration_edge_count':len(integration_edges),
            'volume':volume,'volume_exact':exact,'volume_relative_error':abs(volume-exact)/exact,
            'same_center_computed':False,'production_admission':'HOLD'}}
