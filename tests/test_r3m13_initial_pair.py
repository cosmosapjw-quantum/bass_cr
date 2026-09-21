"""No cross sections or production simulations: mathematical and sidecar contracts."""
import copy, importlib.util, json, math
from pathlib import Path
import numpy as np
import pytest

P = Path(__file__).resolve().parents[1]/"scripts/r3m13_initial_state_pair.py"
spec = importlib.util.spec_from_file_location("r3m13_pair", P)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def test_phase_and_weight_invariance():
    a=np.array([1.,1.j])/2
    b=np.exp(.731j)*a
    out=m.ray_distance(a,b,2.)
    assert out["ray_distance"]<2e-15
    assert out["trace_distance"]<2e-15

def test_orthogonal():
    out=m.ray_distance(np.array([1.,0]),np.array([0.,1.]),1.)
    assert out["ray_distance"]==pytest.approx(math.sqrt(2))
    assert out["trace_distance"]==pytest.approx(1.)

@pytest.mark.parametrize("a,b,dv",[
    ([1,1],[1,0],1.),([1,0],[1,0,0],1.),
    ([float("nan"),0],[1,0],1.),([1,0],[1,0],0.),
    ([],[],1.)
])
def test_invalid_states(a,b,dv):
    with pytest.raises(ValueError):m.ray_distance(np.asarray(a),np.asarray(b),dv)

def test_pair_bound_zero_and_screen():
    out=m.probability_interval(.00775827737938,0.,.01)
    assert out["lower"]==pytest.approx(.00775827737938)
    assert out["upper"]==pytest.approx(.00775827737938)
    assert out["roundoff_certified"] is False
    assert out["bgrid"]=="NO_GO"
    d=m.sufficient_ray_distance(.00775827737938,.01)
    assert d==pytest.approx(.000439309877938035,rel=1e-13)
    assert m.probability_interval(.00775827737938,d*.99,.01)["floating_pair_screen"]

@pytest.mark.parametrize("p,d,s",[(-1,0,.01),(2,0,.01),(.5,-1,.01),
    (.5,2.,.01),(.5,float("nan"),.01),(.5,.1,0.)])
def test_invalid_bound_arguments(p,d,s):
    with pytest.raises(ValueError):m.probability_interval(p,d,s)

def test_zero_anchor_never_relative_pass():
    out=m.probability_interval(0.,1e-3,.01)
    assert out["lower"]==0.
    assert out["floating_pair_screen"] is False
    assert out["relative_error_upper"] is None

def test_random_contractions_obey_interval():
    rng=np.random.default_rng(17)
    for _ in range(120):
        a=rng.normal(size=5)+1j*rng.normal(size=5);a/=np.linalg.norm(a)
        b=a+.015*(rng.normal(size=5)+1j*rng.normal(size=5));b/=np.linalg.norm(b)
        u,_,vh=np.linalg.svd(rng.normal(size=(5,5))+1j*rng.normal(size=(5,5)))
        K=u@np.diag(rng.uniform(.1,1,size=5))@vh
        q,_=np.linalg.qr(rng.normal(size=(5,3))+1j*rng.normal(size=(5,3)))
        pa=float(np.linalg.norm(q.conj().T@K@a)**2)
        pb=float(np.linalg.norm(q.conj().T@K@b)**2)
        dd=m.ray_distance(a,b,1.)["ray_distance"]
        bound=m.probability_interval(pa,dd,.01)
        assert bound["lower"]-2e-14<=pb<=bound["upper"]+2e-14

def cfg():
    return dict(energy_keV_per_u=100.,b=2.,backend="numpy",dt=.05,
      grid=dict(xlim=[-2,2],ylim=[-2,2],zlim=[-2,4],dx=1.),
      z_start=-1.,z_stop=1.,absorber_width=1.,absorber_power=.125,
      absorber_reference_dt=.05,project_nmax=1,capture_plane=1.,
      initial_state="imag_time",imag_dt=.025,imag_steps=1200)

def test_config_equality_and_changed_dynamics():
    a=cfg();b=copy.deepcopy(a);b.update(imag_dt=.0125,imag_steps=2400)
    assert m.validate_pair_configs(a,b)["same_total_preparation_time"]
    b["dt"]=.025
    with pytest.raises(ValueError,match="dynamics"):m.validate_pair_configs(a,b)
    b=copy.deepcopy(a);b["imag_steps"]=2400
    with pytest.raises(ValueError,match="preparation time"):m.validate_pair_configs(a,b)

@pytest.mark.parametrize("key,value",[("imag_dt",0),("imag_steps",True),
    ("initial_state","analytic"),("imag_steps",1.1)])
def test_bad_preparation_config(key,value):
    a=cfg();a[key]=value
    with pytest.raises(ValueError):m.validate_preparation_config(a)

def test_json_duplicate_keys_rejected(tmp_path):
    p=tmp_path/"input.json";p.write_text('{"x":1,"x":2}')
    with pytest.raises(ValueError,match="duplicate"):m.load_json(p)

def test_completed_preparation_and_tamper(tmp_path):
    a=cfg();a.update(imag_steps=2,imag_dt=.025)
    out=m.prepare(a,tmp_path/"initial")
    assert out["collision_propagation_executed"] is False
    assert out["source_digest"]==m.current_source_digest()
    assert out["initial"]["stationary_residual_Eh"]>=0
    assert out["target_only"]["projectile_potential_included"] is False
    loaded=m.load_prepared(tmp_path/"initial")
    assert loaded[0].shape==(4,4,6)
    with pytest.raises(FileExistsError):m.prepare(a,tmp_path/"initial")
    (tmp_path/"initial/initial.npy").write_bytes(b"tampered")
    with pytest.raises(ValueError,match="hash"):m.load_prepared(tmp_path/"initial")
