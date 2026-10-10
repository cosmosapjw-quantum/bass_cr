import sys,unittest
sys.path.insert(0,'/root/bass_cr_ncp_r17b2b/research/cr_r17b2b_20261010/tests')
import test_contract as t
t.channel_jump_orders=lambda *a,**k:dict(J012=[0,0,0],J3=None)
r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([t.ContractTests('test_same_box_independent_channels_not_same_physics')]))
sys.exit(0 if r.wasSuccessful() else 1)
