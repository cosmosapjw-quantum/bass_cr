#!/usr/bin/env python3
"""Source-native REI-F05 tick160 full H cooling closure spread, NONAUTHORITATIVE.

Cen92 is ALREADY inside original thermochemical RHS. SW91 is a standalone
alternative fit, NOT an additive correction or a new time-evolved solution.
Inputs are immutable original private F05 preview/source + original owner volume.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE_PARENT=HERE.parent/"cr_rei_f05_caseb_lya_20261101"
sys.path.insert(0,str(SOURCE_PARENT))
import native_caseb_lya as source_owner

MODEL="BASS_CR_REI_F05_CEN92_VS_SW91_FULL46K_SOURCE_V1"
OUT="REI_ORIGINAL_F05_CEN92_SW91_46080_DERIVED.csv.gz"
SOURCE_SHA="713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d"
OWNER_RHS_SHA="b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36"
KB_ERG_K=1.380649e-16
N=46080
T_LO,T_HI=2000.,67000.
COLS=("node","legacy_cen_erg_s_mid","alternative_sw_erg_s_mid",
      "alternative_minus_legacy_erg_s_lower","alternative_minus_legacy_erg_s_mid",
      "alternative_minus_legacy_erg_s_upper","sw_over_cen_mid",
      "frozen_delta_lnT_lower","frozen_delta_lnT_mid","frozen_delta_lnT_upper",
      "robust_model_response_gt_abs_preview_delta_lnT")

def require(flag,msg):
    if not flag:raise ValueError(msg)

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block)
    return h.hexdigest()

def read_original(path=source_owner.PREVIEW):
    path=Path(path)
    require(path.is_file() and digest(path)==SOURCE_SHA,"ORIGINAL_SOURCE_SHA_MISMATCH")
    return source_owner.read_csv(path,SOURCE_SHA)

def log_p(T):
    require(math.isfinite(T) and T_LO<=T<=T_HI,"SOURCE_T_OUT_OF_SW91_DOMAIN")
    u=math.log(T)
    return ((((-0.003290382*u+0.1515352)*u-2.762755)*u+25.06062)*u-113.9492)*u+213.7913

def cen(T):
    require(math.isfinite(T) and T_LO<=T<=T_HI,"SOURCE_T_OUT_OF_CEN_DOMAIN")
    return 7.5e-19*math.exp(-118348./T)/(1.+math.sqrt(T/100000.))

def scholz_walters(T):
    return 1.e-20*math.exp(log_p(T)-118348./T)

def deriv_log_sw(T):
    require(math.isfinite(T) and T_LO<=T<=T_HI,"SOURCE_T_OUT_OF_SW91_DOMAIN")
    u=math.log(T)
    return ((((-0.01645191*u+0.6061408)*u-8.288265)*u+50.12124)*u-113.9492)+118348./T

def deriv2_p(u):
    return ((-0.06580764*u+1.8184224)*u-16.57653)*u+50.12124

def signed_ratio_interval(lo,hi,pos_lo,pos_hi):
    require(pos_lo>0 and pos_lo<=pos_hi and lo<=hi,"INVALID_SIGNED_INTERVAL_DIVISION")
    return min(lo/pos_lo,lo/pos_hi,hi/pos_lo,hi/pos_hi),max(lo/pos_lo,lo/pos_hi,hi/pos_lo,hi/pos_hi)

def generate(out_dir):
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    require(source_owner.LOCKS["preview"]==SOURCE_SHA,"SOURCE_LOCK_CONFLICT")
    require(source_owner.LOCKS["native"]==OWNER_RHS_SHA,"ORIGINAL_RHS_LOCK_CONFLICT")
    rows=read_original()
    native=source_owner.native() # read-only original owner code and proper volume; all SHA-locked
    require(len(rows)==N and len(native["vol"])==N,"ORIGINAL_CELL_COUNT_MISMATCH")
    dt=float(native["dt"])
    require(math.isfinite(dt) and abs(dt/4871848749.16828-1.)<2.e-14,"NATIVE_PROPER_CLOCK")
    outrows=[]
    all_c,all_sw,all_delta,all_u=[],[],[],[]
    all_dlog=[];all_ratio=[]
    counts={"positive_model_change":0,"negative_model_change":0,"interval_sign_uncertain":0,
            "robust_over_native_preview_delta":0,"mid_over_native_preview_delta":0,
            "mid_delta_over_2e_4":0,"mid_delta_over_2e_6":0}
    bound_sign=[]
    max_raw_relative=0.
    tmin=float("inf");tmax=0.
    for j,s in enumerate(rows):
        require(int(s["node"])==j,"NODE_ALIGNMENT")
        def rng(prefix):
            lo=float(s[prefix+"_lower"]);hi=float(s[prefix+"_upper"])
            require(0<lo<=hi and math.isfinite(hi),"NONPOSITIVE_SOURCE_"+prefix)
            return lo,hi,(lo+hi)/2.
        h0,h1,h=rng("source_H_nuclei_N")
        he0,he1,he=rng("source_He_nuclei_N")
        e0,e1,e=rng("tick160_electron_count_N")
        t0,t1,t=rng("tick160_Tgas_K")
        require(T_LO<=t0<=t<=t1<=T_HI,"INVALID_PUBLISHED_T_DOMAIN")
        x0=float(s["tick160_xHII_lower"]);x1=float(s["tick160_xHII_upper"])
        require(0<=x0<=x1<=1 and math.isfinite(x1),"XHII_INTERVAL_DOMAIN")
        vol=float(native["vol"][j])
        require(vol>0 and math.isfinite(vol),"ORIGINAL_PROPER_VOLUME")
        relative=abs(float(native["h"][j])/h-1.)
        max_raw_relative=max(max_raw_relative,relative)
        require(relative<1.5e-12,"NATIVE_H_SOURCE_CROSSWALK")
        k0=h0*(1-x1)*e0/vol
        k1=h1*(1-x0)*e1/vol
        km=h*(1-(x0+x1)/2)*e/vol
        require(0<=k0<=km<=k1 and math.isfinite(k1),"NATIVE_COLLISION_WEIGHT")
        u0=1.5*KB_ERG_K*(h0+he0+e0)*t0
        u1=1.5*KB_ERG_K*(h1+he1+e1)*t1
        um=1.5*KB_ERG_K*(h+he+e)*t
        require(0<u0<=um<=u1 and math.isfinite(u1),"NATIVE_THERMAL_RESERVOIR")
        c0,cm,c1=cen(t0),cen(t),cen(t1)
        w0,wm,w1=scholz_walters(t0),scholz_walters(t),scholz_walters(t1)
        # Positivity of dLambda/dT on 2000..67000 proven from P'' bounds in THEORY.
        require(0<c0<=cm<=c1 and 0<w0<=wm<=w1,"COEFFICIENT_MONOTONICITY")
        pc0,pcm,pc1=k0*c0,km*cm,k1*c1
        pw0,pwm,pw1=k0*w0,km*wm,k1*w1
        require(0<=pc0<=pcm<=pc1 and 0<=pw0<=pwm<=pw1,"POWER_INTERVAL")
        # Signed difference of two *correlated* functions; this enclosure
        # is conservative because independent interval evaluation loses correlation.
        dlo=pw0-pc1
        dhi=pw1-pc0
        dm=pwm-pcm
        require(dlo<=dm+3e-15*max(abs(dm),abs(dlo),abs(dhi)) and dm<=dhi+3e-15*max(abs(dm),abs(dlo),abs(dhi)),
                "SIGNED_DIFFERENCE_INTERVAL")
        f_lo,f_hi=signed_ratio_interval(-dt*dhi,-dt*dlo,u0,u1)
        fm=-dt*dm/um
        require(f_lo<=fm+1e-14*max(abs(fm),abs(f_lo),abs(f_hi)) and fm<=f_hi+1e-14*max(abs(fm),abs(f_lo),abs(f_hi)),
                "FROZEN_LOGT_INTERVAL")
        native_dlo=float(s["tick160_to_161_delta_logT_lower"])
        native_dhi=float(s["tick160_to_161_delta_logT_upper"])
        require(math.isfinite(native_dlo) and native_dlo<=native_dhi,"ORIGINAL_PREVIEW_DIAGNOSTIC")
        lower_abs=0. if f_lo<=0<=f_hi else min(abs(f_lo),abs(f_hi))
        peak_preview=max(abs(native_dlo),abs(native_dhi))
        robust=int(lower_abs>peak_preview)
        counts["robust_over_native_preview_delta"]+=robust
        counts["mid_over_native_preview_delta"]+=int(abs(fm)>abs((native_dlo+native_dhi)/2))
        counts["mid_delta_over_2e_4"]+=int(abs(fm)>2.e-4)
        counts["mid_delta_over_2e_6"]+=int(abs(fm)>2.e-6)
        counts["positive_model_change"]+=int(dm>0)
        counts["negative_model_change"]+=int(dm<0)
        counts["interval_sign_uncertain"]+=int(dlo<=0<=dhi)
        all_c.append(pcm);all_sw.append(pwm);all_delta.append(dm)
        all_u.append(um);all_dlog.append(fm);all_ratio.append(wm/cm)
        bound_sign.append(max(abs(f_lo),abs(f_hi)))
        tmin=min(tmin,t0);tmax=max(tmax,t1)
        # no source T, species populations, volume, original native preview ΔlnT
        # written to the PUBLIC derived CSV.
        outrows.append((j,pcm,pwm,dlo,dm,dhi,wm/cm,f_lo,fm,f_hi,robust))
    require(len(outrows)==N and counts["positive_model_change"]+counts["negative_model_change"]==N,
            "FULL_SOURCE_COVERAGE_OR_ZERO_CASE")
    file=out_dir/OUT
    with file.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw,mode="wb",mtime=0,filename="",compresslevel=9) as gz:
            with io.TextIOWrapper(gz,encoding="utf-8",newline="") as txt:
                writer=csv.writer(txt,lineterminator="\n")
                writer.writerow(COLS);writer.writerows(outrows)
    old=math.fsum(all_c);new=math.fsum(all_sw);delta=math.fsum(all_delta)
    require(abs((old+delta)/new-1)<5e-15,"CROSS_MODEL_ENERGY_PARTITION")
    output={
      "schema":MODEL,"status":"ORIGINAL_SOURCE_CONDITIONAL_NONAUTHORITATIVE",
      "accepted_tick":"160/131072","tick161":"NOT_ACCEPTED",
      "original_source_cells":N,"temperature_support_K":[T_LO,T_HI],
      "original_T_min_K":tmin,"original_T_max_K":tmax,
      "original_private_F05_SHA256":SOURCE_SHA,
      "original_owner_HEAD":source_owner.LOCKS["owner_git"],
      "original_legacy_RHS_SHA256":OWNER_RHS_SHA,
      "original_dt_s":dt,
      "two_atomic_models_not_statistical_error_envelope":True,
      "no_original_REI_mutation":True,"no_new_cooling_term_added":True,
      "not_an_IVP_or_native_14ledger_replay":True,
      "energy_source_Cen_erg_s":old,
      "energy_source_SW_erg_s":new,
      "energy_difference_SW_minus_Cen_erg_s":delta,
      "signed_fractional_difference_integrated":new/old-1,
      "frozen_tick_energy_difference_erg":delta*dt,
      "source_ideal_thermal_energy_erg":math.fsum(all_u),
      "max_abs_local_frozen_delta_lnT_mid":max(map(abs,all_dlog)),
      "max_abs_local_frozen_delta_lnT_interval_upper":max(bound_sign),
      "median_abs_local_frozen_delta_lnT_mid":sorted(map(abs,all_dlog))[N//2],
      "sw_over_cen_ratio_min_max":[min(all_ratio),max(all_ratio)],
      "max_native_H_source_rel_mismatch":max_raw_relative,
      "counts":counts,
      "csv_sha256":digest(file),
      "REI_central_DAG":"28/88_DELTA0",
      "REI_working_DAG":"33/88_DELTA0",
      "BASS_CR_extension_DAG":"0/3_DELTA0",
      "CR_OFF_unchanged":True,"production":"HOLD",
      "native_subagent":"NOT_RUN",
      "independent_external_referee":"NOT_RUN"
    }
    path=out_dir/"RESULT.json"
    path.write_text(json.dumps(output,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return file,output

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=HERE)
    args=ap.parse_args()
    file,result=generate(args.out)
    print(json.dumps({"csv":str(file),"n":result["original_source_cells"],"ratio":result["signed_fractional_difference_integrated"],"sha256":result["csv_sha256"]},sort_keys=True))
