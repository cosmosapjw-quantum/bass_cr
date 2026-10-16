"""C21B standalone positive source-age FLRW H/He photo-only reference.

No native Rust invoked. Physical photon energy E=q20/a, qref=q20/(1/21).
Every photon (number per total H) retains its birth x and q. Gas nuclei also
use per-total-H. Exact symmetric binary reactions guarantee nonnegative stocks.
The method has NO Case-A recombination, collisional processes, Thomson/CMB or
actual Bianchi dynamics: do not pass this model as a production reionization run.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math
from typing import Callable
import numpy as np
from numpy.polynomial.legendre import leggauss

A_REF = 1.0 / 21.0
BIND_EV = (13.598434599702, 24.587389011, 54.41776)
FIT_EV = (13.60, 24.59, 54.42)
EV_ERG = 1.602176634e-12
KB_ERG_K = 1.380649e-16
C_CM_S = 2.99792458e10
MPC_CM = 3.0856775814913673e24
NH0_CM3 = 1.8981984507140266e-7  # Native-total-H at a=.047620181473387826, HE23 PR70
Y_HE = 0.2454 / (4 * (1-0.2454))
H0_S = 67.4 * 1e5 / MPC_CM
COSMO = (0.315, 9.2e-5, 1.0 - 0.315 - 9.2e-5)
# Owner AtomicProvider::cross_section row order eth,E0,s0,ya,p,yw,y0,y1
VERNER = (
    (13.60, 0.4298, 5.475e4, 32.88, 2.963, 0., 0., 0.),
    (24.59, 13.61, 949.2, 1.469, 3.188, 2.039, 0.4434, 2.136),
    (54.42, 1.720, 1.369e4, 32.88, 2.963, 0., 0., 0.),
)


def finite_nonnegative(*v:float)->bool:
    return all(math.isfinite(float(x)) and float(x) >= 0 for x in v)


def E_from_q20(q20: float, x: float)->float:
    if not(math.isfinite(q20) and q20>0 and math.isfinite(x)):
        raise ValueError("invalid canonical energy")
    return q20*math.exp(-x)


def to_ref_energy(q20:float)->float:
    if not math.isfinite(q20) or q20<=0:
        raise ValueError('invalid q20')
    return q20/A_REF


def from_ref_energy(qref:float)->float:
    if not math.isfinite(qref) or qref<=0:
        raise ValueError('invalid qref')
    return qref*A_REF


def hubble(x:float)->float:
    if not math.isfinite(x):raise ValueError("nonfinite epoch")
    m,r,l=COSMO
    v=H0_S*math.sqrt(m*math.exp(-3*x)+r*math.exp(-4*x)+l)
    if not math.isfinite(v) or v<=0:raise ValueError("invalid FLRW clock")
    return v


def nH_total(x:float)->float:
    return NH0_CM3*math.exp(-3*x)


def md14_rate_per_total_h_s(x:float)->float:
    """User owner's MD14_Z002_FESC_BB50K_13P6_100 source exactly as coded."""
    z=math.exp(-x)-1
    if not 4 <= z <= 20:raise ValueError("outside owner MD14 redshift support")
    zp=1+z
    sfr=0.015*zp**2.7/(1+(zp/2.9)**5.6)
    log_yield=1/(0.00038*0.002**0.227+0.01858)-math.log10(2.55)
    return 0.2*10**log_yield*sfr/(MPC_CM**3*NH0_CM3)


def verner_sigma_cm2(species:int,energy_ev:float)->float:
    if species not in (0,1,2):raise ValueError("bad species")
    if not math.isfinite(energy_ev) or not 0<=energy_ev<=50000:
        raise ValueError("invalid Verner energy")
    et,e0,s0,ya,p,yw,y0,y1=VERNER[species]
    if energy_ev<et:return 0.
    xx=energy_ev/e0-y0
    yy=math.hypot(xx,y1)
    return s0*((xx-1)**2+yw*yw)*yy**(p/2-5.5)*(1+math.sqrt(yy/ya))**(-p)*1e-18


