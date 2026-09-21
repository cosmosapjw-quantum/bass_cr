from __future__ import annotations
import sys,math
from pathlib import Path
import numpy as np
from scipy.linalg import eigh,solve_triangular
from .observables import projectile_speed_au,metric_projector_probability

_VENDOR=Path(__file__).resolve().parents[1]/'vendor_w1r'
sys.path.insert(0,str(_VENDOR))
from gaussian_cartesian import Shell,overlap,kinetic,nuclear,moving_ket_overlap

class OneElectronAOCC:
    def __init__(self,cfg):
        self.cfg=dict(cfg); self.v=projectile_speed_au(cfg['energy_keV_per_u']); self.b=float(cfg['b'])
        self.zmax=float(cfg.get('zmax',30)); self.dt=float(cfg.get('dt',0.05)); self.t0=-self.zmax/self.v; self.tf=self.zmax/self.v
        self.groups=[]; off=0
        specs=[('s',(0,0,0),int(cfg.get('ns',10)),float(cfg.get('alpha_min',0.001)),float(cfg.get('alpha_max',100.0)))]
        np_=int(cfg.get('np',6))
        if np_:
            for ax in range(3): specs.append((f'p{ax}',tuple(int(i==ax) for i in range(3)),np_,float(cfg.get('pmin',0.001)),float(cfg.get('pmax',10.0))))
        for name,pow,n,amin,amax in specs:
            exps=np.geomspace(amin,amax,n); sh=Shell(exps,pow,np.zeros(3),np.zeros(3))
            S=overlap(sh,sh).real; H=(kinetic(sh,sh)+nuclear(sh,sh,[0,0,0])).real; eps,C=eigh(H,S)
            for j in range(C.shape[1]):
                k=np.argmax(abs(C[:,j]));
                if C[k,j]<0: C[:,j]*=-1
            self.groups.append({'name':name,'pow':pow,'exps':exps,'eps':eps,'C':C,'sl':slice(off,off+n)}); off+=n
        self.eps=np.concatenate([g['eps'] for g in self.groups]); self.na=len(self.eps)
        # Keep a finite pseudostate window but always all negative states.
        emax=float(cfg.get('eps_max',5.0)); keep=np.where(self.eps<=emax)[0]; self.keep=keep; self.epsk=self.eps[keep]
        self.basis=[('T',int(a)) for a in keep]+[('P',int(a)) for a in keep]; self.nb=len(self.basis)
        self._index_by_atomic={int(a):i for i,a in enumerate(keep)}
        if 0 not in self._index_by_atomic: raise RuntimeError('ground state not retained')
        self.target_ground=self._index_by_atomic[0]
    def center(self,label,t): return np.zeros(3) if label=='T' else np.array([self.b,0.,self.v*t])
    def kvec(self,label): return np.zeros(3) if label=='T' else np.array([0.,0.,self.v])
    def velocity(self,label): return np.zeros(3) if label=='T' else np.array([0.,0.,self.v])
    def phase(self,label,t): return 1.0+0j if label=='T' else np.exp(-0.5j*self.v*self.v*t)
    def atomic_components(self,a):
        for g in self.groups:
            if g['sl'].start<=a<g['sl'].stop: return g,a-g['sl'].start
        raise IndexError(a)
    def matrix(self,t):
        O=np.zeros((self.nb,self.nb),complex);H=np.zeros_like(O);D=np.zeros_like(O)
        for i,(L,a) in enumerate(self.basis):
            ga,ia=self.atomic_components(a); ca=ga['C'][:,ia]; A=self.center(L,t); ka=self.kvec(L); pha=self.phase(L,t)
            sha=Shell(ga['exps'],ga['pow'],A,ka)
            for j,(R,b) in enumerate(self.basis):
                gb,ib=self.atomic_components(b); cb=gb['C'][:,ib]; B=self.center(R,t); kb=self.kvec(R); phb=self.phase(R,t); shb=Shell(gb['exps'],gb['pow'],B,kb)
                ph=np.conj(pha)*phb
                S0=ca.T@overlap(sha,shb)@cb
                H0=ca.T@(kinetic(sha,shb)+nuclear(sha,shb,[0,0,0])+nuclear(sha,shb,self.center('P',t)))@cb
                D0=ca.T@moving_ket_overlap(sha,shb,self.velocity(R))@cb
                if R=='P': D0 += (-0.5j*self.v*self.v)*S0
                O[i,j]=ph*S0; H[i,j]=ph*H0; D[i,j]=ph*D0
        return O,H,D
    @staticmethod
    def metric_factor(O): return np.linalg.cholesky((O+O.conj().T)/2).conj().T
    @staticmethod
    def unitary_step(G,y,dt):
        K=0.5*(1j*G+(1j*G).conj().T); lam,U=np.linalg.eigh(K); return U@(np.exp(-1j*dt*lam)*(U.conj().T@y))
    def generator(self,t):
        O,H,D=self.matrix(t); R=self.metric_factor(O); Ri=solve_triangular(R,np.eye(self.nb),lower=False)
        Dt=Ri.conj().T@D@Ri; Ht=Ri.conj().T@H@Ri; W=Dt+Dt.conj().T
        X=np.triu(W,1)+np.diag(np.real(np.diag(W))/2); G=X-Dt-1j*Ht
        defect=float(np.linalg.norm(G+G.conj().T)/max(np.linalg.norm(G),1e-30))
        return G,R,O,defect
    def run(self):
        span=self.tf-self.t0; nstep=math.ceil(span/self.dt); dt=span/nstep
        G,R,O,defect=self.generator(self.t0); C=np.zeros(self.nb,complex); C[self.target_ground]=1.; y=R@C; md=defect
        for j in range(nstep):
            t=self.t0+(j+0.5)*dt; G,Rm,Om,d=self.generator(t); y=self.unitary_step(G,y,dt); md=max(md,d)
        G,R,O,defect=self.generator(self.tf); C=np.linalg.solve(R,y); norm=float(np.real(np.vdot(C,O@C)))
        pidx=[i for i,(c,a) in enumerate(self.basis) if c=='P' and self.eps[a]<0]
        tidx=[i for i,(c,a) in enumerate(self.basis) if c=='T' and self.eps[a]<0]
        return {'status':'completed','nstep':nstep,'dt_actual':dt,'v_au':self.v,'nbasis':self.nb,'norm':norm,'P_projectile_bound':metric_projector_probability(O,C,pidx),'P_target_bound':metric_projector_probability(O,C,tidx),'max_antihermitian_defect':md,'negative_atomic_energies_Eh':[float(x) for x in self.eps[self.eps<0]],'claim':'one-electron AOCC independent comparator; W1R two-electron/Hminus physics not imported'}
