"""C21D same-IC photo-only, source-age-positive ENDPOINT-BE, frozen-end exponential, and midpoint-exposure exponential controls.

Research-only mathematical alternatives to native PreparedAbsorption; the compiled
owner is neither invoked nor claimed equivalent. Provenance: pinned C21C original
Verner, MD14 total rate, BB50k *manufactured 3-energy* photons, H(a), total nH.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from pathlib import Path
import sys
from typing import Literal
import numpy as np
from scipy.optimize import least_squares

BASE = Path(__file__).resolve().parents[1]
PARENT = BASE/'vendor'/'c21c'
if str(PARENT) not in sys.path: sys.path.insert(0,str(PARENT))
from radau_exposure_oracle import (
    BIND_EV, C_CM_S, FIT, N_H0, Y_HE, H, Cohort, binding, cross,
    initial_atoms, make_cohorts, run_reference, thermal_ev,
)

X4=(-.8611363115940526,-.3399810435848563,.3399810435848563,.8611363115940526)
W4=(.34785484513745385,.6521451548625461,.6521451548625461,.34785484513745385)
ABS_ID=(0,2,3)
MAX_HARD_STEPS=4096

@dataclass
class State:
    x:float
    photons:np.ndarray
    atoms:np.ndarray
    thermal:float
    photoevents:np.ndarray
    photoheat:np.ndarray
    photon_work:float=0.
    gas_work:float=0.
    source_n:float=0.
    source_u:float=0.
    max_solver_residual:float=0.
    max_solver_calls:int=0

    def copy(self):
        return State(self.x,self.photons.copy(),self.atoms.copy(),self.thermal,
                     self.photoevents.copy(),self.photoheat.copy(),
                     self.photon_work,self.gas_work,self.source_n,self.source_u,
                     self.max_solver_residual,self.max_solver_calls)


def proper_dt(x0:float,x1:float)->float:
    if not (math.isfinite(x0) and math.isfinite(x1) and x1>=x0):
        raise ValueError('invalid proper time interval')
    h=.5*(x1-x0)
    m=.5*(x0+x1)
    return h*math.fsum(w/H(m+h*z) for z,w in zip(X4,W4))


def one_absorber_endpoint(photon:float, absorber:float, kdt:float,
                          mode:Literal['BE','EXP'])->tuple[float,float]:
    """Unique nonnegative scalar endpoint root via monotone bracketing.

    Returns end survivor and photon loss; no epsilon absorber clipping.
    """
    from scipy.optimize import brentq
    if not all(math.isfinite(z) and z>=0 for z in (photon,absorber,kdt)):
        raise ValueError('scalar inputs')
    if mode not in ('BE','EXP'):raise ValueError('unknown mode')
    if absorber==0 or photon==0 or kdt==0:return absorber,0.
    def loss_at(a):
        return photon*(kdt*a/(1+kdt*a) if mode=='BE' else -math.expm1(-kdt*a))
    f=lambda a:absorber-a-loss_at(a)
    a=brentq(f,0.,absorber,xtol=5e-324,rtol=9e-16,maxiter=160)
    return a,loss_at(a)


def evaluate_frozen_endpoint(photons:np.ndarray, atom0:np.ndarray,
                             k:np.ndarray, dt:float,
                             mode:Literal['BE','EXP','MIDEXP']):
    """Coupled nonlinear endpoint absorber root and exact per-event gas mapping.

    5 atom states: HI,HII,HeI,HeII,HeIII. k[r,j] in per-total-H photon
    hazard coefficient (s^-1) per unit absorber_j. The total photon absorption
    for a photo channel is allocated as competing risks, not two photons.
    """
    if mode not in ('BE','EXP','MIDEXP') or dt<=0 or not math.isfinite(dt):raise ValueError('mode/dt')
    photons=np.asarray(photons,dtype=float);atom0=np.asarray(atom0,dtype=float)
    k=np.asarray(k,dtype=float)
    if photons.ndim!=1 or atom0.shape!=(5,) or k.shape!=(len(photons),3):raise ValueError('shape')
    if not (np.all(np.isfinite(photons)) and np.all(photons>=0) and np.all(np.isfinite(atom0)) and np.all(atom0>=0) and np.all(np.isfinite(k)) and np.all(k>=0)):
        raise ValueError('invalid physical input')
    if atom0[0]+atom0[1]<=0 or atom0[2]+atom0[3]+atom0[4]<=0:
        raise ValueError('invalid original nuclei')
    if max(photons,default=0)==0 or np.max(k,initial=0)==0:
        return photons.copy(),atom0.copy(),np.zeros((len(photons),3)),0.,0
    aH,aHeI,aHeII=atom0[0],atom0[2],atom0[3]
    p_total=max(float(np.sum(photons)),1e-25)
    def candidate(u):
        h=aH*u[0]
        i=aHeI*u[1]
        j=(aHeII+i)*u[2]
        a=np.array([aH-h,aHeI-i,aHeII+i-j])
        ev=np.array([h,i,j])
        tau=dt*(k@a)
        if mode=='BE':
            np1=photons/(1+tau)
            species=dt*(np1[:,None]*k)*a[None,:]
        else:
            # MIDEXP uses a *physical time* midpoint absorber exposure
            # approximation, not the Strang pseudo-time subreaction exposure.
            aa=.5*(atom0[[0,2,3]]+a) if mode=='MIDEXP' else a
            tau=dt*(k@aa)
            loss=photons*(-np.expm1(-tau))
            weights=np.divide(k*aa[None,:], (k@aa)[:,None],
                              out=np.zeros_like(k),where=(k@aa)[:,None]>0)
            species=loss[:,None]*weights
            np1=photons-loss
        return ev, a, np1, species
    active=np.any((k>0)&(photons[:,None]>0),axis=0)
    if not active.any():
        return photons.copy(),atom0.copy(),np.zeros((len(photons),3)),0.,0
    def unfold(y):
        u=np.zeros(3)
        u[active]=y
        return u
    def residual(y):
        e,_,_,species=candidate(unfold(y))
        return (e-np.sum(species,axis=0))[active]/p_total
    # Do not optimize channels whose original photon/hazard support is exactly
    # zero. Their numerical near-zero bound derivative would falsely trigger
    # a gradient-only convergence declaration and fabricate photoevents.
    y0=np.full(int(np.sum(active)),.02)
    out=least_squares(residual,y0,bounds=(np.zeros(len(y0)),np.ones(len(y0))),
                      ftol=2e-14,xtol=2e-14,gtol=1e-14,max_nfev=160)
    e,a,phot1,species=candidate(unfold(out.x))
    raw_res=float(np.max(np.abs(e-np.sum(species,axis=0))))
    if not out.success or raw_res>2e-11*max(1.,p_total):
        raise RuntimeError('C21D_COUPLED_NONLINEAR_HOLD '+str(raw_res))
    # The photon absorption event counts, not the fitted optimizer unknowns,
    # own all gas updates and binding/thermal accounting.
    L=np.sum(species,axis=0)
    h,i,j=L
    atom1=atom0+np.array([-h,h,-i,i-j,j])
    if not (np.all(np.isfinite(atom1)) and np.all(atom1>=-1e-14)):
        raise RuntimeError('C21D_INFEASIBLE_GAS')
    if abs(sum(photons)-sum(phot1)-sum(L))>1e-12*max(1,sum(photons)):
        raise RuntimeError('C21D_PHOTON_LEDGER_HOLD')
    if abs(atom1[0]+atom1[1]-atom0[0]-atom0[1])>1e-13 or abs(np.sum(atom1[2:])-np.sum(atom0[2:]))>1e-13:
        raise RuntimeError('C21D_NUCLEI_LEDGER_HOLD')
    return phot1,atom1,species,raw_res,out.nfev


def _state_validation(s:State):
    if np.any(s.photons<-1e-14) or np.any(s.atoms<-1e-14) or s.thermal<0:
        raise RuntimeError('C21D_STATE_NEGATIVE')
    if abs(s.atoms[0]+s.atoms[1]-1.)>3e-13 or abs(np.sum(s.atoms[2:])-Y_HE)>3e-13:
        raise RuntimeError('C21D_NUCLEI')
    if not all(math.isfinite(float(v)) for v in list(s.photons)+list(s.atoms)+[s.thermal,s.photon_work,s.gas_work]):
        raise RuntimeError('C21D_NONFINITE')


def _geom(s:State,xto:float,cohorts:tuple[Cohort,...]):
    """External FLRW work map. No photon-injection or chemistry inside geometry."""
    old_x=s.x
    if xto<old_x:raise ValueError('time reverse')
    delta=xto-old_x
    oldE=np.array([c.q20*math.exp(-old_x) for c in cohorts])
    newE=np.array([c.q20*math.exp(-xto) for c in cohorts])
    s.photon_work+=float(np.dot(s.photons,oldE-newE))
    oldth=s.thermal
    s.thermal*=math.exp(-2*delta)
    s.gas_work+=oldth-s.thermal
    s.x=xto


def _stage(s:State,end_x:float,cohorts:tuple[Cohort,...],opacity_scale:float,mode):
    if end_x<=s.x:return
    xstart=s.x;xm=.5*(xstart+end_x)
    dt=proper_dt(xstart,end_x)
    _geom(s,xm,cohorts)
    nh=N_H0*math.exp(-3*xm)
    energies=np.array([c.q20*math.exp(-xm) for c in cohorts])
    k=np.array([[opacity_scale*C_CM_S*nh*cross(j,float(E)) for j in range(3)] for E in energies])
    n1,a1,species,residual,calls=evaluate_frozen_endpoint(s.photons,s.atoms,k,dt,mode)
    heat=float(np.sum(species*(energies[:,None]-np.array(BIND_EV)[None,:])))
    if heat < -1e-13:raise RuntimeError('C21D_NEGATIVE_HEAT')
    s.photons=n1;s.atoms=a1;s.thermal+=heat
    s.photoevents+=np.sum(species,axis=0)
    s.photoheat+=np.sum(species*(energies[:,None]-np.array(BIND_EV)[None,:]),axis=0)
    s.max_solver_residual=max(s.max_solver_residual,residual)
    s.max_solver_calls=max(s.max_solver_calls,calls)
    _geom(s,end_x,cohorts)
    _state_validation(s)


def run_common_ic(mode:Literal['BE','EXP','MIDEXP'],steps_per_birth:int,
                  x0=math.log(1/12),dx=.025,opacity_scale=.001):
    """Same IC, source impulses, q, true cutoff and FLRW background as C21C Radau."""
    if steps_per_birth<1 or steps_per_birth>MAX_HARD_STEPS or not (0<dx<.1) or opacity_scale<0:
        raise ValueError('bounded run domain')
    cohorts,nold=make_cohorts(x0,dx)
    ps=np.zeros(len(cohorts))
    for i,c in enumerate(cohorts[:nold]):ps[i]=c.start_n
    atom=initial_atoms()
    s=State(x0,ps,atom,thermal_ev(atom,T=8500),np.zeros(3),np.zeros(3))
    initial_th=s.thermal
    initial_bind=binding(atom)
    old_n=sum(ps)
    old_u=sum(c.start_n*c.q20*math.exp(-x0) for c in cohorts[:nold])
    birth_x=sorted(set(c.birth_x for c in cohorts[nold:]))
    epochs=[x0]+birth_x+[x0+dx]
    for l,r in zip(epochs[:-1],epochs[1:]):
        for j in range(steps_per_birth):
            lo=l+(r-l)*j/steps_per_birth
            hi=l+(r-l)*(j+1)/steps_per_birth
            # Independent event alignment with actual moving Verner fit threshold.
            cuts=[lo,hi]
            for i,c in enumerate(cohorts):
                if s.photons[i]<=0:continue
                for eth in FIT:
                    xc=math.log(c.q20/eth)
                    if lo<xc<hi:cuts.append(xc)
            cuts=sorted(set(cuts))
            for ca,cb in zip(cuts[:-1],cuts[1:]):
                if abs(s.x-ca)>3e-14:raise AssertionError('split clock mismatch')
                _stage(s,cb,cohorts,opacity_scale,mode)
        for i,c in enumerate(cohorts[nold:],start=nold):
            if c.birth_x==r:
                s.photons[i]+=c.start_n
                s.source_n+=c.start_n
                s.source_u+=c.start_n*c.q20*math.exp(-r)
        _state_validation(s)
    nfinal=float(np.sum(s.photons))
    ufinal=float(sum(c.q20*math.exp(-s.x)*s.photons[i] for i,c in enumerate(cohorts)))
    number_res=old_n+s.source_n-nfinal-sum(s.photoevents)
    energy_res=old_u+s.source_u-ufinal-(s.thermal-initial_th)-(
        binding(s.atoms)-initial_bind)-s.photon_work-s.gas_work
    return dict(mode=mode,n=steps_per_birth,dx=dx,opacity_scale=opacity_scale,
                photons=s.photons.tolist(),gas=s.atoms.tolist(),thermal_ev_H=s.thermal,
                events=s.photoevents.tolist(),heat_ev_H=s.photoheat.tolist(),
                source_n=s.source_n,source_u=s.source_u,work_gamma=s.photon_work,
                work_gas=s.gas_work,number_res=number_res,energy_res=energy_res,
                max_root_residual=s.max_solver_residual,max_root_calls=s.max_solver_calls,
                xfinal=s.x,cohort_names=[c.name for c in cohorts],
                scientific_scope='manufactured GL2 3-energy MD14+Verner photo-only; no native H/He microphysical RHS')


def compare_grid(ns=(2,4,8,16,32,64),dx=.025,opacity_scale=.001):
    ref=run_reference(x0=math.log(1/12),dx=dx,opacity_scale=opacity_scale)
    j=len(ref.cohorts)
    truth=np.r_[ref.yfinal[:j],ref.yfinal[j:j+5],ref.yfinal[j+5]]
    data=[]
    for mode in ['BE','EXP','MIDEXP']:
        cases=[]
        for n in ns:
            v=run_common_ic(mode,n,dx=dx,opacity_scale=opacity_scale)
            state=np.r_[v['photons'],v['gas'],v['thermal_ev_H']]
            v['state_max_abs_error_vs_radau']=float(np.max(np.abs(state-truth)))
            cases.append(v)
        for a,b in zip(cases,cases[1:]):
            a['next_error_order']=math.log(a['state_max_abs_error_vs_radau']/b['state_max_abs_error_vs_radau'],2)
        data.append(dict(mode=mode,cases=cases))
    return dict(schema='C21D_SAME_IC_RAD_AU_BE_END_EXP_MID_EXP_V2',
                ref=dict(source_n=ref.source_n,source_u=ref.source_u,events=ref.endpoint_rates.events_H,
                         exposure=ref.exposures,endpoint_rate=ref.endpoint_rates.gamma_endpoint_s,
                         exposure_rate=ref.endpoint_rates.gamma_exposure_s,
                         photon_mass_res=ref.mass_res,energy_res=ref.energy_res,
                         state=truth.tolist()),
                controls=dict(dx=dx,opacity_scale=opacity_scale,cohorts=j,
                              initial_photo_species=['HI','HeI','HeII'],
                              source='MD14 time-rate, manufactured 3-positive-energy nodes and GL2 age impulses'),
                mathematical_photo_lanes=data,
                claims=['No literal native PreparedAbsorption data','No Case-A/CMB/CI/RR/DR',
                        'No native C21 production certification'])

if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--n',nargs='+',type=int,default=[2,4,8,16,32,64]);a=p.parse_args()
    r=compare_grid(a.n)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+'\n')
    for lane in r['mathematical_photo_lanes']:
        print(lane['mode'],[(x['n'],round(x['state_max_abs_error_vs_radau'],12)) for x in lane['cases']])
