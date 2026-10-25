"""Targeted tests of new semantics/arithmetic only; no old provider suites."""
from __future__ import annotations
import argparse
from copy import deepcopy
from decimal import Decimal
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import resource
import tempfile
import time
import unittest

import n5_semantics as n5
from decimal_reference import (reference_envelope, reference_first_event,
                               reference_hazard_limit, reference_product, scaled_error)
from dispatcher import MIB, create_output, memory_admission


def provider_fixture():
    return {"process": "CE", "nuclide": "H1", "charge": 0, "internal_state": "1S",
            "quantity_kind": "Maxwell_thermal_rate_coefficient", "frame": "bath_frame_rest_target",
            "clock": "proper_seconds", "unit": "cm^3/s", "interpolation": "none_exact_saved_T_row",
            "isotope_mapping": "source_H1_only", "owner_gate": "NUMERICALLY_CHECKED_SCOPED",
            "temperature_K_values": [10000], "value": 1e-10, "source_identity": "SYNTHETIC_ADMISSION_FIXTURE"}


def request_fixture():
    p = provider_fixture()
    return {**{key: p[key] for key in n5.IDENTITY_KEYS}, "temperature_K": 10000}


class SemanticTests(unittest.TestCase):
    def test_required_selectors_c9(self):
        # Every provider-declared selector is mandatory; omission cannot mean
        # "any temperature/energy/angle". The existing fully selected case stays valid.
        provider = provider_fixture()
        request = request_fixture()
        del request["temperature_K"]
        result = n5.admit_rate(request, provider)
        self.assertFalse(result["admitted"])
        self.assertIsNone(result["value"])
        provider.pop("temperature_K_values")
        self.assertFalse(n5.admit_rate(request, provider)["admitted"])
        cases = (("incident_energy_eV", "incident_energy_eV_values", [20], 20),
                 ("energy_domain_eV", "energy_domain_eV", [1, 10], [2, 9]),
                 ("outgoing_energy_domain_eV", "outgoing_energy_domain_eV", [3, 6], [3, 6]),
                 ("angle_domain_deg", "angle_domain_deg", [15, 120], [15, 120]))
        for selector, field, values, selected in cases:
            provider = provider_fixture()
            provider[field] = values
            request = request_fixture()
            self.assertFalse(n5.admit_rate(request, provider)["admitted"], selector)
            request[selector] = None
            self.assertFalse(n5.admit_rate(request, provider)["admitted"], selector)
            request[selector] = selected
            self.assertTrue(n5.admit_rate(request, provider)["admitted"], selector)
        provider = provider_fixture()
        request = request_fixture()
        provider.pop("temperature_K_values")
        request.pop("temperature_K")
        provider["quantity_kind"] = request["quantity_kind"] = "tagged_electron_collision_hazard"
        provider["unit"] = request["unit"] = "per_proper_second"
        self.assertFalse(n5.admit_rate(request, provider)["admitted"])
        provider["energy_domain_eV"] = [1, 10]
        request["energy_domain_eV"] = [2, 9]
        self.assertTrue(n5.admit_rate(request, provider)["admitted"])
        self.assertTrue(n5.admit_rate(request_fixture(), provider_fixture())["admitted"])

    def test_exact_admission(self):
        result = n5.admit_rate(request_fixture(), provider_fixture())
        self.assertTrue(result["admitted"])
        self.assertEqual(result["value"], 1e-10)

    def test_quantity_mismatch_not_tagged_hazard_or_heat(self):
        for kind in ("tagged_electron_collision_hazard", "energy_loss_moment", "angular_joint_secondary_law"):
            req = request_fixture()
            req["quantity_kind"] = kind
            result = n5.admit_rate(req, provider_fixture())
            self.assertFalse(result["admitted"])
            self.assertIsNone(result["value"])

    def test_frame_clock_and_unit(self):
        for key, value in (("frame", "tilted_frame"), ("clock", "conformal_seconds"), ("unit", "m^3/s")):
            req = request_fixture()
            req[key] = value
            self.assertFalse(n5.admit_rate(req, provider_fixture())["admitted"])

    def test_isotope_and_internal_state(self):
        for key, value in (("nuclide", "D"), ("internal_state", "2S"), ("isotope_mapping", "elemental_H_equality"), ("charge", True)):
            req = request_fixture()
            req[key] = value
            result = n5.admit_rate(req, provider_fixture())
            self.assertFalse(result["admitted"])
            self.assertIsNone(result["value"])

    def test_wait_gate_rejected(self):
        for gate in ("NUMERICAL_ADMISSION_WAIT", "SOURCE_INPUT_PENDING", "CODE_EXISTS", None):
            provider = provider_fixture()
            provider["owner_gate"] = gate
            self.assertFalse(n5.admit_rate(request_fixture(), provider)["admitted"])

    def test_missing_and_unqualified_zero(self):
        self.assertIsNone(n5.admit_rate(request_fixture(), None)["value"])
        for value in (None, 0.0, True, float("nan"), float("inf"), -1):
            provider = provider_fixture()
            provider["value"] = value
            result = n5.admit_rate(request_fixture(), provider)
            self.assertFalse(result["admitted"])
            self.assertIsNone(result["value"])
            json.dumps(result, allow_nan=False)

    def test_explicit_owner_zero(self):
        provider = provider_fixture()
        provider.update(value=0.0, zero_basis="explicit_owner_exact_zero")
        self.assertTrue(n5.admit_rate(request_fixture(), provider)["admitted"])

    def test_temperature_exact_only(self):
        req = request_fixture()
        req["temperature_K"] = 10000.00001
        self.assertFalse(n5.admit_rate(req, provider_fixture())["admitted"])
        rows = [{"temperature_K": "10000.0", "q": "1"}, {"temperature_K": "10001", "q": "2"}]
        self.assertEqual(n5.exact_temperature_rows(rows, 10000)[0]["q"], "1")
        with self.assertRaises(n5.InputError):
            n5.exact_temperature_rows(rows, 10000.5)
        with self.assertRaises(n5.InputError):
            n5.exact_temperature_rows(rows, True)

    def test_initial_source_vs_full_path(self):
        initial = n5.domain_coverage(["0", "10"], ["10.20435", "968.6058"], threshold="10.20435")
        full = n5.domain_coverage(["1.29", "68.94"], ["10.20435", "968.6058"], threshold="10.20435")
        self.assertEqual(initial["reason"], "OWNER_THRESHOLD_ZERO")
        self.assertEqual(initial["value"], 0)
        self.assertTrue(full["covered"])
        self.assertIsNone(full["value"])
        for support in (["24.6", "60"], ["6", "15"]):
            self.assertFalse(n5.domain_coverage(["1.29", "68.94"], support, threshold=support[0])["covered"])

    def test_window_floor_not_threshold(self):
        self.assertFalse(n5.domain_coverage([0, 10], [13.6, 1000])["covered"])
        self.assertIsNone(n5.domain_coverage([0, 10], [13.6, 1000])["value"])
        self.assertFalse(n5.domain_coverage([0, 20], [14, 1000], threshold=13.6)["covered"])
        self.assertFalse(n5.domain_coverage([0, 20], None)["covered"])

    def test_he_angular_and_incident_window(self):
        provider = provider_fixture()
        provider.update(incident_energy_eV_values=[20], outgoing_energy_domain_eV=[3, 6], angle_domain_deg=[15, 120])
        req = request_fixture()
        req.update(incident_energy_eV=20, outgoing_energy_domain_eV=[3, 6], angle_domain_deg=[15, 120])
        self.assertTrue(n5.admit_rate(req, provider)["admitted"])
        for key, value in (("incident_energy_eV", 30), ("angle_domain_deg", [0, 180]), ("outgoing_energy_domain_eV", [0, 20])):
            bad = deepcopy(req)
            bad[key] = value
            self.assertFalse(n5.admit_rate(bad, provider)["admitted"])


