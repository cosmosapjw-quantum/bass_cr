"""A standalone, positive, energy-and-number-conserving threshold-aware RT prototype.

This IS NOT the rei_bianchi production spectrum or chemical solver. The only imported
model choices are its 50,000 K truncated blackbody source, Verner atomic fit and
implicit backward-Euler absorption transaction. Every threshold carries TWO
states, inactive from below and active from above for that absorber, at an
identical limiting energy. Distinct tags are accounting states, NOT novel physics.

Unit convention: E [eV], N photon count per unit H, neutral [cm^-3], t [s],
c [cm s^-1], cross section [cm^2]. Rest-frame proper time, signature (-+++).
"""
from __future__ import annotations
from dataclasses import dataclass
from bisect import bisect_left
from math import expm1, exp, hypot, sqrt, isfinite
from typing import Sequence

SOURCE_EDGES=(13.60,24.59,54.42,100.0)
ION_NAMES=("HI","HeI","HeII")
ATOMIC = {"HI": (13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),
          "HeI":(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),
          "HeII":(54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.)}
C_CM_S=2.99792458e10
BOLTZMANN_EV_K=8.617333262145e-5


def verner(kind: str, E:float)->float:
    if kind not in ATOMIC or not isfinite(E) or E<0 or E>50000:
        raise ValueError('unsupported absorber/energy')
    threshold,e0,sigma0,ya,p,yw,y0,y1=ATOMIC[kind]
    if E<threshold: return 0.
    x=E/e0-y0; y=hypot(x,y1)
    return sigma0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+sqrt(y/ya))**(-p)*1e-18


def source_shape(E:float)->float:
    return E*E/expm1(E/(50000*BOLTZMANN_EV_K))


def _simpson(a:float,b:float,n:int,power:int)->float:
    h=(b-a)/n
    sm=0.
    for i in range(n+1):
        E=a+i*h
        sm+=(1 if i in(0,n) else (4 if i%2 else 2))*source_shape(E)*E**power
    return sm*h/3


def frozen_source(n_per_segment:int=16)->list[tuple[float,float]]:
    """(centroid energy, fraction) from frozen AXBI per-segment Simpson-32."""
    if n_per_segment not in (8,16,32,64,128):raise ValueError('unsupported numerical axis')
    cells=[]
    for a,b in zip(SOURCE_EDGES,SOURCE_EDGES[1:]):
        for j in range(n_per_segment):
            lo=a if j==0 else a*(b/a)**(j/n_per_segment)
            hi=b if j+1==n_per_segment else a*(b/a)**((j+1)/n_per_segment)
            m0=_simpson(lo,hi,32,0); m1=_simpson(lo,hi,32,1)
            if not m0>0:raise ValueError('zero source cell')
            cells.append((m1/m0,m0))
    norm=sum(c for _,c in cells)
    return [(e,c/norm) for e,c in cells]


def frozen_grid(n_per_segment:int=16)->tuple[float,...]:
    grid=[SOURCE_EDGES[0]]
    for a,b in zip(SOURCE_EDGES,SOURCE_EDGES[1:]):
        for j in range(n_per_segment):
            grid.append(b if j+1==n_per_segment else a*(b/a)**((j+1)/n_per_segment))
    return tuple(grid)

@dataclass(frozen=True)
class Node:
    E:float
    side:str # ordinary, inactive (chi^-), active (chi^+)
    threshold:str|None = None

    def cross_section(self,kind:str)->float:
        if self.side=='inactive' and self.threshold==kind:
            return 0.0
        return verner(kind,self.E)


