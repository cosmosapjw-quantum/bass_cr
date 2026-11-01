#!/usr/bin/env python3
"""Bounded falsification tests for 2016 published CX table and conditional closure."""
import math
import random
import unittest
from pathlib import Path
import primary_source_and_moments as p


class PublishedTableTests(unittest.TestCase):
    def test_exact_primary_2016_seven_rows(self):
        rows = p.table2()
        expected = (
            (1e-4, 4047., 3640., 3642.),
            (1e-3, 1154., 1111., 1111.),
            (1e-2, 327.2, 322.5, 322.5),
            (1e-1, 223.2, 222.7, 222.8),
            (1., 162.2, 162.2, 162.2),
            (10., 121., 121., 121.),
            (100., 85.10, 85.10, 85.10),
        )
        self.assertEqual(tuple(tuple(r[k] for k in
            ("E_cm_eV", "cx_2016_a0_sq",
             "cx_no_l0_a0_sq", "cx_2008_a0_sq")) for r in rows), expected)

    def test_source_fit_support_has_four_original_points(self):
        rows = p.crosswalk()
        self.assertEqual(sum(r["within_existing_3_to_200_km_s_fit_window"]
                             for r in rows), 4)
        self.assertEqual(
            [r["E_cm_eV"] for r in rows
             if r["within_existing_3_to_200_km_s_fit_window"]],
            [0.1, 1., 10., 100.])

    def test_2016_low_energy_swave_correction_not_hidden(self):
        r = p.crosswalk()[0]
        self.assertAlmostEqual(r["relative_missing_l0_correction"],
                               4047./3640.-1., places=13)
        self.assertGreater(r["relative_missing_l0_correction"], 0.11)

    def test_1999_extrapolation_is_not_falsely_supported(self):
        r = p.crosswalk()[0]
        self.assertFalse(r["within_existing_3_to_200_km_s_fit_window"])
        self.assertLess(r["A4_vs_primary_fraction"], -0.8)

    def test_a4_in_window_primary_anchors(self):
        four = p.crosswalk()[3:]
        expected_percent = (-4.962, 0.3967, -0.7707, -1.5317)
        for r, expected in zip(four, expected_percent):
            self.assertAlmostEqual(
                100. * r["A4_vs_primary_fraction"], expected, delta=0.01)

    def test_energy_speed_bijection(self):
        for e in (1e-4, 0.0235, 0.1, 1., 10., 100., 1e4):
            g = p.cm_speed_from_energy_cm_s(e)
            self.assertAlmostEqual(p.energy_cm_eV_from_speed(g)/e, 1.,
                                   delta=1e-14)

    def test_2016_rounded_atomic_area_source_unit(self):
        self.assertAlmostEqual(4047.*p.A0SQ_CM2_PUBLISHED_ROUNDED,
                               1.13328141e-13, delta=1e-24)


class AngularMomentTests(unittest.TestCase):
    def test_tabulated_preweighted_isotropic_total_mt_viscosity(self):
        N = 4001
        theta = [math.pi*j/N for j in range(N+1)]
        sigma = 17.
        # f(theta)=2*pi*sin(theta)*dSigma/dOmega=sigma*sin(theta)/2
        ds = [0.5*sigma*math.sin(t) for t in theta]
        q = p.angular_moments_preweighted(theta, ds, "charged_cm")
        self.assertAlmostEqual(q["sigma_total_a0_sq"], sigma, delta=1e-5)
        self.assertAlmostEqual(q["sigma_mt_charge_a0_sq"], sigma, delta=1e-5)
        self.assertAlmostEqual(q["sigma_viscosity_a0_sq"],
                               2.*sigma/3., delta=1e-5)

    def test_charge_nuclear_exchange_inverse_angle(self):
        N = 1200
        theta = [math.pi*j/N for j in range(N+1)]
        ds = [math.sin(t)*math.exp(-(t/0.1)**2) for t in theta]
        nuclear = p.angular_moments_preweighted(theta, ds, "nuclear_cx_cm")
        charged = p.angular_moments_preweighted(theta, ds, "charged_cm")
        total = nuclear["sigma_total_a0_sq"]
        self.assertAlmostEqual(nuclear["sigma_mt_charge_a0_sq"]+
                               charged["sigma_mt_charge_a0_sq"],
                               2.*total, delta=1e-11)
        self.assertGreater(nuclear["sigma_mt_charge_a0_sq"], 1.95*total)

    def test_refuse_ambiguous_angular_frame(self):
        with self.assertRaises(ValueError):
            p.angular_moments_preweighted([0.,1.,math.pi],[0.,1.,0.],
                                         "angle_unspecified")

    def test_refuse_nonmonotone_or_negative_dcs(self):
        with self.assertRaises(ValueError):
            p.angular_moments_preweighted([0., 2., 1.],[0.,1.,0.],
                                         "charged_cm")
        with self.assertRaises(ValueError):
            p.angular_moments_preweighted([0.,1.,math.pi],[0.,-1.,0.],
                                         "charged_cm")


