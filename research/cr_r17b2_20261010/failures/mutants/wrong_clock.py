import sys,unittest
sys.path.insert(0,'/root/bass_cr_ncp_r17b2/research/cr_r17b2_20261010/tests')
import test_backend as t
original=t.load_pins; t.load_pins=lambda **kw:original()
suite=unittest.TestSuite([t.BackendTests('test_clock')])
r=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if r.wasSuccessful() else 1)
