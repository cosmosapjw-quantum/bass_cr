#!/usr/bin/env python3
"""PHYS22 E1 photoelectron angular scenarios into a fixed observer Stokes frame.

Reproduce 2066 original He-origin H 1s→2p source-weighted scenario calculations.
SOURCE DIRECTIONS/PHOTON POLARIZATION WERE NOT STORED BY THE ORIGINAL RR SOURCE.
This is explicitly conditional, NOT a global Bianchi astrophysical prediction.
Input: immutable PHYS18 2066 source Git blob, PHYS21 HIGH_ORDER 2*1033 events.
Bray 1991 6CCO P1=2lambda-1 is integrated in the PHYS21 source moments.
"""
from __future__ import annotations
import csv,hashlib,math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
SRC=ROOT/'research/cr_phys18_spin1_polarized_lya_20261031/results/SOURCE_2P_ALIGNMENT_MOMENTS.csv'
MOMS=[ROOT/f'research/cr_phys21_full_energy_20261031/results/SOURCE_2066_HIGH_ORDER_EVENT_MOMENTS_PART{i}.csv' for i in (1,2)]
SHA1='d7034188ca5a02dc37db24aaf8f7d550624567bd'
SCENARIOS={
'isotropic_RR_photon_bath':(0,(0,0,1)),
'unpolarized_collimated_photons_kz':(-1,(0,0,1)),
'ray_quadrupole_alpha_plus2_z':(-.4,(0,0,1)),
'ray_quadrupole_alpha_minus1_z':(.2,(0,0,1)),
'linear_polarized_photons_kz_epsx':(2,(1,0,0))}
TH=(0,30,45,60,90,120,135,150,180);PH=(0,45,90)
N={'earliest':3.3158906934521573e-31,'latest':9.85567761064524e-32}
def read(f):
 with Path(f).open(newline='',encoding='utf-8')as io:return list(csv.DictReader(io))
