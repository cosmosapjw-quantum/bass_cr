import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import shutil
import unittest
import zipfile
from unittest.mock import patch
STUDY=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('frontier_ops',STUDY/'ncp/postprocess_frontier.py');ops=importlib.util.module_from_spec(spec);spec.loader.exec_module(ops)

def item(raw):return {'bytes':len(raw),'sha256':ops.digest(raw)}

def corruptible_family(root,extra=False):
    with zipfile.ZipFile(root/'f.zip','x') as z:
        raw=b'{}';z.writestr('a.json',raw)
        z.writestr('RETURN_MANIFEST.json',json.dumps({'files':{'a.json':item(raw)}}))
        if extra:z.writestr('unexpected.json',b'{}')
    ops.write(root/'RETURN_FAMILY_MANIFEST.json',{'files':{'f.zip':item((root/'f.zip').read_bytes())}})

class FrontierOpsTests(unittest.TestCase):
    def test_stdlib_plan_waiting_and_no_numpy(self):
        code="import runpy,sys;sys.argv=['postprocess_frontier.py','--plan'];runpy.run_path(%r,run_name='__main__')"%str(STUDY/'ncp/postprocess_frontier.py')
        r=subprocess.run([sys.executable,'-S','-c',code],capture_output=True,text=True,timeout=15)
        self.assertEqual(r.returncode,0,r.stderr);row=json.loads(r.stdout)
        self.assertEqual(row['status'],'WAITING_FOR_F_ACTUAL_RETURN');self.assertEqual(row['actual_postprocess_reservations'],0)
    def test_corrupt_family_and_zip_membership_before_load(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);corruptible_family(root,extra=True)
            with self.assertRaisesRegex(ValueError,'ZIP_MEMBERSHIP'):ops.verify_family(root)
            (root/'unexpected').write_text('x')
            with self.assertRaisesRegex(ValueError,'F_FAMILY_MEMBERSHIP'):ops.verify_family(root)
    def test_corrupt_family_hash(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);corruptible_family(root);(root/'f.zip').write_bytes(b'bad')
            with self.assertRaisesRegex(ValueError,'IDENTITY_MISMATCH'):ops.verify_family(root)
    def test_global_create_only_reservation(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);out=root/'out';out.mkdir();ledger=root/'ledger'
            ops.reserve(out,ledger,'f'*64)
            other=root/'other';other.mkdir()
            with self.assertRaises(FileExistsError):ops.reserve(other,ledger,'f'*64)
    def test_owned_child_first_failure_and_deadline_receipts(self):
        for command,timeout,expected in [([sys.executable,'-c',"import sys;print('raw first failure');print('raw stderr',file=sys.stderr);sys.exit(7)"],5,7),([sys.executable,'-c','import time;time.sleep(5)'],.15,124)]:
            with tempfile.TemporaryDirectory() as d:
                root=pathlib.Path(d);family=root/'family';family.mkdir();out=root/'out'
                fake={'source_admission':{'status':'PREPARED_SOURCE_ADMITTED'},'F_identity':{'zip_sha256':'e'*64}}
                with patch.object(ops,'plan',return_value=fake):code=ops.coordinate(out,root/'ledger',family,timeout_s=timeout,command=command)
                self.assertEqual(code,expected);row=json.loads((out/'ACTUAL_EXIT.json').read_text());self.assertEqual(row['actual_exit'],expected)
                self.assertFalse(row['automatic_retry']);self.assertTrue((out/'stdout.log').is_file());self.assertTrue((out/'stderr.log').is_file())
                evidence=STUDY/'evidence/ncp_validation'/('SYNTHETIC_CHILD_FAILURE' if expected==7 else 'SYNTHETIC_CHILD_DEADLINE')
                shutil.copytree(out,evidence)
                shutil.copytree(root/'ledger',evidence/'ledger')
                manifest=json.loads((out/'RETURN_MANIFEST.json').read_text())
                for name,pin in manifest['files'].items():ops.identity((out/name).read_bytes(),pin,name)
                with self.assertRaises(ValueError):ops.coordinate(out,root/'ledger',family)
    def test_admission_failure_preserved_without_child(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);family=root/'family';family.mkdir();out=root/'out'
            with patch.object(ops,'plan',side_effect=ValueError('concrete admission failure')):self.assertEqual(ops.coordinate(out,root/'ledger',family),1)
            row=json.loads((out/'ACTUAL_EXIT.json').read_text());self.assertIsNone(row['observed_child_exit']);self.assertIn('concrete admission failure',(out/'stderr.log').read_text())
    def test_finalized_own_source_admission_mutations(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);study=root/'research/cr_phys02g_20261011';study.mkdir(parents=True)
            for name in ops.PINS:
                path=study/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((STUDY/name).read_bytes())
            for name in ops.REQUIRED_CODE:
                path=study/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('# synthetic source fixture\n')
            reviewed={name:item((study/name).read_bytes()) for name in list(ops.PINS)+ops.REQUIRED_CODE}
            review={'decision':'PASS_SCOPED','reviewer_role':'INDEPENDENT_ASTRA','independent_of_implementation':True,'independent_of_candidate_design':True,'independent_of_acceptance':True,
                'scientific_contract_sha256':ops.PINS['state/SCIENTIFIC_CONTRACT.json'],'validation_contract_sha256':ops.PINS['state/VALIDATION_CONTRACT.json'],
                'ncp_contract_sha256':ops.PINS['ncp/NCP_EXECUTION_CONTRACT.json'],'input_manifest_sha256':ops.PINS['inputs/INPUT_IDENTITIES.json'],
                'dependency_manifest_sha256':ops.PINS['inputs/F_BACKUP_DEPENDENCY.json'],'reviewed_files':reviewed}
            rp=study/'review/INDEPENDENT_DECISION.json';rp.parent.mkdir();ops.write(rp,review)
            task={'id':ops.TASK,'status':'WAITING_FOR_F_ACTUAL_RETURN','preparation_status':'PASS_SCOPED','consumed':False,'max_postprocess_runs':1,'total_wall_s':90,
                'physical_G_calls':0,'linear_solve_calls':0,'pulse_calls':0,'expm_calls':0,'independent_review':{'path':'review/INDEPENDENT_DECISION.json','sha256':ops.digest(rp.read_bytes())}}
            dag={'schema':'cr-phys02g-next-dag.v1','scientific_contract_sha256':ops.PINS['state/SCIENTIFIC_CONTRACT.json'],'tasks':[task]}
            dp=study/'state/NEXT_DAG.json';ops.write(dp,dag)
            def rebind_manifest():
                manifest={'schema':'cr-phys02g-file-manifest.v1','path_basis':'repository-root','files':{p.relative_to(root).as_posix():item(p.read_bytes()) for p in study.rglob('*') if p.is_file() and p.name!='FILE_MANIFEST.json'}}
                (study/'FILE_MANIFEST.json').write_text(json.dumps(manifest))
            rebind_manifest();self.assertEqual(ops.own_admission(study)['status'],'PREPARED_SOURCE_ADMITTED')
            task['independent_review']['sha256']='0'*64;dp.write_text(json.dumps(dag));rebind_manifest()
            with self.assertRaisesRegex(ValueError,'FINAL_REVIEW_BINDING'):ops.own_admission(study)
            task['independent_review']['sha256']=ops.digest(rp.read_bytes());dp.write_text(json.dumps(dag));rebind_manifest()
            path=study/'src/frontier.py';path.write_text('# mutated unreviewed source\n');rebind_manifest()
            with self.assertRaisesRegex(ValueError,'IDENTITY_MISMATCH'):ops.own_admission(study)
if __name__=='__main__':unittest.main()
