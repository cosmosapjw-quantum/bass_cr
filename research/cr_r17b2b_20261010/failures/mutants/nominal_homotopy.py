import sys,unittest
sys.path.insert(0,'/root/bass_cr_ncp_r17b2b/research/cr_r17b2b_20261010/tests')
import test_peano_gate as t
t.peano_transfer=lambda e:0
r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([t.PeanoGateTests('test_nominal_only')]))
sys.exit(0 if r.wasSuccessful() else 1)
