"""New adapter tests on byte-preserved F05 records; no evaluator calls."""
import copy
import json
import shutil
import tempfile
from fractions import Fraction
from pathlib import Path
import unittest

from receiver_binding import bind_record, decode, frame_sources, verify_archive, Context, History

INPUT = Path(__file__).parent / 'inputs'


class BindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = Context.from_capsule(INPUT)
        cls.rows = [json.loads(x) for x in (INPUT/'level_0_sample.jsonl').read_text().splitlines()]

    def test_actual_output_order_and_once_normalization(self):
        r = bind_record(self.rows[0], self.context)
        self.assertEqual(len(r['values_hex']), 25)
        self.assertEqual(r['values_hex'][7], (self.rows[0]['events']['photo'][0][0]/self.context.nh).hex())
        self.assertEqual(r['event_escape_exact_ratios'][0], str(Fraction(self.rows[0]['events']['photo'][0][0])/Fraction(self.context.nh)))
        self.assertEqual(r['values_hex'][:7], [v.hex() for v in self.rows[0]['sites'][2]['center']])

    def test_incremental_escape_not_cumulative(self):
        d = self.rows[1]; r = bind_record(d, self.context)
        expected = (Fraction(d['state'][7])-Fraction(d['old_state'][7]))/(Fraction(self.context.nh)*Fraction(self.context.ev))
        self.assertEqual(r['event_escape_exact_ratios'][-1], str(expected))
        self.assertNotEqual(expected, Fraction(d['state'][7])/(Fraction(self.context.nh)*Fraction(self.context.ev)))

    def test_discarded_full_not_used(self):
        a = bind_record(self.rows[0], self.context)
        d = copy.deepcopy(self.rows[0]); d['sites'][0]['center'][0] = d['sites'][0]['box'][0][0]
        self.assertEqual(a, bind_record(d, self.context))

    def test_rejection_cannot_supply_outputs(self):
        d = copy.deepcopy(self.rows[0]); d['accepted'] = False
        self.assertIsNone(bind_record(d, self.context))

    def test_model_mismatch(self):
        d = copy.deepcopy(self.rows[0]); d['model_id'] = 'EXPANDING'
        with self.assertRaisesRegex(ValueError, 'MODEL'): bind_record(d, self.context)

    def test_wrong_half_order(self):
        d = copy.deepcopy(self.rows[0]); d['sites'][1],d['sites'][2] = d['sites'][2],d['sites'][1]
        with self.assertRaisesRegex(ValueError, 'SITE'): bind_record(d, self.context)

    def test_wrong_half_step(self):
        d = copy.deepcopy(self.rows[0]); d['sites'][1]['step_s'] *= 2
        with self.assertRaisesRegex(ValueError, 'SITE_STEP'): bind_record(d, self.context)

    def test_normalization_and_state_mismatch(self):
        d = copy.deepcopy(self.rows[0]); d['state'][4] *= 2
        with self.assertRaisesRegex(ValueError, 'STATE_CENTER'): bind_record(d, self.context)

    def test_strict_gate_not_relaxed(self):
        d = copy.deepcopy(self.rows[0]); d['local_bounds'][0] = 2e-4
        with self.assertRaisesRegex(ValueError, 'LOCAL'): bind_record(d, self.context)

    def test_missing_events_not_zero(self):
        d = copy.deepcopy(self.rows[0]); del d['events']
        with self.assertRaisesRegex(ValueError, 'SCHEMA'): bind_record(d, self.context)

    def test_nonfinite_and_boolean_numeric_rejected(self):
        for value in [float('nan'), True]:
            d = copy.deepcopy(self.rows[0]); d['events']['dr'][0] = value
            with self.assertRaises(ValueError): bind_record(d, self.context)

    def test_time_and_parent_chain(self):
        h = History(self.context); h.add(self.rows[0]); h.add(self.rows[1])
        self.assertEqual(h.accepted, 2)
        for key in ['t0_s','old_state','parent_center','parent_box']:
            d = copy.deepcopy(self.rows[1])
            if key == 't0_s': d[key] += 1
            elif key == 'parent_box': d[key][0][0] -= 1e-8
            else: d[key][0] += 1e-8
            h = History(self.context);h.add(self.rows[0])
            with self.assertRaises(ValueError): h.add(d)

    def test_rejected_trial_does_not_advance_time(self):
        h = History(self.context)
        d = copy.deepcopy(self.rows[0]);d['accepted'] = False
        self.assertIsNone(h.add(d));h.add(self.rows[0])
        self.assertEqual((h.accepted,h.rejected), (1,1))

    def test_source_frames_and_corruption(self):
        b = (INPUT/'source_identity.dat').read_bytes();frames = frame_sources(b)
        self.assertEqual(len(frames),22)
        self.assertIn('rust/rei_microphysics/src/ft03_rates.rs',frames)
        for broken in [b[:-1], b'WRONG\n'+b, b+b'rust/rei_microphysics/src/ft03_rates.rs 1\nx\n']:
            with self.assertRaises(ValueError): frame_sources(broken)

    def test_fixed_bits_not_recomputed(self):
        c = json.loads((INPUT/'ft03_map_constants.json').read_text())
        gap = Fraction(decode(c['b12_bits']))-Fraction(decode(c['b1_bits']))-Fraction(decode(c['b2_bits']))
        self.assertEqual(gap, Fraction(3,68719476736))

    def test_input_archive_manifest_and_crc(self):
        self.assertEqual(verify_archive(INPUT/'BASS_CR_CHAT_F04D_20261005_v1.zip'),40)

    def test_source_and_parent_mutations_fail_identity(self):
        for name in ['source_identity.dat','parent_manifest.json','ft03_map_constants.json','SOURCE_LOCK.json']:
            with tempfile.TemporaryDirectory() as temp:
                p=Path(temp)/'inputs';shutil.copytree(INPUT,p)
                with (p/name).open('ab') as f:f.write(b' ')
                with self.assertRaisesRegex(ValueError,'IDENTITY'):Context.from_capsule(p)

    def test_width_and_ledger_limits_unchanged(self):
        for key in ['width','ledger']:
            d=copy.deepcopy(self.rows[0])
            if key=='width':d['public_widths'][0][0]=2e-3
            else:d['ledgers']['H_nuclei']=1e-12
            with self.assertRaisesRegex(ValueError,'LIMIT'):bind_record(d,self.context)

    def test_event_shape_and_negative_are_errors(self):
        for value in [[], [-1.0,0.0]]:
            d=copy.deepcopy(self.rows[0]);d['events']['dr']=value
            with self.assertRaises(ValueError):bind_record(d,self.context)

    def test_no_parent_reset_in_history(self):
        h=History(self.context);h.add(self.rows[0])
        d=copy.deepcopy(self.rows[1]);d['parent_box']=copy.deepcopy(self.rows[0]['parent_box'])
        with self.assertRaisesRegex(ValueError,'BOX_CHAIN'):h.add(d)


if __name__ == '__main__': unittest.main()
