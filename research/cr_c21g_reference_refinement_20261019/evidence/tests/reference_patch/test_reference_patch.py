"""Focused C21G reference-contract checks on small non-native fixtures.

Set C21F_SOURCE_DIR to the published C21F src directory outside this staging
layout. These checks do not run a native executable or the inherited suite.
"""
from __future__ import annotations

import json
import hashlib
import math
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get(
    'C21F_SOURCE_DIR', str(HERE.parent / 'upstream' / 'c21f' / 'src')))
sys.path.insert(0, str(SOURCE))

from event_coupler import DomainError, StepRejected, ZeroMicro
from run_experiment import make_fixture
import reference_tau


class CountedZero:
    kind = 'COUNTED_ZERO_MICRO_TEST_ONLY'

    def __init__(self):
        self.calls = 0
        self.gases = []
        self.inner = ZeroMicro()

    def __call__(self, a, g, nh0, Y):
        self.calls += 1
        self.gases.append(np.asarray(g).copy())
        return self.inner(a, g, nh0, Y)


def small_fixture(Y=None):
    kwargs = dict(a0=0.09, dx=2e-5, opacity_scale=0.001, source_on=True)
    if Y is not None:
        kwargs['Y'] = Y
    return make_fixture(**kwargs)


def physical_output(result):
    return {key: result[key] for key in (
        'gas', 'photons', 'optical_depth', 'log_survivor', 'ledgers',
        'temperature_K', 'number_defect_H', 'energy_defect_eV_H',
        'species_defect', 'min_accepted_optical_depth',
        'underflowed_positive_cohorts')}


