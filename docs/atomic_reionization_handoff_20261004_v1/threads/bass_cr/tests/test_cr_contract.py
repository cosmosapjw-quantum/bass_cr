import unittest
from fractions import Fraction as F
from cr_contract import CHANNELS, conservation, event_delta, ecm_from_lab, number_rate, cr_sources, close_energy

class ContractTests(unittest.TestCase):
    def test_every_channel_conserves_nuclei_and_charge(self):
        for name in CHANNELS:
            self.assertEqual(conservation(name), (0, 0))
    def test_cx_has_no_total_ionization(self):
        d=event_delta('resonant_cx_1s', 3)
        self.assertEqual(d['p_fast']+d['p_gas'],0)
        self.assertEqual(d['H_fast']+d['H_gas'],0)
        self.assertEqual(d['e_free'],0)
        self.assertEqual(d['p_gas'],3)
    def test_ionization_and_stripping(self):
        self.assertEqual(event_delta('target_ionization',1)['e_free'],1)
        self.assertEqual(event_delta('fast_neutral_stripping',1)['e_free'],1)
    def test_energy_frame(self):
        self.assertEqual(ecm_from_lab(100,1,1),50)
        self.assertEqual(ecm_from_lab(400,4,1),80)
    def test_number_density_measure(self):
        self.assertEqual(number_rate(F(2),[F(3)],[F(5)],[F(7)],[F(11)]),F(2310))
    def test_off_never_calls_provider(self):
        def fail(): raise AssertionError('off called provider')
        self.assertTrue(all(x==0 for x in cr_sources(False,fail).values()))
    def test_on_calls_provider(self):
        self.assertEqual(cr_sources(True,lambda:{'target_ionization':2})['e_free'],2)
    def test_unknown_channel_rejected(self):
        with self.assertRaises(ValueError):event_delta('total_cross_section',1)
    def test_energy_ledger(self):
        self.assertEqual(close_energy(10,heat=2,ion_potential=3,excitation=1,radiation=1,nonthermal=2,escape=1),0)
        with self.assertRaises(ValueError):close_energy(10,heat=10,ion_potential=3)
    def test_invalid_rates_and_inputs(self):
        for bad in [-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):event_delta('resonant_cx_1s',bad)
        with self.assertRaises(ValueError):number_rate(1,[1],[1,2],[1],[1])
        with self.assertRaises(ValueError):ecm_from_lab(1,0,1)
        with self.assertRaises(ValueError):cr_sources('false',lambda:{})

if __name__=='__main__':unittest.main()
