"""One Astra-authorized repair campaign; original calculation is imported unchanged."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import signal
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT.parent
PINS = {
    ORIGINAL / 'RESULTS.json': 'ee26c7f4386779c4f2bb2508b2ccec6df1465da7a9b6848ff807ba2e61f6fd8e',
    ORIGINAL / 'validate.py': '985c155cfe9109e757c7a9785caf619e097b3d44e5c59907fe12f1d53556d110',
    ORIGINAL / 'CONTRACT.json': '4db788aeb4af86d36c9425e481fabac2f7c20f7a820e2eec246b0a64712215fb',
}
for path, expected in PINS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise RuntimeError('IMMUTABLE_ORIGINAL_IDENTITY:' + str(path))
spec = importlib.util.spec_from_file_location('original_prescribed_campaign', ORIGINAL / 'validate.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
np = v.np
v.ROOT = ROOT
v.wall0, v.cpu0 = time.monotonic(), time.process_time()
v.result = {
    'unit': 'CR_NONAUTONOMOUS_PRESCRIBED_DENSITY01_REPAIR01', 'status': 'RUNNING',
    'base': '5a95e976aef0e2b1e399174c120c9d23c5d4d930',
    'command': 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B research/cr_nonautonomous_prescribed_density01_20261011/repair01/validate_refinement.py',
    'requested_role': 'lower-tier implementation/execution', 'observed_model': 'NOT_OBSERVED',
    'checks': {}, 'cases': {}, 'total_response_steps': 0, 'block_actions': 0,
    'columns_per_action': 3, 'independent_review': 'PENDING', 'global_scientific_admission': 'HOLD',
    'preserved_original_inputs': {str(p.resolve()): h for p, h in PINS.items()},
    'reused_controls': 'Original t0/OFF, zero initial energy, cold guard, analytic absolute-clock results retained; not rerun',
}

def budget():
    if time.monotonic() - v.wall0 > 360 or time.process_time() - v.cpu0 > 360:
        raise RuntimeError('REPAIR01_BUDGET')
    if v.result['total_response_steps'] > 6144 or v.result['block_actions'] > 6144 or v.result['block_actions'] * 3 > 18432:
        raise RuntimeError('REPAIR01_ACTION_BUDGET')

v.budget = budget

def saved_channels(case):
    keys = ('active_energy_eV', 'binding_energy_eV', 'excitation_energy_eV', 'coulomb_heat_eV', 'cutoff_energy_eV')
    return np.array([[[row[k] for k in keys] for row in epoch['rows']] for epoch in case['observations']]) / v.ENERGIES[None, :, None]

def difference(left, right):
    return float(np.max(np.abs(left - right)))

def main():
    if (ROOT / 'RESULTS.json').exists():
        raise FileExistsError('REPAIR01_ALREADY_STARTED')
    signal.signal(signal.SIGALRM, v.alarm)
    signal.alarm(360)
    resource.setrlimit(resource.RLIMIT_CPU, (360, 361))
    v.result['environment'] = {'python': platform.python_version(), 'numpy': np.__version__,
        'scipy': v.scipy.__version__, 'threads': {k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS')}}
    v.result['driver_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    v.result['contract_sha256'] = hashlib.sha256((ROOT / 'CONTRACT.json').read_bytes()).hexdigest()
    try:
        for path, expected in v.PINS.items():
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            v.require('pin:' + str(path), actual == expected, actual)
        v.result['source_manifest_verified'] = v.c.verify_sources()
        old = json.loads((ORIGINAL / 'RESULTS.json').read_text())
        v.densities = np.array([[e[2], e[3], e[11]] for e in old['bath_input']['epochs']])
        v.result['bath_input'] = old['bath_input']
        reference = saved_channels(old['cases']['reference_ssprk2'])
        sparse512 = saved_channels(old['cases']['main512'])
        v.require('saved_reference_epoch_times', [e['tau'] for e in old['cases']['reference_ssprk2']['observations']] == [0., v.T/4, v.T/2, 3*v.T/4, v.T])
        continuation = v.run_case('constant512', 512, constant=True)
        g = v.c.assemble(128, v.bath(0), 8)
        legacy, records = v.legacy_case(g, v.initial(g))
        v.result['cases']['legacy512'] = {'shared_timeline_steps': 512, 'observations': records}
        v.require('constant_legacy', difference(continuation, legacy) <= 2e-4, difference(continuation, legacy))
        sparse1024 = v.run_case('sparse1024', 1024)
        sparse2048 = v.run_case('sparse2048', 2048)
        errors = [difference(output, reference) for output in (sparse512, sparse1024, sparse2048)]
        v.require('main_refinement', errors[0] > errors[1] > errors[2] and errors[2] <= 2e-4, errors)
        daughter = v.run_case('daughter12_2048', 2048, order=12)
        v.require('daughter_quadrature', difference(daughter, sparse2048) <= 1e-8, difference(daughter, sparse2048))
        budget()
        for path, expected in PINS.items():
            v.require('preserved:' + str(path), hashlib.sha256(path.read_bytes()).hexdigest() == expected)
        v.result['column_actions'] = v.result['block_actions'] * 3
        v.result['status'] = 'IMPLEMENTED_VALIDATION_PASS_PENDING_ASTRA'
    except Exception as exc:
        v.result['status'] = 'FIRST_FAILURE_HOLD'
        v.result['failure'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
        print(v.result['failure']['traceback'], flush=True)
    finally:
        signal.alarm(0)
        v.result['column_actions'] = v.result['block_actions'] * 3
        v.save()
    return 0 if v.result['status'] == 'IMPLEMENTED_VALIDATION_PASS_PENDING_ASTRA' else 1

if __name__ == '__main__':
    sys.exit(main())
