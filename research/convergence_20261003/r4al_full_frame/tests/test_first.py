from fractions import Fraction as F
from full_frame import gram_tube

def test_anchor_and_motion_cost_are_not_omitted():
    r=gram_tube(F(1),F(1),F(1,16),F(2),F(1,32))
    assert r['lower']==F(7,8)
    assert r['upper']==F(9,8)
