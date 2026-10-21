"""Focused ownership, exact-key, cell, and failure semantics for C21K."""
from dataclasses import dataclass, replace
import importlib.util
import math
from pathlib import Path
import struct
import sys
from types import SimpleNamespace
import unittest
import numpy as np

UNIT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("epoch_test_module", UNIT / "epoch_adapter.py")
epoch = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = epoch
spec.loader.exec_module(epoch)


@dataclass(frozen=True)
class Fixture:
    gas0: tuple = (0.1, 0.2, 0.3, 4.0)
    q: tuple = (13.6, 24.6)
    birth: tuple = (0., 0.)
    amounts: tuple = (2., 3.)


class EpochTests(unittest.TestCase):
    def create(self, capacity=16):
        fixture, cache, calls = Fixture(), epoch.EpochMemo(capacity=capacity), []

        def opacity(f, x):
            calls.append(struct.pack("<d", float(x)))
            return np.array([x, -x]), np.full((2, 3), x)

        cache._opacity, cache._hubble = opacity, lambda x: 1.0 + x
        cache.begin_cell(fixture, 0., 1.)
        return fixture, cache, calls

    def test_outputs_are_owned_and_cached_storage_cannot_be_mutated(self):
        f, cache, calls = self.create()
        first = cache.opacity(f, .25)
        first[0][:] = 99.; first[1][:] = -88.
        second = cache.opacity(f, .25)
        np.testing.assert_array_equal(second[0], [.25, -.25])
        np.testing.assert_array_equal(second[1], np.full((2, 3), .25))
        self.assertEqual(len(calls), 1)
        for value in cache._opacities.values():
            with self.assertRaises(ValueError):
                value[0].setflags(write=True)

    def test_signed_zero_and_adjacent_representable_epochs_do_not_alias(self):
        f, cache, calls = self.create()
        for x in (0., -0., .5, math.nextafter(.5, 1.)):
            cache.opacity(f, x)
        self.assertEqual(len(calls), 4)
        self.assertEqual(len(set(calls)), 4)
        self.assertEqual(struct.pack('<d', cache.opacity(f, -0.)[0][0]), struct.pack('<d', -0.))
        self.assertEqual(len(calls), 4)

    def test_lru_hit_refresh_and_capacity_eviction(self):
        f, cache, calls = self.create(capacity=2)
        for x in (.1, .2, .1, .3, .2):
            cache.opacity(f, x)
        self.assertEqual(len(calls), 4)
        self.assertEqual(cache.counts['opacity_hits'], 1)
        self.assertEqual(cache.counts['opacity_evictions'], 2)

    def test_cell_boundary_clears_both_tables(self):
        f, cache, calls = self.create()
        cache.opacity(f, .5); cache.hubble(.5)
        cache.begin_cell(f, 1., 2.)
        cache.opacity(f, .5); cache.hubble(.5)
        self.assertEqual(len(calls), 2)
        self.assertEqual(cache.counts['hubble_misses'], 2)
        self.assertEqual(cache.counts['hubble_hits'], 0)

    def test_failed_or_nonfinite_results_are_never_cached(self):
        f, cache, calls = self.create()
        original = cache._opacity
        cache._opacity = lambda f, x: (_ for _ in ()).throw(RuntimeError('original failure'))
        with self.assertRaisesRegex(RuntimeError, 'original failure'):
            cache.opacity(f, .1)
        cache._opacity = lambda f, x: (np.full(2, np.nan), np.zeros((2, 3)))
        with self.assertRaisesRegex(epoch.EpochError, 'RESULT_DOMAIN'):
            cache.opacity(f, .1)
        self.assertFalse(cache._opacities)
        cache._opacity = original
        cache.opacity(f, .1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(cache.counts['opacity_hits'], 0)

    def test_mutable_fixture_and_different_fixture_are_rejected(self):
        f, cache, calls = self.create()
        with self.assertRaisesRegex(epoch.EpochError, 'OWNED_TUPLES'):
            epoch.EpochMemo().begin_cell(replace(f, q=list(f.q)), 0., 1.)
        with self.assertRaisesRegex(epoch.EpochError, 'SCOPE_CHANGED'):
            cache.begin_cell(Fixture(), 0., 1.)
        with self.assertRaisesRegex(epoch.EpochError, 'SCOPE_MISMATCH'):
            cache.opacity(Fixture(), .2)

    def test_rebound_source_function_rejected_even_on_exact_hit(self):
        f, cache, calls = self.create()
        real = SimpleNamespace(opacity=cache._opacity)
        cache.modules['run_experiment'] = (real, None)
        cache.opacity(f, .1)
        real.opacity = lambda f, x: (np.ones(2), np.ones((2, 3)))
        with self.assertRaisesRegex(epoch.EpochError, 'FUNCTION_CHANGED'):
            cache.opacity(f, .1)

    def test_unbound_and_nonfinite_epoch_rejected_before_original_call(self):
        f, cache, calls = self.create()
        for x in (math.inf, -math.inf, math.nan):
            with self.assertRaisesRegex(epoch.EpochError, 'NONFINITE_ARGUMENT'):
                cache.opacity(f, x)
        with self.assertRaisesRegex(epoch.EpochError, 'CELL_NOT_BOUND'):
            epoch.EpochMemo().hubble(.2)
        self.assertFalse(calls)

    def test_unsupported_numeric_types_do_not_share_binary64_key(self):
        f, cache, calls = self.create()
        cache.opacity(f, .5)
        for value in (np.float32(.5), np.longdouble(.5), 0, True):
            with self.assertRaisesRegex(epoch.EpochError, 'BINARY64_ARGUMENT_REQUIRED'):
                cache.opacity(f, value)
        cache.opacity(f, np.float64(.5))
        self.assertEqual(len(calls), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
