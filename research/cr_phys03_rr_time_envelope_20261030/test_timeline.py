#!/usr/bin/env python3
"""Physical contract, source identity and interval-vs-explicit-birth tests."""
import csv
import math
import os
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import generate as g
import rr_boundfree as p


class TestTimeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name=os.environ.get('PR125_SOURCE_ZIP')
        if not name: raise RuntimeError('PR125_SOURCE_ZIP required')
        cls.source=Path(name)
        cls.params,cls.tabhash=p.load_verner()
        _,cls.arr,cls.density=p.read_source(cls.source)
        cls.meta,cls.rows,cls.totals,cls.hist=g.compute(cls.arr,cls.density,cls.params)

    def test_original_source_sha_locked(self):
        self.assertEqual(p.sha256(self.source.read_bytes()),p.PR125_SOURCE_SHA)
        self.assertEqual(self.tabhash,'a9ae2f7e7393de6f9ad89376cf5dd4be84da60cb3dadde3be37a4d3bd5989492')

    def test_parent_code_locked(self):
        g._check_parent()
        original=g.SOURCE_MODULE_SHA256
        try:
            g.SOURCE_MODULE_SHA256='0'*64
            with self.assertRaisesRegex(ValueError,'PR127_PARENT_MODULE_SHA256_MISMATCH'):
                g._check_parent()
        finally: g.SOURCE_MODULE_SHA256=original

    def test_sha_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            broken=Path(d)/'corrupted.zip'
            broken.write_bytes(self.source.read_bytes()[:-2])
            with self.assertRaisesRegex(ValueError,'PR125_SOURCE_ZIP_SHA256_MISMATCH'):
                p.read_source(broken)

    def test_source_ranges_thresholds(self):
        for ch,thr in [('H',13.6),('He',24.59)]:
            E=self.arr[f'photon_{ch}_eV']
            self.assertEqual(E.shape,(3200,))
            self.assertTrue(np.all(E>=thr))
            self.assertTrue(np.all(E<thr+10.01))
        self.assertEqual(self.arr['capture_H_bins_m3'].shape,(4,3200))

    def test_time_grid_and_row_count(self):
        self.assertEqual(len(self.rows),36)
        self.assertEqual(len(self.totals),9)
        self.assertEqual(len(self.hist),9*2*2*22)
        self.assertEqual(self.totals[-1]['T_s'],1e10)

    def test_no_negative_or_superluminal_absorptions(self):
        for v in self.totals:
            self.assertGreaterEqual(v['absorbed_lo_m3'],0.)
            self.assertLessEqual(v['absorbed_lo_m3'],v['absorbed_hi_m3'])
            self.assertLessEqual(v['absorbed_hi_m3'],v['emitted_hi_m3']*(1+2e-13))
        for k in ('absorbed_lo_m3','absorbed_hi_m3'):
            self.assertTrue(np.all(np.diff([r[k] for r in self.totals])>=-1e-40))

    def test_exact_parent_horizon_replay(self):
        old,_,_,_=p.evaluate(self.arr,self.density,self.params)
        new=self.totals[-1]
        for key,oldkey in [('absorbed_lo_m3','absorbed_lower_m3'),('absorbed_hi_m3','absorbed_upper_m3')]:
            self.assertAlmostEqual(new[key]/old[oldkey],1.,places=13)

    def test_h_emissions_cannot_ionize_helium(self):
        for x in self.rows:
            if x['photon_channel']=='H' and x['absorber']=='HeI':
                self.assertEqual(x['absorbed_hi_m3'],0.)
                self.assertEqual(x['electron_excess_hi_J_m3'],0.)

    def test_primary_electron_plus_threshold_energy_exact(self):
        for row in self.rows:
            for s in ('lo','hi'):
                self.assertTrue(math.isclose(row[f'photon_energy_{s}_J_m3'],
                    row[f'threshold_{s}_J_m3']+row[f'electron_excess_{s}_J_m3'],rel_tol=3e-13,abs_tol=1e-78))

    def test_electron_spectrum_reconstitutes_counts(self):
        lookup={(r['T_s'],r['photon_channel'],r['absorber']):r for r in self.rows}
        summed={}
        for x in self.hist:
            k=(x['T_s'],x['photon_channel'],x['absorber'])
            if k not in summed:summed[k]=[0.,0.]
            summed[k][0]+=x['electron_count_lo_m3']
            summed[k][1]+=x['electron_count_hi_m3']
        for k,(lo,hi) in summed.items():
            target=lookup[k]
            self.assertTrue(math.isclose(lo,target['absorbed_lo_m3'],rel_tol=3e-13,abs_tol=1e-78))
            self.assertTrue(math.isclose(hi,target['absorbed_hi_m3'],rel_tol=3e-13,abs_tol=1e-78))

    def test_partial_bin_survivor_bound(self):
        a=np.array([1e-18,4e-17])
        lo,hi=g.survival_bounds(a,0.,4.,2.)
        np.testing.assert_equal(lo,np.zeros(2))
        np.testing.assert_equal(hi,np.ones(2))
        lo,hi=g.survival_bounds(a,0.,4.,10.)
        np.testing.assert_allclose(lo,np.exp(-a*g.C*10.))
        np.testing.assert_allclose(hi,np.exp(-a*g.C*6.))

    def test_exact_birth_scenarios_enclosed(self):
        # Explicit birth schedules test mathematical bounds, NOT samples from a physical birth-time distribution.
        rng=np.random.default_rng(1745)
        for T in g.OBS_TIMES_S:
            for ch in ('H','He'):
                E=self.arr[f'photon_{ch}_eV']
                alpha={a:self.density[a]*p.verner_sigma(E,self.params[a]) for a in ('HI','HeI')}
                atot=alpha['HI']+alpha['HeI']
                for a in ('HI','HeI'):
                    tally=0.
                    for j in range(4):
                        s=float(self.arr['time_edges_s'][j])+rng.random(3200)*2.5e9
                        dt=np.maximum(T-s,0.)
                        pa=(alpha[a]/atot)*(-np.expm1(-atot*g.C*dt))
                        tally+=g._sum(self.arr[f'capture_{ch}_bins_m3'][j]*pa)
                    rec=next(r for r in self.rows if r['T_s']==T and r['photon_channel']==ch and r['absorber']==a)
                    self.assertGreaterEqual(tally+1e-75,rec['absorbed_lo_m3'])
                    self.assertLessEqual(tally,rec['absorbed_hi_m3']+1e-75)

    def test_no_unclaimed_chemistry_or_optical_depth(self):
        self.assertFalse(self.meta['production'])
        self.assertFalse(self.meta['L4'])
        self.assertIsNone(self.meta['physical_K'])
        self.assertEqual(self.meta['central_dag'],'28/88')

    def test_bad_time_grid_rejected(self):
        with self.assertRaisesRegex(ValueError,'OBSERVATION_TIMES_MUST_INCREASE'):
            g.compute(self.arr,self.density,self.params,[1.,0.])
        with self.assertRaisesRegex(ValueError,'OBSERVATION_TIMES_MUST_INCREASE'):
            g.compute(self.arr,self.density,self.params,[float('nan')])


if __name__=='__main__': unittest.main(verbosity=2)
