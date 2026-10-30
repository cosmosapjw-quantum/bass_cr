#!/usr/bin/env python3
"""Focused physics/source/implementation tests, same-author (NOT distinct-author review)."""
import csv,hashlib,json,math,unittest
from pathlib import Path
import numpy as np
from scipy.integrate import quad
import primary_tables as t
import phys17_primary_dcs as m
import phys16_spectral as old
ROOT=Path(__file__).resolve().parent

def table(name):
 with (ROOT/'results'/name).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))

class PHYS17Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads((ROOT/'results/RESULT.json').read_text())
  cls.cross=table('SOURCE_UB2P_RECOIL_CROSSWALK.csv')
  cls.comp=table('WILLIAMS_MEASURED_N2_VS_KFB_UB_N2.csv')
  cls.spectra=table('SOURCE_UB2P_EMISSION_SPECTRA.csv')
  cls.time=table('TIME_ORDERED_MODEL_FIRST_SCATTER_SPECTRA.csv')
  cls.npz=np.load(ROOT/'results/SOURCE_EMISSION_PROFILES.npz',allow_pickle=False)
 def test_01_parent_exact_SHA(self):
  self.assertEqual(m.sha((ROOT/'sources/PR141_PHYS16_SOURCE.zip').read_bytes()),m.PARENT_SHA)
 def test_02_nested_PHYS15_exact_SHA(self):
  self.assertEqual(m.sha((ROOT/'sources/PR140_PHYS15_SOURCE.zip').read_bytes()),old.PHYS15_SHA)
 def test_03_original_PWBA_npz_identity(self):
  self.assertEqual(m.sha((ROOT/'sources/PHYS16_SOURCE_EMISSION_PROFILES.npz').read_bytes()),m.PWBA_PDF_SHA)
 def test_04_primary_tab_count(self):
  self.assertEqual(len(table('KINGSTON_1976_TABLE4_TABLE5_UB_DCS.csv')),90)
  self.assertEqual(len(table('WILLIAMS_1976_TABLE1_MEASURED_N2_DCS.csv')),48)
  self.assertEqual(len(table('KINGSTON_1976_TABLE6_TABLE7_TOTALS.csv')),6)
 def test_05_2p_UB_points(self):
  self.assertAlmostEqual(t.K2P[0,0],1.67);self.assertAlmostEqual(t.K2P[14,0],.0264)
  self.assertAlmostEqual(t.K2P[0,1],6.47);self.assertAlmostEqual(t.K2P[14,2],.000171)
 def test_06_Williams_N2_not_2p(self):
  self.assertEqual(t.W_N2.shape,(16,3));self.assertAlmostEqual(t.W_N2[-1,1],.142)
  self.assertEqual(self.r['measured_comparison_semantics'],'WILLIAMS_1976_TABLE1_N2_2S_PLUS_2P_UNRESOLVED')
 def test_07_K2_S_table_not_confused(self):
  self.assertAlmostEqual(t.K2S[0,0],.443);self.assertAlmostEqual(t.K2S[14,1],.00587)
 def test_08_physical_unit_cross_integral(self):
  for k in self.r['angular_table_integral_checks']:
   self.assertLess(abs(k['relative_difference']),.015)
 def test_09_2p_UB_k2_anchor(self):
  for j,e in enumerate(m.K_EV):
   for i,tdeg in enumerate(t.K_TH):
    self.assertAlmostEqual(float(m.dcs_at_mu(e,np.cos(np.deg2rad(tdeg)))),t.K2P[i,j],places=11)
 def test_10_energy_out_of_range(self):
  with self.assertRaisesRegex(ValueError,'OUTSIDE'):m.dcs_at_mu(13.,0.)
  with self.assertRaisesRegex(ValueError,'OUTSIDE'):m.dcs_at_mu(35.,0.)
 def test_11_angular_positive_normal(self):
  for e in [14.60140625,16.46,19.58,20.99]:
   p,s=m.normalized_angular(e)
   self.assertTrue(np.all(p>0));self.assertAlmostEqual(sum(p),1.,12);self.assertGreater(s,0.)
 def test_12_distinguish_DCS_total_vs_NIST_rate(self):
  self.assertEqual(self.r['source_ownership'],'UNCHANGED_NIST_BE_TOTAL_SHAH_MEASURED_EII')
 def test_13_model_KFB_dcs_vs_measure_count(self):self.assertEqual(len(self.comp),48)
 def test_14_backscatter_discriminator(self):
  r=next(x for x in self.comp if float(x['energy_eV'])==16.46 and int(x['angle_deg'])==150)
  self.assertGreater(float(r['measured_N2_DCS_a0_sq_sr'])/float(r['KFB_UB_N2_sum_model_DCS_a0_sq_sr']),5.)
 def test_15_no_invented_stats(self):
  self.assertGreater(self.r['measured_comparison']['16.46']['RMS_reported_error_standardized'],3.)
  self.assertEqual(self.r['R06_distinct_author'],'NOT_RUN')
 def test_16_source_count(self):
  self.assertEqual(len(self.cross),2066);self.assertEqual(self.r['source_photon_atoms'],6400)
 def test_17_original_source_owner_stable(self):
  self.assertEqual({r['source'] for r in self.cross},{'He'})
  self.assertAlmostEqual(sum(float(r['excitation_earliest_m3']) for r in self.cross)/3.3158906934521573e-31,1.,12)
 def test_18_source_energy_coverage(self):
  self.assertTrue(all(14.6<=float(r['Ee_eV'])<=21.0 for r in self.cross))
 def test_19_recoil_collision_energy(self):
  self.assertLess(max(float(r['relative_kinetic_energy_residual']) for r in self.cross),1.e-12)
 def test_20_emission_npz_shape(self):
  self.assertEqual(self.npz['profiles'].shape,(2066,3,161))
 def test_21_reference_pwba_exact(self):
  with np.load(ROOT/'sources/PHYS16_SOURCE_EMISSION_PROFILES.npz',allow_pickle=False) as x:
   self.assertTrue(np.array_equal(self.npz['profiles'][:,2,:],x['profiles'][:,0,:]))
 def test_22_model_emission_positive(self):self.assertTrue(np.all(self.npz['profiles']>=0))
 def test_23_model_emission_mass_window(self):
  u=np.trapezoid(self.npz['profiles'],old.XGRID,axis=2)
  self.assertTrue(np.all((u>.9995)&(u<1.0001)))
 def test_24_emission_spectra_count(self):self.assertEqual(len(self.spectra),2*3*161)
 def test_25_source_time_spectrum_count(self):self.assertEqual(len(self.time),2*3*161)
 def test_26_source_time_positive(self):self.assertTrue(all(float(r['source_qualified_first_scatter_spectral_density_per_x_m3'])>=0 for r in self.time))
 def test_27_source_birth_N2p_parity(self):
  for p,tar in [('earliest',3.3158906934521573e-31),('latest',9.85567761064524e-32)]:
   self.assertLess(abs(self.r['spectrum'][p+':KFB_UB2P_E1']['parent_N2p_m3']/tar-1),1e-12)
 def test_28_time_integral_valid(self):
  for x in self.r['time_ordered_first_scatter_integrals'].values():
   self.assertTrue(0<x['first_scatter_x16_lower_m3']<x['injection_x16_m3']<x['parent_excitation_m3'])
 def test_29_time_per_atom_original_exact(self):
  self.assertLess(max(x['original_x0_max_per_atom_relative_residual'] for x in self.r['time_ordered_first_scatter_integrals'].values()),1e-12)
 def test_30_tail_bound_status(self):
  self.assertTrue(self.r['rigorous_model_tail_probability_upper_x16']>0)
  self.assertTrue(all(x['tail_upper_excludes_core_quadrature_error'] for x in self.r['time_ordered_first_scatter_integrals'].values()))
 def test_31_no_central_promotion(self):
  self.assertEqual(self.r['central_DAG'],'28/88 DELTA0');self.assertEqual(self.r['extension_DAG'],'0/3 DELTA0')
 def test_32_hold(self):
  self.assertEqual(self.r['production'],'HOLD');self.assertEqual(self.r['L4'],'HOLD');self.assertEqual(self.r['native25'],'HOLD')
 def test_33_no_merge_no_forcepush(self):self.assertTrue(self.r['no_merge'] and self.r['no_force_push'])
 def test_34_2p_aligment_not_measured(self):self.assertEqual(self.r['true_2p_density_matrix'],'UNBOUND')
 def test_35_recoil_model_not_probabilistic_false_CERT(self):self.assertEqual(self.r['calculation'],'MODEL_CONDITIONAL_WITH_KFB_UB2P_SHAPE_AND_ASSUMED_E1_ALIGNMENT')

if __name__=='__main__':unittest.main(verbosity=2)
