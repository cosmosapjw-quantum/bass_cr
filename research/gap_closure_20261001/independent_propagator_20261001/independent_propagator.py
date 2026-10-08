"""Nonnative CF4 reference and exact-trajectory comparison with existing TP1.

No production algorithm or physical run is replaced. Cholesky whitening keeps
the derivative connection; omitting it changes the differential equation.
"""
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json
import sys
import numpy as np
from scipy.linalg import expm, solve_triangular


@dataclass(frozen=True)
class WhitenedGenerator:
    R: np.ndarray
    X: np.ndarray
    B: np.ndarray
    compatibility_defect: float
    antihermitian_defect: float


def _congruence_inverse(R,M):
    # R^-dagger M R^-1 using two triangular solves, no explicit inverse.
    left=solve_triangular(R.conj().T,M,lower=True)
    return solve_triangular(R.T,left.T,lower=True).T


def whitened_generator(S,H,D,Sdot,*,tolerance=1e-12):
    S,H,D,Sdot=(np.asarray(a,complex) for a in (S,H,D,Sdot))
    if S.ndim!=2 or S.shape[0]!=S.shape[1] or S.shape[0]==0:
        raise ValueError('nonempty square matrices required')
    if any(a.shape!=S.shape or not np.isfinite(a).all() for a in (S,H,D,Sdot)):
        raise ValueError('finite matrices of the same shape required')
    for name,a in (('S',S),('H',H),('Sdot',Sdot)):
        if np.linalg.norm(a-a.conj().T)>tolerance*max(1.,np.linalg.norm(a)):
            raise ValueError(name+' must be Hermitian')
    R=np.linalg.cholesky(S).conj().T
    defect=float(np.linalg.norm(Sdot-D-D.conj().T))
    if defect>tolerance*max(1.,np.linalg.norm(Sdot),np.linalg.norm(D+D.conj().T)):
        raise ValueError('metric derivative compatibility failed')
    E=_congruence_inverse(R,Sdot)
    X=np.triu(E,1)+np.diag(np.real(np.diag(E))/2)
    B=X-_congruence_inverse(R,D)-1j*_congruence_inverse(R,H)
    return WhitenedGenerator(R,X,B,defect,float(np.linalg.norm(B+B.conj().T)))


def propagate_cf4(provider,c0,t0,tf,nstep):
    if type(nstep) is not int or nstep<1 or not np.isfinite([t0,tf]).all() or tf<=t0:
        raise ValueError('positive integer step count and finite increasing interval required')
    s0=provider.at(t0);g0=whitened_generator(s0.S,s0.H,s0.D,s0.Sdot)
    y=g0.R@np.asarray(c0,complex)
    norm0=float(np.vdot(y,y).real)
    if not np.isfinite(y).all() or norm0<=0: raise ValueError('finite nonzero initial state required')
    # Preserve supplied norm; do not renormalize during propagation.
    norms=[norm0]; maxdef=g0.antihermitian_defect
    h=(tf-t0)/nstep; d=np.sqrt(3.)/6
    early=0.5-d;late=0.5+d
    a1=(3-2*np.sqrt(3.))/12;a2=(3+2*np.sqrt(3.))/12
    for k in range(nstep):
        t=t0+k*h
        s1=provider.at(t+early*h);s2=provider.at(t+late*h)
        g1=whitened_generator(s1.S,s1.H,s1.D,s1.Sdot)
        g2=whitened_generator(s2.S,s2.H,s2.D,s2.Sdot)
        # The rightmost (early-weighted) exponential acts first.
        y=expm(h*(a2*g1.B+a1*g2.B))@y
        y=expm(h*(a1*g1.B+a2*g2.B))@y
        norms.append(float(np.vdot(y,y).real))
        maxdef=max(maxdef,g1.antihermitian_defect,g2.antihermitian_defect)
    sf=provider.at(tf);Rf=np.linalg.cholesky(sf.S).conj().T
    cf=solve_triangular(Rf,y,lower=False)
    return {'final_state':cf,'nstep':nstep,'max_norm_drift':float(max(abs(x-norm0) for x in norms)),
            'max_generator_defect':float(maxdef),'initial_metric_norm':norm0,'operator_queries':2*nstep+2}