class ReferencePatchTests(unittest.TestCase):
    def test_default_scalar_output_preserves_original_small_fixture(self):
        baseline = json.loads((HERE / 'ORIGINAL_SCALAR_SMOKE.json').read_text())
        actual = reference_tau.run_reference_tau(small_fixture(), CountedZero())
        self.assertEqual(physical_output(actual), baseline['physical_output'])

    def test_full_uniform_atol_vector_matches_scalar(self):
        fixture = small_fixture()
        scalar = reference_tau.run_reference_tau(fixture, CountedZero())
        vector = reference_tau.run_reference_tau(
            fixture, CountedZero(), atol=np.full(len(fixture.q) + 19, 2e-13))
        self.assertEqual(physical_output(scalar), physical_output(vector))
        contract = vector['tolerance_contract']
        self.assertEqual(contract['atol_kind'], 'full_state_vector')
        self.assertEqual(contract['full_state_size'], len(fixture.q) + 19)
        self.assertEqual(contract['integrated_state_size'], len(fixture.q) + 19)
        self.assertEqual(
            [s['accepted_grid_sha256'] for s in scalar['solver_diagnostics']['segments']],
            [s['accepted_grid_sha256'] for s in vector['solver_diagnostics']['segments']])

    def test_y0_atol_vector_is_reduced_and_helium_stays_zero(self):
        fixture = small_fixture(Y=0.0)
        size = len(fixture.q) + 19
        full_atol = np.linspace(1e-13, 4e-13, size)
        excluded = (len(fixture.q) + 1, len(fixture.q) + 2)
        dynamic = [index for index in range(size) if index not in excluded]
        captured = []
        original_solve = reference_tau.solve_ivp

        def recording_solve(fun, interval, initial, **kwargs):
            captured.append((len(initial), np.asarray(kwargs['atol']).copy()))
            return original_solve(fun, interval, initial, **kwargs)

        provider = CountedZero()
        with patch.object(reference_tau, 'solve_ivp', side_effect=recording_solve):
            result = reference_tau.run_reference_tau(fixture, provider, atol=full_atol)
        self.assertTrue(captured)
        for dimension, supplied_atol in captured:
            self.assertEqual(dimension, size - 2)
            np.testing.assert_array_equal(supplied_atol, full_atol[dynamic])
        self.assertEqual(result['gas'][1:3], [0.0, 0.0])
        self.assertTrue(all(gas[1] == gas[2] == 0.0 for gas in provider.gases))
        self.assertEqual(result['tolerance_contract']['dynamic_indices'], dynamic)
        np.testing.assert_array_equal(full_atol, np.linspace(1e-13, 4e-13, size))

    def test_invalid_atol_rejected_before_provider(self):
        fixture = small_fixture()
        size = len(fixture.q) + 19
        bad = [[], np.ones(size - 1), np.ones(size + 1),
               np.ones((size, 1)), np.ones((1, size)),
               [1e-13] * (size - 1) + [math.nan],
               [1e-13] * (size - 1) + [math.inf],
               [1e-13] * (size - 1) + [0.0],
               [1e-13] * (size - 1) + [-1e-13],
               0.0, -1e-13, math.inf, math.nan]
        for value in bad:
            with self.subTest(value=repr(value)):
                provider = CountedZero()
                with self.assertRaisesRegex(DomainError, 'RADAU_TOLERANCE'):
                    reference_tau.run_reference_tau(fixture, provider, atol=value)
                self.assertEqual(provider.calls, 0)

    def test_invalid_rtol_and_floor_rejected_before_provider(self):
        fixture = small_fixture()
        for value in (0.0, -1e-10, math.inf, math.nan, [2e-10]):
            with self.subTest(value=value):
                provider = CountedZero()
                with self.assertRaisesRegex(DomainError, 'RADAU_TOLERANCE'):
                    reference_tau.run_reference_tau(fixture, provider, rtol=value)
                self.assertEqual(provider.calls, 0)
        provider = CountedZero()
        with self.assertRaisesRegex(DomainError, 'RADAU_RTOL_BELOW_FLOAT64_FLOOR'):
            reference_tau.run_reference_tau(fixture, provider, rtol=1e-15)
        self.assertEqual(provider.calls, 0)

    def test_max_step_option_is_reported_and_enforced(self):
        result = reference_tau.run_reference_tau(
            small_fixture(), CountedZero(), max_step_divisor=16.0)
        diagnostics = result['solver_diagnostics']
        self.assertEqual(result['tolerance_contract']['max_step_divisor'], 16.0)
        for segment in diagnostics['segments']:
            self.assertGreaterEqual(segment['accepted_steps'], 16)
            self.assertGreater(segment['min_x_step'], 0.0)
            self.assertLessEqual(segment['max_x_step'],
                                 segment['max_step_bound'] + 2e-15)
            self.assertEqual(segment['max_step_bound'],
                             (segment['x1'] - segment['x0']) / 16.0)

    def test_invalid_max_step_rejected_before_provider(self):
        for divisor in (0.0, -1.0, 0.5, math.inf, math.nan, [8.0]):
            with self.subTest(divisor=divisor):
                provider = CountedZero()
                with self.assertRaisesRegex(DomainError, 'RADAU_MAX_STEP_DOMAIN'):
                    reference_tau.run_reference_tau(
                        small_fixture(), provider, max_step_divisor=divisor)
                self.assertEqual(provider.calls, 0)

    def test_counters_include_finite_difference_provider_calls(self):
        provider = CountedZero()
        grids = []
        original_solve = reference_tau.solve_ivp

        def capture_grid(*args, **kwargs):
            solution = original_solve(*args, **kwargs)
            grids.append(np.asarray(solution.t, dtype='<f8').tobytes(order='C'))
            return solution

        with patch.object(reference_tau, 'solve_ivp', side_effect=capture_grid):
            result = reference_tau.run_reference_tau(small_fixture(), provider)
        diagnostics = result['solver_diagnostics']
        self.assertEqual(result['rhs_evaluations'], provider.calls)
        self.assertGreater(provider.calls, result['nfev'])
        self.assertEqual(sum(s['rhs_evaluations'] for s in diagnostics['segments']),
                         provider.calls)
        for key in ('nfev', 'njev', 'nlu', 'accepted_steps'):
            self.assertEqual(diagnostics[key], sum(s[key] for s in diagnostics['segments']))
        self.assertTrue(diagnostics['rhs_evaluations_include_jacobian_finite_differences'])
        self.assertEqual(diagnostics['nfev'], result['nfev'])
        self.assertGreater(diagnostics['njev'], 0)
        self.assertGreater(diagnostics['nlu'], 0)
        self.assertGreater(diagnostics['accepted_steps'], 0)
        self.assertIn('little-endian float64', diagnostics['accepted_grid_encoding'])
        self.assertEqual(len(grids), len(diagnostics['segments']))
        for raw_grid, segment in zip(grids, diagnostics['segments']):
            self.assertEqual(segment['accepted_grid_sha256'],
                             hashlib.sha256(raw_grid).hexdigest())
        self.assertIn('lo+1e-9*(hi-lo)',
                      result['tolerance_contract']['endpoint_sampling_policy'])

    def test_floor_boundary_accepted_and_evaluation_budget_retained(self):
        floor = 100 * np.finfo(float).eps
        result = reference_tau.run_reference_tau(small_fixture(), CountedZero(), rtol=floor)
        self.assertEqual(result['tolerance_contract']['rtol'], floor)
        self.assertEqual(result['tolerance_contract']['rtol_minimum'], floor)
        with self.assertRaisesRegex(StepRejected, 'RADAU_EVALUATION_BUDGET'):
            reference_tau.run_reference_tau(small_fixture(), CountedZero(), max_evaluations=1)


if __name__ == '__main__':
    unittest.main()
