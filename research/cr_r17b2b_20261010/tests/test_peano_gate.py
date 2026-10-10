import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from homotopy import peano_transfer,Unproved
from interval_backend import I
class PeanoGateTests(unittest.TestCase):
 def test_unreported_third_kink(self):
  with self.assertRaises(Unproved):peano_transfer(dict(J012=[0,0,0],jumps=[],regularity=True))
 def test_nominal_only(self):
  with self.assertRaises(Unproved):peano_transfer(dict(eta=[0,0],K4=I('1e-9')))
 def test_toy_third_jump(self):
  with self.assertRaises(Unproved):peano_transfer(dict(J3='-93/20000',interval=True))
if __name__=='__main__':unittest.main()
