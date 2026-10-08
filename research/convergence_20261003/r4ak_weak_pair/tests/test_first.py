from weak_pair import exact_pair_certificate

def test_decoupled_pair_has_exact_zero_residual_without_spectral_gap():
    # All three energies coincide; a gap-based implementation would reject it.
    result=exact_pair_certificate([[1,0,0],[0,1,0],[0,0,1]],
                                  [[0,0,0],[0,0,0],[0,0,0]],(0,1))
    assert result is not None, 'missing weak retained-pair certificate'
    assert result['residual_upper_per_ta']=='0'
    assert result['metric_defect_upper_per_ta']=='0'
    assert result['spectral_gap_required'] is False
    assert result['physical_admission'] is False
