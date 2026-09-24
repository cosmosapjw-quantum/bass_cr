import copy
import json

import pytest

from scripts import r3m27_b3_execute as b3


def test_exact_b3_family_and_geometry():
    cfg = json.loads((b3.ROOT / 'configs/r3m27/B3.json').read_text())
    b3.validate_b3_config(cfg)
    n = b3.numerical_metadata(cfg)
    assert (n['nstep'], n['chunk_count'], n['last_chunk_steps']) == (7172, 57, 4)
    assert n['actual_dt'] == pytest.approx(0.00624946176119497, abs=1e-16)
    for key, value in [('b', 2.01), ('imag_steps', 4799), ('dt', .0125)]:
        bad = copy.deepcopy(cfg)
        bad[key] = value
        with pytest.raises(ValueError):
            b3.validate_b3_config(bad)


def test_canonical_commands_and_mutation_rejected(tmp_path, monkeypatch):
    cfg_path = b3.ROOT / 'configs/r3m27/B3.json'
    monkeypatch.setattr(b3, 'runtime_identity', lambda: {'fixture': 'runtime'})
    monkeypatch.setattr(b3, 'git', lambda *args: b3.PARENT if args[0] == 'merge-base' else 'f' * 40)
    plan = b3.build_plan(cfg_path, tmp_path / 'B3')
    assert len(plan['commands']) == 116
    assert plan['commands'][2]['argv'][-1] == '128'
    assert plan['commands'][-2]['steps'] == 4
    b3.validate_plan(plan, cfg_path, tmp_path / 'B3')
    for mutation in ('argv', 'config'):
        bad = copy.deepcopy(plan)
        if mutation == 'argv':
            bad['commands'][2]['argv'][-1] = '64'
        else:
            bad['config']['dt'] = .0125
        with pytest.raises(ValueError):
            b3.validate_plan(bad, cfg_path, tmp_path / 'B3')


def test_frontier_resume_publish_only_and_reject_escape():
    assert b3.frontier_action(1, 0, 128, False) == 'RUN_CHUNK'
    assert b3.frontier_action(2, 128, 256, False) == 'RUN_CHUNK'
    assert b3.frontier_action(2, 256, 256, False) == 'PUBLISH_ONLY'
    assert b3.frontier_action(2, 256, 256, True) == 'SKIP_VERIFIED_GENERATION'
    for done in (-1, 127, 129, 257, 384):
        with pytest.raises(ValueError):
            b3.frontier_action(2, done, 256, False)