class AlgebraTests(unittest.TestCase):
    def test_decimal_coercion_underflow_c9(self):
        for value in (Decimal("1e-1000"), Decimal("-1e-1000")):
            with self.assertRaisesRegex(n5.InputError, "NONZERO_COERCION_UNDERFLOW"):
                n5.real(value, "tiny_Decimal")
            with self.assertRaisesRegex(n5.InputError, "NONZERO_COERCION_UNDERFLOW"):
                n5.product(1, value)
        self.assertEqual(n5.real(Decimal("0e-1000"), "zero_Decimal"), 0.0)
        self.assertEqual(n5.real(Decimal("-0e-1000"), "signed_zero_Decimal"), 0.0)
        self.assertEqual(n5.real(Decimal("1e-20"), "representable_Decimal"), 1e-20)
        self.assertEqual(n5.real(0.0, "JSON_float_zero"), 0.0)

    def test_hcrit_decimal(self):
        for epsilon in (1e-20, 0.01, 0.1, 0.5, 0.999999):
            for mean in (1e-5, 3.25, 2.8e5):
                actual = n5.hazard_limit(epsilon, mean)
                self.assertLessEqual(scaled_error(actual, reference_hazard_limit(epsilon, mean)), Decimal("5e-14"))
        self.assertEqual(n5.hazard_limit(0, 10), 0)

    def test_product_decimal(self):
        for values in ((0.14, 7.1e-13, 2.8e5), (1e-100, 1e100), (0, 2), (0.1, 0.2, 0.3)):
            self.assertLessEqual(scaled_error(n5.product(*values), reference_product(*values)), Decimal("5e-14"))

    def test_invalid_arithmetic(self):
        for bad in (True, -1, float("nan"), float("inf"), "0.1"):
            with self.assertRaises(n5.InputError):
                n5.hazard_limit(bad, 10)
            with self.assertRaises(n5.InputError):
                n5.product(1, bad)
        for epsilon, mean in ((1, 10), (1.1, 10), (0.1, 0), (0.1, -1), (0.1, True)):
            with self.assertRaises(n5.InputError):
                n5.hazard_limit(epsilon, mean)
        for values in ((1e308, 1e308), (1e-300, 1e-300)):
            with self.assertRaises(n5.InputError):
                n5.product(*values)
        with self.assertRaises(n5.InputError):
            n5.hazard_limit(1e-300, 1e300)
        with self.assertRaises(n5.InputError):
            n5.first_event_estimate(1, 2, 1.1)

    def test_jensen_toy_distributions(self):
        for exposure in (1e-10, 0.001, 0.1, 1, 10, 1000):
            bound = n5.first_event_estimate(exposure, 1)["active_first_event_upper_estimate"]
            deterministic = -math.expm1(-exposure)
            exponential = exposure / (1 + exposure)
            two_point = -0.5 * math.expm1(-2 * exposure)
            self.assertEqual(bound, deterministic)
            self.assertLessEqual(exponential, bound + 1e-16)
            self.assertLessEqual(two_point, bound + 1e-16)

    def test_active_and_whole_distinct(self):
        result = n5.first_event_estimate(2e-9, 2e5, 0.42)
        active, whole = reference_first_event(2e-9, 2e5, 0.42)
        self.assertLessEqual(scaled_error(result["active_first_event_upper_estimate"], active), Decimal("5e-14"))
        self.assertLessEqual(scaled_error(result["whole_selected_first_event_upper_estimate"], whole), Decimal("5e-14"))
        self.assertLess(result["whole_selected_first_event_upper_estimate"], result["active_first_event_upper_estimate"])
        self.assertEqual(n5.first_event_estimate(0, 2, 0.4)["active_first_event_upper_estimate"], 0)


