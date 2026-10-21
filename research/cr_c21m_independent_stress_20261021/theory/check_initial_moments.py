#!/usr/bin/env python3
"""Independent initial-moment checks only: no ODE integrations."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import sys, math, json, hashlib
import numpy as np
from scipy.integrate import quad
ROOT=Path('/workspace/scratch/10765dc22dcf')
BASE=ROOT/'bass_cr/research/cr_c21l_rei_pilot_20261021'
sys.path.insert(0,str(BASE))
from adapter import CanonicalMomentumFV, CanonicalFVSpecies, source_lock, G_SI, C_SI, verify_source

M=30.
fd=lambda q: math.exp(-q)/(1+math.exp(-q))
Ir,eIr=quad(lambda q:q*q*fd(q)*math.hypot(M,q),0,np.inf,epsabs=1e-11,epsrel=1e-12)
Ip,eIp=quad(lambda q:q**4*fd(q)/math.hypot(M,q),0,np.inf,epsabs=1e-12,epsrel=1e-12)
ratio=Ip/Ir
rows=[]
for A in (-1.,-.5,0.,.5,1.,2.):
    m=CanonicalMomentumFV(M,A,24,12,3)
    v=m.moments(0.,0.)
    rows.append({'A':A,'rho_norm':v.rho,'p_parallel':v.pressure_parallel,
        'p_perp':v.pressure_perp,'delta_p':v.delta_p,'pi_s':v.pi_s,
        'continuum_delta_p':A*ratio/5,'delta_p_quadrature_error':v.delta_p-A*ratio/5,
        'min_packet':float(m._numbers.min()),'min_cell':float(m.cell_numbers.min()),
        'reference_energy_norm':m.reference_energy_norm,'total_number':m.total_cell_number,
        'angular_weight_min_continuum':min(1+A,1-A/2)})
    assert abs(v.rho-1)<4e-16
    assert m._numbers.min()>=0 and m.cell_numbers.min()>=0
    assert abs(v.delta_p-A*ratio/5)<2e-7

physics=[]
for S0,A,k in [(0.,0.,0.),(.02,0.,.2),(-.02,.5,0.),(.01,-.5,.1),(.04,2.,-.5)]:
    source=source_lock()
    s=CanonicalFVSpecies(source,2.7255,8,Sigma_ref=abs(S0)/math.sqrt(2),
        orientation=int(np.sign(S0)),kappa_gamma=k,kappa_nu=k,ne_source=None,
        mass_fraction=.1,massive_A=A,mass_over_Tref=M,radial_cells=24,angular_cells=12,subcell_gauss_order=3)
    y=s.initial_state();v=s.fields(0.,y);H=v['H']
    cfac=8*math.pi*G_SI/C_SI**2*math.sqrt(6)/H**2
    Pm=cfac*v['Pi_matter_J_m3']
    Pr=cfac*(v['Pi_gamma_J_m3']+v['Pi_nu_J_m3'])
    Pm_cont=cfac*source.rhocrit_j_m3*.1*source.omega_m/source.aref**3*A*ratio/15
    Pr_expected=cfac*source.rhocrit_j_m3*source.omega_r/source.aref**4*k/15
    measured_S=math.sqrt(6)*v['s']/H
    physics.append({'S0':S0,'A':A,'k':k,'measured_S0':measured_S,'P_m':Pm,'P_r':Pr,
        'P_m_continuum':Pm_cont,'P_r_expected':Pr_expected,
        'P_m_quadrature_error':Pm-Pm_cont,'P_r_angular_error':Pr-Pr_expected,
        'H2_constraint_relative':v['Einstein_H2']/H**2-1})
    assert abs(measured_S-S0)<1e-16
    assert abs(Pr-Pr_expected)<1e-17
    assert abs(Pm-Pm_cont)<1e-7

out={'status':'PASS_SCOPED','execution':'initial fields and independent 1D radial scipy.quad; no ODE run',
    'PYTHON_STATUS':'PYTHON_PASS','M_over_Tref':M,'I_rho':Ir,'I_pressure':Ip,'Ipressure_over_Irho':ratio,
    'quad_internal_error_estimates':[eIr,eIp],'massive_initial_rows':rows,'initial_physics_cases':physics,
    'source_manifest_verified':verify_source(),'global_error_bound':None,
    'claims':['full Frobenius and signed initial maps','finite angular positivity domain','same initial normalization across A'],
    'limits':['quadrature discrepancy is retained and not a global bound','only source-locked 24x12 Gauss3 M/Tref30 at eta=b=0']}
dest=Path(__file__).with_name('initial_moments_checks.json')
dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:out[k] for k in ('status','execution','Ipressure_over_Irho')}))
print(json.dumps({'max_massive_delta_p_quadrature_error':max(abs(r['delta_p_quadrature_error']) for r in rows),'physics_cases':physics},indent=2))
