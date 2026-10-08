from pathlib import Path
import sys,unittest,os
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from global_fubini import compute,verify_native_history,exp_moment
from fractions import Fraction as F
from zipfile import ZipFile

BASE=Path(os.environ.get('R16_PARENT_STAGE',Path(__file__).resolve().parents[1]/'parent'))

class FubiniTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=compute(BASE)
    def test_real_32_cell_nonempty(self):
        self.assertEqual(self.result['panels'],64+31*16)
        self.assertTrue(self.result['global_strict_sign_positive'])
    def test_global_and_old_interval_overlap(self):
        o=self.result['old_interval'];i=self.result['interval']
        self.assertLessEqual(max(o[0],i[0]),min(o[1],i[1]))
    def test_narrowing_not_asserted_without_signed_jacobian(self):
        o=self.result['old_interval'];i=self.result['interval']
        self.assertLess(abs(float(i[0]-o[0]))/float(o[0]),1e-20)
        self.assertLess(abs(float(i[1]-o[1]))/float(o[1]),1e-20)
    def test_separate_future_weight_is_positive(self):
        self.assertGreater(self.result['global_future_direct'][0],0)
        self.assertGreater(self.result['future_feedback'],0)
    def test_native_gas_and_carried_cohorts_bit_equal(self):
        self.assertEqual(self.result['native']['birth_indices'],[4,8,12,16,20,24])
    def test_corrupt_clock_link_rejected(self):
        with ZipFile(BASE/'inputs/REI_XTHREAD_BRIDGE13_20261008.zip') as z:
            b=z.read('rei_bridge13_20261008/inputs/BRIDGE11_NATIVE.jsonl').decode().splitlines()
        import json
        rec=[json.loads(s) for s in b]
        for r in rec:
            if r.get('kind')=='root' and r.get('index')==1:
                r['t0']+=1;break
        with self.assertRaisesRegex(ValueError,'NATIVE_CLOCK_MISMATCH'):
            verify_native_history('\n'.join(json.dumps(r) for r in rec))
    def test_exp_moment_exact_simple(self):
        self.assertEqual(exp_moment(F(0),5),F(1))

if __name__=='__main__':unittest.main()
