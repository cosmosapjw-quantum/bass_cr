from pathlib import Path
import pytest
import numpy as np
import run_experiment as runner
from event_coupler import ManufacturedMicro


def test_external_native_bridge_uses_accessible_owner_api():
    native=(Path(__file__).resolve().parents[1]/'native/native_point.rs').read_text()
    assert '.evaluate_for_cell_count(' not in native, 'pub(crate) owner function is not an external API'
    assert 'prepared.evaluate(absorbers,nh,dt)' in native


def test_physical_opacity_reference_completes_without_negative_populations():
    f=runner.make_fixture(a0=.09,dx=.0001,opacity_scale=1.)
    r=runner.run_reference(f,ManufacturedMicro())
    assert min(r['photons'])>=0
    assert abs(r['energy_defect_eV_H'])<2e-10
    assert abs(r['number_defect_H'])<2e-11


def test_optical_coordinates_agree_in_resolved_weak_regime():
    f=runner.make_fixture(a0=.09,dx=.0001,opacity_scale=.001)
    old=runner.run_reference(f,ManufacturedMicro(),coordinates='population')
    new=runner.run_reference(f,ManufacturedMicro())
    assert old['fixture_sha256']==new['fixture_sha256']
    np.testing.assert_allclose(new['gas'],old['gas'],rtol=2e-10,atol=2e-12)
    np.testing.assert_allclose(new['photons'],old['photons'],rtol=2e-9,atol=2e-13)
    assert new['reference_coordinates']=='cumulative_optical_depth'


def test_strong_regime_matches_tighter_same_equations():
    f=runner.make_fixture(a0=.09,dx=.0001,opacity_scale=1.)
    a=runner.run_reference(f,ManufacturedMicro())
    b=runner.run_reference(f,ManufacturedMicro(),rtol=2e-12,atol=2e-15)
    np.testing.assert_allclose(a['gas'],b['gas'],rtol=2e-9,atol=2e-11)
    np.testing.assert_allclose(a['photons'],b['photons'],rtol=2e-7,atol=2e-13)
    assert a['photon_clipping'] is False
    assert a['min_accepted_optical_depth']>=0


def test_birth_mass_and_energy_remain_exact_same_source():
    from event_coupler import ZeroMicro
    f=runner.make_fixture(a0=.09,dx=.0001,opacity_scale=0.)
    r=runner.run_reference(f,ZeroMicro())
    np.testing.assert_allclose(r['photons'],f.amounts,rtol=2e-15,atol=0)
    np.testing.assert_array_equal(r['optical_depth'],np.zeros(len(f.q)))
    assert r['ledgers']['source_n']==sum(n for n,b in zip(f.amounts,f.birth) if b>f.x0)
    assert abs(r['number_defect_H'])<3e-17
    assert abs(r['energy_defect_eV_H'])<2e-11


def test_exact_stiff_single_absorber_in_optical_coordinates(monkeypatch):
    import math
    from event_coupler import ZeroMicro,gas_from_temperature,H,N_H0
    from run_experiment import Fixture
    a0=.09;x0=math.log(a0);dx=.01;n0=.05;A0=.8;kappa=10000.
    g=gas_from_temperature([1-A0,0.,0.],8500.,0.)
    f=Fixture(x0,dx,N_H0,0.,tuple(g),(a0*30.,),(x0,),(n0,),1.,'MANUFACTURED_EXACT_PAIR_PER_LOG_A').validate()
    def manufactured_opacity(f,x):
        return np.asarray(f.q)*np.exp(-x),np.array([[kappa*H(x),0.,0.]])
    monkeypatch.setattr(runner,'opacity',manufactured_opacity)
    r=runner.run_reference(f,ZeroMicro(),rtol=2e-11,atol=2e-14)
    d=A0-n0;surv=n0*d*np.exp(-d*kappa*dx)/(d+n0*(-np.expm1(-d*kappa*dx)))
    assert r['photons'][0]>0
    assert r['photons'][0]==pytest.approx(surv,rel=3e-8,abs=0.)
    assert r['gas'][0]==pytest.approx(1-A0+n0-surv,abs=2e-11)
    assert abs(r['energy_defect_eV_H'])<3e-10


def test_inactive_and_zero_weight_cohorts_are_structural_zeros():
    from reference_tau import reconstruct_population
    n,logs=reconstruct_population([0.,1.,2.],[100.,100.,-10.],[True,True,False])
    assert n[0]==n[2]==0.
    assert n[1]==pytest.approx(np.exp(-100.),rel=2e-15)
    assert logs[0]==logs[2]==-np.inf


def test_internal_negative_tau_is_not_a_negative_photon_or_clipping():
    from reference_tau import reconstruct_population
    n,_=reconstruct_population([1.],[-.01],[True])
    assert n[0]==pytest.approx(np.exp(.01))
    assert n[0]>1


def test_reconstruction_reports_underflow_instead_of_epsilon():
    from reference_tau import reconstruct_population
    n,logs=reconstruct_population([1.],[1000.],[True])
    assert n[0]==0 and logs[0]==-1000.


def test_invalid_log_reconstruction_rejected():
    from reference_tau import reconstruct_population
    from event_coupler import DomainError
    for args in [([-1.],[1.],[True]),([1.],[float('nan')],[True]),([1.],[-1000.],[True]),([1.],[1.,2.],[True])]:
        with pytest.raises(DomainError):reconstruct_population(*args)


def test_unknown_coordinate_is_not_silent_fallback():
    from event_coupler import DomainError
    with pytest.raises(DomainError,match='SELECTION'):
        runner.run_reference(runner.make_fixture(),ManufacturedMicro(),coordinates='nonsense')


def test_reference_evaluation_budget_stops_expensive_calls():
    from reference_tau import run_reference_tau
    from event_coupler import StepRejected
    with pytest.raises(StepRejected,match='BUDGET'):
        run_reference_tau(runner.make_fixture(dx=.0001),ManufacturedMicro(),max_evaluations=1)
