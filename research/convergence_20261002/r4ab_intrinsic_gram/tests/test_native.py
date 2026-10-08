from fractions import Fraction as F
import os
import numpy as np
import pytest
from native import Native
from gram_exact import exact_moments

@pytest.fixture(scope='module')
def kernel():return Native(os.environ['R4AB_NATIVE_MANIFEST'])

def test_fixed_panel_analytic_bubble(kernel):
    e=np.array([0.,1.]);ep=np.zeros((2,2));q=np.zeros((2,1,3));q[:,0,0]=[1.,2.]
    m=kernel.moments(e,ep,q,32)
    for key,value in [('G',F(1,30)),('R1',F(1,12)),('R2',F(1,3)),('T',F(1,3))]:
        assert np.allclose(m[key],float(value)*np.array([[1,2],[2,4]]),atol=3e-15,rtol=0)
    assert np.max(abs(m['J']))<3e-16
    assert np.array_equal(m['G'],m['G'].T)
    assert np.array_equal(m['G'],kernel.moments(e,ep,q,32)['G'])

def test_five_point_gram_matches_exact(kernel):
    e=np.array([0.,.25,1.]);ep=np.array([[0.,.375,0.],[0.,.25,0.]])
    q=np.array([[[.5,-.25,.125],[.25,-.5,.125]],[[1.,.5,-.25],[.125,.25,.5]]])
    exact,_=exact_moments(e,ep,q);actual=kernel.moments(e,ep,q,5)
    assert np.max(abs(actual['G']-np.array(exact['G'],float)))<2e-16
    assert np.max(abs(actual['J']-np.array(exact['J'],float)))<4e-16

def test_native_rejects_bad_inputs(kernel):
    e=np.array([0.,1.]);ep=np.zeros((1,2));q=np.zeros((1,1,3))
    with pytest.raises(ValueError):kernel.moments(e,ep,q,4)
    with pytest.raises(ValueError):kernel.moments(e,ep,q,True)
    with pytest.raises(ValueError):kernel.moments(e[::-1].copy(),ep,q,5)
    ep[0,0]=.5
    with pytest.raises(ValueError):kernel.moments(e,ep,q,5)
