"""C21E: integrated photo events coupled to a non-photo microphysics owner.

All amounts are per TOTAL hydrogen nucleus, times proper seconds and energies
in eV. This solver never constructs Gamma by dividing events by a depleted
endpoint absorber. Original native chemistry is supplied through a narrow
point-provider interface with exactly zero photo rates and zero Hubble term.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol
from pathlib import Path
import math
import sys
import numpy as np
from numpy.typing import NDArray

VENDOR=Path(__file__).resolve().parents[1]/'vendor/pr79'
if str(VENDOR) not in sys.path: sys.path.insert(0,str(VENDOR))
from radau_exposure_oracle import H, cross, FIT, C_CM_S, N_H0, Y_HE
from exposure_contract import BIND_EV, EV_ERG
KB_EV=1.380649e-16/EV_ERG
Array=NDArray[np.float64]

class DomainError(ValueError): pass
class StepRejected(RuntimeError): pass
class ProviderFailure(RuntimeError): pass


def state_valid(g: Array,Y: float)->bool:
    g=np.asarray(g,dtype=float)
    if g.shape!=(4,) or not np.isfinite(g).all() or not math.isfinite(Y) or Y<0: return False
    x,y,z,w=g
    return bool(0<=x<=1 and y>=0 and z>=0 and y+z<=1 and w>0 and (Y>0 or (y==0 and z==0)))


def require_state(g: Array,Y: float)->Array:
    g=np.asarray(g,dtype=float)
    if not state_valid(g,Y):raise DomainError('GAS_STATE_DOMAIN')
    return g


def alpha(g: Array,Y:float)->Array:
    x,y,z,_=g
    return np.array([1-x,Y*(1-y-z),Y*y])


def binding_weights(Y:float)->Array:
    return np.array([BIND_EV[0],Y*BIND_EV[1],Y*(BIND_EV[1]+BIND_EV[2])])


def temperature(g: Array,Y:float)->float:
    return float(g[3]/(1.5*KB_EV*(1+Y+g[0]+Y*(g[1]+2*g[2]))))


def gas_from_temperature(frac: Array,T:float,Y:float)->Array:
    x,y,z=map(float,frac)
    g=np.array([x,y,z,1.5*KB_EV*T*(1+Y+x+Y*(y+2*z))])
    return require_state(g,Y).copy()


def event_fractions(events: Array,Y:float)->Array:
    h,i,j=map(float,events)
    if Y==0:
        if i!=0 or j!=0:raise DomainError('HE_EVENTS_WITHOUT_HE')
        return np.array([h,0.,0.])
    return np.array([h,(i-j)/Y,j/Y])


@dataclass(frozen=True)
class MicroRates:
    fraction_s:Array
    thermal_ev_h_s:float
    binding_ev_h_s:float
    escaped_ev_h_s:float
    cmb_ev_h_s:float
    ci_h_s:Array=field(default_factory=lambda:np.zeros(3))
    rr_h_s:Array=field(default_factory=lambda:np.zeros(3))
    dr_h_s:float=0.

    def validate(self,Y:float)->None:
        f=np.asarray(self.fraction_s,dtype=float)
        ci=np.asarray(self.ci_h_s,dtype=float); rr=np.asarray(self.rr_h_s,dtype=float)
        scalars=np.array([self.thermal_ev_h_s,self.binding_ev_h_s,self.escaped_ev_h_s,self.cmb_ev_h_s,self.dr_h_s])
        if f.shape!=(3,) or ci.shape!=(3,) or rr.shape!=(3,) or not all(np.isfinite(a).all() for a in (f,ci,rr,scalars)):
            raise ProviderFailure('MICRO_NONFINITE_OR_SHAPE')
        if min(*ci,*rr,self.dr_h_s,self.escaped_ev_h_s)<0:raise ProviderFailure('MICRO_NEGATIVE_EVENT_OR_ESCAPE')
        net=ci-rr-np.array([0.,self.dr_h_s,0.])
        expected=event_fractions(net,Y)
        if not np.allclose(f,expected,rtol=2e-11,atol=1e-28):raise ProviderFailure('MICRO_STOICHIOMETRY')
        if not math.isclose(self.binding_ev_h_s,float(binding_weights(Y)@f),rel_tol=2e-11,abs_tol=1e-28):raise ProviderFailure('MICRO_BINDING_OWNER')
        terms=[self.thermal_ev_h_s,self.binding_ev_h_s,self.escaped_ev_h_s,-self.cmb_ev_h_s]
        if abs(math.fsum(terms))>1e-28+2e-11*math.fsum(abs(v) for v in terms):raise ProviderFailure('MICRO_ENERGY_OWNER')


class MicroProvider(Protocol):
    kind:str
    def __call__(self,a:float,g:Array,nh0:float,Y:float)->MicroRates: ...


class ZeroMicro:
    kind='PHOTO_ONLY_NO_MICRO'
    def __call__(self,a,g,nh0,Y):
        return MicroRates(np.zeros(3),0.,0.,0.,0.)


class ManufacturedMicro:
    """Conservative nonlinear CI/RR/DR/cooling fixture, NOT native Grackle.

    Rate constants are chosen for bounded numerical testing, not astrophysical
    fits. The same continuous provider is used in the independent Radau ODE.
    """
    kind='MANUFACTURED_CONSERVATIVE_MICRO_NOT_GRACKLE'
    def __call__(self,a,g,nh0,Y):
        require_state(g,Y)
        if not (math.isfinite(a) and a>0 and math.isfinite(nh0) and nh0>0):raise DomainError('EPOCH_DENSITY')
        T=temperature(g,Y)
        if not 1<T<1e6:raise DomainError('MANUFACTURED_TEMPERATURE_DOMAIN')
        neH=g[0]+Y*(g[1]+2*g[2])
        n=nh0/a**3
        speed=1e-12*n
        ions=np.array([g[0],Y*g[1],Y*g[2]])
        ci=speed*neH*np.array([.03,.012,.008])*alpha(g,Y)*(T/8500.)**.2
        rr=speed*neH*np.array([1.,.8,1.2])*ions*(8500./T)**.6
        dr=speed*neH*.13*ions[1]*(T/8500.)**.25
        net=ci-rr-np.array([0.,dr,0.])
        f=event_fractions(net,Y)
        capture=float(np.dot(rr,BIND_EV)+dr*BIND_EV[1])
        kinetic=.7*KB_EV*T*(float(rr.sum())+dr)+.05*speed*neH*g[3]
        equilibrium=1.5*KB_EV*100.*(1+Y+neH)
        cmb=.02*speed*neH*(equilibrium-g[3])
        return MicroRates(f,-float(ci@BIND_EV)-kinetic+cmb,float(binding_weights(Y)@f),capture+kinetic,cmb,ci,rr,dr)


@dataclass(frozen=True)
class Controls:
    photon_method:str='EXP'
    theta_photo:float=.5
    theta_micro:float=.5
    nonlinear_tol:float=2e-13
    energy_atol:float=1e-14
    energy_rtol:float=2e-12
    max_newton:int=24

    def validate(self):
        if self.photon_method not in ('EXP','BE') or self.theta_photo not in (.5,1.) or self.theta_micro not in (.5,1.):raise DomainError('METHOD_POLICY')
        if any(not math.isfinite(v) or v<=0 for v in (self.nonlinear_tol,self.energy_atol,self.energy_rtol)):raise DomainError('ACCEPTANCE_POLICY')
        if not 1<=self.max_newton<=80:raise DomainError('NEWTON_BUDGET')


MODES={
    'BE':Controls(photon_method='BE',theta_photo=1.,theta_micro=1.),
    'MIDPHOTO_ENDMICRO':Controls(theta_photo=.5,theta_micro=1.),
    'FULLMID':Controls(),
}


def photon_events(n0:Array,energy:Array,k:Array,absorber:Array,dt:float,method:str):
    rates=k*absorber[None,:]
    total=rates.sum(axis=1)
    tau=dt*total
    if not np.isfinite(tau).all():raise DomainError('OPTICAL_DEPTH_OVERFLOW')
    if method=='EXP':
        lost=n0*(-np.expm1(-tau))
        n1=n0*np.exp(-tau)
    else:
        n1=n0/(1.+tau)
        lost=n1*tau
    events=np.divide(rates,total[:,None],out=np.zeros_like(rates),where=total[:,None]>0)*lost[:,None]
    heat=float(np.sum(events*(energy[:,None]-np.asarray(BIND_EV)[None,:])))
    return n1,events,heat


@dataclass
class Step:
    gas:Array
    photons:Array
    events:Array
    heat_ev_h:float
    micro:MicroRates
    residual:Array
    energy_defect:float
    number_defect:float
    nfev:int
    iterations:int


def reaction_step(g0,n0,energy,k,dt,a,nh0,Y,provider:MicroProvider,controls:Controls|None=None)->Step:
    """Pure transaction: input arrays unchanged on success or rejection."""
    c=controls or Controls();c.validate()
    g0=require_state(g0,Y).copy();n0=np.asarray(n0,float).copy();energy=np.asarray(energy,float);k=np.asarray(k,float)
    if n0.ndim!=1 or energy.shape!=n0.shape or k.shape!=(len(n0),3):raise DomainError('PHOTON_SHAPE')
    if not all(np.isfinite(v).all() for v in (n0,energy,k)) or (n0<0).any() or (energy<=0).any() or (k<0).any():raise DomainError('PHOTON_DOMAIN')
    if not all(math.isfinite(v) and v>0 for v in (dt,a,nh0)):raise DomainError('TIME_DENSITY_DOMAIN')
    for j in range(3):
        if np.any((energy<FIT[j]) & (k[:,j]>0)):raise DomainError('INACTIVE_FIT_CUTOFF')
    if Y==0 and not (g0[1:3]==0).all():raise DomainError('ABSENT_HELIUM_STATE')
    b=binding_weights(Y);scale=np.array([1.,1.,1.,max(g0[3],1e-8)])
    calls=0

    def evaluate(g):
        nonlocal calls
        require_state(g,Y)
        pg=(1-c.theta_photo)*g0+c.theta_photo*g
        mg=(1-c.theta_micro)*g0+c.theta_micro*g
        n1,event,heat=photon_events(n0,energy,k,alpha(pg,Y),dt,c.photon_method)
        r=provider(a,mg,nh0,Y);calls+=1;r.validate(Y)
        species=event.sum(axis=0)
        residual=np.r_[g[:3]-g0[:3]-event_fractions(species,Y)-dt*r.fraction_s,
                       g[3]-g0[3]-heat-dt*r.thermal_ev_h_s]
        du_photon=float(np.dot(n1-n0,energy))
        db=float(b@(g[:3]-g0[:3]));dw=float(g[3]-g0[3])
        esc=dt*r.escaped_ev_h_s;cmb=dt*r.cmb_ev_h_s
        energy_defect=math.fsum([du_photon,db,dw,esc,-cmb])
        energy_budget=c.energy_atol+c.energy_rtol*math.fsum(map(abs,[du_photon,db,dw,esc,cmb]))
        if not np.isfinite(residual).all() or not math.isfinite(energy_defect):raise StepRejected('NONFINITE_RESIDUAL')
        norm=float(np.max(np.abs(residual)/scale))
        return norm,residual,energy_defect,energy_budget,n1,event,heat,r

    g=g0.copy()
    for iteration in range(c.max_newton+1):
        cur=evaluate(g)
        norm,res,defect,budget,n1,event,heat,micro=cur
        if norm<=c.nonlinear_tol and abs(defect)<=budget:
            return Step(g.copy(),n1.copy(),event.copy(),heat,micro,res.copy(),defect,
                        float(math.fsum(n0)-math.fsum(n1)-math.fsum(event.ravel())),calls,iteration)
        if iteration==c.max_newton:break
        jac=np.empty((4,4))
        for j in range(4):
            if Y==0 and j in (1,2):
                jac[:,j]=0.;jac[j,j]=1.;continue
            delta=2e-6*max(abs(g[j]),1e-4 if j<3 else 1e-6)
            candidates=(delta,-delta)
            col=None
            for d in candidates:
                gp=g.copy();gp[j]+=d
                if not state_valid(gp,Y):continue
                try:
                    rr=evaluate(gp)[1]
                except DomainError:
                    continue
                col=(rr-res)/d;break
            if col is None:raise StepRejected('NO_ADMISSIBLE_JACOBIAN')
            jac[:,j]=col
        try:
            direction=np.linalg.solve(jac,-res)
        except np.linalg.LinAlgError as e:raise StepRejected('SINGULAR_JACOBIAN') from e
        if Y==0:direction[1:3]=0.
        merit=max(norm/c.nonlinear_tol,abs(defect)/budget)
        accepted=False
        for ls in range(25):
            trial=g+2.**(-ls)*direction
            if not state_valid(trial,Y):continue
            try:new=evaluate(trial)
            except DomainError:continue
            new_merit=max(new[0]/c.nonlinear_tol,abs(new[2])/new[3])
            if new_merit<merit or (new[0]<=c.nonlinear_tol and abs(new[2])<=new[3]):
                g=trial;accepted=True;break
        if not accepted:raise StepRejected(f'LINE_SEARCH_REJECT norm={norm:.17e}, energy={defect:.17e}, budget={budget:.17e}')
    raise StepRejected(f'NEWTON_BUDGET_EXHAUSTED nfev={calls}')
