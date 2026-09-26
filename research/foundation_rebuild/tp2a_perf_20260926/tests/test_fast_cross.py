import numpy as np
import pytest
from bass_foundations.radial_basis import RadialSpec, atomic_bank
from bass_foundations.two_center import Trajectory, symmetric_channels
from aligned_cross import cross_blocks
from fast_cross import fast_cross

@pytest.fixture(scope='module')
def basis():
    b=atomic_bank(RadialSpec(radius=10.,elements=6,degree=4,lmax=1,bound_nmax=2,positive_per_l=1))
    return symmetric_channels(b),b[0].edges

@pytest.mark.parametrize('z',[-4.,0.,3.])
def test_raw_six_blocks_match_frozen_reference(basis,z):
    ch,e=basis
    tr=Trajectory(((.3,-.4,.5),(2.3,-.4,z+.5)),((.12,-.07,.03),(.05,.2,1.1)))
    t=.21
    ref=cross_blocks(tr,ch,e,t,order=8)
    got=fast_cross(tr,ch,e,t,order=8,batch=97)
    for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt'):
        np.testing.assert_allclose(got[k],ref[k],atol=2e-12,rtol=2e-10,err_msg=k)


def test_fast_path_does_not_repeat_generic_point_evaluator(basis,monkeypatch):
    ch,e=basis
    import aligned_cross
    def forbidden(*args,**kwargs):raise AssertionError('generic per-point evaluator was called')
    monkeypatch.setattr(aligned_cross,'basis_values',forbidden)
    got=fast_cross(Trajectory(((0,0,0),(2,0,-4)),((0,0,0),(0,0,2))),ch,e,0.,order=6)
    assert np.isfinite(got['H_tp']).all()

@pytest.mark.parametrize('batch',[1,19,1024])
def test_batching_and_channel_order_do_not_change_answer(basis,batch):
    ch,e=basis;rng=np.random.default_rng(3);per=rng.permutation(len(ch));shuffled=tuple(ch[i] for i in per)
    tr=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,1.4)))
    got=fast_cross(tr,shuffled,e,.17,order=4,batch=batch);ref=cross_blocks(tr,shuffled,e,.17,order=4)
    for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt'):np.testing.assert_allclose(got[k],ref[k],atol=2e-12,rtol=2e-10)

@pytest.mark.parametrize('order,batch',[(True,64),(1,64),(65,64),(6,0),(6,True),(6,4097)])
def test_invalid_execution_parameters_fail(basis,order,batch):
    ch,e=basis
    with pytest.raises(ValueError):fast_cross(Trajectory(((0,0,0),(2,0,0))),ch,e,0,order=order,batch=batch)

def test_disjoint_support_is_exact_zero(basis):
    ch,e=basis;got=fast_cross(Trajectory(((0,0,0),(25,0,0))),ch,e,0)
    for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt'):assert np.count_nonzero(got[k])==0

def test_coincident_centers_rejected(basis):
    with pytest.raises(ValueError,match='coincident'):fast_cross(Trajectory(((0,0,0),(0,0,0))),*basis,0)

def test_higher_l_not_silently_dropped():
    from bass_foundations.two_center import Channel
    b=atomic_bank(RadialSpec(radius=15,elements=6,lmax=2,bound_nmax=3))
    ch=symmetric_channels(b)
    with pytest.raises(ValueError,match='s.p only'):fast_cross(Trajectory(((0,0,0),(2,0,0))),ch,b[0].edges,0)
