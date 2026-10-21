"""Independent full-Frobenius initial stresses on the immutable PR147 source.

Reuse the original 40-state CanonicalFVSpecies RHS and DOP853 integrator.
The initial massive FV distribution is rebuilt and normalized for every A.
No old C21L trajectory is executed by this module.

Units: source H and shear s use proper time [s^-1], pressures use J/m^3.
Thus K_t = c^2 kappa_E = 8*pi*G/c^2. Equivalently use kappa_E with
H_geom=H/c. Full Frobenius = sqrt(2) times the source half-contraction.
"""
from __future__ import annotations

import os
for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
              'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_name] = '1'

import copy
import hashlib
import math
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
C21L = HERE.parent / 'cr_c21l_rei_pilot_20261021'
sys.path.insert(0, str(C21L))
import adapter as parent

SOURCE_COMMIT = '3b85dedce84d37b3e165da00685a8a984950aafe'
SETTINGS = dict(parent.SETTINGS)
SETTINGS['massive_A'] = 'independently inverted in [-1,2]'
KAPPA_ENERGY_SI = 8 * math.pi * parent.G_SI / parent.C_SI**4
KAPPA_TIME_SI = 8 * math.pi * parent.G_SI / parent.C_SI**2
AXIS_ATOL = 2e-13


def component_fields(d):
    """Signed LRS scalar and norm for each actually present source sector.

    Source Pi_*_J_m3 means p_X=Delta p_X/3, not a tensor norm.
    Tensor diagonal is (-p_X,-p_X,2p_X), hence |pi_X|=sqrt(6)|p_X|.
    The isotropic dust is modeled with zero stress; no unmodeled species
    is represented by a numerical zero here.
    """
    h = float(d['H'])
    if not math.isfinite(h) or h <= 0:
        raise ValueError('NONPOSITIVE_H')
    p = {sector: float(d[key]) for sector, key in (
        ('m', 'Pi_matter_J_m3'), ('gamma', 'Pi_gamma_J_m3'),
        ('nu', 'Pi_nu_J_m3'))}
    p['r'] = p['gamma'] + p['nu']
    p['tot'] = p['m'] + p['r']
    if not all(math.isfinite(v) for v in p.values()):
        raise ValueError('NONFINITE_STRESS')
    out = {'signed_Sigma_F': math.sqrt(6) * float(d['s']) / h}
    out['Sigma_F'] = abs(out['signed_Sigma_F'])
    out['Sigma_half'] = out['Sigma_F'] / math.sqrt(2)
    factor = math.sqrt(6) * KAPPA_TIME_SI / h**2
    for sector, value in p.items():
        out['p_' + sector + '_J_m3'] = value
        out['delta_p_' + sector + '_J_m3'] = 3 * value
        out['signed_Pi_' + sector + '_F'] = factor * value
        out['Pi_' + sector + '_F'] = abs(factor * value)
        out['Pi_' + sector + '_half'] = abs(factor * value) / math.sqrt(2)
    denom = abs(p['m']) + abs(p['r'])
    out['cancellation_fraction'] = None if denom == 0 else 1 - abs(p['tot']) / denom
    return out


def _new_momentum(amplitude, optimized):
    # Recreate source weight, cell populations AND reference energy norm.
    # Sharing a previous distribution and changing .amplitude is forbidden.
    momentum = parent.CanonicalMomentumFV(30., float(amplitude), 24, 12, gauss_order=3)
    if optimized:
        momentum.__class__ = parent.ExactReuseMomentum
        momentum._one_minus_mu2 = 1 - momentum._mu2
        momentum._one_minus_mu2.flags.writeable = False
        momentum._min_cell = float(np.min(momentum._cell_numbers))
    return momentum


def _set_shear(obj, signed_sigma):
    """Map a requested actual s/H into the source's Sigma_ref argument.

    Explicitly use the actual discrete normalized massive energy in Hbase.
    This avoids treating the source parameter as an exact actual invariant
    if the finite-precision reference normalization differs from unity.
    """
    obj.Sigma_ref = 0.
    obj.orientation = 0
    hbase = float(obj.fields(0., obj.initial_state())['H'])
    q = signed_sigma * hbase / (obj.source.href * math.sqrt(6 - signed_sigma**2))
    obj.Sigma_ref = math.sqrt(3) * abs(q) / math.sqrt(1 + q*q)
    obj.orientation = int(np.sign(q))


