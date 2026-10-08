"""New binding/identity rejection tests; no native execution or old suite replay."""
import os
from pathlib import Path
import sys
import unittest
from bind import analyze, read_observation

sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)

class ParserTests(unittest.TestCase):
    def test_exact_negative_zero(self):
        self.assertEqual(read_observation('X,0,8000000000000000,-0.00000000000000000e0')['X'][0],0)
    def test_reject_nonfinite(self):
        with self.assertRaises(ValueError):read_observation('X,0,7ff0000000000000,inf')
    def test_reject_inconsistent_decimal(self):
        with self.assertRaises(ValueError):read_observation('X,0,3ff0000000000000,2.0')
    def test_reject_duplicate_index(self):
        with self.assertRaises(ValueError):read_observation('X,0,3ff0000000000000,1.0\nX,0,3ff0000000000000,1.0')

class BindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=Path(os.environ['F04B_OBSERVATION']).read_text()
        cls.reference=Path(os.environ['F04B_REFERENCE'])
    def replace_group_first(self,name,bits,value):
        return '\n'.join(f'{name},0,{bits},{value}' if line.startswith(name+',0,') else line
                         for line in self.text.splitlines())
    def test_native_binding_and_nonzero_residual(self):
        r=analyze(self.text,self.reference)
        self.assertTrue(r['endpoint_in_inherited_cube'])
        self.assertGreater(r['root_distance_inf'],0)
        self.assertTrue(any(r['reduced_fraction_residual']))
        self.assertTrue(all(z==0 for z in r['projection_identity']))
        self.assertTrue(all(0<=z<=r['root_distance_inf'] for z in r['component_root_distance']))
        self.assertGreater(r['thermal_numerator_lower'],0)
        self.assertNotEqual(r['old_u_difference_from_reference'],0)
        self.assertFalse(r['global_F04_closed'])
    def test_reject_changed_model(self):
        with self.assertRaisesRegex(ValueError,'model differs'):
            analyze(self.replace_group_first('MODEL','3ff0000000000000','1.0'),self.reference)
    def test_reject_outside_cube(self):
        with self.assertRaisesRegex(ValueError,'outside'):
            analyze(self.replace_group_first('ENDPOINT','3fe0000000000000','0.5'),self.reference)
    def test_reject_changed_dt(self):
        with self.assertRaisesRegex(ValueError,'dt mismatch'):
            analyze(self.replace_group_first('DT','3ff0000000000000','1.0'),self.reference)
    def test_reject_changed_native_control(self):
        with self.assertRaisesRegex(ValueError,'control changed'):
            analyze(self.replace_group_first('CONTROL','3ff0000000000000','1.0'),self.reference)
    def test_reject_changed_old_fractions(self):
        with self.assertRaisesRegex(ValueError,'input differs'):
            analyze(self.replace_group_first('OLD','3fe0000000000000','0.5'),self.reference)

if __name__=='__main__':unittest.main()
