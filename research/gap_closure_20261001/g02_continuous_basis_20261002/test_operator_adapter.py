"""Targeted synthetic guard, unchanged-operator and coordinator failure tests."""
import copy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import operator_bootstrap
import numpy as np
from bass_foundations.radial_basis import FEMRadial, readonly
from bass_foundations.two_center import Trajectory, symmetric_channels
import basis_representation as basis
import continuous_adapter_support as guards
import continuous_full_operator as adapted_full
import continuous_exact_cross as adapted_cross
import full_operator as legacy_full
import exact_cross as legacy_cross
from fast_cross import _validate as legacy_validate
import run_static_comparison as runner


def fem():
    return FEMRadial(0, 1, -0.5, readonly([0., 0.5, 1.]),
                     readonly([[0., 0.25, -0.0625, 0., 0.],
                               [0.1875, 0.125, -0.3125, 0., 0.]]), 'a' * 64, 0.)


def candidate():
    old = fem()
    endpoints = np.array([0., 0.1875, 0.])
    bubbles = np.array([[0.0625, 0., 0.], [0.3125, 0., 0.]])
    nodes = basis.reconstructed_nodes(endpoints, bubbles)
    metadata = {k: getattr(old, k) for k in ('l', 'principal_n', 'energy', 'identity', 'residual')}
    ident = basis._mode_identity(metadata, old.edges, endpoints, bubbles, nodes)
    return basis.ContinuousRadial(old.l, old.principal_n, old.energy, old.edges,
                                  endpoints, bubbles, nodes, old.identity, ident, old.residual)


class RecordingKernel:
    def __init__(self):
        self.calls = []

    def accumulate(self, *args, **kwargs):
        self.calls.append((tuple(np.array(x, copy=True) if isinstance(x, np.ndarray) else x for x in args), kwargs))
        nt, np_ = len(args[3]), len(args[4])
        # Synthetic deterministic contraction tests adapter input/order invariance.
        # No native kernel or real archived physical bank is involved.
        value = np.sum(args[6]) + np.sum(args[7]) + np.sum(args[1]) + np.sum(args[2])
        return np.full((4, nt, np_), value, dtype=complex)


