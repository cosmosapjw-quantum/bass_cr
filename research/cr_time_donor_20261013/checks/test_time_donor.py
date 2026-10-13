import sys, unittest, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from time_donor import phi2_rate, saturated_convolution
class Kernels(unittest.TestCase):
    def test_zero_feedback_limit(self):
        self.assertAlmostEqual(phi2_rate(0,2),2)
    def test_small_feedback(self):
        self.assertAlmostEqual(phi2_rate(1e-18,2),2)
    def test_nonzero_feedback(self):
        self.assertAlmostEqual(phi2_rate(.3,2),(math.expm1(.6)-.6)/.09)
    def test_positive_saturated_birth(self):
        self.assertGreater(saturated_convolution(.1,.4,2),0)
    def test_zero_birth(self):
        self.assertEqual(saturated_convolution(.1,0,2),0)
    def test_zero_feedback_birth(self):
        self.assertAlmostEqual(saturated_convolution(0,.4,2),2+math.expm1(-.8)/.4)
    def test_small_time_order(self):
        a=saturated_convolution(.2,.3,1e-4); b=saturated_convolution(.2,.3,5e-5)
        self.assertAlmostEqual(a/b,4,places=3)
    def test_negative_rejected(self):
        with self.assertRaises(ValueError): phi2_rate(-1,2)
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError): saturated_convolution(0,1,float('nan'))
if __name__=='__main__':unittest.main()
