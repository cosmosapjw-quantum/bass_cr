"""Read-only federation for one explicitly authorized R4Z runtime recovery.

No worker is launched here and no historical marker is created or modified.
The original analyzer is called with only its data collector temporarily replaced;
its S-only formula, norm calculations, original R2 diagnostics and gates are intact.
The interrupted context's 28 reservations remain charged against the shared cap.
"""
from pathlib import Path
import argparse
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import derivative_analyzer as analyzer
import runner

ORIGINAL_CONTEXT_SHA = '81f8caeb79a366ae88f1309a59aa6ebd92d68f51f176debcbcf33d89ff1d0d23'
ORIGINAL_ANALYZER_SHA = '49d2fed8bfd53514a1a3ae495d7a9a07b7c8652cdcd78284096e61ede755e5c6'
COMPLETED_MAIN = list(range(17)) + [18]
INTERRUPTED_MAIN = [17, 19, 20]
UNSTARTED_MAIN = list(range(21, 33))
ORIGINAL_RESERVED = 28
NEW_TASKS = 15


def require(value, message):
    if not value:
        raise ValueError(message)


def file_binding(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': runner.sha(path), 'bytes': path.stat().st_size}


def validate_file(binding):
    path = Path(binding['path'])
    require(path.stat().st_size == binding['bytes'] and runner.sha(path) == binding['sha256'],
            'recovery file binding changed: ' + str(path))


def create_json(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def validate_authorization(path):
    inv = runner.read_json(path)
    require(inv['schema'] == 'BASS_R4Z_RUNTIME_INTERRUPTION_RECOVERY_V1' and
            inv['classification'] == 'RUNTIME_INTERRUPTION_RECOVERY' and bool(inv['authorization']),
            'explicit interruption recovery authorization required')
    expected = {'original_context_sha256': ORIGINAL_CONTEXT_SHA, 'pilot_complete': 7,
                'main_completed_indices': COMPLETED_MAIN, 'main_interrupted_indices': INTERRUPTED_MAIN,
                'main_unstarted_indices': UNSTARTED_MAIN, 'completed_operator_evaluations': 25,
                'consumed_reservations': ORIGINAL_RESERVED, 'new_missing_evaluations': NEW_TASKS,
                'planned_cumulative_reservations': 43}
    require(all(inv[k] == v for k, v in expected.items()), 'unexpected recovery inventory')
    for item in inv['files']:
        validate_file(item)
    return inv


def validated_observation(target, context, manifest, task, ledger):
    """Same payload validation as frozen analyzer.collect, without batch fabrication."""
    rec, raw, full = runner.load_payload(target, context, manifest, task)
    require(rec['status'] == 'COMPLETED_SHIFTED_SPATIAL_DIAGNOSTIC' and
            rec['candidate_basis_identity'] == context['candidate_basis_identity'], 'payload status/candidate mismatch')
    reservation = rec['reservation']
    require(reservation in ledger and reservation['task'] == task and
            reservation['manifest_id'] == manifest['manifest_id'], 'payload reservation mismatch')
    require(rec['source_pins_digest'] == runner.digest(context['source_pins']) and
            rec['input_pins'] == context['input_pins'], 'payload source/input mismatch')
    rawrec = runner.read_json(target / 'RAW.json')
    require(rawrec['sha256'] == rec['raw_sha256'], 'raw metadata/payload mismatch')
    screens = runner._screen_full(full, context['screens'])
    control = runner.central_s_control(raw, task['z_a0'])
    require(screens == rec['qualification_screens'] and control == rec['central_s_diagonal_control'],
            'recomputed payload screens differ')
    meta = rawrec['metadata']
    require(meta['candidate_basis_identity'] == context['candidate_basis_identity'], 'raw candidate mismatch')
    require(all(meta[k] == task[k] for k in ('order', 'subdivisions', 'inner_phase_budget')),
            'raw numerical task mismatch')
    require(rec['moment_call_evidence']['radial_pairs'] == meta['radial_pairs'], 'native radial-pair mismatch')
    name = analyzer.task_label(task)
    row = {'label': name, 'task': task, 'batch': manifest['batch'],
           'global_attempt': reservation['global_attempt'], 'screens': screens,
           'central_control': control, 'raw_sha256': rec['raw_sha256'], 'full_sha256': rec['full_sha256'],
           'record_sha256': runner.sha(target / 'COMPLETED.json'), 'radial_pairs': meta['radial_pairs'],
           'wall_seconds': rec['wall_seconds'], 'peak_rss_kib': rec['peak_rss_kib'],
           'geometry_identity': rec['geometry_identity'], 'moment_call_evidence': rec['moment_call_evidence'],
           'radial_total_call_evidence': rec['radial_total_call_evidence'], 'raw': raw, 'full': full,
           'execution_context_id': context['context_id'],
           'context_local_reserved_attempt': reservation['global_attempt'],
           'federated_reserved_attempt': reservation['global_attempt']}
    bindings = [file_binding(target / name) for name in ('RAW.npz', 'RAW.json', 'FULL.npz', 'COMPLETED.json')]
    return row, bindings


def collect_original(root, context_sha, authorization):
    require(context_sha == ORIGINAL_CONTEXT_SHA, 'wrong historical context')
    require(runner.sha(HERE / 'derivative_analyzer.py') == ORIGINAL_ANALYZER_SHA, 'original analyzer changed')
    inv = validate_authorization(authorization)
    root, context = runner.load_context(root, context_sha)
    require({p.name for p in (root / 'batches').iterdir() if p.is_dir()} == {'main', 'pilot'},
            'unexpected original batch set')
    ledger = runner.reservations(root, context)
    require(len(ledger) == ORIGINAL_RESERVED, 'original reservation count changed')
    observations, bindings, terminal, partial, missing = {}, [], [], [], []
    for batch in ('pilot', 'main'):
        dest = root / 'batches' / batch
        manifest_sha = runner.sha(dest / 'MANIFEST.json')
        _, manifest = runner.load_batch(root, context, batch, manifest_sha)
        require(manifest['context_sha256'] == context_sha, 'historical manifest context hash mismatch')
        start = runner.read_json(dest / 'STARTED.json')
        require(start['context_id'] == context['context_id'] and start['manifest_id'] == manifest['manifest_id'],
                'historical start identity mismatch')
        expected_indices = list(range(7)) if batch == 'pilot' else COMPLETED_MAIN
        require(len(manifest['tasks']) == (7 if batch == 'pilot' else 33), 'historical task count changed')
        for task in manifest['tasks']:
            target = dest / 'attempts' / f"{task['index']:03}"
            completed = (target / 'COMPLETED.json').exists()
            require(completed == (task['index'] in expected_indices), 'historical completion inventory changed')
            matches = [x for x in ledger if x['manifest_id'] == manifest['manifest_id'] and x['task'] == task]
            if completed:
                require(len(matches) == 1, 'completed historical task lacks unique reservation')
                row, payloads = validated_observation(target, context, manifest, task, ledger)
                require(row['label'] not in observations, 'duplicate original completed task')
                observations[row['label']] = row
                bindings.extend(payloads)
            else:
                require(batch == 'main', 'pilot must be completely terminal')
                is_interrupted = task['index'] in INTERRUPTED_MAIN
                require(len(matches) == int(is_interrupted), 'uncompleted historical reservation mismatch')
                require((target / 'STARTED.json').exists() == is_interrupted, 'uncompleted start inventory changed')
                if is_interrupted:
                    attempt_start = runner.read_json(target / 'STARTED.json')
                    require(attempt_start['task'] == task and attempt_start['reservation'] == matches[0],
                            'interrupted task start identity mismatch')
                else:
                    require(not target.exists(), 'unstarted task gained artifacts')
                missing.append(task)
        if batch == 'pilot':
            done, summary = runner.read_json(dest / 'COMPLETED.json'), runner.read_json(dest / 'SUMMARY.json')
            for record in (done, summary):
                require(record['context_id'] == context['context_id'] and record['manifest_id'] == manifest['manifest_id'],
                        'terminal historical batch identity mismatch')
            require(done['summary_sha256'] == runner.sha(dest / 'SUMMARY.json') and
                    done['actual_cross_calls'] == 7 and done['owned_worker_processes_remaining'] == 0,
                    'pilot not fully terminal')
            terminal.append({'name': batch, 'context_id': context['context_id'], 'manifest_id': manifest['manifest_id'],
                             'manifest_sha256': manifest_sha, 'summary_sha256': runner.sha(dest / 'SUMMARY.json'),
                             'completed_sha256': runner.sha(dest / 'COMPLETED.json'), 'actual_cross_calls': 7,
                             'wall_seconds': summary['batch_wall_seconds'], 'status': 'COMPLETED'})
        else:
            require(manifest_sha == inv['original_main_manifest_sha256'], 'original main manifest changed')
            require(not (dest / 'COMPLETED.json').exists() and not (dest / 'SUMMARY.json').exists(),
                    'interrupted historical batch was retroactively marked complete')
            partial.append({'name': batch, 'context_id': context['context_id'], 'manifest_id': manifest['manifest_id'],
                            'manifest_sha256': manifest_sha, 'status': 'RUNTIME_INTERRUPTED_PRESERVED',
                            'validated_completed_calls': 18, 'reserved_attempts': 21, 'interrupted_attempts': 3,
                            'unstarted_tasks': 12, 'wall_seconds': None, 'complete_batch_wall_observed': False})
    require(len(observations) == 25 and len(missing) == 15, 'historical count mismatch')
    return root, context, observations, terminal, partial, bindings, ledger, missing


def assert_missing_plan(plan, missing, completed_ids, ledger):
    require(set(plan) == {'tasks'}, 'plan must contain tasks only')
    tasks = runner.validate_tasks(plan['tasks'])
    require([x['task_id'] for x in tasks] == [x['task_id'] for x in missing], 'recovery plan differs from missing tasks')
    require(not ({x['task_id'] for x in tasks} & set(completed_ids)), 'recovery attempts a completed task')
    incomplete_reserved = {x['task']['task_id'] for x in ledger} - set(completed_ids)
    require(({x['task_id'] for x in tasks} & {x['task']['task_id'] for x in ledger}) == incomplete_reserved,
            'only incomplete historical reservations may recur')
    require(len(ledger) + len(tasks) <= runner.CAP, 'cumulative recovery budget exceeded')
    return tasks


def freeze_binding(original_root, context_sha, authorization, plan_path, out):
    root, ctx, obs, terminal, partial, payloads, ledger, missing = collect_original(original_root, context_sha, authorization)
    tasks = assert_missing_plan(runner.read_json(plan_path), missing, [x['task']['task_id'] for x in obs.values()], ledger)
    binding = {'schema': 'BASS_R4Z_RECOVERY_BINDING_V1', 'original_root': str(root),
               'original_context_sha256': context_sha, 'original_context_id': ctx['context_id'],
               'authorization': file_binding(authorization), 'recovery_plan': file_binding(plan_path),
               'adapter_source': file_binding(__file__), 'unchanged_analyzer_source': file_binding(HERE / 'derivative_analyzer.py'),
               'original_completed_task_ids': [x['task']['task_id'] for x in obs.values()],
               'recovery_task_ids': [x['task_id'] for x in tasks],
               'original_reserved_attempts': len(ledger), 'original_completed_calls': len(obs),
               'original_incomplete_reserved_attempts': 3, 'new_recovery_calls': len(tasks),
               'cumulative_reserved_attempts_on_completion': len(ledger) + len(tasks),
               'maximum_raw_attempt_budget': runner.CAP, 'automatic_retries': 0,
               'manual_recovery_reexecutions_of_incomplete_tasks': 3,
               'original_terminal_batches': terminal, 'original_interrupted_batches': partial,
               'original_payload_bindings': payloads, 'scientific_contract_changed': False,
               'physical_calls_by_adapter': 0}
    create_json(out, binding)
    return binding


def load_binding(path, expected_sha):
    require(runner.sha(path) == expected_sha, 'recovery binding bytes changed')
    binding = runner.read_json(path)
    require(binding['schema'] == 'BASS_R4Z_RECOVERY_BINDING_V1', 'wrong recovery binding schema')
    for name in ('authorization', 'recovery_plan', 'adapter_source', 'unchanged_analyzer_source'):
        validate_file(binding[name])
    require(binding['adapter_source']['path'] == str(Path(__file__).resolve()), 'wrong recovery adapter path')
    return binding


def preflight(binding_path, binding_sha, recovery_root, recovery_context_sha, batch, manifest_sha, terminal=False):
    binding = load_binding(binding_path, binding_sha)
    original = collect_original(binding['original_root'], binding['original_context_sha256'], binding['authorization']['path'])
    _, old, obs, _, _, _, ledger, missing = original
    require(binding['original_completed_task_ids'] == [x['task']['task_id'] for x in obs.values()], 'historical completed IDs changed')
    root, new = runner.load_context(recovery_root, recovery_context_sha)
    require(root != original[0] and new['context_id'] != old['context_id'], 'recovery needs a distinct fresh context')
    for k in ('input_pins', 'candidate_basis_identity', 'original_basis_identity', 'speed_a0_per_ta', 'fixed_geometry',
              'fixed_numerics', 'screens', 'allowed_z_a0', 'resolution_grid', 'contract', 'raw_attempt_budget', 'automatic_retries'):
        require(new[k] == old[k], 'scientific/native input context changed: ' + k)
    require(all(new['source_pins'].get(k) == v for k, v in old['source_pins'].items()), 'historical source pins not preserved')
    require(new['source_pins'].get(str(Path(__file__).resolve())) == runner.sha(__file__), 'fresh context must pin recovery adapter')
    require({p.name for p in (root / 'batches').iterdir() if p.is_dir()} == {batch}, 'recovery must have one declared batch only')
    dest, manifest = runner.load_batch(root, new, batch, manifest_sha)
    require(manifest['context_sha256'] == recovery_context_sha, 'recovery manifest context hash mismatch')
    require(manifest['plan_sha256'] == binding['recovery_plan']['sha256'], 'recovery manifest plan binding mismatch')
    tasks = assert_missing_plan(manifest['plan'], missing, binding['original_completed_task_ids'], ledger)
    require(binding['recovery_task_ids'] == [x['task_id'] for x in tasks], 'bound recovery task IDs changed')
    fresh_ledger = runner.reservations(root, new)
    require(len(ledger) + len(fresh_ledger) <= runner.CAP, 'cumulative reservation cap exceeded')
    if not terminal:
        require(not fresh_ledger and not (dest / 'STARTED.json').exists(), 'preflight is for a fresh unstarted recovery batch')
    else:
        require(len(fresh_ledger) == NEW_TASKS, 'terminal recovery reservation count mismatch')
    return binding, original, root, new, manifest


def analyze_recovery(binding_path, binding_sha, recovery_root, recovery_context_sha, batch, manifest_sha):
    binding, original, root, context, manifest = preflight(binding_path, binding_sha, recovery_root,
                                                           recovery_context_sha, batch, manifest_sha, terminal=True)
    _, old, old_obs, old_batches, partial, old_payloads, old_ledger, missing = original
    collect_unchanged = analyzer.collect
    # Preserve original collect's terminal semantics for the new context.
    fresh = collect_unchanged(root, recovery_context_sha)
    _, _, contract, new_obs, new_batches, new_payloads = fresh
    require(len(new_obs) == NEW_TASKS, 'new completed payload count mismatch')
    require(not (set(old_obs) & set(new_obs)), 'duplicate completed numerical task across contexts')
    for row in new_obs.values():
        row['execution_context_id'] = context['context_id']
        row['context_local_reserved_attempt'] = row['global_attempt']
        row['federated_reserved_attempt'] = ORIGINAL_RESERVED + row['global_attempt']
    observations = {**old_obs, **new_obs}
    require(len(observations) == 40, 'federated completed payload count mismatch')
    for row in new_batches:
        row['context_id'] = context['context_id']
        row['status'] = 'COMPLETED'
    def federated_collect(requested_root, requested_sha):
        require(Path(requested_root).resolve() == root and requested_sha == recovery_context_sha,
                'federated collector request mismatch')
        return root, context, contract, observations, old_batches + new_batches, old_payloads + new_payloads
    analyzer.collect = federated_collect
    try:
        result = analyzer.analyze(root, recovery_context_sha)
    finally:
        analyzer.collect = collect_unchanged
    # Reporting repairs only: the historical main has no terminal timing marker.
    result['known_terminal_batch_wall_seconds_subtotal'] = result['batch_wall_seconds_sum']
    result['batch_wall_seconds_sum'] = None
    result['batch_wall_seconds_sum_status'] = 'UNAVAILABLE_ORIGINAL_MAIN_INTERRUPTED'
    result['batch_records'].extend(partial)
    result['actual_raw_operator_calls'] = 40
    result['actual_raw_operator_calls_definition'] = 'Completed and hash-validated full cross-operator payloads; interrupted calls excluded'
    result['completed_operator_calls'] = 40
    result['global_reserved_attempts'] = 43
    result['interrupted_attempts_without_completed_payload'] = 3
    result['attempt_identifier_scope'] = 'global_attempt is context-local; federated_reserved_attempt charges old1..28 and new29..43'
    result['recovery_adapter_source'] = {**file_binding(__file__), 'execution_context_source_pin_member': True}
    result['runtime_recovery'] = {'classification': 'RUNTIME_INTERRUPTION_RECOVERY',
        'binding': file_binding(binding_path), 'authorization': binding['authorization'],
        'original_context_id': old['context_id'], 'original_context_sha256': binding['original_context_sha256'],
        'recovery_context_id': context['context_id'], 'recovery_context_sha256': recovery_context_sha,
        'original_completed_calls_reused': 25, 'new_completed_calls': 15, 'original_reserved_attempts': 28,
        'cumulative_reserved_attempts': 43, 'original_incomplete_attempts_preserved': 3,
        'manual_recovery_reexecutions_of_incomplete_tasks': 3, 'original_never_started_tasks_executed': 12,
        'automatic_retries': 0, 'duplicate_completed_tasks': 0, 'historical_artifacts_modified': False,
        'original_partial_batch_fabricated_complete': False, 'scientific_contract_changed': False,
        'numerical_analyzer_functions_changed': False, 'federation_affects_collection_and_reporting_only': True}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    freeze = sub.add_parser('freeze')
    for arg in ('original-root', 'original-context-sha256', 'authorization', 'plan', 'out'):
        freeze.add_argument('--' + arg, required=True)
    for command in ('preflight', 'analyze'):
        p = sub.add_parser(command)
        for arg in ('binding', 'binding-sha256', 'root', 'context-sha256', 'batch', 'manifest-sha256', 'out'):
            p.add_argument('--' + arg, required=True)
    args = parser.parse_args()
    require(not Path(args.out).exists(), 'output is create-only')
    if args.command == 'freeze':
        value = freeze_binding(args.original_root, args.original_context_sha256, args.authorization, args.plan, args.out)
        print(json.dumps({'status': 'RECOVERY_BINDING_FROZEN_NO_PHYSICAL_CALLS', 'sha256': runner.sha(args.out),
                          'missing_tasks': value['new_recovery_calls'], 'cumulative_reserved_on_completion': 43}))
        return
    params = (args.binding, args.binding_sha256, args.root, args.context_sha256, args.batch, args.manifest_sha256)
    if args.command == 'preflight':
        binding, _, _, context, manifest = preflight(*params)
        value = {'status': 'RECOVERY_PREFLIGHT_PASS_NO_PHYSICAL_CALLS', 'binding': file_binding(args.binding),
                 'context_id': context['context_id'], 'context_sha256': args.context_sha256,
                 'manifest_id': manifest['manifest_id'], 'manifest_sha256': args.manifest_sha256,
                 'original_reserved_attempts': 28, 'new_tasks': 15, 'cumulative_reserved_on_completion': 43,
                 'maximum_raw_attempt_budget': 64, 'automatic_retries': 0}
    else:
        value = analyze_recovery(*params)
    create_json(args.out, value)
    print(json.dumps({'status': value['status'], 'sha256': runner.sha(args.out)}))
    if args.command == 'analyze' and not value['selected_checks_pass']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
