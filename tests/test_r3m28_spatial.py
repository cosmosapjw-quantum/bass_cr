import pytest

from scripts.r3m28_spatial import screen


def _rows(a3=0.00807):
    return (
        {'P1': .00587, 'P2': .00733, 'P3': .007825},
        {'P1': .00606, 'P2': .00756, 'P3': .008063},
        {'P1': .00608, 'P2': .00758, 'P3': a3},
        {'P1': .00609, 'P2': .00759, 'P3': .008089},
    )


def test_pair_screen_pass_does_not_admit_spatial_budget():
    result = screen(*_rows())
    assert result['status'] == 'SPATIAL_PAIR_SCREEN_PASS_BUDGET_OPEN'
    assert result['spatial_budget'] == 'OPEN'
    assert not result['pair_is_validated_spatial_error_estimate']
    assert result['channels']['P3']['raw_h_dt_interaction'] == pytest.approx(
        (.008089-.00807)-(.008063-.007825))


def test_any_channel_exceedance_is_no_go_not_error_lower_bound():
    result = screen(*_rows(a3=.00783))
    assert result['status'] == 'SPATIAL_PAIR_SCREEN_NO_GO'
    assert not result['channels']['P3']['pair_screen_pass']
    assert result['channels']['P3']['pair_relative_to_B3'] > .003
    assert not result['h_dt_interaction_is_validated_error_estimate']


def test_zero_denominator_and_boolean_probability_rejected():
    rows = list(_rows())
    rows[-1] = dict(rows[-1], P3=0)
    with pytest.raises(ValueError):
        screen(*rows)
    rows[-1] = dict(_rows()[-1], P3=True)
    with pytest.raises(ValueError):
        screen(*rows)
