"""Create-only saved-grid/accepted-mesh omission diagnostics; no ODE calls."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
            'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[key] = '1'
import hashlib
import io
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

RUN = Path(__file__).resolve().parent
ROOT = RUN.parent.parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(ROOT))
from run_pilot import lease_snapshot
from run_pilot import resource_control
observe_resources = resource_control.observe_resources

snapshot = observe_resources()
reserved, lease = lease_snapshot(snapshot['allowed_cpus'])
cpu = 2
if cpu not in snapshot['allowed_cpus'] or cpu in reserved or cpu in (0, 1, 55):
    raise RuntimeError('DIAGNOSTIC_CPU_UNAVAILABLE')
if snapshot['per_cpu_busy'][cpu] > .35:
    raise RuntimeError('DIAGNOSTIC_CPU_BUSY')
os.sched_setaffinity(0, {cpu})

import numpy as np
from model import ThermochemicalFactory
from diagnose_omissions import diagnose_history


def write_json(path, data):
    with path.open('x') as f:
        json.dump(data, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def write_npz(path, data):
    with path.open('xb') as f:
        np.savez_compressed(f, **data)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


manifest = json.loads((RUN/'SOURCE_IDENTITY.json').read_bytes())
for row in manifest['files']:
    raw = (REPO/row['path']).read_bytes()
    if len(raw) != row['size_bytes'] or sha(raw) != row['sha256']:
        raise RuntimeError('FROZEN_SOURCE_MISMATCH:'+row['path'])
out = RUN/'omission_mesh_comparison_v1'
out.mkdir(exist_ok=False)
write_json(out/'RESOURCE.json', {
    'snapshot':snapshot, 'lease_observation':lease,
    'actual_affinity':sorted(os.sched_getaffinity(0)), 'single_process':True,
    'numerical_threads':1, 'protected_cpu':55,
    'excluded_coordinator_cpu':0, 'excluded_reference_worker_cpu':1,
    'new_ODE_runs':0})
inputs = json.loads((RUN/'INPUT.json').read_bytes())
factory = ThermochemicalFactory(ellmax=8)
diagnostic_sha = sha((ROOT/'diagnose_omissions.py').read_bytes())
cases = {}


def diagnose_from_bytes(raw, path, folder, metadata):
    with np.load(io.BytesIO(raw), allow_pickle=False) as arr:
        report, values = diagnose_history(arr)
    report['input'] = {'path':str(path), 'sha256':sha(raw), 'size_bytes':len(raw)}
    report['diagnostic_code_sha256'] = diagnostic_sha
    report['derivation'] = metadata
    folder.mkdir(exist_ok=False)
    write_json(folder/'OMISSIONS.json', report)
    write_npz(folder/'OMISSIONS.npz', values)
    return report


def comparison(a, b):
    return {'saved_201':a, 'accepted_mesh':b,
            'saved_minus_accepted':None if a is None or b is None else a-b,
            'relative_saved_minus_accepted':None if a is None or b in (None,0) else (a-b)/abs(b),
            'interpretation':'finite_quadrature_comparison; accepted_mesh_is_not_an_exact_integral_or_global_error_bound'}


for case in inputs['cases']:
    folder = RUN/'cases'/case['name']
    path = folder/'history.npz'
    raw = path.read_bytes()
    complete = json.loads((folder/'COMPLETE.json').read_bytes())
    if sha(raw) != complete['history_sha256']:
        raise RuntimeError('RAW_HISTORY_HASH_MISMATCH')
    with np.load(io.BytesIO(raw), allow_pickle=False) as data:
        eta = data['accepted_eta'].copy()
        y = data['accepted_Y'].copy()
        saved_temperature = data['temperature_K'].copy()
    saved = diagnose_from_bytes(raw, path, folder/'omissions_saved', {
        'mesh':'original_saved_201', 'raw_unchanged':True, 'new_ODE_runs':0})
    model = factory.build(case)
    accepted = model.summarize(eta, y)
    derived_folder = folder/'omissions_accepted'
    derived_folder.mkdir(exist_ok=False)
    derived_path = derived_folder/'accepted_history.npz'
    write_npz(derived_path, accepted)
    derived_raw = derived_path.read_bytes()
    accepted_report = diagnose_from_bytes(derived_raw, derived_path,
        derived_folder/'diagnostics', {
            'mesh':'original_solver_accepted_mesh', 'source_raw_sha256':sha(raw),
            'frozen_model_source_identity':manifest['identity_sha256'],
            'source_manifest_file_count':len(manifest['files']),
            'operation':'ThermochemicalModel.summarize(accepted_eta, accepted_Y)',
            'new_ODE_runs':0, 'new_solver_steps':0,
            'raw_unchanged':True, 'population_clipping':False})
    process = {}
    for key, row in saved['diagnostics'].items():
        other = accepted_report['diagnostics'][key]
        process[key] = {
            'availability_saved':row['availability'],
            'availability_accepted':other['availability'],
            'absolute_energy_eV_per_Href':comparison(
                row['integrated_absolute_energy_eV_per_Href']['value'],
                other['integrated_absolute_energy_eV_per_Href']['value']),
            'absolute_energy_over_initial_thermal':comparison(
                row['integrated_absolute_over_initial_Uthermal'],
                other['integrated_absolute_over_initial_Uthermal']),
            'absolute_energy_over_initial_total':comparison(
                row['integrated_absolute_over_initial_total_energy'],
                other['integrated_absolute_over_initial_total_energy']),
            'maximum_abs_rate_over_H_U':comparison(
                row['rate_over_H_Uthermal']['maximum_absolute'],
                other['rate_over_H_Uthermal']['maximum_absolute']),
            'available_time_fraction':comparison(
                row['integrated_absolute_energy_eV_per_Href']['available_duration_fraction'],
                other['integrated_absolute_energy_eV_per_Href']['available_duration_fraction']),
        }
    cases[case['name']] = {
        'raw_history_sha256':sha(raw),
        'accepted_history_sha256':sha(derived_raw),
        'saved_points':201, 'accepted_points':len(eta),
        'temperature_minmax_K_saved':[float(saved_temperature.min()),float(saved_temperature.max())],
        'temperature_minmax_K_accepted':[float(accepted['temperature_K'].min()),float(accepted['temperature_K'].max())],
        'included_RR_energy_eV_per_Href':comparison(
            saved['included_RR_cooling_integral_eV_per_Href']['value'],
            accepted_report['included_RR_cooling_integral_eV_per_Href']['value']),
        'processes':process,
        'negative_populations_saved':saved['population_numerical_residuals'],
        'negative_populations_accepted':accepted_report['population_numerical_residuals'],
    }
    print(json.dumps({'case':case['name'], 'accepted_points':len(eta),
                      'status':'DIAGNOSTICS_COMPLETE_SCOPED', 'new_ODE_runs':0}),flush=True)

result = {
    'schema':'C22A_OMISSION_SAVED_ACCEPTED_COMPARISON_V1',
    'created_utc':datetime.now(timezone.utc).isoformat(),
    'execution':'COMPLETE_SCOPED_POSTPROCESSING_ODE0',
    'publication':'PENDING', 'backup':'PENDING_NEW_PACKAGE',
    'DAG':'OMISSION_DIAGNOSTICS_COMPLETE_SCOPED;FULL_CLOSURE_OPEN',
    'source_identity_sha256':manifest['identity_sha256'],
    'source_manifest_files_verified':len(manifest['files']),
    'setup_attempt_history':[{'outcome':'ModuleNotFoundError: resource_control',
                             'correction':'reuse run_pilot.resource_control import',
                             'outputs_created':0, 'ODE_runs':0},
                            {'outcome':"KeyError: '2' in in-memory per_cpu_busy",
                             'correction':'integer CPU keys before JSON serialization',
                             'outputs_created':0, 'ODE_runs':0}],
    'diagnostic_code_sha256':diagnostic_sha,
    'driver_sha256':sha(Path(__file__).read_bytes()),
    'new_ODE_runs':0, 'old_C21O_ODE_runs':0,
    'cases':cases,
    'interpretation':'omitted_processes_evaluated_on_incomplete_original_trajectory; not_self_consistent_alternate_solution; trapezoids_on_two_finite_meshes_only; accepted_mesh_not_certified_quadrature_reference',
    'temperature_boundary_policy':'no_bridging_unavailable_intervals_no_extrapolation; different_available_intervals_can_contribute_to_mesh_difference',
    'global_error_bound':None,
}
write_json(out/'MESH_COMPARISON.json', result)
print(json.dumps(result,sort_keys=True),flush=True)
