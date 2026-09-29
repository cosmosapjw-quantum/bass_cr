"""Cache-preserving N384 to N768 migration, isolated from the serial runner."""
from __future__ import annotations

from dataclasses import dataclass
from concurrent.futures import FIRST_COMPLETED, wait
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import threading
import time

import numpy as np

HERE = Path(__file__).resolve().parent
TP2D = HERE.parents[1] / 'tp2d_runtime_self_qualified_transport_20260927'
R4C = HERE.parent / 'r4c_temporal_continuation'
for directory in (TP2D, R4C):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
from execution_admission import strict_json
from qualified_provider import CROSS_KEYS, _screen_full


class CacheMiss(RuntimeError):
    pass


class InvalidPair(ValueError):
    pass


class BudgetExceeded(RuntimeError):
    pass


class MigrationCancelled(RuntimeError):
    pass


def query_id(context_id: str, time_hex: str) -> str:
    value = {'schema': 'BASS_TP2D_RUNTIME_QUERY_V1',
             'context_id': context_id, 'time_hex': time_hex}
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class PlannedQuery:
    query_id: str
    time_hex: str
    step: int | None
    width_hex: str | None


def plan_queries(context_id: str, t0: float, tf: float, nstep: int = 768) -> list[PlannedQuery]:
    if nstep != 768 or not np.isfinite((t0, tf)).all() or not tf > t0:
        raise ValueError('frozen N768 increasing finite window required')
    dt = (float(tf) - float(t0)) / nstep

    def entry(t: float, step: int | None, width: float | None) -> PlannedQuery:
        th = float(t).hex()
        return PlannedQuery(query_id(context_id, th), th, step,
                            None if width is None else float(width).hex())

    plan = [entry(float(t0), None, None)]
    for j in range(nstep):
        ta = float(t0) + j * dt
        tb = ta + dt
        tm = 0.5 * (ta + tb)
        plan.append(entry(tm, j, tb - ta))
    plan.append(entry(float(tf), None, None))
    if len({x.query_id for x in plan}) != nstep + 2:
        raise ValueError('duplicate required time query')
    return plan


def select_missing(plan: list[PlannedQuery], present: set[str]) -> list[tuple[int, PlannedQuery]]:
    return [(i, item) for i, item in enumerate(plan) if item.query_id not in present]


def _close(a: float, b: float) -> bool:
    return math.isclose(float(a), float(b), rel_tol=2e-12, abs_tol=2e-15)


def _relative(a: np.ndarray, b: np.ndarray) -> float:
    den = max(float(np.linalg.norm(a)), float(np.linalg.norm(b)), 1e-300)
    return float(np.linalg.norm(a-b)/den)


