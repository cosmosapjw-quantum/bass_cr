# SPDX-License-Identifier: GPL-3.0-only
"""Source-pinned conditional CR proton ionization + FS10 terminal deposition.

This imports the GPLv3 Rudd port; this combined program is GPLv3. It computes
an instantaneous local component, not a causal complete CR/EoR history.
The finite collisionless source population is a prescribed input state; the
terminal cascade assumes quasistatic local degradation. Its finite turn-on
delay is NOT solved. Outside-band collisions remain unmodelled, never heat.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from injection import InjectionModel, transport_population, EV_J
import rudd
from fs10 import FS10Table, IONIZATION_EV, PROJECTION_REL_BOUND

ROOT = Path(__file__).resolve().parents[1]
CHANNELS = ['heat_eV','raw_heat_eV','excitation_eV','source_projection_correction_eV',
            'threshold_interpolation_correction_eV','HI','HeI','HeII','lya_count']

def response_vector(table, energy):
    d = table.evaluate(energy)
    return np.stack([d[k] if k not in ('HI','HeI','HeII') else d['ionization_counts'][k]
                     for k in CHANNELS], axis=-1)

def convolve_secondary(proton_eV, target, table):
    """Analytic SDCS moments against each piecewise-linear terminal yield.

    Split at every raw-grid and threshold breakpoint; quarter-point values
    determine each segment's slope without confusing a threshold's one-sided
    limit with its point value. Integrate over the exact physical endpoint.
    """
    K = np.asarray(proton_eV, dtype=float)
    if np.any(K < 1e6) or np.any(K > 4e6):
        raise ValueError('COMMON_PROVIDER_DOMAIN_1_TO_4_MEV')
    edges = np.unique(np.r_[0.0, table.energy_eV, 10.2, IONIZATION_EV])
    left, right = edges[:-1], edges[1:]
    first, last = left + .25*(right-left), left + .75*(right-left)
    va, vb = response_vector(table, first), response_vector(table, last)
    slope = (vb-va)/(last-first)[:,None]
    intercept = va-slope*first[:,None]
    moments = rudd.cross_section_moments(K[:,None], target,
                                       left[None,:], right[None,:])
    return moments['sigma_m2'] @ intercept + moments['secondary_eV_m2'] @ slope

def provider_id_for_xi(xi):
    return f'CRP_L17_MD14_RUDD_FS10_XI{round(100*xi):03d}_CONDITIONAL_V1'


def source_manifest(scenario, table):
    files = [Path('src')/n for n in ('injection.py','rudd.py','fs10.py','provider.py')]
    files += [Path(table.relative_path)]
    return {'schema':'cr-source-manifest.v1', 'provider_id':provider_id_for_xi(scenario['xi']),
            'files':{str(p):hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
            'scenario':scenario,
            'sources':{'injection':'https://arxiv.org/abs/1703.09337v1',
                       'sfrd':'https://arxiv.org/abs/1403.0007v3',
                       'proton_kernel':rudd.SOURCE_URL,
                       'cascade':'https://arxiv.org/abs/0910.4410v1'},
            'scope':'instantaneous conditional ionization channel; no full CR closure',
            'gas_transplant':'nominal primordial Y=.248; original FS10 MC abundance not recovered; z8 low-density adoption of z10 table',
            'interpolation':'threshold-aware piecewise-linear energy/count; separate bounded numerical heat projection',
            'terminal_closure':'quasistatic local cascade, sub-13.6eV excitation radiation escapes gas energy account; no tracked ionizing-photon reinjection'}

def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def build_packet(energy_order=48, age_order=8, mu_order=8, xi=0.01):
    # Explicit local scenario: no claim that a cold xi=.01 gas at z8 is a
    # fitted cosmological solution. nH is a declared proper density parameter.
    scenario = {'z_source':8.0,'dt_s':1e10,'H_s':3.3e-17,'shear_s':3.3e-18,
                'n_h_m3':140.0,'y_he_mass_fraction':.248,'xi':float(xi),'temperature_k':100.0,
                'active_proton_eV':[1e6,4e6],
                'energy_order':energy_order,'age_order':age_order,'mu_order':mu_order}
    model = InjectionModel(z_snapshot=scenario['z_source'])
    pop = transport_population(model,scenario['dt_s'],scenario['H_s'],scenario['shear_s'],
                               age_order=age_order,mu_order=mu_order,energy_order=energy_order)
    table = FS10Table(scenario['xi'])
    K,N = pop['nodes']['kinetic_eV'],pop['nodes']['number_density_m3']
    nH = scenario['n_h_m3']; Y = scenario['y_he_mass_fraction']; nHe=nH*Y/(4*(1-Y))
    rates=[]; vectors=[]; losses=[]; sec_powers=[]; thin=[]
    for target, density in [('H',nH*(1-scenario['xi'])),('He',nHe*(1-scenario['xi']))]:
        flux = N*rudd.proton_speed_m_s(K)*density
        moment = rudd.cross_section_moments(K,target)
        rates.append(float(np.dot(flux,moment['sigma_m2'])))
        vectors.append(flux @ convolve_secondary(K,target,table))
        losses.append(float(np.dot(flux,moment['loss_eV_m2']))*EV_J)
        sec_powers.append(float(np.dot(flux,moment['secondary_eV_m2']))*EV_J)
        thin.append(float(np.max(rudd.proton_speed_m_s(K)*density*moment['loss_eV_m2']/K))*scenario['dt_s'])
    v=np.sum(vectors,axis=0); secondary=v[5:8]
    primary_threshold = np.array([rudd.TARGETS[t]['I_eV'] for t in ('H','He')])*EV_J
    secondary_threshold=IONIZATION_EV*EV_J
    ion=float(np.dot(rates,primary_threshold)+np.dot(secondary,secondary_threshold))
    heat=float(v[0])*EV_J; raw_table_heat=float(v[1])*EV_J; exc=float(v[2])*EV_J
    source_correction=float(v[3])*EV_J; threshold_correction=float(v[4])*EV_J
    preprojection_heat=raw_table_heat+threshold_correction
    loss=math.fsum(losses); secondary_power=math.fsum(sec_powers)
    residual=math.fsum([preprojection_heat,ion,exc,-loss])
    # Use compensated aggregate closure; the ~ulp quadrature discrepancy is
    # recorded separately from the acquired table correction.
    corrected_heat=math.fsum([loss,-ion,-exc])
    correction=corrected_heat-preprojection_heat
    bound=PROJECTION_REL_BOUND*secondary_power
    if abs(correction)>bound or corrected_heat<0 or sum(thin)>1e-3:
        raise ValueError('PROJECTION_OR_THIN_LOSS_DOMAIN')
    manifest=source_manifest(scenario, table)
    packet={'provider_id':provider_id_for_xi(scenario['xi']),'manifest_sha256':canonical_hash(manifest),
            'closure':'FS10_LOCAL_DEPOSITION_PROMPT_EXCITATION_AND_CONTINUUM_ESCAPE',
            'gas':{'time_s':scenario['dt_s'],'n_h_m3':nH,'n_he_m3':nHe,
                   'xi':scenario['xi'],'temperature_k':scenario['temperature_k'],
                   'y_he_mass_fraction':Y},
            'primary_rate_m3_s':rates,'primary_threshold_j':primary_threshold.tolist(),
            'secondary_rate_m3_s':secondary.tolist(),'secondary_threshold_j':secondary_threshold.tolist(),
            'ionization_power_j_m3_s':ion,'raw_heat_power_j_m3_s':preprojection_heat,
            'heat_power_j_m3_s':corrected_heat,'heat_correction_j_m3_s':correction,
            'excitation_escape_power_j_m3_s':exc,'continuum_escape_power_j_m3_s':0.0,
            'modelled_ionization_loss_power_j_m3_s':loss,
            'full_injection_power_j_m3_s':model.power_proper_J_m3_s(),
            'table_raw_residual_j_m3_s':residual,'table_correction_bound_j_m3_s':bound}
    packet['packet_sha256']=canonical_hash(packet)
    audit={'table':table.audit,'source':pop['source'],'background':pop['background'],
           'CR_storage_budgets':pop['budgets'],'quadrature_orders':pop['quadrature_orders'],
           'population_node_count':len(K),'sampled_fractional_ionization_loss_age_estimate':sum(thin),
           'loss_estimate_semantics':'maximum over final-population quadrature nodes times age; not a trajectory supremum or certified bound',
           'raw_table_heat_power_j_m3_s':raw_table_heat,
           'threshold_interpolation_heat_change_j_m3_s':threshold_correction,
           'source_projection_heat_change_j_m3_s':source_correction,
           'analytic_convolution_roundoff_j_m3_s':corrected_heat-heat,
           'secondary_kinetic_power_j_m3_s':secondary_power,
           'lya_count_m3_s':float(v[8]),
           'closed_power_residual_j_m3_s':math.fsum([corrected_heat,ion,exc,-loss]),
           'scope':'physical-model component with declared approximations; not a causal turn-on deposition history',
           'delay_admission':False,
           'unmodelled':['CR collisions outside1..4MeV','proton Coulomb/primary excitation/HeII targets','magnetic spatial diffusion','secondary cascade delay','gas feedback on cascade','arbitrary ionization fraction','complete EoR history']}
    return packet,manifest,audit

if __name__=='__main__':
    out=ROOT/'evidence'; out.mkdir(exist_ok=True)
    packet,manifest,audit=build_packet()
    for name,obj in [('CR_PACKET.json',packet),('SOURCE_MANIFEST.json',manifest),('PROVIDER_AUDIT.json',audit)]:
        (out/name).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'status':'CONDITIONAL_COMPONENT_BUILT','packet_sha256':packet['packet_sha256'],
                      'primary_rates':packet['primary_rate_m3_s'],'secondary_rates':packet['secondary_rate_m3_s'],
                      'heat':packet['heat_power_j_m3_s'],'excitation':packet['excitation_escape_power_j_m3_s']}))
