"""Prospective empirical temporal gate, with synthetic versus raw evidence separated."""
import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('r3m26_temporal',ROOT/'scripts/r3m26_temporal.py')
MOD=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MOD)


def forecasts(values,dt):
    return MOD.channel_forecasts(values[:3],dt[:3],dt[3])


def test_true_even_model_with_high_p_can_pass_heldout_gate():
    dt=[.05,.025,.0125,.00625]
    v=[.008-.01*t*t-20*t**4 for t in dt]
    out=MOD.channel_gate(v,dt,forecasts(v,dt))
    assert out['accepted']
    assert out['fine_observed_order']>2.5
    assert out['evidence_scope']=='SYNTHETIC_OR_CALLER_VALUES_NOT_RAW_EVIDENCE'
    assert out['certified_error_bound'] is None
    assert len(out['leave_one_out_even_diagnostics'])==4


def test_exact_p2_unequal_actual_step_ratios():
    dt=[.0501,.0249,.0124,.0061]
    v=[.008-.015*t*t for t in dt]
    out=MOD.channel_gate(v,dt,forecasts(v,dt))
    assert out['accepted']
    assert out['fine_observed_order']==pytest.approx(2,abs=1e-9)
    assert all(abs(x-.008)<1e-13 for x in out['infinite_step_estimates'].values())


def test_heldout_miss_can_fail_even_when_pair_and_remainder_are_small():
    dt=[.05,.025,.0125,.00625]
    v=[.008-.001*t*t for t in dt]
    frozen=forecasts(v,dt)
    frozen['single_power_old_triplet']+=1e-5
    out=MOD.channel_gate(v,dt,frozen)
    assert out['fine_pair_relative']<.001
    assert not out['accepted']
    assert out['D_hold']>=9e-6


def test_same_sign_reversal_and_no_contraction_rejected():
    dt=[.05,.025,.0125,.00625]
    old=[.0079,.008,.008002]
    f=MOD.channel_forecasts(old,dt[:3],dt[3])
    assert MOD.channel_gate(old+[.008001],dt,f)['status']=='SIGN_CHANGE_NONASYMPTOTIC'
    assert MOD.channel_gate(old+[.008005],dt,f)['status']=='NO_FINE_CONTRACTION'


def test_small_pair_does_not_hide_large_model_remainder():
    dt=[.05,.025,.0125,.00625]
    v=[.008-.00003*t**.1 for t in dt]
    out=MOD.channel_gate(v,dt,forecasts(v,dt))
    assert out['fine_pair_relative']<.001
    assert not out['accepted']
    assert out['U_t_relative']>.001


@pytest.mark.parametrize('bad',[True,False,float('nan'),float('inf'),0.,-.1])
def test_bad_probability_rejected(bad):
    with pytest.raises(ValueError):
        MOD.channel_gate([.007,.0075,.0079,bad],[.05,.025,.0125,.00625],{'a':.008})


def test_roundoff_increment_is_unresolved():
    v=[.007,.0075,.0079,.0079+1e-18]
    out=MOD.channel_gate(v,[.05,.025,.0125,.00625],MOD.channel_forecasts(v[:3],[.05,.025,.0125],.00625))
    assert out['status']=='UNRESOLVED_FINE_DIFFERENCES'
    assert not out['accepted']


def test_duplicate_nonfinite_json_keys_rejected(tmp_path):
    path=tmp_path/'bad.json'
    for text in ['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}']:
        path.write_text(text)
        with pytest.raises(ValueError): MOD.read_json(path)


def test_forecast_is_frozen_prospective_and_actual_dt_correct():
    f=MOD.freeze_forecast()
    p=f['payload']
    assert f['payload_sha256']==MOD.EXPECTED_FORECAST_PAYLOAD_SHA256
    assert p['B3']['nstep']==7172
    assert p['B3']['actual_dt']==p['rows']['B2']['actual_dt']/2
    assert p['B3']['config']['dt']==.00625
    assert f['B3_execution_status']=='NOT_RUN'
    assert f['production_admitted'] is False
    assert p['rows']['B2']['result_sha256']=='f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc'


