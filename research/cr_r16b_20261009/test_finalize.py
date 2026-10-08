import unittest,copy,os
from fractions import Fraction as Q
from pathlib import Path
from finalize_math import combine_once
from prepare import context,validate,compute_cell
class NewReductionTests(unittest.TestCase):
    def test_source_exactly_once(self):
        t=(Q('2e-17'),Q('3e-17'));b=Q('1e-17')
        self.assertEqual(combine_once(t,b),(Q('1e-17'),Q('4e-17')))
        self.assertNotEqual(combine_once(combine_once(t,b),b),combine_once(t,b))
    def test_source_domain_rejects(self):
        for t,b in [((2,1),0),((1,2),-1)]:
            with self.assertRaises(ValueError):combine_once(t,b)
    def test_inexact_panel_clock_rejected(self):
        with self.assertRaisesRegex(ValueError,'EXACT_PANEL_CLOCK'):compute_cell(('unused',0,63))
    def test_absolute_clock_domain_rejected(self):
        import json
        stage=Path(os.environ['R16B_STAGE']);ch,_,_=context(stage)
        cert=json.loads((stage/'donor/rei_bridge13_20261008/results/final_interval/CHAIN_CERTIFICATE.json').read_text())
        e=copy.deepcopy(ch.ENTRIES);e['root'][0]['t0']=1
        with self.assertRaisesRegex(ValueError,'CLOCK_DOMAIN'):validate(e,cert)
if __name__=='__main__':unittest.main()
