from fractions import Fraction as F
from bridge import stored_ground_gap, exact_projector_rank_distance

def test_rank_one_and_five_cannot_have_small_mapping_error():
    assert exact_projector_rank_distance(1,5,9)==F(1)

def test_minmax_gap_for_exact_saved_matrix_with_coupling():
    out=stored_ground_gap([[1,0],[0,1]],[[-2,F(1,10)],[F(1,10),1]], F(-1),F(1,2))
    assert out['verified'] is True
    assert F(out['gap_lower'])==F(3,2)
