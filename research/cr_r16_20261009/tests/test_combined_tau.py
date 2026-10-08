import sys,unittest,os
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from combine_source_optical import combine_bounds

class CombineTauTests(unittest.TestCase):
    def test_strict_positive_minkowski_sum(self):
        a,b=combine_bounds((F('2e-17'),F('3e-17')),F('1e-17'))
        self.assertEqual((a,b),(F('1e-17'),F('4e-17')))
    def test_sign_not_promoted_when_source_is_wide(self):
        a,b=combine_bounds((F('2e-17'),F('3e-17')),F('4e-17'))
        self.assertTrue(a<0<b)
    def test_missing_source_not_silent_zero(self):
        with self.assertRaises((TypeError,ValueError)):
            combine_bounds((F(1),F(2)),None)

if __name__=='__main__':unittest.main()

class RealDonorTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from combine_source_optical import run
        cls.value=run(Path(os.environ.get('R16_R15_ZIP','/mnt/data/BASS_CR_NCP_R15_20261008_v1.zip')),
                      Path(os.environ.get('R16_BRIDGE14_ZIP','/mnt/data/REI_XTHREAD_BRIDGE14_20261008.zip')))
    def test_source_same_sha_model_and_sign(self):
        x=self.value
        self.assertTrue(x['combined_sign_strict_positive'])
        self.assertLess(x['combined_contS_continuum_minus_native'][0],x['combined_contS_continuum_minus_native'][1])
        self.assertEqual(x['source_only_used_upper'],F('1.021773e-17'))
    def test_thomson_cgs_si_rounding_safe(self):
        self.assertLessEqual(self.value['Thomson_CT_R15_over_donor'],F(1))
    def test_source_bound_still_not_observer_tail(self):
        self.assertIn('whole history or observer tail',self.value['not_certified'])
