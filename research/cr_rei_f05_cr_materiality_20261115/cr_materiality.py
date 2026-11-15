#!/usr/bin/env python3
"""Source-only CR-ON materiality FRONTIER on 184320 real REI F05 points.

Exact source crosswalk (REI367 20 fields vs WU R57 27 fields); no CR source,
no CR-ON simulation, no thermal photon or spectrum assumptions. No private
source arrays written to public outputs. See THEORY_AND_GATES.md.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,itertools,json,math,zipfile
from pathlib import Path
from typing import Iterator

HERE=Path(__file__).resolve().parent
ROOT=Path("/home/cosmosapjw")
WU=ROOT/"research_backups/WU088_HH/R57_REI_F05_NATIVE_RHS_DI_HISTORY_20261102"
WU_CSV=WU/"source_private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz"
WU_JSON=WU/"source_public/ORIGINAL_F05_4EPOCH_RHS_SCIENCE.json"
REI_ZIP=ROOT/"Dropbox/bianchi/research_backups/rei_bianchi/REI367_F05_ORIGINAL_4EPOCH_26EVENT_SOURCE_FULL_20261102.zip"
ORIGINAL_MEMBER="private_source/NEW_ORIGINAL_F05_184320_26EVENT_SOURCE_RHS.csv.gz"
SHA_WU_CSV="d8d8ce4f3fea820a3b6cfe6bd5d1c4ac48e9f160612cde0ebe00ca04f32af37e"
SHA_WU_JSON="f2adab1ce52992f3da0096ce79acb68d3c65c57f304ab8628e2156d17ffd4cde"
SHA_REI_ZIP="d6d27a7d50a6e106739f1e45e95c41b8218bccba329cd2ce9220bef2ce2543a1"
SHA_REI_MEMBER="5a1fe901809c9df2ce2f42aac81583f1021589958ec1799b07bfff6307ee3913"
REI_ORIGINAL_SOURCE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
REI_KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
PARENT="f990ed8cb66ba5687ef83fceb2699f43a2a8d964"
TICKS=(0,64,128,160)
N=46080
DT=4871848749.16828
EV_ERG=1.602176634e-12
KB_ERG_K=1.380649e-16
CHI_H_EV=13.598434599702
CSV_NAME="ORIGINAL_REI_F05_CR_MATERIALITY_FRONTIER_4_EPOCHS.csv"
ORIG_FIELDS=('node','accepted_tick','proper_time_s','N_H','N_He','N_e','T_K',
 'Bdot_net_erg_s','photo_binding_erg_s','collisional_binding_erg_s',
 'OTS_chemical_erg_s','OTS_resolved_heat_erg_s','OTS_unresolved_erg_s',
 'OTS_escaped_erg_s','primary_photoheat_erg_s','Udot_thermochemical_erg_s',
 'native_thermal_rhs_erg_s','dN_e_dt_per_s','Bdot_stoich_scaled_residual',
 'OTS_energy_scaled_residual')
DERIVED_FIELDS=("original_tick","original_proper_time_s","native_source_cells",
 "original_N_H_total","original_N_HI_total","original_neutral_H_fraction_global",
 "neutral_fraction_min","neutral_fraction_max","native_total_HII_rate_s_inv",
 "native_total_H_recomb_rate_s_inv","native_direct_H_ion_rate_s_inv",
 "derived_total_H_ion_rate_s_inv","derived_He_OTS_H_ion_rate_s_inv",
 "derived_He_OTS_fraction_of_total_H_formation",
 "CR_hazard_match_direct_H_s_inv","CR_hazard_match_all_H_formation_s_inv",
 "CR_hazard_reverse_global_HII_decline_s_inv",
 "CR_hazard_reverse_times_one_proper_tick",
 "native_gas_total_Udot_erg_s",
 "CR_heat_power_per_neutral_for_zero_global_Udot_erg_s",
 "CR_heat_per_new_ion_at_chemical_threshold_eV",
 "CR_temperature_composition_threshold_neutral_weighted_eV",
 "CR_temperature_composition_threshold_min_eV",
 "CR_temperature_composition_threshold_max_eV",
 "neutral_weighted_local_zeta_reverse_p10_s_inv",
 "neutral_weighted_local_zeta_reverse_p50_s_inv",
 "neutral_weighted_local_zeta_reverse_p90_s_inv",
 "cells_original_HII_decreasing","cells_original_HII_increasing",
 "cells_original_HII_stationary",
 "source_thermal_two_paths_max_rel_discrepancy",
 "source_thermal_two_paths_distinct_float64_cell_count")

def req(ok,code):
    if not ok:raise ValueError("CR_F05_MATERIALITY_"+code)

def sha(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def weighted_quantile(pairs:list[tuple[float,float]], frac:float)->float:
    req(len(pairs)>0 and 0<=frac<=1,"QUANTILE_DOMAIN")
    dat=sorted(pairs,key=lambda z:z[0])
    tot=math.fsum(w for _,w in dat)
    req(tot>0 and all(math.isfinite(x) and math.isfinite(w) and w>=0 for x,w in dat),
        "WEIGHTS")
    s=0.
    for x,w in dat:
        s+=w
        if s>=frac*tot:return x
    return dat[-1][0]

def load_science(path:Path)->dict:
    req(sha(path)==SHA_WU_JSON,"WU_SCIENCE_SHA")
    s=json.loads(path.read_text())
    req(s.get("original_state_source_sha256")==REI_ORIGINAL_SOURCE_SHA,"ORIGINAL_TAR_LOCK")
    req(s.get("original_kernel_sha256")==REI_KERNEL_SHA,"ORIGINAL_KERNEL_LOCK")
    req(s.get("private_original_26event_4epoch_gzip_sha256")==SHA_WU_CSV,
        "AUGMENTED_GZIP_LOCK")
    req(int(s.get("source_46080_cell_rows",-1))==N*len(TICKS),"SOURCE_ROW_COUNT")
    epoch={int(e["tick"]):e for e in s["original_epoch_results"]}
    req(set(epoch)==set(TICKS),"SOURCE_EPOCH_SET")
    return epoch

def compute(wu_csv:Path,wu_json:Path,rei_zip:Path,out:Path)->dict:
    wu_csv,wu_json,rei_zip,out=map(lambda p:Path(p).resolve(),
                                  (wu_csv,wu_json,rei_zip,out))
    req(not out.exists(),"NO_OVERWRITE")
    req(sha(wu_csv)==SHA_WU_CSV,"WU_AUGMENTED_SHA")
    req(sha(rei_zip)==SHA_REI_ZIP,"REI367_ARCHIVE_SHA")
    epoch=load_science(wu_json)
    result={t:{"nhi":[],"nh":[],"T":[],"dHII":[],"Udot":[],
               "xHI":[],"zeta_local":[],"epsilon_T":[],"time":None,
               "count_dec":0,"count_inc":0,"count_zero":0,
               "count":0,"thermal_roundoff_count":0,"thermal_max_rel":0.} for t in TICKS}
    hzip=hashlib.sha256()
    fields=None
    with zipfile.ZipFile(rei_zip) as z:
        req(z.testzip() is None,"REI_ZIP_CRC")
        # Verify original source member SHA on the compressed bytes, without
        # placing source-private 184320-row file in the public working tree.
        with z.open(ORIGINAL_MEMBER) as origin_raw:
            for b in iter(lambda:origin_raw.read(1<<20),b""):
                hzip.update(b)
        req(hzip.hexdigest()==SHA_REI_MEMBER,"REI_ORIGINAL_MEMBER_SHA")
        with z.open(ORIGINAL_MEMBER) as raw_orig:
            with gzip.GzipFile(fileobj=raw_orig) as gz_orig:
                with io.TextIOWrapper(gz_orig,encoding="utf-8",newline="") as txt_orig:
                    original=csv.DictReader(txt_orig)
                    with gzip.open(wu_csv,mode="rt",encoding="utf-8",newline="") as txt_wu:
                        augmented=csv.DictReader(txt_wu)
                        fields=list(original.fieldnames or [])
                        req(fields==list(ORIG_FIELDS),"REI367_SOURCE_COLUMNS")
                        req(list(augmented.fieldnames or [])[:len(fields)]==fields,
                            "WU_ORIGINAL_20_FIELD_ALIGNMENT")
                        rows=0
                        for r,a in itertools.zip_longest(original,augmented):
                            req(r is not None and a is not None,"SOURCE_CROSSWALK_ROW_COUNT")
                            req(all(r[f]==a[f] for f in fields),"ORIGINAL_20_FIELD_MISMATCH")
                            t=int(a["accepted_tick"])
                            req(t in result,"UNEXPECTED_EPOCH")
                            j=int(a["node"])
                            req(0<=j<N,"SOURCE_NODE_INDEX")
                            target=result[t]
                            # Original WU R57 preserves native REI367 chronological node order.
                            req(j==target["count"],"NODE_ORDER_OR_DUPLICATE")
                            target["count"]+=1
                            nh=float(a["N_H"])
                            hii=float(a["N_HII_point"])
                            nhi=nh-hii
                            ne=float(a["N_e"])
                            nhe=float(a["N_He"])
                            T=float(a["T_K"])
                            d=float(a["dN_HII_dt_per_s"])
                            Udot=float(a["native_thermal_rhs_erg_s"])
                            dNe=float(a["dN_e_dt_per_s"])
                            dHeII=float(a["dN_HeII_dt_per_s"])
                            dHeIII=float(a["dN_HeIII_dt_per_s"])
                            time=float(a["proper_time_s"])
                            req(all(math.isfinite(v) for v in (nh,hii,nhi,ne,nhe,T,d,Udot,time,
                                   dNe,dHeII,dHeIII)),"NONFINITE_ORIGINAL_SOURCE")
                            req(0<hii<nh and 0<nhi and ne>0 and nhe>0 and T>0,
                                "ORIGINAL_H_HE_GAS_CONE")
                            frac=nhi/nh
                            req(frac>128*math.ulp(1.) and frac<1,"NEUTRAL_CANCELLATION")
                            Npart=nh+nhe+ne
                            U=1.5*KB_ERG_K*T*Npart
                            req(U>0 and math.isfinite(U),"NATIVE_GAS_U")
                            # Secondary source row exact thermo-electron identities.
                            check_dne=d+dHeII+2*dHeIII
                            req(abs(check_dne-dNe)<=2e-10*max(abs(check_dne),abs(dNe),1e-200),
                                "NATIVE_ELECTRON_STOICH")
                            dlog=(Udot/U)-(dNe/Npart)
                            actual_log=float(a["dlogT_dt_per_s"])
                            req(abs(dlog-actual_log)<=2e-10*max(abs(dlog),abs(actual_log),1e-200),
                                "TOTAL_U_VS_LOGT_IDENTITY")
                            original_thermochemical=float(a["Udot_thermochemical_erg_s"])
                            thermal_rel=abs(original_thermochemical-Udot)/max(
                                abs(original_thermochemical),abs(Udot),1e-300)
                            # The two original RHS evaluation paths are numerically,
                            # not byte-, identical. REI367 reports max 7.05795e-16.
                            req(thermal_rel<=1e-15,"ORIGINAL_TOTAL_U_SOURCE_SEMANTICS")
                            target["thermal_roundoff_count"]+=int(original_thermochemical!=Udot)
                            target["thermal_max_rel"]=max(target["thermal_max_rel"],thermal_rel)
                            if target["time"] is None:target["time"]=time
                            req(abs(time-target["time"])<=1e-10*max(1.,abs(time)),
                                "PROPER_EPOCH_TIME_CONSISTENCY")
                            target["nh"].append(nh)
                            target["nhi"].append(nhi)
                            target["T"].append(T)
                            target["xHI"].append(frac)
                            target["dHII"].append(d)
                            target["Udot"].append(Udot)
                            local=max(0.,-d/nhi)
                            epsT=1.5*KB_ERG_K*T/EV_ERG
                            target["zeta_local"].append((local,nhi))
                            target["epsilon_T"].append((epsT,nhi))
                            if d<0:target["count_dec"]+=1
                            elif d>0:target["count_inc"]+=1
                            else:target["count_zero"]+=1
                            rows+=1
    req(rows==4*N,"ORIGINAL_TOTAL_SOURCE_ROWS")
    clean=[]
    for t in TICKS:
        a=result[t]
        req(a["count"]==N and a["count_dec"]+a["count_inc"]+a["count_zero"]==N,
            "PER_EPOCH_SOURCE_COVERAGE")
        expected_time=t*DT
        req(abs(a["time"]-expected_time)<=5e-14*max(1,abs(expected_time)),
            "NATIVE_PROPER_CLOCK")
        totals=epoch[t]["source_powers"]
        events=totals["nine_original_event_rates_per_s"]
        R=float(events["HII_CASE_B"])
        I_dir=float(events["HI_ION"])
        net=math.fsum(a["dHII"])
        Udot=math.fsum(a["Udot"])
        nhi=math.fsum(a["nhi"])
        nh=math.fsum(a["nh"])
        I_tot=R+net
        I_ots=I_tot-I_dir
        req(nh>nhi>0 and net<0 and Udot<0 and R>0 and I_tot>I_dir>0 and I_ots>0,
            "PHYSICAL_SOURCE_SIGN_OR_O_T_S")
        req(abs(Udot-totals["native_thermal_rhs_erg_s"])<=2e-13*abs(Udot),
            "NATIVE_REI_THERMAL_SUM")
        req(math.isfinite(I_tot/nhi),"CR_SOURCE_HAZARD")
        epsstar=(-Udot)/(-net)/EV_ERG
        zeta=(-net)/nhi
        rec={
          "original_tick":t,"original_proper_time_s":a["time"],"native_source_cells":N,
          "original_N_H_total":nh,"original_N_HI_total":nhi,
          "original_neutral_H_fraction_global":nhi/nh,
          "neutral_fraction_min":min(a["xHI"]),
          "neutral_fraction_max":max(a["xHI"]),
          "native_total_HII_rate_s_inv":net,
          "native_total_H_recomb_rate_s_inv":R,
          "native_direct_H_ion_rate_s_inv":I_dir,
          "derived_total_H_ion_rate_s_inv":I_tot,
          "derived_He_OTS_H_ion_rate_s_inv":I_ots,
          "derived_He_OTS_fraction_of_total_H_formation":I_ots/I_tot,
          "CR_hazard_match_direct_H_s_inv":I_dir/nhi,
          "CR_hazard_match_all_H_formation_s_inv":I_tot/nhi,
          "CR_hazard_reverse_global_HII_decline_s_inv":zeta,
          "CR_hazard_reverse_times_one_proper_tick":zeta*DT,
          "native_gas_total_Udot_erg_s":Udot,
          "CR_heat_power_per_neutral_for_zero_global_Udot_erg_s":(-Udot)/nhi,
          "CR_heat_per_new_ion_at_chemical_threshold_eV":epsstar,
          "CR_temperature_composition_threshold_neutral_weighted_eV":
              math.fsum(nh_i*T for T,nh_i in zip(a["T"],a["nhi"]))/nhi*
              1.5*KB_ERG_K/EV_ERG,
          "CR_temperature_composition_threshold_min_eV":
              min(q for q,w in a["epsilon_T"]),
          "CR_temperature_composition_threshold_max_eV":
              max(q for q,w in a["epsilon_T"]),
          "neutral_weighted_local_zeta_reverse_p10_s_inv":
              weighted_quantile(a["zeta_local"],.10),
          "neutral_weighted_local_zeta_reverse_p50_s_inv":
              weighted_quantile(a["zeta_local"],.50),
          "neutral_weighted_local_zeta_reverse_p90_s_inv":
              weighted_quantile(a["zeta_local"],.90),
          "cells_original_HII_decreasing":a["count_dec"],
          "cells_original_HII_increasing":a["count_inc"],
          "cells_original_HII_stationary":a["count_zero"],
          "source_thermal_two_paths_max_rel_discrepancy":a["thermal_max_rel"],
          "source_thermal_two_paths_distinct_float64_cell_count":
              a["thermal_roundoff_count"],
        }
        req(set(rec)==set(DERIVED_FIELDS),"PUBLIC_SCHEMA_MISMATCH")
        req(abs(zeta*epsstar*EV_ERG*nhi+Udot)<5e-14*abs(Udot),
            "SOURCE_DUAL_THRESHOLD_IDENTITY")
        req(zeta*DT<0.1,"FROZEN_HAZARD_IS_NOT_SMALL")
        clean.append(rec)
    req(max(x["original_N_H_total"] for x in clean)/
        min(x["original_N_H_total"] for x in clean)-1<3e-14,
        "ORIGINAL_H_NUCLEI_CONTINUITY")
    out.mkdir(parents=True)
    f=out/CSV_NAME
    with f.open("w",newline="",encoding="utf-8") as o:
        w=csv.DictWriter(o,fieldnames=DERIVED_FIELDS,lineterminator="\n")
        w.writeheader()
        w.writerows(clean)
    summary={
     "schema":"BASS_CR_REI_F05_SOURCE_NATIVE_CR_MATERIALITY_DUAL_FRONTIER_V1",
     "claim":"SOURCE_SCOPED_POINTWISE_CR_IONIZATION_HEATING_MATERIALITY_FRONTIER_ONLY",
     "source_input_rows":rows,"source_cells_per_epoch":N,
     "source_REI_PR367_ZIP_sha256":SHA_REI_ZIP,
     "source_REI367_original_20field_gzip_sha256":SHA_REI_MEMBER,
     "source_WU_R57_augmented_gzip_sha256":SHA_WU_CSV,
     "source_WU_R57_science_sha256":SHA_WU_JSON,
     "source_26event_original_kernel_sha256":REI_KERNEL_SHA,
     "source_20field_text_identical_original_REI_and_WU":"184320/184320_VERIFIED",
     "original_physical_epochs":[0,64,128,160],
     "source_assumption":"ORIGINAL_ACCEPTED_SOURCE_POINT_AT_EPOCH_NOT_CONTINUUM_ENCLOSURE",
     "zeta_definition":"EFFECTIVE_ADDITIONAL_H_IONIZATIONS_PER_NEUTRAL_H_PER_S",
     "epsilon_heat_definition":"ADDITIONAL_NET_GAS_U_PER_NET_H_ION_ERG_NOT_SOURCE_OWNED",
     "no_actual_CR_spectrum_or_flux":True,
     "no_CR_ON_history":True,
     "no_H_He_photon_transport":True,
     "not_statistical_error_bar_or_observed_rate":True,
     "no_chemical_binding_energy_double_count":True,
     "no_net_temperature_from_Udot_alone":True,
     "native_original_proper_tick_seconds":DT,
     "original_V1_last_accepted_tick":"160/131072",
     "separately_versioned_V2_161_163":"RESEARCH_ONLY_NO_V1_PROMOTION",
     "original_source_RUX11_materiality":"NOT_OFFICIALLY_COMPLETED",
     "BASS_CR_extension":"0/3_DELTA0","REI_canonical":"28/88_DELTA0",
     "REI_working":"33/88_DELTA0","REI_Fast":"4/7_DELTA0",
     "CR_OFF":True,"PRODUCTION":"HOLD","NO_SOURCE_MUTATION":True,
     "native_subagent":"NOT_RUN","distinct_author_referee":"NOT_RUN",
     "epochs":clean,"csv_sha256":sha(f)
    }
    jf=out/"SCIENCE_RESULT.json"
    jf.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--wu-augmented",type=Path,default=WU_CSV)
    p.add_argument("--wu-science",type=Path,default=WU_JSON)
    p.add_argument("--rei367-source-zip",type=Path,default=REI_ZIP)
    p.add_argument("--out",type=Path,default=HERE)
    x=p.parse_args()
    result=compute(x.wu_augmented,x.wu_science,x.rei367_source_zip,x.out)
    for e in result["epochs"]:
        print(json.dumps({"epoch":e["original_tick"],"zeta_crit":e["CR_hazard_reverse_global_HII_decline_s_inv"],
           "epsilon_star_eV":e["CR_heat_per_new_ion_at_chemical_threshold_eV"],
           "OTS_fraction":e["derived_He_OTS_fraction_of_total_H_formation"]},sort_keys=True),flush=True)
    print(json.dumps({"rows_verified":result["source_input_rows"],"csv_sha256":result["csv_sha256"],"status":result["claim"]},sort_keys=True))
