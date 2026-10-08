"""Tiny CPU state checkpoints; no physical convergence experiment."""
import json
import numpy as np
import pytest

from cr_repro.r3m11 import ControlledTDLRunner, file_sha


def config():
    return dict(energy_keV_per_u=100., b=2., backend='numpy',
        grid=dict(xlim=[-2,2], ylim=[-2,2], zlim=[-2,4], dx=1.),
        dt=.01, z_start=-1., z_stop=1., initial_state='analytic',
        absorber_width=1., absorber_power=.25, absorber_reference_dt=.05,
        checkpoint_stride=1, project_nmax=1, capture_plane=1.)


def test_completed_stride_checkpoint_survives_later_step_interrupt(tmp_path):
    runner = ControlledTDLRunner(config())
    original_step = runner.step
    calls = 0
    def interrupted(psi, t_mid):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise KeyboardInterrupt('fixture interruption after first saved stride')
        return original_step(psi, t_mid)
    runner.step = interrupted
    with pytest.raises(KeyboardInterrupt):
        runner.run(tmp_path / 'interrupted', max_steps=3)
    out = tmp_path / 'interrupted'
    assert json.loads((out/'state.json').read_text())['done'] == 1
    seal = json.loads((out/'r3m11_checkpoint_seal.json').read_text())
    assert seal['files'] == {name:file_sha(out/name) for name in ['state.json','state.npy']}
    resumed = ControlledTDLRunner(config()).run(out, max_steps=1)
    assert resumed['status'] == 'checkpoint' and resumed['done'] == 2
    ControlledTDLRunner(config()).run(tmp_path/'reference', max_steps=2)
    np.testing.assert_array_equal(np.load(out/'state.npy'), np.load(tmp_path/'reference/state.npy'))


def test_unsealed_or_changed_checkpoint_is_still_rejected(tmp_path):
    out = tmp_path/'run'
    ControlledTDLRunner(config()).run(out, max_steps=1)
    (out/'state.npy').write_bytes(b'changed')
    with pytest.raises(ValueError, match='checkpoint hash mismatch'):
        ControlledTDLRunner(config()).run(out, max_steps=1)
