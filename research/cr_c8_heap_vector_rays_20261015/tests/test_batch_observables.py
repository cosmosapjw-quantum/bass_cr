"""Reference parity over scientific ray inputs and threshold discontinuities."""
import math,random
import numpy as np
import pytest
from batch_observables import batch_frozen_be_readout,_cross_sections_numpy
from compressed_cohorts import frozen_be_readout
from threshold_rt import frozen_source,verner,ION_NAMES

NN=(1e-3,8e-5,2e-5)

def test_verner_vector_original_over_thresholds():
    x=np.asarray([13.599999,13.6,24.589999,24.59,54.419999,54.42,432.2293723204678,49999.])
    sigma=_cross_sections_numpy(x)
    for k,name in enumerate(ION_NAMES):
        assert np.allclose(sigma[:,k],[verner(name,e) for e in x],rtol=3e-15,atol=0)

@pytest.mark.parametrize('nrays',[1,8,32])
def test_variable_ray_neutrals_and_redshift_parity(nrays):
    rng=random.Random(100+nrays)
    base=frozen_source(16)
    rays=[[(e*(1+.003*rng.random()),cnt*rng.uniform(.1,2)) for e,cnt in base] for _ in range(nrays)]
    rays[0].extend([(432.2293723204678,.13),(24.59,.1),(54.42,.0001),(13.5,.01)])
    neutrals=[tuple(x*rng.uniform(.5,2) for x in NN) for _ in range(nrays)]
    dt=[rng.uniform(.01,2)*1e9 for _ in range(nrays)]
    red=[rng.uniform(.97,1.) for _ in range(nrays)]
    events,heat=batch_frozen_be_readout(rays,neutrals,dt,red)
    for j in range(nrays):
        sr,sh=frozen_be_readout(rays[j],neutrals[j],dt[j],red[j])
        np.testing.assert_allclose(events[j],sr,rtol=3e-13,atol=3e-17)
        np.testing.assert_allclose(heat[j],sh,rtol=3e-13,atol=3e-16)


def test_empty_and_all_below_source():
    e,h=batch_frozen_be_readout([[],[(12.,1.)]],[(0.,0.,0.),NN],[0.,1e9],[1.,.99])
    assert e.shape==(2,3) and not e.any() and not h.any()


def test_shape_domain_reject():
    with pytest.raises(ValueError):batch_frozen_be_readout([[(24.,1.)]],[(.1,.2,.3)],[],[1.])
    with pytest.raises(ValueError):batch_frozen_be_readout([[(24.,-1.)]],[NN],[1e9],[1.])
    with pytest.raises(ValueError):batch_frozen_be_readout([[(50001.,1.)]],[NN],[1e9],[1.])
    with pytest.raises(ValueError):batch_frozen_be_readout([[(25.,1.)]],[NN],[1e9],[float('nan')])
