from __future__ import annotations
import csv,hashlib,io,math,os,sys,tempfile,unittest,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np
import source_cx_screen as s
Z=Path(os.environ.get('REI_SOURCE_ZIP', str(Path(__file__).resolve().parent/'REI_F4_CCC_HHE_FIRST_COLLISION_20261031_FULL.zip')))
class Tests(unittest.TestCase):
 def test_original_source_readback(self):
  d=s.source_rows(Z)
  self.assertEqual(tuple(map(len,d.values())),(192,192,192,193))
 def test_sha_tamper(self):
  with tempfile.NamedTemporaryFile(suffix='.zip') as f:
   f.write(b'spoof');f.flush()
   with self.assertRaisesRegex(ValueError,'SOURCE_ZIP_SHA_MISMATCH'):s.source_rows(f.name)
 def test_sigma_reference(self):
  for vel in (3e5,1e6,2e6):
   self.assertAlmostEqual(s.sigma_cx_cm2(vel),(s.FIT_A_CM-s.FIT_B_CM*math.log(vel))**2,delta=1e-28)
 def test_bad_domain(self):
  for v in (0,-1,float('nan')):
   with self.assertRaises(ValueError):s.sigma_cx_cm2(v)
 def test_reduced_mass_and_units(self):
  self.assertTrue(.5*s.MP_G < s.MU_G < .51*s.MP_G)
  self.assertGreater(s.thermal_speed_cm_s(10000),1e6)
 def test_analytic_vs_true_all_quadrature(self):
  for T in (100,150,1000,3000,6000,12000):
   a=s.rate_fit_all_analytic(T);b=s.rate_quadrature(T,0,float('inf'))
   self.assertAlmostEqual(a/b,1.,delta=3e-10)
 def test_truncation(self):
  for T in (100,12000):
   self.assertLess(s.rate_quadrature(T),s.rate_fit_all_analytic(T))
  self.assertLess(s.rate_quadrature(100)/s.rate_fit_all_analytic(100),.3)
  self.assertGreater(s.rate_quadrature(12000)/s.rate_fit_all_analytic(12000),.99)
 def test_thermal_energy(self):
  self.assertAlmostEqual(s.MU_G*s.thermal_speed_cm_s(1000)**2/(2*s.KB_ERG_K),1000,places=8)
 def test_physical_rows(self):
  rows=s.compute(Z);self.assertEqual(len(rows),192)
  self.assertEqual(rows[0]['interval'],0)
  self.assertAlmostEqual(rows[0]['z_high'],20)
  self.assertAlmostEqual(rows[-1]['z_low'],2)
  self.assertTrue(all(x['nu_neutral_s']>=0 and x['H_effective_per_s']>0 for x in rows))
  self.assertTrue(all(x['direct_electron_source_s']==0 for x in rows))
 def test_independent_CCC_source_density_match(self):
  rows=s.compute(Z)
  with zipfile.ZipFile(Z) as z:
   other=list(csv.DictReader(io.StringIO(z.read('results/CCC_FIRST_COLLISION_ARRIVAL_192.csv').decode())))
  self.assertEqual(len(other),len(rows))
  self.assertLess(max(abs(r['nH_cm3']/float(o['nH_cm3'])-1) for r,o in zip(rows,other)),3e-13)
  self.assertLess(max(abs(r['x_HII_end']-float(o['xHII_end'])) for r,o in zip(rows,other)),2e-14)
 def test_exact_ionization_zero(self):
  rows=s.compute(Z)
  for row in rows:
   self.assertEqual(row['direct_H_ionization_source_s'],0)
   self.assertEqual(row['direct_electron_source_s'],0)
   self.assertEqual(row['direct_binding_energy_source_erg_per_H_s'],0)
 def test_saved_replay(self):
  rows=s.compute(Z)
  with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
   fa,ja=s.save(rows,a);fb,jb=s.save(rows,b)
   self.assertEqual(fa.read_bytes(),fb.read_bytes())
   self.assertEqual(ja.read_bytes(),jb.read_bytes())
 def test_tiny_tail_no_precision_shortcut(self):
  # At 100 K much of the collision weight is below 3 km/s, NOT a 100%-covered source.
  lo=s.rate_quadrature(100,0,3e5)
  hi=s.rate_quadrature(100,3e5,2e7)
  self.assertAlmostEqual((lo+hi)/s.rate_fit_all_analytic(100),1,delta=1e-10)
 def test_no_rei_dag_promotion(self):
  self.assertEqual(s.summarize(s.compute(Z))['canonical_delta'],0)

if __name__=='__main__':unittest.main()
