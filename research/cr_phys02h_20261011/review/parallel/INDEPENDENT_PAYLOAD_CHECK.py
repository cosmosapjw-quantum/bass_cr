"""Bounded read-only AST and persisted-payload review; no producer imports.

Only stdlib is used. No generator, physical formula, solver, pilot or old test
is executed. NPY headers and raw bytes are checked directly.
"""
from datetime import datetime, timezone
from pathlib import Path
import ast
import bisect
import copy
import hashlib
import json
import math
import signal
import struct
import sys
import time

HERE = Path(__file__).resolve().parent
H = HERE.parents[1]
REPO = H.parents[1]
PILOT = H/'evidence/parallel/pilot'
INPUTS = {}
COUNTS = {'payloads': 0, 'npy_arrays': 0, 'same_input_candidate_pairs': 0,
          'raw_array_pair_comparisons': 0, 'repeat_reference_pairs': 0,
          'stored_column_occurrences': 0, 'diagnostic_records': 0,
          'stored_worker_proofs': 0}
PINNED = {
    'state/SCIENTIFIC_CONTRACT.json': 'a49b1fa88c86d46c4e37cdb7ba37fbd44e5fa05511febc3a3089ab5ed5331dc4',
    'src/parallel_operator.py': '3a7e89f158339712a2c1109b2599d3062fff21a1ab99fadf4f906f5375e3bfbd',
    'scripts/run_parallel_pilot.py': 'b431a553880c27777ea0afbe60658bcd0cb1a7a5ddc7cfbf1a0bfd66c6a88454',
    'tests/test_parallel_operator.py': '549d35d6f8b70d4e1e9ba90b1c1071646646435b8103a7341b9fbeb9beca3ef0',
    'evidence/parallel/PILOT_PLAN.json': '069398cddac9ac4ac4dc7a9f67fc0fdcebb47fe794418623b2c536770706220c',
    'evidence/parallel/pilot/RESULT.json': '7546b4b8e04adae6f2d033c562ce7c3cfbf52a23ba54b0c655881276e19ada5a',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    INPUTS[str(path.relative_to(REPO))] = {'bytes': len(raw), 'sha256': digest(raw)}
    return raw


def jread(path):
    return json.loads(read(path))


def read_array(path, info):
    raw = read(path)
    assert len(raw) == info['file_bytes'] and digest(raw) == info['file_sha256']
    assert raw[:6] == b'\x93NUMPY'
    version = tuple(raw[6:8])
    if version == (1, 0):
        size = struct.unpack_from('<H', raw, 8)[0]
        offset = 10
    elif version in ((2, 0), (3, 0)):
        size = struct.unpack_from('<I', raw, 8)[0]
        offset = 12
    else:
        raise AssertionError('Unknown NPY version')
    header = ast.literal_eval(raw[offset:offset+size].decode('utf8'))
    assert header['fortran_order'] is False
    assert header['descr'] == info['dtype'] and list(header['shape']) == info['shape']
    assert len(header['shape']) == 1
    dtype = header['descr']
    assert dtype in ('<f8', '<i4')
    code, itemsize = ('<d', 8) if dtype == '<f8' else ('<i', 4)
    payload = raw[offset+size:]
    assert len(payload) == header['shape'][0]*itemsize
    assert digest(payload) == info['raw_sha256']
    values = tuple(z[0] for z in struct.iter_unpack(code, payload))
    if dtype == '<f8':
        assert all(math.isfinite(z) for z in values)
    COUNTS['npy_arrays'] += 1
    return {'dtype': dtype, 'shape': header['shape'], 'raw': payload, 'values': values}


def ast_proof(parent_source):
    tree = ast.parse(parent_source)
    cascade = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Cascade')
    original = next(x for x in cascade.body if isinstance(x, ast.FunctionDef) and x.name == '_generator')
    candidate = copy.deepcopy(original)
    loops = [x for x in candidate.body if isinstance(x, ast.For) and ast.unparse(x.iter) == 'enumerate(self.E)']
    assert len(loops) == 1 and ast.unparse(loops[0].target) == '(j, energy)'
    candidate.name = '_cr_phys02h_restricted_generator'
    candidate.args.args.append(ast.arg(arg='columns'))
    loops[0].iter = ast.GeneratorExp(
        elt=ast.Tuple(elts=[ast.Name(id='j', ctx=ast.Load()),
            ast.Subscript(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='E', ctx=ast.Load()),
                          slice=ast.Name(id='j', ctx=ast.Load()), ctx=ast.Load())], ctx=ast.Load()),
        generators=[ast.comprehension(target=ast.Name(id='j', ctx=ast.Store()),
            iter=ast.Name(id='columns', ctx=ast.Load()), ifs=[], is_async=0)])
    restored = copy.deepcopy(candidate)
    restored.name = original.name
    restored.args.args.pop()
    next(x for x in restored.body if isinstance(x, ast.For) and ast.unparse(x.target) == '(j, energy)').iter = copy.deepcopy(
        next(x for x in original.body if isinstance(x, ast.For) and ast.unparse(x.iter) == 'enumerate(self.E)').iter)
    assert ast.dump(restored, include_attributes=False) == ast.dump(original, include_attributes=False)
    return {'original_AST_sha256': digest(ast.dump(original, include_attributes=False).encode()),
            'restricted_AST_sha256': digest(ast.dump(candidate, include_attributes=False).encode())}


