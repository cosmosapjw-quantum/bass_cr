import copy
from fractions import Fraction as F
import pytest
from tube_cli import evaluate_packet
from weak_pair import ContractError

def fixture():
    z=[['0','0']];one=[['1','0']]
    return {'schema':'R4AK_POLYNOMIAL_OPERATOR_TUBE_INPUT_V1','units':{'energy':'Eh','time':'ta','hbar':'Eh*ta'},
       'frame_connection_in_K':True,'model_origin':'EXACT_POLYNOMIAL_REFERENCE','candidate_or_fixture_identity':'TEST_ONLY_DECOUPLED',
       'hbar':'1','retained_indices':[0,1],
       'S':[[one,z,z],[z,one,z],[z,z,one]],'K':[[z,z,z],[z,z,z],[z,z,one]],
       'slabs':[{'interval':['0','1']}],'initial_state_bounds':{'error_S':'0','retained_norm_G':'1'}}

def test_exact_reference_file_contract():
    r=evaluate_packet(fixture());assert r['propagation']['state_error_upper']=='0';assert r['physical_admission'] is False

def test_missing_initial_state_is_not_zero():
    d=fixture();d['initial_state_bounds']=None;r=evaluate_packet(d);assert r['propagation'] is None

@pytest.mark.parametrize('key,value',[('schema','other'),('frame_connection_in_K',False),('model_origin','EMPIRICAL_FIT'),
                                     ('candidate_or_fixture_identity',''),('hbar',1.0),('units',{'energy':'eV','time':'s'})])
def test_wrong_contract_fields(key,value):
    d=fixture();d[key]=value
    with pytest.raises(ContractError):evaluate_packet(d)

def test_missing_remainder_is_not_zero():
    d=fixture();d['model_origin']='POLYNOMIAL_PLUS_ASSUMED_UNIFORM_REMAINDERS'
    with pytest.raises(ContractError):evaluate_packet(d)

def test_conditional_remainder_never_physical_admission():
    d=fixture();d['model_origin']='POLYNOMIAL_PLUS_ASSUMED_UNIFORM_REMAINDERS'
    d['slabs'][0]['remainders']={'epsilon_S':'1/10000','epsilon_K':'1/1000','epsilon_Sdot':'0','evidence_id':'TEST_ONLY_ASSUMPTION'}
    r=evaluate_packet(d);assert r['physical_admission'] is False;assert r['tubes'][0]['internal_measurement_rate_upper_per_ta'] is None

def test_gap_in_slabs_even_without_state():
    d=fixture();d['initial_state_bounds']=None;d['slabs'].append({'interval':['2','3']})
    with pytest.raises(ContractError):evaluate_packet(d)

def test_float_coefficients_rejected():
    d=fixture();d['S'][0][0]=[[1.0,'0']]
    with pytest.raises(ContractError):evaluate_packet(d)