def validate_pair(query_dir: Path, item: PlannedQuery, context_id: str, contract: dict) -> dict:
    """Validate a complete committed pair, including its ordered qualification."""
    query_dir = Path(query_dir)
    jp = query_dir / (item.query_id + '.json')
    npz = query_dir / (item.query_id + '.npz')
    try:
        if not jp.is_file() or not npz.is_file() or jp.is_symlink() or npz.is_symlink():
            raise ValueError('missing or symlink query pair')
        rec = strict_json(jp)
        if (rec.get('schema') != 'BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1'
            or rec.get('query_id') != item.query_id
            or rec.get('context_id') != context_id
            or rec.get('time_hex') != item.time_hex
            or query_id(context_id, item.time_hex) != item.query_id):
            raise ValueError('query identity mismatch')
        if not math.isfinite(float.fromhex(item.time_hex)):
            raise ValueError('nonfinite query time')
        if rec.get('capture_execution_allowed') is not False or rec.get('continuous_global_supremum_bound') is not False:
            raise ValueError('claim ceiling mismatch')
        payload = npz.read_bytes()
        if hashlib.sha256(payload).hexdigest() != rec.get('payload_sha256'):
            raise ValueError('payload sha256 mismatch')
        q = rec['qualification']
        attempts = rec['attempts']
        ladder = contract['runtime_reference_resolutions']
        screens = contract['screens']
        if (q['status'] != 'RUNTIME_QUERY_QUALIFIED' or not isinstance(attempts, list)
            or not 2 <= len(attempts) <= len(ladder)
            or [r['resolution'] for r in attempts] != ladder[:len(attempts)]
            or q['lower_resolution'] != attempts[-2]['resolution']
            or q['selected_resolution'] != attempts[-1]['resolution']):
            raise ValueError('ordered resolution qualification mismatch')
        with np.load(npz, allow_pickle=False) as f:
            selected = {k: np.array(f['selected__' + k]) for k in ('S', 'H', 'D')}
            if any(a.shape != (18, 18) or not np.isfinite(a).all() for a in selected.values()):
                raise ValueError('selected operator shape/finiteness mismatch')
            screen = _screen_full(selected, screens)
            for k in ('S_hermiticity_relative', 'H_hermiticity_relative',
                      'hermiticity_relative_max', 'metric_min', 'metric_max', 'metric_ratio'):
                if not _close(rec['selected_diagnostics'][k], screen[k]):
                    raise ValueError('selected diagnostic mismatch')
            if not screen['hermiticity_pass'] or not screen['metric_pass']:
                raise ValueError('selected operator screen fails')
            previous = None
            last_differences = None
            for i, row in enumerate(attempts):
                rule = row['resolution']
                tag = f"q{rule['order']}_h{rule['subdivisions']}"
                raw = {k: np.array(f[f'{tag}__{k}']) for k in CROSS_KEYS}
                if any(a.shape != (9, 9) or not np.isfinite(a).all() for a in raw.values()):
                    raise ValueError('raw operator shape/finiteness mismatch')
                diag = row['diagnostics']
                for key in ('S_hermiticity_relative', 'H_hermiticity_relative',
                            'hermiticity_relative_max', 'metric_min', 'metric_max', 'metric_ratio'):
                    if not math.isfinite(float(diag[key])):
                        raise ValueError('nonfinite attempt diagnostic')
                hp = diag['hermiticity_relative_max'] <= screens['operator_hermiticity_relative_max']
                mp = diag['metric_ratio'] >= screens['metric_min_ratio']
                if (diag['hermiticity_pass'] is not hp or diag['metric_pass'] is not mp
                    or not _close(diag['hermiticity_relative_max'], max(diag['S_hermiticity_relative'], diag['H_hermiticity_relative']))
                    or not _close(diag['metric_ratio'], diag['metric_min']/diag['metric_max'])):
                    raise ValueError('attempt diagnostic logic mismatch')
                if previous is None:
                    if any(row[k] is not None for k in ('previous_raw_cross_relative_max',
                             'previous_raw_cross_relative_differences', 'raw_cross_convergence_pass')):
                        raise ValueError('first attempt has previous difference')
                else:
                    differences = {k: _relative(previous['raw'][k], raw[k]) for k in CROSS_KEYS}
                    maximum = max(differences.values())
                    last_differences = differences
                    if (not _close(row['previous_raw_cross_relative_max'], maximum)
                        or any(not _close(row['previous_raw_cross_relative_differences'][k], value)
                               for k, value in differences.items())
                        or row['raw_cross_convergence_pass'] is not (maximum <= screens['raw_cross_relative_max'])):
                        raise ValueError('raw cross qualification mismatch')
                    passed = (previous['diag']['hermiticity_pass'] and previous['diag']['metric_pass']
                              and hp and mp and maximum <= screens['raw_cross_relative_max'])
                    if passed != (i == len(attempts)-1):
                        raise ValueError('first passing adjacent pair mismatch')
                previous = {'raw': raw, 'diag': diag}
            assert last_differences is not None
            if (not _close(q['max_raw_cross_relative_difference'], max(last_differences.values()))
                or any(not _close(q['raw_cross_relative_differences'][k], value)
                       for k, value in last_differences.items())
                or q.get('evidence_relation') != 'INDEPENDENT_NUMERICAL_RESOLUTION_COMPARISON'):
                raise ValueError('selected adjacent pair mismatch')
        return {'query_id': item.query_id, 'time_hex': item.time_hex,
                'json_sha256': hashlib.sha256(jp.read_bytes()).hexdigest(),
                'payload_sha256': hashlib.sha256(payload).hexdigest(),
                'json_bytes': jp.stat().st_size, 'payload_bytes': len(payload),
                'raw_attempts': len(attempts)}
    except Exception as exc:
        raise InvalidPair(f'{item.query_id}: {exc}') from exc


