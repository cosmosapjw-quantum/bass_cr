# SPDX-License-Identifier: GPL-3.0-only
"""Identity-pinned saved-grid admission; no physical imports or grid regeneration.

This unit checks byte identity and constructor binding. It makes no claim of
operator parity across runtimes or physical validation.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import io
from pathlib import Path
import platform

import numpy as np

ENERGY_SHA256 = '6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292'
MODELS = ('fullBED', 'legacy')
FIELDS = ('energy_eV', 'state_normalized', 'source_vectors', 'terminal_yields',
          'physical_energy_scale_eV_m3', 'time_s', 'birth_tags')
LEDGERS = ('heat', 'binding_HI', 'binding_HeI', 'excitation_HI',
           'excitation_HeI', 'cutoff_energy', 'ionizations_HI',
           'ionizations_HeI', 'cutoff_number', 'low_cross_energy',
           'low_cross_number')
BIRTH_TAGS = ('direct_0p1_10', 'direct_10_900')


class SavedGridError(ValueError):
    """Fail-closed input/constructor error with a stable machine-readable reason."""
    def __init__(self, reason, detail=''):
        self.reason = reason
        self.detail = str(detail)
        super().__init__(reason + (': ' + self.detail if self.detail else ''))


def _fail(reason, detail=''):
    raise SavedGridError(reason, detail)


def _raw_hash(array):
    if not isinstance(array, np.ndarray) or not array.flags.c_contiguous:
        _fail('ARRAY_NOT_C_CONTIGUOUS')
    return hashlib.sha256(memoryview(array).cast('B')).hexdigest()


def grid_fingerprint(E):
    """C-order raw-byte identity; does not convert dtype or numerical values."""
    return {'shape': list(E.shape), 'dtype': E.dtype.str,
            'raw_C_sha256': _raw_hash(E)}


def _numeric(array, field, shape):
    if not isinstance(array, np.ndarray) or array.shape != shape:
        _fail('INVALID_SHAPE', field)
    if array.dtype.str != '<f8':
        _fail('INVALID_DTYPE', field)
    if not array.flags.c_contiguous:
        _fail('ARRAY_NOT_C_CONTIGUOUS', field)
    if not np.all(np.isfinite(array)):
        _fail('NONFINITE_FIELD', field)


def _validate_energy(E):
    _numeric(E, 'energy_eV', (9600,))
    if not np.all(E > 0):
        _fail('ENERGY_NOT_POSITIVE')
    if not np.all(np.diff(E) > 0):
        _fail('ENERGY_NOT_STRICTLY_ASCENDING')
    if (not np.all(E[:3200] > .1) or E[3199] != 10.
            or not np.all(E[:3200] <= 10.)
            or not np.all(E[3200:] > 10.) or E[-1] != 900.):
        _fail('ENERGY_BOUNDS_OR_SPLIT_MISMATCH')
    if _raw_hash(E) != ENERGY_SHA256:
        _fail('ENERGY_RAW_HASH_MISMATCH')


def _immutable_copy(array):
    # Immutable bytes back the copied array: even setflags(write=True) fails.
    return np.frombuffer(array.tobytes(order='C'), dtype=array.dtype).reshape(array.shape)


def _validate_bundle(arrays):
    missing = set(FIELDS) - set(arrays)
    if missing:
        _fail('MISSING_NPZ_FIELDS', ','.join(sorted(missing)))
    _validate_energy(arrays['energy_eV'])
    for field, shape in (('source_vectors', (9611, 2)),
                         ('terminal_yields', (9611, 2)),
                         ('state_normalized', (2, 9611, 2)),
                         ('time_s', (2,)),
                         ('physical_energy_scale_eV_m3', ())):
        _numeric(arrays[field], field, shape)
    if not np.array_equal(arrays['time_s'], np.array([0., 1.e10])):
        _fail('TIME_IDENTITY_MISMATCH')
    tags = arrays['birth_tags']
    if (tags.shape != (2,) or tags.dtype.kind != 'U'
            or not tags.flags.c_contiguous
            or tuple(tags.tolist()) != BIRTH_TAGS):
        _fail('BIRTH_TAG_IDENTITY_MISMATCH')
    if not np.all(arrays['source_vectors'][9600, :] == 0.):
        _fail('SOURCE_HEAT_NOT_INITIAL_ZERO')
    if not arrays['physical_energy_scale_eV_m3'].item() > 0.:
        _fail('INVALID_PHYSICAL_ENERGY_SCALE')


def _runtime_versions():
    result = {'python': platform.python_version(), 'numpy': np.__version__}
    try:
        result['scipy'] = importlib.metadata.version('scipy')
    except importlib.metadata.PackageNotFoundError:
        result['scipy'] = None
    return result


def preflight_saved_inputs(study: Path, identities: dict):
    """Check BOTH whole files, then all loaded fields, before any physical work.

    The identity argument is INPUT_IDENTITIES['inputs']. Immutable copies retain
    complete stored source/cutoff/counter arrays without projection or rewriting.
    """
    raw_files, file_receipts = {}, {}
    for model in MODELS:
        key = model + '_9600_npz'
        info = identities.get(key)
        if (not isinstance(info, dict) or not isinstance(info.get('path'), str)
                or type(info.get('bytes')) is not int
                or not isinstance(info.get('sha256'), str)):
            _fail('INVALID_INPUT_IDENTITY', key)
        path = Path(study) / info['path']
        try:
            raw = path.read_bytes()
        except OSError as exc:
            _fail('INPUT_READ_FAILED', str(exc))
        digest = hashlib.sha256(raw).hexdigest()
        if len(raw) != info['bytes'] or digest != info['sha256']:
            _fail('INPUT_FILE_IDENTITY_MISMATCH', key)
        raw_files[model] = raw
        file_receipts[model] = {'identity_key': key, 'path': info['path'],
                                'bytes': len(raw), 'sha256': digest}

    bundles, array_receipts = {}, {}
    for model in MODELS:
        try:
            with np.load(io.BytesIO(raw_files[model]), allow_pickle=False) as saved:
                arrays = {field: saved[field] for field in saved.files}
        except (OSError, ValueError, EOFError) as exc:
            _fail('INVALID_NPZ', str(exc))
        _validate_bundle(arrays)
        bundles[model] = {field: _immutable_copy(arrays[field]) for field in FIELDS}
        array_receipts[model] = {field: grid_fingerprint(bundles[model][field])
                                 for field in FIELDS}
    if not np.array_equal(bundles['fullBED']['energy_eV'], bundles['legacy']['energy_eV']):
        _fail('MODEL_ENERGY_ARRAY_MISMATCH')
    receipt = {'schema': 'cr-phys02e-saved-input-preflight.v1',
               'inputs': file_receipts, 'arrays': array_receipts,
               'checks': {'both_file_identities': True, 'all_required_fields': True,
                          'exact_saved_grid_digest': True, 'exact_two_model_grid': True,
                          'source_heat_initial_zero': True, 'read_only_copies': True,
                          'cut_eV': .1, 'split_eV': 10., 'upper_eV': 900.,
                          'grid_cells': [3200, 6400], 'time_s': [0., 1.e10],
                          'birth_tags': list(BIRTH_TAGS)},
               'runtime_versions': _runtime_versions(),
               'physical_G_builds': 0, 'physical_pulse_calls': 0}
    return bundles, receipt


def _method_bindings(parent_class, subclass):
    bindings = {}
    for name, method in parent_class.__dict__.items():
        if name != '__init__' and callable(method):
            same = getattr(subclass, name) is method
            if not same:
                _fail('INHERITED_METHOD_IDENTITY_MISMATCH', name)
            bindings[name] = {'same_parent_object': same,
                              'module': method.__module__,
                              'qualname': method.__qualname__}
    return bindings


def make_saved_grid_cascade(parent_module, energy_eV, *, atomic):
    """Install validated immutable saved E before one inherited generator call."""
    _validate_energy(energy_eV)
    E = _immutable_copy(energy_eV)
    if atomic is None:
        _fail('ATOMIC_OBJECT_REQUIRED')
    if tuple(parent_module.LEDGERS) != LEDGERS:
        _fail('PARENT_LEDGER_IDENTITY_MISMATCH')
    parent_class = parent_module.Cascade

    class SavedGridCascade(parent_class):
        _saved_grid_parent = parent_class

        def __init__(self):
            self.E = E
            self.n = len(self.E)
            self.size = self.n + len(parent_module.LEDGERS)
            self.ix = {name: self.n + k for k, name in enumerate(parent_module.LEDGERS)}
            self.atomic = atomic
            self.sharing_order = 4
            self.quantum_constant = 0.
            self.mesh = (3200, 6400)
            self.normalization_diagnostics = []
            _method_bindings(parent_class, type(self))
            self.G = self._generator()
            _validate_energy(self.E)
            if self.E is not E or not np.array_equal(self.E, energy_eV) or self.E.flags.writeable:
                _fail('POST_CONSTRUCTION_GRID_IDENTITY_MISMATCH')

    return SavedGridCascade()


def operator_identity(cascade):
    """Hash existing CSC storage with memoryviews, without mutating/converting G."""
    G = cascade.G
    if getattr(G, 'format', None) != 'csc' or G.shape != (cascade.size, cascade.size):
        _fail('INVALID_OPERATOR_CSC_SHAPE')
    parent_class = getattr(type(cascade), '_saved_grid_parent', None)
    if parent_class is None:
        _fail('SAVED_GRID_PARENT_BINDING_MISSING')
    _validate_energy(cascade.E)
    return {'schema': 'cr-phys02e-operator-identity.v1',
            'energy_eV': grid_fingerprint(cascade.E),
            'method_bindings': _method_bindings(parent_class, type(cascade)),
            'G': {'format': G.format, 'shape': list(G.shape), 'nnz': int(G.nnz),
                  'arrays': {name: grid_fingerprint(getattr(G, name))
                             for name in ('data', 'indices', 'indptr')}},
            'scientific_parity_claim': False}
