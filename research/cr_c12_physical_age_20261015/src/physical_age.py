"""Owner-bound physical-emissivity-weighted source age plus conservative local H/He bath.

IMPORTANT: Short frozen-geometry photon-reservoir surrogate, not complete
reionization RT. Historical photons are assumed unattenuated until receiver.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import argparse
import copy
import json
import time

import numpy as np
from numpy.polynomial.legendre import leggauss

from owner_age_bridge import (
    source_identity, owner_namespace, make_packets, EmissionPackets,
)

K_B_EV_PER_K = 8.617333262145e-5
C_CM_PER_S = 29979245800.0


@dataclass
class Gas:
    xhi: float = 0.7
    xhei: float = 0.6
    xheii: float = 0.35
    xheiii: float = 0.05
    temp_K: float = 1200.0

    def __post_init__(self) -> None:
        a=np.array([self.xhi, self.xhei, self.xheii, self.xheiii, self.temp_K])
        if not np.all(np.isfinite(a)) or not 0 <= self.xhi <= 1 or min(self.xhei,self.xheii,self.xheiii)<0 or self.temp_K<=0:
            raise ValueError("invalid nonnegative gas state")
        if not np.isclose(self.xhei+self.xheii+self.xheiii, 1., atol=1e-11,rtol=0):
            raise ValueError("helium fractions must sum to one")

    def electrons_per_h(self,y:float) -> float:
        return 1. - self.xhi + y*(self.xheii + 2*self.xheiii)

    def thermal_energy_ev_per_h(self,y:float) -> float:
        return 1.5*K_B_EV_PER_K*self.temp_K*(1.+y+self.electrons_per_h(y))

    def proper_absorbers(self,nH:float,nHe:float) -> np.ndarray:
        return np.array([nH*self.xhi,nHe*self.xhei,nHe*self.xheii])


def physical_age_rule(ns: dict, q: float, n_age: int) -> tuple[np.ndarray,np.ndarray]:
    """Correct proper emission per original H: rate/H d ln a at owner source ages."""
    if n_age<4:
        raise ValueError("n_age must be >=4")
    m=ns["model"]
    x,w=leggauss(n_age)
    length=np.log(.2/m.ar)
    ages=m.ar*np.exp(.5*(1+x)*length)
    weights=w * (.5*length) * np.array([
        m.rate(float(a))/m.hubble(float(a),float(q)) for a in ages])
    if not np.all(weights>0):
        raise ValueError("nonpositive source rate weights")
    return ages,weights


def positive_nullspace_reduce(original:np.ndarray, tensor:np.ndarray,
                              ntrain:int, tolerance:float=1e-10):
    """Caratheodory-style positive reduction using explicit SVD nullvectors.

    This deterministic construction avoids numerically false LP infeasibility
    from near-dependent training constraints. It is NOT an assertion of exact
    moment equality: return the measured full-row residual, reject if beyond
    the separate chosen numerical implementation tolerance.
    """
    if not (1<=ntrain<=len(tensor)):
        raise ValueError("invalid training state count")
    if np.any(original<0) or not np.isclose(np.sum(original),1.,rtol=0,atol=1e-12):
        raise ValueError("source weights must be positive and normalized")
    raw=np.concatenate([np.ones((1,len(original))),
                        *(tensor[j].T for j in range(ntrain))],axis=0)
    scales=np.maximum(np.max(np.abs(raw),axis=1),1e-30)
    A=raw/scales[:,None]
    target=A@original
    spectral=np.linalg.svd(A,compute_uv=False)
    numerical_rank=int(np.sum(spectral > spectral[0]*1e-12))
    w=original.copy()
    for _ in range(len(w)-numerical_rank):
        active=np.flatnonzero(w>0)
        if len(active)<=numerical_rank:
            break
        Vh=np.linalg.svd(A[:,active],full_matrices=True)[2]
        direction=Vh[-1]
        candidates=[]
        for sign in (-1,1):
            possible=np.flatnonzero(sign*direction>1e-14)
            if len(possible):
                # Step opposite this nonzero-direction sign, eliminating
                # the first nonnegative weight at the feasibility boundary.
                ratio=w[active][possible]/(sign*direction[possible])
                step=float(np.min(ratio))
                candidates.append((-sign*step,step))
        if not candidates:
            raise ArithmeticError("zero null direction without eliminable support")
        alpha,_=min(candidates,key=lambda pair:abs(pair[0]))
        trial=w[active]+alpha*direction
        if np.min(trial)<-1e-13:
            raise ArithmeticError("reduction broke weight positivity")
        trial[np.abs(trial)<1e-15]=0
        w[active]=np.maximum(trial,0)
        if np.count_nonzero(w>0)>=len(active):
            raise ArithmeticError("nullspace reduction failed to remove support")
    ref=np.einsum("gaf,a->gf",tensor[:ntrain],original)
    fit=np.einsum("gaf,a->gf",tensor[:ntrain],w)
    error=float(np.max(np.abs(ref-fit)/np.maximum(np.abs(ref),1e-14)))
    scaled_error=float(np.max(np.abs(A@w-target)))
    if error>tolerance or not np.isclose(np.sum(w),1.,rtol=0,atol=1e-12):
        raise ArithmeticError(f"compression residual outside numerical budget: {error:.5g}")
    return w,{"algorithm":"positive_SVD_nullspace_pruning",
        "numerical_rank":numerical_rank,"full_training_relative_error":error,
        "all_rows_scaled_residual":scaled_error,"rank_relative_cut":1e-12,
        "numeric_residual_gate":tolerance}


def emission_packets(ns: dict,q:float,n_age:int,train:tuple[Gas,...], mode:str):
    ages, wsource=physical_age_rule(ns,q,n_age)
    packets=make_packets(ns,q,ages)
    orig=wsource / np.sum(wsource)
    nH=ns["model"].nh * 5.**3
    nHe=ns["nhe"]
    method_diagnostics={"algorithm":"uncompressed"}
    if mode=="full":
        chosen=wsource
        relative_training_error=0.
    else:
        if mode not in {"one","three"}:
            raise ValueError("unknown compression mode")
        ntraining=1 if mode=="one" else 3
        gases=np.stack([x.proper_absorbers(nH,nHe) for x in train])
        tensor=packets.response(gases)
        weights,method_diagnostics=positive_nullspace_reduce(orig,tensor,ntraining)
        chosen=weights * np.sum(wsource)
        relative_training_error=method_diagnostics["full_training_relative_error"]
    if np.any(chosen<0):
        raise AssertionError("negative compression age weight")
    block_n=np.diff(np.r_[packets.age_starts,len(packets.flux)])
    if not np.isclose(float(np.sum(wsource)),float(np.sum(chosen)),rtol=2e-9,atol=0.):
        raise AssertionError("source photon mass not preserved")
    # A sparse age solution must also sparsify the physical photon packet
    # arrays. Keeping zero-weight packets would preserve science but not RAM
    # or the cost of repeated H/He chemistry updates.
    positive=np.flatnonzero(chosen>0.)
    if len(positive)<len(chosen):
        old_start=np.r_[packets.age_starts,len(packets.flux)]
        retained_parts=[np.arange(old_start[j],old_start[j+1]) for j in positive]
        keep=np.concatenate(retained_parts)
        packets.flux=packets.flux[keep]*np.repeat(chosen[positive],block_n[positive])
        packets.physical_eV=packets.physical_eV[keep]
        packets.sigma_cm2=packets.sigma_cm2[keep]
        packets.age_starts=np.r_[0,np.cumsum(block_n[positive])[:-1]]
    else:
        packets.flux *= np.repeat(chosen,block_n)
    meta={"mode":mode,"ages":ages,"raw_emission_weights":wsource,
          "compressed_weights":chosen,
          "age_nodes":n_age,"retained_age_nodes":int(np.count_nonzero(chosen>1e-9)),
          "source_photons_per_H":float(np.sum(wsource)),
          "training_relative_error":relative_training_error,
          "compression_numerics":method_diagnostics,
          "npackets":len(packets.flux),
          "packet_bytes":int(packets.flux.nbytes+packets.physical_eV.nbytes+
                packets.sigma_cm2.nbytes+packets.age_starts.nbytes)}
    return packets, meta


def absorb_species(p:EmissionPackets, photons:np.ndarray, gas:Gas,
                   dt:float, nH:float,nHe:float):
    """One conservative frozen-opacity photon step. Exact packet exponential."""
    if dt<=0 or not np.isfinite(dt):
        raise ValueError("positive finite proper step required")
    absorber=gas.proper_absorbers(nH,nHe)
    tau=dt*C_CM_PER_S*np.sum(p.sigma_cm2*absorber,axis=1)
    frac=-np.expm1(-tau)
    weighted=p.sigma_cm2*absorber
    denom=np.sum(weighted,axis=1)
    branch=np.zeros_like(weighted)
    np.divide(weighted,denom[:,None],out=branch,where=denom[:,None]>0)
    events=photons[:,None]*frac[:,None]*branch
    totals=np.sum(events,axis=0)
    heat=np.sum(events*(p.physical_eV[:,None]-p.bind_eV[None,:]),axis=0)
    survived=photons*np.exp(-tau)
    if np.any(events<0) or np.any(survived<0):
        raise AssertionError("negative photon packet event")
    return survived,totals,heat


def update_gas(g:Gas,events:np.ndarray,heat:float,nH:float,nHe:float):
    """Numerical chemistry: photon-conserving HI->HII, HeI->HeII->HeIII."""
    y=nHe/nH
    after=Gas(xhi=g.xhi-events[0],
              xhei=g.xhei-events[1]/y,
              xheii=g.xheii+(events[1]-events[2])/y,
              xheiii=g.xheiii+events[2]/y,
              temp_K=g.temp_K)
    thermal=g.thermal_energy_ev_per_h(y)+float(heat)
    after.temp_K=thermal/(1.5*K_B_EV_PER_K*(1+y+after.electrons_per_h(y)))
    after.__post_init__()
    return after


def evolve(ns:dict,p:EmissionPackets,g0:Gas,t_end_seconds:float,nsteps:int,
           method:str="midpoint") -> dict:
    """Piecewise-frozen photon opacities, conservation exact per discrete step.

    midpoint evaluates mid-step gas with a disposable half-step packet
    predictor, then performs one full exponential photon update from the
    original photons. For gas depletion use enough steps that every
    proposed state remains positive; no unphysical clipping is used.
    """
    if method not in {"frozen","midpoint"}:
        raise ValueError("unknown integrator")
    nH=ns["model"].nh*5.**3
    nHe=ns["nhe"]
    y=nHe/nH
    dt=t_end_seconds/nsteps
    g=replace(g0)
    photon=p.flux.copy()
    n_initial=float(photon.sum())
    initial_energy=float(np.dot(photon,p.physical_eV))
    initial_gas_thermal=g.thermal_energy_ev_per_h(y)
    event_cumulative=np.zeros(3)
    heat_cumulative=np.zeros(3)
    history=[]
    for k in range(nsteps):
        evaluation_gas=g
        if method=="midpoint":
            _,half_events,half_heats=absorb_species(p,photon,g,.5*dt,nH,nHe)
            evaluation_gas=update_gas(g,half_events,float(sum(half_heats)),nH,nHe)
        photon,new_events,new_heat=absorb_species(p,photon,evaluation_gas,dt,nH,nHe)
        g=update_gas(g,new_events,float(sum(new_heat)),nH,nHe)
        event_cumulative+=new_events
        heat_cumulative+=new_heat
        history.append([float((k+1)*dt),g.xhi,g.xhei,g.xheii,g.xheiii,g.temp_K])
    n_final=float(np.sum(photon))
    end_ph_energy=float(np.dot(photon,p.physical_eV))
    heat_tot=float(sum(heat_cumulative))
    binding=float(np.dot(event_cumulative,p.bind_eV))
    ledger={
        "initial_photons_per_H":n_initial,
        "final_photons_per_H":n_final,
        "absorbed_photons_per_H":event_cumulative.tolist(),
        "photoheats_eV_per_H":heat_cumulative.tolist(),
        "binding_energy_eV_per_H":binding,
        "photon_number_residual":float(n_initial-n_final-sum(event_cumulative)),
        "photon_energy_residual_eV_per_H":float(initial_energy-end_ph_energy-heat_tot-binding),
        "thermal_energy_residual_eV_per_H":float(g.thermal_energy_ev_per_h(y)-
                                   initial_gas_thermal-heat_tot),
        "hydrogen_nuclei_residual":float((g.xhi+(1-g.xhi))-1.),
        "helium_nuclei_residual":float(g.xhei+g.xheii+g.xheiii-1.),
        "charge_residual_per_H":float(g.electrons_per_h(y)-
            (1-g.xhi + y*(g.xheii+2*g.xheiii))),
    }
    return {"initial_gas":g0.__dict__.copy(),"final_gas":g.__dict__.copy(),
            "final_electrons_per_H":g.electrons_per_h(y),"method":method,
            "elapsed_s":t_end_seconds,"steps":nsteps,
            "ledger":ledger,"history":history}


def compare(root:Path,q:float=0.,n_age:int=48,total_seconds:float=8e10,steps=(4,8,16,32)):
    ns=owner_namespace(root)
    nH=ns["model"].nh*5.**3;nHe=ns["nhe"]
    initial=Gas()
    training=(initial,Gas(.25,.25,.6,.15,1500.),Gas(.95,.8,.15,.05,400.))
    out={}
    for mode in ("full","one","three"):
        t=time.perf_counter()
        packets,info=emission_packets(ns,q,n_age,training,mode)
        outcomes={}
        for method in ("frozen","midpoint"):
            for n in steps:
                run=evolve(ns,packets,initial,total_seconds,int(n),method)
                outcomes[f"{method}_{n}"]=run
        out[mode]={"meta":{k:(v.tolist() if isinstance(v,np.ndarray) else v)
                       for k,v in info.items()},
                   "runs":outcomes,"runtime_s":time.perf_counter()-t}
    # The full bath at finest midpoint discretization is an internal
    # time reference, not a cosmologically exact physical solution.
    ref=out["full"]["runs"][f"midpoint_{max(steps)}"]["final_gas"]
    for mode in out:
        for name,r in out[mode]["runs"].items():
            r["vs_full_finest_midpoint"]={
                k:float(r["final_gas"][k]-ref[k]) for k in ref}
    return {"schema":"BASS_CR_C12_PHYSICAL_AGE_IGM_SHORT_V1",
            "owner_source_hashes":source_identity(root),
            "source_age_rule":"MD14 source-rate(a)/H(a,q) d ln(a), positive GL nodes",
            "radiation_model":"unattenuated initial source reservoir; local photon absorption only",
            "geometry":"fixed receiver q/ratios during short step; owner angular Jacobian not inserted",
            "chemistry":"photoionization only, no recombinations/cooling, gas density fixed",
            "initial_state":initial.__dict__.copy(),
            "q":q,"total_seconds":total_seconds,"ages":n_age,
            "results":out,"scientific_gate":"EXPLORATORY_NOT_ADMITTED"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--n-age",type=int,default=48)
    p.add_argument("--q",type=float,default=0.)
    args=p.parse_args()
    v=compare(args.owner,args.q,args.n_age)
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(v,indent=2)+"\n")
    for mode,row in v["results"].items():
        run=row["runs"]["midpoint_32"]
        print(mode,"age",row["meta"]["retained_age_nodes"],
            "total_photons/H",row["meta"]["source_photons_per_H"],
            "ion_final",run["final_gas"],
            "N_resid",run["ledger"]["photon_number_residual"],
            "E_resid",run["ledger"]["photon_energy_residual_eV_per_H"],
            "runtime_s",row["runtime_s"])
