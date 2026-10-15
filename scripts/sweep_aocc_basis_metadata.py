"""Cheap, non-dynamical AOCC basis sensitivity preflight; NOT a convergence gate."""
import argparse
import json
from pathlib import Path
from cr_repro.aocc import OneElectronAOCC

def sweep(cfg):
    variants=[("baseline",{}),("ns_plus4",{"ns":int(cfg["ns"])+4}),
              ("np_plus2",{"np":int(cfg["np"])+2}),
              ("eps_max_half",{"eps_max":float(cfg["eps_max"])/2}),
              ("eps_max_double",{"eps_max":float(cfg["eps_max"])*2})]
    records=[]
    for name,delta in variants:
        p=dict(cfg,**delta)
        m=OneElectronAOCC(p)
        records.append({"variant":name,"changed":delta,"nbasis":m.nb,
                        "negative_per_center":int(sum(m.epsk<0)),
                        "nonnegative_per_center":int(sum(m.epsk>=0)),
                        "ground_Eh":float(m.groups[0]["eps"][0])})
    return {"schema":"AOCC_BASIS_METADATA_EXPLORATORY_V1",
            "not_a_capture_probability_or_convergence_test":True,
            "records":records}

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("config");ap.add_argument("--output",required=True)
    a=ap.parse_args()
    data=sweep(json.loads(Path(a.config).read_text()))
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps(data,indent=2))