def write(f,rows):
 if not rows:raise ValueError('NO_ROWS')
 Path(f).parent.mkdir(parents=True,exist_ok=True)
 with Path(f).open('w',newline='',encoding='utf-8')as io:
  w=csv.DictWriter(io,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def dot(a,b):return math.fsum(x*y for x,y in zip(a,b))
def stokes(p1,beta,axis,theta,phi,weight):
 t=math.radians(theta);p=math.radians(phi);ct=math.cos(t);st=math.sin(t);cp=math.cos(p);sp=math.sin(p)
 n=(st*cp,st*sp,ct);et=(ct*cp,ct*sp,-st);ep=(-sp,cp,0)
 lamb=(1+p1)/2;chi=beta*(3*lamb-1)/10
 cn=dot(axis,n);aa=dot(axis,et);bb=dot(axis,ep);P2=(3*cn*cn-1)/2
 v=weight/(4*math.pi)
 I=v*(1-chi*P2);Q=1.5*v*chi*(aa*aa-bb*bb);U=3*v*chi*aa*bb;V=0.
 if I<0 or math.hypot(Q,U,V)>I*(1+2e-12):raise ValueError('STOKES_NOT_PSD')
 return I,Q,U,V,chi
def events():
 raw=SRC.read_bytes();sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 if sha!=SHA1:raise ValueError('ORIGINAL_PHYS18_SOURCE_DRIFT')
 source=read(SRC);parents=[r for f in MOMS for r in read(f)]
 if len(source)!=2066 or len(parents)!=2066:raise ValueError('ROW_COUNT_CHANGED')
 owners={(r['source'],r['source_atom_index']):r for r in source}
 if len(owners)!=2066:raise ValueError('DUPLICATE_SOURCE_ID')
 for r in parents:
  k=(r['source'],r['source_atom_index']);o=owners.get(k)
  if o is None or r['source']!='He':raise ValueError('OWNER')
  for a,b in [('Ee_eV','Ee_eV'),('excitation_earliest_m3','original_earliest_m3'),('excitation_latest_m3','original_latest_m3')]:
   if not math.isclose(float(o[a]),float(r[b]),rel_tol=1e-14,abs_tol=1e-45):raise ValueError('SOURCE_EVENT_DRIFT')
  for k in ('local_P1_high35','local_P1_high40'):
   if not -1.000000000001<=float(r[k])<=1.000000000001:raise ValueError('INVALID_BRAY_P1')
 for birth in N:
  if abs(math.fsum(float(r['original_'+birth+'_m3'])for r in parents)/N[birth]-1)>1e-11:raise ValueError('SOURCE_WEIGHT_DRIFT')
 return parents
def run():
 own=events();out=HERE/'results';out.mkdir(exist_ok=True)
 atlas=[]
 for scenario,(beta,axis) in SCENARIOS.items():
  for upper in (35,40):
   rr=[];aggregates={(birth,theta,phi):[0.,0.,0.,0.]for birth in N for theta in TH for phi in PH}
   for r in own:
    p1=float(r['local_P1_high'+str(upper)])
    a=stokes(p1,beta,axis,60,45,float(r['original_earliest_m3']))
    b=stokes(p1,beta,axis,60,45,float(r['original_latest_m3']))
    rr.append(dict(source=r['source'],source_atom_index=r['source_atom_index'],Ee_eV=r['Ee_eV'],
      original_earliest_m3=r['original_earliest_m3'],original_latest_m3=r['original_latest_m3'],
      scenario=scenario,electron_direction_beta=beta,axis_x=axis[0],axis_y=axis[1],axis_z=axis[2],
      Bray_upper_anchor_eV=upper,local_P1=p1,chi_directional=a[4],observer_theta_deg=60,observer_phi_deg=45,
      earliest_I_m3_sr=a[0],earliest_Q_m3_sr=a[1],earliest_U_m3_sr=a[2],earliest_V_m3_sr=a[3],
      latest_I_m3_sr=b[0],latest_Q_m3_sr=b[1],latest_U_m3_sr=b[2],latest_V_m3_sr=b[3],
      source_scope='E1_CONDITIONAL_ORIGINAL_PHOTON_DIRECTIONS_UNBOUND'))
    for birth in N:
     w=float(r['original_'+birth+'_m3'])
     for theta in TH:
      for phi in PH:
       v=stokes(p1,beta,axis,theta,phi,w)
       dest=aggregates[(birth,theta,phi)]
       for j in range(4):dest[j]+=v[j]
   write(out/f'EVENT_2066_{scenario.upper()}_ANCHOR{upper}.csv',rr)
   for (birth,theta,phi),v in aggregates.items():
    I,Q,U,V=v
    atlas.append(dict(scenario=scenario,Bray_upper_anchor_eV=upper,birth_policy=birth,
        observer_theta_deg=theta,observer_phi_deg=phi,I_m3_sr=I,Q_m3_sr=Q,U_m3_sr=U,V_m3_sr=V,
        QoverI=Q/I,UoverI=U/I,VoverI=V/I,original_N2p_m3=N[birth],
        scope='FIXED_OBSERVER_E1_SCENARIO_NO_ORIGINAL_RAY_OWNER'))
 write(out/'SOURCE_540_FIXED_OBSERVER_E1_STOKES_ATLAS.csv',atlas)
 r=dict(original_source_events=len(own),per_event_scenario_rows=len(own)*len(SCENARIOS)*2,
        fixed_observer_atlas_rows=len(atlas),main_DAG='28/88_DELTA0',extension_DAG='0/3_DELTA0',
        actual_source_photoelectron_direction='UNBOUND',physical_full_2p_rho='UNBOUND',
        production='HOLD',NO_MERGE=True,NO_FORCE_PUSH=True,AUTO_NEXT_NODE=False)
 (out/'RESULT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
 print(json.dumps(r,sort_keys=True))
if __name__=='__main__':run()
