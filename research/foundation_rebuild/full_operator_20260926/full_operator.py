"""Full finite-FEM S/H/D in a0, Eh, ta; no time propagation or admission.

Same-center blocks use each complete own sphere and a finite projected Coulomb
multipole sum. Cross blocks come from the unchanged validated aligned_cross
kernel, or an identity-bound saved result. Raw operators are never symmetrized.
"""
from __future__ import annotations
from functools import lru_cache
from dataclasses import dataclass
from types import MappingProxyType
import hashlib
import json
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import eval_legendre
from bass_foundations.radial_basis import FEMRadial, readonly
from bass_foundations.two_center import solid_harmonic


def _integer(x, name, lo, hi):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, (int, np.integer)) or not lo <= x <= hi:
        raise ValueError(f'{name} must be an integer in [{lo}, {hi}]')
    return int(x)


def _basis(channels):
    channels = tuple(channels)
    if not channels or len(channels) > 128:
        raise ValueError('1..128 channels required')
    if not all(isinstance(c.radial, FEMRadial) for c in channels):
        raise ValueError('finite common-mesh FEM radial channels required')
    edges = np.asarray(channels[0].radial.edges, float)
    if edges.ndim != 1 or len(edges) < 2 or edges[0] != 0 or not np.isfinite(edges).all() or np.any(np.diff(edges) <= 0):
        raise ValueError('invalid FEM partition')
    if not all(np.array_equal(c.radial.edges, edges) for c in channels):
        raise ValueError('all channels must use identical radial edges')
    if len({(c.center, c.radial.identity, c.m) for c in channels}) != len(channels):
        raise ValueError('duplicate channel identities')
    return channels, edges


@lru_cache(maxsize=8)
def _angular_rule(lmax):
    # Solid-harmonic products times P_L have degree <=4*lmax on the sphere.
    # The periodic sum is exact for its azimuthal polynomial, then Gauss
    # integrates the surviving polynomial in cos(theta).
    x, w = leggauss(max(8, 2*lmax+3))
    nphi = max(16, 4*lmax+5)
    phi = 2*np.pi*np.arange(nphi)/nphi
    r = np.sqrt(1-x*x)
    points = np.stack(np.broadcast_arrays(r[:, None]*np.cos(phi),
                      r[:, None]*np.sin(phi), x[:, None]), axis=-1).reshape(-1, 3)
    weights = np.broadcast_to(w[:, None]*(2*np.pi/nphi), (len(x), nphi)).ravel().copy()
    return readonly(points), readonly(weights)


def _radial_rule(edges, order, split):
    knots = np.unique(np.r_[edges, split[(split > 0) & (split < edges[-1])]])
    x, w = leggauss(order)
    a, b = knots[:-1], knots[1:]
    return ((a+b)[:, None]/2+(b-a)[:, None]*x/2).ravel(), ((b-a)[:, None]*w/2).ravel()


