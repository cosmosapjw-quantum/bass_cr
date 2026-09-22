#!/usr/bin/env python3
"""Metadata-only B2 plan: no grid, CUDA allocation, or scientific process launch.

Atomic units follow the frozen TDL runner. The kinetic phase and mesh-crossing
sampling are diagnostics, not stability/CFL or probability-error certificates.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from cr_repro.observables import projectile_speed_au
from cr_repro.r3m11 import source_digest

FROZEN_SOURCE = '581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b'
FROZEN_HEAD = '7844bc0d8122070b267ee77c75cb2c9447435155'
FROZEN_B1_CONFIG_SHA256 = '7a7fc7a4ea484fa65d73d38eeb49b628760a7b4ed144075275988139c0c8ab2c'
SCIENCE_PYTHON = '/mnt/sn850x2t/bass_cr_r3m11_20260921/.venv/bin/python'
CHUNK_STEPS = 128
REQUIRED_RUNTIME = {
    'python': '3.12.3', 'numpy': '2.5.3', 'scipy': '1.18.1', 'cupy': '14.2.0',
    'cuda_runtime': 12090, 'cuda_driver_api': 13020,
    'nvidia_driver': '595.84', 'device': 'NVIDIA GeForce RTX 3090',
}


def _positive(value, name):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be finite and positive')
    return value


def _sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def validate_b2_config(cfg):
    """Only requested real dt changes from canonical B1; all other keys match."""
    reference = ROOT/'configs/r3m16/B1.json'
    if _sha(reference) != FROZEN_B1_CONFIG_SHA256:
        raise ValueError('frozen B1 reference config byte identity changed')
    expected = json.loads(reference.read_text())
    expected['dt'] = .0125
    if cfg != expected:
        raise ValueError('B2 config family differs from frozen B1 plus requested dt=.0125')
    if source_digest() != FROZEN_SOURCE:
        raise ValueError('frozen numerical source mismatch')


def _grid_geometry(grid):
    h = _positive(grid['dx'], 'dx')
    intervals, shape = [], []
    for key in ('xlim', 'ylim', 'zlim'):
        if len(grid[key]) != 2:
            raise ValueError('each grid interval must have two endpoints')
        lo, hi = map(float, grid[key])
        if not all(math.isfinite(x) for x in (lo, hi)) or hi <= lo:
            raise ValueError('finite increasing grid bounds required')
        n = round((hi-lo)/h)
        if n < 2 or abs(n*h-(hi-lo)) > 1e-9:
            raise ValueError('grid lengths must be integer multiples of dx with at least two points')
        intervals.append((lo, hi)); shape.append(n)
    return h, intervals, tuple(shape)


def _axis_point(point, lo, n, h):
    """Distance to a finite cell-centered axis without constructing the axis."""
    u = (point-lo)/h-.5
    nearest = min(n-1, max(0, round(u)))
    delta = u-nearest
    # Floating descriptions of offsets such as -29.9 + .1 reach a center within
    # coordinate-roundoff. This resolves representational zero, not a soft core.
    tol = 16*sys.float_info.epsilon*max(1., abs(u), abs(lo/h), abs(point/h))
    is_center = abs(delta) <= tol
    return {
        'nearest_index': int(nearest), 'distance_over_h': abs(delta),
        'distance_a0': abs(delta)*h, 'cell_center_phase_fraction': u-math.floor(u),
        'coincides_with_cell_center_to_coordinate_roundoff': is_center,
        'coordinate_roundoff_tolerance_over_h': tol,
    }


def _interval_axis_distance(start, stop, lo, n, h):
    lower, upper = sorted((start, stop))
    first = max(0, math.ceil((lower-lo)/h-.5))
    last = min(n-1, math.floor((upper-lo)/h-.5))
    if first <= last:
        return 0., True
    return min(_axis_point(lower,lo,n,h)['distance_a0'],
               _axis_point(upper,lo,n,h)['distance_a0']), False


def fft_kinetic_metadata(shape, h, actual_dt):
    h = _positive(h, 'h'); actual_dt = _positive(actual_dt, 'actual_dt')
    if len(shape) != 3 or any(isinstance(n,bool) or int(n) != n or n < 2 for n in shape):
        raise ValueError('three integer FFT lengths >=2 required')
    kmax = [2*math.pi*(n//2)/(n*h) for n in shape]
    energy = .5*sum(k*k for k in kmax)
    return {
        'axis_kmax_au_inverse': kmax, 'axis_parity': ['even' if n%2 == 0 else 'odd' for n in shape],
        'maximum_kinetic_energy_Eh': energy,
        'maximum_kinetic_phase_radians': actual_dt*energy,
        'formula': 'kmax_i=2*pi*floor(n_i/2)/(n_i*h); Tmax=sum(kmax_i^2)/2',
        'universal_CFL_stability_limit_claimed': False,
        'interpretation': 'operator-bandwidth diagnostic; no universal state-dependent splitting error or stability certificate',
    }


def numerical_metadata(cfg):
    """Audit generic frozen-style geometry for A/B/C and future B2, without arrays."""
    h, bounds, shape = _grid_geometry(cfg['grid'])
    dt = _positive(cfg['dt'], 'requested dt')
    energy = _positive(cfg['energy_keV_per_u'], 'energy')
    b, start, stop = map(float, (cfg['b'], cfg.get('z_start',-30.), cfg.get('z_stop',60.)))
    if not all(math.isfinite(x) for x in (b,start,stop)) or stop <= start:
        raise ValueError('finite geometry with z_stop>z_start required')
    v = projectile_speed_au(energy)
    horizon = (stop-start)/v
    nstep = math.ceil(horizon/dt); actual = horizon/nstep
    target = [_axis_point(0., interval[0], n, h) for interval,n in zip(bounds,shape)]
    if all(axis['coincides_with_cell_center_to_coordinate_roundoff'] for axis in target):
        raise ValueError('target point-Coulomb singularity lies on a grid sample')
    transverse = [_axis_point(pos,bounds[j][0],shape[j],h) for j,pos in enumerate((b,0.))]
    dz, contains_center = _interval_axis_distance(start,stop,bounds[2][0],shape[2],h)
    if contains_center and all(axis['coincides_with_cell_center_to_coordinate_roundoff'] for axis in transverse):
        raise ValueError('projectile path intersects a sampled point-Coulomb singularity')
    rho = math.hypot(*(axis['distance_a0'] for axis in transverse))
    match = all(abs((target[j]['cell_center_phase_fraction']-
                     transverse[j]['cell_center_phase_fraction']+.5)%1.-.5) <= 1e-12
                for j in range(2))
    chunk_count = math.ceil(nstep/CHUNK_STEPS)
    return {
        'grid_shape': list(shape), 'grid_points': math.prod(shape),
        'requested_dt': dt, 'actual_dt': actual, 'nstep': nstep,
        'physical_horizon_au': horizon, 'speed_au': v,
        'chunk_max_steps': CHUNK_STEPS, 'chunk_count': chunk_count,
        'last_chunk_steps': nstep-(chunk_count-1)*CHUNK_STEPS,
        'fft_kinetic': fft_kinetic_metadata(shape,h,actual),
        'target': {
            'axis_phases': target,
            'nearest_sample_radius_a0': math.sqrt(sum(axis['distance_a0']**2 for axis in target)),
        },
        'projectile': {
            'axis_phases_xy': transverse,
            'nearest_transverse_axis_distance_over_h': [x['distance_over_h'] for x in transverse],
            'minimum_transverse_distance_a0': rho, 'minimum_transverse_distance_over_h': rho/h,
            'path_contains_z_cell_center': contains_center,
            'minimum_sample_distance_over_continuous_path_a0': math.hypot(rho,dz),
            'displacement_per_step_a0': v*actual,
            'displacement_per_step_over_h': v*actual/h,
            'steps_per_grid_crossing': h/(v*actual),
            'mesh_phase_matches_target_transverse': match,
            'interpretation': 'geometric sampling diagnostics, not a capture-probability error estimate',
        },
    }


def _installed_version(*names):
    for name in names:
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    return None


def runtime_metadata(scientific_python):
    """Inspect caller only; the authorized science interpreter is never launched."""
    caller = {
        'python': platform.python_version(), 'numpy': _installed_version('numpy'),
        'scipy': _installed_version('scipy'),
        'cupy': _installed_version('cupy','cupy-cuda12x','cupy-cuda13x'),
        'cuda_runtime': None, 'cuda_driver_api': None, 'nvidia_driver': None, 'device': None,
    }
    return {
        'caller_interpreter': sys.executable, 'caller_metadata': caller,
        'required_scientific_interpreter': str(scientific_python),
        'required_scientific_interpreter_exists': Path(scientific_python).is_file(),
        'required_scientific_environment': REQUIRED_RUNTIME,
        'caller_comparison_to_required': {
            key: 'NOT_INSPECTED' if caller[key] is None else
            ('MATCH' if caller[key] == required else 'DIFFERS')
            for key,required in REQUIRED_RUNTIME.items()
        },
        'science_environment_verified': False,
        'science_environment_status': 'REQUIRES_ACTUAL_RUNTIME_IDENTITY_AND_EXISTING_RESOURCE_PREFLIGHT',
        'CUDA_imported_or_initialized': False,
        'cpu_fallback_allowed': False, 'package_upgrade_authorized': False,
    }


def build_preflight(cfg, *, config_path, job_root, scientific_python=SCIENCE_PYTHON):
    validate_b2_config(cfg)
    numerical = numerical_metadata(cfg)
    config_path, job_root = Path(config_path), Path(job_root)
    if config_path.exists() and (not config_path.is_file() or json.loads(config_path.read_text()) != cfg):
        raise ValueError('config file is not the validated B2 config')
    prepared, collision = job_root/'preparation', job_root/'collision'
    commands = [
        {'phase':'resource_preflight', 'argv':[str(scientific_python), str(ROOT/'scripts/r3m15_resource_probe.py'),
          '--config',str(config_path),'--out',str(job_root/'resource.json')]},
        {'phase':'prepare', 'argv':[str(scientific_python),str(ROOT/'scripts/r3m13_initial_state_pair.py'),
          'prepare','--config',str(config_path),'--out',str(prepared)]},
    ]
    for chunk in range(1,numerical['chunk_count']+1):
        done = min(chunk*CHUNK_STEPS,numerical['nstep'])
        commands.append({
            'phase':'collision_chunk','chunk':chunk,
            'maximum_steps_in_chunk':min(CHUNK_STEPS,numerical['nstep']-(chunk-1)*CHUNK_STEPS),
            'argv':[str(scientific_python),str(ROOT/'scripts/r3m14_collision_initial_witness.py'),
                    '--config',str(config_path),'--prepared',str(prepared),
                    '--out',str(collision),'--max-steps',str(CHUNK_STEPS)],
            'must_stop_on_previous_failure':True,
            'sealed_restart_and_same_runtime_required':chunk>1,
            'stdout_path':str(job_root/f'collision.chunk{chunk:03d}.stdout'),
            'stderr_path':str(job_root/f'collision.chunk{chunk:03d}.stderr'),
        })
        commands.append({
            'phase':'checkpoint_snapshot','chunk':chunk,'expected_completed_steps':done,
            'argv':[str(scientific_python),str(ROOT/'scripts/r3m17_checkpoint_guard.py'),
                    'snapshot','--run',str(collision),
                    '--out',str(job_root/'generations'/f'g{done:06d}'),
                    '--config',str(config_path)],
            'must_stop_on_previous_failure':True,
            'must_finish_before_next_collision_chunk':True,
            'required_witness':'R3M14_V2_WITH_PREPARED_AND_INTERNAL_ARRAY_DIGESTS',
        })
    # Complex128 payload dominates retention. The 128-byte NPY header is the
    # canonical array estimate; actual header/metadata/filesystem overhead must
    # be checked locally before launching any scientific process.
    state_estimate = numerical['grid_points']*16+128
    return {
        'schema':'BASS_CR_R3M17_B2_METADATA_PREFLIGHT_V2',
        'status':'PLAN_ONLY_NOT_EXECUTED','collision_execution_performed':False,
        'new_collision_budget':1, 'job':'B2',
        'frozen_authority_commit':FROZEN_HEAD,'numerical_source_digest':source_digest(),
        'instrumentation_sha256':_sha(Path(__file__)),
        'reference_B1_config_sha256':_sha(ROOT/'configs/r3m16/B1.json'),
        'config':cfg,'config_path':str(config_path),
        'config_file_sha256':_sha(config_path) if config_path.is_file() else None,
        'config_file_verified':config_path.is_file(),
        'job_root':str(job_root),'job_root_already_exists':job_root.exists(),
        'command_working_directory':str(ROOT),
        'command_environment_required':{
            'PYTHONPATH':str(ROOT),'PYTHONDONTWRITEBYTECODE':'1',
            'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1',
        },
        'CUDA_library_path_policy':'reuse and verify the existing R3M16 scientific environment; do not guess or upgrade libraries',
        'numerical':numerical,'runtime':runtime_metadata(scientific_python),
        'checkpoint_retention':{
            'generation_parent':str(job_root/'generations'),
            'create_parent_on_same_filesystem_as_collision_before_execution':True,
            'state_file_bytes_estimate':state_estimate,
            'retained_generation_count':numerical['chunk_count'],
            'retained_state_bytes_estimate':state_estimate*numerical['chunk_count'],
            'minimum_free_disk_floor_bytes':40*1024**3,
            'floor_is_sufficient_space_certificate':False,
            'additional_space_required_for':'live/replacement/prepared arrays, metadata, logs, archives and filesystem overhead; calculate actual total locally',
        },
        'prerequisites':{
            'plan_is_execution_authorization':False,
            'exact_config_file_must_exist_and_match_plan_before_execution':True,
            'fresh_output_or_explicit_preserved_failure_reconciliation_required':True,
            'fresh_B2_preparation_receipt_for_exact_B2_config_required':True,
            'same_grid_preparation_byte_identity_required':True,
            'preparation_binding_reference':'historical B1/R3M15 B same-grid saved initial array; compare array dtype/shape/content identity before propagation',
            'internal_initial_binding':'existing R3M14 v2 witness must PASS; do not substitute states or weaken receipt compatibility',
            'historical_source_result_state_seal_bytes_immutable':True,
            'actual_resource_probe_PASS_required':True,
            'stdout_stderr_separated_and_failures_preserved':True,
            'no_repeat_after_completed_collision':True,
            'restart_retention':'preserve a verified complete checkpoint generation before replacing the next; current in-place pair is not transactional',
        },
        'command_plan':commands,
        'claim_ceiling':{
            'temporal_budget_closed':False,'representation_change_authorized':False,
            'all_bound_admitted':False,'bgrid_admitted':False,'physical_rate_admitted':False,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True,type=Path)
    parser.add_argument('--job-root',required=True,type=Path)
    parser.add_argument('--scientific-python',default=SCIENCE_PYTHON)
    parser.add_argument('--out',required=True,type=Path)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    result = build_preflight(cfg,config_path=args.config,job_root=args.job_root,
                             scientific_python=args.scientific_python)
    write_new(args.out,result)
    print(json.dumps({'status':result['status'],'nstep':result['numerical']['nstep'],
                      'chunks':result['numerical']['chunk_count'],'out':str(args.out)},allow_nan=False))


if __name__ == '__main__':
    main()