def blackbody_shape(E_ev:float)->float:
    kT=50000*KB_ERG_K/EV_ERG
    return E_ev**2/math.expm1(E_ev/kT)


def bb50k_positive_bins(n_per_band:int=2)->list[tuple[float,float]]:
    """True positive child weights of original 13.6..100 eV shape, normalized.

    This is a discrete Gauss source model, not owner C20 centroid or PR150 cell
    moment closure; always record n_per_band when comparing outputs.
    """
    if not 1<=n_per_band<=32:raise ValueError("bad source quadrature")
    nodes,w=leggauss(n_per_band)
    energies=[]; weights=[]
    for lo,hi in zip([13.6,24.59,54.42],[24.59,54.42,100.]):
        half=(hi-lo)/2;center=(hi+lo)/2
        for u,wg in zip(nodes,w):
            e=center+half*float(u)
            energies.append(e);weights.append(half*float(wg)*blackbody_shape(e))
    norm=math.fsum(weights)
    assert norm>0
    return [(a,b/norm) for a,b in zip(energies,weights)]


def exact_pair(N:float,A:float,k:float,dt:float)->tuple[float,float,float]:
    """Stable exact solution N' = A' = -k N A; numbers dimensionless per H."""
    if not finite_nonnegative(N,A,k,dt):raise ValueError("pair domain")
    if N==0 or A==0 or k==0 or dt==0:return N,A,0.
    m=min(N,A);d=abs(N-A)
    z=k*d*dt
    if not math.isfinite(z) or z<0:raise ValueError("optical-depth overflow")
    eta=(-math.expm1(-z)/d) if d>0 else (k*dt)
    if not math.isfinite(eta):raise ValueError("reaction overflow")
    mnew=m*math.exp(-z)/(1+m*eta)
    lost=m-mnew
    # Reconstruct both from common minority to preserve their exact difference.
    # Avoid cancellation and numerical negatives in the optically thick limit.
    if N>=A:
        return d+mnew,mnew,lost
    return mnew,d+mnew,lost


@dataclass
class Photon:
    q20:float
    number:float
    birth_x:float | None
    energy_emitted_ev:float
    birth_id:int


@dataclass
class State:
    x:float
    atoms:list[float]  # H0, H+, He0, He+, He++ each per total H
    thermal_ev:float
    photons:list[Photon]=field(default_factory=list)
    source_n:float=0.
    source_u:float=0.
    photo_events:list[float]=field(default_factory=lambda:[0.,0.,0.])
    photoheat:list[float]=field(default_factory=lambda:[0.,0.,0.])
    work_gamma:float=0.
    work_gas:float=0.
    crossings:list[int]=field(default_factory=lambda:[0,0,0])
    initial_n:float=0.
    initial_u:float=0.
    initial_b:float=0.
    initial_w:float=0.

    def clone(self)->"State":
        return State(self.x,self.atoms.copy(),self.thermal_ev,
            [Photon(p.q20,p.number,p.birth_x,p.energy_emitted_ev,p.birth_id) for p in self.photons],
            self.source_n,self.source_u,self.photo_events.copy(),self.photoheat.copy(),
            self.work_gamma,self.work_gas,self.crossings.copy(),self.initial_n,self.initial_u,
            self.initial_b,self.initial_w)

    def fractions(self)->tuple[float,float,float]:
        return self.atoms[1],self.atoms[3]/Y_HE,self.atoms[4]/Y_HE

    def binding_ev(self)->float:
        h0,hp,he0,hep,hepp=self.atoms
        return BIND_EV[0]*hp+BIND_EV[1]*(hep+hepp)+BIND_EV[2]*hepp

    def energy_photons(self)->float:
        return math.fsum(p.number*E_from_q20(p.q20,self.x) for p in self.photons)

    def number_photons(self)->float:
        return math.fsum(p.number for p in self.photons)

    def eos_temperature_K(self)->float:
        n_e=self.atoms[1]+self.atoms[3]+2*self.atoms[4]
        n_particles=1+Y_HE+n_e
        return self.thermal_ev*EV_ERG/(1.5*KB_ERG_K*n_particles)

    def validation(self)->None:
        if not math.isfinite(self.x) or not finite_nonnegative(self.thermal_ev,*self.atoms):
            raise ValueError("gas simplex/energy domain")
        if not abs(math.fsum(self.atoms[:2])-1.)<=2e-12:raise ValueError("H nuclei")
        if not abs(math.fsum(self.atoms[2:])-Y_HE)<=2e-12*Y_HE:raise ValueError("He nuclei")
        if any(not finite_nonnegative(p.q20,p.number) or p.q20<=0 for p in self.photons):
            raise ValueError("negative/nonfinite photon")

    def ledgers(self)->dict:
        photon=self.number_photons();u=self.energy_photons()
        ev=math.fsum(self.photo_events)
        n_res=math.fsum([self.initial_n,self.source_n,-photon,-ev])
        e_res=math.fsum([self.initial_u,self.source_u,-u,
           -(self.binding_ev()-self.initial_b),-(self.thermal_ev-self.initial_w),
           -self.work_gamma,-self.work_gas])
        return dict(number_residual=n_res,energy_residual_ev_per_H=e_res,
           emitted_per_H=self.source_n,photo_events_per_H=self.photo_events,
           photoheat_ev_per_H=self.photoheat,photons_per_H=photon,
           photon_energy_ev_per_H=u,work_photon_ev_per_H=self.work_gamma,
           work_thermal_ev_per_H=self.work_gas,
           x=self.x,x_fractions=self.fractions(),T_K=self.eos_temperature_K(),
           number_cohorts=len(self.photons),crossings=self.crossings)