class MaxwellMomentClosureTests(unittest.TestCase):
    def calc(self, **kwargs):
        args = dict(k_mt_cm3_s=1.5e-8, n_ion_cm3=3e-4,
                    n_H_cm3=2e-3, u_ion_cm_s=(1000.,0.,0.),
                    u_H_cm_s=(0., 100., 0.), T_ion_K=5002., T_H_K=5000.)
        args.update(kwargs)
        return p.linear_momentum_energy_exchange(**args)

    def test_force_exact_opposite(self):
        q=self.calc()
        for x,y in zip(q["R_ion_g_cm_minus2_s_minus2"],
                       q["R_H_g_cm_minus2_s_minus2"]):
            self.assertEqual(x, -y)

    def test_energy_exchange_conserves_total_in_local_frame(self):
        q=self.calc()
        self.assertEqual(q["Q_ion_erg_cm_minus3_s_minus1"],
                         -q["Q_H_erg_cm_minus3_s_minus1"])

    def test_drift_heating_equal_power_loss(self):
        U=(1000.,-100.,0.)
        q=self.calc()
        R=q["R_ion_g_cm_minus2_s_minus2"]
        wanted=-sum(x*y for x,y in zip(U,R))
        self.assertAlmostEqual(q["total_frictional_internal_heating_erg_cm_minus3_s_minus1"],
                               wanted, delta=max(1e-40, 1e-12*abs(wanted)))
        self.assertGreater(q["total_frictional_internal_heating_erg_cm_minus3_s_minus1"],0)

    def test_temperature_exchange_when_zero_drift(self):
        q=self.calc(u_ion_cm_s=(0.,0.,0.),u_H_cm_s=(0.,0.,0.))
        self.assertTrue(all(x==0 for x in q["R_ion_g_cm_minus2_s_minus2"]))
        self.assertLess(q["Q_ion_erg_cm_minus3_s_minus1"], 0)
        self.assertGreater(q["Q_H_erg_cm_minus3_s_minus1"], 0)

    def test_exact_zero_chemistry_input_no_collision(self):
        q=self.calc(n_ion_cm3=0)
        self.assertEqual(q["Q_ion_erg_cm_minus3_s_minus1"],0)
        self.assertEqual(q["R_ion_g_cm_minus2_s_minus2"],(0.,0.,0.))

    def test_equal_mass_thermal_and_drift_relaxation_eigenrate(self):
        q=self.calc(m_ion_g=1.7e-24,m_H_g=1.7e-24)
        self.assertAlmostEqual(q["linear_drift_relaxation_s_minus1"],
                               q["linear_temperature_relaxation_s_minus1"],
                               delta=1e-14*q["linear_drift_relaxation_s_minus1"])

    def test_unequal_mass_formula_lambdas(self):
        q=self.calc()
        mi=p.original.MP_G; mn=p.original.MH_G
        mu=mi*mn/(mi+mn)
        k=1.5e-8; ni=3e-4; nn=2e-3
        self.assertAlmostEqual(q["linear_drift_relaxation_s_minus1"],
                               mu*k*(nn/mi+ni/mn))
        self.assertAlmostEqual(q["linear_temperature_relaxation_s_minus1"],
                               2*mu/(mi+mn)*k*(ni+nn))

    def test_invalid_inputs_fail(self):
        for kwargs in (dict(k_mt_cm3_s=-1.),dict(T_ion_K=0.),
                       dict(n_ion_cm3=-1.),dict(u_ion_cm_s=(math.nan,0.,0.))):
            with self.assertRaises(ValueError):
                self.calc(**kwargs)

    def test_randomized_energy_and_momentum_balance(self):
        rnd=random.Random(20261101)
        for i in range(128):
            U=tuple(rnd.uniform(-10000,10000) for _ in range(3))
            q=self.calc(u_ion_cm_s=U,u_H_cm_s=(0.,0.,0.),
                        T_ion_K=5000+rnd.uniform(-10,10),T_H_K=5000)
            self.assertEqual(tuple(-x for x in q["R_H_g_cm_minus2_s_minus2"]),
                             q["R_ion_g_cm_minus2_s_minus2"])
            self.assertEqual(-q["Q_H_erg_cm_minus3_s_minus1"],
                             q["Q_ion_erg_cm_minus3_s_minus1"])
            self.assertGreaterEqual(
                q["total_frictional_internal_heating_erg_cm_minus3_s_minus1"],
                -1e-39)


if __name__=="__main__":
    unittest.main()
