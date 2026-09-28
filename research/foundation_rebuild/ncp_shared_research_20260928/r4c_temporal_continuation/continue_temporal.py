#!/usr/bin/env python3
"""Continue one frozen TP2D temporal-refinement rung without replaying old rungs.

This runner is deliberately narrow.  It accepts an exact prior TP2D return
archive, validates its numerical context and qualified query store, restores
that store into a fresh output, and evaluates exactly one larger candidate
step count.  It does not rerun the DOP853 reference, metric sentinels, earlier
candidate rungs, capture observables, all-bound extraction, or b integration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FND = HERE.parents[1]
REPO = HERE.parents[3]
ANALYTIC = FND / 'tp2a_analytic_pruning_20260926' / 'code'
PERF = FND / 'tp2a_perf_20260926'
TP1 = FND / 'tp1_short_transport_20260926'
FND_SRC = FND / 'src'
FULL = FND / 'full_operator_20260926'
REPAIR = FND / 'reaudit_20260925' / 'repair'
TP2D = FND / 'tp2d_runtime_self_qualified_transport_20260927'
for p in (HERE, TP2D, ANALYTIC, PERF, TP1, FND_SRC, FULL, REPAIR, REPO):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

CLAIM_CEILING = {
    'capture_execution_allowed': False,
    'production_admission': 'HOLD',
    'all_bound': 'OPEN',
    'b_grid': 'NO_GO',
    'original_capture_gap_resolved': False,
    'continuous_global_supremum_bound': False,
    'continuous_trajectory_error_bound': False,
}
ALLOWED_SOURCE_STATUSES = {
    'TEMPORAL_REFINEMENT_UNRESOLVED',
    'TP2D_TEMPORAL_CONTINUATION_UNRESOLVED',
}


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def write_new(path: Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def copy_new(src: Path, dst: Path) -> None:
    src = Path(src); dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open('xb') as f:
        f.write(src.read_bytes())
        f.flush(); os.fsync(f.fileno())


def git_identity():
    try:
        head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
        tree = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD^{tree}'], text=True, stderr=subprocess.DEVNULL).strip()
        return head, tree
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None


def verify_pinned_dependencies() -> dict:
    manifest = json.loads((HERE / 'PINNED_DEPENDENCIES.json').read_text())
    actual = {}
    for rel, expected in manifest['files'].items():
        p = REPO / rel
        if not p.is_file():
            raise ValueError('pinned dependency missing: ' + rel)
        got = sha256_path(p)
        actual[rel] = got
        if got != expected:
            raise ValueError('pinned dependency hash mismatch: ' + rel)
    return {'manifest': manifest, 'actual': actual}


def validate_query_store(source: Path, context_id: str) -> dict:
    qdir = source / 'runtime_queries'
    if not qdir.is_dir():
        raise ValueError('resume archive lacks runtime_queries')
    rows = sorted(qdir.glob('*.json'))
    if not rows:
        raise ValueError('empty resume query store')
    maxdiff = 0.0
    for jp in rows:
        qid = jp.stem
        npz = qdir / (qid + '.npz')
        if not npz.is_file():
            raise ValueError('resume query payload missing: ' + qid)
        rec = json.loads(jp.read_text())
        if rec.get('schema') != 'BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1':
            raise ValueError('bad resume query schema: ' + qid)
        if rec.get('query_id') != qid or rec.get('context_id') != context_id:
            raise ValueError('resume query identity mismatch: ' + qid)
        if rec.get('qualification', {}).get('status') != 'RUNTIME_QUERY_QUALIFIED':
            raise ValueError('unqualified stored runtime query: ' + qid)
        if sha256_path(npz) != rec.get('payload_sha256'):
            raise ValueError('resume query payload hash mismatch: ' + qid)
        maxdiff = max(maxdiff, float(rec['qualification']['max_raw_cross_relative_difference']))
    npz_count = len(list(qdir.glob('*.npz')))
    if npz_count != len(rows):
        raise ValueError('resume query json/npz count mismatch')
    return {'qualified_query_count': len(rows), 'npz_count': npz_count, 'max_raw_cross_relative_difference': maxdiff}


def load_candidate(source: Path, nstep: int):
    from metric_transport import CandidateResult
    jp = source / f'CANDIDATE_N{nstep}.json'
    npz = source / f'CANDIDATE_N{nstep}.npz'
    if not jp.is_file() or not npz.is_file():
        raise ValueError(f'resume archive lacks CANDIDATE_N{nstep}')
    rec = json.loads(jp.read_text())
    if int(rec.get('nstep', -1)) != int(nstep):
        raise ValueError('previous candidate nstep mismatch')
    with np.load(npz, allow_pickle=False) as f:
        return CandidateResult(
            True,
            int(nstep),
            float(rec['dt']),
            np.array(f['initial_state']),
            np.array(f['final_state']),
            np.array(f['norm_history']),
            float(rec['max_norm_drift']),
            float(rec['max_generator_defect']),
        )


def validate_source(source: Path, previous_nstep: int, next_nstep: int) -> dict:
    required = ['RETURN_REPORT.json', 'SCIENCE_CONTEXT.json', 'BASIS.json', 'BASIS.npz',
                'REFERENCE_STATES.npz', 'REFERENCE_RECEIPT.json', 'METRIC_CONNECTION.json',
                f'CANDIDATE_N{previous_nstep}.json', f'CANDIDATE_N{previous_nstep}.npz']
    for rel in required:
        if not (source / rel).is_file():
            raise ValueError('resume archive missing required file: ' + rel)
    report = json.loads((source / 'RETURN_REPORT.json').read_text())
    if report.get('status') not in ALLOWED_SOURCE_STATUSES:
        raise ValueError('resume status is not an unresolved temporal-continuation source')
    for key, value in CLAIM_CEILING.items():
        if report.get(key) != value:
            raise ValueError('resume claim ceiling mismatch: ' + key)
    sc = json.loads((source / 'SCIENCE_CONTEXT.json').read_text())
    context = sc.get('context'); context_id = sc.get('context_id')
    if not isinstance(context, dict) or digest(context) != context_id:
        raise ValueError('SCIENCE_CONTEXT identity mismatch')
    contract = context['contract']
    if contract.get('candidate_step_counts') != [24, 48, 96, 192, 384]:
        raise ValueError('unexpected frozen historical candidate ladder')
    if next_nstep <= previous_nstep or next_nstep != 2 * previous_nstep:
        raise ValueError('continuation must be exactly one doubling rung')
    budget = int(contract['max_unique_runtime_queries'])
    # run_candidate accesses t0, one midpoint per step, and tf.  Even with no
    # restored hits, one isolated continuation rung therefore needs <= N+2.
    per_run_upper_bound = int(next_nstep) + 2
    if per_run_upper_bound > budget:
        raise ValueError('single-rung continuation exceeds frozen per-run query budget')
    screens = contract['screens']
    metric_rows = json.loads((source / 'METRIC_CONNECTION.json').read_text())
    if len(metric_rows) != len(contract['metric_sentinel_z_a0']) or any(float(x['relative_residual']) > float(screens['metric_derivative_relative_max']) for x in metric_rows):
        raise ValueError('inherited metric sentinel evidence does not pass frozen screen')
    rr = json.loads((source / 'REFERENCE_RECEIPT.json').read_text())
    if rr.get('method') != contract['reference_solver']['method'] or float(rr['rtol']) != float(contract['reference_solver']['rtol']) or float(rr['atol']) != float(contract['reference_solver']['atol']):
        raise ValueError('inherited reference solver identity mismatch')
    if float(rr['max_norm_drift']) > float(screens['reference_norm_drift_max']):
        raise ValueError('inherited reference norm drift fails frozen screen')
    prev = load_candidate(source, previous_nstep)
    store = validate_query_store(source, context_id)
    return {
        'report_status': report['status'],
        'context_id': context_id,
        'context': context,
        'contract': contract,
        'previous_candidate': prev,
        'query_store': store,
        'per_run_query_upper_bound': per_run_upper_bound,
        'frozen_query_budget': budget,
    }


def extract_validated_archive(archive: Path, expected_sha256: str, destination: Path) -> dict:
    archive = Path(archive).resolve()
    if not archive.is_file():
        raise ValueError('resume archive not found')
    got = sha256_path(archive)
    if got != expected_sha256:
        raise ValueError('resume archive sha256 mismatch')
    with zipfile.ZipFile(archive) as zf:
        bad = zf.testzip()
        if bad is not None:
            raise ValueError('resume archive CRC failure: ' + bad)
        zf.extractall(destination)
    return {'path': str(archive), 'bytes': archive.stat().st_size, 'sha256': got, 'crc': 'PASS'}


def execute_science(source: Path, out: Path, source_info: dict, analytic_build: Path, next_nstep: int) -> dict:
    from bass_foundations.two_center import Trajectory, symmetric_channels
    from cr_repro.observables import projectile_speed_au
    from exact_cross import MomentKernel
    from assemble import assemble
    from runtime import load_bank
    from metric_transport import run_candidate, phase_aligned_metric_distance
    from qualified_provider import ResolutionQualifiedProvider, restore_query_store
    from analytic_adapter import AnalyticEvaluator
    from transport_policy import assess_temporal_pair

    contract = source_info['contract']; context_id = source_info['context_id']
    bank, basis_record = load_bank(source)
    expected_basis = source_info['context']['physics_identity']['basis_identity']
    if basis_record['identity'] != expected_basis:
        raise ValueError('basis identity mismatch')
    channels = symmetric_channels(bank)
    v = projectile_speed_au(contract['energy_keV_per_u'])
    trajectory = Trajectory(((0.,0.,0.),(contract['b_a0'],0.,0.)),((0.,0.,0.),(0.,0.,v)))

    kernel = MomentKernel(str(Path(analytic_build).resolve()))
    analytic = kernel.receipt
    if analytic.get('source_sha256') != contract['analytic_source_sha256']:
        raise ValueError('analytic source sha256 mismatch')
    if analytic.get('library_sha256') != contract['analytic_library_sha256']:
        raise ValueError('analytic library sha256 mismatch')

    restored = restore_query_store(source, out, context_id)
    if restored != source_info['query_store']['qualified_query_count']:
        raise ValueError('restored query count mismatch')
    for rel in ('BASIS.json','BASIS.npz','SCIENCE_CONTEXT.json','REFERENCE_STATES.npz','REFERENCE_RECEIPT.json','METRIC_CONNECTION.json'):
        copy_new(source/rel, out/rel)
    prev_n = int(source_info['previous_candidate'].nstep)
    for rel in (f'CANDIDATE_N{prev_n}.json', f'CANDIDATE_N{prev_n}.npz'):
        copy_new(source/rel, out/rel)

    evaluator = AnalyticEvaluator(assemble, trajectory=trajectory, channels=channels, kernel=kernel)
    provider = ResolutionQualifiedProvider(
        evaluate=evaluator,
        resolutions=contract['runtime_reference_resolutions'],
        screens=contract['screens'],
        context_id=context_id,
        out_dir=out,
        max_unique_queries=contract['max_unique_runtime_queries'],
    )
    refs = np.load(source/'REFERENCE_STATES.npz', allow_pickle=False)
    reference_final = np.array(refs['final_state'])
    previous = source_info['previous_candidate']
    t0 = contract['z_initial_a0']/v; tf = contract['z_final_a0']/v
    current = run_candidate(provider, previous.initial_state, t0, tf, int(next_nstep))
    np.savez_compressed(out/f'CANDIDATE_N{next_nstep}.npz', initial_state=current.initial_state,
                        final_state=current.final_state, norm_history=current.norm_history)
    crec = {
        'nstep': int(next_nstep), 'dt': float(current.dt),
        'max_norm_drift': float(current.max_norm_drift),
        'max_generator_defect': float(current.max_generator_defect),
        'unique_runtime_queries_this_run': int(provider.unique_query_count),
        'restored_query_reads_this_run': int(provider.restored_query_reads),
        'new_raw_operator_evaluations_this_run': int(provider.raw_operator_evaluation_count),
    }
    write_new(out/f'CANDIDATE_N{next_nstep}.json', crec)
    Sf = provider.at(tf).S
    pair = assess_temporal_pair(previous, current, reference_final, Sf, phase_aligned_metric_distance, contract['screens'])
    write_new(out/f'TEMPORAL_PAIR_N{prev_n}_N{next_nstep}.json', pair)
    audit = provider.audit_summary(); write_new(out/'PROVIDER_AUDIT.json', audit)
    return {
        'previous_nstep': prev_n,
        'selected_nstep': int(next_nstep),
        'candidate': crec,
        'pair': pair,
        'provider_audit': audit,
        'source_store_qualified_queries': source_info['query_store']['qualified_query_count'],
        'restored_store_files': restored,
        'all_restored_source_queries_individually_qualified': True,
        'all_queries_accessed_this_run_qualified': bool(audit['all_runtime_operator_queries_qualified']),
    }


def finish(out: Path, report: dict) -> Path:
    write_new(out/'RETURN_REPORT.json', report)
    manifest = {}
    for p in sorted(out.rglob('*')):
        if p.is_file():
            manifest[str(p.relative_to(out))] = {'bytes': p.stat().st_size, 'sha256': sha256_path(p)}
    write_new(out/'MANIFEST.json', manifest)
    archive = out.with_name(out.name + '_RETURN.zip')
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.rglob('*')):
            if p.is_file():
                zf.write(p, str(p.relative_to(out)))
    return archive


def build_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', required=True)
    p.add_argument('--resume-archive', required=True)
    p.add_argument('--expected-resume-archive-sha256', required=True)
    p.add_argument('--previous-nstep', required=True, type=int)
    p.add_argument('--next-nstep', required=True, type=int)
    p.add_argument('--analytic-build')
    p.add_argument('--expected-commit')
    p.add_argument('--preflight-only', action='store_true')
    return p


def run_cli(argv=None) -> int:
    args = build_parser().parse_args(argv)
    out = Path(args.out).resolve(); archive = out.with_name(out.name + '_RETURN.zip')
    if out.exists() or archive.exists():
        print('OUTPUT_EXISTS: fresh output path required', file=sys.stderr); return 3
    if not args.preflight_only and not args.analytic_build:
        print('ANALYTIC_BUILD_REQUIRED for science execution', file=sys.stderr); return 3
    out.mkdir(parents=True)
    t0 = time.monotonic()
    head, tree = git_identity()
    report = {
        'schema':'BASS_R4C_TEMPORAL_CONTINUATION_RETURN_V1',
        'status':'IN_PROGRESS',
        'execution_head':head,'execution_tree':tree,
        'previous_nstep':args.previous_nstep,'next_nstep':args.next_nstep,
        **CLAIM_CEILING,
        'capture_run_performed':False,'b_grid_run_performed':False,
        'full_window_transport_qualified':False,
    }
    code = 0
    try:
        if args.expected_commit and head != args.expected_commit:
            raise ValueError('execution commit identity mismatch')
        deps = verify_pinned_dependencies()
        with tempfile.TemporaryDirectory(prefix='bass_r4c_resume_') as td:
            source = Path(td)
            ar = extract_validated_archive(Path(args.resume_archive), args.expected_resume_archive_sha256, source)
            info = validate_source(source, args.previous_nstep, args.next_nstep)
            preflight = {
                'resume_archive': ar,
                'source_status': info['report_status'],
                'context_id': info['context_id'],
                'qualified_query_store_count': info['query_store']['qualified_query_count'],
                'query_store_max_raw_cross_relative_difference': info['query_store']['max_raw_cross_relative_difference'],
                'single_rung_query_upper_bound': info['per_run_query_upper_bound'],
                'frozen_query_budget': info['frozen_query_budget'],
                'pinned_dependencies': deps,
                'old_reference_reexecuted': False,
                'old_candidate_rungs_reexecuted': False,
            }
            write_new(out/'PREFLIGHT.json', preflight)
            if args.preflight_only:
                report['status'] = 'R4C_PREFLIGHT_PASS'
            else:
                science = execute_science(source, out, info, Path(args.analytic_build), args.next_nstep)
                report['temporal_continuation'] = science
                if science['pair']['qualified']:
                    report['status'] = 'TP2D_TEMPORAL_CONTINUATION_PASS'
                    report['full_window_transport_qualified'] = True
                else:
                    report['status'] = 'TP2D_TEMPORAL_CONTINUATION_UNRESOLVED'
    except BaseException as e:
        code = 2
        report['status'] = 'R4C_BLOCKED'
        report['first_failure'] = {'type': type(e).__name__, 'message': str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    report['wall_seconds'] = time.monotonic() - t0
    final_archive = finish(out, report)
    print(json.dumps({'status':report['status'],'report':str(out/'RETURN_REPORT.json'),
                      'archive':str(final_archive),'capture_execution_allowed':False}, indent=2))
    return code


def main():
    return run_cli()

if __name__ == '__main__':
    raise SystemExit(main())
