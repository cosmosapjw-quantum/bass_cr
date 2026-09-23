"""Reject plan substitution before reading large arrays or launching commands."""
import copy
import json
from pathlib import Path

import pytest

from scripts import r3m18_b2_execute as coordinator
from scripts.r3m17_preflight import build_preflight


def fixture(tmp_path, monkeypatch):
    root = tmp_path / 'B2'
    (root / 'preparation').mkdir(parents=True)
    (root / 'preparation/initial.npy').write_bytes(b'identity fixture only')
    (root / 'preparation/receipt.json').write_text(json.dumps({
        'status': 'COMPLETE', 'source_digest': coordinator.FROZEN_SOURCE}))
    (root / 'resource.json').write_text(json.dumps({'status': 'PASS_RESOURCE_PREFLIGHT'}))
    cfg_path = coordinator.ROOT / 'configs/r3m17/B2.json'
    cfg = json.loads(cfg_path.read_text())
    plan = build_preflight(cfg, config_path=cfg_path, job_root=root)
    monkeypatch.setattr(coordinator, 'sha', lambda _: coordinator.CANONICAL_INITIAL_SHA256)
    return root, cfg_path, plan


@pytest.mark.parametrize('change', [
    'arbitrary_command', 'interpreter', 'prepared_path', 'out_path',
    'command_config', 'max_steps', 'unwitnessed', 'frontier',
    'working_directory', 'environment', 'missing_prerequisite', 'plan_schema',
])
def test_mutated_execution_plan_rejected_before_launch(tmp_path, monkeypatch, change):
    root, config, plan = fixture(tmp_path, monkeypatch)
    plan = copy.deepcopy(plan)
    chunk, snapshot = plan['command_plan'][2:4]
    if change == 'arbitrary_command': chunk['argv'] = ['UNEXPECTED_COMMAND']
    elif change == 'interpreter': chunk['argv'][0] = '/other/python'
    elif change == 'prepared_path': chunk['argv'][chunk['argv'].index('--prepared')+1] = '/other/prep'
    elif change == 'out_path': chunk['argv'][chunk['argv'].index('--out')+1] = '/other/run'
    elif change == 'command_config': chunk['argv'][chunk['argv'].index('--config')+1] = '/other/config'
    elif change == 'max_steps': chunk['argv'][-1] = '256'
    elif change == 'unwitnessed': snapshot['argv'].append('--allow-unwitnessed')
    elif change == 'frontier': snapshot['expected_completed_steps'] = 256
    elif change == 'working_directory': plan['command_working_directory'] = '/other/repo'
    elif change == 'environment': plan['command_environment_required']['PYTHONPATH'] = '/other/repo'
    elif change == 'missing_prerequisite': plan['prerequisites']['same_grid_preparation_byte_identity_required'] = False
    elif change == 'plan_schema': plan['schema'] = 'UNKNOWN'
    with pytest.raises(ValueError, match='execution plan'):
        coordinator.validate_inputs(root, config, plan)


def test_consistently_changed_config_is_not_frozen_b2(tmp_path, monkeypatch):
    root, _, plan = fixture(tmp_path, monkeypatch)
    cfg = dict(plan['config'], b=3.0)
    config = tmp_path / 'changed.json'
    config.write_text(json.dumps(cfg))
    plan['config'] = cfg
    with pytest.raises(ValueError, match='B2 config family'):
        coordinator.validate_inputs(root, config, plan)


def test_original_plan_retains_identical_argv_and_snapshot_order(tmp_path, monkeypatch):
    root, config, plan = fixture(tmp_path, monkeypatch)
    _, commands = coordinator.validate_inputs(root, config, plan)
    assert commands == plan['command_plan'][2:]
    assert [c['phase'] for c in commands] == ['collision_chunk', 'checkpoint_snapshot'] * 29
