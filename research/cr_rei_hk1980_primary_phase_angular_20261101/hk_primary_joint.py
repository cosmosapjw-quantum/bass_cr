#!/usr/bin/env python3
"""HK1980 original printed g/u phases -> physically tagged elastic/CX moments.
Distinct from, and NOT a replacement for, the Schultz2016 raw UGA DCS.
Outputs original-source finite-L science, NOT spin-averaged indistinguishable p-H.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import zipfile
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import legval, leggauss

HERE=Path(__file__).resolve().parent
SOURCE_SHA="562aba864fa55119e8454f4484ae3b09433df990ab589a3b9725544a8b6a5913"
PHASE_MEMBER="data/HK1980_FIRST_SLICE_PHASES.csv"
K_HK={0.1:2.597682,1.0:8.214591}  # printed native K a0^-1, archived R12
N_L={0.1:147,1.0:190}
A0_CM=5.291772109e-9 # 2023 Schultz et al published rounded a0 in cm
RELATIVE_SOURCE="PRIMARY_HK1980_P298_PHASES_FROZEN_R12_RECONSTRUCTION"
PUBLIC_2016=HERE.parent/"cr_rei_primary_cx_2016_t2_20261101"/"PRIMARY_DCS_SCHULTZ2016_TABLE1_E1EV.csv"

def sha_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def read_original_phases(archive):
    archive=Path(archive)
    if sha_file(archive)!=SOURCE_SHA:
        raise ValueError("wrong immutable HK1980 R12 source archive")
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("source archive CRC failure")
        raw=z.read(PHASE_MEMBER)
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    if len(rows)!=674:
        raise ValueError("unexpected source phase count")
    native={e:{"g":{},"u":{}} for e in K_HK}
    for row in rows:
        E=float(row["E_cm_eV"])
        L=int(row["L"])
        s=row["symmetry"]
        v=float(row["phase_rad"])
        if E not in native or s not in ("g","u") or not math.isfinite(v):
            raise ValueError("bad source row")
        if L in native[E][s]:
            raise ValueError("duplicate partial wave")
        native[E][s][L]=v
    out={}
    for E in sorted(native):
        g= native[E]["g"];u=native[E]["u"]
        if sorted(g)!=list(range(N_L[E])) or sorted(u)!=list(range(N_L[E])):
            raise ValueError("missing source partial wave")
        out[E]=(np.array([g[L] for L in range(N_L[E])]),
                np.array([u[L] for L in range(N_L[E])]))
    return out,hashlib.sha256(raw).hexdigest()

def amplitudes(g,u):
    """S^g/u_l = exp(2i delta); tagged elastic=(f_g+f_u)/2, CT=(f_g-f_u)/2."""
    # avoid cancellation near S=1
    ag=np.exp(1j*g)*np.sin(g)
    au=np.exp(1j*u)*np.sin(u)
    return ag+au,ag-au

def moments(a,k):
    l=np.arange(len(a),dtype=float)
    pref=math.pi/k**2
    total=pref*np.sum((2*l+1)*abs(a)**2)
    q1=2*pref*np.sum((l[:-1]+1)*np.real(a[:-1]*np.conj(a[1:])))
    c=np.zeros(len(a)+1,dtype=complex)
    c[1:]+=(l+1)*a
    c[:len(a)-1]+=l[1:]*a[1:]
    q2=pref*np.sum(abs(c)**2/(2*np.arange(len(c))+1))
    return dict(total=float(total),mt_minus=float(total-q1),
                mt_plus=float(total+q1),viscosity=float(total-q2),
                q1=float(q1),q2=float(q2))

def independent_angle_moments(a,k,charge_reverse=False,n=512):
    x,w=leggauss(n)    # outgoing projectile nucleus theta, x=cos theta
    f=legval(x,(2*np.arange(len(a))+1)*a)/(2*k)
    d=2*math.pi*(abs(f)**2)
    s0=float(np.dot(w,d))
    mt=float(np.dot(w,d*(1+x if charge_reverse else 1-x)))
    visc=float(np.dot(w,d*(1-x*x)))
    return (s0,mt,visc)

def finite_l_sensitivity(g,u,E):
    K=K_HK[E]
    summary={}
    for stop in sorted({max(1,len(g)-21),max(1,len(g)-6),len(g)-1,len(g)}):
        ae,ac=amplitudes(g[:stop],u[:stop])
        me= moments(ae,K); mc=moments(ac,K)
        summary[str(stop)]=dict(el_mt=me["mt_minus"],
              cx_mt_charge=mc["mt_plus"],combined_mt=me["mt_minus"]+mc["mt_plus"],
              el_total=me["total"],cx_total=mc["total"])
    return summary

def source_bound_rows(archive):
    phase,phase_sha=read_original_phases(archive)
    out=[];checks={}
    for E,(g,u) in phase.items():
        k=K_HK[E]
        ae,ac=amplitudes(g,u)
        checks[str(E)]=finite_l_sensitivity(g,u,E)
        for kind,coeff,reversed_charge in (("elastic",ae,False),("CX",ac,True)):
            m=moments(coeff,k)
            sigma_mt=m["mt_plus" if reversed_charge else "mt_minus"]
            nums=independent_angle_moments(coeff,k,reversed_charge)
            reference=(m["total"],sigma_mt,m["viscosity"])
            relative=max(abs((a-b)/a) for a,b in zip(reference,nums) if a>0)
            out.append(dict(E_cm_eV=E,
              process=kind,
              original_printed_partial_waves=len(g),
              sigma_total_a0_sq=m["total"],
              sigma_mt_charge_a0_sq=sigma_mt,
              sigma_viscosity_a0_sq=m["viscosity"],
              sigma_mt_over_total=sigma_mt/m["total"],
              sigma_total_cm2=m["total"]*A0_CM**2,
              sigma_mt_cm2=sigma_mt*A0_CM**2,
              angular_GL512_relative_max=relative,
              source_kind=RELATIVE_SOURCE,
              identifiable_spin_average=False,original_2016_full_DCS=False))
    return out,checks,phase_sha

def prior_2016_sparse_comparison(phase):
    """Different source and partial-L cutoff; discrepancy is a measurement, NOT fail/pass."""
    g,u=phase[1.0];ae,ac=amplitudes(g,u);k=K_HK[1.0]
    theta={"forward":7.69075e-6,"mid":1.56759,"back":3.14158}
    # parent PR156 source table had 8 lmax rows; use lmax1400 for each angle
    with PUBLIC_2016.open(newline="",encoding="utf-8") as f:
        table=[r for r in csv.DictReader(f) if int(r["ell_max"])==1400]
    if len(table)!=1:raise ValueError("2016 anchor row unavailable")
    orig=table[0]
    out=[]
    for angle,chi in theta.items():
        for kind,a,flip in (("elastic",ae,False),("CX",ac,True)):
            x= -math.cos(chi) if flip else math.cos(chi)
            f=legval(x,(2*np.arange(len(a))+1)*a)/(2*k)
            computed=float(2*math.pi*math.sin(chi)*abs(f)**2)
            prefix="charge_exchange" if flip else "elastic"
            published=float(orig[prefix+"_theta_"+angle+"_a0_sq"])
            out.append(dict(E_cm_eV=1,angle=angle,theta_charge_rad=chi,
                process=kind,hk1980_original_phase_dSigma_dTheta_a0_sq_rad=computed,
                schultz2016_published_l1400_dSigma_dTheta_a0_sq_rad=published,
                hk_over_2016_minus1=computed/published-1,
                source_equivalence="NOT_PROVED_DIFFERENT_PHASE_CALCULATION_AND_LMAX"))
    return out

def write_csv(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        w.writeheader();w.writerows(rows)

def run(archive):
    data,checks,phase_sha=source_bound_rows(archive)
    phase,_=read_original_phases(archive)
    compare=prior_2016_sparse_comparison(phase)
    write_csv(HERE/"HK1980_PRIMARY_JOINT_4_ROWS.csv",data)
    write_csv(HERE/"HK1980_VS_SCHULTZ2016_DCS_SIX_ANGLES.csv",compare)
    summary=dict(status="DERIVED_NUMERICALLY_CHECKED_PRIMARY_HK1980_PHASE_SCOPED",
        original_input_zip_sha256=SOURCE_SHA,original_phase_member_sha256=phase_sha,
        primary_source="Hunter and Kuriyan 1980 Atomic Data Nucl Data Tables 25 287 original printed phases p298",
        original_HK_energy_eV=[0.1,1.0],physical_rows=4,
        source_phase_cells=674,independent_source="Schultz 2016 Table1 only sparse comparison",
        spin_averaged_joint_operator="NOT_ADMITTED",
        original_full_2016_DCS="NOT_RETRIEVED",Bianchi_tilt="NOT_SOURCE_VERIFIED",
        REI_central="28/88_REPORTED_UNCHANGED",
        REI_working="33/88_REPORTED_UNCHANGED",
        bass_cr_extension="0/3_UNCHANGED",source_mutation=False,production="HOLD",
        finite_l_sensitivity=checks,
        files=[r.name for r in (HERE/"HK1980_PRIMARY_JOINT_4_ROWS.csv",
                                  HERE/"HK1980_VS_SCHULTZ2016_DCS_SIX_ANGLES.csv")])
    (HERE/"RESULT.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    return summary

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source-zip",required=True,type=Path)
    args=a.parse_args()
    print(json.dumps(run(args.source_zip),sort_keys=True))
if __name__=="__main__":main()