class EnvelopeTests(unittest.TestCase):
    def check_envelope(self, channels, domain):
        result = n5.ce_envelope(channels, domain, threshold_eV=1, n_1s_cm3=0.9, eV_J=0.5, m_e_kg=1)
        reference = reference_envelope(channels, domain, 1, 0.9, 0.5, 1)
        self.assertLessEqual(scaled_error(result["hmax_per_proper_s"], reference["hmax"]), Decimal("5e-14"))
        return result

    def test_known_endpoint_maximum(self):
        result = self.check_envelope({"synthetic": ([1, 2, 9], [0, 2, 9])}, [0.5, 9])
        self.assertEqual(result["maximizing_energy_eV"], 9)
        self.assertAlmostEqual(result["hmax_per_proper_s"], 270)
        self.assertEqual(result["endpoint_samples"][0]["h_total_per_proper_s"], 0)

    def test_stationary_point_is_minimum(self):
        result = self.check_envelope({"synthetic": ([1, 2, 9], [0, 6, 13])}, [2, 9])
        self.assertGreater(result["stationary_candidate_count"], 0)
        self.assertNotEqual(result["candidate_type"], "stationary_b_over_a")

    def test_union_grid_and_clipped_endpoints(self):
        result = self.check_envelope({"a": ([1, 2, 5], [0, 4, 1]), "b": ([1, 3, 5], [0, 2, 1])}, [1.5, 4.5])
        self.assertEqual(result["maximizing_energy_eV"], 2)
        self.assertEqual([row["energy_eV"] for row in result["endpoint_samples"]], [1.5, 2, 3, 4.5])
        self.assertEqual(result["union_panel_count"], 3)

    def test_uncovered_path_and_bad_source(self):
        for channels, domain in (({"a": ([1, 2], [0, 1])}, [1, 3]),
                                  ({"a": ([1, 1], [0, 1])}, [1, 2]),
                                  ({"a": ([1, 2], [0, -1])}, [1, 2]),
                                  ({"a": ([1, 2], [1, 2])}, [1, 2]),
                                  ({"a": ([1, 2], [0, 1])}, [0, 2])):
            with self.assertRaises(n5.InputError):
                self.check_envelope(channels, domain)


