import pytest
from ray_invariants import RayLane,compress_bianchi_ray_lanes,normal_tetrad_photon_moments
from compressed_cohorts import CompressionHold
from threshold_rt import frozen_source

NN=(1e-3,8e-5,2e-5)

def mk():
    s=frozen_source(16)
    return [RayLane('R+',0.,100.,(0.,0.,1.),tuple(s)),
            RayLane('R-',0.,100.,(0.,0.,-1.),tuple(s))]


def test_opposite_ray_momentum_preserved_while_merging_per_ray():
    start=mk()
    old=normal_tetrad_photon_moments(start)
    out,cert=compress_bianchi_ray_lanes(start,[32,32],[NN,NN],[1e9]*2,[.99]*2,
                                        .1,10.,workers=2)
    now=normal_tetrad_photon_moments(out)
    assert len(out[0].cohorts)==len(out[1].cohorts)==32
    assert old[:2]==pytest.approx(now[:2],rel=5e-15)
    assert old[2]==pytest.approx(now[2],rel=5e-15,abs=2e-21)
    assert all(len(x.cohorts)==48 for x in start)
    assert out[0].ray_id=='R+' and out[1].ray_id=='R-'


def test_no_ray_angular_merge_even_if_same_energy():
    start=[RayLane('A',0.,1.,(1.,0.,0.),((20.,1.),)),
           RayLane('B',0.,1.,(0.,1.,0.),((20.,1.),))]
    out,cert=compress_bianchi_ray_lanes(start,[1,1],[NN,NN],[1e9]*2,[1.]*2)
    assert len(out)==2 and out==start


def test_bad_direction_and_duplicate_identity_rejected():
    with pytest.raises(ValueError):RayLane('A',0.,1.,(0.,0.,2.),((20.,1.),))
    start=mk(); start.append(start[0])
    with pytest.raises(ValueError,match='duplicate'):
        compress_bianchi_ray_lanes(start,[32]*3,[NN]*3,[1e9]*3,[.99]*3,.1,10.)


def test_hold_is_atomic_across_all_ray_lanes():
    start=mk();old=tuple(start)
    with pytest.raises(CompressionHold):
        compress_bianchi_ray_lanes(start,[32,16],[NN]*2,[1e9]*2,[.99]*2,
                                  1e-5,1e-4,workers=2)
    assert tuple(start)==old
