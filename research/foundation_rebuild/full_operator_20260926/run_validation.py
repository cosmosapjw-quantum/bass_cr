#!/usr/bin/env python3
"""New full-operator tests + own-sphere assembly using an existing order-24 cross.

No capture, GPU, original cross-ladder rerun, install, retry, or Git mutation.
Outputs are fresh/create-only and include a return ZIP, also on ordinary failure.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import xml.etree.ElementTree as ET
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
if os.getenv('BASS_UPSTREAM_ROOT'):
    U = Path(os.environ['BASS_UPSTREAM_ROOT']).resolve()
    REPO = U/'source'
    REPAIR = U/'repair'
else:
    REPO = HERE.parents[2]
    REPAIR = HERE.parent/'reaudit_20260925/repair'
FND_SRC = REPO/'research/foundation_rebuild/src'
sys.path[:0] = [str(HERE), str(REPAIR), str(FND_SRC), str(REPO)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def verify_sources():
    expected = json.loads((HERE/'SOURCE_MANIFEST.json').read_text())
    for rel, digest in expected['files'].items():
        if sha(HERE/rel) != digest:
            raise ValueError('new package source mismatch: '+rel)
    pins = json.loads((HERE/'DEPENDENCY_PINS.json').read_text())
    actual = {}
    for row in pins['files']:
        path = (REPO/row['path']) if row['root'] == 'repo' else (REPAIR/row['path'])
        actual[str(path)] = sha(path)
        if actual[str(path)] != row['sha256']:
            raise ValueError('unchanged dependency mismatch: '+str(path))
    return actual


def finish(out, report):
    write_new(out/'RETURN_REPORT.json', report)
    files = sorted(p for p in out.rglob('*') if p.is_file())
    manifest = {str(p.relative_to(out)): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in files}
    write_new(out/'MANIFEST.json', manifest)
    archive = out.with_name(out.name+'_RETURN.zip')
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(p for p in out.rglob('*') if p.is_file()):
            z.write(p, str(p.relative_to(out)))
    print(json.dumps({'status': report['status'], 'report': str(out/'RETURN_REPORT.json'),
                      'archive': str(archive), 'capture_execution_allowed': False}), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cross-dir', required=True, help='existing successful run_cross_probe order24 output directory')
    ap.add_argument('--out', required=True)
    ap.add_argument('--expected-commit', help='when supplied, refuse another repository HEAD')
    args = ap.parse_args()
    out = Path(args.out).resolve()
    if out.exists() or out.with_name(out.name+'_RETURN.zip').exists():
        print('OUTPUT_EXISTS: choose a fresh output path; nothing overwritten', file=sys.stderr)
        return 3
    out.mkdir(parents=True)
    report = {'schema': 'BASS_FND_FULL_OPERATOR_RETURN_V1', 'status': 'IN_PROGRESS',
              'scope': 'NEW_TESTS_AND_FULL_STATIC_18_CHANNEL_Z_MINUS12',
              'production_admission': 'HOLD', 'all_bound': 'OPEN', 'b_grid': 'NO_GO',
              'capture_execution_allowed': False, 'capture_run_performed': False,
              'original_cross_ladder_rerun': False, 'gpu_run': False,
              'historical_test_suite_rerun': False, 'steps': []}
    phase = 'preflight'
    code = 0
    try:
        sources = verify_sources()
        try:
            head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
            tree = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD^{tree}'], text=True, stderr=subprocess.DEVNULL).strip()
        except subprocess.CalledProcessError:
            head = tree = None
        if args.expected_commit and head != args.expected_commit:
            raise ValueError('execution commit identity mismatch')
        if os.getenv('BASS_UPSTREAM_ROOT') and args.expected_commit:
            raise ValueError('explicit recovery layout cannot claim repository-mode execution')
        import numpy as np
        import scipy
        from bass_foundations.radial_basis import RadialSpec, atomic_bank
        from bass_foundations.two_center import Trajectory, symmetric_channels
        from cr_repro.observables import projectile_speed_au
        from full_operator import load_cross_archive, assemble_full
        contract = json.loads((HERE/'CONTRACT.json').read_text())
        source = Path(args.cross_dir).resolve()
        saved = json.loads((source/'RESULT.json').read_text())
        if saved.get('spec') != contract['radial_spec'] or saved.get('order') != 24 or saved.get('angular') != 'bessel' or saved.get('z') != -12.:
            raise ValueError('cross input differs from the accepted order24 z=-12 scope')
        ch = symmetric_channels(atomic_bank(RadialSpec(**contract['radial_spec'])))
        v = projectile_speed_au(100.)
        tr = Trajectory(((0, 0, 0), (2., 0, 0)), ((0, 0, 0), (0, 0, v)))
        t = -12./v
        cross = load_cross_archive(source, tr, ch, t)
        report.update(execution_head=head, execution_tree=tree, source_layout=('recovered_reference' if os.getenv('BASS_UPSTREAM_ROOT') else 'repository'),
                      cross_directory=str(source), cross_identity=cross.signature,
                      environment={'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__,
                                   'threads': {k: os.getenv(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']}})
        write_new(out/'INTAKE.json', {'contract': contract, 'source_hashes': sources,
                  'cross_result_sha256': sha(source/'RESULT.json'), 'cross_matrix_sha256': sha(source/'matrices.npz'),
                  'cross_kernel_and_ordered_basis_identity': 'EXACT_MATCH', **report})
        phase = 'new_tests'
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',
                   OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        cmd = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', str(HERE/'tests'), '--junitxml='+str(out/'tests.xml')]
        with (out/'tests.stdout').open('x') as so, (out/'tests.stderr').open('x') as se:
            p = subprocess.run(cmd, stdout=so, stderr=se, env=env, timeout=180)
        suites = ET.parse(out/'tests.xml').getroot().iter('testsuite')
        counts = dict.fromkeys(['tests','failures','errors','skipped'], 0)
        for suite in suites:
            for key in counts:
                counts[key] += int(suite.attrib.get(key, 0))
        report['steps'].append({'name': phase, 'command': cmd, 'returncode': p.returncode, 'counts': counts})
        write_new(out/'TEST_RECEIPT.json', report['steps'][-1])
        print(json.dumps(report['steps'][-1]), flush=True)
        if p.returncode or counts['failures'] or counts['errors'] or counts['skipped']:
            raise RuntimeError('new tests did not all pass without skips')
        phase = 'full_static_assembly'
        results = []
        for order in contract['same_center_orders']:
            x = assemble_full(tr, ch, t, same_order=order, cross=cross)
            mats = {k: x[k] for k in ('S','H','D')}
            for label in ('T','P'):
                for k in ('S','H','D','H0','V_other','A'):
                    mats[label+'_'+k] = x['same_center'][label][k]
            name = 'full_same_order'+str(order)
            with (out/(name+'.npz')).open('xb') as f:
                np.savez_compressed(f, **mats)
            write_new(out/(name+'.json'), {'metadata': x['metadata'], 'diagnostics': x['diagnostics'],
                      'matrix_sha256': sha(out/(name+'.npz'))})
            results.append(x)
        a,b = results
        changes = {k: float(np.linalg.norm(a[k]-b[k])/max(np.linalg.norm(b[k]),1e-300)) for k in ('S','H','D')}
        diag = b['diagnostics']
        bound = contract['screens']
        failures = []
        if max(changes.values()) > bound['same_center_refinement_relative_max']:
            failures.append('same-center refinement')
        for label,d in diag['same_center'].items():
            if d['boost_cancellation_absolute'] > bound['same_center_boost_cancellation_absolute_max']:
                failures.append(label+' boost cancellation')
            if d['A_skew_absolute_max'] > bound['same_center_A_skew_absolute_max']:
                failures.append(label+' integration by parts')
        report['full_static'] = {'channel_count': len(ch), 'z_a0': -12., 'cross_reintegrated': False,
                'same_center_order12_to20': changes, 'diagnostics': diag,
                'norms': {k: float(np.linalg.norm(b[k])) for k in ('S','H','D')}, 'failed_screens': failures}
        write_new(out/'FULL_STATIC_RECEIPT.json', report['full_static'])
        if failures:
            raise ArithmeticError('full static screens failed: '+', '.join(failures))
        report['status'] = 'FULL_STATIC_OPERATOR_VALIDATION_PASS'
        report['next_scope'] = 'bounded time-dependent operator/transport design; no capture authorized by this report'
    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            report['status'] = 'INTERRUPTED';code = 130
        elif isinstance(e, (ImportError, ModuleNotFoundError)):
            report['status'] = 'ENVIRONMENT_BLOCKED';code = 3
        elif isinstance(e, (FileNotFoundError, ValueError)):
            report['status'] = 'IDENTITY_OR_INPUT_BLOCKED';code = 3
        elif isinstance(e, ArithmeticError):
            report['status'] = 'NUMERICAL_SCREEN_FAILED';code = 2
        else:
            report['status'] = 'EXECUTION_OR_TEST_FAILED';code = 3
        report['first_failure'] = {'phase': phase, 'type': type(e).__name__, 'message': str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    finish(out, report)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
