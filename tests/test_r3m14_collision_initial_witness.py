import importlib.util, json
from pathlib import Path
import numpy as np
import pytest
from cr_repro.backend import asnumpy
from cr_repro.r3m11 import ControlledTDLRunner, file_sha, source_digest
from cr_repro.util import atomic_json, atomic_npy

P = Path(__file__).resolve().parents[1] / "scripts/r3m14_collision_initial_witness.py"
spec = importlib.util.spec_from_file_location("witness", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def cfg():
    return dict(energy_keV_per_u=100., b=2., backend="numpy", dt=.05,
      grid=dict(xlim=[-2,2], ylim=[-2,2], zlim=[-2,4], dx=1.),
      z_start=-1., z_stop=1., absorber_width=1., absorber_power=.125,
      absorber_reference_dt=.05, project_nmax=1, capture_plane=1.,
      checkpoint_stride=1, initial_state="imag_time", imag_dt=.025, imag_steps=2)

def make_prepared(root, c):
    r = ControlledTDLRunner(c)
    psi, info = r.relaxed_initial()
    root.mkdir()
    atomic_npy(root / "initial.npy", asnumpy(psi))
    rec = dict(schema="BASS_CR_R3M13_PREPARATION_V1", status="COMPLETE",
      config=c, shape=list(psi.shape), dv=r.dv, source_digest=source_digest(),
      initial_state_sha256=file_sha(root / "initial.npy"), initial=info,
      environment=dict(backend=r.backend))
    atomic_json(root / "receipt.json", rec)
    return rec

def test_witness_does_not_change_one_step(tmp_path):
    c = cfg(); prep = tmp_path / "prep"; make_prepared(prep, c)
    cp = tmp_path / "c.json"; cp.write_text(json.dumps(c))
    actual = source_digest(); m.EXPECTED_SOURCE_DIGEST = actual
    plain = tmp_path / "plain"; bound = tmp_path / "bound"
    ControlledTDLRunner(c).run(plain, max_steps=1)
    m.run_bound(cp, prep, bound, 1, expected_source_digest=actual)
    np.testing.assert_array_equal(np.load(plain / "state.npy"), np.load(bound / "state.npy"))
    w = json.loads((bound / "r3m14_initial_binding.json").read_text())
    assert w["status"] == "PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED"
    assert w["numerical_state_substituted"] is False
    assert w["backend_match"] is True
    assert json.loads((bound / "state.json").read_text())["done"] == 1

def test_resume_requires_same_prepared_bytes(tmp_path):
    c = cfg(); prep = tmp_path / "prep"; make_prepared(prep, c)
    cp = tmp_path / "c.json"; cp.write_text(json.dumps(c))
    actual = source_digest(); m.EXPECTED_SOURCE_DIGEST = actual
    out = tmp_path / "run"; m.run_bound(cp, prep, out, 1, expected_source_digest=actual)
    a = np.load(prep / "initial.npy").copy(); a.flat[0] += 1e-12
    atomic_npy(prep / "initial.npy", a)
    with pytest.raises(ValueError, match="file hash"):
        m.run_bound(cp, prep, out, 1, expected_source_digest=actual)

def test_mismatched_prepared_initial_fails_before_propagation(tmp_path):
    c = cfg(); prep = tmp_path / "prep"; make_prepared(prep, c)
    cp = tmp_path / "c.json"; cp.write_text(json.dumps(c))
    actual = source_digest(); m.EXPECTED_SOURCE_DIGEST = actual
    a = np.roll(np.load(prep / "initial.npy").copy(), 1, axis=0)
    atomic_npy(prep / "initial.npy", a)
    rec = json.loads((prep / "receipt.json").read_text())
    rec["initial_state_sha256"] = file_sha(prep / "initial.npy")
    atomic_json(prep / "receipt.json", rec)
    out = tmp_path / "run"
    with pytest.raises(ValueError, match="not byte-identical"):
        m.run_bound(cp, prep, out, 1, expected_source_digest=actual)
    assert not (out / "state.json").exists()
    w = json.loads((out / "r3m14_initial_binding.json").read_text())
    assert w["status"] == "FAIL_INTERNAL_INITIAL_NOT_IDENTICAL"
