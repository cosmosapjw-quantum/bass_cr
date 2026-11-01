#!/usr/bin/env python3
"""Schultz et al. 2016 Table 1 actual PUBLISHED three-angle DCS samples.

Only 48 printed numerical entries at E_CM=1 eV and eight l_max values.
Do NOT interpolate three angles to create an integral cross section:
the original full 768-angle files are still missing.
All entries are f(theta)=2*pi*sin(theta)*dSigma/dOmega (a0^2 per rad).
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"PRIMARY_DCS_SCHULTZ2016_TABLE1_E1EV.csv"
OUT=HERE/"PRIMARY_DCS_SCHULTZ2016_TABLE1_SAMPLES_48.csv"
ANGLES={"forward":7.69075e-6,"mid":1.56759,"back":3.14158}
LGRID=(100,200,400,600,800,1000,1200,1400)

def source_rows():
    with SOURCE.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    if [int(r["ell_max"]) for r in rows] != list(LGRID):
        raise ValueError("unexpected original published partial-wave cutoffs")
    return [{k:(int(v) if k=="ell_max" else float(v))
             for k,v in row.items()} for row in rows]

def published_samples():
    out=[]
    for row in source_rows():
        for angle, th in ANGLES.items():
            for chan, prefix in (("elastic_distinguishable","elastic"),
                                 ("CX_distinguishable","charge_exchange")):
                value=row[prefix+"_theta_"+angle+"_a0_sq"]
                if value < 0:
                    raise ValueError("negative published angular DCS datum")
                out.append({
                  "E_cm_eV":1.,
                  "lmax":row["ell_max"],
                  "theta_label":angle,
                  "theta_rad":th,
                  "channel":chan,
                  "f_theta_preweighted_a0_sq_per_rad":value,
                  "raw_full_DCS_768_angles":False,
                  "source":"Schultz et al 2016 Table 1, E_cm=1 eV"
                })
    if len(out)!=48:
        raise ValueError("unexpected number of original published DCS points")
    return out

def summary():
    rows=source_rows()
    a,b=rows[0],rows[-1]
    c=rows[-2]
    return {
      "source":"Schultz et al. J Phys B 49 (2016) 084004 Table 1",
      "E_CM_eV":1,
      "original_published_DCS_numbers":48,
      "sampled_angles_rad":[ANGLES[k] for k in ("forward","mid","back")],
      "lmax_values":list(LGRID),
      "elastic_forward_relative_change_l100_to_1400":
           b["elastic_theta_forward_a0_sq"]/a["elastic_theta_forward_a0_sq"]-1,
      "elastic_forward_relative_change_l1200_to_1400":
           b["elastic_theta_forward_a0_sq"]/c["elastic_theta_forward_a0_sq"]-1,
      "CX_mid_relative_change_l100_to_1400":
           b["charge_exchange_theta_mid_a0_sq"]/a["charge_exchange_theta_mid_a0_sq"]-1,
      "CX_back_relative_change_l100_to_1400":
           b["charge_exchange_theta_back_a0_sq"]/a["charge_exchange_theta_back_a0_sq"]-1,
      "full_original_DCS_matrix":"NOT_RETRIEVED",
      "integral_cross_section_from_3_angles":"NOT_COMPUTED"
    }

def save():
    rows=published_samples()
    with OUT.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator=chr(10))
        w.writeheader()
        w.writerows(rows)
    return summary()

if __name__=="__main__":
    print(json.dumps(save(),sort_keys=True))
