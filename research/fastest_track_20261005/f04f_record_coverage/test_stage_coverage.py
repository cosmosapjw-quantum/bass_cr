import copy
from fractions import Fraction
from pathlib import Path
import unittest

from stage_coverage import analyze,intake_f04e,static_stage_views,owner_contract

ROOT=Path(__file__).parent


class StageCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.c,cls.record,cls.obs,cls.execution=intake_f04e(ROOT/'inputs')

    def test_packet_absorber_transpose_and_single_normalization(self):
        views=static_stage_views(self.c,self.record,self.obs)
        for i,v in enumerate(views):
            events=self.obs[f'HALF{i+1}_EVENTS']
            for g in range(3):
                for a in range(3):self.assertEqual(Fraction(v['photo_per_h_packet_major_exact'][g][a]),Fraction(events[3*a+g])/Fraction(self.c.nh))

    def test_actual_receiver_context_stays_unobserved(self):
        for v in static_stage_views(self.c,self.record,self.obs):
            for key in ['actual_F08_stage','actual_expanding_time_a','actual_stage_weight','actual_F08_thermal_work_ev_per_h']:self.assertIsNone(v[key])

    def test_derived_static_times_preserve_half_sites(self):
        a,b=static_stage_views(self.c,self.record,self.obs)
        self.assertEqual((a['static_endpoint_s'],b['static_endpoint_s']),('500000000','1000000000'))
        self.assertNotEqual(a['temperature_observed_K'],b['temperature_observed_K'])

    def test_wrong_record_not_substituted_for_native_observation(self):
        d=copy.deepcopy(self.record);d['t0_s']=1
        with self.assertRaisesRegex(ValueError,'STATIC_TIME'):static_stage_views(self.c,d,self.obs)

    def test_wrong_model_bits_not_substituted(self):
        o=copy.deepcopy(self.obs);o['CONSTANTS'][0]*=2
        with self.assertRaisesRegex(ValueError,'STATIC_MODEL'):static_stage_views(self.c,self.record,o)

    def test_owner_domain_does_not_inherit_static_certificate(self):
        c=owner_contract(ROOT)
        self.assertEqual(c['paired_history'],'NOT_EXECUTED')
        self.assertEqual(c['reuse_static_records_as_expanding_stage'],'FORBIDDEN_CONTEXT_NOT_OBSERVED')
        self.assertFalse(c['mandatory_new_gate'])

    def test_stage_coverage_is_one_record_not_whole_history(self):
        r=analyze(ROOT)
        self.assertEqual((r['aggregate_25_output_records'],r['native_stage_observed_records'],r['remaining_native_stage_observation_records']),(7000,1,6999))
        self.assertEqual(r['new_native_runs'],0)


if __name__=='__main__':unittest.main()