class IndependentStressBuilder:
    """One immutable parent angular/operator template per process.

    This builder exposes a common gamma/nu initial quadrupole k, as in C21L.
    The species remain separately present in the full source state and output.
    Independent gamma-versus-neutrino targets are a separate input extension.
    """
    def __init__(self, *, optimized=True):
        self.source_manifest = parent.verify_source()
        self.optimized = bool(optimized)
        self.template = parent.make_template(optimized=self.optimized)

    def identity(self):
        return {
            'builder_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'parent_adapter_sha256': hashlib.sha256((C21L / 'adapter.py').read_bytes()).hexdigest(),
            'source_manifest_sha256': hashlib.sha256((C21L / 'SOURCE_MANIFEST.json').read_bytes()).hexdigest(),
            'source_commit': SOURCE_COMMIT,
            'source_files': self.source_manifest['files'],
            'settings': SETTINGS,
            'optimized_exact_reuse_moments': self.optimized,
            'norm': 'full Frobenius; sqrt(2) times half-contraction',
            'pressure_unit': 'J/m^3',
            'clock': 'cosmic proper time [s]',
            'kappa_energy_SI': KAPPA_ENERGY_SI,
            'kappa_time_SI': KAPPA_TIME_SI,
            'radiation_initial_family': 'common k_gamma=k_nu; both sectors present',
        }

    def build(self, signed_sigma, signed_pi_m, signed_pi_r):
        targets = tuple(map(float, (signed_sigma, signed_pi_m, signed_pi_r)))
        if not all(map(math.isfinite, targets)) or abs(targets[0]) >= math.sqrt(6):
            raise ValueError('INVALID_FULL_FROBENIUS_TARGET: finite values and |S0|<sqrt(6) required')
        signed_sigma, signed_pi_m, signed_pi_r = targets
        obj = copy.copy(self.template)
        obj.k_gamma = obj.k_nu = 0.
        obj._nfev = 0

        def matter_at(amplitude):
            obj.momentum = _new_momentum(amplitude, self.optimized)
            _set_shear(obj, signed_sigma)
            return component_fields(obj.fields(0., obj.initial_state()))['signed_Pi_m_F']

        lower, upper = matter_at(-1.), matter_at(2.)
        if not lower <= signed_pi_m <= upper:
            raise ValueError('UNREALIZABLE_MATTER_TARGET: requested '
                             f'{signed_pi_m:.17g}; attainable full signed Pi_m '
                             f'[{lower:.17g}, {upper:.17g}] for S0={signed_sigma:.17g}')
        # Preserve the exact isotropic massive source whenever its existing
        # FP value is consistent with a requested physical zero. Retain that
        # tiny realized offset; do not clip a raw stress to zero.
        at_zero = matter_at(0.)
        if signed_pi_m == 0. and abs(at_zero) <= AXIS_ATOL:
            amplitude = 0.
        elif signed_pi_m == lower:
            amplitude = -1.
        elif signed_pi_m == upper:
            amplitude = 2.
        else:
            amplitude = float(brentq(lambda a: matter_at(a) - signed_pi_m,
                                    -1., 2., xtol=1e-13, rtol=1e-14))
        matter_at(amplitude)
        zero = component_fields(obj.fields(0., obj.initial_state()))
        obj.k_gamma = obj.k_nu = .5
        half = component_fields(obj.fields(0., obj.initial_state()))
        slope = 2 * (half['signed_Pi_r_F'] - zero['signed_Pi_r_F'])
        if not math.isfinite(slope) or slope <= 0:
            raise ArithmeticError('INVALID_SOURCE_RADIATION_SLOPE')
        k = (signed_pi_r - zero['signed_Pi_r_F']) / slope
        if not math.isfinite(k) or abs(k) > .5:
            lo = zero['signed_Pi_r_F'] - .5 * slope
            hi = zero['signed_Pi_r_F'] + .5 * slope
            raise ValueError('UNREALIZABLE_RADIATION_TARGET: requested '
                             f'{signed_pi_r:.17g}; source-admitted full signed Pi_r '
                             f'[{lo:.17g}, {hi:.17g}] with |k|<=0.5')
        obj.k_gamma = obj.k_nu = float(k)
        y0 = obj.initial_state()
        fields = obj.fields(0., y0)
        actual = component_fields(fields)
        errors = dict(zip(('Sigma_F', 'Pi_m_F', 'Pi_r_F'),
                         (abs(actual[key] - target) for key, target in zip(
                             ('signed_Sigma_F', 'signed_Pi_m_F', 'signed_Pi_r_F'), targets))))
        if max(errors.values()) > AXIS_ATOL:
            raise ArithmeticError('INITIAL_COMPONENT_MAPPING_DISCREPANCY:' + repr(errors))
        m = obj.momentum.moments(0., 0.)
        continuum_min_Wm = min(1 + amplitude, 1 - amplitude/2)
        continuum_min_Wr = min(1 + k, 1 - k/2)
        hres = abs(fields['Einstein_H2'] / fields['H']**2 - 1)
        if (m.min_cell_number < 0 or continuum_min_Wm < 0 or continuum_min_Wr < 0
                or hres > 2e-13 or abs(m.rho - 1) > 2e-13):
            raise ArithmeticError('INITIAL_POSITIVITY_NORMALIZATION_CONSTRAINT')
        receipt = {
            'targets_signed_full_Frobenius': dict(zip(('Sigma', 'Pi_m', 'Pi_r'), targets)),
            'actual': actual,
            'axis_absolute_errors': errors,
            'A_m': amplitude,
            'k_gamma': k,
            'k_nu': k,
            'source_Sigma_ref_half': obj.Sigma_ref,
            'source_orientation': obj.orientation,
            'source_q': float(y0[2]),
            'attainable_matter_signed_full': [lower, upper],
            'attainable_radiation_signed_full': [-.5*slope, .5*slope],
            'continuum_min_W_m': continuum_min_Wm,
            'continuum_min_W_r': continuum_min_Wr,
            'massive_reference_energy_norm': obj.momentum.reference_energy_norm,
            'massive_total_cell_number': obj.momentum.total_cell_number,
            'massive_initial_rho_normalized': m.rho,
            'minimum_massive_cell_number': m.min_cell_number,
            'Hamiltonian_relative_residual': hres,
            'massive_distribution_rebuilt': True,
            'original_RHS_and_integrator_unchanged': True,
            'state_count': len(y0),
            'species': {'matter_massive': 'PRESENT', 'matter_dust': 'PRESENT_ISOTROPIC',
                        'photons': 'PRESENT', 'neutrinos': 'PRESENT_MASSLESS',
                        'UV': 'ABSENT_FROM_MODEL', 'baryonic_anisotropic_stress': 'UNMODELED'},
            'global_error_bound': None,
        }
        return obj, receipt


