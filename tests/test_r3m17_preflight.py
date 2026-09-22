"""Small metadata-only tests; no GPU or production grid allocation."""
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('r3m17_preflight', ROOT/'scripts/r3m17_preflight.py')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def config(job='B'):
    return json.loads((ROOT/f'configs/r3m15/{job}.json').read_text())


def b2_config():
    cfg = json.loads((ROOT/'configs/r3m16/B1.json').read_text())
    cfg['dt'] = .0125
    return cfg


def test_b2_frozen_family_and_chunk_count():
    cfg = b2_config()
    result = MOD.build_preflight(cfg, config_path='/tmp/B2.json', job_root='/tmp/future-B2')
    assert result['status'] == 'PLAN_ONLY_NOT_EXECUTED'
    assert result['collision_execution_performed'] is False
    assert result['new_collision_budget'] == 1
    assert result['numerical']['nstep'] == 3586
    assert result['numerical']['chunk_count'] == 29
    assert result['numerical']['chunk_count'] > 15
    assert result['numerical']['actual_dt'] <= cfg['dt']
    assert result['numerical']['actual_dt'] * result['numerical']['nstep'] == pytest.approx(result['numerical']['physical_horizon_au'])
    assert result['runtime']['cpu_fallback_allowed'] is False
    assert result['runtime']['science_environment_verified'] is False
    commands = result['command_plan']
    assert commands[0]['phase'] == 'resource_preflight'
    assert commands[1]['phase'] == 'prepare'
    chunks = [x for x in commands if x['phase'] == 'collision_chunk']
    assert len(chunks) == result['numerical']['chunk_count']
    assert all(x['argv'][-2:] == ['--max-steps', '128'] for x in chunks)
    assert all('r3m14_collision_initial_witness.py' in ' '.join(x['argv']) for x in chunks)
    assert all(x['must_stop_on_previous_failure'] for x in chunks)
    assert result['prerequisites']['same_grid_preparation_byte_identity_required'] is True


@pytest.mark.parametrize('field,value', [('dt', .00625), ('b', 3.), ('energy_keV_per_u', 225), ('absorber_reference_dt', .025)])
def test_only_frozen_dt_change_is_allowed(field, value):
    cfg = b2_config(); cfg[field] = value
    with pytest.raises(ValueError, match='B2 config family'):
        MOD.validate_b2_config(cfg)


def test_numerical_metadata_known_grid_phases():
    a = MOD.numerical_metadata(config('A'))
    b = MOD.numerical_metadata(config('B'))
    c = MOD.numerical_metadata(config('C'))
    for item in (a, b):
        assert item['projectile']['nearest_transverse_axis_distance_over_h'] == pytest.approx([.5, .5])
        assert item['projectile']['minimum_transverse_distance_over_h'] == pytest.approx(math.sqrt(.5))
    assert c['projectile']['nearest_transverse_axis_distance_over_h'] == pytest.approx([.1, .5])
    assert c['projectile']['minimum_transverse_distance_over_h'] == pytest.approx(math.sqrt(.26))
    assert b['projectile']['displacement_per_step_over_h'] == pytest.approx(450/897)
    assert a['projectile']['mesh_phase_matches_target_transverse'] is True
    assert c['projectile']['mesh_phase_matches_target_transverse'] is False


@pytest.mark.parametrize('shape', [(4, 6, 8), (5, 7, 9), (4, 7, 8)])
def test_fft_max_uses_actual_parity_against_independent_fftfreq(shape):
    h = .2
    info = MOD.fft_kinetic_metadata(shape, h, .025)
    maxima = [float(np.max(abs(2*np.pi*np.fft.fftfreq(n, d=h)))) for n in shape]
    expected = .5*sum(x*x for x in maxima)
    assert info['axis_kmax_au_inverse'] == pytest.approx(maxima)
    assert info['maximum_kinetic_energy_Eh'] == pytest.approx(expected)
    assert info['maximum_kinetic_phase_radians'] == pytest.approx(.025*expected)
    assert info['universal_CFL_stability_limit_claimed'] is False


def test_shifted_grid_records_mesh_phase_and_rejects_exact_moving_singularity():
    cfg = config('B')
    cfg['grid']['xlim'] = [-29.9, 40.1]
    cfg['grid']['ylim'] = [-29.9, 30.1]
    # Both x=b and y=0 now coincide with cell centers; path contains z centers.
    with pytest.raises(ValueError, match='projectile.*Coulomb singularity'):
        MOD.numerical_metadata(cfg)


def test_near_but_not_exact_axis_is_diagnostic_not_singular():
    cfg = config('B')
    cfg['grid']['xlim'] = [-29.899999, 40.100001]
    cfg['grid']['ylim'] = [-29.9, 30.1]
    result = MOD.numerical_metadata(cfg)
    assert result['projectile']['minimum_transverse_distance_a0'] > 0
    assert result['projectile']['minimum_transverse_distance_a0'] < 2e-6


def test_output_refuses_overwrite(tmp_path):
    path = tmp_path/'plan.json'
    MOD.write_new(path, {'status': 'PLAN_ONLY_NOT_EXECUTED'})
    with pytest.raises(FileExistsError):
        MOD.write_new(path, {'status': 'CHANGED'})
    assert json.loads(path.read_text())['status'] == 'PLAN_ONLY_NOT_EXECUTED'


def test_plan_does_not_create_data_directories(tmp_path):
    job = tmp_path/'does-not-exist'/'B2'
    MOD.build_preflight(b2_config(), config_path=tmp_path/'B2.json', job_root=job)
    assert not job.exists()


def test_existing_plan_config_must_match_validated_config(tmp_path):
    path = tmp_path/'B2.json'
    path.write_text(json.dumps(config('B')))
    with pytest.raises(ValueError, match='config file'):
        MOD.build_preflight(b2_config(), config_path=path, job_root=tmp_path/'future')


def test_frozen_reference_byte_identity_is_checked(monkeypatch):
    monkeypatch.setattr(MOD, 'FROZEN_B1_CONFIG_SHA256', '0'*64)
    with pytest.raises(ValueError, match='reference config byte identity'):
        MOD.validate_b2_config(b2_config())


def test_each_collision_chunk_has_witnessed_snapshot_before_next_chunk(tmp_path):
    plan = MOD.build_preflight(b2_config(), config_path=tmp_path/'B2.json', job_root=tmp_path/'job')
    commands = plan['command_plan'][2:]
    assert len(commands) == 58
    for chunk, (collision, snapshot) in enumerate(zip(commands[::2], commands[1::2]), 1):
        assert collision['phase'] == 'collision_chunk'
        assert snapshot['phase'] == 'checkpoint_snapshot'
        assert snapshot['chunk'] == collision['chunk'] == chunk
        assert snapshot['expected_completed_steps'] == min(chunk*128, 3586)
        assert snapshot['must_finish_before_next_collision_chunk'] is True
        assert snapshot['must_stop_on_previous_failure'] is True
        assert '--allow-unwitnessed' not in snapshot['argv']
        assert snapshot['argv'][-2:] == ['--config', str(tmp_path/'B2.json')]
    retention = plan['checkpoint_retention']
    assert retention['create_parent_on_same_filesystem_as_collision_before_execution'] is True
    assert retention['retained_generation_count'] == 29
    assert retention['retained_state_bytes_estimate'] == 29*1_008_000_128
    assert retention['floor_is_sufficient_space_certificate'] is False
