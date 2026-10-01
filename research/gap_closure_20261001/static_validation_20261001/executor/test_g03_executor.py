import copy
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock,patch
import numpy as np
import g03_executor as g


class G03ExecutorTests(unittest.TestCase):
    def sample(self):
        authority={k:'a'*64 for k in g.AUTHORITY_KEYS}
        authority['execution_commit']='b'*40;authority['execution_tree']='c'*40
        p={**authority,**g.fixed_scope(),'authorization_id':'G03-STATIC48-20261001-SYNTHETIC-TEST',
           'workers':1,'hard_max_workers':2,'approved_cpu_list':[0],
           'worker_ram_bytes':4<<30,'total_worker_ram_cap_bytes':4<<30,
           'minimum_live_available_bytes':8<<30,'wall_seconds':100,
           'deadline_unix':time.time()+99,'termination_grace_seconds':1,'cost_scope':'TEST ONLY no native'}
        return p,authority

    def test_exact_twoquery_frozen_scope(self):
        plan=g.frozen_plan();self.assertEqual([q['z_a0'] for q in plan['queries']],[-48.,48.])
        self.assertEqual(len(g.exact_items(plan)),2)
        bad=copy.deepcopy(plan);bad['queries'][0]['z_a0']=-44
        with self.assertRaises(ValueError):g.exact_items(bad)

    def test_no_g02_or_old_auth_or_resource_expansion(self):
        p,a=self.sample();g.validate_scope(p,a,approved=True)
        for key,value in [('authorization_id','G02-FD-20261001-SYNTHETIC-TEST'),
            ('raw_operator_evaluation_cap',726),('operator_query_count',66),('transport',True),
            ('derivative_fd_queries',66),('workers',3),('worker_ram_bytes',1<<30),
            ('deadline_unix',0),('wall_seconds',901)]:
            bad=copy.deepcopy(p);bad[key]=value
            with self.subTest(key=key),self.assertRaises((ValueError,PermissionError)):
                g.validate_scope(bad,a,approved=True)

    def test_unapproved_and_unknown_query_never_native(self):
        trap=Mock(side_effect=AssertionError('native factory reached'))
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);p=root/'p.json';s=root/'s.json';p.write_text('{}');s.write_text('{}')
            with self.assertRaises(PermissionError):g.request(p,s,root/'i',root/'b',root/'o',approved_sha='',pool_factory=trap)
        trap.assert_not_called()
        import g03_worker
        with self.assertRaises(ValueError):g03_worker.compute(g.PlannedQuery('other','0x0.0p+0',None,None))

    def test_synthetic_pair_full_return(self):
        from qualified_provider import ResolutionQualifiedProvider,CROSS_KEYS
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);plan=g.frozen_plan()
            budget=g.GlobalBudget.create(out/'GLOBAL_BUDGET',parent_attempts=0,maximum=22,deadline_unix=time.time()+60)
            def compute(item):
                task=out/'worker_tasks'/item.query_id;task.mkdir(parents=True)
                def evaluate(t,order,subdivisions):
                    budget.reserve(item.query_id,order,subdivisions)
                    raw={k:np.zeros((9,9),complex) for k in CROSS_KEYS}
                    H=np.eye(18,dtype=complex);H[0,9]=H[9,0]=.0002
                    raw['H_tp'][0,0]=raw['H_pt'][0,0]=.0002
                    return raw,{'S':np.eye(18,dtype=complex),'H':H,'D':np.zeros((18,18),complex)}
                p=ResolutionQualifiedProvider(evaluate=evaluate,resolutions=plan['qualification_ladder'],
                    screens=plan['active_screens'],context_id=plan['context_id'],out_dir=task,max_unique_queries=1)
                p.at(float.fromhex(item.time_hex));return {'task_dir':str(task),'worker_pid':os.getpid()}
            with patch('ctypes.CDLL',side_effect=AssertionError('native load forbidden')) as trap:
                with ThreadPoolExecutor(max_workers=2) as pool:audit=g.execute_plan(plan,out,budget,pool,compute,2)
            trap.assert_not_called();self.assertEqual(audit['completed_queries'],2)
            self.assertEqual(audit['raw_attempts'],4);self.assertFalse(audit['physical_G03_closed'])
            samples=json.loads((out/'RHO_SAMPLES.json').read_text())['samples']
            self.assertEqual([x['z_a0'] for x in samples],[-48.,48.])
            self.assertTrue(all(abs(x['rho_per_atomic_time']-.0002)<1e-12 for x in samples))
            self.assertTrue(all((out/x['diagnostic_relative_path']).is_file() for x in samples))
            self.assertTrue((out/'G03_RETURN_ANALYSIS.json').is_file())
            with ThreadPoolExecutor(max_workers=1) as pool:
                with self.assertRaises(FileExistsError):g.execute_plan(plan,out,budget,pool,compute,1)


if __name__=='__main__':unittest.main()
