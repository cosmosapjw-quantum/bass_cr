"""Synthetic cache/provenance tests only; no native evaluator or physics."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import fresh_context_analysis as a


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, allow_nan=False)+'\n')


def evaluator(t, order, subdivisions):
    raw = {name+suffix: np.zeros((9,9), complex)
           for name in ('S','H','D') for suffix in ('_tp','_pt')}
    full = {'S': np.eye(18, dtype=complex), 'H': np.diag(np.arange(18)).astype(complex),
            'D': np.zeros((18,18),complex), 'metadata': {'synthetic': True}}
    return raw, full


def fixture(root, name='lane', time=1., context_id='test-context'):
    root = Path(root); out = root/name; out.mkdir()
    contract = {'runtime_reference_resolutions': [{'order':32,'subdivisions':1},
                                                 {'order':40,'subdivisions':1}],
                'screens': {'raw_cross_relative_max':1e-9,
                            'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8}}
    context = {'context_id': context_id, 'backend':'fortran', 'threads':2,
               'qualification_contract':contract, 'old_context_reuse':False}
    task = a.hp.build_tasks(context_id,[time],contract)[0]
    def reserve(index): return index+1
    reserve.task_dir = str(out/'synthetic_task')
    row = a.hp.qualified_task(task,reserve,evaluator,context_id,contract)
    cache = a.hp.collect_cache([row],out/'cache',context_id,contract)
    manifest = {'schema':'BASS_R4U_PHYSICAL_EXECUTION_V1', 'inputs':'synthetic-input',
                'build':'synthetic-build', 'output':str(out), 'context':context,
                'tasks':[task], 'limits':{'max_attempts':2}}
    path = root/(name+'_PLAN.json'); write(path,manifest)
    (out/'EXECUTION.json').write_bytes(path.read_bytes()); digest=a.hp.sha(path)
    write(out/'ADMISSION.json',{'admitted':True,'execution_sha256':digest})
    write(out/'SUPERVISOR_RESULT.json',{'success':True,'status':'EXITED',
                                      'returncode':0,'execution_sha256':digest})
    write(out/'RESULT.json',{'ok':True,'execution_sha256':digest,
                            'context_id':context_id,'cache':cache})
    write(out/'queue/QUEUE_RECEIPT.json',{'status':'COMPLETE','failure':None,
          'task_count':1,'canonical_prefix_count':1,'max_attempts':2,'raw_attempts_reserved':2})
    return path, context, task


class FreshAnalysisTests(unittest.TestCase):
    def test_real_saved_pair_validation_without_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,context,task=fixture(tmp)
            with patch.object(a.hp,'prepare_context',return_value=context), \
                 patch.object(a.hp,'PinnedEvaluator',side_effect=AssertionError('native forbidden')):
                samples,provenance,actual=a._load_lanes([path],[task['time_hex']])
            self.assertEqual(actual,context)
            self.assertEqual(provenance[0]['raw_attempts'],2)
            np.testing.assert_array_equal(samples[task['time_hex']]['S'],np.eye(18))

    def test_missing_required_time_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,context,task=fixture(tmp)
            with patch.object(a.hp,'prepare_context',return_value=context):
                with self.assertRaisesRegex(ValueError,'missing exact'):
                    a._load_lanes([path],[task['time_hex'],float(2).hex()])

    def test_duplicate_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,context,task=fixture(tmp)
            with self.assertRaisesRegex(ValueError,'distinct lane'):
                a._load_lanes([path,path],[task['time_hex']])

    def test_duplicate_time_across_lanes_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p0,context,task=fixture(tmp,'lane0')
            p1,_,_=fixture(tmp,'lane1')
            with patch.object(a.hp,'prepare_context',return_value=context):
                with self.assertRaisesRegex(ValueError,'duplicate or foreign'):
                    a._load_lanes([p0,p1],[task['time_hex']])

    def test_foreign_context_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p0,c0,t0=fixture(tmp,'lane0')
            p1,c1,t1=fixture(tmp,'lane1',time=2.,context_id='foreign')
            with patch.object(a.hp,'prepare_context',side_effect=[c0,c1]):
                with self.assertRaisesRegex(ValueError,'foreign context'):
                    a._load_lanes([p0,p1],[t0['time_hex'],t1['time_hex']])

    def test_fresh_context_source_change_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,context,task=fixture(tmp);changed={**context,'source_pins':{'changed':'hash'}}
            with patch.object(a.hp,'prepare_context',return_value=changed):
                with self.assertRaisesRegex(ValueError,'fresh source/native/input'):
                    a._load_lanes([path],[task['time_hex']])

    def test_tampered_payload_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,context,task=fixture(tmp)
            payload=Path(tmp)/'lane/cache'/(task['query_id']+'.npz')
            payload.write_bytes(payload.read_bytes()+b'tampered')
            with patch.object(a.hp,'prepare_context',return_value=context):
                with self.assertRaisesRegex(ValueError,'sha256'):
                    a._load_lanes([path],[task['time_hex']])

    def test_foreign_provider_context_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,context,task=fixture(tmp)
            record=Path(tmp)/'lane/cache'/(task['query_id']+'.json')
            data=a.read(record); data['context_id']='foreign'; write(record,data)
            with patch.object(a.hp,'prepare_context',return_value=context):
                with self.assertRaisesRegex(ValueError,'query identity'):
                    a._load_lanes([path],[task['time_hex']])

    def test_incomplete_supervisor_prevents_any_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path,context,task=fixture(tmp)
            receipt=Path(tmp)/'lane/SUPERVISOR_RESULT.json'
            data=a.read(receipt); data['success']=False; write(receipt,data)
            with patch.object(a.hp,'prepare_context',return_value=context):
                with self.assertRaisesRegex(ValueError,'completed admission'):
                    a._load_lanes([path],[task['time_hex']])

    def test_g02_calls_exact_unchanged_comparator_for_all_eight_centers(self):
        plan=a._fixed(a.FD_PLAN,a.FD_PLAN_SHA); samples={};k=.01;v=plan['identity']['velocity_au']
        for q in plan['queries']:
            S=np.eye(18)*np.exp(k*q['z_a0'])
            samples[q['time_hex']]={'S':S,'D':.5*v*k*S,
                    'evidence':{'query_id':'synthetic-'+q['z_hex']}}
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'report.json'
            with patch.object(a,'_load_lanes',return_value=(samples,[{'raw_attempts':144}],{'context_id':'ctx'})), \
                 patch.object(a.fd,'compare_ladder',wraps=a.fd.compare_ladder) as compare:
                report=a.analyze_g02(['mock_lane'],output)
            self.assertEqual(compare.call_count,8)
            for call in compare.call_args_list:
                self.assertEqual(call.args[2:],(v,1e-6,1e-12))
                self.assertEqual([row[0] for row in call.args[1]],[.4,.2,.1,.05])
            self.assertEqual(report['fresh_snapshot_count'],72)
            self.assertEqual(report['historical_snapshot_reuse_count'],0)
            self.assertFalse(report['physical_G02_closed'])
            self.assertEqual(report['status'],'ALL_FD_DIAGNOSTICS_PASS')

    def test_exact_plateau_is_not_automatic_order_pass(self):
        D=np.zeros((18,18));S=np.eye(18)
        result=a.fd.compare_ladder(D,[(h,S,S) for h in [.4,.2,.1,.05]],2.)
        self.assertEqual(result['status'],'ORDER_NOT_RESOLVED')
        self.assertFalse(result['passed'])
        self.assertEqual(result['observed_orders'],[None,None,None])

    def test_freeze_is_create_only_and_tamper_blocks_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            frozen=Path(tmp)/'frozen.json';output=Path(tmp)/'result'
            a.freeze_g03_predictions(frozen)
            with self.assertRaises(FileExistsError):a.freeze_g03_predictions(frozen)
            record=a.read(frozen);record['baseline_samples'][0]['rho_per_atomic_time']*=2
            write(frozen,record)
            with patch.object(a,'_load_lanes',side_effect=AssertionError('must validate frozen first')):
                with self.assertRaisesRegex(ValueError,'predeclared baseline'):
                    a.analyze_g03('unused_manifest',frozen,output)
            self.assertFalse(output.exists())

    def test_existing_root_frozen_format_validated_before_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            baseline=a.models.load_samples();frozen=a.models.analyze(baseline)
            frozen.update(source_csv_sha256=a.hp.sha(a.models.DEFAULT_SAMPLES),
                          analyzer_sha256=a.hp.sha(a.models.__file__),
                          purpose='FROZEN_BEFORE_ANY_R4V_PHYSICAL_CALL')
            path=Path(tmp)/'frozen.json';write(path,frozen)
            with patch.object(a,'_load_lanes',side_effect=ValueError('reached verified cache')):
                with self.assertRaisesRegex(ValueError,'reached verified cache'):
                    a.analyze_g03('unused',path,Path(tmp)/'output')


if __name__=='__main__':unittest.main()
