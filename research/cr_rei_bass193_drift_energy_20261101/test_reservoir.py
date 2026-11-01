#!/usr/bin/env python3
"""Bounded independent science checks, no private REI ZIP access required."""
import csv
import math
import tempfile
import unittest
from pathlib import Path

import reservoir as r


class TestDriftEnergy(unittest.TestCase):
    def test_original_public_identity_and_clock(self):
        self.assertEqual(r.hash256(r.SOURCE_CSV), r.SOURCE_SHA256)
        rows = r.load_source()
        self.assertEqual(len(rows), 192)
        self.assertEqual([int(x["interval"]) for x in rows], list(range(192)))

    def test_source_denominator_h_nuclei(self):
        for row in r.load_source():
            ni, nn = float(row["nHII_cm3"]), float(row["nHI_cm3"])
            self.assertAlmostEqual(ni / (ni+nn), float(row["x_HII_end"]), delta=1e-13)

    def test_mass_weighted_com_decomposition(self):
        ni, nn = 0.7, 0.3
        mi, mn = 1.5, 2.5
        ui, un = 7., -4.
        rhoi, rhon = mi*ni, mn*nn
        V=(rhoi*ui+rhon*un)/(rhoi+rhon)
        rd=rhoi*rhon/(rhoi+rhon)
        self.assertAlmostEqual(.5*rhoi*ui**2+.5*rhon*un**2,
            .5*(rhoi+rhon)*V**2+.5*rd*(ui-un)**2, places=13)

    def test_equal_mass_closed_form(self):
        for x in (0., 1e-6, .2, .5, .8, 1.):
            b=r.snapshot_budget(x,1-x,100.,0.1,mi=1e-24,mn=1e-24)
            self.assertAlmostEqual(
                b["capacity_ratio_DeltaT_over_T"],
                4./3.*x*(1-x)*0.01, delta=2e-16)

    def test_maximum_at_half_for_equal_masses(self):
        b=r.snapshot_budget(.5,.5,200.,0.1,mi=1e-24,mn=1e-24)
        self.assertAlmostEqual(b["capacity_ratio_DeltaT_over_T"],.01/3,places=14)
        self.assertAlmostEqual(r.mass_general_max_ratio(0.1,1e-24,1e-24),.01/3,places=14)

    def test_general_mass_optimum(self):
        mi,mn=4.,1.
        x=math.sqrt(mn)/(math.sqrt(mi)+math.sqrt(mn))
        v=r.snapshot_budget(x,1-x,42.,0.1,mi=mi,mn=mn)
        self.assertAlmostEqual(v["capacity_ratio_DeltaT_over_T"],
                               r.mass_general_max_ratio(.1,mi,mn),places=13)

    def test_no_coupling_when_one_species_absent(self):
        for ni,nn in ((1.,0.),(0.,1.)):
            b=r.snapshot_budget(ni,nn,8000.,0.1,nu=1e-8,dt=1e12)
            self.assertEqual(b["relative_energy_erg_cm3"],0.)
            self.assertEqual(b["DeltaT_K_A7_conditional"],0.)

    def test_ion_neutral_exchange_symmetry(self):
        b1=r.snapshot_budget(.3,.8,8000.,.07,mi=4e-24,mn=1e-24)
        b2=r.snapshot_budget(.8,.3,8000.,.07,mi=1e-24,mn=4e-24)
        self.assertAlmostEqual(b1["relative_energy_erg_cm3"],b2["relative_energy_erg_cm3"],places=22)
        self.assertAlmostEqual(b1["capacity_ratio_DeltaT_over_T"],b2["capacity_ratio_DeltaT_over_T"],places=13)

    def test_epsilon_quadratic(self):
        b1=r.snapshot_budget(.1,.9,2000.,.05)
        b2=r.snapshot_budget(.1,.9,2000.,.1)
        self.assertAlmostEqual(b2["relative_energy_erg_cm3"]/b1["relative_energy_erg_cm3"],4.)
        self.assertAlmostEqual(b2["capacity_DeltaT_K"]/b1["capacity_DeltaT_K"],4.)

    def test_zero_or_large_finite_relaxation(self):
        zero=r.snapshot_budget(.3,.7,1000.,.1,nu=0.,dt=1e14)
        big=r.snapshot_budget(.3,.7,1000.,.1,nu=1e-9,dt=1e14)
        self.assertEqual(zero["drift_energy_conversion_fraction_A7_conditional"],0.)
        self.assertEqual(zero["U_survival_A7_conditional"],1.)
        self.assertEqual(big["drift_energy_conversion_fraction_A7_conditional"],1.)
        self.assertEqual(big["U_survival_A7_conditional"],0.)

    def test_loss_vs_deposition_consistency(self):
        for nu_dt in (.00001,.01,.1,1.,10.,100.):
            b=r.snapshot_budget(.3,.7,1000.,.1,nu=nu_dt,dt=1.)
            frac=b["drift_energy_conversion_fraction_A7_conditional"]
            survive=b["U_survival_A7_conditional"]
            self.assertAlmostEqual(frac + survive**2, 1., places=14)
            self.assertAlmostEqual(b["deposited_eV_per_H_A7_conditional"],
                b["capacity_eV_per_H"]*frac,places=13)

    def test_input_validation(self):
        bad=((-.1,.8,100.,.1,None,None),(0.,0.,100.,.1,None,None),
             (.2,.3,-5.,.1,None,None),(.2,.3,100.,-.1,None,None),
             (.2,.3,100.,.1,1e-4,None),(.2,.3,100.,.1,-1.,1.))
        for ni,nn,T,eps,nu,dt in bad:
            with self.subTest(case=(ni,nn,T,eps,nu,dt)):
                with self.assertRaises(ValueError):
                    r.snapshot_budget(ni,nn,T,eps,nu=nu,dt=dt)

    def test_tampered_source_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            dst=Path(td)/"source.csv"
            data=r.SOURCE_CSV.read_bytes()
            dst.write_bytes(data+b"\n")
            with self.assertRaisesRegex(ValueError,"byte-lock"):
                r.load_source(dst)

    def test_original_gamma_nu_crosswalk(self):
        mu=r.MP_G*r.MH_G/(r.MP_G+r.MH_G)
        for row in r.load_source():
            ni=float(row["nHII_cm3"]); nn=float(row["nHI_cm3"])
            g=float(row["ion_neutral_drag_gamma_g_cm_minus3_s_minus1"])
            k=float(row["k_mt_CX_A7_window_cm3_s"])
            nu=float(row["nu_rel_linear_drag_s_minus1"])
            self.assertTrue(math.isclose(g,mu*ni*nn*k,rel_tol=5e-13))
            self.assertTrue(math.isclose(nu,g*(1/(r.MP_G*ni)+1/(r.MH_G*nn)),
                                          rel_tol=5e-13))

    def test_real_192_results_bound_and_columns(self):
        rows, summary=r.generate()
        self.assertEqual(len(rows),192)
        bound=r.mass_general_max_ratio(.1)
        self.assertLessEqual(summary["max_source_capacity_ratio"],bound*(1+1e-12))
        self.assertTrue(all(0 <= x["drift_energy_conversion_fraction_A7_conditional"] <= 1
                            for x in rows))
        self.assertTrue(all(0 <= x["deposited_eV_per_H_A7_conditional"] <=
                            x["capacity_eV_per_H"]*(1+1e-12) for x in rows))
        self.assertEqual(summary["canonical_rei_DAG"],"28/88_REPORTED_DELTA0")

    def test_writer_byte_repro(self):
        rows, summary=r.generate()
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            f1=r.write_results(Path(a),rows,summary)
            f2=r.write_results(Path(b),rows,summary)
            self.assertEqual([p.read_bytes() for p in f1],[p.read_bytes() for p in f2])


if __name__=="__main__":
    unittest.main(verbosity=2)
