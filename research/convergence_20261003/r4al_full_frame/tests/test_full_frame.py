import copy
from fractions import Fraction as F
import numpy as np
import pytest
from full_frame import (ContractError, rat, sqrt_bounds, gram_tube, symmetric_bounds,
    angular_frame,h1_motion,weak_operator_norms,interval_from_dict,anchor_matrix,
    phase_correct,make_certificate,json_safe)


def mats():
    return [[F(int(i==j)) for j in range(5)] for i in range(5)]


def frame():
    return angular_frame(mats(),mats(),[0,0,0,1,1])


def iv(lo,hi):
    return {'denominator_power2':256,'lower_numerator':str(int(F(lo)*2**256)),
            'upper_numerator':str(int(F(hi)*2**256))}


def enclosure():
    return {'matrix_shape':[9,9], 'entries':[{'re':iv(0,0),'im':iv(0,0)} for _ in range(81)],
            'full_cross_radius_upper':'0'}


@pytest.mark.parametrize('x',[F(0),F(1),F(2),F(1,7),F(17,64),F(10)**30])
def test_sqrt_outward_by_exact_square(x):
    lo,hi=sqrt_bounds(x)
    assert lo*lo<=x<=hi*hi and hi-lo<=F(1,2**256)

@pytest.mark.parametrize('x',[True,1.0,complex(1,0),None])
def test_certificate_rejects_implicit_numeric_conversion(x):
    with pytest.raises(ContractError):rat(x)

@pytest.mark.parametrize('args',[(-1,), (1,1), (1,False), (1,2048)])
def test_sqrt_domain_guards(args):
    with pytest.raises(ContractError):sqrt_bounds(*args)


def test_motion_block_has_no_spurious_factor_two():
    C=np.array([[1+2j,3],[2j,-1j]])
    A=np.block([[np.zeros((2,2)),C],[C.conj().T,np.zeros((2,2))]])
    assert np.linalg.norm(A,2)==pytest.approx(np.linalg.norm(C,2),rel=1e-14)
    assert np.linalg.norm(A,'fro')==pytest.approx(2**.5*np.linalg.norm(C,'fro'))


def test_gram_extremes_have_exact_scalar_fixture():
    b=gram_tube(1,1,F(1,4),F(1,2),F(1,4))
    assert b['lower']==F(5,8) and b['upper']==F(11,8)
    assert b['condition_upper']==F(11,5)

@pytest.mark.parametrize('args',[(0,1,0,0,0),(1,0,0,0,0),(1,1,-1,0,0),(1,1,0,1,-1),(1,1,1,0,0)])
def test_gram_invalid_or_nonpositive_bounds_rejected(args):
    with pytest.raises(ContractError):gram_tube(*args)


def test_gershgorin_does_not_project_asymmetry():
    with pytest.raises(ContractError):symmetric_bounds([[1,F(1,10)],[0,1]])
    assert symmetric_bounds([[1,F(1,10)],[F(1,10),1]])==(F(9,10),F(11,10))


def test_complete_multiplet_trace_not_individual_isotropy():
    f=frame()
    assert len(f['channels'])==9
    assert f['norm_trace']==9 and f['gradient_trace_upper']==57
    assert f['z_gradient_trace_upper']==19
    assert f['channels'][3:6]==[(3,1,-1),(3,1,0),(3,1,1)]
    with pytest.raises(ContractError):angular_frame(mats(),mats(),[0,0,0,1,2])


def test_angular_orthogonality_zeros_only_different_l_or_m():
    g=mats();g[0][1]=g[1][0]=F(1,100)
    f=angular_frame(g,mats(),[0,0,0,1,1])
    assert f['G'][0][1]==F(1,100) and f['G'][3][4]==0


def test_velocity_scalings_and_phase_term():
    f=frame();m=h1_motion(f,2)
    assert m['beta_z_derivative_trace']==28
    assert m['projectile_time_derivative_trace_upper']==112
    assert m['two_centre_gradient_trace_upper']==150
    assert m['full_Sdot_operator_upper']==2*m['cross_z_Lipschitz_upper']
    with pytest.raises(ContractError):h1_motion(f,0)


def test_zero_gradient_fixture():
    o=weak_operator_norms(1,0,0)
    assert o['H_operator_upper_Eh']==0 and o['K_operator_upper_Eh']==0


def test_weak_operator_hardy_factors():
    o=weak_operator_norms(4,9,1)
    assert o['H_operator_upper_Eh']==F(57,2)
    assert o['D_operator_upper_per_ta']==2
    assert o['K_operator_upper_Eh']==F(61,2)


def test_anchor_radius_understatement_is_rejected():
    e=enclosure();e['entries'][0]['re']=iv(-F(1,8),F(1,8))
    with pytest.raises(ContractError):anchor_matrix(e)
    e['full_cross_radius_upper']='1/4'
    a=anchor_matrix(e)
    assert a['C_norm_upper']==F(1,8) and a['rectangle_radius_square_full_X']==F(1,32)


def test_anchor_shape_and_endpoint_order():
    e=enclosure();e['matrix_shape']=[18,18]
    with pytest.raises(ContractError):anchor_matrix(e)
    with pytest.raises(ContractError):interval_from_dict(iv(1,-1))
    a=iv(0,1);a['denominator_power2']=128
    with pytest.raises(ContractError):interval_from_dict(a)


def test_epoch_sign_and_exact_zero():
    m=[[(F(1),F(0))]]
    p=phase_correct(m,2,1,F(1,2))
    assert p['delta']==p['phase_error_upper']==0
    t=F(1,2)-F(1,10000)
    p=phase_correct(m,2,1,t)
    assert p['delta']==F(1,5000) and p['C_ideal_mid'][0][0][1]==-F(1,5000)
    assert p['phase_error_upper']==F(1,750000000000)
    with pytest.raises(ContractError):phase_correct(m,2,1,0)


def test_missing_science_remains_null_and_no_old_assembly_claim():
    c=make_certificate(frame(),anchor_matrix(enclosure()),2,-32,-16,[F(1,64),F(1,128)])
    assert c['physical_bridge_upper'] is None
    assert c['full_stencil_total_upper']==[None,None]
    assert c['old_numerical_metric_defect_certified_zero'] is False
    assert c['coarse_K_tube_accepted_as_small_bridge_error'] is False
    assert c['new_cross_integrals']==c['new_radial_integrals']==0
    assert json_safe(c)['windows'][0]['halfwidth_a0']=='1/64'

@pytest.mark.parametrize('hs',[[F(1,32),F(1,64)],[F(1,64)],[F(1,64),F(1,64)]])
def test_scope_expansion_and_duplicate_windows_fail(hs):
    with pytest.raises(ContractError):make_certificate(frame(),anchor_matrix(enclosure()),2,-32,-16,hs)


def test_quadrature_norm_zero_does_not_remove_h1_motion_uncertainty():
    c=make_certificate(frame(),anchor_matrix(enclosure()),2,-32,-16,[F(1,64),F(1,128)])
    assert c['windows'][0]['S_constant_reference_error_operator_upper']>0
    assert c['windows'][0]['K_zero_reference_error_operator_upper_Eh']>0
