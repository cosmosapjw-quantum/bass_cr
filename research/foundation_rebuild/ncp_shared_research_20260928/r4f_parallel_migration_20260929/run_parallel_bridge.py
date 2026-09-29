#!/usr/bin/env python3
"""One approved cache-preserving N768 migration after the serial parent stops."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
import traceback

import numpy as np

HERE = Path(__file__).resolve().parent
R4C = HERE.parent/'r4c_temporal_continuation'
for directory in (HERE, R4C):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
import continue_temporal as serial
from execution_admission import (ARCHIVE_SHA256, MAX_RAW_ATTEMPTS, THREAD_KEYS,
                                 check_native_build, strict_json)
from parallel_bridge import (CacheOnlyProvider, GlobalBudget, InvalidPair,
                             PlannedQuery, dispatch_bounded, import_parent_extra,
                             plan_queries, publish_pair, select_missing,
                             validate_pair)
from worker_runtime import compute_query, initialize_worker

PARENT_COMMIT = '4c2c0be5171c74a52b4a6e96b04c33fa00c62481'
PARENT_TREE = '2e1a3175a7d20cf9c0218fb15f07f72d4afcb425'
CONTEXT_ID = 'bb2a6d2cb7b598441e44294ae9d9499e983f6bfebe9ec4dcfdbc29b9ac7f1cda'
D384_REF = 2.6345608772805691e-6
D192_384 = 7.9047694323699088e-6
_STOP = False


def _signal(signum, frame):
    global _STOP
    _STOP = True
    raise InterruptedError('migration coordinator received signal ' + str(signum))


def _sha(path: Path) -> str:
    return serial.sha256_path(path)


def _write(path: Path, value) -> None:
    serial.write_new(path, value)


def _identity(args) -> dict:
    if os.environ.get('ALLOW_NEW_NATIVE_R4F') != 'YES_I_AUTHORIZE_MIGRATION':
        raise PermissionError('R4F_NATIVE_MIGRATION_NOT_AUTHORIZED')
    head, tree = serial.git_identity()
    if not head or args.expected_commit != head or args.expected_tree != tree:
        raise ValueError('new execution commit/tree mismatch')
    if subprocess.check_output(['git','-C',str(serial.REPO),'status','--porcelain','--untracked-files=all'],text=True):
        raise ValueError('new execution worktree must be clean')
    if Path(args.out).resolve().is_relative_to(serial.REPO):
        raise ValueError('migration output must be outside source worktree')
    import scipy
    if (not sys.flags.isolated or sys.version_info < (3,11)
        or np.__version__ != '2.3.5' or scipy.__version__ != '1.17.0'):
        raise ValueError('pinned isolated Python/numerical environment required')
    if any(os.environ.get(k) != '1' for k in THREAD_KEYS):
        raise ValueError('all four thread limits must be one before Python starts')
    if args.expected_resume_sha256 != ARCHIVE_SHA256:
        raise ValueError('original source archive identity mismatch')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{15,95}', args.authorization_id):
        raise PermissionError('explicit new migration authorization ID required')
    if args.authorization_id == args.parent_authorization_id:
        raise PermissionError('parent authorization ID cannot be reused')
    if args.parity_count != 2 or not 1 <= args.workers <= 8 or not 4 <= args.pilot_queries <= 8:
        raise ValueError('migration worker/parity/pilot bounds exceeded')
    cpus = [int(x) for x in args.cpus.split(',')]
    if len(cpus) != len(set(cpus)) or len(cpus) < args.workers or not set(cpus).issubset(os.sched_getaffinity(0)):
        raise ValueError('approved CPUs unavailable')
    if args.worker_ram_bytes < 512*1024*1024:
        raise ValueError('approved worker RAM too small')
    if not math.isfinite(args.deadline_unix) or time.time() >= args.deadline_unix:
        raise ValueError('migration deadline expired')
    return {'schema':'BASS_R4F_EXECUTION_ADMISSION_V1',
            'execution_commit':head,'execution_tree':tree,
            'base_serial_commit':PARENT_COMMIT,'base_serial_tree':PARENT_TREE,
            'original_archive_sha256':ARCHIVE_SHA256,
            'authorization_id':args.authorization_id,
            'parent_authorization_id':args.parent_authorization_id,
            'deadline_unix':args.deadline_unix,'workers':args.workers,
            'pilot_queries':args.pilot_queries,'parity_count':2,
            'cpus':cpus,'worker_ram_bytes':args.worker_ram_bytes,
            'global_raw_attempt_cap':MAX_RAW_ATTEMPTS,
            'cost_scope':args.cost_scope,
            'cost_limit_enforced_by_code':False,
            'python':sys.version,'executable':sys.executable,
            'numpy':np.__version__,'scipy':scipy.__version__,
            'threads':{k:os.environ[k] for k in THREAD_KEYS}}


def _parent_receipt(parent_out: Path, parent_id: str, migration_id: str,
                    stop_receipt: Path, deadline: float) -> dict:
    admission = strict_json(parent_out/'EXECUTION_ADMISSION.json')
    consumed = strict_json(parent_out/'AUTHORIZATION_CONSUMED.json')
    stopped = strict_json(stop_receipt)
    if (admission.get('authorization_id') != parent_id
        or consumed.get('authorization_id') != parent_id
        or admission.get('execution_head') != PARENT_COMMIT
        or admission.get('execution_tree') != PARENT_TREE
        or admission.get('source_archive_sha256') != ARCHIVE_SHA256
        or consumed.get('state') != 'CONSUMED_BEFORE_NATIVE_LOAD'
        or Path(consumed.get('out','')).resolve() != parent_out.resolve()
        or stopped.get('python_pid') != consumed.get('pid')
        or stopped.get('parent_authorization_id') != parent_id
        or stopped.get('migration_authorization_id') != migration_id
        or stopped.get('child_exited') is not True
        or stopped.get('supervisor_exited') is not True
        or stopped.get('classification') != 'PLANNED_SERIAL_TO_PARALLEL_MIGRATION'):
        raise ValueError('stopped parent lineage is incomplete')
    started_file=parent_out.parent/'START_UTC.txt'
    started_unix=datetime.fromisoformat(started_file.read_text().strip().replace('Z','+00:00')).timestamp()
    if deadline > started_unix + admission['max_wall_seconds']:
        raise ValueError('migration deadline exceeds parent approved wall envelope')
    if (Path('/proc')/str(consumed['pid'])).exists():
        raise ValueError('parent Python PID still exists')
    if admission['max_raw_attempts'] != MAX_RAW_ATTEMPTS:
        raise ValueError('parent raw attempt cap mismatch')
    raw_path = parent_out/'RAW_EVALUATION_LEDGER.jsonl'
    starts = 0
    for line in raw_path.read_text().splitlines():
        row = json.loads(line)
        if row.get('event') == 'attempt_started': starts += 1
    return {'schema':'BASS_R4F_PARENT_LINEAGE_V1',
            'authorization_id':parent_id,'admission_sha256':_sha(parent_out/'EXECUTION_ADMISSION.json'),
            'consumed_sha256':_sha(parent_out/'AUTHORIZATION_CONSUMED.json'),
            'stop_receipt_sha256':_sha(stop_receipt),
            'parent_raw_attempts':starts,
            'parent_started_unix':started_unix,
            'parent_deadline_unix':started_unix+admission['max_wall_seconds'],
            'parent_out':str(parent_out.resolve())}


def _freeze_parent(parent_out: Path, destination: Path) -> dict:
    root=parent_out.parent
    files = {}
    for p in sorted(root.rglob('*')):
        if p.is_file():
            rel = str(p.relative_to(root))
            files[rel] = {'bytes':p.stat().st_size,'sha256':_sha(p)}
    result = {'schema':'BASS_R4F_FROZEN_PARENT_MANIFEST_V1',
              'parent_run_root':str(root.resolve()),'files':files}
    _write(destination, result)
    return result


def _assert_frozen(parent_out: Path, manifest: dict) -> None:
    root=parent_out.parent
    current={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    if current != set(manifest['files']):
        raise ValueError('parent file membership changed after freeze')
    for rel, record in manifest['files'].items():
        path = root/rel
        if not path.is_file() or path.stat().st_size != record['bytes'] or _sha(path) != record['sha256']:
            raise ValueError('parent changed after freeze: ' + rel)


def _base_pairs(source: Path, context_id: str, contract: dict) -> list[PlannedQuery]:
    result = []
    for jp in sorted((source/'runtime_queries').glob('*.json')):
        rec = strict_json(jp)
        item = PlannedQuery(jp.stem, rec['time_hex'], None, None)
        validate_pair(jp.parent, item, context_id, contract)
        result.append(item)
    if len(result) != 1279:
        raise ValueError('frozen archive query count changed')
    return result


def _compare_parity(base: Path, task: Path, item: PlannedQuery,
                    context_id: str, contract: dict) -> dict:
    import numpy as np
    old = validate_pair(base, item, context_id, contract)
    new = validate_pair(task/'runtime_queries', item, context_id, contract)
    old_rec = strict_json(base/(item.query_id+'.json'))
    new_rec = strict_json(task/'runtime_queries'/(item.query_id+'.json'))
    if (old_rec['qualification']['selected_resolution'] != new_rec['qualification']['selected_resolution']
        or old_rec['qualification']['lower_resolution'] != new_rec['qualification']['lower_resolution']):
        raise ValueError('native parity selected resolution mismatch')
    maxdiff = 0.0
    with np.load(base/(item.query_id+'.npz'),allow_pickle=False) as left, np.load(task/'runtime_queries'/(item.query_id+'.npz'),allow_pickle=False) as right:
        if set(left.files) != set(right.files):
            raise ValueError('native parity payload keys mismatch')
        for key in left.files:
            a=np.asarray(left[key]);b=np.asarray(right[key])
            if a.shape != b.shape:
                raise ValueError('native parity payload shape mismatch')
            d=float(np.linalg.norm(a-b)/max(float(np.linalg.norm(a)),float(np.linalg.norm(b)),1e-300))
            if not np.isfinite(d) or d > 2e-12:
                raise ValueError('native parity operator mismatch: '+key)
            maxdiff=max(maxdiff,d)
    return {'query_id':item.query_id,'old':old,'new':new,'max_payload_relative_difference':maxdiff}


def _run_pool(items: list[PlannedQuery], source: Path, args, contract: dict,
              context_id: str, budget: GlobalBudget, out: Path,
              canonical: Path, workers: int, *, parity: bool = False) -> dict:
    if not items:
        return {}
    state = multiprocessing.get_context('spawn')
    with ProcessPoolExecutor(max_workers=workers, mp_context=state,
            initializer=initialize_worker,
            initargs=(str(source),args.analytic_build,contract,context_id,
                      str(budget.root),str(out/'worker_tasks'),
                      [int(x) for x in args.cpus.split(',')],args.worker_ram_bytes)) as pool:
        def on_result(item, receipt):
            task = Path(receipt['task_dir'])
            if receipt['query_id'] != item.query_id or receipt['raw_attempts'] > len(contract['runtime_reference_resolutions']):
                raise ValueError('worker task identity or raw bound mismatch')
            if parity:
                proof = _compare_parity(source/'runtime_queries',task,item,context_id,contract)
                _write(task/'PARITY_RESULT.json',proof)
            else:
                publish_pair(task/'runtime_queries',canonical,item,context_id,contract)
        try:
            return dispatch_bounded(items,pool,compute_query,on_result,
                                    max_inflight=workers,deadline_unix=args.deadline_unix,
                                    cancelled=lambda:_STOP)
        except BaseException as exc:
            try: budget.cancel(type(exc).__name__ + ': ' + str(exc))
            except FileExistsError: pass
            raise


def _science(args, out: Path, admission: dict) -> dict:
    import continue_temporal as serial
    from cr_repro.observables import projectile_speed_au
    from metric_transport import run_candidate, phase_aligned_metric_distance
    from transport_policy import assess_temporal_pair

    parent_out = Path(args.parent_out).resolve()
    lineage = _parent_receipt(parent_out,args.parent_authorization_id,args.authorization_id,
                              Path(args.stop_receipt),args.deadline_unix)
    _write(out/'PARENT_LINEAGE.json',lineage)
    serial.copy_new(Path(args.stop_receipt),out/'STOP_RECEIPT.json')
    loss=Path(args.stop_receipt).with_name(Path(args.stop_receipt).stem+'_LOSS_LEDGER.json')
    if loss.is_file():
        serial.copy_new(loss,out/'LOSS_LEDGER.json')
    for rel, target in (('RETURN_REPORT.json','PARENT_RETURN_REPORT.json'),
                        ('failure.traceback.txt','PARENT_FAILURE_TRACEBACK.txt')):
        if (parent_out/rel).is_file():
            serial.copy_new(parent_out/rel,out/target)
    frozen = _freeze_parent(parent_out,out/'FROZEN_PARENT_MANIFEST.json')
    deps = serial.verify_pinned_dependencies()
    _write(out/'PINNED_NUMERICAL_DEPENDENCIES.json',deps)

    with tempfile.TemporaryDirectory(prefix='bass_r4f_original_') as temp:
        source = Path(temp)
        archive = serial.extract_validated_archive(Path(args.resume_archive),
                                                   args.expected_resume_sha256,source)
        info = serial.validate_source(source,384,768)
        if info['context_id'] != CONTEXT_ID or archive['bytes'] != 31849212:
            raise ValueError('frozen original archive/context mismatch')
        contract = info['contract'];context_id=info['context_id']
        native = check_native_build(Path(args.analytic_build),contract,
                                    serial.ANALYTIC/'moment_kernel.cpp')
        _write(out/'NATIVE_PRELOAD_CHECK.json',native)
        base_items = _base_pairs(source,context_id,contract)
        velocity = projectile_speed_au(contract['energy_keV_per_u'])
        t0=contract['z_initial_a0']/velocity;tf=contract['z_final_a0']/velocity
        required=plan_queries(context_id,t0,tf)
        base_ids={x.query_id for x in base_items}
        if len({x.query_id for x in required}&base_ids)!=2:
            raise ValueError('required/base exact-hit count mismatch')
        canonical=out/'runtime_queries'
        serial.restore_query_store(source,out,context_id)
        bridge=import_parent_extra(parent_out/'runtime_queries',source/'runtime_queries',
                                   canonical,required,context_id,contract)
        quarantine=out/'parent_quarantine'
        for qid in bridge['orphan_ids']:
            for ext in ('.json','.npz'):
                path=parent_out/'runtime_queries'/(qid+ext)
                if path.is_file():
                    serial.copy_new(path,quarantine/path.name)
        for path in (parent_out/'runtime_queries').glob('.partial_*'):
            if path.is_file():
                serial.copy_new(path,quarantine/path.name)
        bridge.update({'parent_manifest_sha256':_sha(out/'FROZEN_PARENT_MANIFEST.json'),
                       'base_archive_sha256':ARCHIVE_SHA256,
                       'parent_authorization_id':args.parent_authorization_id})
        _write(out/'IMPORT_BRIDGE.json',bridge)
        _assert_frozen(parent_out,frozen)
        present=base_ids|set(bridge['imported_ids'])
        missing=[item for _,item in select_missing(required,present)]
        _write(out/'REQUIRED_MISSING_QUERY_PLAN.json',{
            'schema':'BASS_R4F_REQUIRED_QUERY_PLAN_V1',
            'required':[x.__dict__ for x in required],
            'base_required_hits':2,'parent_extra_hits':len(bridge['imported_ids']),
            'missing_ids':[x.query_id for x in missing]})

        # The authorization is durable before the first native worker can load.
        authroot=Path.home()/'.local/state/bass_r4f/authorizations'
        authroot.mkdir(parents=True,exist_ok=True)
        auth={**admission,'out':str(out),'state':'CONSUMED_BEFORE_NATIVE_WORKERS',
              'created_unix_seconds':time.time()}
        _write(authroot/(args.authorization_id+'.json'),auth)
        _write(out/'AUTHORIZATION_CONSUMED.json',auth)
        budget=GlobalBudget.create(out/'global_budget',
                                   parent_attempts=lineage['parent_raw_attempts'],
                                   maximum=MAX_RAW_ATTEMPTS,
                                   deadline_unix=args.deadline_unix)
        tasks=out/'worker_tasks';tasks.mkdir()
        parity_items=[required[0],required[-1]]
        parity_receipts=_run_pool(parity_items,source,args,contract,context_id,
                                  budget,out,canonical,min(2,args.workers),parity=True)
        _write(out/'NATIVE_PARITY_AUDIT.json',{
            'schema':'BASS_R4F_NATIVE_PARITY_V1',
            'query_ids':[x.query_id for x in parity_items],
            'maximum_raw_attempts':2*len(contract['runtime_reference_resolutions']),
            'receipts':list(parity_receipts.values())})

        pilot=missing[:args.pilot_queries]
        _run_pool(pilot,source,args,contract,context_id,budget,out,canonical,
                  min(4,args.workers))
        _write(out/'PILOT_AUDIT.json',{'schema':'BASS_R4F_PILOT_V1',
                                     'query_ids':[x.query_id for x in pilot],
                                     'worker_cap':min(4,args.workers),
                                     'raw_used_after_pilot':budget.used()})
        _run_pool(missing[len(pilot):],source,args,contract,context_id,
                  budget,out,canonical,args.workers)
        all_valid={x.query_id for x in required
                   if (canonical/(x.query_id+'.json')).is_file()
                   and (canonical/(x.query_id+'.npz')).is_file()}
        if len(all_valid)!=770:
            raise ValueError('CACHE_MISS before replay')
        for item in required:
            validate_pair(canonical,item,context_id,contract)
        _write(out/'CACHE_COVERAGE_AUDIT.json',{
            'schema':'BASS_R4F_CACHE_COVERAGE_V1','required':770,
            'verified':770,'new_native_queries':len(missing),
            'global_raw_attempts_used':budget.used()})

        for rel in ('BASIS.json','BASIS.npz','SCIENCE_CONTEXT.json',
                    'REFERENCE_STATES.npz','REFERENCE_RECEIPT.json',
                    'METRIC_CONNECTION.json','CANDIDATE_N384.json',
                    'CANDIDATE_N384.npz'):
            serial.copy_new(source/rel,out/rel)
        with np.load(source/'REFERENCE_STATES.npz',allow_pickle=False) as f:
            reference_final=np.array(f['final_state'])
        previous=info['previous_candidate']
        provider=CacheOnlyProvider(canonical,context_id,contract['screens'],
                                   {x.query_id for x in required})
        current=run_candidate(provider,previous.initial_state,t0,tf,768)
        if provider.reads != 770 or provider.native_calls != 0:
            raise ValueError('cache-only replay audit mismatch')
        sf=provider.at(tf).S
        dprevious=phase_aligned_metric_distance(previous.final_state,reference_final,sf)
        pair=assess_temporal_pair(previous,current,reference_final,sf,
                                  phase_aligned_metric_distance,contract['screens'])
        dref=pair['candidate_reference_metric_distance'];dself=pair['candidate_refinement_metric_distance']
        tolerance=1e-12
        if (not math.isclose(dprevious,D384_REF,rel_tol=0,abs_tol=tolerance)
            or D384_REF > dref+dself+tolerance
            or pair['reference_pass'] and pair['refinement_pass']):
            raise ValueError('METRIC_OR_EVIDENCE_INCONSISTENCY')
        if not pair['previous_norm_pass'] or not pair['selected_norm_pass']:
            raise ValueError('N768_NORM_QUALIFICATION_FAILURE')
        np.savez_compressed(out/'CANDIDATE_N768.npz',initial_state=current.initial_state,
                            final_state=current.final_state,norm_history=current.norm_history)
        _write(out/'CANDIDATE_N768.json',{'nstep':768,'dt':float(current.dt),
               'max_norm_drift':float(current.max_norm_drift),
               'max_generator_defect':float(current.max_generator_defect)})
        _write(out/'TEMPORAL_PAIR_N384_N768.json',pair)
        audit={'schema':'BASS_R4F_CACHE_ONLY_REPLAY_AUDIT_V1',
               'required_query_count':770,'cache_reads':provider.reads,
               'native_operator_calls':provider.native_calls,
               'original_initial_state_used':True,'d384_reference':dprevious,
               'triangle_tolerance':tolerance}
        _write(out/'CACHE_ONLY_REPLAY_AUDIT.json',audit)
        _write(out/'PROVIDER_AUDIT.json',{
            'schema':'BASS_R4F_PROVIDER_AUDIT_V1',
            'all_runtime_operator_queries_qualified':True,
            'required_runtime_queries':770,
            'base_exact_hits':2,
            'parent_extra_cache_hits':len(bridge['imported_ids']),
            'new_unique_query_times':len(missing),
            'cache_only_reads':provider.reads,'cache_hits':provider.cache_hits,
            'replay_native_calls':provider.native_calls,
            'global_raw_attempts_used':budget.used()})
        diagnostics={}
        if dref>0 and dself>0 and np.isfinite((dref,dself)).all():
            diagnostics={'p_ref':math.log2(D384_REF/dref),
                         'p_self':math.log2(D192_384/dself),
                         'd_ref_pred_1536':dref*dref/D384_REF,
                         'd_self_pred_1536':dself*dself/D192_384}
        _write(out/'SCHEDULING_DIAGNOSTICS.json',diagnostics)
        return {'status':'R4E_N768_BRIDGE_COMPLETE__N1536_DECISION_PENDING',
                'pair':pair,'candidate_norm_drift':current.max_norm_drift,
                'previous_norm_drift':previous.max_norm_drift,
                'operator_queries_qualified':770,
                'parent_extra_cache_hits':len(bridge['imported_ids']),
                'base_exact_hits':2,'new_unique_query_times':len(missing),
                'global_raw_attempts_used':budget.used(),
                'cache_only_replay':audit,'scheduling_diagnostics':diagnostics,
                'source_archive':archive}


def parse_args(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True)
    p.add_argument('--resume-archive',required=True)
    p.add_argument('--expected-resume-sha256',required=True)
    p.add_argument('--parent-out',required=True)
    p.add_argument('--stop-receipt',required=True)
    p.add_argument('--parent-authorization-id',required=True)
    p.add_argument('--authorization-id',required=True)
    p.add_argument('--expected-commit',required=True)
    p.add_argument('--expected-tree',required=True)
    p.add_argument('--analytic-build',required=True)
    p.add_argument('--deadline-unix',type=float,required=True)
    p.add_argument('--workers',type=int,required=True)
    p.add_argument('--pilot-queries',type=int,default=8)
    p.add_argument('--parity-count',type=int,default=2)
    p.add_argument('--cpus',required=True)
    p.add_argument('--worker-ram-bytes',type=int,required=True)
    p.add_argument('--cost-scope',required=True)
    return p.parse_args(argv)


def main(argv=None) -> int:
    args=parse_args(argv)
    out=Path(args.out).resolve()
    if out.exists() or out.with_name(out.name+'_RETURN.zip').exists():
        print('OUTPUT_EXISTS',file=sys.stderr);return 3
    admission=_identity(args)
    out.mkdir(parents=True)
    _write(out/'EXECUTION_ADMISSION.json',admission)
    signal.signal(signal.SIGTERM,_signal)
    start=time.monotonic();code=0
    report={'schema':'BASS_R4F_PARALLEL_BRIDGE_RETURN_V1','status':'IN_PROGRESS',
            **serial.CLAIM_CEILING,'capture_run_performed':False,
            'b_grid_run_performed':False,'full_window_transport_qualified':False,
            'execution_head':admission['execution_commit'],
            'execution_tree':admission['execution_tree']}
    try:
        result=_science(args,out,admission)
        report.update(result)
    except BaseException as exc:
        code=2
        report['status']=(str(exc) if str(exc) in ('METRIC_OR_EVIDENCE_INCONSISTENCY',
                             'N768_NORM_QUALIFICATION_FAILURE') else 'R4F_MIGRATION_BLOCKED')
        report['first_failure']={'type':type(exc).__name__,'message':str(exc)}
        with (out/'failure.traceback.txt').open('x') as f:
            f.write(traceback.format_exc())
    report['wall_seconds']=time.monotonic()-start
    _write(out/'RETURN_REPORT.json',report)
    print(json.dumps({'status':report['status'],'report':str(out/'RETURN_REPORT.json'),
                      'exit_code':code},indent=2))
    return code


if __name__=='__main__':
    raise SystemExit(main())
