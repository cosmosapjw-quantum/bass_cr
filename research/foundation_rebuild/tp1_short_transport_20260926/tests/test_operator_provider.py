import numpy as np
import pytest

from bass_foundations.radial_basis import RadialSpec, atomic_bank
from bass_foundations.two_center import Trajectory, symmetric_channels
from cr_repro.observables import projectile_speed_au


def small_system():
    spec=RadialSpec(radius=16.,elements=8,degree=2,lmax=0,bound_nmax=1,
                    positive_per_l=0,positive_emax=2.,quad_order=6,grading=2.)
    ch=symmetric_channels(atomic_bank(spec))
    v=projectile_speed_au(100.)
    tr=Trajectory(((0.,0.,0.),(2.,0.,0.)),((0.,0.,0.),(0.,0.,v)))
    return tr,ch,v


def test_exact_time_cache_and_distinct_times():
    from operator_provider import OperatorProvider
    tr,ch,v=small_system()
    p=OperatorProvider(tr,ch,same_order=8,cross_order=8)
    a=p.at(-12./v)
    b=p.at(-12./v)
    assert a is b
    assert p.evaluation_count == 1
    c=p.at(-11.9/v)
    assert c is not a
    assert p.evaluation_count == 2


def test_snapshot_is_raw_finite_and_identity_bound():
    from operator_provider import OperatorProvider
    tr,ch,v=small_system()
    records=[c.record() for c in ch]
    p=OperatorProvider(tr,ch,same_order=8,cross_order=8,expected_channel_records=records)
    s=p.at(-12./v)
    for name in ('S','H','D'):
        a=getattr(s,name)
        assert a.shape==(len(ch),len(ch))
        assert np.isfinite(a).all()
        assert a.flags.writeable is False
    assert s.identity == p.identity
    assert s.channel_records == tuple(tuple(sorted(x.items())) for x in records)
    bad=list(records);bad.reverse()
    with pytest.raises(ValueError,match='channel identity'):
        OperatorProvider(tr,ch,same_order=8,cross_order=8,expected_channel_records=bad)


def test_metric_derivative_uses_direct_D_and_centered_S_difference():
    from operator_provider import OperatorProvider, metric_derivative_residual
    tr,ch,v=small_system()
    p=OperatorProvider(tr,ch,same_order=8,cross_order=8)
    t=-11./v
    eps=1e-4/v
    out=metric_derivative_residual(p,t,eps)
    assert out['epsilon_t']==eps
    assert out['relative_residual'] < 2e-5
    assert p.evaluation_count == 3
    direct=p.at(t).D+p.at(t).D.conj().T
    assert np.allclose(out['D_plus_Ddagger'],direct)


def test_operator_screen_refuses_bad_metric_without_repair(monkeypatch):
    import operator_provider as mod
    tr,ch,v=small_system()
    original=mod.assemble_full
    def broken(*args,**kwargs):
        x=original(*args,**kwargs)
        x=dict(x);x['S']=np.array(x['S'],copy=True);x['S'][0,0]=-1.
        return x
    monkeypatch.setattr(mod,'assemble_full',broken)
    p=mod.OperatorProvider(tr,ch,same_order=8,cross_order=8)
    with pytest.raises(ArithmeticError,match='metric'):
        p.at(-12./v)


def test_provider_surface_has_no_capture_api():
    from operator_provider import OperatorProvider
    assert not any('capture' in name.lower() for name in dir(OperatorProvider))
