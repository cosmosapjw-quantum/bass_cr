#!/usr/bin/env python3
"""Bounded, identity-checked B0/B1/B2 temporal analysis; no certified admission.

The three-point ansatz P(dt)=P(0)+c*dt**p is an empirical model. Neither a
small pair difference nor a fitted order proves a remainder bound. The
autonomous target-only order never authorizes a moving two-center collision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cr_repro.hydrogen import bound_quantum_numbers
from cr_repro.observables import projectile_speed_au
from cr_repro.r3m11 import source_digest
from cr_repro.util import config_hash

SOURCE = '581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b'
INITIAL_SHA = 'ed2ff41eb7517f245d5d5a2df4ce699b607f101406c1a588d3fd4a9b522f5daa'
PINS = {
    'B0': ('results/R3M15/B/collision/result.json',
           '23da11c5b877d133db1ddaaeff4b52081c22f930e752aec608e13966d454a1d7',
           'configs/r3m15/B.json'),
    'B1': ('results/R3M16/collisions/B1_result.json',
           'ae4f70261f866a601a51a80c5d00a1fde1394644c3808558e91519bbf124f11f',
           'configs/r3m16/B1.json'),
}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_json(path):
    def pairs(items):
        output = {}
        for key, value in items:
            if key in output:
                raise ValueError('duplicate JSON key: ' + key)
            output[key] = value
        return output
    def invalid(token):
        raise ValueError('nonfinite JSON constant: ' + token)
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs, parse_constant=invalid)


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def enriched(cfg):
    return dict(cfg, _r3m11_controls='FIXED_CAP_SYMMETRIC_V1', _r3m11_source_digest=SOURCE)


def validate_result(result, expected_cfg):
    if result.get('status') != 'completed' or result.get('config') != enriched(expected_cfg):
        raise ValueError('completed result with exact config/source family required')
    if result.get('backend') != expected_cfg['backend']:
        raise ValueError('backend identity mismatch')
    speed = projectile_speed_au(expected_cfg['energy_keV_per_u'])
    horizon = (expected_cfg['z_stop'] - expected_cfg['z_start']) / speed
    nstep = math.ceil(horizon / expected_cfg['dt'])
    if (isinstance(result.get('nstep'), bool) or result.get('nstep') != nstep or
            not math.isclose(result.get('dt_actual', math.nan), horizon/nstep,
                             rel_tol=2e-14, abs_tol=0.0)):
        raise ValueError('nstep/actual dt does not close frozen physical horizon')
    if not math.isclose(result.get('v_au', math.nan), speed, rel_tol=2e-14):
        raise ValueError('velocity/energy mismatch')
    audit = result['analysis']['gram_audit']
    expected_qns = [list(q) for q in bound_quantum_numbers(expected_cfg['project_nmax'])]
    if (audit.get('quantum_numbers') != expected_qns or
            audit.get('project_nmax') != expected_cfg['project_nmax']):
        raise ValueError('projector channel identity mismatch')
    eigen = audit['Gram_eigenvalues']
    cond = audit['Gram_condition']
    norms = audit['finite_grid_state_norms']
    if (len(eigen) != 2 or not all(math.isfinite(x) for x in eigen) or
            not 0 < eigen[0] <= eigen[1] or eigen[0] <= 1e-10*eigen[1] or
            not math.isfinite(cond) or not math.isclose(cond, eigen[1]/eigen[0], rel_tol=1e-10) or
            len(norms) != len(expected_qns) or not all(math.isfinite(x) and x > 0 for x in norms)):
        raise ValueError('invalid projector Gram rank/condition/channel norms')
    norm = audit['wavefunction_norm']
    if not math.isfinite(norm) or not 0 < norm <= 1 + 2e-10:
        raise ValueError('invalid contractive wavefunction norm')
    spans = [audit['P_span_by_nmax'][str(n)] for n in (1, 2, 3)]
    if (not all(math.isfinite(x) and 0 <= x <= norm*(1+5e-10) for x in spans)
            or spans != sorted(spans)):
        raise ValueError('invalid finite-span probability or nesting')
    if not math.isfinite(audit['P_region']) or not 0 <= audit['P_region'] <= norm*(1+5e-10):
        raise ValueError('invalid region probability')
    residual = result['initial']['stationary_residual_Eh']
    if not math.isfinite(residual) or residual < 0:
        raise ValueError('invalid initial residual')
    return dict(zip(('P1','P2','P3'), spans), actual_dt=result['dt_actual'],
                requested_dt=expected_cfg['dt'], nstep=nstep, norm=norm,
                initial_residual_Eh=residual)


def validate_witness(witness, cfg, initial_sha=INITIAL_SHA):
    required = {
        'schema': 'BASS_CR_R3M14_INTERNAL_INITIAL_BINDING_V2',
        'status': 'PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED',
        'expected_source_digest': SOURCE, 'actual_source_digest': SOURCE,
        'prepared_state_file_sha256': initial_sha,
        'enriched_config_hash': config_hash(enriched(cfg)),
        'array_digest_match': True, 'norm_match': True, 'environment_match': True,
        'numerical_state_substituted': False, 'numerical_state_renormalized': False,
    }
    if any(witness.get(k) != v for k,v in required.items()):
        raise ValueError('v2 witness/config/initial identity mismatch')
    digest = witness.get('prepared_array_digest')
    if (not isinstance(digest, str) or re.fullmatch(r'[0-9a-f]{64}', digest) is None or
            witness.get('internal_array_digest') != digest):
        raise ValueError('v2 internal/prepared array digest mismatch')


def historical_baseline():
    rows = {}
    for cell, (path, digest, cfgpath) in PINS.items():
        path = ROOT/path
        if sha(path) != digest:
            raise ValueError('historical result identity changed: ' + cell)
        rows[cell] = validate_result(read_json(path), read_json(ROOT/cfgpath))
        rows[cell]['result_sha256'] = digest
    prep = read_json(ROOT/'results/R3M15/B/preparation/receipt.json')
    pointer = read_json(ROOT/'results/R3M16/collisions/B1_MANIFEST.json')
    if (prep['initial_state_sha256'] != INITIAL_SHA or
            pointer['immutable_arrays'][0]['sha256'] != INITIAL_SHA or
            pointer['binding_status'] != 'PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED' or
            pointer['seal_source_digest'] != SOURCE or
            pointer['result']['sha256'] != PINS['B1'][1]):
        raise ValueError('historical preparation identities disagree')
    rows.update(initial_bytes_match=True, initial_state_sha256=INITIAL_SHA,
                authority='Pinned R3M15 raw receipt and R3M16 repository pointer; no new raw remote readback')
    return rows


def temporal_triplet(values, steps, *, relative_tolerance=.001, absolute_tolerance=None):
    if len(values) != 3 or len(steps) != 3:
        raise ValueError('exactly three values and actual timesteps required')
    if not all(math.isfinite(x) and 0 <= x <= 1+2e-10 for x in values):
        raise ValueError('finite nonnegative probabilities required')
    if not all(math.isfinite(x) and x > 0 for x in steps) or not steps[0] > steps[1] > steps[2]:
        raise ValueError('strictly decreasing positive actual timesteps required')
    if not math.isfinite(relative_tolerance) or relative_tolerance <= 0:
        raise ValueError('positive finite relative tolerance required')
    if absolute_tolerance is not None and (not math.isfinite(absolute_tolerance) or absolute_tolerance <= 0):
        raise ValueError('positive explicit absolute tolerance required')
    p0,p1,p2 = values
    d01,d12 = p1-p0,p2-p1
    relative = abs(d12)/abs(p2) if p2 != 0 else None
    if p2 == 0:
        screen = ('ABSOLUTE_TOLERANCE_REQUIRED' if absolute_tolerance is None else
                  'PASS_ABSOLUTE_PAIR_ONLY' if abs(d12) <= absolute_tolerance else 'FAIL_ABSOLUTE_PAIR_SCREEN')
    else:
        screen = 'PASS_PAIR_ONLY' if relative <= relative_tolerance else 'FAIL_PAIR_SCREEN'
    result = dict(status='UNRESOLVED_DIFFERENCES', values=list(values), actual_dt=list(steps),
                  signed_coarse_change=d01, signed_fine_change=d12,
                  fine_pair_absolute=abs(d12), fine_pair_relative=relative,
                  relative_denominator=abs(p2), fine_pair_screen=screen,
                  relative_tolerance=relative_tolerance, absolute_tolerance=absolute_tolerance,
                  observed_order=None, extrapolated_value=None,
                  conditional_fine_error_absolute=None, conditional_fine_error_relative=None,
                  clean_second_order_consistency=False, budget_closed=False,
                  certified_error_bound=None,
                  empirical_model='P(dt)=P(0)+c*dt**p; three levels cannot validate their own remainder model')
    if screen == 'ABSOLUTE_TOLERANCE_REQUIRED':
        result['status'] = screen
        return result
    # Resolution test is a floating-point diagnostic, never an absolute scientific tolerance.
    floor = 64*np.finfo(float).eps*max(abs(x) for x in values)
    result['roundoff_resolution_floor'] = floor
    if min(abs(d01), abs(d12)) <= floor:
        return result
    if d01*d12 < 0:
        result['status'] = 'SIGN_CHANGE_NONASYMPTOTIC'
        return result
    if abs(d12) >= abs(d01):
        result['status'] = 'NO_CONTRACTION'
        return result
    l01, l12 = math.log(steps[0]/steps[1]), math.log(steps[1]/steps[2])
    ratio = d01/d12
    def ratio_model(order):
        return math.expm1(order*l01)/(-math.expm1(-order*l12))
    if not ratio_model(1e-6) < ratio < ratio_model(12):
        result['status'] = 'NO_RESOLVED_POSITIVE_ORDER_IN_REGISTERED_RANGE'
        return result
    order = brentq(lambda p: ratio_model(p)-ratio, 1e-6, 12, xtol=1e-12)
    correction = d12/math.expm1(order*l12)
    result.update(status='EMPIRICAL_CONTRACTION_ONLY', observed_order=order,
                  extrapolated_value=p2+correction,
                  conditional_fine_error_absolute=abs(correction),
                  conditional_fine_error_relative=abs(correction)/abs(p2) if p2 else None,
                  clean_second_order_consistency=1.5 <= order <= 2.5)
    if (result['clean_second_order_consistency'] and screen == 'PASS_PAIR_ONLY' and
            result['conditional_fine_error_relative'] <= relative_tolerance):
        result['status'] = 'EMPIRICAL_TEMPORAL_CANDIDATE_REQUIRES_CROSSCHECK'
    return result


def analyze_b2(run, prepared):
    """Read and hash local B2 evidence once; does not re-download remote arrays."""
    from scripts.r3m14_collision_initial_witness import validate_prepared
    from scripts.r3m17_checkpoint_guard import validate_checkpoint
    if source_digest() != SOURCE:
        raise ValueError('frozen numerical source changed')
    run, prepared = Path(run), Path(prepared)
    cfg = read_json(ROOT/'configs/r3m16/B1.json')
    cfg['dt'] = .0125
    raw = read_json(run/'result.json')
    row = validate_result(raw, cfg)
    prepared_info = validate_prepared(prepared, cfg, SOURCE)
    if prepared_info['state_file_sha256'] != INITIAL_SHA:
        raise ValueError('B2 preparation bytes differ from B0/B1')
    witness = read_json(run/'r3m14_initial_binding.json')
    validate_witness(witness, cfg)
    if (witness['prepared_receipt_sha256'] != prepared_info['receipt_sha256'] or
            witness['prepared_array_digest'] != prepared_info['array_digest']):
        raise ValueError('witness does not bind supplied preparation')
    checkpoint = validate_checkpoint(run, cfg, require_witness=True)
    state = read_json(run/'state.json')
    if (checkpoint['done'] != row['nstep'] or checkpoint['nstep'] != row['nstep']):
        raise ValueError('B2 completed checkpoint identity mismatch')
    if (state['initial'] != raw['initial'] or raw['initial'] != witness['initial_metadata'] or
            not math.isclose(state['norm'], row['norm'], rel_tol=5e-10, abs_tol=0.0)):
        raise ValueError('B2 result/checkpoint/initial witness metadata mismatch')
    row['result_sha256'] = checkpoint['files']['result.json']['sha256']
    baseline = historical_baseline()
    rows = {key:baseline[key] for key in ('B0','B1')}
    rows['B2'] = row
    per_channel = {p: temporal_triplet([rows[k][p] for k in rows],
                                     [rows[k]['actual_dt'] for k in rows]) for p in ('P1','P2','P3')}
    candidate = all(v['status'] == 'EMPIRICAL_TEMPORAL_CANDIDATE_REQUIRES_CROSSCHECK' for v in per_channel.values())
    return dict(schema='BASS_CR_R3M17_B_TEMPORAL_V1', rows=rows,
                channel_temporal_analysis=per_channel,
                decision='EMPIRICAL_TEMPORAL_CANDIDATE_REQUIRES_CROSSCHECK' if candidate else 'TIME_REFINEMENT_STILL_OPEN',
                production_admitted=False, representation_change_admitted=False,
                spatial_gap_at_dt0125=None, missing_spatial_cell='A2_NOT_RUN',
                initial_state_sha256=INITIAL_SHA, numerical_source_digest=SOURCE,
                instrumentation_sha256=sha(Path(__file__)),
                evidence={'B2_witness_sha256':sha(run/'r3m14_initial_binding.json'),
                          'B2_seal_sha256':sha(run/'r3m11_checkpoint_seal.json'),
                          'B2_run_receipt_sha256':checkpoint['files']['r3m14_witness_run_receipt.json']['sha256'],
                          'B2_prepared_receipt_sha256':prepared_info['receipt_sha256']},
                claim_ceiling='Same-grid finite-span empirical temporal diagnostic only; all-bound/b-grid/rates OPEN')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--b2-run', type=Path, required=True)
    parser.add_argument('--b2-prepared', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('preserve existing temporal evidence')
    try:
        value = analyze_b2(args.b2_run, args.b2_prepared)
        write_new(args.out, value)
    except Exception as exc:
        failure = args.out.with_name(args.out.stem+'.failure.json')
        if not failure.exists():
            write_new(failure, {'status':'STRUCTURAL_OR_EVIDENCE_BLOCKED','type':type(exc).__name__,'message':str(exc)})
        raise
    print(json.dumps(value, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
