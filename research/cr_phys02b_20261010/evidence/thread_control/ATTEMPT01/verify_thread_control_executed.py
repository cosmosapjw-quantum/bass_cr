# SPDX-License-Identifier: GPL-3.0-only
"""Focused canonical reproduction with explicit one-thread environment.

This does not rerun the scientific suite or change the physical operator.
"""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'evidence/thread_control'
contract = json.loads((OUT/'FOCUSED_CONTRACT.json').read_text())
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
t0 = time.perf_counter()


def identity(path):
    b = path.read_bytes()
    return {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}


def run():
    # Check process controls before importing any BLAS-dependent module.
    env = {k: os.environ.get(k) for k in contract['environment']}
    if env != contract['environment']:
        raise RuntimeError('EXPLICIT_THREAD_ENVIRONMENT_MISMATCH')
    import numpy as np
    import scipy
    from threadpoolctl import threadpool_info
    spec = importlib.util.spec_from_file_location('phys02b_thread_candidate', ROOT/'src/causal_cascade.py')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    reference_path = ROOT/contract['expected_reference']
    if identity(reference_path)['sha256'] != contract['reference_result_sha256']:
        raise RuntimeError('REFERENCE_RESULT_IDENTITY_MISMATCH')
    ref = json.loads(reference_path.read_text())
    for name, expected in ref['source_identities'].items():
        if identity(ROOT/name) != expected:
            raise RuntimeError('CANDIDATE_IDENTITY_MISMATCH: '+name)
    controls = threadpool_info()
    if not controls or any(x['num_threads'] != 1 for x in controls):
        raise RuntimeError('LOADED_NATIVE_THREAD_CONTROL_MISMATCH')
    resource = {}
    for f in ('memory.max', 'memory.current', 'cpu.max'):
        p = Path('/sys/fs/cgroup')/f
        resource[f] = p.read_text().strip() if p.exists() else 'UNAVAILABLE'
    resource['affinity_logical_cpus'] = len(os.sched_getaffinity(0))
    resource['concurrent_cascade_processes'] = 1
    # Prior same-shape execution succeeded; this run adds no concurrent solver.
    if resource['memory.max'].isdigit():
        limit = int(resource['memory.max'])
        reserve = max(1<<30, limit/8)
        estimated = 3*(1<<30)
        resource.update(reserve_bytes=reserve, conservative_incremental_estimate_bytes=estimated)
        current = int(resource['memory.current'])
        if limit-current-reserve < estimated:
            raise RuntimeError('INSUFFICIENT_MEMORY_FOR_ONE_CANONICAL_REPRODUCTION')
    print(json.dumps({'start_utc': started, 'environment': env,
                      'native_threadpools': controls, 'resource_observation': resource}), flush=True)
    source = mod.ElectronSource()
    model = mod.Cascade(*ref['canonical_mesh'])
    a = model.source_vectors(source)
    state = model.evolve(a, samples=2)[-1]
    summary = model.summarize(state, a, source, 1.)
    with np.load(ROOT/'evidence/runs/R002/CANONICAL_SPECTRUM.npz', allow_pickle=False) as r:
        if not np.array_equal(model.E, r['energy_eV']):
            raise RuntimeError('REFERENCE_GRID_MISMATCH')
        refstate = r['state_normalized'][-1]
        srcdiff = float(np.max(np.abs(a-r['source_vectors'])))
    ef,_ = model.functionals()
    scales = .5*(ef@a)
    state_error = np.max(np.abs(state-refstate), axis=0)/scales
    observable_errors = {}
    for tag, values in summary['components'].items():
        old = ref['final']['components'][tag]
        for name, value in values.items():
            if name.endswith('relative_residual'):
                continue
            oracle = old[name]
            error = abs(value-oracle)/abs(oracle) if oracle != 0 else abs(value-oracle)
            observable_errors[tag+'/'+name] = float(error)
    max_observable = max(observable_errors.values())
    passed = (float(max(state_error)) <= contract['state_normalized_linf_limit']
              and max_observable <= contract['positive_observable_relative_limit']
              and srcdiff <= contract['state_normalized_linf_limit'])
    np.savez_compressed(OUT/'ONE_THREAD_CANONICAL_STATE.npz', energy_eV=model.E,
                        state_normalized=state, source_vectors=a)
    proc = {}
    for line in Path('/proc/self/status').read_text().splitlines():
        if line.startswith(('VmPeak:', 'VmRSS:', 'VmHWM:', 'Threads:')):
            k,v = line.split(':',1)
            proc[k] = v.strip()
    return {'schema': 'cr-phys02b-focused-thread-control-result.v1',
            'status': 'PASS_SCOPED_THREAD_CONTROL' if passed else 'FAIL',
            'passed': passed, 'start_utc': started,
            'end_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'elapsed_seconds': time.perf_counter()-t0,
            'command': list(sys.argv), 'environment': env,
            'runtime': {'python': sys.version.split()[0], 'numpy': np.__version__, 'scipy': scipy.__version__},
            'native_threadpools': controls, 'resource_observation': resource,
            'process_peak_observation': proc,
            'contract_identity': identity(OUT/'FOCUSED_CONTRACT.json'),
            'script_identity': identity(Path(__file__)),
            'reference_result_identity': identity(reference_path),
            'physical_candidate_identities': ref['source_identities'],
            'canonical_cells': ref['canonical_mesh'], 'canonical_nodes': model.n,
            'actual_propagations': 1, 'scientific_suites_rerun': 0,
            'state_normalized_linf_per_tag': state_error.tolist(),
            'source_normalized_linf': srcdiff,
            'max_observable_relative_error': max_observable,
            'observable_relative_errors': observable_errors,
            'final': summary,
            'actual_state_identity': identity(OUT/'ONE_THREAD_CANONICAL_STATE.npz'),
            'limit': 'Explicit local thread-policy compliance and same-input FP64 reproducibility; original R002 thread count not retrospectively inferred; no physical accuracy or HPC64 speed claim.'}


try:
    result = run()
except Exception as exc:
    result = {'schema': 'cr-phys02b-focused-thread-control-result.v1', 'status': 'FAIL',
              'passed': False, 'start_utc': started,
              'end_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'elapsed_seconds': time.perf_counter()-t0,
              'exception_type': type(exc).__name__, 'exception': str(exc)}
    import traceback
    traceback.print_exc()
(OUT/'THREAD_CONTROL_RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result), flush=True)
raise SystemExit(0 if result['passed'] else 1)