class OperatorAdapterTests(unittest.TestCase):
    def test_candidate_cannot_enter_legacy_guards(self):
        channels = symmetric_channels([candidate()])
        self.assertFalse(hasattr(channels[0].radial, 'polynomial_coefficients'))
        with self.assertRaises(ValueError):
            legacy_full._basis(channels)
        with self.assertRaises(ValueError):
            legacy_validate(channels, channels[0].radial.edges, 32, 1024)
        self.assertEqual(len(adapted_full._basis(channels)[0]), 2)

    def test_mixed_representation_rejected(self):
        channels = (symmetric_channels([fem()])[0], symmetric_channels([candidate()])[1])
        with self.assertRaises(ValueError):
            guards.validate_cross_channels(channels, channels[0].radial.edges, 32, 1024)

    def test_candidate_tamper_rejected(self):
        radial = candidate()
        radial.bubble_coefficients.setflags(write=True)
        radial.bubble_coefficients[0, 0] += 0.01
        with self.assertRaises(ValueError):
            guards.radial_fingerprint(radial)

    def test_same_center_original_path_bitwise_unchanged(self):
        channels = symmetric_channels([fem()])
        tr = Trajectory(((0., 0., 0.), (0.2, 0., 0.)), ((0., 0., 0.), (0., 0., 1.)))
        for center in (0, 1):
            old = legacy_full.same_center_blocks(tr, channels, 0.3, center, order=8)
            new = adapted_full.same_center_blocks(tr, channels, 0.3, center, order=8)
            for key in ('S', 'H', 'D', 'H0', 'V_other', 'A', 'indices'):
                self.assertTrue(np.array_equal(old[key], new[key]), key)

    def test_cross_quadrature_native_arguments_and_results_unchanged(self):
        channels = symmetric_channels([fem()])
        tr = Trajectory(((0., 0., 0.), (0.2, 0., 0.)), ((0., 0., 0.), (0., 0., 1.)))
        a, b = RecordingKernel(), RecordingKernel()
        old = legacy_cross.cross(tr, channels, 0.3, a, order=4, batch=11)
        new = adapted_cross.cross(tr, channels, 0.3, b, order=4, batch=11)
        self.assertEqual(len(a.calls), len(b.calls))
        self.assertGreater(len(a.calls), 1)
        for (args_a, kw_a), (args_b, kw_b) in zip(a.calls, b.calls):
            self.assertEqual(kw_a, kw_b)
            for aa, bb in zip(args_a, args_b):
                self.assertTrue(np.array_equal(aa, bb))
        for key in runner.RAW_KEYS:
            self.assertTrue(np.array_equal(old[key], new[key]), key)

    def test_resource_admission_includes_coordinator(self):
        info = {'usable_cpu_budget': 4, 'affinity_cpus': list(range(8)),
                'memory_limit_bytes': 8 * runner.GiB, 'memory_available_bytes': 8 * runner.GiB}
        with self.assertRaises(ValueError):
            runner.admit_resources(4, info)
        info['usable_cpu_budget'] = 8
        plan = runner.admit_resources(4, info)
        self.assertNotIn(plan['coordinator_cpu_id'], plan['worker_cpu_ids'])
        info['memory_available_bytes'] = 5 * runner.GiB
        with self.assertRaises(ValueError):
            runner.admit_resources(4, info)

    def test_duplicate_json_and_create_only_receipts(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'x.json'
            p.write_text('{"a": 1, "a": 2}')
            with self.assertRaises(ValueError):
                runner.read_json(p)
            with self.assertRaises(FileExistsError):
                runner.write_json(p, {'new': True})
            self.assertEqual(p.read_text(), '{"a": 1, "a": 2}')

    def test_failed_worker_cancels_only_owned_peers_no_retry(self):
        info = {'usable_cpu_budget': 8, 'affinity_cpus': list(range(8)),
                'memory_limit_bytes': 8 * runner.GiB, 'memory_available_bytes': 8 * runner.GiB}
        allocation = runner.admit_resources(4, info)
        manifest = {'manifest_id': 'fixture', 'resources': allocation, 'source_pins': {}, 'input_pins': {},
                    'tasks': [{'index': i} for i in range(8)], 'timeout_seconds_per_attempt': 900}
        procs = []
        class Process:
            def __init__(self, index):
                self.pid, self.code = 80000 + index, 1 if index == 0 else None
            def poll(self):
                return self.code
            def wait(self, timeout):
                self.code = -15
                return self.code
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            def start(command, **kwargs):
                index = int(command[command.index('--index') + 1])
                rec = runner.read_json(root / 'reservations' / f'{index:03}.json')
                self.assertEqual(rec['global_attempt'], index + 1)
                proc = Process(index)
                procs.append(proc)
                return proc
            with patch.object(runner, 'load_manifest', return_value=(root, manifest)), \
                 patch.object(runner, 'census', return_value=info), \
                 patch.object(runner.os, 'sched_getaffinity', return_value={4}), \
                 patch.object(runner.os, 'sched_setaffinity'), \
                 patch.object(runner.subprocess, 'Popen', side_effect=start), \
                 patch.object(runner.os, 'killpg') as kill:
                with self.assertRaises(RuntimeError):
                    runner.execute(root, 'fixture')
            self.assertEqual(len(procs), 4)
            self.assertEqual(len(list((root / 'reservations').glob('*.json'))), 4)
            self.assertEqual(kill.call_count, 3)
            self.assertTrue(all(p.poll() is not None for p in procs))
            self.assertTrue(runner.read_json(root / 'FAILED.json')['no_retry'])

    def test_process_creation_failure_reports_consumed_reservation(self):
        info = {'usable_cpu_budget': 8, 'affinity_cpus': list(range(8)),
                'memory_limit_bytes': 8 * runner.GiB, 'memory_available_bytes': 8 * runner.GiB}
        manifest = {'manifest_id': 'fixture', 'resources': runner.admit_resources(4, info),
                    'source_pins': {}, 'input_pins': {},
                    'tasks': [{'index': i} for i in range(8)], 'timeout_seconds_per_attempt': 900}
        opened_logs = []
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            def fail_start(command, **kwargs):
                opened_logs.append(kwargs['stdout'])
                self.assertTrue((root / 'reservations' / '000.json').exists())
                raise OSError('simulated process creation failure')
            try:
                with patch.object(runner, 'load_manifest', return_value=(root, manifest)), \
                     patch.object(runner, 'census', return_value=info), \
                     patch.object(runner.os, 'sched_getaffinity', return_value={4}), \
                     patch.object(runner.os, 'sched_setaffinity'), \
                     patch.object(runner.subprocess, 'Popen', side_effect=fail_start) as start, \
                     patch.object(runner.os, 'killpg') as kill:
                    with self.assertRaises(OSError):
                        runner.execute(root, 'fixture')
                failure = runner.read_json(root / 'FAILED.json')
                self.assertEqual(failure['reserved_attempts'], 1)
                self.assertEqual(failure['completed_indices'], [])
                self.assertEqual(failure['worker_processes_remaining'], 0)
                self.assertTrue(failure['no_retry'])
                self.assertEqual(start.call_count, 1)
                kill.assert_not_called()
            finally:
                for log in opened_logs:
                    log.close()


if __name__ == '__main__':
    unittest.main()
