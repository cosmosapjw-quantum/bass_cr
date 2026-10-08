"""Frozen ladder parity and metric sentinels for a later authorized F1 run."""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

TP2D = Path(__file__).resolve().parents[3] / 'tp2d_runtime_self_qualified_transport_20260927'
if str(TP2D) not in sys.path:
    sys.path.insert(0, str(TP2D))
from qualified_provider import CROSS_KEYS, ResolutionQualifiedProvider, ResolutionQualificationError


class EngineAdmissionError(RuntimeError):
    def __init__(self, status, message):
        super().__init__(status + ': ' + message)
        self.status = status


def _comparison(historical, current, rtol, atol):
    old, new = np.asarray(historical), np.asarray(current)
    if old.shape != new.shape or not np.isfinite(old).all() or not np.isfinite(new).all():
        return {'allclose': False, 'relative_frobenius': None, 'max_absolute_difference': None}
    delta = new - old
    den = max(float(np.linalg.norm(old)), float(np.linalg.norm(new)), 1e-300)
    return {'allclose': bool(np.allclose(new, old, rtol=rtol, atol=atol)),
            'relative_frobenius': float(np.linalg.norm(delta) / den),
            'max_absolute_difference': float(np.max(np.abs(delta)))}


def _screens(policy):
    return {'raw_cross_relative_max': policy['runtime_raw_cross_convergence_max'],
            'operator_hermiticity_relative_max': policy['operator_hermiticity_relative_max'],
            'metric_min_ratio': policy['metric_min_ratio']}


def admit_query(query, evaluator, contract, check_budget=lambda: None):
    """Evaluate the original finite ladder, then compare every archived attempt."""
    policy = contract['parity_policy']
    historical = query.record
    representative = query.representative
    if representative['query_id'] != historical['query_id'] or representative['time_hex'] != historical['time_hex']:
        raise EngineAdmissionError('F1_INPUT_IDENTITY_BLOCKED', 'query identity drift')
    t = float.fromhex(representative['time_hex'])
    evaluated = {}
    def capture(time, q, h):
        check_budget()
        raw, full = evaluator(time, q, h)
        evaluated[(q, h)] = (raw, full)
        return raw, full
    provider = ResolutionQualifiedProvider(
        evaluate=capture, resolutions=contract['runtime_reference_resolutions'],
        screens=_screens(policy), context_id=historical['context_id'])
    try:
        snapshot = provider.at(t)
    except ResolutionQualificationError as exc:
        for _, full in evaluated.values():
            try:
                S, H = np.asarray(full['S']), np.asarray(full['H'])
                ratio = np.linalg.eigvalsh((S + S.conj().T) / 2)
                bad_metric = ratio[-1] <= 0 or ratio[0] / ratio[-1] < policy['metric_min_ratio']
                bad_hermiticity = any(
                    np.linalg.norm(x - x.conj().T) / max(float(np.linalg.norm(x)), 1e-300)
                    > policy['operator_hermiticity_relative_max'] for x in (S, H))
                if bad_metric or bad_hermiticity:
                    raise EngineAdmissionError('F1_FULL_OPERATOR_PARITY_FAILED', 'new full operator screen failed') from exc
            except (KeyError, ValueError, np.linalg.LinAlgError) as screen_exc:
                raise EngineAdmissionError('F1_FULL_OPERATOR_PARITY_FAILED', str(screen_exc)) from screen_exc
        raise EngineAdmissionError('POLICY_SELECTION_DRIFT', str(exc)) from exc
    selected = snapshot.qualification['selected_resolution']
    if selected != representative['selected_resolution'] or selected != historical['qualification']['selected_resolution']:
        raise EngineAdmissionError('POLICY_SELECTION_DRIFT', 'new selected q/h differs from historical')
    expected_attempts = [x['resolution'] for x in historical['attempts']]
    actual_attempts = [{'order': q, 'subdivisions': h} for q, h in evaluated]
    if expected_attempts != actual_attempts:
        raise EngineAdmissionError('POLICY_SELECTION_DRIFT', 'new finite ladder attempt sequence differs')
    # The historical provider stops at the first qualified pair. F1 separately
    # evaluates the rest of the frozen ladder without changing that selection.
    for resolution in contract['runtime_reference_resolutions'][len(actual_attempts):]:
        check_budget()
        q, h = resolution['order'], resolution['subdivisions']
        raw, full = evaluator(t, q, h)
        if (set(policy['raw_cross_keys']) - set(raw)
                or any(not np.isfinite(np.asarray(raw[key])).all() for key in policy['raw_cross_keys'])):
            raise EngineAdmissionError('F1_RAW_PARITY_FAILED', 'invalid full-ladder raw cross array')
        try:
            S, H, D = (np.asarray(full[key]) for key in ('S', 'H', 'D'))
            eig = np.linalg.eigvalsh((S + S.conj().T) / 2)
            herm = max(float(np.linalg.norm(x - x.conj().T) / max(np.linalg.norm(x), 1e-300))
                       for x in (S, H))
            valid = (all(np.isfinite(x).all() and x.shape == S.shape for x in (S, H, D))
                     and S.ndim == 2 and S.shape[0] == S.shape[1] and eig[-1] > 0
                     and eig[0] / eig[-1] >= policy['metric_min_ratio']
                     and herm <= policy['operator_hermiticity_relative_max'])
        except (KeyError, ValueError, np.linalg.LinAlgError):
            valid = False
        if not valid:
            raise EngineAdmissionError('F1_FULL_OPERATOR_PARITY_FAILED', 'full-ladder operator screen failed')
        evaluated[(q, h)] = (raw, full)
    tolerance = policy['numpy_allclose']
    raw_rows = []
    for resolution in expected_attempts:
        q, h = resolution['order'], resolution['subdivisions']
        raw, _ = evaluated[(q, h)]
        tag = f'q{q}_h{h}'
        for key in policy['raw_cross_keys']:
            comparison = _comparison(query.arrays[f'{tag}__{key}'], raw[key],
                                     tolerance['rtol'], tolerance['atol'])
            raw_rows.append({'resolution': resolution, 'array': key, **comparison})
            if not comparison['allclose']:
                raise EngineAdmissionError('F1_RAW_PARITY_FAILED', tag + ' ' + key)
    full_rows = []
    for key in policy['compare_selected_full_arrays']:
        comparison = _comparison(query.arrays['selected__' + key], getattr(snapshot, key),
                                 tolerance['rtol'], tolerance['atol'])
        full_rows.append({'array': key, **comparison})
        if not comparison['allclose']:
            raise EngineAdmissionError('F1_FULL_OPERATOR_PARITY_FAILED', key)
    diagnostics = snapshot.diagnostics
    if not diagnostics['hermiticity_pass'] or not diagnostics['metric_pass']:
        raise EngineAdmissionError('F1_FULL_OPERATOR_PARITY_FAILED', 'new full operator screen failed')
    if snapshot.qualification['max_raw_cross_relative_difference'] > policy['runtime_raw_cross_convergence_max']:
        raise EngineAdmissionError('F1_RAW_PARITY_FAILED', 'new raw convergence screen failed')
    return {'status': 'PASS', 'query_id': historical['query_id'], 'time_hex': historical['time_hex'],
            'selected_resolution': selected, 'evaluated_resolutions': actual_attempts,
            'full_ladder_evaluated_resolutions': contract['runtime_reference_resolutions'],
            'raw_comparisons': raw_rows, 'full_comparisons': full_rows,
            'new_selected_diagnostics': diagnostics,
            'new_raw_cross_relative_max': snapshot.qualification['max_raw_cross_relative_difference']}


