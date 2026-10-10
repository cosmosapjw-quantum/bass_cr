"""Pinned FS10 secondary-electron terminal yields; bounded conditional adapter.

Only xHII=xHeII=0.01 (He fraction normalized to He), xHeIII=0.
No source, proton transport, arbitrary-composition or causal-start claim.
The original data retain their MIT distribution notice in vendor/fs10/21cmfast.
This independently written adapter preserves raw values in every result.
"""
from pathlib import Path
import hashlib
import numpy as np

SPECIES = ('HI', 'HeI', 'HeII')
IONIZATION_EV = np.array([13.6, 24.6, 54.4])
PROJECTION_REL_BOUND = 1.0e-4  # fixed before the integration probe
DATA_COMMIT = 'c01373543fb83a721c48cdcbcd0a08ea53afe78c'
TABLES = {
    0.01: {
        'relative_path': 'vendor/fs10/21cmfast/src/py21cmfast/_data/x_int_tables/log_xi_-2.0.dat',
        'sha256': '59a4b1c0467402d65062976d6ca0cae0e810f881b5c2c4b5fe0c82595386571d',
        'header': (0.99, 0.99, 0.01, 10.0, 100.0),
    },
    0.1: {
        'relative_path': 'vendor/fs10/21cmfast/src/py21cmfast/_data/x_int_tables/log_xi_-1.0.dat',
        'sha256': '3a83d09a3741d11f7d667156d8bd2a6d026fb7f624cbea98e58b789b0a9deea5',
        'header': (0.9, 0.9, 0.1, 10.0, 100.0),
    },
}


def table_config(xhii):
    """Return one explicitly acquired FS10 composition knot; never interpolate xi."""
    if not np.isfinite(xhii) or float(xhii) not in TABLES:
        raise ValueError('OUT_OF_DOMAIN: implemented compositions are xHII=xHeII in {.01,.1}, xHeIII=0')
    return TABLES[float(xhii)]


