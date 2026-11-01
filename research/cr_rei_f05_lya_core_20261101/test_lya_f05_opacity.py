#!/usr/bin/env python3
"""Tests of real F05 native 46k H/He lyalpha-to-Thomson opacity bound."""
import csv
import gzip
import math
import tempfile
import unittest
from pathlib import Path
from decimal import Decimal,localcontext
import lya_f05_opacity as p


class OriginalF05LineScattering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=p.load_rows()
        cls.report=__import__("json").loads((p.HERE/"RESULT.json").read_text())

    def test_original_source_byte_identity(self):
        self.assertEqual(p.sha256(p.PRIVATE_SOURCE),p.SOURCE_SHA256)

    def test_three_original_shape_lanes_equal(self):
        for lane in ("recomb","shield"):
            q=p.PRIVATE_SOURCE.parent.parent/lane/p.PRIVATE_SOURCE.name
            self.assertEqual(p.sha256(q),p.SOURCE_SHA256)

    def test_source_node_number_and_size(self):
        self.assertEqual(len(self.source),46080)
        self.assertEqual([int(x["node"]) for x in self.source],list(range(46080)))

    def test_original_source_H_He_charge_stoichiometry(self):
        for row in self.source:
            yes,error=p.source_preview_electron_stoichiometry(row)
            self.assertTrue(yes)
            self.assertLessEqual(abs(error),8e-15)

    def test_line_energy_and_atomic_Doppler_reference(self):
        self.assertAlmostEqual(p.H_PLANCK*p.NU_ALPHA/p.ERG_PER_EV,
                               10.198835887565243,places=11)
        self.assertAlmostEqual(p.sigma0_cm2(1e4),5.894917537882223e-14,
                               delta=2e-26)
        self.assertLess(abs(p.sigma0_cm2(1e4)/5.88e-14-1),0.004)

    def test_voigt_sigma_monotone_temperature(self):
        prev=math.inf
        for T in (10.,200.,1000.,2096.,5000.,10000.,66262.,2e5,1e8):
            sig=p.sigma0_cm2(T)
            self.assertTrue(0<sig<prev)
            prev=sig

    def test_independent_source_intervals_all_nodes(self):
        for row in self.source:
            for tag in ("tick160","tick161_preview"):
                v=p.numeric_bounds(row,tag)
                self.assertTrue(0<v[0]<=v[1]<=v[2])
                self.assertTrue(0<v[4]<=v[5]<=v[6])
                self.assertTrue(0<v[7]<=v[8]<=v[9])
            a=p.numeric_bounds(row,"tick160");b=p.numeric_bounds(row,"tick161_preview")
            d_lo=math.log(b[0]/a[2]);d_hi=math.log(b[2]/a[0])
            d_mid=math.log(b[1]/a[1])
            self.assertLessEqual(d_lo-2e-13,d_mid)
            self.assertLessEqual(d_mid,d_hi+2e-13)

    def test_volume_and_particle_scale_cancel(self):
        for row in self.source[::3071]:
            old=p.numeric_bounds(row,"tick160")
            new=dict(row)
            for col,val in row.items():
                if col.startswith(("source_H_nuclei_N_","tick160_electron_count_N_")):
                    new[col]=str(float(val)*1e-4)
            new_ratio=p.numeric_bounds(new,"tick160")
            for j in (0,1,2):
                self.assertTrue(math.isclose(old[j],new_ratio[j],rel_tol=2e-13))

    def test_unmeasured_ground_population_cannot_be_promoted(self):
        a=p.numeric_bounds(self.source[1234],"tick160")
        for g1 in (0.,.01,.5,1.):
            actual=g1*a[1]
            self.assertTrue(0<=actual<=a[2]*(1+1e-14))
        self.assertEqual(self.report["line_ground_population"],
                         "g_1=1_saturation_model_not_source_measured")

    def test_negative_temperature_and_bad_source_rejected(self):
        with self.assertRaises(ValueError):
            p.sigma0_cm2(-5.)
        with tempfile.TemporaryDirectory() as td:
            bad=Path(td)/"bad_source.csv.gz"
            bad.write_bytes(p.PRIVATE_SOURCE.read_bytes() + b"extra")
            with self.assertRaisesRegex(ValueError,"byte lock"):
                p.load_rows(bad)

    def test_numerically_independent_decimal50_selected_cells(self):
        with localcontext() as ctx:
            ctx.prec=50
            for k in (0,1024,23039,46079):
                row=self.source[k]
                fl=lambda key:Decimal(row[key])
                nh=fl("source_H_nuclei_N_lower")
                ne=fl("tick160_electron_count_N_lower")
                x=fl("tick160_xHII_lower")
                s=Decimal(str(p.sigma0_cm2(float(fl("tick160_Tgas_K_lower")))))
                reference=(nh/ne)*(1-x)*s/Decimal(str(p.SIGMA_T))
                upper=Decimal(str(p.numeric_bounds(row,"tick160")[2]))
                self.assertLess(abs(reference/upper-1),Decimal("4e-12"))

    def test_output_rows_and_no_private_source_members(self):
        with gzip.open(p.HERE/"REI_F05_HI_LYA_TO_THOMSON_46080.csv.gz",
                       "rt",newline="") as f:
            reader=csv.DictReader(f)
            self.assertEqual(tuple(reader.fieldnames),p.FIELDS)
            result=list(reader)
        self.assertEqual(len(result),46080)
        self.assertFalse(any(s in p.FIELDS for s in (
            "source_H_nuclei_N_lower", "tick160_Tgas_K_lower",
            "tick161_preview_electron_count_N_lower")))
        for i in (0,23,2048,46079):
            row=result[i]
            self.assertEqual(int(row["node"]),i)
            self.assertTrue(0<float(row["saturated_R_tick160_lower"])
                            <=float(row["saturated_R_tick160_upper"]))

    def test_global_area_positive_not_optical_depth(self):
        for tag in ("tick160_accepted","tick161_NONAUTHORITATIVE_preview"):
            d=self.report[tag]
            self.assertLess(d["global_cross_section_area_ratio_lower"],
                            d["global_cross_section_area_ratio_upper"])
            self.assertGreater(d["total_HI_N_lower"],0.)
            self.assertGreater(d["geometric_HI_Lya_area_cm2_lower"],0.)
        self.assertEqual(self.report["measured_lya_optical_depth"],
                         "NOT_COMPUTABLE_WITHOUT_PHOTON_FREQUENCY_AND_PATH")
        self.assertEqual(self.report["REI_central_DAG"],
                         "28/88_REPORTED_DELTA0")

    def test_accepted_tick_and_unapproved_preview_labels(self):
        self.assertEqual(self.report["accepted_tick"],160)
        self.assertEqual(self.report["preview_tick_not_accepted"],161)
        self.assertEqual(self.report["PRODUCTION"],"HOLD")
        self.assertTrue(self.report["CR_OFF_UNCHANGED"])

    def test_cold_source_output_byte_reproduction(self):
        with tempfile.TemporaryDirectory() as td:
            _,out=p.generate(outdir=Path(td))
            for item in out:
                self.assertEqual(item.read_bytes(),(p.HERE/item.name).read_bytes())


if __name__=="__main__":
    unittest.main(verbosity=2)
