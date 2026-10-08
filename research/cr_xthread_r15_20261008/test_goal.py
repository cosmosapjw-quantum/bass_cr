import unittest
from fractions import Fraction as Q
from goal import cell_goal, ContractError

class GoalTests(unittest.TestCase):
    def test_nonzero_incoming_and_constant_residual(self):
        # e(s)=2-3s; integral_0^1 e(s) ds = 1/2.
        p=[{'s':['0','1'],'residual':[['3','3'],['0','0'],['0','0']]}]
        r=cell_goal(p, [(2,2),(0,0),(0,0)], [0,0,0], Q(0), (1,1), Q(1), Q(83,1000))
        self.assertEqual(r['initial'], (Q(2),Q(2)))
        self.assertEqual(r['forcing'], (Q(-3,2),Q(-3,2)))
        self.assertEqual(r['difference'], (Q(1,2),Q(1,2)))

    def test_no_sign_from_endpoint(self):
        p=[{'s':['0','1'],'residual':[['0','0'],['0','0'],['0','0']]}]
        r=cell_goal(p, [(-1,1),(0,0),(0,0)], [0,0,0], Q(0), (1,1), Q(1), Q(83,1000))
        self.assertEqual(r['difference'], (Q(-1),Q(1)))

    def test_bad_clock_panels_rejected(self):
        p=[{'s':['0','.9'],'residual':[['0','0']]*3}]
        with self.assertRaisesRegex(ContractError, 'COVER'):
            cell_goal(p, [(0,0)]*3, [0]*3, Q(0), (1,1), Q(1), Q(83,1000))

if __name__=='__main__': unittest.main()
