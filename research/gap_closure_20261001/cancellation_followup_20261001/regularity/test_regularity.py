import unittest
from fractions import Fraction as F
from regularity import mode_traces,broken_difference_squared,finite_residual,real_metric_defect,matmul,transpose

class ExactRegularityTests(unittest.TestCase):
    def test_nonzero_small_hat_has_distributional_second_derivative(self):
        eps=F(1,10**20)
        traces=mode_traces([[F(0),eps],[eps,-eps]],[F(0),F(1),F(2)])
        self.assertEqual(traces['nonzero_value_jumps'],0)
        self.assertEqual([x['derivative_jump'] for x in traces['shells']],[-2*eps,eps])
        d=broken_difference_squared([[0,0],[0,0]],[[0,eps],[eps,-eps]],[0,1,2])
        self.assertEqual(d['L2_radial_squared'],F(2,3)*eps**2)
        self.assertEqual(d['cellwise_radial_derivative_squared'],2*eps**2)
    def test_smooth_H1_small_strong_residual_large(self):
        # f_k=k^-3 sin(k^2 x)/sqrt(pi) on the 2pi circle; alpha=1.
        for k in [2,10,100]:
            H1_squared=F(1,k**6)+F(1,k**2);Hf_squared=F(k*k)
            self.assertLess(H1_squared,F(2,k*k));self.assertEqual(Hf_squared,k*k)
        self.assertLess(F(1,100**6)+F(1,100**2),F(1,10**6)+F(1,10**2))
    def test_nonorthogonal_exact_intertwiner(self):
        S1=[[F(4),F(0)],[F(0),F(9)]];T=[[F(1,2),0],[0,F(1,3)]]
        L0=[[0,F(-1)],[F(1),0]];L1=[[0,F(-3,2)],[F(2,3),0]];zero=[[F(0),F(0)],[F(0),F(0)]]
        self.assertEqual(real_metric_defect(S1,zero,L1),zero)
        self.assertEqual(finite_residual(L1,T,L0,zero),zero)
        self.assertEqual(matmul(transpose(T),matmul(S1,T)),[[1,0],[0,1]])
    def test_time_dependent_map_sign(self):
        self.assertEqual(finite_residual([[F(2)]],[[F(3)]],[[F(1)]],[[F(4)]]),[[F(-1)]])
    def test_metric_defect_cannot_be_omitted(self):
        for t in [F(0),F(1,3),F(2)]:
            S=[[1+t]];G=real_metric_defect(S,[[F(1)]],[[F(0)]])
            self.assertEqual(G,[[1]])
            # d ||c||_S^2/dt=1 for c=1; setting defect to zero gives a false invariant.
            self.assertEqual(G[0][0]/(2*S[0][0]),1/(2*(1+t)))
    def test_nonconforming_value_jump_is_detected(self):
        t=mode_traces([[0,F(1)],[F(1)+F(1,10**30),F(-1)]],[0,1,2])
        self.assertEqual(t['nonzero_value_jumps'],2)
        self.assertEqual(t['max_abs_value_jump'],F(1,10**30))
    def test_invalid_partition_rejected(self):
        with self.assertRaises(ValueError):mode_traces([[0,1]],[0,0])
if __name__=='__main__':unittest.main()
