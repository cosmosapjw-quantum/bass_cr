from fractions import Fraction as F
import pytest
from weak_pair import (CQ,P,I,rat,sqrt_bounds,bernstein_coefficients,rectangle,
    matrix,dagger,mmul,mscale,madd,msub,mderiv,submatrix,lower_metric,
    residual_polynomials,exact_pair_certificate,Remainders,propagate_certificates,
    ContractError,exp_upper)

E=matrix([[1,0,0],[0,1,0],[0,0,1]])
Z=matrix([[0,0,0],[0,0,0],[0,0,0]])

def moving_model(a=F(1,100),k=F(1,4),coupling=F(1,1000)):
    t=P([0,1]); M=matrix([[1,0,0],[0,1,0],[a*t,0,1]])
    H=matrix([[0,k,0],[k,0,coupling],[0,coupling,2]])
    S=mmul(dagger(M),M)
    K=msub(mmul(mmul(dagger(M),H),M),mscale(mmul(dagger(M),mderiv(M)),I))
    return S,K

@pytest.mark.parametrize('x',[True,False,float('nan'),float('inf'),'nan','1/0',None])
def test_bad_rational_rejected(x):
    with pytest.raises(ContractError): rat(x)

@pytest.mark.parametrize('x',[F(0),F(1,3),F(9,16),F(1234567,456789)])
def test_sqrt_directed_integer_inequality(x):
    lo,hi=sqrt_bounds(x)
    assert lo*lo<=x<=hi*hi
    assert hi-lo<=F(1,2**192)

def test_complex_arithmetic_exact():
    z=CQ(F(1,3),F(2,5)); w=CQ(F(-7,4),F(3,2))
    assert z*w/w==z
    assert z*z.conj()==CQ(z.abs2())

def test_polynomial_derivative_and_product():
    p=P([1,2,3]); q=P([0,I,2])
    assert (p*q).deriv()==p.deriv()*q+p*q.deriv()
    assert (p*q).value(F(1,3))==p.value(F(1,3))*q.value(F(1,3))

@pytest.mark.parametrize('poly',[P([1,2,3]),P([1,-5,3,2]),P([I,2+1j,-3])])
def test_bernstein_hull_contains_exact_values(poly):
    lo,hi,il,ih=rectangle(poly,(F(-2,3),F(3,4)))
    for j in range(31):
        t=F(-2,3)+F(j,30)*F(17,12); y=poly.value(t)
        assert lo<=y.re<=hi and il<=y.im<=ih

def test_bernstein_known_change_of_basis():
    assert bernstein_coefficients(P([0,0,1]),(0,1))==(CQ(0),CQ(0),CQ(1))
    assert bernstein_coefficients(P([0,1,-1]),(0,1))==(CQ(0),CQ(F(1,2)),CQ(0))

def test_nonhermitian_metric_is_not_projected():
    with pytest.raises(ContractError): exact_pair_certificate([[1,1,0],[0,1,0],[0,0,1]],Z,(0,1))

@pytest.mark.parametrize('r',[(0,0),(0,3),(True,1),(0,), (0,1,2)])
def test_bad_selector_rejected(r):
    with pytest.raises(ContractError): exact_pair_certificate(E,Z,(0,1),retained=r)

def test_near_singular_metric_not_silently_regularized():
    with pytest.raises(ContractError): exact_pair_certificate([[1,2,0],[2,1,0],[0,0,1]],Z,(0,1))

def test_gapless_coupling_has_a_nonzero_weak_bound():
    eps=F(1,1000)
    K=matrix([[0,0,eps],[0,0,0],[eps,0,0]])
    c=exact_pair_certificate(E,K,(0,3))
    assert eps<=F(c['residual_upper_per_ta'])<eps+F(1,10**50)
    assert c['spectral_gap_required'] is False

def test_exact_galerkin_cancellation_and_scalar_energy_gauge():
    S,K=moving_model(); _,_,_,_,_,_,N,Gamma=residual_polynomials(S,K)
    assert all(not v for row in submatrix(N,(0,1),(0,1)) for v in row)
    assert all(not v for row in Gamma for v in row)
    K2=madd(K,mscale(S,P([7,-2,3])))
    N2=residual_polynomials(S,K2)[6]
    assert N2==N
    c=exact_pair_certificate(S,K,(0,1)); c2=exact_pair_certificate(S,K2,(0,1))
    assert c['residual_upper_per_ta']==c2['residual_upper_per_ta']
    assert c['internal_measurement_rate_upper_per_ta']==c2['internal_measurement_rate_upper_per_ta']

