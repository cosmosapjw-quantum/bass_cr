"""Scientific tests for distribution-free moment-sufficient rate/heat bounds."""
import math
import numpy as np
import pytest
from scipy.optimize import linprog
from moment_envelopes import (
    make_template, threshold_occupation_bounds, _hull, _hull_at,
    _curvature_upper, _response_interval,
)
from source_subcells import source_quadrature, source_and_reaction, reference_edges, reaction_fraction
from threshold_rt import ATOMIC

RHO=(0.0017575700008892194,0.0001429214010766023,0.)
DT=1.e10
EMITTED=4.298036114764196e-8

@pytest.mark.parametrize('support,m,threshold,expected',[
    ((23,24),23.5,24.59,(0.,0.)),
    ((25,28),25.1,24.59,(1.,1.)),
    ((24,25.1),24.55,24.59,(0.,(24.55-24)/(.59+24-24))),
    ((24,24.59),24.59,24.59,(1.,1.)),
])
def test_threshold_moment_extrema(support,m,threshold,expected):
    ans=threshold_occupation_bounds(*support,m,threshold)
    assert ans==pytest.approx(expected,abs=1e-13)

@pytest.mark.parametrize('support,m,threshold',[
    ((24,25.1),22,24.59),((0,25),24,24.59),((24,25),26,24.59)
])
def test_invalid_moments(support,m,threshold):
    with pytest.raises(ValueError):threshold_occupation_bounds(*support,m,threshold)


def test_exact_convex_envelopes_parabola():
    x=[0.,.25,.5,.75,1.]
    y=[v*v for v in x]
    low=_hull(x,y,False);up=_hull(x,y,True)
    assert _hull_at(low,.5,False)<=.25
    assert _hull_at(up,.5,True)>=.5
    assert len(low)==len(x) and len(up)==2


def test_duplicate_jump_kept_extremally():
    x=[1.,2.,2.,3.]
    y=[0.,0.,1.,1.]
    assert _hull_at(_hull(x,y,False),2.,False)<=0.
    assert _hull_at(_hull(x,y,True),2.,True)>=1.


def test_nonidentifiable_helium_event():
    # Identical mass and energy, different true HeI reaction due spectral cutoff.
    x=np.array([24.,24.55,25.1])
    g,_=reaction_fraction(x,RHO,DT)
    assert g[1,1]==0. and g[1,0]==0. and g[1,2]>0.
    t=make_template((24.,25.1),RHO,DT,6)
    a=t.evaluate(1.,24.55)['event'][1]
    assert a[0]<=0. and a[1]>=.5*g[1,2]


def test_zero_species_exact_zero():
    x=make_template((23.,26.),(0.,0.,0.),DT,5).evaluate(1.,24.55)
    assert x['event']==((0.,0.),)*3
    assert x['heat']==((0.,0.),)*3


@pytest.mark.parametrize('n', [64,128,256,512])
def test_real_source_within_distribution_free_bounds(n):
    q=source_quadrature(n,order=8)
    counts,energy=q.number_and_energy()
    edges=reference_edges(n)
    true=source_and_reaction(q,RHO,DT,EMITTED)
    totals=np.zeros((6,2))
    for i in np.flatnonzero(counts>0):
        t=make_template((float(edges[i]),float(edges[i+1])),RHO,DT,4)
        v=t.evaluate(float(counts[i]*EMITTED),float(energy[i]/counts[i]))
        for j in range(3):
            totals[j]+=v['event'][j];totals[j+3]+=v['heat'][j]
    actual=np.concatenate((true['absorb_species'].sum(axis=1),true['heat_species'].sum(axis=1)))
    assert np.all(totals[:,0]<=actual+1e-28)
    assert np.all(actual<=totals[:,1]+1e-28)
    assert true['number_residual']<1e-19
    assert abs(true['energy_residual_eV'])<1e-17


@pytest.mark.parametrize('lo,hi,ion',[
    (24.59,24.9,1),(54.42,54.8,2),(26.,26.5,1),(13.6,14.,0),
])
def test_verified_curvature_encloses_numerical_derivatives(lo,hi,ion):
    # Independent high precision finite differencing is a diagnostic, not the proof.
    t=make_template((lo,hi),(.001,.0001,.00002),DT,6)
    for heat in (False,True):
        M=float(_curvature_upper(lo,hi,(.001,.0001,.00002),DT,ion,heat))
        for center in np.linspace(lo+0.2*(hi-lo),hi-0.2*(hi-lo),3):
            h=(hi-lo)*0.002
            y=[float(_response_interval(float(center+d),(.001,.0001,.00002),DT,ion,heat,frozenset()).a) for d in (-h,0,h)]
            approximation=abs((y[2]-2*y[1]+y[0])/h**2)
            assert approximation<=M*1.001+1e-9


@pytest.mark.parametrize('cut,mean',[(24.59,24.5),(24.59,24.59),(54.42,54.6)])
def test_spectral_threshold_error_not_silently_smoothed(cut,mean):
    t=make_template((cut-.4,cut+.5),(.001,.0001,.00002),DT,5)
    v=t.evaluate(.3,mean)
    for a,b in v['event']+v['heat']:
        assert a>=0 and b>=a and math.isfinite(b)


