"""Conditional projector repair checks; never changes project J or basis."""
from fractions import Fraction as F
import unittest
import numpy as np
from reference_selector_certificate import projector_distance_enclosure


class TestReferenceSelectorRepair(unittest.TestCase):
    def test_exact_residual_gap_enclosure(self):
        out=projector_distance_enclosure(F(1,8),F(1,2000),F(1,10**12))
        self.assertEqual(out,F(1,10**12)/(F(1,8)+F(1,2000)))
        self.assertEqual(projector_distance_enclosure(F(1),F(1),F(9)),F(1))
        with self.assertRaises(ValueError):projector_distance_enclosure(F(0),F(1),F(1))
        with self.assertRaises(TypeError):projector_distance_enclosure(0.1,F(1),F(1))

    def test_two_by_two_spectral_projector_bound(self):
        for a,d,r in [(1.,2.,.1),(.125,.0005,1e-5),(.5,.2,.8)]:
            H=np.array([[-a,r],[r,d]]);P=np.diag([1.,0.])
            vals,U=np.linalg.eigh(H);E=np.outer(U[:,0],U[:,0])
            delta=np.linalg.norm(P-E,2)
            self.assertLessEqual(delta,min(1.,r/(a+d))*(1+1e-12))
            expected=np.sqrt((1-(a+d)/np.hypot(a+d,2*r))/2)
            self.assertAlmostEqual(delta,expected,delta=2e-12)
            self.assertLessEqual(vals[0],-a);self.assertGreaterEqual(vals[1],d)

    def test_original_projector_can_oscillate_while_reference_constant(self):
        a,d,r=.5,.2,.04; H=np.array([[-a,r],[r,d]]);P=np.diag([1.,0.])
        vals,U=np.linalg.eigh(H);E=np.outer(U[:,0],U[:,0]);c0=np.array([1.,0.]);omega=vals[1]-vals[0]
        records=[]
        for t in (0,np.pi/omega,2*np.pi/omega,3*np.pi/omega):
            c=U@(np.exp(-1j*vals*t)*(U.T@c0))
            pj=float(np.vdot(c,P@c).real);pe=float(np.vdot(c,E@c).real)
            self.assertLessEqual(abs(pj-pe),np.linalg.norm(P-E,2)+1e-15)
            records.append((pj,pe))
        self.assertGreater(abs(records[0][0]-records[1][0]),.01)
        self.assertAlmostEqual(records[0][0],records[2][0],delta=1e-14)
        self.assertAlmostEqual(records[0][1],records[1][1],delta=1e-14)

    def test_uniform_observable_difference_is_sharp_for_some_state(self):
        H=np.array([[-.5,.04],[.04,.2]]);P=np.diag([1.,0.]);_,U=np.linalg.eigh(H)
        E=np.outer(U[:,0],U[:,0]);lam,V=np.linalg.eigh(P-E);i=np.argmax(abs(lam));c=V[:,i]
        delta=np.linalg.norm(P-E,2)
        self.assertAlmostEqual(abs(np.vdot(c,(P-E)@c)),delta,delta=1e-14)


if __name__=='__main__':unittest.main()
