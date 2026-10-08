"""Research-only matrix postprocessor: no native operator or transport launcher.

General formula keeps hbar explicit. The CLI reads pinned atomic-unit arrays and
passes hbar=1 because that is their declared unit convention. Sdot=D+D^dagger
is an assumed exact Galerkin kinematic identity, NOT a measured finite difference.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np


def adj(a):
    return a.conj().T


def matrix(a, name):
    a = np.asarray(a, dtype=complex)
    if a.ndim != 2 or not np.isfinite(a).all():
        raise ValueError(f'{name}: finite matrix required')
    return a


def hermitian(a, name, tolerance=1e-11):
    a = matrix(a, name)
    if a.shape[0] != a.shape[1]:
        raise ValueError(f'{name}: square matrix required')
    defect = float(np.linalg.norm(a-adj(a), 2))
    if defect > tolerance*max(1.0, float(np.linalg.norm(a, 2))):
        raise ValueError(f'{name}: non-Hermitian input')
    return a, defect


def rate_matrices(S, H, D, J, *, hbar, Jdot=None):
    """Return Q, Qdot, A, W and local generalized spectral envelope rho.

    Jdot=0 describes a fixed coefficient selector in the declared moving basis.
    Under a time-dependent coordinate change Jdot generally cannot be set to zero.
    No input matrix is regularized, clipped, or used to launch a new evaluation.
    """
    if isinstance(hbar, bool) or not np.isscalar(hbar) or not math.isfinite(hbar) or hbar <= 0:
        raise ValueError('positive finite hbar required')
    S, sdef = hermitian(S, 'S'); H, hdef = hermitian(H, 'H')
    D = matrix(D, 'D'); J = matrix(J, 'J'); n = len(S)
    if H.shape != S.shape or D.shape != S.shape or J.shape[0] != n or not 0 < J.shape[1] <= n:
        raise ValueError('inconsistent matrix/selector shapes')
    if np.linalg.eigvalsh(S)[0] <= 0:
        raise ValueError('S must be positive definite')
    if Jdot is None:
        Jdot = np.zeros_like(J)
    Jdot = matrix(Jdot, 'Jdot')
    if Jdot.shape != J.shape:
        raise ValueError('Jdot shape mismatch')
    Sd = D+adj(D)
    X = S@J; Xd = Sd@J+S@Jdot
    G = adj(J)@X
    if np.linalg.eigvalsh(G)[0] <= 0:
        raise ValueError('selected Gram must be positive definite')
    Gd = adj(Jdot)@S@J + adj(J)@Sd@J + adj(J)@S@Jdot
    Y = np.linalg.solve(G, adj(X))
    Q = X@Y
    Qd = Xd@Y + X@np.linalg.solve(G, adj(Xd)) - X@np.linalg.solve(G, Gd@Y)
    A = -1j*np.linalg.solve(S,H)/hbar - np.linalg.solve(S,D)
    W = Qd + adj(A)@Q + Q@A
    W, wdef = hermitian(W, 'W')
    # S = L L^dagger. For y=L^dagger c, c^dagger W c = y^dagger L^-1 W L^-dagger y.
    L = np.linalg.cholesky(S)
    left = np.linalg.solve(L, W)
    whitened = adj(np.linalg.solve(L, adj(left)))
    # Only after reporting/passing the Hermiticity check, use the Hermitian part
    # for a real eigensolver; this is roundoff evaluation, not an input repair.
    ew = np.linalg.eigvalsh((whitened+adj(whitened))/2)
    rho = float(np.max(np.abs(ew)))
    return {'Q':Q, 'Qdot':Qd, 'A':A, 'W':W, 'rho':rho,
            'metric_identity_residual':float(np.linalg.norm(Sd+adj(A)@S+S@A,2)),
            'input_S_hermiticity_defect':sdef, 'input_H_hermiticity_defect':hdef,
            'W_hermiticity_defect':wdef,
            'selected_gram_condition':float(np.linalg.cond(G)),
            'S_condition':float(np.linalg.cond(S))}


def analyze_preparation(preparation):
    root = Path(preparation).resolve()
    contract = json.loads((root/'CONTRACT.json').read_text())
    checked = {}
    for name, pin in contract['input_files'].items():
        p = root/'inputs'/name
        raw = p.read_bytes()
        got = hashlib.sha256(raw).hexdigest()
        if len(raw) != pin['bytes'] or got != pin['sha256']:
            raise ValueError(f'input identity mismatch: {name}')
        checked[name] = got
    with np.load(root/'inputs/runtime_queries'/(contract['final_query_id']+'.npz'),allow_pickle=False) as f:
        S,H,D = [np.array(f['selected__'+k]) for k in ('S','H','D')]
    with np.load(root/'inputs/CANDIDATE_N1536.npz',allow_pickle=False) as f:
        c = np.array(f['final_state'])
    J = np.eye(len(c),dtype=complex)[:,contract['selected_indices']]
    mats = rate_matrices(S,H,D,J,hbar=1.0)
    p = np.vdot(c,mats['Q']@c); pd = np.vdot(c,mats['W']@c)
    nn = np.vdot(c,S@c)
    if max(abs(p.imag),abs(pd.imag),abs(nn.imag)) > 1e-11:
        raise ValueError('non-real quadratic form beyond roundoff')
    if abs(pd.real) > nn.real*mats['rho']+1e-12:
        raise ValueError('local generalized envelope inconsistent')
    result = {'schema':'BASS_R4P0A_STORED_ENDPOINT_RATE_PROBE_V1',
      'status':'LOCAL_SEMIDISCRETE_DIAGNOSTIC_ONLY',
      'basis':'B0', 'z_a0':12.0, 'b_a0':2.0,
      'selected_indices':contract['selected_indices'],
      'P_selected':float(p.real), 'Pdot_per_atomic_time':float(pd.real),
      'rho_per_atomic_time':mats['rho'], 'state_metric_norm':float(nn.real),
      'quadratic_form_imaginary_parts':[float(p.imag),float(pd.imag),float(nn.imag)],
      'metric_identity_residual':mats['metric_identity_residual'],
      'metric_identity_interpretation':'ALGEBRAIC_SIGN_CHECK_NOT_INDEPENDENT_DERIVATIVE_VALIDATION',
      'W_hermiticity_defect':mats['W_hermiticity_defect'],
      'S_condition':mats['S_condition'], 'selected_gram_condition':mats['selected_gram_condition'],
      'Sdot_source':'ASSUMED_KINEMATIC_IDENTITY_D_PLUS_D_DAGGER',
      'probability_rate_interpretation':'finite Galerkin model local derivative at matched archived state/time; not discrete step derivative or exact full-space dynamics',
      'tail_integral_evaluated':False, 'tail_error_bound_certified':False,
      'new_native_operator_evaluations':0, 'new_transport_executions':0,
      'input_sha256':checked}
    return result

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preparation',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    data=analyze_preparation(args.preparation)
    with args.out.open('x') as stream:
        json.dump(data,stream,indent=2,allow_nan=False); stream.write('\n')
    print(json.dumps(data,indent=2,allow_nan=False))
