from fractions import Fraction as F
import pytest
from test_cubature import constant_s_fixture
from weak_kernel import Context,Cell
from cubature import Budget,entry_enclosure

def test_deterministic_union_collection_and_checkpoint():
    c=constant_s_fixture();ct=Context(3,4,0,0);cells=[Cell('origin_T',0,4),Cell('origin_P',4,0)];records=[]
    result=entry_enclosure(c,cells,ct,(0,0,0,0),absolute_target=F(1,1000),degree=8,max_depth=0,budget=Budget(132),checkpoint=records.append)
    assert result['target_met'] and result['root_cells']==2 and result['accepted_cells']==2
    assert result['evaluations']==132 and [x['root_cell'] for x in records]==[0,1]
    expected=2*(-F(1,8)**2/2-F(1,8)**3/15)
    assert result['values']['K_TP'].re.contains(expected)
    assert result['coverage']=='COMPLETE_COVER_SINGLE_ENTRY_NOT_FULL_MATRIX'

def test_depth_failure_preserves_no_false_complete_result():
    c=constant_s_fixture();records=[]
    with pytest.raises(RuntimeError,match='depth'):
        entry_enclosure(c,[Cell('origin_T',0,4)],Context(3,4,0,0),(0,0,0,0),absolute_target=F(1,10**50),degree=8,max_depth=0,budget=Budget(66),checkpoint=records.append)
    assert records==[]

@pytest.mark.parametrize('target',[F(0),F(-1)])
def test_nonpositive_total_tolerance_rejected(target):
    with pytest.raises(ValueError):
        entry_enclosure(constant_s_fixture(),[Cell('origin_T',0,4)],Context(3,4,0,0),(0,0,0,0),absolute_target=target,budget=Budget(100))
