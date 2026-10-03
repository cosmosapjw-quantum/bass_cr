from fractions import Fraction as F
import pytest
from cr_reion.spectrum import powerlaw_p_minus2_weights
from cr_reion.core import ContractError

def test_h5_radial_measure_is_dp_not_p_squared_dp():
    assert powerlaw_p_minus2_weights([1,2,4])==(F(2,3),F(1,3))

@pytest.mark.parametrize('edges',[[0,1],[2,1],[1,1],[],[1],[-1,2]])
def test_invalid_spectrum(edges):
    with pytest.raises(ContractError):powerlaw_p_minus2_weights(edges)

def test_scale_change_preserves_probability_bins():
    assert powerlaw_p_minus2_weights([10,20,40])==powerlaw_p_minus2_weights([1,2,4])
