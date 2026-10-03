from fractions import Fraction as F
from radial_pair import tail_mass

def test_polynomial_tail_is_exact_not_a_sampled_quadrature():
    assert tail_mass([0,1],[0,1],[[0,0,0]],F(1,2)) == F(7,24)
