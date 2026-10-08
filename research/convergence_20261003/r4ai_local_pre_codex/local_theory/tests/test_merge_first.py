import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'runtime_tools'))
from merge_returns import combine_verified

def test_disjoint_returns_keep_origin():
    groups=[{'batch_sha256':'a','packets':[{'node_id':'m64'}]},
            {'batch_sha256':'b','packets':[{'node_id':'m128'}]}]
    merged,origin=combine_verified(groups)
    assert [p['node_id'] for p in merged]==['m64','m128']
    assert origin=={'m64':'a','m128':'b'}

def test_duplicate_is_not_silently_replaced():
    with pytest.raises(ValueError,match='duplicate'):
        combine_verified([{'batch_sha256':'a','packets':[{'node_id':'m64'}]},
                          {'batch_sha256':'b','packets':[{'node_id':'m64'}]}])
