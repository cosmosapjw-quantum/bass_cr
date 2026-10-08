from fractions import Fraction as F
import copy,hashlib,json,math
import numpy as np
import pytest
from cr_reion.core import *
from cr_reion.provider import *
from cr_reion.kinetics import *
from cr_reion.bianchi import *
from cr_reion.metric import metric_defect

def objects():
    source={'schema':'CX_LINEAR_MODEL_V1','source_id':'SYNTHETIC_NOT_ATOMIC',
      'profile':'MODEL','reaction':REACTION,'energy_kind':'E_CM_J','sigma_unit':'m^2',
      'interpolation':'PIECEWISE_LINEAR_MODEL_FAMILY','energies':['0','25'],
      'sigma_envelopes':[['1','2'],['1','2']]}
    event={'schema':'CX_DISCRETE_EVENT_V1','event_id':'SYNTHETIC_EVENT',
      'origin':'model_defined','frame':'gas_tetrad','time':'proper_seconds',
      'measure':MEASURE,'density_unit':'m^-3','projectile_mass_kg':'2','target_mass_kg':'2',
      'n_CR':'2','n_HI':'3','projectile':[{'velocity_m_s':['3','4','0'],'probability':'1'}],
      'target':[{'velocity_m_s':['0','0','0'],'probability':'1'}],
      'outgoing_acceptance':'POPULATION_LABEL_ONLY_NO_OUTGOING_THRESHOLD'}
    return source,event

def evaluate(s,e,**kw):
    sb=json.dumps(s,sort_keys=True).encode();eb=json.dumps(e,sort_keys=True).encode()
    return evaluate_count(sb,hashlib.sha256(sb).hexdigest(),eb,hashlib.sha256(eb).hexdigest(),**kw)

def test_discrete_rate_exact_and_claim_ceiling():
    s,e=objects();r=evaluate(s,e)
    assert r['K_1s_m3_s']==['5','10']
    assert r['R_1s_m_minus3_s']==['30','60']
    assert r['source_model_discrepancy'] is None
    assert not r['physical_admission'] and not r['actual_host_bound']
    assert r['momentum_or_heat'] is None and r['free_electron_source_elementary_reaction']=='0'

@pytest.mark.parametrize('field',['n_CR','n_HI'])
def test_zero_density(field):
    s,e=objects();e[field]='0'
    assert evaluate(s,e)['R_1s_m_minus3_s']==['0','0']

def test_density_bilinearity():
    s,e=objects();e['n_CR']='4';e['n_HI']='9'
    assert evaluate(s,e)['R_1s_m_minus3_s']==['180','360']

@pytest.mark.parametrize('field,bad',[('frame','normal_tetrad'),('time','conformal_time'),
 ('measure','UNKNOWN'),('origin','actual_verified'),('density_unit','cm^-3'),
 ('outgoing_acceptance','energy_above_cut')])
def test_event_conventions_rejected(field,bad):
    s,e=objects();e[field]=bad
    with pytest.raises(ContractError): evaluate(s,e)

@pytest.mark.parametrize('field,bad',[('profile','STRICT_CERTIFIED'),('energy_kind','E_LAB_J'),
 ('sigma_unit','cm^2'),('reaction','TOTAL_CAPTURE'),('interpolation','PHYSICAL_TRUE_ENVELOPE')])
def test_source_conventions_rejected(field,bad):
    s,e=objects();s[field]=bad
    with pytest.raises(ContractError): evaluate(s,e)

@pytest.mark.parametrize('cap',['reservoir_transfer','momentum_or_heat','free_electron_production'])
def test_capability_not_inferred(cap):
    s,e=objects()
    with pytest.raises(ContractError,match='UNSUPPORTED'): evaluate(s,e,capability=cap)

def test_source_hash_mismatch():
    s,e=objects();sb=json.dumps(s).encode();eb=json.dumps(e).encode()
    with pytest.raises(ContractError,match='IDENTITY'):
        evaluate_count(sb,'0'*64,eb,hashlib.sha256(eb).hexdigest())

def test_outside_source_domain_refused():
    s,e=objects();e['projectile'][0]['velocity_m_s']=['20','0','0']
    with pytest.raises(ContractError,match='OUT_OF_DOMAIN'): evaluate(s,e)

def test_wrong_distribution_normalization():
    s,e=objects();e['projectile'][0]['probability']='0.9'
    with pytest.raises(ContractError,match='NORMALIZATION'): evaluate(s,e)

def test_rational_positive_mixture():
    s,e=objects();e['projectile']=[{'velocity_m_s':['0','0','0'],'probability':'1/3'},
                                 {'velocity_m_s':['3','4','0'],'probability':'2/3'}]
    assert evaluate(s,e)['K_1s_m3_s']==['10/3','20/3']

def test_isotropic_target_rotation_invariance_discrete_rotation():
    s,e=objects();r=evaluate(s,e)
    e['projectile'][0]['velocity_m_s']=['-4','0','3']
    assert r['K_1s_m3_s']==evaluate(s,e)['K_1s_m3_s']

def test_piecewise_model_interior_not_physical_envelope():
    s,e=objects();s['sigma_envelopes']=[['0','0'],['2','4']]
    assert evaluate(s,e)['K_1s_m3_s']==['5','10']

