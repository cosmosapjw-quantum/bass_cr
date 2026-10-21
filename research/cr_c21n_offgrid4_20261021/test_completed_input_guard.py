"""Focused consumption-of-input checks; no scientific library or solver import."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import tempfile

import completed_input_guard as guard


def run(output):
    registry = guard.load_registry()
    checked = 0
    for index, old in enumerate(registry['targets']):
        case = {key: old[key] for key in guard.AXES}
        case['case_id'] = 'renamed_' + str(index)
        result = guard.inspect_grid({'schema': 'C21N_GRID_V1', 'cases': [case]}, registry)
        assert result['status'] == 'REFUSE_COMPLETED_INPUTS'
        assert len(result['completed_matches']) == 1
        checked += 1
    old = registry['targets'][-1]
    near = {key: old[key] for key in guard.AXES}
    near['case_id'] = 'near_completed'
    near['Pm0'] += 1e-13
    assert guard.inspect_grid({'schema': 'C21N_GRID_V1', 'cases': [near]}, registry)['completed_matches']
    new = {'S0': .003, 'Pm0': .000125, 'Pr0': -.000125, 'case_id': 'unexecuted_example'}
    clear = guard.inspect_grid({'schema': 'C21N_GRID_V1', 'cases': [new]}, registry)
    assert clear['status'] == 'NO_COMPLETED_TARGET_OVERLAP'
    assert clear['science_execution'] == 'NOT_RUN' and clear['new_science_authorization'] is False
    for invalid in ({**new, 'Pm0': float('nan')}, {**new, 'Pr0': True}):
        try:
            guard.inspect_grid({'schema': 'C21N_GRID_V1', 'cases': [invalid]}, registry)
        except ValueError as error:
            assert str(error) == 'FINITE_SIGNED_COORDINATES_REQUIRED'
        else:
            raise AssertionError('INVALID_COORDINATES_ADMITTED')
    try:
        guard.inspect_grid({'schema': 'C21N_GRID_V1', 'cases': [new, {**new, 'case_id': 'renamed_again'}]}, registry)
    except ValueError as error:
        assert str(error) == 'DUPLICATE_TARGET_IN_REQUEST'
    else:
        raise AssertionError('RENAMED_DUPLICATE_IN_GRID_ADMITTED')
    bad = copy.deepcopy(registry)
    bad['source_bindings'][0]['sha256'] = '0' * 64
    with tempfile.TemporaryDirectory(prefix='c21n_consumption_guard_') as directory:
        path = Path(directory) / 'invalid_registry.json'
        path.write_text(json.dumps(bad))
        try:
            guard.load_registry(path)
        except ValueError as error:
            assert str(error).startswith('COMPLETED_REGISTRY_SOURCE_CHANGED:')
        else:
            raise AssertionError('CHANGED_AUTHORITY_ADMITTED')
    receipt = {'schema': 'C21N_OFFGRID4_INPUT_GUARD_CHECK_V1', 'status': 'PASS_SCOPED',
        'renamed_completed_inputs_refused': checked, 'near_target_within_axis_tolerance_refused': True,
        'distinct_unexecuted_example_classified_without_execution': True,
        'nonfinite_and_boolean_coordinates_refused': True,
        'renamed_duplicate_request_refused': True, 'altered_authority_digest_refused': True,
        'registry_sha256': guard.sha(guard.REGISTRY),
        'guard_sha256': guard.sha(Path(guard.__file__)),
        'test_sha256': guard.sha(Path(__file__)), 'new_scientific_ODE_integrations': 0,
        'scope': 'duplicate guard only; not a new physical input certificate', 'global_error_bound': None}
    with Path(output).open('x') as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output)
