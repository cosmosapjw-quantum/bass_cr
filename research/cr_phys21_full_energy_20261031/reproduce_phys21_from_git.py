#!/usr/bin/env python3
"""PHYS21: rebuild primary-source 2p source-event angular Stokes science.
Run in a complete checkout of cosmosapjw-quantum/bass_cr.
Requires numpy, scipy. Original immutable PR143 source blob and Bray Tables
III-VI (PR145 72 rows and this branch 48 high-energy rows) are explicit.
This is collision-plane-local E1 emission; global axis/radiative transport unbound.
"""
from __future__ import annotations
import argparse,csv,hashlib,math,json
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.integrate import simpson

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SRC=ROOT/'research/cr_phys18_spin1_polarized_lya_20261031/results/SOURCE_2P_ALIGNMENT_MOMENTS.csv'
LOW=ROOT/'research/cr_phys20_williams_bray_20261031/results/BRAY1991_6CCO_2P_DCS_LAMBDA_R_I.csv'
HIGH=HERE/'results/BRAY1991_PRINTED_35_40_EV_48_STATE_ROWS.csv'
OWNER='d7034188ca5a02dc37db24aaf8f7d550624567bd'
T=np.asarray([0,5,10,15,20,25,30,35,40,45,50,60,70,80,90,100,110,120,130,140,150,160,170,180],float)
G=np.linspace(0,180,721);EDGE=np.r_[0,(T[:-1]+T[1:])/2,180]
ME=9.1093837139e-31;MH=1.6735575e-27;EV=1.602176634e-19;E21=10.1988
J0=3/(8*math.pi);STEP=(math.pi/180)/4

