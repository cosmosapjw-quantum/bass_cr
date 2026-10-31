#!/usr/bin/env python3
"""PHYS23: collisionless Bianchi I transfer of PHYS22 source-conditioned Ly-alpha.

Exact null geodesic p_i conservation, exact sky Jacobian, parallel transport of
screen coherency, and Gaussian source-line shift. Shear is declared CONDITIONAL,
not an actual cosmological background owned by the source. Original PHYS22 source
weights/chi are immutable, and original collision/production models are unchanged.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.special import wofz

HERE=Path(__file__).resolve().parent
PARENT_NAME='BASS_CR_PHYS22_E1_OBSERVER_FRAME_SCENARIOS_20261031.zip'
PARENT_SHA256='c40decf905f146ebe5e3fe40ba39f59fbf29567819cfc6be4c629e3aaf8f5aa6'
PARENT_GIT_HEAD='fac9a25d53468502b3807da2034e4bfa99325c8f'
ORIGINAL_SOURCE_GIT_BLOB='d7034188ca5a02dc37db24aaf8f7d550624567bd'
E21_EV=10.1988;EV=1.602176634e-19;HPLANCK=6.62607015e-34;C=299792458.0
KB=1.380649e-23;MH=1.6735575e-27;T_K=100.0
NU0=E21_EV*EV/HPLANCK;DNU=NU0*math.sqrt(2*KB*T_K/MH)/C
A21=6.2649e8;VOIGT_A=A21/(4*math.pi*DNU)
SCENARIOS={
 'isotropic_RR_photon_bath':np.array([0.,0.,1.]),
 'unpolarized_collimated_photons_kz':np.array([0.,0.,1.]),
 'ray_quadrupole_alpha_plus2_z':np.array([0.,0.,1.]),
 'ray_quadrupole_alpha_minus1_z':np.array([0.,0.,1.]),
 'linear_polarized_photons_kz_epsx':np.array([1.,0.,0.]),
}
# The integrated shear Delta beta_i between emission and observation (sum=0).
# These are diagnostic backgrounds, NOT the original CR source's Einstein solution.
SHEARS={
 'flrw_zero':np.array([0.,0.,0.]),
 'biax_plus2e-6':np.array([2.e-6,2.e-6,-4.e-6]),
 'biax_minus2e-6':np.array([-2.e-6,-2.e-6,4.e-6]),
 'triax_3e-6':np.array([3.e-6,-3.e-6,0.]),
}
THT=np.array([15.,45.,75.,105.,135.,165.]); PHT=np.array([0.,45.,90.,135.])
OBS_SPECTRAL_TH=(45.,90.,135.);OBS_SPECTRAL_PH=(0.,90.,135.)
XOBS=np.arange(-16.,16.00001,.5)

def validate_parent_zip(zip_path:Path):
 data=zip_path.read_bytes()
 if hashlib.sha256(data).hexdigest()!=PARENT_SHA256:
  raise ValueError('IMMUTABLE_PHYS22_SOURCE_ZIP_SHA256_MISMATCH')

def load_source():
 paths={'RESULT.json':'5e7245cc8d1bea2248ddce240914763a564c08f7592aa109a3edf4b698178fbd','SCENARIO_CHI_FROM_GITHUB.json':'9595a898366c9e3b1999066910a12058558d0335c718cbada77ca5615bef8728'}
 for name,expected in paths.items():
  if hashlib.sha256((HERE/'input'/name).read_bytes()).hexdigest()!=expected:raise ValueError('IMMUTABLE_PHYS22_INPUT_DRIFT_'+name)
 doc=json.loads((HERE/'input'/'RESULT.json').read_text())
 chi=json.loads((HERE/'input'/'SCENARIO_CHI_FROM_GITHUB.json').read_text())
 if doc['original_events']!=2066 or doc['original_source_git_blob_sha1']!=ORIGINAL_SOURCE_GIT_BLOB:raise ValueError('ORIGINAL_EVENT_IDENTITY')
 if doc['source_moment_github_blobs']!=['2846e114b6a2f1a4088894fa7d798ef9c665d983','1cff64adba88cd75b0659acad8849afb0c194f47']:raise ValueError('PHYS21_SOURCE_MOMENTS_DRIFT')
 if len(chi)!=10:raise ValueError('EXPECTED_10_ORIGINAL_SOURCE_CHI_RECORDS')
 weights={'earliest':doc['earliest_excitation_m3'],'latest':doc['latest_excitation_m3']}
 for key,acc in chi.items():
  if not set(acc)=={'earliest','latest'} or any(not (-.5<float(v)<.5)for v in acc.values()):raise ValueError('CHI_OUT_OF_DOMAIN '+key)
 return weights,chi

def build_dirs(mu:np.ndarray,phi:np.ndarray):
 mu=np.asarray(mu);phi=np.asarray(phi)
 m,p=np.meshgrid(mu,phi,indexing='ij');c=m.ravel();v=p.ravel();s=np.sqrt(np.maximum(0,1-c*c));
 n=np.column_stack((s*np.cos(v),s*np.sin(v),c))
 et=np.column_stack((c*np.cos(v),c*np.sin(v),-s))
 ep=np.column_stack((-np.sin(v),np.cos(v),np.zeros_like(v)))
 return n,et,ep

def screen_of_n(n:np.ndarray):
 s=np.hypot(n[:,0],n[:,1]);
 if np.any(s<1e-12):raise ValueError('POLE_BASIS_DEGENERACY')
 ep=np.column_stack((-n[:,1]/s,n[:,0]/s,np.zeros_like(s)))
 et=np.cross(ep,n)
 return et,ep

def photon_dir(t:float,nobs:np.ndarray,db:np.ndarray):
 z=nobs*np.exp((1.-t)*db)[None,:]
 return z/np.linalg.norm(z,axis=1)[:,None]

def rhs(t:float,nobs:np.ndarray,db:np.ndarray,E:np.ndarray):
 n=photon_dir(t,nobs,db)
 a=np.sum(n[:,None,:]*db[None,None,:]*E,axis=2)
 return n[:,None,:]*a[:,:,None]

def transported_screen(nobs:np.ndarray,db:np.ndarray,steps=12):
 gvec=nobs*np.exp(db)[None,:];g=np.linalg.norm(gvec,axis=1)
 nem=gvec/g[:,None];r=1/g
 et0,ep0=screen_of_n(nem);et1,ep1=screen_of_n(nobs)
 if np.max(np.abs(db))==0:
  return nem,r,np.tile(np.eye(2),(len(r),1,1)),et1,ep1,0.
 # Integrate f'_i=n_i sum_j H_j n_j f_j for both screen polarization basis vectors.
 E=np.stack([et0,ep0],axis=1)
 step=1./steps
 for i in range(steps):
  t=i*step
  k1=rhs(t,nobs,db,E)
  k2=rhs(t+step/2,nobs,db,E+step*k1/2)
  k3=rhs(t+step/2,nobs,db,E+step*k2/2)
  k4=rhs(t+step,nobs,db,E+step*k3)
  E=E+(step/6)*(k1+2*k2+2*k3+k4)
 R=np.empty((len(r),2,2))
 for j,etobs in enumerate([et1,ep1]):
  R[:,j,:]=np.sum(etobs[:,None,:]*E,axis=2)
 gram=np.einsum('bij,bik->bjk',R,R)
 d=np.max(np.abs(gram-np.eye(2)))
 if d>1e-10:raise ArithmeticError('SCREEN_NONORTHOGONAL '+str(d))
 return nem,r,R,et1,ep1,d

def output(nobs:np.ndarray,geom,axis:np.ndarray,chi:float,N:float):
 nem,r,R,et,ep,ortherr=geom
 # Original 3D density rho=(1-chi)/3 I +chi a a^T. E1 source emission screen.
 em_et,em_ep=screen_of_n(nem)
 bx=np.stack([np.einsum('ij,j->i',em_et,axis),np.einsum('ij,j->i',em_ep,axis)],axis=-1)
 b=np.einsum('bij,bj->bi',R,bx)
 fac=N*r**3/(8*math.pi)
 Is=fac*(2*(1-chi)+3*chi*np.sum(b*b,axis=1))
 Qs=fac*(3*chi*(b[:,0]**2-b[:,1]**2))
 Us=fac*(6*chi*b[:,0]*b[:,1]);Vs=np.zeros_like(Is)
 if np.any(Is<0) or np.any(np.hypot(Qs,Us)>Is*(1+1e-12)):
  raise ArithmeticError('TRANSVERSE_PSD_FAIL')
 return Is,Qs,Us,Vs

def produce(out:Path, nmu=24, nphi=48):
 out.mkdir(parents=True,exist_ok=True)
 weights,chis=load_source()
 mu,wm=np.polynomial.legendre.leggauss(nmu)
 ph=np.arange(nphi)*2*math.pi/nphi
 no,et,ep=build_dirs(mu,ph)
 ww=np.repeat(wm,nphi)*2*math.pi/nphi
 names=['scenario','upper_anchor_eV','birth','shear','beta_x','beta_y','beta_z','theta_obs_deg','phi_obs_deg','n_em_x','n_em_y','n_em_z','nu_obs_Hz','x_line_centre_obs','redshift_r','dOmega_em_dOmega_obs','I_photons_m3_sr','Q_photons_m3_sr','U_photons_m3_sr','V_photons_m3_sr','QoverI','UoverI','status']
 summary=['scenario','upper_anchor_eV','birth','shear','N_source_m3','N_observer_integrated_m3','relative_number_error','E_emitted_J_m3','E_observed_J_m3','energy_ratio','quadrupole_I_theta_z','max_abs_QoverI','max_abs_UoverI','max_screen_rotation','max_screen_orth_err']
 spectra=['scenario','upper_anchor_eV','birth','shear','theta_obs_deg','phi_obs_deg','x_obs','I_photons_m3_sr_per_x','Q_photons_m3_sr_per_x','U_photons_m3_sr_per_x','line_centre_shift_x','redshift_r']
 rows=[];diagnostics=[];sp=[];all_profs={}
 obsSTheta=np.radians(np.array(OBS_SPECTRAL_TH))
 ns,_,_=build_dirs(np.cos(obsSTheta),np.radians(np.array(OBS_SPECTRAL_PH)))
 # geometric optics map is computed once for each background, reused for all original event weights.
 for shear,db in SHEARS.items():
  if abs(sum(db))>1e-18:raise ValueError('SHEAR_TRACE')
  geom=transported_screen(no,db)
  nem,r,R,et,ep,orth=geom
  if np.max(np.abs(np.sum(nem*nem,axis=1)-1))>=1e-12:raise ValueError('NULL_UNIT_DIRECTION_FAIL')
  jac=r**3
  if abs(np.sum(ww*jac)-4*math.pi)>1e-10:raise ValueError('ANGULAR_JACOBIAN_INTEGRAL')
  # Map 3x3 fundamental null rays to sparse spectral observer set.
  gs=transported_screen(ns,db)
  for scenario,axis in SCENARIOS.items():
   for upper in (35,40):
    for birth,N in weights.items():
     chi=chis[f'{scenario}::{upper}'][birth]
     I,Q,U,V=output(no,geom,axis,chi,N)
     rel=np.sum(ww*I)/N-1
     if abs(rel)>1e-11:raise ArithmeticError('PHOTON_NUMBER_CHANGE '+str(rel))
     ratio=np.sum(ww*I*r)/N
     if not 0.999<ratio<1.001:raise ArithmeticError('ABSURD_SHEAR')
     P2=.5*(3*no[:,2]**2-1)
     qI=np.sum(ww*I*P2)/N
     maxP=np.max(np.abs(Q/I)); maxU=np.max(np.abs(U/I))
     maxRot=np.max(np.abs(np.arctan2(R[:,1,0],R[:,0,0])))
     diagnostics.append([scenario,upper,birth,shear,N,np.sum(ww*I),rel,N*E21_EV*EV,N*E21_EV*EV*ratio,ratio,qI,maxP,maxU,maxRot,orth])
     # Finite angular quadrature: all values are source-weighted, no event owner mutation.
     for j in range(len(no)):
      theta=math.degrees(math.acos(float(np.clip(no[j,2],-1,1))))
      phi=math.degrees(math.atan2(no[j,1],no[j,0]))%360
      shift=(r[j]-1)*NU0/DNU
      rows.append([scenario,upper,birth,shear,*db,theta,phi,*nem[j],r[j]*NU0,shift,r[j],jac[j],I[j],Q[j],U[j],V[j],Q[j]/I[j],U[j]/I[j], 'SOURCE_WEIGHTED_CONDITIONAL_DIAGONAL_BIANCHI_FREE_STREAMING'])
     # Spectral line at a sparse, independently configured sky grid.
     sl=output(ns,gs,axis,chi,N)
     rs=gs[1]
     for k in range(len(ns)):
      theta=math.degrees(math.acos(float(np.clip(ns[k,2],-1,1))))
      phi=math.degrees(math.atan2(ns[k,1],ns[k,0]))%360
      shift=(rs[k]-1)*NU0/DNU
      for x in XOBS:
       # Source 100 K thermal + NIST 2p natural-width Voigt, full x integral=1.
       f=np.real(wofz((x-shift)/rs[k]+1j*VOIGT_A))/(math.sqrt(math.pi)*rs[k])
       sp.append([scenario,upper,birth,shear,theta,phi,x,sl[0][k]*f,sl[1][k]*f,sl[2][k]*f,shift,rs[k]])
     if shear=='flrw_zero':
      # Exact PHYS22 same observer E1 direction, independent no-transport limit.
      if np.max(np.abs(r-1))>1e-14:raise AssertionError('FLRW_REDSHIFT')
      if scenario=='isotropic_RR_photon_bath' and (np.max(np.abs(Q))+np.max(np.abs(U)))>1e-85:raise AssertionError('ISOTROPIC_PHI')
  print('PHASE',shear,'angular='+str(len(rows)),'spectral='+str(len(sp)))
 def save(path,head,body):
  with (out/path).open('w',newline='',encoding='utf-8') as f:
   w=csv.writer(f);w.writerow(head);w.writerows(body)
 save('BIANCHI_3D_SKY_STOKES_92160.csv',names,rows)
 save('BIANCHI_ANGLE_NORMALIZATION_80.csv',summary,diagnostics)
 save('BIANCHI_ANGULAR_LYA_SPECTRA.csv',spectra,sp)
 res=dict(unit='CR_PHYS23_SOURCE_CONDITIONAL_BIANCHI_I_LYA_GEODESIC_SCREEN',original_parent_PR147_sha=PARENT_GIT_HEAD,
    original_source_git_blob_sha1=ORIGINAL_SOURCE_GIT_BLOB,source_events=2066,chi_models=10,
    shear_cases={k:list(map(float,v))for k,v in SHEARS.items()},n_angles=nmu*nphi,full_sky_rows=len(rows),
    diagnostic_rows=len(diagnostics),frequency_rows=len(sp),nu_Lya_Hz=NU0,source_100K_Doppler_width_Hz=DNU,
    sky_number_residual_max=max(abs(a[6])for a in diagnostics),max_screen_orth=max(a[-1] for a in diagnostics),
    source_2p_spontaneous_A21_s=A21,source_voigt_a=VOIGT_A,spectral_source_model='SOURCE_NIST_A21_100K_THERMAL_VOIGT_WITHOUT_ORIGINAL_RECOIL_TRANSPORT',
    model_status='CONDITIONAL_SHEAR_NOT_REAL_CR_BIANCHI_GEOMETRY',source_photons_not_modified=True,
    central_DAG='28/88_DELTA0',extension_DAG='0/3_DELTA0',production='HOLD')
 (out/'RESULT.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
 print('RESULT',json.dumps(res,sort_keys=True))
 return res

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(HERE/'results'));ap.add_argument('--nmu',type=int,default=24);ap.add_argument('--nphi',type=int,default=48);args=ap.parse_args()
 produce(Path(args.out),nmu=args.nmu,nphi=args.nphi)