"""Finite scope scientific output: source rate/age, energy and dynamic time checks."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import numpy as np

from owner_age_bridge import owner_namespace,make_packets,source_identity
from physical_age import Gas,physical_age_rule,emission_packets,evolve
from continuum_oracle import reference_eight
from independent_ode import solve_reference


def validate(root:Path) -> dict:
    ns=owner_namespace(root)
    rates={}
    for q in (-.01,0.,.01):
        numbers=[]
        for n in (16,32,64):
            age,w=physical_age_rule(ns,q,n)
            numbers.append({"n_age":n,"emission_photons_per_H":float(w.sum())})
        quadpack=float(ns["model"].total_emitted(q))
        rates[str(q)]={"gauss_integrals":numbers,"owner_quadpack":quadpack,
             "max_relative_difference":max(abs(v["emission_photons_per_H"]-quadpack)/quadpack for v in numbers)}
    # Independently integrate across emitted energy for three distinct histories
    age=np.array([.08,.14,.2])
    nH=ns["model"].nh*125
    nHe=ns["nhe"]
    gas=np.array([.7*nH,.6*nHe,.35*nHe])
    packets=make_packets(ns,.01,age)
    actual=packets.response(gas[None,:])[0]
    oracle=[]
    for a,approx in zip(age,actual):
        reference=reference_eight(ns,float(a),.01,gas)
        oracle.append({"age_scale_factor":float(a),
            "max_relative_difference":float(np.max(abs(approx-reference)/np.maximum(abs(reference),1e-14))),
            "max_absolute_difference":float(np.max(abs(approx-reference))),
            "reference_HeII_events":float(reference[4]),
            "reference_HeII_heat_eV":float(reference[7])})
    initial=Gas()
    train=(initial,Gas(.25,.25,.6,.15,1500.),Gas(.95,.8,.15,.05,400.))
    compressed,meta=emission_packets(ns,0.,48,train,"one")
    ode=solve_reference(ns,compressed,initial,8e10,rtol=5e-11,atol=5e-13)
    time_errors={}
    for method in ("frozen","midpoint"):
        group=[]
        for n in (8,16,32,64,128):
            out=evolve(ns,compressed,initial,8e10,n,method)
            group.append({
                "nstep":n,
                "error_xHI":float(out["final_gas"]["xhi"]-ode["final_gas"]["xhi"]),
                "error_temperature_K":float(out["final_gas"]["temp_K"]-ode["final_gas"]["temp_K"]),
                "photon_number_ledger":out["ledger"]["photon_number_residual"],
                "energy_ledger_eV_per_H":out["ledger"]["photon_energy_residual_eV_per_H"]})
        group=[dict(v, observed_order_to_next=float(
            np.log2(abs(v["error_xHI"])/abs(group[i+1]["error_xHI"])))
              if i+1<len(group) else v) for i,v in enumerate(group)]
        time_errors[method]=group
    # Width of age integration versus its own increasing quadrature resolution
    resolution={}
    for q in (-.01,0.,.01):
        group=[]
        for n in (32,48,96):
            pack,meta=emission_packets(ns,q,n,train,"full")
            out=evolve(ns,pack,initial,8e10,64,"midpoint")
            group.append({"age_count":n,"xhi":out["final_gas"]["xhi"],
                   "xheiii":out["final_gas"]["xheiii"],
                   "temperature_K":out["final_gas"]["temp_K"]})
        resolution[str(q)]=group
    return {"schema":"BASS_CR_C12_VALIDATION_V1",
            "source_sha256":source_identity(root),
            "source_weight_validation":rates,
            "independent_energy_QUADPACK":oracle,
            "time_reference_DOP853":ode,
            "time_convergence":time_errors,
            "source_age_quadrature_refinement":resolution,
            "metadata":{"clock":"proper seconds","energy":"physical eV",
              "source":"MD14-inspired configured rate/H d ln a from owner code",
              "gas":"fixed proper n_H and n_He, dynamic ionization fractions",
              "temperature":"monatomic ideal gas heat capacity, photoheating only"},
            "science_status":"SCOPED_CHECKED_NOT_COMPLETE_REI_BIANCHI"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    d=validate(args.owner)
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(d,indent=2)+"\n")
    print("source age quadrature max relative error",max(x["max_relative_difference"]
          for x in d["source_weight_validation"].values()))
    print("source emitted-energy quadrature max relative error",max(x["max_relative_difference"]
          for x in d["independent_energy_QUADPACK"]))
    for k,rows in d["time_convergence"].items():
        print(k,"observed orders",[round(r["observed_order_to_next"],3) for r in rows[:-1]])