class FS10Table:
    """Cold, static, matched-composition terminal response at one reliable knot.

    ``evaluate`` accepts scalar or array energies in eV. Source knots receive a
    bounded heat-only closure projection, with raw defect retained. Threshold
    guards are separate declared interpolation modifications. No fraction-wide
    renormalization, high-energy clipping, or x interpolation is performed.
    """

    def __init__(self, xhii=0.01, data_path=None):
        config = table_config(xhii)
        self.xhii = float(xhii)
        self.relative_path = config['relative_path']
        self.path = Path(data_path) if data_path is not None else Path(__file__).resolve().parents[1] / self.relative_path
        payload = self.path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != config['sha256']:
            raise ValueError('SOURCE_HASH_MISMATCH')
        header = payload.splitlines()
        try:
            declared = tuple(float(v) for v in header[1].decode('ascii').split())
        except (IndexError, UnicodeDecodeError, ValueError) as exc:
            raise ValueError('INVALID_SOURCE_HEADER') from exc
        if declared != config['header']:
            raise ValueError('SOURCE_HEADER_MISMATCH')
        rows = np.loadtxt(self.path, skiprows=3)
        if rows.shape != (258, 9) or not np.all(np.isfinite(rows)) or np.any(rows < 0):
            raise ValueError('INVALID_SOURCE_ROWS')
        self.raw = rows
        self.energy_eV = rows[:, 0].copy()
        if not np.all(np.diff(self.energy_eV) > 0):
            raise ValueError('INVALID_ENERGY_GRID')
        E = self.energy_eV
        self._raw_heat = E * rows[:, 2]
        self._exc = E * rows[:, 3]
        self._counts = rows[:, 5:8].copy()
        self._raw_defect = self._raw_heat + self._exc + self._counts @ IONIZATION_EV - E
        if np.any(np.abs(self._raw_defect) > PROJECTION_REL_BOUND * E):
            raise ValueError('SOURCE_ENERGY_DEFECT_EXCEEDS_FIXED_BOUND')
        self._closed_heat = self._raw_heat - self._raw_defect
        if np.any(self._closed_heat < 0):
            raise ValueError('PROJECTION_NEGATIVE_HEAT')
        for j, threshold in enumerate(IONIZATION_EV):
            if np.any(self._counts[E < threshold, j] != 0):
                raise ValueError('SOURCE_SUBTHRESHOLD_IONIZATION')
        if np.any(10.2 * rows[:, 4] > self._exc + 2e-5 * E):
            raise ValueError('LYA_EXCEEDS_EXCITATION_BUDGET')
        self.audit = {
            'source_commit': DATA_COMMIT, 'source_sha256': config['sha256'],
            'source_relative_path': self.relative_path,
            'source_xHII': self.xhii, 'source_xHeII_per_He': self.xhii, 'source_xHeIII': 0.0,
            'source_header_z': 10.0, 'source_header_T_K': 100.0,
            'helium_abundance': 'TABLE_GENERATION_VALUE_NOT_CERTIFIED; original example nHe/(nH+nHe)=0.08',
            'energy_domain_eV': [float(E[0]), float(E[-1])],
            'subthreshold_domain_eV': [0.0, float(E[0])],
            'secondary_ionization_potentials_eV': IONIZATION_EV.tolist(),
            'threshold_precision_claim': 'DECLARED_STANDARD_APPROXIMATE; NOT_RECOVERED_MC_CONSTANTS',
            'projection_type': 'BOUNDED_NUMERICAL_HEAT_CLOSURE_PROJECTION_NOT_PRINTED_ROUNDING_ONLY',
            'fixed_relative_projection_bound': PROJECTION_REL_BOUND,
            'max_raw_fraction_sum_residual': float(np.max(abs(rows[:, 1:4].sum(axis=1)-1))),
            'max_event_relative_energy_defect': float(np.max(abs(self._raw_defect / E))),
            'max_abs_heat_projection_eV': float(np.max(abs(self._raw_defect))),
            'max_abs_ion_fraction_vs_counts_residual': float(np.max(abs(self._counts @ IONIZATION_EV / E-rows[:, 1]))),
            'deposition_mode': 'QUASISTATIC_TERMINAL_CASCADE; NOT_A_CAUSAL_TURN_ON_SOLUTION',
            'interpolation': 'linear energy/channel-energy and count interpolation; explicit threshold anchors/guards',
            'source_grid_count': len(E),
        }

    def evaluate(self, E_eV):
        E = np.asarray(E_eV, dtype=float)
        scalar = E.ndim == 0
        if np.any(~np.isfinite(E)) or np.any(E < 0) or np.any(E > self.energy_eV[-1]):
            raise ValueError('OUT_OF_DOMAIN: finite 0 <= electron energy <= 9937.21 eV required')
        interp = lambda y: np.interp(E, self.energy_eV, y)
        below = E < self.energy_eV[0]
        raw_heat = np.where(below, E, interp(self._raw_heat))
        raw_exc = np.where(below, 0.0, interp(self._exc))
        base_heat_projection = np.where(below, 0.0, -interp(self._raw_defect))
        counts = []
        for j, threshold in enumerate(IONIZATION_EV):
            # An exact zero threshold anchor prevents interpolation leakage.
            ge = self.energy_eV > threshold
            support_E = np.r_[threshold, self.energy_eV[ge]]
            support_N = np.r_[0.0, self._counts[ge, j]]
            counts.append(np.where(E <= threshold, 0.0, np.interp(E, support_E, support_N)))
        counts = np.stack(counts, axis=-1)
        exc = np.where(E < 10.2, 0.0, raw_exc)
        lya = np.where(E < 10.2, 0.0, interp(self.raw[:, 4]))
        ion_e = counts * IONIZATION_EV
        heat = E - exc - ion_e.sum(axis=-1)
        if np.any(heat < -2e-12 * np.maximum(E, 1)):
            raise ValueError('INTERPOLATION_NEGATIVE_HEAT')
        heat = np.maximum(heat, 0.0)
        correction = heat - raw_heat
        threshold_correction = correction - base_heat_projection
        raw_counts = np.stack([np.where(below, 0.0, interp(self._counts[:, j])) for j in range(3)], axis=-1)
        raw_defect = raw_heat + raw_exc + (raw_counts * IONIZATION_EV).sum(axis=-1) - E
        val = lambda x: float(x) if scalar else x
        # Raw fractions are descriptive only; interpolation acts on energies.
        frac = lambda column: np.where(below, 0.0, interp(self.raw[:, column]))
        return {
            'energy_eV': val(E), 'heat_eV': val(heat), 'excitation_eV': val(exc),
            'ionization_counts': {s: val(counts[..., j]) for j, s in enumerate(SPECIES)},
            'ionization_energy_eV': {s: val(ion_e[..., j]) for j, s in enumerate(SPECIES)},
            'lya_count': val(lya), 'raw_heat_eV': val(raw_heat), 'raw_excitation_eV': val(raw_exc),
            'raw_fion': val(frac(1)), 'raw_fheat': val(np.where(below, 1.0, interp(self.raw[:, 2]))),
            'raw_fexc': val(frac(3)),
            'raw_fraction_sum_residual': val(np.where(below, 0.0, interp(self.raw[:, 1:4].sum(axis=1)-1))),
            'event_energy_residual_eV': val(raw_defect),
            'correction_eV': val(correction),
            'source_projection_correction_eV': val(base_heat_projection),
            'threshold_interpolation_correction_eV': val(threshold_correction),
            'resolved_subthreshold_heat_eV': val(np.where(below, E, 0.0)),
            'closed_energy_residual_eV': val(heat+exc+ion_e.sum(axis=-1)-E),
            'closure_status': 'CLOSED_CONDITIONAL_TERMINAL_KERNEL',
            'deposition_mode': self.audit['deposition_mode'],
        }


def electron_loss_timescale_estimate(E_eV, z=10.0, xhii=0.01):
    """FS10 Eqs.(8-10), approximate 1-keV based diagnostic, not solved cascade.

    Returns instantaneous E/b estimates and their harmonic combination in years.
    Near atomic thresholds or finite cells these are not a cascade-delay bound.
    """
    E = np.asarray(E_eV, dtype=float)
    if np.any(E <= 0) or z < 0 or not 0 < xhii < 1:
        raise ValueError('INVALID_TIMESCALE_INPUT')
    common = (E / 1000.0)**1.5 * ((1.0+z)/10.0)**-3
    tcoul = 5e3/xhii * common
    thion = 5e5/(1-xhii) * common
    tatomic = 1/(1/tcoul + 1/thion)
    tics = 1e8*((1.0+z)/10.0)**-4
    return {'coulomb_year': tcoul, 'HI_ionization_year': thion,
            'atomic_combined_year': tatomic, 'ICS_year': tics,
            'atomic_over_ICS': tatomic/tics,
            'status': 'APPROXIMATE_E_OVER_B_NOT_FULL_CASCADE_DELAY'}
