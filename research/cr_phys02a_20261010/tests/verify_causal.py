# SPDX-License-Identifier: GPL-3.0-only
"""Bounded independent quadrature/ODE checks of the new causal component.

No inherited PHYS01 suite is rerun. All acceptance thresholds are recorded in
state/SCIENTIFIC_CONTRACT.json before the first scientific execution.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import hashlib
import json
import math
import platform
import time

import numpy as np
import scipy
from scipy.integrate import quad, solve_ivp
from scipy.constants import e, epsilon_0, m_e, k, hbar
from causal_subthreshold import CoulombClock, DirectElectronSource, aggregate, EV_J, YEAR_S, ROOT


def relative(a,b):
    return abs(a-b)/max(abs(a),abs(b),1e-290)


def main():
    begin = time.perf_counter()
    out = ROOT/'evidence'
    out.mkdir(exist_ok=True)
    clock = CoulombClock()
    source = DirectElectronSource(64)
    checks = []
    details = {}
    def check(name, metric, threshold):
        checks.append({'test_id':name,'metric':float(metric),'threshold':threshold,
                       'status':'PASS' if metric <= threshold else 'FAIL'})

    # Independent integration of 1/b does not use the Ei primitive.
    clock_errors=[]
    for energy in [.101,.2,1,3,10]:
        direct = quad(lambda x:1/float(clock.stopping_eV_s(x)), .1, energy,
                      epsabs=1e-8,epsrel=2e-12)[0]
        clock_errors.append(relative(direct,float(clock.clock_s(energy))))
    check('CLOCK_EI_VS_ADAPTIVE_ENERGY_QUADRATURE',max(clock_errors),2e-9)

    # Independent forward scalar ODE and time-domain integrals. The oracle
    # continues the analytic drag infinitesimally below cutoff only to locate
    # its terminal event; no below-cutoff trajectory is used in any observable.
    ode_errors=[]; ode_rows=[]
    kap=e*e/(4*math.pi*epsilon_0)
    omega=math.sqrt(clock.n_e_m3*e*e/(epsilon_0*m_e))
    def rhs(age_yr, state):
        energy=state[0]
        speed=math.sqrt(2*energy*e/m_e)
        rho=kap/(energy*e)
        drag=4*math.pi*kap*kap*clock.n_e_m3/(m_e*speed*e)*math.log(speed/(omega*rho))
        return [-YEAR_S*drag]
    def at_cutoff(t,y):return y[0]-.1
    at_cutoff.terminal=True
    at_cutoff.direction=-1
    for E0,t_yr in [(1.0,30.0),(1.0,100.0),(3.0,100.0),(10.0,1e10/YEAR_S)]:
        tau_yr=float(clock.clock_s(E0))/YEAR_S
        sol=solve_ivp(rhs,[0,max(t_yr,tau_yr)*1.001],[E0],method='DOP853',
            rtol=2e-11,atol=2e-12,events=at_cutoff,dense_output=True,
            max_step=min(t_yr,tau_yr)/128)
        if not sol.success or len(sol.t_events[0]) != 1:
            raise RuntimeError('INDEPENDENT_ODE_FAILED')
        end=min(t_yr,float(sol.t_events[0][0]))
        def power_density(a):
            return (t_yr-a)*(-rhs(a,sol.sol(a))[0])
        ode_power=quad(power_density,0,end,epsabs=1e-10,epsrel=2e-10)[0]*YEAR_S
        ode_heat=.5*quad(lambda a:(t_yr-a)*power_density(a),0,end,
                        epsabs=1e-9,epsrel=2e-10)[0]*YEAR_S**2
        # A separate storage integral checks the ledger independently of
        # the production code's definition by subtraction.
        stored=quad(lambda a:(t_yr-a)*float(sol.sol(a)[0]),0,end,
                    epsabs=1e-9,epsrel=2e-10)[0]*YEAR_S**2
        if t_yr > end:stored += .05*(t_yr-end)**2*YEAR_S**2
        got=clock.ramp_response(E0,t_yr*YEAR_S,96)
        errs=[relative(got['power_per_A'],ode_power),relative(got['deposited_per_A'],ode_heat),
              relative(got['active_kinetic_per_A']+got['cutoff_kinetic_per_A'],stored)]
        ode_errors += errs
        ode_rows.append({'E0_eV':E0,'time_year':t_yr,'clock_cutoff_year':tau_yr,
                         'ode_cutoff_year':float(sol.t_events[0][0]),'relative_errors':errs})
    check('RAMP_POWER_ENERGY_STORAGE_VS_FORWARD_ODE',max(ode_errors),2e-6)
    details['independent_ode']=ode_rows

    # Direct SDCS integral, as opposed to the rational separated coefficients.
    spectrum_errors=[]
    for W in [.1,1,3,10]:
        direct=0.0
        for target,density in source.densities.items():
            def f(logK):
                K=math.exp(logK)
                return float(source.model.q_proper_m3_s_eV(K))*K*float(source.rudd.proton_speed_m_s(K))*density*float(source.rudd.dsigma_dW_m2_per_eV(K,W,target))
            direct += quad(f,math.log(1e6),math.log(4e6),epsabs=1e-80,epsrel=1e-11)[0]
        spectrum_errors.append(relative(direct,float(source.spectrum_A(W))))
    check('SOURCE_SEPARATION_VS_DIRECT_SDCS',max(spectrum_errors),2e-10)

    rows=[]; conv=[]; ledgers=[]
    source96=DirectElectronSource(96)
    for t_yr in [0.0,1.0,10.0,30.0,100.0,1e10/YEAR_S]:
        t=t_yr*YEAR_S
        row=aggregate(source,clock,t,64,64)
        fine=aggregate(source96,clock,t,96,96)
        for key in ['stopping_heat_power_J_m3_s','deposited_stopping_energy_J_m3',
                    'active_electron_kinetic_J_m3','cutoff_residual_kinetic_J_m3']:
            conv.append(relative(row[key],fine[key]))
        if t>0:
            en=fine['injected_selected_electron_energy_J_m3']
            summed=math.fsum([fine['deposited_stopping_energy_J_m3'],fine['active_electron_kinetic_J_m3'],fine['cutoff_residual_kinetic_J_m3']])
            ledgers.append(relative(en,summed))
            fine['instantaneous_heat_to_terminal_selected_ratio']=fine['stopping_heat_power_J_m3_s']/fine['terminal_selected_heat_power_J_m3_s']
            fine['cumulative_deposited_fraction']=fine['deposited_stopping_energy_J_m3']/en
            fine['active_kinetic_fraction']=fine['active_electron_kinetic_J_m3']/en
            fine['cutoff_residual_fraction']=fine['cutoff_residual_kinetic_J_m3']/en
        rows.append(fine)
    check('SOURCE_KERNEL_QUADRATURE_64_VS_96',max(conv),2e-7)
    check('SELECTED_CAUSAL_ENERGY_LEDGER',max(ledgers),2e-11)

    # The exact inherited Bianchi source is inspected at fixed times; this is
    # a new approximation check, not another full inherited validation suite.
    bianchi_rows=[]; bianchi_error=[]
    for frac in [.25,.5,1.0]:
        t=frac*1e10
        b=source.bianchi_coefficients(t)
        relative_by_target={}
        for target in b:
            relative_by_target[target]=[relative(b[target][j],t*source.coefficients[target][j]) for j in (0,1)]
            bianchi_error.extend(relative_by_target[target])
        bianchi_rows.append({'time_s':t,'relative_by_target':relative_by_target})
    check('LOCAL_RAMP_VS_EXACT_BIANCHI_SOURCE_SAMPLES',max(bianchi_error),3e-6)
    details['source_approximation_samples']=bianchi_rows
    details['source_approximation_semantics']='Finite samples, not an interval certificate; no claim of exact time-varying Bianchi electron transport.'

    # Required source/off and domain behavior.
    invalid_calls=[lambda:clock.energy_after(1,-1),lambda:clock.energy_after(11,1),
        lambda:clock.stopping_eV_s(float('nan')),lambda:aggregate(source,clock,-1),
        lambda:aggregate(source,clock,1e10+1),lambda:source.spectrum_A(11),
        lambda:CoulombClock(n_e_m3=0),lambda:CoulombClock(n_e_m3=1.0),
        lambda:CoulombClock(temperature_k=200)]
    rejected=0
    for call in invalid_calls:
        try:call()
        except ValueError:rejected+=1
    check('INVALID_INPUTS_REJECTED',len(invalid_calls)-rejected,0)
    off=aggregate(DirectElectronSource(64,enabled=False),clock,1e10)
    fields=['stopping_heat_power_J_m3_s','deposited_stopping_energy_J_m3','active_electron_kinetic_J_m3',
            'cutoff_residual_kinetic_J_m3','injected_selected_electron_energy_J_m3']
    check('ZERO_TIME_AND_OFF',max([abs(rows[0][f]) for f in fields]+[abs(off[f]) for f in fields]),0)

    bands=[(0,.1),(.1,1),(1,3),(3,10),(10,100),(100,1000),(1000,None)]
    totalA=source96.source_energy_coefficient()
    band_rows=[]
    for lo,hi in bands:
        value=source96.source_energy_coefficient(lo,hi)
        band_rows.append({'lower_eV':lo,'upper_eV':hi,'electron_energy_coefficient_eV_m3_s2':value,
                         'fraction_of_all_direct_secondary_kinetic':value/totalA})
    check('DIRECT_ELECTRON_SOURCE_PARTITION',relative(math.fsum(x['electron_energy_coefficient_eV_m3_s2'] for x in band_rows),totalA),2e-12)
    details['direct_electron_source_bands']=band_rows

    primary=source96.primary_number_coefficients()
    details['primary_causal_turn_on']={target:{'endpoint_rate_m3_s':value*1e10,
      'cumulative_number_m3':.5*value*1e20,'status':'leading local expansion primary collisions; no secondary delay included'} for target,value in primary.items()}
    diagnostics=[]
    for E in [.1,1,3,10]:
        speed=math.sqrt(2*E*e/m_e)
        diagnostics.append({'energy_eV':E,'coulomb_log':float(clock.coulomb_log(E)),
          'instantaneous_E_over_b_year':E/float(clock.stopping_eV_s(E))/YEAR_S,
          'time_to_cutoff_year':float(clock.clock_s(E))/YEAR_S,
          'energy_over_kBT':E*e/(k*100),'classical_parameter_kappa_over_hbar_v':kap/(hbar*speed)})
    report={'schema':'cr-phys02a-numerical-result.v1','scope':'conditional direct-ejection Coulomb stopping; not complete secondary deposition',
      'physical_accuracy_certificate':False,'full_secondary_delay_admission':False,'production_history':'HOLD',
      'ne_m3':clock.n_e_m3,'omega_p_s':clock.omega_p_s,'closure':'classical superthermal leading-log fixed-bath CSDA',
      'diagnostics':diagnostics,'time_series':rows,'details':details,'checks':checks,
      'status':'PASS_SCOPED' if all(c['status']=='PASS' for c in checks) else 'FAIL',
      'execution':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),
          'elapsed_s':time.perf_counter()-begin,'precision':'FP64','old_PHYS01_suites_rerun':0,
          'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'src/causal_subthreshold.py',Path(__file__)]}}}
    (out/'NUMERICAL_RESULT.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':report['status'],'checks':checks,'endpoint':rows[-1],'elapsed_s':report['execution']['elapsed_s']},indent=2))
    return 0 if report['status']=='PASS_SCOPED' else 1


if __name__=='__main__':raise SystemExit(main())
