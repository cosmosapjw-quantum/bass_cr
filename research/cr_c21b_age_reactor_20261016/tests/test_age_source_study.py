from pathlib import Path
import json,math,sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from c21b_age_reactor import PhotonReactor,initial_state,hubble
from independent_mono import solve_continuous_mono


def load_study():
    return json.loads((ROOT/'evidence/STUDY.json').read_text())


def test_manufactured_continuous_source_real_second_order():
    d=load_study()['cases']['manufactured_const_sigma']
    errors=d['radau']['errors']
    assert len(errors)==5
    assert all(errors[i]>errors[i+1] for i in range(len(errors)-1))
    assert 1.9<d['radau']['last_effective_orders'][-1]<2.1
    assert errors[-1]<2.5e-8


def test_study_ledgers_for_all_cases():
    d=load_study()['cases']
    assert set(d)=={'smooth_real_verner','manufactured_const_sigma','native_opacity_stiff'}
    for row in d.values():
        assert row['max_abs_number_ledger']<1e-12
        assert row['max_abs_energy_ledger_ev_H']<1e-10
        for pt in row['data']:
            assert pt['N_end']>=0
            assert pt['U_end_ev_H']>=0
            assert pt['source_N']>0
            assert all(e>=0 for e in pt['species_events_per_H'])
            assert all(q>=0 for q in pt['species_heat_ev_H'])
            assert pt['Tgas_K']>0


def test_original_Verner_data_time_difference_not_certified():
    d=load_study()['cases']['smooth_real_verner']['adjacent_thermal_differences']
    # Comparisons reach small absolute differences; do not require artificial
    # idealized asymptotic order at near-roundoff resolution.
    assert len(d)==4
    assert max(d)<2e-11


def test_matched_source_budget_noncommutation_of_birth_ages():
    z=load_study()['age_matched_birth_counterexample']
    assert abs(z['source_N_diff'])<=1e-17
    assert abs(z['source_U_diff'])<=1e-15
    a=z['age_GL2'];b=z['midpoint_collapse']
    assert a['crossings'][2]==1
    assert b['crossings'][2]==0
    assert abs(z['delta_HeII_events_per_total_H'])>1e-6
    assert abs(z['delta_Tgas_K'])>10
    for r in (a,b):
        assert abs(r['number_residual'])<1e-13
        assert abs(r['energy_residual_ev_per_H'])<1e-11


def test_independent_reference_reproducible_with_new_process():
    x0=math.log(1/12)
    start=initial_state(x0,8500.,(.2,.2,.01),((80.,.004),))
    r=PhotonReactor(energy_nodes=1,source_scale=2.,opacity_scale=1e-4)
    r.spectrum=[(80.,1.)]
    sig=(1e-18,3e-18,5e-18)
    r.sigma=lambda j,e:sig[j]
    out=r.advance(start,x0+.015,16)
    reference=solve_continuous_mono(start,x0+.015)['final']
    assert abs(out.number_photons()-reference[0])<1.5e-7
    assert abs(out.thermal_ev-reference[7])<1.5e-7
    assert start.x==x0  # read-only caller input
