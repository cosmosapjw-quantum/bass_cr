"""CPU-only evidence semantics; does not change a historical threshold or solver."""
from __future__ import annotations

import math


def _nonnegative(value, name):
    if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f'finite nonnegative {name} required')
    return float(value)


def state_budget(q: float, delta_q: float) -> float:
    """Stable inverse of 2 sqrt(q) e + e**2 <= delta_q for a projector."""
    q = _nonnegative(q, 'q'); delta_q = _nonnegative(delta_q, 'delta_q')
    if delta_q == 0 or not math.isfinite(q+delta_q):
        raise ValueError('positive representable probability budget required')
    return delta_q / (math.sqrt(q+delta_q)+math.sqrt(q))


def repeat_kind(a: dict, b: dict) -> str:
    """Different tolerance labels alone cannot supply independent evidence."""
    for row in (a,b):
        n, s = row.get('n'), row.get('action_substeps')
        dims = row.get('basis_dimensions', [])
        if (type(n) is not int or n < 1 or type(s) is not int or s < 1 or
                len(dims) != 2*n*s or any(type(x) is not int or x < 1 for x in dims) or
                sum(dims) != row.get('matvecs')):
            raise ValueError('incomplete/inconsistent actual work trace')
    for key in ('input_sha256','source_key','t0','horizon','n'):
        if a[key] != b[key]:
            raise ValueError(f'not a same-input repeat: {key}')
    same = all(a[key] == b[key] for key in
               ('action_substeps','backend','dtype','basis_dimensions','matvecs'))
    if same:
        return ('UNCHANGED_WORK_NOT_INDEPENDENT' if a['endpoint_sha256']==b['endpoint_sha256']
                else 'SAME_WORK_DIFFERENT_OUTPUT')
    return 'CHANGED_WORK'


def tightening_is_unchanged(actions: list[dict], global_budget: float) -> bool:
    """Predict same first stopping indices, assuming deterministic fixed inputs.

    All earlier indices failed the looser budget; if every accepted bound already
    meets the tighter per-action budget, tightening cannot change an index. This
    is reuse of the original work, NOT a new floating-point error experiment.
    """
    if not actions or _nonnegative(global_budget,'global_budget') == 0:
        raise ValueError('nonempty actions and positive budget required')
    bounds = [_nonnegative(a['physical_upper_bound'],'action bound') for a in actions]
    return all(b <= global_budget/len(actions) for b in bounds)


def strang_gate(scale: float, outer_difference: float, independent_difference: float,
                independence: str) -> dict:
    scale = _nonnegative(scale,'scale')
    outer_difference = _nonnegative(outer_difference,'outer difference')
    independent_difference = _nonnegative(independent_difference,'action difference')
    if scale == 0:
        raise ValueError('positive frozen comparison scale required')
    status = ('UNRESOLVED_INDEPENDENT_ACTION' if independence != 'CHANGED_WORK' else
              'PASS_STRANG_SCALE_ONLY' if max(outer_difference,independent_difference) < .01*scale else
              'UNRESOLVED_STRANG_SCALE')
    return dict(status=status, scope='REFERENCE_FOR_STRANG', threshold=.01*scale,
                CF4_ORDER_CHARACTERIZATION='NOT_EVALUATED',
                REFERENCE_FOR_TARGET_Q='NOT_EVALUATED', GLOBAL_TIME_ERROR='NOT_EVALUATED',
                production_admission=False)


def discriminator_design(dt: float, nstep: int, z_start: float, z_stop: float, saved_done: int) -> dict:
    """No propagation; distinguish the event window and B3 from the old contract."""
    if (not math.isfinite(dt) or dt <= 0 or type(nstep) is not int or nstep <= 0 or
            not all(math.isfinite(x) for x in (z_start,z_stop)) or
            not z_start < 0 < z_stop or type(saved_done) is not int):
        raise ValueError('finite ordered event geometry required')
    initial_time = z_start/(z_stop-z_start) * nstep*dt
    first = math.floor(-initial_time/dt)-1
    if saved_done < 0 or saved_done > first or first+4 > nstep:
        raise ValueError('saved generation cannot reach proposed four-step event window')
    return dict(execution_admission='DESIGN_ONLY', production_admission=False,
                event_window=dict(t0=initial_time+first*dt,t1=initial_time+(first+4)*dt,
                                  start_step=first,steps=4,warmup_steps=first-saved_done,
                                  warmup_is_exact_initial_state=False),
                B3=dict(nstep=2*nstep,actual_dt_au=dt/2,
                        prediction_is_acceptance_target=False,automatic_B4=False,
                        admission='REQUIRES_NEW_RESOURCE_AND_SCIENTIFIC_CONTRACT'))
