"""CPU-first opt-in coordinator. Backend construction is the GPU boundary.

No automatic retry. A failed attempt is immutable. To reuse sealed successful
windows, explicitly freeze a new contract pointing to their manifests and use a
fresh output directory. Inherited work and this attempt's work stay separate.
"""
from __future__ import annotations

from contextlib import ExitStack
import os
from pathlib import Path
import time
from typing import Callable

from .r3m24_guard import (bind_generation, file_sha, fsync_dir, object_sha,
                          publish_json, read_json, safe_path)


def check_sources(plan: dict) -> None:
    root = safe_path(plan['root'])
    for relative, expected in plan['sources'].items():
        path = safe_path(root/relative)
        if not path.is_relative_to(root) or file_sha(path) != expected:
            raise ValueError(f'execution source identity mismatch: {relative}')


def read_window(directory: Path | str, plan: dict, spec: dict,
                manifest_sha: str | None = None) -> dict:
    root = safe_path(directory)
    manifest = read_json(root/'MANIFEST.json',manifest_sha)
    if set(p.name for p in root.iterdir()) != {'RESULT.json','MANIFEST.json'}:
        raise ValueError('partial/foreign window evidence; retain for diagnosis')
    for key, value in dict(schema='BASS_CR_R3M24_WINDOW_SEAL_V1',
                           computation_key=plan['computation_key'], label=spec['label'],
                           checkpoint_sha256=spec['expected_state_npy_sha256'],
                           input_spec_sha256=object_sha(spec)).items():
        if manifest.get(key) != value:
            raise ValueError(f'window binding mismatch: {key}')
    result = read_json(root/'RESULT.json',manifest['result_sha256'])
    if (result.get('label') != spec['label'] or result.get('production_admission') is not False or
            result.get('checkpoint_sha256') != spec['expected_state_npy_sha256']):
        raise ValueError('window result identity/scope mismatch')
    return dict(directory=str(root), manifest_sha256=file_sha(root/'MANIFEST.json'), result=result)


def _save_window(out: Path, plan: dict, spec: dict, result: dict) -> dict:
    root = out/'windows'/spec['label']
    root.mkdir(exist_ok=False); fsync_dir(root.parent)
    publish_json(root/'RESULT.json',result)
    publish_json(root/'MANIFEST.json',dict(schema='BASS_CR_R3M24_WINDOW_SEAL_V1',
        computation_key=plan['computation_key'],label=spec['label'],
        checkpoint_sha256=spec['expected_state_npy_sha256'],input_spec_sha256=object_sha(spec),
        result_sha256=file_sha(root/'RESULT.json')))
    return read_window(root,plan,spec)


def _replay(out: Path, plan: dict) -> dict:
    if not (out/'COMPLETED.json').is_file():
        raise FileExistsError('existing attempt: no retry/overwrite; use fresh output and explicit sealed reuse')
    seal = read_json(out/'COMPLETED.json')
    if seal.get('contract_sha256') != object_sha(plan):
        raise ValueError('completed attempt belongs to a different contract')
    summary = read_json(out/'SUMMARY.json',seal['summary_sha256'])
    for spec in plan['windows']:
        pointer = summary['windows'][spec['label']]
        read_window(pointer['directory'],plan,spec,pointer['manifest_sha256'])
    return summary


