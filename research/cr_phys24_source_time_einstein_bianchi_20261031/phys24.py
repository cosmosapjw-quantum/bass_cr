#!/usr/bin/env python3
"""PHYS24: source-timed, exact Einstein-dust Bianchi-I Ly-alpha test-photon transfer.

All metric and emission-time bins are declared conditional. The PHYS15 atom-owner
source ledger and PHYS22 ensemble E1 chi are immutable. First HI interaction is a
loss-only opacity, not a redistributed polarized emitted signal.
"""
from __future__ import annotations
import csv, hashlib, json, math
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.special import wofz

ROOT=Path(__file__).resolve().parent
INPUT=ROOT/'input';OUT=ROOT/'results'
G=6.67430e-11;C=299792458.0;KB=1.380649e-23;H=6.62607015e-34;EV=1.602176634e-19
MH=1.6735575e-27; ME=9.1093837139e-31;EPS0=8.8541878128e-12;QE=1.602176634e-19
T_OBS=1.e10;NHI_OBS=138.6;TEMP=100.;E21=10.1988;A21=6.2649e8;FOSC=.41641
NU0=E21*EV/H;DNU=NU0*math.sqrt(2*KB*TEMP/MH)/C; DAMP=A21/(4*math.pi*DNU)
SIGMA_PREF=QE**2*FOSC/(4*EPS0*ME*C*math.sqrt(math.pi)*DNU)
EXPECTED={
 'PHYS15_TIME_LYA_2P_RADIATION_LEDGER.csv':'1d29a8c540ce756b50552b85a8f7af52f1ce7e681dd257a2ee28264c6eb12dd8',
 'PHYS15_TIME_SOURCE_LYA_LEDGER.csv':'4b3460855bfcd78e51948ce5953cc0ff1e847cdf3d9ad2db7a574597977d598e',
 'PHYS22_SCENARIO_CHI.json':'9595a898366c9e3b1999066910a12058558d0335c718cbada77ca5615bef8728',
 'PHYS22_RESULT.json':'5e7245cc8d1bea2248ddce240914763a564c08f7592aa109a3edf4b698178fbd'}
SCENARIOS={'isotropic_RR_photon_bath':np.array([0.,0.,1.]),
'unpolarized_collimated_photons_kz':np.array([0.,0.,1.]),
'ray_quadrupole_alpha_plus2_z':np.array([0.,0.,1.]),
'ray_quadrupole_alpha_minus1_z':np.array([0.,0.,1.]),
'linear_polarized_photons_kz_epsx':np.array([1.,0.,0.])}
CS={'flrw_dust':np.array([0.,0.,0.]),
 'axisymmetric_dust':np.array([2.e-16,2.e-16,-4.e-16]),
 'triaxial_dust':np.array([3.e-16,-3.e-16,0.])}
TIMING={'start':0.,'midpoint':.5,'end':1.}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_csv(path):
 with Path(path).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
 if not rows:raise ValueError('EMPTY_ROWS')
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='',encoding='utf8') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)

def source():
 for p,s in EXPECTED.items():
  if sha(INPUT/p)!=s:raise ValueError('SOURCE_BYTE_IDENTITY_FAILURE '+p)
 result=json.loads((INPUT/'PHYS22_RESULT.json').read_text())
 if result['original_events']!=2066 or result['original_source_git_blob_sha1']!='d7034188ca5a02dc37db24aaf8f7d550624567bd':
  raise ValueError('ORIGINAL_EVENT_SOURCE_IDENTITY_FAILURE')
 chi=json.loads((INPUT/'PHYS22_SCENARIO_CHI.json').read_text())
 if len(chi)!=10:raise ValueError('TEN_ORIGINAL_CHI_EXPECTED')
 rows=read_csv(INPUT/'PHYS15_TIME_LYA_2P_RADIATION_LEDGER.csv')
 if len(rows)!=27:raise ValueError('PHYS15_ORIGINAL_TIME_27_ROWS_REQUIRED')
 by_policy={}
 for b in ('earliest','latest'):
  group=sorted((r for r in rows if r['birth_policy']==b),key=lambda r:float(r['observation_s']))
  times=np.array([float(r['observation_s']) for r in group]);cumul=np.array([float(r['calculated_2p_excitations_m3']) for r in group]);
  lower=np.array([float(r['conditional_emitted_Lya_lower_m3']) for r in group]);
  if len(times)!=9 or not np.array_equal(times,np.arange(9)*1.25e9):raise ValueError('SOURCE_TIME_GRID')
  if np.any(np.diff(cumul)<0) or np.any(lower>cumul) or np.any(lower<0):raise ValueError('SOURCE_CAUSAL_MONOTONICITY')
  if not math.isclose(cumul[-1],float(result[b+'_excitation_m3']),rel_tol=2e-13):raise ValueError('PHYS15_PHYS22_2P_PARITY_'+b)
  by_policy[b]=dict(times=times,amounts=np.diff(cumul),cumulative=cumul,lower=lower)
 rows_by_source=read_csv(INPUT/'PHYS15_TIME_SOURCE_LYA_LEDGER.csv')
 for b,doc in by_policy.items():
  he=[r for r in rows_by_source if r['birth_policy']==b and r['source']=='He']
  h=[r for r in rows_by_source if r['birth_policy']==b and r['source']=='H']
  if len(he)!=9 or len(h)!=9 or any(float(r['H_2p_first_inelastic_m3'])!=0 for r in h):raise ValueError('ORIGINAL_SOURCE_HE_ONLY')
  if not np.allclose([float(r['H_2p_first_inelastic_m3']) for r in he],doc['cumulative'],rtol=1e-13,atol=1e-75):raise ValueError('HE_SOURCE_TIME_PARITY')
 return by_policy,chi

