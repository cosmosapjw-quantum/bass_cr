"""Focused source-bound H/He ground RR photon product tests (not transport validation)."""
import copy
import io
import json
import os
from pathlib import Path
import unittest
import zipfile
import numpy as np

from cr_ionizing_rr import (SOURCE_ZIP_SHA256, SOURCE_ARRAYS_SHA256, SOURCE_RESULT_SHA256,
                            STORED_SOURCE_RECORD_SHA256, read_pinned, generate,
                            EV_J, PLANCK_J_S, C_M_S, SIGMA_THOMSON_M2)

SOURCE_PATH = Path(os.environ.get('CR_PR110_SOURCE', '/mnt/data/BASS_CR_LOW_BIRTH_SOURCE_20261027_2eed7ef835c5.zip'))

class FrozenPhotonProduct(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old, cls.arr = read_pinned(SOURCE_PATH)
        cls.new,cls.csv,cls.raw = generate(cls.old,cls.arr)

    def test_immutable_source(self):
        self.assertEqual(len(self.arr['E_eV']),3200)
        self.assertEqual(self.old['input']['sha256'],STORED_SOURCE_RECORD_SHA256)
        self.assertEqual(self.old['input']['source_payload_sha256'],
                         '7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc')
        self.assertEqual(self.old['input']['selected_tag'],'direct_0p1_10')
        self.assertTrue(self.old['context']['source_parent_ion_chemistry'] is None)

    def test_original_source_channels_and_four_intervals(self):
        for i,old in enumerate(self.old['observation_bins']):
            self.assertEqual(self.new['time_grid_s'][i:i+2],old['interval_s'])
            for ch in ['H','He']:
                w=self.arr[f'capture_{ch}_bins_m3'][i]
                count=float(np.sum(w))
                energy=float(np.dot(w,self.arr[f'photon_{ch}_energy_eV']))
                e=old['channels'][ch]
                self.assertLessEqual(abs(count-e['capture_number_m3']),1e-12*e['capture_number_m3'])
                self.assertLessEqual(abs(energy-e['retained_photon_energy_eV_m3']),1e-12*e['retained_photon_energy_eV_m3'])

    def test_native_atomic_photon_energy_and_frequency(self):
        e=self.arr['E_eV']
        for ch,ion_e in [('H',13.60),('He',24.59)]:
            photon=self.arr[f'photon_{ch}_energy_eV']
            self.assertLessEqual(np.max(abs(photon-e-ion_e)),1e-12)
            self.assertLessEqual(np.max(abs(self.raw[f'photon_{ch}_freq_Hz']-photon*EV_J/PLANCK_J_S)),1.)

    def test_ledger_and_threshold_classes(self):
        caps=self.new['ionizing_energy_gate_counts_m3']
        N=self.new['totals']['N_all_m3']
        NH=self.new['totals']['N_H_m3']; NHe=self.new['totals']['N_He_m3']
        self.assertAlmostEqual(caps['HI']['H']+caps['HI']['He'],N,delta=1e-12*N)
        self.assertAlmostEqual(caps['HeI']['He'],NHe,delta=1e-12*NHe)
        self.assertEqual(caps['HeI']['H'],0)
        self.assertEqual(caps['HeII']['He'],0)
        self.assertEqual(caps['HeII']['H'],0)
        self.assertEqual(self.new['scientific_gates']['real_He_exclusive_joint_kernel'],None)
        self.assertAlmostEqual(NH+NHe,N,delta=1e-12*N)

    def test_spectral_csv_integrals(self):
        self.assertEqual(len(self.csv),4*2*46)
        for ch in ['H','He']:
            for j in range(4):
                r=[q for q in self.csv if q['channel']==ch and q['time_bin']==j+1]
                count=sum(q['N_ph_m3'] for q in r)
                energy=sum(q['U_ph_J_m3'] for q in r)
                origin=self.old['observation_bins'][j]['channels'][ch]
                self.assertAlmostEqual(count,origin['capture_number_m3'],delta=2e-12*origin['capture_number_m3'])
                self.assertAlmostEqual(energy,origin['retained_photon_energy_eV_m3']*EV_J,delta=2e-12*origin['retained_photon_energy_eV_m3']*EV_J)
                for q in r:
                    self.assertAlmostEqual(q['nu_high_Hz']-q['nu_low_Hz'],.5*EV_J/PLANCK_J_S,delta=2.)
                    self.assertAlmostEqual(q['bin_density_m3_Hz']*(q['nu_high_Hz']-q['nu_low_Hz']),q['N_ph_m3'],delta=max(1e-70,2e-12*q['N_ph_m3']))

    def test_thomson_signed_slabs(self):
        z=self.new['thomson_signed_RR_only']
        lo,hi=z['delta_tau_bracket']
        self.assertLess(lo,hi)
        self.assertLess(hi,0.)
        self.assertGreaterEqual(lo,-SIGMA_THOMSON_M2*C_M_S*1e10*self.new['totals']['N_all_m3']*(1+1e-12))
        ne=self.new['constants']['n_e_m3']
        self.assertAlmostEqual(z['frozen_baseline_tau0'],ne*1e10*C_M_S*SIGMA_THOMSON_M2,delta=1e-12*z['frozen_baseline_tau0'])
        self.assertLess(abs(lo),z['frozen_baseline_tau0'])

    def test_baryon_fraction_and_clock(self):
        nb=self.new['constants']['n_b_m3']
        self.assertAlmostEqual(nb,8750/47,delta=1e-12)
        for row in self.new['photon_rows']:
            self.assertAlmostEqual(row['N_ph_m3']/nb,row['N_ph_per_baryon'],delta=1e-12*row['N_ph_per_baryon'])
            self.assertAlmostEqual(row['mean_rate_m3_s']*(row['interval_s'][1]-row['interval_s'][0]),row['N_ph_m3'],delta=1e-12*row['N_ph_m3'])

    def test_reject_negative_capture(self):
        bad={k:v.copy() for k,v in self.arr.items()}
        bad['capture_H_bins_m3'][0,0]=-1e-21
        with self.assertRaises(ValueError):generate(self.old,bad)

    def test_reject_wrong_clock(self):
        bad={k:v.copy() for k,v in self.arr.items()}
        bad['times_s'][0] = 1e9
        with self.assertRaises(ValueError):generate(self.old,bad)

    def test_reject_wrong_photon_energy(self):
        bad={k:v.copy() for k,v in self.arr.items()}
        bad['photon_He_energy_eV'][0]+=0.001
        with self.assertRaises(ValueError):generate(self.old,bad)

    def test_reject_source_partition_or_bath(self):
        for key, val in [('input','total'),('scope','not qualified')]:
            d=copy.deepcopy(self.old)
            if key=='input':d['input']['selected_tag']=val
            else:d['scope']=val
            with self.assertRaises(ValueError):generate(d,self.arr)
        bad=copy.deepcopy(self.old)
        bad['inventory']['values']['n_b_m3']=0
        with self.assertRaises(ValueError):generate(bad,self.arr)

    def test_repeat_determinism(self):
        q,r,s=generate(self.old,self.arr)
        self.assertEqual(json.dumps(q,sort_keys=True),json.dumps(self.new,sort_keys=True))
        self.assertEqual(r,self.csv)
        for key in s: np.testing.assert_array_equal(s[key],self.raw[key])

if __name__=='__main__':unittest.main()
