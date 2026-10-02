import numpy as np
from reassemble_vother import reassemble

def fixture():
    d={'S':np.eye(4,dtype=complex),'D':np.zeros((4,4),complex),'H':np.zeros((4,4),complex)}
    for lab,idx in (('T',[0,1]),('P',[2,3])):
        for key in ('S','H0','A','D','H','V_other'):
            d[lab+'__'+key]=(np.eye(2,dtype=complex) if key=='S' else np.zeros((3,2,2),complex) if key=='A' else np.zeros((2,2),complex))
        d[lab+'__indices']=np.array(idx)
    return d

def test_only_V_and_H_change_with_consistent_boost():
    old=fixture();pot={'T':np.eye(2)*-.25,'P':np.eye(2)*-.3}
    new=reassemble(old,pot,[[0.,0.,0.],[0.,0.,2.]])
    assert np.array_equal(new['T__H'],pot['T'])
    assert np.array_equal(new['P__H'],pot['P']+2*np.eye(2))
    for k in old:
        if k not in ('H','T__H','P__H','T__V_other','P__V_other'):assert np.array_equal(old[k],new[k])
    assert np.array_equal(new['H'][:2,2:],old['H'][:2,2:])

def test_shape_and_order_fail_closed():
    import pytest
    old=fixture()
    with pytest.raises(ValueError):reassemble(old,{'T':np.eye(2)},[[0,0,0],[0,0,0]])
    with pytest.raises(ValueError):reassemble(old,{'T':np.eye(3),'P':np.eye(2)},[[0,0,0],[0,0,0]])
    old['P__indices']=np.array([3,2])
    with pytest.raises(ValueError):reassemble(old,{'T':np.eye(2),'P':np.eye(2)},[[0,0,0],[0,0,0]])

def test_pin_tamper_and_path_escape_refusal(tmp_path):
    import pytest
    from runtime_contract import verify_pins,sha
    p=tmp_path/'x';p.write_text('first');pins={'x':sha(p)}
    verify_pins(tmp_path,pins);p.write_text('changed')
    with pytest.raises(ValueError):verify_pins(tmp_path,pins)
    with pytest.raises(ValueError):verify_pins(tmp_path,{'../escape':'0'*64})