def publish_pair(source: Path, destination: Path, item: PlannedQuery,
                 context_id: str, contract: dict) -> dict:
    result = validate_pair(source, item, context_id, contract)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    paths = [(Path(source) / (item.query_id + ext), destination / (item.query_id + ext))
             for ext in ('.npz', '.json')]
    if any(dst.exists() for _, dst in paths):
        raise FileExistsError('canonical query ID already published: ' + item.query_id)
    for src, dst in paths:
        with dst.open('xb') as target:
            target.write(src.read_bytes())
            target.flush(); os.fsync(target.fileno())
    fd = os.open(destination, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)
    return result


def import_parent_extra(parent: Path, base: Path, canonical: Path,
                        required: list[PlannedQuery], context_id: str,
                        contract: dict) -> dict:
    """Admit only complete extra required pairs; keep partial files as evidence."""
    parent = Path(parent); base = Path(base); canonical = Path(canonical)
    required_by_id = {item.query_id: item for item in required}
    parent_json = {p.stem for p in parent.glob('*.json')}
    parent_npz = {p.stem for p in parent.glob('*.npz')}
    orphan = sorted(parent_json ^ parent_npz)
    imported = []
    records = []
    duplicates = 0
    for qid in sorted(parent_json & parent_npz):
        pj = parent / (qid + '.json'); pn = parent / (qid + '.npz')
        bj = base / (qid + '.json'); bn = base / (qid + '.npz')
        if bj.is_file() or bn.is_file():
            if not bj.is_file() or not bn.is_file():
                raise InvalidPair('base cache has orphan: ' + qid)
            if pj.read_bytes() != bj.read_bytes() or pn.read_bytes() != bn.read_bytes():
                raise InvalidPair('parent conflicts with frozen base: ' + qid)
            duplicates += 1
            continue
        item = required_by_id.get(qid)
        if item is None:
            raise InvalidPair('parent has unexpected extra query: ' + qid)
        records.append(publish_pair(parent, canonical, item, context_id, contract))
        imported.append(qid)
    return {'schema': 'BASS_R4F_IMPORT_BRIDGE_V1', 'base_duplicates': duplicates,
            'imported_ids': imported, 'imported_records': records,
            'orphan_ids': orphan}


class GlobalBudget:
    """One durable, process-shared reservation ledger for every native raw call."""
    def __init__(self, root: Path):
        self.root = Path(root)
        self._thread_lock = threading.Lock()
        self.seed = strict_json(self.root / 'SEED.json')

    @classmethod
    def create(cls, root: Path, *, parent_attempts: int, maximum: int,
               deadline_unix: float) -> 'GlobalBudget':
        root = Path(root)
        if (parent_attempts < 0 or maximum <= parent_attempts
            or not math.isfinite(deadline_unix)):
            raise ValueError('invalid global budget')
        root.mkdir(parents=True, exist_ok=False)
        seed = {'schema': 'BASS_R4F_GLOBAL_BUDGET_V1',
                'parent_raw_attempts': parent_attempts, 'maximum': maximum,
                'deadline_unix': deadline_unix}
        with (root / 'SEED.json').open('x') as f:
            json.dump(seed, f); f.flush(); os.fsync(f.fileno())
        (root / 'RESERVATIONS.jsonl').open('x').close()
        (root / '.lock').open('x').close()
        return cls(root)

    def _rows(self) -> list[dict]:
        rows = []
        with (self.root / 'RESERVATIONS.jsonl').open('rb') as f:
            for line in f:
                rows.append(json.loads(line))
        return rows

    def reservations(self) -> int:
        return len(self._rows())

    def used(self) -> int:
        return int(self.seed['parent_raw_attempts']) + self.reservations()

    def cancel(self, reason: str) -> None:
        with (self.root / 'CANCELLED.json').open('x') as f:
            json.dump({'reason': reason, 'unix': time.time()}, f)
            f.flush(); os.fsync(f.fileno())

    def reserve(self, query_id_value: str, order: int, subdivisions: int) -> int:
        with self._thread_lock, (self.root / '.lock').open('r+b') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                if (self.root / 'CANCELLED.json').exists() or time.time() >= self.seed['deadline_unix']:
                    raise MigrationCancelled('migration cancelled or deadline reached')
                used = self.used()
                if used >= int(self.seed['maximum']):
                    raise BudgetExceeded('global raw attempt cap exhausted')
                number = used + 1
                row = {'schema': 'BASS_R4F_RAW_ATTEMPT_RESERVATION_V1',
                       'global_attempt': number, 'query_id': query_id_value,
                       'order': int(order), 'subdivisions': int(subdivisions),
                       'pid': os.getpid(), 'unix': time.time()}
                with (self.root / 'RESERVATIONS.jsonl').open('ab') as f:
                    f.write((json.dumps(row, allow_nan=False) + '\n').encode())
                    f.flush(); os.fsync(f.fileno())
                return number
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)