def initial_state(x:float,T_K:float=8500.,
                  fractions=(0.0991426055371428,0.1047018209734982,3.0750379671694307e-5),
                  injected_initial:tuple[tuple[float,float],...]=())->State:
    h,y,z=map(float,fractions)
    if not(math.isfinite(x) and 0<=h<=1 and 0<=y and 0<=z and y+z<=1 and T_K>0):
        raise ValueError("invalid initial gas")
    atoms=[1-h,h,Y_HE*(1-y-z),Y_HE*y,Y_HE*z]
    n_particles=1+Y_HE+h+Y_HE*(y+2*z)
    w=1.5*KB_ERG_K*T_K*n_particles/EV_ERG
    p=[Photon(math.exp(x)*e,n,None,e,i) for i,(e,n) in enumerate(injected_initial)]
    s=State(x=x,atoms=atoms,thermal_ev=w,photons=p)
    s.initial_n=s.number_photons()
    s.initial_u=s.energy_photons()
    s.initial_b=s.binding_ev()
    s.initial_w=s.thermal_ev
    s.validation()
    return s


class PhotonReactor:
    def __init__(self,energy_nodes=2,source_scale=1.,opacity_scale=1.,
                 source:Callable[[float],float]=md14_rate_per_total_h_s,
                 clock:Callable[[float],float]=hubble,
                 sigma:Callable[[int,float],float]=verner_sigma_cm2,
                 density:Callable[[float],float]=nH_total):
        if not finite_nonnegative(source_scale,opacity_scale):raise ValueError("bad scaling")
        self.spectrum=bb50k_positive_bins(energy_nodes)
        self.source=source;self.clock=clock;self.sigma=sigma;self.density=density
        self.source_scale=source_scale;self.opacity_scale=opacity_scale
        self._serial=0

    def _geometry(self,s:State,x:float):
        if x<s.x:raise ValueError("reverse geometry")
        dx=x-s.x
        if dx==0:return
        factor=math.exp(-dx)
        # Difference form avoids subtracting nearly equal global radiation energies.
        work=math.fsum(p.number*E_from_q20(p.q20,s.x)*(-math.expm1(-dx)) for p in s.photons)
        s.work_gamma+=work
        prev=s.thermal_ev
        s.thermal_ev=prev*math.exp(-2*dx)
        s.work_gas+=prev-s.thermal_ev
        s.x=x

    def _reaction(self,s:State,x:float,dt_s:float):
        if dt_s<=0:return
        a=math.exp(x)
        nH=self.density(x)
        if not math.isfinite(nH) or nH<=0:raise ValueError("bad proper total H")
        options=[]
        for i,p in enumerate(s.photons):
            if p.number<=0:continue
            ee=p.q20/a
            for j in range(3):
                sig=self.sigma(j,ee)
                if sig<0 or not math.isfinite(sig):raise ValueError("invalid cross-section")
                k=C_CM_S*nH*sig*self.opacity_scale
                if k>0:options.append((i,j,k,ee))
        if not options:return
        for entries in (options,reversed(options)):
            for i,j,k,ee in entries:
                photon=s.photons[i]
                ai=(0,2,3)[j]; successor=(1,3,4)[j]
                n1,a1,delta=exact_pair(photon.number,s.atoms[ai],k,dt_s/2)
                photon.number=n1
                s.atoms[ai]=a1
                s.atoms[successor]+=delta
                s.photo_events[j]+=delta
                heat=delta*(ee-BIND_EV[j])
                if heat<-1e-20:raise ValueError("negative photoheat: fitting threshold vs binding")
                s.photoheat[j]+=heat
                s.thermal_ev+=heat

    def _segment(self,s:State,x0:float,x1:float,split_thresholds=True):
        if x1<x0:raise ValueError("invalid step direction")
        if x1==x0:return
        cuts=[x0,x1]
        if split_thresholds:
            for p in s.photons:
                if p.number<=0:continue
                for j,cut in enumerate(FIT_EV):
                    xc=math.log(p.q20/cut)
                    if x0<xc<x1:
                        cuts.append(xc)
                        s.crossings[j]+=1
        cuts=sorted(set(cuts))
        if len(cuts)>2048:raise ValueError("too many threshold events for reference")
        for left,right in zip(cuts[:-1],cuts[1:]):
            mid=0.5*(left+right)
            self._geometry(s,mid)
            # GL4 positive proper-time quadrature; no time frozen at a0.
            gx,gw=leggauss(4)
            dt=(right-left)/2 * math.fsum(float(w)/self.clock(mid+float(g)*(right-left)/2) for g,w in zip(gx,gw))
            self._reaction(s,mid,dt)
            self._geometry(s,right)

    def _birth(self,s:State,xb:float,weight_dx:float):
        rate=self.source_scale*self.source(xb)
        if not finite_nonnegative(rate) or self.clock(xb)<=0:raise ValueError("bad emission")
        birth_count=rate*weight_dx/self.clock(xb)
        s.source_n+=birth_count
        for e,w in self.spectrum:
            n=birth_count*w
            self._serial+=1
            s.photons.append(Photon(math.exp(xb)*e,n,xb,e,self._serial))
            s.source_u+=n*e

    def advance(self,s:State,end_x:float,nsteps:int,source_on=True,split_thresholds=True)->State:
        if not isinstance(nsteps,int) or not 1<=nsteps<=1024:
            raise ValueError("bad nsteps")
        if not math.isfinite(end_x) or end_x<=s.x:raise ValueError("end epoch")
        initial_x=s.x
        for step in range(nsteps):
            x0=initial_x+(end_x-initial_x)*step/nsteps
            x1=initial_x+(end_x-initial_x)*(step+1)/nsteps
            if abs(s.x-x0)>3e-12:raise RuntimeError("step alignment")
            if source_on:
                mid=(x0+x1)/2
                half=(x1-x0)/2
                left=mid-half/math.sqrt(3)
                right=mid+half/math.sqrt(3)
                for xb in (left,right):
                    self._segment(s,s.x,xb,split_thresholds)
                    self._birth(s,xb,half)
                self._segment(s,s.x,x1,split_thresholds)
            else:
                self._segment(s,s.x,x1,split_thresholds)
        s.validation()
        return s