def same_center_blocks(trajectory, channels, t, center, *, order=20):
    """Integrate on the entire selected center's support, never the lens.

    H0 uses the radial weak form, not the stored isolated eigenvalue. The other
    point-Coulomb potential is integrated after an exact finite angular
    projection; the radial partition is split at the nuclear distance R.
    A[j,a,b] = <phi_a | partial_j phi_b> uses direct spatial derivatives.
    """
    center = _integer(center, 'center', 0, 1)
    order = _integer(order, 'order', 6, 64)
    channels, edges = _basis(channels)
    if not np.isfinite(t):
        raise ValueError('finite time required')
    ix = np.array([i for i, c in enumerate(channels) if c.center == center], int)
    if not len(ix):
        raise ValueError('requested center has no channels')
    ch = tuple(channels[i] for i in ix)
    ell = np.array([c.radial.l for c in ch], int)
    em = np.array([c.m for c in ch], int)
    centers = trajectory.centers(t)
    delta = centers[1-center]-centers[center]
    R = float(np.linalg.norm(delta))
    r, w = _radial_rule(edges, order, np.array([R]))
    evaluated = [c.radial.evaluate(r) for c in ch]
    u = np.array([a for a, _ in evaluated]).T
    du = np.array([b for _, b in evaluated]).T
    if not np.isfinite(u).all() or not np.isfinite(du).all():
        raise ArithmeticError('nonfinite radial basis evaluation')
    overlap = u.conj().T @ (w[:, None]*u)
    radial1 = u.conj().T @ ((w/r)[:, None]*u)
    radial2 = u.conj().T @ ((w/r**2)[:, None]*u)
    derivative = u.conj().T @ (w[:, None]*du)
    angular_delta = (ell[:, None] == ell) & (em[:, None] == em)
    S = overlap*angular_delta
    H0 = (0.5*du.conj().T @ (w[:, None]*du)
          +0.5*(ell*(ell+1))[None, :]*radial2
          -trajectory.charges[center]*radial1)*angular_delta
    n, wn = _angular_rule(int(ell.max()))
    solids = [solid_harmonic(n, int(l), int(m)) for l, m in zip(ell, em)]
    Y = np.array([a for a, _ in solids]).T
    gradY = np.stack([b for _, b in solids], axis=1)
    A = np.empty((3, len(ch), len(ch)), complex)
    for j in range(3):
        N = Y.conj().T @ ((wn*n[:, j])[:, None]*Y)
        G = Y.conj().T @ (wn[:, None]*gradY[:, :, j])
        A[j] = derivative*N + radial1*(G-(ell+1)[None, :]*N)
    Vother = np.zeros_like(S, dtype=complex)
    if R == 0:
        Vother = -trajectory.charges[1-center]*radial1*angular_delta
    else:
        cosangle = n @ (delta/R)
        for L in range(2*int(ell.max())+1):
            angular = Y.conj().T @ ((wn*eval_legendre(L, cosangle))[:, None]*Y)
            radial_weight = np.minimum(r, R)**L/np.maximum(r, R)**(L+1)
            radial = u.conj().T @ ((w*radial_weight)[:, None]*u)
            Vother -= trajectory.charges[1-center]*angular*radial
    velocity = trajectory.velocities[center]
    vA = np.tensordot(velocity, A, axes=(0, 0))
    v2 = float(velocity @ velocity)
    # This is the raw expansion of <grad chi_a | grad chi_b>/2, not an
    # a-posteriori Hermitian projection of H. It retains an independent
    # integration-by-parts defect in H-iD if A+A^dagger is not zero.
    H = H0+Vother+0.5j*(vA.conj().T-vA)+0.5*v2*S
    D = -vA-0.5j*v2*S
    result = {k: readonly(a) for k, a in dict(S=S, H=H, D=D, H0=H0, V_other=Vother, A=A).items()}
    result['indices'] = readonly(ix)
    result['metadata'] = {
        'support': 'OWN_FULL_SPHERE', 'center': center, 'radius_a0': float(edges[-1]),
        'order': order, 'radial_nodes': len(r), 'other_center_distance_a0': R,
        'other_potential': 'FINITE_ANGULAR_MULTIPOLE_PROJECTION_RADIAL_SPLIT_AT_R',
        'maximum_projected_multipole': 2*int(ell.max()), 'eigenvalue_substitution': False,
        'volume': float(4*np.pi*np.sum(w*r*r)), 'production_admission': 'HOLD'}
    return result


_CROSS_KEYS = ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')