class ExecutionContractTests(unittest.TestCase):
    def test_manifest_pin_and_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "inputs").mkdir()
            data = root / "inputs/data.json"
            data.write_text('{"saved": 1}\n')
            manifest = {"files": [{"path": "inputs/data.json", "sha256": hashlib.sha256(data.read_bytes()).hexdigest(), "bytes": data.stat().st_size}]}
            (root / "inputs/INPUT_MANIFEST.json").write_text(json.dumps(manifest))
            self.assertEqual(n5.verify_manifest(root)["verified_files"], 1)
            data.write_text('{"saved": 2}\n')
            with self.assertRaises(n5.InputError):
                n5.verify_manifest(root)

    def test_path_escape_and_duplicate_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            for relative in ("../escape", "/tmp/absolute"):
                with self.assertRaises(n5.InputError):
                    n5.contained_path(temp, relative)

    def test_create_only_run_id(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = create_output(root, "synthetic_v1")
            sentinel = output / "keep.txt"
            sentinel.write_text("original")
            with self.assertRaises(FileExistsError):
                create_output(root, "synthetic_v1")
            self.assertEqual(sentinel.read_text(), "original")
            with self.assertRaises(ValueError):
                create_output(root, "../escape")

    def test_cache_aware_memory_admission(self):
        check = memory_admission(8190 * MIB, 8192 * MIB, 1700 * MIB, 0, 0)
        self.assertTrue(check["admitted"])
        self.assertFalse(memory_admission(8190 * MIB, 8192 * MIB, 100 * MIB, 0, 0)["admitted"])
        self.assertFalse(memory_admission(8190 * MIB, 8192 * MIB, 500 * MIB, 450 * MIB, 0)["admitted"])

    def test_import_has_no_outputs(self):
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as temp:
            try:
                os.chdir(temp)
                path = Path(n5.__file__)
                spec = importlib.util.spec_from_file_location("n5_import_safety_check", path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.assertEqual(list(Path(temp).iterdir()), [])
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start_wall, start_cpu = time.monotonic(), time.process_time()
    selected = os.environ.get("N5_TEST_ONLY")
    suite = (unittest.defaultTestLoader.loadTestsFromName(selected, __import__(__name__)) if selected
             else unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__)))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    record = {"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
              "status": "PASS" if result.wasSuccessful() else "FAILED_RETAINED", "fixtures": "SYNTHETIC_NEW_IMPLEMENTATION_ONLY",
              "selected_test": selected,
              "new_ODE": 0, "old_science_replays": 0, "provider_rate_evaluations": 0,
              "cpu_s": time.process_time() - start_cpu, "wall_s": time.monotonic() - start_wall,
              "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    with (args.output / "TEST_RESULT.json").open("x") as handle:
        json.dump(record, handle, indent=2, allow_nan=False)
        handle.write("\n")
    raise SystemExit(0 if result.wasSuccessful() else 1)
