"""Small synthetic moving-frame checks; no B0 data or propagation."""
from pathlib import Path
import sys
import unittest
import numpy as np
from numpy.testing import assert_allclose
from scipy.linalg import eigh

from projector_rate import cancellation_rate, state_rate

G01 = Path(__file__).resolve().parents[2] / 'rho_integration_theorem_20261001'
sys.path.insert(0, str(G01))
from rho_theorem import rate_forms


def fixture(t=0.2):
    b0 = np.array([[2,.25j,0,0], [0,1,.125,0], [0,0,1.5,-.2j], [0,0,0,.75]], complex)
    bd = np.array([[.1,.2,0,.03j], [0,-.05,.04j,0], [0,0,.07,.03], [0,0,0,.02]], complex)
    b = b0+t*bd
    hp = np.array([[.3,.1j,.2,0], [-.1j,-.5,.07,.08], [.2,.07,.2,-.1j], [0,.08,.1j,.8]], complex)
    j = np.array([[1,0], [.1j,1], [.2,.15j], [0,.1]], complex)
    jd = np.array([[0,.03], [.02,0], [.05j,0], [0,-.04]], complex)
    return b, bd, hp, j, jd


def forms(t=.2, moving=False):
    b,bd,hp,j,jd = fixture(t)
    return b.conj().T@b, b.conj().T@hp@b, b.conj().T@bd, b.conj().T@bd+bd.conj().T@b, j+t*jd if moving else j, jd


