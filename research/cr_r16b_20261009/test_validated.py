import unittest
from validated import IV,D,backward_step,Aff

class DirectedTests(unittest.TestCase):
    def test_signed_negative_offdiagonal_not_absolute(self):
        A=[[IV(0),IV('-0.3')],[IV(0),IV(0)]]
        left,tube=backward_step(A,[IV(1),IV(0)],[IV(0),IV(0)],D(1))
        self.assertTrue(left[0].contains(1))
        self.assertTrue(left[1].contains(D('-.15')))
        self.assertLessEqual(left[1].hi,0)
    def test_nonzero_terminal_incoming_not_reset(self):
        left,_=backward_step([[IV(0)]],[IV(2)],[IV(4)],D(1))
        self.assertEqual(left[0].data(),['6','6'])
    def test_shared_birth_noise_cancels(self):
        a=Aff(0,{'theta_birth_1':IV(2)})
        self.assertEqual((a+a.scale(-1)).box().lo,D(0))
        self.assertEqual((a+a.scale(-1)).box().hi,D(0))
        self.assertEqual(a.box().data(),['-2','2'])
    def test_loss_of_correlation_counterexample(self):
        a=Aff(0,{'theta_birth_1':IV(2)})
        wrong=Aff(0,{'theta_birth_regenerated':IV(-2)})
        self.assertEqual((a+wrong).box().data(),['-4','4'])
        self.assertEqual((a+a.scale(-1)).box().hi,D(0))
    def test_compression_preserves_birth_and_relaxes_only_other_noise(self):
        a=Aff(1,{'theta_birth_1':IV(2),'other_1':IV(3),'other_2':IV(-4)})
        b=a.compress('compressed_test')
        self.assertEqual(b.noise['theta_birth_1'].data(),['2','2'])
        self.assertLessEqual(b.box().lo,a.box().lo)
        self.assertGreaterEqual(b.box().hi,a.box().hi)

if __name__=='__main__':unittest.main()
