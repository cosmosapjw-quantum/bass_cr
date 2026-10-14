"""Direct red-green parity and physical/transactional tests of heap versus frozen scan."""
import math
import random
import pytest
from compressed_cohorts import CompressedCohortTransport,CompressionHold,frozen_be_readout
from fast_compression import HeapCompressedCohortTransport
from threshold_rt import frozen_source

NN=(1e-3,8e-5,2e-5)


def compare(initial,cap,ratio=.99,ebudget=.01,hbudget=1.,dt=1e9):
    a=CompressedCohortTransport(initial,cap)
    b=HeapCompressedCohortTransport(initial,cap)
    outputs=[]
    for obj in (a,b):
        try:outputs.append(('PASS',obj.compress(NN,dt,ratio,ebudget,hbudget)))
        except CompressionHold as err:outputs.append(('HOLD',str(err)))
    assert outputs[0][0]==outputs[1][0]
    if outputs[0][0]=='HOLD':
        assert a.cohorts==b.cohorts==list(initial)
        assert a.last_certificate is b.last_certificate is None
        return
    # Strict same algorithmic choices, same moment arithmetic and same bounds.
    assert a.cohorts==b.cohorts
    assert outputs[0][1]==outputs[1][1]
    for r in (1.,(1.+ratio)/2,ratio):
        assert frozen_be_readout(a.cohorts,NN,dt,r)==frozen_be_readout(b.cohorts,NN,dt,r)


@pytest.mark.parametrize('axis,cap',[ (8,16),(16,32),(32,80),(64,160),(128,320)])
def test_source_resolutions_identical_greedy(axis,cap):
    compare(frozen_source(axis),cap)


@pytest.mark.parametrize('seed',[0,1,2,3,4,42,404])
def test_random_safe_and_challenging_cases(seed):
    rng=random.Random(seed)
    base=frozen_source(16)
    # Multiplicative counts and redshift-ratio stress.
    array=[(e,rng.uniform(.25,2.0)*n) for e,n in base]
    for cap in (48,40,32,24,16):
        compare(array,cap,rng.choice((1.,.995,.99,.975)),
                rng.choice((.01,.1,1.)),rng.choice((1.,10.,100.)))


def test_equal_energy_ties_and_zero_budget():
    compare([(25.,.1)]*20,2,1.,0.,0.)
    compare([(20.,.2),(20.,.1),(21.,.1),(22.,.1)],2,1.,1.,10.)


def test_above_100eV_same_source07_bound():
    compare([(400.,.15),(415.,.1),(432.2293723204678,.25)],2,.99,1.,100.)


def test_injected_repeated_old_vs_new_four_steps():
    aa=CompressedCohortTransport.frozen_source(16,max_cohorts=32)
    bb=HeapCompressedCohortTransport.frozen_source(16,max_cohorts=32)
    assert aa.compress(NN,1e9,.995,.05,10.)==bb.compress(NN,1e9,.995,.05,10.)
    for i in range(4):
        assert aa.redshift(.997)==bb.redshift(.997)
        assert aa.absorb_backward_euler(NN,1e9)==bb.absorb_backward_euler(NN,1e9)
        src=[(e,.1*n) for e,n in frozen_source(16)]
        assert aa.inject_and_compress(src,NN,1e9,.995,.05,10.)==bb.inject_and_compress(src,NN,1e9,.995,.05,10.)
        assert aa.cohorts==bb.cohorts


def test_forecast_crossing_holds():
    compare([(24.8,.1),(25.2,.2)],1,.98,1.,10.)
    compare([(13.65,.1),(13.8,.1)],1,.98,1.,10.)


def test_absorption_and_redshift_clear_certificate():
    b=HeapCompressedCohortTransport.frozen_source(16,max_cohorts=32)
    b.compress(NN,1e9,.99,.01,1.)
    assert b.last_certificate is not None
    b.redshift(.999)
    assert b.last_certificate is None
    b.compress(NN,1e9,.99,.01,1.)
    b.absorb_backward_euler(NN,1e9)
    assert b.last_certificate is None
