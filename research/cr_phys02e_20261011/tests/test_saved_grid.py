"""SG01--SG05: saved inputs and mocked constructor only; no physical G/pulse."""
from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY / 'src'))
import saved_grid as sg


class SavedGridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.identities = json.loads((STUDY / 'inputs/INPUT_IDENTITIES.json').read_text())['inputs']
        cls.bundles, cls.receipt = sg.preflight_saved_inputs(STUDY, cls.identities)

    def assert_reason(self, reason, function, *args, **kwargs):
        with self.assertRaises(sg.SavedGridError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.reason, reason)

    def load_isolated_parent(self):
        name = 'saved_grid_test_isolated_parent'
        path = STUDY / self.identities['inherited_cascade']['path']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         self.identities['inherited_cascade']['sha256'])
        spec = importlib.util.spec_from_file_location(name, path)
        parent = importlib.util.module_from_spec(spec)
        sys.modules[name] = parent
        spec.loader.exec_module(parent)
        self.addCleanup(sys.modules.pop, name, None)
        return parent

    def test_SG01_actual_both_npz_and_no_physical_import(self):
        self.assertEqual(self.receipt['physical_G_builds'], 0)
        self.assertEqual(self.receipt['physical_pulse_calls'], 0)
        json.dumps(self.receipt)
        for model in sg.MODELS:
            with np.load(STUDY / self.identities[model + '_9600_npz']['path'], allow_pickle=False) as saved:
                for field in sg.FIELDS:
                    result = self.bundles[model][field]
                    self.assertEqual(result.dtype, saved[field].dtype)
                    self.assertTrue(np.array_equal(result, saved[field]))
                    self.assertEqual(result.tobytes(), saved[field].tobytes())
                    self.assertFalse(result.flags.writeable)
                    with self.assertRaises(ValueError):
                        result.setflags(write=True)
            self.assertEqual(sg.grid_fingerprint(self.bundles[model]['energy_eV'])['raw_C_sha256'],
                             sg.ENERGY_SHA256)
        script = '''import json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1]+'/src')
from saved_grid import preflight_saved_inputs
s=Path(sys.argv[1]); ids=json.loads((s/'inputs/INPUT_IDENTITIES.json').read_text())['inputs']
b,r=preflight_saved_inputs(s,ids)
assert 'scipy' not in sys.modules
assert not any('causal_cascade' in k or 'coherent_bed' in k for k in sys.modules)
print(json.dumps({'preflight_only':True,'physical_G_builds':0,'physical_pulse_calls':0}))
'''
        completed = subprocess.run([sys.executable, '-c', script, str(STUDY)],
                                   capture_output=True, text=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(json.loads(completed.stdout)['preflight_only'])

    def test_SG02_second_file_identity_rejects_before_npz_load(self):
        identities = copy.deepcopy(self.identities)
        identities['legacy_9600_npz']['sha256'] = '0' * 64
        with patch.object(sg.np, 'load', side_effect=AssertionError('NPZ LOAD BEFORE BOTH HASHES')) as load:
            self.assert_reason('INPUT_FILE_IDENTITY_MISMATCH', sg.preflight_saved_inputs,
                               STUDY, identities)
            load.assert_not_called()

    def test_SG02_one_ulp_rejects_with_updated_whole_file_identity(self):
        arrays = {k: np.array(v, copy=True) for k, v in self.bundles['legacy'].items()}
        arrays['energy_eV'][100] = np.nextafter(arrays['energy_eV'][100], np.inf)
        self.assert_reason('ENERGY_RAW_HASH_MISMATCH', sg._validate_bundle, arrays)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'mutated_legacy.npz'
            np.savez(path, **arrays)
            raw = path.read_bytes()
            identities = copy.deepcopy(self.identities)
            identities['legacy_9600_npz'] = {'path': str(path), 'bytes': len(raw),
                                             'sha256': hashlib.sha256(raw).hexdigest()}
            self.assert_reason('ENERGY_RAW_HASH_MISMATCH', sg.preflight_saved_inputs,
                               STUDY, identities)

    def test_SG03_invalid_field_matrix(self):
        base = self.bundles['fullBED']
        cases = [
            ('energy_eV', np.zeros(9599, dtype='<f8'), 'INVALID_SHAPE'),
            ('energy_eV', base['energy_eV'].astype('<f4'), 'INVALID_DTYPE'),
            ('energy_eV', base['energy_eV'].astype('>f8'), 'INVALID_DTYPE'),
            ('source_vectors', np.zeros((9600, 2)), 'INVALID_SHAPE'),
            ('source_vectors', np.zeros((9611, 2), dtype=np.int64), 'INVALID_DTYPE'),
            ('terminal_yields', np.zeros((9611, 1)), 'INVALID_SHAPE'),
            ('state_normalized', np.zeros((1, 9611, 2)), 'INVALID_SHAPE'),
            ('time_s', np.array([0., 1.e9]), 'TIME_IDENTITY_MISMATCH'),
            ('birth_tags', np.array(['direct_10_900', 'direct_0p1_10']), 'BIRTH_TAG_IDENTITY_MISMATCH'),
            ('birth_tags', np.array(sg.BIRTH_TAGS, dtype='S13'), 'BIRTH_TAG_IDENTITY_MISMATCH'),
            ('physical_energy_scale_eV_m3', np.array(0.), 'INVALID_PHYSICAL_ENERGY_SCALE'),
            ('physical_energy_scale_eV_m3', np.array(-1.), 'INVALID_PHYSICAL_ENERGY_SCALE'),
            ('physical_energy_scale_eV_m3', np.array([1.]), 'INVALID_SHAPE'),
        ]
        for field, value, reason in cases:
            with self.subTest(field=field, reason=reason, shape=value.shape, dtype=value.dtype):
                arrays = dict(base); arrays[field] = value
                self.assert_reason(reason, sg._validate_bundle, arrays)
        for field in ('energy_eV', 'source_vectors', 'terminal_yields', 'state_normalized',
                      'time_s', 'physical_energy_scale_eV_m3'):
            with self.subTest(nonfinite=field):
                arrays = dict(base); value = np.array(base[field], copy=True)
                value.flat[0] = np.nan; arrays[field] = value
                self.assert_reason('NONFINITE_FIELD', sg._validate_bundle, arrays)
        for index, value, reason in ((0, -1., 'ENERGY_NOT_POSITIVE'),
                                     (100, base['energy_eV'][99], 'ENERGY_NOT_STRICTLY_ASCENDING'),
                                     (0, .1, 'ENERGY_BOUNDS_OR_SPLIT_MISMATCH'),
                                     (3199, 9.999, 'ENERGY_BOUNDS_OR_SPLIT_MISMATCH'),
                                     (9599, 901., 'ENERGY_BOUNDS_OR_SPLIT_MISMATCH')):
            with self.subTest(energy_index=index, reason=reason):
                arrays = dict(base); value_array = np.array(base['energy_eV'], copy=True)
                value_array[index] = value; arrays['energy_eV'] = value_array
                self.assert_reason(reason, sg._validate_bundle, arrays)
        arrays = dict(base); arrays.pop('state_normalized')
        self.assert_reason('MISSING_NPZ_FIELDS', sg._validate_bundle, arrays)
        arrays = dict(base); source = np.array(base['source_vectors'], copy=True)
        source[9600, 0] = 1.e-300; arrays['source_vectors'] = source
        self.assert_reason('SOURCE_HEAT_NOT_INITIAL_ZERO', sg._validate_bundle, arrays)

    def test_SG04_generator_observes_saved_grid_and_inherited_bindings(self):
        parent = self.load_isolated_parent()
        atomic = object()
        calls = []
        E = self.bundles['fullBED']['energy_eV']
        source_before = self.bundles['fullBED']['source_vectors'].tobytes()

        def generator(instance):
            calls.append(instance)
            self.assertEqual(instance.E.tobytes(), E.tobytes())
            self.assertFalse(instance.E.flags.writeable)
            with self.assertRaises(ValueError):
                instance.E.setflags(write=True)
            self.assertEqual(instance.n, 9600)
            self.assertEqual(instance.size, 9611)
            self.assertEqual(instance.ix, {name: 9600 + k for k, name in enumerate(parent.LEDGERS)})
            self.assertIs(instance.atomic, atomic)
            self.assertEqual(instance.sharing_order, 4)
            self.assertEqual(instance.quantum_constant, 0.)
            self.assertEqual(instance.mesh, (3200, 6400))
            self.assertEqual(instance.normalization_diagnostics, [])
            return parent.sparse.csc_matrix((instance.size, instance.size))

        with patch.object(parent.Cascade, '_generator', generator), \
             patch.object(parent.Cascade, '__init__', side_effect=AssertionError('PARENT INIT CALLED')), \
             patch.object(parent, 'energy_grid', side_effect=AssertionError('GRID REGENERATED')) as grid:
            cascade = sg.make_saved_grid_cascade(parent, E, atomic=atomic)
            self.assertEqual(len(calls), 1)
            grid.assert_not_called()
            for name in ('_generator', 'project', '_sharing', 'functionals', 'source_vectors',
                         'augmented', 'evolve', 'terminal_yields', 'summarize'):
                self.assertIs(getattr(type(cascade), name), getattr(parent.Cascade, name))
            arrays_before = {name: getattr(cascade.G, name).tobytes()
                             for name in ('data', 'indices', 'indptr')}
            identity = sg.operator_identity(cascade)
            json.dumps(identity)
            self.assertEqual(identity['G']['shape'], [9611, 9611])
            self.assertEqual(identity['G']['nnz'], 0)
            self.assertFalse(identity['scientific_parity_claim'])
            self.assertTrue(all(v['same_parent_object'] for v in identity['method_bindings'].values()))
            for name, raw in arrays_before.items():
                self.assertEqual(getattr(cascade.G, name).tobytes(), raw)
            changed = np.array(E, copy=True); changed[100] = np.nextafter(changed[100], np.inf)
            self.assert_reason('ENERGY_RAW_HASH_MISMATCH', sg.make_saved_grid_cascade,
                               parent, changed, atomic=atomic)
            self.assertEqual(len(calls), 1)
        self.assertEqual(source_before, self.bundles['fullBED']['source_vectors'].tobytes())

    def test_SG05_inherited_projection_conserves_saved_coordinates(self):
        parent = self.load_isolated_parent()

        def generator(instance):
            return parent.sparse.csc_matrix((instance.size, instance.size))

        with patch.object(parent.Cascade, '_generator', generator):
            cascade = sg.make_saved_grid_cascade(parent, self.bundles['fullBED']['energy_eV'], atomic=object())
        energies = np.array([0., .05, .1, (.1 + cascade.E[0])/2, 10., 10.1, 899., 900.])
        counts = np.array([1., 2., .5, 3., 4., 5., .125, .25])
        energy_functional, number_functional = cascade.functionals()
        for from_high in (False, True):
            projected = cascade.project(energies, counts, from_high=from_high)
            np.testing.assert_allclose(energy_functional @ projected, energies @ counts,
                                       rtol=2.e-13, atol=1.e-12)
            np.testing.assert_allclose(number_functional @ projected, np.sum(counts),
                                       rtol=2.e-13, atol=1.e-12)
            self.assertEqual(projected[cascade.ix['heat']], 0.)
            self.assertGreater(projected[cascade.ix['cutoff_energy']], 0.)
            self.assertGreater(projected[cascade.ix['cutoff_number']], 0.)
            for name in ('binding_HI', 'binding_HeI', 'excitation_HI', 'excitation_HeI',
                         'ionizations_HI', 'ionizations_HeI'):
                self.assertEqual(projected[cascade.ix[name]], 0.)
            if not from_high:
                self.assertEqual(projected[cascade.ix['low_cross_energy']], 0.)
                self.assertEqual(projected[cascade.ix['low_cross_number']], 0.)
            else:
                low = cascade.E <= parent.SPLIT
                np.testing.assert_allclose(projected[cascade.ix['low_cross_energy']],
                                           projected[:cascade.n][low].sum() + projected[cascade.ix['cutoff_energy']],
                                           rtol=2.e-13, atol=1.e-12)
                np.testing.assert_allclose(projected[cascade.ix['low_cross_number']],
                                           np.sum(projected[:cascade.n][low]/cascade.E[low]) + projected[cascade.ix['cutoff_number']],
                                           rtol=2.e-13, atol=1.e-12)

    def test_SG05_exact_energy_vs_number_counterexample(self):
        # One drifting electron 2 -> 1 deposits one energy unit as heat.
        # Fixed energy coordinates use column (1/2, -1, 1/2).
        column = (Fraction(1, 2), Fraction(-1), Fraction(1, 2))
        dot = lambda a, b: sum(x*y for x, y in zip(a, b))
        energy = (Fraction(1), Fraction(1), Fraction(1))
        number_old = (Fraction(1), Fraction(1, 2), Fraction(0))
        number_after_E_rewrite = (Fraction(2, 3), Fraction(1, 2), Fraction(0))
        self.assertEqual(dot(energy, column), 0)
        self.assertEqual(dot(number_old, column), 0)
        self.assertEqual(dot(energy, column), 0)
        self.assertEqual(dot(number_after_E_rewrite, column), Fraction(-1, 6))


if __name__ == '__main__':
    unittest.main()
