"""Source-free numerical claims and negative checks, active under Python -O."""
from __future__ import annotations
import csv,hashlib,json,math,unittest
from pathlib import Path
import numpy as np
import mprk_effective_h as m

class FormulaTests(unittest.TestCase):
    def test_true_two_species_mprk_closed_form(self):
        for Y,H,u,v in ((5,11,.032,0.0625),(1,2,1e-6,1e-3),(9,10,2,5)):
            X=(Y+u*H)/(1+u+v)
            R=v*X
            I=u*(H-X)
            self.assertGreaterEqual(R,0)
            self.assertGreaterEqual(I,0)
            self.assertLess(abs((X-Y)-(I-R))/H,1e-15)
    def test_nonnegative_source_weights_vs_wrong_stage_quadrature(self):
        f0,f1,pred,corrector,dt=2.,3.,4.,5.,1.
        fbar=.5*(f0+f1)
        true_numerical_transfer=dt*fbar*corrector/pred
        stage_quadrature=dt*fbar
        self.assertAlmostEqual(true_numerical_transfer,3.125)
        self.assertNotEqual(true_numerical_transfer,stage_quadrature)
    def test_negative_unsafe_science_guard_python_optimized(self):
        with self.assertRaisesRegex(ValueError,"WRONG_INPUT"):
            m.check(False,"WRONG_INPUT")
    def test_synthetic_nonoverlap_detects_real_discrepancy(self):
        initial=type("B",(),{"lo":np.zeros((2,5)),"hi":np.zeros((2,5))})()
        final=type("B",(),{"lo":np.zeros((2,5)),"hi":np.zeros((2,5))})()
        initial.lo[0,1]=2.;initial.hi[0,1]=2.
        final.lo[0,1]=1.;final.hi[0,1]=1.
        result=m.overlap_metrics((np.zeros(2),np.zeros(2)),
                                 (np.zeros(2),np.zeros(2)),
                                 initial,final,np.ones(2))
        self.assertEqual(result["cell_overlap"],1)
        self.assertAlmostEqual(result["gap_sum"],1.)
        self.assertFalse(result["global_overlap"])
    def test_unit_energy(self):
        self.assertLess(abs(m.prior.CHI_H_EV*m.prior.EV_ERG/2.17896e-11-1),1e-3)

class PublishedSourceScience(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.j=json.loads((m.HERE/"SCIENCE_RESULT.json").read_text())
        with (m.HERE/m.OUTPUT).open(newline="") as f:
            r=csv.DictReader(f);cls.fields=r.fieldnames;cls.rows=list(r)
    def test_exact_source_authority(self):
        j=self.j
        self.assertEqual(j["original_source_REI_HEAD"],m.prior.SOURCE_REI_HEAD)
        self.assertEqual(j["original_26event_kernel_SHA256"],m.prior.SOURCE_KERNEL_SHA)
        self.assertEqual(j["original_REC195_source_SHA256"],m.prior.REC195_ZIP_SHA)
        self.assertEqual(j["original_accepted_ticks"],[0,64,128,160])
        self.assertEqual(j["original_tick161"],"NOT_ACCEPTED")
    def test_three_native_original_intervals(self):
        self.assertEqual(len(self.rows),3)
        self.assertEqual([(int(z["tick_left"]),int(z["tick_right"])) for z in self.rows],
                         [(0,64),(64,128),(128,160)])
        self.assertEqual(set(self.fields),set(self.j["intervals"][0]))
    def test_exact_reconstructed_conservation_on_46k_cells(self):
        self.assertEqual([r["accepted_delta_HII_overlap_cells"] for r in self.j["intervals"]],
                         [46080,46080,46080])
        self.assertTrue(all(r["accepted_delta_HII_nonoverlap_gap_sum"]==0 for r in self.j["intervals"]))
        self.assertFalse(self.j["any_local_source_HII_nonoverlap"])
        self.assertTrue(all(r["accepted_delta_HII_global_overlap"] for r in self.j["intervals"]))
    def test_discrete_recombination_positive_and_distinct_stage(self):
        ratios=[]
        for r in self.j["intervals"]:
            lo=r["weighted_MPRK_caseB_recomb_lo"];hi=r["weighted_MPRK_caseB_recomb_hi"]
            self.assertTrue(0<lo<=hi)
            self.assertTrue(0<r["weighted_MPRK_H_ion_lo"]<=r["weighted_MPRK_H_ion_hi"])
            self.assertLess(abs(r["weighted_MPRK_H_gross_binding_lo_erg"]/(lo*m.prior.CHI_H_EV*m.prior.EV_ERG)-1),2e-14)
            ratios.append(r["MPRK_to_stage_midpoint_ratio"])
            self.assertEqual(r["source_14_ledgers"],"PASS_ON_ALL_THREE_SOURCE_MAPS")
            self.assertLess(r["original_local_defect_max"],2e-4)
            self.assertLess(r["original_width_max"],2e-3)
        self.assertTrue(any(abs(a-1)>1e-6 for a in ratios))
    def test_csv_hash_and_nonpromotion(self):
        self.assertEqual(m.prior.sha(m.HERE/m.OUTPUT),self.j["csv_sha256"])
        self.assertEqual(self.j["REI_canonical_DAG"],"28/88_DELTA0")
        self.assertEqual(self.j["BASS_CR_extension"],"0/3_DELTA0")
        self.assertEqual(self.j["PRODUCTION"],"HOLD")
        self.assertTrue(self.j["not_exact_continuum_CaseB_reactions"])
        self.assertTrue(self.j["not_hydrogen_Lya_photon_emissivity"])
        self.assertTrue(self.j["CR_OFF"])
    def test_no_raw_private_population_in_public_csv(self):
        for r in self.rows:
            for k in ("N_HII","N_HI","xHII","raw_state","T_K","proper_volume"):
                self.assertFalse(k in r)
if __name__=="__main__":unittest.main()
