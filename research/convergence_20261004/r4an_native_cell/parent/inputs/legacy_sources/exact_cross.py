"""Analytically contracted s+p cross operators, retaining original FEM data.

S/H reverse blocks use exact conjugacy, not numerical symmetrization.
Both D directions use independent derivative expressions. Atomic units.
"""
from pathlib import Path
import ctypes,hashlib,json,math,platform,time
import numpy as np
import bootstrap
from fast_cross import _validate,_batches,_P,_Y00
from aligned_cross import intersection_volume
from analytic_moments import moments

KEYS=('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')

def _radials(r,channels):
    out=np.empty((len(r),len(channels),2));memo={}
    for i,c in enumerate(channels):
        key=c.radial.identity
        if key not in memo:memo[key]=c.radial.evaluate(r)
        u,du=memo[key];ell=c.radial.l
        out[:,i,0]=u/r**(ell+1)
        out[:,i,1]=(du/r**(ell+1)-(ell+1)*u/r**(ell+2))/r
    return out

def _coefficients(channels,axes):
    q=np.zeros((len(channels),4),complex)
    for i,c in enumerate(channels):
        if c.radial.l==0:q[i,0]=_Y00
        else:q[i,1:]=axes@_P[c.m]
    return q

class MomentKernel:
    def __init__(self,directory):
        directory=Path(directory).resolve();src=Path(__file__).with_name('moment_kernel.cpp')
        rec=json.loads((directory/'BUILD.json').read_text());lib=directory/'libmoments.so'
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        if rec.get('schema')!='BASS_ANALYTIC_MOMENTS_BUILD_V1' or rec['source_sha256']!=sha(src) or rec['library_sha256']!=sha(lib):
            raise ValueError('analytic native source/binary identity mismatch')
        if rec.get('machine')!=platform.machine() or rec.get('system')!=platform.system():
            raise ValueError('native library architecture mismatch')
        self.receipt=rec;self.lib=ctypes.CDLL(str(lib));self.fn=self.lib.bass_moment_accumulate_v1
        self.ptr=ctypes.POINTER(ctypes.c_double)
        self.fn.argtypes=[ctypes.c_size_t]*3+[self.ptr]*8+[ctypes.c_double]*3+[self.ptr]
        self.fn.restype=ctypes.c_int
        self.real_fn=self.lib.bass_moment_accumulate_real_v1
        self.real_fn.argtypes=self.fn.argtypes;self.real_fn.restype=ctypes.c_int

    def accumulate(self,geo,radt,radp,qt,qp,vel,weights,phase,R,charges,*,real_coefficients=False):
        n=len(geo);nt=len(qt);np_=len(qp)
        if not 0<n<=4096 or not 0<nt<=128 or not 0<np_<=128:raise ValueError('bounded native dimensions required')
        expected=[(n,4),(n,nt,2),(n,np_,2),(nt,4),(np_,4),(6,),(n,6),(n,)]
        dtypes=[float,float,float,complex,complex,float,complex,complex]
        arrays=[np.ascontiguousarray(a,dtype=d) for a,d in zip((geo,radt,radp,qt,qp,vel,weights,phase),dtypes)]
        if any(a.shape!=s or not np.isfinite(a).all() for a,s in zip(arrays,expected)):
            raise ValueError('native input shape/finiteness mismatch')
        if not np.isfinite([R,*charges]).all() or R<=0 or np.any(np.asarray(charges)<=0) or np.any(arrays[0][:,:2]<=0):
            raise ValueError('positive distances and charges required')
        result=np.zeros((4,nt,np_),complex)
        if real_coefficients and (np.any(arrays[3].imag!=0) or np.any(arrays[4].imag!=0)):raise ValueError("real-coefficient branch received complex harmonics")
        fn=self.real_fn if real_coefficients else self.fn
        rc=fn(n,nt,np_,*(a.ctypes.data_as(self.ptr) for a in arrays),float(R),float(charges[0]),float(charges[1]),result.ctypes.data_as(self.ptr))
        if rc or not np.isfinite(result).all():raise ArithmeticError('native contraction failure')
        return result

