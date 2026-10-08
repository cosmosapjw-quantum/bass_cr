import unittest
from fractions import Fraction as F
from exact_reference import I, log_enclosure, sqrt_enclosure, repair_coefficients, local_value, gram_matrix, isolated_matrices, projector_bridge, block_certificate

class ExactReferenceTests(unittest.TestCase):
    def test_interval_arithmetic_contains_exact(self):
        a=I(F(1,3),F(2,3)); b=I(-2,3)
        self.assertTrue((a*b).contains(F(-4,3)))
        self.assertTrue((a*b).contains(2))
        self.assertTrue((a-b).contains(F(8,3)))
        self.assertTrue((I(1)/I(3)).contains(F(1,3)))
        with self.assertRaises(ValueError): I(1)/b
    def test_log_identity_and_independent_rational_bracket(self):
        self.assertEqual(log_enclosure(F(1)).lo,0)
        # 2 sum_{k>=0} (1/3)^(2k+1)/(2k+1); first two terms and geometric tail.
        x=log_enclosure(F(2)); lower=F(2,3)+F(2,81)
        upper=lower+2*F(1,3)**5/(5*(1-F(1,9)))
        self.assertGreater(x.lo,lower); self.assertLess(x.hi,upper)
        self.assertTrue((x+log_enclosure(F(1,2))).contains(0))
        self.assertLess(x.hi-x.lo,F(1,10**70))
        with self.assertRaises(ValueError): log_enclosure(0)
    def test_sqrt_bounds_are_exact(self):
        x=sqrt_enclosure(F(2)); self.assertLessEqual(x.lo*x.lo,2); self.assertGreaterEqual(x.hi*x.hi,2)
        self.assertEqual(sqrt_enclosure(F(9,4)).lo,F(3,2))
        with self.assertRaises(ValueError): sqrt_enclosure(-1)
    def test_repair_conforming_endpoints_and_idempotent(self):
        p=[[[F(1),F(2),F(1)],[F(5),F(1),F(-2)]]]
        q=repair_coefficients(p)
        self.assertEqual(local_value(q[0][0],0),0)
        self.assertEqual(local_value(q[0][-1],1),0)
        self.assertEqual(local_value(q[0][0],1),local_value(q[0][1],0))
        self.assertEqual(local_value(q[0][0],1),F(9,2))
        self.assertEqual(repair_coefficients(q),q)
    def test_exact_mass_and_weak_hamiltonian(self):
        # u=r(1-r), exact Dirichlet on [0,1]: mass 1/30, kinetic 1/6,
        # Coulomb -1/12; l=1 centrifugal adds 1/3.
        p=[[[F(0),F(1),F(-1)]]]; edges=[F(0),F(1)]
        S,H=isolated_matrices(p,edges,[0])
        self.assertEqual(S[0][0],F(1,30)); self.assertTrue(H[0][0].contains(F(1,12)))
        S,H=isolated_matrices(p,edges,[1]); self.assertTrue(H[0][0].contains(F(5,12)))
    def test_angular_orthogonality_is_exact(self):
        p=[[[F(0),F(1),F(-1)]],[[F(0),F(1),F(-1)]]]
        S,H=isolated_matrices(p,[F(0),F(1)],[0,1])
        self.assertEqual(S[0][1],0); self.assertEqual(H[0][1].lo,0); self.assertEqual(H[0][1].hi,0)
    def test_same_span_mapping_zero_despite_column_rescaling(self):
        p=[[[F(0),F(1),F(-1)]]]
        result=projector_bridge(p,p,[F(0),F(1)],[0],[0])
        self.assertEqual(result['eta_projector_upper'],0)
    def test_spectral_gap_certificate_and_obstruction(self):
        S=[[F(1),F(0)],[F(0),F(1)]]; H=[[I(-1),I(F(1,100))],[I(F(1,100)),I(2)]]
        result=block_certificate(S,H,[0],[1])
        self.assertEqual(result['a_lower'],1); self.assertEqual(result['d_lower'],2)
        self.assertGreaterEqual(result['r_upper'],F(1,100))
        self.assertLessEqual(result['delta_selector_upper'],F(1,299))
        with self.assertRaises(ValueError): block_certificate(S,[[I(-1),I(0)],[I(0),I(-2)]],[0],[1])
    def test_s_orthogonal_complement_schur(self):
        S=[[F(1),F(1,10)],[F(1,10),F(1)]]
        # H obtained from diag(-1,2) in an S-orthogonal basis; H_BA = S_BA H_AA.
        H=[[I(-1),I(F(-1,10))],[I(F(-1,10)),I(F(197,100))]]
        result=block_certificate(S,H,[0],[1])
        self.assertEqual(result['r_upper'],0)
        self.assertEqual(result['a_lower'],1); self.assertEqual(result['d_lower'],2)

if __name__=='__main__':unittest.main()
