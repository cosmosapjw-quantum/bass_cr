#!/usr/bin/env python3
"""Original REI F05 H excitation cooling partition, source-bound, nonproduction.

DO NOT add the source 2p cooling to the already-present legacy H excitation
term or replace the whole legacy term with 2p alone.  This calculates the
existing source-local sector overlap, not an evolved REI trajectory.
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

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"cr_rei_f05_ehi2p_20261101"
sys.path.insert(0,str(PARENT))
import ehi2p_source as two_p

ORIG=two_p.orig
PUBLIC_2P=PARENT/two_p.DATAFILE
SOURCE_SHA="09c564df9400b171617ce5006b2c7eee94085f8d321f8d41648fc9456cbd1628"
N=12528
EV_ERG=1.602176634e-12
KB_ERG=1.380649e-16
E12_ERG=two_p.E12_EV*EV_ERG
OUT="ORIGINAL_REI_F05_2P_LEGACY_COOLING_PARTITION_12528.csv.gz"
COLUMNS=("node","legacy_exc_erg_s_mid","two_p_exc_erg_s_mid",
         "other_exc_residual_erg_s_mid","two_p_over_legacy_mid",
         "two_p_over_legacy_lower","two_p_over_legacy_upper",
         "epsilon_two_p_lower","epsilon_two_p_mid","epsilon_two_p_upper",
         "epsilon_legacy_mid",
         "two_p_over_native_robust_gt_0p1","two_p_over_native_robust_gt_1")
def require(test,msg):
    if not test: raise ValueError(msg)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()

def legacy(T):
    require(math.isfinite(T) and T>0,"LEGACY_NONPOSITIVE_T")
    return 7.5e-19*math.exp(-118348./T)/(1.+math.sqrt(T/1.e5))

def two_p_cooling(T):
    return E12_ERG*two_p.q_exc(T)

def quantile(vals,f):
    v=sorted(vals)
    p=f*(len(v)-1);i=int(p);j=min(i+1,len(v)-1)
    return v[i]*(1.-(p-i))+v[j]*(p-i)

def generate(out_dir):
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    require(sha(PUBLIC_2P)==SOURCE_SHA,"PUBLIC_PARENT_SOURCE_SHA_MISMATCH")
    src=ORIG.read_csv(ORIG.PREVIEW,ORIG.LOCKS["preview"])
    native=ORIG.native()  # exact H/He proper volumes and original code SHA locks
    with gzip.open(PUBLIC_2P,"rt",encoding="utf-8",newline="") as f:
        orig_2p=list(csv.DictReader(f))
    require(len(src)==46080 and len(orig_2p)==N,"SOURCE_COUNT")
    dt=float(native["dt"])
    require(abs(dt/4871848749.16828-1.)<1.e-14,"ORIGINAL_NATIVE_CLOCK")
    output=[]
    legacy_p=[];two_p_p=[];other_p=[];U_p=[];epsilon_p=[];ratios=[];native_ratios=[]
    global_bounds=[float("inf"),0.];max_cross=0.;max_cone=0.;rob01=0;rob1=0
    for r in orig_2p:
        i=int(r["node"]);require(0<=i<46080 and int(src[i]["node"])==i,"SOURCE_NODE_ID")
        s=src[i];V=float(native["vol"][i])
        tlo=float(s["tick160_Tgas_K_lower"]);thi=float(s["tick160_Tgas_K_upper"])
        require(5000.<=tlo<=thi<=20000. and V>0,"SUPPORTED_DOMAIN_OR_VOLUME")
        T=(tlo+thi)*.5
        def limits(root):
            lo=float(s[root+"_lower"]);hi=float(s[root+"_upper"])
            require(math.isfinite(lo) and math.isfinite(hi) and 0<lo<=hi,"SOURCE_CONE_"+root)
            return lo,hi,(lo+hi)*.5
        nhl,nhu,nh=limits("source_H_nuclei_N")
        nhel,nheu,nhe=limits("source_He_nuclei_N")
        nel,neu,ne=limits("tick160_electron_count_N")
        xl=float(s["tick160_xHII_lower"]);xu=float(s["tick160_xHII_upper"])
        require(0<xl<=xu<1,"SOURCE_XHII")
        kmin=nhl*(1.-xu)*nel/V
        kmax=nhu*(1.-xl)*neu/V
        kmid=nh*(1.-(xl+xu)*.5)*ne/V
        require(kmin>0 and kmin<=kmid<=kmax,"ORIGINAL_K_CONE")
        umin=1.5*KB_ERG*(nhl+nhel+nel)*tlo
        umax=1.5*KB_ERG*(nhu+nheu+neu)*thi
        umid=1.5*KB_ERG*(nh+nhe+ne)*T
        require(umin>0 and umin<=umid<=umax,"ORIGINAL_THERMAL_CONE")
        a_lo=legacy(tlo);a_mid=legacy(T);a_hi=legacy(thi)
        b_lo=two_p_cooling(tlo);b_mid=two_p_cooling(T);b_hi=two_p_cooling(thi)
        # Both coefficients increase on 5000..20000 K.  Coefficient ratio
        # uses independent interval bounds, never assumes identical endpoints.
        frac_lo=b_lo/a_hi;frac_hi=b_hi/a_lo;frac=b_mid/a_mid
        require(0<frac_lo<=frac<=frac_hi<1,"NEGATIVE_REMAINING_LEGACY_CHANNEL")
        global_bounds[0]=min(global_bounds[0],frac_lo)
        global_bounds[1]=max(global_bounds[1],frac_hi)
        old=kmid*a_mid;new=kmid*b_mid;remainder=old-new
        residual_bound_low=kmin*(a_lo-b_hi)
        require(residual_bound_low>0 and remainder>0,"REMAINDER_CONE_FAIL")
        via_parent=float(r["excitation_s_inv_mid"])*E12_ERG
        err=abs(new/via_parent-1.)
        max_cross=max(max_cross,err)
        require(err<3.e-12,"PRIMARY_SOURCE_RATE_CROSSWALK")
        prelo=float(r["excitation_s_inv_lower"])*E12_ERG
        prehi=float(r["excitation_s_inv_upper"])*E12_ERG
        p2lo=kmin*b_lo;p2hi=kmax*b_hi
        # Different interval extension paths can give safely overlapping hulls.
        require(prelo<=new*(1.+3.e-12) and new<=prehi*(1.+3.e-12),"PARENT_EXC_ENCLOSURE")
        require(p2lo<=new<=p2hi,"DIRECT_EXC_ENCLOSURE")
        ep_lo=dt*p2lo/umax;ep_mid=dt*new/umid;ep_hi=dt*p2hi/umin
        old_ep=dt*old/umid
        require(0<=ep_lo<=ep_mid<=ep_hi and math.isfinite(ep_hi),"THERMAL_RESPONSE_ENCLOSURE")
        dlo=float(s["tick160_to_161_delta_logT_lower"]);dhi=float(s["tick160_to_161_delta_logT_upper"])
        require(math.isfinite(dlo) and math.isfinite(dhi) and dlo<=dhi,"NATIVE_PREVIEW_DELTA_CONE")
        dmid=(dlo+dhi)*.5
        dabsmax=max(abs(dlo),abs(dhi))
        flag1=int(ep_lo>dabsmax);flag01=int(ep_lo>0.1*dabsmax)
        ratio_native=ep_mid/max(abs(dmid),1.e-300)
        rob1+=flag1;rob01+=flag01
        native_ratios.append(ratio_native)
        legacy_p.append(old);two_p_p.append(new);other_p.append(remainder)
        U_p.append(umid);epsilon_p.append(ep_mid);ratios.append(frac)
        output.append((i,old,new,remainder,frac,frac_lo,frac_hi,
                       ep_lo,ep_mid,ep_hi,old_ep,flag01,flag1))
    require(len(output)==N and all(output[i][0]<output[i+1][0] for i in range(N-1)),"SORTED_UNIQUE_SOURCE_NODES")
    path=out_dir/OUT
    with path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw,mode="wb",filename="",mtime=0,compresslevel=9) as zipped:
            with io.TextIOWrapper(zipped,encoding="utf-8",newline="") as w:
                wr=csv.writer(w,lineterminator="\n")
                wr.writerow(COLUMNS);wr.writerows(output)
    sums={"legacy_H_exc_erg_per_s":math.fsum(legacy_p),
          "two_p_exc_erg_per_s":math.fsum(two_p_p),
          "other_H_exc_residual_erg_per_s":math.fsum(other_p),
          "thermal_U_supported_erg":math.fsum(U_p)}
    require(abs((sums["two_p_exc_erg_per_s"]+sums["other_H_exc_residual_erg_per_s"])/sums["legacy_H_exc_erg_per_s"]-1.)<5.e-15,
            "ENERGY_PARTITION_SUM")
    result={
        "schema":"BASS_CR_REI_F05_2P_LEGACY_H_EXCITATION_PARTITION_V1",
        "status":"SOURCE_CONDITIONAL_NONAUTHORITATIVE_HOLD",
        "parent_bass_cr_PR":161,
        "parent_head":"a555eeb75eae79a5b05ee9054323c3ce06e3075d",
        "original_REI_owner_head":ORIG.LOCKS["owner_git"],
        "original_source_private_SHA256":ORIG.LOCKS["preview"],
        "parent_two_p_source_SHA256":SOURCE_SHA,
        "original_legacy_rhs_SHA256":ORIG.LOCKS["native"],
        "native_tick160_to_161_dt_seconds":dt,
        "original_source_cells":46080,
        "supported_source_cells":N,
        "excluded_source_cells":46080-N,
        "temperature_support_K":[5000,20000],
        "q12_source":"published_scholz_pradhan_knots_linear_interpolant",
        "source_assumptions":["Te_equals_gas_T","neutral_f1s_equals_1_saturation","fixed_original_source_state"],
        "legacy_H_exc_in_original_RHS":True,
        "no_new_cooling_term_to_add":True,
        "no_replacement_of_whole_legacy_by_2p":True,
        "not_proven_exact_atomic_2s_or_higher_residual":True,
        "no_actual_2p_level_occupation_or_escaping_line_flux":True,
        "original_tick160_accepted":True,"tick161_preview_unaccepted":True,
        "aggregates":sums,
        "two_p_fraction_of_legacy_integrated":sums["two_p_exc_erg_per_s"]/sums["legacy_H_exc_erg_per_s"],
        "two_p_over_legacy_mid_min_median_max":[min(ratios),quantile(ratios,.5),max(ratios)],
        "source_cell_fraction_enclosure_min_max":global_bounds,
        "epsilon_two_p_mid_max":max(epsilon_p),
        "epsilon_two_p_mid_median":quantile(epsilon_p,.5),
        "epsilon_two_p_mid_over_abs_native_preview_mid_gt_one_count":sum(x>1 for x in native_ratios),
        "epsilon_two_p_ROBUST_vs_original_native_preview_abs_gt_one_count":rob1,
        "epsilon_two_p_ROBUST_vs_original_native_preview_abs_gt_0p1_count":rob01,
        "max_source_excitation_rate_crosswalk_rel_error":max_cross,
        "csv_sha256":sha(path),
        "REI_central_DAG":"28/88_DELTA0","REI_working_DAG":"33/88_DELTA0",
        "BASS_CR_extension_DAG":"0/3_DELTA0","CR_OFF_unchanged":True,
        "PRODUCTION":"HOLD","NO_MERGE":True,"NO_FORCE_PUSH":True,
        "NO_REI_MUTATION":True,"native_subagent":"NOT_RUN",
        "distinct_author_referee":"NOT_RUN"
    }
    meta_path=out_dir/"RESULT.json"
    meta_path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return path,result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=HERE)
    a=p.parse_args()
    file,data=generate(a.out)
    print(json.dumps({"csv":str(file),"sha256":data["csv_sha256"],
                      "n":data["supported_source_cells"],
                      "partition":data["two_p_fraction_of_legacy_integrated"]},sort_keys=True))
