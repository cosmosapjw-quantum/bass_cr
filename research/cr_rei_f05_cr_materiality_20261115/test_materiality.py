"""Source-free unit/physics audit, no private original IGM data required."""
from __future__ import annotations
import csv,json,math,tempfile,unittest
from pathlib import Path
import cr_materiality as m

class OriginalPhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=json.loads((m.HERE/"SCIENCE_RESULT.json").read_text())
        cls.audit=json.loads((m.HERE/"INDEPENDENT_AUDIT.json").read_text())
        with (m.HERE/m.CSV_NAME).open(newline="") as f:
            r=csv.DictReader(f);cls.columns=r.fieldnames;cls.rows=list(r)
    def test_four_real_approved_epochs_no_research_tick_promoted(self):
        j=self.result
        self.assertEqual(j["source_input_rows"],184320)
        self.assertEqual(j["original_physical_epochs"],[0,64,128,160])
        self.assertEqual(j["original_V1_last_accepted_tick"],"160/131072")
        self.assertIn("RESEARCH_ONLY",j["separately_versioned_V2_161_163"])
        self.assertEqual(len(self.rows),4)
    def test_native_source_exact_locks(self):
        j=self.result
        self.assertEqual(j["source_REI_PR367_ZIP_sha256"],m.SHA_REI_ZIP)
        self.assertEqual(j["source_REI367_original_20field_gzip_sha256"],m.SHA_REI_MEMBER)
        self.assertEqual(j["source_WU_R57_augmented_gzip_sha256"],m.SHA_WU_CSV)
        self.assertEqual(j["source_26event_original_kernel_sha256"],m.REI_KERNEL_SHA)
        self.assertEqual(j["source_20field_text_identical_original_REI_and_WU"],
                         "184320/184320_VERIFIED")
        self.assertEqual(self.audit["original_source_rows_compared_text_identically"],184320)
    def test_critical_hazard_values_from_original_source(self):
        expected=[6.221590792959104e-13,5.208749780227057e-13,
                  4.452012894008359e-13,4.14761070259447e-13]
        for x,z in zip(self.result["epochs"],expected):
            self.assertLess(abs(x["CR_hazard_reverse_global_HII_decline_s_inv"]/z-1),5e-14)
    def test_no_missing_he_ots_ionizations(self):
        f=[.8509734214398823,.7901381422967598,.7431472043190351,.7234572698332826]
        for x,r in zip(self.result["epochs"],f):
            self.assertLess(abs(x["derived_He_OTS_fraction_of_total_H_formation"]-r),5e-14)
            self.assertGreater(x["derived_total_H_ion_rate_s_inv"],
                               x["native_direct_H_ion_rate_s_inv"])
            self.assertGreater(x["derived_He_OTS_H_ion_rate_s_inv"],0)
    def test_energy_frontier_identity_and_ion_unit(self):
        e=[9.406515542672588,11.237129866295321,
           13.009966715799045,13.853704950859028]
        for x,v in zip(self.result["epochs"],e):
            self.assertLess(abs(x["CR_heat_per_new_ion_at_chemical_threshold_eV"]/v-1),5e-14)
            hazard=x["CR_hazard_reverse_global_HII_decline_s_inv"]
            heat=x["CR_heat_per_new_ion_at_chemical_threshold_eV"]*m.EV_ERG
            actual=x["native_gas_total_Udot_erg_s"]
            self.assertLess(abs(hazard*heat*x["original_N_HI_total"]+actual)/abs(actual),2e-14)
            self.assertLess(x["CR_hazard_reverse_times_one_proper_tick"],.1)
    def test_heating_does_not_equal_temperature_even_with_ionization(self):
        for x in self.result["epochs"]:
            eps=x["CR_temperature_composition_threshold_neutral_weighted_eV"]
            self.assertGreater(eps,x["CR_temperature_composition_threshold_min_eV"])
            self.assertLess(eps,x["CR_temperature_composition_threshold_max_eV"])
            self.assertGreater(eps,0)
        # For a source temperature, the new electron increases degrees of freedom.
        T=10000.;npop=100.;nhi=1.;zeta=1e-14
        U=1.5*m.KB_ERG_K*T*npop
        eps=1.5*m.KB_ERG_K*T
        self.assertAlmostEqual(zeta*nhi*(eps/U-1/npop),0.,delta=1e-26)
        self.assertLess(zeta*nhi*(0./U-1/npop),0.)
    def test_original_neutral_ionization_cone(self):
        j=self.result
        self.assertEqual(self.columns,list(m.DERIVED_FIELDS))
        for x in j["epochs"]:
            self.assertEqual(x["native_source_cells"],46080)
            self.assertGreater(x["neutral_fraction_min"],128*math.ulp(1.))
            self.assertLess(x["neutral_fraction_max"],1.)
            self.assertLess(x["neutral_weighted_local_zeta_reverse_p10_s_inv"],
                            x["neutral_weighted_local_zeta_reverse_p50_s_inv"])
            self.assertLess(x["neutral_weighted_local_zeta_reverse_p50_s_inv"],
                            x["neutral_weighted_local_zeta_reverse_p90_s_inv"])
            self.assertEqual(x["cells_original_HII_decreasing"]+
                             x["cells_original_HII_increasing"]+
                             x["cells_original_HII_stationary"],46080)
    def test_numerical_representation_not_false_byte_equality(self):
        expected=[16992,16930,17212,17293]
        for x,n in zip(self.result["epochs"],expected):
            self.assertEqual(x["source_thermal_two_paths_distinct_float64_cell_count"],n)
            self.assertGreater(x["source_thermal_two_paths_max_rel_discrepancy"],0)
            self.assertLess(x["source_thermal_two_paths_max_rel_discrepancy"],1e-15)
    def test_original_source_independent_audit(self):
        a=self.audit
        self.assertEqual(a["source_REI367_zip_sha256"],m.SHA_REI_ZIP)
        self.assertEqual(a["source_WU_R57_gzip_sha256"],m.SHA_WU_CSV)
        self.assertEqual(a["all_original_source_checks"],"PASS")
        self.assertEqual(len(a["epoch_audit"]),4)
    def test_no_CR_on_or_canonical_false_promotion(self):
        j=self.result
        self.assertTrue(j["no_actual_CR_spectrum_or_flux"])
        self.assertTrue(j["no_CR_ON_history"])
        self.assertTrue(j["no_H_He_photon_transport"])
        self.assertTrue(j["CR_OFF"])
        self.assertEqual(j["PRODUCTION"],"HOLD")
        self.assertEqual(j["REI_canonical"],"28/88_DELTA0")
        self.assertEqual(j["BASS_CR_extension"],"0/3_DELTA0")
        self.assertEqual(j["source_assumption"],"ORIGINAL_ACCEPTED_SOURCE_POINT_AT_EPOCH_NOT_CONTINUUM_ENCLOSURE")
    def test_deterministic_public_output_and_negative_guard(self):
        self.assertEqual(m.sha(m.HERE/m.CSV_NAME),self.result["csv_sha256"])
        with tempfile.TemporaryDirectory() as f:
            p=Path(f)/"forged.json";p.write_bytes(b"not original")
            self.assertNotEqual(m.sha(p),m.SHA_WU_JSON)
        with self.assertRaisesRegex(ValueError,"CR_F05_MATERIALITY_FALSE_PASS"):
            m.req(False,"FALSE_PASS")

if __name__=="__main__":unittest.main()