def cartesian_transform(channels):
    """Exact unitary magnetic-basis transform; no radial-state mixing."""
    n=len(channels);U=np.eye(n,dtype=complex);blocks={}
    for i,c in enumerate(channels):
        if c.radial.l==1:blocks.setdefault(c.radial.identity,{})[c.m]=i
    for ms in blocks.values():
        if set(ms)!={-1,0,1}:return None
        ix=[ms[-1],ms[0],ms[1]]
        U[np.ix_(ix,ix)]=np.array([[1/np.sqrt(2),1j/np.sqrt(2),0],[0,0,1],[-1/np.sqrt(2),1j/np.sqrt(2),0]])
    return U

def frame(trajectory,t):
    centers=trajectory.centers(t);delta=centers[1]-centers[0];R=float(np.linalg.norm(delta))
    if R<=1e-7:raise ValueError('coincident foci not admitted')
    ez=delta/R;dv=trajectory.velocities[1]-trajectory.velocities[0]
    perp=dv-(dv@ez)*ez;kn=float(np.linalg.norm(perp))
    if kn>4*np.finfo(float).eps*max(1.,np.linalg.norm(dv)):
        e1=perp/kn;e2=np.cross(ez,e1);e2/=np.linalg.norm(e2);e1=np.cross(e2,ez)
    else:
        axis=np.eye(3)[np.argmin(abs(ez))];e1=np.cross(ez,axis);e1/=np.linalg.norm(e1);e2=np.cross(ez,e1)
    return centers,R,np.array([ez,e1,e2]),dv

def split_edges(edges,subdivisions):
    if type(subdivisions) is not int or subdivisions not in (1,2,4):raise ValueError('subdivisions must be 1,2,4')
    if subdivisions==1:return np.array(edges,copy=True)
    out=[float(edges[0])]
    for a,b in zip(edges[:-1],edges[1:]):
        out.extend(np.linspace(a,b,subdivisions+1)[1:-1].tolist());out.append(float(b))
    return np.array(out)

def resolution_edges(edges,R,kparallel,subdivisions=1,phase_budget=None):
    panel=np.asarray(edges,float)
    if phase_budget is not None:
        from phase_panels import phase_split_edges
        panel=phase_split_edges(panel,R,kparallel,phase_budget)
    return split_edges(panel,subdivisions)

def rebatch(generator,batch):
    buffer=np.empty((3,batch));used=0
    for packet in generator:
        if len(packet)!=3 or any(len(a)!=len(packet[0]) for a in packet):raise ValueError('invalid quadrature packet')
        start=0;length=len(packet[0])
        while start<length:
            take=min(length-start,batch-used)
            for k in range(3):buffer[k,used:used+take]=packet[k][start:start+take]
            used+=take;start+=take
            if used==batch:
                yield buffer;used=0
    if used:yield buffer[:,:used]