def _signature(trajectory, channels, t):
    record = {'trajectory': trajectory.record(), 't': float(t),
              'channels': [c.record() for c in channels]}
    return hashlib.sha256(json.dumps(record, sort_keys=True, allow_nan=False,
                          separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class CrossSnapshot:
    signature: str
    arrays: object
    metadata: dict


def _bind_cross(trajectory, channels, t, arrays, metadata):
    nt = sum(c.center == 0 for c in channels)
    np_ = sum(c.center == 1 for c in channels)
    if not nt or not np_:
        raise ValueError('both centers required')
    frozen = {}
    for key in _CROSS_KEYS:
        a = np.asarray(arrays[key], complex)
        expected = (nt, np_) if key.endswith('tp') else (np_, nt)
        if a.shape != expected or not np.isfinite(a).all():
            raise ValueError('cross matrix shape/finiteness mismatch: '+key)
        frozen[key] = readonly(a)
    return CrossSnapshot(_signature(trajectory, channels, t),
                         MappingProxyType(frozen), dict(metadata))


def compute_cross_snapshot(trajectory, channels, t, *, order=24):
    from aligned_cross import cross_blocks
    channels, edges = _basis(channels)
    result = cross_blocks(trajectory, channels, edges, t, order=order, angular='bessel')
    return _bind_cross(trajectory, channels, t, result, result['metadata'])


def assemble_full(trajectory, channels, t, *, same_order=20, cross_order=24, cross=None):
    """Join own-sphere TT/PP with identity-bound cross blocks in caller order.

    Supplying a CrossSnapshot reuses a saved or just-computed cross result.
    No cross integration is run in that path. Otherwise compute only once.
    A rank-deficient/non-Hermitian metric fails rather than being projected.
    """
    channels, edges = _basis(channels)
    if cross is None:
        cross = compute_cross_snapshot(trajectory, channels, t, order=cross_order)
    if not isinstance(cross, CrossSnapshot) or cross.signature != _signature(trajectory, channels, t):
        raise ValueError('cross basis/geometry/time identity mismatch')
    tt = same_center_blocks(trajectory, channels, t, 0, order=same_order)
    pp = same_center_blocks(trajectory, channels, t, 1, order=same_order)
    ti, pi = tt['indices'], pp['indices']
    n = len(channels)
    result = {}
    for name in ('S', 'H', 'D'):
        m = np.empty((n, n), complex)
        m[np.ix_(ti, ti)] = tt[name]
        m[np.ix_(pi, pi)] = pp[name]
        m[np.ix_(ti, pi)] = cross.arrays[name+'_tp']
        m[np.ix_(pi, ti)] = cross.arrays[name+'_pt']
        result[name] = readonly(m)
    diagnostics = {}
    for name in ('S', 'H'):
        mat = result[name]
        defect = float(np.linalg.norm(mat-mat.conj().T)/max(np.linalg.norm(mat), 1e-300))
        diagnostics[name+'_hermiticity_relative'] = defect
        if defect > 1e-11:
            raise ArithmeticError('full '+name+' Hermiticity defect')
    ev = np.linalg.eigvalsh(result['S'])
    ratio = float(ev[0]/ev[-1]) if ev[-1] > 0 else -1.
    diagnostics.update(metric_min=float(ev[0]), metric_max=float(ev[-1]), metric_ratio=ratio)
    if ratio < 1e-8:
        raise ArithmeticError('full metric rank/positive-definiteness unresolved')
    diagnostics['same_center'] = {}
    for label, block in [('T', tt), ('P', pp)]:
        diagnostics['same_center'][label] = {
            'A_skew_absolute_max': max(float(np.linalg.norm(a+a.conj().T)) for a in block['A']),
            'boost_cancellation_absolute': float(np.linalg.norm(block['H']-1j*block['D']-block['H0']-block['V_other'])),
            'D_skew_absolute': float(np.linalg.norm(block['D']+block['D'].conj().T))}
    result['same_center'] = {'T': tt, 'P': pp}
    result['diagnostics'] = diagnostics
    result['metadata'] = {
        'scope': 'FULL_STATIC_FINITE_BASIS_OPERATOR_NOT_CAPTURE',
        'signature': cross.signature, 'channel_count': n, 'units': 'a0_Eh_ta',
        'trajectory': trajectory.record(), 'time_ta': float(t),
        'channels': [c.record() for c in channels], 'cross_metadata': cross.metadata,
        'same_order': same_order, 'production_admission': 'HOLD',
        'all_bound': 'OPEN', 'b_grid': 'NO_GO', 'capture_execution_allowed': False}
    return result



def load_cross_archive(directory, trajectory, channels, t):
    """Reuse the original run_cross_probe RESULT.json/matrices.npz verbatim.

    That legacy schema fixes 100 keV/u, b=2, stationary target, unit charges;
    z and basis identities are read from the saved result. It does not record
    an arbitrary trajectory, so this adapter explicitly refuses other ones.
    Kernel and array bytes plus ALL ordered channel records must match. A
    nearby spectrum on another host is not enough for silent basis rebinding.
    """
    import aligned_cross
    from cr_repro.observables import projectile_speed_au
    from bass_foundations.two_center import Trajectory
    directory = Path(directory)
    meta = json.loads((directory/'RESULT.json').read_text(encoding='utf-8'))
    if meta.get('schema') != 'REAUDIT_STATIC_CROSS_PROBE_V1' or meta.get('status') != 'COMPLETED_STATIC_PROBE':
        raise ValueError('unsupported or incomplete saved cross schema')
    if meta.get('capture_execution_allowed') is not False or meta.get('production_admission') != 'HOLD':
        raise ValueError('saved cross scope is not a bounded static probe')
    channels, edges = _basis(channels)
    if meta.get('channel_identities') != [c.record() for c in channels]:
        raise ValueError('saved cross channel identity mismatch; do not silently rebind eigenvectors')
    kernel_sha = hashlib.sha256(Path(aligned_cross.__file__).read_bytes()).hexdigest()
    if meta.get('kernel_sha256') != kernel_sha:
        raise ValueError('saved cross kernel identity mismatch')
    z = float(meta['z'])
    v = projectile_speed_au(100.)
    source_tr = Trajectory(((0, 0, 0), (2., 0, 0)), ((0, 0, 0), (0, 0, v)))
    if not np.isfinite(z) or _signature(source_tr, channels, z/v) != _signature(trajectory, channels, t):
        raise ValueError('saved cross geometry/time identity mismatch')
    path = directory/'matrices.npz'
    if hashlib.sha256(path.read_bytes()).hexdigest() != meta.get('matrix_sha256'):
        raise ValueError('saved cross matrix hash mismatch')
    with np.load(path, allow_pickle=False) as source:
        if not all(k in source.files for k in _CROSS_KEYS):
            raise ValueError('saved cross matrix components missing')
        arrays = {k: np.array(source[k]) for k in _CROSS_KEYS}
    bound_meta = dict(meta.get('metadata', {}))
    bound_meta.update(reused_without_cross_reintegration=True,
                      source_result_sha256=hashlib.sha256((directory/'RESULT.json').read_bytes()).hexdigest(),
                      source_matrix_sha256=meta['matrix_sha256'], source_kernel_sha256=kernel_sha,
                      original_order=meta['order'], original_angular=meta['angular'])
    return _bind_cross(trajectory, channels, t, arrays, bound_meta)

