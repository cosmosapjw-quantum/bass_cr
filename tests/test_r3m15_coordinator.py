import copy
import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('coordinator',ROOT/'scripts/r3m15_coordinator.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

@pytest.mark.parametrize('job',['A','B','C'])
def test_matrix_configs(job):
    cfg=json.loads((ROOT/'configs/r3m15'/f'{job}.json').read_text())
    mod.validate_config(job,cfg)
    assert cfg['imag_dt']*cfg['imag_steps']==30

@pytest.mark.parametrize('key,value',[('b',3),('energy_keV_per_u',50),('dt',.025),('backend','auto'),('imag_steps',2400),('absorber_power',.2)])
def test_no_silent_matrix_drift(key,value):
    cfg=json.loads((ROOT/'configs/r3m15/A.json').read_text());cfg[key]=value
    with pytest.raises(ValueError):mod.validate_config('A',cfg)

def test_no_fourth_collision():
    with pytest.raises(ValueError):mod.validate_config('D',{})

def test_corrupt_checkpoint_stops(tmp_path):
    (tmp_path/'state.npy').write_bytes(b'corrupt')
    (tmp_path/'r3m11_checkpoint_seal.json').write_text(json.dumps({'source_digest':mod.SOURCE,'files':{'state.npy':'0'*64}}))
    with pytest.raises(ValueError):mod.verify_seal(tmp_path)

def test_seal_source_mismatch_stops(tmp_path):
    (tmp_path/'r3m11_checkpoint_seal.json').write_text(json.dumps({'source_digest':'wrong','files':{}}))
    with pytest.raises(ValueError):mod.verify_seal(tmp_path)

def test_declared_budget_is_separate_from_free_headroom():
    assert mod.memory_stop_reason(13000,24576,500,10000*1024**2)=='DECLARED_JOB_MEMORY_BUDGET_BREACH'
    assert mod.memory_stop_reason(24000,24576,500,None)=='RESOURCE_HEADROOM_BREACH'
    assert mod.memory_stop_reason(6000,24576,500,10000*1024**2) is None
