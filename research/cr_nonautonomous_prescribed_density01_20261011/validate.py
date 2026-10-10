"""Frozen prescribed-density experiment; no production/provider mutation."""
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import sys
import time
import traceback

import numpy as np
import scipy
from scipy.sparse.linalg import expm_multiply

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'cr_phys02b_delay_20261010'
sys.path.insert(0, str(SOURCE))
import causal_generator as c

T = 1e13
ENERGIES = np.array([20., 100., 1000.])
REI = Path('/tmp/rei-cold-conditional-ivp01-20261011/research/cold_conditional_ivp01_20261011')
PINS = {
    SOURCE / 'causal_generator.py': 'ea72b12d07bc500cb7c917c5e500325c6864da77cdd90637ddceab7aeddfa0da',
    SOURCE / 'SOURCE_MANIFEST.json': 'e803089f05c46fa3d054b0172914a524244df1aaf32045c4eefa35c136efa2cb',
    REI / 'evidence/RESULTS.json': '0c00898ab15025cae874b026e52ecc99a357496a5db5c230f8d39a834a8b5818',
    REI / 'CONTRACT.json': 'f7f90c9c0160a8f3d9c2367b53d508543cc4ac0b85ebc8a27f98062b4c297173',
    REI / 'independent_review.json': '7ac2643da76771b7a48aa0357b4fd7ab574e4c5d9d92f3d807f1375436947fb7',
}
wall0, cpu0 = time.monotonic(), time.process_time()
result = {'unit': 'CR_NONAUTONOMOUS_PRESCRIBED_DENSITY01', 'status': 'RUNNING',
          'base': '5a95e976aef0e2b1e399174c120c9d23c5d4d930',
          'command': 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B research/cr_nonautonomous_prescribed_density01_20261011/validate.py',
          'requested_role': 'lower-tier implementation', 'observed_model': 'NOT_OBSERVED',
          'checks': {}, 'cases': {}, 'total_response_steps': 0, 'block_actions': 0,
          'columns_per_action': 3,
          'global_scientific_admission': 'HOLD', 'independent_review': 'PENDING'}

def save():
    result['wall_s'] = time.monotonic() - wall0
    result['cpu_s'] = time.process_time() - cpu0
    (ROOT / 'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')

def require(name, condition, evidence=None):
    result['checks'][name] = {'pass': bool(condition), 'evidence': evidence}
    save()
    if not condition:
        raise RuntimeError('FIRST_FAILURE:' + name)

def budget():
    if time.monotonic() - wall0 > 900 or time.process_time() - cpu0 > 900:
        raise RuntimeError('CAMPAIGN_BUDGET')
    if result['total_response_steps'] > 6560 or result['block_actions'] > 10658:
        raise RuntimeError('CAMPAIGN_ACTION_BUDGET')

def alarm(signum, frame):
    raise RuntimeError('CAMPAIGN_WALL_LIMIT')

def bath(tau):
    if not 0 <= tau <= 2.5e13:
        raise ValueError('ABSOLUTE_BATH_TIME_DOMAIN')
    nhi, nhii, nhei = densities[0] + tau / 2.5e13 * (densities[1] - densities[0])
    nh = nhi + nhii
    return c.Gas(n_h_m3=float(nh), helium_mass_fraction=float(4*nhei/(nh+4*nhei)),
                 x_hii_per_h=float(nhii/nh), x_heii_per_he=0., x_heiii_per_he=0., temperature_k=100.)

def initial(g):
    return np.column_stack([g.impulse(float(e)) for e in ENERGIES])

def observations(g, state, grid):
    rows = [g.observe(c.CharacteristicState(state[:, j], grid, 0.)) for j in range(3)]
    for j, row in enumerate(rows):
        require('finite_nonnegative', bool(np.all(np.isfinite(state))) and float(state.min()) >= 0,
                {'minimum': float(state.min())})
        require('ledger', abs(row['number_ledger']-1) <= 2e-11 and
                abs(row['energy_ledger_eV']/ENERGIES[j]-1) <= 2e-11,
                {'E0': float(ENERGIES[j]), 'N': row['number_ledger'], 'U': row['energy_ledger_eV']})
        require('HeII_structural_zero', row['ionization_counts'][2] == 0 and row['excitation_counts'][2] == 0)
    channels = np.array([[r[k] for k in ('active_energy_eV', 'binding_energy_eV',
                         'excitation_energy_eV', 'coulomb_heat_eV', 'cutoff_energy_eV')] for r in rows])
    return rows, channels / ENERGIES[:, None]

