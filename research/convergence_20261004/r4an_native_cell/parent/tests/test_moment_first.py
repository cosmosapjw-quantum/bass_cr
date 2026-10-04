from fractions import Fraction as F
from moments import moment

def test_quartic_azimuthal_moment_at_zero_phase_is_not_discarded():
    # Defect detected: extending the old quadratic angular provider by zero.
    r=moment(4,0,F(2),F(0))
    assert r.re.contains(F(3,2)) and r.im.contains(0)

def test_sparse_product_keeps_the_rhs_object_for_every_left_term():
    from moments import U,V
    x=(1+U)*(2+V)
    assert x.evaluate(3,4).re.contains(24)
