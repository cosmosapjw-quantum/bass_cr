import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from scipy.integrate import solve_ivp
from adjoint_linear import Cell, Link, forward_error, backward_dual

class AdjointTests(unittest.TestCase):
    def test_scalar_residual_sign(self):
        c=Cell(A=np.zeros((1,1)), g=lambda t:np.array([2.]), r=lambda t:np.array([3.]))
        # e'=-3, g=2, goal=-3
        fw=forward_error([c], [], np.array([0.]))
        dual=backward_dual([c], [], np.array([0.]))
        self.assertAlmostEqual(fw['goal'],-3.,places=10)
        self.assertAlmostEqual(dual['goal'],-3.,places=10)
    def test_initial_state_term(self):
        c=Cell(A=np.zeros((1,1)),g=lambda t:np.array([2.]),r=lambda t:np.array([3.]))
        self.assertAlmostEqual(backward_dual([c],[],np.array([4.]))['goal'],5.,places=10)
    def test_birth_injection_dimension_growth(self):
        a=Cell(A=np.zeros((1,1)),g=lambda t:np.array([0.]),r=lambda t:np.array([0.]))
        A=np.array([[0.,3.],[0.,0.]])
        b=Cell(A=A,g=lambda t:np.array([1.,0.]),r=lambda t:np.array([0.,0.]))
        link=Link(B=np.array([[1.],[0.]]),delta=np.array([0.,2.]))
        # birth photon amount 2 increases gas via A_01=3 for unit cell: total=3
        f=forward_error([a,b],[link],np.array([0.]))
        d=backward_dual([a,b],[link],np.array([0.]))
        self.assertAlmostEqual(f['goal'],3.,places=8)
        self.assertAlmostEqual(d['goal'],3.,places=8)
    def test_interface_nominal_jump(self):
        # numerical reconstruction jumps from 1 to 0 but true state remains 1:
        # e^+=e^-+1, with local optical mass 2 -> 2.
        a=Cell(A=np.zeros((1,1)),g=lambda t:np.array([0.]),r=lambda t:np.array([0.]))
        b=Cell(A=np.zeros((1,1)),g=lambda t:np.array([2.]),r=lambda t:np.array([0.]))
        L=Link(B=np.eye(1),delta=np.array([1.]))
        self.assertAlmostEqual(backward_dual([a,b],[L],np.array([0.]))['goal'],2.,places=10)
    def test_signed_time_varying_two_dimensional(self):
        c=Cell(A=np.array([[-.2,.7],[-.3,-.1]]),
              g=lambda s:np.array([1.+s,-.4]),
              r=lambda s:np.array([.1*s,.2+.2*s]))
        init=np.array([.1,-.1])
        f=forward_error([c],[],init)
        d=backward_dual([c],[],init)
        self.assertAlmostEqual(f['goal'],d['goal'],places=8)
    def test_variable_dimensions_and_two_births(self):
        cells=[Cell(A=np.array([[-.2]]),g=lambda t:np.array([1.]),r=lambda t:np.array([.1])),
               Cell(A=np.array([[.1,.3],[0.,-.2]]),g=lambda t:np.array([1.,0.]),r=lambda t:np.array([.1,.2])),
               Cell(A=np.array([[.0,.3,.1],[0.,-.2,0.],[0.,0.,-.3]]),g=lambda t:np.array([1.,0.,0.]),r=lambda t:np.array([.1,.1,.1]))]
        links=[Link(np.array([[1.],[0.]]),np.array([0.,.4])), Link(np.array([[1.,0.],[0.,1.],[0.,0.]]),np.array([.05,-.02,-.3]))]
        f=forward_error(cells,links,np.array([.02]))
        d=backward_dual(cells,links,np.array([.02]))
        self.assertAlmostEqual(f['goal'],d['goal'],places=8)
        self.assertEqual(len(d['residual_contributions']),3)
        self.assertEqual(len(d['interface_contributions']),2)
    def test_bad_dimension_rejected(self):
        c=Cell(np.zeros((1,1)),lambda s:np.array([1.]),lambda s:np.array([0.]))
        bad=Link(B=np.eye(2),delta=np.zeros(2))
        with self.assertRaisesRegex(ValueError,'LINK_DIMENSION'):
            backward_dual([c,c],[bad],np.array([0.]))

if __name__=='__main__':unittest.main()