def solve_case(builder, signed_sigma, signed_pi_m, signed_pi_r):
    """Execute only an explicitly selected new case with the original solver.

    Caller owns create-only run identity, deduplication and resource admission.
    No main entry point starts science automatically.
    """
    obj, mapping = builder.build(signed_sigma, signed_pi_m, signed_pi_r)
    sol, diag, seconds = obj.integrate(n=SETTINGS['n'], rtol=SETTINGS['rtol'], atol=SETTINGS['atol'])
    history = {'eta': sol.t, 'Y': sol.y,
               'proper_elapsed_s': sol.y[0] / obj.source.href}
    for key, value in diag[0].items():
        if isinstance(value, (float, int, np.floating, np.integer)):
            history[key] = np.array([d[key] for d in diag], dtype=np.float64)
    for key in ('E_gamma', 'N_gamma', 'E_nu', 'N_nu'):
        history[key] = np.stack([d[key] for d in diag])
    components = [component_fields(d) for d in diag]
    for key in components[0]:
        history[key] = np.array([np.nan if d[key] is None else d[key] for d in components], dtype=np.float64)
    if sol.y.dtype != np.float64 or sol.y.shape != (40, SETTINGS['n']):
        raise ArithmeticError('FULL_FP64_STATE_SHAPE')
    for key, value in history.items():
        if key != 'cancellation_fraction' and not np.isfinite(value).all():
            raise ArithmeticError('NONFINITE_HISTORY:' + key)
    constraint = max(abs(d['Einstein_H2']/d['H']**2 - 1) for d in diag)
    number = max(max(abs(d['N_gamma'][0]-1), abs(d['N_nu'][0]-1)) for d in diag)
    mincell = min(d['massive_min_cell_population'] for d in diag)
    mnumber = float(np.max(abs(history['massive_physical_number_norm'] * np.exp(3*sol.t)
                               / obj.momentum.total_cell_number - 1)))
    if constraint > 2e-13 or number > 2e-10 or mincell < 0 or mnumber > 2e-13:
        raise ArithmeticError('CONSTRAINT_NUMBER_POSITIVITY')
    receipt = {'mapping': mapping, 'nfev': int(sol.nfev), 'solver_wall_s': seconds,
               'state_shape': list(sol.y.shape), 'dtype': str(sol.y.dtype),
               'diagnostics': {'Hamiltonian_max_relative': constraint,
                               'radiation_number_max_abs': number,
                               'massive_comoving_number_max_relative': mnumber,
                               'min_massive_cell_number': mincell},
               'endpoint': components[-1], 'global_error_bound': None}
    return receipt, history
