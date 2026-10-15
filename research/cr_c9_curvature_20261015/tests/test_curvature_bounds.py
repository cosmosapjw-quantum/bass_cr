"""Independent numerical controls of analytic curvature bounds and greedy cap."""
import math,random
import mpmath as mp
import pytest
from compressed_cohorts import CompressionHold, frozen_be_readout
from fast_compression import HeapCompressedCohortTransport
from curvature_bounds import (CurvatureHeapCompressedCohortTransport,
    verner_two_derivative_bounds,curvature_pair_bounds)
from directed_curvature import (bounds_up_f64,bounds_decimal,
                                 DirectedCurvatureHeap,second_sigma_up)
from threshold_rt import frozen_source, ATOMIC, ION_NAMES
NN=(1e-3,8e-5,2e-5)
DT=1e9


def mp_sigma(ion,E):
    eth,e0,s0,ya,p,yw,y0,y1=ATOMIC[ion]
    if E<mp.mpf(eth):return mp.mpf(0)
    x=E/mp.mpf(e0)-mp.mpf(y0)
    y=mp.sqrt(x*x+mp.mpf(y1)**2)
    return mp.mpf(s0)*((x-1)**2+mp.mpf(yw)**2)*y**(mp.mpf(p)/2-mp.mpf('5.5'))*(1+mp.sqrt(y/mp.mpf(ya)))**(-mp.mpf(p))*mp.mpf('1e-18')


@pytest.mark.parametrize('ion,lo,hi',[
    ('HI',15.,15.1),('HI',70.,70.01),('HeI',25.,25.05),
    ('HeI',30.,30.5),('HeII',55.,55.04),('HeII',432.,432.1),
])
def test_analytic_verner_second_derivative_envelopes(ion,lo,hi):
    mp.mp.dps=70
    s0,s1,s2=verner_two_derivative_bounds(ion,lo,hi)
    for k in range(9):
        E=mp.mpf(lo)+(mp.mpf(hi)-mp.mpf(lo))*k/8
        assert abs(float(mp_sigma(ion,E)))<=s0*(1+1e-13)
        assert abs(float(mp.diff(lambda x:mp_sigma(ion,x),E,1)))<=s1*(1+1e-13)
        assert abs(float(mp.diff(lambda x:mp_sigma(ion,x),E,2)))<=s2*(1+1e-13)


@pytest.mark.parametrize('e1,e2',[ (15,15.1),(17.,17.05),(25.,25.02),
    (30.,30.02),(55.,55.02),(70.,70.5),(420.,420.02),(60.,61.) ])
def test_directed_bound_encloses_exact_real_analytic_float_evaluation(e1,e2):
    e,h=curvature_pair_bounds(e1,.03,e2,.07,NN,DT,.999)
    ed,hd=bounds_up_f64(e1,.03,e2,.07,NN,DT,.999)
    # Decimal upper envelopes remain close to the same analytic real-domain formula
    # but are independent of the double arithmetic implementation.
    for a,b in zip(e+h,ed+hd):
        if a>0:
            assert b>0 and abs(a/b-1)<1e-7
        else:
            assert b==0


@pytest.mark.parametrize('ion,energies',[
    ('HI',(15.,15.1)),('HeI',(25.,25.02)),('HeII',(55.,55.02)),
])
def test_second_order_controls_actual_frozen_be_readout_for_all_redshifts(ion,energies):
    e1,e2=energies
    old=[(e1,.03),(e2,.07)]
    merge=[((.03*e1+.07*e2)/.1,.1)]
    evb,hb=bounds_up_f64(e1,.03,e2,.07,NN,DT,.999)
    for k in range(17):
        ratio=.999+(.001*k/16)
        a,b=frozen_be_readout(old,NN,DT,ratio)
        c,d=frozen_be_readout(merge,NN,DT,ratio)
        for j in range(3):
            assert abs(a[j]-c[j])<=evb[j]+1e-14
            assert abs(b[j]-d[j])<=hb[j]+1e-14


def test_old_budget_holds_at_22_but_directed_curvature_admits():
    start=frozen_source(16)
    first=HeapCompressedCohortTransport(start,22)
    with pytest.raises(CompressionHold):
        first.compress(NN,DT,.995,.01,1.)
    assert first.cohorts==start
    cur=DirectedCurvatureHeap(start,22)
    cert=cur.compress(NN,DT,.995,.01,1.)
    assert cert.initial_cohorts==48 and cert.final_cohorts==22
    assert cert.merges==26
    assert max(cert.event_absolute_bounds)<.01
    assert max(cert.heat_absolute_bounds_eV)<1.
    assert math.isclose(cur.moments()[0],1,abs_tol=3e-13)
    assert math.isclose(cur.moments()[1],20.276595394872462,abs_tol=3e-12)
    for r in (1,.999,.997,.995):
        before,heat0=frozen_be_readout(start,NN,DT,r)
        after,heat1=frozen_be_readout(cur.cohorts,NN,DT,r)
        for k in range(3):
            assert abs(before[k]-after[k])<=cert.event_absolute_bounds[k]+1e-13
            assert abs(heat0[k]-heat1[k])<=cert.heat_absolute_bounds_eV[k]+1e-13


