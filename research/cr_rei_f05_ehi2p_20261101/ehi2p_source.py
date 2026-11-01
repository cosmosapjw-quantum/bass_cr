#!/usr/bin/env python3
"""Original REI-F05 t160 electron-H(1s)->H(2p) source, only supported 5k..20k K.
Physical photon source conditional on Maxwellian Te=Tgas and HI 1s saturation.
No extra original REI event, actual Ly-alpha occupation, or t161 acceptance.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import sys
from pathlib import Path
from functools import lru_cache

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"cr_rei_f05_caseb_lya_20261101"
sys.path.insert(0,str(PARENT))
import native_caseb_lya as orig

DATAFILE="ORIGINAL_REI_F05_EHI_2P_COLLISION_12528.csv.gz"
PARENT_CSV=PARENT/orig.DATAFILE
PARENT_SHA="5aa85017b9bebb11822aca4780e9c3c248aadb87f8175575f1d8f8fd8821c154"
KNOTS=((5000.,.416),(10000.,.472),(15000.,.528),(20000.,.585))
E12_EV=10.198835887565243
KB_EV_K=8.617333262145e-5
A21=6.265e8
G1,G2=2.,6.
CM3_RATE_CONST=8.629e-6
SOURCE_N=46080
FIELDS=("node","upsilon_1s2p_interp","q12_cm3_s","q21_cm3_s",
        "excitation_s_inv_lower","excitation_s_inv_mid","excitation_s_inv_upper",
        "two_level_radiative_branch_lower","two_level_radiative_branch_mid",
        "produced_lya_s_inv_lower","produced_lya_s_inv_mid","produced_lya_s_inv_upper",
        "caseb_lya_s_inv_mid","excitation_over_caseb_lya_mid",
        "produced_over_caseb_lya_mid")

def ensure(condition, message):
    if not condition:
        raise ValueError(message)

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for part in iter(lambda:f.read(1<<20),b""):
            h.update(part)
    return h.hexdigest()

def upsilon(T):
    T=float(T)
    if not math.isfinite(T) or not KNOTS[0][0]<=T<=KNOTS[-1][0]:
        raise ValueError("UPSILON_OUTSIDE_TABULATED_DOMAIN")
    for (ta,ya),(tb,yb) in zip(KNOTS,KNOTS[1:]):
        if ta<=T<=tb:
            return ya+(yb-ya)*(T-ta)/(tb-ta)
    raise ValueError("UPSILON_NO_SEGMENT")

def q_exc(T):
    return CM3_RATE_CONST*upsilon(T)*math.exp(-E12_EV/(KB_EV_K*T))/(G1*math.sqrt(T))

def q_deexc(T):
    return CM3_RATE_CONST*upsilon(T)/(G2*math.sqrt(T))

def cell_excitation_rate(N_HI, ne_cm3, T, f1s=1.0):
    ensure(0<=f1s<=1 and N_HI>=0 and ne_cm3>=0 and
           math.isfinite(N_HI) and math.isfinite(ne_cm3),
           'INVALID_GROUND_FRACTION_OR_DENSITY')
    return N_HI*ne_cm3*q_exc(T)*f1s

# Rigorous upper on q21 for any 5000-20000K, though not tight:
Q21_GLOBAL_UPPER=CM3_RATE_CONST*max(y for t,y in KNOTS)/(G2*math.sqrt(KNOTS[0][0]))

@lru_cache(maxsize=1)
def old_source():
    ensure(PARENT_CSV.is_file() and sha(PARENT_CSV)==PARENT_SHA,"PARENT_CASEB_SHA_MISMATCH")
    with gzip.open(PARENT_CSV,"rt",encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    ensure(len(rows)==SOURCE_N and all(int(r["node"])==i for i,r in enumerate(rows)),
           "PARENT_CASEB_SOURCE_NODE_IDENTITY")
    return rows

def calculate():
    ensure(sha(orig.PREVIEW)==orig.LOCKS["preview"],"ORIGINAL_PRIVATE_SOURCE_SHA")
    src=orig.read_csv(orig.PREVIEW,orig.LOCKS["preview"])
    old=old_source()
    geo=orig.native()  # independent original-owner proper V, SHA locked original physics
    ensure(len(src)==SOURCE_N and len(geo["vol"])==SOURCE_N,"ORIGINAL_VOLUME_NODE_COUNT")
    counts={"supported":0,"cold":0,"hot":0,"boundary":0}
    neutral_weights={x:[] for x in counts}
    rate_low,rate_mid,rate_up=[],[],[]
    emitted_low,emitted_mid,emitted_up=[],[],[]
    original_caseb_supported=[]
    rows=[]; max_quench=0.; ne_parity=0.; max_ratio_residual=0.
    for i,(s,o) in enumerate(zip(src,old)):
        ensure(int(s["node"])==i and int(o["node"])==i,"SOURCE_ORDER")
        Tl=float(s["tick160_Tgas_K_lower"]); Tu=float(s["tick160_Tgas_K_upper"])
        xl=float(s["tick160_xHII_lower"]);xu=float(s["tick160_xHII_upper"])
        NHlo=float(s["source_H_nuclei_N_lower"]);NHhi=float(s["source_H_nuclei_N_upper"])
        Nelo=float(s["tick160_electron_count_N_lower"]);Nehi=float(s["tick160_electron_count_N_upper"])
        ensure(0<Tl<=Tu and 0<xl<=xu<1 and 0<NHlo<=NHhi and 0<Nelo<=Nehi,"NATIVE_STATE_CONE")
        nHImid=(NHlo+NHhi)*.5*(1.-(xl+xu)*.5)
        if Tl>=5000 and Tu<=20000:
            category="supported"
        elif Tu<5000: category="cold"
        elif Tl>20000: category="hot"
        else: category="boundary"
        counts[category]+=1
        neutral_weights[category].append(nHImid)
        if category!="supported":continue
        V=float(geo["vol"][i])
        ensure(math.isfinite(V) and V>0,"ORIGINAL_POSITIVE_PROPER_VOLUME")
        ensure(abs(float(geo["h"][i]) / ((NHlo+NHhi)*.5)-1)<1.5e-12,"ORIGINAL_H_NUCLEI_IDENTITY")
        ne=(Nelo+Nehi)*.5/V
        ne_saved=float(o["ne_cm_minus3_mid"])
        ne_parity=max(ne_parity,abs(ne/ne_saved-1.))
        Tmid=(Tl+Tu)*.5; qlo=q_exc(Tl);qmid=q_exc(Tmid);qup=q_exc(Tu)
        ensure(0<qlo<=qmid<=qup,"Q_EXC_INTERVAL_MONOTONICITY")
        rlo=cell_excitation_rate(NHlo*(1-xu),Nelo/V,Tl)
        rmid=cell_excitation_rate(nHImid,ne,Tmid)
        rup=cell_excitation_rate(NHhi*(1-xl),Nehi/V,Tu)
        ensure(0<=rlo<=rmid<=rup and math.isfinite(rmid),"SOURCE_COLLISION_INTERVAL")
        q21=q_deexc(Tmid)
        branch=A21/(A21+ne*q21)
        # n_e*q21/A21~1e-19: binary64 would round true branch below 1 to 1.
        # One-ulp outward downward step prevents a falsely exact lower bound.
        branchlo=math.nextafter(A21/(A21+(Nehi/V)*Q21_GLOBAL_UPPER),0.0)
        ensure(0<branchlo<=branch<=1,"QUENCH_INTERVAL")
        emissionlo=rlo*branchlo;emissionmid=rmid*branch;emissionup=rup
        recmid=float(o["conditional_Lya_s_minus1_mid"])
        ensure(recmid>0,"CASEB_COMPARISON_POSITIVE")
        rate_ratio=rmid/recmid
        ref_ratio=((1-(xl+xu)*.5)/((xl+xu)*.5)*qmid/
                   (float(orig.alphaB(Tmid))*float(orig.pB_fit(Tmid))))
        max_ratio_residual=max(max_ratio_residual,abs(rate_ratio/ref_ratio-1))
        max_quench=max(max_quench,ne*q21/A21)
        rate_low.append(rlo);rate_mid.append(rmid);rate_up.append(rup)
        emitted_low.append(emissionlo);emitted_mid.append(emissionmid);emitted_up.append(emissionup)
        original_caseb_supported.append(recmid)
        rows.append((i,upsilon(Tmid),qmid,q21,rlo,rmid,rup,
                     branchlo,branch,emissionlo,emissionmid,emissionup,
                     recmid,rate_ratio,emissionmid/recmid))
    ensure(sum(counts.values())==SOURCE_N and counts["supported"]==len(rows),"DOMAIN_PARTITION")
    neutral={k:math.fsum(v) for k,v in neutral_weights.items()}
    def S(arr):return math.fsum(arr)
    partial=S(rate_mid); rec=S(original_caseb_supported)
    ensure(partial>0 and rec>0 and len(rows)>0,"NO_SUPPORTED_PHYSICS")
    ensure(ne_parity<3e-13 and max_ratio_residual<3e-12,"INDEPENDENT_ORIGINAL_CASEB_CROSSWALK")
    result={
        "unit":"REI_F05_T160_ELECTRON_HI_1S_TO_2P_PHYSICAL_SOURCE",
        "original_cells":SOURCE_N,"source_supported_cells":len(rows),
        "source_unsupported_cold_cells":counts["cold"],
        "source_unsupported_hot_cells":counts["hot"],
        "source_unsupported_boundary_cells":counts["boundary"],
        "source_supported_neutral_H_fraction":neutral["supported"]/S(neutral.values()),
        "table_T_domain_K":[5000,20000],
        "Upsilon_original_published_knots":[list(x) for x in KNOTS],
        "interpolation":"linear_Upsilon_MODEL_not_original_continuous_data",
        "original_private_F05_source_SHA256":orig.LOCKS["preview"],
        "original_REI_owner_HEAD":orig.LOCKS["owner_git"],
        "parent_CaseB_derived_CSV_SHA256":PARENT_SHA,
        "original_last_accepted_tick":160,"nonaccepted_candidate_tick":161,
        "electron_temperature":"Te_equals_original_Tgas_ASSUMED",
        "HI_1s_fraction":"f1s_equals_1_saturation_model_NOT_native_measured",
        "Maxwellian_electrons":"ASSUMED_not_independently_evolved",
        "source_excitation_s_inv_lower":S(rate_low),
        "source_excitation_s_inv_mid":partial,
        "source_excitation_s_inv_upper":S(rate_up),
        "two_level_prompt_Lya_s_inv_lower":S(emitted_low),
        "two_level_prompt_Lya_s_inv_mid":S(emitted_mid),
        "two_level_prompt_Lya_s_inv_upper":S(emitted_up),
        "same_supported_cells_caseB_Lya_s_inv_mid":rec,
        "excitation_over_same_domain_caseB":partial/rec,
        "prompt_Lya_over_same_domain_caseB":S(emitted_mid)/rec,
        "source_limited_collisional_excitation_energy_erg_s":partial*E12_EV*1.602176634e-12,
        "maximum_ne_q21_over_A21":max_quench,
        "original_parent_ne_density_max_relative_residual":ne_parity,
        "local_ratio_independent_cancel_max_relative_residual":max_ratio_residual,
        "NOT_computed_outside_tabulated_temperature_domain":True,
        "NOT_an_integrated_true_Lya_source_or_full_transfer":True,
        "NOT_actual_line_photon_field_or_escaped_luminosity":True,
        "NOT_independent_electron_temperature_or_1s_fraction":True,
        "REI_central_DAG":"28/88_REPORTED_DELTA0",
        "REI_working_DAG":"33/88_REPORTED_DELTA0",
        "BASS_CR_extension_DAG":"0/3_DELTA0",
        "CR_OFF_unchanged":True,"NO_REI_MUTATION":True,
        "NO_FORCE_PUSH":True,"NO_MERGE":True,
        "PRODUCTION":"HOLD","native_subagent":"NOT_RUN",
        "distinct_author_referee":"NOT_RUN"}
    return rows,result

def generate(out=HERE):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows,meta=calculate()
    dest=out/DATAFILE
    with dest.open("wb") as f:
        with gzip.GzipFile(filename="",fileobj=f,mode="wb",mtime=0,compresslevel=9) as g:
            with io.TextIOWrapper(g,encoding="utf-8",newline="") as txt:
                w=csv.writer(txt,lineterminator="\n")
                w.writerow(FIELDS)
                for row in rows:w.writerow(row)
    result=out/"RESULT.json"
    result.write_text(json.dumps(meta,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return (dest,result),meta

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=HERE)
    args=ap.parse_args()
    output,result=generate(args.out)
    print(json.dumps({"result":result,"sha256":{p.name:sha(p) for p in output}},
                     indent=2,sort_keys=True))
