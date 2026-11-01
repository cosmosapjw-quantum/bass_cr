#!/usr/bin/env python3
"""Original REI F05 46,080-cell H I Ly-alpha / Thomson opacity coefficient ceiling.

The original PR352 27-field source CSV is PRIVATE and SHA-locked. Its accepted
tick160 data and nonauthoritative tick161 preview are distinguished throughout.
One conditional neutral-1s saturation Maxwellian Doppler/Voigt line-centre model.
No line photon occupation, cell volume, actual optical depth or CR-ON transport.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import os
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIVATE_SOURCE = Path(os.environ.get(
    "REI_F05_OWNER_PREVIEW",
    "/home/cosmosapjw/archives/rei_f05_tick161_owner_candidate_20261101/"
    "primary/ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz"))
SOURCE_SHA256 = "713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d"
N_CELLS = 46080
REI_F05_PARENT_PR = 352
REI_F05_SHADOW_PR = 354
REI_ACCEPTED_TICK = 160
REI_PREVIEW_TICK = 161
ORIGINAL_TAR_SHA256_REPORTED = (
    "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
ORIGINAL_ACCEPTED_STATE_SHA256_REPORTED = (
    "cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01")
C = 2.99792458e10                 # cm/s
KB = 1.380649e-16                # erg/K
MH = 1.6735575e-24               # g
ME = 9.1093837139e-28           # g
ESU = 4.80320471257e-10          # Gaussian statC
H_PLANCK = 6.62607015e-27        # erg s
ERG_PER_EV = 1.602176634e-12     # erg
LAM_ALPHA = 1.2156701e-5         # cm
F12 = 0.4162
A21 = 6.265e8                    # s^-1
SIGMA_T = 6.6524587051e-25      # cm^2
NU_ALPHA = C / LAM_ALPHA
SOURCE_POLICY = "REI_F05_ORIGINAL_TICK160_ACCEPTED_TICK161_SHADOW_HOLD"
FIELDS = (
    "node", "sigma0_tick160_mid_cm2", "saturated_R_tick160_lower",
    "saturated_R_tick160_mid", "saturated_R_tick160_upper",
    "sigma0_tick161_preview_mid_cm2", "saturated_R_tick161_preview_lower",
    "saturated_R_tick161_preview_mid", "saturated_R_tick161_preview_upper",
    "delta_logR_shadow_minus160_lower", "delta_logR_shadow_minus160_mid",
    "delta_logR_shadow_minus160_upper"
)


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sigma0_cm2(T: float) -> float:
    if not math.isfinite(T) or T <= 0:
        raise ValueError("Tgas must be finite positive kelvin")
    v = math.sqrt(2.0*KB*T/MH)
    dv = v / LAM_ALPHA
    a = A21/(4*math.pi*dv)
    H0 = math.exp(a*a)*math.erfc(a)
    sigma = (math.sqrt(math.pi)*ESU**2*F12/(ME*C*dv))*H0
    if not math.isfinite(sigma) or sigma<=0:
        raise ValueError("positive finite Voigt line-centre cross section required")
    return sigma


def numeric_bounds(row: dict, label: str):
    # Source counts per original material cell, NOT number density.
    def get(name):
        v = float(row[name])
        if not math.isfinite(v):
            raise ValueError("nonfinite original source value "+name)
        return v
    hnlo=get("source_H_nuclei_N_lower")
    hnhi=get("source_H_nuclei_N_upper")
    enlo=get(label+"_electron_count_N_lower")
    enhi=get(label+"_electron_count_N_upper")
    xlo=get(label+"_xHII_lower")
    xhi=get(label+"_xHII_upper")
    tlo=get(label+"_Tgas_K_lower")
    thi=get(label+"_Tgas_K_upper")
    if not(0<hnlo<=hnhi and 0<enlo<=enhi and 0<=xlo<=xhi<1
           and 0<tlo<=thi):
        raise ValueError("invalid original H/electron/ion fraction/T interval")
    sm= sigma0_cm2((tlo+thi)*.5)
    s_lo = sigma0_cm2(thi)     # sigma(T) strictly decreasing
    s_hi = sigma0_cm2(tlo)
    h_mid = (hnlo+hnhi)*.5
    e_mid = (enlo+enhi)*.5
    x_mid = (xlo+xhi)*.5
    ratio_lo = (hnlo/enhi)*(1.-xhi)*(s_lo/SIGMA_T)
    ratio_hi = (hnhi/enlo)*(1.-xlo)*(s_hi/SIGMA_T)
    ratio_mid = (h_mid/e_mid)*(1.-x_mid)*(sm/SIGMA_T)
    if not(0<ratio_lo<=ratio_mid*(1+2e-12)
           and ratio_mid<=ratio_hi*(1+2e-12)):
        raise AssertionError("conditional interval ratio enclosure failed")
    n_hi_lo = hnlo*(1.-xhi)
    n_hi_hi = hnhi*(1.-xlo)
    n_hi_mid = h_mid*(1.-x_mid)
    return (ratio_lo,ratio_mid,ratio_hi,sm,
            n_hi_lo,n_hi_mid,n_hi_hi,
            n_hi_lo*s_lo,n_hi_mid*sm,n_hi_hi*s_hi,
            enlo,enhi)


def load_rows(source=PRIVATE_SOURCE):
    source = Path(source)
    if sha256(source) != SOURCE_SHA256:
        raise ValueError("original F05 physical-source byte lock failed")
    with gzip.open(source, "rt", encoding="utf-8", newline="") as f:
        reader=csv.DictReader(f)
        rows=list(reader)
    if len(rows)!=N_CELLS:
        raise ValueError("original F05 46,080-cell source count mismatch")
    for i,r in enumerate(rows):
        if int(r["node"])!=i:
            raise ValueError("source cell indices must be exactly ordered")
    return rows


def source_preview_electron_stoichiometry(row):
    fl=lambda s:float(row[s])
    nhl,nhu=fl("source_H_nuclei_N_lower"),fl("source_H_nuclei_N_upper")
    hel,heu=fl("source_He_nuclei_N_lower"),fl("source_He_nuclei_N_upper")
    lower=(nhl*fl("tick161_preview_xHII_lower")+
           hel*(fl("tick161_preview_xHeII_lower")+
                2*fl("tick161_preview_xHeIII_lower")))
    upper=(nhu*fl("tick161_preview_xHII_upper")+
           heu*(fl("tick161_preview_xHeII_upper")+
                2*fl("tick161_preview_xHeIII_upper")))
    nel,neu=(fl("tick161_preview_electron_count_N_"+s)
             for s in ("lower","upper"))
    return max(lower,nel)<=min(upper,neu), (
        ((lower+upper)*.5)/((nel+neu)*.5)-1.)


def generate(source=PRIVATE_SOURCE, outdir=HERE):
    original = load_rows(source)
    outdir=Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    dst=outdir/"REI_F05_HI_LYA_TO_THOMSON_46080.csv.gz"
    s = {name: [] for name in ("nHI160_lower","nHI160_mid","nHI160_upper",
         "nHI161_lower","nHI161_mid","nHI161_upper",
         "A160_lower","A160_mid","A160_upper","A161_lower","A161_mid","A161_upper",
         "Ne160_lower","Ne160_upper","Ne161_lower","Ne161_upper")}
    r0_mids=[];r1_mids=[]; certified_plus=certified_minus=0
    minr0=math.inf;maxr0=0.;maxlogerr=0.
    with dst.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb",filename="",mtime=0,
                           compresslevel=9) as zipped:
            with io.TextIOWrapper(zipped,encoding="utf-8",newline="") as txt:
                writer=csv.writer(txt,lineterminator="\n")
                writer.writerow(FIELDS)
                for i,row in enumerate(original):
                    good,err=source_preview_electron_stoichiometry(row)
                    if not good:
                        raise ValueError("preview H/He electron charge conservation mismatch")
                    maxlogerr=max(maxlogerr,abs(err))
                    a=numeric_bounds(row,"tick160")
                    b=numeric_bounds(row,"tick161_preview")
                    difflo=math.log(b[0])-math.log(a[2])
                    diffmid=math.log(b[1])-math.log(a[1])
                    diffhi=math.log(b[2])-math.log(a[0])
                    if not difflo<=diffmid+1e-12<=diffhi+2e-12:
                        raise AssertionError("source independent interval log ratio")
                    certified_plus+=difflo>0
                    certified_minus+=diffhi<0
                    r0_mids.append(a[1]);r1_mids.append(b[1])
                    minr0=min(minr0,a[0]);maxr0=max(maxr0,a[2])
                    writer.writerow((i,a[3],a[0],a[1],a[2],b[3],b[0],b[1],b[2],
                                     difflo,diffmid,diffhi))
                    for name,v in zip(
                        ("nHI160_lower","nHI160_mid","nHI160_upper",
                         "A160_lower","A160_mid","A160_upper",
                         "Ne160_lower","Ne160_upper"),(*a[4:10],*a[10:12])):
                        s[name].append(v)
                    for name,v in zip(
                        ("nHI161_lower","nHI161_mid","nHI161_upper",
                         "A161_lower","A161_mid","A161_upper",
                         "Ne161_lower","Ne161_upper"),(*b[4:10],*b[10:12])):
                        s[name].append(v)
    sums={k:math.fsum(v) for k,v in s.items()}
    def global_area(prefix):
        return {
          "geometric_HI_Lya_area_cm2_lower":sums["A"+prefix+"_lower"],
          "geometric_HI_Lya_area_cm2_mid":sums["A"+prefix+"_mid"],
          "geometric_HI_Lya_area_cm2_upper":sums["A"+prefix+"_upper"],
          "total_HI_N_lower":sums["nHI"+prefix+"_lower"],
          "total_HI_N_mid":sums["nHI"+prefix+"_mid"],
          "total_HI_N_upper":sums["nHI"+prefix+"_upper"],
          "total_electron_thomson_area_cm2_lower":sums["Ne"+prefix+"_lower"]*SIGMA_T,
          "total_electron_thomson_area_cm2_upper":sums["Ne"+prefix+"_upper"]*SIGMA_T,
          "global_cross_section_area_ratio_lower":
              sums["A"+prefix+"_lower"]/(sums["Ne"+prefix+"_upper"]*SIGMA_T),
          "global_cross_section_area_ratio_upper":
              sums["A"+prefix+"_upper"]/(sums["Ne"+prefix+"_lower"]*SIGMA_T)
        }
    info={
        "unit": "F05_NATIVE_LYA_LINE_CENTRE_VERSUS_THOMSON_SOURCE_OPACITY_CEILING",
        "source_original_private_46k_csv_sha256":SOURCE_SHA256,
        "source_original_tar_SHA256_reported_not_reopened":ORIGINAL_TAR_SHA256_REPORTED,
        "source_accepted_tick160_arrays_SHA256_reported_not_reopened":ORIGINAL_ACCEPTED_STATE_SHA256_REPORTED,
        "REI_parent_PR":REI_F05_PARENT_PR,"REI_V2_shadow_PR":REI_F05_SHADOW_PR,
        "accepted_tick":REI_ACCEPTED_TICK,"preview_tick_not_accepted":REI_PREVIEW_TICK,
        "original_physical_cells":N_CELLS,
        "neutral_temperature_model":"T_HI=Tgas_no_extra_turbulent_Doppler",
        "line_ground_population":"g_1=1_saturation_model_not_source_measured",
        "line_frequency_Hz":NU_ALPHA,
        "line_energy_eV":H_PLANCK*NU_ALPHA/ERG_PER_EV,
        "sigma_line_10000K_cm2":sigma0_cm2(1e4),
        "sigmaT_cm2":SIGMA_T,
        "tick160_saturated_ratio_source_cell_median_unweighted":
              statistics.median(r0_mids),
        "tick161_preview_saturated_ratio_source_cell_median_unweighted":
              statistics.median(r1_mids),
        "tick160_ratio_lower_across_cells_min":minr0,
        "tick160_ratio_upper_across_cells_max":maxr0,
        "shadow_delta_lnR_certified_increase_cells":certified_plus,
        "shadow_delta_lnR_certified_decrease_cells":certified_minus,
        "shadow_delta_lnR_unresolved_cells":N_CELLS-certified_plus-certified_minus,
        "preview_H_He_electron_charge_max_midpoint_rel_residual":maxlogerr,
        "tick160_accepted":global_area("160"),
        "tick161_NONAUTHORITATIVE_preview":global_area("161"),
        "measured_lya_photon_source":"NOT_PRESENT_IN_THIS_SOURCE",
        "measured_lya_optical_depth":"NOT_COMPUTABLE_WITHOUT_PHOTON_FREQUENCY_AND_PATH",
        "global_area_interpretation":"sum_N_times_sigma_not_a_line_of_sight_tau",
        "REI_central_DAG":"28/88_REPORTED_DELTA0",
        "REI_working_DAG":"33/88_REPORTED_DELTA0",
        "BASS_CR_extension_DAG":"0/3_DELTA0",
        "source_authority":"SCOPED_CONDITIONAL_INPUT_DIAGNOSTIC_ONLY",
        "CR_OFF_UNCHANGED":True,"PRODUCTION":"HOLD",
        "NO_REI_MUTATION":True,"NO_MERGE":True,"NO_FORCE_PUSH":True
    }
    p=outdir/"RESULT.json"
    p.write_text(json.dumps(info,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return info, (dst,p)


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=PRIVATE_SOURCE)
    ap.add_argument("--out",type=Path,default=HERE)
    args=ap.parse_args()
    ans,paths=generate(args.input,args.out)
    print(json.dumps({"result":ans,"output_SHA256":{p.name:sha256(p) for p in paths}},
                     sort_keys=True,indent=2))
