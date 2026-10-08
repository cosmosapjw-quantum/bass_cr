"""Actual-dt scalar interpolation checks; no scientific trajectory is run."""
from pathlib import Path
import importlib.util
import json

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('r3m19_temporal_models',ROOT/'scripts/r3m19_temporal_models.py')
MOD=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def rows():
    return json.loads((ROOT/'results/R3M18/B_TEMPORAL_ANALYSIS.json').read_text())['rows']


def test_known_quadratic_quartic_independent_polynomial():
    dt=np.array([.12,.05,.02])
    values=.17+.4*dt**2+3.*dt**4
    out=MOD.even_interpolant(values.tolist(),dt.tolist())
    assert out['P_at_dt_zero']==pytest.approx(.17,abs=1e-15)
    assert out['c2_physical_au']==pytest.approx(.4,rel=1e-10)
    assert out['c4_physical_au']==pytest.approx(3.,rel=1e-10)
    assert out['three_point_fit_validates_remainder'] is False
    assert out['certified_error_bound'] is None


def test_exact_quadratic_at_unequal_step_ratios():
    dt=[.13,.061,.024]
    values=[.21-2*x*x for x in dt]
    out=MOD.single_power_model(values,dt)
    assert out['observed_order']==pytest.approx(2.,abs=1e-10)
    assert out['P_at_dt_zero']==pytest.approx(.21,abs=1e-14)
    assert out['budget_closed'] is False


def test_high_observed_order_is_possible_with_regular_even_error_terms():
    dt=[.1,.05,.025]
    values=[.2-x*x-100*x**4 for x in dt]
    out=MOD.single_power_model(values,dt)
    assert out['observed_order']>2.5
    interp=MOD.even_interpolant(values,dt)
    assert interp['P_at_dt_zero']==pytest.approx(.2)
    assert interp['c2_physical_au']==pytest.approx(-1)
    assert interp['c4_physical_au']==pytest.approx(-100)


@pytest.mark.parametrize('values,status',[([.3,.4,.35],'SIGN_CHANGE'),([.3,.31,.4],'NO_CONTRACTION'),([.3,.3,.3],'UNRESOLVED_DIFFERENCES')])
def test_single_power_does_not_force_invalid_signed_ratio(values,status):
    result=MOD.single_power_model(values,[.1,.05,.025])
    assert result['status']==status
    assert result['observed_order'] is None
    assert result['P_at_dt_zero'] is None


def test_nullspace_alters_continuum_value_while_preserving_three_samples():
    dt=np.array([.1,.05,.025]);u=(dt/dt[-1])**2
    lam=1e-5
    correction=lambda x:lam*np.prod(x-u)
    assert [correction(x) for x in u]==[0.,0.,0.]
    expected=correction(0.)
    out=MOD.even_interpolant([.2,.21,.212],dt.tolist())
    assert out['unidentified_even_degree_six']['P0_shift_per_lambda']==pytest.approx(expected/lam)
    assert out['unidentified_even_degree_six']['three_point_data_constrain_lambda'] is False


@pytest.mark.parametrize('key,value',[('norm',float('nan')),('norm',0.),('P1',-.1),('P3',2.),('actual_dt',float('inf')),('nstep',False)])
def test_invalid_row_values_are_rejected(key,value):
    data=rows();data['B2'][key]=value
    with pytest.raises(ValueError):MOD.analyze_rows(data)


def test_probability_nesting_is_required():
    data=rows();data['B2']['P1']=data['B2']['P2']+.0001
    with pytest.raises(ValueError,match='nesting'):MOD.analyze_rows(data)


def test_fixed_horizon_identity_is_required():
    data=rows();data['B2']['nstep']+=1
    with pytest.raises(ValueError,match='horizon'):MOD.analyze_rows(data)


def test_zero_probability_has_no_relative_error_or_auto_admission():
    out=MOD.channel_models([0.,0.,0.],[.1,.05,.025])
    assert out['fine_pair_relative'] is None
    assert out['assumed_second_order']['fine_error_relative'] is None
    assert out['budget_closed'] is False


def test_r3m18_values_recomputed_and_normalization_remains_diagnostic():
    out=MOD.analyze_rows(rows())
    p3=out['observables']['P3']
    assert p3['single_power']['observed_order']==pytest.approx(2.878018289926647)
    assert p3['even_dt2_dt4']['P_at_dt_zero']==pytest.approx(.008089558562378446)
    assert out['observables']['shell_n2']['single_power']['observed_order']==pytest.approx(2.45644213845)
    conditional=out['observables']['P3_divided_by_survival_norm']
    assert conditional['physical_capture_probability'] is False
    assert conditional['single_power']['observed_order']==pytest.approx(2.2075897518781717)
    assert out['production_admitted'] is False
    assert out['source_observables_overwritten'] is False


def test_output_create_only(tmp_path):
    path=tmp_path/'result.json';MOD.write_new(path,{'a':1})
    with pytest.raises(FileExistsError):MOD.write_new(path,{'a':2})
    assert json.loads(path.read_text())=={'a':1}


def test_canonical_source_identity_and_small_data_scope():
    result=MOD.analyze_file(ROOT/'results/R3M18/B_TEMPORAL_ANALYSIS.json')
    assert result['source']['sha256']==MOD.CANONICAL_SHA256
    assert result['evidence_scope']['B2_raw_state_reprojection']=='NOT_RUN'
    assert result['evidence_scope']['B2_raw_result_in_repository'] is False