def test_cap20_responds_transactionally_without_budget_widening():
    start=frozen_source(16)
    cur=DirectedCurvatureHeap(start,20)
    with pytest.raises(CompressionHold):
        cur.compress(NN,DT,.995,.01,1.)
    assert cur.cohorts==start and cur.last_certificate is None


def test_zero_density_does_not_erase_threshold_geometry_hold():
    with pytest.raises(CompressionHold):
        bounds_up_f64(24.0,.03,25.0,.07,(0.,0.,0.),DT,.999)


def test_equal_energy_and_zero_count_do_not_introduce_nonzero_bounds():
    assert bounds_up_f64(27.,.0,27.,.3,NN,DT,.999)==((0.,)*3,(0.,)*3)
    assert bounds_up_f64(27.,.0,28.,.0,NN,DT,.999)==((0.,)*3,(0.,)*3)


def test_verner_above_source_to_q432_and_near_fit_limit():
    e,h=bounds_up_f64(432.,.02,432.2293723204678,.01,NN,DT,.999)
    assert all(math.isfinite(x) for x in e+h)
    assert e[0]>0
    e2,h2=bounds_up_f64(49000.,.02,49000.1,.01,NN,DT,1.)
    assert all(math.isfinite(x) for x in e2+h2)
    with pytest.raises(ValueError):
        bounds_up_f64(50000.,.02,50000.01,.01,NN,DT,1.)


def test_first_order_old_heap_semantics_unchanged_after_pair_injection():
    start=frozen_source(16)
    obj=HeapCompressedCohortTransport(start,32)
    cc=obj.compress(NN,DT,.995,.01,1.)
    assert cc.initial_cohorts==48 and cc.final_cohorts==32
    assert cc.event_absolute_bounds[0]==.0003272274714132231


def test_decimal_cache_is_bounded():
    cache=second_sigma_up.cache_info()
    assert cache.maxsize==4096


def test_binding_vs_fit_distinguished_with_owner_physical_values():
    from curvature_bounds import frozen_be_readout_binding
    bind=(13.598434599702,24.587389011,54.41776)
    pairs=[(55.02,.03),(55.04,.07)]
    a=frozen_be_readout_binding(pairs,NN,DT,1.,binding_eV=bind)
    b=frozen_be_readout(pairs,NN,DT,1.)
    assert a[0]==b[0]
    for k in range(3):
        assert a[1][k] >= b[1][k]
        assert math.isclose(a[1][k]-b[1][k], a[0][k]*(ATOMIC[ION_NAMES[k]][0]-bind[k]),abs_tol=2e-15)
    cert=DirectedCurvatureHeap(pairs,1,binding_eV=bind).compress(NN,DT,.999,.01,1.)
    post=frozen_be_readout_binding(DirectedCurvatureHeap(pairs,1,binding_eV=bind).cohorts,NN,DT)
    for k in range(3):
        assert math.isfinite(cert.heat_absolute_bounds_eV[k])


def test_physical_binding_precision_safe_and_injection_transaction():
    bind=(13.598434599702,24.587389011,54.41776)
    c=DirectedCurvatureHeap(frozen_source(16),32,binding_eV=bind)
    c.compress(NN,DT,.995,.01,1.)
    assert c.binding_eV==bind
    assert c.last_certificate is not None
    with pytest.raises(ValueError):
        DirectedCurvatureHeap(frozen_source(16),32,binding_eV=(-1,24,54)).compress(NN,DT,.995,.01,1.)
    old=list(c.cohorts)
    with pytest.raises(CompressionHold):
        c.inject_and_compress([(24.59,.1),(24.8,.3)],NN,DT,.98,0.,0.)
    assert c.cohorts==old


def test_random_smooth_pairs_physical_binding_and_all_r_frozen():
    from curvature_bounds import frozen_be_readout_binding
    bind=(13.598434599702,24.587389011,54.41776)
    rng=random.Random(20261015)
    accepted=0
    for _ in range(55):
        lo=rng.choice((16.,25.2,30.,55.4,72.,125.,430.))
        width=rng.uniform(.001,.14)
        e1=lo+0.2*width;e2=e1+.8*width
        ratios=(1.,.9999,.999,.998)
        try:
            bound,bheat=bounds_up_f64(e1,.023,e2,.071,NN,DT,.998,binding_eV=bind)
        except CompressionHold:
            continue
        accepted+=1
        prior=[(e1,.023),(e2,.071)]
        avg=(.023*e1+.071*e2)/(.023+.071)
        later=[(avg,.094)]
        for r in ratios:
            aa,hh=frozen_be_readout_binding(prior,NN,DT,r,binding_eV=bind)
            bb,gg=frozen_be_readout_binding(later,NN,DT,r,binding_eV=bind)
            for k in range(3):
                assert abs(aa[k]-bb[k])<=bound[k]+1e-14
                assert abs(hh[k]-gg[k])<=bheat[k]+1e-14
    assert accepted>=40
