#!/usr/bin/env python3
"""Focused PHYS24 mathematics, provenance, transfer, and saved-output regression tests."""
import csv, json, math, shutil, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.integrate import quad
import phys24 as p

class Phys24Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s, cls.chi=p.source()
  cls.bg={k:p.DustBianchi(k,v) for k,v in p.CS.items()}

 def test_01_original_source_identity_and_photon_count(self):
  self.assertEqual(len(self.chi),10)
  self.assertEqual(set(self.s),{'earliest','latest'})
  for b,N in [('earliest',3.315890693452162e-31),('latest',9.85567761064523e-32)]:
   self.assertAlmostEqual(self.s[b]['cumulative'][-1]/N,1,places=12)
   self.assertAlmostEqual(sum(self.s[b]['amounts'])/N,1,places=12)
   self.assertTrue(np.all(self.s[b]['amounts']>=0))

 def test_02_time_bin_source_no_fabrication(self):
  rows=p.read_csv(p.OUT/'SOURCE_TIME_INTERVAL_INJECTION.csv')
  self.assertEqual(len(rows),16)
  for row in rows:
   self.assertEqual(row['source'],'He')
   self.assertEqual(row['within_interval_emission_age'],'UNBOUND')
   self.assertLessEqual(float(row['cumulative_lower_m3']),float(row['cumulative_upper_m3']))

 def test_03_immutable_source_mutation_fails(self):
  with tempfile.TemporaryDirectory() as td:
   target=Path(td)
   for name in p.EXPECTED: shutil.copyfile(p.INPUT/name,target/name)
   f=target/'PHYS22_RESULT.json';f.write_bytes(f.read_bytes()+b' ')
   with patch.object(p,'INPUT',target),self.assertRaisesRegex(ValueError,'SOURCE_BYTE_IDENTITY_FAILURE'):
    p.source()

 def test_04_dust_exact_hamiltonian_and_shear_sum(self):
  for bg in self.bg.values():
   for t in np.linspace(0,p.T_OBS,13):
    self.assertGreater(bg.V(t),0)
    self.assertLess(bg.einstein_resid(float(t)),1e-12)
    self.assertLess(abs(sum(bg.beta(float(t)))),1e-20)
    self.assertLess(abs(sum(bg.H_i(float(t))-np.mean(bg.H_i(float(t))))),1e-23)

 def test_05_dust_spatial_einstein_pressure_free(self):
  # For each i, spatial Einstein equation: Hdot_j+Hdot_k+H_j^2+H_k^2+H_j H_k=0.
  for bg in self.bg.values():
   for t in (0.,5e9,1e10):
    v=float(bg.V(t));dv=float(bg.Vdot(t));ddv=.5*bg.A
    h=bg.H_i(t)
    dh=ddv/(3*v)-dv*dv/(3*v*v)-bg.cvec*dv/(v*v)
    for j,k in ((1,2),(0,2),(0,1)):
     residual=dh[j]+dh[k]+h[j]**2+h[k]**2+h[j]*h[k]
     scale=max(float(np.max(h*h)),1e-40)
     self.assertLess(abs(residual)/scale,1e-12)

 def test_06_photon_covariant_momenta_and_null_redshift(self):
  n,_,_=p.build_dirs(np.array([.1,.71]),np.array([.3,1.2]))
  for bg in self.bg.values():
   for t in (1.25e9,6.3e9):
    a=bg.ai(t);nu=bg.local_scale(t,n);direc=(n/a)/nu[:,None]
    np.testing.assert_allclose(a[None,:]*direc*nu[:,None],n,rtol=0,atol=5e-16)
    self.assertLess(np.max(np.abs(np.sum(direc*direc,axis=1)-1)),2e-15)

 def test_07_solid_angle_jacobian_and_full_sky(self):
  mu,weights=p.gauss_nodes(24);n,_,_=p.build_dirs(mu,np.arange(48)*2*math.pi/48)
  W=np.repeat(weights,48)*2*math.pi/48
  for bg in self.bg.values():
   for t in (1.25e9,6.25e9):
    ge=p.get_geom(bg,t,n)
    self.assertLess(abs(float(np.dot(W,ge[3]))/(4*math.pi)-1),4e-14)
    expected=ge[1]**3/bg.V(t)
    np.testing.assert_allclose(ge[3],expected,rtol=2e-15,atol=1e-15)

 def test_08_screen_transversality_and_rotation(self):
  n,_,_=p.build_dirs(np.array([-.7,.2,.9]),np.array([.2,1.7]))
  for bg in self.bg.values():
   ge=p.get_geom(bg,1.3e9,n)
   R=ge[4]
   np.testing.assert_allclose(np.einsum('nij,nik->njk',R,R),np.broadcast_to(np.eye(2),R.shape),rtol=0,atol=2e-12)
   self.assertLess(ge[-1],2e-12)

 def test_09_flrw_and_isotropic_zero_polarization(self):
  n,_,_=p.build_dirs(np.array([-.4,.35]),np.array([.5,1.]))
  for bg in self.bg.values():
   ge=p.get_geom(bg,1.25e9,n)
   IQUV=p.stokes(n,ge,p.SCENARIOS['isotropic_RR_photon_bath'],0.,1.)
   np.testing.assert_array_equal(IQUV[:,1:],0.)
   np.testing.assert_allclose(IQUV[:,0],ge[3]/(4*math.pi),rtol=1e-14)
   if bg.name=='flrw_dust':
    np.testing.assert_allclose(ge[3],1.,rtol=0,atol=1e-14)

 def test_10_e1_emission_psd_and_photon_normalization(self):
  mu,w=p.gauss_nodes(20);n,_,_=p.build_dirs(mu,np.arange(40)*2*math.pi/40)
  W=np.repeat(w,40)*2*math.pi/40
  for bg in self.bg.values():
   ge=p.get_geom(bg,4.75e9,n)
   for key,axis in p.SCENARIOS.items():
    for b in self.s:
     S=p.stokes(n,ge,axis,float(self.chi[key+'::35'][b]),1.)
     self.assertLess(abs(float(np.dot(W,S[:,0]))-1),1e-11)
     self.assertTrue(np.all(S[:,0]>=np.hypot(S[:,1],S[:,2])*(1-1e-12)))
     np.testing.assert_array_equal(S[:,3],0.)

 def test_11_line_profile_frequency_jacobian(self):
  for r in (.98,1.,1.02):
   shift=(r-1.)*p.NU0/p.DNU
   # Integrate in the comoving line-centered coordinate; direct uncentered
   # infinite-interval QUADPACK misses the narrow shifted peak for r != 1.
   def integrand(y):
    x=shift+r*y
    return float(r*p.voigt_obs(np.array([x]),np.array([r]))[0,0])
   value,err=quad(integrand,-np.inf,np.inf,epsabs=1e-9,epsrel=1e-9,limit=250)
   self.assertLess(abs(value-1.),3e-8)

 def test_12_first_HI_survival_monotone_by_emission_time(self):
  n,_,_=p.build_dirs(np.array([.2]),np.array([.8]))
  x=np.array([-4.,0.,4.,10.]);bg=self.bg['axisymmetric_dust']
  old=p.optical_depth(bg,1.25e9,n,x,nq=28)
  new=p.optical_depth(bg,5e9,n,x,nq=28)
  self.assertTrue(np.all(old>=new))
  self.assertTrue(np.all(new>=0))
  self.assertTrue(np.all(np.exp(-old)<=1))
  self.assertTrue(np.all(np.exp(-old)>=0))
  np.testing.assert_equal(p.optical_depth(bg,p.T_OBS,n,x),0.)

 def test_13_optical_depth_static_limit(self):
  # For an exactly stationary reference gas, q=c nHI sigma(x) and tau=q*dt.
  n,_,_=p.build_dirs(np.array([.0]),np.array([.0]))
  dt=1e3
  bg=self.bg['flrw_dust']; x=np.array([0.,10.])
  tau=p.optical_depth(bg,p.T_OBS-dt,n,x)
  expect=p.C*p.NHI_OBS*p.SIGMA_PREF*np.real(p.wofz(x+1j*p.DAMP))*dt
  np.testing.assert_allclose(tau[0],expect,rtol=2e-6,atol=1e-12)

 def test_14_saved_diagnostics_and_counts(self):
  d=p.read_csv(p.OUT/'DIAGNOSTICS.csv')
  self.assertEqual(len(d),180)
  self.assertEqual(len(p.read_csv(p.OUT/'SOURCE_TIME_INTERVAL_INJECTION.csv')),16)
  for rec in d:
   self.assertLess(abs(float(rec['relative_number_error'])),5e-11)
   self.assertLess(float(rec['max_screen_gram']),1e-11)
   self.assertEqual(rec['N_scattered_output_claim'],'NOT_COMPUTED_RII_UNBOUND')

 def test_15_saved_count_and_original_provenance(self):
  res=json.loads((p.OUT/'RESULT.json').read_text())
  self.assertEqual(res['row_counts'],{'source_bins':16,'Einstein_background':123,'sky':207360,'spectra':105300,'interval_witness':74844,'diagnostics':180})
  self.assertEqual(res['source_closure'],'GLOBAL_PHYS22_CHI_PER_TIME_BIN_UNVALIDATED')
  self.assertEqual(res['cosmology'],'EXACT_EINSTEIN_DUST_BIANCHI_I_WITH_PRESCRIBED_CR_TEST_EMISSIVITY')
  for file, digest in res['files'].items():self.assertEqual(p.sha(p.OUT/file),digest)

 def test_16_saved_first_interaction_always_loss(self):
  with (p.OUT/'TIME_RESOLVED_SPECTRA_FIRST_HI.csv').open(newline='') as f:
   rr=csv.DictReader(f);ct=0
   for r in rr:
    ct+=1
    I=float(r['I_free']);surv=float(r['I_no_first_scatter']);removed=float(r['first_interaction_removed_I'])
    self.assertGreaterEqual(I,0.)
    self.assertLessEqual(surv,I*(1+1e-13)+1e-100)
    self.assertGreaterEqual(removed,0.)
    self.assertLess(abs((surv+removed-I))/max(I,1e-80),2e-15)
   self.assertEqual(ct,105300)

 def test_17_original_emitted_lower_upper_and_2p_delay(self):
  rr=p.read_csv(p.INPUT/'PHYS15_TIME_LYA_2P_RADIATION_LEDGER.csv')
  for row in rr:
   if row['birth_policy'] not in ('earliest','latest'):continue
   upper=float(row['conditional_new_Lya_photons_upper_m3'])
   lower=float(row['conditional_emitted_Lya_lower_m3'])
   pop=float(row['conditional_unemitted_2p_upper_m3'])
   self.assertGreaterEqual(upper,lower)
   self.assertGreaterEqual(pop,0.)
   self.assertLessEqual(upper-lower,max(pop*1.01,1e-60))

 def test_18_first_HI_gauss_quadrature_convergence(self):
  n,_,_=p.build_dirs(np.array([-.4,.2,.8]),np.array([.2,1.7]))
  x=np.array([-4.,0.,3.,10.])
  for bg in self.bg.values():
   for t in (0.,5e9,9.5e9):
    q20=p.optical_depth(bg,t,n,x,nq=20)
    q64=p.optical_depth(bg,t,n,x,nq=64)
    self.assertLess(float(np.max(np.abs(q20-q64)/np.maximum(1.,q64))),1e-9)

if __name__=='__main__':unittest.main(verbosity=2)
