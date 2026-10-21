"""Three focused operation checks. All generated cases are TEST DOUBLES.

No call to the scientific builder or Einstein--Vlasov ODE is made here.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import shared_resources as resources
import shared_runner as runner


def synthetic_snapshot(cpus):
    return {'allowed_cpus': list(cpus), 'affinity': list(cpus), 'quota': len(cpus),
            'memory_limit': 16 * resources.GIB, 'memory_available': 14 * resources.GIB,
            'cgroups': [], 'protected_cpu': 55}


class OperationsTests(unittest.TestCase):
    def test_1_resource_limits_v1_v2_and_shared_leases(self):
        v2 = {'cpu.max': '250000 100000', 'cpu.stat': 'usage_usec 1200000',
              'memory.max': '8589934592', 'memory.current': '1073741824',
              'cpuset.cpus.effective': '2-4,55'}
        d2 = resources.decode_cgroup({'path': '/synthetic', 'version': 2},
                                     lambda p: v2.get(p.name))
        self.assertEqual(d2['quota_cores'], 2.5)
        self.assertEqual(d2['usage_seconds'], 1.2)
        self.assertEqual(d2['memory_remaining'], 7 * resources.GIB)
        v1 = {'cpu.cfs_quota_us': '300000', 'cpu.cfs_period_us': '100000',
              'cpuacct.usage': '2500000000', 'memory.limit_in_bytes': '4294967296',
              'memory.usage_in_bytes': '1073741824', 'cpuset.cpus': '2-5'}
        d1 = resources.decode_cgroup({'path': '/synthetic', 'version': 1},
                                     lambda p: v1.get(p.name))
        self.assertEqual((d1['quota_cores'], d1['usage_seconds']), (3., 2.5))
        self.assertEqual(d1['memory_remaining'], 3 * resources.GIB)
        snap = synthetic_snapshot(range(64))
        cap = resources.capacity(snap, 64, 2)
        self.assertNotIn(55, cap['cpu_candidates'])
        self.assertEqual(cap['maximum_workers'], 2)
        snap['quota'] = 2.5
        self.assertEqual(resources.capacity(snap, 64, 20)['maximum_workers'], 1)
        snap['quota'] = 1.
        self.assertEqual(resources.capacity(snap, 64, 20)['maximum_workers'], 0)
        base = {**synthetic_snapshot([2, 3, 4]), 'quota': 2.}
        before = {**base, 'cgroups': [
            {'path': '/leaf', 'quota_cores': 2., 'usage_seconds': 0.},
            {'path': '/parent', 'quota_cores': 64., 'usage_seconds': 0.}]}
        after = {**base, 'cgroups': [
            {'path': '/leaf', 'quota_cores': 2., 'usage_seconds': 0.},
            {'path': '/parent', 'quota_cores': 64., 'usage_seconds': 6.}]}
        with patch.object(resources, 'snapshot', side_effect=[before, after]), patch.object(resources, 'process_seconds', return_value=0.):
            nested = resources.observe_load(seconds=.2)
        self.assertEqual(nested['available_quota_cores'], 2.)
        self.assertEqual(nested['external_cgroup_cores'], 0.)
        with tempfile.TemporaryDirectory() as tmp:
            handle = resources.acquire_cpu(tmp, 7)
            self.assertIsNotNone(handle)
            self.assertIsNone(resources.acquire_cpu(tmp, 7))
            handle.close()
            again = resources.acquire_cpu(tmp, 7)
            self.assertIsNotNone(again)
            again.close()

    def test_2_resume_never_started_vs_interrupted_and_raw_hashes(self):
        template = type('ExplicitOperationalDouble', (), {'identity': lambda _: {'TEST_DOUBLE': True}})()
        code = {name: runner.digest_file(runner.HERE / name) for name in runner.CODE_FILES}
        runner.verify_worker_contract(template, {'TEST_DOUBLE': True}, code)
        with self.assertRaisesRegex(RuntimeError, 'WORKER_CODE_IDENTITY_MISMATCH'):
            runner.verify_worker_contract(template, {'TEST_DOUBLE': True}, {})
        with self.assertRaisesRegex(RuntimeError, 'WORKER_SOURCE_IDENTITY_MISMATCH'):
            runner.verify_worker_contract(template, {'TEST_DOUBLE': False}, code)
        case = {'case_id': 'TEST_DOUBLE', 'S0': 0., 'Pm0': 0., 'Pr0': 1.}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'case'
            self.assertEqual(runner.resume_status(out, 'test-id', case), 'NOT_STARTED')
            out.mkdir()
            runner.write_new(out / 'RESERVATION.json', {'identity': 'test-id', 'case': case})
            self.assertEqual(runner.resume_status(out, 'test-id', case), 'NOT_STARTED')
            runner.write_new(out / 'STARTED.json', {'TEST_DOUBLE': True})
            self.assertEqual(runner.resume_status(out, 'test-id', case), 'INTERRUPTED_NO_AUTORETRY')
            with self.assertRaises(FileExistsError):
                runner.write_new(out / 'STARTED.json', {})
            raw = out / 'history.npz'
            raw.write_bytes(b'TEST_DOUBLE_BYTES_NOT_A_SCIENTIFIC_NPZ')
            raw_hash = runner.digest_file(raw)
            runner.write_new(out / 'RESULT.json', {'identity': 'test-id', 'case': case,
                             'status': 'COMPLETE', 'history_sha256': raw_hash})
            self.assertEqual(runner.resume_status(out, 'test-id', case), 'INTERRUPTED_UNSEALED')
            runner.write_new(out / 'COMPLETE.json', {'identity': 'test-id', 'case_id': case['case_id'],
                             'history_sha256': raw_hash, 'result_sha256': runner.digest_file(out / 'RESULT.json')})
            self.assertEqual(runner.resume_status(out, 'test-id', case), 'COMPLETE')
            raw.write_bytes(b'CHANGED_TEST_DOUBLE_BYTES')
            with self.assertRaisesRegex(RuntimeError, 'COMPLETED_RAW_OR_RECEIPT_CHANGED'):
                runner.resume_status(out, 'test-id', case)

    def test_3_bounded_spawn_queue_live_shrink_plan_only_and_resume(self):
        cpus = sorted(set(os.sched_getaffinity(0)) - {55})[:3]
        self.assertGreaterEqual(len(cpus), 3, 'focused spawn fixture needs three admitted affinity CPUs')
        snapshot = synthetic_snapshot(cpus)
        observation = {'snapshot': snapshot, 'per_cpu': {c: 0. for c in cpus},
                       'external_cgroup_cores': 0., 'idle_threshold': .35}
        self.assertEqual(len(resources.dispatch_cpus(observation, set(), set(cpus[1:]), 2, 3, cpus[1:], cpus[0])), 2)
        restricted = {**observation, 'external_cgroup_cores': 1.}
        self.assertEqual(resources.dispatch_cpus(restricted, {cpus[1]}, {cpus[2]}, 2, 3, cpus[1:], cpus[0]), [])
        backend_code = '''import numpy as np\nclass IndependentStressBuilder:\n def identity(self): return {"OPERATIONAL_TEST_DOUBLE":True}\ndef solve_case(builder,s,pm,pr):\n value=s+pm+pr\n return {"endpoint":{"synthetic_value":value},"nfev":0,"solver_wall_s":0.,"global_error_bound":None},{"synthetic":np.array([value])}\n'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            backend_name = 'c21m_operational_test_double'
            (root / (backend_name + '.py')).write_text(backend_code)
            sys.path.insert(0, str(root))
            grid = root / 'grid.json'
            grid.write_text(json.dumps({'schema': 'C21M_GRID_V1', 'run_id': 'OPERATIONAL_TEST_DOUBLE',
                'cases': [{'case_id': 'double' + str(i), 'S0': float(i), 'Pm0': 0., 'Pr0': 0.} for i in range(3)]}))
            output, leases = root / 'output', root / 'leases'
            args = runner.parser().parse_args(['--grid', str(grid), '--output', str(output),
                   '--workers', '2', '--lease-dir', str(leases), '--execution-site', 'other',
                   '--timeout-seconds', '30', '--active-grace-seconds', '1', '--plan-only'])
            before = sorted(str(p) for p in root.rglob('*'))
            original_mpl = os.environ.get('MPLCONFIGDIR')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.run(args, _backend_module=backend_name), 0)
            self.assertEqual(before, sorted(str(p) for p in root.rglob('*')))
            self.assertEqual(original_mpl, os.environ.get('MPLCONFIGDIR'))

            def synthetic_admission(workers, remaining, lease_dir, restrict, affinity):
                Path(lease_dir).mkdir()
                handles = [(c, resources.acquire_cpu(lease_dir, c)) for c in cpus]
                return {'coordinator_cpu': cpus[0], 'worker_cpus': cpus[1:], 'lease_directory': lease_dir,
                        'observation': observation}, handles, observation

            args.plan_only = False
            with patch.object(resources, 'try_admit', side_effect=synthetic_admission), patch.object(resources, 'observe_load', return_value=observation), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.run(args, _backend_module=backend_name), 0)
            starts = {str(p): p.read_bytes() for p in output.glob('cases/*/STARTED.json')}
            raw_hashes = {str(p): runner.digest_file(p) for p in output.glob('cases/*/history.npz')}
            self.assertEqual(len(starts), 3)
            event_rows = [json.loads(line) for file in output.glob('EVENTS_*.jsonl') for line in file.read_text().splitlines()]
            self.assertTrue(all(e['inflight_cases'] <= 2 for e in event_rows if e['kind'] == 'DISPATCH'))
            args.resume = True
            with patch.object(resources, 'try_admit', side_effect=AssertionError('complete raw must not redispatch')), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.run(args, _backend_module=backend_name), 0)
            self.assertEqual(starts, {str(p): p.read_bytes() for p in output.glob('cases/*/STARTED.json')})
            self.assertEqual(raw_hashes, {str(p): runner.digest_file(p) for p in output.glob('cases/*/history.npz')})
            sys.path.remove(str(root))


if __name__ == '__main__':
    unittest.main(verbosity=2)