def test_fixed_support_many_unknown_nonthermal_spectra():
    rng=np.random.default_rng(3041)
    neutrals=(.001,.0001,.00005)
    t=make_template((24.,26.),neutrals,DT,7)
    for _ in range(40):
        xx=np.r_[rng.uniform(24,24.59,12),rng.uniform(24.59,26,12)]
        ww=rng.random(len(xx));ww/=ww.sum()
        e=float(ww@xx)
        bounds=t.evaluate(1.,e)
        frac,_=reaction_fraction(xx,neutrals,DT)
        for k in range(3):
            obs=float(ww@frac[k]);low,up=bounds['event'][k]
            assert low<=obs<=up
            h=float(ww@(frac[k]*(xx-[13.598434599702,24.587389011,54.41776][k])))
            lo,hi=bounds['heat'][k]
            assert lo<=h<=hi


def test_vectorized_preview_matches_scalar_without_certifying_float():
    rho=(.001,.0001,.00002)
    t=make_template((25.,27.),rho,DT,6)
    xx=np.linspace(25,27,100)
    masses=np.linspace(.3,1.,100)
    fast=t.vector_preview(masses,xx)
    for i in (0,17,47,77,99):
        z=t.evaluate(float(masses[i]),float(xx[i]))
        for k in range(3):
            assert fast['event_lower'][k,i]==pytest.approx(z['event'][k][0],rel=3e-13,abs=1e-14)
            assert fast['event_upper'][k,i]==pytest.approx(z['event'][k][1],rel=3e-13,abs=1e-14)


def test_discrete_lp_reference_for_one_piecewise_polyline():
    x=np.linspace(0.,1.,17)
    y=np.sin(x*2.2)**2
    t=.37
    A=np.vstack([np.ones(len(x)),x])
    for sign in (1.,-1.):
        out=linprog(sign*y,A_eq=A,b_eq=[1,t],bounds=(0,None),method='highs')
        assert out.success
        hull=_hull(x.tolist(),y.tolist(),upper=(sign==-1.))
        got=_hull_at(hull,t,upper=(sign==-1.))
        if sign==1:assert got<=out.fun+1e-13
        else:assert got>=-out.fun-1e-13


def test_transactional_invalid_template_inputs():
    for s in [(24.,24.),(0.,26.),(24.,60000.),(float('nan'),25.)]:
        with pytest.raises(ValueError):make_template(s,RHO,DT)
    with pytest.raises(ValueError):make_template((24,26),(-.001,0,0),DT)
    with pytest.raises(ValueError):make_template((24,26),RHO,-1)
    with pytest.raises(ValueError):make_template((24,26),RHO,DT,1)


def test_support_entirely_below_hei_cannot_photoionize_hei():
    t=make_template((23.1,24.3),(.001,.0002,.00005),DT)
    result=t.evaluate(1.,23.9)
    assert result['event'][1]==(0.,0.)
    assert result['heat'][1]==(0.,0.)


def test_mixed_age_hardened_stock_enclosed_at_new_gas_state():
    from moment_benchmark import mixed_age
    v=mixed_age(128)
    assert v['two_ages_no_BB_reclosure']
    for lo,exact,hi in zip(v['event_lower'],v['event_truth'],v['event_upper']):
        assert lo<=exact<=hi
    for lo,exact,hi in zip(v['heat_lower'],v['heat_truth'],v['heat_upper']):
        assert lo<=exact<=hi


def test_reference_ratio_changes_support_not_original_spectrum():
    from moment_envelopes import enclose_q_bins
    for ratio in (.97,1.):
        q=source_quadrature(64,ratio_R=ratio)
        N,U=q.number_and_energy()
        v=enclose_q_bins(reference_edges(64),N*EMITTED,U*EMITTED,ratio,RHO,DT,4)
        true=source_and_reaction(q,RHO,DT,EMITTED)
        assert v['event'][1,0]<=true['absorb_species'][1].sum()<=v['event'][1,1]
        assert v['heat'][0,0]<=true['heat_species'][0].sum()<=v['heat'][0,1]


def test_wrong_q_support_is_rejected_not_silently_clipped():
    from moment_envelopes import enclose_q_bins
    edges=[13.6,15.,18.]
    with pytest.raises(ValueError):enclose_q_bins(edges,[1.,0.],[40.,0.],1.,RHO,DT)
    with pytest.raises(ValueError):enclose_q_bins(edges,[0.,0.],[1.,0.],1.,RHO,DT)
    with pytest.raises(ValueError):enclose_q_bins(edges,[1.,0.],[14.,0.],0.,RHO,DT)


def test_serial_parallel_identical_outward_ends():
    from parallel_moments import parallel_enclose_q_bins
    q=source_quadrature(64)
    N,U=q.number_and_energy()
    values=[]
    for workers in (1,2):
        values.append(parallel_enclose_q_bins(reference_edges(64),N*EMITTED,U*EMITTED,1.,RHO,DT,4,workers))
    for k in ('event','heat'):
        assert np.array_equal(values[0][k],values[1][k])
