#!/usr/bin/env python3
"""Primary 2016 Table 1 sparse quantum DCS source check."""
import math
import unittest
import primary_table1_dcs_samples as p


class PublishedSparseDcsTests(unittest.TestCase):
    def test_all_48_original_numbers_independently_transcribed(self):
        expected=(
            (100,6.951,2.492e-5,58.93,5.568,3.311e-5,0.9539),
            (200,8.957,3.452e-5,57.11,5.252,6.353e-5,1.024),
            (400,10.50,3.452e-5,56.95,5.252,8.840e-5,1.024),
            (600,11.13,3.452e-5,56.97,5.252,9.361e-5,1.024),
            (800,11.49,3.452e-5,56.99,5.252,9.540e-5,1.024),
            (1000,11.74,3.452e-5,57.00,5.252,9.618e-5,1.024),
            (1200,11.94,3.452e-5,57.01,5.252,9.656e-5,1.024),
            (1400,12.12,3.452e-5,57.02,5.252,9.674e-5,1.024),
        )
        got=tuple(tuple(r[k] for k in (
            "ell_max","elastic_theta_forward_a0_sq",
            "charge_exchange_theta_forward_a0_sq",
            "elastic_theta_mid_a0_sq","charge_exchange_theta_mid_a0_sq",
            "elastic_theta_back_a0_sq",
            "charge_exchange_theta_back_a0_sq")) for r in p.source_rows())
        self.assertEqual(got,expected)

    def test_48_actual_published_dcs_values_not_full_matrix(self):
        rows=p.published_samples()
        self.assertEqual(len(rows),48)
        self.assertEqual({r["E_cm_eV"] for r in rows},{1.})
        self.assertEqual(len({r["theta_rad"] for r in rows}),3)
        self.assertEqual({r["channel"] for r in rows},
            {"elastic_distinguishable","CX_distinguishable"})
        self.assertTrue(all(not r["raw_full_DCS_768_angles"] for r in rows))

    def test_distinguishable_forward_elastic_not_well_converged(self):
        s=p.summary()
        self.assertGreater(s["elastic_forward_relative_change_l100_to_1400"],
                           0.7)
        self.assertGreater(s["elastic_forward_relative_change_l1200_to_1400"],
                           0.01)

    def test_cx_backward_printed_value_stable_after_l200(self):
        r=p.source_rows()
        self.assertTrue(all(x["charge_exchange_theta_back_a0_sq"]==1.024
                            for x in r[1:]))

    def test_actual_angles_are_neither_0_nor_exact_pi(self):
        self.assertGreater(p.ANGLES["forward"],0.)
        self.assertLess(p.ANGLES["back"],math.pi)
        self.assertEqual(p.ANGLES["mid"],1.56759)

    def test_no_fake_integration_from_three_angles(self):
        s=p.summary()
        self.assertEqual(s["full_original_DCS_matrix"],"NOT_RETRIEVED")
        self.assertEqual(s["integral_cross_section_from_3_angles"],
                         "NOT_COMPUTED")

if __name__=="__main__":
    unittest.main()
