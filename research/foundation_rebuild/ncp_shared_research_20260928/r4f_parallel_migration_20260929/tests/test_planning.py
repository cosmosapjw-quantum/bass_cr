from __future__ import annotations

import sys
from pathlib import Path
import hashlib
import json
import zipfile

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / 'research/foundation_rebuild/tp1_short_transport_20260926'))
from parallel_bridge import CacheMiss, CacheOnlyProvider, plan_queries, query_id, select_missing
from metric_transport import run_candidate
from cr_repro.observables import projectile_speed_au


def test_planner_matches_unchanged_candidate_traversal(monkeypatch):
    import metric_transport

    touched = []
    widths = []

    class Provider:
        def at(self, t):
            touched.append(float(t).hex())
            return type('Snapshot', (), {'S': np.eye(2), 'H': np.zeros((2, 2)), 'D': np.zeros((2, 2))})()

    real_step = metric_transport.candidate_step

    def record_step(provider, y, ta, tb):
        widths.append(float(tb - ta).hex())
        return real_step(provider, y, ta, tb)

    monkeypatch.setattr(metric_transport, 'candidate_step', record_step)
    run_candidate(Provider(), np.array([1., 0.]), -3.125, 6.375, 768)
    plan = plan_queries('context-test', -3.125, 6.375, 768)
    assert [x.time_hex for x in plan] == touched
    assert [x.width_hex for x in plan if x.step is not None] == widths
    assert len({x.query_id for x in plan}) == 770


def test_frozen_window_has_two_original_hits_and_607_shortcut_mismatches():
    archive=REPO/'research/foundation_rebuild/ncloud_c64g3_20260928/artifacts/tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip'
    with zipfile.ZipFile(archive) as z:
        sc=json.loads(z.read('SCIENCE_CONTEXT.json'))
        base={Path(n).stem for n in z.namelist()
              if n.startswith('runtime_queries/') and n.endswith('.json')}
    c=sc['context']['contract'];v=projectile_speed_au(c['energy_keV_per_u'])
    t0=c['z_initial_a0']/v;tf=c['z_final_a0']/v;dt=(tf-t0)/768
    plan=plan_queries(sc['context_id'],t0,tf)
    shortcut=[float(t0+(j+0.5)*dt).hex() for j in range(768)]
    assert len(plan)==770
    assert sum(x.query_id in base for x in plan)==2
    assert sum(plan[j+1].time_hex!=shortcut[j] for j in range(768))==607


@pytest.mark.parametrize('present,expected', [
    (set(), [0, 1, 2, 3]),
    ({'q0', 'q1', 'q2', 'q3'}, []),
    ({'q0', 'q2'}, [1, 3]),
])
def test_missing_selection_never_assumes_prefix(present, expected):
    plan = [type('Q', (), {'query_id': f'q{i}'})() for i in range(4)]
    assert [i for i, _ in select_missing(plan, present)] == expected


def test_cache_only_miss_has_no_evaluator(tmp_path):
    provider = CacheOnlyProvider(tmp_path, 'context-test', {'raw_cross_relative_max': 1e-9},
                                 set())
    with pytest.raises(CacheMiss):
        provider.at(0.125)
    assert provider.native_calls == 0


def test_shuffled_cache_completion_replays_original_time_order(tmp_path):
    cid = 'synthetic-context'
    t0 = -1.; tf = 1.; n = 8; dt = (tf-t0)/n
    times = [t0]
    for j in range(n):
        ta = t0+j*dt; tb = ta+dt
        times.append(0.5*(ta+tb))
    times.append(tf)
    ids = {query_id(cid, float(t).hex()) for t in times}
    # Store in reverse completion order; replay must still follow run_candidate.
    for t in reversed(times):
        th = float(t).hex(); qid = query_id(cid, th)
        npz = tmp_path/(qid+'.npz')
        np.savez_compressed(npz,selected__S=np.eye(18),
                            selected__H=np.zeros((18,18)),
                            selected__D=np.zeros((18,18)))
        rec={'schema':'BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1',
             'query_id':qid,'time_hex':th,'context_id':cid,
             'payload_sha256':hashlib.sha256(npz.read_bytes()).hexdigest(),
             'qualification':{'status':'RUNTIME_QUERY_QUALIFIED'}}
        (tmp_path/(qid+'.json')).write_text(json.dumps(rec))
    provider=CacheOnlyProvider(tmp_path,cid,{},ids)
    accessed=[]
    real_at=provider.at
    def record(t):
        accessed.append(float(t).hex())
        return real_at(t)
    provider.at=record
    initial=np.eye(18)[0]
    result=run_candidate(provider,initial,t0,tf,n)
    assert accessed==[float(t).hex() for t in times]
    assert np.allclose(result.final_state,initial)
    assert provider.reads==10 and provider.native_calls==0
    with pytest.raises(CacheMiss):
        provider.at(0.123)
