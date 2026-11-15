#!/usr/bin/env python3
"""Independent stdlib-only source scientific audit of public four-row CR frontier.

Does not import cr_materiality.py. Re-reads original private source bytes.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,itertools,json,math,zipfile
from pathlib import Path
BASE=Path("/home/cosmosapjw")
WU=BASE/"research_backups/WU088_HH/R57_REI_F05_NATIVE_RHS_DI_HISTORY_20261102"
ZIP=BASE/"Dropbox/bianchi/research_backups/rei_bianchi/REI367_F05_ORIGINAL_4EPOCH_26EVENT_SOURCE_FULL_20261102.zip"
GZ=WU/"source_private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz"
RATES=WU/"source_public/ORIGINAL_F05_4EPOCH_RHS_SCIENCE.json"
MEMBER="private_source/NEW_ORIGINAL_F05_184320_26EVENT_SOURCE_RHS.csv.gz"
SHA_ZIP="d6d27a7d50a6e106739f1e45e95c41b8218bccba329cd2ce9220bef2ce2543a1"
SHA_WU="d8d8ce4f3fea820a3b6cfe6bd5d1c4ac48e9f160612cde0ebe00ca04f32af37e"
SHA_SCI="f2adab1ce52992f3da0096ce79acb68d3c65c57f304ab8628e2156d17ffd4cde"
EV=1.602176634e-12
N=46080
TICKS=(0,64,128,160)

def require(ok,label):
    if not ok:raise ValueError("CR_MATERIALITY_AUDITOR_"+label)
def hash_file(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for x in iter(lambda:f.read(1048576),b""):h.update(x)
    return h.hexdigest()
def relative(a,b):
    return abs(a-b)/max(abs(a),abs(b),1e-300)
def run(source_zip,wu_source,wu_science,result_json,out):
    source_zip,wu_source,wu_science,result_json,out=map(Path,
                (source_zip,wu_source,wu_science,result_json,out))
    require(hash_file(source_zip)==SHA_ZIP,"ORIGINAL_REI367_ZIP_SHA")
    require(hash_file(wu_source)==SHA_WU,"ORIGINAL_WU_27FIELD_SHA")
    require(hash_file(wu_science)==SHA_SCI,"ORIGINAL_NINE_RATE_SHA")
    source=json.loads(wu_science.read_text())
    published=json.loads(result_json.read_text())
    require(published["source_20field_text_identical_original_REI_and_WU"]==
            "184320/184320_VERIFIED","PUBLIC_SOURCE_CROSSWALK_CONTRACT")
    by_tick={x["original_tick"]:x for x in published["epochs"]}
    rates={x["tick"]:x["source_powers"] for x in source["original_epoch_results"]}
    totals={t:{"nhi":[],"dHII":[],"Udot":[],"count":0,"neutral_bad":0,
               "temperature_bad":0,"max_u_rel":0.} for t in TICKS}
    read_rows=0;original_matches=0
    with zipfile.ZipFile(source_zip) as z:
        with z.open(MEMBER) as raw:
            with gzip.GzipFile(fileobj=raw) as deco:
                with io.TextIOWrapper(deco,encoding="utf-8",newline="") as org:
                    orig=csv.DictReader(org)
                    with gzip.open(wu_source,"rt",encoding="utf-8",newline="") as f:
                        aug=csv.DictReader(f)
                        require(list(aug.fieldnames or [])[:20]==orig.fieldnames,
                                "FIELD_PROVENANCE")
                        for o,w in itertools.zip_longest(orig,aug):
                            require(o is not None and w is not None,"SOURCE_COUNT")
                            for name in orig.fieldnames:
                                require(o[name]==w[name],"ORIGINAL_BYTE_TEXT_COLUMN")
                            original_matches+=1
                            tick=int(w["accepted_tick"]);t=totals[tick]
                            neutral=float(w["N_H"])-float(w["N_HII_point"])
                            if neutral<=0:t["neutral_bad"]+=1
                            temp=float(w["T_K"])
                            if temp<=0:t["temperature_bad"]+=1
                            t["nhi"].append(neutral)
                            t["dHII"].append(float(w["dN_HII_dt_per_s"]))
                            u=float(w["native_thermal_rhs_erg_s"])
                            t["Udot"].append(u)
                            t["max_u_rel"]=max(t["max_u_rel"],relative(
                                 u,float(w["Udot_thermochemical_erg_s"])))
                            t["count"]+=1
                            read_rows+=1
    require(read_rows==184320 and original_matches==184320,"ALL_ROWS")
    report=[]
    for tick in TICKS:
        b=totals[tick];p=by_tick[tick]
        require(b["count"]==N and b["neutral_bad"]==0 and b["temperature_bad"]==0,
                "POSITIVE_SOURCE")
        nhi=math.fsum(b["nhi"]);d=math.fsum(b["dHII"]);U=math.fsum(b["Udot"])
        r_H=float(rates[tick]["nine_original_event_rates_per_s"]["HII_CASE_B"])
        direct=float(rates[tick]["nine_original_event_rates_per_s"]["HI_ION"])
        total_ion=r_H+d
        ots=total_ion-direct
        require(ots>=0 and d<0 and U<0 and nhi>0,"SIGN_CONE")
        expected={
            "original_N_HI_total":nhi,
            "native_total_HII_rate_s_inv":d,
            "native_total_H_recomb_rate_s_inv":r_H,
            "native_direct_H_ion_rate_s_inv":direct,
            "derived_total_H_ion_rate_s_inv":total_ion,
            "derived_He_OTS_H_ion_rate_s_inv":ots,
            "native_gas_total_Udot_erg_s":U,
            "CR_hazard_reverse_global_HII_decline_s_inv":-d/nhi,
            "CR_hazard_match_all_H_formation_s_inv":total_ion/nhi,
            "CR_heat_per_new_ion_at_chemical_threshold_eV":U/d/EV,
            "CR_heat_power_per_neutral_for_zero_global_Udot_erg_s":-U/nhi,
            "derived_He_OTS_fraction_of_total_H_formation":ots/total_ion,
        }
        for name,v in expected.items():
            require(relative(v,float(p[name]))<3e-14,"INDEPENDENT_AGGREGATE_"+name)
        require(relative(b["max_u_rel"],p["source_thermal_two_paths_max_rel_discrepancy"])<1e-14,
                "TWO_ORIGINAL_THERMAL_CALCULATIONS")
        report.append({"tick":tick,"source_rows":N,"source_neutral_H_atoms":nhi,
            "source_HII_signed_rate":d,"source_Udot_total_erg_s":U,
            "source_He_OTS_fraction":ots/total_ion,
            "independent_zeta_chem_s_inv":-d/nhi,
            "independent_epsilon_star_eV":U/d/EV,
            "source_thermal_float64_max_relative_difference":b["max_u_rel"],
            "source_consistency":"PASS"})
    result={"schema":"BASS_CR_CR_MATERIALITY_INDEPENDENT_ORIGINAL_SOURCE_AUDIT_V1",
       "original_source_rows_compared_text_identically":original_matches,
       "original_original_data_sets":1,
       "source_REI367_zip_sha256":SHA_ZIP,"source_WU_R57_gzip_sha256":SHA_WU,
       "source_WU_R57_science_sha256":SHA_SCI,"epoch_audit":report,
       "all_original_source_checks":"PASS","claim":"SOURCE_SCOPED_DIAGNOSTIC",
       "independent_implementation":"STDLIB_SEPARATE_NO_IMPORT"}
    require(not out.exists(),"NO_AUDIT_OVERWRITE")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-zip",type=Path,default=ZIP)
    p.add_argument("--wu-csv",type=Path,default=GZ)
    p.add_argument("--wu-science",type=Path,default=RATES)
    p.add_argument("--science-result",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    res=run(a.original_zip,a.wu_csv,a.wu_science,a.science_result,a.out)
    print(json.dumps({"source_rows":res["original_source_rows_compared_text_identically"],"status":res["all_original_source_checks"]},sort_keys=True))
