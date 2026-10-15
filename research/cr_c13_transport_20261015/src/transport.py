"""Source-born Bianchi-I photon transport and H/He microphysics, scoped C13.

Independent owner-bound numerical study, not the rei_bianchi Rust runtime.
Origin-of-photon direction is sampled isotropically in a birth tetrad;
photon numbers per original comoving hydrogen nucleus, received energy
redshifted along a retained birth-direction label. The source spectrum
is the SHA-locked owner Scenario/Spectrum; ionization Verner fits same owner.

New in C13 vs C12: no pre-population with future unattenuated source.
Sources are born at midpoint of each history step, then lose photon
occupation by chemistry while energy redshifts under anisotropic
Bianchi-I expansion. Gas density scales exactly as a^-3.
Case-A recombination may be enabled as a separate anchored Grackle
source-law module, with escaping recombination radiation explicitly
ledgered rather than double-counted as ionizing source photons.

Important NOT INCLUDED: actual ray-traced SOURCE07 evolved q stocks,
angular Jacobian R*J, clumping/source fluctuations, full cooling/OTS,
Compton, secondary ionization, or actual cosmological science admission.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import math
import time

import numpy as np
from numpy.polynomial.legendre import leggauss

from owner_age_bridge import (
    owner_namespace,source_identity,verner_sigma_array,
)
from physical_age import Gas,K_B_EV_PER_K,update_gas

C = 29979245800.0
BEGIN_E, END_E = 13.6, 100.0
BOUNDARIES = (13.6,24.59,54.42,100.0)


@dataclass
class PhotonStock:
    """Flat vectorized list of source-born photon packets."""
    birth_a: np.ndarray
    birth_mu: np.ndarray
    birth_energy_eV: np.ndarray
    photons_per_H: np.ndarray
    current_energy_eV: np.ndarray

    @classmethod
    def empty(cls) -> PhotonStock:
        v=np.empty(0,dtype=float)
        return cls(*(v.copy() for _ in range(5)))

    @property
    def count(self)->int:
        return len(self.photons_per_H)

    def byte_count(self)->int:
        return sum(getattr(self,k).nbytes for k in
                   ("birth_a","birth_mu","birth_energy_eV",
                    "photons_per_H","current_energy_eV"))

    def append(self,other:PhotonStock) -> None:
        for k in ("birth_a","birth_mu","birth_energy_eV",
                  "photons_per_H","current_energy_eV"):
            setattr(self,k,np.r_[getattr(self,k),getattr(other,k)])


def photon_energy_ratio(model,birth:np.ndarray,at:float,
                        q:float,mu:np.ndarray)->np.ndarray:
    """Exact given owner's axisymmetric Bianchi-I energy factors.

    mu is tetrad polar cosine AT BIRTH. Multiplication by a_birth/a
    handles FLRW. q is the owner's fixed shear-family parameter.
    """
    a=np.asarray(birth,dtype=float)
    mu=np.asarray(mu,dtype=float)
    if np.any(a>at) or np.any(a<=0) or np.any(abs(mu)>1):
        raise ValueError("invalid birth/current photon time or mu")
    # owner b(a,q) denotes logarithmic anisotropic scale distortion
    bnow=model.b(float(at),float(q))
    bold=np.array([model.b(float(ai),float(q)) for ai in np.unique(a)])
    uniq,ids=np.unique(a,return_inverse=True)
    db=bnow-bold[ids]
    return a/at * np.sqrt(np.exp(2*db)*(1-mu**2)+np.exp(-4*db)*mu**2)


def make_birth_cohort(ns:dict,a:float,q:float,source_photons:float,
                      nmu:int=8,energy_order:int=8) -> PhotonStock:
    """Inject nonnegative source photon packet weights at actual age a."""
    if source_photons<0 or nmu<2 or energy_order<2:
        raise ValueError("invalid source/birth quadrature")
    mus,mweights=leggauss(nmu)
    x,w=leggauss(energy_order)
    Es=[];ws=[]
    for lo,hi in zip(BOUNDARIES[:-1],BOUNDARIES[1:]):
        E=(lo+hi)/2+(hi-lo)/2*x
        W=.5*(hi-lo)*w*ns["spec"].phi(E)
        Es.append(E);ws.append(W)
    energies=np.concatenate(Es)
    evw=np.concatenate(ws)
    # Explicitly normalize the discretized known source law.
    evw=evw/np.sum(evw)
    mu=np.repeat(mus,len(energies))
    en=np.tile(energies,nmu)
    weight=source_photons*np.repeat(mweights/2,len(energies))*np.tile(evw,nmu)
    if np.any(weight<0) or not np.isclose(sum(weight),source_photons,rtol=2e-13,atol=1e-14):
        raise AssertionError("source photon count not preserved")
    return PhotonStock(np.full(len(en),a),mu,en,weight,en.copy())


def alpha_owner_rr(T:float)->np.ndarray:
    """Selected pinned owner Grackle-3.4.1 Case-A RR coefficient subset.

    Exact math expressions transcribed from rei_microphysics/src/igm_rates.rs,
    sha-locked in the consumer record. Process order HII, HeII, HeIII.
    No extrapolation outside owner operational T domain 1..1e6 K.
    """
    if not np.isfinite(T) or not (1.0<=T<=1e6):
        raise ValueError("owner IGM rate temperature outside 1..1e6 K")
    te=T/11605.
    l=np.log(te)
    if T>5500.:
        hrr=np.exp(
            -28.61303380689232
            -0.7241125657826851*l
            -0.02026044731984691*l**2
            -0.002380861877349834*l**3
            -0.0003212605213188796*l**4
            -0.00001421502914054107*l**5
            +4.989108920299513e-6*l**6
            +5.755614137575758e-7*l**7
            -1.856767039775261e-8*l**8
            -3.071135243196595e-9*l**9)
    else:
        # The selected source's K2 low branch uses he_recombination(T).0.
        hrr=3.92e-13/te**.6353
    he2=3.92e-13/te**.6353
    he3=3.36e-10/np.sqrt(T)/(T/1000.)**.2/(1+(T/1e6)**.7)
    return np.array([hrr,he2,he3])


def recombine_case_a(g:Gas,delta_t:float,nH:float,nHe:float,
                     ne_method:str="frozen")->tuple[Gas,np.ndarray,float]:
    """Positive exact-Markov H/He RR with selected electron-density time centering.

    The "frozen" option is the original C13 scheme. The "midpoint" option
    solves a scalar implicit electron-density consistency condition. At a
    given n_e midpoint, H/He are propagated by exactly the same matrix
    exponential as C13; positivity and all stage ledgers are preserved.
    nH, nHe and T are frozen at the OWNER segment midpoint. This addresses
    *one* numerical defect only, not the entire cosmological time error.
    """
    if delta_t<=0:return g,np.zeros(3),0.
    if ne_method not in ("frozen","midpoint"):
        raise ValueError("unknown electron time-centering method")
    y=nHe/nH
    xe_start=g.electrons_per_h(y)
    coeff=alpha_owner_rr(g.temp_K)*nH*delta_t

    def propagate(xe:float)->Gas:
        a=coeff*xe
        hii0=1.-g.xhi
        hii_end=hii0*np.exp(-a[0])
        x1,x2,x3=g.xhei,g.xheii,g.xheiii
        x3_end=x3*np.exp(-a[2])
        if abs(a[1]-a[2])<1e-8:
            x2_end=np.exp(-a[1])*(x2+a[2]*x3)
        else:
            x2_end=x2*np.exp(-a[1])+x3*a[2]*(
                np.exp(-a[2])-np.exp(-a[1]))/(a[1]-a[2])
        return Gas(1.-hii_end,1.-x2_end-x3_end,x2_end,x3_end,g.temp_K)

    if ne_method=="frozen" or xe_start==0:
        xe_effective=xe_start
    else:
        # Electron abundance falls monotonically under pure Case-A RR,
        # so x_e^mid = [x_e(initial)+x_e(final(x_e^mid))]/2 has a
        # bracket [0,x_e(initial)]. Brent finds the unique physical
        # branch without clamping any species or changing rates.
        from scipy.optimize import brentq
        xe_effective=brentq(
            lambda x:x-.5*(xe_start+propagate(x).electrons_per_h(y)),
            0.,xe_start,xtol=2e-14,rtol=9e-16)
    updated=propagate(xe_effective)
    events=np.array([(1.-g.xhi)-(1.-updated.xhi),
                     y*(updated.xhei-g.xhei),
                     y*(g.xheiii-updated.xheiii)])
    if np.any(events<-2e-13):
        raise AssertionError("negative recombination events")
    events=np.maximum(events,0.)
    thermal_escape=1.5*K_B_EV_PER_K*g.temp_K*float(np.sum(events))
    old_u=g.thermal_energy_ev_per_h(y)
    new_u=updated.thermal_energy_ev_per_h(y)
    if not np.isclose(old_u-new_u,thermal_escape,rtol=1e-9,atol=1e-12):
        raise AssertionError("thermal recombination ledger mismatch")
    return updated,events,thermal_escape


def vector_photo_reactions(photons:np.ndarray, energy_eV:np.ndarray,
                           absorber_cm3:np.ndarray, delta_t:float,
                           source_fit:tuple, binding_eV:np.ndarray):
    """Batched exact frozen-opacity photon event integrator.

    Photon probability is independent for each input packet. Total species
    events and heats are reductions over packets. This reusable kernel is
    separately cross-checked against a scalar reference and does not
    assume an unknown spectrum reconstructed from N/U moments.
    """
    if delta_t<=0 or np.any(absorber_cm3<0):
        raise ValueError("positive proper dt and nonnegative species required")
    sig=np.column_stack([verner_sigma_array(energy_eV,p) for p in source_fit])
    tau_species=C*delta_t*sig*absorber_cm3[None,:]
    tau=tau_species.sum(axis=1)
    g=np.ones_like(tau)
    np.divide(-np.expm1(-tau),tau,out=g,where=tau>0)
    packet_events=photons[:,None]*tau_species*g[:,None]
    survived=photons*np.exp(-tau)
    species_events=packet_events.sum(axis=0)
    heats=np.sum(packet_events*(energy_eV[:,None]-binding_eV[None,:]),axis=0)
    if np.any(survived<0) or np.any(species_events<0):
        raise AssertionError("negative photon counts")
    return survived,species_events,heats


def segment(ns:dict,stock:PhotonStock,gas:Gas,
            a0:float,a1:float,q:float,
            recombination:bool,ledger:dict,rr_ne_method:str="frozen")->Gas:
    """Advance existing photon packets through one *half* epoch substep."""
    model=ns["model"]
    mid=math.sqrt(a0*a1)
    # proper dt via positive 2-node Gauss in ln a
    x,w=leggauss(2)
    la0,la1=np.log(a0),np.log(a1)
    nodes=np.exp((la0+la1)/2+(la1-la0)*x/2)
    dt=(la1-la0)/2*sum(w[k]/model.hubble(float(nodes[k]),q) for k in range(2))
    if dt<=0:raise AssertionError("nonpositive proper step")
    y=ns["nhe"]/(model.nh*5.**3)
    nH=model.nh/mid**3
    nHe=y*nH

    def redshift(at:float):
        if stock.count==0:return
        before=float(np.dot(stock.photons_per_H,stock.current_energy_eV))
        ratio=photon_energy_ratio(model,stock.birth_a,at,q,stock.birth_mu)
        en=stock.birth_energy_eV*ratio
        after=float(np.dot(stock.photons_per_H,en))
        ledger["geometric_photon_work_eV_per_H"]+=before-after
        stock.current_energy_eV=en

    def gas_adiabatic(g:Gas,left:float,right:float):
        before=g.thermal_energy_ev_per_h(y)
        t=g.temp_K*(left/right)**2
        after=Gas(g.xhi,g.xhei,g.xheii,g.xheiii,t)
        ledger["adiabatic_gas_work_eV_per_H"]+=before-after.thermal_energy_ev_per_h(y)
        return after

    gas=gas_adiabatic(gas,a0,mid)
    redshift(mid)
    if recombination:
        gas,recs,therm=recombine_case_a(gas,dt/2,nH,nHe,ne_method=rr_ne_method)
        ledger["recomb_events_per_H"]+=recs
        ledger["recomb_thermal_escape_eV_per_H"]+=therm

    if stock.count:
        # Midpoint predictor changes ONLY the absorber state, not the
        # tracked stock or the ledger. The full exponential is recomputed
        # from original packet counts for second-order coupled chemistry.
        _,preview_events,preview_heat=vector_photo_reactions(
            stock.photons_per_H,stock.current_energy_eV,
            gas.proper_absorbers(nH,nHe),0.5*dt,
            ns["fit"],np.asarray(ns["bind"]))
        gas_half=update_gas(gas,preview_events,float(np.sum(preview_heat)),nH,nHe)
        survived,absorbed,heats=vector_photo_reactions(
            stock.photons_per_H,stock.current_energy_eV,
            gas_half.proper_absorbers(nH,nHe),dt,
            ns["fit"],np.asarray(ns["bind"]))
        gas=update_gas(gas,absorbed,float(np.sum(heats)),nH,nHe)
        stock.photons_per_H=survived
        ledger["photo_events_per_H"]+=absorbed
        ledger["photo_heat_eV_per_H"]+=heats

    if recombination:
        gas,recs,therm=recombine_case_a(gas,dt/2,nH,nHe,ne_method=rr_ne_method)
        ledger["recomb_events_per_H"]+=recs
        ledger["recomb_thermal_escape_eV_per_H"]+=therm
    redshift(a1)
    gas=gas_adiabatic(gas,mid,a1)
    return gas


def integrate(ns:dict,q:float,nstep:int=32,a0:float=.1,a1:float=.11,
              gas0:Gas|None=None,recombination:bool=True,
              nmu:int=8,ne:int=8,source_scale:float=1.,
              source_rule:str="midpoint",rr_ne_method:str="frozen") -> dict:
    """Age-resolved injection and transport using the exact owner source curve."""
    if gas0 is None:gas0=Gas(.9,.85,.15,0.,4000.)
    if nstep<2 or not (0<a0<a1<=.2) or source_scale<0:
        raise ValueError("invalid time/source domain")
    if source_rule not in {"midpoint","gauss2"}:
        raise ValueError("source_rule must be midpoint or gauss2")
    if rr_ne_method not in {"frozen","midpoint"}:
        raise ValueError("rr_ne_method must be frozen or midpoint")
    model=ns["model"]
    stock=PhotonStock.empty()
    gas=gas0
    y=ns["nhe"]/(model.nh*5.**3)
    t0=time.perf_counter()
    ledger=dict(
        source_emitted_photons_per_H=0.,
        source_emitted_energy_eV_per_H=0.,
        photo_events_per_H=np.zeros(3),
        photo_heat_eV_per_H=np.zeros(3),
        recomb_events_per_H=np.zeros(3),
        recomb_thermal_escape_eV_per_H=0.,
        adiabatic_gas_work_eV_per_H=0.,
        geometric_photon_work_eV_per_H=0.,
    )
    u_start=gas.thermal_energy_ev_per_h(y)
    xi=np.linspace(np.log(a0),np.log(a1),nstep+1)
    history=[]
    if source_rule=="midpoint":
        emission_x=np.array([0.])
        emission_w=np.array([2.])
    else:
        emission_x,emission_w=leggauss(2)
    for i in range(nstep):
        astart,aend=np.exp(xi[i]),np.exp(xi[i+1])
        last=astart
        for xn,wn in zip(emission_x,emission_w):
            birth=np.exp(.5*(xi[i]+xi[i+1])+.5*(xi[i+1]-xi[i])*xn)
            gas=segment(ns,stock,gas,last,birth,q,recombination,ledger,rr_ne_method)
            source_count=source_scale*.5*(xi[i+1]-xi[i])*wn*(
                    model.rate(birth)/model.hubble(birth,q))
            # No source implies no emitted photon cohort. Avoid building
            # zero-mass source packets that would otherwise consume O(Nstep)
            # memory and O(Nstep^2) work across pure-recombination tests.
            if source_count:
                cohort=make_birth_cohort(ns,birth,q,source_count,nmu,ne)
                stock.append(cohort)
                ledger["source_emitted_photons_per_H"]+=source_count
                ledger["source_emitted_energy_eV_per_H"]+=float(
                    np.dot(cohort.photons_per_H,cohort.birth_energy_eV))
            last=birth
        gas=segment(ns,stock,gas,last,aend,q,recombination,ledger,rr_ne_method)
        history.append((aend,gas.xhi,gas.xhei,gas.xheii,gas.xheiii,gas.temp_K,
                        float(sum(stock.photons_per_H))))
    nfinal=float(np.sum(stock.photons_per_H))
    e_final=float(np.dot(stock.photons_per_H,stock.current_energy_eV))
    p=ledger["photo_events_per_H"]
    r=ledger["recomb_events_per_H"]
    q_photo=float(np.sum(ledger["photo_heat_eV_per_H"]))
    b_photo=float(np.dot(p,ns["bind"]))
    b_recomb=float(np.dot(r,ns["bind"]))
    u_final=gas.thermal_energy_ev_per_h(y)
    # Local physical energy:
    # emitted radiation = final radiation+gas thermal increase+net ionic
    # binding+geometry and expansion work+escaping recombination photons.
    energy_defect=(ledger["source_emitted_energy_eV_per_H"]-e_final
                   -ledger["geometric_photon_work_eV_per_H"]
                   -(u_final-u_start)
                   -ledger["adiabatic_gas_work_eV_per_H"]
                   -(b_photo-b_recomb)
                   -(b_recomb+ledger["recomb_thermal_escape_eV_per_H"]))
    output={
       "schema":"BASS_CR_C13_BIANCHI_I_BIRTH_TRANSPORT_V1",
       "q":q,"nsteps":nstep,"a0":a0,"a1":a1,
       "source_scale":source_scale,"recombination":recombination,
       "source_quadrature":source_rule,
       "recombination_electron_centering":rr_ne_method,
       "gas_initial":gas0.__dict__.copy(),"gas_final":gas.__dict__.copy(),
       "output_photon_packets":stock.count,
       "packet_memory_bytes":stock.byte_count(),
       "elapsed_wall_seconds":time.perf_counter()-t0,
       "history":history,
       "ledgers":{
          **{k:v.tolist() if isinstance(v,np.ndarray) else v
               for k,v in ledger.items()},
          "final_photons_per_H":nfinal,
          "final_photon_energy_eV_per_H":e_final,
          "initial_gas_thermal_eV_per_H":u_start,
          "final_gas_thermal_eV_per_H":u_final,
          "ionization_binding_stored_eV_per_H":b_photo-b_recomb,
          "recomb_binding_escaped_eV_per_H":b_recomb,
          "photon_count_residual":(
             ledger["source_emitted_photons_per_H"]-nfinal-float(sum(p))),
          "total_local_energy_residual_eV_per_H":float(energy_defect),
          "helium_nucleus_residual":float(gas.xhei+gas.xheii+gas.xheiii-1.),
          "charge_residual":float(gas.electrons_per_h(y)-
                (1-gas.xhi+y*(gas.xheii+2*gas.xheiii))),
       },
       "scope":"single-homogeneous-reservoir, fresh emission births, energy redshift, proper density, optional local CaseA; no owner radiation R*J or full EoR admission",
    }
    if min(gas.xhi,gas.xhei,gas.xheii,gas.xheiii)<-1e-12:
        raise AssertionError("negative final state")
    return output


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--owner",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--nsteps",type=int,default=32)
    parser.add_argument("--q",type=float,default=0.)
    parser.add_argument("--a0",type=float,default=.1)
    parser.add_argument("--a1",type=float,default=.11)
    parser.add_argument("--no-recomb",action="store_true")
    parser.add_argument("--source-rule",choices=("midpoint","gauss2"),default="midpoint")
    parser.add_argument("--rr-ne",choices=("frozen","midpoint"),default="frozen")
    args=parser.parse_args()
    ns=owner_namespace(args.owner)
    result=integrate(ns,args.q,args.nsteps,args.a0,args.a1,
                     recombination=not args.no_recomb,source_rule=args.source_rule,
                     rr_ne_method=args.rr_ne)
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({
        "gas_final":result["gas_final"],"packets":result["output_photon_packets"],
        "source_N":result["ledgers"]["source_emitted_photons_per_H"],
        "photon_count_residual":result["ledgers"]["photon_count_residual"],
        "energy_defect":result["ledgers"]["total_local_energy_residual_eV_per_H"],
        "seconds":result["elapsed_wall_seconds"]},indent=2))
