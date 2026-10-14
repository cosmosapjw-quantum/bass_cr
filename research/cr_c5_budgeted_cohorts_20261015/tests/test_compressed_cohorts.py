"""C5/C6 tests for compression reference. No cosmological-history admission."""
from __future__ import annotations
import math
import pytest
from compressed_cohorts import (
    CompressedCohortTransport, CompressionHold,
    one_step_pair_bounds, _verner_derivative_bound,
    frozen_be_readout,
)
from threshold_rt import frozen_source, verner, ION_NAMES, SOURCE_EDGES, CohortTransport

NEUTRALS=(1e-3,8e-5,2e-5)

@pytest.mark.parametrize('kind,lo,hi',[
    ('HI',17.,18.),('HI',55.,56.),('HeI',26.,27.),
    ('HeI',74.,75.),('HeII',58.,59.),('HeII',84.,85.),
])
def test_analytical_verner_derivative_lipschitz_is_sufficient(kind,lo,hi):
    upper_sigma,upper_grad=_verner_derivative_bound(kind,lo,hi)
    # Sampled falsification control; analytical bounding formulas provide the
    # justification, this finite sampling is NOT itself a rigorous certificate.
    es=[lo+(hi-lo)*i/100 for i in range(101)]
    vals=[verner(kind,e) for e in es]
    assert max(vals)<upper_sigma
    assert max(abs(b-a)/(es[i+1]-es[i]) for i,(a,b) in enumerate(zip(vals,vals[1:])))<upper_grad


def test_zero_opacity_below_threshold_and_crossing_hold():
    assert _verner_derivative_bound('HeII',23.,40.)==(0.,0.)
    with pytest.raises(CompressionHold,match='THRESHOLD'):
        _verner_derivative_bound('HeII',54.,56.)

@pytest.mark.parametrize('ratio',[1.,.999,.995,.99])
def test_end_to_end_component_errors_bounded_over_forecast_tube(ratio):
    obj=CompressedCohortTransport.frozen_source(16,max_cohorts=32)
    old=list(obj.cohorts)
    cert=obj.compress(NEUTRALS,1e9,.99,.01,1.)
    assert cert.final_cohorts==32 and cert.merges==16
    expected=frozen_be_readout(old,NEUTRALS,1e9,ratio)
    observed=frozen_be_readout(obj.cohorts,NEUTRALS,1e9,ratio)
    for k in range(3):
        assert abs(expected[0][k]-observed[0][k])<=cert.event_absolute_bounds[k]
        assert abs(expected[1][k]-observed[1][k])<=cert.heat_absolute_bounds_eV[k]


def test_compression_conserves_both_moments_and_nonnegativity():
    obj=CompressedCohortTransport.frozen_source(16,max_cohorts=40)
    before=obj.moments()
    cert=obj.compress(NEUTRALS,1e9,.99,.001,.1)
    assert cert.final_cohorts==40
    assert obj.moments()==pytest.approx(before,rel=5e-15)
    assert all(e>0 and n>=0 for e,n in obj.cohorts)


def test_budget_hold_transactional_does_not_mutate_state():
    obj=CompressedCohortTransport.frozen_source(16,max_cohorts=24)
    old=list(obj.cohorts)
    with pytest.raises(CompressionHold,match='HOLD_BUDGET_OR_THRESHOLD'):
        obj.compress(NEUTRALS,1e9,.99,.001,.1)
    assert obj.cohorts==old
    assert obj.last_certificate is None


def test_injection_hold_transactional_does_not_erase_original_state():
    obj=CompressedCohortTransport.frozen_source(16,max_cohorts=24)
    old=list(obj.cohorts)
    with pytest.raises(CompressionHold):
        obj.inject_and_compress(frozen_source(16),NEUTRALS,1e9,.99,.001,.1)
    assert old==obj.cohorts


def test_zero_budget_can_merge_exactly_identical_cohorts():
    obj=CompressedCohortTransport([(25.,.5),(25.,.5)],max_cohorts=1)
    out=obj.compress(NEUTRALS,1e9,.99,0.,0.)
    assert out.merges==1 and obj.cohorts==[(25.,1.)]


