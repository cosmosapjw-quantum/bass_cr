"""Source-scoped physical tests; explicit checks remain active under python -O."""
from __future__ import annotations
import csv
import gzip
import json
import math
import tempfile
import unittest
from decimal import Decimal,localcontext
from pathlib import Path
import partition as m

class FormulaChecks(unittest.TestCase):
    def test_wolfram_independent_reference_knots(self):
        refs=((5000,0.6760564508233273),(10000,0.5837199358663981),
              (15000,0.5620253178553837),(20000,0.5626059816131181))
        for T,answer in refs:
            self.assertLess(abs(m.two_p_cooling(T)/m.legacy(T)-answer),2e-14)
    def test_positive_nonoverlap_residual_all_support(self):
        for i in range(1501):
            T=5000+10*i
            r=m.two_p_cooling(T)/m.legacy(T)
            self.assertGreater(r,0);self.assertLess(r,1)
    def test_legacy_requires_valid_temperature(self):
        for T in (0,-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):m.legacy(T)
    def test_2p_table_rejects_extrapolation(self):
        for T in (4999,20001):
            with self.assertRaises(ValueError):m.two_p_cooling(T)
    def test_energy_units(self):
        self.assertAlmostEqual(m.E12_ERG/(m.two_p.E12_EV*1.602176634e-12),1.,places=14)
    def test_decimal_original_legacy_coeff(self):
        with localcontext() as c:
            c.prec=60
            for T in (5000,10000,15000,20000):
                t=Decimal(T)
                val=Decimal('7.5e-19')*(-Decimal(118348)/t).exp()/(1+(t/Decimal(100000)).sqrt())
                self.assertLess(abs(m.legacy(T)/float(val)-1.),5e-15)
    def test_explicit_guard_works_under_optimization(self):
        with self.assertRaisesRegex(ValueError,"GUARD_SAMPLE"):
            m.require(False,"GUARD_SAMPLE")
    def test_source_lock_wrong_hash(self):
        self.assertNotEqual(m.sha(Path(__file__)),m.SOURCE_SHA)
        self.assertEqual(len(m.SOURCE_SHA),64)

class RealOriginalSourceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="rei_original_2p_partition_")
        cls.csvfile,cls.data=m.generate(Path(cls.temp.name))
        with gzip.open(cls.csvfile,"rt",newline="") as f:
            cls.rows=list(csv.DictReader(f))
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
    def test_exact_original_source_and_owner(self):
        a=self.data
        self.assertEqual(a["original_source_private_SHA256"],m.ORIG.LOCKS["preview"])
        self.assertEqual(a["original_legacy_rhs_SHA256"],m.ORIG.LOCKS["native"])
        self.assertEqual(a["parent_two_p_source_SHA256"],m.SOURCE_SHA)
        self.assertEqual(a["original_REI_owner_head"],m.ORIG.LOCKS["owner_git"])
    def test_row_domain_and_order(self):
        self.assertEqual(len(self.rows),12528)
        self.assertEqual([int(x["node"]) for x in self.rows],sorted(set(int(x["node"]) for x in self.rows)))
        # Do not publish the private original tick160 gas-temperature values.
        source=m.ORIG.read_csv(m.ORIG.PREVIEW,m.ORIG.LOCKS["preview"])
        self.assertTrue(all(5000<=float(source[int(x["node"])]["tick160_Tgas_K_lower"])<=20000 for x in self.rows))
        self.assertTrue(all("Tgas_K_mid" not in x and "native_preview_delta_lnT_mid" not in x for x in self.rows))
        self.assertEqual(self.data["excluded_source_cells"],33552)
    def test_power_partitions_per_node(self):
        for r in self.rows:
            old=float(r["legacy_exc_erg_s_mid"]);two=float(r["two_p_exc_erg_s_mid"]);res=float(r["other_exc_residual_erg_s_mid"])
            self.assertGreater(old,0);self.assertGreater(two,0);self.assertGreater(res,0)
            self.assertLess(abs((two+res)/old-1),8e-15)
    def test_interval_one_sided_consistency(self):
        for r in self.rows:
            x=float(r["two_p_over_legacy_mid"])
            lo=float(r["two_p_over_legacy_lower"]);hi=float(r["two_p_over_legacy_upper"])
            self.assertTrue(0<lo<=x<=hi<1)
            el=float(r["epsilon_two_p_lower"]);em=float(r["epsilon_two_p_mid"]);eh=float(r["epsilon_two_p_upper"])
            self.assertTrue(0<=el<=em<=eh)
    def test_robust_thresholds_from_original_preview(self):
        r1=r01=mid=0
        # Private source preview delta lnT is read to check flags but NEVER
        # published per-node in derived CSV, since it is not our source data.
        preview=m.ORIG.read_csv(m.ORIG.PREVIEW,m.ORIG.LOCKS["preview"])
        for r in self.rows:
            el=float(r["epsilon_two_p_lower"]);em=float(r["epsilon_two_p_mid"])
            native=preview[int(r["node"])]
            dlo=float(native["tick160_to_161_delta_logT_lower"])
            dhi=float(native["tick160_to_161_delta_logT_upper"])
            dmax=max(abs(dlo),abs(dhi))
            self.assertEqual(int(r["two_p_over_native_robust_gt_1"]),int(el>dmax))
            self.assertEqual(int(r["two_p_over_native_robust_gt_0p1"]),int(el>.1*dmax))
            r1+=int(el>dmax);r01+=int(el>.1*dmax)
            mid+=int(em>abs((dlo+dhi)*.5))
        self.assertEqual(r1,120);self.assertEqual(r01,1776);self.assertEqual(mid,180)
    def test_integrated_source_power_numeric_witness(self):
        a=self.data["aggregates"]
        self.assertLess(abs(a["two_p_exc_erg_per_s"]/8.216438058687765e37-1),2e-14)
        self.assertLess(abs(a["legacy_H_exc_erg_per_s"]/1.4642738832064828e38-1),2e-14)
        self.assertLess(abs(a["other_H_exc_residual_erg_per_s"]/6.426300773377064e37-1),2e-14)
        self.assertLess(abs(self.data["two_p_fraction_of_legacy_integrated"]/.5611271329032599-1),2e-14)
    def test_correct_nonpromotion_contract(self):
        d=self.data
        self.assertTrue(d["legacy_H_exc_in_original_RHS"])
        self.assertTrue(d["no_new_cooling_term_to_add"])
        self.assertTrue(d["no_replacement_of_whole_legacy_by_2p"])
        self.assertTrue(d["not_proven_exact_atomic_2s_or_higher_residual"])
        self.assertTrue(d["tick161_preview_unaccepted"])
        self.assertEqual(d["REI_central_DAG"],"28/88_DELTA0")
        self.assertEqual(d["BASS_CR_extension_DAG"],"0/3_DELTA0")
    def test_cold_output_identity(self):
        self.assertEqual(m.sha(self.csvfile),self.data["csv_sha256"])
        saved=(Path(self.temp.name)/"RESULT.json")
        self.assertEqual(json.loads(saved.read_text()),self.data)
        self.assertEqual(m.sha(self.csvfile),m.sha(m.HERE/m.OUT))
        self.assertEqual(m.sha(saved),m.sha(m.HERE/"RESULT.json"))

if __name__=="__main__":
    unittest.main()
