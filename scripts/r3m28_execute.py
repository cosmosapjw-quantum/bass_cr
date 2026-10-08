#!/usr/bin/env python3
"""A3-only coordinator for the preregistered same-dt spatial discriminator."""
from __future__ import annotations

import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import time
import traceback

from cr_repro.r3m11 import source_digest
from scripts import r3m27_b3_execute as base
from scripts import r3m17_checkpoint_guard as guard
from scripts.r3m17_preflight import numerical_metadata

ROOT = Path(__file__).resolve().parents[1]
PARENT = '1ff87bf27a18fd0acfe8cffe788ae07deac7650a'
SOURCE = base.SOURCE
CONFIG = ROOT / 'configs/r3m28/A3.json'
A1_CONFIG = ROOT / 'configs/r3m16/A1.json'
A1_CONFIG_SHA = 'af90d1c60f8c4c63ed309261945d441d86ebe095bb4a556385aade81a56830aa'
A1_RESULT = ROOT / 'results/R3M16/collisions/A1_result.json'
A1_RESULT_SHA = 'c2f19c93020f11e9e56e1045f733201de826043aaf6928a74a7871d154e0c775'
B1_RESULT = ROOT / 'results/R3M16/collisions/B1_result.json'
B1_RESULT_SHA = 'ae4f70261f866a601a51a80c5d00a1fde1394644c3808558e91519bbf124f11f'
B3_RESULT = ROOT / 'results/R3M27/B3_TEMPORAL_EVALUATION.json'
B3_RESULT_SHA = '8ead001d4a0cb45f92f82ae9722ad96b420dff80b1325d29124f39eaeb7529dc'
DESIGN = ROOT / 'results/R3M28/DESIGN.json'
A1_INITIAL = Path('/mnt/sn850x2t/bass_cr_r3m16_20260922/A1/preparation/initial.npy')
INITIAL_SHA = '08595a1a42900da0a86f0401d28e98f79c0663524a8222d3c51756223a13ee8e'
STATE_BYTES = 516_096_128
NSTEP = 7172
CHUNKS = 57
SOURCE_PATHS = (
    'scripts/r3m28_execute.py', 'tests/test_r3m28_execute.py',
    'scripts/r3m28_spatial.py', 'tests/test_r3m28_spatial.py',
    'scripts/r3m27_b3_execute.py', 'scripts/r3m14_collision_initial_witness.py',
    'scripts/r3m17_checkpoint_guard.py', 'scripts/r3m13_initial_state_pair.py',
    'scripts/r3m15_resource_probe.py', 'configs/r3m28/A3.json',
)


def validate_config(cfg: dict) -> dict:
    if base.sha(A1_CONFIG) != A1_CONFIG_SHA:
        raise ValueError('frozen A1 config changed')
    expected = base.read(A1_CONFIG)
    expected['dt'] = .00625
    if cfg != expected or type(cfg.get('dt')) is not float:
        raise ValueError('A3 must equal frozen A1 except requested dt=.00625')
    if source_digest() != SOURCE:
        raise ValueError('frozen numerical source digest changed')
    numerical = numerical_metadata(cfg)
    if (numerical['grid_shape'] != [280, 240, 480] or
            numerical['nstep'] != NSTEP or numerical['chunk_count'] != CHUNKS or
            numerical['last_chunk_steps'] != 4 or
            not math.isclose(numerical['actual_dt'], .00624946176119497,
                             rel_tol=0, abs_tol=1e-16) or
            not math.isclose(numerical['physical_horizon_au'], 44.821139751290325,
                             rel_tol=0, abs_tol=1e-11)):
        raise ValueError('A3 physical horizon, dt or geometry changed')
    return numerical


