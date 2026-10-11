"""SG06–09: isolated plumbing fixtures, never a physical G or pulse."""
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
import zipfile
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'ncp'))
import launch_pulse as launcher
import collect_return as collector
import run_and_collect as wrapper
import ops
import numpy as np


class PlumbingTests(unittest.TestCase):
    def worker_run(self, run):
        cap = 'synthetic-private-capability-no-physical-child'
        launcher.write(run / 'RESERVATION.json', {
            'capability_sha256': hashlib.sha256(cap.encode()).hexdigest(),
            'coordinator_pid': os.getppid(), 'run_dir': str(run)})
        readfd, writefd = os.pipe()
        os.write(writefd, cap.encode())
        os.close(writefd)
        return readfd

    def test_SG06_preflight_failure_has_no_build_or_atomic_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = pathlib.Path(tmp)
            fd = self.worker_run(run)
            with patch.object(launcher, 'admission', return_value={}), \
                 patch.object(launcher, 'numerical_preflight', side_effect=ValueError('SECOND_MODEL_INVALID')), \
                 patch.object(launcher, 'import_file') as imports:
                with self.assertRaisesRegex(ValueError, 'SECOND_MODEL_INVALID'):
                    launcher.worker(run, fd)
                imports.assert_not_called()
            self.assertFalse(list(run.glob('BUILD_*')))
            self.assertFalse(list(run.glob('PULSE_*')))

    def prefix_fixture(self, run, wrong_grid=False):
        events = []
        E = np.array([1., 2.])
        data = {'energy_eV': E, 'source_vectors': np.zeros((3, 2))}
        fake_cascade = types.SimpleNamespace(E=E.copy(), G='MOCK_G', n=2,
                                             ix={'heat': 2}, functionals=lambda: (np.ones(3),))
        if wrong_grid:
            fake_cascade.E[0] = np.nextafter(E[0], np.inf)
        def make(parent, energy, *, atomic):
            events.append('constructor')
            self.assertTrue((run / 'BUILD_1_RESERVATION.json').is_file())
            self.assertEqual(events[:2], ['preflight_fullBED', 'preflight_legacy'])
            return fake_cascade
        grid = types.SimpleNamespace(make_saved_grid_cascade=make,
                                     operator_identity=lambda c: {'G': 'MOCK_IDENTITY'})
        def preflight(_):
            events.extend(['preflight_fullBED', 'preflight_legacy'])
            return grid, {'fullBED': data, 'legacy': data}, {}, {}
        def pulse(*args):
            events.append('pulse')
            self.assertTrue((run / 'G_COMPLETION_1.json').is_file())
            raise RuntimeError('MOCK_PULSE_PREFIX_STOP_NO_NUMERICS')
        def importing(name, path):
            events.append('import_' + name)
            if name == 'phys02e_pulse':
                return types.SimpleNamespace(pulse_response=pulse)
            self.assertTrue((run / 'BUILD_1_RESERVATION.json').is_file())
            return types.SimpleNamespace(parent='MOCK_PARENT', AtomicData=lambda: 'MOCK_ATOMIC')
        return events, preflight, importing

    def test_SG06_preflight_before_build_completion_before_pulse(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = pathlib.Path(tmp)
            fd = self.worker_run(run)
            events, preflight, importing = self.prefix_fixture(run)
            with patch.object(launcher, 'admission', return_value={}), \
                 patch.object(launcher, 'numerical_preflight', side_effect=preflight), \
                 patch.object(launcher, 'import_file', side_effect=importing), \
                 patch.object(launcher, 'probe', return_value={'admitted': True}), \
                 patch('threadpoolctl.threadpool_info', return_value=[{'num_threads': 1}]):
                with self.assertRaisesRegex(RuntimeError, 'MOCK_PULSE_PREFIX_STOP'):
                    launcher.worker(run, fd)
            self.assertEqual(events[:2], ['preflight_fullBED', 'preflight_legacy'])
            completion = json.loads((run / 'G_COMPLETION_1.json').read_text())
            self.assertEqual(completion['operator_identity'], {'G': 'MOCK_IDENTITY'})
            self.assertEqual(len(list(run.glob('BUILD_*_RESERVATION.json'))), 1)
            self.assertEqual(len(list(run.glob('G_COMPLETION_*.json'))), 1)

    def test_SG06_exact_guard_blocks_completion_and_pulse(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = pathlib.Path(tmp)
            fd = self.worker_run(run)
            events, preflight, importing = self.prefix_fixture(run, wrong_grid=True)
            with patch.object(launcher, 'admission', return_value={}), \
                 patch.object(launcher, 'numerical_preflight', side_effect=preflight), \
                 patch.object(launcher, 'import_file', side_effect=importing), \
                 patch.object(launcher, 'probe', return_value={'admitted': True}), \
                 patch('threadpoolctl.threadpool_info', return_value=[{'num_threads': 1}]):
                with self.assertRaisesRegex(ValueError, 'STORED_SOURCE_GRID_FIELDS_MISMATCH'):
                    launcher.worker(run, fd)
            self.assertNotIn('pulse', events)
            self.assertFalse(list(run.glob('G_COMPLETION_*')))
            self.assertFalse(list(run.glob('PULSE_*')))

    def fixture(self, base):
        repository = base / 'repository'
        study = repository / 'research/cr_phys02e_20261011'
        shutil.copytree(ROOT, study, ignore=shutil.ignore_patterns('__pycache__', 'runs', 'returns', 'FILE_MANIFEST.json'))
        dep = ROOT / 'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'
        for rel, item in ops.entries(json.loads(dep.read_text())):
            dest = repository / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT.parents[1] / rel, dest)
        return repository, study

    def ready_fixture(self, study):
        required = ['src/saved_grid.py', 'src/pulse_response.py', 'ncp/launch_pulse.py',
                    'ncp/collect_return.py', 'ncp/ops.py', 'ncp/run_and_collect.py']
        reviewed = {rel: {'bytes': (study / rel).stat().st_size,
                          'sha256': ops.sha(study / rel)} for rel in required}
        decision = {'fixture_only': True, 'decision': 'PASS_SCOPED',
                    'independent_of_implementation': True,
                    'independent_of_candidate_design': True,
                    'reviewer_role': 'INDEPENDENT_ASTRA',
                    'scientific_contract_sha256': launcher.SCI,
                    'ncp_contract_sha256': launcher.NCP,
                    'input_manifest_sha256': launcher.INPUT,
                    'dependency_manifest_sha256': launcher.DEP,
                    'reviewed_files': reviewed}
        path = study / 'review/INDEPENDENT_DECISION.json'
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(decision))
        dagpath = study / 'state/NEXT_DAG.json'
        dag = json.loads(dagpath.read_text())
        task = next(t for t in dag['tasks'] if t['id'] == launcher.TASK)
        task.update(status='READY', independent_review={'path': 'review/INDEPENDENT_DECISION.json', 'sha256': ops.sha(path)})
        dagpath.write_text(json.dumps(dag))
        manifest = {'fixture_only': True, 'files': {
            rel: {'bytes': p.stat().st_size, 'sha256': ops.sha(p)}
            for p in sorted(study.rglob('*')) if p.is_file()
            for rel in [p.relative_to(study).as_posix()]}}
        (study / 'FILE_MANIFEST.json').write_text(json.dumps(manifest))
        return path, dagpath

    def test_SG07_plan_stays_standard_library(self):
        code = "import sys;sys.path.insert(0,'ncp');import launch_pulse as x;sys.argv=['launch','--plan'];x.admission=lambda:(_ for _ in ()).throw(ValueError('ISOLATED_FIXTURE_HOLD'));x.probe=lambda root:{'admitted':False};assert x.main()==0;assert 'numpy' not in sys.modules and 'scipy' not in sys.modules"
        completed = subprocess.run([sys.executable, '-c', code], cwd=ROOT,
                                   capture_output=True, text=True, timeout=5)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)['admission_status'], 'HOLD')

    def test_SG07_new_identity_and_independent_review_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, study = self.fixture(pathlib.Path(tmp))
            decision, dag = self.ready_fixture(study)
            live_before = (ROOT / 'state/NEXT_DAG.json').read_bytes()
            with patch.object(launcher, 'STUDY', study):
                result = launcher.admission()
                self.assertGreater(result['dependency_verification']['verified_entries'], 259)
                with patch.object(launcher, 'SCI', 'SYNTHETIC_WRONG_SCI'):
                    with self.assertRaisesRegex(ValueError, 'EXACT_IDENTITY_MISMATCH'):
                        launcher.admission()
                review = json.loads(decision.read_text())
                del review['reviewed_files']['src/saved_grid.py']
                decision.write_text(json.dumps(review))
                content = json.loads(dag.read_text())
                next(t for t in content['tasks'] if t['id'] == launcher.TASK)['independent_review']['sha256'] = ops.sha(decision)
                dag.write_text(json.dumps(content))
                # Keep the synthetic frozen manifest in sync; live state is untouched.
                manifest = json.loads((study / 'FILE_MANIFEST.json').read_text())
                for p in (decision, dag):
                    manifest['files'][p.relative_to(study).as_posix()] = {'bytes': p.stat().st_size, 'sha256': ops.sha(p)}
                (study / 'FILE_MANIFEST.json').write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, 'REVIEW_CODE_COVERAGE_MISSING'):
                    launcher.admission()
            self.assertEqual(live_before, (ROOT / 'state/NEXT_DAG.json').read_bytes())

    def test_SG08_execute_failure_and_collection_success_stays_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = pathlib.Path(tmp) / 'run'
            calls = []
            def execute(command, **kwargs):
                calls.append('execute')
                run.mkdir()
                launcher.write(run / 'FIRST_FAILURE.json', {'actual_exit': 1})
                return types.SimpleNamespace(returncode=1)
            def collect(study, run, out):
                calls.append('collect')
                return {'synthetic_archive': True}
            self.assertEqual(wrapper.run_and_collect(run, pathlib.Path(tmp) / 'out', executor=execute, collector=collect), 1)
            self.assertEqual(calls, ['execute', 'collect'])
            self.assertEqual(json.loads((run / 'WRAPPER_EXECUTE_EXIT.json').read_text())['actual_exit'], 1)
            self.assertEqual(json.loads((run / 'WRAPPER_COLLECTION_EXIT.json').read_text())['actual_exit'], 0)
            self.assertTrue((run / 'FIRST_FAILURE.json').is_file())

    def test_SG08_collection_failure_after_success_stays_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = pathlib.Path(tmp) / 'run'
            def execute(command, **kwargs):
                run.mkdir()
                return types.SimpleNamespace(returncode=0)
            def fail(*args):
                raise OSError('SYNTHETIC_COLLECTION_FAILURE')
            self.assertEqual(wrapper.run_and_collect(run, pathlib.Path(tmp) / 'out', executor=execute, collector=fail), 1)
            receipt = json.loads((run / 'WRAPPER_COLLECTION_EXIT.json').read_text())
            self.assertIn('SYNTHETIC_COLLECTION_FAILURE', receipt['exception'])
            self.assertEqual(receipt['actual_exit'], 1)

    def test_SG09_exact_archive_transitive_payload_and_prior_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            repository, study = self.fixture(base)
            self.ready_fixture(study)
            run = base / 'run'
            run.mkdir()
            launcher.write(run / 'ACTUAL_EXIT.json', {'status': 'SYNTHETIC_FAILURE', 'actual_exit': 1})
            launcher.write(run / 'operational_sidecar.json', {'preserve': True})
            result = collector.collect(study, run, base / 'returns')
            expected_dep = {'dependency_payload/' + rel for rel, _ in ops.entries(json.loads((study / 'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json').read_text()))}
            self.assertTrue(any('cr_phys02d_ncp_return_20261011/actual_run/' in rel for rel in expected_dep))
            with zipfile.ZipFile(result['path']) as archive:
                manifest = json.loads(archive.read('RETURN_MANIFEST.json'))
                self.assertEqual(set(archive.namelist()), set(manifest['files']) | {'RETURN_MANIFEST.json'})
                self.assertEqual(expected_dep, {p for p in archive.namelist() if p.startswith('dependency_payload/')})
                self.assertIn('actual_run/operational_sidecar.json', manifest['files'])
                self.assertIn('source_unit/ncp/run_and_collect.py', manifest['files'])
                for name, item in manifest['files'].items():
                    raw = archive.read(name)
                    self.assertEqual(len(raw), item['bytes'])
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), item['sha256'])
                restored = base / 'restored'
                for name in expected_dep:
                    p = restored / name.removeprefix('dependency_payload/')
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(archive.read(name))
                self.assertEqual(ops.verify(restored, study / 'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json')['verified_entries'], len(expected_dep))


if __name__ == '__main__':
    unittest.main()