class TaggedGrid:
    def __init__(self,base_energies:Sequence[float]):
        energies=tuple(float(x) for x in base_energies)
        if len(energies)<2 or any(not isfinite(e) for e in energies) or any(b<=a for a,b in zip(energies,energies[1:])):
            raise ValueError('strict increasing finite energy grid required')
        if energies[0]!=SOURCE_EDGES[0] or energies[-1]!=SOURCE_EDGES[-1]:
            raise ValueError('frozen source interval is 13.6 to 100 eV')
        self.base=energies
        self.states=[]
        self.by_side={}
        for i,e in enumerate(energies):
            threshold=next((k for k in ION_NAMES if ATOMIC[k][0]==e),None)
            if threshold is None:
                self._put(i,'ordinary',None)
            else:
                if i>0:self._put(i,'inactive',threshold)
                self._put(i,'active',threshold)
        # 13.6 inactive deliberately omitted since energies below support go to escrow.

    def _put(self,i,side,threshold):
        index=len(self.states)
        self.states.append(Node(self.base[i],side,threshold))
        self.by_side[(i,side)]=index

    def endpoint(self,i:int,toward:str)->int:
        e=self.base[i]
        if e not in SOURCE_EDGES[:3]:return self.by_side[(i,'ordinary')]
        if (i,'inactive') not in self.by_side:return self.by_side[(i,'active')]
        return self.by_side[(i,'active' if toward=='from_above' else 'inactive')]

    def _weights(self,E:float,number:float,boundary_ok:bool=True):
        """Sparse nonnegative push, O(log N) bracketing and <=2 states."""
        if not isfinite(E) or not isfinite(number) or E<=0 or number<0:
            raise ValueError('nonnegative finite count and positive energy required')
        if E<self.base[0]:
            if not boundary_ok: raise ValueError('below support')
            return (),number,number*E
        if E>self.base[-1]:raise ValueError('above support')
        upper=bisect_left(self.base,E)
        if upper==0 or E==self.base[upper]:
            return ((self.endpoint(upper,'from_above'),number),),0.,0.
        lower=upper-1
        w=(E-self.base[lower])/(self.base[upper]-self.base[lower])
        return ((self.endpoint(lower,'from_above'),number*(1-w)),
                (self.endpoint(upper,'from_below'),number*w)),0.,0.

    def deposit(self,E:float,number:float=1.,boundary_ok:bool=True)->tuple[list[float],float,float]:
        """Convenience dense form for tests and small component fixtures."""
        weights,escn,escu=self._weights(E,number,boundary_ok)
        result=self.empty()
        for i,n in weights:result[i]+=n
        return result,escn,escu

    def empty(self)->list[float]:return [0.]*len(self.states)

    def add(self,target:list[float],packet:list[float]):
        if len(target)!=len(self.states) or len(packet)!=len(self.states):raise ValueError('shape mismatch')
        for i,value in enumerate(packet):target[i]+=value

    def moments(self,stock:Sequence[float]):
        if len(stock)!=len(self.states):raise ValueError('length mismatch')
        if any(not isfinite(x) or x<-1e-25 for x in stock):raise ValueError('invalid stock')
        return sum(stock),sum(n*state.E for n,state in zip(stock,self.states))

    def from_frozen_source(self,axis:int=16)->list[float]:
        if self.base!=frozen_grid(axis):
            raise ValueError('source spectral resolution and receiver grid identity mismatch')
        stock=self.empty()
        for E,n in frozen_source(axis):
            sparse,_,_=self._weights(E,n)
            for i,value in sparse:stock[i]+=value
        return stock

    def redshift(self,stock:Sequence[float],energy_ratio:float):
        if len(stock)!=len(self.states) or not isfinite(energy_ratio) or energy_ratio<=0:
            raise ValueError('invalid redshift input')
        out=self.empty();escrow_count=escrow_energy=0.
        N0,U0=self.moments(stock)
        for old_index,(old,number) in enumerate(zip(self.states,stock)):
            if number==0:continue
            energy=old.E*energy_ratio
            if energy==old.E and energy_ratio==1:
                # Preserve chi^- state at exactly zero redshift.
                out[old_index]+=number
                continue
            if energy==old.E and energy_ratio<1 and old.side=='active':
                # Sub-ulp redshift: physical energy is below this threshold.
                if old.threshold and (j:=bisect_left(self.base,old.E))>0:
                    out[self.by_side[(j,'inactive')]]+=number
                    continue
            sparse,esc_n,esc_u=self._weights(energy,number)
            for i,value in sparse:out[i]+=value
            escrow_count+=esc_n;escrow_energy+=esc_u
        N1,U1=self.moments(out)
        work=U0-U1-escrow_energy
        return out,{'boundary_count':escrow_count,'boundary_energy_eV':escrow_energy,
                    'photon_redshift_work_eV':work,'count_residual':N0-N1-escrow_count,
                    'energy_residual_eV':U0-U1-escrow_energy-work,'expected_work_eV':(1-energy_ratio)*U0}

    def absorb_backward_euler(self,stock:Sequence[float],neutrals_cm3:Sequence[float],dt_s:float):
        """Frozen-neutral one-step implicit photon absorption, NOT chemistry evolution."""
        if len(stock)!=len(self.states) or len(neutrals_cm3)!=3 or any(not isfinite(x) or x<0 for x in neutrals_cm3) or not isfinite(dt_s) or dt_s<0:
            raise ValueError('invalid absorption input')
        updated=self.empty();events=[0.]*3;heat=[0.]*3;binding=[0.]*3
        for index,(node,n0) in enumerate(zip(self.states,stock)):
            if not isfinite(n0) or n0<0:raise ValueError('negative photon stock')
            if n0==0:continue
            rates=[dt_s*C_CM_S*d*node.cross_section(k) for d,k in zip(neutrals_cm3,ION_NAMES)]
            n1=n0/(1+sum(rates));updated[index]=n1
            for j,r in enumerate(rates):
                ev=n1*r
                if ev<0:raise ArithmeticError('negative event')
                events[j]+=ev
                binding[j]+=ev*ATOMIC[ION_NAMES[j]][0]
                heat[j]+=ev*(node.E-ATOMIC[ION_NAMES[j]][0])
        N0,U0=self.moments(stock);N1,U1=self.moments(updated)
        evtotal=sum(events);binding_total=sum(binding);heat_total=sum(heat)
        # Species numbers are per initial H normalization, NOT normalized by helium.
        ionic_delta={'H_I':-events[0],'H_II':events[0],
                     'He_I':-events[1],'He_II':events[1]-events[2],
                     'He_III':events[2],'electron':evtotal}
        return updated,{
            'photo_events_per_H':dict(zip(ION_NAMES,events)),
            'stoichiometric_deltas_per_H':ionic_delta,
            'binding_eV_per_H':dict(zip(ION_NAMES,binding)),
            'direct_photoheat_eV_per_H':dict(zip(ION_NAMES,heat)),
            'free_electron_births_per_H':evtotal,
            'photon_count_consumed_per_H':N0-N1,
            'count_ledger_residual':N0-N1-evtotal,
            'energy_ledger_residual_eV':U0-U1-binding_total-heat_total,
            'photon_energy_before_eV':U0,'photon_energy_after_eV':U1
        }


