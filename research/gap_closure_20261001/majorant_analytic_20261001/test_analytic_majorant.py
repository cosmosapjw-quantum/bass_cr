"""Synthetic algebra and conditional integral tests; no physical operator calls."""
import numpy as np
import unittest
from scipy.integrate import quad
from analytic_majorant import cancellation_rate, compact_support_tail, inverse_square_tail


class TestAnalyticMajorant(unittest.TestCase):
    def test_fixed_selector_cancellation_matches_full_derivative(self):
        rng=np.random.default_rng(904)
        for n,m in [(3,1),(6,3),(8,7)]:
            X=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))
            S=X.conj().T@X+np.eye(n)
            X=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)); H=(X+X.conj().T)/2
            D=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)); Sd=D+D.conj().T
            J=np.eye(n)[:,:m]; G=J.conj().T@S@J
            Q=S@J@np.linalg.solve(G,J.conj().T@S)
            Qd=Sd@J@np.linalg.solve(G,J.conj().T@S)+S@J@np.linalg.solve(G,J.conj().T@Sd)-S@J@np.linalg.solve(G,J.conj().T@Sd@J)@np.linalg.solve(G,J.conj().T@S)
            A=-np.linalg.solve(S,1j*H+D)
            W=Qd+A.conj().T@Q+Q@A
            got=cancellation_rate(S,H,D,J)
            np.testing.assert_allclose(got['W'],W,atol=4e-13,rtol=1e-12)
            L=np.linalg.cholesky(S); Linv=np.linalg.solve(L,np.eye(n))
            ref=np.max(np.abs(np.linalg.eigvalsh(Linv@W@Linv.conj().T)))
            assert got['rho_offdiagonal']==ref or abs(got['rho_offdiagonal']-ref)<3e-13+1e-12*abs(ref)
    
    
    def test_commuting_large_isolated_energy_and_monopole_cancel_exactly(self):
        S=np.eye(3); H=np.diag([1e12,-1e12,4e12])+1e8*S
        got=cancellation_rate(S,H,np.zeros((3,3)),np.eye(3)[:,:1])
        assert got['rho_offdiagonal']==0.0
        assert np.linalg.norm(got['W'])==0.0
    
    
    def test_noncommuting_isolated_residual_creates_constant_floor(self):
        eps=1e-5; S=np.eye(2); J=S[:,:1]; D=np.zeros((2,2))
        for radius in (10,100,10000):
            H=np.diag([-0.5,0.1])+np.array([[0,eps+radius**-2],[eps+radius**-2,0]])
            got=cancellation_rate(S,H,D,J)
            assert got['rho_offdiagonal']==eps+radius**-2 or abs(got['rho_offdiagonal']-(eps+radius**-2))<1e-14
    
    
    def test_coulomb_range_bound_for_nontrivial_selected_span(self):
        rng=np.random.default_rng(301)
        a=64.; charge=1.; n=13
        X=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))
        U,_=np.linalg.qr(X); J=U[:,:5]; S=np.eye(n)
        for radius in (128.01,160.,1000.):
            values=np.linspace(-charge/(radius-a),-charge/(radius+a),n)
            H=np.diag(values)
            rho=cancellation_rate(S,H,np.zeros_like(H),J)['rho_offdiagonal']
            bound=charge*a/(radius*radius-a*a)
            self.assertLessEqual(rho,bound*(1+1e-12))

    def test_archived_audit_integrates_known_polynomials(self):
        from audit_saved_radial import integrate,global_poly
        from fractions import Fraction as F
        from decimal import Decimal,localcontext
        # x^2 on [0,2]: mass 8/3; /x integral 2; /x^2 integral 2.
        with localcontext() as ctx:
            ctx.prec=80
            p=[F(0),F(0),F(1)]
            self.assertEqual(integrate(p,F(0),F(2)),Decimal(8)/3)
            self.assertEqual(integrate(p,F(0),F(2),-1),Decimal(2))
            self.assertEqual(integrate(p,F(0),F(2),-2),Decimal(2))
            self.assertEqual(global_poly([1.,2.,3.],F(1),F(2)),[F(3,4),F(-1,2),F(3,4)])

    def test_non_spd_is_rejected_without_shift(self):
        with self.assertRaises(np.linalg.LinAlgError):
            cancellation_rate(np.diag([1.,-1.]),np.eye(2),np.zeros((2,2)),np.eye(2)[:,:1])
    
    
    def test_compact_support_tail_integral_against_quadrature(self):
        for b in [0.,2.,64.,80.]:
            self._check_support_integral(b)
    
    def _check_support_integral(self,b):
        a=64.; Z=160.; v=2.; charge=1.; hbar=1.
        got=compact_support_tail(Z,b,a,v,charge,hbar)
        expected=quad(lambda z:charge*a/(hbar*v*(z*z+b*b-a*a)),Z,np.inf,epsabs=1e-12)[0]
        assert got==expected or abs(got-expected)<1e-13+3e-13*abs(expected)
    
    
    def test_support_tail_rejects_unproven_overlap_region(self):
        with self.assertRaises(ValueError): compact_support_tail(32,2,64,2)
    
    
    def test_inverse_square_tail_stable_at_large_radius(self):
        for b in [0.,2.,1e-9]:
            self._check_inverse_square(b)
    
    def _check_inverse_square(self,b):
        Z=1e20; got=inverse_square_tail(3,Z,b,2)
        assert got==3/(2*Z) or abs(got-3/(2*Z))<1e-15*3/(2*Z)

if __name__ == "__main__":
    unittest.main()