def dispatch_bounded(items, executor, fn, on_result, *, max_inflight: int,
                     deadline_unix: float, cancelled=lambda: False):
    """Dispatch at most max_inflight tasks and stop issuing work on first failure."""
    if max_inflight < 1:
        raise ValueError('positive inflight limit required')
    remaining = iter(items)
    active = {}
    completed = {}

    def submit_one():
        if cancelled() or time.time() >= deadline_unix:
            raise MigrationCancelled('cancelled or deadline reached before dispatch')
        try:
            item = next(remaining)
        except StopIteration:
            return False
        active[executor.submit(fn, item)] = item
        return True

    try:
        for _ in range(max_inflight):
            if not submit_one():
                break
        while active:
            if cancelled() or time.time() >= deadline_unix:
                raise MigrationCancelled('cancelled or deadline reached while tasks active')
            done, _ = wait(active, timeout=min(1.0, deadline_unix-time.time()),
                           return_when=FIRST_COMPLETED)
            for future in done:
                item = active.pop(future)
                value = future.result()
                on_result(item, value)
                completed[item] = value
            for _ in done:
                submit_one()
        return completed
    except BaseException:
        for future in active:
            future.cancel()
        raise


class CacheOnlyProvider:
    def __init__(self, query_dir: Path, context_id: str, screens: dict,
                 allowed_ids: set[str]):
        self.query_dir = Path(query_dir)
        self.context_id = context_id
        self.screens = screens
        self.allowed_ids = frozenset(allowed_ids)
        self.native_calls = 0
        self.reads = 0
        self.cache_hits = 0
        self._cache = {}

    def at(self, t: float):
        from types import SimpleNamespace
        th = float(t).hex()
        qid = query_id(self.context_id, th)
        if qid not in self.allowed_ids:
            raise CacheMiss('CACHE_MISS_UNEXPECTED: ' + qid)
        if th in self._cache:
            self.cache_hits += 1
            return self._cache[th]
        jp = self.query_dir / (qid + '.json')
        npz = self.query_dir / (qid + '.npz')
        if not jp.is_file() or not npz.is_file():
            raise CacheMiss('CACHE_MISS: ' + qid)
        rec = json.loads(jp.read_text())
        if (rec.get('schema') != 'BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1'
            or rec.get('query_id') != qid or rec.get('time_hex') != th
            or rec.get('context_id') != self.context_id
            or rec.get('qualification',{}).get('status') != 'RUNTIME_QUERY_QUALIFIED'):
            raise ValueError('cache identity mismatch: ' + qid)
        if hashlib.sha256(npz.read_bytes()).hexdigest() != rec.get('payload_sha256'):
            raise ValueError('cache payload mismatch: ' + qid)
        with np.load(npz, allow_pickle=False) as f:
            arrays = [np.array(f['selected__' + k]) for k in ('S', 'H', 'D')]
        if any(a.shape != (18, 18) or not np.isfinite(a).all() for a in arrays):
            raise ValueError('nonfinite or wrong-shape cache operator: ' + qid)
        self.reads += 1
        snap = SimpleNamespace(t=float(t), S=arrays[0], H=arrays[1], D=arrays[2],
                               qualification=rec['qualification'], identity=qid)
        self._cache[th] = snap
        return snap
