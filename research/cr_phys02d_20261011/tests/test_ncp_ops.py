import importlib.util,json,pathlib,subprocess,sys,tempfile,unittest,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'ncp'));import launch_pulse as launcher;import collect_return;import ops
class OperationalTests(unittest.TestCase):
    def test_plan_standardlib_hold(self):
        code="import sys;sys.path.insert(0,'ncp');import launch_pulse as x;sys.argv=['launch_pulse','--plan'];x.admission=lambda:(_ for _ in ()).throw(ValueError('SYNTHETIC_HOLD_FIXTURE'));x.main();assert 'numpy' not in sys.modules and 'scipy' not in sys.modules"
        p=subprocess.run([sys.executable,'-c',code],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(p.returncode,0,p.stderr);r=json.loads(p.stdout);self.assertEqual(r['state'],'PREPARED_NOT_EXECUTED');self.assertEqual(r['admission_status'],'HOLD')
    def test_ops_exact(self):self.assertEqual(ops.sha(ROOT/'ncp/ops.py'),'8360e9f123bfc5814507728d6f946acd5109daaff2b475048d7c6ff586a4f2e7')
    def test_no_worker_bypass(self):
        p=subprocess.run([sys.executable,'ncp/launch_pulse.py','--worker','--run-dir','.'],cwd=ROOT,capture_output=True,text=True,timeout=10);self.assertNotEqual(p.returncode,0);self.assertIn('PRIVATE_COORDINATOR_CAPABILITY_REQUIRED',p.stderr)
    def test_fresh_guard_and_collector(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=pathlib.Path(tmp);run=base/'run';run.mkdir();(run/'FIRST_FAILURE.json').write_text('{"status":"FAILED"}')
            p=subprocess.run([sys.executable,'ncp/launch_pulse.py','--execute','--run-dir',str(run)],cwd=ROOT,capture_output=True,text=True,timeout=20);self.assertNotEqual(p.returncode,0)
            import shutil
            repository=base/'synthetic_repository';fixture=repository/'research/cr_phys02d_20261011'
            shutil.copytree(ROOT,fixture,ignore=shutil.ignore_patterns('__pycache__','runs','returns','FILE_MANIFEST.json'))
            for rel,item in ops.entries(json.loads((ROOT/'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json').read_text())):
                destination=repository/rel;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT.parents[1]/rel,destination)
            names=['REPORT_KO.md','START_NCP_CODEX_KO.md','tests/test_ncp_ops.py']
            synthetic={'schema':'SYNTHETIC_COLLECTOR_FIXTURE_ONLY_NO_REVIEW_DECISION','files':{n:{'bytes':(fixture/n).stat().st_size,'sha256':ops.sha(fixture/n)} for n in names}}
            (fixture/'FILE_MANIFEST.json').write_text(json.dumps(synthetic))
            a=collect_return.collect(fixture,run,base/'returns');b=collect_return.collect(fixture,run,base/'returns');self.assertNotEqual(a['path'],b['path'])
            with zipfile.ZipFile(a['path']) as z:
                self.assertIn('source_unit/REPORT_KO.md',z.namelist());self.assertIn('source_unit/START_NCP_CODEX_KO.md',z.namelist());self.assertIn('source_unit/tests/test_ncp_ops.py',z.namelist());self.assertIn('RESTORE_LAYOUT.json',z.namelist());self.assertIn('actual_run/FIRST_FAILURE.json',z.namelist());m=json.loads(z.read('RETURN_MANIFEST.json'));self.assertEqual(m['files']['actual_run/FIRST_FAILURE.json']['sha256'],ops.sha(run/'FIRST_FAILURE.json'))
                import hashlib
                self.assertEqual(set(z.namelist()),set(m['files'])|{'RETURN_MANIFEST.json'})
                self.assertEqual(a['files'],len(m['files']))
                for name,item in m['files'].items():
                    raw=z.read(name);self.assertEqual(len(raw),item['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),item['sha256'])
    def test_dependency_manifest_and_npz_schema(self):
        self.assertEqual(ops.sha(ROOT/'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'),launcher.DEP)
        verified=ops.verify(ROOT.parents[1],ROOT/'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json')
        self.assertEqual(verified['verified_entries'],259)
        import numpy as np
        pins=json.loads((ROOT/'inputs/INPUT_IDENTITIES.json').read_text())['inputs']
        for model in ('fullBED','legacy'):
            with np.load(ROOT/pins[model+'_9600_npz']['path'],allow_pickle=False) as data:
                self.assertEqual(data['time_s'].shape,(2,))
                np.testing.assert_array_equal(data['time_s'],[0.,1e10])
                self.assertEqual(data['source_vectors'].shape,(9611,2))
                np.testing.assert_array_equal(data['source_vectors'][9600],0.)
        module=launcher.import_file('closure_coherent',ROOT/pins['inherited_atomic']['path'])
        module.parent.parent_low()  # imports and pinned manifests only, no Cascade/G
        from unittest.mock import patch
        with patch.object(launcher,'SCI','synthetic_wrong_contract_hash'):
            with self.assertRaises(ValueError):launcher.admission()
    def test_injected_startup_failure_and_no_overwrite(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            run=pathlib.Path(tmp)/'new'
            args=['launch_pulse','--execute','--run-dir',str(run)]
            with patch.object(sys,'argv',args),patch.object(launcher,'admission',return_value={'synthetic_fixture':True}),patch.object(launcher,'probe',return_value={'admitted':True}),patch.object(launcher.subprocess,'Popen',side_effect=OSError('SYNTHETIC_STARTUP_FAILURE')):
                self.assertEqual(launcher.main(),1)
            receipt=json.loads((run/'ACTUAL_EXIT.json').read_text());self.assertIn('SYNTHETIC_STARTUP_FAILURE',receipt['exception']);self.assertIsNone(receipt['observed_child_exit'])
            before={p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
            with patch.object(sys,'argv',args),patch.object(launcher,'admission',return_value={'synthetic_fixture':True}),patch.object(launcher,'probe',return_value={'admitted':True}):
                with self.assertRaises(FileExistsError):launcher.main()
            self.assertEqual(before,{p.name:p.read_bytes() for p in run.iterdir() if p.is_file()})
    def test_true_root_missing_limits(self):
        h={'ancestors':[{'is_true_cgroup2_root':True,'values':{'cpu.max':None,'memory.max':None,'memory.current':None}}]}
        self.assertGreater(ops.effective_capacity({'MemTotal':32*ops.GIB,'MemAvailable':30*ops.GIB},h)['available_working_bytes'],12*ops.GIB)
        h['ancestors'][0]['is_true_cgroup2_root']=False
        with self.assertRaises(ValueError):ops.effective_capacity({'MemTotal':32*ops.GIB,'MemAvailable':30*ops.GIB},h)
if __name__=='__main__':unittest.main()

