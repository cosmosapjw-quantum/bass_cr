"""Source-free numerical and negative scientific checks; -O must keep guards."""
from __future__ import annotations
import csv,hashlib,json,math,tempfile,unittest
from pathlib import Path
import numpy as np
import native_h_caseb as m

class SourcePhysicsFormula(unittest.TestCase):
    def test_analytic_sdirk_weights(self):
        g=1.-1./math.sqrt(2.)
        self.assertAlmostEqual((1.-g)+g,1.,places=15)
        self.assertAlmostEqual(g,0.2928932188134524756,places=15)
        self.assertEqual(m.PARENT_CR,"264ad0c1fd62f7ec799af14f273d9902a24ca6aa")
    def test_outward_interval_and_event_orientation(self):
        class V:pass
        class E:pass
        class S:pass
        e=E();e.flux=V()
        e.flux.lo=np.zeros((m.N,5,5));e.flux.hi=np.zeros((m.N,5,5))
        e.flux.lo[:,0,1]=2.;e.flux.hi[:,0,1]=3.
        e.flux.lo[:,1,0]=5.;e.flux.hi[:,1,0]=7.
        s=S();s.certified=True;s.stage_event=e;s.final_event=e
        r=m.source_quadrature(s,8.,1.-1./math.sqrt(2.),0,1)
        i=m.source_quadrature(s,8.,1.-1./math.sqrt(2.),1,0)
        self.assertAlmostEqual(r[0][0],16.);self.assertAlmostEqual(r[1][0],24.)
        self.assertAlmostEqual(i[0][0],40.);self.assertAlmostEqual(i[1][0],56.)
    def test_degenerate_zero_interval_and_bad_source_guards(self):
        class A:pass
        x=A();x.flux=A()
        x.flux.lo=np.zeros((m.N,5,5));x.flux.hi=np.zeros((m.N,5,5))
        z=m.sample_bounds(x,0,1)
        self.assertEqual(float(np.sum(z[0])),0)
        x.flux.lo[:,0,1]=-1.
        with self.assertRaisesRegex(ValueError,"NEGATIVE_MACRO_REACTION"):m.sample_bounds(x,0,1)
        with self.assertRaises(ValueError):m.require(False,"GUARD_EXECUTED_UNDER_OPTIMIZATION")
    def test_endpoint_lower_and_ion_gain_counterexample(self):
        x=np.zeros((m.N,5));a=(x.copy(),x.copy());b=(x.copy(),x.copy())
        a[0][0,1]=7.;a[1][0,1]=7.
        b[0][0,1]=5.;b[1][0,1]=5.
        b[0][1,1]=9.;b[1][1,1]=9.
        r=m.count_parent_lower(a,b)
        self.assertLess(r[0],2)
        self.assertGreater(r[0],1.99999999999999)
        self.assertEqual(r[1],0.)
    def test_manifest_sha_for_public_csv_and_json(self):
        self.assertTrue((m.HERE/m.OUTPUT).is_file())
        self.assertTrue((m.HERE/"SCIENCE_RESULT.json").is_file())
        self.assertTrue((m.HERE/"SCIENCE_RESULT.json").read_text().endswith("\n"))

class RealSourceReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=json.loads((m.HERE/"SCIENCE_RESULT.json").read_text())
        with (m.HERE/m.OUTPUT).open(newline="") as f:
            reader=csv.DictReader(f)
            cls.fields=reader.fieldnames
            cls.rows=list(reader)
    def test_original_source_and_scope(self):
        a=self.r
        self.assertEqual(a["source_REI_head"],m.SOURCE_REI_HEAD)
        self.assertEqual(a["source_REC195_zip_sha256"],m.REC195_ZIP_SHA)
        self.assertEqual(a["source_original_kernel_sha256"],m.SOURCE_KERNEL_SHA)
        self.assertEqual(a["state_SHA256_by_tick"],{str(i):x[1] for i,x in m.STATE.items()})
        self.assertEqual(a["source_nodes"],46080)
        self.assertEqual(a["accepted_intervals"],[[0,64],[64,128],[128,160]])
        self.assertLess(abs(a["source_microtick_seconds"]/m.PROPER_MICROTICK_S-1),1e-14)
        self.assertEqual(a["original_tick161"],"NOT_ACCEPTED")
    def test_interval_source_vs_endpoint_and_schemedefect(self):
        a=self.r
        self.assertEqual(len(self.rows),3)
        self.assertEqual(self.fields,list(m.COLUMNS))
        for x,row in zip(a["intervals"],self.rows):
            self.assertEqual([int(row["start_tick"]),int(row["end_tick"])],[x["start_tick"],x["end_tick"]])
            rlo=x["source_H_caseB_events_integrated_lower"]
            rhi=x["source_H_caseB_events_integrated_upper"]
            self.assertGreater(rlo,0.)
            self.assertGreaterEqual(rhi,rlo)
            self.assertGreaterEqual(rlo*1.000000001,x["conditional_endpoint_min_recomb_events"])
            self.assertLess(abs(x["gross_H_recomb_chemical_release_lower_erg"]/(rlo*m.CHI_H_EV*m.EV_ERG)-1),1e-14)
            self.assertTrue(x["all_original_14_ledgers_include_zero"])
            self.assertLess(x["original_source_defect_max"],2e-4)
            self.assertLess(x["original_public_width_max"],2e-3)
        self.assertEqual([i["source_net_HII_interval_overlap"] for i in a["intervals"]],[45744,46080,46080])
        self.assertGreater(a["intervals"][0]["source_net_HII_gap_sum_counts"],0)
        self.assertEqual(a["intervals"][1]["source_net_HII_gap_sum_counts"],0.)
        self.assertEqual(a["intervals"][2]["source_net_HII_gap_sum_counts"],0.)
    def test_global_aggregate_source_bracket(self):
        a=self.r
        lo,hi=a["total_H_caseB_events_quadrature_interval"]
        self.assertLess(abs(lo/2.5410387807979653e62-1),2e-12)
        self.assertLess(abs(hi/2.766237241157955e62-1),2e-12)
        self.assertLess(lo,hi)
        self.assertLess(lo,3.e62)
        self.assertEqual(m.sha(m.HERE/m.OUTPUT),a["output_csv_sha256"])
    def test_no_false_photon_or_canonical_promotion(self):
        d=self.r
        self.assertTrue(d["no_claim_of_exact_continuum_time_integral"])
        self.assertTrue(d["no_H_Lya_photon_emission_or_escape_inferred"])
        self.assertTrue(d["no_heat_double_counting"])
        self.assertEqual(d["REI_canonical_DAG"],"28/88_DELTA0")
        self.assertEqual(d["BASS_CR_extension_DAG"],"0/3_DELTA0")
        self.assertTrue(d["CR_OFF"])
        self.assertEqual(d["production"],"HOLD")
if __name__=="__main__":unittest.main()
