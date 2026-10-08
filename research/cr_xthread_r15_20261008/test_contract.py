import copy,json,os,unittest,tempfile,shutil
from pathlib import Path
from run_r15 import validate_history,verify_binding,ContractError

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stage=Path(os.environ['R15_INPUT_STAGE'])
        cls.root=stage/'extracted/REI_XTHREAD_BRIDGE13_20261008/rei_bridge13_20261008'
        rows=[json.loads(v) for v in (cls.root/'inputs/BRIDGE11_NATIVE.jsonl').read_text().splitlines()]
        cls.entries={k:{r['index']:r for r in rows if r.get('kind')==k and (k!='point' or r.get('variant')==0)} for k in ('root','point','after')}
        cls.cert=json.loads((cls.root/'results/final_interval/CHAIN_CERTIFICATE.json').read_text())
        cls.cells=json.loads((cls.root/'results/final_interval/CELL_EVIDENCE.json').read_text())
    def test_authentic_history(self):
        self.assertEqual(len(validate_history(self.entries,self.cert,self.cells)),6)
        verify_binding(self.root)
    def test_clock_corruption(self):
        e=copy.deepcopy(self.entries);e['root'][3]['t0']+=1
        with self.assertRaisesRegex(ContractError,'CLOCK_GAP'):validate_history(e,self.cert,self.cells)
    def test_birth_corruption(self):
        e=copy.deepcopy(self.entries);e['point'][4]['p0'][-1]*=2
        with self.assertRaisesRegex(ContractError,'BIRTH_WEIGHT_MISMATCH'):validate_history(e,self.cert,self.cells)
    def test_variant_corruption(self):
        e=copy.deepcopy(self.entries);e['point'][31]['variant']=4
        with self.assertRaisesRegex(ContractError,'VARIANT_MISMATCH'):validate_history(e,self.cert,self.cells)
    def test_source_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'donor';shutil.copytree(self.root,root)
            p=root/'source/interval_decimal.py';p.write_bytes(p.read_bytes()+b'\n# corrupted\n')
            with self.assertRaisesRegex(ContractError,'SOURCE_HASH_MISMATCH'):verify_binding(root)

if __name__=='__main__':unittest.main()
