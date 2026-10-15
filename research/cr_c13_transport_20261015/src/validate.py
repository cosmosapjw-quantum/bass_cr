"""C13 scoped source transport science checks, independent QUADPACK emission."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from scipy.integrate import quad

from owner_age_bridge import owner_namespace,source_identity
from transport import integrate,alpha_owner_rr


def validate(owner:Path,output:Path) -> dict:
    ns=owner_namespace(owner);m=ns["model"]
    qcases={}
    for q in (-.01,0.,.01):
        # The emitting source kernel is integrated independently over log a.
        ref=quad(lambda u:m.rate(np.exp(u))/m.hubble(np.exp(u),q),
            np.log(.1),np.log(.11),epsabs=1e-12,epsrel=1e-12)[0]
        series=[]
        for n in (16,32,64,128):
            run=integrate(ns,q,n)
            if abs(run["ledgers"]["photon_count_residual"])>1e-10:
                raise AssertionError("photon conservation defect")
            if abs(run["ledgers"]["total_local_energy_residual_eV_per_H"])>1e-9:
                raise AssertionError("local energy ledger defect")
            series.append({
                "nsteps":n,
                "source_relative_error":float((run["ledgers"]["source_emitted_photons_per_H"]-ref)/ref),
                "xhi":run["gas_final"]["xhi"],
                "xheiii":run["gas_final"]["xheiii"],
                "temperature_K":run["gas_final"]["temp_K"],
                "wall_seconds":run["elapsed_wall_seconds"],
                "photon_conservation_residual":run["ledgers"]["photon_count_residual"],
                "energy_conservation_residual_eV_per_H":run["ledgers"]["total_local_energy_residual_eV_per_H"],
            })
        qcases[str(q)]={"exact_source_emission_per_H":float(ref),
                        "convergence":series}
        print(q,"N64 source error",series[2]["source_relative_error"],
              "xHI_128",series[3]["xhi"],"T_128",series[3]["temperature_K"],flush=True)
    # Zero-recombination isolates the photo-/geometry transport and
    # exposes which reaction closure contributes to the final result.
    zero=integrate(ns,0.,64,recombination=False)
    with_rec=integrate(ns,0.,64,recombination=True)
    q0=qcases["0.0"]["convergence"]
    orders=[]
    for i in range(2):
        e1=abs(q0[i]["xhi"]-q0[-1]["xhi"])
        e2=abs(q0[i+1]["xhi"]-q0[-1]["xhi"])
        orders.append(float(np.log2(e1/e2)))
    result={
        "schema":"BASS_CR_C13_TRANSPORT_VALIDATION_V1",
        "source_owner_sha256":source_identity(owner),
        "grackle_owner_rr_source_sha256":None,
        "run_scope":"midpoint birth, Bianchi-I packet energy redshift, proper density, evolving H/He with selected Case-A recombination; not owner SOURCE07 flux solve",
        "samples":qcases,
        "intermediate_reference_time_orders":orders,
        "no_recombination_control":{
            "without_rr":{"xHI":zero["gas_final"]["xhi"],"T":zero["gas_final"]["temp_K"]},
            "with_rr":{"xHI":with_rec["gas_final"]["xhi"],"T":with_rec["gas_final"]["temp_K"]}},
        "scientific_gate":"EXPLORATORY_PHYSICS_HOLD",
    }
    import hashlib
    rust=owner/'rust/rei_microphysics/src/igm_rates.rs'
    result["grackle_owner_rr_source_sha256"]=hashlib.sha256(rust.read_bytes()).hexdigest()
    output.parent.mkdir(exist_ok=True,parents=True)
    output.write_text(json.dumps(result,indent=2)+"\n")
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    v=p.parse_args();out=validate(v.owner,v.output)
    print("REFERENCE_ORDERS",out["intermediate_reference_time_orders"])
