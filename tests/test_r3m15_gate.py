"""Gate semantics are tested with normalized finite-dimensional counterexamples."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import subprocess

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('gate', ROOT/'scripts/r3m15_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def identity():
    return dict(grid='g', K='k', Q='q', source='s', binding_verified=True)

def test_inconclusive_counterexample_equal_probability():
    p, theta = .008, .03
    a = np.array([np.sqrt(p), np.sqrt(1-p), 0.])
    b = np.array([np.sqrt(p), np.sqrt(1-p)*np.cos(theta), np.sqrt(1-p)*np.sin(theta)])
    d = np.linalg.norm(a-b)
    assert np.linalg.norm(a) == pytest.approx(1)
    assert np.linalg.norm(b) == pytest.approx(1)
    assert d*d == pytest.approx(2*(1-p)*(1-np.cos(theta)))
    result = gate.evaluate_pair(a[0]**2, b[0]**2, d, identity(), identity())
    assert result['a_priori_pair_certificate'] == 'INCONCLUSIVE'
    assert result['measured_capture_test'] == 'PASS_PAIR_ONLY'
    assert result['relative_measured_change'] == 0

def test_same_distance_different_projector_and_direction():
    a = np.array([np.sqrt(.008), np.sqrt(.992), 0.])
    theta = .03
    b = np.array([a[0], a[1]*np.cos(theta), a[1]*np.sin(theta)])
    d = np.linalg.norm(a-b)
    # Same states and distance, a rotated projector responds differently.
    q = np.array([1., 0., 1.])/np.sqrt(2)
    r = gate.evaluate_pair(float((q@a)**2), float((q@b)**2), d, identity(), identity())
    assert r['a_priori_pair_certificate'] == 'INCONCLUSIVE'
    assert r['measured_capture_test'] == 'FAIL_OBSERVABLE_PAIR'
    # Same phase-aligned distance, rotate toward the measured first component.
    angle = 2*np.arcsin(d/2)
    tangent = np.array([a[1], -a[0], 0.])
    c = np.cos(angle)*a + np.sin(angle)*tangent
    assert np.linalg.norm(a-c) == pytest.approx(d)
    assert c[0]**2 != pytest.approx(b[0]**2)

def test_zero_reference_is_not_relative_pass():
    r = gate.evaluate_pair(0., 0., 0., identity(), identity())
    assert r['relative_measured_change'] is None
    assert r['measured_capture_test'] == 'UNDEFINED_RELATIVE_REFERENCE_ZERO'
    assert r['a_priori_pair_certificate'] == 'UNDEFINED_RELATIVE_REFERENCE_ZERO'

@pytest.mark.parametrize('key', ['grid', 'K', 'Q', 'source', 'binding_verified'])
def test_incompatible_pair_rejected(key):
    a, b = identity(), identity()
    b[key] = False if key == 'binding_verified' else 'different'
    with pytest.raises(ValueError):
        gate.evaluate_pair(.008, .008, .001, a, b)

@pytest.mark.parametrize('p,q,d', [(float('nan'),.1,.1), (.1,float('inf'),.1), (-.1,.1,.1), (.1,1.1,.1),(.1,.1,-.1)])
def test_invalid_numbers(p,q,d):
    with pytest.raises(ValueError): gate.evaluate_pair(p,q,d,identity(),identity())

def test_historical_bytes_and_numerical_sources_unchanged():
    base = '8c7bbfce157f17b85dc9082c62c63c05fef3b294'
    paths = subprocess.check_output(['git','ls-tree','-r','--name-only',base],cwd=ROOT,text=True).splitlines()
    paths = [p for p in paths if p.startswith(('cr_repro/','docs/r3m14/','results/R3M14_'))]
    for path in paths:
        old = subprocess.check_output(['git','show',f'{base}:{path}'],cwd=ROOT)
        assert hashlib.sha256(old).digest() == hashlib.sha256((ROOT/path).read_bytes()).digest(), path

def test_small_observable_explicit_absolute_branch():
    assert gate.observable_change(0.,0.)['mode'] == 'ABSOLUTE'
    assert gate.observable_change(0.,0.)['relative_change'] is None
    assert gate.observable_change(2e-10,0.)['status'] == 'FAIL_PAIR_ONLY'

def test_nonmonotone_order_is_not_forced():
    assert gate.spatial_order(.01,.009,.0101)['observed_order'] is None
    out=gate.spatial_order(.01+.3125**2,.01+.25**2,.01+.20**2)
    assert out['observed_order'] == pytest.approx(2)
    assert out['extrapolated'] == pytest.approx(.01)
