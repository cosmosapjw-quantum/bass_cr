#!/usr/bin/env python3
"""Independent finite-L and source-identity checks; NOT physical spin/UQ admission."""
import math
import tempfile
import unittest
from pathlib import Path
import numpy as np
import hk_primary_joint as j

SOURCE=Path("/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/"
  "WU088_P0_R12_HK_NATIVE_RECONSTRUCTION_AND_ANGLE_CONTRACT_20260921.zip")

class OriginalQuantumSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.phases,cls.digest=j.read_original_phases(SOURCE)

    def test_private_archive_identity_and_no_raw_public_phase_file(self):
        self.assertEqual(j.sha_file(SOURCE),j.SOURCE_SHA)
        self.assertEqual(self.digest,"ae2b3159eaefc699ec8763f3153dddfd3a3ce2aca6151a9a1718ab67997ca6c2")
        self.assertFalse((j.HERE/"HK1980_FIRST_SLICE_PHASES.csv").exists())

    def test_source_shape(self):
        self.assertEqual([(e,len(g),len(u)) for e,(g,u) in self.phases.items()],
                         [(0.1,147,147),(1.0,190,190)])

    def test_source_suspicious_original_value_unchanged(self):
        self.assertEqual(self.phases[1.0][0][152],0.030380)
        self.assertEqual(self.phases[1.0][1][152],0.031137)

    def test_bad_source_sha_refused(self):
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/"wrong.zip"
            f.write_bytes(b"not the source archive")
            with self.assertRaises(ValueError):
                j.read_original_phases(f)

    def test_cx_previous_primary_reconstruction_replay(self):
        for E,expected in (
            (0.1,(222.616344765,130.011619917,315.221069613,88.828416619)),
            (1.0,(162.393433950,57.371626198,267.415241702,47.599098503))
        ):
            g,u=self.phases[E]
            _,ac=j.amplitudes(g,u)
            q=j.moments(ac,j.K_HK[E])
            for k,x in zip(("total","mt_minus","mt_plus","viscosity"),expected):
                self.assertAlmostEqual(q[k],x,delta=1.0e-8)

    def test_partial_wave_optical_decomposition(self):
        for E,(g,u) in self.phases.items():
            ag=np.exp(1j*g)*np.sin(g)
            au=np.exp(1j*u)*np.sin(u)
            ae,ac=j.amplitudes(g,u)
            left=abs(ae)**2+abs(ac)**2
            right=2*(abs(ag)**2+abs(au)**2)
            self.assertLess(max(abs(left-right)),2e-14)

    def test_orthogonal_channel_dcs_nonnegative_and_first_moment_bounds(self):
        for E,(g,u) in self.phases.items():
            for a in j.amplitudes(g,u):
                m=j.moments(a,j.K_HK[E])
                self.assertGreater(m["total"],0)
                self.assertGreaterEqual(m["mt_minus"],0)
                self.assertGreaterEqual(m["mt_plus"],0)
                self.assertLessEqual(m["mt_minus"],2*m["total"]+1e-12)
                self.assertLessEqual(m["mt_plus"],2*m["total"]+1e-12)
                self.assertGreaterEqual(m["viscosity"],0)
                self.assertLessEqual(m["viscosity"],m["total"]+1e-12)
                self.assertAlmostEqual(m["mt_plus"]+m["mt_minus"],2*m["total"],delta=2e-12)

    def test_angle_integration_independent_of_recurrence(self):
        for E,(g,u) in self.phases.items():
            for ch,a,reverse in (("el",j.amplitudes(g,u)[0],False),
                                 ("cx",j.amplitudes(g,u)[1],True)):
                m=j.moments(a,j.K_HK[E])
                q=j.independent_angle_moments(a,j.K_HK[E],reverse,512)
                target=(m["total"],m["mt_plus" if reverse else "mt_minus"],m["viscosity"])
                for x,y in zip(target,q):
                    self.assertLess(abs(y/x-1),1e-9)

    def test_reversing_g_u_keeps_physical_cross_sections(self):
        for E,(g,u) in self.phases.items():
            ae,ac=j.amplitudes(g,u)
            be,bc=j.amplitudes(u,g)
            for a,b in ((ae,be),(ac,bc)):
                ma=j.moments(a,j.K_HK[E]);mb=j.moments(b,j.K_HK[E])
                for key in ("total","mt_minus","mt_plus","viscosity"):
                    self.assertAlmostEqual(ma[key],mb[key],delta=1e-10)

    def test_constant_and_identical_phase_limits(self):
        g=np.zeros(10)
        ae,ac=j.amplitudes(g,g)
        self.assertEqual(j.moments(ae,5)["total"],0.)
        self.assertEqual(j.moments(ac,5)["total"],0.)
        phi=np.linspace(0.,0.1,10)
        ae,ac=j.amplitudes(phi,phi)
        self.assertEqual(j.moments(ac,5)["total"],0.)
        self.assertGreater(j.moments(ae,5)["total"],0.)

    def test_partial_wave_truncation_not_tail_certificate(self):
        rows,checks,_=j.source_bound_rows(SOURCE)
        self.assertEqual(len(rows),4)
        for E,n in ((0.1,147),(1.0,190)):
            d=checks[str(E)]
            last=d[str(n)]
            prior=d[str(n-1)]
            relative=abs(last["combined_mt"]-prior["combined_mt"])/last["combined_mt"]
            self.assertLess(relative,1e-5)
            self.assertGreater(relative,0.)
        self.assertTrue(all(r["original_2016_full_DCS"] is False for r in rows))
        self.assertTrue(all(r["identifiable_spin_average"] is False for r in rows))

    def test_source_quadrature_moments_genuine_nonzero(self):
        rows,_,_=j.source_bound_rows(SOURCE)
        lookup={(r["E_cm_eV"],r["process"]):r for r in rows}
        self.assertAlmostEqual(lookup[(0.1,"elastic")]["sigma_mt_charge_a0_sq"],137.108491672575,delta=1e-8)
        self.assertAlmostEqual(lookup[(1.0,"elastic")]["sigma_mt_charge_a0_sq"],57.864672349719,delta=1e-8)
        for E in (0.1,1.0):
            self.assertGreater(lookup[(E,"CX")]["sigma_mt_charge_a0_sq"],lookup[(E,"CX")]["sigma_total_a0_sq"])
            self.assertLess(lookup[(E,"elastic")]["sigma_mt_charge_a0_sq"],lookup[(E,"elastic")]["sigma_total_a0_sq"])

    def test_literature_comparison_does_not_pretend_same_source(self):
        six=j.prior_2016_sparse_comparison(self.phases)
        self.assertEqual(len(six),6)
        self.assertTrue(all(r["source_equivalence"]=="NOT_PROVED_DIFFERENT_PHASE_CALCULATION_AND_LMAX" for r in six))
        self.assertGreater(abs(six[-1]["hk_over_2016_minus1"]),0.5)

    def test_negative_invalid_energy_archive_path_and_shape(self):
        with self.assertRaises(FileNotFoundError):
            j.read_original_phases(Path("/definitely/missing/file.zip"))
        with self.assertRaises(ValueError):
            j.amplitudes(np.zeros(2),np.zeros(3))

if __name__=="__main__":unittest.main()
