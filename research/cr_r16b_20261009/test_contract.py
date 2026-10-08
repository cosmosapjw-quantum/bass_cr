import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from prepare import context,validate,PIN_R16
from validated import IV,birth_transpose

class IdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        cls.stage=Path(os.environ['R16B_STAGE']);cls.ch,_,_=context(cls.stage)
        cls.cert=json.loads((cls.stage/'donor/rei_bridge13_20261008/results/final_interval/CHAIN_CERTIFICATE.json').read_text())
    def test_real_clocks_and_six_births(self):validate(self.ch.ENTRIES,self.cert)
    def test_wrong_clock(self):
        e=copy.deepcopy(self.ch.ENTRIES);e['root'][8]['t0']+=1
        with self.assertRaisesRegex(ValueError,'CLOCK_IDENTITY'):validate(e,self.cert)
    def test_wrong_birth_weight(self):
        e=copy.deepcopy(self.ch.ENTRIES);e['point'][12]['p0'][-1]*=2
        with self.assertRaisesRegex(ValueError,'BIRTH_WEIGHT'):validate(e,self.cert)
    def test_wrong_variant(self):
        e=copy.deepcopy(self.ch.ENTRIES);e['point'][31]['variant']=4
        with self.assertRaisesRegex(ValueError,'VARIANT_IDENTITY'):validate(e,self.cert)
    def test_wrong_source_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'r15/inputs').mkdir(parents=True)
            (root/'r15/inputs/REI_XTHREAD_BRIDGE13_20261008.zip').write_bytes(b'wrong source')
            with self.assertRaisesRegex(ValueError,'SOURCE_IDENTITY'):context(root)
    def test_transpose_5_to_11(self):
        lam=[IV(i) for i in range(11)]
        for n in reversed(range(5,11)):lam=birth_transpose(lam,n)
        self.assertEqual([int(v.lo) for v in lam],[0,1,2,3,4])
        with self.assertRaisesRegex(ValueError,'BIRTH_DIMENSION'):birth_transpose([IV(0)]*11,5)

if __name__=='__main__':unittest.main()