class ProjectorRateTests(unittest.TestCase):
    def test_fixed_selector_exact_relation_to_existing_G01(self):
        s,h,d,sd,j,_ = forms()
        new = cancellation_rate(s,h,d,sd,j,hbar=.7)
        old = rate_forms(s,h/.7,d,sd,j)
        assert_allclose(new.W, old.W, atol=4e-15, rtol=2e-13)
        self.assertAlmostEqual(new.rho, old.rho, places=13)
        assert_allclose(new.X.conj().T@s@new.Y, 0, atol=4e-16)

    def test_spectrum_is_paired_singular_values_without_factor_two(self):
        s,h,d,sd,j,_ = forms()
        f = cancellation_rate(s,h,d,sd,j[:,:1],hbar=1)
        singular = np.linalg.svd(f.E,compute_uv=False)
        values = eigh(f.W,s,eigvals_only=True)
        assert_allclose(values,[-singular[0],0,0,singular[0]],atol=3e-15)
        self.assertAlmostEqual(f.rho,singular[0],places=14)

    def test_hamiltonian_connection_cancellation_before_norm(self):
        s,_,_,_,j,_ = forms()
        # Exactly Hermitian binary data: do not amplify a rounded B†hB
        # antisymmetric defect and then falsely declare Sdot=0 compatible.
        h = np.array([[1,2j,3,0],[-2j,-4,0,1],[3,0,2,-1j],[0,1,1j,3]],complex)*2**30
        f = cancellation_rate(s,h,-1j*h,np.zeros_like(s),j,hbar=1)
        assert_allclose(f.E,0,atol=0,rtol=0)
        self.assertEqual(f.rho,0)
        self.assertGreater(np.linalg.norm(h),1e8)

    def test_schur_complement_cancels_large_selected_energy(self):
        b=np.array([[2,1],[0,2]],complex)
        hp=np.array([[2**30,1],[1,-2**28]],complex)
        z=np.zeros((2,2),complex)
        f=cancellation_rate(b.conj().T@b,b.conj().T@hp@b,z,z,[[1],[0]],hbar=1,K=[[0],[1]])
        assert_allclose(f.E,[[1j]],atol=0,rtol=0)
        self.assertEqual(f.rho,1)

    def test_state_aware_bound_is_sharp_at_fixed_population(self):
        z=np.zeros((2,2),complex)
        f=cancellation_rate(np.eye(2),z,[[0,-3],[3,0]],z,[[1],[0]],hbar=1)
        for a,b in ((3,4),(1,1),(0,2),(2,0)):
            c=f.X[:,0]*a+f.Y[:,0]*b
            result=state_rate(f,c)
            self.assertAlmostEqual(result.population,a*a,places=14)
            self.assertAlmostEqual(result.norm,a*a+b*b,places=14)
            self.assertAlmostEqual(result.rate,2*a*b*3,places=14)
            self.assertAlmostEqual(result.bound,abs(result.rate),places=14)
        self.assertEqual(state_rate(f,[1,1]).bound,2*f.rho)

    def test_complement_choice_does_not_change_rho(self):
        s,h,d,sd,j,_=forms()
        first=cancellation_rate(s,h,d,sd,j,hbar=1)
        k=first.Y@np.array([[1,.2j],[.1,1.3]])+j@np.array([[.2,.1],[.3j,-.1]])
        second=cancellation_rate(s,h,d,sd,j,hbar=1,K=k)
        self.assertAlmostEqual(first.rho,second.rho,places=13)
        assert_allclose(first.W,second.W,atol=3e-15)

    def test_time_dependent_basis_change_requires_Jdot_and_is_covariant(self):
        s,h,d,sd,j,jd=forms(moving=True)
        t=np.array([[1,.1j,0,0],[0,1.2,.1,0],[0,0,.8,.15j],[0,0,0,1.1]],complex)
        td=np.array([[.1,0,0,.02],[0,-.07,0,0],[0,0,.04,0],[0,0,0,.03]],complex)
        change=lambda x:t.conj().T@x@t
        jp=np.linalg.solve(t,j)
        jdp=np.linalg.solve(t,jd-td@jp)
        dp=change(d)+t.conj().T@s@td
        sp=change(s)
        sdp=change(sd)+td.conj().T@s@t+t.conj().T@s@td
        a=cancellation_rate(s,h,d,sd,j,hbar=.7,Jdot=jd)
        b=cancellation_rate(sp,change(h),dp,sdp,jp,hbar=.7,Jdot=jdp)
        self.assertAlmostEqual(a.rho,b.rho,places=13)
        assert_allclose(b.W,change(a.W),atol=5e-15)
        wrong=cancellation_rate(sp,change(h),dp,sdp,jp,hbar=.7)
        self.assertGreater(np.linalg.norm(wrong.W-b.W),.01)

    def test_moving_selector_independent_centered_difference(self):
        s,h,d,sd,j,jd=forms(moving=True)
        f=cancellation_rate(s,h,d,sd,j,hbar=.7,Jdot=jd)
        a=np.linalg.solve(s,-1j*h/.7-d)
        errors=[]
        for step in (.04,.02,.01):
            q=[]
            for tt in (.2-step,.2+step):
                st,ht,dt,sdt,jt,jdt=forms(tt,moving=True)
                q.append(cancellation_rate(st,ht,dt,sdt,jt,hbar=.7,Jdot=jdt).Q)
            w=(q[1]-q[0])/(2*step)+a.conj().T@f.Q+f.Q@a
            errors.append(np.linalg.norm(w-f.W))
        self.assertTrue(all(3.9<x/y<4.1 for x,y in zip(errors,errors[1:])),errors)

    def test_full_span_and_zero_norm(self):
        s,h,d,sd,_,_=forms()
        f=cancellation_rate(s,h,d,sd,np.eye(4),hbar=1)
        self.assertEqual(f.E.shape,(0,4))
        self.assertEqual(f.rho,0)
        self.assertEqual(state_rate(f,np.zeros(4)).bound,0)
        assert_allclose(f.W,0,atol=0)

    def test_invalid_input_is_rejected_without_repair(self):
        s,h,d,sd,j,_=forms()
        with self.assertRaisesRegex(ValueError,'compatibility'):
            cancellation_rate(s,h,d,sd+np.eye(4),j,hbar=1)
        with self.assertRaises(ValueError):
            cancellation_rate(s,h,d,sd,j,hbar=0)
        with self.assertRaises(np.linalg.LinAlgError):
            cancellation_rate(np.diag([1,1,1,0]),h,d,sd,j,hbar=1)
        with self.assertRaises(np.linalg.LinAlgError):
            cancellation_rate(s,h,d,sd,j,hbar=1,K=j)

    def test_exact_fraction_replay(self):
        from exact_replay import replay
        result=replay()
        self.assertGreaterEqual(result['exact_assertions'],30)


if __name__=='__main__':unittest.main(verbosity=2)
