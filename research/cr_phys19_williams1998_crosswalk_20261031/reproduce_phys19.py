#!/usr/bin/env python3
"""PHYS19: conditional pure-q collision coherency, measured 54.4-eV method benchmark.
Does NOT digitize Williams 1998 Fig6/7 and does NOT predict cosmological Stokes.
"""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'research/cr_phys18_spin1_polarized_lya_20261031/results/SOURCE_2P_ALIGNMENT_MOMENTS.csv'
SOURCE_GIT_BLOB='d7034188ca5a02dc37db24aaf8f7d550624567bd'
EXCITATION_EV=10.1988
ANGLES=(30,90,150)
# O'Neill et al. PRL 80 (1998) 1632 Table I. These are 54.4 eV measured
# D-target reduced P1,P2 +/- 1sigma; not measured Williams 16.5 eV values.
MEASURED=((2,.459,.048,-.169,.045),(4,.244,.047,-.553,.048),
(6,.052,.029,-.748,.030),(8,-.115,.052,-.762,.056),
(10,-.369,.061,-.681,.068),(15,-.480,.030,-.780,.030),
(20,-.445,.062,-.681,.068),(30,-.120,.090,-.680,.090),
(90,.115,.100,.170,.102),(110,.010,.114,-.169,.113),
(120,.143,.175,-.194,.189))
def born(E, theta):
    if E<=EXCITATION_EV or theta<0 or theta>180: raise ValueError('DOMAIN')
    p=math.sqrt((E-EXCITATION_EV)/E)
    t=theta*math.pi/180
    qz=1-p*math.cos(t);qx=-p*math.sin(t)
    q2=qz*qz+qx*qx
    lam=qz*qz/q2;rr=-qz*qx/(math.sqrt(2)*q2)
    p1=2*lam-1;p2=-2*math.sqrt(2)*rr
    det=lam*(1-lam)-2*rr*rr
    if det<-1e-12 or lam<0 or lam>1:raise ValueError('PSD_FAIL')
    return (lam,rr,0.,p1,p2,0.,det)

def read_source():
    raw=SOURCE.read_bytes()
    computed=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()
    if computed!=SOURCE_GIT_BLOB: raise ValueError('ORIGINAL_SOURCE_GIT_BLOB_MISMATCH')
    rows=list(csv.DictReader(raw.decode('utf-8').splitlines()))
    if len(rows)!=2066:raise ValueError('SOURCE_2066_COUNT')
    if {r['source'] for r in rows}!={'He'}:raise ValueError('SOURCE_OWNER')
    if len({(r['source'],r['source_atom_index']) for r in rows})!=2066:raise ValueError('SOURCE_IDS')
    vals=[[float(r[k]) for r in rows] for k in ('excitation_earliest_m3','excitation_latest_m3')]
    for s,expect in zip(map(math.fsum,vals),(3.3158906934521573e-31,9.85567761064524e-32)):
        if abs(s/expect-1)>1e-11:raise ValueError('SOURCE_RATE_DRIFT')
    return rows

def write(path,fields,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(fields);w.writerows(rows)

def main():
    rows=read_source()
    cols=('source','source_atom_index','Ee_eV','theta_e_deg','lambda_born','R_born','I_born',
      'P1_born','P2_born','P3_born','psd_det','source_earliest_m3','source_latest_m3','parent_KFB_A2','scope')
    for t in ANGLES:
        out=[]
        for r in rows:
            E=float(r['Ee_eV']); vals=born(E,t)
            out.append((r['source'],r['source_atom_index'],r['Ee_eV'],t,
                *(format(v,'.17g') for v in vals),
                r['excitation_earliest_m3'],r['excitation_latest_m3'],
                r['q_quadrupole_A2'],'SOURCE_ENERGY_KFB_OWNER_PURE_Q_BORN_CONDITIONAL_NOT_MEASURED'))
        write(HERE/f'results/SOURCE_2066_BORN_THETA_{t}DEG.csv',cols,out)
    bm=[]
    for ang,p1,s1,p2,s2 in MEASURED:
        la=(1+p1)/2;rr=-p2/(2*math.sqrt(2))
        if p1*p1+p2*p2>1:raise ValueError('MEASURED_CENTRAL_VALUE_OUTSIDE_PSD')
        imax=math.sqrt(1-p1*p1-p2*p2)/(2*math.sqrt(2))
        bm.append((54.4,ang,p1,s1,p2,s2,la,rr,imax,
           'P3_I_NOT_MEASURED','ATOMIC_DEUTERIUM_NOT_SOURCE_H'))
    write(HERE/'results/ONEILL1998_54P4_MEASURED_P1_P2.csv',
      ('Ee_eV','theta_e_deg','measured_P1','sigma_P1','measured_P2','sigma_P2','lambda_from_P1',
       'R_from_P2','abs_I_max_CENTRAL_PSD_ONLY','I_status','target'),bm)
    refs=[(16.5,t,*born(16.5,t)) for t in range(0,181,5)]
    write(HERE/'results/PURE_Q_BORN_REFERENCE_16P5_NOT_MEASURED.csv',
      ('Ee_eV','theta_e_deg','lambda_born','R_born','I_born','P1_born','P2_born','P3_born','psd_det'),refs)
    result=dict(source_original_rows=len(rows),new_source_conditional_rows=len(rows)*len(ANGLES),
      new_measured_high_energy_benchmark_rows=len(bm),new_born_reference_rows=len(refs),
      WILLIAMS1998_FIG6_FIG7_MEASURED_NUMERIC='UNBOUND',
      electron_incidence_source_direction='UNBOUND',physical_full_2p_density_matrix='UNBOUND',
      central_DAG='28/88_DELTA0',extension_DAG='0/3_DELTA0',
      PRODUCTION='HOLD',NATIVE25='HOLD',L4='HOLD',NO_MERGE=True,
      NO_FORCE_PUSH=True,AUTO_NEXT_NODE=False)
    (HERE/'results/RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
