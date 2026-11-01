#!/usr/bin/env python3
"""Genuine original REI-F05 tick160 Case-B recombination event rates and
conditional Ly-alpha cascade production. Original 26-event owner unchanged.
No true line-photon transfer, escape, or canonical tick161 acceptance.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,os,subprocess,sys
from pathlib import Path
from functools import lru_cache
import numpy as np

HERE=Path(__file__).resolve().parent
OWNER=Path(os.environ.get("REI_F05_OWNER_REPO",
 "/home/cosmosapjw/worktrees/rei-f05-v2-versioned-owner-decision-20261101"))
PREVIEW=Path(os.environ.get("REI_F05_PREVIEW_CSV",
 "/home/cosmosapjw/archives/rei_f05_tick161_owner_candidate_20261101/primary/"
 "ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz"))
INCREMENTS=Path(os.environ.get("REI_F05_ORIGINAL_INCREMENT_CSV",
 "/home/cosmosapjw/archives/rei_f05_direct_interval_audit_20261101/primary/"
 "REI_ORIGINAL26_COMMON_PARENT_INCREMENT_46080.csv.gz"))
LOCKS={
 "owner_git":"cc1929982948265f6d0b0f699353b3170ccd1792",
 "preview":"713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d",
 "increments":"3cd9d158a74e781da39cf2e2a6424ce5b1bd147be226a0c0070ebbb5e846d635",
 "tensor":"4d8a71debcecbd723bc9a2a194be869ab9e0b378c432e01ab70acc5416b755f6",
 "forcing":"5c1df4c93d47198f9046e27bda3e029a7797f856fbd4dced0822efd688c557a1",
 "native":"b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36",
 "atomic":"bd2c519a5ca9c1c8d0cfafa3050d6ead3e714b4d9e8ba97c4ac8f46567450ee5"}
N=46080; TICK=160; TOTAL_TICKS=131072
E_LYA_ERG=6.62607015e-27*2.99792458e10/1.2156701e-5
FIELDS=("node","alphaB_cm3_s_mid","ne_cm_minus3_mid",
 "caseB_recomb_s_minus1_lower","caseB_recomb_s_minus1_mid","caseB_recomb_s_minus1_upper",
 "P_Lya_Bfit_mid","conditional_Lya_s_minus1_lower","conditional_Lya_s_minus1_mid",
 "conditional_Lya_s_minus1_upper","frozen_one_tick_recomb_events_mid",
 "native_twohalf_delta_HII_lower","native_twohalf_delta_HII_upper",
 "mixed_clock_residual_NOT_photoion_source_s_minus1_mid")
DATAFILE="ORIGINAL_REI_F05_CASEB_LYA_RECOMB_46080.csv.gz"

def check(ok,message):
    if not ok:raise ValueError(message)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def byte_lock(path,digest):
    check(Path(path).is_file() and sha(path)==digest,"SOURCE_SHA_MISMATCH:"+str(path))

def alphaB(T):
    x=np.asarray(T,dtype=np.float64)
    check(bool(np.all(np.isfinite(x)&(x>0))),"INVALID_T")
    lam=315614.0/x
    return 2.753e-14*lam**1.5/(1.0+(lam/2.740)**0.407)**2.242

def pB_fit(T):
    x=np.asarray(T,dtype=np.float64)/1.0e4
    check(bool(np.all(np.isfinite(x)&(x>0))),"INVALID_T")
    p=0.686-0.106*np.log10(x)-0.009*x**(-0.44)
    check(bool(np.all((p>0)&(p<1))),"P_B_BRANCH_DOMAIN")
    return p

def read_csv(path,digest):
    byte_lock(path,digest)
    with gzip.open(path,"rt",encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    check(len(rows)==N and all(int(r["node"])==i for i,r in enumerate(rows)),
          "ORIGINAL_46080_NODE_ORDER")
    return rows

def col(rows,name):
    x=np.fromiter((float(r[name]) for r in rows),dtype=np.float64,count=N)
    check(bool(np.all(np.isfinite(x))),"NONFINITE_"+name)
    return x

def load_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    check(spec is not None and spec.loader is not None,"ORIGINAL_MODULE")
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

@lru_cache(maxsize=1)
def native():
    root=OWNER.resolve()
    head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                  text=True).strip()
    check(head==LOCKS["owner_git"],"OWNER_BRANCH_AUTHORITY")
    tensor=root/"stages"/(
        "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_"
        "ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK")/"analysis"
    nativefile=root/"stages"/(
        "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_"
        "R2_R1A_R1_VALIDATED_CONTINUOUS_BRANCH_DIFFERENTIAL_INCLUSION_ENCLOSURE_LOCK"
        )/"analysis/reduced_interval_rhs.py"
    for path,key in ((tensor/"tensorized_inputs.py","tensor"),
                     (tensor/"array_forcing.py","forcing"),
                     (nativefile,"native"),
                     (root/"src/rei_bianchi/phase_space_kernel_b2c0.py","atomic")):
        byte_lock(path,LOCKS[key])
    mod=load_mod("locked_rei_f05_caseb_tensor",tensor/"tensorized_inputs.py")
    fmod=load_mod("locked_rei_f05_caseb_forcing",tensor/"array_forcing.py")
    inputs=mod.load_tensorized_inputs(repo_root=root)
    forcing=fmod.ArrayContinuousForcing(inputs=inputs)
    start=float(forcing._model(0)["times"][0]); duration=forcing.duration_seconds(0)
    t160=start+duration*TICK/TOTAL_TICKS
    z=float(forcing.point(interval=0,time_s=t160).z)
    h=np.asarray(inputs.state0.values[0]+inputs.state0.values[1],float)
    he=np.asarray(inputs.state0.values[2]+inputs.state0.values[3]+inputs.state0.values[4],float)
    vol=np.asarray(inputs.comoving_volume_cm3,float)/(1+z)**3
    check(h.shape==(N,) and he.shape==(N,) and vol.shape==(N,),
          "NATIVE_SOURCE_SHAPE")
    check(bool(np.all((vol>0)&np.isfinite(vol)) and np.all(h>0) and np.all(he>0)),
          "NATIVE_VOLUME_COUNTS")
    return dict(h=h,he=he,vol=vol,z=z,t160=t160,dt=duration/TOTAL_TICKS)

def calculate(preview=PREVIEW,increments=INCREMENTS):
    original=read_csv(Path(preview),LOCKS["preview"])
    diff=read_csv(Path(increments),LOCKS["increments"])
    geo=native();H=geo["h"]; He=geo["he"];V=geo["vol"]
    for field,vec in (("source_H_nuclei_N_lower",H),
                      ("source_H_nuclei_N_upper",H),
                      ("source_He_nuclei_N_lower",He),
                      ("source_He_nuclei_N_upper",He)):
        raw=col(original,field)
        check(bool(np.all(raw>0) and np.max(np.abs(vec/raw-1))<1.5e-12),
              "SAME_ORIGINAL_NATIVE_NUCLEI")
    xlo=col(original,"tick160_xHII_lower");xhi=col(original,"tick160_xHII_upper")
    ne_lo=col(original,"tick160_electron_count_N_lower")
    ne_hi=col(original,"tick160_electron_count_N_upper")
    tlo=col(original,"tick160_Tgas_K_lower")
    thi=col(original,"tick160_Tgas_K_upper")
    check(bool(np.all((0<xlo)&(xlo<=xhi)&(xhi<1)&(ne_lo>0)&(ne_lo<=ne_hi)&
                      (0<tlo)&(tlo<=thi))),"SOURCE_CONE")
    amid=alphaB((tlo+thi)*.5); alow=alphaB(thi); ahi=alphaB(tlo)
    pmid=pB_fit((tlo+thi)*.5);plow=pB_fit(thi);phi=pB_fit(tlo)
    check(bool(np.all((alow<=amid)&(amid<=ahi)&(plow<=pmid)&(pmid<=phi))),
          "PHYSICAL_T_MONOTONICITY")
    lo=alow*H*xlo*ne_lo/V
    mid=amid*H*((xlo+xhi)*.5)*((ne_lo+ne_hi)*.5)/V
    hi=ahi*H*xhi*ne_hi/V
    ll=plow*lo;lm=pmid*mid;lh=phi*hi
    check(bool(np.all(np.isfinite(mid)&(mid>0)&(lo<=mid)&(mid<=hi)&
                      (0<ll)&(ll<=lm)&(lm<=lh)&(lh<=hi))),"RATE_BOUNDS")
    dh_lo=col(diff,"x_HII_original_twohalf_increment_lower")*H
    dh_hi=col(diff,"x_HII_original_twohalf_increment_upper")*H
    check(bool(np.all(dh_lo<=dh_hi)),"NATIVE_HII_INCREMENT_ORDER")
    mixed=(dh_lo+dh_hi)*.5/geo["dt"]+mid
    cols=[np.arange(N),amid,(ne_lo+ne_hi)*.5/V,lo,mid,hi,
          pmid,ll,lm,lh,mid*geo["dt"],dh_lo,dh_hi,mixed]
    def S(x):return math.fsum(float(y) for y in x)
    recomb=[S(a) for a in (lo,mid,hi)]
    lya=[S(a) for a in (ll,lm,lh)]
    d_H=[S(a) for a in (dh_lo,dh_hi)]
    check(recomb[0]<=recomb[1]<=recomb[2] and
          lya[0]<=lya[1]<=lya[2]<=recomb[2],"GLOBAL_BOUNDS")
    ranked_rec=np.sort(mid)
    ranked_lya=np.sort(lm)
    top1count=math.ceil(0.01*N)
    top10count=math.ceil(0.10*N)
    top1_rec_share=S(ranked_rec[-top1count:])/recomb[1]
    top10_rec_share=S(ranked_rec[-top10count:])/recomb[1]
    top1_lya_share=S(ranked_lya[-top1count:])/lya[1]
    result=dict(
        unit="REI_F05_ORIGINAL_CASEB_H_RECOMB_AND_CONDITIONAL_LYA_SOURCE",
        original_cells=N,source_accepted_tick="160/131072",
        tick161_source_status="UNACCEPTED_NOT_USED",
        source_original_owner_head=LOCKS["owner_git"],
        sources_sha256=LOCKS,
        original_proper_time_s=geo["t160"],original_redshift=geo["z"],
        original_one_tick_s=geo["dt"],
        alphaB_cm3_s_min=float(alow.min()),alphaB_cm3_s_max=float(ahi.max()),
        original_H_CaseB_recomb_s_inv_lower=recomb[0],
        original_H_CaseB_recomb_s_inv_mid=recomb[1],
        original_H_CaseB_recomb_s_inv_upper=recomb[2],
        absolute_recomb_sector_Lya_photons_s_inv_upper=recomb[2],
        caseB_fit_probability_min=float(plow.min()),
        caseB_fit_probability_max=float(phi.max()),
        conditional_Lya_recomb_fit_s_inv_lower=lya[0],
        conditional_Lya_recomb_fit_s_inv_mid=lya[1],
        conditional_Lya_recomb_fit_s_inv_upper=lya[2],
        conditional_Lya_line_luminosity_erg_s_lower=lya[0]*E_LYA_ERG,
        conditional_Lya_line_luminosity_erg_s_mid=lya[1]*E_LYA_ERG,
        conditional_Lya_line_luminosity_erg_s_upper=lya[2]*E_LYA_ERG,
        conditional_CaseB_Lya_yield_source_weighted=lya[1]/recomb[1],
        top_1percent_cells_number=top1count,
        top_1percent_cells_recomb_event_fraction=top1_rec_share,
        top_10percent_cells_number=top10count,
        top_10percent_cells_recomb_event_fraction=top10_rec_share,
        top_1percent_cells_conditional_Lya_emission_fraction=top1_lya_share,
        rate_concentration_interpretation="SOURCE_NODES_NOT_EQUAL_VOLUME_CELLS",
        recomb_sector_Lya_energy_upper_erg_s=recomb[2]*E_LYA_ERG,
        original_static_tick160_caseB_event_exposure_mid=recomb[1]*geo["dt"],
        original_native_HII_twohalf_delta_lower=d_H[0],
        original_native_HII_twohalf_delta_upper=d_H[1],
        mixed_time_diagnostic_not_photo_source_s_inv_mid=S(mixed),
        HII_negative_cells=int(np.count_nonzero(dh_hi<0)),
        HII_positive_cells=int(np.count_nonzero(dh_lo>0)),
        HII_sign_unresolved_cells=int(np.count_nonzero((dh_lo<=0)&(dh_hi>=0))),
        Lya_photon_energy_eV=E_LYA_ERG/1.602176634e-12,
        native_rate_clock="FROZEN_T160_NOT_INTEGRATED_F05_RECOMB",
        photon_cascade_branching="DIJKSTRA_CANTALUPO_CASEB_FIT_CONDITIONAL",
        Lyalpha_level_population="NOT_OBSERVED_OR_NATIVE_OWNER",
        observed_escaping_Lya_luminosity="NOT_COMPUTED",
        original_photon_groups="4_IONIZING_NOT_LYA_10p2EV",
        source_model_other_recomb_or_collisional_Lya="EXCLUDED",
        REI_central="28/88_REPORTED_DELTA0",
        REI_working="33/88_REPORTED_DELTA0",
        BASS_CR_extension="0/3_DELTA0",
        production="HOLD",no_merge=True,no_force_push=True,
        no_REI_owner_mutation=True,CR_OFF_unchanged=True)
    return cols,result

def generate(out=HERE,preview=PREVIEW,increments=INCREMENTS):
    cols,result=calculate(preview,increments)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    data=out/DATAFILE
    with data.open("wb") as stream:
        with gzip.GzipFile(fileobj=stream,mode="wb",filename="",mtime=0,
                           compresslevel=9) as gz:
            with io.TextIOWrapper(gz,encoding="utf-8",newline="") as tf:
                wr=csv.writer(tf,lineterminator="\n")
                wr.writerow(FIELDS)
                for i in range(N):wr.writerow(tuple(float(c[i]) if j else i
                                                   for j,c in enumerate(cols)))
    summary=out/"RESULT.json"
    summary.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",
                       encoding="utf-8")
    return (data,summary),result

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,default=HERE)
    a.add_argument("--preview",type=Path,default=PREVIEW)
    a.add_argument("--increments",type=Path,default=INCREMENTS)
    x=a.parse_args()
    files,meta=generate(x.out,x.preview,x.increments)
    print(json.dumps({"result":meta,"sha256":{p.name:sha(p) for p in files}},
                     sort_keys=True,indent=2))
