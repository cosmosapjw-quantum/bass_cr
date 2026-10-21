"""PR147-exact immutable quadrature preparation for independent A trials.

Only A-independent constructor work is cached. Every call regenerates W,
packets, cell populations, reference energy normalization and number sum.
The source moment/RHS/integrator and all floating reduction orders are reused.

The immutable-bytes backing pattern follows REI ACCEL01 cached_context.py
(source 526870b3; exact full identity is recorded in EXTERNAL_REUSE.json).
Its C15 solver and (x,b) result cache are not imported into this PR147 family.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import math
from pathlib import Path
import sys
from types import MappingProxyType

import numpy as np
from numpy.polynomial.legendre import leggauss

C21L = Path(__file__).resolve().parent.parent / 'cr_c21l_rei_pilot_20261021'
sys.path.insert(0, str(C21L))
import adapter as parent


def immutable_exact(array):
    """Byte-preserving C-contiguous array whose backing bytes are immutable."""
    arr = np.asarray(array)
    return np.frombuffer(arr.tobytes(order='C'), dtype=arr.dtype).reshape(arr.shape)


def _signature(arr):
    return (id(arr), arr.dtype.str, arr.shape, arr.strides, arr.flags.writeable)


@dataclass(frozen=True, eq=False)
class PreparedMomentumFactory:
    """One immutable geometry/mass-shell preparation per science worker.

    Configuration validation is the same as CanonicalMomentumFV. Python's
    metadata is also checked before use: read-only data alone does not prevent
    an ndarray shape or stride assignment. This is not a hostile-memory model.
    """
    mass: float = 30.
    radial_cells: int = 24
    angular_cells: int = 12
    gauss_order: int = 3
    _arrays: object = field(init=False, repr=False)
    _signatures: object = field(init=False, repr=False)
    _configuration: tuple = field(init=False, repr=False)

    def __post_init__(self):
        mass, nr, nm, ng = self.mass, self.radial_cells, self.angular_cells, self.gauss_order
        if not (math.isfinite(mass) and 3 <= mass <= 1e5):
            raise ValueError('mass/Tref outside BASS exploratory domain')
        if not (isinstance(nr, int) and isinstance(nm, int)
                and 4 <= nr <= 256 and 4 <= nm <= 128):
            raise ValueError('canonical cell resolution not supported')
        if ng not in (2, 3, 4):
            raise ValueError('positive subcell Gauss order must be 2,3,4')
        object.__setattr__(self, 'mass', float(mass))
        # Expressions below preserve the source's operation order exactly.
        z, w = leggauss(ng)
        tr = np.linspace(-1., 1., nr + 1)
        tm = np.linspace(-1., 1., nm + 1)
        hr, hm = np.diff(tr) / 2, np.diff(tm) / 2
        rr = (tr[:-1] + hr)[:, None] + hr[:, None] * z[None, :]
        aa = (tm[:-1] + hm)[:, None] + hm[:, None] * z[None, :]
        wt = (hr[:, None] * w[None, :]).reshape(-1)
        wm = (hm[:, None] * w[None, :] / 2).reshape(-1)
        q = 3 * (1 + rr.reshape(-1)) / (1 - rr.reshape(-1))
        jac = 6 / (1 - rr.reshape(-1))**2
        fd = np.exp(-q) / (1 + np.exp(-q))
        radial_number = wt * jac * q * q * fd
        mu = aa.reshape(-1)
        # Do NOT cache P2=(3*mu*mu-1)/2: moving /2 before *A changes FP order.
        numerator = 3 * mu * mu - 1
        arrays = {
            'q': immutable_exact(q),
            'mu2': immutable_exact(mu * mu),
            'angular_numerator': immutable_exact(numerator),
            'wm': immutable_exact(wm),
            'radial_number': immutable_exact(radial_number),
            'initial_E': immutable_exact(np.hypot(self.mass, q)),
            'one_minus_mu2': immutable_exact(1 - (mu * mu)),
        }
        object.__setattr__(self, '_arrays', MappingProxyType(arrays))
        object.__setattr__(self, '_signatures', tuple((k, _signature(v)) for k, v in arrays.items()))
        object.__setattr__(self, '_configuration', (self.mass, nr, nm, ng))

    def _check(self):
        if self._configuration != (self.mass, self.radial_cells, self.angular_cells, self.gauss_order):
            raise RuntimeError('PREPARED_CONFIGURATION_CHANGED')
        if tuple((k, _signature(v)) for k, v in self._arrays.items()) != self._signatures:
            raise RuntimeError('PREPARED_ARRAY_METADATA_CHANGED')

    def identity(self):
        self._check()
        return {
            'schema': 'C21N_PREPARED_MOMENTUM_V1',
            'configuration': list(self._configuration),
            'array_sha256': {k: hashlib.sha256(v.tobytes()).hexdigest()
                             for k, v in self._arrays.items()},
            'amplitude_dependent_quantities_rebuilt':
                ['W', 'packets', 'cell_numbers', 'reference_energy_norm', 'number_sum', 'min_cell'],
            'floating_reassociation': False,
            'solver_or_moment_formula_changed': False,
        }

    def make(self, amplitude, *, optimized=True):
        self._check()
        if not (math.isfinite(amplitude) and -1 <= amplitude <= 2):
            raise ValueError('nonpositive initial angular distribution')
        amplitude = float(amplitude)
        a = self._arrays
        W = 1 + amplitude * a['angular_numerator'] / 2
        if np.any(W < 0):
            raise ArithmeticError('positive source f violated')
        packets = a['radial_number'][:, None] * (a['wm'] * W)[None, :]
        if not np.all(packets >= 0) or not np.isfinite(packets).all():
            raise ValueError('negative/nonfinite canonical cell number')
        cell_mass = packets.reshape(self.radial_cells, self.gauss_order,
                                    self.angular_cells, self.gauss_order).sum(axis=(1, 3))
        norm = float(np.sum(packets * a['initial_E'][:, None]))
        if norm <= 0:
            raise ArithmeticError('no positive physical reference rho')
        if np.min(cell_mass) < 0:
            raise ArithmeticError('negative cell mass')
        cls = parent.ExactReuseMomentum if optimized else parent.CanonicalMomentumFV
        obj = cls.__new__(cls)
        obj.mass, obj.amplitude = self.mass, amplitude
        obj.radial_cells, obj.angular_cells = self.radial_cells, self.angular_cells
        obj.gauss_order = self.gauss_order
        obj.reference_energy_norm = norm
        obj._q = a['q'][:, None]
        obj._mu2 = a['mu2'][None, :]
        obj._numbers = immutable_exact(packets)
        obj._cell_numbers = immutable_exact(cell_mass)
        obj._number_sum = float(np.sum(cell_mass))
        if optimized:
            obj._one_minus_mu2 = a['one_minus_mu2'][None, :]
            obj._min_cell = float(np.min(cell_mass))
        return obj
