#!/usr/bin/env python3
"""F1 admission entrypoint. Native work requires an external, exact-commit authorization."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[4]
SIDE = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.archive_evidence import open_evidence
from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.cloud_engine import build_engine, verify_engine_identity, verify_source_pins
from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.engine_admission import EngineAdmissionError, make_evaluator, run_admission


class ExecutionNotAuthorized(ValueError):
    def __init__(self, reason):
        super().__init__('F1_EXECUTION_NOT_AUTHORIZED: ' + reason)
        self.status = 'F1_EXECUTION_NOT_AUTHORIZED'


def check_authorization(path, implementation_commit, implementation_tree):
    if path is None or not Path(path).is_file():
        raise ExecutionNotAuthorized('external authorization file missing')
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ExecutionNotAuthorized('invalid authorization JSON') from exc
    if (data.get('schema') != 'BASS_NCLOUD_F1_RUN_AUTHORIZATION_V1'
            or data.get('implementation_commit') != implementation_commit
            or data.get('implementation_tree') != implementation_tree
            or data.get('native_admission_allowed') is not True):
        raise ExecutionNotAuthorized('implementation identity or native permission mismatch')
    wall = data.get('max_wall_seconds')
    if type(wall) is not int or wall <= 0:
        raise ExecutionNotAuthorized('positive integer wall budget required')
    cost = data.get('spending_limit_krw')
    prepaid = data.get('prepaid_host_approved') is True
    if cost is None and not prepaid:
        raise ExecutionNotAuthorized('cost budget or approved prepaid host required')
    if cost is not None and (type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0):
        raise ExecutionNotAuthorized('nonnegative finite cost budget required')
    return data


def verify_f0_durable(repo_root):
    root = Path(repo_root)
    base = root / 'research/foundation_rebuild/ncloud_c64g3_20260928'
    closure = json.loads((base / 'F0_DURABLE_CLOSURE.json').read_text())
    evidence_root = base / 'f0_evidence/20260928T045058Z'
    manifest_path = evidence_root / 'EVIDENCE_MANIFEST.json'
    manifest = json.loads(manifest_path.read_text())
    report = json.loads((evidence_root / 'RETURN_REPORT.json').read_text())
    handoff = json.loads((evidence_root / 'F0_RETURN_HANDOFF.json').read_text())
    if closure['status'] != 'F0_DURABLE_CLOSED':
        raise ValueError('F0 durable closure is not closed')
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != closure['execution_evidence']['evidence_manifest_sha256']:
        raise ValueError('F0 durable manifest hash mismatch')
    for item in manifest['files']:
        path = root / item['published_path']
        data = path.read_bytes()
        if len(data) != item['published']['bytes'] or hashlib.sha256(data).hexdigest() != item['published']['sha256']:
            raise ValueError('F0 published evidence identity mismatch: ' + item['name'])
    if not (closure['scientific_status'] == manifest['scientific_status'] == report['status']
            == 'TP2E_CACHE_ONLY_M4_COMPARISON_PASS'):
        raise ValueError('F0 scientific status mismatch')
    if not (closure['handoff_status'] == manifest['handoff_status'] == handoff['status'] == 'STOP_F0_COMPLETE'):
        raise ValueError('F0 handoff status mismatch')
    counts = [closure['scientific_evidence']['fresh_tests'], manifest['fresh_tests'],
              report['new_tests'], handoff['new_tests']]
    if (any(x.get('tests', x.get('count')) != 32 or any(x.get(k) != 0 for k in ('failures', 'errors', 'skipped'))
            for x in counts) or report['new_tests']['returncode'] != 0):
        raise ValueError('F0 fresh tests mismatch')
    replay = report['comparison']['historical_replay']
    if (replay['stored_vs_replayed_metric_distance'] > 1e-10
            or closure['scientific_evidence']['historical_n384_replay_metric_distance'] > 1e-10
            or report['comparison']['selected_nstep'] != handoff['selected_m4_nstep']):
        raise ValueError('F0 N384 replay or M4 selection mismatch')
    if (report['comparison']['selected_nstep'] != 96
            or report['comparison']['new_operator_evaluations'] != 0
            or handoff['new_spatial_operator_evaluations'] != 0
            or report['comparison']['reference_reintegrated'] is not False):
        raise ValueError('F0 cache-only assertion mismatch')
    if (closure['historical_tp2d_status'] != report['original_tp2d_status']
            or report['original_tp2d_status'] != 'TEMPORAL_REFINEMENT_UNRESOLVED'
            or closure['claim_ceiling'] != manifest['claim_ceiling']
            or closure['claim_ceiling'] != handoff['claim_ceiling']):
        raise ValueError('F0 historical status or claim ceiling mismatch')
    return closure


def _identity():
    head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
    tree = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD^{tree}'], text=True).strip()
    return head, tree


def _write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def verify_source_manifest(repo_root, sidecar):
    manifest = json.loads((Path(sidecar) / 'SOURCE_MANIFEST.json').read_text())
    for relative, pin in manifest['files'].items():
        payload = (Path(repo_root) / relative).read_bytes()
        if len(payload) != pin['bytes'] or hashlib.sha256(payload).hexdigest() != pin['sha256']:
            raise ValueError('source manifest mismatch: ' + relative)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--authorization', help='external RUN_AUTHORIZATION.json; never generated by this runner')
    parser.add_argument('--out', required=True, help='create-only F1 output directory')
    parser.add_argument('--archive', help='exact historical TP2D RETURN ZIP; defaults to repository artifact')
    args = parser.parse_args(argv)
    out = Path(args.out)
    if out.exists():
        print('F1_INPUT_IDENTITY_BLOCKED: output collision', file=sys.stderr)
        return 3
    try:
        head, tree = _identity()
        approved = check_authorization(args.authorization, head, tree)
    except (ExecutionNotAuthorized, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 3
    return execute_authorized(args, out, head, tree, approved)


def execute_authorized(args, out, head, tree, approved):
    """Later authorized execution; this implementation session only tests pre-science failures."""
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    ceiling = json.loads((SIDE / 'F1_CONTRACT.json').read_text())['claim_ceiling']
    report = {'schema': 'BASS_NCLOUD_F1_RUN_RETURN_V1', 'status': 'F1_INPUT_IDENTITY_BLOCKED',
              'implementation_commit': head, 'implementation_tree': tree,
              'scientific_execution_performed': False, 'first_failure': None,
              'claim_ceiling': ceiling}
    progress = out / 'PROGRESS.jsonl'
    def event(phase, **detail):
        with progress.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'phase': phase, 'elapsed_seconds': time.monotonic() - started,
                                     **detail}, allow_nan=False) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
    def remaining():
        value = approved['max_wall_seconds'] - (time.monotonic() - started)
        if value <= 0:
            raise TimeoutError('authorized wall budget exhausted')
        return value
    try:
        # Every identity gate precedes tests, compiler invocation, and evaluation.
        contract = json.loads((SIDE / 'F1_CONTRACT.json').read_text())
        representatives = json.loads((SIDE / 'F1_REPRESENTATIVE_QUERIES.json').read_text())
        pins = json.loads((SIDE / 'SOURCE_PINS.json').read_text())
        verify_source_manifest(REPO, SIDE)
        verify_f0_durable(REPO)
        verify_source_pins(REPO, pins)
        if representatives['source_archive_sha256'] != contract['historical_tp2d_archive']['sha256']:
            raise ValueError('representative/archive identity mismatch')
        archive = Path(args.archive) if args.archive else REPO / contract['historical_tp2d_archive']['path']
        evidence = open_evidence(archive, contract, representatives)
        report['historical_tp2d_status'] = 'TEMPORAL_REFINEMENT_UNRESOLVED'
        event('input_identity_verified', archive_sha256=contract['historical_tp2d_archive']['sha256'])
        remaining()
        report['status'] = 'F1_TESTS_FAILED'
        tests = subprocess.run([sys.executable, '-m', 'pytest', '-q',
                                str(SIDE / 'runtime/tests')], cwd=REPO,
                               capture_output=True, text=True, timeout=remaining(), check=False)
        (out / 'FOCUSED_TESTS.log').write_text(tests.stdout + tests.stderr)
        if tests.returncode:
            raise RuntimeError('fresh F1 focused tests failed')
        event('focused_tests_passed')
        remaining()
        report['status'] = 'F1_BUILD_FAILED'
        source = REPO / contract['build_policy']['source_path']
        engine = out / 'engine'
        build = build_engine(source, engine, contract, timeout_seconds=remaining())
        identity = verify_engine_identity(engine)
        for name in ('ENGINE_IDENTITY.json', 'ENGINE_BUILD.json'):
            shutil.copyfile(engine / name, out / name)
        report['engine_identity_sha256'] = identity['identity_sha256']
        event('engine_build_verified', library_sha256=build['library_sha256'])
        remaining()
        report['status'] = 'F1_ENGINE_LOAD_FAILED'
        basis = evidence.materialize_basis(out / 'basis')
        tp2d_contract = json.loads((REPO / 'research/foundation_rebuild/tp2d_runtime_self_qualified_transport_20260927/CONTRACT.json').read_text())
        evaluator, speed = make_evaluator(REPO, engine, basis, tp2d_contract)
        event('engine_loaded')
        remaining()
        report['status'] = 'F1_INTERRUPTED'
        report['scientific_execution_performed'] = True
        parity, metric = run_admission(evidence, evaluator, speed, contract,
                                       identity['identity_sha256'], check_budget=remaining)
        _write_new(out / 'REPRESENTATIVE_PARITY.json', {'schema': 'BASS_NCLOUD_F1_REPRESENTATIVE_PARITY_V1',
                   'engine_identity_sha256': identity['identity_sha256'], 'queries': parity})
        _write_new(out / 'METRIC_CONNECTION_PARITY.json', {'schema': 'BASS_NCLOUD_F1_METRIC_CONNECTION_PARITY_V1',
                   'engine_identity_sha256': identity['identity_sha256'], 'sentinels': metric})
        _write_new(out / 'ENGINE_ADMISSION.json', {'schema': 'BASS_NCLOUD_F1_ENGINE_ADMISSION_V1',
                   'status': contract['success_status'], 'representative_queries': len(parity),
                   'metric_sentinels': len(metric), 'engine_identity_sha256': identity['identity_sha256'],
                   'claim_ceiling': ceiling})
        report['status'] = contract['success_status']
        event('admission_completed')
        return 0
    except EngineAdmissionError as exc:
        report['status'] = exc.status
        report['first_failure'] = str(exc)
    except TimeoutError as exc:
        report['status'] = 'F1_INTERRUPTED'
        report['first_failure'] = str(exc)
    except subprocess.TimeoutExpired as exc:
        report['status'] = 'F1_INTERRUPTED'
        report['first_failure'] = str(exc)
    except (ValueError, FileNotFoundError, KeyError, OSError) as exc:
        report['first_failure'] = str(exc)
    except Exception as exc:
        report['first_failure'] = type(exc).__name__ + ': ' + str(exc)
    finally:
        report['elapsed_seconds'] = time.monotonic() - started
        _write_new(out / 'RETURN_REPORT.json', report)
    event('stopped', status=report['status'])
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
