#!/usr/bin/env python3
"""PHYS18: actual source-owned 2p impact angular DCS to polarized Ly-alpha emission.

2p spin-1 density matrix is a POSITIVE SEMIDEFINITE ASSUMPTION FAMILY
rho_xi(qhat)=(1-xi) I3/3 + xi |qhat><qhat|,  -1/2 <= xi <= 1.
NOT Williams-1998 measured lambda/R/I, NOT physical unique atomic density matrix.
Conditioned on a COMMON lab electron incident beam k along +z. Original source
supplies electron energies/rates but NOT incoming electron directions. Therefore
no macroscopic astrophysical polarization is claimed; isotropic axes erase it.
At each source event, electron scattering angle density from Kingston-Fon-Burke
1976 unitarized Born pure-2p table, rates from PHYS17 frozen NIST/Shah source.
Stokes Q sign: Q=I(e_theta)-I(e_phi). U=2Re coherency, V=-2Im.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, sys
from pathlib import Path
import numpy as np
from scipy.special import wofz
from scipy.integrate import simpson
ROOT=Path(__file__).resolve().parent
PARENT=ROOT/'parent'; sys.path.insert(0,str(PARENT))
import phys17_primary_dcs as kfb
import phys16_spectral as old
PARENT_SOURCE_SHA='5fc70cfa638f6b6fffbc61f05f46d28a9be1eefef43851a75bb175383d87666d'
PARENT_SOURCE_FILE=ROOT/'sources'/'PR142_PHYS17_SOURCE.zip'
XI=np.array([-0.5,0.0,0.5,1.0]); THETA=np.linspace(0,180,13)
SPECTRAL_TH=np.array([0.0,90.0,180.0]); SPECTRAL_X=np.linspace(-12,12,81)
PHI=(np.arange(16)+0.5)*2*np.pi/16

def source_rows():
 with (PARENT/'results/SOURCE_UB2P_RECOIL_CROSSWALK.csv').open(newline='') as f: return list(csv.DictReader(f))

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def record_csv(path,rows):
 with path.open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)

def geometry(e):
 p,_=kfb.normalized_angular(e)
 ratio, vrec, erec, err,_=old.exact_recoil(e,kfb.G_MU)
 mu=kfb.G_MU
 qq=np.sqrt(1+ratio*ratio-2*ratio*mu)
 cb=(1-ratio*mu)/qq
 sb=ratio*np.sqrt(1-mu*mu)/qq
 if np.max(abs(cb*cb+sb*sb-1))>2e-13:raise ValueError('Q_DIRECTION_NONUNIT')
 A2=float(np.dot(p,(3*cb*cb-1)/2))
 return p,vrec,cb,sb,A2,err

def moments_from_geometry(p,v,cb,sb,theta_deg,xi):
 """Azimuth-integrated Stokes, photon line-center 1st and 2nd moments before Lorentz convolution."""
 t=np.deg2rad(theta_deg)
 b=cb*np.cos(t);c=sb*np.sin(t)
 az_s2=b*b+c*c/2
 az_s3=b**3+1.5*b*c*c
 az_s4=b**4+3*b*b*c*c+3*c**4/8
 base=1+xi/2
 W0=base-1.5*xi*az_s2
 P=float(p@W0)
 I=P/(4*np.pi)
 z1=float(p@(v*(base*b-1.5*xi*az_s3)))/P
 z2=float(p@(v*v*(base*az_s2-1.5*xi*az_s4)))/P
 mean=z1-old.ETA_EM
 central_variance=.5+z2-z1*z1
 if central_variance<.5-1e-9:raise ValueError('NEGATIVE_CENTRE_VARIANCE')
 A2=float(p@((3*cb*cb-1)/2))
 Q=(3/(8*np.pi))*xi*A2*(np.sin(t)**2)
 # Fixed incident beam axial symmetry and reflection: U=V=0 after electron-scattering azimuth average.
 return I,Q,0.0,0.0,mean,central_variance

def stokes_spectrum(p,v,cb,sb,theta_deg,x=SPECTRAL_X):
 """Frequency-resolved Stokes array [I_iso, I_aligned, Q_aligned] for fixed beam axis.
 Unit per photon, per sr per Doppler x. U,V vanish under azimuth average.
 """
 sgn=1 if theta_deg==0 else -1
 if theta_deg in (0.,180.):
  centre=sgn*v*cb
  profile=np.real(wofz(x[None,:]-centre[:,None]+old.ETA_EM+1j*old.A))/np.sqrt(np.pi)
  spec_i=(p@profile)/(4*np.pi)
  spec_a=(3/(8*np.pi))*((p*(sb**2))@profile)
  spec_q=np.zeros_like(spec_i)
 elif theta_deg==90.:
  cosphi=np.cos(PHI);sinphi=np.sin(PHI)
  centre=v[:,None]*sb[:,None]*cosphi[None,:]
  z=x[None,None,:]-centre[:,:,None]+old.ETA_EM+1j*old.A
  profile=np.real(wofz(z))/np.sqrt(np.pi)
  aligned=(cb[:,None]**2 + sb[:,None]**2*sinphi[None,:]**2)
  qweight=(cb[:,None]**2 - sb[:,None]**2*sinphi[None,:]**2)
  spec_i=np.einsum('i,ijk->k',p,np.mean(profile,axis=1))/(4*np.pi) if False else np.einsum('i,ik->k',p,np.mean(profile,axis=1))/(4*np.pi)
  spec_a=(3/(8*np.pi))*np.einsum('i,ijk,ij->k',p,profile,aligned,optimize=True)/len(PHI)
  spec_q=(3/(8*np.pi))*np.einsum('i,ijk,ij->k',p,profile,qweight,optimize=True)/len(PHI)
 else: raise ValueError('SPECTRUM_ONLY_0_90_180')
 if min(float(np.min(spec_i)),float(np.min(spec_a)))<0:raise ValueError('NEGATIVE_EMISSION_PDF')
 return np.asarray([spec_i,spec_a,spec_q])

def run(out):
 out=Path(out);(out/'results').mkdir(parents=True,exist_ok=True)
 if sha(PARENT_SOURCE_FILE)!=PARENT_SOURCE_SHA:raise ValueError('PARENT_BYTE_IDENTITY')
 cross=source_rows()
 if len(cross)!=2066 or set(x['source'] for x in cross)!={'He'}:raise ValueError('SOURCE_IDENTITY')
 em=np.asarray([float(x['Ee_eV']) for x in cross]);w_ear=np.asarray([float(x['excitation_earliest_m3']) for x in cross]);w_late=np.asarray([float(x['excitation_latest_m3']) for x in cross]);weights=np.array([w_ear,w_late]);totals=weights.sum(axis=1)
 if not np.allclose(totals,[3.3158906934521573e-31,9.85567761064524e-32],rtol=2e-13):raise ValueError('ORIGINAL_EVENTS_CHANGED')
 # [birth=2, xi=4, theta=13, columns I,Q,meanUnnormalized,secondMomentUnnormalized]
 agg=np.zeros((2,len(XI),len(THETA),4),dtype=float)
 spec_agg=np.zeros((2,3,3,3,len(SPECTRAL_X)),dtype=float) # birth, xi={-0.5,0,1}, theta, {I,Q,base},x
 spec_xis=np.array([-.5,0,1.])
 own=[];maxerr=0.
 for i,(e,weight) in enumerate(zip(em,weights.T)):
  p,v,cb,sb,A2,err=geometry(e);maxerr=max(maxerr,err)
  one={'source':cross[i]['source'],'source_atom_index':int(cross[i]['source_atom_index']),'Ee_eV':e,'excitation_earliest_m3':weight[0],'excitation_latest_m3':weight[1],'q_quadrupole_A2':A2,'q_cos2_mean':float(p@(cb*cb)),'q_alignment_polarization_theta90':3*A2/(2+A2),'recoil_mean_vth':float(p@v),'electron_axis':'FIXED_Z_CONDITIONAL'}
  own.append(one)
  for j,xi in enumerate(XI):
   for k,t in enumerate(THETA):
    I,Q,U,V,m,var=moments_from_geometry(p,v,cb,sb,t,xi)
    if not (I>=0 and I+1e-12>=abs(Q)):raise ValueError('STOKES_CONE_VIOLATION')
    agg[:,j,k,0]+=weight*I
    agg[:,j,k,1]+=weight*Q
    agg[:,j,k,2]+=weight*I*m
    agg[:,j,k,3]+=weight*I*(var+m*m)
  for k,t in enumerate(SPECTRAL_TH):
   si,sa,sq=stokes_spectrum(p,v,cb,sb,float(t))
   for j,xi in enumerate(spec_xis):
    flux=(1-xi)*si+xi*sa
    fluxq=xi*sq
    spec_agg[:,j,k,0,:]+=weight[:,None]*flux[None,:]
    spec_agg[:,j,k,1,:]+=weight[:,None]*fluxq[None,:]
    # base source numbers as internal normalization witness, not spectrum
    spec_agg[:,j,k,2,:]+=weight[:,None]*si[None,:]
 # Save science tables
 record_csv(out/'results/SOURCE_2P_ALIGNMENT_MOMENTS.csv',own)
 angular=[]
 for b,policy in enumerate(('earliest','latest')):
  for j,xi in enumerate(XI):
   for k,t in enumerate(THETA):
    I,Q,W1,W2=agg[b,j,k]
    mean=W1/I;var=W2/I-mean*mean
    angular.append(dict(birth_policy=policy,xi_alignment=float(xi),observer_theta_deg=float(t),dN_dOmega_m3_sr=I,dQ_dOmega_m3_sr=Q,dU_dOmega_m3_sr=0,dV_dOmega_m3_sr=0,linear_polarization_QoverI=Q/I,pre_natural_line_centre_mean_x=mean,pre_natural_line_centre_variance_x2=var,gas_K=100,electron_axis='FIXED_Z_CONDITIONAL',original_total_excitation_m3=float(totals[b])))
 record_csv(out/'results/SOURCE_DIRECTIONAL_STOKES_ATLAS.csv',angular)
 spectral=[];spectral_check=[]
 for b,policy in enumerate(('earliest','latest')):
  for j,xi in enumerate(spec_xis):
   for k,t in enumerate(SPECTRAL_TH):
    I,Q,_=spec_agg[b,j,k]
    for x,a,c in zip(SPECTRAL_X,I,Q):
     spectral.append(dict(birth_policy=policy,xi_alignment=float(xi),observer_theta_deg=float(t),x_Doppler=float(x),d2N_dOmega_dx_m3_sr=float(a),d2Q_dOmega_dx_m3_sr=float(c),d2U_dOmega_dx_m3_sr=0,d2V_dOmega_dx_m3_sr=0))
    ktheta=int(np.argmin(abs(THETA-t)));expected=agg[b,int(np.flatnonzero(XI==xi)[0]),ktheta,0]
    got=float(np.trapezoid(I,SPECTRAL_X));spectral_check.append(dict(policy=policy,xi=float(xi),theta=float(t),mass_fraction_x12=got/expected))
 record_csv(out/'results/SOURCE_DIRECTIONAL_STOKES_FREQUENCY_ATLAS.csv',spectral)
 # Isotropic incident electron-axis average gives rho=I/3, so I=N/(4pi) Q=U=V=0 in fixed global basis.
 # The observed Stokes atlas is conditional and NOT a global cosmological prediction.
 result={'unit':'CR_PHYS18_SPIN1_PSD_SOURCE_DIRECTIONAL_LYA_STOKES','source_owner':'PHYS17_PR142_B64D3A0E','source_atoms_original':6400,'qualified_source_events':len(cross),'source_photon_excitation_density_m3':dict(zip(('earliest','latest'),map(float,totals))),'conditional_incident_electron_axis':'FIXED_Z_NO_SOURCE_DIRECTION_OWNER','density_matrix_family':'rho_xi=(1-xi)*I3/3+xi|qhat><qhat|','xi_interval':[-.5,1.],'rho_eigenvalues':['(1+2xi)/3','(1-xi)/3','(1-xi)/3'],'tensor_A2_source_range':[float(min(x['q_quadrupole_A2'] for x in own)),float(max(x['q_quadrupole_A2'] for x in own))], 'source_angular_moments_rows':len(own),'source_angular_stokes_rows':len(angular),'source_frequency_stokes_rows':len(spectral),'spectral_mass_window':spectral_check,'max_nonrel_energy_residual':maxerr,'isotropic_electron_axes':'UNPOLARIZED_ISOTROPIC_AFTER_ROTATIONAL_AVERAGE','physical_sublevel_density_matrix':'UNBOUND','Williams1998_16p5_DCS_and_lambda_R_I':'LITERATURE_SUPPORTED_FIGURES_NOT_NUMERICALLY_INGESTED','Bray1991_13p87_16p46_19p58_lambda_R_I':'LITERATURE_SUPPORTED_THEORY_NOT_NUMERICALLY_INGESTED','original_2p_total_source_rates':'UNCHANGED','full_transport_recoil_detailed_balance':'UNBOUND','common_evolving_gas_radiation_clock_geometry':'UNBOUND','global_He_exclusive':'UNBOUND','physical_K':'UNBOUND','central_DAG':'28/88_DELTA0','extension_DAG':'0/3_DELTA0','R06_distinct_author':'NOT_RUN','C09_distinct_author':'NOT_RUN','production':'HOLD','native25':'HOLD','L4':'HOLD','NO_MERGE':True,'NO_FORCE_PUSH':True,'AUTO_NEXT_NODE':False}
 (out/'results/RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
 print('PHYS18_RESULT',json.dumps({k:result[k] for k in ['qualified_source_events','source_angular_moments_rows','source_angular_stokes_rows','source_frequency_stokes_rows','tensor_A2_source_range','max_nonrel_energy_residual']},sort_keys=True))
 print('SOURCE_POLARIZATION_90_EAR',[(q['xi_alignment'],q['linear_polarization_QoverI']) for q in angular if q['birth_policy']=='earliest' and q['observer_theta_deg']==90])
 print('SPECTRAL_MASS_MIN',min(q['mass_fraction_x12'] for q in spectral_check))
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',default=str(ROOT));a=p.parse_args();run(a.out)