def test_connection_omission_is_visible_not_absorbed_in_gap():
    a=F(1,100); t=P([0,1]); M=matrix([[1,0,0],[0,1,0],[a*t,0,1]])
    S=mmul(dagger(M),M); K=mscale(mmul(dagger(M),mderiv(M)),-I)
    good=exact_pair_certificate(S,K,(0,1)); bad=exact_pair_certificate(S,Z,(0,1))
    assert F(good['metric_defect_upper_per_ta'])==0
    assert F(good['residual_upper_per_ta'])>0
    assert F(bad['metric_defect_upper_per_ta'])>0
    assert F(bad['residual_upper_per_ta'])==0
    assert bad['physical_admission'] is False

def test_nonorthogonal_pair_measurement_not_coordinate_probability():
    S=matrix([[1,F(1,3),0],[F(1,3),1,0],[0,0,1]])
    c=exact_pair_certificate(S,S,(0,2))
    assert c['residual_upper_per_ta']=='0'
    assert c['internal_measurement_rate_upper_per_ta']=='0'

def test_interval_must_cover_whole_time_not_reversed():
    with pytest.raises(ContractError): exact_pair_certificate(E,Z,(2,1))

@pytest.mark.parametrize('kwargs',[{'epsilon_S':-1},{'epsilon_K':None},{'epsilon_Sdot':-1},
    {'bound_type':'QUADRATURE_DIFFERENCE'},{'bound_type':'POINT_DIAGNOSTIC'},
    {'energy_unit':'eV'},{'time_unit':'s'},{'evidence_id':''}])
def test_incompatible_remainder_not_admitted(kwargs):
    k=dict(epsilon_S=0,epsilon_K=0,epsilon_Sdot=0,evidence_id='fixture-uniform');k.update(kwargs)
    with pytest.raises(ContractError): exact_pair_certificate(E,Z,(0,1),remainders=Remainders(**k))

def test_fitted_polynomial_never_becomes_exact_operator():
    c=exact_pair_certificate(E,Z,(0,1),remainders=Remainders(F(1,100),F(1,1000),0,'conditional-ref'))
    assert c['bound_type']=='CONDITIONAL_UNIFORM_OPERATOR_REMAINDERS'
    assert F(c['residual_upper_per_ta'])>0
    assert c['physical_bridge_upper'] is None
    assert c['internal_measurement_rate_upper_per_ta'] is None

def test_remainder_that_consumes_metric_is_rejected():
    with pytest.raises(ContractError): exact_pair_certificate(E,Z,(0,1),remainders=Remainders(1,0,0,'x'))

def test_piecewise_composition_missing_slab_rejected():
    c=exact_pair_certificate(E,Z,(0,1)); d=exact_pair_certificate(E,Z,(2,3))
    with pytest.raises(ContractError): propagate_certificates([c,d])

def test_piecewise_composition_duplicate_slab_rejected():
    c=exact_pair_certificate(E,Z,(0,1))
    with pytest.raises(ContractError): propagate_certificates([c,c])

def test_piecewise_exact_zero_propagates_without_hidden_error():
    c=exact_pair_certificate(E,Z,(0,1)); d=exact_pair_certificate(E,Z,(1,2))
    out=propagate_certificates([c,d],initial_error=F(1,10))
    assert out['state_error_upper']=='1/10'
    assert out['same_observable_error_upper']=='21/100'
    assert out['physical_bridge_upper'] is None

def test_model_identity_mismatch_rejected():
    c=exact_pair_certificate(E,Z,(0,1)); d=exact_pair_certificate(E,E,(1,2))
    with pytest.raises(ContractError): propagate_certificates([c,d])

def test_growth_bound_known_series():
    import decimal
    with decimal.localcontext() as ctx:
        ctx.prec=80
        for x in [F(0),F(1,100),F(1,2),F(1),F(2)]:
            q=exp_upper(x); val=decimal.Decimal(x.numerator)/decimal.Decimal(x.denominator)
            assert decimal.Decimal(q.numerator)/decimal.Decimal(q.denominator)>=ctx.exp(val)

def test_excess_growth_is_not_clipped_to_zero():
    with pytest.raises(ContractError): exp_upper(33)
