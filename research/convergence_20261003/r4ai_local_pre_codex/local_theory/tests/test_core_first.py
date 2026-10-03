from fractions import Fraction as F
from cr_reion.core import weighted_intervals,cx_delta,state_error_bound

def test_positive_interval_functional_exact():
    assert weighted_intervals([F(1,4),F(3,4)],[(2,3),(4,6)]) == (F(7,2),F(21,4))

def test_cx_population_transfer_is_not_electron_creation():
    assert cx_delta(F(3,2)) == (-F(3,2),-F(3,2),F(3,2),F(3,2),0)

def test_zero_metric_defect_residual_accumulates_linearly():
    assert state_error_bound(F(1,100),[(2,0,F(3,100))]) == F(7,100)