def build_plan(config: Path, output_root: Path) -> dict:
    config, output_root = Path(config).absolute(), Path(output_root).absolute()
    if config != CONFIG or output_root == ROOT or ROOT in output_root.parents:
        raise ValueError('canonical A3 config and external output root required')
    cfg = base.read(config)
    numerical = validate_config(cfg)
    pins = ((A1_RESULT, A1_RESULT_SHA), (B1_RESULT, B1_RESULT_SHA),
            (B3_RESULT, B3_RESULT_SHA), (A1_INITIAL, INITIAL_SHA))
    for path, digest in pins:
        if base.sha(path) != digest:
            raise ValueError(f'preregistered input bytes changed: {path}')
    design = base.read(DESIGN)
    if (design.get('schema') != 'R3M28_SPATIAL_HDT_DESIGN_V1' or
            design.get('created_before_A3') is not True or
            design.get('A3_config_sha256') != base.sha(config) or
            design.get('spatial_pair_screen_relative') != .003 or
            design.get('A3_initial_reference_sha256') != INITIAL_SHA):
        raise ValueError('spatial design differs from preregistration')
    head = base.git('rev-parse', 'HEAD')
    if (base.git('branch', '--show-current') != 'cr/r3m28-spatial-hdt-budget-20260924' or
            base.git('merge-base', PARENT, head) != PARENT or head == PARENT):
        raise ValueError('committed R3M28 descendant branch required')
    return dict(schema='BASS_CR_R3M28_A3_CONTRACT_V1',
        canonical_node='N1_TDL_PRODUCTION_H_SPATIAL_H_DT_BUDGET',
        hypothesis='One same-horizon A3 point discriminates the spatial .30% pair screen and raw h-dt interaction.',
        source_commit=head, parent_commit=PARENT, source_digest=SOURCE,
        source_hashes={name: base.sha(ROOT/name) for name in SOURCE_PATHS},
        config=cfg, config_path=str(config), config_sha256=base.sha(config),
        design_sha256=base.sha(DESIGN), numerical=numerical,
        input_hashes={str(path): digest for path, digest in pins},
        runtime=base.runtime_identity(), output_root=str(output_root),
        commands=base.command_plan(config, output_root),
        resource_caps=dict(base_plan_disk_required_free_bytes=base.DISK_REQUIRED,
            disk_remaining_floor_bytes=base.DISK_REMAIN,
            gpu_free_reserve_bytes=base.GPU_RESERVE,
            host_available_reserve_bytes=base.HOST_RESERVE,
            max_total_seconds=base.TOTAL_SECONDS,
            command_seconds_cap=base.COMMAND_SECONDS,
            cpu_workers=1, state_bytes=STATE_BYTES,
            retained_generations=CHUNKS,
            generation_state_bytes=STATE_BYTES*CHUNKS),
        spatial_pair_screen_relative=.003,
        pair_screen_is_validated_error_estimate=False,
        h_dt_raw_interaction_counted_as_error_estimate=False,
        new_full_collision_limit=1, exact_preparation_limit=1,
        automatic_retry=False, production_admission=False)


