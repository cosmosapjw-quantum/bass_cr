import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from crossing_flux import K,boundary,flux,packet_row,slab_flux

def test_column_flux_and_t0():
    g=K.make_graph(1000.001); p=K.sparse_evolve(g,0)
    np.testing.assert_allclose(flux(g,p),K.rates(1000.001),rtol=1e-15)
    assert not np.any(p[boundary(g)])

def test_exact_daughters_and_labels():
    g=K.make_graph(1000.001)
    row=packet_row(g,0,K.sparse_evolve(g,0))
    assert [(x['energy_meV'],x['m_H'],x['n_He']) for x in row['boundary']]==[(989797,1,0),(978783,0,1)]

def test_off():
    g=K.make_graph(3000,False)
    assert len(flux(g,K.sparse_evolve(g,1e13)))==0

def test_slab_channel_oracle():
    g=K.make_graph(1000.001); t=1e13; r=K.rates(g.initial_eV)
    expected=r/r.sum()*(-np.expm1(-r.sum()*t))
    np.testing.assert_allclose(slab_flux(g,0,t,32),expected,rtol=2e-11,atol=2e-11)

def test_bad_time():
    g=K.make_graph(1000.001)
    import pytest
    with pytest.raises(ValueError):slab_flux(g,1,0,16)
