"""Opt-in controlled diagnostics. Historical R3M10 runners/results are unchanged.

Atomic units in computational routines. No all-bound, continuum-only, covariance,
physical-rate, or b-grid admission is implied by a successful run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import time
import numpy as np
from scipy.linalg import solve_triangular
from .backend import asnumpy
from .hydrogen import orbital, bound_quantum_numbers
from .tdl import TDLRunner
from .util import atomic_json, config_hash

METHOD = 'R3M11_FIXED_CAP_SYMMETRIC_GRAM_V1'


def positive(value, name):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(name + ' must be finite and positive')
    return value


def scale_mask(mask, dt, reference_dt, xp=np):
    """M(dt)=M_ref**(dt/reference_dt); damping amplitude, not probability."""
    ratio = positive(dt, 'dt') / positive(reference_dt, 'reference_dt')
    if bool(asnumpy(xp.any(~xp.isfinite(mask) | (mask <= 0) | (mask > 1)))):
        raise ValueError('mask must satisfy 0 < M <= 1')
    return xp.exp(xp.log(mask) * ratio)


def projector_diagnostics(G, c, GR, cR, norm_region):
    """Selected finite-grid subspace, with the actual quadrature metric.

    c=B^dagger W psi; G=B^dagger W B. The complement is NOT pure continuum.
    All matrices and overlaps must use the same state, grid and quadrature.
    """
    G, GR = np.asarray(G, complex), np.asarray(GR, complex)
    c, cR = np.asarray(c, complex), np.asarray(cR, complex)
    if c.ndim != 1 or c.size == 0 or G.shape != (c.size, c.size) or GR.shape != G.shape or cR.shape != c.shape:
        raise ValueError('invalid Gram/overlap shapes')
    if any(not np.isfinite(v).all() for v in (G, GR, c, cR)) or not math.isfinite(float(norm_region)):
        raise ValueError('nonfinite projector input')
    if not np.allclose(G, G.conj().T, rtol=1e-12, atol=1e-13) or not np.allclose(GR, GR.conj().T, rtol=1e-12, atol=1e-13):
        raise ValueError('Gram matrices must be Hermitian')
    ev = np.linalg.eigvalsh(G)
    if ev[0] <= 1e-12 * max(ev[-1], 1e-300):
        raise ValueError('Gram matrix rank/conditioning failure; no silent pseudoinverse')
    alpha = np.linalg.solve(G, c)
    p = float(np.vdot(c, alpha).real)
    in_bound = float(np.vdot(alpha, GR @ alpha).real)
    cross = float(np.vdot(alpha, cR).real)
    eb, er = p - in_bound, float(norm_region) + in_bound - 2*cross
    tol = 1e-11 * max(1., p, abs(float(norm_region)))
    if min(p, in_bound, eb, er, float(norm_region)) < -tol:
        raise ValueError('inconsistent regional projector moments')
    # Only cancel roundoff-size negative values; preserve the raw moments too.
    bound = max(eb, 0.) + max(er, 0.) + 2*math.sqrt(max(in_bound, 0.)*max(er, 0.))
    return dict(P_selected_bound_gram=p, P_region=float(norm_region),
                overlap_sum_legacy=float(np.vdot(c,c).real),
                eps_bound_outside_raw=eb, eps_selected_complement_inside_raw=er,
                gap=float(norm_region)-p, gap_bound=bound,
                gap_bound_valid=bool(abs(float(norm_region)-p) <= bound+tol),
                gram_min_eigenvalue=float(ev[0]), gram_condition=float(ev[-1]/ev[0]),
                gram_identity_defect=float(np.linalg.norm(G-np.eye(c.size),2)),
                complement_is_pure_continuum=False,
                claim='finite_grid_selected_subspace_only; complement includes omitted bound, target bound and continuum')


class ControlledTDL(TDLRunner):
    """Same Coulomb grid/Hamiltonian, fixed absorber and symmetric damping."""
    def __init__(self, cfg):
        cfg = dict(cfg)
        for key in ('energy_keV_per_u', 'dt'):
            positive(cfg[key], key)
        positive(cfg['absorber_reference_dt'], 'absorber_reference_dt')
        positive(cfg['grid']['dx'], 'dx')
        if not math.isfinite(float(cfg['b'])) or float(cfg['b']) < 0:
            raise ValueError('b must be finite and nonnegative')
        if float(cfg.get('z_stop',60)) <= float(cfg.get('z_start',-30)):
            raise ValueError('z_stop must exceed z_start')
        if int(cfg.get('checkpoint_stride',100)) < 1:
            raise ValueError('checkpoint_stride must be positive')
        if int(cfg.get('project_nmax',3)) < 1:
            raise ValueError('project_nmax must be positive')
        cfg['method_id'] = METHOD
        super().__init__(cfg)
        if min(self.spec.shape()) < 2 or not np.isfinite(asnumpy(self.Vtarget)).all():
            raise ValueError('invalid grid or target Coulomb singularity on node')
        # y=0 projectile path must not lie on a grid line with x=b.
        if np.min(abs(asnumpy(self.y))) < 1e-12 and np.min(abs(asnumpy(self.x)-self.b)) < 1e-12:
            raise ValueError('projectile Coulomb singularity can cross a grid node')
        self.half_mask = scale_mask(self.mask, self.dt_actual/2, cfg['absorber_reference_dt'], self.xp)

    def step(self, psi, t_mid):
        ph = self.xp.exp(-0.5j*self.dt_actual*self.Vmid(t_mid))
        psi = self.half_mask*ph*psi
        psi = self.xp.fft.ifftn(self.kin*self.xp.fft.fftn(psi))
        return self.half_mask*ph*psi

    def initial_metrics(self, psi):
        hp = self.xp.fft.ifftn(.5*self.k2*self.xp.fft.fftn(psi)) + self.Vtarget*psi
        norm = self.norm(psi)
        en = float(asnumpy(self.xp.sum(self.xp.conj(psi)*hp).real*self.dv))/norm
        residual = math.sqrt(self.norm(hp-en*psi)/norm)
        return dict(energy_Eh=en, discrete_eigen_residual_Eh=residual,
                    exact_infinite_mass_1s_energy_error_Eh=en+.5,
                    claim='residual separates discrete stationarity from continuum spatial error; no physical error bound')

    def analyze_streaming(self, psi, block_size=65536):
        """O(N*k^2), memory O(block_size*k), no full N-by-k allocation."""
        if block_size < 1:
            raise ValueError('block_size must be positive')
        flat = np.asarray(asnumpy(psi)).ravel()
        xs, ys, zs = map(asnumpy, (self.x,self.y,self.z))
        nx,ny,nz = self.spec.shape()
        qns = bound_quantum_numbers(int(self.cfg.get('project_nmax',3)))
        k = len(qns); G=np.zeros((k,k),complex); GR=G.copy()
        c=np.zeros(k,complex); cR=c.copy(); nr=0.
        plane=float(self.cfg.get('capture_plane',30.))
        for start in range(0,flat.size,block_size):
            ix=np.arange(start,min(start+block_size,flat.size))
            x=xs[ix//(ny*nz)]-self.b; y=ys[(ix//nz)%ny]; z=zs[ix%nz]
            spatial_z=z-self.v*self.tf
            # State-dependent energy phases are irrelevant to span probabilities.
            B=np.column_stack([orbital(n,l,m,x,y,spatial_z) for n,l,m in qns])
            B*=np.exp(1j*self.v*z)[:,None]
            f=flat[start:start+ix.size]; region=z>plane
            G+=self.dv*(B.conj().T@B); c+=self.dv*(B.conj().T@f)
            BR=B[region];fr=f[region]
            GR+=self.dv*(BR.conj().T@BR);cR+=self.dv*(BR.conj().T@fr)
            nr+=self.dv*float(np.vdot(fr,fr).real)
        result=projector_diagnostics(G,c,GR,cR,nr)
        result.update(selected_subspace=[list(q) for q in qns],
                      project_nmax=int(self.cfg.get('project_nmax',3)),
                      wavefunction_norm=self.norm(psi),
                      state_amplitudes={str(q):[float(a.real),float(a.imag)] for q,a in zip(qns,c)},
                      finite_grid_state_norms=np.diag(G).real.tolist(),
                      n1=projector_diagnostics(G[:1,:1],c[:1],GR[:1,:1],cR[:1],nr))
        return result


def runtime_identity(cfg):
    root=Path(__file__).resolve().parents[1]
    selected=sorted((root/'cr_repro').glob('*.py'))+sorted((root/'vendor_w1r').glob('*.py'))
    hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in selected}
    from importlib.metadata import version, PackageNotFoundError
    versions={}
    for name in ('numpy','scipy','mpmath','cupy','cupy-cuda12x','cupy-cuda13x'):
        try:versions[name]=version(name)
        except PackageNotFoundError:versions[name]=None
    return dict(method=METHOD, config_hash=config_hash(cfg), code_hashes=hashes,
                packages=versions, python=platform.python_version(), architecture=platform.machine())


def save_checkpoint(path, psi, metadata):
    tmp=Path(str(path)+'.tmp')
    with tmp.open('wb') as f:
        np.savez(f,psi=asnumpy(psi),metadata=np.array(json.dumps(metadata,sort_keys=True)))
        f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)


def run_tdl(cfg, outdir, max_steps=None, resume=False):
    out=Path(outdir)
    if out.exists() and not resume:
        raise FileExistsError('use a new directory or explicit --resume')
    runner=ControlledTDL(cfg);ident=runtime_identity(runner.cfg)
    ident['actual_backend']=runner.backend
    if runner.backend=='cupy':
        ident['cuda_runtime']=int(runner.xp.cuda.runtime.runtimeGetVersion())
        ident['cuda_driver']=int(runner.xp.cuda.runtime.driverGetVersion())
    out.mkdir(parents=True,exist_ok=True);cp=out/'checkpoint.npz';tic=time.monotonic()
    if resume:
        with np.load(cp,allow_pickle=False) as z:
            meta=json.loads(str(z['metadata']));psi=runner.xp.asarray(z['psi'])
        if meta['identity']!=ident or meta['nstep']!=runner.nstep:
            raise ValueError('checkpoint config/code/environment identity mismatch')
        done=int(meta['done']);initial=meta['initial']
        if psi.shape!=runner.spec.shape() or not 0<=done<=runner.nstep or not np.isfinite(asnumpy(psi)).all():
            raise ValueError('invalid checkpoint state')
    else:
        psi,initial=runner.relaxed_initial();initial.update(runner.initial_metrics(psi));done=0
        atomic_json(out/'identity.json',ident)
    limit=runner.nstep if max_steps is None else min(runner.nstep,done+int(positive(max_steps,'max_steps')))
    for j in range(done,limit):
        psi=runner.step(psi,runner.t0+(j+.5)*runner.dt_actual);done=j+1
        if done%int(cfg.get('checkpoint_stride',100))==0 or done==limit:
            save_checkpoint(cp,psi,dict(identity=ident,done=done,nstep=runner.nstep,initial=initial))
    result=dict(status='completed' if done==runner.nstep else 'checkpoint',done=done,
                nstep=runner.nstep,dt_actual=runner.dt_actual,initial=initial,
                config=runner.cfg,backend=runner.backend,identity=ident,
                seconds_last_call=time.monotonic()-tic,
                bgrid_admitted=False,physical_rate_evaluated=False)
    if done==runner.nstep:
        result['analysis']=runner.analyze_streaming(psi,int(cfg.get('projection_block_size',65536)))
    atomic_json(out/'result.json',result)
    return result


def audit_aocc_matrix(aocc,t):
    O,H,D=aocc.matrix(t);R=aocc.metric_factor(O)
    Ri=solve_triangular(R,np.eye(aocc.nb),lower=False)
    Ht=Ri.conj().T@H@Ri;G,_,_,defect=aocc.generator(t)
    expected=-1j*(Ht-Ht.conj().T)
    residual=np.linalg.norm(G+G.conj().T-expected)/max(np.linalg.norm(G),1e-300)
    return dict(time_au=float(t),generator_identity_residual=float(residual),
                overlap_min_eigenvalue=float(np.linalg.eigvalsh((O+O.conj().T)/2)[0]),
                H_hermitian_relative_defect=float(np.linalg.norm(H-H.conj().T)/max(np.linalg.norm(H),1e-300)),
                whitened_H_hermitian_defect=float(np.linalg.norm(Ht-Ht.conj().T)),
                generator_antihermitian_relative_defect=defect,
                claim='matrix diagnostic only; not_a_covariance; unitary postprocessing does not certify raw H')



def controlled_boys(n, z):
    """Complex Boys: erf base plus upward recurrence for large |z|.

    Extends the legacy large-argument branch into Re(z)<=0. The observed
    complex hyp1f1 conjugacy defect is avoided, without symmetrizing H.
    Validated here for the n=0,1,2 s+p nuclear integrals at 100 keV/u.
    Nonfinite/overflow remains fail-closed, not silently rescaled.
    """
    from scipy.special import erf, hyp1f1
    if not isinstance(n, int) or n < 0:
        raise ValueError('nonnegative integer Boys order required')
    zz=np.asarray(z,complex);flat=zz.ravel();out=np.empty_like(flat)
    if not np.isfinite(flat).all():
        raise ValueError('finite Boys argument required')
    large=np.abs(flat)>max(20.,2*n+4.)
    q=flat[large];sq=np.sqrt(q)
    f=.5*np.sqrt(np.pi)*erf(sq)/sq
    for j in range(n):
        f=((2*j+1)*f-np.exp(-q))/(2*q)
    out[large]=f
    out[~large]=hyp1f1(n+.5,n+1.5,-flat[~large])/(2*n+1)
    if not np.isfinite(out).all():
        raise FloatingPointError('Boys range overflow; scaled implementation required')
    out=out.reshape(zz.shape)
    return out.item() if out.ndim==0 else out


def isolated_kernel():
    """Load unmodified vendor bytes in a separate namespace; no global patch."""
    import importlib.util, sys
    name='cr_repro._r3m11_private_gto'
    if name not in sys.modules:
        path=Path(__file__).resolve().parents[1]/'vendor_w1r/gaussian_cartesian.py'
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module
        spec.loader.exec_module(module)
        module.boys=controlled_boys
    return sys.modules[name]


from .aocc import OneElectronAOCC


class ControlledAOCC(OneElectronAOCC):
    """Same s+p AOCC problem with an independently evaluated Boys branch."""
    def __init__(self,cfg):
        self.kernel=isolated_kernel()
        super().__init__(cfg)

    def matrix(self,t):
        k=self.kernel;blocks=[]
        for label in ('T','P'):
            for g in self.groups:
                selected=[(i,a-g['sl'].start) for i,(L,a) in enumerate(self.basis)
                          if L==label and g['sl'].start<=a<g['sl'].stop]
                if not selected:continue
                rows,cols=map(list,zip(*selected))
                sh=k.Shell(g['exps'],g['pow'],self.center(label,t),self.kvec(label))
                blocks.append((label,rows,g['C'][:,cols],sh,self.phase(label,t)))
        O=np.zeros((self.nb,self.nb),complex);H=np.zeros_like(O);D=np.zeros_like(O)
        projectile=self.center('P',t)
        for L,rows,ca,sha,pha in blocks:
            for R,cols,cb,shb,phb in blocks:
                ph=np.conj(pha)*phb
                S0=ca.T@k.overlap(sha,shb)@cb
                H0=ca.T@(k.kinetic(sha,shb)+k.nuclear(sha,shb,[0,0,0])+k.nuclear(sha,shb,projectile))@cb
                D0=ca.T@k.moving_ket_overlap(sha,shb,self.velocity(R))@cb
                if R=='P':D0+=(-.5j*self.v*self.v)*S0
                ix=np.ix_(rows,cols);O[ix]=ph*S0;H[ix]=ph*H0;D[ix]=ph*D0
        return O,H,D


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['tdl','initial','aocc-audit','aocc'])
    p.add_argument('--config',required=True);p.add_argument('--out',required=True)
    p.add_argument('--max-steps',type=int);p.add_argument('--resume',action='store_true')
    args=p.parse_args();cfg=json.loads(Path(args.config).read_text())
    if args.action=='tdl':
        result=run_tdl(cfg,args.out,args.max_steps,args.resume)
    else:
        out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
        if args.action=='initial':
            r=ControlledTDL(cfg);psi,prep=r.relaxed_initial()
            result=dict(config=r.cfg,preparation=prep,metrics=r.initial_metrics(psi),identity=runtime_identity(r.cfg))
        else:
            a=ControlledAOCC(cfg)
            if args.action=='aocc':
                result=a.run()
                result.update(config=cfg,identity=runtime_identity(cfg),method='R3M11_CONTROLLED_BOYS_SP',bgrid_admitted=False,physical_rate_evaluated=False)
            else:
                times=cfg.get('audit_times_au',[a.t0,0.,a.tf])
                result=dict(config=cfg,nbasis=a.nb,
                            matrix_audit=[audit_aocc_matrix(a,float(t)) for t in times],
                            negative_atomic_energies=a.eps[a.eps<0].tolist(),identity=runtime_identity(cfg))
        atomic_json(out/'result.json',result)
    print(json.dumps({k:result[k] for k in ('status','done','nstep','metrics','nbasis') if k in result},indent=2))

if __name__=='__main__':
    main()