def synthetic_raw_fixture(tmp_path):
    f=MOD.freeze_forecast(); cfg=f['payload']['B3']['config']
    raw=MOD.read_json(ROOT/MOD.B2_RESULT[0]); witness=MOD.read_json(ROOT/MOD.B2_WITNESS[0])
    raw['config']=MOD.enriched(cfg); raw['nstep']=7172
    raw['dt_actual']=f['payload']['B3']['actual_dt']
    for i,key in enumerate(('P1','P2','P3'),1):
        value=f['payload']['forecasts'][key]['even_dt2_dt4_old_triplet']
        raw['analysis']['gram_audit']['P_span_by_nmax'][str(i)]=value
    raw['analysis']['gram_audit']['P_span_nmax']=raw['analysis']['gram_audit']['P_span_by_nmax']['3']
    witness['enriched_config_hash']=MOD.config_hash(MOD.enriched(cfg))
    witness['prepared_receipt_sha256']='a'*64  # Explicit synthetic fresh-receipt fixture.
    paths=[tmp_path/name for name in ('synthetic_result.json','synthetic_witness.json','forecast.json')]
    for path, value in zip(paths,(raw,witness,f)): MOD.write_new(path,value)
    return paths,raw,witness,f


def test_raw_config_false_witness_and_metadata_mismatches_rejected(tmp_path):
    paths,raw,witness,f=synthetic_raw_fixture(tmp_path)
    raw['config']['absorber_reference_dt']=.00625
    paths[0].write_text(json.dumps(raw))
    with pytest.raises(ValueError,match='config'):MOD.evaluate_result(*paths)
    raw['config']=MOD.enriched(f['payload']['B3']['config']); paths[0].write_text(json.dumps(raw))
    witness['array_digest_match']=1; paths[1].write_text(json.dumps(witness))
    with pytest.raises(ValueError,match='Boolean'):MOD.evaluate_result(*paths)
    witness['array_digest_match']=True; witness['prepared_array_digest']='a'*64
    witness['internal_array_digest']='a'*64; paths[1].write_text(json.dumps(witness))
    with pytest.raises(ValueError,match='initial'):MOD.evaluate_result(*paths)


def test_forecast_tampering_rejected_even_with_recomputed_self_hash(tmp_path):
    paths,raw,witness,f=synthetic_raw_fixture(tmp_path)
    f['payload']['forecasts']['P1']['single_power_old_triplet']+=1e-7
    f['payload_sha256']=MOD.payload_hash(f['payload'])
    paths[2].write_text(json.dumps(f))
    with pytest.raises(ValueError,match='forecast'):MOD.evaluate_result(*paths)


def test_raw_boolean_numeric_probability_rejected(tmp_path):
    paths,raw,witness,f=synthetic_raw_fixture(tmp_path)
    raw['analysis']['gram_audit']['P_span_by_nmax']['1']=False
    paths[0].write_text(json.dumps(raw))
    with pytest.raises(ValueError):MOD.evaluate_result(*paths)


def test_relabelled_B2_preparation_receipt_rejected(tmp_path):
    paths,raw,witness,f=synthetic_raw_fixture(tmp_path)
    witness['prepared_receipt_sha256']=MOD.B2_PREPARED_RECEIPT
    paths[1].write_text(json.dumps(witness))
    with pytest.raises(ValueError,match='fresh B3 preparation'):MOD.evaluate_result(*paths)


def test_validated_synthetic_raw_evaluator_exercises_all_channels(tmp_path):
    paths,raw,witness,f=synthetic_raw_fixture(tmp_path)
    out=MOD.evaluate_result(*paths)
    assert set(out['channels'])=={'P1','P2','P3'}
    assert out['production_admitted'] is False
    assert out['certified_error_bound'] is None
    # This is explicitly a fabricated fixture, never saved as real B3 evidence.
    assert out['input_files']['result']['sha256']==MOD.sha(paths[0])


def test_no_overwrite(tmp_path):
    path=tmp_path/'out.json'; MOD.write_new(path,{'x':1}); original=path.read_bytes()
    with pytest.raises(FileExistsError):MOD.write_new(path,{'x':2})
    assert path.read_bytes()==original
