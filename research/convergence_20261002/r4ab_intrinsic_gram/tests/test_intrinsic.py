import numpy as np
import pytest
from intrinsic_blocks import angular_sp,boost_blocks

def test_sp_angular_integrals_direct_not_projection():
    N,G=angular_sp([(0,0),(1,0),(1,1),(1,-1)])
    assert abs(N[2,0,1]-1/np.sqrt(3))<2e-16
    assert abs(G[2,0,1]-np.sqrt(3))<4e-16
    assert G[2,1,0]==0
    assert abs(N[1,0,2]+1j/np.sqrt(6))<2e-16
    assert abs(N[0,0,3]-1/np.sqrt(6))<2e-16
    assert np.count_nonzero(N[:,1:,1:])==0

def test_new_overlap_propagates_to_H_and_D():
    S=np.diag([2.,3.]); H0=np.diag([5.,7.]);V=np.diag([11.,13.]);A=np.zeros((3,2,2),complex)
    b=boost_blocks(S,H0,A,V,[0.,0.,2.])
    assert np.array_equal(b['H'],np.diag([20.,26.]))
    assert np.array_equal(b['D'],np.diag([-4j,-6j]))
    assert np.array_equal(b['H']-1j*b['D'],H0+V)

def test_raw_derivative_defect_is_retained():
    S=np.eye(2);H0=np.zeros((2,2));V=H0.copy();A=np.zeros((3,2,2),complex);A[2]=np.diag([.125,-.25])
    b=boost_blocks(S,H0,A,V,[0.,0.,2.])
    assert np.array_equal(b['D']+b['D'].conj().T,np.diag([-.5,1.]))
    assert np.array_equal(b['H']-1j*b['D']-H0-V,np.diag([.25j,-.5j]))

def test_unsupported_angular_and_bad_velocity_rejected():
    with pytest.raises(ValueError):angular_sp([(2,0)])
    with pytest.raises(ValueError):boost_blocks(np.eye(2),np.eye(2),np.zeros((3,2,2)),np.eye(2),[0.,0.,float('nan')])
