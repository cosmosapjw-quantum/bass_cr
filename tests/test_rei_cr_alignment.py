"""Source-bound adversarial negative controls for BASS-CR REI governance overlay."""
from __future__ import annotations
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from verify_rei_cr_alignment import validate
class REIAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((ROOT/"governance"/"REI_CR_CONSUMER_DAG.v1.json").read_text(encoding="utf-8"))
    def check_reject(self,f):
        d=copy.deepcopy(self.original);f(d)
        with self.assertRaises(AssertionError):validate(d)
    def test_actual(self):validate(copy.deepcopy(self.original))
    def test_false_canonical_delta(self):self.check_reject(lambda d:d["authority"].__setitem__("canonical_delta",1))
    def test_working_doublecount(self):self.check_reject(lambda d:d["authority"].__setitem__("working_is_not_additive",False))
    def test_cr_on_as_default(self):self.check_reject(lambda d:d["baseline"].__setitem__("CR","ON"))
    def test_cr_adapter_blocks_off(self):self.check_reject(lambda d:d["nodes"][2]["deps"].append("BCR-01"))
    def test_early_CR(self):self.check_reject(lambda d:d["nodes"][3]["requires"].remove("REI:RUX11"))
    def test_cycle(self):self.check_reject(lambda d:d["nodes"][0]["deps"].append("BCR-05"))
    def test_fake_external(self):self.check_reject(lambda d:d["nodes"][4]["requires"].append("BOGUS:PROXY"))
    def test_false_science_admission(self):self.check_reject(lambda d:d["nodes"][5].__setitem__("status","PROMOTED"))
    def test_optional_made_required(self):self.check_reject(lambda d:d["nodes"][2].__setitem__("optional",False))
if __name__=="__main__":unittest.main()
