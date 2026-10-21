"""Exact owner reuse and explicit full-tensor observables for a REI control pilot.

No HH rate, chemistry, electron replay, UV source or collision closure is enabled.
The owner RHS/integrator and quadratures remain byte-identical in donor/.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
DONOR=HERE/'donor'
OWNER=DONOR/'research/rei_bass_hierarchy_backreaction_20261015'
KAPPA_TIME=8*math.pi*6.67430e-11/299792458.0**2
SIGMA_GRID=(0.,.0005,.001,.002,.004)
PI_GRID=(0.,.00025,.0005,.001)


def verify_donor() -> dict:
    lock=json.loads((HERE/'DONOR_LOCK.json').read_text())
    for name,expected in lock['files'].items():
        p=DONOR/name
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise ValueError('DONOR_IDENTITY_MISMATCH: '+name)
    return lock


def norms(H:float,s:float,pi_s_components,*,kappa_time:float=KAPPA_TIME)->dict:
    """All pressures are SI energy density, each entry is DeltaP/3, not DeltaP.

    Contract tensors are diagonal in one common normal orthonormal frame.
    Sum signed stress components BEFORE taking a tensor norm.
    """
    parts=[float(p) for p in pi_s_components]
    if not parts or not all(math.isfinite(z) for z in [H,s,kappa_time,*parts]):
        raise ValueError('finite H,s,kappa and nonempty stress components required')
    if H<=0 or kappa_time<=0:raise ValueError('positive proper-time H and kappa required')
    p=math.fsum(parts)
    S=math.sqrt(6)*s/H
    P=kappa_time*math.sqrt(6)*p/H**2
    return dict(Sigma_F=abs(S),Pi_F=abs(P),Sigma_signed=S,Pi_signed=P,
                Sigma_half=math.sqrt(3)*abs(s)/H,pi_s_total_J_m3=p,
                work=6*kappa_time*s*p/H**3,
                alignment=None if s==0 or p==0 else math.copysign(1,s*p),
                shear_energy_fraction=S*S/6)


def make_grid():
    """63 distinct signed initial states; zero-sign duplicates are removed."""
    ss=sorted(set([*SIGMA_GRID,*[-s for s in SIGMA_GRID]]))
    pp=sorted(set([*PI_GRID,*[-p for p in PI_GRID]]))
    return [(s,p) for s in ss for p in pp]


class PreparedFactory:
    """One immutable owner preparation per worker; fresh evolving state per case.

    Shallow copies may share only checked read-only operators, fixed SourceLock
    and the canonical momentum packet whose arrays are already read-only.
    No global monkeypatch and no change to owner class methods.
    """
    def __init__(self):
        self.lock=verify_donor()
        for p in (OWNER,OWNER/'canonical_fv_20261015'):
            sys.path.insert(0,str(p))
        import canonical_fv
        from run_hierarchy import source_lock
        if Path(canonical_fv.__file__).resolve()!=OWNER/'canonical_fv_20261015/canonical_fv.py':
            raise RuntimeError('conflicting pre-imported owner module')
        self.cls=canonical_fv.CanonicalFVSpecies
        self.source=source_lock()
        self.fixed=dict(mass_fraction=.1,massive_A=0.,mass_over_Tref=30.,
                        radial_cells=24,angular_cells=12,subcell_gauss_order=3)
        self.template=self.fresh(0.,0,0.,0.)
        for value in vars(self.template).values():
            if isinstance(value,np.ndarray):value.flags.writeable=False
        self.preparations=1
        self.clones=0

    def fresh(self,Sigma_ref,orientation,kg,kn):
        return self.cls(self.source,2.7255,8,Sigma_ref=Sigma_ref,
            orientation=orientation,kappa_gamma=kg,kappa_nu=kn,
            ne_source=None,**self.fixed)

    def clone(self,Sigma_ref,orientation,kg,kn):
        if not all(math.isfinite(v) for v in (Sigma_ref,kg,kn)):
            raise ValueError('finite initial controls required')
        if not(0<=Sigma_ref<math.sqrt(3) and orientation in (-1,0,1)
               and (Sigma_ref==0)==(orientation==0) and abs(kg)<=.5 and abs(kn)<=.5):
            raise ValueError('original owner IC domain violated')
        obj=copy.copy(self.template)
        obj.Sigma_ref=Sigma_ref;obj.orientation=orientation
        obj.k_gamma=kg;obj.k_nu=kn;obj._nfev=0
        self.clones+=1
        return obj


def mapped_case(factory:PreparedFactory,SignedSigma:float,SignedPi:float):
    """Map requested norms/signs to admissible original radiation initial data.

    Both photon/neutrino occupation P2 coefficients share kappa_radiation.
    This is a declared 2D slice, not a unique inversion of all stress species.
    The fixed massive distribution is initially isotropic. Its tiny quadrature
    residual is included in the affine map; no value is silently zeroed.
    """
    S=float(SignedSigma);P=float(SignedPi)
    if not all(math.isfinite(x) for x in (S,P)) or abs(S)>=math.sqrt(6):
        raise ValueError('finite signed controls and |Sigma|<sqrt(6) required')
    half=abs(S)/math.sqrt(2);orient=0 if S==0 else int(math.copysign(1,S))
    probe=factory.clone(half,orient,0.,0.)
    d=probe.fields(0.,probe.initial_state())
    target_p=P*d['H']**2/(math.sqrt(6)*KAPPA_TIME)
    coeff=factory.source.rhocrit_j_m3*factory.source.omega_r/factory.source.aref**4/15
    k=(target_p-d['Pi_matter_J_m3'])/coeff
    obj=factory.clone(half,orient,k,k)  # owner bounds enforced, never clipped
    return obj,dict(Sigma0_signed=S,Pi0_signed=P,kappa_radiation=k,
                    orientation_s=orient,initial_H_per_s=d['H'],
                    initial_massive_pi_s_J_m3=d['Pi_matter_J_m3'])


_FACTORY=None

def run_case(request:dict)->dict:
    global _FACTORY
    if _FACTORY is None:_FACTORY=PreparedFactory()
    obj,initial=mapped_case(_FACTORY,request['Sigma0_signed'],request['Pi0_signed'])
    sol,diag,_=obj.integrate(n=request['points'],rtol=request['rtol'],atol=request['atol'])
    rows=[]
    max_number=0.;max_constraint=0.;min_cell=math.inf
    for x,d in zip(sol.t,diag):
        p=[d['Pi_gamma_J_m3'],d['Pi_nu_J_m3'],d['Pi_matter_J_m3']]
        v=norms(float(d['H']),float(d['s']),p)
        # Keep species pressures and signed raw quantities, not only norms.
        rows.append(dict(x=float(x),a=float(d['a']),zbar=1/float(d['a'])-1,
             H_per_s=float(d['H']),s_per_s=float(d['s']),b=float(d['b']),
             pi_s_gamma_J_m3=float(p[0]),pi_s_nu_J_m3=float(p[1]),
             pi_s_massive_J_m3=float(p[2]),E2_gamma=float(d['E_gamma'][2]),
             E2_nu=float(d['E_nu'][2]),**v))
        max_number=max(max_number,abs(float(d['N_gamma'][0])-1),abs(float(d['N_nu'][0])-1))
        max_constraint=max(max_constraint,abs(float(d['Einstein_H2'])/float(d['H'])**2-1))
        min_cell=min(min_cell,float(d['massive_min_cell_population']))
    mismatch=max(abs(rows[0]['Sigma_signed']-initial['Sigma0_signed']),
                 abs(rows[0]['Pi_signed']-initial['Pi0_signed']))
    if mismatch>1e-13 or max_number>5e-11 or min_cell<0 or max_constraint>2e-13:
        raise ArithmeticError('initial mapping/number/constraint/positive-cell check failed')
    return dict(schema='PHYS74_REI_COLLISIONLESS_CONTROL_V1',request=request,
        initial=initial,history=rows,diagnostics=dict(nfev=int(sol.nfev),
        initial_coordinate_abs_error=mismatch,max_number_error=max_number,
        max_algebraic_H_constraint_relative=max_constraint,min_cell_number=min_cell,
        owner_preparations_in_worker=_FACTORY.preparations,
        owner_clones_in_worker=_FACTORY.clones),
        scope='Original REI PR147 Einstein–gamma/nu + canonical massive collisionless control',
        HHe_feedback=False,ionizing_source=False,polarization=False,
        continuum_error_certified=False,HH_R10='OFF')