def read(path):
 with Path(path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write(path, rows):
 Path(path).parent.mkdir(parents=True,exist_ok=True)
 with Path(path).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
  w.writeheader();w.writerows(rows)
def source():
 raw=SRC.read_bytes()
 sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 if sha!=OWNER:raise ValueError('SOURCE_GIT_BLOB_DRIFT')
 rows=read(SRC)
 if len(rows)!=2066 or {r['source'] for r in rows}!={'He'}:raise ValueError('SOURCE_OWNER_OR_COUNT')
 if len({(r['source'],r['source_atom_index']) for r in rows})!=2066:raise ValueError('SOURCE_DUPLICATES')
 for f,expect in [('excitation_earliest_m3',3.3158906934521573e-31),
                  ('excitation_latest_m3',9.85567761064524e-32)]:
  if abs(math.fsum(float(r[f]) for r in rows)/expect-1)>1e-11:raise ValueError('RATE_CHANGED')
 return rows
def tables():
 a={}
 for r in read(LOW)+read(HIGH):
  e=float(r['E_eV']);th=int(float(r['theta_e_deg']))
  key=(e,th)
  if key in a:raise ValueError('DUPLICATE_BRAY_INPUT')
  a[key]=[float(r.get('DCS_a0sq_per_sr',r.get('DCS_a0sq_sr'))),
          float(r.get('lambda',r.get('lambda_'))),float(r['R']),float(r['Icorr'])]
 if len(a)!=120:raise ValueError('EXPECTED_FIVE_BY_24_TABLE')
 return a
def exact_q_A2(E):
 pi=math.sqrt(2*ME*EV*E);mu=np.cos(np.deg2rad(G))
 aa=1/ME+1/MH;bb=2*pi*mu/MH
 cc=2*E21*EV+pi*pi/MH-pi*pi/ME
 disc=bb*bb-4*aa*cc
 if np.min(disc)<0:raise ValueError('CLOSED_EXCITATION')
 pf=(bb+np.sqrt(disc))/(2*aa);q2=np.maximum(pi*pi+pf*pf-2*pi*pf*mu,0)
 cb=(pi-pf*mu)/np.sqrt(q2)
 err=(E-E21)*EV-pf*pf/(2*ME)-q2/(2*MH)
 if np.max(np.abs(err)/(E*EV))>1e-12:raise ValueError('TWO_BODY_KINEMATICS')
 return (3*cb*cb-1)/2
def profile(E,top,data,qA2):
 if E>top or E<13.87:raise ValueError('ENERGY_UNBRACKETED')
 es=(13.87,16.46,19.58,top)
 i=0 if E<=16.46 else 1 if E<=19.58 else 2
 x=(E-es[i])/(es[i+1]-es[i])
 rows=np.asarray([[(1-x)*np.log(data[(es[i],int(th))][0])+x*np.log(data[(es[i+1],int(th))][0]),
                   *[(1-x)*data[(es[i],int(th))][j]+x*data[(es[i+1],int(th))][j] for j in (1,2,3)]]
                   for th in T],float)
 d=np.exp(PchipInterpolator(T,rows[:,0])(G))
 lam=np.interp(G,T,rows[:,1]);rr=np.interp(G,T,rows[:,2]);im=np.interp(G,T,rows[:,3])
 if np.max((2*lam-1)**2+8*(rr*rr+im*im))>1+1e-10:raise ValueError('BRAY_RHO_PSD')
 W=d*np.sin(np.deg2rad(G))
 P=np.column_stack([np.ones(len(G)),2*lam-1,-2*np.sqrt(2)*rr,2*np.sqrt(2)*im])
 v=[];qa=[];norm=0
 for j in range(24):
  lo=int(round(EDGE[j]*4));hi=int(round(EDGE[j+1]*4))
  if (hi-lo)%2:raise ValueError('SIMPSON_ODD')
  sub=W[lo:hi+1]
  row=simpson(sub[:,None]*P[lo:hi+1],dx=STEP,axis=0)
  v.append(row);qa.append(simpson(sub*qA2[lo:hi+1],dx=STEP))
  norm+=row[0]
 out=np.asarray(v)/norm
 if max(abs(float(np.sum(out[:,0]))-1),0)>1e-11:raise ValueError('PROBABILITY_NOT_NORMALIZED')
 if np.any(np.linalg.norm(out[:,1:],axis=1)>out[:,0]*(1+1e-11)):raise ValueError('BIN_STOKES_CONE')
 return out,float(np.sum(qa)/norm)
def execute(out):
 own=source();data=tables()
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 moment=[];tail=[[]for _ in range(6)]
 atlas={(birth,upper):np.zeros((24,4))for birth in ('earliest','latest')for upper in (35,40)}
 for r in own:
  E=float(r['Ee_eV']);wa=float(r['excitation_earliest_m3']);wb=float(r['excitation_latest_m3'])
  Q=exact_q_A2(E)
  A,a2=profile(E,35,data,Q);B,b2=profile(E,40,data,Q)
  mA=A[:,1:].sum(axis=0);mB=B[:,1:].sum(axis=0)
  moment.append(dict(source=r['source'],source_atom_index=r['source_atom_index'],Ee_eV=E,
     original_earliest_m3=wa,original_latest_m3=wb,original_KFB_A2=float(r['q_quadrupole_A2']),
     A2_highorder35=a2,A2_highorder40=b2,A2_delta_vs_KFB=a2-float(r['q_quadrupole_A2']),
     A2_delta_high_model=a2-b2,local_P1_high35=mA[0],local_P2_high35=mA[1],local_P3_high35=mA[2],
     local_P1_high40=mB[0],local_P2_high40=mB[1],local_P3_high40=mB[2],
     energy_domain='PUBLISHED_19P58_35_40'if E>19.58 else'PUBLISHED_LOW_6CCO',
     source_scope='PCHIP_LOG_DCS_CONVEX_RHO_SIMPSON_0P25_LOCAL_PLANE_ONLY'))
  for birth,w in [('earliest',wa),('latest',wb)]:
   atlas[(birth,35)]+=J0*w*A
   atlas[(birth,40)]+=J0*w*B
  if E>19.58:
   for j,angle in enumerate(T):
    a,b=A[j],B[j]
    if a[0]<=0 or b[0]<=0:raise ValueError('ZERO_EVENT_ANGLE_BIN')
    tail[j//4].append(dict(source_atom_index=r['source_atom_index'],Ee_eV=E,theta_bin_deg=angle,
      original_earliest_m3=wa,original_latest_m3=wb,
      angle_mass_high35=a[0],lambda_bin_high35=(1+a[1]/a[0])/2,
      R_bin_high35=-a[2]/a[0]/(2*np.sqrt(2)),Icorr_bin_high35=a[3]/a[0]/(2*np.sqrt(2)),
      angle_mass_high40=b[0],lambda_bin_high40=(1+b[1]/b[0])/2,
      R_bin_high40=-b[2]/b[0]/(2*np.sqrt(2)),Icorr_bin_high40=b[3]/b[0]/(2*np.sqrt(2)),
      scope='BRAY1991_6CCO_SOURCE_HIGH_ORDER_BIN_AVERAGED_NOT_GLOBAL'))
 for j in range(2):write(out/f'SOURCE_2066_HIGH_ORDER_EVENT_MOMENTS_PART{j+1}.csv',moment[j*1033:(j+1)*1033])
 for j in range(6):write(out/f'TAIL_456_HIGH_ORDER_4ANGLES_SECTOR_{j+1}.csv',tail[j])
 ar=[]
 for (birth,upper),x in atlas.items():
  target=3.3158906934521573e-31 if birth=='earliest'else 9.85567761064524e-32
  if abs(float(x[:,0].sum())/(J0*target)-1)>1e-11:raise ValueError('SOURCE_RATE_CHANGED')
  for k,th in enumerate(T):
   p=x[k];ar.append(dict(birth=birth,upper_anchor_eV=upper,theta_e_bin_deg=th,
     I_local_m3_sr=p[0],Q_local_m3_sr=p[1],U_local_m3_sr=p[2],V_local_m3_sr=p[3],
     electron_probability_bin=p[0]/(J0*target),scope='CO_ROTATING_COLLISION_PLANE_NOT_GLOBAL'))
 write(out/'SOURCE_24ANGLE_HIGH_ORDER_STOKES_ATLAS.csv',ar)
 print(json.dumps(dict(source_events=len(own),new_tail_events=sum(float(r['Ee_eV'])>19.58 for r in own),
    new_tail_angle_rows=sum(len(v)for v in tail),local_atlas_rows=len(ar),
    source_event_weight_unchanged=True,central_DAG='28/88',extension_DAG='0/3',production='HOLD')))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(HERE/'scratch_reproduce'))
 args=ap.parse_args();execute(args.out)
