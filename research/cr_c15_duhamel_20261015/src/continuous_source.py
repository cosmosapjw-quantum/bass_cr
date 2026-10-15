"""C15 constructive source-born Bianchi-I H/He radiation/chemistry prototype.

The photon-number birth spectrum is an authenticated owner Scenario/Spectrum.
Unlike C13 midpoint point-injection, this variant integrates the emitted source
inside the SAME time interval as local absorptions via positive Duhamel phi(-tau).

Conditional accuracy scope: piecewise midpoint source, gas, physical density,
direction-dependent photon energies; exact continuous-source/opacity only when
S, lambda, E and gas are constant on each interval. The gas midpoint predictor
uses both existing and newly emitted photons. Case-A H/He recombination uses C14
self-consistent electron midpoint but still has the C13 toy thermal closure.
No owner SOURCE07 spatial ray, R*J or actual EoR history is computed.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss

from owner_age_bridge import owner_namespace,verner_sigma_array,source_identity
from physical_age import Gas,K_B_EV_PER_K,update_gas
from transport import (
    C,PhotonStock,make_birth_cohort,photon_energy_ratio,recombine_case_a,
)
from exponential_source import absorb_with_source


def proper_dt(model,a0:float,a1:float,q:float)->float:
    """Positive GL2 dt/d ln a, aligned to owner proper-time clock."""
    if a1<=a0 or a0<=0:
        raise ValueError("proper time interval endpoints must increase")
    x,w=leggauss(2)
    la,lb=np.log(a0),np.log(a1)
    aa=np.exp(.5*(la+lb)+.5*(lb-la)*x)
    d=.5*(lb-la)*np.sum([w[j]/model.hubble(float(z),q)
                       for j,z in enumerate(aa)])
    if not d>0 or not np.isfinite(d):
        raise ArithmeticError("invalid proper clock")
    return float(d)


def evolve_continuous(ns:dict,q:float,nstep:int=32,a0:float=.1,a1:float=.11,
                      gas0:Gas|None=None,recombination:bool=True,
                      nmu:int=8,ne:int=8,source_scale:float=1.,
                      rr_ne_method:str="midpoint",
                      exact_zero_prune:bool=True,
                      cached_birth_spectrum:bool=True)->dict:
    """Time centered absorption and positive Duhamel newborn-source transport."""
    if gas0 is None:gas0=Gas(.9,.85,.15,0.,4000.)
    if nstep<2 or not 0<a0<a1<=.2 or source_scale<0 or nmu<2 or ne<2:
        raise ValueError("invalid local continuous source configuration")
    if rr_ne_method not in ("frozen","midpoint"):
        raise ValueError("invalid RR electron centering")
    m=ns["model"]
    y=ns["nhe"]/(m.nh*5.**3)
    initial_T=gas0.thermal_energy_ev_per_h(y)
    state=Gas(**gas0.__dict__)
    photons=PhotonStock.empty()
    L={
      "source_photons_per_H":0.,
      "source_energy_eV_per_H":0.,
      "photo_events_per_H":np.zeros(3),
      "photoheat_eV_per_H":np.zeros(3),
      "RR_events_per_H":np.zeros(3),
      "RR_thermal_escape_eV_per_H":0.,
      "geometric_work_eV_per_H":0.,
      "gas_adiabatic_work_eV_per_H":0.,
      "zero_mass_packets_pruned":0,
    }
    start=time.perf_counter()
    # Fixed birth-frame BB spectrum, angular Gauss rule and threshold-split
    # energy nodes are independent of birth epoch and q. Evaluate them once.
    template=make_birth_cohort(ns,a0,q,1.0,nmu,ne) if cached_birth_spectrum else None
    xgrid=np.linspace(np.log(a0),np.log(a1),nstep+1)
    history=[]
    bind=np.array(ns["bind"],float)
    for i in range(nstep):
        left,right=float(np.exp(xgrid[i])),float(np.exp(xgrid[i+1]))
        mid=math.sqrt(left*right)
        dt=proper_dt(m,left,right,q)
        nH=m.nh/mid**3
        nHe=y*nH

        # Time-centered photon energies and gas with explicit geometry work.
        if photons.count:
            old_energy=float(np.dot(photons.photons_per_H,photons.current_energy_eV))
            photons.current_energy_eV=photons.birth_energy_eV*photon_energy_ratio(
                m,photons.birth_a,mid,q,photons.birth_mu)
            new_energy=float(np.dot(photons.photons_per_H,photons.current_energy_eV))
            L["geometric_work_eV_per_H"]+=old_energy-new_energy
        therm_before=state.thermal_energy_ev_per_h(y)
        state=Gas(state.xhi,state.xhei,state.xheii,state.xheiii,
                  state.temp_K*(left/mid)**2)
        L["gas_adiabatic_work_eV_per_H"]+=therm_before-state.thermal_energy_ev_per_h(y)
        if recombination:
            state,rr,esc=recombine_case_a(state,dt/2,nH,nHe,
                                          ne_method=rr_ne_method)
            L["RR_events_per_H"]+=rr
            L["RR_thermal_escape_eV_per_H"]+=esc

        # This full time interval's new source has a true continuous proper
        # rate; midpoint emission age represents its spectrum and redshift.
        source_count=float(source_scale*(xgrid[i+1]-xgrid[i]) *
                     m.rate(mid)/m.hubble(mid,q))
        if source_count<0 or not np.isfinite(source_count):
            raise AssertionError("nonpositive physical source")
        old_num=photons.count
        source_rate=np.zeros(old_num,dtype=float)
        if source_count:
            if template is None:
                cohort=make_birth_cohort(ns,mid,q,source_count,nmu,ne)
            else:
                cohort=PhotonStock(
                    birth_a=np.full(template.count,mid),
                    birth_mu=template.birth_mu,
                    birth_energy_eV=template.birth_energy_eV,
                    photons_per_H=source_count*template.photons_per_H,
                    current_energy_eV=template.birth_energy_eV,
                )
            photons.append(cohort)
            source_rate=np.r_[source_rate,cohort.photons_per_H/dt]
            # Do NOT inject newborn photons as an initial stock.
            photons.photons_per_H[old_num:]=0.0
            L["source_photons_per_H"]+=source_count
            L["source_energy_eV_per_H"]+=float(np.dot(
                cohort.photons_per_H,cohort.birth_energy_eV))

        if photons.count:
            E=photons.current_energy_eV
            # Sigma is independent of evolving receiver gas at fixed
            # midpoint photon energy. Cache once across predictor/corrector.
            sig=np.column_stack([verner_sigma_array(E,p) for p in ns["fit"]])
            nstart=state.proper_absorbers(nH,nHe)
            preview_lam=C*sig*nstart[None,:]
            _,preview_events,_=absorb_with_source(
                photons.photons_per_H,source_rate,preview_lam,dt/2)
            preview_heat=np.sum(preview_events*(E[:,None]-bind[None,:]),axis=0)
            gas_mid=update_gas(state,preview_events.sum(axis=0),
                               float(preview_heat.sum()),nH,nHe)
            lam=C*sig*gas_mid.proper_absorbers(nH,nHe)[None,:]
            survived,packet_events,_=absorb_with_source(
                photons.photons_per_H,source_rate,lam,dt)
            absorbed=packet_events.sum(axis=0)
            heats=np.sum(packet_events*(E[:,None]-bind[None,:]),axis=0)
            state=update_gas(state,absorbed,float(heats.sum()),nH,nHe)
            photons.photons_per_H=survived
            L["photo_events_per_H"]+=absorbed
            L["photoheat_eV_per_H"]+=heats

        if recombination:
            state,rr,esc=recombine_case_a(state,dt/2,nH,nHe,
                                           ne_method=rr_ne_method)
            L["RR_events_per_H"]+=rr
            L["RR_thermal_escape_eV_per_H"]+=esc

        if photons.count:
            before=float(np.dot(photons.photons_per_H,photons.current_energy_eV))
            photons.current_energy_eV=photons.birth_energy_eV*photon_energy_ratio(
                m,photons.birth_a,right,q,photons.birth_mu)
            after=float(np.dot(photons.photons_per_H,photons.current_energy_eV))
            L["geometric_work_eV_per_H"]+=before-after

            if exact_zero_prune:
                # Drop ONLY exactly zero stock entries; no threshold
                # approximation, so every retained science value is unchanged.
                keep=photons.photons_per_H>0.
                if not np.all(keep):
                    L["zero_mass_packets_pruned"]+=int((~keep).sum())
                    for name in ("birth_a","birth_mu","birth_energy_eV",
                                 "photons_per_H","current_energy_eV"):
                        setattr(photons,name,getattr(photons,name)[keep])

        therm_before=state.thermal_energy_ev_per_h(y)
        state=Gas(state.xhi,state.xhei,state.xheii,state.xheiii,
                  state.temp_K*(mid/right)**2)
        L["gas_adiabatic_work_eV_per_H"]+=therm_before-state.thermal_energy_ev_per_h(y)
        history.append([
            right,state.xhi,state.xhei,state.xheii,state.xheiii,
            state.temp_K,float(photons.photons_per_H.sum())])

    photons_final=float(photons.photons_per_H.sum())
    energy_final=float(np.dot(photons.photons_per_H,photons.current_energy_eV))
    photo=L["photo_events_per_H"];rr=L["RR_events_per_H"]
    thermo_final=state.thermal_energy_ev_per_h(y)
    Bphoto=float(np.dot(photo,bind));Brec=float(np.dot(rr,bind))
    balance=(L["source_energy_eV_per_H"]-energy_final
          -L["geometric_work_eV_per_H"]
          -(thermo_final-initial_T)-L["gas_adiabatic_work_eV_per_H"]
          -(Bphoto-Brec)-(Brec+L["RR_thermal_escape_eV_per_H"]))
    ledger={
       **{k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in L.items()},
       "final_photons_per_H":photons_final,
       "final_photon_energy_eV_per_H":energy_final,
       "initial_thermal_energy_eV_per_H":initial_T,
       "final_thermal_energy_eV_per_H":thermo_final,
       "photon_number_residual":float(
           L["source_photons_per_H"]-photons_final-photo.sum()),
       "local_energy_residual_eV_per_H":float(balance),
       "nuclei_He_residual":float(state.xhei+state.xheii+state.xheiii-1.),
       "charge_residual_per_H":float(state.electrons_per_h(y)-
           (1-state.xhi+y*(state.xheii+2*state.xheiii)))
    }
    return {
        "schema":"BASS_CR_C15_CONTINUOUS_SOURCE_BIANCHI_I_V1",
        "scope":"piecewise-midpoint Duhamel photon birth and chemistry, owner analytical source; no SOURCE07 spatial rays or full temperature physics",
        "q":q,"nstep":nstep,"source_scale":source_scale,
        "gas_initial":gas0.__dict__.copy(),
        "gas_final":state.__dict__.copy(),
        "wall_seconds":time.perf_counter()-start,
        "photon_packet_count":photons.count,
        "packet_bytes":photons.byte_count(),
        "history":history,"ledgers":ledger,
        "rr_midpoint":rr_ne_method,"zero_exact_prune":exact_zero_prune,
        "cached_birth_spectrum":cached_birth_spectrum,
        "scientific_gate":"EXPLORATORY_NUMERICALLY_CHECKED_NOT_EOR_ADMITTED"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--q",type=float,default=0.)
    p.add_argument("--nstep",type=int,default=32)
    p.add_argument("--source-scale",type=float,default=1.)
    p.add_argument("--no-recomb",action="store_true")
    p.add_argument("--rr-ne",choices=("frozen","midpoint"),default="midpoint")
    args=p.parse_args()
    ns=owner_namespace(args.owner)
    value=evolve_continuous(ns,args.q,args.nstep,
            source_scale=args.source_scale,
            recombination=not args.no_recomb,rr_ne_method=args.rr_ne)
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(value,indent=2)+"\n")
    print(json.dumps({
        "xHI":value["gas_final"]["xhi"],
        "HeIII":value["gas_final"]["xheiii"],
        "T_K":value["gas_final"]["temp_K"],
        "photon_stock":value["ledgers"]["final_photons_per_H"],
        "number_residual":value["ledgers"]["photon_number_residual"],
        "energy_residual_eV_per_H":value["ledgers"]["local_energy_residual_eV_per_H"],
        "seconds":value["wall_seconds"]},indent=2))
