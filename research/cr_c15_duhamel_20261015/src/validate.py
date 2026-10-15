"""Scoped numerical C15 assessment; never owner science admission."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from owner_age_bridge import owner_namespace,source_identity
from physical_age import Gas
from transport import integrate
from continuous_source import evolve_continuous

def summarize(r):
    l=r["ledgers"]
    assert abs(l["photon_number_residual"])<1e-11
    assert abs(l["local_energy_residual_eV_per_H"])<1e-10
    return {"n":r["nstep"],"xHI":r["gas_final"]["xhi"],
            "xHeIII":r["gas_final"]["xheiii"],"T":r["gas_final"]["temp_K"],
            "photons":l["final_photons_per_H"],"energy_res":l["local_energy_residual_eV_per_H"],
            "source":l["source_photons_per_H"],"events":l["photo_events_per_H"],
            "packets":r["photon_packet_count"],"bytes":r["packet_bytes"],
            "seconds":r["wall_seconds"]}

def orders(v):
    d=np.abs(np.diff(np.asarray(v,float)))
    return [float(np.log2(d[i]/d[i+1])) if d[i+1]>0 else None
            for i in range(len(d)-1)]

def validate(root):
    ns=owner_namespace(root);m=ns["model"];spec=ns["spec"]
    cases={}
    definitions={
      "weak_below5500":(.05,True,4000.),
      "strong_cross5500":(1.,True,4000.),
      "hot_above5500":(1.,True,9000.),
      "strong_no_rr":(1.,False,4000.),
    }
    for label,(scale,recomb,T) in definitions.items():
        rows=[summarize(evolve_continuous(ns,0.,n,source_scale=scale,
                 recombination=recomb,gas0=Gas(.9,.85,.15,0.,T)))
              for n in (16,32,64,128,256)]
        cases[label]={"source_scale":scale,"recombination":recomb,
             "initial_T":T,"runs":rows,
             "orders_xHI":orders([r["xHI"] for r in rows]),
             "orders_T":orders([r["T"] for r in rows]),
             "orders_survivor":orders([r["photons"] for r in rows])}
        print(label,"xHI orders",cases[label]["orders_xHI"],flush=True)
    qcases={}
    for q in (-.01,0.,.01):
        qcases[str(q)]=[summarize(evolve_continuous(ns,q,n))
                         for n in (16,32,64,128)]
    old=integrate(ns,0.,32,rr_ne_method="midpoint")
    new=evolve_continuous(ns,0.,32)
    exact_n=quad(lambda u:m.rate(np.exp(u))/m.hubble(np.exp(u),0),
          np.log(.1),np.log(.11),epsrel=1e-12)[0]
    mean_e=quad(lambda E:E*float(spec.phi(E)),13.6,100.,epsrel=1e-12)[0]/quad(
          lambda E:float(spec.phi(E)),13.6,100.,epsrel=1e-12)[0]
    exact_e=mean_e/.11*quad(lambda u:np.exp(u)*m.rate(np.exp(u))/m.hubble(np.exp(u),0),
          np.log(.1),np.log(.11),epsrel=1e-12)[0]
    no_opacity=[]
    for n in (16,32,64,128):
        r=evolve_continuous(ns,0.,n,gas0=Gas(0,0,0,1,4000.),recombination=False)
        no_opacity.append({"n":n,"delta_N":r["ledgers"]["final_photons_per_H"]-exact_n,
               "delta_E_eV":r["ledgers"]["final_photon_energy_eV_per_H"]-exact_e})
    return {"schema":"BASS_CR_C15_SCOPED_CONTINUOUS_SOURCE_V1",
            "owner_sha256":source_identity(root),
            "owner_zero_opacity_reference":{"emitted_photons_per_H":exact_n,
                       "mean_emitted_energy_eV":mean_e,"energy_at_end_eV_per_H":exact_e},
            "zero_opacity_checks":no_opacity,
            "controlled_q_sweep":qcases,
            "controlled_gas_convergence":cases,
            "C13_C15_photon_stock_n32":{"old_midpoint":old["ledgers"]["final_photons_per_H"],
                       "new_continuous":new["ledgers"]["final_photons_per_H"]},
            "conclusions":{"gas_2nd_order":"conditional without coefficient kink",
                   "surviving_photon_order":"first-order-like in stiff tested range",
                   "true_ray_transport":"NOT_RUN",
                   "full_reionization_admission":"HOLD"}}

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--owner",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    opt=a.parse_args()
    record=validate(opt.owner)
    opt.out.parent.mkdir(exist_ok=True,parents=True)
    opt.out.write_text(json.dumps(record,indent=2)+"\n")
    print("C15_OWNER_VALIDATION_SAVED",opt.out)