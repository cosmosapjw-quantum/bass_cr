"""Independent scope-matched C21 scientific and numeric controls."""
import math
import json
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad
from src.c21_reference import (
    A_REF,BIND,HEL_Y,FIT,H,C_CM_S,EV_ERG,Moment,
    birth_quadrature,c20_to_pr150,pr150_to_c20,
    physical_energy_from_pr150,threshold_q_pr150,epoch_gas,fractions,
    per_absorber_rust_input,verner_sigma,source_rate_per_H,native_spectral_cells,
    powerlaw_hazard,continuum_packet,independent_packet_ivp,
    threshold_partition,dt_x,
)
from run_study import source_integral,source_shape_study,main


def test_q_roundtrip_and_three_physical_epochs():
    q=np.array([A_REF*13.60, A_REF*24.59, A_REF*54.42, A_REF*100.])
    expected=q/A_REF
    np.testing.assert_allclose(c20_to_pr150(q),expected,rtol=1e-15)
    np.testing.assert_allclose(pr150_to_c20(expected),q,rtol=1e-15)
    for a in [A_REF,.08873654701704167,.2]:
        np.testing.assert_allclose(physical_energy_from_pr150(expected,a),q/a,rtol=1e-15)
        np.testing.assert_allclose(threshold_q_pr150(a),FIT*a/A_REF,rtol=1e-15)


def test_moment_support_and_physical_energy():
    m=Moment(3,A_REF*(25+60+90),A_REF*25,A_REF*90).check()
    n,q,lo,hi=m.in_pr150()
    assert n==3
    assert lo==25 and hi==90
    np.testing.assert_allclose(q,(25+60+90))
    for a in [A_REF,.18]:
        assert abs(q*A_REF/a-m.energy(a))<1e-12
    with pytest.raises(ValueError): Moment(1,1,2,3).check()
    with pytest.raises(ValueError): Moment(1,1,-1,3).check()


def test_helium_nuclei_not_neutral_hydrogen():
    g=(.2,.15,.1)
    fr=fractions(g)
    np.testing.assert_allclose(fr,[.8,HEL_Y*.75,HEL_Y*.15])
    gas=epoch_gas(.1,1.9e-7,1.9e-7*HEL_Y)
    assert gas['nH_total_cm3']>gas['nH_total_cm3']*fr[0]
    assert abs(gas['nHe_total_cm3']/gas['nH_total_cm3']-HEL_Y)<1e-14
    assert gas['Tcmb_K']==pytest.approx(27.255)
    assert epoch_gas(.05,1.9e-7,1.9e-7*HEL_Y)['nH_total_cm3'] == pytest.approx(8*gas['nH_total_cm3'])
    with pytest.raises(ValueError): fractions((.3,.8,.3))


def test_c19_native_photo_input_volume_conversion():
    g=(.2,.15,.1);f=fractions(g);dt=1e10;nh=2e-4
    events=np.array([1e-5,2e-6,3e-7]);heat=np.array([2e-4,5e-5,1e-6])
    gamma,heatpower=per_absorber_rust_input(events,heat,g,dt)
    np.testing.assert_allclose(gamma*f,events/dt,rtol=1e-14)
    np.testing.assert_allclose(heatpower*f,heat*EV_ERG/dt,rtol=1e-14)
    np.testing.assert_allclose(nh*gamma*f,nh*events/dt,rtol=1e-14)
    assert np.all(gamma>=0) and np.all(heatpower>=0)
    with pytest.raises(ValueError):per_absorber_rust_input(events,heat,(1,.15,.1),dt)
    with pytest.raises(ValueError):per_absorber_rust_input([0,0,1],[0,0,1],(0,0,0),dt)


@pytest.mark.parametrize('i',range(3))
def test_original_verner_fitted_threshold_and_positive_heat(i):
    t=FIT[i]
    assert verner_sigma(np.nextafter(t,0),i)==0
    assert verner_sigma(t,i)>0
    assert verner_sigma(t,i)*(t-BIND[i])>=0
    assert verner_sigma(120,i)<verner_sigma(60,i) if i==2 else verner_sigma(120,i)<verner_sigma(40,i)


