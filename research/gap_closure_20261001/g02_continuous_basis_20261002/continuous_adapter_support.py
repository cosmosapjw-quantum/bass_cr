"""Identity guards; no numerical operator or quadrature changes."""
import hashlib
import numpy as np
import operator_bootstrap
from bass_foundations.radial_basis import FEMRadial
from basis_representation import ContinuousRadial


def radial_fingerprint(radial):
    if type(radial) is FEMRadial:
        coef = np.asarray(radial.polynomial_coefficients)
        if np.iscomplexobj(coef):
            raise ValueError('real radial coefficient payload required')
        if not np.isfinite(coef).all():
            raise ValueError('finite radial coefficient payload required')
        return (radial.l, float(radial.energy), hashlib.sha256(coef.tobytes()).hexdigest())
    if type(radial) is ContinuousRadial:
        radial.payload_fingerprint()
        return (radial.l, float(radial.energy), radial.identity)
    raise ValueError('unrecognized radial representation')


def validate_radial_channel_types(channels):
    kinds = {type(c.radial) for c in channels}
    if len(kinds) != 1 or not kinds <= {FEMRadial, ContinuousRadial}:
        raise ValueError('one recognized finite radial representation required')
    seen = {}
    for channel in channels:
        radial = channel.radial
        fp = radial_fingerprint(radial)
        if radial.identity in seen and seen[radial.identity] != fp:
            raise ValueError('inconsistent radial identity payload')
        seen[radial.identity] = fp


def validate_cross_channels(channels, edges, order, batch):
    """Original fast_cross._validate, with only the radial type guard extended."""
    ch = tuple(channels)
    if not ch or len(ch) > 128:
        raise ValueError('finite radial channels required')
    validate_radial_channel_types(ch)
    if any(c.radial.l not in (0, 1) for c in ch):
        raise ValueError('optimized kernel admits s+p only; use reference for l>1')
    e = np.asarray(edges, float)
    if (e.ndim != 1 or len(e) < 2 or e[0] != 0 or not np.isfinite(e).all()
            or np.any(np.diff(e) <= 0) or any(not np.array_equal(c.radial.edges, e) for c in ch)):
        raise ValueError('identical strictly increasing radial edges required')
    if isinstance(order, bool) or not isinstance(order, int) or not 2 <= order <= 64:
        raise ValueError('order must be 2..64')
    if isinstance(batch, bool) or not isinstance(batch, int) or not 1 <= batch <= 4096:
        raise ValueError('batch must be 1..4096')
    if len({(c.center, c.radial.identity, c.m) for c in ch}) != len(ch):
        raise ValueError('duplicate channels')
    groups = [tuple(c for c in ch if c.center == j) for j in (0, 1)]
    if not all(groups):
        raise ValueError('both centers required')
    return groups, e


def representation_metadata(channels):
    validate_radial_channel_types(channels)
    return {'radial_representation': ('SHARED_ENDPOINT_BUBBLE_R4X'
            if type(channels[0].radial) is ContinuousRadial else 'ORIGINAL_FEM_MONOMIAL'),
            'adapter': 'R4X_DIAGNOSTIC_ONLY', 'archived_context_compatible': False}
