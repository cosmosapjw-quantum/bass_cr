import math
import numpy as np
import pytest
from cr_repro.r3m13 import (
    phase_aligned_distance, probability_transfer_interval,
    sufficient_screen_distance, trace_distance_from_phase_l2,
    build_preparation_configs,
)


def test_phase_aligned_distance_ignores_global_phase():
    a=np.array([1.0,1.0j])/math.sqrt(2); b=np.exp(0.37j)*a
    assert phase_aligned_distance(a,b,1.0) < 1e-14


def test_transfer_interval_contains_extreme_amplitude_bound():
    p=0.04; d=0.01; lo,hi=probability_transfer_interval(p,d)
    assert lo == pytest.approx((math.sqrt(p)-d)**2)
    assert hi == pytest.approx((math.sqrt(p)+d)**2)


def test_one_percent_screen_threshold_matches_r3m12_reference():
    assert sufficient_screen_distance(0.00775827737938,0.01) == pytest.approx(0.00043930987793802824,rel=1e-12)


def test_trace_distance_relation_for_normalized_pure_states():
    d=0.2
    assert trace_distance_from_phase_l2(d) == pytest.approx(d*math.sqrt(1-d*d/4))


def test_build_preparation_configs_changes_only_imaginary_time_pair():
    base=dict(energy_keV_per_u=100.,b=2.,backend='auto',
        grid=dict(xlim=[-30,40],ylim=[-30,30],zlim=[-30,90],dx=.25),
        dt=.05,z_start=-30.,z_stop=60.,absorber_width=4.,absorber_power=.125,
        absorber_reference_dt=.05,initial_state='imag_time',imag_dt=.025,imag_steps=1200,
        project_nmax=3,capture_plane=30.,checkpoint_stride=100,projection_slab_x=2)
    ref,new=build_preparation_configs(base)
    assert ref['imag_dt']==.025 and ref['imag_steps']==1200
    assert new['imag_dt']==.0125 and new['imag_steps']==2400
    assert ref['imag_dt']*ref['imag_steps']==pytest.approx(30.)
    assert new['imag_dt']*new['imag_steps']==pytest.approx(30.)
    for key in base:
        if key not in {'imag_dt','imag_steps'}: assert ref[key]==new[key]==base[key]


def test_builder_rejects_wrong_r3m12_physics_lane():
    bad=dict(grid={'dx':.3125},dt=.05,absorber_reference_dt=.05,imag_dt=.025,imag_steps=1200)
    with pytest.raises(ValueError): build_preparation_configs(bad)
