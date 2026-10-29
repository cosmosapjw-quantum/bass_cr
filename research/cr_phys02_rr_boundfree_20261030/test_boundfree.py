from __future__ import annotations
import copy, json,math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from rr_boundfree import load_verner,verner_sigma,read_source,evaluate,PR125_SOURCE_SHA,HI,HEI,C_M_S
from independent_reference import independent_sigma,P,D

ROOT=Path(__file__).parent
SOURCE=ROOT/'BASS_CR_PHYS02_RR_IONIZING_PHOTON_SOURCE_20261029.zip'

class Physics(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.table,cls.tablehash=load_verner()
    cls.source,cls.arr,cls.den=read_source(SOURCE)
    cls.result,cls.rows,cls.samples,cls.atom=evaluate(cls.arr,cls.den,cls.table)

 def test_origin(self):
    self.assertEqual(self.source['authority']['source_PR'],110)
    self.assertEqual(self.result['source_sha256'],PR125_SOURCE_SHA)
    self.assertEqual(len(self.rows),16)
    self.assertEqual(self.source['scope']['photon_transport'],False)

 def test_threshold_and_supported_range(self):
    self.assertEqual(float(verner_sigma([13.59999],self.table[HI])[0]),0)
    self.assertEqual(float(verner_sigma([24.5899],self.table[HEI])[0]),0)
    self.assertGreater(float(verner_sigma([13.6],self.table[HI])[0]),0)
    self.assertGreater(float(verner_sigma([24.59],self.table[HEI])[0]),0)
    self.assertEqual(float(verner_sigma([50001.],self.table[HEI])[0]),0)
    self.assertRaises(ValueError,verner_sigma,[-1],self.table[HI])

 def test_independent_sigma_mpmath(self):
    for name in (HI,HEI):
      for en in [13.6,20.,24.59,27.6,30.,34.59]:
        fast=float(verner_sigma([en],self.table[name])[0])
        slow=float(independent_sigma(D(en),name))
        self.assertAlmostEqual(fast,slow,delta=max(1e-100,1e-13*abs(slow)))

 def test_channel_support(self):
    self.assertEqual(self.result['channels']['H']['HeI']['hi'],0)
    self.assertGreater(self.result['channels']['He']['HeI']['hi'],0)
    self.assertEqual(self.rows[-1]['source_channel'],'He')

 def test_bounds(self):
    for v in self.rows:
       self.assertGreaterEqual(v['absorbed_lower_m3'],0)
       self.assertLessEqual(v['absorbed_lower_m3'],v['absorbed_upper_m3'])
       self.assertLessEqual(v['absorbed_upper_m3'],v['photons_emitted_m3']*(1+1e-13))
    self.assertLess(self.result['absorbed_upper_m3'],self.result['source_photons_m3'])
    self.assertGreater(self.result['surviving_lower_m3'],0)

 def test_last_bin_lower_bound_is_zero(self):
    self.assertEqual(sum(x['absorbed_lower_m3'] for x in self.rows if x['time_bin']==4),0)

 def test_energy_bookkeeping(self):
    for v in self.rows:
       for lab in ('lower','upper'):
          err=abs(v[f'first_absorbed_photon_energy_{lab}_J_m3']-v[f'ionization_threshold_energy_{lab}_J_m3']-v[f'photoelectron_excess_avail_{lab}_J_m3'])
          self.assertLessEqual(err,1e-12*max(1e-100,v[f'first_absorbed_photon_energy_{lab}_J_m3']))

 def test_endpoint_monotonicity_strong(self):
    for ch in ('H','He'):
        for j in range(4):
           w=self.arr[f'capture_{ch}_bins_m3'][j]
           alpha=self.atom[f'alpha_{ch}_total_m_inv']
           pmax=-np.expm1(-alpha*C_M_S*(1e10-self.arr['time_edges_s'][j]))
           pmin=-np.expm1(-alpha*C_M_S*(1e10-self.arr['time_edges_s'][j+1]))
           self.assertTrue(np.all(pmin<=pmax))
           self.assertLessEqual(math.fsum(w*pmin), math.fsum(w*pmax))

 def test_negative_source_sha(self):
    bad=ROOT/'results'/'bad_source_truncated.zip'
    bad.write_bytes(SOURCE.read_bytes()[:100])
    try:
      with self.assertRaisesRegex(ValueError,'SOURCE_ZIP_SHA256'):
        read_source(bad)
    finally:bad.unlink()

 def test_negative_table(self):
    bad=ROOT/'results'/'bad_verner.dat'
    bad.write_text((ROOT/'source/VERNER1996_HI_HEI_TABLE1.dat').read_text().replace('5.475E+04','5.475E+03'))
    try:
      with self.assertRaisesRegex(ValueError,'NOT_SOURCE_LOCKED'):
        load_verner(bad)
    finally:bad.unlink()

 def test_negative_atom_counts_and_energy(self):
    copyarr=dict(self.arr)
    copyarr['capture_H_bins_m3']=self.arr['capture_H_bins_m3'].copy()
    copyarr['capture_H_bins_m3'][0,0]=-1
    with self.assertRaisesRegex(ValueError,'SOURCE_ARRAY_INVALID'):
      evaluate(copyarr,self.den,self.table)
    self.assertLess(copyarr['capture_H_bins_m3'][0,0],0)

 def test_first_target_probability_partition(self):
    for ch in ('H','He'):
       alpha=self.atom[f'alpha_{ch}_total_m_inv']
       h=self.atom[f'alpha_{ch}_HI_m_inv'];he=self.atom[f'alpha_{ch}_HeI_m_inv']
       self.assertTrue(np.allclose(h+he,alpha,rtol=1e-14,atol=0))
       self.assertTrue(np.all(h>=0));self.assertTrue(np.all(he>=0))

if __name__=='__main__':unittest.main()