class DustBianchi:
 """Exact diagonal Einstein-dust Bianchi I, Lambda=0, V(T)=1, beta_i(T)=0.
 dV/dt=+sqrt(A V+B), beta_i'=C_i/V, A=24 pi G rho(T), B=3|C|^2/2.
 PHYS15 source held as externally prescribed test-emissivity per observer comoving volume.
 """
 def __init__(self,name,Cs):
  self.name=name;self.cvec=np.asarray(Cs,float)
  if abs(float(self.cvec.sum()))>1e-25:raise ValueError('TRACE_SHEAR')
  self.rho0=NHI_OBS*MH;self.A=24*math.pi*G*self.rho0
  self.B=1.5*float(self.cvec@self.cvec);self.vprime0=math.sqrt(self.A+self.B)
  if self.V(0)<=0:raise ValueError('SINGULAR_BACKGROUND_IN_DOMAIN')
 def V(self,t):
  u=(np.asarray(t,dtype=float)-T_OBS)
  return 1.+self.vprime0*u+(.25*self.A)*u*u
 def Vdot(self,t):return self.vprime0+.5*self.A*(np.asarray(t,dtype=float)-T_OBS)
 @lru_cache(maxsize=1024)
 def Bint(self,t):return quad(lambda x:1./float(self.V(x)),float(t),T_OBS,epsrel=3e-13)[0]
 def beta(self,t):return -self.cvec*self.Bint(float(t))
 def ai(self,t):return float(self.V(t))**(1./3.)*np.exp(self.beta(t))
 def H_i(self,t):return (self.Vdot(t)/(3*self.V(t)))+self.cvec/self.V(t)
 def einstein_resid(self,t):
  v=float(self.V(t));hi=self.H_i(t);Hav=float(np.mean(hi))
  constraint=(3*Hav*Hav-8*math.pi*G*self.rho0/v-0.5*float(np.sum((hi-Hav)**2)))
  scale=max(3*Hav*Hav,1e-99)
  return abs(constraint)/scale
 def local_scale(self,t,nobs):
  """nu(t)/nu(obs) for observer-frame directions, exact p_i constants."""
  f=1./self.ai(t)
  return np.linalg.norm(nobs*f,axis=1)


def build_dirs(mu,phi):
 u,v=np.meshgrid(np.asarray(mu),np.asarray(phi),indexing='ij')
 mu=u.ravel();phi=v.ravel();sn=np.sqrt(np.maximum(0,1-mu*mu))
 n=np.column_stack((sn*np.cos(phi),sn*np.sin(phi),mu))
 et=np.column_stack((mu*np.cos(phi),mu*np.sin(phi),-sn))
 ep=np.column_stack((-np.sin(phi),np.cos(phi),np.zeros_like(phi)))
 return n,et,ep

def screen(n):
 d=np.hypot(n[:,0],n[:,1]);
 if np.min(d)<1e-12:raise ValueError('OBSERVER_SCREEN_POLE')
 ep=np.column_stack((-n[:,1]/d,n[:,0]/d,np.zeros_like(d)))
 return np.cross(ep,n),ep

