#!/usr/bin/env python3
"""One source-owned 46k Case-B recombination/Lyalpha cascade scientific test pass."""
import csv,gzip,math,os,tempfile,unittest
from pathlib import Path
from decimal import Decimal,localcontext
import numpy as np
import native_caseb_lya as p


class RecombCaseB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=p.read_csv(p.PREVIEW,p.LOCKS["preview"])
        cls.native=p.read_csv(p.INCREMENTS,p.LOCKS["increments"])
        cls.geo=p.native()
        cls.data,cls.result=p.calculate()

    def test_original_46k_byte_sources_and_fixed_original_owner(self):
        self.assertEqual(p.sha(p.PREVIEW),p.LOCKS["preview"])
        self.assertEqual(p.sha(p.INCREMENTS),p.LOCKS["increments"])
        self.assertEqual(self.result["source_original_owner_head"],p.LOCKS["owner_git"])

    def test_node_order_exact_one_original_source(self):
        self.assertEqual(len(self.raw),46080)
        self.assertEqual([int(x["node"]) for x in self.raw],list(range(46080)))
        self.assertEqual([int(x["node"]) for x in self.native],list(range(46080)))

    def test_source_3_lanes_are_same_original_physics(self):
        for lane in ("recomb","shield"):
            alt=(p.PREVIEW.parent.parent/lane/p.PREVIEW.name)
            self.assertEqual(p.sha(alt),p.LOCKS["preview"])

    def test_source_conserved_chemical_counts(self):
        H=self.geo["h"];He=self.geo["he"]
        for field,v in (("source_H_nuclei_N_lower",H),
                        ("source_H_nuclei_N_upper",H),
                        ("source_He_nuclei_N_lower",He),
                        ("source_He_nuclei_N_upper",He)):
            src=p.col(self.raw,field)
            self.assertLess(float(np.max(np.abs(src/v-1))),1.5e-12)

    def test_clock_source_not_mock_time(self):
        self.assertEqual(self.result["source_accepted_tick"],"160/131072")
        self.assertEqual(self.result["tick161_source_status"],"UNACCEPTED_NOT_USED")
        self.assertAlmostEqual(self.geo["z"],5.95,delta=1e-12)
        self.assertAlmostEqual(self.geo["dt"],4.87184874916828e9,delta=1e-3)

    def test_native_alphaB_against_independent_decimal50(self):
        with localcontext() as ctx:
            ctx.prec=50
            for T in (Decimal("2200"),Decimal("10000"),Decimal("60000")):
                lam=Decimal("315614")/T
                a=(Decimal("2.753e-14")*lam**Decimal("1.5")
                   /(Decimal(1)+(lam/Decimal("2.740"))**Decimal("0.407"))
                    **Decimal("2.242"))
                got=Decimal(str(float(p.alphaB(float(T)))))
                self.assertLess(abs(got/a-1),Decimal("2e-14"))

    def test_native_alphaB_monotonic(self):
        grid=np.geomspace(2e3,7e4,77)
        alpha=p.alphaB(grid)
        self.assertTrue(np.all(np.diff(alpha)<0))
        self.assertGreater(float(alpha[0]),float(alpha[-1]))

    def test_caseB_cascade_prob_is_positive_decreasing_and_not_native(self):
        grid=np.geomspace(2e3,7e4,77)
        P=p.pB_fit(grid)
        self.assertTrue(np.all((P>0)&(P<1)))
        self.assertTrue(np.all(np.diff(P)<0))
        self.assertAlmostEqual(float(p.pB_fit(1e4)),.677,places=14)
        self.assertEqual(self.result["photon_cascade_branching"],
                         "DIJKSTRA_CANTALUPO_CASEB_FIT_CONDITIONAL")

    def test_source_conditioned_46k_rates_nonnegative_and_bounded(self):
        rows=self.data
        self.assertEqual(len(rows),14)
        self.assertEqual(len(rows[0]),46080)
        for j in (3,4,5,7,8,9):
            self.assertTrue(np.all(np.isfinite(rows[j])))
            self.assertGreater(float(np.min(rows[j])),0)
        self.assertTrue(np.all(rows[3]<=rows[4]))
        self.assertTrue(np.all(rows[4]<=rows[5]))
        self.assertTrue(np.all(rows[7]<=rows[8]))
        self.assertTrue(np.all(rows[8]<=rows[9]))
        self.assertTrue(np.all(rows[9]<=rows[5]))

    def test_native_source_recombination_is_highly_spatially_concentrated(self):
        r=self.result
        self.assertEqual(r["top_1percent_cells_number"],461)
        self.assertEqual(r["top_10percent_cells_number"],4608)
        self.assertTrue(.45<r["top_1percent_cells_recomb_event_fraction"]<.47)
        self.assertTrue(.99<r["top_10percent_cells_recomb_event_fraction"]<1)
        self.assertTrue(.45<r["top_1percent_cells_conditional_Lya_emission_fraction"]<.47)
        self.assertEqual(r["rate_concentration_interpretation"],"SOURCE_NODES_NOT_EQUAL_VOLUME_CELLS")

    def test_rate_erg_and_event_dimensions(self):
        dt=self.result["original_one_tick_s"]
        R=self.result["original_H_CaseB_recomb_s_inv_mid"]
        self.assertAlmostEqual(
            self.result["original_static_tick160_caseB_event_exposure_mid"]/(R*dt),1.,places=14)
        self.assertAlmostEqual(
            self.result["conditional_Lya_line_luminosity_erg_s_mid"]/
             (self.result["conditional_Lya_recomb_fit_s_inv_mid"]*p.E_LYA_ERG),
            1.,places=14)

    def test_independent_proper_volume_common_particle_scaling(self):
        # nHI+ and ne density fixed; N_source volume simultaneous rescaling
        row=180
        N=float(self.geo["h"][row]);ne=float(p.col(self.raw,"tick160_electron_count_N_lower")[row])
        V=float(self.geo["vol"][row]);T=float(p.col(self.raw,"tick160_Tgas_K_lower")[row])
        x=float(p.col(self.raw,"tick160_xHII_lower")[row])
        a=p.alphaB(T)
        r=a*N*x*ne/V
        scale=123.0
        self.assertAlmostEqual((a*(N*scale)*x*(ne*scale)/(V*scale))/r,scale,places=13)

    def test_exact_native_HII_increment_is_not_recomb_events(self):
        lo=self.result["original_native_HII_twohalf_delta_lower"]
        hi=self.result["original_native_HII_twohalf_delta_upper"]
        self.assertLess(lo,hi)
        self.assertLess(hi,0)
        self.assertGreater(self.result["original_static_tick160_caseB_event_exposure_mid"],-lo)
        self.assertEqual(self.result["HII_negative_cells"],42534)
        self.assertEqual(self.result["HII_positive_cells"],2268)
        self.assertEqual(self.result["HII_sign_unresolved_cells"],1278)

    def test_original_recomb_rate_full_source_semantic_alignment(self):
        # Independent scalar direct use of original HII*Ne/V at selected source rows
        H=self.geo["h"];V=self.geo["vol"]
        for j in (0,1024,23039,46079):
            r=self.raw[j]
            T=(float(r["tick160_Tgas_K_lower"])+float(r["tick160_Tgas_K_upper"]))/2
            x=(float(r["tick160_xHII_lower"])+float(r["tick160_xHII_upper"]))/2
            ne=(float(r["tick160_electron_count_N_lower"])+float(r["tick160_electron_count_N_upper"]))/2
            l=315614.0/T
            a=2.753e-14*l**1.5/(1+(l/2.740)**.407)**2.242
            direct=a*H[j]*x*ne/V[j]
            self.assertLess(abs(direct/self.data[4][j]-1),2e-13)

    def test_corrupt_or_missing_sources_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            altered=Path(td)/"input.csv.gz"
            altered.write_bytes(p.PREVIEW.read_bytes()+b"x")
            with self.assertRaisesRegex(ValueError,"SOURCE_SHA_MISMATCH"):
                p.read_csv(altered,p.LOCKS["preview"])
        with self.assertRaisesRegex(ValueError,"INVALID_T"):
            p.alphaB(-1.0)

    def test_not_observable_photo_source_or_official_tick161(self):
        r=self.result
        self.assertFalse(r["original_tick161_officially_accepted"]) if "original_tick161_officially_accepted" in r else self.assertEqual(r["tick161_source_status"],"UNACCEPTED_NOT_USED")
        self.assertEqual(r["observed_escaping_Lya_luminosity"],"NOT_COMPUTED")
        self.assertEqual(r["REI_central"],"28/88_REPORTED_DELTA0")
        self.assertTrue(r["no_REI_owner_mutation"])

    def test_published_new_46k_output_is_deterministic(self):
        with gzip.open(p.HERE/p.DATAFILE,"rt",newline="") as f:
            rd=csv.DictReader(f)
            self.assertEqual(tuple(rd.fieldnames),p.FIELDS)
            self.assertEqual(sum(1 for _ in rd),p.N)
        with tempfile.TemporaryDirectory() as td:
            artifacts,_=p.generate(Path(td))
            for test_path in artifacts:
                self.assertEqual(test_path.read_bytes(),(p.HERE/test_path.name).read_bytes())


if __name__=="__main__":
    unittest.main(verbosity=2)
