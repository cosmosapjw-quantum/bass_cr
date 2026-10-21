"""Focused static checks; the original ODE integrator is never called."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
            'BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key] = '1'

import numpy as np

import mass_shell_derivatives as diagnostic


def load_baseline(repo):
    path = repo/'research/cr_c21m_independent_stress_20261021/builder.py'
    spec = importlib.util.spec_from_file_location('c21m_original_builder_for_derivatives', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def complex_step(momentum, eta, b, velocity):
    step = 1e-24
    r = np.exp(-(eta+1j*step))
    bc = b+1j*step*velocity
    u = (r*momentum._q)**2*np.exp(2*bc)*(1-momentum._mu2)
    w = (r*momentum._q)**2*np.exp(-4*bc)*momentum._mu2
    energy = np.sqrt(momentum.mass*momentum.mass+u+w)
    weighted = r**3/momentum.reference_energy_norm*momentum._numbers
    values = np.array([np.sum(weighted*energy),
                       np.sum(weighted*u/(2*energy)), np.sum(weighted*w/energy)])
    return values.imag/step


def forward4(function, step=2e-4):
    values = [np.asarray(function(j*step)) for j in range(5)]
    return (-25*values[0]+48*values[1]-36*values[2]+16*values[3]-3*values[4])/(12*step)


def run(repo):
    baseline = load_baseline(repo)
    groups = []
    moment_max = 0.
    conservation_max = 0.
    for amplitude in (-1., 0., .4, 2.):
        m = baseline.parent.CanonicalMomentumFV(30., amplitude, 24, 12, gauss_order=3)
        before = [a.tobytes() for a in (m._q,m._mu2,m._numbers,m._cell_numbers)]
        for eta,b,v in ((0.,0.,0.), (.13,-.021,.035), (1.1,.019,-.027)):
            d = diagnostic.packet_derivatives(m,eta,b,v)
            original = m.moments(eta,b)
            for key in ('rho','pressure_perp','pressure_parallel'):
                assert np.float64(d[key]).tobytes() == np.float64(getattr(original,key)).tobytes()
            actual = np.array([d['rho_eta'],d['pressure_perp_eta'],d['pressure_parallel_eta']])
            independent = complex_step(m,eta,b,v)
            np.testing.assert_allclose(actual,independent,rtol=8e-14,atol=1e-14)
            moment_max = max(moment_max,float(np.max(abs(actual-independent))))
            conservation_max = max(conservation_max,abs(d['energy_conservation_residual']))
            assert abs(d['energy_conservation_residual']) < 2e-14
        after = [a.tobytes() for a in (m._q,m._mu2,m._numbers,m._cell_numbers)]
        assert before == after
    groups.append({'name':'packet_chain_rule_and_energy_conservation', 'states':12,
                   'original_moment_FP64_bytes':'IDENTICAL',
                   'complex_step_max_absolute_difference':moment_max,
                   'maximum_energy_conservation_residual':conservation_max,
                   'inputs_unchanged':True})
    builder = baseline.IndependentStressBuilder(optimized=False)
    directional_max = 0.
    for coordinates in ((.012,.0002,-.0001),(-.012,-.0001,.0002),(0.,.0002,0.)):
        obj,_ = builder.build(*coordinates)
        state = obj.initial_state()
        before_counter = obj._nfev
        d = diagnostic.source_derivatives(obj,0.,state)
        assert obj._nfev == before_counter
        direction = d['source_rhs']
        def source_values(step):
            values=baseline.component_fields(obj.fields(step,state+step*direction))
            return [values[k] for k in ('signed_Sigma_F','signed_Pi_m_F','signed_Pi_r_F','signed_Pi_tot_F')]
        finite = forward4(source_values)
        analytic = np.array([d['signed_S_eta'],d['signed_P_eta']['m'],
                             d['signed_P_eta']['r'],d['signed_P_eta']['tot']])
        np.testing.assert_allclose(analytic,finite,rtol=2e-7,atol=1e-12)
        directional_max=max(directional_max,float(np.max(abs(analytic-finite))))
    groups.append({'name':'full_source_field_directional_derivative', 'states':3,
                   'forward_difference_order':4,'step':2e-4,
                   'max_absolute_difference':directional_max,'source_counter_preserved':True})
    jets=[]
    jet_second_max=0.
    for pm,pr in ((.0002,-.0002),(-.0002,.0002),(.0001,-.0001),
                  (-.0001,.0001),(.0002,0.),(0.,.0002),(0.,0.)):
        obj,_=builder.build(0.,pm,pr)
        state=obj.initial_state()
        d=diagnostic.source_derivatives(obj,0.,state)
        jet=diagnostic.initial_cancellation_jet(obj,state)
        assert abs(jet['actual_offset_Pprime_formula_residual'])<2e-14
        assert abs(jet['actual_offset_Ssecond_formula_residual'])<2e-14
        if pm and pm == -pr:
            assert pm*jet['mass_shell_release_direct']<0
        direction=d['source_rhs']
        numerical=float(forward4(lambda step: diagnostic.source_derivatives(
            obj,step,state+step*direction)['signed_S_eta']))
        np.testing.assert_allclose(jet['actual_Ssecond0'],numerical,rtol=2e-7,atol=1e-12)
        jet_second_max=max(jet_second_max,abs(jet['actual_Ssecond0']-numerical))
        jets.append({'requested_Pm0':pm,'requested_Pr0':pr,**jet})
    groups.append({'name':'initial_actual_offset_and_ideal_cancellation_jets',
                   'cases':len(jets),'second_derivative_directional_max_absolute_difference':jet_second_max,
                   'jets':jets})
    source=builder.identity()
    return {'schema':'C21N_MASS_SHELL_DERIVATIVE_STATIC_CHECKS_V1',
            'status':'PASS_SCOPED','source':source,'groups':groups,
            'diagnostic_sha256':hashlib.sha256(Path(diagnostic.__file__).read_bytes()).hexdigest(),
            'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'new_ODE_integrations':0,'finite_window_error_bound':None,'global_error_bound':None}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='c21n_derivative_mpl_') as cache:
        os.environ['MPLCONFIGDIR']=cache
        result=run(args.repo.resolve())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result,stream,indent=2,sort_keys=True,allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status':result['status'],'groups':len(result['groups']),
                      'new_ODE_integrations':0,'receipt':str(args.output)}))
