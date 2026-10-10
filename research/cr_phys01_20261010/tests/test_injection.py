"""Focused source/transport checks; no full-history or collision solver."""
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
from scipy.integrate import quad

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
import injection as inj


class InjectionTests(unittest.TestCase):
    def test_md14_units_and_salpeter_normalization(self):
        model = inj.InjectionModel()
        z = 8.0
        sfr = .015*(1+z)**2.7/(1+((1+z)/2.9)**5.6)
        expected = 1e44*.1*.0068*sfr/(31557600*(3.085677581491367e22)**3)
        self.assertAlmostEqual(model.power_comoving_J_m3_s()/expected, 1.0, places=14)
        self.assertAlmostEqual(model.power_proper_J_m3_s()/expected, 729.0, places=10)

    def test_energy_normalization_independent_adaptive_quadrature(self):
        model = inj.InjectionModel()
        # Independent log coordinate, adaptive integrator, direct beta formula.
        m = inj.PROTON_REST_EV
        p02 = 1e9*(1e9+2*m)
        def integrand(logk):
            k = math.exp(logk)
            beta = math.sqrt(k*(k+2*m))/(k+m)
            shape = ((k*(k+2*m))/p02)**(-1.1)/beta
            return k*k*shape
        integral, _ = quad(integrand, math.log(1e4), math.log(1e15),
                           epsabs=0, epsrel=2e-12)
        self.assertLess(abs(integral/inj.source_energy_shape_integral()-1), 2e-12)
        computed = model.normalization_m3_s_eV()*integral*inj.EV_J
        self.assertLess(abs(computed/model.power_proper_J_m3_s()-1), 2e-12)

    def test_momentum_powerlaw_jacobian(self):
        k = np.geomspace(1e4, 1e15, 21)
        pc = np.sqrt(k*(k+2*inj.PROTON_REST_EV))
        # q_K = const p^-alpha dp/dK, with constant independent of K.
        inverse_powerlaw = inj.leite_shape(k)*pc**2.2/( (k+inj.PROTON_REST_EV)/pc )
        self.assertLess(np.ptp(inverse_powerlaw)/np.mean(inverse_powerlaw), 2e-14)

    def test_cutoffs_not_extrapolated(self):
        q = inj.InjectionModel().q_proper_m3_s_eV([9999, 1e4, 1e15, 1.001e15])
        self.assertEqual(q[0], 0)
        self.assertEqual(q[-1], 0)
        self.assertGreater(q[1], 0)
        self.assertGreater(q[2], 0)

    def test_stable_relativistic_roundtrip(self):
        k = np.geomspace(1e-8, 1e15, 32)
        got = inj.kinetic_from_pc_eV(inj.momentum_c_eV(k))
        np.testing.assert_allclose(got, k, rtol=5e-16, atol=0)

    def test_isotropic_characteristic_exact(self):
        k = np.array([1e4, 1e6, 1e15])
        mu = np.array([-.8, 0, .7])
        H, age = 2e-14, 1e10
        out = inj.characteristic(k, mu, age, H, 0)
        np.testing.assert_allclose(out["pc_eV"], inj.momentum_c_eV(k)*math.exp(-H*age),
                                   rtol=5e-16)
        np.testing.assert_allclose(out["mu"], mu, rtol=5e-16, atol=0)

    def test_axisymmetric_characteristic_components(self):
        k, mu, age, H, s = 2e6, .6, 1e10, 1e-14, 2e-15
        out = inj.characteristic(k, mu, age, H, s)
        p0 = math.sqrt(k*(k+2*inj.PROTON_REST_EV))
        self.assertAlmostEqual(out["pc_perp_eV"]/(p0*.8*math.exp(-(H-s)*age)), 1, places=14)
        self.assertAlmostEqual(out["pc_parallel_eV"]/(p0*.6*math.exp(-(H+2*s)*age)), 1, places=14)
        self.assertNotEqual(out["mu"], mu)

    def test_static_source_full_energy_and_no_window_renormalization(self):
        model, dt = inj.InjectionModel(), 1e10
        a = inj.transport_population(model, dt, 0, 0, age_order=2, mu_order=2, energy_order=64)
        b = inj.transport_population(model, dt, 0, 0, (2e6,3e6),
                                     age_order=2, mu_order=2, energy_order=64)
        expected = model.power_proper_J_m3_s()*dt
        self.assertLess(abs(a["budgets"]["final_CR_energy_J_m3"]/expected-1), 3e-13)
        self.assertLess(abs(b["budgets"]["final_CR_energy_J_m3"]/expected-1), 3e-13)
        self.assertGreater(a["budgets"]["active_CR_energy_J_m3"],
                           b["budgets"]["active_CR_energy_J_m3"])
        self.assertLess(a["budgets"]["active_CR_energy_J_m3"], expected*.1)
        self.assertEqual(a["budgets"]["adiabatic_work_J_m3"], 0)

    def test_population_partition_and_actual_band(self):
        pop = inj.transport_population(inj.InjectionModel(), 1e10, 1e-14, 2e-15,
                                       age_order=4, mu_order=4, energy_order=32)
        b, nodes = pop["budgets"], pop["nodes"]
        self.assertGreater(len(nodes["kinetic_eV"]), 0)
        self.assertTrue(np.all((nodes["kinetic_eV"]>=1e6)&(nodes["kinetic_eV"]<=4e6)))
        self.assertGreater(b["outside_collision_window_energy_J_m3"], 0)
        self.assertAlmostEqual((b["active_CR_energy_J_m3"]+
                                b["outside_collision_window_energy_J_m3"])/
                               b["final_CR_energy_J_m3"], 1, places=14)
        self.assertAlmostEqual(np.dot(nodes["number_density_m3"],nodes["kinetic_eV"])*
                               inj.EV_J/b["active_CR_energy_J_m3"], 1, places=14)
        self.assertGreater(b["adiabatic_work_J_m3"], 0)

    def test_expanding_population_number_dilution(self):
        model, dt, H = inj.InjectionModel(), 1e10, 1e-14
        pop = inj.transport_population(model, dt, H, 0,
                                       age_order=4, mu_order=2, energy_order=64)
        qnumber, _ = quad(lambda x: math.exp(x)*float(model.q_proper_m3_s_eV(math.exp(x))),
                          math.log(1e4), math.log(1e15), epsabs=0, epsrel=2e-12)
        expected = qnumber*(-math.expm1(-3*H*dt))/(3*H)
        self.assertLess(abs(pop["budgets"]["final_CR_number_m3"]/expected-1), 3e-12)

    def test_orders_refinement_including_split_tails(self):
        model = inj.InjectionModel()
        # Larger bounded expansion than the default pilot exposes moving-band errors.
        a = inj.transport_population(model, 1e10, 2e-11, 5e-12,
                                     age_order=8, mu_order=8, energy_order=48)
        b = inj.transport_population(model, 1e10, 2e-11, 5e-12,
                                     age_order=16, mu_order=16, energy_order=96)
        for field in ("final_CR_energy_J_m3", "active_CR_energy_J_m3",
                      "outside_collision_window_energy_J_m3", "active_CR_number_m3"):
            self.assertLess(abs(a["budgets"][field]/b["budgets"][field]-1), 2e-10)

    def test_off_and_zero_efficiency_do_not_evaluate_spectrum(self):
        for model in (inj.InjectionModel(enabled=False), inj.InjectionModel(cr_efficiency=0),
                      inj.InjectionModel(escape_fraction=0)):
            with patch.object(inj, "source_energy_shape_integral", side_effect=AssertionError("called")):
                pop = inj.transport_population(model, 1e10, 1e-14, 0)
            self.assertEqual(len(pop["nodes"]["kinetic_eV"]), 0)
            self.assertTrue(all(v==0 for v in pop["budgets"].values()))

    def test_zero_duration_and_empty_active_domain(self):
        zero = inj.transport_population(inj.InjectionModel(), 0, 1e-14, 0)
        self.assertEqual(zero["budgets"]["final_CR_energy_J_m3"], 0)
        pop = inj.transport_population(inj.InjectionModel(), 1e10, 0, 0,
                                       (1e16,2e16),age_order=2,mu_order=2,energy_order=64)
        self.assertEqual(len(pop["nodes"]["kinetic_eV"]), 0)
        self.assertEqual(pop["budgets"]["active_CR_energy_J_m3"], 0)
        self.assertGreater(pop["budgets"]["outside_collision_window_energy_J_m3"], 0)

    def test_invalid_input_guards(self):
        for kwargs in ({"z_snapshot":8.1},{"alpha":0},{"cr_efficiency":-1},
                       {"escape_fraction":1.1},{"enabled":1},{"supernova_energy_J":math.inf}):
            with self.assertRaises(ValueError):
                inj.InjectionModel(**kwargs)
        for args in ((-1,0,0),(1,math.nan,0),(1e10,1,0)):
            with self.assertRaises(ValueError):
                inj.transport_population(inj.InjectionModel(), *args)
        with self.assertRaises(ValueError):
            inj.transport_population(inj.InjectionModel(), 1,0,0,(4,1))
        with self.assertRaises(ValueError):
            inj.characteristic(1e6,1.1,1,0,0)
        with self.assertRaises(ValueError):
            inj.leite_shape([0,math.nan])


if __name__ == "__main__":
    unittest.main(verbosity=2)

