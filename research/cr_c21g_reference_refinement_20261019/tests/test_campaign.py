"""Bounded orchestration checks; synthetic payloads never claim native physics."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import campaign_contract as contract
import run_campaign as campaign


def fixture():
    return {'x0': -2.4, 'dx': 1e-7, 'nh0': 1e-7, 'Y': 0.0,
            'gas0': [0.2, 0.0, 0.0, 1.0], 'q': [2.0], 'birth': [-2.4],
            'amounts': [0.001], 'opacity_scale': 0.0003,
            'source_identity': 'SYNTHETIC_ORCHESTRATION_TEST_ONLY'}


def reference_job():
    return {'id': 'test_reference_L1', 'fixture': 'common_ic',
            'kind': 'reference', 'tier': dict(contract.TIERS[0])}


def expectation(f, job):
    controls = contract.reference_controls(f, job['tier'])
    return {'kind': 'reference', 'schema': 'C21F_OPTICAL_DEPTH_RADAU_REFERENCE_V1',
            'status': 'PASS_SCOPED_CONTINUOUS_IVP', 'cohorts': len(f['q']),
            'x0': f['x0'], 'x1': f['x0'] + f['dx'],
            **{key: controls[key] for key in ('rtol', 'atol', 'max_step_divisor', 'max_evaluations')}}


def synthetic_payload(payload, signature, data):
    payload.mkdir(parents=True, exist_ok=True)
    expected = data['expected_execution']
    result = {'schema': expected['schema'], 'status': expected['status'],
              'fixture_sha256': data['fixture_sha256'],
              'microphysics': 'MANUFACTURED_CONSERVATIVE_MICRO_NOT_GRACKLE',
              'gas': [0.2, 0.0, 0.0, 1.0], 'photons': [0.001],
              'tolerance_contract': {key: expected[key] for key in ('rtol', 'atol', 'max_step_divisor')},
              'rhs_evaluations': 3, 'solver_diagnostics': {'segments': [
                  {'accepted_grid_sha256': 'a' * 64, 'accepted_steps': 1}]}}
    closure = {'verified': True, 'input_identity_sha256': data['input_identity_sha256']}
    worker = {'status': 'COMPLETE', 'signature': signature, 'runtime': data['runtime'],
              'microphysics': result['microphysics'], 'native_process_exit_code': None,
              'provider_calls': None, 'input_identity_sha256': data['input_identity_sha256'],
              'execution_closure_before': closure, 'execution_closure_after': closure}
    contract.write_new_json(payload / 'result.json', result)
    contract.write_new_json(payload / 'worker_receipt.json', worker)


def synthetic_receipt(root):
    f = fixture(); job = reference_job()
    data = {'job': job, 'fixture': f, 'fixture_sha256': contract.canonical_hash(f),
            'input_manifest_sha256': '0' * 64, 'input_identity_sha256': '1' * 64,
            'runtime': campaign.runtime_identity(), 'micro': 'manufactured',
            'binary_sha256': None, 'expected_execution': expectation(f, job)}
    signature = contract.canonical_hash(data)
    payload = root / 'payload'
    synthetic_payload(payload, signature, data)
    receipt = {'schema': 'C21G_JOB_RECEIPT_V1', 'job': job, 'signature': signature,
               'signature_data': data, 'status': 'COMPLETE', 'payload_directory': str(payload),
               'payload_files': campaign.payload_files(payload),
               'process': {'exit_code': 0, 'timed_out': False, 'execution_status': 'EXIT_0'},
               'native_science': False}
    path = root / 'receipt.json'; contract.write_new_json(path, receipt)
    return path, receipt


def replace_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


class CampaignTests(unittest.TestCase):
    def assert_not_admitted(self, path, signature):
        try:
            result = campaign.verify_reusable_job(path, signature)
        except ValueError:
            return
        self.assertIsNone(result, 'incomplete or contradictory payload was admitted')

    def test_create_only_write_preserves_existing_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'receipt.json'
            contract.write_new_json(path, {'old': 1})
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                contract.write_new_json(path, {'replacement': 2})
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(tmp).glob('*.partial')), [])

    def test_valid_reuse_is_read_only_and_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, receipt = synthetic_receipt(Path(tmp))
            before = campaign.payload_files(Path(tmp))
            reused = campaign.verify_reusable_job(path, receipt['signature'])
            self.assertTrue(reused['reused_without_execution'])
            self.assertEqual(campaign.payload_files(Path(tmp)), before)
            (Path(tmp) / 'payload' / 'result.json').write_text('{}\n')
            self.assert_not_admitted(path, receipt['signature'])

    def test_empty_complete_receipt_is_not_reusable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, receipt = synthetic_receipt(Path(tmp))
            for child in (Path(tmp) / 'payload').iterdir():
                child.unlink()
            receipt['payload_files'] = {}
            replace_json(path, receipt)
            self.assert_not_admitted(path, receipt['signature'])

    def test_rehashed_worker_or_requested_tolerance_mismatch_is_rejected(self):
        for mutation in ('worker_failed', 'worker_signature', 'worker_runtime', 'wrong_rtol'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                path, receipt = synthetic_receipt(Path(tmp))
                target = Path(tmp) / 'payload' / ('result.json' if mutation == 'wrong_rtol' else 'worker_receipt.json')
                data = contract.read_json(target)
                if mutation == 'worker_failed': data['status'] = 'FAILED'
                elif mutation == 'worker_signature': data['signature'] = 'f' * 64
                elif mutation == 'worker_runtime': data['runtime'] = {'python': 'different'}
                else: data['tolerance_contract']['rtol'] *= 10
                replace_json(target, data)
                receipt['payload_files'] = campaign.payload_files(Path(tmp) / 'payload')
                replace_json(path, receipt)
                self.assert_not_admitted(path, receipt['signature'])

    def test_failed_process_is_not_reusable_even_with_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, receipt = synthetic_receipt(Path(tmp))
            receipt['process']['exit_code'] = 1
            replace_json(path, receipt)
            self.assert_not_admitted(path, receipt['signature'])

    def test_native_metadata_or_incomplete_point_log_is_rejected(self):
        # These are synthetic receipt records only. No NativeMicro is started.
        for mutation in ('valid', 'owner', 'binary', 'native_exit', 'missing_point'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); f = fixture(); job = campaign.job_plan()['references'][0]
                data = {'job': job, 'fixture': f, 'fixture_sha256': contract.canonical_hash(f),
                        'input_manifest_sha256': '0' * 64, 'input_identity_sha256': '1' * 64,
                        'runtime': campaign.runtime_identity(), 'micro': 'native',
                        'binary_sha256': '2' * 64, 'expected_execution': expectation(f, job)}
                signature = contract.canonical_hash(data); payload = root / 'payload'
                synthetic_payload(payload, signature, data)
                result = contract.read_json(payload / 'result.json')
                result['microphysics'] = contract.NATIVE_KIND
                replace_json(payload / 'result.json', result)
                worker = contract.read_json(payload / 'worker_receipt.json')
                worker.update(microphysics=contract.NATIVE_KIND, provider_calls=3,
                              native_process_exit_code=1 if mutation == 'native_exit' else 0)
                replace_json(payload / 'worker_receipt.json', worker)
                process = {'owner': 'wrong' if mutation == 'owner' else contract.OWNER,
                           'binary_sha256': '3' * 64 if mutation == 'binary' else data['binary_sha256'],
                           'timeout_s': contract.POLICY['native_call_timeout_s'],
                           'max_calls': contract.POLICY['max_native_calls_per_job'],
                           'test_fixture_only': True}
                contract.write_new_json(payload / 'process' / 'native_process.json', process)
                (payload / 'process' / 'native_stderr.log').write_text('')
                (payload / 'process' / 'native_points.jsonl').write_text(
                    '{"synthetic_point_log_test_only":true}\n' * (2 if mutation == 'missing_point' else 3))
                receipt = {'status': 'COMPLETE', 'job': job, 'signature_data': data,
                           'signature': signature, 'payload_directory': str(payload),
                           'payload_files': campaign.payload_files(payload),
                           'process': {'exit_code': 0, 'timed_out': False, 'execution_status': 'EXIT_0'}}
                if mutation == 'valid':
                    self.assertEqual(campaign.verify_payload_record(receipt), result)
                else:
                    with self.assertRaises(ValueError):
                        campaign.verify_payload_record(receipt)

    def test_unlisted_payload_and_path_escape_are_rejected(self):
        for mutation in ('extra', 'escape'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                path, receipt = synthetic_receipt(Path(tmp))
                if mutation == 'extra':
                    (Path(tmp) / 'payload' / 'unlisted.json').write_text('{}\n')
                else:
                    escaped = Path(tmp) / 'outside.txt'; escaped.write_text('outside payload\n')
                    receipt['payload_files']['../outside.txt'] = contract.file_record(escaped)
                    replace_json(path, receipt)
                self.assert_not_admitted(path, receipt['signature'])

    def test_refinement_gate_requires_all_reference_execution(self):
        ready = {'execution_status': 'COMPLETE', 'fixtures': {
            'common_ic': {'pilot_status': 'REF_COMPARISON_BUDGET_HOLD'},
            'native_source': {'pilot_status': 'REF_READY_FOR_BOUNDED_REFINEMENT'}}}
        self.assertTrue(campaign.can_refine(ready))
        for execution in ('PARTIAL', 'NOT_RUN'):
            failed = copy.deepcopy(ready); failed['execution_status'] = execution
            self.assertFalse(campaign.can_refine(failed))
        held = copy.deepcopy(ready)
        held['fixtures']['native_source']['pilot_status'] = 'REF_COMPARISON_BUDGET_HOLD'
        self.assertFalse(campaign.can_refine(held))

    @unittest.skipUnless(hasattr(os, 'killpg') and Path('/proc').exists(), 'Linux process group check')
    def test_timeout_cleans_owned_child_that_ignores_term(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); leader_file = root / 'leader.pid'; child_file = root / 'child.pid'
            child = ('import os,signal,time;from pathlib import Path;'
                     'signal.signal(signal.SIGTERM,signal.SIG_IGN);'
                     f'Path({str(child_file)!r}).write_text(str(os.getpid()));'
                     'time.sleep(60)')
            leader = ('import os,subprocess,sys,time;from pathlib import Path;'
                      f'Path({str(leader_file)!r}).write_text(str(os.getpid()));'
                      f'subprocess.Popen([sys.executable,"-c",{child!r}]);time.sleep(60)')
            unrelated = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(5)'],
                                         start_new_session=True)
            try:
                result = campaign.launch_process([sys.executable, '-c', leader], root / 'process', 0.5)
                self.assertTrue(result['timed_out'])
                self.assertTrue(child_file.exists(), 'owned child did not reach readiness')
                child_pid = int(child_file.read_text())
                deadline = time.monotonic() + 0.5
                running = True
                while time.monotonic() < deadline:
                    # Some sandbox /proc views retain synthetic stale rows;
                    # query the known child through the actual OS API first.
                    try:
                        os.getpgid(child_pid)
                    except ProcessLookupError:
                        running = False; break
                    stat = Path(f'/proc/{child_pid}/stat')
                    if not stat.exists() or stat.read_text().rsplit(') ', 1)[1].split()[0] == 'Z':
                        running = False; break
                    time.sleep(0.01)
                self.assertFalse(running, 'owned SIGTERM-ignoring child survived launcher timeout')
                self.assertIsNone(unrelated.poll(), 'an unrelated process group was signaled')
            finally:
                unrelated.kill(); unrelated.wait()
                if leader_file.exists():
                    try: os.killpg(int(leader_file.read_text()), signal.SIGKILL)
                    except ProcessLookupError: pass

    def test_launch_error_has_terminal_failed_job_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'output'; out.mkdir()
            identity = {'manifest_sha256': '0' * 64}
            with patch.object(campaign, 'verify_execution_closure', create=True, return_value={'verified': True}), \
                 patch.object(campaign, 'launch_process', side_effect=OSError('synthetic launch failure')):
                try:
                    campaign.run_job(out, reference_job(), root / 'source', root / 'baseline',
                                     identity, None, None, micro='manufactured', fixture_override=fixture())
                except OSError:
                    pass
            receipt = out / 'job_receipts' / 'test_reference_L1.json'
            self.assertTrue(receipt.is_file(), 'launch failure lost the per-job terminal state')
            self.assertEqual(contract.read_json(receipt)['status'], 'FAILED')
            self.assertTrue((out / 'jobs' / 'test_reference_L1' / 'spec.json').is_file())

    def test_source_drift_before_job_prevents_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'output'; out.mkdir()
            with patch.object(campaign, 'verify_execution_closure', create=True,
                              side_effect=ValueError('PINNED_FILE_MISMATCH')), \
                 patch.object(campaign, 'launch_process', side_effect=AssertionError('must not launch')) as launch:
                try:
                    campaign.run_job(out, reference_job(), root / 'source', root / 'baseline',
                                     {'manifest_sha256': '0' * 64}, None, None,
                                     micro='manufactured', fixture_override=fixture())
                except (ValueError, AssertionError):
                    pass
                self.assertEqual(launch.call_count, 0)
            receipt = out / 'job_receipts' / 'test_reference_L1.json'
            self.assertTrue(receipt.is_file())
            self.assertEqual(contract.read_json(receipt)['status'], 'FAILED')

    def test_source_drift_after_worker_preserves_failed_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'output'; out.mkdir()
            def launch(argv, output, timeout, env):
                partial = Path(output) / 'payload' / 'partial.json'
                contract.write_new_json(partial, {'partial_data': 'preserve'})
                return {'exit_code': 0, 'timed_out': False, 'execution_status': 'EXIT_0'}
            with patch.object(campaign, 'verify_execution_closure',
                              side_effect=[{'verified': True}, ValueError('PINNED_FILE_MISMATCH'),
                                           ValueError('PINNED_FILE_MISMATCH')]), \
                 patch.object(campaign, 'launch_process', side_effect=launch):
                receipt = campaign.run_job(out, reference_job(), root / 'source', root / 'baseline',
                                          {'manifest_sha256': '0' * 64}, None, None,
                                          micro='manufactured', fixture_override=fixture())
            self.assertEqual(receipt['status'], 'FAILED')
            self.assertFalse(receipt['execution_closure_after']['verified'])
            self.assertIn('partial.json', receipt['payload_files'])
            self.assertEqual(contract.read_json(Path(receipt['payload_directory']) / 'partial.json'),
                             {'partial_data': 'preserve'})

    def test_frozen_source_or_runner_records_detect_changed_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / 'source'; source.mkdir()
            baseline = root / 'baseline'; baseline.mkdir()
            code = source / 'owned_source.py'; code.write_text('baseline_source = 1\n')
            manifest = root / 'manifest.json'; contract.write_new_json(manifest, {'test': True})
            identity = {'manifest_path': str(manifest), 'manifest_sha256': contract.sha256(manifest),
                        'policy_sha256': contract.canonical_hash(contract.POLICY),
                        'c21g_runtime_files': {'run_campaign.py': contract.file_record(Path(campaign.__file__))},
                        'c21f_runtime_files': {'owned_source.py': contract.file_record(code)},
                        'baseline_files': {}}
            self.assertTrue(campaign.verify_execution_closure(source, baseline, identity)['verified'])
            code.write_text('baseline_source = 2\n')
            with self.assertRaisesRegex(ValueError, 'PINNED_FILE_MISMATCH'):
                campaign.verify_execution_closure(source, baseline, identity)
            identity['c21g_runtime_files']['run_campaign.py']['sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'RUNNER_NOT_PINNED_OR_CHANGED'):
                campaign.verify_execution_closure(source, baseline, identity)

    def test_malformed_complete_receipts_fail_with_value_error(self):
        for value in (None, [], {'status': 'COMPLETE'},
                      {'status': 'COMPLETE', 'signature_data': None}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                campaign.verify_payload_record(value)


if __name__ == '__main__':
    unittest.main()