def metric_sentinels(provider, speed, contract, check_budget=lambda: None):
    policy = contract['parity_policy']
    speed = float(speed)
    if not np.isfinite(speed) or speed <= 0:
        raise ValueError('positive finite projectile speed required')
    epsilon_t = float(policy['epsilon_z_a0']) / speed
    rows = []
    for z in policy['metric_connection_sentinels_z_a0']:
        check_budget()
        t = float(z) / speed
        low, center, high = (provider.at(t - epsilon_t), provider.at(t), provider.at(t + epsilon_t))
        sdot = (np.asarray(high.S) - np.asarray(low.S)) / (2 * epsilon_t)
        direct = np.asarray(center.D) + np.asarray(center.D).conj().T
        den = max(float(np.linalg.norm(sdot)), float(np.linalg.norm(direct)), 1e-300)
        residual = float(np.linalg.norm(sdot - direct) / den)
        row = {'z_a0': z, 'time_hex': float(t).hex(), 'epsilon_z_a0': policy['epsilon_z_a0'],
               'epsilon_t': epsilon_t, 'relative_residual': residual,
               'minus_time_hex': float(t - epsilon_t).hex(),
               'plus_time_hex': float(t + epsilon_t).hex(),
               'minus_selected_resolution': low.qualification['selected_resolution'],
               'selected_resolution': center.qualification['selected_resolution'],
               'plus_selected_resolution': high.qualification['selected_resolution']}
        rows.append(row)
        if not np.isfinite(residual) or residual > policy['metric_derivative_relative_max']:
            raise EngineAdmissionError('F1_METRIC_CONNECTION_FAILED', 'new metric derivative residual exceeds gate')
    return rows


def run_admission(evidence, evaluator, speed, contract, engine_identity, check_budget=lambda: None):
    """Evaluate only the fifteen contract queries, then five fixed metric sentinels."""
    representatives = evidence.representatives['queries']
    if len(representatives) != evidence.representatives['query_count']:
        raise EngineAdmissionError('F1_INPUT_IDENTITY_BLOCKED', 'representative count mismatch')
    parity = [admit_query(evidence.query(rep), evaluator, contract, check_budget) for rep in representatives]
    provider = ResolutionQualifiedProvider(
        evaluate=evaluator, resolutions=contract['runtime_reference_resolutions'],
        screens=_screens(contract['parity_policy']), context_id=engine_identity)
    metric = metric_sentinels(provider, speed, contract, check_budget)
    return parity, metric


def make_evaluator(repo_root, build_dir, basis_dir, tp2d_contract):
    """Bind the original evaluator to exact archived basis bytes and a new engine."""
    repo_root = Path(repo_root).resolve()
    fnd = repo_root / 'research/foundation_rebuild'
    imports = (fnd / 'tp2d_runtime_self_qualified_transport_20260927',
               fnd / 'tp2a_analytic_pruning_20260926/code',
               fnd / 'tp2a_perf_20260926', fnd / 'tp1_short_transport_20260926',
               fnd / 'src', fnd / 'full_operator_20260926',
               fnd / 'reaudit_20260925/repair', repo_root)
    for path in imports:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    from bass_foundations.two_center import Trajectory, symmetric_channels
    from cr_repro.observables import projectile_speed_au
    from exact_cross import MomentKernel
    from assemble import assemble
    from runtime import load_bank
    from analytic_adapter import AnalyticEvaluator
    bank, _ = load_bank(basis_dir)
    channels = symmetric_channels(bank)
    speed = projectile_speed_au(tp2d_contract['energy_keV_per_u'])
    trajectory = Trajectory(((0., 0., 0.), (tp2d_contract['b_a0'], 0., 0.)),
                            ((0., 0., 0.), (0., 0., speed)))
    kernel = MomentKernel(build_dir)
    return AnalyticEvaluator(assemble, trajectory=trajectory, channels=channels, kernel=kernel), speed
