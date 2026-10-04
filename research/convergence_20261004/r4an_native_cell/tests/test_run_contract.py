import json
from pathlib import Path
import pytest
from run_parity import run,ROOT
from prepare_fixture import prepare

def test_consumed_fixture_contract_does_not_reexecute_native(tmp_path):
    output=tmp_path/'consumed';output.mkdir()
    c={'schema':'R4AN_THREE_FIXTURE_RUN_V1','actual_atomic_integral_cap':0,'precision_bits':256,'pins':{},'output':str(output)}
    p=tmp_path/'used.json';p.write_text(json.dumps(c))
    with pytest.raises(FileExistsError):run(p)

def test_changed_source_pin_rejected_before_output(tmp_path):
    c={'schema':'R4AN_THREE_FIXTURE_RUN_V1','actual_atomic_integral_cap':0,'precision_bits':256,'output':str(tmp_path/'run'),'pins':{'source/weak_cell.cpp':'0'*64}}
    p=tmp_path/'contract.json';p.write_text(json.dumps(c))
    with pytest.raises(ValueError,match='source/input changed'):run(p)
    assert not (tmp_path/'run').exists()

@pytest.mark.parametrize('field,value',[('precision_bits',128),('actual_atomic_integral_cap',1),('schema','OTHER')])
def test_scope_or_precision_not_expandable(tmp_path,field,value):
    c={'schema':'R4AN_THREE_FIXTURE_RUN_V1','actual_atomic_integral_cap':0,'precision_bits':256,'pins':{},'output':str(tmp_path/'run')};c[field]=value
    p=tmp_path/'contract.json';p.write_text(json.dumps(c))
    with pytest.raises(ValueError,match='contract scope'):run(p)
    assert not (tmp_path/'run').exists()

def test_prepare_existing_path_rejected(tmp_path):
    with pytest.raises(FileExistsError):prepare(tmp_path,tmp_path/'contract.json')

def test_prepare_relative_paths_rejected(tmp_path):
    with pytest.raises(ValueError,match='absolute'):prepare('relative',tmp_path/'contract.json')
