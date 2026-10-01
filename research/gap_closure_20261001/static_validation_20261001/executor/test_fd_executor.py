import copy
import json
import tempfile
import time
import unittest
import os
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock,patch
import fd_executor as fd


class ExecutorTests(unittest.TestCase):
    def sample(self):
        authority={k:'a'*64 for k in fd.AUTHORITY_KEYS}
        authority['execution_commit']='b'*40;authority['execution_tree']='c'*40
        p={**authority,**fd.fixed_scope(),'authorization_id':'G02-FD-20261001-SYNTHETIC-TEST',
           'workers':1,'hard_max_workers':8,'approved_cpu_list':[0],
           'worker_ram_bytes':1<<30,'total_worker_ram_cap_bytes':1<<30,
           'minimum_live_available_bytes':5<<30,'wall_seconds':100,
           'deadline_unix':time.time()+99,'termination_grace_seconds':1,'cost_scope':'TEST ONLY no native'}
        return p,authority

    def test_frozen_plan_rejects_changed_scope(self):
        plan=fd.frozen_plan();items=fd.exact_items(plan)
        self.assertEqual(len(items),66)
        self.assertEqual(plan['max_raw_operator_evaluations'],726)
        bad=copy.deepcopy(plan);bad['queries'][0]['z_a0']=-100
        with self.assertRaises(ValueError):fd.exact_items(bad)

    def test_scope_rejects_old_auth_and_all_resource_drift(self):
        p,a=self.sample();fd.validate_scope(p,a,approved=True)
        with self.assertRaises(PermissionError):fd.validate_scope(p,a,approved=False)
        with self.assertRaises(PermissionError):fd.validate_scope(p,a,approved=True,unused=False)
        for key,value in [('authorization_id','R4P0-B0-STATIC-TAIL-20260930-A1'),
            ('raw_operator_evaluation_cap',88),('operator_query_count',8),('transport',True),
            ('numerical_threads',2),('workers',9),('approved_cpu_list',[0,0]),
            ('worker_ram_bytes',2<<30),('deadline_unix',0),('pilot_queries',1)]:
            bad=copy.deepcopy(p);bad[key]=value
            with self.subTest(key=key),self.assertRaises((ValueError,PermissionError)):
                fd.validate_scope(bad,a,approved=True)

    def test_unapproved_request_never_reaches_factory(self):
        trap=Mock(side_effect=AssertionError('native factory reached'))
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);proposal=root/'p.json';pins=root/'pins.json'
            proposal.write_text('{}');pins.write_text('{}')
            with self.assertRaises(PermissionError):
                fd.request(proposal,pins,root/'inputs',root/'build',root/'output',approved_sha='',pool_factory=trap)
        trap.assert_not_called()

    def test_budget_shape_and_deadline(self):
        with tempfile.TemporaryDirectory() as td:
            b=fd.GlobalBudget.create(Path(td)/'budget',parent_attempts=0,maximum=726,deadline_unix=time.time()+60)
            fd.verify_budget(b,1)
            b.seed['maximum']=88
            with self.assertRaises(ValueError):fd.verify_budget(b,1)

    def test_query_whitelist_before_worker(self):
        import fd_worker
        with self.assertRaises(ValueError):fd_worker.compute(fd.PlannedQuery('unplanned','0x0.0p+0',None,None))

    def test_source_pin_drift_fails_closed(self):
        pins={'source_files':{n:fd.sha(fd.REPO/n) for n in fd.required_sources()}}
        first=next(iter(pins['source_files']));pins['source_files'][first]='0'*64
        with self.assertRaisesRegex(ValueError,'pinned source mismatch'):fd.verify_source(pins)

    def test_synthetic_full_collector_66_new_and_6_real_saved(self):
        # Synthetic evaluator exercises publication and return plumbing only.
        # It never claims its made-up operators are physical source outputs.
        from qualified_provider import ResolutionQualifiedProvider,CROSS_KEYS
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);plan=fd.frozen_plan()
            budget=fd.GlobalBudget.create(out/'GLOBAL_BUDGET',parent_attempts=0,maximum=726,deadline_unix=time.time()+60)
            def compute(item):
                task=out/'worker_tasks'/item.query_id;task.mkdir(parents=True)
                def evaluate(t,order,subdivisions):
                    budget.reserve(item.query_id,order,subdivisions)
                    raw={k:np.zeros((9,9),complex) for k in CROSS_KEYS}
                    return raw,{'S':np.eye(18,dtype=complex),'H':np.eye(18,dtype=complex),'D':np.zeros((18,18),complex)}
                p=ResolutionQualifiedProvider(evaluate=evaluate,resolutions=plan['qualification_ladder'],
                    screens=plan['active_screens'],context_id=plan['context_id'],out_dir=task,max_unique_queries=1)
                p.at(float.fromhex(item.time_hex))
                return {'task_dir':str(task),'worker_pid':os.getpid()}
            with patch('ctypes.CDLL',side_effect=AssertionError('native load forbidden')) as trap:
                with ThreadPoolExecutor(max_workers=2) as pool:
                    audit=fd.execute_plan(plan,out,budget,pool,compute,2)
            trap.assert_not_called()
            self.assertEqual(audit['completed_queries'],66);self.assertEqual(audit['reused_queries'],6)
            self.assertEqual(audit['raw_attempts'],132);self.assertEqual(audit['total_snapshots'],72)
            self.assertFalse(audit['physical_G02_closed'])
            manifest=json.loads((out/'ALL_SNAPSHOTS_MANIFEST.json').read_text())
            self.assertEqual(len(manifest['snapshots']),72)
            with ThreadPoolExecutor(max_workers=1) as pool:
                with self.assertRaises(FileExistsError):fd.execute_plan(plan,out,budget,pool,compute,1)

    def test_saved_native_preload_validation_never_dlopen(self):
        root=fd.REPO.parent/'restored_static_A1/EXECUTION_PREPARATION'
        if not root.exists():self.skipTest('optional restored-byte audit fixture absent')
        with patch('ctypes.CDLL',side_effect=AssertionError('native load forbidden')) as trap:
            contract,plan,native=fd.verify_inputs(root/'runtime_inputs',root/'native_build')
        trap.assert_not_called();self.assertFalse(native['native_loaded_by_check'])

    def test_complete_synthetic_collector_and_create_only(self):
        from qualified_provider import ResolutionQualifiedProvider
        plan=fd.frozen_plan()
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'return';out.mkdir()
            budget=fd.GlobalBudget.create(out/'GLOBAL_BUDGET',parent_attempts=0,maximum=726,deadline_unix=time.time()+60)
            def compute(item):
                task=out/'worker_tasks'/item.query_id;task.mkdir(parents=True)
                def evaluate(t,order,subdivisions):
                    budget.reserve(item.query_id,order,subdivisions)
                    raw={k:np.zeros((9,9),complex) for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')}
                    return raw,{'S':np.eye(18),'H':np.eye(18),'D':np.zeros((18,18))}
                provider=ResolutionQualifiedProvider(evaluate=evaluate,resolutions=plan['qualification_ladder'],
                     screens=plan['active_screens'],context_id=plan['context_id'],out_dir=task,max_unique_queries=1)
                provider.at(float.fromhex(item.time_hex))
                return {'task_dir':str(task),'worker_pid':os.getpid()}
            with ThreadPoolExecutor(max_workers=2) as pool:
                result=fd.execute_plan(plan,out,budget,pool,compute,2)
            self.assertEqual(result['completed_queries'],66)
            self.assertEqual(result['reused_queries'],6)
            self.assertEqual(result['raw_attempts'],132)
            self.assertFalse(result['physical_G02_closed'])
            manifest=json.loads((out/'ALL_SNAPSHOTS_MANIFEST.json').read_text())
            self.assertEqual(len(manifest['snapshots']),72)
            with ThreadPoolExecutor(max_workers=1) as pool:
                with self.assertRaises(FileExistsError):fd.execute_plan(plan,out,budget,pool,compute,1)
            self.assertEqual(budget.used(),132)

    def test_first_failure_cancels_dispatch_without_native(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);budget=fd.GlobalBudget.create(out/'GLOBAL_BUDGET',parent_attempts=0,maximum=726,deadline_unix=time.time()+60)
            calls=[]
            def fail(item):calls.append(item);raise ValueError('synthetic first failure')
            with ThreadPoolExecutor(max_workers=1) as pool:
                with self.assertRaises(ValueError):fd.execute_plan(fd.frozen_plan(),out,budget,pool,fail,1)
            self.assertEqual(len(calls),1)
            self.assertEqual(budget.used(),0)
            self.assertTrue((out/'FIRST_FAILURE.json').exists())
            self.assertTrue((budget.root/'CANCELLED.json').exists())


if __name__=='__main__':unittest.main()
