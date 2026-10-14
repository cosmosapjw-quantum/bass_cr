import pytest
from ray_parallel import compress_rays
from compressed_cohorts import CompressionHold
from threshold_rt import frozen_source

NE=(1.e-3,8.e-5,2.e-5)

@pytest.mark.parametrize('rays_n',[2,8])
def test_two_process_exactly_same_as_serial(rays_n):
    original=[[(e*(1.+j*0.0001),c) for e,c in frozen_source(16)] for j in range(rays_n)]
    opts=([32]*rays_n,[NE]*rays_n,[1.e9]*rays_n,[.99]*rays_n)
    single=compress_rays(original,*opts,event_budget=.1,heat_budget_eV=10.,workers=1)
    multi=compress_rays(original,*opts,event_budget=.1,heat_budget_eV=10.,workers=2)
    assert single==multi
    assert all(len(r[0])==32 for r in multi)
    assert all(len(x)==48 for x in original)


def test_parallel_budget_hold_preserves_all_inputs():
    arr=[frozen_source(16),frozen_source(16)]
    with pytest.raises(CompressionHold):
        compress_rays(arr,[16,32],[NE,NE],[1.e9,1.e9],[.99,.99],
                      .00001,.001,workers=2)
    assert all(len(x)==48 for x in arr)


def test_invalid_workers_inputs():
    with pytest.raises(ValueError):compress_rays([[]],[1],[NE],[0],[1],workers=0)
    with pytest.raises(ValueError):compress_rays([[]],[1],[NE],[0],[],workers=1)