def validate_plan(plan: dict) -> None:
    expected = build_plan(Path(plan['config_path']), Path(plan['output_root']))
    frozen_head = plan.get('source_commit')
    current_head = expected['source_commit']
    if (not isinstance(frozen_head, str) or
            (frozen_head != current_head and
             base.git('merge-base', frozen_head, current_head) != frozen_head)):
        raise ValueError('A3 source commit is not an ancestor of current checkout')
    # Delivery commits may follow the frozen source commit. Exact source hashes
    # still reject code changes; they need not invalidate a result-only commit.
    expected['source_commit'] = frozen_head
    if json.dumps(plan, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
        raise ValueError('A3 config/argv/source/runtime/resource contract mismatch')


def _prepared(root: Path, cfg: dict) -> dict:
    from scripts.r3m14_collision_initial_witness import validate_prepared
    prepared = validate_prepared(root/'preparation', cfg, SOURCE)
    if (prepared['state_file_sha256'] != INITIAL_SHA or
            prepared['receipt']['config'] != cfg):
        raise ValueError('fresh A3 preparation differs from A1 canonical initial/config')
    return prepared


def execute(contract: Path, approval: str, *, explicit_resume: bool = False) -> dict:
    contract = Path(contract).absolute()
    if base.sha(contract) != approval:
        raise ValueError('explicit A3 contract SHA approval mismatch')
    plan = base.read(contract)
    validate_plan(plan)
    root = Path(plan['output_root'])
    if root.exists() and not explicit_resume:
        raise FileExistsError('fresh A3 output required')
    if not root.exists():
        root.mkdir(parents=True, exist_ok=False)
        base.publish(root/'RUN.json', dict(contract_sha256=approval,
            source_commit=plan['source_commit'], new_full_collisions=1,
            automatic_retry=False, production_admission=False))
    elif base.read(root/'RUN.json')['contract_sha256'] != approval:
        raise ValueError('resume contract SHA mismatch')
    (root/'receipts').mkdir(exist_ok=True)
    (root/'generations').mkdir(exist_ok=True)
    started = time.monotonic()
    stage = 'RESOURCE_PREFLIGHT'
    with (root/'gpu.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            if (root/'COMPLETE.json').exists():
                raise FileExistsError('completed A3 must not rerun')
            if not (root/'RESOURCE_INVENTORY.json').exists():
                base.publish(root/'RESOURCE_INVENTORY.json', base.resources(root))
            else:
                base.resources(root)
            if not (root/'resource.json').exists():
                base._command('resource_preflight', plan['commands'][0], root, started)
            if not (root/'receipts/resource_preflight.json').is_file():
                raise ValueError('resource output without completed command receipt')
            if base.read(root/'resource.json').get('status') != 'PASS_RESOURCE_PREFLIGHT':
                raise ValueError('FFT resource preflight did not pass')
            stage = 'PREPARATION'
            if not (root/'preparation').exists():
                base._command('prepare', plan['commands'][1], root, started)
            if not (root/'receipts/prepare.json').is_file():
                raise ValueError('preparation output without completed command receipt')
            prepared = _prepared(root, plan['config'])
            if not (root/'PREPARATION_BINDING.json').exists():
                base.publish(root/'PREPARATION_BINDING.json', dict(
                    status='PASS_EXACT_A3_CONFIG_AND_A1_CANONICAL_INITIAL',
                    receipt_sha256=prepared['receipt_sha256'],
                    initial_sha256=prepared['state_file_sha256'],
                    seconds=prepared['receipt']['seconds'],
                    internal_preparation_expected_once_on_first_collision_chunk=True))
            commands = plan['commands'][2:]
            for i in range(CHUNKS):
                collision, snapshot = commands[2*i:2*i+2]
                chunk, expected = i+1, snapshot['done']
                stage = f'COLLISION_CHUNK_{chunk:03d}'
                if source_digest() != SOURCE:
                    raise ValueError('frozen numerical source changed before chunk')
                generation = root/'generations'/f'g{expected:06d}'
                if generation.exists():
                    base.validate_generation(generation, plan['config'], expected)
                    continue
                active = root/'collision'
                done = guard.validate_checkpoint(active, plan['config'])['done'] if (active/'state.json').exists() else 0
                action = base.frontier_action(chunk, done, expected, False)
                if action == 'RUN_CHUNK':
                    base._command(f'collision.chunk{chunk:03d}', collision, root, started)
                    if guard.validate_checkpoint(active, plan['config'])['done'] != expected:
                        raise ValueError('writer returned outside exact A3 frontier')
                stage = f'SNAPSHOT_CHUNK_{chunk:03d}'
                base._command(f'snapshot.g{expected:06d}', snapshot, root, started)
                manifest = base.validate_generation(generation, plan['config'], expected)
                base.publish(root/'receipts'/f'chunk{chunk:03d}.committed.json', dict(
                    status='CHUNK_AND_GENERATION_COMMITTED', chunk=chunk, done=expected,
                    generation_manifest_sha256=base.sha(generation/guard.MANIFEST_NAME),
                    state_sha256=manifest['files']['state.npy']['sha256'],
                    next_chunk_authorized=chunk<CHUNKS))
            stage = 'FINAL_AUDIT'
            final = guard.validate_checkpoint(root/'collision', plan['config'])
            result = base.read(root/'collision/result.json')
            if final['done'] != NSTEP or result.get('status') != 'completed':
                raise ValueError('A3 final result/checkpoint incomplete')
            complete = dict(status='COMPLETE', job='A3', chunks=CHUNKS,
                retained_generations=CHUNKS, done=NSTEP, nstep=NSTEP,
                contract_sha256=approval,
                preparation_receipt_sha256=prepared['receipt_sha256'],
                result_sha256=base.sha(root/'collision/result.json'),
                final_generation_manifest_sha256=base.sha(root/'generations'/'g007172'/guard.MANIFEST_NAME),
                new_full_collisions=1, production_admission=False)
            base.publish(root/'COMPLETE.json', complete)
            return complete
        except BaseException as exc:
            failure = root/'FIRST_FAILURE.json'
            if not failure.exists():
                try:
                    base.publish(failure, dict(stage=stage, exception_type=type(exc).__name__,
                        message=str(exc), traceback=traceback.format_exc(),
                        automatic_retry=False, scientific_nonconvergence='UNDETERMINED',
                        completed_generations=len(list((root/'generations').glob('g*/r3m17_generation_manifest.json'))),
                        production_admission=False))
                except BaseException:
                    pass
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    f = sub.add_parser('freeze')
    f.add_argument('--config', type=Path, default=CONFIG)
    f.add_argument('--root', type=Path, required=True)
    f.add_argument('--contract', type=Path, required=True)
    r = sub.add_parser('run')
    r.add_argument('--contract', type=Path, required=True)
    r.add_argument('--approve-sha256', required=True)
    r.add_argument('--explicit-resume', action='store_true')
    args = parser.parse_args()
    if args.command == 'freeze':
        dirty = base.git('status', '--porcelain', '--',
            'scripts/r3m28_execute.py', 'scripts/r3m28_spatial.py',
            'tests/test_r3m28_execute.py', 'tests/test_r3m28_spatial.py',
            'configs/r3m28/A3.json', 'results/R3M28/DESIGN.json')
        if dirty:
            raise ValueError('commit A3 source/config/design/tests before freeze')
        if args.root.exists():
            raise FileExistsError('fresh A3 output root required')
        plan = build_plan(args.config, args.root)
        base.resources(args.root)
        base.publish(args.contract, plan)
        base.publish(args.contract.with_name('HASH_MANIFEST.json'), dict(
            contract_sha256=base.sha(args.contract),
            config_sha256=plan['config_sha256'],
            design_sha256=plan['design_sha256'],
            source_hashes=plan['source_hashes'],
            output_root=plan['output_root']))
        print(json.dumps(dict(contract=str(args.contract),
                              sha256=base.sha(args.contract),
                              generations=CHUNKS, gpu_work=0)))
    else:
        print(json.dumps(execute(args.contract, args.approve_sha256,
                                 explicit_resume=args.explicit_resume), sort_keys=True))


if __name__ == '__main__':
    main()
