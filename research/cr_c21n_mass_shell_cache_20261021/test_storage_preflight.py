"""Focused C21N storage/no-replay/cached-worker checks; scientific ODE calls=0.

Only three synthetic cases use multiprocessing. Their backend imports the real
prepared builder for READY/source checks but never calls build/integrate/RHS.
Prior C21M resource and science suites are intentionally not repeated.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import shared_runner as runner
import storage_preflight as storage


EVIDENCE = Path(os.environ['C21N_OPS_EVIDENCE_DIR']) if 'C21N_OPS_EVIDENCE_DIR' in os.environ else None


def preserve(name, value):
    if EVIDENCE is not None:
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        runner.write_new(EVIDENCE / name, value)


def synthetic_vfs(**overrides):
    values = dict(f_bsize=4096, f_frsize=4096, f_blocks=10_000_000,
                  f_bfree=9_000_000, f_bavail=8_000_000,
                  f_files=10_000_000, f_ffree=9_000_000,
                  f_favail=8_000_000, f_flag=0)
    return SimpleNamespace(**{**values, **overrides})


class StorageTests(unittest.TestCase):
    def test_1_available_blocks_inodes_and_fail_before_metadata(self):
        fixtures = [
            ('reserved_blocks_not_usable', {'f_bavail': 0}, 'INSUFFICIENT_AVAILABLE_BYTES'),
            ('inode_exhaustion', {'f_favail': 0}, 'INSUFFICIENT_AVAILABLE_INODES'),
            ('inode_count_unavailable', {'f_files': 0}, 'AVAILABLE_INODES_UNKNOWN'),
            ('read_only_filesystem', {'f_flag': getattr(os, 'ST_RDONLY', 1)}, 'FILESYSTEM_READ_ONLY'),
        ]
        rows = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output, leases = root / 'new_parent' / 'run', root / 'leases'
            sentinel = root / 'unrelated_existing_metadata.json'
            sentinel.write_text('{"owner":"unrelated","preserve":true}\n')
            before = sentinel.read_bytes()
            for label, overrides, expected in fixtures:
                with self.subTest(label=label):
                    report = storage.observe(output, 3, statvfs=lambda _, kw=overrides: synthetic_vfs(**kw), access=lambda *_: True)
                    self.assertEqual(report['status'], 'BLOCKED')
                    self.assertIn(expected, report['reasons'])
                    self.assertFalse(output.parent.exists())
                    rows.append({'fixture': label, 'synthetic_statvfs_overrides': overrides, 'observed': report})
            with patch.object(storage.os, 'statvfs', side_effect=OSError('SYNTHETIC_STATVFS_UNAVAILABLE')):
                report = storage.observe(output, 3)
            self.assertIn('STORAGE_OBSERVATION_UNAVAILABLE', report['reasons'])
            rows.append({'fixture': 'statvfs_unavailable', 'observed': report})
            unwritable = storage.observe(output, 3, statvfs=lambda _: synthetic_vfs(), access=lambda *_: False)
            self.assertIn('OUTPUT_ANCESTOR_NOT_WRITABLE', unwritable['reasons'])
            rows.append({'fixture': 'unwritable_ancestor', 'observed': unwritable})
            # Check the exact available-block boundary, with privileged f_bfree
            # deliberately much larger. Only f_bavail participates in admission.
            required = storage.budget_for(3, 2)['required_available_bytes']
            report = storage.observe(output, 3, statvfs=lambda _: synthetic_vfs(f_bavail=required // 4096), access=lambda *_: True)
            self.assertEqual(report['status'], 'PASS_SCOPED')
            self.assertEqual(report['available_bytes'], required)
            args = runner.parser().parse_args(['--grid', str(root / 'placeholder.json'), '--output', str(output),
                '--execution-site', 'other', '--lease-dir', str(leases)])
            grid = {'schema': 'C21N_GRID_V1', 'run_id': 'c21n_STORAGE_TEST_DOUBLE',
                    'cases': [{'case_id': 'synthetic', 'S0': .001, 'Pm0': 0., 'Pr0': 0.}]}
            blocked = rows[0]['observed']
            original_mpl = os.environ.get('MPLCONFIGDIR')
            with patch.object(runner, 'load_grid', return_value=(grid, 'TEST_DOUBLE')), \
                 patch.object(runner, 'manifest_for', return_value=({'test_double': True}, 'TEST_DOUBLE')), \
                 patch.object(storage, 'observe', return_value=blocked):
                with self.assertRaises(storage.StorageAdmissionError) as caught:
                    runner.run(args, _backend_module='NOT_IMPORTED_TEST_DOUBLE')
            self.assertIs(caught.exception.receipt, blocked)
            self.assertFalse(output.parent.exists())
            self.assertFalse(leases.exists())
            self.assertEqual(before, sentinel.read_bytes())
            self.assertEqual(original_mpl, os.environ.get('MPLCONFIGDIR'))
            real_observation = storage.observe(root / 'never_created_output', 3)
            self.assertIn('available_bytes', real_observation)
            self.assertIn('available_inodes', real_observation)
            preserve('storage_negative_fixtures.json', {
                'status': 'PASS_SCOPED', 'fixtures': rows, 'exact_block_boundary': report,
                'existing_metadata_unchanged': True, 'output_and_leases_created': False,
                'real_local_statvfs_observation': real_observation,
                'scientific_ODE_calls': 0, 'NCP_execution': 'NOT_RUN', 'global_error_bound': None})

    def test_2_completed125_hash_bound_guard_and_new_schema(self):
        completed = runner.load_completed_targets()
        self.assertEqual(len(completed['targets']), 125)
        tested = []
        with tempfile.TemporaryDirectory() as tmp:
            gridpath = Path(tmp) / 'explicit_grid.json'
            grid = {'schema': 'C21N_GRID_V1', 'run_id': 'c21n_NO_REPLAY_TEST_DOUBLE', 'cases': []}
            # Exercise all accepted old targets, including the reused center;
            # this is JSON/hash validation only, with no scientific builder import.
            for prior in completed['targets']:
                case = {key: prior[key] for key in ('S0', 'Pm0', 'Pr0')}
                case['case_id'] = 'renamed_old_target'
                grid['cases'] = [case]
                gridpath.write_text(json.dumps(grid))
                with self.assertRaisesRegex(ValueError, 'ALREADY_COMPLETED_PHYSICAL_TARGET') as error:
                    runner.load_grid(gridpath)
                tested.append(str(error.exception))
            grid['cases'] = [{'case_id': 'near_old_center', 'S0': 1e-13, 'Pm0': -1e-13, 'Pr0': 1e-13}]
            gridpath.write_text(json.dumps(grid))
            with self.assertRaisesRegex(ValueError, 'ALREADY_COMPLETED_PHYSICAL_TARGET'):
                runner.load_grid(gridpath)
            grid['cases'] = [{'case_id': 'NEW_TEST_DOUBLE', 'S0': .001, 'Pm0': 0., 'Pr0': 0.}]
            gridpath.write_text(json.dumps(grid))
            runner.load_grid(gridpath)
            grid['schema'] = 'C21M_GRID_V1'
            gridpath.write_text(json.dumps(grid))
            with self.assertRaisesRegex(ValueError, 'GRID_SCHEMA_OR_RUN_ID'):
                runner.load_grid(gridpath)
        preserve('completed_target_guard.json', {
            'status': 'PASS_SCOPED', 'registry_sha256': runner.digest_file(runner.HERE / 'completed_targets.json'),
            'bound_source_files_checked': len(completed['source_bindings']),
            'old_targets_rejected': len(tested), 'near_center_tolerance_rejected': True,
            'old_schema_rejected': True, 'unused_synthetic_target_accepted': True,
            'failure_messages': tested, 'scientific_ODE_calls': 0, 'global_error_bound': None})

    def test_3_cached_builder_READY_and_storage_pause_resume_three_fake_cases(self):
        resources = runner.resources
        cpus = sorted(set(os.sched_getaffinity(0)) - {55})[:2]
        self.assertEqual(len(cpus), 2, 'focused fake-worker fixture needs coordinator + one affinity CPU')
        snapshot = {'allowed_cpus': cpus, 'affinity': cpus, 'quota': 2.,
                    'memory_limit': 16 * resources.GIB, 'memory_available': 14 * resources.GIB,
                    'cgroups': [], 'protected_cpu': 55}
        observation = {'snapshot': snapshot, 'per_cpu': {c: 0. for c in cpus},
                       'external_cgroup_cores': 0., 'idle_threshold': .35}
        backend_source = '''"""OPERATIONAL TEST DOUBLE: no build/RHS/integrate calls."""
import numpy as np
from builder import IndependentStressBuilder
def solve_case(template, s, pm, pr):
    prepared = template.momentum_factory
    assert prepared.identity()['schema'] == 'C21N_PREPARED_MOMENTUM_V1'
    assert all(not a.flags.writeable for a in prepared._arrays.values())
    value = s + pm + pr
    return ({'endpoint': {'synthetic_value': value}, 'nfev': 0,
             'solver_wall_s': 0., 'global_error_bound': None,
             'cached_builder_import_verified': True, 'scientific_ODE_calls': 0},
            {'synthetic': np.array([value], dtype=np.float64)})
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            backend_name = 'c21n_operational_cached_test_double'
            (root / (backend_name + '.py')).write_text(backend_source)
            sys.path.insert(0, str(root))
            self.addCleanup(lambda: sys.path.remove(str(root)))
            grid = root / 'grid.json'
            grid.write_text(json.dumps({'schema': 'C21N_GRID_V1', 'run_id': 'c21n_CACHED_OPERATIONAL_TEST_DOUBLE',
                'cases': [{'case_id': 'fake' + str(i), 'S0': .001 * (i + 1), 'Pm0': 0., 'Pr0': 0.} for i in range(3)]}))
            output, leases = root / 'output', root / 'leases'
            args = runner.parser().parse_args(['--grid', str(grid), '--output', str(output),
                '--workers', '1', '--lease-dir', str(leases), '--execution-site', 'other',
                '--timeout-seconds', '30', '--active-grace-seconds', '1', '--plan-only'])
            listing = sorted(str(p) for p in root.rglob('*'))
            original_mpl = os.environ.get('MPLCONFIGDIR')
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                self.assertEqual(runner.run(args, _backend_module=backend_name), 0)
            self.assertEqual(listing, sorted(str(p) for p in root.rglob('*')))
            self.assertEqual(original_mpl, os.environ.get('MPLCONFIGDIR'))
            plan = json.loads(captured.getvalue())

            def fake_admission(workers, remaining, lease_dir, restrict, affinity):
                Path(lease_dir).mkdir(exist_ok=True)
                handles = [(c, resources.acquire_cpu(lease_dir, c)) for c in cpus]
                self.assertTrue(all(handle is not None for _, handle in handles))
                return {'coordinator_cpu': cpus[0], 'worker_cpus': cpus[1:], 'lease_directory': lease_dir,
                        'observation': observation, 'OPERATIONAL_TEST_DOUBLE_ADMISSION': True}, handles, observation

            observe = storage.observe
            def storage_depletes_after_one_completion(path, remaining):
                result = observe(path, remaining)
                if list(output.glob('cases/*/COMPLETE.json')):
                    result.update(status='BLOCKED', reasons=['SYNTHETIC_EXTERNAL_DISK_DEPLETION'])
                    result['OPERATIONAL_TEST_DOUBLE'] = True
                return result

            args.plan_only = False
            with patch.object(resources, 'try_admit', side_effect=fake_admission), \
                 patch.object(resources, 'observe_load', return_value=observation), \
                 patch.object(storage, 'observe', side_effect=storage_depletes_after_one_completion), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.run(args, _backend_module=backend_name), 2)
            first = {str(p.relative_to(output)): p.read_bytes() for p in output.glob('cases/*/*') if p.is_file()}
            self.assertEqual(len(list(output.glob('cases/*/COMPLETE.json'))), 1)
            self.assertEqual(len(list(output.glob('cases/*/STARTED.json'))), 1)
            args.resume = True
            with patch.object(resources, 'try_admit', side_effect=fake_admission), \
                 patch.object(resources, 'observe_load', return_value=observation), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.run(args, _backend_module=backend_name), 0)
            for path, data in first.items():
                self.assertEqual((output / path).read_bytes(), data)
            self.assertEqual(len(list(output.glob('cases/*/STARTED.json'))), 3)
            results = [json.loads(p.read_text()) for p in output.glob('cases/*/RESULT.json')]
            self.assertTrue(all(r['cached_builder_import_verified'] and r['operational_test_double']
                                and r['nfev'] == 0 and r['scientific_ODE_calls'] == 0 for r in results))
            events = [json.loads(line) for path in output.glob('EVENTS_*.jsonl') for line in path.read_text().splitlines()]
            self.assertEqual(sum(e['kind'] == 'READY' for e in events), 2)
            self.assertEqual(sum(e['kind'] == 'DISPATCH' for e in events), 3)
            self.assertEqual(sum(e['kind'] == 'STORAGE_BLOCKED' for e in events), 1)
            self.assertTrue(all(e['inflight_cases'] <= 1 for e in events if e['kind'] == 'DISPATCH'))
            self.assertEqual(original_mpl, os.environ.get('MPLCONFIGDIR'))
            if EVIDENCE is not None:
                shutil.copytree(output, EVIDENCE / 'fakeworker_run')
                (EVIDENCE / 'fakeworker_backend.py.txt').write_text(backend_source)
                shutil.copyfile(grid, EVIDENCE / 'fakeworker_grid.json')
            preserve('cached_worker_storage_resume.json', {
                'status': 'PASS_SCOPED', 'plan': plan, 'synthetic_cases_completed': 3,
                'cached_builder_READY_messages': 2, 'dispatches': 3,
                'disk_change_blocks_further_dispatch': True,
                'first_completed_raw_preserved_byte_identically': True,
                'resume_admits_only_two_never_started': True,
                'scientific_ODE_calls': 0, 'NCP_execution': 'NOT_RUN',
                'old_suite_repeated': False, 'global_error_bound': None})


if __name__ == '__main__':
    unittest.main(verbosity=2)