class OriginalGrid(TaggedGrid):
    """Control mimicking the two-neighbor deposit, using only ordinary active nodes."""
    def __init__(self,base_energies):
        self.base=tuple(float(x) for x in base_energies)
        self.states=[Node(x,'ordinary') for x in self.base]
        self.by_side={(i,'ordinary'):i for i in range(len(self.states))}

    def endpoint(self,i:int,toward:str)->int:return i


class CohortTransport:
    """Unmerged finite source-packet characteristic CONTROL, not production data model.

    Keeps energy for each photon source-centroid cohort until redshift/absorption,
    avoiding remap-created threshold mixing. Complexity scales with the number
    of separately injected cohorts and therefore cannot be a drop-in full-history
    AXBI replacement without bounded compression/advection analysis.
    """
    def __init__(self,cohorts:Sequence[tuple[float,float]]):
        if any(not isfinite(e) or e<=0 or not isfinite(n) or n<0 for e,n in cohorts):
            raise ValueError('invalid cohort input')
        self.cohorts=list(cohorts)

    @classmethod
    def frozen_source(cls,axis:int=16):
        return cls(frozen_source(axis))

    def moments(self):
        return sum(n for _,n in self.cohorts),sum(e*n for e,n in self.cohorts)

    def redshift(self,energy_ratio:float):
        if not isfinite(energy_ratio) or energy_ratio<=0:raise ValueError('invalid redshift ratio')
        before=self.moments();updated=[];b_n=b_u=0.
        for E,n in self.cohorts:
            e=E*energy_ratio
            if e<SOURCE_EDGES[0]:b_n+=n;b_u+=n*e
            elif e>SOURCE_EDGES[-1]:raise ValueError('above support')
            else:updated.append((e,n))
        self.cohorts=updated
        after=self.moments()
        work=before[1]-after[1]-b_u
        return {'boundary_count':b_n,'boundary_energy_eV':b_u,'photon_work_eV':work,
                'number_residual':before[0]-after[0]-b_n,
                'energy_residual_eV':before[1]-after[1]-b_u-work}

    def absorb_backward_euler(self,neutrals_cm3:Sequence[float],dt_s:float):
        if len(neutrals_cm3)!=3 or any(not isfinite(x) or x<0 for x in neutrals_cm3) or not isfinite(dt_s) or dt_s<0:
            raise ValueError('invalid absorption parameters')
        before=self.moments();updated=[];events=[0.]*3;heats=[0.]*3;bindings=[0.]*3
        for E,n in self.cohorts:
            rates=[dt_s*C_CM_S*d*verner(kind,E) for d,kind in zip(neutrals_cm3,ION_NAMES)]
            new=n/(1+sum(rates));updated.append((E,new))
            for j,r in enumerate(rates):
                ev=new*r;events[j]+=ev;bindings[j]+=ev*ATOMIC[ION_NAMES[j]][0]
                heats[j]+=ev*(E-ATOMIC[ION_NAMES[j]][0])
        self.cohorts=updated;after=self.moments()
        return {'photo_events_per_H':dict(zip(ION_NAMES,events)),
                'binding_eV_per_H':dict(zip(ION_NAMES,bindings)),
                'direct_photoheat_eV_per_H':dict(zip(ION_NAMES,heats)),
                'number_residual':before[0]-after[0]-sum(events),
                'energy_residual_eV':before[1]-after[1]-sum(heats)-sum(bindings)}
