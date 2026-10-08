"""Synthetic end-to-end qualification/cache/trajectory/restart tests only."""
from pathlib import Path
import json
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
import numpy as np
from numpy.testing import assert_array_equal,assert_allclose
import bootstrap_runtime
from qualified_provider import ResolutionQualifiedProvider,CROSS_KEYS
from metric_transport import run_candidate
from solver_plan import make_plan,digest
from qualified_cache import QualifiedCache
from checkpoint_solver import run_cached

CONTRACT={'runtime_reference_resolutions':[{'order':4,'subdivisions':1},{'order':8,'subdivisions':1}],
          'screens':{'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-11,
                     'metric_min_ratio':1e-8,'candidate_norm_drift_max':1e-8}}

def fixture(tmp,nstep=8):
    plan=make_plan(-.3,.7,nstep,digest({'synthetic':1}),qualification_contract=CONTRACT,selected_indices=[0])
    out=Path(tmp)/'queries';out.mkdir()
    def evaluate(t,order,subdivisions):
        # Coupled exact two-state Hamiltonian embedded in the real18-channel shape.
        s=np.eye(18,dtype=complex);h=np.zeros((18,18),complex);d=np.zeros_like(h)
        h[0,1]=.3+.1j*t;h[1,0]=h[0,1].conjugate();h[0,0]=.2*t;h[1,1]=-.1*t
        raw={key:np.zeros((9,9),complex) for key in CROSS_KEYS}
        return raw,{'S':s,'H':h,'D':d}
    provider=ResolutionQualifiedProvider(evaluate=evaluate,resolutions=CONTRACT['runtime_reference_resolutions'],
         screens=CONTRACT['screens'],context_id=plan['context_id'],out_dir=out,max_unique_queries=nstep+2)
    for row in plan['queries']:provider.at(float.fromhex(row['time_hex']))
    c0=np.zeros(18,complex);c0[0]=2
    return plan,out/'runtime_queries',c0

class RuntimeSolverTests(unittest.TestCase):
    def test_identical_to_frozen_midpoint_and_restart_bitwise(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan,cache,c0=fixture(tmp)
            old=run_candidate(QualifiedCache(cache,plan),c0,-.3,.7,8)
            full=run_cached(plan,cache,Path(tmp)/'full',c0)
            run_cached(plan,cache,Path(tmp)/'partial',c0,stop_after_steps=3)
            resumed=run_cached(plan,cache,Path(tmp)/'resumed',c0,resume_from=Path(tmp)/'partial')
            for path in ('full','resumed'):
                with np.load(Path(tmp)/path/'CANDIDATE_RESULT.npz',allow_pickle=False) as data:
                    assert_array_equal(data['final_state'],old.final_state)
                    assert_array_equal(data['norm_history'],old.norm_history)
            self.assertEqual(full['max_norm_drift'],resumed['max_norm_drift'])
            self.assertEqual(full['new_native_operator_calls'],0)
            self.assertFalse(full['continuous_trajectory_error_bound'])

    def test_cache_miss_and_tampering_fail_without_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan,path,c0=fixture(tmp)
            cache=QualifiedCache(path,plan)
            with self.assertRaises(KeyError):cache.at(.123456)
            payload=path/(plan['queries'][0]['query_id']+'.npz')
            payload.write_bytes(payload.read_bytes()+b'tamper')
            with self.assertRaises(ValueError):cache.at(-.3)
            self.assertEqual(cache.native_calls,0)

    def test_cache_rejects_each_rehashed_full_raw_cross_mismatch(self):
        for key in CROSS_KEYS:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as tmp:
                plan,path,c0=fixture(tmp,nstep=2)
                payload=path/(plan['queries'][0]['query_id']+'.npz')
                with np.load(payload,allow_pickle=False) as data:arrays={name:np.array(data[name]) for name in data.files}
                # Both resolutions retain exact convergence; the full matrix is unchanged.
                for level in ('q4_h1','q8_h1'):arrays[level+'__'+key][0,0]=.001
                np.savez_compressed(payload,**arrays)
                record=payload.with_suffix('.json');row=json.loads(record.read_text())
                row['payload_sha256']=hashlib.sha256(payload.read_bytes()).hexdigest()
                record.write_text(json.dumps(row))
                with self.assertRaisesRegex(ValueError,'cross binding'):
                    QualifiedCache(path,plan)

    def test_resume_rejects_state_plan_and_checkpoint_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan,cache,c0=fixture(tmp)
            partial=Path(tmp)/'partial';run_cached(plan,cache,partial,c0,stop_after_steps=3)
            changed=c0.copy();changed[0]=1
            with self.assertRaisesRegex(ValueError,'initial'):
                run_cached(plan,cache,Path(tmp)/'badstate',changed,resume_from=partial)
            changed_plan=json.loads(json.dumps(plan));changed_plan['selected_indices']=[1]
            with self.assertRaises(ValueError):
                run_cached(changed_plan,cache,Path(tmp)/'badplan',c0,resume_from=partial)
            payload=partial/'checkpoints/STEP_00000002.npz';payload.write_bytes(payload.read_bytes()+b'x')
            with self.assertRaisesRegex(ValueError,'checkpoint'):
                run_cached(plan,cache,Path(tmp)/'badpayload',c0,resume_from=partial)

    def test_partial_pair_and_existing_output_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan,cache,c0=fixture(tmp)
            partial=Path(tmp)/'partial';run_cached(plan,cache,partial,c0,stop_after_steps=3)
            with self.assertRaises(FileExistsError):run_cached(plan,cache,partial,c0)
            (partial/'checkpoints/STEP_00000004.npz').write_bytes(b'incomplete')
            with self.assertRaisesRegex(ValueError,'orphan'):
                run_cached(plan,cache,Path(tmp)/'resume',c0,resume_from=partial)

    def test_isolated_cli_runs_same_cache_only_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan,cache,c0=fixture(tmp,nstep=2)
            path=Path(tmp)
            (path/'PLAN.json').write_text(json.dumps(plan))
            np.savez(path/'STATE.npz',initial_state=c0)
            command=[sys.executable,'-I',str(Path(__file__).with_name('solver_cli.py')),'propagate',
                     '--plan',str(path/'PLAN.json'),'--cache-dir',str(cache),
                     '--initial-state',str(path/'STATE.npz'),'--out',str(path/'cli_out')]
            result=subprocess.run(command,capture_output=True,text=True,env=dict(os.environ),timeout=20)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads(result.stdout)
            self.assertEqual(report['completed_steps'],2)
            self.assertEqual(report['new_native_operator_calls'],0)
            self.assertEqual(report['production_admission'],'HOLD')
            self.assertEqual(report['observable_scope'],'FINITE_SELECTED_SPAN_DIAGNOSTIC_NOT_CAPTURE')

if __name__=='__main__':unittest.main(verbosity=2)
