"""Independent physical-time H/He photo-only Radau reference with source-age impulses.

This is NOT native Grackle / Case-A / cosmological reionization. Actual owner
MD14 *total emission clock*, original Verner fit, conditional 3-energy manufactured
spectral source. Both density and photon energy vary in the same FLRW x=ln(a).

Independent of exact-pair solver: integrates elementary continuous ODE and true
absorber exposure for native rate representability diagnostics.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Sequence
import numpy as np
from scipy.integrate import solve_ivp
from exposure_contract import BIND_EV, EV_ERG, A_REF, native_photo_rates

H0=67.4*1e5/3.0856775814913673e24
N_H0=1.8981984507140266e-7
Y_HE=0.2454/(4*(1-0.2454))
C_CM_S=2.99792458e10
MPC_CM=3.0856775814913673e24
VERNER=(
(13.60,0.4298,54750.,32.88,2.963,0.,0.,0.),
(24.59,13.61,949.2,1.469,3.188,2.039,0.4434,2.136),
(54.42,1.72,13690.,32.88,2.963,0.,0.,0.),
)
FIT=(13.60,24.59,54.42)


def H(x):
    a=math.exp(x)
    return H0*math.sqrt(.315/a**3+9.2e-5/a**4+(1-.315-9.2e-5))


def source_rate(x):
    zp=math.exp(-x)
    if not 5<=zp<=21:raise ValueError('original MD14 bounded domain')
    sfr=.015*zp**2.7/(1+(zp/2.9)**5.6)
    log_yield=1/(.00038*.002**.227+.01858)-math.log10(2.55)
    return .2*10**log_yield*sfr/MPC_CM**3/N_H0


def cross(j,e):
    eth,e0,s0,ya,p,yw,y0,y1=VERNER[j]
    if e<eth:return 0.
    xx=e/e0-y0
    yy=math.sqrt(xx*xx+y1*y1)
    return s0*((xx-1)**2+yw*yw)*yy**(.5*p-5.5)*(1+math.sqrt(yy/ya))**(-p)*1e-18


def initial_atoms(xh=.2,y=.15,z=.01):
    return np.array([1-xh,xh,Y_HE*(1-y-z),Y_HE*y,Y_HE*z],float)


def binding(atoms):
    return BIND_EV[0]*atoms[1]+BIND_EV[1]*(atoms[3]+atoms[4])+BIND_EV[2]*atoms[4]


def thermal_ev(atoms,T=8500):
    kb=1.380649e-16
    particles=1+Y_HE+atoms[1]+atoms[3]+2*atoms[4]
    return 1.5*kb*T*particles/EV_ERG


@dataclass(frozen=True)
class Cohort:
    q20:float
    birth_x:float
    start_n:float
    name:str


@dataclass
class PhotoHistory:
    x0:float
    xend:float
    cohorts:tuple[Cohort,...]
    initial_photons:tuple[float,...]
    source_n:float
    source_u:float
    initial_gas:tuple[float,...]
    initial_thermal:float
    yfinal:np.ndarray
    segments:int
    exposures:tuple[float,float,float]
    endpoint_rates:object
    mass_res:float
    energy_res:float
    initial_photon_energy:float
    photon_work:float
    gas_work:float


def make_cohorts(x0:float,dx:float,
                 initial_energy=(13.8,24.8,55.0),
                 initial_count=(.014,.010,.008),
                 birth_energy=(15.1,26.1,55.0),
                 birth_weights=(.2,.3,.5)):
    if any(v<=0 for v in initial_energy+birth_energy):raise ValueError('energy')
    xend=x0+dx
    mid=x0+dx/2
    births=(mid-dx/(2*math.sqrt(3)),mid+dx/(2*math.sqrt(3)))
    cohorts=[Cohort(math.exp(x0)*energy,x0,n,f'old{i}') for i,(energy,n) in enumerate(zip(initial_energy,initial_count))]
    oldn=len(cohorts)
    for age_id,xb in enumerate(births):
        dsource=source_rate(xb)*dx/(2*H(xb))
        for j,(energy,w) in enumerate(zip(birth_energy,birth_weights)):
            cohorts.append(Cohort(math.exp(xb)*energy,xb,dsource*w,f'birth{age_id}_species{j}'))
    return tuple(cohorts),oldn


def run_reference(x0=math.log(1./12), dx=.025,opacity_scale=1e-3,
                  rtol=3e-11,atol=1e-13):
    if not (dx>0 and opacity_scale>=0):raise ValueError('controlled domain')
    cohorts,nold=make_cohorts(x0,dx)
    ns=len(cohorts)
    xend=x0+dx
    atoms=initial_atoms()
    thermal=thermal_ev(atoms)
    # y=[photons M, gas atoms5, gas thermal, species photo events3,
    #    species heat3, photon work, gas work, absorber exposure3]
    offsets=dict(atom=ns,thermal=ns+5,event=ns+6,heat=ns+9,
                 wg=ns+12,wgas=ns+13,expo=ns+14)
    size=ns+17
    y=np.zeros(size,dtype=float)
    for i,c in enumerate(cohorts[:nold]):y[i]=c.start_n
    y[ns:ns+5]=atoms
    y[offsets['thermal']]=thermal
    source_n=sum(c.start_n for c in cohorts[nold:])
    source_u=sum(c.start_n*c.q20*math.exp(-c.birth_x) for c in cohorts[nold:])
    initial_u=sum(c.start_n*c.q20*math.exp(-x0) for c in cohorts[:nold])
    init_b=binding(atoms)
    mints=[x0,xend]+[c.birth_x for c in cohorts if x0<c.birth_x<xend]
    for c in cohorts:
        for eth in FIT:
            xc=math.log(c.q20/eth)
            if x0<xc<xend:mints.append(xc)
    cuts=sorted(set(mints))

    def rhs(xx,yv,lo,hi):
        # One-sided at exact Verner discontinuities; positive interval interior.
        xc=min(max(xx,lo+(hi-lo)*1e-9),hi-(hi-lo)*1e-9)
        dydx=np.zeros_like(yv)
        invH=1/H(xc)
        nh=N_H0*math.exp(-3*xc)
        atoms_now=yv[ns:ns+5]
        tr=[0,2,3]; post=[1,3,4]
        for r,c in enumerate(cohorts):
            N=yv[r]
            if N==0.0:continue
            E=c.q20*math.exp(-xc)
            dydx[offsets['wg']]+=N*E
            for j in range(3):
                coeff=opacity_scale*C_CM_S*nh*cross(j,E)*invH
                f=coeff*N*atoms_now[tr[j]]
                dydx[r]-=f
                dydx[ns+tr[j]]-=f
                dydx[ns+post[j]]+=f
                dydx[offsets['event']+j]+=f
                dydx[offsets['heat']+j]+=f*(E-BIND_EV[j])
                dydx[offsets['thermal']]+=f*(E-BIND_EV[j])
        dydx[offsets['thermal']]-=2*yv[offsets['thermal']]
        dydx[offsets['wgas']]+=2*yv[offsets['thermal']]
        for j,index in enumerate(tr):
            dydx[offsets['expo']+j]+=atoms_now[index]*invH
        return dydx

    source_births={}
    for r,c in enumerate(cohorts[nold:],start=nold):
        source_births.setdefault(c.birth_x,[]).append(r)
    for lo,hi in zip(cuts[:-1],cuts[1:]):
        if hi<=lo:continue
        sol=solve_ivp(lambda x,v:rhs(x,v,lo,hi),(lo,hi),y,method='Radau',
                      rtol=rtol,atol=atol,max_step=(hi-lo)/8)
        if not sol.success:raise RuntimeError('reference Radau failed: '+sol.message)
        y=sol.y[:,-1].copy()
        # An exact source impulse belongs to its original birth x and q.
        for i in source_births.get(hi,[]):y[i]+=cohorts[i].start_n
    final_atoms=y[ns:ns+5]
    photon_n=float(sum(y[:ns]))
    photon_u=float(sum(y[i]*c.q20*math.exp(-xend) for i,c in enumerate(cohorts)))
    event=y[offsets['event']:offsets['event']+3]
    heat=y[offsets['heat']:offsets['heat']+3]
    expo=y[offsets['expo']:offsets['expo']+3]
    mass_res=float(sum(c.start_n for c in cohorts)-photon_n-sum(event))
    energy_res=float(initial_u+source_u-photon_u-
         (binding(final_atoms)-init_b)-(y[offsets['thermal']]-thermal)-
         y[offsets['wg']]-y[offsets['wgas']])
    from scipy.integrate import quad
    dt=quad(lambda x:1/H(x),x0,xend,epsrel=2e-13,epsabs=.05)[0]
    rates=native_photo_rates(event,heat,expo,final_atoms[[0,2,3]],dt,N_H0*math.exp(-3*xend))
    return PhotoHistory(x0,xend,cohorts,tuple(c.start_n for c in cohorts[:nold]),
       source_n,source_u,tuple(atoms),thermal,y,len(cuts)-1,tuple(expo),rates,
       mass_res,energy_res,initial_u,float(y[offsets['wg']]),float(y[offsets['wgas']]))
