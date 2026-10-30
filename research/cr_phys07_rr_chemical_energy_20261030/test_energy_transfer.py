#!/usr/bin/env python3
"""Source-qualified narrowly scoped scientific validation for PHYS07."""
import hashlib, json, math, tempfile, unittest
from pathlib import Path
import energy_transfer as e

class PhysicalTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.edges,cls.prep,cls.params,cls.dens,cls.prev=e.load_source()
        cls.final_early,cls.channels_early=e.epoch_ledger(cls.prep,cls.edges,cls.params,1e10,'earliest')
        cls.final_late,cls.channels_late=e.epoch_ledger(cls.prep,cls.edges,cls.params,1e10,'latest')

    def test_01_byte_locked_source(self):
        self.assertEqual(hashlib.sha256(e.SOURCE.read_bytes()).hexdigest(),e.SOURCE_SHA256)
    def test_02_actual_native_shapes(self):
        self.assertEqual(len(self.prep),2)
        self.assertEqual([p['weights'].shape for p in self.prep],[(4,3200),(4,3200)])
        self.assertEqual(len(self.edges),5)
    def test_03_source_ion_thresholds(self):
        self.assertEqual([self.params[a][0] for a in e.TARGETS],[13.6,24.59])
    def test_04_cross_He_to_H_positive(self):
        a=self.final_late['He_origin_to_HI_m3'];b=self.final_early['He_origin_to_HI_m3']
        self.assertGreater(b,a)
        self.assertAlmostEqual(a/self.prev['cross_He_to_H_abs_lower_m3'],1,places=12)
        self.assertAlmostEqual(b/self.prev['cross_He_to_H_abs_upper_m3'],1,places=12)
    def test_05_cross_H_to_He_subthreshold_exact(self):
        self.assertEqual([x['absorption_m3'] for x in self.channels_early if x['source']=='H' and x['target']=='HeI'],[0.])
        self.assertLess(self.prep[0]['energy'].max(),self.params['HeI'][0])
    def test_06_event_energy_gain_per_absorbed_photon(self):
        for row in self.channels_early+self.channels_late:
            s=row['source'];a=row['target'];I_s=self.params['HI' if s=='H' else 'HeI'][0];I_a=self.params[a][0]
            target=(I_s-I_a)*row['absorption_m3']*e.EV_J
            self.assertLessEqual(abs(row['net_kinetic_transfer_from_binding_J_m3']-target),max(1e-75,abs(target)*1e-13))
    def test_07_photon_energy_and_charge_conservation(self):
        for t in e.TIMES:
            for policy in e.POLICIES:
                r,ch=e.epoch_ledger(self.prep,self.edges,self.params,float(t),policy)
                original=r['source_recombination_binding_release_J_m3']+r['pre_recombination_selected_e_kinetic_J_m3']
                final=r['surviving_photon_energy_J_m3']+r['target_ionization_threshold_energy_J_m3']+r['primary_photoelectron_energy_J_m3']
                self.assertLessEqual(abs(original-final),max(1e-75,original*1e-12))
                self.assertLessEqual(abs(r['net_free_electron_change_m3']+r['surviving_photons_m3']),max(1e-75,sum(r['source_'+a+'_births_m3'] for a in ('H','He'))*1e-12))
    def test_08_chemistry_opacity_not_treated_as_evolving(self):
        self.assertEqual(self.dens['HI'],138.6)
        self.assertTrue(self.dens['HeI']>11.)
        self.assertEqual(self.params['HI'][0],13.6)
    def test_09_time_endpoints(self):
        self.assertEqual(self.final_early['source_H_births_m3'],self.final_late['source_H_births_m3'])
        self.assertEqual(self.final_early['source_He_births_m3'],self.final_late['source_He_births_m3'])
        self.assertGreater(self.final_early['He_to_H_primary_electron_kinetic_boost_J_m3'],self.final_late['He_to_H_primary_electron_kinetic_boost_J_m3'])
    def test_10_energy_spectral_rows(self):
        rows=e.spectral_energy(self.prep,self.edges,self.params)
        self.assertEqual(len(rows),368)
        self.assertTrue(all(r['first_absorbed_ions_lo_m3']<=r['first_absorbed_ions_hi_m3']+1e-82 for r in rows))
    def test_11_invalid_input(self):
        with self.assertRaises(ValueError):e.epoch_ledger(self.prep,self.edges,self.params,1e10,'wrong')
        with self.assertRaises(ValueError):e.epoch_ledger(self.prep,self.edges,self.params,-1,'earliest')
    def test_12_corrupt_sha_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'corrupt.zip'; p.write_bytes(e.SOURCE.read_bytes()+b'x')
            with self.assertRaisesRegex(ValueError,'SHA_MISMATCH'):e.load_source(p)
    def test_13_saved_replay(self):
        with tempfile.TemporaryDirectory() as d:
            r=e.run(e.SOURCE,Path(d));self.assertEqual(r['time_history_rows'],27)
            self.assertEqual(r['channel_time_rows'],108)
            self.assertEqual(r['final_energy_spectral_rows'],368)
    def test_14_BI_sign_identity(self):
        for row in self.channels_early:
            if row['source']==row['target'].replace('I',''):
                self.assertAlmostEqual(row['net_kinetic_transfer_from_binding_J_m3'],0,delta=1e-80)
    def test_15_no_plasma_heating_promotion(self):
        with tempfile.TemporaryDirectory() as d:
            r=e.run(e.SOURCE,Path(d)); self.assertFalse(r['production']);self.assertFalse(r['L4']);self.assertFalse(r['native25'])

if __name__=='__main__':unittest.main()