def execute(plan: dict, output: Path | str, backend_factory: Callable) -> dict:
    """Run already-frozen intent; the public CLI also verifies source/config lock.

    A test backend may exercise orchestration, but only explicit local CuPy
    execution can supply GPU evidence. No CPU fallback is implemented here.
    """
    if (plan.get('schema') != 'BASS_CR_R3M24_SAFE_RESTART_V1' or
            plan.get('scope') != 'REFERENCE_FOR_STRANG' or
            plan.get('production_admission') is not False):
        raise ValueError('unsupported/scientifically elevated execution scope')
    labels=[s['label'] for s in plan['windows']]
    if not labels or len(labels)!=len(set(labels)) or any(not x.replace('_','').isalnum() for x in labels):
        raise ValueError('unique safe window labels required')
    if not set(plan['reuse']) <= set(labels):
        raise ValueError('reuse of an unselected window')
    check_sources(plan)
    out = safe_path(output)
    if os.path.lexists(out):
        return _replay(out,plan)  # Before hashing states or constructing backend.
    out.mkdir(exist_ok=False); fsync_dir(out.parent)  # Exclusive run reservation.
    publish_json(out/'RUN.json',dict(contract_sha256=object_sha(plan),
                                  schema='BASS_CR_R3M24_RUN_RESERVATION_V1'))
    (out/'windows').mkdir(); fsync_dir(out)
    completed={}; backend=None; cleanup_attempted=False; stage='INTAKE'; start=time.monotonic()
    try:
        for spec in plan['windows']:
            if spec['label'] in plan['reuse']:
                p=plan['reuse'][spec['label']]
                saved=read_window(p['directory'],plan,spec,p['manifest_sha256'])
                if saved['result']['status']!='STRANG_SCALE_REFERENCE_CONSISTENT':
                    raise ValueError('unresolved window cannot satisfy required work')
                completed[spec['label']]=saved
        remaining=[s for s in plan['windows'] if s['label'] not in completed]
        with ExitStack() as stack:
            if remaining:
                unique={s['generation_directory']:s for s in [plan['probe'],*remaining]}
                bound={path:stack.enter_context(bind_generation(s)) for path,s in unique.items()}
                for value in bound.values(): value.assert_current()
                publish_json(out/'INTAKE.json',dict(inputs=[v.receipt for v in bound.values()],
                                                   contract_sha256=object_sha(plan)))
                check_sources(plan)
                stage='BACKEND_INIT'
                backend=backend_factory(plan)
                stage='PREFLIGHT'
                preflight=backend.probe(bound[plan['probe']['generation_directory']])
                publish_json(out/'PREFLIGHT.json',preflight)
                if preflight.get('status')!='PASS':
                    raise RuntimeError('resource preflight unresolved')
                for spec in remaining:
                    stage='WINDOW_'+spec['label']
                    state=bound[spec['generation_directory']]
                    state.assert_current()
                    result=backend.window(spec,state)
                    saved=_save_window(out,plan,spec,result)
                    completed[spec['label']]=saved
                    if result['status']!='STRANG_SCALE_REFERENCE_CONSISTENT':
                        raise RuntimeError('scientific local-reference gate unresolved')
            if backend is not None:
                stage='BACKEND_CLEANUP'; cleanup_attempted=True
                backend.close()
            stage='CLOSEOUT'
            work=(backend.snapshot() if backend is not None else
                  dict(kinetic_matvecs=0,fft_transforms=0,wall_seconds=0.,backend='NO_BACKEND'))
            summary=dict(schema='BASS_CR_R3M24_ATTEMPT_RESULT_V1',
                         status='LOCAL_REFERENCE_COMPLETE', production_admission=False,
                         GLOBAL_TIME_ERROR='NOT_EVALUATED',work=work,
                         windows=completed,reused_labels=list(plan['reuse']),
                         attempt_wall_seconds=time.monotonic()-start,
                         inherited_work_counted_in_new_job=False,
                         full_collision=False,preparation_run=False,projection='NOT_RUN')
            publish_json(out/'SUMMARY.json',summary)
            publish_json(out/'COMPLETED.json',dict(contract_sha256=object_sha(plan),
                                                 summary_sha256=file_sha(out/'SUMMARY.json')))
            return summary
    except BaseException as exc:
        cleanup_error=None
        if backend is not None and not cleanup_attempted:
            cleanup_attempted=True
            try:
                backend.close()
            except Exception as secondary:
                cleanup_error=repr(secondary)
                exc.add_note(f'cleanup also failed: {secondary!r}')
        work=(backend.snapshot() if backend is not None else
              dict(kinetic_matvecs=0,fft_transforms=0,wall_seconds=0.,backend='NOT_CONSTRUCTED'))
        try:
            publish_json(out/'FIRST_FAILURE.json',dict(stage=stage,type=type(exc).__name__,
                message=str(exc),completed_windows=completed,work=work,
                cleanup_error=cleanup_error,automatic_retry=False,production_admission=False))
        except Exception as evidence_error:
            exc.add_note(f'failure publication also failed: {evidence_error!r}; keep all existing evidence')
        raise
