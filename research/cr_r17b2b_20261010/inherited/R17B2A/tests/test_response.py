import sys
from pathlib import Path
import unittest
import json
from fractions import Fraction as F
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from response import blocks
from ft03_point import Model,W0,H,TEND,FHE,KB,EV,CHI,temperature,temperature_gradient,nonphoto,nonphoto_jac
from kernel_regularity import second_jump

class BlockTests(unittest.TestCase):
    def test_multi_cohort_charge_transfer_conserves_count(self):
        p=np.array([.05,.001]);kap=np.array([.2,.3]);gr=np.array([[-2.],[-3.]])
        J=blocks(np.zeros((1,1)),p,kap,gr,np.ones((1,2)))
        np.testing.assert_allclose(np.ones(3)@J,np.zeros(3),atol=1e-17)
    def test_zero_stock_decouples_old_photon_feedback(self):
        J=blocks(np.zeros((2,2)),np.zeros(1),np.ones(1),np.ones((1,2)),np.ones((2,1)))
        np.testing.assert_array_equal(J[2,:2],[0,0])
    def test_no_absorption_no_probe_gas_response(self):
        J=blocks(np.zeros((2,2)),np.ones(1),np.zeros(1),np.zeros((1,2)),np.ones((2,1)))
        np.testing.assert_array_equal(J,np.zeros((3,3)))
    def test_block_matrix_matches_directional_difference(self):
        m=Model([0.,.3]);u=.6;y=np.array([.9,.3,.6,1.,.05,.0001]);d=np.array([.1,-.01,.02,.04,.02,.03]);eps=1e-5
        fd=(m.rhs(u,y+eps*d)-m.rhs(u,y-eps*d))/(2*eps)
        np.testing.assert_allclose(m.jac(u,y)@d,fd,rtol=1e-8,atol=1e-13)

class PhysicsTests(unittest.TestCase):
    def test_source_initial_temperature(self):
        self.assertAlmostEqual(temperature(np.array([.9,.3,.6,1.])),50000.,places=8)
    def test_soft_photoionization_cools_temperature_but_adds_energy(self):
        g=np.array([.9,.3,.6,1.]);v=np.array([1.,0,0,(13.7-CHI[0])/W0])
        self.assertGreater(v[3],0)
        self.assertLess(temperature_gradient(g)@v,0)
    def test_temperature_gradient_against_finite_difference(self):
        g=np.array([.9,.3,.6,1.]);d=np.array([.1,.02,-.01,.03]);e=1e-5
        fd=(temperature(g+e*d)-temperature(g-e*d))/(2*e)
        self.assertAlmostEqual(float(temperature_gradient(g)@d/fd),1.,places=8)
    def test_fit_cutoff_raises_instead_of_silent_extension(self):
        with self.assertRaises(ValueError):Model([0.],[13.59]).rhs(0.,np.array([.9,.3,.6,1.,.05]))
    def test_helium_threshold_raises(self):
        with self.assertRaises(ValueError):Model([0.],[24.59]).rhs(0.,np.array([.9,.3,.6,1.,.05]))
    def test_thermal_domain_raises(self):
        with self.assertRaises(ValueError):nonphoto(0.,np.array([.9,.3,.6,3.]))
    def test_real_source_parameters_not_grackle(self):
        self.assertEqual(W0,13.620772387478219);self.assertEqual(FHE,.083)
        self.assertEqual(TEND,1250000000.)

class RegularityTests(unittest.TestCase):
    def args(self):
        return dict(weight=F(1,10),kappa_background=F(2),grad_background=[F(-3),F(0)],yield_background=[F(1),F(1,20)],psi_background=F(3,7),kappa_probe=F(2),grad_probe=[F(-3),F(0)],yield_probe=[F(1),F(1,20)],psi_probe=F(3,7),lambda_g=[F(4,5),F(2,3)])
    def test_same_channel_second_jump_cancels_exactly(self):
        r=second_jump(**self.args());self.assertNotEqual(r['opacity_term'],0);self.assertEqual(r['kernel_second_jump'],0)
    def test_unlike_channel_second_jump_need_not_cancel(self):
        a=self.args();a['psi_probe']=F(4,7)
        self.assertNotEqual(second_jump(**a)['kernel_second_jump'],0)
    def test_zero_birth_has_no_jump(self):
        a=self.args();a['weight']=F(0)
        self.assertEqual(second_jump(**a)['kernel_second_jump'],0)
    def test_float_rejected_in_exact_algebra(self):
        a=self.args();a['weight']=.1
        with self.assertRaises(TypeError):second_jump(**a)
    def test_mismatched_dimension_rejected(self):
        a=self.args();a['grad_probe']=[F(1)]
        with self.assertRaises(ValueError):second_jump(**a)
    def test_negative_weight_rejected(self):
        a=self.args();a['weight']=F(-1)
        with self.assertRaises(ValueError):second_jump(**a)
if __name__=='__main__':unittest.main()
