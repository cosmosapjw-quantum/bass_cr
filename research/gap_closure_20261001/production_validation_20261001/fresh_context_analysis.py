"""Offline G02/G03 diagnostics with fresh HPC context and exact cache binding.

No physical evaluator is imported or constructed here. Historical query plans
define coordinates and numerical acceptance only; their cache identities are
never rewritten or added to the fresh operator context.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
GAP = HERE.parent
for directory in (GAP/'production_solver_20261001/provider',
                  GAP/'static_validation_20261001',
                  GAP/'static_validation_20261001/executor',
                  GAP/'asymptotics_20261001'):
    sys.path.insert(0, str(directory))
import hpc_provider as hp
import static_validation as fd
import g03_rate_postprocess as rates
import asymptotic_models as models
import numpy as np

FD_PLAN = GAP/'static_validation_20261001/E_SDOT_FD_EXECUTION_CONTRACT.json'
FD_PLAN_SHA = '6644827b9cbde65a5a27f8d2229ed9dc99caf9022c70e2c8663a43dfda0b1c7c'
G03_PLAN = GAP/'static_validation_20261001/executor/G03_SCIENCE_CONTRACT.json'
G03_PLAN_SHA = '479ca3efdbbacfdc698b29a9c4eeef2597e5979b2960e14a594cad7f96bb01b4'
CEILINGS = {'capture': False, 'production_admission': 'HOLD',
            'all_bound': 'OPEN', 'b_grid': 'NO_GO',
            'continuous_trajectory_error_bound': False,
            'new_native_calls_in_analysis': 0}


def read(path):
    return hp.strict_json(Path(path))


def _fixed(path, expected):
    if hp.sha(path) != expected:
        raise ValueError('historical science contract byte identity mismatch')
    return read(path)


def _pins():
    files = [Path(__file__), Path(fd.__file__), Path(rates.__file__),
             Path(models.__file__), FD_PLAN, G03_PLAN, models.DEFAULT_SAMPLES,
             GAP/'production_solver_20261001/evidence/PHYSICAL_PARITY.json']
    return {str(p.relative_to(hp.REPO)): hp.sha(p) for p in files}


def freeze_g03_predictions(output_path):
    """Create once before physics; the parent run contract must bind its SHA."""
    plan = _fixed(G03_PLAN, G03_PLAN_SHA)
    baseline = models.load_samples()
    frozen = models.analyze(baseline)
    # Verify historical contract predictions against the unchanged model fits.
    for q in plan['queries']:
        sign = 'incoming' if q['z_a0'] < 0 else 'outgoing'
        for model, fit in frozen['signed_fits'][sign].items():
            pred = float(models.predict(fit, q['R_a0']))
            if not np.isclose(pred, q['predictions'][model], rtol=1e-12, atol=0):
                raise ValueError('frozen historical model predictions changed')
    value = {'schema': 'BASS_R4V_FROZEN_G03_PREDICTIONS_V1',
             'source_pins': _pins(), 'baseline_samples': baseline,
             'frozen_models': frozen, 'signed48_queries': plan['queries'],
             'baseline_provenance': {
                 'path': str(models.DEFAULT_SAMPLES.relative_to(hp.REPO)),
                 'sha256': hp.sha(models.DEFAULT_SAMPLES),
                 'context': 'ARCHIVED_CXX_PHYSICAL_STATIC_EIGHT_POINT_BASELINE',
                 'same_context_as_new_fortran': False,
                 'comparison': 'same archived B0 physics, frozen model prediction versus fresh implementation',
                 'backend_bridge': 'R4U parity supports only the physically compared z32 query and resolutions; no universal backend equivalence claim'},
             'predeclared_analysis': plan['predeclared_analysis'],
             'scope': 'freeze before separately bound signed48 physical execution',
             **CEILINGS}
    hp.write_new(output_path, value)
    return value


def _load_lanes(manifest_paths, expected_times):
    """Read-only admission of completed caches; returns exact time->matrix map."""
    paths = [Path(p).resolve() for p in manifest_paths]
    if not paths or len(set(paths)) != len(paths):
        raise ValueError('nonempty distinct lane manifests required')
    expected_times = list(expected_times)
    if len(set(expected_times)) != len(expected_times):
        raise ValueError('expected time IDs are not unique')
    expected = set(expected_times)
    seen = set(); samples = {}; provenance = []; common = None
    for path in paths:
        m = read(path); context = m['context']; contract = context['qualification_contract']
        if m.get('schema') != 'BASS_R4U_PHYSICAL_EXECUTION_V1':
            raise ValueError('fresh execution manifest required')
        if context.get('backend') != 'fortran' or context.get('old_context_reuse') is not False:
            raise ValueError('fresh Fortran context without historical reuse required')
        fresh = hp.prepare_context(m['inputs'], m['build'], contract,
                                   backend=context['backend'], threads=context['threads'])
        if fresh != context:
            raise ValueError('fresh source/native/input context mismatch')
        if common is not None and context != common:
            raise ValueError('foreign context among lane manifests')
        common = context
        context_id = context['context_id']
        tasks = m['tasks']; times = [t['time_hex'] for t in tasks]
        if (not times or len(set(times)) != len(times) or seen.intersection(times)
                or not set(times) <= expected):
            raise ValueError('duplicate or foreign exact query time')
        if hp.build_tasks(context_id, [float.fromhex(t) for t in times], contract) != tasks:
            raise ValueError('task/context/ladder identity mismatch')
        maximum = m['limits']['max_attempts']
        if type(maximum) is not int or maximum != len(times)*len(contract['runtime_reference_resolutions']):
            raise ValueError('complete no-transfer per-lane attempt cap required')
        out = Path(m['output']).resolve(); cache = out/'cache'; manifest_sha = hp.sha(path)
        if hp.sha(out/'EXECUTION.json') != manifest_sha:
            raise ValueError('executed manifest bytes differ from analyzed manifest')
        admission = read(out/'ADMISSION.json')
        supervisor = read(out/'SUPERVISOR_RESULT.json')
        result = read(out/'RESULT.json'); queue = read(out/'queue/QUEUE_RECEIPT.json')
        receipt = read(cache/'CACHE_RECEIPT.json')
        if (admission.get('admitted') is not True
                or admission.get('execution_sha256') != manifest_sha
                or supervisor.get('success') is not True
                or supervisor.get('status') != 'EXITED' or supervisor.get('returncode') != 0
                or supervisor.get('execution_sha256') != manifest_sha
                or result.get('ok') is not True or result.get('execution_sha256') != manifest_sha
                or result.get('context_id') != context_id or result.get('cache') != receipt):
            raise ValueError('completed admission/supervisor/result chain required')
        if (queue.get('status') != 'COMPLETE' or queue.get('failure') is not None
                or queue.get('task_count') != len(times)
                or queue.get('canonical_prefix_count') != len(times)
                or queue.get('max_attempts') != maximum):
            raise ValueError('complete scoped queue receipt required')
        ids = {t['query_id'] for t in tasks}
        if ({p.stem for p in cache.glob('*.npz')} != ids
                or {p.stem for p in cache.glob('*.json') if p.name != 'CACHE_RECEIPT.json'} != ids):
            raise ValueError('cache has missing, orphan or foreign query files')
        records = []
        for t in tasks:
            item = hp.PlannedQuery(t['query_id'], t['time_hex'], None, None)
            record = hp.validate_pair(cache, item, context_id, contract)
            hp.validate_cached_cross_binding(cache, item.query_id)
            with np.load(cache/(item.query_id+'.npz'), allow_pickle=False) as payload:
                full = {k: np.array(payload['selected__'+k]) for k in ('S', 'H', 'D')}
            samples[item.time_hex] = {**full, 'cache': cache, 'item': item,
                                      'context_id': context_id, 'evidence': record}
            records.append(record)
        if (receipt.get('schema') != 'BASS_R4U_QUALIFIED_CACHE_V1'
                or receipt.get('context_id') != context_id
                or receipt.get('qualified_queries') != len(times)
                or receipt.get('records') != records
                or receipt.get('cache_payloads_digest') != hp.digest(records)
                or receipt.get('capture') is not False or receipt.get('continuous_bound') is not False):
            raise ValueError('qualified cache receipt differs from verified records')
        raw_count = sum(r['raw_attempts'] for r in records)
        if raw_count != queue.get('raw_attempts_reserved') or raw_count > maximum:
            raise ValueError('qualified evidence and consumed attempt count differ')
        seen.update(times)
        provenance.append({'manifest': str(path), 'manifest_sha256': manifest_sha,
                           'output': str(out), 'context_id': context_id,
                           'queries': len(times), 'raw_attempts': raw_count,
                           'cache_receipt_sha256': hp.sha(cache/'CACHE_RECEIPT.json'),
                           'supervisor_result_sha256': hp.sha(out/'SUPERVISOR_RESULT.json')})
    if seen != expected:
        raise ValueError('missing exact required query times')
    return samples, provenance, common


def analyze_g02(lane_manifest_paths, output_path):
    plan = _fixed(FD_PLAN, FD_PLAN_SHA)
    samples, provenance, context = _load_lanes(lane_manifest_paths,
                                             [q['time_hex'] for q in plan['queries']])
    by_z = {q['z_hex']: samples[q['time_hex']] for q in plan['queries']}
    results = []
    for z in plan['centers']:
        center = by_z[float(z).hex()]
        ladder = [(h, by_z[float(z-h).hex()]['S'], by_z[float(z+h).hex()]['S'])
                  for h in plan['h_ladder']]
        row = fd.compare_ladder(center['D'], ladder, plan['identity']['velocity_au'],
                                plan['acceptance']['relative_target'],
                                plan['acceptance']['absolute_target_atomic_time_inverse'])
        results.append({'z_a0': z, **row})
    report = {'schema': 'BASS_R4V_FRESH_G02_DIAGNOSTICS_V1',
              'status': 'ALL_FD_DIAGNOSTICS_PASS' if all(r['passed'] for r in results) else 'FD_VALIDATION_UNRESOLVED',
              'context_id': context['context_id'], 'source_pins': _pins(),
              'historical_plan_sha256': FD_PLAN_SHA, 'fresh_snapshot_count': len(samples),
              'historical_snapshot_reuse_count': 0, 'native_calls_for_run': sum(p['raw_attempts'] for p in provenance),
              'acceptance': plan['acceptance'], 'results': results, 'provenance': provenance,
              'coordinate_binding': [{'z_hex': q['z_hex'], 'time_hex': q['time_hex'],
                                      **samples[q['time_hex']]['evidence']} for q in plan['queries']],
              'physical_G02_closed': False,
              'closure_requires': 'independent review of actual physical FD evidence; finite stencil is not a certified operator-error bound',
              **CEILINGS}
    hp.write_new(output_path, report)
    return report


def analyze_g03(manifest_path, frozen_predictions_path, output_dir):
    frozen = read(frozen_predictions_path)
    plan = _fixed(G03_PLAN, G03_PLAN_SHA)
    baseline = models.load_samples(); recomputed = models.analyze(baseline)
    if frozen.get('schema') == 'BASS_R4V_FROZEN_G03_PREDICTIONS_V1':
        if (frozen.get('source_pins') != _pins()
                or frozen.get('baseline_samples') != baseline
                or frozen.get('signed48_queries') != plan['queries']
                or frozen.get('predeclared_analysis') != plan['predeclared_analysis']
                or frozen.get('frozen_models') != recomputed):
            raise ValueError('predeclared baseline/model/source binding changed')
        baseline_provenance = frozen['baseline_provenance']
    elif frozen.get('schema') == 'BASS_CR_G03_OFFLINE_MODELS_V1':
        # Root's already-predeclared record predates this adapter and contains
        # the complete unchanged model report plus explicit source byte pins.
        if (frozen.get('source_csv_sha256') != hp.sha(models.DEFAULT_SAMPLES)
                or frozen.get('analyzer_sha256') != hp.sha(models.__file__)
                or frozen.get('purpose') != 'FROZEN_BEFORE_ANY_R4V_PHYSICAL_CALL'
                or {k:v for k,v in frozen.items() if k not in
                    ('source_csv_sha256','analyzer_sha256','purpose')} != recomputed):
            raise ValueError('predeclared baseline/model/source binding changed')
        baseline_provenance = {
            'path': str(models.DEFAULT_SAMPLES.relative_to(hp.REPO)),
            'sha256': hp.sha(models.DEFAULT_SAMPLES),
            'context': 'ARCHIVED_CXX_PHYSICAL_STATIC_EIGHT_POINT_BASELINE',
            'same_context_as_new_fortran': False,
            'comparison': 'same archived B0 physics; historical frozen prediction and fresh Fortran holdout',
            'backend_bridge': 'R4U physical parity is limited to actually checked z32 query and resolutions',
            'backend_bridge_receipt_sha256': hp.sha(GAP/'production_solver_20261001/evidence/PHYSICAL_PARITY.json')}
    else:
        raise ValueError('recognized predeclared G03 record required')
    samples, provenance, context = _load_lanes([manifest_path],
                                             [q['time_hex'] for q in plan['queries']])
    output = Path(output_dir)
    # No output is created until every source, context and cache has passed.
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for q in plan['queries']:
        item = samples[q['time_hex']]
        rows.append(rates.analyze_query(item['cache'], item['item'], q, output/'rates'))
    scored = models.evaluate_return(baseline, {'samples': rows})
    report = {'schema': 'BASS_R4V_FRESH_G03_DIAGNOSTICS_V1',
              'status': 'SIGNED48_PHYSICAL_HOLDOUT_SCORED', 'context_id': context['context_id'],
              'frozen_prediction_sha256': hp.sha(frozen_predictions_path),
              'baseline_provenance': baseline_provenance,
              'source_pins': _pins(), 'provenance': provenance, 'samples': rows,
              'frozen_holdout_analysis': scored,
              'native_calls_for_run': sum(p['raw_attempts'] for p in provenance),
              'physical_G03_closed': False,
              'Sdot_source': 'ASSUMED_D_PLUS_D_DAGGER; G02 evidence remains separately reported',
              'automatic_followup_authorized': False, **CEILINGS}
    hp.write_new(output/'G03_RESULT.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    p = sub.add_parser('g02'); p.add_argument('--manifests', nargs='+', required=True); p.add_argument('--output', required=True)
    p = sub.add_parser('freeze-g03'); p.add_argument('--output', required=True)
    p = sub.add_parser('g03'); p.add_argument('--manifest', required=True); p.add_argument('--frozen', required=True); p.add_argument('--output', required=True)
    args = parser.parse_args()
    if args.mode == 'g02': result = analyze_g02(args.manifests, args.output)
    elif args.mode == 'freeze-g03': result = freeze_g03_predictions(args.output)
    else: result = analyze_g03(args.manifest, args.frozen, args.output)
    print(json.dumps({'status': result.get('status', result['schema']), 'output': args.output,
                      'new_native_calls_in_analysis': 0}))


if __name__ == '__main__':
    main()
