"""Targeted receiver-boundary checks without a nonzero physics evolution."""
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import response as r

class BoundaryTest(unittest.TestCase):
    def test_each_grid_gets_fresh_exact_number_and_energy_projection(self):
        for n in (128,256,512):
            grid=r.P.make_grid(n)
            g=r.P.Generator(grid,None,r.P.Gas(),8)
            y=r.initial(g)
            self.assertEqual(y.shape,(n+10,2))
            np.testing.assert_array_equal(y[g.n:],0)
            for j,row in enumerate(r.UPSTREAM):
                self.assertAlmostEqual(float(y[:g.n,j].sum()),1,places=14)
                self.assertAlmostEqual(float(grid@y[:g.n,j]),row[1]/1000,places=11)

    def test_upstream_channels_and_combined_energy_at_birth(self):
        grid=r.P.make_grid(128)
        g=r.P.Generator(grid,None,r.P.Gas(),8)
        rows=r.observe(g,r.initial(g))
        self.assertEqual(rows[0]['upstream_HI_NIST_2p_events'],1)
        self.assertEqual(rows[0]['upstream_HeI_NIST_singlet_events'],0)
        self.assertEqual(rows[1]['upstream_HI_NIST_2p_events'],0)
        self.assertEqual(rows[1]['upstream_HeI_NIST_singlet_events'],1)
        for row in rows:
            self.assertAlmostEqual(row['combined_energy_ledger_eV'],r.E0,places=11)
            self.assertEqual(row['downstream_HeI_old23s_excitation_energy_eV'],0)
            self.assertEqual(row['cutoff_energy_eV'],0)

if __name__=='__main__':
    unittest.main()
