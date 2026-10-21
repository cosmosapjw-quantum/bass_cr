"""Independent original-expression parity at threshold and fixture boundaries."""
import importlib.util
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import numpy as np

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
spec = importlib.util.spec_from_file_location("epoch_physics_module", UNIT / "epoch_adapter.py")
epoch = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = epoch
spec.loader.exec_module(epoch)


class PhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = REPO / "research/cr_c21e_event_native_20261018"
        sys.path.insert(0, str(source / "vendor/pr79"))
        optimizer, _ = epoch.prepare_optimizer(c21i_dir=REPO / "research/cr_c21i_callback_optimization_20261020")
        optimizer.source_snapshot(source, REPO / "research/cr_c21g_reference_refinement_20261019")
        optimizer.load_frozen_adapter(REPO / "research/cr_c21h_vigilode_bridge_20261019").private_reference(source)
        import run_experiment
        cls.original = run_experiment

    def test_factored_opacity_matches_original_bits_for_126_boundary_cases(self):
        from dataclasses import replace
        x0 = math.log(1/12)
        energies = [e for threshold in self.original.FIT
                    for e in (math.nextafter(threshold, 0.), threshold, math.nextafter(threshold, math.inf))]
        epochs = [x0, math.nextafter(x0, -math.inf), math.nextafter(x0, math.inf),
                  x0+1e-4/2, math.nextafter(x0+1e-4/2, math.inf), x0+1e-4,
                  math.nextafter(x0+1e-4, math.inf)]
        cases = 0
        for Y in (0., self.original.Y_HE):
            base = self.original.make_fixture(dx=1e-4, Y=Y)
            for repetitions in (1, 3, 9):
                q = tuple(e*math.exp(x0) for e in energies)*repetitions
                for scale in (0., .001, 1.):
                    fixture = replace(base, q=q, birth=(x0,)*len(q), amounts=(.01,)*len(q),
                                      opacity_scale=scale).validate()
                    scope = epoch.EpochMemo(cache_hubble=False, factor_opacity=True)
                    scope.importer("run_experiment", fromlist=("opacity",))
                    scope.begin_cell(fixture, x0, x0+1e-4)
                    for x in epochs:
                        expected = self.original.opacity(fixture, x)
                        for actual in (scope.opacity(fixture, x), scope.opacity(fixture, x)):
                            for a, b in zip(actual, expected):
                                self.assertEqual((a.shape, a.dtype.str, a.tobytes()),
                                                 (b.shape, b.dtype.str, b.tobytes()))
                        cases += 1
        self.assertEqual(cases, 126)

    def test_default_runtime_keeps_original_hubble_binding(self):
        import event_coupler
        optimizer, scope = epoch.prepare_optimizer(c21i_dir=REPO / "research/cr_c21i_callback_optimization_20261020")
        reference = optimizer.load_frozen_adapter(REPO / "research/cr_c21h_vigilode_bridge_20261019").private_reference(
            REPO / "research/cr_c21e_event_native_20261018")
        self.assertIs(reference.H, event_coupler.H)
        self.assertIs(sys.modules['run_experiment'].opacity, self.original.opacity)
        self.assertFalse(scope.cache_hubble)

    def test_setup_consumes_inherited_job_deadline(self):
        with patch.object(epoch, 'prepare_optimizer', return_value=(None, None)), \
                patch.object(epoch.time, 'monotonic', side_effect=[10., 11.1]):
            with self.assertRaisesRegex(epoch.EpochError, 'JOB_WALL_BUDGET'):
                epoch.run_optimized_reference(None, None, None, None, None, None, wall_s=1.)

    def test_invalid_mode_and_wall_fail_before_loading_source(self):
        for value in (0., -1., math.inf, math.nan):
            with self.assertRaisesRegex(epoch.EpochError, 'POSITIVE_FINITE'):
                epoch.run_optimized_reference(None, None, None, None, None, None, wall_s=value)
        with self.assertRaisesRegex(epoch.EpochError, 'OPTIMIZATION_MODE'):
            epoch.run_optimized_reference(None, None, None, None, None, None, optimization='baseline')


if __name__ == '__main__':
    unittest.main(verbosity=2)
