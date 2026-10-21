"""Prepare 26 new explicit cases and one immutable C21L reference; no ODE import.

Known external grids are reconstructed from fetched, pinned source metadata.
This is a scoped duplicate check, not a claim that all conversations are visible.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
C21L = HERE.parent / 'cr_c21l_rei_pilot_20261021'
REI = '3b85dedce84d37b3e165da00685a8a984950aafe'
FULL_S = (-.012, 0., .012)
FULL_P = (-.0002, 0., .0002)
TOLERANCE = 2e-13


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as out:
        json.dump(value, out, indent=2, sort_keys=True, allow_nan=False)
        out.write('\n')


def load_components():
    spec = importlib.util.spec_from_file_location('c21l_components_readonly', C21L / 'component_split_20261021/analyze_components.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    targets = [dict(case_id=f's{i}_m{j}_r{k}', S0=s, Pm0=m, Pr0=r)
               for (i,s),(j,m),(k,r) in itertools.product(enumerate(FULL_S), enumerate(FULL_P), enumerate(FULL_P))]
    grid = {'schema':'C21M_GRID_V1', 'run_id':'c21m_pilot26_z20_z4_20261021',
            'cases':[c for c in targets if c['case_id'] != 's1_m1_r1']}
    parent_manifest_path = C21L / 'runs/pilot81/MANIFEST.json'
    parent_manifest = json.loads(parent_manifest_path.read_text())
    reference_dir = C21L / 'runs/pilot81/cases/s04_p04'
    receipt = json.loads((reference_dir / 'RESULT.json').read_text())
    if (receipt['status'] != 'COMPLETE' or receipt['identity'] != parent_manifest['identity']
            or sha(reference_dir / 'history.npz') != receipt['history_sha256']):
        raise ValueError('REFERENCE_IDENTITY_OR_RAW_HASH')
    analyzer = load_components()
    with np.load(reference_dir / 'history.npz', allow_pickle=False) as raw:
        if raw['Y'].shape != (40,101) or raw['Y'].dtype != np.float64:
            raise ValueError('REFERENCE_STATE_SHAPE')
        values = analyzer.components(raw)
    actual = {k:float(values[v][0]) for k,v in
              {'S0':'S_signed_F','Pm0':'P_m_signed_F','Pr0':'P_r_signed_F','Ptot0':'P_tot_signed_F'}.items()}
    if max(map(abs, actual.values())) > TOLERANCE:
        raise ValueError('REFERENCE_OFFSET_EXCEEDS_DECLARED_AXIS_TOLERANCE')
    reference = {
        'schema':'C21M_REFERENCE_REUSE_V1', 'case_id':'s1_m1_r1',
        'status':'REUSE_EXISTING_TRAJECTORY_NO_NEW_ODE',
        'requested_display_coordinates':{'S0':0.,'Pm0':0.,'Pr0':0.},
        'actual_initial_signed_full_Frobenius':actual,
        'offset_policy':'Preserve actual quadrature-scale matter/radiation offsets and original common k; do not rewrite raw or claim exact equality to a new builder input.',
        'display_coordinate_axis_tolerance':TOLERANCE,
        'upstream_source_commit':REI,
        'original_content_commit':'60a3f1cb0d8f0875820d18c0d10c448d480334c4',
        'source_case_id':'s04_p04', 'source_input_identity':receipt['identity'],
        'source_paths_relative_to_C21L':{
            'manifest':'runs/pilot81/MANIFEST.json',
            'receipt':'runs/pilot81/cases/s04_p04/RESULT.json',
            'raw':'runs/pilot81/cases/s04_p04/history.npz'},
        'source_sha256':{'manifest':sha(parent_manifest_path),
                         'receipt':sha(reference_dir / 'RESULT.json'),
                         'raw':sha(reference_dir / 'history.npz')},
        'original_mapping':receipt['mapping'], 'original_runtime':receipt['runtime'],
        'solver':'DOP853', 'n_saved':101, 'state_count':40,
        'rtol':parent_manifest['manifest']['settings']['rtol'],
        'atol':parent_manifest['manifest']['settings']['atol'],
        'new_ODE_solves':0, 'global_error_bound':None}
    sqrt2 = math.sqrt(2)
    old_s = parent_manifest['manifest']['S_grid']
    old_p = parent_manifest['manifest']['P_grid']
    half_s = [0.] + [sign*i*.004/12 for i in range(1,13) for sign in (-1,1)]
    half_p = [0.] + [sign*i*.001/12 for i in range(1,13) for sign in (-1,1)]
    half_m = [sign*i*.0004/12 for i in range(1,13) for sign in (-1,1)]
    hh_s = [0.] + [sign*s for s in (.0005,.001,.002,.004) for sign in (-1,1)]
    hh_p = [0.] + [sign*p for p in (.00025,.0005,.001) for sign in (-1,1)]
    families = {
        'C21L81':list(itertools.product(old_s,[0.],old_p)),
        'HH63':list(itertools.product(hh_s,[0.],hh_p)),
        'PR198_parent625':[(sqrt2*s,0.,sqrt2*p) for s,p in itertools.product(half_s,half_p)],
        'PR198_matter600':[(sqrt2*s,sqrt2*m,0.) for s,m in itertools.product(half_s,half_m)],
        'PR198_mixed6':[(sqrt2*s,sqrt2*sign*.0004,-sqrt2*sign*.0004) for s,sign in itertools.product((0.,.004,-.004),(-1,1))]}
    case_checks = []
    for case in targets:
        point = np.array([case[k] for k in ('S0','Pm0','Pr0')])
        matches, nearest = {}, {}
        for name,coords in families.items():
            distances = np.max(abs(np.array(coords)-point),axis=1)
            matches[name] = int(np.count_nonzero(distances <= TOLERANCE))
            nearest[name] = float(np.min(distances))
        if case['case_id'] != 's1_m1_r1' and any(matches.values()):
            raise ValueError('NEW_CASE_OVERLAPS_KNOWN_INPUT_METADATA:' + case['case_id'])
        case_checks.append({**case,'matching_known_target_counts':matches,
                            'nearest_known_target_Linf_distance':nearest,
                            'decision':'REFERENCE_REUSE' if case['case_id']=='s1_m1_r1' else 'NEW_TARGET_IN_AUDITED_SCOPE'})
    evidence = {str(p.relative_to(HERE)):sha(p) for p in
                (HERE/'external_evidence/parent198.py', HERE/'external_evidence/component198.py',
                 HERE/'external_evidence/hh_bridge.py', HERE/'EXTERNAL_UPTAKE.json')}
    dedup = {'schema':'C21M_INPUT_DEDUP_V1', 'status':'PASS_SCOPED',
             'new_target_count':26, 'reused_target_count':1, 'new_ODE_solves':0,
             'norm':'signed full Frobenius; all PR198 half coordinates multiplied by sqrt(2)',
             'axis_absolute_tolerance':TOLERANCE,
             'comparison_scope':'Input grid metadata; C21L A=0 residual matter and compensating radiation offsets are quadrature-scale. External raw whole-ensemble byte identity is not asserted.',
             'unavailable_scope':'Other unexposed conversations, private execution returns, and unobserved backup objects: UNAVAILABLE.',
             'known_grid_sizes':{name:len(coords) for name,coords in families.items()},
             'known_grid_source_sha256':evidence,
             'C21L_manifest_sha256':sha(parent_manifest_path),
             'different_physics_lane_excluded':'REI213/BASS176/REC116 reuse the same C15 warm a=.1999->.2 source-on729. They are not duplicate source/input histories of the z20->4 collisionless pilot.',
             'case_checks':case_checks, 'global_error_bound':None}
    for name,val in [('grid_pilot26.json',grid),('REFERENCE_REUSE.json',reference),('GRID_DEDUP.json',dedup)]:
        write(output/name,val)
    print(json.dumps({'new_cases':26,'reused_cases':1,'new_ODE_solves':0,'reference_actual':actual,
                      'outputs':{n:sha(output/n) for n in ('grid_pilot26.json','REFERENCE_REUSE.json','GRID_DEDUP.json')}},indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    prepare(parser.parse_args().output_dir)