def equal_arrays(a, b):
    assert list(a) == list(b)
    for key in a:
        assert a[key]['dtype'] == b[key]['dtype'] and a[key]['shape'] == b[key]['shape']
        assert a[key]['raw'] == b[key]['raw']
        COUNTS['raw_array_pair_comparisons'] += 1


def run():
    for rel, sha in PINNED.items():
        assert digest(read(H/rel)) == sha
    contract = jread(H/'state/SCIENTIFIC_CONTRACT.json')
    for entry in contract['immutable_inputs'].values():
        raw = read(REPO/entry['relative_to_repo'])
        assert len(raw) == entry['bytes'] and digest(raw) == entry['sha256']
    parent_path = REPO/contract['immutable_inputs']['parent_cascade']['relative_to_repo']
    proof = ast_proof(parent_path.read_text())
    plan = jread(H/'evidence/parallel/PILOT_PLAN.json')
    result = jread(PILOT/'RESULT.json')
    summary = jread(H/'evidence/parallel/SUMMARY.json')
    external = jread(H/'evidence/parallel/pilot.ACTUAL_EXIT.json')
    tests = jread(H/'evidence/parallel/tests.ACTUAL_EXIT.json')
    assert external['actual_exit'] == tests['actual_exit'] == 0
    assert not external['timeout'] and not tests['timeout']
    assert 0 < result['wall_s'] < external['wall_s'] < 240
    assert result['plan_sha256'] == PINNED['evidence/parallel/PILOT_PLAN.json']
    reservation = jread(PILOT/'PILOT_RESERVATION.json')
    assert reservation['plan_sha256'] == result['plan_sha256'] and reservation['budget_program_runs'] == 1
    rows = result['rows']
    expected = {(scope, model, rep, mode, workers)
        for scope in ('small', 'selected') for model in ('legacy', 'fullBED') for rep in (1, 2)
        for mode, workers in ([('serial', 0), ('parallel', 1), ('parallel', 2), ('parallel', 4)]
            if scope == 'small' else [('serial', 0), ('parallel', 4)])}
    assert len(rows) == len(expected) == 24
    assert {(r['scope'], r['model'], r['rep'], r['mode'], r['workers']) for r in rows} == expected
    assert len({r['name'] for r in rows}) == 24
    assert sum(r['actual_generator_invocations'] for r in rows) == 52
    assert sum(r['actual_generator_invocations'] for r in rows if r['mode'] == 'parallel') == 44
    assert result['logical_small_builds'] == 16 and result['logical_selected_builds'] == 8
    assert result['actual_original_unrestricted_generators'] == result['actual_serial_restricted_generators'] == 4
    assert result['full9600_complete_builds'] == 0
    runtime = result['runtime']
    assert runtime['sources'] == plan['sources']
    assert all(x == '1' for x in runtime['threads'].values())
    assert all(x['num_threads'] == 1 for x in runtime['threadpools'])
    snapshots, timing = {}, []
    peak_workers, peak_coordinators = [], []
    for row in rows:
        name = row['name']
        directory = PILOT/name
        side = jread(directory/'SIDECAR.json')
        rsv = jread(PILOT/(name+'_RESERVATION.json'))
        n = 240 if row['scope'] == 'small' else 9600
        columns = list(range(n)) if n == 240 else plan['selected_columns']
        assert side['schema'] == 'cr-phys02h-persistent-raw-csc.v1'
        assert side['shape'] == [n+11, n+11] and side['columns'] == columns
        assert rsv['columns'] == columns and rsv['expected_generator_invocations'] == (row['workers'] or 1)
        assert side['arrays'] == row['arrays'] and side['telemetry'] == row['telemetry']
        assert side['runtime'] == runtime
        arrays = {key: read_array(directory/(key+'.npy'), info) for key, info in side['arrays'].items()}
        assert list(arrays) == ['data', 'indices', 'indptr', 'energy', 'rate_stopping_eV_s',
                                'rate_ion_HI', 'rate_ion_HeI', 'rate_exc_HI', 'rate_exc_HeI']
        data, indices, pointers, energies = (arrays[key]['values'] for key in ('data', 'indices', 'indptr', 'energy'))
        assert len(data) == len(indices) and len(pointers) == n+12 and len(energies) == n
        assert pointers[0] == 0 and pointers[-1] == len(data)
        assert all(a <= b for a, b in zip(pointers, pointers[1:]))
        assert all(0 <= i < n+11 for i in indices)
        assert all(a < b for a, b in zip(energies, energies[1:])) and energies[0] > 0.1 and energies[-1] == 900
        assert any(x < 0 for x in data) and row['signed_data_preserved'] is True
        owned = set(columns)
        for col, (lo, hi) in enumerate(zip(pointers, pointers[1:])):
            if col not in owned:
                assert lo == hi
            else:
                assert lo < hi
                assert all(a < b for a, b in zip(indices[lo:hi], indices[lo+1:hi]))
        if n == 9600:
            assert digest(arrays['energy']['raw']) == plan['energy_raw_sha256']
            assert [energies[j] for j in columns] == plan['selected_energy_eV']
            selection = {0, 3199, 3200, 9599}
            for value in plan['anchors_eV']:
                k = bisect.bisect_left(energies, value)
                selection.update((k-1, k))
            assert sorted(selection) == columns and len(columns) == 16
        expected_diagnostics = [(sp, energies[j]) for j in columns for sp in ('HI', 'HeI')
                                if arrays['rate_ion_'+sp]['values'][j] != 0]
        assert [(d[0], d[1]) for d in side['diagnostics']] == expected_diagnostics
        assert all(len(d) == 4 and math.isfinite(d[2]) and 0 <= d[2] <= 2e-8
                   and math.isfinite(d[3]) and d[3] > 0 for d in side['diagnostics'])
        assembly = side['assembly_identity']
        if row['mode'] == 'serial':
            peak_coordinators.append(side['telemetry']['peakRSS_bytes'])
            if n == 240:
                assert assembly == {'unmodified_original_generator': True}
                fragments = []
            else:
                fragments = [assembly]
        else:
            fragments = assembly['tiles']
            assert len(fragments) == row['workers']
            tel = side['telemetry']
            assert tel['exitcodes'] == [0]*row['workers']
            assert len(tel['worker_processes']) == tel['actual_generator_invocations'] == row['workers']
            admit = tel['admission']
            assert admit['workers'] == row['workers'] and admit['coordinator_processes'] == 1
            assert admit['cpu_max'] == '800000 100000' and admit['quota_cpus'] == 8.0
            assert admit['memory_max_bytes'] == 8*2**30 and admit['reserve_bytes'] >= 2*2**30
            assert row['workers']+1 <= min(admit['affinity_cpus'], admit['quota_cpus'])
            assert admit['memory_current_bytes']+admit['estimated_new_peak_bytes']+admit['reserve_bytes'] <= admit['memory_max_bytes']
            peak_workers.extend(p['peakRSS_bytes'] for p in tel['worker_processes'])
            peak_coordinators.append(tel['coordinator_peakRSS_bytes'])
            COUNTS['stored_worker_proofs'] += len(fragments)
        for fragment in fragments:
            assert all(fragment[k] == v for k, v in proof.items())
            assert fragment['restored_AST_exact'] is True
            assert fragment['compiled_globals'] == ('cr_phys02h_real_legacy' if row['model'] == 'legacy' else 'cr_phys02c_checked_parent')
        key = row['scope'], row['model'], row['rep']
        if row['mode'] == 'serial':
            snapshots[key] = (arrays, side['diagnostics'])
        else:
            reference, diagnostic_reference = snapshots[key]
            equal_arrays(reference, arrays)
            assert json.dumps(diagnostic_reference, separators=(',', ':')) == json.dumps(side['diagnostics'], separators=(',', ':'))
            assert row['parity'] == {k: True for k in ('data', 'indices', 'indptr', 'energy', 'rates', 'diagnostics', 'columns')}
            COUNTS['same_input_candidate_pairs'] += 1
        COUNTS['payloads'] += 1
        COUNTS['stored_column_occurrences'] += len(columns)
        COUNTS['diagnostic_records'] += len(side['diagnostics'])
        timing.append({k: row[k] for k in ('scope', 'model', 'rep', 'mode', 'workers', 'end_to_end_wall_s')})
    for scope in ('small', 'selected'):
        for model in ('legacy', 'fullBED'):
            a, da = snapshots[(scope, model, 1)]
            b, db = snapshots[(scope, model, 2)]
            equal_arrays(a, b)
            assert json.dumps(da, separators=(',', ':')) == json.dumps(db, separators=(',', ':'))
            COUNTS['repeat_reference_pairs'] += 1
    assert COUNTS['npy_arrays'] == 216 and COUNTS['same_input_candidate_pairs'] == 16
    assert COUNTS['stored_worker_proofs'] == 44
    return {'checks': COUNTS, 'AST_proof': proof, 'timings': timing,
            'producer_counts': {k: result[k] for k in ('logical_small_builds', 'logical_selected_builds',
                'logical_total', 'actual_generator_invocations', 'actual_original_unrestricted_generators',
                'actual_serial_restricted_generators', 'actual_partial_worker_generators', 'full9600_complete_builds')},
            'producer_process_wall_s': external['wall_s'], 'producer_inner_wall_s': result['wall_s'],
            'worker_lifetime_peakRSS_max_bytes': max(peak_workers),
            'coordinator_lifetime_peakRSS_max_bytes': max(peak_coordinators),
            'RSS_scope_limit':'No simultaneous-total sampler; resource_tracker support process not included; no full-grid or NCP resource inference.',
            'local_runtime': runtime,
            'reviewer_new_physical_calls': {'G': 0, 'F_retry': 0, 'pulse': 0, 'expm': 0,
                'resolvent': 0, 'linear_solve': 0, 'pilot_rerun': 0, 'old_suite_rerun': 0},
            'NCP_preparation_admitted': False}