def get_geom(bg,te,nobs,steps=12):
 emscale=bg.local_scale(te,nobs)
 nem=(nobs/bg.ai(te))/emscale[:,None]
 reff=1./emscale
 es,ep=screen(nem);os,op=screen(nobs)
 vs=bg.V(te)**(1./3.)
 rshear=reff/vs   # nu_o/nu_e=(a_em/a_o)*r_shear
 Jac=rshear**3 # det(B)/|Bn_o|^3, det(B)=(a_o/a_e)^3
 if np.all(bg.cvec==0):
  R=np.broadcast_to(np.eye(2),(len(nobs),2,2)).copy();gram=0.
 else:
  E=np.stack((es,ep),axis=1)
  dt=(T_OBS-te)/steps
  def rhs(t,F):
   nn=(nobs/bg.ai(t));nn/=np.linalg.norm(nn,axis=1)[:,None]
   Cshear=bg.cvec/bg.V(t)
   proj=np.sum(F*(nn*Cshear)[:,None,:],axis=2)
   return nn[:,None,:]*proj[:,:,None]
  for i in range(steps):
   t=te+i*dt
   k1=rhs(t,E);k2=rhs(t+.5*dt,E+.5*dt*k1)
   k3=rhs(t+.5*dt,E+.5*dt*k2);k4=rhs(t+dt,E+dt*k3)
   E+=dt*(k1+2*k2+2*k3+k4)/6
  R=np.empty((len(nobs),2,2))
  for j,e in enumerate((os,op)):R[:,j,:]=np.einsum('ni,nki->nk',e,E)
  gram=float(np.max(np.abs(np.einsum('nij,nik->njk',R,R)-np.eye(2))))
  if gram>1e-11:raise ValueError('SCREEN_GRAM_VIOLATION')
 return (nem,reff,rshear,Jac,R,gram)

def stokes(nobs,geom,axis,chi,N):
 nem,rtot,rshear,jac,R,_=geom
 u,v=screen(nem)
 b=np.stack((u@axis,v@axis),axis=1)
 b=np.einsum('nij,nj->ni',R,b)
 fac=N*jac/(8*math.pi)
 I=fac*(2*(1-chi)+3*chi*np.sum(b*b,axis=1))
 Q=fac*3*chi*(b[:,0]**2-b[:,1]**2)
 U=fac*6*chi*b[:,0]*b[:,1]
 V=np.zeros_like(I)
 if np.any(I<0) or np.any(np.hypot(Q,U)>I*(1+1e-12)):raise ValueError('STOKES_PSD')
 return np.stack((I,Q,U,V),axis=1)

@lru_cache(maxsize=128)
def gauss_nodes(n):return np.polynomial.legendre.leggauss(n)

def optical_depth(bg,te,nobs,xobs,nq=20):
 """First HI interaction opacity along unscattered null path, no redistributed source.
 x_obs is defined using the fixed observer Delta nu; gas temperature 100 K.
 """
 if te>=T_OBS:return np.zeros((len(nobs),len(xobs)))
 gl,ww=gauss_nodes(nq)
 tt=te+(T_OBS-te)*.5*(gl+1)
 tot=np.zeros((len(nobs),len(xobs)))
 for t,w in zip(tt,ww):
  z=bg.local_scale(float(t),nobs)
  x_t=(z[:,None]-1.)*(NU0/DNU)+z[:,None]*xobs[None,:]
  sigma=SIGMA_PREF*np.real(wofz(x_t+1j*DAMP))
  tot+=(.5*(T_OBS-te)*w)*C*NHI_OBS/float(bg.V(t))*sigma
 if np.any(tot<0):raise ValueError('NEGATIVE_OPACITY')
 return tot

