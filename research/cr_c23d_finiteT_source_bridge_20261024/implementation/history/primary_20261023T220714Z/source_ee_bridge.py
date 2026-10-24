"""C23D saved-source adapter. Imports exact completed provider; no old suite replay."""
import csv,hashlib,importlib.util,math,pathlib
import numpy as np
from scipy.constants import e,epsilon_0,m_e,k,c,h
from scipy.integrate import quad
from scipy.special import gammaincc
PROVIDER_SHA='0fae93ddfd555e1d135606eab51cfe010911c7624f661d27317024cf3f54ba86'
CSV_SHA='f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3'
ROOT=pathlib.Path(__file__).resolve().parents[2]
PROVIDER=ROOT/'cr_stopping_loop_20261024/intake/selected_text/bass_cr/research/cr_coulomb_partition_20261014/coulomb_partition.py'
CSV=ROOT/'n4_resume_transport_20261024/verified_restore/main/repository/research/cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv'
def load_provider():
 raw=PROVIDER.read_bytes();assert len(raw)==3984 and hashlib.sha256(raw).hexdigest()==PROVIDER_SHA
 spec=importlib.util.spec_from_file_location('c23d_reused_provider',PROVIDER);mod=importlib.util.module_from_spec(spec)
 import sys
 sys.modules[spec.name]=mod;spec.loader.exec_module(mod);return mod

def validate(x):
 required=['redshifts','density_cm3','n_e_total_initial_cm3','n_e_thermal_cm3','temperature_K','log_lambda','exposure_s','frame','time_unit','rate_unit','closed_box']
 if any(t not in x for t in required):raise ValueError('missing explicit bath/source field')
 if set(x['density_cm3'])!={'HI','HII','HeI','HeII','HeIII'}:raise ValueError('all five species required')
 if any(not math.isfinite(v) or v<0 for v in x['density_cm3'].values()):raise ValueError('invalid density')
 if any(z not in ['2.316','2.479','2.649'] for z in x['redshifts']):raise ValueError('unknown redshift')
 if x['frame']!='bath_frame_rest_target' or x['time_unit']!='proper_seconds' or x['rate_unit']!='per_absorbing_target_per_proper_second':raise ValueError('unit/frame mismatch')
 if not x['closed_box']:raise ValueError('only declared closed box')
 for t in ['n_e_total_initial_cm3','n_e_thermal_cm3','temperature_K','log_lambda','exposure_s']:
  if not math.isfinite(x[t]) or x[t]<=0:raise ValueError('invalid '+t)
 charge=x['density_cm3']['HII']+x['density_cm3']['HeII']+2*x['density_cm3']['HeIII']
 if not math.isclose(charge,x['n_e_total_initial_cm3'],rel_tol=1e-14) or x['n_e_thermal_cm3']!=x['n_e_total_initial_cm3']:raise ValueError('charge-neutral no-resolved-electron contract mismatch')

def anchor(x):
 validate(x);theta=k*x['temperature_K']/e;ne=x['n_e_thermal_cm3']*1e6;v=math.sqrt(2*e*theta/m_e);Gamma=4*math.pi*ne*(e*e/(4*math.pi*epsilon_0))**2*x['log_lambda']/m_e**2;rate=Gamma/v**3;loss=m_e*Gamma/(e*v)
 debye=math.sqrt(epsilon_0*k*x['temperature_K']/(ne*e*e));sphere=(3/(4*math.pi*ne))**(1/3);lam=h/math.sqrt(2*math.pi*m_e*k*x['temperature_K'])
 return dict(theta_eV=theta,Gamma_SI=Gamma,v_theta_m_s=v,tau_per_s=rate,loss_anchor_eV_s=loss,thermal_relativistic_ratio=theta*e/(m_e*c*c),debye_electron_sphere_occupancy=4*math.pi*ne*debye**3/3,classical_plasma_coupling=e*e/(4*math.pi*epsilon_0*sphere*k*x['temperature_K']),degeneracy=ne*lam**3)

def read_source(x):
 validate(x);raw=CSV.read_bytes();assert len(raw)==1681578 and hashlib.sha256(raw).hexdigest()==CSV_SHA
 rows=list(csv.DictReader(raw.decode().splitlines()));assert len(rows)==32592
 for row in rows:
  if set(row)!={'redshift','channel','kinetic_eV','number_weight_per_target_s'}:raise ValueError('CSV header')
  if row['channel'] not in ['HI','HeI','HeII']:raise ValueError('source channel')
  W=float(row['kinetic_eV']);q=float(row['number_weight_per_target_s'])
  if not math.isfinite(W+q) or W<0 or q<=0:raise ValueError('source domain')
 return rows

def project(W,counts,E):
 if np.any(W<E[0]) or np.any(W>E[-1]):raise ValueError('projection out of finite band')
 hi=np.searchsorted(E,W,side='right');hi=np.minimum(hi,len(E)-1);lo=hi-1;f=(W-E[lo])/(E[hi]-E[lo]);N=np.zeros(len(E));np.add.at(N,lo,counts*(1-f));np.add.at(N,hi,counts*f)
 return N,{'count_relative_residual':abs(N.sum()-counts.sum())/counts.sum(),'energy_relative_residual':abs(E@N-W@counts)/(W@counts),'minimum_weight':float(min(f.min(),(1-f).min()))}

def mfpt_dimensionless(y,chi,R,mod):
 model=mod.MaxwellianCoulomb(1.,2.,1.,20.,False)
 def integrand(z):return (gammaincc(1.5,z)-gammaincc(1.5,R))/(float(model.coefficients(z)[1])*float(model.maxwell_weight(z)))
 vals=[];errors=[]
 for value in y:
  if value<=chi:vals.append(0.);errors.append(0.)
  else:
   val,err=quad(integrand,chi,float(value),epsabs=1e-10,epsrel=1e-9);vals.append(val);errors.append(err)
 return np.array(vals),max(errors)
