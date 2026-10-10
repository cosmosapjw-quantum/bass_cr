import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from homotopy import load_contract,channel_jump_orders
class ContractTests(unittest.TestCase):
 def test_wrong_bytes(self):
  with self.assertRaises(ValueError):load_contract(source_bytes=b'{}')
 def test_wrong_clock(self):
  with self.assertRaises(ValueError):load_contract(clock=1250000001)
 def test_wrong_channel(self):
  with self.assertRaises(ValueError):load_contract(channel='unrelated_energy')
 def test_corrupt_injection_energy(self):
  with self.assertRaises(ValueError):load_contract(injection_ev=13.8)
 def test_same_box_independent_channels_not_same_physics(self):
  c=load_contract()
  with self.assertRaises(ValueError):channel_jump_orders(c,probe_alias='independent_Eb')
 def test_whole_eta_same_energy_zero(self):
  c=load_contract();r=channel_jump_orders(c,probe_alias=c['energy_alias'])
  self.assertEqual(r['J012'],[0,0,0]);self.assertIsNone(r['J3'])
if __name__=='__main__':unittest.main()
