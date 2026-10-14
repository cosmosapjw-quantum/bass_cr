import pathlib,sys,unittest,tempfile,json,subprocess,zipfile,hashlib
from unittest.mock import patch
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'ncp'))
import launch_residence as L
import run_and_collect as W
import collect_return as C
class OpsTests(unittest.TestCase):
    def test_stdlib_plan_HOLD_no_numerics(self):
        command=[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(P/'ncp'))+");import launch_residence as m;sys.argv=['launch','--plan'];code=m.main();assert 'numpy' not in sys.modules and 'scipy' not in sys.modules;raise SystemExit(code)"]
        r=subprocess.run(command,capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout)['admission_status'],'HOLD')
    def test_inherited_bundle_not_authority(self):
        with tempfile.TemporaryDirectory() as d:
            repo=pathlib.Path(d);study=repo/'research/f';study.mkdir(parents=True)
            (repo/'BUNDLE_MANIFEST.json').write_text(json.dumps({'schema':'cr-phys02e-bundle.v1'}))
            with patch.object(L,'STUDY',study),patch.object(L,'REPO',repo):
                with self.assertRaisesRegex(ValueError,'CURRENT_F'):L.frozen_payload()
    def test_wrapper_execute_failure_and_collection_failure(self):
        for execute_code,collect_fails in [(1,False),(0,True)]:
            with tempfile.TemporaryDirectory() as d:
                run=pathlib.Path(d)/'run';out=pathlib.Path(d)/'out';calls=[]
                def execute(command,check):calls.append('execute');run.mkdir();return subprocess.CompletedProcess(command,execute_code)
                def collect(study,r,o):
                    calls.append('collect')
                    if collect_fails:raise ValueError('fixture collection failure')
                    o.mkdir();z=o/'fixture.zip';z.write_bytes(b'fixture');return {'path':str(z),'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'bytes':7}
                code=W.run_and_collect(run,out,executor=execute,collector=collect)
                self.assertNotEqual(code,0);self.assertEqual(calls,['execute','collect'])
                receipt=json.loads((run/'WRAPPER_ACTUAL_EXIT.json').read_text());self.assertEqual(receipt['execute_exit'],execute_code)
                if not collect_fails:
                    family=json.loads((out/'RETURN_FAMILY_MANIFEST.json').read_text())
                    self.assertIn('WRAPPER_ACTUAL_EXIT.json',family['files']);self.assertIn('WRAPPER_COLLECTION_EXIT.json',family['files'])
    def test_collector_exact_fixture_membership(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);repo=root/'repo';study=repo/'research/f';study.mkdir(parents=True);(study/'inputs').mkdir();(study/'state').mkdir()
            dep=repo/'dep.txt';dep.write_text('dependency');info={'bytes':dep.stat().st_size,'sha256':C.sha(dep)}
            manifest=study/'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json';manifest.write_text(json.dumps({'files':{'dep.txt':info}}))
            (study/'inputs/INPUT_IDENTITIES.json').write_text(json.dumps({'files':{'fixture':{'path':'dep.txt',**info}}}))
            freeze=study/'FILE_MANIFEST.json';freeze.write_text('{}');run=root/'run';run.mkdir();(run/'ACTUAL_EXIT.json').write_text('{"actual_exit":1}');out=root/'out'
            with patch.object(C,'DEP_HASH',C.sha(manifest)),patch.object(C,'verify',return_value={'fixture':True}),patch.object(L,'frozen_payload',return_value={'path':str(freeze)}):
                result=C.collect(study,run,out)
            with zipfile.ZipFile(result['path']) as z:
                m=json.loads(z.read('RETURN_MANIFEST.json'));self.assertEqual(set(z.namelist()),set(m['files'])|{'RETURN_MANIFEST.json'})
                for name,item in m['files'].items():
                    raw=z.read(name);self.assertEqual(len(raw),item['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),item['sha256'])
                self.assertIn('dependency_payload/dep.txt',m['files']);self.assertIn('dependencies/fixture/dep.txt',m['files']);self.assertIn('actual_run/ACTUAL_EXIT.json',m['files'])
if __name__=='__main__':unittest.main()
