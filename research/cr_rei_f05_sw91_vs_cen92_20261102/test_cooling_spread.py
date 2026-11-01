"""One original F05 source and scientific rate-closure verification pass.

Use python -m unittest -q test_cooling_spread and python -O -m unittest ...
"""
from __future__ import annotations
import csv,gzip,math,tempfile,unittest,json
from decimal import Decimal,localcontext
from pathlib import Path
import cooling_spread as m

class AnalyticRateChecks(unittest.TestCase):
    def test_glover_published_knot_ratios_wolfram(self):
        refs=((2000,1.5462929814968687),(5000,1.0843866177147499),
              (10000,.9464073271908024),(20000,.9689192021346006),
              (66262,1.625724845750143))
        for t,ratio in refs:
            self.assertLess(abs(m.scholz_walters(t)/m.cen(t)-ratio),2e-8)
    def test_analytic_temperature_monotonicity(self):
        # Extremum locations of cubic P'' are roots of its quadratic P'''.
        A,B,C=-.19742292,3.6368448,-16.57653
        disc=B*B-4*A*C
        self.assertGreater(disc,0)
        u_lo=math.log(2000);u_hi=math.log(67000)
        critical=[u_lo,u_hi,(-B-math.sqrt(disc))/(2*A),(-B+math.sqrt(disc))/(2*A)]
        self.assertTrue(all(u_lo<=x<=u_hi for x in critical))
        self.assertLess(max(m.deriv2_p(x) for x in critical),.4)
        self.assertGreater(118348/67000.,1.76)
        self.assertGreater(m.deriv_log_sw(67000),2.)
        prev_c=prev_s=0.
        for k in range(1001):
            T=2000.+65.*k
            v_c=m.cen(T);v_s=m.scholz_walters(T)
            self.assertGreater(v_c,prev_c);self.assertGreater(v_s,prev_s)
            prev_c,prev_s=v_c,v_s
    def test_independent_decimal_60_digit_sw_polynomial(self):
        with localcontext() as ctx:
            ctx.prec=60
            for T in (2000,5000,10000,20000,66262):
                v=Decimal(T);x=v.ln()
                p=(Decimal('213.7913')-Decimal('113.9492')*x+
                   Decimal('25.06062')*x**2-Decimal('2.762755')*x**3+
                   Decimal('0.1515352')*x**4-Decimal('0.003290382')*x**5)
                expected=Decimal('1e-20')*(p-Decimal(118348)/v).exp()
                self.assertLess(abs(m.scholz_walters(T)/float(expected)-1),2e-10)
    def test_signed_interval_division_and_limits(self):
        self.assertEqual(m.signed_ratio_interval(-2,3,2,4),(-1,1.5))
        for T in (1999,67000.1,0,float("inf"),float("nan")):
            with self.assertRaises(ValueError):m.scholz_walters(T)
            with self.assertRaises(ValueError):m.cen(T)
    def test_guards_active_under_python_optimized(self):
        with self.assertRaisesRegex(ValueError,"OPTIMIZATION_GUARD"):
            m.require(False,"OPTIMIZATION_GUARD")
    def test_private_source_hash_mismatch_fails_closed(self):
        with self.assertRaises(ValueError):
            m.read_original(Path(__file__))

class OriginalPhysicalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="bass_cr_sw91_cen92_")
        cls.path=Path(cls.temp.name)
        cls.csv,cls.result=m.generate(cls.path)
        with gzip.open(cls.csv,"rt",newline="") as f:
            cls.rows=list(csv.DictReader(f))
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_exact_native_source_identity_and_contract(self):
        r=self.result
        self.assertEqual(r["original_source_cells"],46080)
        self.assertEqual(r["original_private_F05_SHA256"],m.SOURCE_SHA)
        self.assertEqual(r["original_legacy_RHS_SHA256"],m.OWNER_RHS_SHA)
        self.assertEqual(r["original_owner_HEAD"],m.source_owner.LOCKS["owner_git"])
        self.assertEqual(r["accepted_tick"],"160/131072")
        self.assertEqual(r["tick161"],"NOT_ACCEPTED")
        self.assertEqual(r["REI_central_DAG"],"28/88_DELTA0")
        self.assertEqual(r["BASS_CR_extension_DAG"],"0/3_DELTA0")
    def test_full_source_in_domain_and_source_order(self):
        self.assertEqual(len(self.rows),46080)
        self.assertEqual([int(r["node"]) for r in self.rows],list(range(46080)))
        self.assertTrue(2000<=self.result["original_T_min_K"]<=self.result["original_T_max_K"]<=67000)
        self.assertFalse(any(k in self.rows[0] for k in ("Tgas_K","source_H_nuclei_N","electron_count_N","native_preview_delta_lnT")))
    def test_signed_interval_encloses_mid_all_nodes(self):
        for row in self.rows:
            lo=float(row["alternative_minus_legacy_erg_s_lower"])
            mid=float(row["alternative_minus_legacy_erg_s_mid"])
            hi=float(row["alternative_minus_legacy_erg_s_upper"])
            self.assertLessEqual(lo,mid+2e-13*max(abs(hi),abs(mid),abs(lo)))
            self.assertLessEqual(mid,hi+2e-13*max(abs(hi),abs(mid),abs(lo)))
            a=float(row["frozen_delta_lnT_lower"]);b=float(row["frozen_delta_lnT_mid"]);c=float(row["frozen_delta_lnT_upper"])
            self.assertLessEqual(a,b+1e-14*max(abs(a),abs(b),abs(c)))
            self.assertLessEqual(b,c+1e-14*max(abs(a),abs(b),abs(c)))
            self.assertGreater(float(row["sw_over_cen_mid"]),0)
    def test_energy_partition_aggregates(self):
        r=self.result
        self.assertLess(abs(r["energy_source_Cen_erg_s"]/3.228248858135368e39-1),3e-14)
        self.assertLess(abs(r["energy_source_SW_erg_s"]/3.4012753342571914e39-1),3e-14)
        self.assertLess(abs(r["energy_difference_SW_minus_Cen_erg_s"]/1.730264761218236e38-1),3e-14)
        self.assertLess(abs(r["signed_fractional_difference_integrated"]/.05359762636817389-1),3e-14)
    def test_model_sign_change_and_conservative_uncertainty(self):
        a=self.result["counts"]
        self.assertEqual(a["positive_model_change"],36000)
        self.assertEqual(a["negative_model_change"],10080)
        self.assertEqual(a["interval_sign_uncertain"],42)
        self.assertEqual(a["mid_delta_over_2e_4"],0)
        self.assertEqual(a["mid_delta_over_2e_6"],1116)
        self.assertEqual(a["mid_over_native_preview_delta"],6)
        self.assertEqual(a["robust_over_native_preview_delta"],0)
    def test_frozen_mid_not_numerical_error_approval(self):
        r=self.result
        self.assertLess(r["max_abs_local_frozen_delta_lnT_mid"],8e-6)
        self.assertLess(r["max_abs_local_frozen_delta_lnT_interval_upper"],8e-6)
        self.assertTrue(r["not_an_IVP_or_native_14ledger_replay"])
        self.assertTrue(r["no_new_cooling_term_added"])
        self.assertTrue(r["two_atomic_models_not_statistical_error_envelope"])
        self.assertEqual(r["production"],"HOLD")
    def test_deterministic_cold_generated_output(self):
        self.assertEqual(m.digest(self.csv),self.result["csv_sha256"])
        self.assertEqual(m.digest(self.csv),m.digest(m.HERE/m.OUT))
        self.assertEqual(m.digest(self.path/"RESULT.json"),m.digest(m.HERE/"RESULT.json"))
        self.assertEqual(json.loads((self.path/"RESULT.json").read_text()),self.result)

if __name__=="__main__": unittest.main()
