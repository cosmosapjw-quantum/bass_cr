"""Read-only duplicate guard for the accepted 125 targets plus new offgrid4.

This guard never imports a solver or grants authorization for new science.
Invoke it before the frozen C21N launcher when an explicitly approved future
grid is supplied. A rejected completed target must not be renamed and rerun.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
REGISTRY = HERE / 'COMPLETED_INPUTS_129.json'
AXES = ('S0', 'Pm0', 'Pr0')
ATOL = 2e-13


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def coordinates(case):
    values = tuple(case.get(key) for key in AXES)
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           or not math.isfinite(v) for v in values):
        raise ValueError('FINITE_SIGNED_COORDINATES_REQUIRED')
    return tuple(map(float, values))


def same_target(a, b):
    return all(abs(x-y) <= ATOL for x, y in zip(a, b))


def load_registry(path=REGISTRY):
    registry = json.loads(Path(path).read_text())
    if (registry.get('schema') != 'C21N_OFFGRID4_COMPLETED_INPUTS_V1'
            or registry.get('target_count') != 129
            or registry.get('axis_absolute_tolerance') != ATOL
            or len(registry.get('targets', [])) != 129):
        raise ValueError('COMPLETED_REGISTRY_SCHEMA')
    for item in registry['source_bindings']:
        bound = (REPO / item['path']).resolve()
        if (not bound.is_relative_to(REPO) or not bound.is_file()
                or bound.stat().st_size != item['size']
                or sha(bound) != item['sha256']):
            raise ValueError('COMPLETED_REGISTRY_SOURCE_CHANGED:' + item['path'])
    original = json.loads((REPO / registry['original_registry_path']).read_text())
    run = REPO / registry['new_run_path']
    envelope = json.loads((run / 'MANIFEST.json').read_text())
    identity = hashlib.sha256(json.dumps(envelope['manifest'], sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    if identity != envelope['identity'] or identity != registry['new_run_identity']:
        raise ValueError('COMPLETED_RUN_IDENTITY')
    expected = list(original['targets'])
    for case in envelope['manifest']['grid']['cases']:
        folder = run / 'cases' / case['case_id']
        result = json.loads((folder / 'RESULT.json').read_text())
        seal = json.loads((folder / 'COMPLETE.json').read_text())
        if (result.get('status') != 'COMPLETE'
                or result.get('operational_test_double') is not False
                or result.get('case') != case or result.get('identity') != identity
                or seal.get('identity') != identity
                or seal.get('case_id') != case['case_id']
                or sha(folder / 'history.npz') != seal['history_sha256']
                or result['history_sha256'] != seal['history_sha256']
                or sha(folder / 'RESULT.json') != seal['result_sha256']):
            raise ValueError('COMPLETED_CASE_SEAL:' + case['case_id'])
        expected.append({**case, 'source_run_id': envelope['manifest']['grid']['run_id']})
    if registry['targets'] != expected:
        raise ValueError('COMPLETED_TARGETS_DIFFER_FROM_BOUND_SOURCES')
    seen = []
    for case in expected:
        value = coordinates(case)
        if any(same_target(value, prior) for prior in seen):
            raise ValueError('DUPLICATE_COMPLETED_AUTHORITY')
        seen.append(value)
    return registry


def inspect_grid(grid, registry):
    if grid.get('schema') != 'C21N_GRID_V1' or not isinstance(grid.get('cases'), list) or not grid['cases']:
        raise ValueError('NONEMPTY_C21N_GRID_REQUIRED')
    matches, seen, identifiers = [], [], set()
    for case in grid['cases']:
        value = coordinates(case)
        case_id = case.get('case_id')
        if not isinstance(case_id, str) or not case_id or case_id in identifiers:
            raise ValueError('MISSING_OR_DUPLICATE_CASE_ID')
        if any(same_target(value, prior) for prior in seen):
            raise ValueError('DUPLICATE_TARGET_IN_REQUEST')
        identifiers.add(case_id)
        seen.append(value)
        for old in registry['targets']:
            if same_target(value, coordinates(old)):
                matches.append({'requested_case_id': case_id,
                    'completed_case_id': old['case_id'],
                    'completed_run_id': old['source_run_id']})
    return {'status': 'REFUSE_COMPLETED_INPUTS' if matches else 'NO_COMPLETED_TARGET_OVERLAP',
        'requested_case_count': len(grid['cases']), 'completed_target_count': 129,
        'axis_absolute_tolerance': ATOL, 'completed_matches': matches,
        'science_execution': 'NOT_RUN', 'new_science_authorization': False,
        'scope': 'duplicate guard only; positivity, source, resources and input approval remain separate',
        'global_error_bound': None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--grid', required=True, type=Path)
    args = parser.parse_args()
    registry = load_registry()
    result = inspect_grid(json.loads(args.grid.read_text()), registry)
    result['registry_sha256'] = sha(REGISTRY)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 2 if result['completed_matches'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