def cross(trajectory,channels,t,kernel,*,order=24,subdivisions=1,phase_budget=None,batch=1024,pair_rule=None,progress=None,sector='full'):
    channels=tuple(channels)
    if not channels:raise ValueError('nonempty channels required')
    groups,edges=_validate(channels,channels[0].radial.edges,order,batch)
    # The native specialization assumes the real eigenvectors of this model.
    # Reject, rather than silently dropping, genuinely complex radial data.
    seen={}
    for channel in channels:
        r=channel.radial;coef=np.asarray(r.polynomial_coefficients)
        if np.iscomplexobj(coef):raise ValueError('real radial coefficient payload required')
        if not np.isfinite(coef).all():raise ValueError('finite radial coefficient payload required')
        fingerprint=(r.l,float(r.energy),hashlib.sha256(coef.tobytes()).hexdigest())
        if r.identity in seen and seen[r.identity]!=fingerprint:raise ValueError('inconsistent radial identity payload')
        seen[r.identity]=fingerprint
    if not np.isfinite(t):raise ValueError('finite time required')
    if type(subdivisions) is not int or subdivisions not in (1,2,4):raise ValueError('subdivisions must be 1,2,4')
    if phase_budget is not None and (not np.isfinite(phase_budget) or phase_budget<=0):raise ValueError('positive phase budget required')
    centers,R,axes,dv=frame(trajectory,t);L=float(edges[-1]);nt,np_=map(len,groups)
    output=np.zeros((4,nt,np_),complex)
    transforms=[cartesian_transform(g) for g in groups]
    real_coefficients=all(u is not None for u in transforms)
    if sector not in ('full','even'):raise ValueError('sector must be full or even')
    if sector=='even' and (not real_coefficients or trajectory.origins[0,1]!=trajectory.origins[1,1] or np.any(trajectory.velocities[:,1]!=0)):
        raise ValueError('even-sector contraction requires complete multiplets and exact planar trajectory')
    coeff=[];active=[]
    for g,u in zip(groups,transforms):
        q=_coefficients(g,axes)
        if real_coefficients:
            # Transform in the lab first: px/py/pz are exactly real analytically.
            lab=_coefficients(g,np.eye(3));cart=u.T@lab
            if np.max(abs(cart.imag))>1e-14:raise ArithmeticError('Cartesian harmonic transform inconsistent')
            cart=cart.real
            ix=np.arange(len(g)) if sector=='full' else np.flatnonzero(abs(cart[:,2])<1e-14)
            q=np.column_stack((cart[ix,0],cart[ix,1:]@axes.T)).astype(complex)
            active.append(ix)
        else:active.append(np.arange(len(g)))
        coeff.append(q)
    qt,qp=coeff
    if sector=='even':output=np.zeros((4,len(qt),len(qp)),complex)
    if R>=2*L:
        a,b=output.shape[1:]
        return {**{k:np.zeros((a,b) if k.endswith('tp') else (b,a),complex) for k in KEYS},
            'metadata':{'zero_reason':'DISJOINT_SUPPORTS','sector':sector,'radial_pairs':0,'same_center_computed':False,
              'sector_columns_T':active[0].tolist(),'sector_columns_P':active[1].tolist(),'original_cross_shape':[nt,np_]}}
    vt,vp=trajectory.velocities;vel=np.r_[axes@vt,axes@vp]
    phase_constant=-.5*float(vp@vp-vt@vt)*t+float(centers[0]@dv)
    kp=float(dv@axes[0]);kt=float(np.hypot(dv@axes[1],dv@axes[2]))
    if pair_rule is None:
        panel=resolution_edges(edges,R,kp,subdivisions,phase_budget)
        packets=_batches(panel,R,order,batch)
    else:
        packets=rebatch(pair_rule(edges,R,order,float(np.linalg.norm(dv))),batch)
    count=0;vol=[];last=time.monotonic();started=last
    for r0,r1,wr in packets:
        axial=(r0*r0-r1*r1+R*R)/(2*R)
        pp=((r0+r1+R)*(r0+r1-R)*(R+r0-r1)*(R-r0+r1))/(4*R*R)
        if np.min(pp)<-1e-10*max(1.,L*L):raise ArithmeticError('invalid triangle')
        rho=np.sqrt(np.maximum(pp,0.))
        geo=np.column_stack((r0,r1,axial,rho))
        a0=_radials(r0,groups[0])[:,active[0],:];a1=_radials(r1,groups[1])[:,active[1],:]
        m=moments(kt*rho);phase=wr*np.exp(1j*(kp*axial+phase_constant))
        output+=kernel.accumulate(geo,a0,a1,qt,qp,vel,m,phase,R,trajectory.charges,real_coefficients=real_coefficients)
        vol.append(2*np.pi*float(np.sum(wr)));count+=len(r0)
        if progress and time.monotonic()-last>=2:
            progress({'radial_pairs':count});last=time.monotonic()
    if not np.isfinite(output).all():raise ArithmeticError('nonfinite accumulated matrix')
    if real_coefficients and sector=='full':
        u0,u1=transforms
        output=np.array([u0@a@u1.conj().T for a in output])
    S,H,dt,dc=output;exact=intersection_volume(L,R);volume=math.fsum(vol)
    return {'S_tp':S,'S_pt':S.conj().T.copy(),'H_tp':H,'H_pt':H.conj().T.copy(),'D_tp':dt,'D_pt':dc.conj().T.copy(),
       'metadata':{'backend':'EXACT_SP_MOMENTS_CXX_V1','sector':sector,'cartesian_specialization':real_coefficients,'angular_samples':0,'analytic_moments':6,'max_azimuth_degree':3,
         'SH_reverse':'DERIVED_CONJUGACY_NOT_INDEPENDENT_HERMITICITY_TEST','D':'BOTH_DIRECT','order':order,'subdivisions':subdivisions,
         'phase_budget':phase_budget,'sector_columns_T':active[0].tolist(),'sector_columns_P':active[1].tolist(),'original_cross_shape':[nt,np_],'radial_pairs':count,'volume':volume,'volume_exact':exact,'volume_relative_error':abs(volume-exact)/exact,
         'wall_seconds':time.monotonic()-started,'same_center_computed':False,'production_admission':'HOLD'}}
