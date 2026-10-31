#!/usr/bin/env python3
"""PHYS20 source-owned 6CCO collision-plane Stokes; no cosmological claim.
Reproduces 2066*3 scoped crosswalk from original source and printed 6CCO tables.
Explicitly does not extrapolate E>19.58 eV or replace NIST/Shah source rates.
"""
from __future__ import annotations
import csv,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/'results'
SRC=ROOT/'research/cr_phys18_spin1_polarized_lya_20261031/results/SOURCE_2P_ALIGNMENT_MOMENTS.csv'
TAB=OUT/'BRAY1991_6CCO_2P_DCS_LAMBDA_R_I.csv'
SRC_GIT_BLOB='d7034188ca5a02dc37db24aaf8f7d550624567bd'
BRAY_ANGLES=(30,90,150);EGRID=(13.87,16.46,19.58)
A0SQ_CM2=(5.29177210903e-9)**2
J0=3/(8*math.pi)
def blob_sha(path):
 raw=path.read_bytes()
 return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()
def read(path):
 with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def lerp(vals,E,logs=False):
 if E<13.87 or E>19.58:raise ValueError('E_OUT_OF_PRIMARY_TABLE_DOMAIN')
 j=0 if E<=16.46 else 1
 t=(E-EGRID[j])/(EGRID[j+1]-EGRID[j])
 return math.exp((1-t)*math.log(vals[j])+t*math.log(vals[j+1])) if logs else (1-t)*vals[j]+t*vals[j+1]
def make():
 if blob_sha(SRC)!=SRC_GIT_BLOB:raise ValueError('PR143_SOURCE_GIT_BLOB_CHANGED')
 atoms=read(SRC)
 if len(atoms)!=2066 or len({(r['source'],r['source_atom_index']) for r in atoms})!=2066 or {r['source'] for r in atoms}!={'He'}:raise ValueError('EVENT_OWNER_COUNT_ID')
 sums=[math.fsum(float(r[k]) for r in atoms) for k in ('excitation_earliest_m3','excitation_latest_m3')]
 for s,t in zip(sums,(3.3158906934521573e-31,9.85567761064524e-32)):
  if abs(s/t-1)>1e-11:raise ValueError('SOURCE_RATE_CHANGED')
 tab=read(TAB)
 if len(tab)!=72:raise ValueError('WRONG_6CCO_ORIGINAL_TABLE_LENGTH')
 tmap={(float(r['E_eV']),int(r['theta_e_deg'])):r for r in tab}
 for theta in BRAY_ANGLES:
  nodes=[tmap[(E,theta)] for E in EGRID]
  cols=('source','source_atom_index','Ee_eV','theta_e_deg','excitation_earliest_m3','excitation_latest_m3','KFB_parent_A2','E_valid_6CCO','DCS_6CCO_cm2_sr','lambda_6CCO','R_6CCO','Icorr_6CCO','conditional_Stokes_I_per_sr','conditional_Stokes_Q_per_sr','conditional_Stokes_U_per_sr','conditional_Stokes_V_per_sr','positive_det','scientific_status')
  output=OUT/f'SOURCE_6CCO_COEHERENCY_THETA_{theta}.csv'
  with output.open('w',newline='',encoding='utf-8') as f:
   w=csv.writer(f,lineterminator='\n');w.writerow(cols)
   for row in atoms:
    E=float(row['Ee_eV'])
    common=[row['source'],row['source_atom_index'],row['Ee_eV'],theta,row['excitation_earliest_m3'],row['excitation_latest_m3'],row['q_quadrupole_A2']]
    if E>19.58:
     w.writerow(common+['false']+['']*9+['E_OUTSIDE_6CCO_TABLE_DO_NOT_EXTRAPOLATE'])
     continue
    d=lerp([float(a['DCS_a0sq_per_sr']) for a in nodes],E,True)
    la=lerp([float(a['lambda']) for a in nodes],E)
    R=lerp([float(a['R']) for a in nodes],E)
    Im=lerp([float(a['Icorr']) for a in nodes],E)
    det=la*(1-la)-2*(R*R+Im*Im)
    if det < -2e-12:raise ValueError('PSD_OUTSIDE')
    stokes=(J0,J0*(2*la-1),J0*(-2*math.sqrt(2)*R),J0*(2*math.sqrt(2)*Im))
    if math.fsum(t*t for t in stokes[1:])>stokes[0]**2*(1+1e-11):raise ValueError('STOKES_CONE')
    w.writerow(common+['true']+[format(z,'.17g') for z in (d*A0SQ_CM2,la,R,Im,*stokes,det)]+['PUBLISHED_6CCO_THEORY_SOURCE_ENERGY_CONDITIONAL_COLLISION_PLANE'])
  print('EXPORTED',output,len(atoms))
if __name__=='__main__':make()
