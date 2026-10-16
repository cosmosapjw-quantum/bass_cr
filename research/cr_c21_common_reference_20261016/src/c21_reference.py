"""Conditional C21 common-q, source-age and threshold-split photon controls.

This is NOT the original C21 native Rust solver, not Verner transport parity,
and not an evolving-gas cosmological prediction. Source and atomic constants
are transcribed from pinned original owner files in the associated evidence.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, expm1, log, sqrt
import numpy as np
from scipy.integrate import quad, solve_ivp

A_REF = 1.0/21.0
MPC_CM = 3.0856775814913673e24
C_CM_S = 29979245800.0
EV_ERG = 1.602176634e-12
KB_ERG_K = 1.380649e-16
H0 = 67.4e5/MPC_CM
OMEGA_M, OMEGA_R = .315, 9.2e-5
OMEGA_L = 1.0-OMEGA_M-OMEGA_R
HEL_Y = .2454/(4*(1-.2454))
FIT = np.array([13.60,24.59,54.42], dtype=float)
BIND = np.array([13.598434599702,24.587389011,54.41776],dtype=float)
# True native Verner ground-state fit rows, input photoelectric energy in eV.
VERNER = np.array([
    [13.60,.4298,54750.,32.88,2.963,0.,0.,0.],
    [24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136],
    [54.42,1.72,13690.,32.88,2.963,0.,0.,0.],
],dtype=float)


def _positive(x,name):
    if not (np.isfinite(x) and x>0):
        raise ValueError(f'{name}: expected finite positive')
    return float(x)


def H(a):
    a=_positive(a,'scale factor')
    return H0*sqrt(OMEGA_M/a**3+OMEGA_R/a**4+OMEGA_L)


def dt_x(x0,x1):
    if not(np.isfinite(x0) and np.isfinite(x1) and x1>=x0):
        raise ValueError('clock interval')
    return quad(lambda x:1/H(exp(x)),x0,x1,epsrel=5e-13)[0]


def epoch_gas(a,nH0,nHe0):
    a=_positive(a,'a');nH0=_positive(nH0,'total hydrogen nuclei at a=1')
    nHe0=_positive(nHe0,'total helium nuclei at a=1')
    return {'a':a,'nH_total_cm3':nH0/a**3,'nHe_total_cm3':nHe0/a**3,
            'Tcmb_K':2.7255/a}


def c20_to_pr150(q):
    return np.asarray(q,dtype=float)/A_REF


def pr150_to_c20(q):
    return np.asarray(q,dtype=float)*A_REF


def physical_energy_from_pr150(qref,a):
    return np.asarray(qref,dtype=float)*A_REF/_positive(a,'a')


def threshold_q_pr150(a):
    return FIT*_positive(a,'a')/A_REF


@dataclass(frozen=True)
class Moment:
    n:float
    q_c20:float           # sum photon count times q_C20 [eV/H]
    lo_c20:float
    hi_c20:float
    def check(self):
        if not(all(np.isfinite(x) for x in (self.n,self.q_c20,self.lo_c20,self.hi_c20))
               and self.n>0 and 0<self.lo_c20<=self.hi_c20
               and self.lo_c20*self.n-64*np.finfo(float).eps*max(self.q_c20,self.lo_c20*self.n,self.hi_c20*self.n)<=self.q_c20
               and self.q_c20<=self.hi_c20*self.n+64*np.finfo(float).eps*max(self.q_c20,self.lo_c20*self.n,self.hi_c20*self.n)):
            raise ValueError('unphysical C20 moment/support')
        return self
    def in_pr150(self):
        self.check()
        return (self.n,self.q_c20/A_REF,self.lo_c20/A_REF,self.hi_c20/A_REF)
    def energy(self,a):
        return self.q_c20/_positive(a,'a')


def fractions(g,helium_y=HEL_Y):
    """Absorber counts per TOTAL H nucleus for H, He I, He II."""
    x,y,z=np.asarray(g,dtype=float)
    if not (0<=x<=1 and 0<=y and 0<=z and y+z<=1 and helium_y>0):
        raise ValueError('H/He fractions outside simplex')
    return np.array([1-x,helium_y*(1-y-z),helium_y*y])


def per_absorber_rust_input(events_per_H,heat_eV_per_H,gas,dt):
    """C19/C21 native RHS gamma[s^-1] and heat[erg/absorber/s].

    The caller owns photon absorption; the native owner owns nonphoto
    chemistry, escape, CMB and EOS. Never multiply the source/J again.
    """
    dt=_positive(dt,'proper time')
    abs_per_H=fractions(gas)
    events=np.asarray(events_per_H,dtype=float)
    heat=np.asarray(heat_eV_per_H,dtype=float)
    if not(events.shape==heat.shape==(3,) and np.all(np.isfinite(events))
           and np.all(np.isfinite(heat)) and np.min(events)>=0 and np.min(heat)>=0):
        raise ValueError('invalid photoevents or heat')
    if np.any((abs_per_H==0)&(events>0)) or np.any((abs_per_H==0)&(heat>0)):
        raise ValueError('absent species absorbed photons')
    gamma=np.divide(events,dt*abs_per_H,out=np.zeros(3),where=abs_per_H>0)
    power=np.divide(heat*EV_ERG,dt*abs_per_H,out=np.zeros(3),where=abs_per_H>0)
    return gamma,power


def verner_sigma(E,k):
    """Original owner Verner law: sigma in cm^2, with fit threshold gate."""
    E=float(E)
    if not np.isfinite(E) or E<0 or E>50000: raise ValueError('Verner energy domain')
    eth,e0,s0,ya,p,yw,y0,y1=VERNER[k]
    if E<eth: return 0.
    x=E/e0-y0; y=sqrt(x*x+y1*y1)
    return s0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+sqrt(y/ya))**(-p)*1e-18


def powerlaw_hazard(q_c20,nH0,neutral_per_H,amplitude_cm2):
    """For sigma(E)=amp*(E/Ethr)^-3, lambda_i = constant before fit cutoff.

    Proper nH,total(a)=nH0 a^-3, fixed fractional abundances.
    This is an independent FLRW toy ORACLE, NOT the native Verner fit.
    """
    q=_positive(q_c20,'q_C20');nh=_positive(nH0,'nH0')
    frac=np.asarray(neutral_per_H,dtype=float)
    sigma=np.asarray(amplitude_cm2,dtype=float)
    if frac.shape!=(3,) or sigma.shape!=(3,) or np.any(frac<0) or np.any(sigma<0):
        raise ValueError('species hazards')
    return C_CM_S*nh*frac*sigma*(FIT/q)**3


def threshold_partition(q_c20,a0,a1):
    """Interior thresholds in x=ln(a), no assumed ionization event at exact tie."""
    q=_positive(q_c20,'q');lo=log(_positive(a0,'a0'));hi=log(_positive(a1,'a1'))
    if not hi>lo:raise ValueError('forward interval required')
    crossed=sorted({log(q/t) for t in FIT if lo<log(q/t)<hi})
    return [lo,*crossed,hi]


def continuum_packet(q_c20,a_birth,a_end,n_init,nH0,neutral_per_H,
                    sigma_at_threshold=(8e-18,1.2e-18,1.5e-18)):
    """Exact frozen-composition NUMBER evolution and quadrature energy integrals.

    Constant hazards per active segment are analytic. Work is integrated as
    integral E(x) N(x) dx. This is not a gas-backreacting solution.
    """
    q=_positive(q_c20,'q');a_birth=_positive(a_birth,'birth')
    a_end=_positive(a_end,'end');n_init=_positive(n_init,'initial photons')
    lam=powerlaw_hazard(q,nH0,neutral_per_H,sigma_at_threshold)
    intervals=threshold_partition(q,a_birth,a_end)
    n=n_init;A=np.zeros(3);Q=np.zeros(3);W=0.
    for left,right in zip(intervals[:-1],intervals[1:]):
        mid=(left+right)/2
        active=(q*exp(-mid)>=FIT)
        rate=lam*active
        total=float(sum(rate))
        proper_dt=dt_x(left,right)
        released=n*(-expm1(-total*proper_dt)) if total else 0.
        rate_frac=rate/total if total else np.zeros(3)
        A+=released*rate_frac
        if total:
            # Optical-depth clock u=total*(t-t_left) removes the unresolved
            # x-width ~H/total of an optically thick photon boundary layer.
            # Number attenuation is analytic; energy/work integral is positive.
            tau=total*proper_dt
            ucap=min(tau,52.)
            def optical_rhs(u,v):
                x=v[0]
                energy=q*exp(-x)
                hd=H(exp(x))/total
                survivor=exp(-u)
                return (hd, survivor*energy, survivor*energy*hd)
            solution=solve_ivp(optical_rhs,(0.,ucap),[left,0.,0.],method='DOP853',
                   rtol=2e-13,atol=[2e-17,2e-17,2e-20],max_step=2.)
            if not solution.success:raise ArithmeticError(solution.message)
            # tail contribution at u>52 is bounded by n*E_start*exp(-52)
            # for expansion; it is below ~3e-23*n*E_start.
            integral_energy=n*solution.y[1,-1]
            W+=n*solution.y[2,-1]
            Q+=rate_frac*integral_energy
        else:
            # Exact source-free redshift work, stable for small x intervals.
            W+=n*q*exp(-left)*(-expm1(-(right-left)))
        n-=released
    heat=Q-BIND*A
    e0=q/a_birth*n_init;e1=q/a_end*n
    ledger=(e0-e1-sum(heat+BIND*A)-W)
    return {'n_end':n,'event_per_H':A,'heat_ev_H':heat,'work_ev_H':W,
            'energy_before':e0,'energy_after':e1,'energy_defect':ledger,
            'crossings':len(intervals)-2,'species_absorbed_energy':Q}


def independent_packet_ivp(q_c20,a_birth,a_end,n_init,nH0,neutral_per_H,
                          sigma_at_threshold=(8e-18,1.2e-18,1.5e-18)):
    """Independent augmented continuous IVP in log a, exact fit cuts.

    [N, A_HI,A_HeI,A_HeII, Qheat_HI,Qheat_HeI,Qheat_HeII, W].
    No use of the closed-form exponential endpoint update.
    """
    q=_positive(q_c20,'q');_positive(n_init,'n_init')
    lam=powerlaw_hazard(q,nH0,neutral_per_H,sigma_at_threshold)
    intervals=threshold_partition(q,a_birth,a_end)
    state=np.r_[n_init,np.zeros(7)]
    for left,right in zip(intervals[:-1],intervals[1:]):
        mid=(left+right)/2;rate=lam*(q*exp(-mid)>=FIT)
        def rhs(x,s):
            photo=s[0]*rate/H(exp(x))
            return np.r_[-sum(photo),photo,photo*(q*exp(-x)-BIND),s[0]*q*exp(-x)]
        result=solve_ivp(rhs,(left,right),state,method='Radau',rtol=2e-11,
                         atol=2e-14,max_step=(right-left)/12)
        if not result.success:raise ArithmeticError(result.message)
        state=result.y[:,-1]
    return state


def source_rate_per_H(a,nH0,escape_fraction=.2):
    """Pinned AxbiSource::at_redshift MD14 conditional source per TOTAL H."""
    a=_positive(a,'a');nH0=_positive(nH0,'nH0')
    zp=1/a
    if not 4<=zp-1<=20:raise ValueError('source support z=4..20')
    sfr=.015*zp**2.7/(1+(zp/2.9)**5.6)
    log_yield=1/(.00038*.002**.227+.01858)-np.log10(2.55)
    return float(escape_fraction*10**log_yield*sfr/MPC_CM**3/nH0)


def birth_quadrature(x0,x1,nH0,scheme):
    if x1<=x0:raise ValueError('source interval')
    if scheme=='GL2':
        nodes=(-1/sqrt(3),1/sqrt(3));weights=(1.,1.)
    elif scheme=='MID':
        nodes=(0.,);weights=(2.,)
    else:raise ValueError('quadrature')
    half=(x1-x0)/2;mid=(x1+x0)/2
    return [(exp(mid+half*u),half*w*source_rate_per_H(exp(mid+half*u),nH0)/H(exp(mid+half*u)))
            for u,w in zip(nodes,weights)]


def native_spectral_cells(n=16):
    """Original AxbiSource geometric source cell edges and Simpson32 centroid.

    PR150 instead deposits GL8 shape moments per cell; compare explicitly.
    """
    out=[]
    kt=KB_ERG_K/EV_ERG*50000
    def shape(E): return E*E/expm1(E/kt)
    glx,glw=np.polynomial.legendre.leggauss(8)
    for lo,hi in zip((13.6,24.59,54.42),(24.59,54.42,100)):
        for i in range(n):
            a=lo if i==0 else lo*(hi/lo)**(i/n)
            b=hi if i+1==n else lo*(hi/lo)**((i+1)/n)
            h=(b-a)/32
            s0=s1=0.
            for j in range(33):
                E=a+h*j;w=1 if j==0 or j==32 else (4 if j%2 else 2)
                s0+=w*shape(E);s1+=w*shape(E)*E
            z=(b-a)/2*glx+(a+b)/2;w=(b-a)/2*glw
            mass=float(sum(w*np.array([shape(E) for E in z])))
            u=float(sum(w*np.array([shape(E)*E for E in z])))
            out.append((a,b,s0*h/3,s1*h/3,mass,u))
    mass_sum=sum(x[2] for x in out)
    return [{'lo':a,'hi':b,'frac':m/mass_sum,'centroid_C20':u/m,
             'centroid_PR150':u8/m8,'simpson32_norm':m,'gl8_norm':m8}
            for a,b,m,u,m8,u8 in out]


def frozen_source_age_step(x0,x1,nH0,gas_fractions,source_scheme='GL2',subdivisions=1):
    """Positive FLRW source-birth packet + exact E^-3 toy attenuation.

    This is a C21 pre-adapter acceptance control, NOT native Verner,
    native EOS/RR/CI, source-quadrature parity, or full EoR.
    """
    fr=fractions(gas_fractions)
    aend=exp(x1)
    birth=birth_quadrature(x0,x1,nH0,source_scheme)
    cells=native_spectral_cells(subdivisions)
    source_N=source_U=end_N=end_U=work=0.
    events=np.zeros(3);heat=np.zeros(3)
    for ab,source_birth_count in birth:
        for cell in cells:
            ne=source_birth_count*cell['frac']
            eemit=cell['centroid_C20']
            if ne<=0:raise ValueError('source creation must be positive')
            original=continuum_packet(ab*eemit,ab,aend,ne,nH0,fr)
            source_N+=ne;source_U+=ne*eemit
            end_N+=original['n_end']
            end_U+=original['energy_after']
            events+=original['event_per_H']
            heat+=original['heat_ev_H']
            work+=original['work_ev_H']
    return {'source_N':source_N,'source_U_ev_H':source_U,
            'end_N':end_N,'end_U_ev_H':end_U,'events_per_H':events,
            'heat_eV_H':heat,'work_eV_H':work,'birth_packets':len(birth)*len(cells),
            'number_defect':source_N-end_N-sum(events),
            'energy_defect':source_U-end_U-sum(heat+BIND*events)-work,
            'binding_eV_H':float(np.dot(BIND,events))}