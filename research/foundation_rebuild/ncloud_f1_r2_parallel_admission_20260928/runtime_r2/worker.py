"""Spawn worker: one exact basis/native evaluator binding per process."""
from .resources import enforce_thread_policy

_EVALUATOR = None
_RAW_KEYS = ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')
_FULL_KEYS = ('S', 'H', 'D')


def initialize_worker(repo_root, build_dir, basis_dir, tp2d_contract, evaluator_factory=None):
    global _EVALUATOR
    enforce_thread_policy()
    if evaluator_factory is None:
        from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.engine_admission import make_evaluator
        evaluator_factory = make_evaluator
    bound = evaluator_factory(repo_root, build_dir, basis_dir, tp2d_contract)
    _EVALUATOR = bound[0] if isinstance(bound, tuple) else bound
    if not callable(_EVALUATOR):
        raise RuntimeError('R2_WORKER_INIT_FAILED: evaluator is not callable')


def evaluate_task(spec):
    if _EVALUATOR is None:
        raise RuntimeError('R2_WORKER_INIT_FAILED: evaluator not bound')
    import numpy as np
    time_hex = spec['time_hex']
    t = float.fromhex(time_hex)
    if t.hex() != time_hex or spec.get('sector', 'full') != 'full':
        raise ValueError('R2_WORKER_IDENTITY_BLOCKED: exact time/sector required')
    raw, full = _EVALUATOR(t, spec['order'], spec['subdivisions'])
    if set(_RAW_KEYS) - set(raw) or set(_FULL_KEYS) - set(full):
        raise ValueError('R2_WORKER_PAYLOAD_BLOCKED: scientific array missing')
    arrays = {'raw': {key: np.asarray(raw[key]) for key in _RAW_KEYS},
              'full': {key: np.asarray(full[key]) for key in _FULL_KEYS}}
    if any(not np.isfinite(value).all() for section in arrays.values() for value in section.values()):
        raise ValueError('R2_WORKER_NONFINITE: operator array')
    return {'task_id': spec['task_id'], 'raw': arrays['raw'], 'full': arrays['full']}
