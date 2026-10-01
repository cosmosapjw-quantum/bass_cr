"""Synthetic queue tests; no physical basis, native kernel, or scientific query."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from mpi_queue import QueueExecutionError, run_queue


def _openmpi_btl(version):
    match = re.search(r'\((?:Open MPI|OpenRTE)\)\s+(\d+)\.', version)
    if not match:
        raise RuntimeError('synthetic integration requires OpenMPI; unrecognized mpiexec --version')
    major = int(match.group(1))
    if major < 4:
        raise RuntimeError('synthetic integration supports OpenMPI 4 or newer')
    return 'self,sm' if major >= 5 else 'self,vader'


class SerialComm:
    def Get_rank(self): return 0
    def Get_size(self): return 1
    def bcast(self, value, root=0): return value


class SerialContracts(unittest.TestCase):
    def test_openmpi_version_selection(self):
        self.assertEqual(_openmpi_btl('mpiexec (OpenRTE) 4.1.6'), 'self,vader')
        self.assertEqual(_openmpi_btl('mpiexec (Open MPI) 5.0.11'), 'self,sm')
        with self.assertRaises(RuntimeError):
            _openmpi_btl('HYDRA build details: Version 4.2.0')

    def test_global_cap_and_failure_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'run'
            def worker(task, reserve):
                reserve(0)
                reserve(1)
                return task['value']
            with self.assertRaises(QueueExecutionError):
                run_queue(SerialComm(), [{'levels': [4, 8], 'value': 1}] * 2,
                          worker, max_attempts=3, output_dir=out)
            rows = [json.loads(x) for x in (out / 'RESERVATIONS.jsonl').read_text().splitlines()]
            self.assertEqual([r['global_attempt'] for r in rows], [1, 2, 3])
            self.assertEqual(json.loads((out / 'FIRST_FAILURE.json').read_text())['type'], 'BudgetExceeded')

    def test_first_passing_prefix_and_task_isolation(self):
        tasks = [{'levels': [4, 8, 16], 'value': i} for i in range(3)]
        def worker(task, reserve):
            reserve(0); reserve(1)
            result = task['value']
            task['value'] = -1
            return result
        self.assertEqual(run_queue(SerialComm(), tasks, worker, max_attempts=6), [0, 1, 2])
        self.assertEqual([t['value'] for t in tasks], [0, 1, 2])

    def test_out_of_order_level_rejected_before_work(self):
        calls = []
        def worker(task, reserve):
            reserve(1)
            calls.append('unreachable')
        with self.assertRaises(QueueExecutionError):
            run_queue(SerialComm(), [{'levels': [4, 8]}], worker, max_attempts=2)
        self.assertEqual(calls, [])

    def test_empty_plan_and_invalid_budget(self):
        self.assertEqual(run_queue(SerialComm(), [], lambda *_: None, max_attempts=0), [])
        with self.assertRaises(QueueExecutionError):
            run_queue(SerialComm(), [], lambda *_: None, max_attempts=True)


@unittest.skipUnless(shutil.which('mpiexec'),
                     'mpiexec unavailable: MPI execution unverified')
class RealMPIContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # If a launcher exists but mpi4py/libmpi cannot actually load, the
        # subprocess tests must fail, not silently turn that broken install
        # into an unavailable-runtime skip.
        version = subprocess.run([shutil.which('mpiexec'), '--version'],
                                 capture_output=True, text=True, timeout=10, check=True)
        btl = _openmpi_btl(version.stdout + version.stderr)
        cls.launch = [shutil.which('mpiexec'), '--nooversubscribe',
                      '--mca', 'pml', 'ob1', '--mca', 'btl', btl]

    def test_actual_mpi_success_order_budget_and_failure_drain(self):
        env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
                   OMPI_ALLOW_RUN_AS_ROOT='1', OMPI_ALLOW_RUN_AS_ROOT_CONFIRM='1')
        script = Path(__file__).with_name('mpi_queue.py')
        cases = [('ordered', n) for n in (1, 2, 4)]
        cases += [(case, 4) for case in ('budget', 'level', 'worker_failure')]
        for case, ranks in cases:
            with self.subTest(case=case, ranks=ranks), tempfile.TemporaryDirectory() as tmp:
                command = self.launch + ['-n', str(ranks),
                           sys.executable, str(script), '--self-test', '--case', case,
                           '--output-dir', str(Path(tmp) / 'run')]
                result = subprocess.run(command, capture_output=True, text=True,
                                        env=env, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                report = json.loads(result.stdout.strip().splitlines()[-1])
                self.assertEqual(report['status'], 'PASS')
                self.assertEqual(report['physical_queries'], 0)
                self.assertEqual(report['ranks'], ranks)

    def test_hard_timeout_aborts_without_deadlock(self):
        env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
                   OMPI_ALLOW_RUN_AS_ROOT='1', OMPI_ALLOW_RUN_AS_ROOT_CONFIRM='1')
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'run'
            command = self.launch + ['-n', '4',
                       sys.executable, str(Path(__file__).with_name('mpi_queue.py')),
                       '--self-test', '--case', 'timeout', '--output-dir', str(out)]
            result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads((out / 'FIRST_FAILURE.json').read_text())['type'], 'QueueTimeout')
            self.assertEqual(json.loads((out / 'QUEUE_RECEIPT.json').read_text())['status'], 'FAILED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