def run_case(name, steps, order=8, method='sparse', constant=False):
    g = c.assemble(128, bath(0), order)
    state, grid = initial(g), g.grid.copy()
    rows, channels = observations(g, state, grid)
    case = {'steps': steps, 'order': order, 'method': method, 'constant_bath': constant,
            'observations': [{'tau': 0., 'rows': rows}], 'maximum_collision_cfl': 0.}
    result['cases'][name] = case
    output = [channels]
    h = T / steps
    for i in range(steps):
        budget()
        gas = bath(0 if constant else (i+.5)*h)
        mid = c.characteristic_grid(grid, gas, h/2)
        state[-3] += (grid-mid) @ state[:g.n]
        matrix = c.collision_matrix(mid, gas, order)
        result['total_response_steps'] += 1
        if method == 'ssprk2':
            cfl = h * float(np.max(-matrix.diagonal()))
            case['maximum_collision_cfl'] = max(case['maximum_collision_cfl'], cfl)
            if cfl > .4:
                raise RuntimeError('SSPRK2_COLLISION_CFL')
            result['block_actions'] += 1
            stage = state + h*(matrix @ state)
            result['block_actions'] += 1
            state = .5*state + .5*(stage + h*(matrix @ stage))
        else:
            result['block_actions'] += 1
            state = expm_multiply(h*matrix, state, traceA=h*float(matrix.diagonal().sum()))
        grid = c.characteristic_grid(mid, gas, h/2)
        state[-3] += (mid-grid) @ state[:g.n]
        if (i+1) % (steps//4) == 0:
            rows, channels = observations(g, state, grid)
            case['observations'].append({'tau': (i+1)*h, 'rows': rows})
            output.append(channels)
            save()
    case['wall_s_at_completion'] = time.monotonic()-wall0
    print(name, 'completed', flush=True)
    save()
    return np.array(output)

def main():
    global densities
    if (ROOT/'RESULTS.json').exists():
        raise FileExistsError('CAMPAIGN_ALREADY_STARTED')
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(900)
    resource.setrlimit(resource.RLIMIT_CPU, (900, 901))
    result['environment'] = {'python': platform.python_version(), 'numpy': np.__version__,
                             'scipy': scipy.__version__, 'threads': {k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')}}
    try:
        for p, expected in PINS.items():
            actual = hashlib.sha256(p.read_bytes()).hexdigest()
            require('pin:'+str(p), actual == expected, actual)
        result['source_manifest_verified'] = c.verify_sources()
        payload = json.loads((REI/'evidence/RESULTS.json').read_text())
        native = [r for r in payload['native'] if r['id']==0 and r['n']==32 and r['control']=='physical']
        require('unique_native_payload', len(native)==1)
        epochs = native[0]['epochs'][:2]
        densities = np.array([[e[2],e[3],e[11]] for e in epochs])
        result['bath_input'] = {'epochs': epochs, 'tau_s': [0.,2.5e13], 'density_columns':[2,3,11],
                                'stored_cold_temperature': 'NOT_USED', 'temperature_k':100.,
                                'normalization':'per initial electron; no a^3 or dilution'}
        g = c.assemble(128,bath(0),8)
        y = initial(g)
        require('t0_OFF_identity', np.array_equal(c.evolve(g,y,0.),y) and np.array_equal(c.evolve(g,y,T,enabled=False),y))
        require('zero_deposited_energy_initial', bool(np.all(y[g.n:g.n+7] == 0)))
        try:
            c.Gas(temperature_k=1.)
        except ValueError as exc:
            require('cold_temperature_rejected', str(exc)=='ONLY_100K_CONTRACT')
        else:
            require('cold_temperature_rejected', False)
        analytic_control()
        main_outputs = [run_case('main'+str(n),n) for n in (128,256,512)]
        daughter = run_case('daughter12',512,order=12)
        require('daughter_quadrature', float(np.max(np.abs(daughter-main_outputs[-1])))<=1e-8,
                float(np.max(np.abs(daughter-main_outputs[-1]))))
        reference = run_case('reference_ssprk2',4096,method='ssprk2')
        errors = [float(np.max(np.abs(o-reference))) for o in main_outputs]
        require('main_refinement', errors[-1]<=2e-4 and errors[0]>errors[1]>errors[2], errors)
        continuation = run_case('constant_continuation',512,constant=True)
        legacy,legacy_rows=legacy_case(g,y)
        result['cases']['legacy_P02B']={'shared_timeline_steps':512,'observations':legacy_rows}
        require('legacy_continuation', float(np.max(np.abs(continuation-np.array(legacy))))<=2e-4,
                float(np.max(np.abs(continuation-np.array(legacy)))))
        result['status']='IMPLEMENTED_VALIDATION_PASS_PENDING_ASTRA'
    except Exception as exc:
        result['status']='FIRST_FAILURE_HOLD'
        result['failure']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
        print(result['failure']['traceback'],flush=True)
    finally:
        signal.alarm(0)
        save()
    return 0 if result['status']=='IMPLEMENTED_VALIDATION_PASS_PENDING_ASTRA' else 1

def analytic_control():
    gas=c.Gas(n_h_m3=140.,x_hii_per_h=0.,x_heii_per_he=0.,x_heiii_per_he=0.,temperature_k=100.)
    g=c.assemble(128,gas,8)
    y=initial(g)
    matrix=g.matrix
    result['analytic'] = []
    endpoints=[]
    for born,clock in ((0.,5*T/8),(T/2,7*T/8)):
        state=y.copy()
        h=T/32
        for i in range(16):
            budget()
            tau=born+(i+.5)*h
            scaled=matrix*(h*(1+tau/T))
            result['total_response_steps'] += 1
            result['block_actions'] += 1
            state=expm_multiply(scaled,state,traceA=float(scaled.diagonal().sum()))
        result['block_actions'] += 1
        direct=expm_multiply(matrix*clock,y,traceA=float(matrix.diagonal().sum()*clock))
        state_scale=np.maximum(1.,np.max(np.abs(direct),axis=0))
        error=float(np.max(np.abs(state-direct)/state_scale))
        rows,_=observations(g,state,g.grid)
        require('analytic_clock_'+str(born),error<=2e-11,error)
        result['analytic'].append({'born_tau':born,'age_s':T/2,'end_tau':born+T/2,
                                   'integrated_clock_s':clock,'steps':16,'normalized_state_error':error,'rows':rows})
        endpoints.append(state)
    require('analytic_absolute_time_distinguishes_equal_ages',not np.array_equal(*endpoints))

def legacy_case(g,y):
    state=y.copy()
    old_grid=g.grid.copy()
    rows,ch=observations(g,state,old_grid)
    channels=[ch]
    records=[{'tau':0.,'rows':rows}]
    h=T/512
    for i in range(512):
        budget()
        mid_grid=c.characteristic_grid(g.grid,g.gas,(i+.5)*h)
        new_grid=c.characteristic_grid(g.grid,g.gas,(i+1)*h)
        state[-3] += (old_grid-mid_grid) @ state[:g.n]
        matrix=c.collision_matrix(mid_grid,g.gas,8)
        result['total_response_steps'] += 1
        result['block_actions'] += 1
        state=expm_multiply(h*matrix,state,traceA=h*float(matrix.diagonal().sum()))
        state[-3] += (mid_grid-new_grid) @ state[:g.n]
        old_grid=new_grid
        if (i+1)%128==0:
            rows,ch=observations(g,state,old_grid)
            channels.append(ch); records.append({'tau':(i+1)*h,'rows':rows})
    print('legacy_P02B completed',flush=True)
    return np.array(channels),records

if __name__=='__main__':
    sys.exit(main())
