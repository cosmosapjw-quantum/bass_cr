import json
from pathlib import Path

import pytest

from scripts import r3m28_execute as job


def test_a3_config_only_changes_requested_dt():
    cfg = job.base.read(job.CONFIG)
    assert job.validate_config(cfg)['nstep'] == 7172
    with pytest.raises(ValueError):
        job.validate_config(dict(cfg, absorber_width=4.1))
    with pytest.raises(ValueError):
        job.validate_config(dict(cfg, dt=.0125))


def test_exact_commands_and_frontier_reuse():
    commands = job.base.command_plan(job.CONFIG, Path('/tmp/r3m28-fixture'))
    assert len(commands) == 116
    collisions = [x for x in commands if x['phase'] == 'collision']
    assert len(collisions) == 57
    assert collisions[-1]['done'] == 7172 and collisions[-1]['steps'] == 4
    assert all(str(job.CONFIG) in x['argv'] for x in commands)
    assert job.base.frontier_action(57, 7168, 7172, False) == 'RUN_CHUNK'
    assert job.base.frontier_action(57, 7172, 7172, False) == 'PUBLISH_ONLY'
    assert job.base.frontier_action(57, 7172, 7172, True) == 'SKIP_VERIFIED_GENERATION'
    with pytest.raises(ValueError):
        job.base.frontier_action(57, 7000, 7172, False)


def test_plan_tamper_rejected_without_gpu(monkeypatch, tmp_path):
    monkeypatch.setattr(job.base, 'runtime_identity', lambda: {'fixture': True})
    original_sha = job.base.sha
    monkeypatch.setattr(job.base, 'sha', lambda path: job.INITIAL_SHA
                        if Path(path) == job.A1_INITIAL else original_sha(path))
    monkeypatch.setattr(job.base, 'git', lambda *args:
                        'cr/r3m28-spatial-hdt-budget-20260924' if args[0] == 'branch'
                        else 'test-commit' if args[0] == 'rev-parse' else job.PARENT)
    plan = job.build_plan(job.CONFIG, tmp_path/'A3')
    job.validate_plan(plan)
    altered = json.loads(json.dumps(plan))
    altered['commands'][2]['argv'][-1] = '256'
    with pytest.raises(ValueError, match='contract mismatch'):
        job.validate_plan(altered)
    altered = json.loads(json.dumps(plan))
    altered['config']['dt'] = .0125
    with pytest.raises(ValueError, match='contract mismatch'):
        job.validate_plan(altered)


def test_existing_output_refused_before_gpu(monkeypatch, tmp_path):
    root = tmp_path/'used'
    root.mkdir()
    contract = tmp_path/'CONTRACT.json'
    contract.write_text(json.dumps({'output_root': str(root), 'config_path': str(job.CONFIG)}))
    monkeypatch.setattr(job, 'validate_plan', lambda _: None)
    with pytest.raises(FileExistsError, match='fresh A3'):
        job.execute(contract, job.base.sha(contract))
