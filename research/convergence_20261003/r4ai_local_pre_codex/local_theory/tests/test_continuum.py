import math,hashlib,json
import pytest
from cr_reion.provider import SourceModel,REACTION
from cr_reion.continuum import maxwellian_core
from cr_reion.core import ContractError

def model(energies=None,sigmas=None):
    p={'schema':'CX_LINEAR_MODEL_V1','source_id':'SYNTHETIC_CONSTANT',
       'profile':'MODEL','reaction':REACTION,'energy_kind':'E_CM_J','sigma_unit':'m^2',
       'interpolation':'PIECEWISE_LINEAR_MODEL_FAMILY','energies':energies or ['0','400'],
       'sigma_envelopes':sigmas or [['3','3'],['3','3']]}
    b=json.dumps(p).encode();return SourceModel.load(b,hashlib.sha256(b).hexdigest())

def test_maxwellian_constant_cross_section_integral():
    r=maxwellian_core(model(),reduced_mass_kg=2,thermal_sigma_m_s=1,drift_m_s=0)
    assert abs(r['K_core_interval_estimate_m3_s'][0]-3*math.sqrt(8/math.pi))<1e-12
    assert r['total_K_upper'] is None and r['physical_admission'] is False

@pytest.mark.parametrize('a',[0.001,0.1,1.,10.])
def test_drift_constant_sigma(a):
    from cr_reion.kinetics import constant_sigma_mean_speed_scaled
    r=maxwellian_core(model(),reduced_mass_kg=2,thermal_sigma_m_s=1,drift_m_s=a)
    assert abs(r['K_core_interval_estimate_m3_s'][0]-3*constant_sigma_mean_speed_scaled(a))<2e-10

def test_two_source_envelopes_and_multiple_energy_panels():
    r=maxwellian_core(model(['0','1','400'],[['1','2'],['1','2'],['1','2']]),reduced_mass_kg=2,thermal_sigma_m_s=1,drift_m_s=1)
    lo,hi=r['K_core_interval_estimate_m3_s'];assert abs(hi-2*lo)<1e-12
    assert len(r['panels'])==2 and r['error_type'].endswith('NOT_ENCLOSURE')

def test_energy_linear_source_analytic_third_moment_zero_drift():
    # sigma(E)=E, E=y^2. K=E[y^3]=8 sqrt(2/pi) for central Maxwell.
    r=maxwellian_core(model(['0','400'],[['0','0'],['400','400']]),reduced_mass_kg=2,thermal_sigma_m_s=1,drift_m_s=0)
    assert abs(r['K_core_interval_estimate_m3_s'][0]-8*math.sqrt(2/math.pi))<2e-11

@pytest.mark.parametrize('kwargs',[
    {'reduced_mass_kg':0,'thermal_sigma_m_s':1,'drift_m_s':1},
    {'reduced_mass_kg':1,'thermal_sigma_m_s':0,'drift_m_s':1},
    {'reduced_mass_kg':1,'thermal_sigma_m_s':1,'drift_m_s':-1},
    {'reduced_mass_kg':1,'thermal_sigma_m_s':1,'drift_m_s':float('nan')},
])
def test_invalid_continuum_inputs_rejected(kwargs):
    with pytest.raises(ContractError):maxwellian_core(model(),**kwargs)
