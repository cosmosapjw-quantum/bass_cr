#!/usr/bin/env python3
import csv,hashlib,math,tempfile,unittest,zipfile,json
from pathlib import Path
import numpy as np
from scipy.integrate import quad
import phys15_lya as m

class PHYS15Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory(prefix='phys15_unit_')
  cls.out=Path(cls.tmp.name)
  cls.result=m.generate(m.ROOT/'sources/PR139_ORIGINAL_SOURCE.zip',cls.out)
  cls.tables={}
  for x in ['SOURCE_2P_LYA_ATOMS.csv','TIME_LYA_2P_RADIATION_LEDGER.csv','TIME_SOURCE_LYA_LEDGER.csv','FREQUENCY_FIRST_SCATTER_ATLAS.csv','FINAL_SOURCE_ATOM_LYA_SCATTER.csv','LINE_MICROPHYSICS.csv']:
   with (cls.out/x).open(newline='',encoding='utf8') as f:cls.tables[x]=list(csv.DictReader(f))
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_parent_sha(self):self.assertEqual(m.sha((m.ROOT/'sources/PR139_ORIGINAL_SOURCE.zip').read_bytes()),m.PARENT_SHA)
 def test_parent_nested_source(self):
  with zipfile.ZipFile(m.ROOT/'sources/PR139_ORIGINAL_SOURCE.zip') as z:
   nested=z.read('research/cr_phys14_nist_2p_20261030/sources/PR138_ORIGINAL_SOURCE.zip')
   self.assertEqual(hashlib.sha256(nested).hexdigest(),'fdae18068eb51ae7bdd0785efa371229aa15d33b6f040e0640e0bd65cc66d3a7')
 def test_manifest_parent_count(self):
  with zipfile.ZipFile(m.ROOT/'sources/PR139_ORIGINAL_SOURCE.zip') as z:self.assertEqual(len(json.loads(z.read('SOURCE_MANIFEST.json'))['members']),50)
 def test_corrupt_parent_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'broken.zip';src=bytearray((m.ROOT/'sources/PR139_ORIGINAL_SOURCE.zip').read_bytes());src[-11]^=1;p.write_bytes(src)
   with self.assertRaisesRegex(ValueError,'SHA256_MISMATCH'):m.load_parent(p)
 def test_source_counts(self):self.assertEqual(self.result['source_photon_atoms'],6400)
 def test_row_counts(self):self.assertEqual(self.result['total_rows'],19869)
 def test_parent_time_parity(self):self.assertLess(self.result['source_parity_max_relative'],1e-12)
 def test_positive_line_sigmas(self):self.assertTrue(all(m.scatter_sigma(x)>0 for x in m.X_OFFSETS))
 def test_frequency_symmetry(self):
  for x in [1,2,5,10,100]:self.assertAlmostEqual(m.scatter_sigma(x)/m.scatter_sigma(-x),1.,12)
 def test_line_micro_CGS_SI(self):self.assertTrue(5.8e-17<m.scatter_sigma(0)<6e-17)
 def test_line_doppler_width(self):self.assertTrue(1e10<m.LINE['doppler_width_Hz']<1.1e10)
 def test_lifetime(self):self.assertAlmostEqual(m.LINE['lifetime_s']*m.A21,1.)
 def test_line_wavelength(self):self.assertTrue(121.5e-9<m.LINE['vacuum_wavelength_m']<121.7e-9)
 def test_unit_opacity(self):self.assertAlmostEqual(m.scatter_rate(0),m.H_DENSITY_M3*m.C*m.scatter_sigma(0))
 def test_source_zero_below_threshold(self):
  a=self.tables['SOURCE_2P_LYA_ATOMS.csv'];self.assertEqual(sum(int(x['ionization_excitation_measured_overlap']) for x in a),2066)
 def test_source_positive_support(self):
  a=self.tables['SOURCE_2P_LYA_ATOMS.csv'];self.assertTrue(all(float(x['primary_2p_first_event_rate_s'])>=0 for x in a))
 def test_energy_ledger_each(self):
  for x in self.tables['SOURCE_2P_LYA_ATOMS.csv']:
   if int(x['ionization_excitation_measured_overlap']):
    self.assertAlmostEqual(float(x['primary_electron_energy_eV']),m.E_LYA+float(x['post_2p_excitation_primary_electron_eV']))
 def test_time_origin_zero(self):
  for x in self.tables['TIME_LYA_2P_RADIATION_LEDGER.csv']:
   if float(x['observation_s'])==0:self.assertEqual(float(x['calculated_2p_excitations_m3']),0.)
 def test_time_monotone(self):
  r=self.tables['TIME_LYA_2P_RADIATION_LEDGER.csv']
  for p in m.POLICIES:
   xs=[float(x['calculated_2p_excitations_m3']) for x in r if x['birth_policy']==p]
   self.assertTrue(all(y>=x for x,y in zip(xs,xs[1:])))
 def test_scattering_time_monotone(self):
  d=self.tables['FREQUENCY_FIRST_SCATTER_ATLAS.csv']
  for p in m.POLICIES:
   xs=[float(x['N_Lya_first_scatter_instant_decay_m3']) for x in d if x['birth_policy']==p and float(x['x_Doppler'])==0]
   self.assertTrue(all(y>=x for x,y in zip(xs,xs[1:])))
 def test_scattering_frequency_monotone(self):
  d=self.tables['FREQUENCY_FIRST_SCATTER_ATLAS.csv'];d={float(x['x_Doppler']):float(x['N_Lya_first_scatter_instant_decay_m3']) for x in d if x['birth_policy']=='earliest' and float(x['observation_s'])==1e10}
  self.assertGreater(d[0],d[3]);self.assertGreater(d[3],d[10]);self.assertGreater(d[10],d[100])
 def test_parent_earliest_parity(self):self.assertAlmostEqual(self.result['earliest']['original_parent_H_2p_first_inelastic_m3']/3.315890693452157e-31,1.)
 def test_first_scattering_lower_and_upper(self):
  for x in self.tables['FREQUENCY_FIRST_SCATTER_ATLAS.csv']:
   lo=float(x['N_first_scatter_finite_A_lower_m3']);hi=float(x['N_first_scatter_finite_A_upper_m3']);n=float(x['N_Lya_initial_emission_upper_m3']);self.assertLessEqual(lo,hi*(1+1e-14)+1e-55);self.assertLessEqual(hi,n*(1+1e-12)+1e-55)
 def test_missing_real_escape(self):self.assertEqual(self.result['excluded'].find('finite geometry')>=0,True)
 def test_l4_hold(self):self.assertEqual(self.result['L4'],'HOLD')
 def test_dag_not_promoted(self):self.assertEqual(self.result['central_DAG'],'28/88 DELTA0')
 def test_independent_review_not_run(self):self.assertEqual(self.result['R06_distinct_author'],'NOT_RUN')
 def test_finite_A_correction_bound(self):
  q=m.scatter_rate(0);self.assertLess(q/m.A21,1e-13)
 def test_first_scatter_short_time_scaling(self):
  # Source-free representative microphysical special case, first 3-stage event:
  a=2e-3; nu=3e-3;k=5e-3;q=4e-3;d=.02
  xs,ws=np.polynomial.legendre.leggauss(256);u=(xs+1)*d/2
  den=a*nu*u*np.exp(-k*u)*np.array([m.exprel((k-nu)*v) for v in u]);p=d/2*np.dot(ws,den*(-np.expm1(-q*(d-u))))
  self.assertLess(abs(p/(a*nu*q*d**3/6)-1),0.001)
 def test_first_scatter_zero_horizon(self):
  self.assertTrue(all(float(x['N_Lya_first_scatter_instant_decay_m3'])==0 for x in self.tables['FREQUENCY_FIRST_SCATTER_ATLAS.csv'] if float(x['observation_s'])==0))

if __name__=='__main__':unittest.main(verbosity=2)
