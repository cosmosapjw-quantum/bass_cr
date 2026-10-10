import sys,unittest
sys.path.insert(0,'/root/bass_cr_ncp_r17b2b/research/cr_r17b2b_20261010/tests')
import test_contract as t
old=t.load_contract;t.load_contract=lambda **kw:old()
r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([t.ContractTests('test_wrong_channel')]))
sys.exit(0 if r.wasSuccessful() else 1)
