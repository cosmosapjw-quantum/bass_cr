import sys, unittest, math, tempfile, shutil, hashlib, os
from pathlib import Path
import numpy as np
import pandas as pd

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'src'))
from receiver_tau import calculate,load,_tau_visibility,C_M_S,SIGMA_T_M2
SOURCE=Path(os.getenv('REI_SOURCE_ZIP',BASE/'REI_F4_CCC_HHE_FIRST_COLLISION_20261031_FULL.zip'))

class ReceiverContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=Path(tempfile.mkdtemp(prefix='tau_test_'))
  cls.stats,cls.d=calculate(SOURCE,cls.tmp)
  cls.p,cls.t,cls.s,cls.a=load(SOURCE)
 @classmethod
 def tearDownClass(cls):shutil.rmtree(cls.tmp)
 def test_source_rows_and_physical_window(self):
  self.assertEqual((len(self.p),len(self.t),len(self.s),len(self.a)),(193,192,192,192))
  self.assertAlmostEqual(float(self.p.z.iloc[0]),20,places=12)
  self.assertAlmostEqual(float(self.p.z.iloc[-1]),2,places=12)
 def test_conservation_identity(self):
  for lane in ['full21_saved','instant_static_star','HHe_component']:
   r=self.stats['totals'][lane]
   self.assertLess(r['visibility_telescoping_abs_error'],2e-14)
   self.assertAlmostEqual(r['finite_window_transmission']+r['finite_window_scattering_probability'],1,places=13)
 def test_signs_and_positive_rates(self):
  for name in ['dtau_full_saved_trap','dtau_static_star_trap','dtau_HHe_trap','finite_window_bin_visibility_saved','finite_window_bin_visibility_star']:
   self.assertTrue(np.isfinite(self.d[name]).all());self.assertGreaterEqual(float(self.d[name].min()),0)
 def test_full21_HHe_correspondence_not_identity(self):
  diff=self.stats['diagnostics']['max_rel_HHe_vs_full21_saved_end']
  self.assertGreater(diff,0)
  self.assertLess(diff,1e-3)
  self.assertLess(self.stats['diagnostics']['max_rel_HHe_projection_vs_arrival'],2e-12)
 def test_distinct_static_closure(self):
  a=self.stats['totals']['full21_saved']['tau_trapezoid'];b=self.stats['totals']['instant_static_star']['tau_trapezoid']
  self.assertGreater(b,a)
  self.assertLess(abs(b/a-1-.04411),3e-4)
 def test_source_clock_and_redshift_adjacency(self):
  self.assertTrue((self.d.proper_dt_s>0).all())
  self.assertLess(float(np.max(abs(self.d.z_low.values[:-1]-self.d.z_high.values[1:]))),1e-11)
 def test_trapezoid_formula_independent(self):
  d=self.d
  direct=C_M_S*SIGMA_T_M2*.5*(d.ne_full21_saved_start_m3+d.ne_full21_saved_end_m3)*d.proper_dt_s
  np.testing.assert_allclose(d.dtau_full_saved_trap,direct,rtol=1e-14,atol=0)
 def test_exact_discrete_visibility_telescoping(self):
  for k in ['saved','star']:
   delta=self.d[f'dtau_full_saved_trap'] if k=='saved' else self.d['dtau_static_star_trap']
   remaining=np.cumsum(delta.to_numpy()[::-1])[::-1]
   p=np.exp(-np.r_[remaining[1:],0])-np.exp(-remaining)
   observed=self.d[f'finite_window_bin_visibility_{k}']
   np.testing.assert_allclose(observed,p,rtol=0,atol=2e-16)
 def test_si_dimensions_extreme_cases(self):
  dt=np.array([1e3,1e6]);ne=np.array([0.0,1.0,1.0]);delta,tau,vis=_tau_visibility(ne,dt)
  self.assertAlmostEqual(float(tau.sum()-delta.sum()),float(delta[0]),delta=1e-11)
  self.assertAlmostEqual(float(delta[0]),C_M_S*SIGMA_T_M2*500,delta=1e-19)
 def test_input_sha_rejects_forgery(self):
  with tempfile.TemporaryDirectory() as q:
   p=Path(q)/'corrupted.zip'; b=bytearray(SOURCE.read_bytes());b[-14]^=1;p.write_bytes(b)
   with self.assertRaisesRegex(ValueError,'SOURCE_FULL_ZIP_SHA256_MISMATCH'):load(p)
 def test_noncanonical_ownership(self):
  self.assertEqual(self.stats['admission']['REI_coupled_first_interval'],'NOT_IMPLEMENTED')
  self.assertEqual(self.stats['admission']['Bianchi_directional_tau'],'NOT_COMPUTED')
 def test_saved_result_exact_on_disk(self):
  d=pd.read_csv(self.tmp/'BASS193_HHE_THOMSON_RECEIVER_192.csv',float_precision='round_trip')
  self.assertEqual(len(d),192)
  np.testing.assert_allclose(d.dtau_full_saved_trap,self.d.dtau_full_saved_trap,rtol=5e-15,atol=0)

if __name__=='__main__':unittest.main(verbosity=2)
