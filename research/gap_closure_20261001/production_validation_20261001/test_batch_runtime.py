"""Focused nonphysical tests of fixed budgets, admission, and process cleanup."""
import contextlib
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import batch_runtime as br


def census():
    return {'affinity_cpus':list(range(8)), 'logical_cpus':8, 'physical_cores':8,
            'usable_cpu_budget':8, 'cpu_quota':8., 'cpu_model':'synthetic',
            'memory_limit_bytes':8*br.GiB, 'memory_available_bytes':8*br.GiB}


def fake_manifest(**kw):
    return {'output':str(kw['output']), 'context':{'id':'same-pinned-context'},
            'tasks':[{'time_hex':t.hex(),'levels':list(range(11))} for t in kw['times']],
            'resources':br.pc.admit(census(),1,kw['threads'],kw['cpus'],kw['per_rank_gib'],True),
            'limits':{'max_attempts':kw['max_attempts'],
                      'hard_timeout_seconds':kw['timeout_seconds']}}


class BatchTests(unittest.TestCase):
    @contextlib.contextmanager
    def fixture(self):
        with tempfile.TemporaryDirectory() as d, \
             patch.object(br.pc,'make_manifest',side_effect=fake_manifest), \
             patch.object(br.pc,'validate_manifest'), \
             patch.object(br.pc.resources,'census',side_effect=census), \
             patch.object(br.pc.hp,'PinnedEvaluator') as evaluator:
            root=Path(d)
            planned=br.make_batch(inputs='unused',build='unused',times=list(range(72)),
                manifest=root/'batch.json',output=root/'run',cpus=list(range(8)),
                lanes=4,threads=2,logical=True,max_attempts=792,timeout_seconds=5)
            m=br.pc.read_bound(planned['manifest'],planned['execution_sha256'])
            yield root,m,planned
            evaluator.assert_not_called()

    def rewrite_lane(self,m,index,edit):
        row=m['lanes'][index]; path=Path(row['manifest'])
        lane=json.loads(path.read_text());edit(lane)
        path.write_text(json.dumps(lane))
        row['execution_sha256']=br.pc.hp.sha(path)

    def test_ordered_partition_owns_disjoint_global_reservations(self):
        with self.fixture() as (_,m,_):
            manifests,_=br.validate_batch(m)
            self.assertEqual([len(x['tasks']) for x in manifests],[18]*4)
            self.assertEqual([x['max_attempts'] for x in m['lanes']],[198]*4)
            self.assertEqual([x['global_reservation_range'] for x in m['lanes']],
                             [[1,198],[199,396],[397,594],[595,792]])
            self.assertEqual([t for row in m['lanes'] for t in row['times_hex']],m['times_hex'])

    def test_lane_exact_bytes_tamper_rejected_before_launch(self):
        with self.fixture() as (_,m,p), patch.object(br,'monitor') as monitor:
            path=Path(m['lanes'][2]['manifest']);path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'byte SHA256'):
                br.run_batch(m,p['execution_sha256'])
            monitor.assert_not_called()

    def test_duplicate_cpu_allocations_rejected(self):
        with self.fixture() as (_,m,_):
            self.rewrite_lane(m,1,lambda lane:lane['resources'].update(cpus=[0,1]))
            with self.assertRaisesRegex(ValueError,'overlap'):
                br.validate_batch(m)

    def test_aggregate_cpu_overcommit_rejected_with_individually_valid_lanes(self):
        info=census(); info['usable_cpu_budget']=6
        allocations=[br.pc.admit(census(),1,2,[i,i+1],0.5,True) for i in range(0,8,2)]
        with self.assertRaisesRegex(ValueError,'aggregate allocation'):
            br.aggregate_admit(info,allocations)

    def test_aggregate_memory_overcommit_rejected_with_individually_valid_lanes(self):
        info=census();info['memory_available_bytes']=int(2.5*br.GiB)
        allocations=[br.pc.admit(census(),1,2,[i,i+1],0.5,True) for i in range(0,8,2)]
        with self.assertRaisesRegex(ValueError,'aggregate RSS'):
            br.aggregate_admit(info,allocations)

    def test_lane_cap_transfer_or_global_range_reuse_rejected(self):
        for mutation in ('cap','range'):
            with self.subTest(mutation=mutation),self.fixture() as (_,m,_):
                if mutation=='cap':m['lanes'][0]['max_attempts']+=1
                else:m['lanes'][1]['global_reservation_range']=[1,198]
                with self.assertRaisesRegex(ValueError,'partition or lane cap'):
                    br.validate_batch(m)

    def test_current_memory_is_readmitted_before_any_launch(self):
        with self.fixture() as (_,m,p), patch.object(br,'monitor') as monitor:
            info=census();info['memory_available_bytes']=2*br.GiB
            with patch.object(br.pc.resources,'census',return_value=info):
                with self.assertRaisesRegex(ValueError,'aggregate RSS'):
                    br.run_batch(m,p['execution_sha256'])
            monitor.assert_not_called()

    def test_context_divergence_and_source_change_rejected(self):
        with self.fixture() as (_,m,_):
            self.rewrite_lane(m,1,lambda lane:lane.update(context={'id':'different'}))
            with self.assertRaisesRegex(ValueError,'same physical/numerical context'):
                br.validate_batch(m)
        with self.fixture() as (_,m,_):
            m['source_identity'][str(Path(br.__file__).resolve())]='0'*64
            with self.assertRaisesRegex(ValueError,'source identity'):
                br.validate_batch(m)

    def test_consumed_output_rejected_before_launch(self):
        with self.fixture() as (_,m,p), patch.object(br,'monitor') as monitor:
            Path(m['lanes'][0]['output']).mkdir()
            with self.assertRaisesRegex(ValueError,'consumed'):
                br.run_batch(m,p['execution_sha256'])
            monitor.assert_not_called()

    def test_real_failure_cancels_watchdog_and_long_child(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);lane=out/'fake_lane';lane.mkdir()
            marker=lane/'WORKER.json'
            setup='import sys;sys.path.insert(0,'+repr(str(br.PROVIDER))+');import precompute_cli as pc;'
            worker=setup+'import json,time;from pathlib import Path;Path('+repr(str(marker))+').write_text(json.dumps(pc._process()));time.sleep(30)'
            wrapped=(setup+'import signal,os;from pathlib import Path;\n'
                'def cancel(s,f): raise KeyboardInterrupt("synthetic batch cancellation")\n'
                'signal.signal(signal.SIGTERM,cancel)\n'
                'r=pc.supervise('+repr([sys.executable,'-I','-c',worker])+',Path('+repr(str(lane))+'),30.,"'+('a'*64)+'",os.environ.copy())\n'
                'raise SystemExit(0 if r["success"] else 1)\n')
            fail=('from pathlib import Path\nimport time\np=Path('+repr(str(marker))+')\n'
                  'deadline=time.monotonic()+10\n'
                  'while not p.exists() and time.monotonic()<deadline: time.sleep(0.02)\n'
                  'raise SystemExit(7)\n')
            result=br.monitor([[sys.executable,'-I','-c',wrapped],[sys.executable,'-I','-c',fail]],
                              out,timeout_seconds=12,grace_seconds=4)
            self.assertFalse(result['success']);self.assertTrue(result['cancelled_live_lanes'])
            self.assertEqual(result['first_failure']['returncode'],7)
            receipt=json.loads((lane/'SUPERVISOR_RESULT.json').read_text())
            self.assertFalse(receipt['success']);self.assertIn('KeyboardInterrupt',receipt['error'])
            self.assertEqual(receipt['returncode'],130)
            process=json.loads(marker.read_text())
            try:actual=br.pc._process(process['pid'])
            except (OSError,ValueError):actual=None
            self.assertNotEqual(actual,process,'the synthetic worker must not survive cancellation')

    def test_outer_deadline_cancels_real_hung_child(self):
        with tempfile.TemporaryDirectory() as d:
            result=br.monitor([[sys.executable,'-c','import time;time.sleep(30)']],
                              Path(d),timeout_seconds=0.15,grace_seconds=0.3)
            self.assertFalse(result['success'])
            self.assertEqual(result['first_failure']['kind'],'OVERALL_TIMEOUT')
            self.assertIsNotNone(result['lanes'][0]['returncode'])

    def test_abrupt_wrapper_exit_and_sigkill_leave_no_independent_session_child(self):
        for action in ('exit7','sigkill','exit0'):
            with self.subTest(action=action),tempfile.TemporaryDirectory() as d:
                out=Path(d);marker=out/'WORKER.json'
                setup='import sys;sys.path.insert(0,'+repr(str(br.PROVIDER))+');import precompute_cli as pc;'
                worker=(setup+'import json,time;from pathlib import Path;'
                        'Path('+repr(str(marker))+').write_text(json.dumps(pc._process()));time.sleep(30)')
                ending={'exit7':'os._exit(7)','sigkill':'os.kill(os.getpid(),signal.SIGKILL)',
                        'exit0':'os._exit(0)'}[action]
                wrapper=('import subprocess,sys,time,os,signal\nfrom pathlib import Path\n'
                         'p=subprocess.Popen('+repr([sys.executable,'-I','-c',worker])+',start_new_session=True)\n'
                         'marker=Path('+repr(str(marker))+')\n'
                         'while not marker.exists():time.sleep(0.001)\n'+ending)
                prior=br._subreaper()
                result=br.monitor([[sys.executable,'-I','-c',wrapper]],out,
                                   timeout_seconds=10,grace_seconds=0.2)
                self.assertFalse(result['success'])
                self.assertEqual(result['terminal_cleanup']['survivors'],[])
                self.assertEqual(br._subreaper(),prior)
                identity=json.loads(marker.read_text())
                self.assertFalse(br._alive_exact(identity))
                with self.assertRaises(ChildProcessError):
                    os.waitpid(identity['signal_pid'],os.WNOHANG)

    def test_unbound_receipt_does_not_authorize_signalling_unrelated_identity(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);owner=br.pc._process();fake=dict(owner)
            fake.update(signal_pid=123456,ppid=owner['pid'])
            (out/'SUPERVISOR.json').write_text(json.dumps({'process':fake,'execution_sha256':'wrong'}))
            (out/'ADMISSION.json').write_text(json.dumps({'execution_sha256':'expected','ranks':[
                {'rank':0,'ok':True,'process':owner,'execution_sha256':'expected','context_id':'ctx'}]}))
            rows,rejected=br._receipt_descendants([{'output':d,'execution_sha256':'expected',
                'context_id':'ctx'}],{0:SimpleNamespace(pid=123456)},owner)
            self.assertEqual(rows,[])
            self.assertEqual(len(rejected),1)


if __name__=='__main__':unittest.main()
