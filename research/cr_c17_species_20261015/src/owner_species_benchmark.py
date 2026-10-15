"""Actual owner source/redshift/Verner data in a fixed-gas H/He ray-channel test.

This is a manufactured five-channel source allocation, not the true owner
SOURCE07 age-resolved ray stock. Species photoevent dynamics is checked
against an INDEPENDENT Radau integration, including threshold event splits.
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from owner_age_bridge import owner_namespace,source_identity,verner_sigma_array
from transport import photon_energy_ratio
from continuous_source import proper_dt
from endpoint_quadrature import optical_quadrature
from species_events import species_resolved_affine


def case(ns,q,nsteps=(8,16,32,64,128),a0=.1,a1=.11,outer_nodes=64,inner_nodes=48):
    model=ns["model"]
    energy_birth=np.array([14.,20.,32.,70.,90.])
    mu_birth=np.array([-1.,-.5,0.,.5,1.])
    fractions=np.asarray(ns["spec"].phi(energy_birth),float)
    fractions/=sum(fractions)
    Y=ns["nhe"]/(model.nh*125.)
    neutral=np.array([.9,Y*.85,Y*.15])

    def coeff(a):
        physical=energy_birth*photon_energy_ratio(
             model,np.full(len(energy_birth),a0),float(a),q,mu_birth)
        density=model.nh/a**3*neutral
        rate=29979245800.*np.column_stack(
            [verner_sigma_array(physical,f) for f in ns["fit"]])*density[None,:]
        source=model.rate(a)*fractions
        return model.hubble(a,q),source,rate,physical

    crossing=[]
    for eng,mu in zip(energy_birth,mu_birth):
        for threshold in (13.60,24.59,54.42):
            def g(a):
                return eng*photon_energy_ratio(model,np.array([a0]),float(a),
                    q,np.array([mu]))[0]-threshold
            if g(a0)*g(a1)<0:
                crossing.append(np.log(brentq(g,a0,a1,xtol=1e-15)))
    crossing=sorted(set(crossing))

    def ode(t,z):
        aa=float(np.exp(t))
        H,S,L,_=coeff(aa)
        N=z[:len(energy_birth)]
        dN=(S-L.sum(axis=1)*N)/H
        dE=L*N[:,None]/H
        return np.r_[dN,dE.flatten()]

    def jac(t,z):
        H,_,L,_=coeff(float(np.exp(t)))
        n=len(energy_birth)
        J=np.zeros((n+3*n,n+3*n))
        J[:n,:n]=np.diag(-L.sum(axis=1)/H)
        for i in range(n):
            for j in range(3):
                J[n+3*i+j,i]=L[i,j]/H
        return J

    sol=np.zeros(len(energy_birth)*4)
    begin=np.log(a0)
    tic=time.perf_counter()
    nf=0
    for next_time in crossing+[np.log(a1)]:
        if next_time<=begin:continue
        ref=solve_ivp(ode,(begin,next_time),sol,method="Radau",
          jac=jac,rtol=4e-11,atol=3e-15)
        if not ref.success:raise RuntimeError(ref.message)
        sol=ref.y[:,-1]
        nf+=ref.nfev
        begin=next_time
    wall_ref=time.perf_counter()-tic
    refN=sol[:len(energy_birth)]
    refE=sol[len(energy_birth):].reshape((len(energy_birth),3))
    rows=[]
    for nbase in nsteps:
        grid=np.unique(np.r_[np.linspace(np.log(a0),np.log(a1),nbase+1),crossing])
        Nold=np.zeros(len(energy_birth))
        Nnew=Nold.copy()
        Eold=np.zeros((len(energy_birth),3))
        Enew=Eold.copy()
        worst_defects={"old":0.,"birth":0.}
        total_emitted=np.zeros(len(energy_birth))
        tic=time.perf_counter()
        for t0,t1 in zip(grid[:-1],grid[1:]):
            left,right=np.exp(t0),np.exp(t1)
            dt=proper_dt(model,float(left),float(right),q)
            eps=min(1e-11,(t1-t0)*1e-6)
            alo=np.exp(t0+eps) if any(abs(t0-c)<2e-13 for c in crossing) else left
            ahi=np.exp(t1-eps) if any(abs(t1-c)<2e-13 for c in crossing) else right
            _,S0,_,_=coeff(left)
            _,S1,_,_=coeff(right)
            _,_,L0,_=coeff(alo)
            _,_,L1,_=coeff(ahi)
            trial,approx=optical_quadrature(Nold,S0,S1,L0,L1,dt)
            good,events,diagnostic=species_resolved_affine(
                Nnew,S0,S1,L0,L1,dt,outer_nodes=outer_nodes,
                inner_nodes=inner_nodes)
            Eold+=approx
            Enew+=events
            Nold=trial
            Nnew=good
            total_emitted+=.5*dt*(S0+S1)
            worst_defects["old"]=max(worst_defects["old"],
                     diagnostic["max_old_moment_relative_defect"])
            worst_defects["birth"]=max(worst_defects["birth"],
                     diagnostic["max_birth_moment_relative_defect"])
        sec=time.perf_counter()-tic
        abs_err_new=np.abs(Enew-refE)
        abs_err_old=np.abs(Eold-refE)
        total_species=refE.sum(axis=0)
        results={
            "base_intervals":nbase,
            "actual_intervals":len(grid)-1,
            "end_stock_C16":Nold.tolist(),
            "end_stock_C17":Nnew.tolist(),
            "species_events_C16":Eold.sum(axis=0).tolist(),
            "species_events_C17":Enew.sum(axis=0).tolist(),
            "ref_species_events":total_species.tolist(),
            "C16_species_max_abs_error":float(np.max(abs_err_old)),
            "C17_species_max_abs_error":float(np.max(abs_err_new)),
            "C16_species_total_max_rel_error":float(np.max(
                 abs(Eold.sum(axis=0)-total_species)/np.maximum(total_species,1e-15))),
            "C17_species_total_max_rel_error":float(np.max(
                 abs(Enew.sum(axis=0)-total_species)/np.maximum(total_species,1e-15))),
            "C16_vs_C17_same_survivor_max_abs":float(max(abs(Nnew-Nold))),
            "C16_total_photons_residual":float(max(abs(Nold+Eold.sum(axis=1)-total_emitted))),
            "C17_total_photons_residual":float(max(abs(Nnew+Enew.sum(axis=1)-total_emitted))),
            "moment_raw_relative_defect":worst_defects,
            "elapsed_s":sec
        }
        rows.append(results)
        print("q",q,"N",nbase,"old_species_rel",results["C16_species_total_max_rel_error"],
              "new_species_rel",results["C17_species_total_max_rel_error"],flush=True)
    return {"q":q,"quadrature_nodes":[outer_nodes,inner_nodes],"source":"pinned owner BB/Verner/Bianchi I with manufactured 5 channel source allocation",
       "energies_at_birth_eV":energy_birth.tolist(),
       "mu_birth":mu_birth.tolist(),
       "threshold_event_scale_factors":[float(np.exp(t)) for t in crossing],
       "reference":"separate Radau N+15 species reaction moments in ln a with event partition",
       "reference_photon_survivor":refN.tolist(),
       "reference_species_per_channel":refE.tolist(),
       "reference_species_totals":refE.sum(axis=0).tolist(),
       "reference_nfev":nf,"reference_seconds":wall_ref,
       "grid_runs":rows}

def run(root:Path):
    ns=owner_namespace(root)
    return {"schema":"C17_SOURCE_BOUND_SPECIES_EVENT_RADAU_REFERENCE_V1",
     "source_sha256":source_identity(root),
     "claim_policy":"species events time-variable opacity from independent Radau, not owner full propagated spectrum or gas evolution",
     "q_cases":[case(ns,q) for q in (-.01,0.,.01)],
     "scientific_gate":"SCOPED_H_HE_PHOTO_EVENT_VALIDATION_GLOBAL_EOR_HOLD"}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    o=ap.parse_args()
    d=run(o.owner)
    o.out.parent.mkdir(exist_ok=True,parents=True)
    o.out.write_text(json.dumps(d,indent=2)+"\n")