def test_verner_rejects_invalid_energy():
    for e in (-1,float('nan'),5e4+1):
        with pytest.raises(ValueError):verner_sigma(e,0)


def test_constant_flrw_e_cubed_opacity_before_cutoff():
    a0=A_REF;Ebirth=60.;q=a0*Ebirth;nh0=1.9e-7
    f=fractions((.1,.2,.3))
    lam=powerlaw_hazard(q,nh0,f,[8e-18,1.2e-18,1.5e-18])
    for a in [a0,a0*1.015,a0*1.05]:
        E=q/a
        actual=C_CM_S*nh0*a**(-3)*f*np.array([8e-18,1.2e-18,1.5e-18])*(E/FIT)**(-3)
        np.testing.assert_allclose(actual,lam,rtol=2e-15)
    # At q/a < a species threshold its actual hazard is exactly zero.
    assert len(threshold_partition(q,a0,a0*1.25))==3
    with pytest.raises(ValueError):threshold_partition(q,a0,a0)


@pytest.mark.parametrize('Ebirth,scale',[ (60.,1.20),(25.,1.06),(14.,1.07) ])
def test_closed_positive_packet_vs_independent_radau(Ebirth,scale):
    a0=A_REF;a1=a0*scale;q=a0*Ebirth;n0=2e-6;nh0=1.9e-7/50
    f=fractions((.3,.2,.1))
    result=continuum_packet(q,a0,a1,n0,nh0,f)
    ivp=independent_packet_ivp(q,a0,a1,n0,nh0,f)
    assert result['crossings']>=1
    assert result['n_end']>=0 and result['n_end']<=n0
    assert np.all(result['event_per_H']>=0)
    assert np.all(result['heat_ev_H']>=0)
    np.testing.assert_allclose(sum(result['event_per_H'])+result['n_end'],n0,atol=2e-20)
    np.testing.assert_allclose(result['event_per_H'],ivp[1:4],atol=1e-16)
    np.testing.assert_allclose(result['heat_ev_H'],ivp[4:7],atol=5e-15)
    assert abs(result['work_ev_H']-ivp[7])<2e-17
    assert abs(result['energy_defect'])<5e-15


def test_native_source_age_quadrature_vs_independent_quad():
    x0=math.log(A_REF);x1=x0+.12
    assert len(birth_quadrature(x0,x1,1.9e-7,'GL2'))==2
    for observable in ['N','U']:
        ref=source_integral(x0,x1,observable,'QUAD')
        m=source_integral(x0,x1,observable,'MID')
        gl=source_integral(x0,x1,observable,'GL2')
        assert abs(gl/ref-1)<5e-5
        assert abs(gl-ref)<abs(m-ref)/100
        assert ref>0
    with pytest.raises(ValueError):source_rate_per_H(1./24,1.9e-7)


def test_positive_birth_gl2_vs_mid_and_native_source_support():
    x0=math.log(A_REF);x1=x0+.02
    gl=birth_quadrature(x0,x1,1.9e-7,'GL2')
    assert all(a>=A_REF and a<math.exp(x1) and w>0 for a,w in gl)
    native=native_spectral_cells(16)
    assert len(native)==48
    assert min(c['frac'] for c in native)>0
    assert sum(c['frac'] for c in native)==pytest.approx(1,abs=2e-15)
    assert min(c['lo'] for c in native)>=13.6
    assert max(c['hi'] for c in native)<=100+1e-13


def test_default_spectrum_shape_bias_is_quantified_not_assumed_zero():
    s=source_shape_study(16)
    np.testing.assert_allclose(s['sigma_rel_centroid_minus_GL8'],
        [-.0005960317518041158,-.00037089476862239845,-.0005828673783730975],atol=1e-12)
    assert s['heat_coeff_rel_centroid_minus_GL8'][2]>.004
    assert s['max_source_centroid_difference_eV']<1e-7


