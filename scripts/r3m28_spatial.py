#!/usr/bin/env python3
"""Evaluate preregistered A3/B3 spatial pair and raw h-dt interaction."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from cr_repro.r3m11 import source_digest
from scripts import r3m27_b3_execute as base
from scripts import r3m28_execute as run
from scripts.r3m17_temporal import validate_result, validate_witness

ROOT = Path(__file__).resolve().parents[1]
CHANNELS = ('P1', 'P2', 'P3')
SCREEN = .003
B3_RAW = Path('/mnt/sn850x2t/bass_cr_r3m27_20260924/B3/collision/result.json')
B3_RAW_SHA = '7360649d2148420c3eebdb32f05938a3ee4afc048655e300a6b19b1e12f7dbce'
B3_CONFIG = ROOT / 'configs/r3m27/B3.json'


def screen(a1: dict, b1: dict, a3: dict, b3: dict) -> dict:
    """Arithmetic only; callers must establish raw scientific identities."""
    rows = {}
    for channel in CHANNELS:
        values = [row.get(channel) for row in (a1, b1, a3, b3)]
        if any(isinstance(v, bool) or not isinstance(v, (float, int)) or
               not math.isfinite(v) or v <= 0 for v in values):
            raise ValueError('finite positive channel probabilities required')
        old = b1[channel]-a1[channel]
        fine = b3[channel]-a3[channel]
        interaction = fine-old
        relative = abs(fine)/b3[channel]
        rows[channel] = dict(A1=a1[channel], B1=b1[channel],
            A3=a3[channel], B3=b3[channel],
            old_h_gap=old, fine_h_gap=fine,
            raw_h_dt_interaction=interaction,
            pair_relative_to_B3=relative,
            pair_screen_pass=relative <= SCREEN,
            denominator_B3=b3[channel],
            absolute_screen_threshold=SCREEN*b3[channel])
    pair_pass = all(v['pair_screen_pass'] for v in rows.values())
    return dict(status='SPATIAL_PAIR_SCREEN_PASS_BUDGET_OPEN' if pair_pass else
                'SPATIAL_PAIR_SCREEN_NO_GO', channels=rows,
                pair_screen_relative=SCREEN,
                pair_is_validated_spatial_error_estimate=False,
                h_dt_interaction_is_validated_error_estimate=False,
                h_dt_accounting='OPEN_COUNT_ONCE_IN_FUTURE_VALIDATED_ENVELOPE_OR_SEPARATELY',
                A3_time_error='NOT_INDEPENDENTLY_VALIDATED',
                subcell_translation_full_component='OPEN',
                spatial_budget='OPEN', production_admission=False)


def evaluate(root: Path, contract: Path) -> dict:
    root, contract = Path(root).absolute(), Path(contract).absolute()
    plan = base.read(contract)
    if root != Path(plan['output_root']) or base.sha(contract) != base.read(root/'RUN.json')['contract_sha256']:
        raise ValueError('A3 root/contract SHA binding mismatch')
    run.validate_plan(plan)
    design = base.read(run.DESIGN)
    if (base.sha(run.DESIGN) != plan['design_sha256'] or
            design['spatial_pair_screen_relative'] != SCREEN or
            design['actual_dt'] != .00624946176119497):
        raise ValueError('spatial design/criterion changed after A3')
    if source_digest() != run.SOURCE:
        raise ValueError('numerical source changed')
    if base.sha(run.A1_RESULT) != run.A1_RESULT_SHA or base.sha(run.B1_RESULT) != run.B1_RESULT_SHA:
        raise ValueError('historical A1/B1 raw result changed')
    if base.sha(run.B3_RESULT) != run.B3_RESULT_SHA or base.sha(B3_RAW) != B3_RAW_SHA:
        raise ValueError('R3M27 B3 evidence changed')
    cfg_a1 = base.read(run.A1_CONFIG)
    cfg_b1 = base.read(ROOT/'configs/r3m16/B1.json')
    cfg_a3 = base.read(run.CONFIG)
    cfg_b3 = base.read(B3_CONFIG)
    a1 = validate_result(base.read(run.A1_RESULT), cfg_a1)
    b1 = validate_result(base.read(run.B1_RESULT), cfg_b1)
    b3 = validate_result(base.read(B3_RAW), cfg_b3)
    prior_b3 = base.read(run.B3_RESULT)
    if prior_b3['status'] != 'TEMPORAL_ESTIMATE_VALIDATED_FOR_FIXED_H_SELECTED_SPANS':
        raise ValueError('B3 time evidence did not pass')
    for k in ('P1', 'P2', 'P3', 'actual_dt', 'nstep'):
        if b3[k] != prior_b3['raw_B3_row'][k]:
            raise ValueError('raw B3 result differs from R3M27 evaluator')
    complete = base.read(root/'COMPLETE.json')
    result_path = root/'collision/result.json'
    witness_path = root/'collision/r3m14_initial_binding.json'
    if (complete['status'] != 'COMPLETE' or complete['nstep'] != run.NSTEP or
            complete['result_sha256'] != base.sha(result_path) or
            complete['contract_sha256'] != base.sha(contract)):
        raise ValueError('A3 final result not bound to completed contract')
    a3 = validate_result(base.read(result_path), cfg_a3)
    witness = base.read(witness_path)
    validate_witness(witness, cfg_a3, run.INITIAL_SHA)
    prepared = run._prepared(root, cfg_a3)
    if witness['prepared_receipt_sha256'] != prepared['receipt_sha256']:
        raise ValueError('A3 witness does not bind fresh preparation receipt')
    if a3['nstep'] != b3['nstep'] or a3['actual_dt'] != b3['actual_dt']:
        raise ValueError('A3/B3 actual dt/horizon differs')
    if a1['actual_dt'] != b1['actual_dt']:
        raise ValueError('A1/B1 coarse actual dt differs')
    arithmetic = screen(a1, b1, a3, b3)
    return dict(schema='R3M28_SPATIAL_HDT_EVALUATION_V1', **arithmetic,
        claim_scope='SAME_PHYSICAL_HORIZON_H025_H020_SELECTED_SPANS_RAW_PAIR_ONLY',
        original_A3_row=a3, original_B3_row=b3,
        coarse_actual_dt=a1['actual_dt'], fine_actual_dt=a3['actual_dt'],
        source_digest=source_digest(), contract_sha256=base.sha(contract),
        design_sha256=base.sha(run.DESIGN),
        input_sha256=dict(A1=run.A1_RESULT_SHA, B1=run.B1_RESULT_SHA,
            A3=base.sha(result_path), B3=B3_RAW_SHA,
            witness=base.sha(witness_path),
            preparation_receipt=prepared['receipt_sha256']),
        certified_bound=None, all_bound='OPEN', b_grid='NO_GO')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    value = evaluate(args.root, args.contract)
    base.publish(args.out, value)
    print(json.dumps(dict(output=str(args.out), status=value['status'],
                          production_admission=False)))


if __name__ == '__main__':
    main()
