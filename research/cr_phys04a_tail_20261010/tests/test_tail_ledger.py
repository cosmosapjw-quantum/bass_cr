import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
from scipy.integrate import quad

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tail_ledger as tail
from provider import convolve_secondary


class TailLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coarse = tail.build_tail_ledger(48, 8, 8)
        cls.fine = tail.build_tail_ledger(64, 12, 12)

    def test_domain_and_positive_channels(self):
        for dt in (-1, math.nan, math.inf, True):
            with self.assertRaises(ValueError):
                tail.build_tail_ledger(dt_s=dt)
        with self.assertRaises(ValueError):
            tail.build_tail_ledger(energy_order=1)
        with self.assertRaises(ValueError):
            tail.build_tail_ledger(enabled=1)
        with self.assertRaises(ValueError):
            tail.build_tail_ledger(split_protons=1)
        for target in tail.rudd.TARGETS:
            for band in tail.BANDS:
                for value in self.fine["targets"][target][band].values():
                    self.assertTrue(math.isfinite(value) and value > 0)
        self.assertEqual(self.fine["deposition_status"], "NOT_COMPUTED")
        self.assertEqual(self.fine["solver_intervals"], 0)

    def test_partition_and_binding_additivity(self):
        for target, bands in self.fine["targets"].items():
            for key in tail.MOMENT_KEYS:
                partition = math.fsum([bands["within_table_energy"][key], bands["above_table_energy"][key]])
                self.assertLess(abs(partition/bands["all"][key]-1), 3e-13)
                segments = math.fsum(segment["targets"][target]["all"][key]
                                     for segment in self.fine["segments"])
                self.assertEqual(segments, bands["all"][key])
            for moments in bands.values():
                self.assertLess(abs(math.fsum([moments["binding_j_m3_s"], moments["secondary_j_m3_s"]])
                                    / moments["loss_j_m3_s"] - 1), 3e-13)

    def test_zero_age_and_off_do_not_evaluate_collision_kernel(self):
        with patch.object(tail.rudd, "cross_section_moments", side_effect=AssertionError("kernel called")):
            for kwargs in ({"dt_s": 0}, {"enabled": False}):
                ledger = tail.build_tail_ledger(**kwargs)
                self.assertEqual(ledger["active_cr_energy_j_m3"], 0)
                self.assertEqual(ledger["sampled_fractional_ionization_loss_age_estimate"], 0)
                for band in tail.BANDS:
                    self.assertEqual(list(ledger["combined"][band].values()), [0.0]*4)

    def test_analytic_moments_against_direct_sdcs_quadrature(self):
        # The oracle integrates the independently exposed differential kernel,
        # with its m^2 scale factored out so quad's absolute tolerance is useful.
        for target in tail.rudd.TARGETS:
            for kinetic in (4e6, 5e6, 1e7):
                maximum = float(tail.rudd.secondary_max_eV(kinetic, target))
                for low, high in ((0, min(tail.SECONDARY_MAX_EV, maximum)),
                                  (min(tail.SECONDARY_MAX_EV, maximum), maximum)):
                    if low == high:
                        continue
                    analytic = tail.rudd.cross_section_moments(kinetic, target, low, high)
                    # log(1+W/I) is smooth across the entire ejection support.
                    binding = tail.rudd.TARGETS[target]["I_eV"]
                    a, b = math.log1p(low/binding), math.log1p(high/binding)
                    for power, key in ((0, "sigma_m2"), (1, "secondary_eV_m2")):
                        def integrand(x):
                            w = binding * math.expm1(x)
                            return float(tail.rudd.dsigma_dW_m2_per_eV(kinetic, w, target)) * 1e20 * w**power * binding * math.exp(x)
                        direct = quad(integrand, a, b, epsabs=1e-12, epsrel=2e-12)[0] / 1e20
                        self.assertLess(abs(direct/float(analytic[key])-1), 2e-10)

    def test_exact_breaks_and_refinement(self):
        self.assertEqual(self.fine["proton_edges_eV"], list(tail.PROTON_EDGES_EV))
        for target, crossing in zip(("H", "He"), tail.PROTON_EDGES_EV[1:-1]):
            self.assertLess(abs(float(tail.rudd.secondary_max_eV(crossing, target))/tail.SECONDARY_MAX_EV - 1), 4e-16)
        result = tail.refinement(self.coarse, self.fine)
        self.assertEqual(result["status"], "PASS_SCOPED", result)
        self.assertLessEqual(result["maximum_relative_difference"], 2e-6)

    def test_production_guard_remains_one_to_four_mev(self):
        with self.assertRaisesRegex(ValueError, "COMMON_PROVIDER_DOMAIN_1_TO_4_MEV"):
            convolve_secondary(np.array([5e6]), "H", None)


if __name__ == "__main__":
    unittest.main()
