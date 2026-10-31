#!/usr/bin/env python3
"""Independent physics contract checks for PHYS23 source-conditioned Bianchi I."""
from __future__ import annotations
import unittest,math,csv,sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad,simpson
from scipy.special import wofz
from scipy.integrate import solve_ivp
from phys23 import (load_source,SCENARIOS,SHEARS,build_dirs,screen_of_n,photon_dir,transported_screen,output,NU0,DNU,VOIGT_A,produce,HERE,E21_EV,EV)

class PhysicsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.N,cls.chi=load_source()
 def test_source_provenance(self):
  self.assertEqual(len(self.chi),10)
  self.assertAlmostEqual(self.N['earliest']/3.315890693452162e-31,1,places=13)
  self.assertAlmostEqual(self.N['latest']/9.85567761064523e-32,1,places=13)
 def test_doppler_units(self):
  self.assertAlmostEqual(NU0/2.4660588682175665e15,1,places=12)
  self.assertAlmostEqual(DNU/1.0566205589679062e10,1,places=12)
 def test_shear_trace(self):
  for d in SHEARS.values():self.assertAlmostEqual(float(np.sum(d)),0,places=17)
 def test_momentum_relation(self):
  n,_,_=build_dirs(np.array([-.7,.1,.9]),np.array([0,.7,2.2]))
  for d in SHEARS.values():
   ne,r,R,*_=transported_screen(n,d)
   inv=ne*np.exp(-d)[None,:]
   inv=inv/np.linalg.norm(inv,axis=1)[:,None]
   np.testing.assert_allclose(inv,n,rtol=0,atol=6e-16)
   np.testing.assert_allclose(np.linalg.norm(ne,axis=1),1,atol=8e-16)
 def test_jacobian_exact_analytic(self):
  mu,w=np.polynomial.legendre.leggauss(48)
  n,_,_=build_dirs(mu,np.arange(96)*2*math.pi/96)
  for d in SHEARS.values():
   ne,r,*_=transported_screen(n,d)
   jac=r**3
   area=np.sum(np.repeat(w,96)*(2*math.pi/96)*jac)
   self.assertLess(abs(area/(4*math.pi)-1),1e-13)
 def test_screen_parallel_orthonormal(self):
  n,_,_=build_dirs(np.array([-.7,.1,.9]),np.array([0,.5,1.]))
  for d in SHEARS.values():
   ne,r,R,et,ep,err=transported_screen(n,d,steps=24)
   np.testing.assert_allclose(np.einsum('bij,bkj->bik',R,R),np.tile(np.eye(2),(len(n),1,1)),atol=2e-14)
   self.assertLess(err,2e-14)
 def test_independent_four_vector_parallel_transport(self):
  # Independent 4-vector parallel propagation, including time component;
  # gauge-fix at observer and compare the physical transported 2D screen.
  db=SHEARS['triax_3e-6']
  n,et,ep=build_dirs(np.array([.2]),np.array([.7]))
  nem,r,R,*_=transported_screen(n,db,steps=24)
  et_e,ep_e=screen_of_n(nem)
  for j,start in enumerate((et_e[0],ep_e[0])):
   def ode(t,y):
    f0=y[0];fi=y[1:]
    ni=photon_dir(t,n,db)[0]
    return np.r_[-np.dot(db*ni,fi), -db*ni*f0]
   sol=solve_ivp(ode,(0,1),np.r_[0.,start],rtol=2e-12,atol=2e-13)
   self.assertTrue(sol.success)
   phys=sol.y[1:,-1]-sol.y[0,-1]*n[0]
   screen=np.array([np.dot(phys,et[0]),np.dot(phys,ep[0])])
   np.testing.assert_allclose(screen,R[0,:,j],atol=3e-12,rtol=0)
 def test_no_shear_exact_PHYS22(self):
  source=HERE/'input'/'SOURCE_540_FIXED_OBSERVER_E1_STOKES_ATLAS_REBUILD.csv'
  with source.open(newline='')as f:rows=list(csv.DictReader(f))
  checked=0
  for row in rows:
   theta=float(row['observer_theta_deg']);phi=float(row['observer_phi_deg'])
   if theta==0 or theta==180:continue
   # Individual fixed observer directions, not a common angular quadrature.
   n,_,_=build_dirs(np.array([math.cos(math.radians(theta))]),np.array([math.radians(phi)]))
   geom=transported_screen(n,SHEARS['flrw_zero'])
   scenario=row['scenario'];upper=int(float(row['upper_6CCO_anchor_eV']));birth=row['birth_policy']
   a=SCENARIOS[scenario];chi=self.chi[f'{scenario}::{upper}'][birth]
   I,Q,U,V=output(n,geom,a,chi,self.N[birth]);baseline=np.array([float(row[k])for k in ('I_m3_sr','Q_m3_sr','U_m3_sr','V_m3_sr')])
   np.testing.assert_allclose(np.array([I[0],Q[0],U[0],V[0]])/self.N[birth],baseline/self.N[birth],rtol=1e-12,atol=3e-16)
   checked+=1
  self.assertEqual(checked,420)
 def test_unpolarized_shear_no_Stokes(self):
  n,_,_=build_dirs(np.array([-.7,.1,.8]),np.array([0.,1.,2.]))
  for d in SHEARS.values():
   ge=transported_screen(n,d)
   I,Q,U,V=output(n,ge,SCENARIOS['isotropic_RR_photon_bath'],0,self.N['earliest'])
   self.assertTrue(np.all(Q==0)and np.all(U==0)and np.all(V==0))
   self.assertTrue(np.all(I>0))
 def test_photon_count_integral_4_shear(self):
  mu,w=np.polynomial.legendre.leggauss(32)
  phi=np.arange(64)*2*math.pi/64
  n,_,_=build_dirs(mu,phi);weights=np.repeat(w,64)*2*math.pi/64
  for db in SHEARS.values():
   ge=transported_screen(n,db)
   for scenario in SCENARIOS:
    a=SCENARIOS[scenario];chi=self.chi[f'{scenario}::35']['earliest']
    I,Q,U,V=output(n,ge,a,chi,self.N['earliest'])
    self.assertLess(abs(np.dot(weights,I)/self.N['earliest']-1),1e-12)
    self.assertLess(np.max(np.hypot(Q,U)-I),1e-40)
 def test_source_thermal_voigt_normalization(self):
  for r in [.99,1,1.01]:
   f=lambda x: float(np.real(wofz((x-.3)/r+1j*VOIGT_A))/(math.sqrt(math.pi)*r))
   val,err=quad(f,-np.inf,np.inf,epsabs=1e-9,epsrel=1e-9,limit=200)
   self.assertLess(abs(val-1),3e-8)
 def test_frequency_mapping(self):
  n,_,_=build_dirs(np.array([-.4,.6]),np.array([.2,1.1]))
  for d in SHEARS.values():
   ne,r,*_=transported_screen(n,d)
   delta_nu=(r-1)*NU0
   delta_x=(r-1)*NU0/DNU
   np.testing.assert_allclose(delta_nu/DNU,delta_x,atol=1e-15)
 def test_small_shear_quadrupole(self):
  s=2e-6;d=SHEARS['biax_plus2e-6'];mu,w=np.polynomial.legendre.leggauss(48);ph=np.arange(72)*2*math.pi/72
  n,_,_=build_dirs(mu,ph);W=np.repeat(w,72)*2*math.pi/72
  ge=transported_screen(n,d)
  I,*_=output(n,ge,SCENARIOS['isotropic_RR_photon_bath'],0.,1.)
  P2=(3*n[:,2]**2-1)/2
  q=np.dot(W,I*P2)
  self.assertLess(abs(q/s-(6/5)),2e-5)
 def test_triax_screen_rotation_nonzero(self):
  n,_,_=build_dirs(np.array([-.7,.2,.8]),np.array([.5,.9,1.2]))
  R=transported_screen(n,SHEARS['triax_3e-6'])[2]
  self.assertGreater(np.max(np.abs(R[:,0,1])),1e-8)
 def test_no_unphysical_polarization(self):
  mu=np.array([-.7,-.2,.3,.85]);phi=np.array([0.,.3,1.3])
  n,_,_=build_dirs(mu,phi)
  for d in SHEARS.values():
   ge=transported_screen(n,d)
   for name,a in SCENARIOS.items():
    for hi in (35,40):
     I,Q,U,V=output(n,ge,a,self.chi[f'{name}::{hi}']['earliest'],self.N['earliest'])
     self.assertTrue(np.all(np.hypot(Q,U)<=I*(1+1e-12)))
 def test_spectral_lorentz_tail(self):
  f=lambda x: np.real(wofz(x+1j*VOIGT_A))/math.sqrt(math.pi)
  xs=np.linspace(-16,16,1601)
  mass=simpson(f(xs),x=xs)
  self.assertTrue(.9997<mass<1)
 def test_saved_80_cases(self):
  with (HERE/'results'/'BIANCHI_ANGLE_NORMALIZATION_80.csv').open(newline='') as f:r=list(csv.DictReader(f))
  self.assertEqual(len(r),80)
  for item in r:
   self.assertLess(abs(float(item['relative_number_error'])),1e-12)
   self.assertLess(float(item['max_screen_orth_err']),1e-12)
 def test_saved_92160(self):
  import pandas as pd
  d=pd.read_csv(HERE/'results'/'BIANCHI_3D_SKY_STOKES_92160.csv')
  self.assertEqual(len(d),92160)
  self.assertEqual(d['shear'].nunique(),4)
  self.assertLess(float((np.hypot(d['Q_photons_m3_sr'],d['U_photons_m3_sr'])>d['I_photons_m3_sr']*(1+1e-12)).sum()),1)
 def test_saved_spectrum_count(self):
  import pandas as pd
  d=pd.read_csv(HERE/'results'/'BIANCHI_ANGULAR_LYA_SPECTRA.csv')
  self.assertEqual(len(d),46800)
  self.assertEqual(d['x_obs'].nunique(),65)

if __name__=='__main__':unittest.main(verbosity=2)