def test_he_threshold_pair_rejected_across_predicted_future_crossing():
    # Both at 25eV now; the lower characteristic crosses 24.59eV by r=.98.
    with pytest.raises(CompressionHold,match='THRESHOLD'):
        one_step_pair_bounds(24.8,.1,25.2,.2,NEUTRALS,1e9,.98)


def test_cutoff_boundary_pair_rejected_for_forecast():
    with pytest.raises(CompressionHold,match='BOUNDARY'):
        one_step_pair_bounds(13.65,.1,13.8,.1,NEUTRALS,1e9,.98)


def test_invalid_rates_and_redshift_rejected():
    x=CompressedCohortTransport.frozen_source(16,max_cohorts=32)
    with pytest.raises(ValueError):x.compress((1.,-1.,1.),1e9)
    with pytest.raises(ValueError):x.compress(NEUTRALS,float('nan'))
    with pytest.raises(ValueError):x.compress(NEUTRALS,1e9,0.)
    with pytest.raises(ValueError):x.compress(NEUTRALS,1e9,1.,-1.)


def test_one_step_pos_energy_ledger_after_compression():
    x=CompressedCohortTransport.frozen_source(16,max_cohorts=32)
    x.compress(NEUTRALS,1e9,.99,.01,1.)
    before=x.moments()
    red=x.redshift(.995)
    absorption=x.absorb_backward_euler(NEUTRALS,1e9)
    after=x.moments()
    consumed=sum(absorption['photo_events_per_H'].values())
    heat=sum(absorption['direct_photoheat_eV_per_H'].values())
    binding=sum(absorption['binding_eV_per_H'].values())
    assert abs(before[0]-after[0]-red['boundary_count']-consumed)<1e-13
    assert abs(before[1]-after[1]-red['boundary_energy_eV']-red['photon_work_eV']-heat-binding)<1e-11


def test_no_false_continuum_guarantee_fields_on_certificate():
    x=CompressedCohortTransport.frozen_source(16,max_cohorts=40)
    c=x.compress(NEUTRALS,1e9,.99,.001,.1)
    assert 'ONE_STEP' in c.status
    assert 'EXACT_REAL' in c.status
    assert c.forecast_min_redshift_ratio==.99


def test_forecast_certificate_is_invalidated_by_time_evolution():
    x=CompressedCohortTransport.frozen_source(16,max_cohorts=32)
    x.compress(NEUTRALS,1e9,.99,.01,1.)
    assert x.last_certificate is not None
    x.redshift(.997)
    assert x.last_certificate is None
    x.compress(NEUTRALS,1e9,.99,.01,1.)
    x.absorb_backward_euler(NEUTRALS,1e9)
    assert x.last_certificate is None


def test_repeated_injection_stays_at_fixed_cap_without_inventing_global_error_bar():
    from compression_benchmark import repeated_injection_experiment
    x=repeated_injection_experiment(axis=16,steps=4,cap=32,injection_scale=.1)
    assert [row['raw_cohorts'] for row in x['rows']]==[96,144,192,240]
    assert [row['compressed_cohorts'] for row in x['rows']]==[32,32,32,32]
    for row in x['rows']:
        assert abs(row['number_residual_raw'])<1e-13
        assert abs(row['number_residual_compressed'])<1e-13
        assert abs(row['energy_residual_raw_eV'])<1e-11
        assert abs(row['energy_residual_compressed_eV'])<1e-11
    assert 'Empirical' in x['note']


def test_repeated_injection_explicit_hold_keeps_old_state():
    x=CompressedCohortTransport.frozen_source(16,max_cohorts=16)
    old=x.cohorts.copy()
    with pytest.raises(CompressionHold):
        x.inject_and_compress([(e,.1*n) for e,n in frozen_source(16)],NEUTRALS,1e9,.98,.0001,.01)
    assert x.cohorts==old
