"""Original-source (46,080 cells) physical and integrity tests, also under python -O."""
from __future__ import annotations
import csv,hashlib,json,math,struct,tempfile,unittest
from array import array
from pathlib import Path
import numpy as np
import accepted_recomb_min as m

class AnalyticChecks(unittest.TestCase):
    def test_positive_ionization_recomb_lower(self):
        # N_b=N_a + I - R. Equal additions I+=k, R+=k leave endpoints fixed.
        for k in (0,1,10000):
            a,b,I,R=8,5,5+k,8+k
            self.assertEqual(a+I-R,b)
            self.assertGreaterEqual(R,max(0,a-b))
        self.assertEqual(max(0,5-8),0)
    def test_rounding_outward_and_order(self):
        a=np.ones(m.N);b=np.ones(m.N)
        a[:4]=[1.,3.,5.,9.];b[:4]=[2.,2.,5.,4.]
        v=m.lower_envelope(a,b)
        self.assertEqual(v[0],0);self.assertEqual(v[2],0)
        self.assertLess(v[1],1);self.assertLess(v[3],5)
        self.assertGreater(v[1],0);self.assertGreater(v[3],0)
        self.assertLess(m.exact_nonnegative_sum_down(v),6.)
    def test_guard_really_raises_under_python_optimized(self):
        with self.assertRaisesRegex(ValueError,"BASS_CR_RECOMB_TEST"):
            m.ensure(False,"TEST")
    def test_bad_source_hash_and_magic_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/"corrupted.state"
            f.write_bytes(b"REIADP1\x00"+b"x"*32)
            with self.assertRaisesRegex(ValueError,"STATE_SHA256"):
                m.source_state(f,64,m.STATE_SHA[64])
            # A correct SHA of malformed bytes cannot bypass parser.
            with self.assertRaisesRegex(ValueError,"HEADER_LENGTH"):
                m.source_state(f,64,hashlib.sha256(f.read_bytes()).hexdigest())
    def test_nonpositive_aggregate_fail_closed(self):
        with self.assertRaises(ValueError):m.exact_nonnegative_sum_down([0.,0.])
        with self.assertRaises(ValueError):m.exact_nonnegative_sum_down([1.,-1.])

class FullRealSourceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir=tempfile.TemporaryDirectory(prefix="original_f05_caseb_min_")
        cls.data=m.run(Path(cls.dir.name))
        with (Path(cls.dir.name)/m.OUTPUT).open(newline="") as f:
            cls.rows=list(csv.DictReader(f))
    @classmethod
    def tearDownClass(cls):cls.dir.cleanup()
    def test_source_identity_actual_accepted_ticks(self):
        a=self.data
        self.assertEqual(a["input_original_NPZ_sha256"],m.INIT_SHA)
        self.assertEqual(a["source_original_HII_RHS_sha256"],m.RHS_SHA)
        self.assertEqual(a["input_rei_accepted_state_sha256"],{str(k):v for k,v in m.STATE_SHA.items()})
        self.assertEqual(a["original_accepted_ticks"],[0,64,128,160])
        self.assertEqual(a["original_t161"],"NOT_ACCEPTED")
        self.assertEqual(a["source_cells"],46080)
    def test_three_original_physics_intervals(self):
        self.assertEqual(len(self.rows),3)
        self.assertEqual([(int(r["tick_start"]),int(r["tick_end"])) for r in self.rows],[(0,64),(64,128),(128,160)])
        self.assertEqual([int(r["certified_net_HII_decline_nodes"]) for r in self.rows],[42474,42534,42522])
        self.assertEqual([int(r["certified_net_HII_gain_nodes"]) for r in self.rows],[3600,3366,2622])
        self.assertEqual([int(r["source_sign_ambiguous_nodes"]) for r in self.rows],[6,180,936])
        self.assertEqual([int(float(r["original_proper_duration_s"])/m.DT_REF+1e-10) for r in self.rows],[64,64,32])
    def test_numerical_conservative_lower_sums(self):
        references=[8.879746299967944e61,8.835204102163904e61,4.381986121562682e61]
        for got,ref in zip(self.rows,references):
            val=float(got["min_caseB_recombination_events_conditional"])
            self.assertLess(abs(val/ref-1),1e-13)
            self.assertGreaterEqual(val*(1.+1e-13),float(got["weaker_global_net_HII_decline_lower"]))
            self.assertGreater(float(got["min_caseB_gross_binding_release_erg_conditional"]),0)
        self.assertLess(abs(self.data["min_total_caseB_event_lower_conditional"]/2.209693652369452e62-1),1e-13)
    def test_independent_array_body_read_all_original_cells(self):
        with np.load(m.INIT,allow_pickle=False) as z:
            n0=np.asarray(z["N_HII"])
        previous=np.asarray(n0,dtype=np.float64).copy()
        lower_list=[]
        for t in (64,128,160):
            b=m.STATE_FILES[t].read_bytes()
            h=struct.unpack_from("<Q",b,8)[0]
            data=b[16+h:]
            a=array("d");a.frombytes(data)
            self.assertEqual(len(a),m.N*12)
            old=previous
            lo=np.asarray([a[i*5+1] for i in range(m.N)])
            hi=np.asarray([a[m.N*5+i*5+1] for i in range(m.N)])
            # Source-owner admissible interval: compare previous LOWER to new UPPER.
            v=[max(0.,math.nextafter(float(x-y),-math.inf)) for x,y in zip(old,hi)]
            # For the next interval start, use lower state, not prior upper.
            # This deliberately recomputes the source-independent local bound.
            x=math.nextafter(math.fsum(v),-math.inf)
            lower_list.append(x)
            previous=lo
        for k,(got,public) in enumerate(zip(lower_list,self.data["intervals"])):
            self.assertLess(abs(got/public["min_caseB_recombination_events_conditional"]-1),2e-15)
    def test_output_only_derived_three_rows_no_private_original(self):
        self.assertEqual(set(self.rows[0]),set(m.COLUMNS))
        forbidden=("HII_lower","HII_upper","N_HI","N_HeI","raw_state","Tgas","proper_volume")
        self.assertTrue(all(not any(s in col for s in forbidden) for col in self.rows[0]))
        self.assertTrue(self.data["no_nonzero_lower_bound_on_actual_Lya_emission"])
        self.assertTrue(self.data["no_finite_recomb_upper_from_endpoints"])
        self.assertEqual(self.data["actual_26event_time_integrated_reactions"],"NOT_MEASURED")
    def test_no_false_promotion_or_thermal_double_count(self):
        d=self.data
        self.assertEqual(d["REI_central_DAG"],"28/88_DELTA0")
        self.assertEqual(d["BASS_CR_extension"],"0/3_DELTA0")
        self.assertTrue(d["CR_OFF"])
        self.assertTrue(d["NO_REI_MUTATION"])
        self.assertEqual(d["PRODUCTION"],"HOLD")
    def test_cold_source_generated_data_exact(self):
        p=Path(self.dir.name)
        self.assertEqual(m.sha(p/m.OUTPUT),self.data["output_csv_sha256"])
        self.assertEqual(m.sha(p/m.OUTPUT),m.sha(m.HERE/m.OUTPUT))
        self.assertEqual(m.sha(p/"SCIENCE_RESULT.json"),m.sha(m.HERE/"SCIENCE_RESULT.json"))
        self.assertEqual(json.loads((p/"SCIENCE_RESULT.json").read_text()),self.data)
if __name__=="__main__":
    unittest.main()
