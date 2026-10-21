#!/usr/bin/env python3
"""Read-only, pinned PR94 return comparison; no solver imports or executions.

Writes a create-only JSON receipt. --git-repository is an isolated clone with
the PR94 commit and original execution commit available; it is never mutated.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess

import numpy as np

HEAD = '92b1b3f5575375580cf8de8039252ac492353b7e'
CONTENT = '5ecb8a6c4961302b7066b06278e72ecd2d77f8c9'
PHYSICS = '3b85dedce84d37b3e165da00685a8a984950aafe'
PREFIX = 'research/cr_c21n_mass_shell_cache_20261021/'
GRID_SHA = '2a74af40c5508fc332dd3671955ad2dda6fc3e8de51bc61dcc3730a6798913b5'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def canonical(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def differences(left, right, path=''):
    if isinstance(left, dict) and isinstance(right, dict):
        return sum((differences(left.get(k), right.get(k), path + '/' + k)
                    for k in sorted(left.keys() | right.keys())), [])
    return [] if left == right else [{'path': path, 'ncp': left, 'sandbox': right}]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--git-repository', type=Path, required=True)
    ap.add_argument('--pr94-original', type=Path, required=True)
    ap.add_argument('--sandbox-unit', type=Path, required=True)
    ap.add_argument('--pinned-export', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    ext, local = args.pr94_original, args.sandbox_unit
    raw, prior = ext / 'raw', local / 'raw_offgrid4'
    em, sm = read(raw / 'MANIFEST.json'), read(prior / 'MANIFEST.json')
    for m in (em, sm):
        assert canonical(m['manifest']) == m['identity']
    emc, smc = em['manifest'], sm['manifest']
    delta = differences(emc, smc)
    assert {x['path'] for x in delta} == {'/execution_site', '/software/python'}
    assert emc['grid'] == smc['grid'] and emc['source'] == smc['source']
    assert emc['code_sha256'] == smc['code_sha256']
    assert emc['source']['source_commit'] == PHYSICS
    assert emc['grid_file_sha256'] == smc['grid_file_sha256'] == GRID_SHA

    def git_bytes(ref, path):
        return subprocess.check_output(['git', '-C', str(args.git_repository),
                                        'show', f'{ref}:{path}'])

    source_binding_path = local / 'execution_checks/FROZEN_SOURCE_BINDING.json'
    source_binding = read(source_binding_path)
    source_rows = []
    for b in source_binding['bindings']:
        ncp_bytes, old_bytes = git_bytes(HEAD, b['path']), git_bytes(CONTENT, b['path'])
        actual_sha = sha(ncp_bytes)
        assert actual_sha == b['sha256'] and ncp_bytes == old_bytes
        source_rows.append({'path': b['path'], 'sha256': actual_sha,
                            'PR94_equals_frozen_execution_content': True})
    assert len(source_rows) == 17
    grid = git_bytes(HEAD, PREFIX + 'prepared_offgrid4/grid_offgrid4.json')
    assert sha(grid) == GRID_SHA
    assert json.loads(grid)['cases'] == emc['grid']['cases']

    export = read(args.pinned_export)
    exported_count = 0
    for row in export['exported_files']:
        rel = row['path'].split('offgrid4_return_20261021/', 1)[1]
        data = (ext / rel).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
        assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob_sha1']
        exported_count += 1

    sum_results = []
    for line in (ext / 'SHA256SUMS').read_text().splitlines():
        expected, rel = line.split(maxsplit=1)
        p = ext / rel
        if not p.exists():
            assert rel == './analysis/components_campaign129.npz'
            sum_results.append({'path': rel, 'status': 'OMITTED_NOT_VERIFIED', 'advertised_sha256': expected})
        else:
            assert sha(p.read_bytes()) == expected
            sum_results.append({'path': rel, 'status': 'PASS'})

    cases, arrays = [], []
    for case in emc['grid']['cases']:
        cid = case['case_id']
        d, old = raw / 'cases' / cid, prior / 'cases' / cid
        result, previous = read(d / 'RESULT.json'), read(old / 'RESULT.json')
        complete, start, reservation = (read(d / n) for n in ('COMPLETE.json', 'STARTED.json', 'RESERVATION.json'))
        hb, oldhb = (d / 'history.npz').read_bytes(), (old / 'history.npz').read_bytes()
        digest = sha(hb)
        assert hb == oldhb and digest == complete['history_sha256'] == result['history_sha256']
        assert sha((d / 'RESULT.json').read_bytes()) == complete['result_sha256']
        assert complete['case_id'] == cid
        for r in (result, complete, start, reservation):
            assert r['identity'] == em['identity']
        for r in (result, start, reservation):
            assert r['case'] == case
        assert result['status'] == 'COMPLETE' and result['state_shape'] == [40, 101]
        assert result['dtype'] == 'float64' and result['operational_test_double'] is False
        assert result['runtime']['execution_site'] == 'ncp'
        assert result['runtime']['NCP_execution'] is True
        same_fields = ['case', 'mapping', 'diagnostics', 'endpoint', 'nfev', 'dtype', 'state_shape']
        assert all(result[k] == previous[k] for k in same_fields)
        case_arrays = []
        with np.load(d / 'history.npz', allow_pickle=False) as nc, np.load(old / 'history.npz', allow_pickle=False) as sc:
            assert nc.files == sc.files and len(nc.files) == 59
            for key in nc.files:
                a, b = nc[key], sc[key]
                assert a.dtype == b.dtype == np.dtype('float64') and a.shape == b.shape
                assert np.isfinite(a).all() and np.isfinite(b).all()
                assert a.tobytes(order='C') == b.tobytes(order='C')
                assert np.array_equal(a, b)
                error = float(np.max(np.abs(a - b), initial=0.0))
                row = {'case_id': cid, 'array': key, 'dtype': a.dtype.str,
                       'shape': list(a.shape), 'scalar_count': int(a.size),
                       'sha256_C_order_bytes': sha(a.tobytes(order='C')),
                       'finite': True, 'byte_equal': True, 'max_absolute_difference': error}
                arrays.append(row)
                case_arrays.append(row)
        cases.append({'case': case, 'history_sha256': digest, 'history_bytes': len(hb),
                      'whole_npz_byte_equal': True, 'result_sha256': complete['result_sha256'],
                      'complete_sha256': sha((d / 'COMPLETE.json').read_bytes()),
                      'start_utc': start['started_utc'], 'nfev': result['nfev'],
                      'same_science_result_fields': same_fields,
                      'diagnostics': result['diagnostics'], 'runtime': result['runtime'],
                      'solver_wall_s_reported_not_benchmark': result['solver_wall_s'],
                      'numeric_arrays': len(case_arrays)})

    returned = read(next(raw.glob('RETURN_*.json')))
    resources = read(next(raw.glob('RESOURCES_*.json')))
    storage = read(next(raw.glob('STORAGE_*.json')))
    assert returned['failure'] is None and set(returned['own_worker_exit_codes'].values()) == {0}
    assert returned['summary']['completion_counts'] == {'COMPLETE': 4}
    assert returned['summary']['identity'] == em['identity']
    assert resources['worker_cpus'] == [1, 2, 3, 4] and resources['coordinator_cpu'] == 0
    assert resources['observation']['snapshot']['protected_cpu'] == 55
    assert 55 not in resources['worker_cpus']
    original_review_path = local / 'checks/INDEPENDENT_REVIEW.json'
    original_review = read(original_review_path)
    assert original_review['status'] == 'PASS_SCOPED'
    assert original_review['source_identity']['run_identity'] == sm['identity']
    assert original_review['source_identity']['execution_content_commit'] == CONTENT
    inputs = read(ext / 'analysis/INPUT_BINDINGS.json')
    assert inputs['run_manifest_sha256'] == sha((raw / 'MANIFEST.json').read_bytes())
    assert inputs['run_identity'] == inputs['content_tree'] == em['identity']
    assert inputs['content_commit'] == CONTENT
    result = {
        'schema': 'C21N_PR94_EXTERNAL_RETURN_ACCEPTANCE_V1',
        'observed_utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS_SCOPED',
        'scope': 'Pinned PR94 source17, grid4, actual raw4/seals, 236 saved numeric arrays and reported resource receipts; no ODE, benchmark, repeated physics/static campaign, provider upload or provider readback.',
        'publication': {'repository': 'cosmosapjw-quantum/bass_cr', 'pr': 94,
                        'url': 'https://github.com/cosmosapjw-quantum/bass_cr/pull/94',
                        'head': HEAD, 'branch': 'research/cr-c21n-offgrid4-evidence-20261021',
                        'state_observed': 'OPEN_DRAFT', 'created_utc': '2026-10-21T13:14:54Z',
                        'updated_utc': '2026-10-21T13:19:04Z',
                        'prior_complete_refs_intake_utc': '2026-10-21T13:06:07Z',
                        'historical_intake_preserved': True},
        'source': {'execution_content_commit': CONTENT, 'physics_commit': PHYSICS,
                   'bindings': source_rows, 'frozen_binding_receipt_sha256': sha(source_binding_path.read_bytes()),
                   'grid_sha256': GRID_SHA, 'grid': emc['grid'], 'settings': emc['source']['settings'],
                   'solver': 'DOP853 (unchanged frozen integrator)', 'state': [40, 101],
                   'signed_coordinates': 'full Frobenius; separate massive matter, photons and massless neutrinos',
                   'new_source_adopted': False},
        'identities': {'ncp': em['identity'], 'sandbox': sm['identity'],
                       'canonical_manifest_sha256_valid_both': True,
                       'manifest_differences': delta, 'science_source_grid_code_equal': True,
                       'ncp_software': emc['software'], 'sandbox_software': smc['software']},
        'byte_comparison': {'cases': cases, 'arrays': arrays,
                            'whole_npz_equal_count': len(cases), 'numeric_array_count': len(arrays),
                            'numeric_scalar_count': sum(r['scalar_count'] for r in arrays),
                            'all_finite': True, 'all_bytes_equal': True, 'max_absolute_difference': 0.0,
                            'tolerance_applied_or_promoted': False,
                            'scope_limit': 'Stored output equality on these four cases does not establish global solver equivalence or a global error bound.'},
        'external_execution': {'return': returned, 'resources': resources, 'storage': storage,
                               'resource_time_scope': '2026-10-21T13:10:24Z observed snapshot, not a current reservation',
                               'site_basis': 'Operator-declared ncp; host/platform independently preserved in raw receipts',
                               'quota_scope': 'No finite CPU quota observed in visible memberships/ancestors; no exclusive host-capacity guarantee',
                               'build_scope': 'Python/NumPy/SciPy versions and observed platform; complete compiler/BLAS build provenance not supplied'},
        'physics_receipt_reuse': {'local_independent_review_path': 'checks/INDEPENDENT_REVIEW.json',
                                 'local_independent_review_sha256': sha(original_review_path.read_bytes()),
                                 'local_status': 'PASS_SCOPED',
                                 'external_reported_checks': read(ext / 'analysis/PHYSICS_CHECKS.json'),
                                 'basis': 'Actual source17 and all four NPZ bytes identical to independently reviewed sandbox raw; no repeated original field/RHS evaluation',
                                 'combined129_prefix_claim': 'PR94 author reports equality; combined129 artifact deliberately omitted and not independently revalidated in this intake'},
        'original_metadata_clarifications': [
            {'file': 'analysis/INPUT_BINDINGS.json', 'field': 'content_tree',
             'observed_value': inputs['content_tree'],
             'meaning': 'This 64-hex value is the canonical execution run identity, not a Git tree SHA. The explicit content_commit and actual source17 bind scientific provenance. Original metadata preserved.'},
            {'file': 'PUBLICATION_RECEIPT.json', 'field': 'head_sha_at_open',
             'meaning': 'Historical PR-open head a517d475d34a37b50d8f0eb7c4f7749dce67520a; latest observed pinned head is ' + HEAD}],
        'export_scope': {'pinned_export_sha256': sha(args.pinned_export.read_bytes()),
                         'exported_file_count': exported_count,
                         'exported_bytes': sum(r['bytes'] for r in export['exported_files']),
                         'git_blob_all_verified': True, 'SHA256SUMS_checks': sum_results,
                         'omitted_files': export['excluded_files'],
                         'complete_original_subtree_restored': False,
                         'original_manifests_preserved_unmodified': True},
        'backup_scope': {'external_receipt_sha256': sha((ext / 'BACKUP_RECEIPT.json').read_bytes()),
                         'status': 'PR94_AUTHOR_REPORTED_PROVIDER_ACK_AND_READBACK',
                         'provider_rechecked_by_this_intake': False,
                         'receipt': read(ext / 'BACKUP_RECEIPT.json'),
                         'prior_ambiguous_uploads_resolved_by_this_receipt': False},
        'dag_transition': {'NCP_offgrid4': 'COMPLETE_SCOPED_EXTERNAL_RETURN_ACCEPTED',
                           'historical_NOT_RUN_snapshots': 'PRESERVED',
                           'unique_science_targets_before': 129, 'unique_science_targets_after': 129,
                           'external_execution_count': 4, 'additional_unique_targets': 0,
                           'identical_inputs_already_completed_in_sandbox': 4,
                           'new_ODE_integrations_by_this_intake': 0,
                           'next_same_input_execution': 'BLOCKED_CONSUMED_INPUTS'},
        'states': {'EXECUTION': 'EXTERNAL_NCP_4_COMPLETE; INTAKE_NEW_ODE_0',
                   'PUBLICATION': 'PR94_PUBLISHED_DRAFT; ACCEPTANCE_ADDENDUM_PREPARED',
                   'BACKUP': 'EXTERNAL_REPORTED_DRIVE_DROPBOX_ACK_AND_READBACK; NO_PROVIDER_REQUERY',
                   'DAG': '129_UNIQUE_TARGETS_UNCHANGED; NCP_4_NEWLY_ACCEPTED'},
        'P0_findings': [], 'global_error_bound': None,
        'comparison_script_sha256': sha(Path(__file__).read_bytes()),
        'comparison_runtime': {'numpy': np.__version__, 'purpose': 'saved-array byte comparison only'},
    }
    with args.out.open('x') as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write('\n')
    print(json.dumps({'status': result['status'], 'source_bindings': len(source_rows),
                      'cases': len(cases), 'arrays': len(arrays),
                      'scalars': result['byte_comparison']['numeric_scalar_count'],
                      'max_absolute_difference': 0.0, 'out_sha256': sha(args.out.read_bytes())}))


if __name__ == '__main__':
    main()
