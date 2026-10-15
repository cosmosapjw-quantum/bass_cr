from fractions import Fraction
from math import isclose
import numpy as np
import pytest
from adaptive_q import PositivePacketOracle,AdaptiveQGrid
from adaptive_benchmark import current_packets,packet_truth

BUDGET=(1e-8,1e-9,1e-12,1e-7,1e-8,1e-11)
RHO=(.0017575700008892194,.0001429214010766023,0.)

def tiny():
    return PositivePacketOracle([13.6,24.,24.58,24.6,25.,55.],[.1,.2,.3,.2,.1,.1],
                                'test-positive-dyadic','single-ray',0.)

def grid(o,edges=None,ratio=1.,gas=RHO,dt=1e10):
    return AdaptiveQGrid(o,[13.6,20.,24.4,24.59,26.,55.,80.] if edges is None else edges,
                         ratio,gas,dt,BUDGET,3)

def test_fraction_exact_count_energy_partition():
    m=tiny();a,b=m.moments(13.6,24.59); c,d=m.moments(24.59,80.,True)
    assert a+c==m.total_n and b+d==m.total_u

def test_parent_only_refinement_explicitly_rejected():
    with pytest.raises(ValueError,match='oracle'):
        AdaptiveQGrid(([1,2],[3,4]),[13.6,80.],1.,RHO,1e10,BUDGET)

def test_identity_and_source_owner_required():
    with pytest.raises(ValueError):PositivePacketOracle([24.],[1.],'','ray',0.)
    with pytest.raises(ValueError):PositivePacketOracle([24.],[-1.],'s','ray',0.)
    with pytest.raises(ValueError):PositivePacketOracle([24.],[1.],'s','',0.)

def test_transactional_invalid_input():
    o=tiny()
    for edges in [[13.6,13.6,80.],[13.6,54.],[0,80],[13.6,float('nan'),80]]:
        with pytest.raises(ValueError):grid(o,edges)
    with pytest.raises(ValueError):grid(o,[13.6,24.59,80.],gas=(-.1,0,0))
    with pytest.raises(ValueError):grid(o,[13.6,24.59,80.],ratio=-1)

def test_true_packet_first_moments_and_nesting():
    a=grid(tiny());old=a.summary()
    end=a.run(12)
    assert end['cells']==12 and end['exact_dyadic_partition']
    assert end['widths'][1]<=old['widths'][1]
    assert end['mass']==old['mass'] and end['reference_energy_eV']==old['reference_energy_eV']
    assert all(x['new_cells']<=12 for x in a.trace)

def test_refinement_cutoff_splitting_priority():
    o=PositivePacketOracle([24.4,24.6],[.5,.5],'s','r',0.)
    a=grid(o,[13.6,25.],gas=(.001,.0001,0))
    assert abs(a._split_location(next(iter(a.cells.values())))-24.59)<1e-11
    out=a.run(2)
    assert out['cells']==2 and any(abs(v-24.59)<1e-11 for v in a.sorted_edges())

def test_no_double_count_boundary_packet():
    o=PositivePacketOracle([24.59,25.],[.5,.5],'s','r',0.)
    a=grid(o,[13.6,24.59,30.])
    assert sum(c.n for c in a.cells.values())==o.total_n
    assert sum(c.u for c in a.cells.values())==o.total_u

def test_one_real_source_enclosed_after_adapt():
    o,r,gas,dt=current_packets(False)
    g=AdaptiveQGrid(o,np.geomspace(13.6,433.,17),r,gas,dt,BUDGET,3)
    old=g.summary()
    a=g.run(25);truth=packet_truth(o,r,gas,dt)
    z=np.asarray(a['event']+a['heat']);assert np.all(z[:,0]<=truth+1e-25) and np.all(z[:,1]>=truth-1e-25)
    assert a['widths'][1]<=old['widths'][1]
    assert all(c.n>=0 for c in g.cells.values())

@pytest.mark.parametrize('hardened',[False,True])
def test_source_or_hardened_totals_conserved(hardened):
    o,r,gas,dt=current_packets(hardened)
    g=AdaptiveQGrid(o,np.geomspace(13.6,433.,17),r,gas,dt,BUDGET,3)
    after=g.run(20)
    assert Fraction.from_float(after['mass'])>0
    z=np.asarray(after['event']+after['heat']);t=packet_truth(o,r,gas,dt)
    assert np.all(z[:,0]<=t+1e-24) and np.all(z[:,1]>=t-1e-24)

def test_massless_gas_all_zero_and_safe():
    g=grid(tiny(),gas=(0,0,0))
    assert all(x==0 for x in g.summary()['widths'])
    assert g.run(15)['cells']>=7  # zero-score entries cannot force forbidden guesses

def test_parent_same_moments_different_child_moments():
    # Same exactly represented N=1 and U=25 eV but distinct child moments.
    a=PositivePacketOracle([25.],[1.],'one','r',0.)
    b=PositivePacketOracle([24.5,25.5],[.5,.5],'two','r',0.)
    assert a.total_n==b.total_n and a.total_u==b.total_u
    assert a.moments(24.,24.59)!=b.moments(24.,24.59)


def test_heI_focused_goal_refinement_against_uniform_on_true_packet():
    from adaptive_benchmark import HEI_FOCUS_BUDGET
    o,r,gas,dt=current_packets(False)
    adaptive=AdaptiveQGrid(o,np.geomspace(13.6,433.,65),r,gas,dt,HEI_FOCUS_BUDGET,3)
    a=adaptive.run(96)
    uniform=AdaptiveQGrid(o,np.geomspace(13.6,433.,97),r,gas,dt,BUDGET,3).summary()
    assert a['widths'][1]<uniform['widths'][1]
    assert a['mass']==uniform['mass']


def test_hardened_heI_focused_refinement_against_uniform():
    from adaptive_benchmark import HEI_FOCUS_BUDGET
    o,r,gas,dt=current_packets(True)
    a=AdaptiveQGrid(o,np.geomspace(13.6,433.,65),r,gas,dt,HEI_FOCUS_BUDGET,3).run(96)
    u=AdaptiveQGrid(o,np.geomspace(13.6,433.,97),r,gas,dt,BUDGET,3).summary()
    assert a['widths'][1]<u['widths'][1]


def test_precision_gate_and_positive_early_stop():
    from adaptive_benchmark import HEI_FOCUS_BUDGET
    o,r,gas,dt=current_packets(False)
    obj=AdaptiveQGrid(o,np.geomspace(13.6,433.,65),r,gas,dt,HEI_FOCUS_BUDGET,3)
    start=obj.summary()
    assert not start['precision_target_met']
    met=obj.run(128,stop_on_precision=True)
    assert met['precision_target_met'] and met['cells']<=128
    assert met['precision_gate']=='PASS_SCOPED'


def test_precision_hold_does_not_claim_pass_at_limit():
    from adaptive_benchmark import HEI_FOCUS_BUDGET
    o,r,gas,dt=current_packets(False)
    obj=AdaptiveQGrid(o,np.geomspace(13.6,433.,65),r,gas,dt,HEI_FOCUS_BUDGET,3)
    met=obj.run(80,stop_on_precision=True)
    assert met['precision_gate']=='HOLD_PRECISION_TARGET' and met['cells']==80
