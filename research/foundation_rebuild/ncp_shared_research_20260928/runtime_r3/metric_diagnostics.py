"""Independent finite-difference diagnostics from stored samples only.

Formal units: i*hbar*S*dc/dt=(H-i*hbar*D)c. The admitted arrays use their
original atomic-time/energy convention, so hbar_scaled=1 there. No SI rate,
continuous supremum, integrated eta or new trajectory certificate is inferred.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.linalg import cholesky, solve_triangular
from .integrity import AuditError


def _matrix(value, shape=None):
    value = np.asarray(value)
    if (value.ndim != 2 or value.shape[0] != value.shape[1]
            or (shape is not None and value.shape != shape) or not np.isfinite(value).all()):
        raise AuditError('R3_METRIC_ARRAY', 'finite equal-sized square matrices required')
    return value


def hermiticity_relative(value):
    a = _matrix(value)
    return float(np.linalg.norm(a-a.conj().T)/max(float(np.linalg.norm(a)),1e-300))


def whiten(S, R):
    """S=C†C, C upper: return C^-† R C^-1 using lower L=C† solves."""
    S=_matrix(S); R=_matrix(R,S.shape)
    if hermiticity_relative(S)>1e-11:
        raise AuditError('R3_METRIC_NOT_HERMITIAN','do not silently symmetrize S')
    try:
        lower=cholesky(S,lower=True,check_finite=True)
    except np.linalg.LinAlgError as exc:
        raise AuditError('R3_METRIC_NOT_POSITIVE','no clipping or regularization allowed') from exc
    left=solve_triangular(lower,R,lower=True,check_finite=True)
    return solve_triangular(lower,left.conj().T,lower=True,check_finite=True).conj().T


def matrix_diagnostics(Sminus,S,Splus,D,H,*,epsilon_t:float,hbar_scaled:float,
                       hermiticity_gate:float) -> dict:
    if (not all(math.isfinite(v) and v>0 for v in (epsilon_t,hbar_scaled,hermiticity_gate))):
        raise AuditError('R3_METRIC_PARAMETERS','positive finite eps/hbar/gate required')
    S=_matrix(S)
    low,high,D,H=(_matrix(v,S.shape) for v in (Sminus,Splus,D,H))
    sdot=(high-low)/(2*epsilon_t)
    direct=D+D.conj().T
    residual=sdot-direct
    # The extra term is needed when H is not Hermitian; never hide that failure.
    h_term=(1j/hbar_scaled)*(H.conj().T-H)
    total=residual+h_term
    w=whiten(S,residual);wt=whiten(S,total)
    eig=np.linalg.eigvalsh(S)
    denominator=max(float(np.linalg.norm(sdot)),float(np.linalg.norm(direct)),1e-300)
    hrel=hermiticity_relative(H)
    return {'raw_residual_frobenius':float(np.linalg.norm(residual)),
            'relative_residual':float(np.linalg.norm(residual)/denominator),
            'inherited_denominator':denominator,
            'sdot_fd_frobenius':float(np.linalg.norm(sdot)),
            'connection_sum_frobenius':float(np.linalg.norm(direct)),
            'whitened_connection_spectral_norm':float(np.linalg.norm(w,2)),
            'whitened_total_spectral_norm':float(np.linalg.norm(wt,2)),
            'whitened_connection_hermiticity_relative':hermiticity_relative(w),
            'h_hermiticity_relative':hrel,'h_hermiticity_gate_pass':hrel<=hermiticity_gate,
            'h_nonhermitian_contribution_frobenius':float(np.linalg.norm(h_term)),
            'S_hermiticity_relative':hermiticity_relative(S),
            'S_eigenvalue_min':float(eig[0]),'S_eigenvalue_max':float(eig[-1]),
            'S_condition_2':float(eig[-1]/eig[0]),
            'S_min_eigenvalue_ratio':float(eig[0]/eig[-1]),
            'epsilon_t':epsilon_t,'hbar_scaled':hbar_scaled,
            'derivative_kind':'CENTERED_FINITE_DIFFERENCE_OF_STORED_S_NOT_EXACT_DERIVATIVE',
            'rate_unit':'per_original_atomic_time',
            'continuous_global_supremum_bound':'NOT_CERTIFIED','integrated_eta':'NOT_CERTIFIED'}


def from_cache(cache, sentinel_document:dict, f1_contract:dict) -> dict:
    policy=f1_contract['parity_policy']; rows=[]
    sentinels=sentinel_document['sentinels']
    if [r['z_a0'] for r in sentinels]!=policy['metric_connection_sentinels_z_a0']:
        raise AuditError('R3_SENTINEL_SET','stored sentinel set disagrees with original contract')
    for old in sentinels:
        t=float.fromhex(old['time_hex']);eps=old['epsilon_t']
        if (not math.isfinite(eps) or eps<=0
                or (t-eps).hex()!=old['minus_time_hex'] or (t+eps).hex()!=old['plus_time_hex']
                or old['epsilon_z_a0']!=policy['epsilon_z_a0']):
            raise AuditError('R3_SENTINEL_TIME','exact time/epsilon relation mismatch')
        blocks=[]
        for time_key,q_key in [('minus_time_hex','minus_selected_resolution'),
                               ('time_hex','selected_resolution'),('plus_time_hex','plus_selected_resolution')]:
            q=old[q_key]
            blocks.append(cache.evaluate(old[time_key],q['order'],q['subdivisions'])['full'])
        low,center,high=blocks
        row=matrix_diagnostics(low['S'],center['S'],high['S'],center['D'],center['H'],
                               epsilon_t=eps,hbar_scaled=1.0,
                               hermiticity_gate=policy['operator_hermiticity_relative_max'])
        row.update({k:old[k] for k in ('z_a0','time_hex','minus_time_hex','plus_time_hex','epsilon_z_a0',
                                      'minus_selected_resolution','selected_resolution','plus_selected_resolution')})
        # Reconstruct the historical expression; do not rerun resolution selection.
        row['published_relative_residual']=old['relative_residual']
        row['reconstruction_absolute_difference']=abs(row['relative_residual']-old['relative_residual'])
        row['inherited_metric_gate']=policy['metric_derivative_relative_max']
        row['inherited_metric_gate_pass']=row['relative_residual']<=row['inherited_metric_gate']
        row['metric_positive_ratio_gate_pass']=row['S_min_eigenvalue_ratio']>=policy['metric_min_ratio']
        if not (row['h_hermiticity_gate_pass'] and row['inherited_metric_gate_pass'] and row['metric_positive_ratio_gate_pass']):
            raise AuditError('R3_STORED_SAMPLE_GATE','stored-sample diagnostics failed inherited checks')
        rows.append(row)
    return {'schema':'BASS_R3_STORED_METRIC_DIAGNOSTICS_V1','sentinels':rows,
            'new_native_evaluations':0,'source_arrays_changed':False,
            'derivative_values_independent_of_D':True,'resolution_selection_reexecuted':False,
            'continuous_global_supremum_bound':'NOT_CERTIFIED','integrated_eta':'NOT_CERTIFIED',
            'limitations':['Five nodes and one finite-difference epsilon only.',
                           'Whitened rates are not interchangeable with relative Frobenius residuals.',
                           'No interpolation, new trajectory, capture or all-bound claim.']}
