"""New synthetic checks; no native operators or archived transport reruns."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import unittest
import numpy as np
from scipy.integrate import solve_ivp
from gapped_tail import tail_bound, first_integer_cutoff


class GappedTailTests(unittest.TestCase):
    def test_exact_rational_arithmetic_and_rejected_assumptions(self):
        result = tail_bound(Z=10, b=0, radius=1, charge=1, gap=2)
        self.assertEqual(result['epsilon'], F(1, 99))
        self.assertEqual(result['projector_distance'], F(1, 197))
        self.assertEqual(result['variation_integral'], F(11, 1764))
        for bad in [dict(gap=0), dict(gap=F(1,1000)), dict(Z=2),
                    dict(Z=1), dict(norm2=-1), dict(b=-1), dict(Z=10.0)]:
            args=dict(Z=10,b=0,radius=1,charge=1,gap=2)
            args.update(bad)
            with self.assertRaises((ValueError,TypeError)):
                tail_bound(**args)

    def test_zero_charge_and_sector_norm_scaling(self):
        args=dict(Z=10,b=2,radius=1,gap=2)
        self.assertEqual(tail_bound(**args,charge=0)['probability_bound'],0)
        full=tail_bound(**args,charge=1)
        half=tail_bound(**args,charge=1,norm2=F(1,2))
        self.assertEqual(half['probability_bound'],full['probability_bound']/2)

    def test_cutoff_is_minimal_and_inverse_square_gain(self):
        args=dict(b=2,radius=64,charge=1,gap=F(1,10))
        target=F(1,200000)
        z=first_integer_cutoff(target=target,**args)
        self.assertLessEqual(tail_bound(Z=z,**args)['probability_bound'],target)
        self.assertGreater(tail_bound(Z=z-1,**args)['probability_bound'],target)
        self.assertGreater(z,16000)
        self.assertLess(z,16200)
        b1=tail_bound(Z=100000,**args)['probability_bound']
        b2=tail_bound(Z=200000,**args)['probability_bound']
        self.assertTrue(3.99<float(b1/b2)<4.01)

    def test_two_level_sylvester_norm_without_factor_two(self):
        delta,k=1.7,.8
        for z in [2.,3.,5.,11.]:
            w=k/z**2
            H=np.array([[-delta/2,w],[w,delta/2]])
            vals,U=np.linalg.eigh(H)
            P=np.outer(U[:,0],U[:,0])
            P0=np.diag([1.,0.])
            exact_distance=np.sqrt((1-delta/np.sqrt(delta**2+4*w*w))/2)
            self.assertAlmostEqual(np.linalg.norm(P-P0,2),exact_distance,places=13)
            self.assertLessEqual(exact_distance,w/(delta-w))
            dz=1e-5
            def projector(at):
                M=np.array([[-delta/2,k/at**2],[k/at**2,delta/2]])
                _,V=np.linalg.eigh(M)
                return np.outer(V[:,0],V[:,0])
            numerical=(projector(z+dz)-projector(z-dz))/(2*dz)
            exact_derivative=2*k*delta/(z**3*(delta**2+4*w*w))
            self.assertAlmostEqual(np.linalg.norm(numerical,2),exact_derivative,places=10)
            self.assertLessEqual(exact_derivative,(2*k/z**3)/(delta-2*w))

    def test_direction_changes_cartesian_derivative_and_support_bounds(self):
        a,b,z,q=1.,3.,4.,1.3
        r=np.array([b,0.,z]); R=np.linalg.norm(r); n=r/R
        # A non-radial point makes the omitted direction term visible.
        x=np.array([.9,0.,0.]); h=1e-5
        def potential(at):
            return -q/np.linalg.norm(np.array([b,0.,at])-x)
        finite_difference=(potential(z+h)-potential(z-h))/(2*h)
        correct=q*(z-x[2])/np.linalg.norm(r-x)**3
        wrong_fixed_direction=q*np.dot(r-x,n)*(z/R)/np.linalg.norm(r-x)**3
        self.assertAlmostEqual(finite_difference,correct,places=10)
        self.assertGreater(abs(correct-wrong_fixed_direction),1e-3)
        rng=np.random.default_rng(391)
        points=rng.normal(size=(200,3))
        points*=a/np.linalg.norm(points,axis=1)[:,None]
        points=np.vstack((points,[a,0,0],[-a,0,0]))
        mid=-q*R/(R*R-a*a)
        epsilon=q*a/(R*R-a*a)
        for point in points:
            distance=np.linalg.norm(r-point)
            self.assertLessEqual(abs(-q/distance-mid),epsilon+1e-15)
            derivative=q*(z-point[2])/distance**3
            self.assertLessEqual(abs(derivative-q*z/R**3),2*q*a/(R-a)**3)

    def test_same_state_finite_interval_population_inequality(self):
        # Independent ODE reference. It checks an actual population, not only
        # the implementation's formula; this is synthetic two-level dynamics.
        delta,k,z0,z1,v=1.7,.8,2.,20.,2.3
        def H(z):
            return np.array([[-delta/2,k/z**2],[k/z**2,delta/2]])
        psi0=np.array([1.,1j])/np.sqrt(2)
        sol=solve_ivp(lambda z,psi:-1j*H(z)@psi/v,(z0,z1),psi0,
                      method='DOP853',rtol=2e-12,atol=2e-14)
        self.assertTrue(sol.success)
        psi1=sol.y[:,-1]
        self.assertLess(abs(np.vdot(psi1,psi1).real-1),2e-11)
        eps0,eps1=k/z0**2,k/z1**2
        endpoint0=eps0/(delta-eps0)
        endpoint1=eps1/(delta-eps1)
        variation=(eps0-eps1)/(delta-2*eps0)
        self.assertLessEqual(abs(abs(psi1[0])**2-abs(psi0[0])**2),
                             endpoint0+endpoint1+variation)
        def projector(z):
            _,U=np.linalg.eigh(H(z))
            return np.outer(U[:,0],U[:,0])
        p0=np.vdot(psi0,projector(z0)@psi0).real
        p1=np.vdot(psi1,projector(z1)@psi1).real
        self.assertLessEqual(abs(p1-p0),variation)

    def test_preserved_cluster_is_not_necessarily_the_negative_cut(self):
        # Strict cluster gap remains open although the upper mode crosses zero.
        alpha,beta,eps=-.1,.001,.004
        self.assertLess(2*eps,beta-alpha)
        vals=np.linalg.eigvalsh(np.diag([alpha+eps,beta-eps]))
        self.assertEqual(np.count_nonzero(vals<0),2)
        self.assertEqual(np.count_nonzero(vals<(alpha+beta)/2),1)

    def test_gap_and_amplitude_alone_do_not_give_inverse_square_population(self):
        # Independent review's exact resonant counterexample: H0=delta*sigma_z/2,
        # V=t^-2 exp(-iH0t) sigma_x exp(iH0t). Its gap never closes, yet
        # interaction-picture phi=exp(i*sigma_x/t)*(1,i)/sqrt(2), giving
        # lower-energy population 1/2 + sin(2/t)/2 = 1/2+O(t^-1).
        delta=1.7
        for t in [10.,100.,1000.]:
            lower=(np.cos(1/t)+np.sin(1/t))**2/2
            self.assertAlmostEqual(lower-.5,np.sin(2/t)/2,places=14)
            self.assertGreater(2*np.sqrt(delta*delta/4+t**-4),delta)
            derivative_norm=np.sqrt(4/t**6+delta**2/t**4)
            self.assertGreater(derivative_norm,delta/t**2)
        ratio=(np.sin(2/100)/2)/(np.sin(2/200)/2)
        self.assertTrue(1.99<ratio<2.01)

    def test_actual_reference_bound_certificate_binding(self):
        here=Path(__file__).resolve().parent
        result=json.loads((here/'CONDITIONAL_CUTOFF.json').read_text())
        source=here.parent/result['reference_certificate_path']
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         result['reference_certificate_sha256'])
        ref=json.loads(source.read_text())
        gap=(F(ref['reference_block_certificate']['a_lower']['rational'])
             +F(ref['reference_block_certificate']['d_lower']['rational']))
        self.assertEqual(gap,F(result['certified_reference_gap_lower']['rational']))
        args=dict(b=2,radius=64,charge=1,gap=gap,norm2=1)
        z=result['minimum_integer_cutoff_a0']
        self.assertEqual(z,14312)
        actual=tail_bound(Z=z,**args)['probability_bound']
        self.assertEqual(actual,F(result['bound_at_cutoff']['probability_bound']['rational']))
        target=F(result['research_target_per_side']['rational'])
        self.assertLessEqual(actual,target)
        self.assertGreater(tail_bound(Z=z-1,**args)['probability_bound'],target)
        self.assertIsNone(result['bridge_bound'])
        self.assertIsNone(result['dynamical_state_transfer_bound'])


if __name__=='__main__':
    unittest.main()
