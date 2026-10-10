import sys,unittest
sys.path.insert(0,'/root/bass_cr_ncp_r17b2/research/cr_r17b2_20261010/tests')
import test_functional as t
original=t.tangent_functional; t.tangent_functional=lambda *a:original(*a[:-1],lambda f:(t.I(0),t.I(0)))
suite=unittest.TestSuite([t.FunctionalTests('test_companion_current_response_participates')])
r=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if r.wasSuccessful() else 1)
