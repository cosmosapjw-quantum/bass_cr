import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
import numpy as np
from hpc_provider import validate_contract, bind_rank, build_tasks, qualified_task, SerialComm, collect_cache,prepare_context,INPUT_SHA,digest,source_pins

LEVELS=[{'order':4,'subdivisions':1},{'order':8,'subdivisions':1},{'order':12,'subdivisions':1}]
SCREENS={'raw_cross_relative_max':1e-9,'operator_hermiticity_relative_max':1e-12,'metric_min_ratio':1e-8}

def contract():return {'runtime_reference_resolutions':LEVELS,'screens':SCREENS}
def evaluator(t,q,h):
    a=np.ones((9,9),complex)*1e-3
    raw={k:a.copy() for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')}
    full={'S':np.eye(18,dtype=complex),'H':np.diag(np.arange(18)).astype(complex),'D':np.zeros((18,18),complex),'metadata':{'backend':'SYNTHETIC'}}
    for name in ('S','H','D'):
        full[name][:9,9:]=raw[name+'_tp']
        full[name][9:,:9]=raw[name+'_pt']
    return raw,full

def rewrite_raw_pair(payload,keys):
    with np.load(payload,allow_pickle=False) as data:arrays={key:np.array(data[key]) for key in data.files}
    for level in ('q4_h1','q8_h1'):
        for key in keys:arrays[level+'__'+key][0,0]+=.001
    np.savez_compressed(payload,**arrays)
    record=payload.with_suffix('.json');row=json.loads(record.read_text())
    row['payload_sha256']=hashlib.sha256(payload.read_bytes()).hexdigest()
    record.write_text(json.dumps(row))

class ProviderTests(unittest.TestCase):
    def test_contract_rejects_duplicate_resolution(self):
        c=contract();c['runtime_reference_resolutions']=[LEVELS[0]]*2
        with self.assertRaises(ValueError):validate_contract(c)
    def test_contract_rejects_missing_or_nonfinite_screen(self):
        for key in SCREENS:
            c=contract();c['screens']={**SCREENS,key:float('nan')}
            with self.assertRaises(ValueError):validate_contract(c)
    def test_tasks_bind_exact_time_context_and_prefix(self):
        c=contract();tasks=build_tasks('ctx',[0.,1.],c)
        self.assertEqual(tasks[0]['levels'],LEVELS)
        self.assertNotEqual(tasks[0]['query_id'],build_tasks('ctx2',[0.],c)[0]['query_id'])
        with self.assertRaises(ValueError):build_tasks('ctx',[0.,0.],c)
        with self.assertRaises(ValueError):build_tasks('ctx',[float('inf')],c)
    def test_rank_binding_exact_and_disjoint(self):
        actual={0,1,2,3};bound=[]
        def set_(pid,cpus):actual.clear();actual.update(cpus);bound.append(cpus)
        r=bind_rank(1,2,2,[0,1,2,3],get=lambda pid:actual,set_=set_)
        self.assertEqual(r['cpus'],[2,3]);self.assertEqual(bound,[{2,3}])
    def test_binding_fails_closed(self):
        with self.assertRaises(ValueError):bind_rank(0,2,2,[0,1,1,2],get=lambda p:{0,1,2},set_=Mock())
        with self.assertRaises(ValueError):bind_rank(0,2,2,[0,1,2,3],get=lambda p:{0,1},set_=Mock())
        with self.assertRaises(ValueError):bind_rank(0,2,2,[0,1,2,3],get=lambda p:{0,1,2,3},set_=lambda p,c:None)
    def test_reserve_precedes_every_attempt(self):
        with tempfile.TemporaryDirectory() as d:
            events=[]
            def ev(t,q,h):events.append(('evaluate',q));return evaluator(t,q,h)
            def reserve(i):events.append(('reserve',i));return i+1
            reserve.task_dir=d
            task=build_tasks('ctx',[0.],contract())[0]
            result=qualified_task(task,reserve,ev,'ctx',contract())
            self.assertEqual(events,[('reserve',0),('evaluate',4),('reserve',1),('evaluate',8)])
            self.assertEqual(result['raw_attempts'],2)
            self.assertEqual(len(list((Path(d)/'attempts').glob('*.npz'))),2)
    def test_wrong_task_never_evaluates(self):
        with tempfile.TemporaryDirectory() as d:
            task=build_tasks('ctx',[0.],contract())[0];task['query_id']='wrong'
            reserve=Mock();reserve.task_dir=d;ev=Mock(side_effect=AssertionError('called'))
            with self.assertRaises(ValueError):qualified_task(task,reserve,ev,'ctx',contract())
            reserve.assert_not_called();ev.assert_not_called()
    def test_denied_reservation_never_evaluates(self):
        with tempfile.TemporaryDirectory() as d:
            reserve=Mock(side_effect=RuntimeError('budget exhausted'));reserve.task_dir=d;ev=Mock()
            with self.assertRaises(RuntimeError):qualified_task(build_tasks('ctx',[0.],contract())[0],reserve,ev,'ctx',contract())
            ev.assert_not_called()
    def test_publish_only_verified_pair_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            taskdir=Path(d)/'task';taskdir.mkdir()
            def reserve(i):return i+1
            reserve.task_dir=str(taskdir)
            row=qualified_task(build_tasks('ctx',[0.],contract())[0],reserve,evaluator,'ctx',contract())
            result=collect_cache([row],Path(d)/'cache','ctx',contract())
            self.assertEqual(result['qualified_queries'],1)
            with self.assertRaises(FileExistsError):collect_cache([row],Path(d)/'cache','ctx',contract())
    def test_corrupt_payload_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            taskdir=Path(d)/'task';taskdir.mkdir()
            def reserve(i):return i+1
            reserve.task_dir=str(taskdir)
            row=qualified_task(build_tasks('ctx',[0.],contract())[0],reserve,evaluator,'ctx',contract())
            p=next((taskdir/'runtime_queries').glob('*.npz'));p.write_bytes(p.read_bytes()+b'corrupt')
            with self.assertRaises(ValueError):collect_cache([row],Path(d)/'cache','ctx',contract())
    def test_each_inconsistent_full_raw_block_is_rejected_before_qualification(self):
        for key in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt'):
            with self.subTest(key=key),tempfile.TemporaryDirectory() as d:
                events=[]
                def reserve(i):events.append(i);return i+1
                reserve.task_dir=d
                def wrong(t,q,h):
                    raw,full=evaluator(t,q,h);raw[key][0,0]+=.001
                    return raw,full
                with self.assertRaisesRegex(ValueError,'cross binding'):
                    qualified_task(build_tasks('ctx',[0.],contract())[0],reserve,wrong,'ctx',contract())
                self.assertEqual(events,[0])
                self.assertFalse((Path(d)/'runtime_queries').exists())
    def test_publish_rejects_rehashed_raw_full_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            def reserve(i):return i+1
            reserve.task_dir=str(Path(d)/'task')
            row=qualified_task(build_tasks('ctx',[0.],contract())[0],reserve,evaluator,'ctx',contract())
            payload=Path(reserve.task_dir)/'runtime_queries'/(row['query_id']+'.npz')
            rewrite_raw_pair(payload,['D_tp'])
            with self.assertRaisesRegex(ValueError,'cross binding'):
                collect_cache([row],Path(d)/'cache','ctx',contract())
    def test_pinned_context_rejects_changed_contract_before_native_load(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);c=contract();basis={'matrix_sha256':INPUT_SHA,'modes':[]}
            basis['identity']=digest(basis)
            (root/'BASIS.json').write_text(json.dumps(basis))
            (root/'SCIENCE_CONTEXT.json').write_text(json.dumps({'context':{'contract':c}}))
            zero='0'*64
            (root/'BUILD_HPC.json').write_text(json.dumps({'libraries':{'libreference.so':zero,'libmoments_f90.so':zero},'source_hashes':{'reference':zero,'fortran':zero}}))
            def fake_sha(path):return INPUT_SHA if Path(path).name=='BASIS.npz' else zero
            variants=[]
            changed=copy.deepcopy(c);changed['screens']['raw_cross_relative_max']=1.;variants.append(changed)
            changed=copy.deepcopy(c);changed['runtime_reference_resolutions']=list(reversed(LEVELS));variants.append(changed)
            changed=copy.deepcopy(c);changed['energy_keV_per_u']=200.;variants.append(changed)
            changed=copy.deepcopy(c);changed['same_center_order']=24;variants.append(changed)
            # This synthetic metadata is deliberately not the archived physical bank.
            with patch('hpc_provider.sha',side_effect=fake_sha),patch('hpc_provider.source_pins',return_value={}), \
                 patch('hpc_provider.ARCHIVED_CONTRACT_SHA256',digest(c),create=True), \
                 patch('hpc_provider.ARCHIVED_BASIS_IDENTITY',basis['identity'],create=True):
                for changed in variants:
                    with self.subTest(changed=changed),self.assertRaisesRegex(ValueError,'archived.*contract'):
                        prepare_context(root,root,changed)
                result=prepare_context(root,root,c)
                self.assertEqual(result['qualification_contract'],c)
                changed=copy.deepcopy(c);changed['energy_keV_per_u']=200.
                (root/'SCIENCE_CONTEXT.json').write_text(json.dumps({'context':{'contract':changed}}))
                with self.assertRaisesRegex(ValueError,'archived.*contract'):
                    prepare_context(root,root,changed)
                (root/'SCIENCE_CONTEXT.json').write_text(json.dumps({'context':{'contract':c}}))
                changed_basis={'matrix_sha256':INPUT_SHA,'modes':[{'identity':'altered-semantic-channel'}]}
                changed_basis['identity']=digest(changed_basis)
                (root/'BASIS.json').write_text(json.dumps(changed_basis))
                with self.assertRaisesRegex(ValueError,'basis semantic'):
                    prepare_context(root,root,c)
    def test_shared_cross_validator_is_in_operator_source_identity(self):
        key='research/gap_closure_20261001/production_solver_20261001/runtime/cache_consistency.py'
        self.assertIn(key,source_pins())
    def test_serial_comm(self):
        c=SerialComm();self.assertEqual(c.Get_size(),1);self.assertEqual(c.Get_rank(),0);self.assertEqual(c.bcast(7),7)

if __name__=='__main__':unittest.main()
