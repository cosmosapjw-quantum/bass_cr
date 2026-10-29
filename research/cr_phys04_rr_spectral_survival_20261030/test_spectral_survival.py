import csv
import io
import json
import pathlib
import tempfile
import unittest
import zipfile
import numpy as np
from spectral_survival import (ROOT, SOURCE_ARCHIVE, SHA128, SHA125, SHA127, 
                               TARGETS, ENERGY_EDGES, TIMES, C, atom_components,
                               witness, source_load, compute, run, sha256)

class ScopedSourceSpectralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arrays,cls.density,cls.params,cls.sigma,cls.parent,cls.old=source_load()
        cls.result,cls.erows,cls.arows,cls.trows,cls.wrows=compute(cls.arrays,cls.density,cls.params,cls.sigma,cls.parent,cls.old)

    def test_source_sha_and_nested_hash(self):
        self.assertEqual(sha256(SOURCE_ARCHIVE.read_bytes()),SHA128)
        with zipfile.ZipFile(SOURCE_ARCHIVE) as f:
            self.assertEqual(sha256(f.read('source/ORIGINAL_PR125_SOURCE_IMMUTABLE.zip')),SHA125)
            self.assertIsNone(f.testzip())

    def test_exact_source_and_shape(self):
        self.assertEqual(self.arrays['capture_H_bins_m3'].shape,(4,3200))
        self.assertEqual(self.arrays['capture_He_bins_m3'].shape,(4,3200))
        self.assertEqual(self.density['HI'],138.6)
        self.assertEqual(len(self.erows),414)
        self.assertEqual(len(self.arows),828)
        self.assertEqual(len(self.wrows),54)
        self.assertEqual(len(self.trows),9)

    def test_all_spectral_interval_orders(self):
        for r in self.erows:
            self.assertLessEqual(0.,r['survive_lo_m3'])
            self.assertLessEqual(r['survive_lo_m3'],r['survive_hi_m3']+1e-91)
            self.assertLessEqual(r['total_absorbed_lo_m3'],r['total_absorbed_hi_m3']+1e-91)
        for r in self.arows:
            self.assertLessEqual(0.,r['absorbed_lo_m3'])
            self.assertLessEqual(r['absorbed_lo_m3'],r['absorbed_hi_m3']+1e-91)

    def test_interior_survivor_max_needs_interior_time(self):
        w=np.array([1.0]);h=np.array([3e-18]);he=np.array([2e-18]);l=1e9;r=3e9;T=2e9
        born_min,born_max,slo,shi,ahlo,ahhi,aelo,aehi=atom_components(w,h,he,l,r,T)
        self.assertEqual(slo[0],0.)
        self.assertEqual(shi[0],1.)  # s=T maximizes survivors, not s=l or s=r
        self.assertEqual(born_max[0],1.)
        self.assertEqual(born_min[0],0.)
        for s in np.linspace(l,r,31):
            U,S,A_H,A_He=(w,np.zeros_like(w),np.zeros_like(w),np.zeros_like(w)) if s>T else (
             np.zeros_like(w),w*np.exp(-(h+he)*C*(T-s)),
             w*(h/(h+he))*(-np.expm1(-(h+he)*C*(T-s))),
             w*(he/(h+he))*(-np.expm1(-(h+he)*C*(T-s))))
            self.assertLessEqual(float(S[0]),float(shi[0])+1e-12)
            self.assertGreaterEqual(float(S[0])+1e-12,float(slo[0]))
            self.assertAlmostEqual(float(U[0]+S[0]+A_H[0]+A_He[0]),1.,places=12)

    def test_early_late_interior_witness_energy(self):
        w=np.array([1.,2.,3.]);H=np.array([1e-17,2e-17,3e-17]);He=np.array([2e-17,0.,1e-17]);E=np.array([13.6,24.7,29.3])
        for T in (0.,1.5e9,2.5e9,4e9):
            for policy in ('earliest','latest','just_in_time'):
                parts=witness(w,H,He,1e9,3e9,T,policy)
                np.testing.assert_allclose(sum(parts),w,rtol=3e-15,atol=2e-15)
                np.testing.assert_allclose(sum(p*E for p in parts),w*E,rtol=3e-15,atol=2e-15)

    def test_parent_pr128_nine_epochs(self):
        for new,old in zip(self.trows,self.old):
            self.assertEqual(new['T_s'],float(old['T_s']))
            for k in ('survive_lo_m3','survive_hi_m3','absorbed_lo_m3','absorbed_hi_m3'):
                self.assertAlmostEqual(new[k]/float(old[k]),1.,places=12) if float(old[k]) else self.assertEqual(new[k],0.)

    def test_final_photon_and_energy_complement(self):
        z=self.trows[-1]
        for s,a in [('survive_lo_m3','absorbed_hi_m3'),('survive_hi_m3','absorbed_lo_m3')]:
            self.assertAlmostEqual((z[s]+z[a])/z['source_photons_m3'],1.,places=12)
        for s,a in [('survive_energy_lo_J_m3','absorbed_photon_energy_hi_J_m3'),('survive_energy_hi_J_m3','absorbed_photon_energy_lo_J_m3')]:
            self.assertAlmostEqual((z[s]+z[a])/z['source_photon_energy_J_m3'],1.,places=12)

    def test_HeI_absorption_for_H_source_strict_zero(self):
        for row in self.arows:
            if row['source']=='H' and row['target']=='HeI':
                self.assertEqual(row['absorbed_lo_m3'],0.)
                self.assertEqual(row['absorbed_hi_m3'],0.)

    def test_witness_number_and_energy_ledgers(self):
        for row in self.wrows:
            self.assertLess(abs(row['number_residual_m3']),1e-35)
            self.assertLess(abs(row['energy_residual_J_m3']),1e-52)

    def test_valid_source_photon_eV_grid(self):
        self.assertEqual(float(ENERGY_EDGES[0]),13.)
        self.assertEqual(float(ENERGY_EDGES[-1]),36.)
        self.assertLess(max(self.arrays['photon_H_eV'].max(),self.arrays['photon_He_eV'].max()),36.)
        self.assertGreater(min(self.arrays['photon_H_eV'].min(),self.arrays['photon_He_eV'].min()),13.)

    def test_bad_source_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)/'broken.zip';raw=bytearray(SOURCE_ARCHIVE.read_bytes());raw[-100]^=1;path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError,'SHA256_MISMATCH'):
                source_load(path)

    def test_invalid_time_grid_rejected(self):
        for bad in ([-1.,1.],[0.,0.],[0.,np.nan],[3.,2.]):
            with self.assertRaisesRegex(ValueError,'INVALID_OBSERVATION_GRID'):
                compute(self.arrays,self.density,self.params,self.sigma,self.parent,self.old,times=bad)

    def test_write_and_readback(self):
        with tempfile.TemporaryDirectory() as d:
            meta=run(SOURCE_ARCHIVE,pathlib.Path(d))
            for k,expected in [('SURVIVING_PHOTON_ENERGY.csv',414),('ABSORBED_PHOTON_ENERGY.csv',828),('TIME_TOTAL.csv',9),('JOINT_WITNESS_LEDGERS.csv',54)]:
                with open(pathlib.Path(d)/k, encoding='utf-8', newline='') as fh:
                    self.assertEqual(len(list(csv.DictReader(fh))),expected)
            self.assertEqual(json.loads((pathlib.Path(d)/'RESULT.json').read_text())['parent_sha256'],SHA128)

if __name__=='__main__':unittest.main()