@pytest.mark.parametrize('x',[F(0),F(1),F(2),F(1,10**100),F(10**80+1),F(81,49)])
def test_sqrt_integer_enclosure(x):
    lo,hi=sqrt_interval(x)
    assert 0<=lo<=hi and lo*lo<=x<=hi*hi and hi-lo<=F(1,2**128)

@pytest.mark.parametrize('x',[True,float('nan'),float('inf'),'-1/0'])
def test_bad_scalar(x):
    with pytest.raises(ContractError): rational(x)

def test_negative_weight_or_invalid_interval():
    for w,i in [([-1],[(1,2)]),([1],[(2,1)]),([1],[(-1,1)]),([],[])]:
        with pytest.raises(ContractError): weighted_intervals(w,i)

def test_tail_absence_never_zero():
    b=continuous_rate_budget((1,2),None,0,0)
    assert b['upper'] is None and b['status']=='MISSING_BOUNDS'

def test_tail_bound_composition():
    b=continuous_rate_budget((1,2),F(1,10),F(1,5),F(1,20))
    assert b['lower']==F(19,20) and b['upper']==F(47,20)
    assert not b['physical_admission']

def test_stoichiometry_all_ledgers_and_gas_split():
    n=(3,5,1,7,10);out=cx_update(n,F(3,2))
    assert conserved_ledger(n)==conserved_ledger(out)
    assert out[3]-n[3]==F(3,2) and out[0]-n[0]==-F(3,2)
    assert out[4]==n[4]

@pytest.mark.parametrize('extent',[-1,4])
def test_extent_bounds(extent):
    with pytest.raises(ContractError): cx_update([3,5,1,7,10],extent)

def test_bianchi_i_volume_density_and_momenta():
    p,n=bianchi_i_map([1,2,3],24,[1,1,1],[2,3,4])
    assert p==(F(1,2),F(2,3),F(3,4)) and n==1

def test_flrw_limit_and_restart_composition():
    p,n=bianchi_i_map([3,6,9],8,[1]*3,[2]*3)
    assert n==1 and p==(F(3,2),3,F(9,2))
    p2,n2=bianchi_i_map(p,n,[2]*3,[4]*3)
    assert (p2,n2)==bianchi_i_map([3,6,9],8,[1]*3,[4]*3)

def test_process_duplicate_owner():
    with pytest.raises(ContractError,match='DOUBLE'):owner_registry([('CX','a'),('CX','b')])

def test_metric_norm_identity_and_defect_sign():
    S=np.diag([2.,3.]);dS=np.diag([.2,-.3]);D=dS/2;H=np.array([[1.,.1j],[-.1j,2.]])
    r=metric_defect(S,dS,H,D,2.)
    assert r['relative_spectral_norm']==0
    H=np.array([[1.+.1j,0],[0,2.]])
    assert abs(metric_defect(S,dS,H,D,2.)['K'][0,0]-.1)<1e-15

def test_metric_rejects_non_positive_S():
    with pytest.raises(ContractError): metric_defect(np.diag([1.,0.]),np.eye(2),np.eye(2),np.eye(2),1)

def test_exp_rational_bounds_against_high_precision():
    import mpmath as mp
    with mp.workdps(100):
        for x in [F(0),F(1,100),F(1),F(5)]:
            lo,hi=exp_positive_interval(x)
            y=mp.exp(mp.mpf(x.numerator)/x.denominator)
            assert mp.mpf(lo.numerator)/lo.denominator<=y<=mp.mpf(hi.numerator)/hi.denominator

def test_population_bound_unnormalized_fixture():
    assert population_error_bound(F(1,10),F(11,10))==F(23,100)

def test_residual_conditional_growth_encloses_scalar_solution():
    import mpmath as mp
    b=state_error_bound(F(1,100),[(2,F(1,5),F(3,100))])
    with mp.workdps(100):
        exact=mp.exp(mp.mpf('0.2'))*mp.mpf('.01')+mp.mpf('.3')*mp.expm1(mp.mpf('.2'))
        assert exact<=mp.mpf(b.numerator)/b.denominator

def test_relative_pdf_zero_and_small_drift_stability():
    for y in [.01,.1,1.,3.,10.]:
        assert relative_speed_pdf_scaled(y,1e-12)==pytest.approx(relative_speed_pdf_scaled(y,0),rel=2e-12)
    assert relative_speed_pdf_scaled(0,1)==0

@pytest.mark.parametrize('a',[0.,1e-8,.1,1.,10.,100.])
def test_relative_pdf_normalization_and_mean(a):
    from scipy.integrate import quad
    low=max(-a,-12.); high=12.
    prob=quad(lambda t:relative_speed_pdf_scaled(a+t,a),low,high,epsabs=1e-11,epsrel=1e-11)[0]
    mean=quad(lambda t:(a+t)*relative_speed_pdf_scaled(a+t,a),low,high,epsabs=1e-10,epsrel=1e-11)[0]
    assert abs(prob-1)<2e-11
    assert mean==pytest.approx(constant_sigma_mean_speed_scaled(a),rel=2e-11,abs=2e-11)

def test_tail_bound_positive_not_underflow_certificate():
    p,m=maxwell_shell_tail_majorant(10,8)
    assert 0<p<m<1e-10