class SyntheticTrajectory:
    """Noncommuting analytic physical evolution and moving nonorthogonal basis."""
    sx=np.array([[0,1],[1,0]],complex)
    sy=np.array([[0,-1j],[1j,0]],complex)
    sz=np.diag([1.,-1.]).astype(complex)

    def __init__(self): self.calls=0

    def components(self,t):
        r1=np.exp(.12*np.sin(t));r2=np.exp(-.1*np.cos(.5*t))
        R=np.array([[r1,.2*np.sin(.7*t)+.1j*np.cos(.9*t)],[0,r2]],complex)
        Rd=np.array([[.12*np.cos(t)*r1,.14*np.cos(.7*t)-.09j*np.sin(.9*t)],[0,.05*np.sin(.5*t)*r2]],complex)
        gamma=.17*np.sin(.8*t);gammad=.136*np.cos(.8*t)
        V=expm(-1j*gamma*self.sy);Vd=(-1j*gammad*self.sy)@V
        phi=.3*t+.11*np.sin(1.4*t);phid=.3+.154*np.cos(1.4*t)
        theta=.5*t+.07*np.sin(.9*t);thetad=.5+.063*np.cos(.9*t)
        Z=expm(-1j*phi*self.sz);U=Z@expm(-1j*theta*self.sx)
        h=phid*self.sz+thetad*Z@self.sx@Z.conj().T
        basis=V@R;basisdot=Vd@R+V@Rd
        return R,Rd,basis,basisdot,h,U

    def at(self,t):
        self.calls+=1
        R,Rd,b,bd,h,_=self.components(t)
        # Sdot is evaluated from Rdot, independently of D's basisdot path.
        return SimpleNamespace(S=b.conj().T@b,H=b.conj().T@h@b,D=b.conj().T@bd,
                               Sdot=Rd.conj().T@R+R.conj().T@Rd)

    def exact(self,t):
        _,_,b,_,_,U=self.components(t)
        v=np.array([1.,.3j],complex);v/=np.linalg.norm(v)
        return np.linalg.solve(b,U@v)


def _observable(c,S):
    J=np.array([[1],[0]],complex)
    q=S@J@np.linalg.solve(J.conj().T@S@J,J.conj().T@S)
    return float(np.vdot(c,q@c).real)


def _metrics(cf,exact,S):
    d=cf-exact
    return {'metric_state_error':float(np.sqrt(max(0.,np.vdot(d,S@d).real))),
            'selected_population_error':abs(_observable(cf,S)-_observable(exact,S))}


def benchmark():
    legacy=Path(__file__).resolve().parents[2]/'foundation_rebuild'/'tp1_short_transport_20260926'
    if str(legacy) not in sys.path: sys.path.insert(0,str(legacy))
    from metric_transport import run_candidate,metric_frame_generator
    from reference_transport import run_reference
    p=SyntheticTrajectory();c0=p.exact(0);exact=p.exact(3);S=p.at(3).S
    midpoint=[];cf4=[]
    for n in (8,16,32,64,128):
        pm=SyntheticTrajectory();m=run_candidate(pm,c0,0,3,n)
        midpoint.append({'nstep':n,**_metrics(m.final_state,exact,S),
                         'max_norm_drift':m.max_norm_drift,'max_generator_defect':m.max_generator_defect,
                         'operator_queries':pm.calls})
        pc=SyntheticTrajectory();c=propagate_cf4(pc,c0,0,3,n)
        cf4.append({'nstep':n,**_metrics(c['final_state'],exact,S),
                    'max_norm_drift':c['max_norm_drift'],'max_generator_defect':c['max_generator_defect'],
                    'operator_queries':pc.calls})
    pr=SyntheticTrajectory();r=run_reference(pr,[],0,3,c0=c0,rtol=5e-13,atol=5e-15,sample_times=np.linspace(0,3,25))
    ref={**_metrics(r.final_state,exact,S),'max_norm_drift':r.max_norm_drift,
         'rtol':r.rtol,'atol':r.atol,'nfev':r.nfev,'operator_queries':pr.calls}
    generator_disagreement=[]
    for t in (0.,.6,1.4,3.):
        s=p.at(t);a=metric_frame_generator(s);b=whitened_generator(s.S,s.H,s.D,s.Sdot)
        generator_disagreement.append(float(np.linalg.norm(a.G-b.B)))
    ratios=lambda rows:[a['metric_state_error']/b['metric_state_error'] for a,b in zip(rows,rows[1:])]
    source_hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (legacy/'metric_transport.py',legacy/'reference_transport.py')}
    return {'scope':'Synthetic exact noncommuting two-state trajectory; interval [0,3] atomic time',
            'midpoint':midpoint,'cf4':cf4,'direct_dop853':ref,
            'midpoint_error_ratios':ratios(midpoint),'cf4_error_ratios':ratios(cf4),
            'max_existing_generator_disagreement':max(generator_disagreement),
            'source_hashes':source_hashes,'physical_parity_certified':False,
            'physical_parity_budget':None,'production_tolerance_claim':False,
            'new_native_calls':0,'new_external_runs':0}


if __name__=='__main__':
    result=benchmark()
    Path(__file__).with_name('E_INDEPENDENT_PROPAGATOR_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