def test_spectral_resolution_reduces_discrepancy_without_proving_continuum_order():
    s16=source_shape_study(16);s32=source_shape_study(32);s64=source_shape_study(64)
    for i in range(3):
        a=abs(s16['heat_coeff_rel_centroid_minus_GL8'][i])
        b=abs(s32['heat_coeff_rel_centroid_minus_GL8'][i])
        c=abs(s64['heat_coeff_rel_centroid_minus_GL8'][i])
        assert a>b>c
        assert 3.5<a/b<4.5 and 3.5<b/c<4.5


def test_same_n_q_support_different_HeII_observable():
    E=np.array([50.,55.,60.]);wA=np.array([.5,0,.5]);wB=np.array([.2,.6,.2])
    assert wA.sum()==wB.sum()==1
    assert np.dot(E,wA)==np.dot(E,wB)==55
    assert E[0]==50 and E[-1]==60
    sigma=np.array([verner_sigma(e,2) for e in E])
    assert abs(np.dot(wA,sigma)-np.dot(wB,sigma))>5e-19
    # Both distributions have true positive endpoints and the same full support.
    assert wA[0]>0 and wA[-1]>0 and wB[0]>0 and wB[-1]>0


def test_clock_transform_and_invalid_epoch_inputs():
    a0=A_REF;a1=.09
    dt=dt_x(math.log(a0),math.log(a1))
    assert dt>0
    assert dt_x(math.log(a0),math.log(a0))==0
    with pytest.raises(ValueError):dt_x(math.log(a1),math.log(a0))
    with pytest.raises(ValueError):epoch_gas(-.1,1.9e-7,HEL_Y*1.9e-7)


def test_saved_raw_benchmark_machine_readable():
    p=Path(__file__).resolve().parents[1]/'evidence'/'RESULT.json'
    d=json.loads(p.read_text())
    assert d['schema']=='C21_COMMON_Q_SOURCE_AGE_SANDBOX_V1'
    assert len(d['source_cell_shape_comparison'])==5
    assert d['owner_PR150']=='4e2f0682fb605c6aa940bd756d9869e67b6ded0b'
    assert d['native_c21_rust_execution']=='NOT_RUN'


def test_combined_positive_gl2_birth_and_powerlaw_attenuation():
    from src.c21_reference import frozen_source_age_step
    x0=math.log(A_REF);x1=x0+.02
    result=frozen_source_age_step(x0,x1,1.9e-7,(.3,.2,.1),source_scheme='GL2',subdivisions=1)
    assert result['birth_packets']==6
    assert result['source_N']>0
    assert result['end_N']>=0
    assert np.all(result['events_per_H']>=0) and np.all(result['heat_eV_H']>=0)
    assert result['work_eV_H']>=0
    assert abs(result['number_defect'])<2e-18
    assert abs(result['energy_defect'])<2e-14
    # A genuine source-age packet calculation conserves first moments even
    # though this synthetic E^-3 model is not the original Verner chemistry.
    assert abs(result['source_U_ev_H']-result['end_U_ev_H']-sum(result['heat_eV_H'])
               -result['binding_eV_H']-result['work_eV_H'])<2e-14


def test_stiff_optical_depth_requires_positive_optical_clock_not_x_quad():
    from src.c21_reference import frozen_source_age_step
    x0=math.log(A_REF);x1=x0+.02
    gl=frozen_source_age_step(x0,x1,1.9e-7,(.3,.2,.1),'GL2',1)
    mid=frozen_source_age_step(x0,x1,1.9e-7,(.3,.2,.1),'MID',1)
    assert abs(gl['energy_defect'])<2e-14
    assert abs(mid['energy_defect'])<2e-14
    assert gl['source_N']!=mid['source_N']
    assert abs(gl['number_defect'])<1e-17
