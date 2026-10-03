from fractions import Fraction as F
import pytest
from radial_pair import tail_mass
from weak_pair import ContractError

@pytest.mark.parametrize('r,answer',[(0,F(1,3)),(F(1,2),F(7,24)),(1,0),(2,0)])
def test_tail_cutoff_limits(r,answer):
    assert tail_mass([0,1],[0,1],[[0,0,0]],r)==answer

def test_tail_exact_bubble_integral():
    assert tail_mass([0,2],[0,0],[[1,0,0]],0)==F(1,15)

def test_joined_panels_tail_without_missing_interface():
    assert tail_mass([0,1,2],[0,1,0],[[0,0,0],[0,0,0]],1)==F(1,3)

@pytest.mark.parametrize('args',[
    ([1,2],[0,1],[[0,0,0]],0),([0,0],[0,1],[[0,0,0]],0),
    ([0,1],[0],[[0,0,0]],0),([0,1],[0,1],[[0,0]],0),
    ([0,1],[0,1],[[0,0,0]],-1),([0,1],[0,True],[[0,0,0]],0)])
def test_malformed_radial_data_rejected(args):
    with pytest.raises(ContractError): tail_mass(*args)
