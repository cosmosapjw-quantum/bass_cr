from fractions import Fraction as F
import numpy as np
import pytest
import gram_exact as g

def test_bubble_polynomial_preserves_nonorthogonality():
    # u=s(1-s), v=2s(1-s): norms and offdiagonal are NOT identity.
    u=g.panel_coefficients(0.,0.,[1.,0.,0.])
    v=g.panel_coefficients(0.,0.,[2.,0.,0.])
    assert u==(F(0),F(1),F(-1),F(0),F(0))
    assert g.product_integral(u,u)==F(1,30)
    assert g.product_integral(u,v)==F(1,15)

def test_endpoints_not_monomial_roundtripped():
    left,right=2.**-47,1.+2.**-49
    c=g.panel_coefficients(left,right,[.125,-.25,.5])
    assert c[0]==F(left)
    assert sum(c)==F(right)

def test_complex_product_unsupported_and_nonfinite_rejected():
    with pytest.raises((TypeError,ValueError)):g.panel_coefficients(0.,0.,[complex(1,1),0,0])
    with pytest.raises(ValueError):g.panel_coefficients(0.,np.nan,[0.,0.,0.])

def test_exact_global_integration_by_parts():
    e=np.array([0.,.125,1.]);p=np.array([[0.,.25,0.],[0.,.5,0.]])
    q=np.array([[[.5,-.25,.125],[.25,-.5,.125]],[[1.,.5,-.25],[.125,.25,.5]]])
    exact,_=g.exact_moments(e,p,q)
    assert all(exact['J'][a][b]+exact['J'][b][a]==0 for a in range(2) for b in range(2))
    assert exact['G'][0][1]!=0 and exact['G'][0][0]!=1

def test_frozen_data_cannot_be_made_writeable():
    a=g.frozen(np.eye(2))
    with pytest.raises(ValueError):a.flags.writeable=True


def test_inverse_moment_origin_cancellation():
    e=np.array([0.,1.]);p=np.zeros((1,2));q=np.array([[[1.,0.,0.]]])
    _,coeff=g.exact_moments(e,p,q);m=g.mp_inverse_moments(e,coeff,70)
    assert m['R1'][0,0]==float(F(1,12))
    assert m['R2'][0,0]==float(F(1,3))
