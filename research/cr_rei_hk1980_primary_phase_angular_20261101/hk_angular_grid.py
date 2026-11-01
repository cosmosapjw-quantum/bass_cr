#!/usr/bin/env python3
"""Source-authentic *finite-L charge-labelled* angular p+H quantum DCS.
Reconstructs 768-node angular DCS at two ORIGINAL HK1980 CM energies.
Not indistinguishable-proton spin-averaged scattering; not a Maxwellian rate.
Private original phase ZIP remains OUTSIDE public Git.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import legval,leggauss
import hk_primary_joint as hk

HERE=Path(__file__).resolve().parent
N_ANGULAR=768
SOURCE_DEFAULT=Path("/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/"
 "WU088_P0_R12_HK_NATIVE_RECONSTRUCTION_AND_ANGLE_CONTRACT_20260921.zip")
OUTPUT_NAME="HK1980_SOURCE_DCS_2E_2CHANNELS_768ANGLES.csv.gz"
COLUMNS=(
 "E_cm_eV","channel","L_finite","j_GL","x_nuclear","x_charge",
 "theta_nuclear_rad","theta_charge_rad","GL_weight_dx",
 "dSigma_dOmega_a0_sq_per_sr","dSigma_dOmega_cm2_per_sr",
 "dSigma_dX_preweighted_a0_sq","sigma_total_GL_contrib_a0_sq",
 "sigma_mt_charge_GL_contrib_a0_sq","sigma_viscosity_GL_contrib_a0_sq",
)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def channel_grid(E,g,u,n=N_ANGULAR):
    if n < 2*max(len(g),len(u))+2:
        raise ValueError("quadrature nodes must resolve all partial-wave products")
    x,weights=leggauss(n)
    k=hk.K_HK[E]
    ae,ac=hk.amplitudes(g,u)
    output=[]
    report={}
    for label,b,charge_sign in (("elastic",ae,1),("CX",ac,-1)):
        l=np.arange(len(b))
        f=legval(x,(2*l+1)*b)/(2*k)
        dsdo=np.square(abs(f))
        preweighted=2*math.pi*dsdo
        mt_factor=1-charge_sign*x
        sigma_terms=weights*preweighted
        mt_terms=sigma_terms*mt_factor
        vis_terms=sigma_terms*(1-x*x)
        integral=(math.fsum(sigma_terms),math.fsum(mt_terms),math.fsum(vis_terms))
        mom=hk.moments(b,k)
        expected=(mom["total"],mom["mt_minus" if label=="elastic" else "mt_plus"],
                  mom["viscosity"])
        reldiff=max(abs(a-b)/a for a,b in zip(expected,integral))
        if reldiff>5e-10:
            raise ArithmeticError(f"angular source mismatch {label} {E} {reldiff}")
        if not (0 <= integral[1] <= 2*integral[0]*(1+1e-12)
                and 0 <= integral[2] <= integral[0]*(1+1e-12)):
            raise ArithmeticError("violates physical nonnegativity bounds")
        report[label]=dict(
            sigma_total_a0_sq=integral[0],
            sigma_mt_charge_a0_sq=integral[1],
            sigma_viscosity_a0_sq=integral[2],
            sigma_total_cm2=integral[0]*hk.A0_CM**2,
            sigma_mt_cm2=integral[1]*hk.A0_CM**2,
            relative_error_vs_finite_l_recursion=reldiff,
            first_moment_charge_sign=charge_sign,
        )
        for j in range(n):
            nuclear_x=float(x[j]); cx=float(charge_sign*x[j]); w=float(weights[j])
            if not (-1 <= nuclear_x <= 1 and -1 <= cx <=1 and w>0):
                raise ArithmeticError("invalid quadrature node")
            one=(E,label,len(b),j,nuclear_x,cx,
                 math.acos(nuclear_x),math.acos(cx),w,
                 float(dsdo[j]),float(dsdo[j])*hk.A0_CM**2,float(preweighted[j]),
                 float(sigma_terms[j]),float(mt_terms[j]),float(vis_terms[j]))
            output.append(one)
    tot=report["elastic"]["sigma_mt_charge_a0_sq"]+report["CX"]["sigma_mt_charge_a0_sq"]
    report["charge_labelled_sum_diagnostic"]=dict(
        sigma_mt_elastic_plus_CX_a0_sq=tot,
        CX_charge_labelled_mt_fraction=report["CX"]["sigma_mt_charge_a0_sq"]/tot,
        does_not_include_identical_nuclear_spin_interference=True,
    )
    return output,report


def run(source_zip:Path=SOURCE_DEFAULT,out_dir:Path=HERE,n=N_ANGULAR):
    if n!=N_ANGULAR:
        raise ValueError("published angular grid requires exactly 768 nodes")
    phases,phase_sha=hk.read_original_phases(source_zip)
    if phase_sha!="ae2b3159eaefc699ec8763f3153dddfd3a3ce2aca6151a9a1718ab67997ca6c2":
        raise ValueError("unexpected primary-source phase identity")
    out_dir=Path(out_dir)
    out_dir.mkdir(parents=True,exist_ok=True)
    dest=out_dir/OUTPUT_NAME
    per_energy={}
    with dest.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw,mode="wb",filename="",mtime=0,
                           compresslevel=9) as compressed:
            with io.TextIOWrapper(compressed,encoding="utf-8",newline="") as tf:
                wr=csv.writer(tf,lineterminator="\n")
                wr.writerow(COLUMNS)
                for E,(g,u) in sorted(phases.items()):
                    rows,part=channel_grid(E,g,u,n)
                    per_energy[str(E)]=part
                    wr.writerows(rows)
    # Data output is a partial-wave-derived angular DCS: no direct original
    # 2016 downloaded DCS or physically spin-symmetrized transport kernel.
    result=dict(
        source="Hunter_Kuriyan_1980_ADNDT_25_287_printed_phase_source",
        DOI="10.1016/0092-640X(80)90006-6",
        source_original_private_zip_sha256=hk.SOURCE_SHA,
        source_phase_member_sha256=phase_sha,
        source_original_phase_rows=674,
        cm_energy_eV=[0.1,1.0],
        channels=["elastic","CX"],
        angular_nodes_per_channel_per_energy=n,
        derived_angular_rows=2*2*n,
        computed_moments=per_energy,
        angular_output_file=OUTPUT_NAME,
        angular_output_sha256=sha(dest),
        nuclear_spin="UNBOUND_NOT_PHYSICAL_SPIN_SYMMETRIZED",
        source_primary_full_2016_DCS="NOT_RETRIEVED",
        REI_BASS193_kinetic_source="NOT_SOURCE_MATCHED",
        REI_F05_160_161="NOT_ACCEPTED",
        REI_central_DAG="28/88_REPORTED_DELTA0",
        REI_working_DAG="33/88_REPORTED_DELTA0",
        BASS_CR_extension_DAG="0/3_DELTA0",
        NO_REI_MUTATION=True,NO_MERGE=True,
        CR_OFF_INDEPENDENT=True,PRODUCTION="HOLD",
    )
    path=out_dir/"ANGULAR_SCIENCE_RESULT.json"
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-zip",type=Path,default=SOURCE_DEFAULT)
    ap.add_argument("--out",type=Path,default=HERE)
    args=ap.parse_args()
    print(json.dumps(run(args.source_zip,args.out),sort_keys=True,indent=2))
