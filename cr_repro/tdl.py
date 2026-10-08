from __future__ import annotations
from pathlib import Path
import json,math,time,os
import numpy as np
from .backend import get_backend,asnumpy
from .grid import GridSpec,k2_grid,absorber_mask
from .hydrogen import one_s,orbital,bound_quantum_numbers
from .observables import projectile_speed_au,estimator_gap_bound
from .util import atomic_json,atomic_npy,config_hash

class TDLRunner:
    def __init__(self,cfg):
        self.cfg=dict(cfg); self.xp,self.backend=get_backend(cfg.get('backend','auto'))
        self.spec=GridSpec.from_dict(cfg['grid']); self.x,self.y,self.z=self.spec.axes(self.xp); self.dv=self.spec.dv
        self.k2=k2_grid(self.spec,self.xp); self.v=projectile_speed_au(cfg['energy_keV_per_u']); self.b=float(cfg['b'])
        self.z_start=float(cfg.get('z_start',-30)); self.z_stop=float(cfg.get('z_stop',60)); self.dt=float(cfg['dt'])
        T=(self.z_stop-self.z_start)/self.v; self.nstep=math.ceil(T/self.dt); self.dt_actual=T/self.nstep
        self.t0=self.z_start/self.v; self.tf=self.z_stop/self.v
        self.mask=absorber_mask(self.spec,self.xp,float(cfg.get('absorber_width',4)),float(cfg.get('absorber_power',0.125)))
        self.kin=self.xp.exp(-0.5j*self.dt_actual*self.k2)
        X=self.x[:,None,None];Y=self.y[None,:,None];Z=self.z[None,None,:]
        self.X,self.Y,self.Z=X,Y,Z
        self.Vtarget=-1/self.xp.sqrt(X*X+Y*Y+Z*Z)
    def norm(self,psi): return float(asnumpy(self.xp.sum(self.xp.abs(psi)**2)*self.dv))
    def normalize(self,psi): return psi/self.xp.sqrt(self.xp.sum(self.xp.abs(psi)**2)*self.dv)
    def target_energy(self,psi):
        pk=self.xp.fft.fftn(psi); Tpsi=self.xp.fft.ifftn(0.5*self.k2*pk)
        val=self.xp.sum(self.xp.conj(psi)*(Tpsi+self.Vtarget*psi))*self.dv
        return float(asnumpy(self.xp.real(val)))
    def relaxed_initial(self):
        mode=self.cfg.get('initial_state','imag_time')
        psi=self.xp.asarray(one_s(asnumpy(self.X),asnumpy(self.Y),asnumpy(self.Z)),dtype=self.xp.complex128)
        psi=self.normalize(psi)
        if mode=='analytic': return psi,{'mode':'analytic','energy_Eh':self.target_energy(psi),'steps':0}
        tau=float(self.cfg.get('imag_dt',0.05)); n=int(self.cfg.get('imag_steps',300)); kin=self.xp.exp(-0.5*tau*self.k2)
        vh=self.xp.exp(-0.5*tau*self.Vtarget)
        last=None
        for j in range(n):
            psi=vh*psi; psi=self.xp.fft.ifftn(kin*self.xp.fft.fftn(psi)); psi=vh*psi; psi=self.normalize(psi)
            if (j+1)%max(10,n//10)==0: last=self.target_energy(psi)
        return psi,{'mode':'imag_time','energy_Eh':last if last is not None else self.target_energy(psi),'steps':n,'imag_dt':tau}
    def Vmid(self,t):
        zp=self.v*t
        rp=self.xp.sqrt((self.X-self.b)**2+self.Y*self.Y+(self.Z-zp)**2)
        return self.Vtarget-1/rp
    def step(self,psi,t_mid):
        ph=self.xp.exp(-0.5j*self.dt_actual*self.Vmid(t_mid)); psi=ph*psi
        psi=self.xp.fft.ifftn(self.kin*self.xp.fft.fftn(psi)); psi=ph*psi
        return self.mask*psi
    def _project_state(self,psi,n,l,m,t):
        xr=asnumpy(self.X)-self.b; yr=asnumpy(self.Y); zr=asnumpy(self.Z)-self.v*t
        phi=orbital(n,l,m,xr,yr,zr)
        phase=np.exp(1j*self.v*asnumpy(self.Z)-0.5j*self.v*self.v*t-1j*(-0.5/n**2)*t)
        st=phi*phase
        a=np.sum(np.conj(st)*asnumpy(psi))*self.dv
        norm=np.sum(np.abs(st)**2)*self.dv
        return complex(a),float(norm),st
    def analyze(self,psi):
        hpsi=asnumpy(psi); t=self.tf; nmax=int(self.cfg.get('project_nmax',3)); qns=bound_quantum_numbers(nmax)
        amps={}; norms={}; P=0.0
        # First pass overlaps.
        for n,l,m in qns:
            a,nrm,_=self._project_state(hpsi,n,l,m,t); amps[f'{n},{l},{m}']=[a.real,a.imag]; norms[f'{n},{l},{m}']=nrm; P+=abs(a)**2
        region=asnumpy(self.z)>float(self.cfg.get('capture_plane',30.0)); preg=float(np.sum(np.abs(hpsi[:,:,region])**2)*self.dv)
        out={'P_bound_truncated_nmax':float(P),'project_nmax':nmax,'P_region':preg,'region_minus_bound':preg-float(P),
             'state_amplitudes':amps,'finite_grid_state_norms':norms,'wavefunction_norm':self.norm(psi)}
        if nmax==1:
            a,_,st=self._project_state(hpsi,1,0,0,t); bcomp=a*st; resid=hpsi-bcomp
            eb=float(np.sum(np.abs(bcomp[:,:,~region])**2)*self.dv); ec=float(np.sum(np.abs(resid[:,:,region])**2)*self.dv)
            out.update({'eps_b_n1':eb,'eps_c_n1':ec,'estimator_gap_bound_n1':estimator_gap_bound(abs(a)**2,eb,ec)})
        return out
    def _save_checkpoint(self, out, psi, metadata):
        atomic_npy(out/'state.npy',asnumpy(psi))
        atomic_json(out/'state.json',metadata)

    def run(self,outdir,max_steps=None):
        out=Path(outdir); out.mkdir(parents=True,exist_ok=True); ident=config_hash(self.cfg); meta=out/'state.json'; state=out/'state.npy'
        if meta.exists():
            m=json.loads(meta.read_text());
            if m['config_hash']!=ident: raise ValueError('checkpoint config mismatch')
            psi=self.xp.asarray(np.load(state,allow_pickle=False)); done=int(m['done']); init=m['initial']
        else:
            psi,init=self.relaxed_initial(); done=0
        stop=self.nstep if max_steps is None else min(self.nstep,done+int(max_steps)); stride=int(self.cfg.get('checkpoint_stride',100)); tic=time.time()
        for j in range(done,stop):
            tm=self.t0+(j+0.5)*self.dt_actual; psi=self.step(psi,tm); done=j+1
            if done%stride==0 or done==stop:
                self._save_checkpoint(out,psi,{'config_hash':ident,'done':done,'nstep':self.nstep,'initial':init,'norm':self.norm(psi),'backend':self.backend})
        if done<self.nstep: return {'status':'checkpoint','done':done,'nstep':self.nstep,'backend':self.backend}
        analysis=self.analyze(psi); result={'status':'completed','config':self.cfg,'backend':self.backend,'nstep':self.nstep,'dt_actual':self.dt_actual,'v_au':self.v,'initial':init,'analysis':analysis,'seconds_last_call':time.time()-tic,
          'claim':'P_bound is truncated at project_nmax; this is an independent paper-based implementation, not Nichols code reproduction'}
        atomic_json(out/'result.json',result); return result