if __name__ == '__main__':
    t0 = time.monotonic()
    receipt = {'schema': 'cr-phys02h-independent-parallel-payload-check.v1',
               'start_utc': datetime.now(timezone.utc).isoformat(), 'command': sys.argv,
               'timeout_s': 60, 'execution_count': 1, 'producer_imports': [],
               'reviewer_script_sha256': digest(Path(__file__).read_bytes())}
    signal.signal(signal.SIGALRM, lambda signum, frame: (_ for _ in ()).throw(TimeoutError('60s read-only review limit')))
    signal.alarm(60)
    try:
        receipt.update(run(), actual_exit=0, status='PASS_READ_ONLY_PARALLEL_PAYLOAD_CHECK')
    except BaseException as exc:
        receipt.update(actual_exit=1, status='FAIL_PRESERVED', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        signal.alarm(0)
        receipt.update(end_utc=datetime.now(timezone.utc).isoformat(), wall_s=time.monotonic()-t0)
        with (HERE/'INDEPENDENT_INPUT_INVENTORY.json').open('x') as f:
            json.dump(INPUTS, f, indent=2, ensure_ascii=False)
            f.write('\n')
        receipt['input_inventory_sha256'] = digest((HERE/'INDEPENDENT_INPUT_INVENTORY.json').read_bytes())
        with (HERE/'INDEPENDENT_PAYLOAD_RECEIPT.json').open('x') as f:
            json.dump(receipt, f, indent=2, ensure_ascii=False, allow_nan=False)
            f.write('\n')
        print(json.dumps({k: receipt[k] for k in ('status', 'actual_exit', 'wall_s')}))
