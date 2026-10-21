#!/usr/bin/env python3
"""Run source-locked BASS ↔ REI Einstein/radiation hierarchy and real HHe ne replay.

The hierarchy is a LRS energy-integrated, unpolarized Thomson sub-block of the
BASS/PSTF T1,T7-9 + collision: not a replacement for E/B polarization or the
full arbitrary-Bianchi multipole tower. Source08 ne(t) is a *one-way* gas replay:
changing radiation/shear does not change this frozen ne(a) donor.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/"suppliers/bass/rei_axbi_initial_stress_20261015"))
from einstein_vlasov import KineticStressBackground,Initial,moments
from lrs_boltzmann import (SourceLock,ElectronHistory,SmoothElectronHistory,HierarchyBackground,
    SIGMA_T_CM2,GAMMA_PER_NE)

SOURCE_HEAD_BASS="fa8c60fba73ce5dd40ce47833749ae70dd0c64d7"
BASE_LOCK="46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0"
ZERO_REL="research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for buf in iter(lambda:f.read(1<<20),b""):h.update(buf)
    return h.hexdigest()

def source_lock():
    p=HERE/"suppliers/bass/rei_axbi_background_supplier_20261015/source/REI_BACKGROUND_FAMILY_LOCK.json"
    if sha(p)!=BASE_LOCK:raise RuntimeError("BASS_ORIGINAL_COSMOLOGY_SOURCE_CHANGED")
    lock=json.loads(p.read_text())
    c=lock["cosmology"];cc=lock["clock"]
    return SourceLock(
     h0=float(c["H0_per_s"]),omega_m=float(c["Omega_m"]),
     omega_r=float(c["Omega_r"]),omega_lambda=float(c["Omega_lambda"]),
     aref=float(cc["a_ref"]),aend=float(cc["a_end"]))

def actual_electrons(owner):
    from lrs_boltzmann import ElectronHistory
    p=owner/ZERO_REL
    r=json.loads((p/"COMPOSITION_RECEIPT.json").read_text())
    if r["status"]!="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION":
        raise RuntimeError("DONOR_HHE_NOT_COMPLETE")
    if r["row_counts"]["history.csv"]["composed_rows"]!=312238:
        raise RuntimeError("DONOR_WRONG_ORIGINAL_ROWS")
    hist=p/"history.csv"
    if sha(hist)!=r["output_sha256"]["history.csv"]:
        raise RuntimeError("DONOR_SOURCE_BYTES_CHANGED")
    arr=np.loadtxt(hist,delimiter=",",skiprows=1,usecols=(4,13),dtype=float)
    if arr.shape!=(312238,2):raise RuntimeError("DONOR_ELECTRON_SHAPE")
    donor=SmoothElectronHistory(arr[:,0],arr[:,1],nodes=8193)
    return donor,{"source":"frozen_zero_HHe_original_full","history_sha256":sha(hist),
            "original_rows":len(arr),"transferred_nodes":len(donor.x),
            "electron_opacity_positive_C2_log_spline":True,
            "max_relative_electron_density_interpolation_error":donor.max_relative_source_error,
            "p999_relative_electron_density_interpolation_error":donor.p999_relative_source_error,
            "source_is_test_particle_one_way":True}

def public_sigma_from_q(q):
    # q is sourced only from old BASS/REI frozen inputs; user plots and new
    # APIs expose actual physical Sigma_ref and orientation, not q_ref.
    return math.sqrt(3)*abs(q)/math.sqrt(1+q*q),int(np.sign(q))

def run(owner,L=8,rtol=3e-11,atol=8e-14):
    c=source_lock()
    donor,donor_meta=actual_electrons(owner)
    cases=[
      (0.,0.,1.,0.,False),
      (0.,+.2,1.,0.,False),
      (0.,+.2,1.,0.,True),
      (0.,-.2,1.,0.,True),
      (+.005,0.,1.,0.,False),
      (+.005,+.2,1.,0.,False),
      (+.005,+.2,1.,0.,True),
      (-.005,+.2,1.,0.,True),
      (+.005,+.2,1.,.02,True),
      (+.01,+.2,1.,0.,True),
      (+.01,+.2,.4,0.,True),
    ]
    records=[]
    spectra={}
    for k,(q,kappa,eta,nu,thomson) in enumerate(cases):
        sig,eps=public_sigma_from_q(q)
        new=HierarchyBackground(c,L,eta,kappa,sig,eps,
                ne_source=donor if thomson else None,nu_visc=nu)
        sol,wall=new.integrate(n=401,rtol=rtol,atol=atol)
        vals=[new.diagnostic(x,sol.y[:,i]) for i,x in enumerate(sol.t)]
        if any(new.minimum_angular_brightness(sol.y[:,i])<-3e-10 for i in range(0,len(sol.t),10)):
            raise RuntimeError("NEGATIVE_LEGENDRE_PHOTON_BRIGHTNESS")
        if max(abs(x["N0"]-1) for x in vals)>2e-11:
            raise RuntimeError("PHOTON_NUMBER_HIERARCHY_CONSERVATION_BROKEN")
        if any(abs(x["piR"])>x["radiation_density"]/3*(1+1e-10) for x in vals):
            raise RuntimeError("ANGULAR_RADIATION_STRESS_OUTSIDE_PHYSICAL_CONE")
        # Energy monopole driven by shear work, not elastic Thomson:
        maxwork=max(abs(((new.rhs(x,sol.y[:,i])[4]+
                     2*(vals[i]["s"]/vals[i]["H"])*vals[i]["J2"])))
                    for i,x in enumerate(sol.t))
        if maxwork>2e-11:
            raise RuntimeError("LIQUID_RADIATION_ENERGY_WORK_LEDGER")
        record={
         "id":k,"Sigma_ref":sig,"epsilon_sigma":eps,
         "initial_rad_quadrupole_kappa":kappa,
         "collisionless_radiation_fraction_eta":eta,
         "viscosity_strength_nu":nu,
         "uses_original_HHe_electrons":thomson,
         "Lmax":L,"new_source_specific_code_id":"BASS_PR159_SOURCE_LOCK_PLUS_REI_AX08_NE",
         "endpoint_a":vals[-1]["a"],"endpoint_b":float(sol.y[1,-1]),
         "endpoint_Sigma":vals[-1]["Sigma"],
         "endpoint_J0_energy":vals[-1]["J0"],
         "endpoint_J2_energy":vals[-1]["J2"],
         "endpoint_N0_photon_number":vals[-1]["N0"],
         "endpoint_N2_number_quadrupole":vals[-1]["N2"],
         "endpoint_radiation_Pi_J_m3":vals[-1]["piR"],
         "endpoint_matter_Pi_J_m3":vals[-1]["piM"],
         "endpoint_thermal_energy_J_m3":vals[-1]["thermal_density"],
         "endpoint_elapsed_proper_s":float(sol.y[0,-1]/c.href),
         "max_energy_shear_ledger_residual":maxwork,
         "max_N0_minus_one":max(abs(x["N0"]-1) for x in vals),
         "min_positive_intensity":min(new.minimum_angular_brightness(sol.y[:,i]) for i in range(0,len(sol.t),10)),
         "nfev":sol.nfev,
         "wall_s":wall,
        }
        if not thomson and nu==0 and eta==1:
            bass=KineticStressBackground(Initial(q,kappa),order=64)
            b=bass.at_a(c.aend)
            rec={
              "BASS_vendor_sha256":sha(HERE/"suppliers/bass/rei_axbi_initial_stress_20261015/einstein_vlasov.py"),
              "endpoint_b_error":record["endpoint_b"]-b["b"],
              "endpoint_energy_monopole_error":record["endpoint_J0_energy"]-b["radiation_monopole_M"],
              "endpoint_Pi_error_J_m3":record["endpoint_radiation_Pi_J_m3"]-
                b["pi_energy_over_crit_today"]*c.rhocrit_j_m3,
              "endpoint_Sigma_error":record["endpoint_Sigma"]-
                math.sqrt(3)*abs(b["s_per_s"])/b["h_per_s"],
            }
            if (abs(rec["endpoint_b_error"])>1e-10 or
                abs(rec["endpoint_energy_monopole_error"])>1e-10 or
                abs(rec["endpoint_Pi_error_J_m3"])>1e-20):
                raise RuntimeError("NOT_BASS_PR159_EINSTEIN_VLASOV_PHYSICS")
            record["independent_original_BASS_PR159"]=rec
        records.append(record)
        spectra[k]={"x":sol.t,"Y":sol.y,
                   "Sigma":np.array([v["Sigma"] for v in vals]),
                   "piR":np.array([v["piR"] for v in vals]),
                   "GammaT":np.array([v["GammaT_per_s"] for v in vals])}
    return {"schema":"rei.crossrepo.BASS_PSTF_LRS_number_energy_thomson_v1",
       "status":"SOURCE_LOCKED_COUPLED_HIERARCHY_REAL_SOURCE_CASES_VERIFIED",
       "source_scoping":{
          "bass_git_commit":SOURCE_HEAD_BASS,"original_locked_cosmology_sha256":BASE_LOCK,
          "bass_Boltzmann_spec":"PLAN-H and lowell 02 multipole hierarchy, 1D axial unpolarized E2=0 projection",
          "rei_original_electron_donor":donor_meta,
          "collision_model":"elastic Thomson unpolarized Legendre monopole-conservative, E/B polarization not yet solved",
          "ionizing_photons_in_Einstein_radiation_stress":False,
          "matter_stress":"optional conditional nu_visc parameter only, not microscopic baryon/DM closure"
       },
       "Lmax":L,"cases":records,
       "physical_status":"Einstein + massless radiation number/energy hierarchy + real REI external HHe ne(a) Thomson damping + optional phenomenological matter Pi; gas reaction feed-forward, not fully recoupled chemistry",
       "scientific_admission":"NOT_ISSUED"},spectra

def plot(results,spectra):
    fig,(ax,bx)=plt.subplots(2,1,figsize=(9,8.5),constrained_layout=True)
    for k,record in enumerate(results["cases"]):
        if record["epsilon_sigma"]!=0 and record["initial_rad_quadrupole_kappa"]==0:
            continue
        r=spectra[k]
        z=21*np.exp(-r["x"])-1
        label=f"k={record['initial_rad_quadrupole_kappa']:+.1f}, E={record['epsilon_sigma']:+d}, Thom={int(record['uses_original_HHe_electrons'])}, nu={record['viscosity_strength_nu']}"
        ax.plot(z,r["Sigma"],lw=1.1,label=label)
        bx.plot(z,r["piR"],lw=1.1,label=label)
    for a in (ax,bx):
        a.invert_xaxis();a.set_xlabel("Mean redshift");a.grid(alpha=.25);a.legend(fontsize=6)
    ax.set_ylabel("Sigma user-normalized (nonnegative)")
    bx.set_ylabel("Radiation anisotropic Pi [J/m3]")
    fig.suptitle("Source-locked BASS Einstein-Vlasov + REI AX08 electron-gated Thomson hierarchy")
    fig.savefig(HERE/"results/hierarchy_backreaction_Sigma_Pi.png",dpi=170)
    plt.close(fig)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--owner-root",required=True,type=Path)
    p.add_argument("--lmax",type=int,default=8)
    args=p.parse_args()
    start=time.perf_counter()
    res,s=run(args.owner_root,args.lmax)
    res["compute_wall_s"]=time.perf_counter()-start
    plot(res,s)
    out=HERE/"results/hierarchy_coupled_results.json"
    out.write_text(json.dumps(res,indent=2)+"\n")
    print(json.dumps({"status":res["status"],"wall_s":res["compute_wall_s"],
      "cases":[{"id":c["id"],"k":c["initial_rad_quadrupole_kappa"],
        "e":c["epsilon_sigma"],"thom":c["uses_original_HHe_electrons"],
        "nu":c["viscosity_strength_nu"],"Sigma_end":c["endpoint_Sigma"],
        "J2_end":c["endpoint_J2_energy"],"piR_end":c["endpoint_radiation_Pi_J_m3"],
        "N0_res":c["max_N0_minus_one"],"BASS_B_error":c.get("independent_original_BASS_PR159",{}).get("endpoint_b_error")}
       for c in res["cases"]]},indent=2))
