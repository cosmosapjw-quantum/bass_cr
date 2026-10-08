from fractions import Fraction as F
import pytest
from cr_reion.core import ContractError
from cr_reion.closure import compose_chain,oscillatory_integral_bound

def edge(a,b,u='1/100'):
    return dict(left=a,right=b,quantity='P_1s_fixed_b',unit='1',upper=u,
                bound_type='DETERMINISTIC_CONDITIONAL',evidence_sha256=['a'*64])

def test_adjacent_chain_sums_real_links():
    r=compose_chain([edge('physical','finite_window'),edge('finite_window','computed')],
                    quantity='P_1s_fixed_b',unit='1',target='1/10')
    assert r['upper']=='1/50'
    assert r['physical_admission'] is False

def test_nonstationary_phase_bound_has_boundary_and_derivative_terms():
    assert oscillatory_integral_bound(2,3,7,11,13,17,5)==F(1789,25)

@pytest.mark.parametrize('kind',['EMPIRICAL','RSS','D_RESIDUAL','LITERATURE_PRECEDENT'])
def test_non_bounds_rejected(kind):
    e=edge('a','b');e['bound_type']=kind
    with pytest.raises(ContractError):compose_chain([e],quantity='P_1s_fixed_b',unit='1',target=1)

def test_missing_bound_not_zero():
    r=compose_chain([edge('a','b'),edge('b','c',None)],quantity='P_1s_fixed_b',unit='1',target=1)
    assert r['upper'] is None and r['within_target'] is None and r['known_partial_sum']=='1/100'

@pytest.mark.parametrize('es',[[edge('a','b'),edge('a','c')],[edge('a','b'),edge('b','a')],[edge('a','a')],[]])
def test_bad_comparison_chain_rejected(es):
    with pytest.raises(ContractError):compose_chain(es,quantity='P_1s_fixed_b',unit='1',target=1)

@pytest.mark.parametrize('key,value',[('unit','m^2'),('quantity','sigma'),('upper','-1'),('evidence_sha256',[])])
def test_invalid_bound_packet_rejected(key,value):
    e=edge('a','b');e[key]=value
    with pytest.raises(ContractError):compose_chain([e],quantity='P_1s_fixed_b',unit='1',target=1)

def test_target_miss_preserved():
    r=compose_chain([edge('a','b','1/10')],quantity='P_1s_fixed_b',unit='1',target='1/100')
    assert r['within_target'] is False

def test_phase_gap_zero_is_obstruction():
    with pytest.raises(ContractError,match='PHASE_GAP'):oscillatory_integral_bound(1,1,1,1,0,0,0)

def test_phase_constant_amplitude_exact_integral_within_bound():
    import cmath
    w=3.;T=2.
    actual=abs((cmath.exp(1j*w*T)-1)/(1j*w))
    assert actual<=float(oscillatory_integral_bound(1,1,2,1,0,0,3))

def test_endpoint_exceeds_supremum_rejected():
    with pytest.raises(ContractError):oscillatory_integral_bound(3,1,2,2,1,0,3)
