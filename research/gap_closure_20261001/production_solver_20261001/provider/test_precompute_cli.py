"""Synthetic execution/admission tests: no native evaluator is constructed."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import precompute_cli as cli


class PrecomputeTests(unittest.TestCase):
    def test_digest_binds_exact_manifest_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'m.json'
            p.write_text('{"schema":"x"}\n')
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(cli.read_bound(p, h)['schema'], 'x')
            p.write_text('{ "schema":"x" }\n')
            with self.assertRaises(ValueError): cli.read_bound(p, h)

    def test_admission_rejects_overcommit_and_cpu_substitution(self):
        info = {'affinity_cpus':[0,1,2,3], 'logical_cpus':4,
                'physical_cores':4, 'usable_cpu_budget':4, 'cpu_quota':4.,
                'memory_limit_bytes':8*cli.GiB, 'memory_available_bytes':8*cli.GiB,
                'cpu_model':'synthetic'}
        with patch.object(cli, '_core_ids', return_value=[(0,0),(0,1)]):
            a = cli.admit(info, 1, 2, [0,1], 1., False)
        self.assertEqual(a['estimated_total_rss_bytes'], cli.GiB)
        for args in [(1,2,[0,4],1.), (3,2,list(range(6)),1.), (1,2,[0,1],8.)]:
            with self.assertRaises(ValueError): cli.admit(info,*args,True)

    def test_watchdog_kills_hung_process_and_preserves_timeout_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            result = cli.supervise([sys.executable,'-c','import time; time.sleep(60)'],
                                   Path(d), 0.2, 'a'*64, os.environ.copy())
            self.assertEqual(result['status'], 'HARD_TIMEOUT')
            self.assertNotEqual(result['returncode'], 0)
            self.assertTrue((Path(d)/'SUPERVISOR_RESULT.json').is_file())

    def test_failed_rank_prevents_native_construction_and_queue(self):
        class Comm:
            def Get_rank(self): return 0
            def Get_size(self): return 2
            def allgather(self,value):
                return [value, {'ok':False,'rank':1,'error':'synthetic binding failure'}]
            def bcast(self,value,root=0): return value
        with tempfile.TemporaryDirectory() as d:
            m = {'output':d,'resources':{'ranks':2,'threads':1,'cpus':[0,1]},
                 'context':{},'inputs':'unused','build':'unused'}
            with patch.object(cli,'rank_admission',return_value={'ok':True,'rank':0}), \
                 patch.object(cli.hp,'PinnedEvaluator') as native, \
                 patch.object(cli,'run_queue') as queue:
                with self.assertRaises(RuntimeError): cli.execute(m,Comm(),'b'*64)
            native.assert_not_called(); queue.assert_not_called()
            self.assertFalse(json.loads((Path(d)/'ADMISSION.json').read_text())['admitted'])

    def test_success_keeps_evaluator_lazy_and_publishes_after_queue(self):
        events=[]
        class Comm(cli.hp.SerialComm):
            def allgather(self,value): events.append('allgather');return [value]
            def bcast(self,value,root=0): events.append('broadcast');return value
        with tempfile.TemporaryDirectory() as d:
            m={'output':d,'context':{'context_id':'ctx','qualification_contract':{}},
               'inputs':'unused','build':'unused','tasks':[{'levels':[1]}],
               'limits':{'max_attempts':1,'queue_timeout_seconds':2}}
            def construct(*args): events.append('native');return object()
            def queue(comm,tasks,worker,**kw):
                events.append('queue');worker(tasks[0],object());return [{'result':1}]
            with patch.object(cli,'rank_admission',return_value={'ok':True,'rank':0}), \
                 patch.object(cli.hp,'PinnedEvaluator',side_effect=construct), \
                 patch.object(cli.hp,'qualified_task',return_value={}), \
                 patch.object(cli,'run_queue',side_effect=queue), \
                 patch.object(cli.hp,'collect_cache',return_value={'synthetic':True}) as collect:
                result=cli.execute(m,Comm(),'d'*64)
            self.assertTrue(result['ok']);collect.assert_called_once()
            self.assertEqual(events[:4],['allgather','broadcast','queue','native'])
            self.assertTrue((Path(d)/'RESULT.json').is_file())

    def test_source_change_rejected_before_binding(self):
        with patch.object(cli,'_supervision_check'), \
             patch.object(cli,'validate_manifest',side_effect=ValueError('source changed')), \
             patch.object(cli.hp,'bind_rank') as bind:
            result=cli.rank_admission({},cli.hp.SerialComm(),'e'*64)
        self.assertFalse(result['ok']);self.assertIn('source changed',result['error'])
        bind.assert_not_called()

    def test_watchdog_ancestry_uses_actual_process_identity(self):
        # Uses a real supervised subprocess, but only reads its process identity.
        with tempfile.TemporaryDirectory() as d:
            code=("import sys;sys.path.insert(0,"+repr(str(cli.HERE))+");"
                  "import precompute_cli as c;"
                  "c._supervision_check({'output':"+repr(d)+"},'"+'f'*64+"')")
            env=os.environ.copy()
            for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
                env[k]='1'
            result=cli.supervise([sys.executable,'-I','-c',code],Path(d),5.,'f'*64,env)
            self.assertTrue(result['success'],(Path(d)/'stderr.log').read_text())

    def test_output_reuse_rejected_before_subprocess(self):
        with tempfile.TemporaryDirectory() as d:
            m={'output':d}
            with patch.object(cli,'validate_manifest'), patch.object(cli,'supervise') as sup:
                with self.assertRaises(FileExistsError): cli.run_manifest(m,'c'*64)
            sup.assert_not_called()

if __name__ == '__main__': unittest.main()
