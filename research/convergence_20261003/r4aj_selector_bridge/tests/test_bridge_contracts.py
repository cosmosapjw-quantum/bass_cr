from dataclasses import replace
from fractions import Fraction as F
import copy,json
from pathlib import Path
import numpy as np
import pytest
from bridge import *
from frames import span_projector,frame_generator
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('x',[True,False,float('inf'),float('-inf'),float('nan'),'not a number',None])
def test_non_number_bound_refused(x):
    with pytest.raises(ContractError):rational(x)
@pytest.mark.parametrize('x',[F(0),F(2),F(1,7),F(9,16),F(1,10**30)])
def test_sqrt_upper_dyadic_proof(x):
    u=sqrt_upper(x,80);assert u*u>=x
    if u:assert (u-F(1,2**80))**2<x
@pytest.mark.parametrize('bits',[True,0,7,4097,1.5])
def test_bad_precision_refused(bits):
    with pytest.raises(ContractError):sqrt_upper(2,bits)
@pytest.mark.parametrize('args',[(1,5,9),(0,2,4),(9,0,9),(2,1,18)])
def test_unequal_rank_distance(args):assert exact_projector_rank_distance(*args)==1
@pytest.mark.parametrize('args',[(1,1,9),(0,0,4),(4,4,4)])
def test_equal_rank_does_not_determine_distance(args):assert exact_projector_rank_distance(*args) is None
@pytest.mark.parametrize('args',[(-1,1,4),(5,1,4),(1.0,1,4),(True,1,4),(0,0,0)])
def test_bad_rank_refused(args):
    with pytest.raises(ContractError):exact_projector_rank_distance(*args)

def pair():return [[1,0],[0,1]],[[-2,F(1,10)],[F(1,10),1]]
@pytest.mark.parametrize('bad',['asymmetry','metric','alpha','gap','complement','shape'])
def test_invalid_gap_premises_refused(bad):
    S,H=pair();alpha,beta=F(-1),F(1,2)
    if bad=='asymmetry':H[0][1]=F(1,3)
    elif bad=='metric':S[0][0]=-1
    elif bad=='alpha':alpha=-3
    elif bad=='gap':beta=alpha
    elif bad=='complement':H[1][1]=F(-2)
    elif bad=='shape':S=[[1,0,0],[0,1,0],[0,0,1]]
    with pytest.raises(ContractError):stored_ground_gap(S,H,alpha,beta)

def test_zero_residual_has_zero_mapping_error():
    q=stored_ground_gap([[1,0],[0,1]],[[-2,0],[0,1]],-1,0)
    assert q['raw_trial_to_stored_ground_projector_upper']=='0'
    assert q['physical_candidate_operator_error_included'] is False

def test_identical_centers_do_not_provide_rank_one_gap():
    S,H=pair();d=doubled_reference_discriminator(stored_ground_gap(S,H,-1,0))
    assert d['single_measurement_to_full_complement_gap']=='0'
    assert d['pair_to_rest_gap_lower']=='1'
    assert d['finite_separation_gap_lower'] is None

def test_no_fake_gap_admission():
    with pytest.raises(ContractError):doubled_reference_discriminator({'verified':True,'bound_type':'FLOAT_DIAGNOSTIC'})

def bound():return BlockBounds(1,F(1,1000),0,0,10,1,'synthetic-constant-H')

def test_exact_action_bound_and_units():
    q=clustered_action_bound(bound())
    assert F(q['primitive_upper'])==F(1,500)
    assert F(q['state_distance_upper'])==F(101,50000)
    assert q['whole_physical_bridge_upper'] is None
    assert q['resonant_internal_transfer_included_in_error'] is False
@pytest.mark.parametrize('change',[{'gap':0},{'hbar':0},{'coupling':-1},{'coupling_derivative':-1},{'duration':-1},{'diagonal_derivative_sum':-1},{'bound_type':'POINTWISE'},{'bound_type':'EMPIRICAL'},{'frame_connection_included':False},{'energy_unit':'eV'},{'time_unit':'s'},{'evidence_id':''}])
def test_invalid_continuous_action_contract(change):
    with pytest.raises(ContractError):clustered_action_bound(replace(bound(),**change))
@pytest.mark.parametrize('change',[{'duration':0},{'coupling':0,'coupling_derivative':0}])
def test_zero_action(change):assert clustered_action_bound(replace(bound(),**change))['state_distance_upper']=='0'
@pytest.mark.parametrize('slot',range(4))
def test_missing_bridge_link_stays_missing(slot):
    v=[F(1,100)]*4;v[slot]=None
    assert probability_bridge_total(*v)['upper'] is None

def test_reference_transfer_cannot_be_dropped():
    q=probability_bridge_total(1,F(1,1000000),0,0)
    assert q['upper']=='1'
    assert reference_transfer_upper(F(1,4),4,1)==1

def test_negative_link_refused():
    with pytest.raises(ContractError):probability_bridge_total(None,-1,0,0)

def test_semantic_channels_and_permutation():
    m={'identity':'c','modes':[{'l':0,'principal_n':1,'identity':'g','energy':-1},{'l':0,'principal_n':2,'identity':'e','energy':F(-1,4)}]}
    r={'candidate':'c','channel_order':[[1,0,0],[0,0,0]]}
    s=select_channels(m,r)
    assert s['measurement_projectile_1s']==[3]
    assert s['dynamic_target_projectile_1s']==[1,3]
@pytest.mark.parametrize('bad',['identity','duplicate','wrong_l','wrong_m','missing_1s'])
def test_semantic_mismatch_refused(bad):
    m={'identity':'c','modes':[{'l':0,'principal_n':1,'identity':'g','energy':-1}]}
    r={'candidate':'c','channel_order':[[0,0,0]]}
    if bad=='identity':r['candidate']='d'
    elif bad=='duplicate':r['channel_order']*=2
    elif bad=='wrong_l':r['channel_order'][0][1]=1
    elif bad=='wrong_m':r['channel_order'][0][2]=1
    elif bad=='missing_1s':m['modes'][0]['principal_n']=2
    with pytest.raises(ContractError):select_channels(m,r)

def test_overlap_pair_projector_is_not_sum_of_singletons():
    S=np.array([[1,.3,0],[.3,1,0],[0,0,1.]])
    J=np.eye(3)[:,:2];p=span_projector(S,J)
    naive=span_projector(S,J[:,:1])+span_projector(S,J[:,1:])
    assert np.linalg.norm(p@p-p)<1e-14
    assert np.linalg.norm(naive@naive-naive)>.1
@pytest.mark.parametrize('S,J',[([[1,2],[2,1]],[[1],[0]]),([[1,0],[0,1]],[[1,1],[0,0]]),([[1,1],[0,1]],[[1],[0]])])
def test_bad_metric_or_selector_refused(S,J):
    with pytest.raises(ContractError):span_projector(S,J)

def test_frame_connection_restores_static_hamiltonian():
    t=.7;M=np.diag([np.exp(t/3),np.exp(-t/5)]).astype(complex)
    Md=np.diag([M[0,0]/3,-M[1,1]/5])
    h=np.array([[.2,.1],[.1,.7]],complex)
    H=M.conj().T@h@M;D=M.conj().T@Md
    got=frame_generator(H,D,M,Md,1.)
    assert np.linalg.norm(got-h)<1e-14
    missing=frame_generator(H,D,M,np.zeros((2,2)),1.)
    assert np.linalg.norm(missing-missing.conj().T)>.1