def voigt_obs(xobs,rtot):
 shift=(rtot-1.)*(NU0/DNU)
 xem=(xobs[None,:]-shift[:,None])/rtot[:,None]
 return np.real(wofz(xem+1j*DAMP))/(math.sqrt(math.pi)*rtot[:,None])

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 bins,chi=source();backgrounds=[DustBianchi(k,v) for k,v in CS.items()]
 mum,wm=gauss_nodes(24);phi=np.arange(48)*2*math.pi/48
 no,_,_=build_dirs(mum,phi);ww=np.repeat(wm,48)*2*math.pi/48
 ns,_,_=build_dirs(np.cos(np.deg2rad([45.,90.,135.])),np.deg2rad([0.,90.,135.]))
 xobs=np.arange(-16.,16.0001,.5)
 source_bins=[];sky_rows=[];spec_rows=[];time_spec_rows=[];diags=[];history=[]
 for b,book in bins.items():
  for j,val in enumerate(book['amounts']):
   source_bins.append(dict(birth=b,interval=j+1,t_start_s=float(book['times'][j]),t_end_s=float(book['times'][j+1]),
     delta_2p_m3=float(val),cumulative_upper_m3=float(book['cumulative'][j+1]),
     cumulative_lower_m3=float(book['lower'][j+1]),source='He',
     event_clock_owner='PHYS15_27_ROW_ORIGINAL',within_interval_emission_age='UNBOUND'))
 for bg in backgrounds:
  for t in np.linspace(0,T_OBS,41):
   b=bg.beta(t);hi=bg.H_i(t)
   history.append(dict(model=bg.name,t_s=float(t),V_dimensionless=float(bg.V(t)),rho_kg_m3=float(bg.rho0/bg.V(t)),
     ax=float(bg.ai(t)[0]),ay=float(bg.ai(t)[1]),az=float(bg.ai(t)[2]),
     beta_x=float(b[0]),beta_y=float(b[1]),beta_z=float(b[2]),
     H_x_s=float(hi[0]),H_y_s=float(hi[1]),H_z_s=float(hi[2]),Einstein_constraint_relative=bg.einstein_resid(t)))
  for tc,frac in TIMING.items():
   # Source timing and optics are cached per interval, background and policy;
   # no artificial x-dependent ray/source-direction owner is introduced.
   gs=[]
   for j in range(8):
    te=(j+frac)*1.25e9
    skygeom=get_geom(bg,te,no)
    specgeom=get_geom(bg,te,ns)
    tau=optical_depth(bg,te,ns,xobs)
    survival=np.exp(-tau)
    phi_obs=voigt_obs(xobs,specgeom[1])
    gs.append((te,skygeom,specgeom,tau,survival,phi_obs))
   for b,book in bins.items():
    Ntot=float(book['cumulative'][-1]);
    for sc,axis in SCENARIOS.items():
     for anchor in (35,40):
      k=f'{sc}::{anchor}';ch=float(chi[k][b])
      sky=np.zeros((len(no),4));spect=np.zeros((len(ns),len(xobs),4));
      spect_escape=np.zeros_like(spect);photon_energy=0.;screen_max=0.;
      for j,(te,skygeom,specgeom,tau,survival,ph) in enumerate(gs):
       Nj=float(book['amounts'][j])
       if Nj==0:continue
       Ssky=stokes(no,skygeom,axis,ch,Nj)
       sky+=Ssky
       photon_energy+=float(np.dot(ww,Ssky[:,0]*skygeom[1]))
       screen_max=max(screen_max,skygeom[-1],specgeom[-1])
       ss=stokes(ns,specgeom,axis,ch,Nj)
       sbin=ss[:,None,:]*ph[:,:,None]
       spect+=sbin;spect_escape+=sbin*survival[:,:,None]
       if sc in ('isotropic_RR_photon_bath','linear_polarized_photons_kz_epsx') and anchor==35:
        # Sample source-time pulse shapes on a 33-point frequency grid.
        for ray in range(len(ns)):
         for ix in range(0,len(xobs),2):
          time_spec_rows.append(dict(birth=b,scenario=sc,shear=bg.name,timing=tc,interval=j+1,
           t_em_s=float(te),ray=ray,mu_observer=float(ns[ray,2]),x_obs=float(xobs[ix]),
           N_source_bin_m3=Nj,nu_ratio_obs_to_em=float(specgeom[1][ray]),
           tau_first_HI=float(tau[ray,ix]),I_free_m3_sr_per_x=float(sbin[ray,ix,0]),
           I_no_first_scatter_m3_sr_per_x=float(sbin[ray,ix,0]*survival[ray,ix]),
           status='SOURCE_TIME_BIN_EINSTEIN_DUST_CONDITIONAL_FIRST_INTERACTION'))
      Nsky=float(np.dot(ww,sky[:,0]));error=Nsky/Ntot-1
      if abs(error)>5e-11:raise ValueError('SOURCE_COUNT_NONCONSERVATION '+str(error))
      diags.append(dict(birth=b,scenario=sc,Bray_upper_eV=anchor,shear=bg.name,timing=tc,
       N_PHYS15_m3=Ntot,N_sky_m3=Nsky,relative_number_error=float(error),
       energy_ratio=float(photon_energy/Ntot),max_screen_gram=float(screen_max),
       quadrupole_P2_z=float(np.dot(ww,sky[:,0]*.5*(3*no[:,2]**2-1))/Ntot),
       N_scattered_output_claim='NOT_COMPUTED_RII_UNBOUND'))
      for i,n in enumerate(no):
       sky_rows.append(dict(birth=b,scenario=sc,Bray_upper_eV=anchor,shear=bg.name,timing=tc,
        mu_observer=float(n[2]),phi_observer_rad=float(math.atan2(n[1],n[0])%(2*math.pi)),
        I_m3_sr=float(sky[i,0]),Q_m3_sr=float(sky[i,1]),U_m3_sr=float(sky[i,2]),V_m3_sr=float(sky[i,3]),
        QoverI=float(sky[i,1]/sky[i,0]),UoverI=float(sky[i,2]/sky[i,0])))
      for i in range(len(ns)):
       for j,x in enumerate(xobs):
        p=spect[i,j];z=spect_escape[i,j];
        spec_rows.append(dict(birth=b,scenario=sc,Bray_upper_eV=anchor,shear=bg.name,timing=tc,
         ray=i,mu_observer=float(ns[i,2]),x_obs=float(x),
         I_free=float(p[0]),Q_free=float(p[1]),U_free=float(p[2]),V_free=float(p[3]),
         I_no_first_scatter=float(z[0]),Q_no_first_scatter=float(z[1]),U_no_first_scatter=float(z[2]),V_no_first_scatter=float(z[3]),
         first_interaction_removed_I=float(p[0]-z[0]),
         status='FREE_AND_FIRST_INTERACTION_LOSS_NOT_REDISTRIBUTED_SIGNAL'))
   print('COMPLETE',bg.name,tc,'cumulative_sky',len(sky_rows),'freq',len(spec_rows),flush=True)
 write_csv(OUT/'SOURCE_TIME_INTERVAL_INJECTION.csv',source_bins)
 write_csv(OUT/'EINSTEIN_BIANCHI_DUST_BACKGROUND.csv',history)
 write_csv(OUT/'TIME_RESOLVED_SKY_STOKES.csv',sky_rows)
 write_csv(OUT/'TIME_RESOLVED_SPECTRA_FIRST_HI.csv',spec_rows)
 write_csv(OUT/'INTERVAL_EMISSION_SPECTRAL_WITNESS.csv',time_spec_rows)
 write_csv(OUT/'DIAGNOSTICS.csv',diags)
 evidence={
  'unit':'CR_PHYS24_INTERVAL_CONDITIONAL_SOURCE_CLOCK_DUST_BIANCHI_I_FIRST_HI_INTERACTION',
  'source_PHYS15_zip_sha256':'48cda47e966bb0e9309753d4cbb089977218d6f1a364f67a8331fec0f19ba316',
  'source_PHYS23_zip_sha256':'22d97f477199e71e2250b83ceb8fb10914457c343125456d981c0f9f34024111',
  'original_source_blob_sha1':'d7034188ca5a02dc37db24aaf8f7d550624567bd',
  'source_closure':'GLOBAL_PHYS22_CHI_PER_TIME_BIN_UNVALIDATED',
  'cosmology':'EXACT_EINSTEIN_DUST_BIANCHI_I_WITH_PRESCRIBED_CR_TEST_EMISSIVITY',
  'first_HI_scattering':'SURVIVAL_LOSS_ONLY_NO_RII_NO_REEMISSION',
  'clock_closure':'START_MIDPOINT_END_INTERVAL_EMISSION_BRACKET',
  'row_counts':{p:len(rows) for p,rows in [('source_bins',source_bins),('Einstein_background',history),('sky',sky_rows),('spectra',spec_rows),('interval_witness',time_spec_rows),('diagnostics',diags)]},
  'max_relative_count_error':max(abs(float(d['relative_number_error']))for d in diags),
  'max_screen_gram':max(float(d['max_screen_gram'])for d in diags),
  'max_Einstein_constraint_relative':max(float(d['Einstein_constraint_relative'])for d in history),
  'central_DAG':'28/88_DELTA0','extension_DAG':'0/3_DELTA0',
  'PHYS24_auxiliary':'1/1_CONSTRUCTED_SOURCE_CONDITIONAL_REVIEW_HOLD','production':'HOLD',
  'native_subagent':'NOT_RUN','distinct_author_R06_C09':'NOT_RUN',
  'no_merge':True,'no_force_push':True,'auto_next_node':False,
  'files':{p.name:sha(p)for p in sorted(OUT.glob('*.csv'))}}
 (OUT/'RESULT.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
 print('RESULT',json.dumps({k:evidence[k]for k in ('row_counts','max_relative_count_error','max_screen_gram','max_Einstein_constraint_relative')}),flush=True)
 return evidence

if __name__=='__main__':main()
