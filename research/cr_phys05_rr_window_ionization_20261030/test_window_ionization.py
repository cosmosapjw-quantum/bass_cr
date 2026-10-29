import json
import math
import tempfile
import unittest
from pathlib import Path
import numpy as np
import window_ionization as m

class WindowPhysics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arrays,cls.density,cls.params,cls.sigma,cls.parent=m.load_sources()
        cls.meta,cls.spectra,cls.totals,cls.witness=m.numeric_rows(cls.arrays,cls.density,cls.params,cls.sigma,cls.parent)

    def test_original_lock(self):
        self.assertEqual(self.meta['source_sha256'],m.SHA129)
        self.assertEqual(len(self.arrays['photon_H_eV']),3200)
        self.assertEqual(len(self.arrays['photon_He_eV']),3200)

    def test_corruption_guard(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.zip';raw=bytearray(m.SOURCE.read_bytes());raw[50]^=1;p.write_bytes(raw)
            with self.assertRaisesRegex(ValueError,'LOCK_PR129_SHA256_FAIL'):m.load_sources(p)

    def test_exact_closed_formula(self):
        k=np.array([0.03,0.1,0.0])
        out=m.event_kernel(0,k,2,5)
        ref=np.exp(-2*k)*(1-np.exp(-3*k))
        np.testing.assert_allclose(out,ref,rtol=3e-15,atol=1e-18)

    def test_unimodal_peak_interior(self):
        k=np.array([0.3])
        lo,hi,sl,sh=m.time_window_extrema(k,0,10,4,6)
        self.assertEqual(sh,4)
        self.assertAlmostEqual(float(hi[0]),-math.expm1(-0.6),14)
        self.assertAlmostEqual(float(lo[0]),0)
        self.assertEqual(float(sl[0]),10)

    def test_lower_endpoint_switch(self):
        k=np.array([0.00001,0.4,1.2])
        lo,hi,sl,sh=m.time_window_extrema(k,0,4,6,7)
        sampled=np.stack([m.event_kernel(s,k,6,7) for s in np.linspace(0,4,101)])
        np.testing.assert_allclose(lo,np.min(sampled,axis=0),atol=5e-15,rtol=5e-14)
        np.testing.assert_allclose(hi,np.max(sampled,axis=0),atol=5e-15,rtol=5e-14)

    def test_synthetic_bad_time(self):
        with self.assertRaises(ValueError):m.event_kernel(0,1,4,4)
        with self.assertRaises(ValueError):m.time_window_extrema(1,4,1,0,3)
        with self.assertRaises(ValueError):m.numeric_rows(self.arrays,self.density,self.params,self.sigma,self.parent,np.array([0.,0.,1e10]))

    def test_source_rows_and_rate_units(self):
        self.assertEqual((len(self.spectra),len(self.totals),len(self.witness)),(736,8,24))
        for row in self.totals:
            self.assertAlmostEqual(row['electron_source_rate_hi_m3_s']*row['duration_s']/row['electron_birth_hi_m3'],1,13)
            self.assertGreaterEqual(row['electron_birth_hi_m3'],row['electron_birth_lo_m3'])

    def test_ion_charge_stoichiometry(self):
        for r in self.totals:
            self.assertAlmostEqual(r['electron_birth_lo_m3'],r['HII_birth_lo_m3']+r['HeII_birth_lo_m3'],40)
            self.assertAlmostEqual(r['electron_birth_hi_m3'],r['HII_birth_hi_m3']+r['HeII_birth_hi_m3'],40)
        for r in self.witness:self.assertAlmostEqual(r['electron_m3'],r['ion_HII_m3']+r['ion_HeII_m3'],40)

    def test_H_photons_cannot_ionize_helium(self):
        self.assertTrue(all(r['ions_hi_m3']==0 for r in self.spectra if r['source_photon']=='H' and r['target']=='HeI'))

    def test_positive_electron_energy_partition(self):
        for r in self.spectra:
            for side in ('lo','hi'):
                self.assertGreaterEqual(r['primary_electron_kinetic_'+side+'_J_m3'],-1e-80)
                self.assertAlmostEqual(r['photon_energy_'+side+'_J_m3'],
                    r['ionization_threshold_'+side+'_J_m3']+r['primary_electron_kinetic_'+side+'_J_m3'],58)

    def test_source_endpoints_and_witness_sum(self):
        self.assertAlmostEqual(self.meta['earliest_witness_window_sum_m3'],self.parent['final']['absorbed_hi_m3'],40)
        self.assertAlmostEqual(self.meta['latest_witness_window_sum_m3'],self.parent['final']['absorbed_lo_m3'],40)
        for w in self.witness:
            r=next(t for t in self.totals if t['window_start_s']==w['window_start_s'])
            self.assertLessEqual(w['electron_m3'],r['electron_birth_hi_m3']+1e-75)
            self.assertGreaterEqual(w['electron_m3']+1e-75,r['electron_birth_lo_m3'])

    def test_window_bounds_not_additive_in_time(self):
        # Different windowwise maxima may require distinct incompatible birth choices.
        self.assertGreater(sum(r['electron_birth_hi_m3'] for r in self.totals),self.parent['final']['absorbed_hi_m3'])

    def test_photo_only_depletion_scope(self):
        eps=self.meta['max_photo_only_density_feedback']
        self.assertLess(eps['max_relative_total_opacity_loss_uniform'],3e-26)
        self.assertLess(eps['max_fractional_depletion_HI'],eps['max_fractional_depletion_HeI'])

if __name__=='__main__':unittest.main()
