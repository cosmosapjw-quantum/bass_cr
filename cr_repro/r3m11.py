"""Opt-in R3M11 controls; archived R3M10 runners and observations stay unchanged.

Atomic units are used internally. A finite sampled hydrogen span is not the
complete spectral bound subspace. Its orthogonal remainder is NOT continuum.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .backend import asnumpy
from .grid import GridSpec
from .hydrogen import orbital, bound_quantum_numbers
from .tdl import TDLRunner
from .util import atomic_json, config_hash


def positive(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be finite and positive')
    return value


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def source_digest() -> str:
    """Bind restart to the numerical source, not a guessed Git branch name."""
    root = Path(__file__).resolve().parent
    h = hashlib.sha256()
    for path in sorted(root.glob('*.py')):
        h.update(path.name.encode()); h.update(bytes.fromhex(file_sha(path)))
    return h.hexdigest()


def fixed_rate_mask(mask: Any, dt: float, reference_dt: float, xp=np):
    """M(dt)=M_ref**(dt/dt_ref); keep W=-log(M_ref)/dt_ref fixed.

    For H_eff=H-iW, probability damping is exp(-2 W t). Valid only for
    0<M_ref<=1. A zero mask would be an infinite CAP and is rejected.
    """
    dt=positive(dt,'dt'); reference_dt=positive(reference_dt,'reference_dt')
    mask=xp.asarray(mask)
    if bool(asnumpy(xp.any(~xp.isfinite(mask) | (mask <= 0) | (mask > 1)))):
        raise ValueError('mask must be finite with 0 < mask <= 1')
    return xp.exp(xp.log(mask)*(dt/reference_dt))


def gram_projection(gram, overlaps, norm: float, rcond: float=1e-10) -> dict:
    """Projection on a full-rank finite span; never silently drop a channel."""
    G=np.asarray(gram,dtype=complex); c=np.asarray(overlaps,dtype=complex)
    norm=positive(norm,'wavefunction norm'); rcond=positive(rcond,'rcond')
    if c.ndim!=1 or c.size==0 or G.shape!=(c.size,c.size):
        raise ValueError('invalid Gram/overlap shape')
    if not np.isfinite(G).all() or not np.isfinite(c).all():
        raise ValueError('nonfinite Gram/overlap')
    herm=float(np.linalg.norm(G-G.conj().T)/max(np.linalg.norm(G),1e-300))
    if herm>1e-12: raise ValueError('non-Hermitian Gram matrix')
    G=(G+G.conj().T)/2
    eig=np.linalg.eigvalsh(G)
    if eig[-1]<=0 or eig[0]<=rcond*eig[-1]:
        raise ValueError('Gram rank loss/ill conditioning; refine the representation')
    alpha=np.linalg.solve(G,c); p=float(np.vdot(c,alpha).real)
    if p < -5e-11*norm or p > norm*(1+5e-10):
        raise ValueError('projector probability outside wavefunction norm')
    return dict(probability=p,coefficients=alpha,condition_number=float(eig[-1]/eig[0]),
                eigenvalue_min=float(eig[0]),eigenvalue_max=float(eig[-1]),
                hermitian_relative_residual=herm)


def _state_slab(spec: GridSpec, b: float, v: float, t: float, qns, start: int, stop: int):
    x,y,z=spec.axes(np)
    X=x[start:stop,None,None]-b;Y=y[None,:,None];Z=z[None,None,:]-v*t
    phases=np.exp(1j*v*z[None,None,:]-.5j*v*v*t)
    cols=[(orbital(n,l,m,X,Y,Z)*phases*np.exp(.5j*t/n**2)).reshape(-1) for n,l,m in qns]
    return np.column_stack(cols)


def projector_audit(psi, spec: GridSpec, b: float, v: float, t: float, *,
                    nmax: int, capture_plane: float, slab_x: int=2) -> dict:
    """Three slab passes: Gram/overlaps, nested spans, and exact gap identity.

    Peak basis memory is O(slab_x * ny * nz * nmax**3), not the full
    wavefunction times all channels. `psi` may be an mmap from an old run.
    """
    if isinstance(nmax,bool) or int(nmax)!=nmax or not 1<=nmax<=8:
        raise ValueError('nmax must be an integer between 1 and 8')
    if isinstance(slab_x,bool) or int(slab_x)!=slab_x or slab_x<1:
        raise ValueError('slab_x must be positive integer')
    if not all(math.isfinite(float(z)) for z in [b,v,t,capture_plane]):
        raise ValueError('nonfinite geometry')
    if psi.shape!=spec.shape(): raise ValueError('state/grid shape mismatch')
    qns=bound_quantum_numbers(nmax);k=len(qns);G=np.zeros((k,k),complex);c=np.zeros(k,complex);norm=0.
    for i in range(0,spec.shape()[0],slab_x):
        j=min(i+slab_x,spec.shape()[0]);a=np.asarray(psi[i:j]).reshape(-1)
        if not np.isfinite(a).all():raise ValueError('nonfinite state')
        B=_state_slab(spec,b,v,t,qns,i,j)
        G+=B.conj().T@B*spec.dv;c+=B.conj().T@a*spec.dv
        norm+=float(np.vdot(a,a).real*spec.dv)
    projection=gram_projection(G,c,norm);alpha=projection['coefficients'];p=projection['probability']
    nested={}
    for n in range(1,nmax+1):
        ix=[i for i,q in enumerate(qns) if q[0]<=n]
        nested[str(n)]=gram_projection(G[np.ix_(ix,ix)],c[ix],norm)['probability']
    z=spec.axes(np)[2];inside_z=z>capture_plane
    preg=eb=ec=cross=orth=0.
    for i in range(0,spec.shape()[0],slab_x):
        j=min(i+slab_x,spec.shape()[0]);shape=(j-i,spec.shape()[1],spec.shape()[2])
        a=np.asarray(psi[i:j]).reshape(-1);B=_state_slab(spec,b,v,t,qns,i,j)
        bound=B@alpha;remainder=a-bound;inside=np.broadcast_to(inside_z,shape).reshape(-1)
        preg+=float(np.vdot(a[inside],a[inside]).real*spec.dv)
        eb+=float(np.vdot(bound[~inside],bound[~inside]).real*spec.dv)
        ec+=float(np.vdot(remainder[inside],remainder[inside]).real*spec.dv)
        cross+=float(2*np.vdot(bound[inside],remainder[inside]).real*spec.dv)
        orth+=abs(np.vdot(bound,remainder)*spec.dv)
    delta=preg-p;cap_inside=max(0.,p-eb);bound=eb+ec+2*math.sqrt(cap_inside*ec)
    return dict(schema='R3M11_FINITE_GRID_SPAN_AUDIT_V1',project_nmax=nmax,
                quantum_numbers=[list(q) for q in qns],wavefunction_norm=norm,
                raw_overlap_sum=float(np.vdot(c,c).real),P_span_nmax=p,
                P_span_by_nmax=nested,P_region=preg,region_minus_span=delta,
                eps_selected_outside=eb,eps_complement_inside=ec,cross_term=cross,
                gap_identity_residual=abs(delta-(-eb+ec+cross)),gap_bound=bound,
                slabwise_orthogonality_bound=orth,
                Gram_condition=projection['condition_number'],
                Gram_eigenvalues=[projection['eigenvalue_min'],projection['eigenvalue_max']],
                Gram_identity_spectral_norm=float(np.linalg.norm(G-np.eye(k),2)),
                finite_grid_state_norms=[float(a) for a in G.diagonal().real],
                continuum_probability=None,
                remainder_semantics='ORTHOGONAL_COMPLEMENT_OF_FINITE_SELECTED_SPAN_NOT_CONTINUUM',
                physical_all_bound_admitted=False,
                span_semantics='SAMPLED_ANALYTIC_HYDROGEN_CHANNELS_NOT_EXACT_SPECTRAL_PROJECTOR')


class ControlledTDLRunner(TDLRunner):
    """New opt-in fixed-CAP symmetric propagation; parent remains historical."""
    def __init__(self,cfg):
        cfg=dict(cfg)
        reference=positive(cfg['absorber_reference_dt'],'absorber_reference_dt')
        positive(cfg['dt'],'dt')
        if cfg.get('initial_state','imag_time') not in ['imag_time','analytic']:
            raise ValueError('unknown initial state')
        cfg['_r3m11_controls']='FIXED_CAP_SYMMETRIC_V1'
        cfg['_r3m11_source_digest']=source_digest()
        super().__init__(cfg)
        self.cap_half=fixed_rate_mask(self.mask,self.dt_actual/2,reference,self.xp)

    def step(self,psi,t_mid):
        # At fixed discretization: V-iW / 2, T, V-iW / 2.
        ph=self.xp.exp(-.5j*self.dt_actual*self.Vmid(t_mid))*self.cap_half
        psi=ph*psi
        psi=self.xp.fft.ifftn(self.kin*self.xp.fft.fftn(psi))
        return ph*psi

    def relaxed_initial(self):
        psi,info=super().relaxed_initial()
        hp=self.xp.fft.ifftn(.5*self.k2*self.xp.fft.fftn(psi))+self.Vtarget*psi
        E=float(info['energy_Eh'])
        residual=float(asnumpy(self.xp.sqrt(self.xp.sum(abs(hp-E*psi)**2)*self.dv)))
        info.update(stationary_residual_Eh=residual,energy_error_from_infinite_mass_1s_Eh=E+.5,
                    residual_semantics='DISCRETE_TARGET_HAMILTONIAN_RESIDUAL_NOT_CONTINUUM_ERROR_BOUND')
        return psi,info

    def analyze(self,psi):
        result=super().analyze(psi)
        # Historical rank-one diagnostics are not normalized projectors; retain
        # those values only under their old names, and give the authoritative
        # new finite-span decomposition a separately typed field.
        result['legacy_n1_diagnostics_authority']='HISTORICAL_ONLY_USE_GRAM_AUDIT'
        result['gram_audit']=projector_audit(asnumpy(psi),self.spec,self.b,self.v,self.tf,
            nmax=int(self.cfg.get('project_nmax',3)),capture_plane=float(self.cfg.get('capture_plane',30.)),
            slab_x=int(self.cfg.get('projection_slab_x',2)))
        result['production_admitted']=False
        return result

    def run(self,outdir,max_steps=None):
        out=Path(outdir);seal=out/'r3m11_checkpoint_seal.json'
        if max_steps is not None and (isinstance(max_steps,bool) or int(max_steps)!=max_steps or max_steps<=0):
            raise ValueError('max_steps must be a positive integer')
        if (out/'state.json').exists() or (out/'state.npy').exists():
            if not seal.is_file():raise ValueError('unsealed/legacy checkpoint: use a fresh output path')
            s=json.loads(seal.read_text())
            if s['source_digest']!=source_digest():raise ValueError('checkpoint source changed')
            for name in ['state.json','state.npy']:
                if not (out/name).is_file() or file_sha(out/name)!=s['files'][name]:
                    raise ValueError('checkpoint hash mismatch')
        result=super().run(out,max_steps=max_steps)
        atomic_json(seal,dict(schema='R3M11_CHECKPOINT_SEAL_V1',source_digest=source_digest(),
                    files={name:file_sha(out/name) for name in ['state.json','state.npy']}))
        return result


def audit_saved(run_dir, *, nmax: int=3, slab_x: int=2, expected_state_sha256: str|None=None) -> dict:
    """Read-only sidecar analysis of completed archived or new state bytes."""
    root=Path(run_dir);meta=json.loads((root/'state.json').read_text())
    if int(meta['done'])!=int(meta['nstep']):raise ValueError('incomplete checkpoint')
    result=json.loads((root/'result.json').read_text());cfg=result['config']
    if result.get('status')!='completed':raise ValueError('incomplete result')
    if meta['config_hash']!=config_hash(cfg):raise ValueError('state/result config mismatch')
    path=root/'state.npy';sha=file_sha(path)
    if expected_state_sha256 and sha!=expected_state_sha256:raise ValueError('state authority hash mismatch')
    p=np.load(path,mmap_mode='r',allow_pickle=False);spec=GridSpec.from_dict(cfg['grid'])
    from .observables import projectile_speed_au
    v=projectile_speed_au(cfg['energy_keV_per_u'])
    obs=projector_audit(p,spec,float(cfg['b']),v,float(cfg.get('z_stop',60))/v,
           nmax=nmax,capture_plane=float(cfg.get('capture_plane',30)),slab_x=slab_x)
    return dict(schema='R3M11_SAVED_STATE_POSTPROCESS_V1',source_state_sha256=sha,
                externally_expected_hash_checked=expected_state_sha256 is not None,
                input_result_sha256=file_sha(root/'result.json'),analysis=obs,
                dynamics_rerun=False,physical_rate_evaluated=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    r=sub.add_parser('run');r.add_argument('--config',required=True);r.add_argument('--out',required=True);r.add_argument('--max-steps',type=int)
    a=sub.add_parser('audit-saved');a.add_argument('--run',required=True);a.add_argument('--out',required=True);a.add_argument('--nmax',type=int,default=3);a.add_argument('--slab-x',type=int,default=2);a.add_argument('--state-sha256')
    args=p.parse_args()
    if args.cmd=='run':
        out=ControlledTDLRunner(json.loads(Path(args.config).read_text())).run(args.out,args.max_steps)
    else:
        target=Path(args.out)
        if target.exists():raise FileExistsError('refuse to overwrite analysis evidence')
        out=audit_saved(args.run,nmax=args.nmax,slab_x=args.slab_x,expected_state_sha256=args.state_sha256)
        atomic_json(target,out)
    print(json.dumps(out,indent=2,allow_nan=False))

if __name__=='__main__':main()
